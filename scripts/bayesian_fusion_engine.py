#!/usr/bin/env python3
"""
Bayesian Fusion Engine

PURPOSE:
Combine multiple detector signals using Bayesian inference with correlation
adjustment. Replaces naive additive risk scoring with principled probability
fusion that accounts for detector correlation.

METHODOLOGY:
1. Start with prior probability P(China) based on base rates
2. For each detector hit, update posterior using Bayes' theorem
3. Adjust for detector correlation (correlated detectors provide less info)
4. Output final posterior probability and confidence intervals

BAYESIAN UPDATE FORMULA:
P(China|D1,D2,...,Dn) = P(D1,D2,...,Dn|China) * P(China) / P(D1,D2,...,Dn)

For independent detectors:
P(D1,D2|China) = P(D1|China) * P(D2|China)

For correlated detectors (correlation r):
Effective evidence discount = 1 - |r|
(e.g., r=0.8 means second detector provides only 20% new information)

ANTI-FABRICATION:
- All detections must have provenance
- Prior probabilities documented with source
- Likelihood ratios calibrated on gold set
- Uncertainty quantification via confidence intervals

Author: OSINT Foresight Team
Version: 1.0
Date: 2025-10-03
"""

import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import numpy as np
from scipy import stats

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


@dataclass
class DetectorCalibration:
    """Calibration parameters for a detector."""
    detector_id: str
    version: str
    true_positive_rate: float  # P(detect|China) = sensitivity
    false_positive_rate: float  # P(detect|~China) = 1-specificity
    base_confidence: float  # Detector base confidence (0-100)

    @property
    def likelihood_ratio_positive(self) -> float:
        """LR+ = TPR / FPR"""
        if self.false_positive_rate == 0:
            return float('inf')
        return self.true_positive_rate / self.false_positive_rate

    @property
    def likelihood_ratio_negative(self) -> float:
        """LR- = (1-TPR) / (1-FPR)"""
        return (1 - self.true_positive_rate) / (1 - self.false_positive_rate)


class BayesianFusionEngine:
    """
    Bayesian fusion engine for combining multiple detector signals.

    Key Concepts:
    - Prior: P(China) before seeing any evidence
    - Likelihood: P(evidence|China) and P(evidence|~China)
    - Posterior: P(China|evidence) after seeing evidence
    - Correlation adjustment: Discount for correlated detectors
    """

    def __init__(self,
                 prior_probability: float = 0.05,
                 correlation_matrix_path: Optional[Path] = None,
                 detector_calibrations_path: Optional[Path] = None):
        """
        Args:
            prior_probability: Base rate P(China connection) before evidence
            correlation_matrix_path: Path to correlation matrix JSON
            detector_calibrations_path: Path to detector calibrations JSON
        """
        self.prior_probability = prior_probability
        self.correlation_matrix = {}
        self.detector_calibrations = {}

        if correlation_matrix_path and correlation_matrix_path.exists():
            self._load_correlation_matrix(correlation_matrix_path)

        if detector_calibrations_path and detector_calibrations_path.exists():
            self._load_detector_calibrations(detector_calibrations_path)

    def _load_correlation_matrix(self, path: Path):
        """Load detector correlation matrix."""
        logging.info(f"Loading correlation matrix: {path}")

        with open(path) as f:
            data = json.load(f)

        # Extract pairwise correlations
        for pair in data.get('correlation_results', {}).get('detector_pairs', []):
            det1 = pair['detector_1']
            det2 = pair['detector_2']
            r = pair['pearson_r']

            self.correlation_matrix[(det1, det2)] = r
            self.correlation_matrix[(det2, det1)] = r  # Symmetric

        logging.info(f"  Loaded {len(self.correlation_matrix) // 2} pairwise correlations")

    def _load_detector_calibrations(self, path: Path):
        """Load detector calibration parameters."""
        logging.info(f"Loading detector calibrations: {path}")

        with open(path) as f:
            calibrations = json.load(f)

        for cal_data in calibrations.get('detectors', []):
            cal = DetectorCalibration(
                detector_id=cal_data['detector_id'],
                version=cal_data['version'],
                true_positive_rate=cal_data['true_positive_rate'],
                false_positive_rate=cal_data['false_positive_rate'],
                base_confidence=cal_data['base_confidence']
            )
            self.detector_calibrations[cal.detector_id] = cal

        logging.info(f"  Loaded {len(self.detector_calibrations)} detector calibrations")

    def get_correlation(self, det1: str, det2: str) -> float:
        """Get correlation between two detectors (0 if not available)."""
        return self.correlation_matrix.get((det1, det2), 0.0)

    def calculate_correlation_discount(self, detectors: List[str]) -> Dict[str, float]:
        """
        Calculate evidence discount for each detector based on correlation.

        For a detector D_i given previous detectors D_1,...,D_{i-1}:
        Discount = max(|r(D_i, D_j)|) for j < i

        Higher correlation = lower weight (more redundant information)

        Args:
            detectors: List of detector IDs in order

        Returns:
            Dict mapping detector_id to discount factor (0-1)
        """
        discounts = {}

        for i, detector in enumerate(detectors):
            if i == 0:
                # First detector gets full weight
                discounts[detector] = 1.0
            else:
                # Calculate max correlation with previous detectors
                max_corr = 0.0
                for prev_detector in detectors[:i]:
                    corr = abs(self.get_correlation(detector, prev_detector))
                    max_corr = max(max_corr, corr)

                # Discount = 1 - max_correlation
                # e.g., r=0.8 -> discount=0.2 (only 20% new info)
                discounts[detector] = 1.0 - max_corr

        return discounts

    def fuse_detections(self, detections: List[Dict]) -> Dict:
        """
        Fuse multiple detections using Bayesian inference.

        Args:
            detections: List of detection records, each with:
                - detector_id
                - confidence_score (0-100)
                - evidence (provenance)

        Returns:
            Fusion result with posterior probability and diagnostics
        """
        if not detections:
            return {
                'posterior_probability': self.prior_probability,
                'risk_score': int(self.prior_probability * 100),
                'risk_level': self._risk_level(self.prior_probability),
                'num_detections': 0,
                'detectors': [],
                'fusion_method': 'prior_only'
            }

        # Sort detectors by confidence (highest first for optimal ordering)
        detections = sorted(detections,
                          key=lambda d: d.get('confidence_score', 50),
                          reverse=True)

        detector_ids = [d['detector_id'] for d in detections]

        # Calculate correlation discounts
        discounts = self.calculate_correlation_discount(detector_ids)

        # Bayesian update
        posterior = self.prior_probability
        fusion_log = []

        for detection in detections:
            detector_id = detection['detector_id']
            confidence = detection.get('confidence_score', 50) / 100  # Normalize to 0-1
            discount = discounts.get(detector_id, 1.0)

            # Get calibration or use defaults
            if detector_id in self.detector_calibrations:
                cal = self.detector_calibrations[detector_id]
                lr_positive = cal.likelihood_ratio_positive
            else:
                # Default calibration based on confidence
                # High confidence -> high TPR, low FPR
                tpr = 0.5 + (confidence * 0.45)  # 0.5 to 0.95
                fpr = 0.1 * (1 - confidence)  # 0.1 to 0.01
                lr_positive = tpr / max(fpr, 0.001)

            # Apply correlation discount to likelihood ratio
            # Discounted LR moves toward 1 (neutral evidence)
            lr_discounted = 1 + (lr_positive - 1) * discount

            # Bayesian update: odds form
            prior_odds = posterior / (1 - posterior)
            posterior_odds = prior_odds * lr_discounted
            posterior_new = posterior_odds / (1 + posterior_odds)

            fusion_log.append({
                'detector_id': detector_id,
                'confidence': confidence,
                'prior': posterior,
                'likelihood_ratio': lr_positive,
                'correlation_discount': discount,
                'lr_discounted': lr_discounted,
                'posterior': posterior_new
            })

            posterior = posterior_new

        # Calculate confidence interval (95%)
        # Use beta distribution approximation
        n_detections = len(detections)
        alpha = posterior * n_detections + 1
        beta_param = (1 - posterior) * n_detections + 1
        ci_lower, ci_upper = stats.beta.interval(0.95, alpha, beta_param)

        return {
            'posterior_probability': posterior,
            'risk_score': int(posterior * 100),
            'risk_level': self._risk_level(posterior),
            'confidence_interval_95': {
                'lower': ci_lower,
                'upper': ci_upper
            },
            'num_detections': len(detections),
            'detectors': detector_ids,
            'fusion_method': 'bayesian_correlated',
            'fusion_log': fusion_log,
            'effective_detections': sum(discounts.values())  # Account for correlation
        }

    def _risk_level(self, probability: float) -> str:
        """Map posterior probability to categorical risk level."""
        if probability < 0.10:
            return "CLEAN"
        elif probability < 0.30:
            return "LOW"
        elif probability < 0.60:
            return "MEDIUM"
        elif probability < 0.85:
            return "HIGH"
        else:
            return "CRITICAL"

    def batch_fuse_entities(self, entities_path: Path, output_path: Path):
        """
        Batch process entities with Bayesian fusion.

        Args:
            entities_path: Path to entities NDJSON (with china_connections)
            output_path: Path to write fused results
        """
        logging.info(f"Batch processing entities: {entities_path}")

        processed = 0
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(entities_path) as f_in, open(output_path, 'w') as f_out:
            for line in f_in:
                entity = json.loads(line.strip())

                # Extract detections
                detections = entity.get('china_connections', [])

                # Fuse
                fusion_result = self.fuse_detections(detections)

                # Update entity
                entity['aggregate_risk'] = {
                    'posterior_probability': fusion_result['posterior_probability'],
                    'risk_score': fusion_result['risk_score'],
                    'risk_level': fusion_result['risk_level'],
                    'confidence_interval_95': fusion_result.get('confidence_interval_95', {}),
                    'fusion_method': fusion_result['fusion_method'],
                    'effective_detections': fusion_result.get('effective_detections', len(detections))
                }

                # Write
                f_out.write(json.dumps(entity) + '\n')
                processed += 1

                if processed % 1000 == 0:
                    logging.info(f"  Processed {processed:,} entities")

        logging.info(f"Batch processing complete: {processed:,} entities")


def create_default_calibrations(output_path: Path):
    """Create default detector calibrations based on expected performance."""

    calibrations = {
        'metadata': {
            'description': 'Default detector calibrations - UPDATE with gold set validation',
            'creation_date': '2025-10-03',
            'calibration_source': 'expert_estimates'
        },
        'detectors': [
            {
                'detector_id': 'psc_strict_v3.0',
                'version': 'v3.0',
                'description': 'PSC nationality-first strict detection',
                'true_positive_rate': 0.90,  # 90% of actual China PSCs detected
                'false_positive_rate': 0.02,  # 2% false positive rate
                'base_confidence': 95,
                'notes': 'High precision nationality-first detection'
            },
            {
                'detector_id': 'usaspending_v2.0',
                'version': 'v2.0',
                'description': 'USAspending China contracts',
                'true_positive_rate': 0.85,
                'false_positive_rate': 0.05,
                'base_confidence': 85,
                'notes': 'Contracts explicitly marked as China-related'
            },
            {
                'detector_id': 'openalex_collaboration_v2.0',
                'version': 'v2.0',
                'description': 'OpenAlex China research collaboration',
                'true_positive_rate': 0.75,
                'false_positive_rate': 0.10,
                'base_confidence': 70,
                'notes': 'Research collaborations - some false positives from diaspora'
            },
            {
                'detector_id': 'sec_edgar_v2.0',
                'version': 'v2.0',
                'description': 'SEC filings China mentions',
                'true_positive_rate': 0.80,
                'false_positive_rate': 0.08,
                'base_confidence': 75,
                'notes': 'China business operations from 10-K/10-Q'
            },
            {
                'detector_id': 'patents_cpc_v2.0',
                'version': 'v2.0',
                'description': 'Patents with China co-inventors',
                'true_positive_rate': 0.70,
                'false_positive_rate': 0.12,
                'base_confidence': 65,
                'notes': 'Patent co-authorship - diaspora effect'
            }
        ]
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(calibrations, f, indent=2)

    logging.info(f"Default calibrations written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Bayesian fusion engine for detector signals'
    )
    parser.add_argument(
        '--entities',
        type=Path,
        required=True,
        help='Input entities NDJSON with china_connections'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output path for fused entities'
    )
    parser.add_argument(
        '--correlation-matrix',
        type=Path,
        default=Path('data/processed/correlation_analysis/correlation_matrix.json'),
        help='Path to correlation matrix JSON'
    )
    parser.add_argument(
        '--calibrations',
        type=Path,
        default=Path('config/detector_calibrations.json'),
        help='Path to detector calibrations JSON'
    )
    parser.add_argument(
        '--prior',
        type=float,
        default=0.05,
        help='Prior probability P(China connection) [default: 0.05 = 5%]'
    )
    parser.add_argument(
        '--create-default-calibrations',
        action='store_true',
        help='Create default calibrations file and exit'
    )

    args = parser.parse_args()

    if args.create_default_calibrations:
        create_default_calibrations(args.calibrations)
        return

    logging.info("=" * 80)
    logging.info("BAYESIAN FUSION ENGINE")
    logging.info("=" * 80)
    logging.info(f"Prior probability: {args.prior:.3f}")

    # Initialize engine
    engine = BayesianFusionEngine(
        prior_probability=args.prior,
        correlation_matrix_path=args.correlation_matrix,
        detector_calibrations_path=args.calibrations
    )

    # Batch process
    engine.batch_fuse_entities(args.entities, args.output)

    logging.info("=" * 80)
    logging.info("BAYESIAN FUSION COMPLETE")
    logging.info("=" * 80)
    logging.info(f"Output: {args.output}")
    logging.info("")
    logging.info("Next steps:")
    logging.info("1. Review fused posterior probabilities")
    logging.info("2. Validate against gold set")
    logging.info("3. Calibrate detector TPR/FPR from validation results")
    logging.info("=" * 80)


if __name__ == '__main__':
    main()
