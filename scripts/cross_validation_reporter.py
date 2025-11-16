#!/usr/bin/env python3
"""
Cross-Validation Report Generator

PURPOSE:
Generate comprehensive validation reports comparing detector outputs against
gold set ground truth. Provides calibration metrics for Bayesian fusion.

OUTPUTS:
1. Per-detector performance (TPR, FPR, precision, recall, F1)
2. Confusion matrices for each detector
3. ROC curves and AUC scores
4. Calibration plots (predicted vs observed probabilities)
5. Cross-detector agreement analysis
6. Misclassification analysis with provenance

ANTI-FABRICATION:
- All metrics calculated on verified gold set entities
- Misclassifications logged with full provenance
- Human-reviewable samples for each error category
- Calibration source documented

Author: OSINT Foresight Team
Version: 1.0
Date: 2025-10-03
"""

import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import pandas as pd
import numpy as np
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_curve, auc, precision_recall_curve,
    matthews_corrcoef, cohen_kappa_score
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


@dataclass
class GoldSetEntity:
    """Gold set entity with ground truth label."""
    canonical_name: str
    entity_id: str
    label: str  # CRITICAL, HIGH, MEDIUM, LOW, CLEAN
    binary_label: int  # 1=China connection, 0=no connection
    confidence_label: str  # VERIFIED, STRONG, MODERATE
    provenance: Dict


@dataclass
class DetectorPrediction:
    """Detector prediction for an entity."""
    entity_id: str
    detector_id: str
    detected: bool  # Binary: detected or not
    confidence_score: float  # 0-100
    evidence: Dict


class CrossValidationReporter:
    """
    Generate cross-validation reports for detector calibration.

    Workflow:
    1. Load gold set (ground truth)
    2. Load detector predictions
    3. Calculate performance metrics
    4. Generate calibration recommendations
    5. Identify systematic errors
    """

    def __init__(self):
        self.gold_set: Dict[str, GoldSetEntity] = {}
        self.predictions: Dict[str, Dict[str, DetectorPrediction]] = defaultdict(dict)
        self.detectors: Set[str] = set()

    def load_gold_set(self, csv_path: Path):
        """Load gold set from CSV."""
        logging.info(f"Loading gold set: {csv_path}")

        df = pd.read_csv(csv_path)

        for _, row in df.iterrows():
            # Map categorical label to binary
            label = row['label']
            binary_label = 1 if label in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] else 0

            # Generate entity_id from canonical name if not present
            entity_id = row.get('entity_id', row['canonical_name'].lower().replace(' ', '_'))

            entity = GoldSetEntity(
                canonical_name=row['canonical_name'],
                entity_id=entity_id,
                label=label,
                binary_label=binary_label,
                confidence_label=row.get('confidence_label', 'VERIFIED'),
                provenance={
                    'primary_source': row.get('provenance__primary_source', ''),
                    'secondary_sources': row.get('provenance__secondary_sources', ''),
                    'justification': row.get('justification_summary', '')
                }
            )

            self.gold_set[entity_id] = entity

        logging.info(f"  Loaded {len(self.gold_set)} gold set entities")
        logging.info(f"    Positive (China): {sum(e.binary_label == 1 for e in self.gold_set.values())}")
        logging.info(f"    Negative (Clean): {sum(e.binary_label == 0 for e in self.gold_set.values())}")

    def load_detector_predictions(self, detector_id: str, detections_path: Path):
        """Load detector predictions (NDJSON format)."""
        logging.info(f"Loading predictions for: {detector_id}")

        if not detections_path.exists():
            logging.warning(f"  File not found: {detections_path}")
            return

        self.detectors.add(detector_id)

        with open(detections_path) as f:
            for line in f:
                record = json.loads(line.strip())

                # Extract entity identifier (try multiple fields)
                entity_id = (
                    record.get('entity_id') or
                    record.get('canonical_name') or
                    record.get('company_number') or
                    record.get('company_name', '')
                )

                if not entity_id:
                    continue

                # Normalize
                entity_id = str(entity_id).strip().lower().replace(' ', '_')

                # Only process if in gold set
                if entity_id not in self.gold_set:
                    continue

                prediction = DetectorPrediction(
                    entity_id=entity_id,
                    detector_id=detector_id,
                    detected=True,  # Present in file = detected
                    confidence_score=record.get('confidence_score', 70),
                    evidence=record.get('evidence', {})
                )

                self.predictions[detector_id][entity_id] = prediction

        logging.info(f"  Loaded {len(self.predictions[detector_id])} predictions on gold set")

    def calculate_detector_performance(self, detector_id: str) -> Dict:
        """
        Calculate performance metrics for a detector.

        Returns:
            Dictionary with TPR, FPR, precision, recall, F1, etc.
        """
        logging.info(f"Calculating performance for: {detector_id}")

        # Build y_true and y_pred
        y_true = []
        y_pred = []
        y_scores = []

        for entity_id, gold_entity in self.gold_set.items():
            y_true.append(gold_entity.binary_label)

            if entity_id in self.predictions[detector_id]:
                pred = self.predictions[detector_id][entity_id]
                y_pred.append(1)
                y_scores.append(pred.confidence_score / 100)
            else:
                y_pred.append(0)
                y_scores.append(0.0)

        # Confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

        # Metrics
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0  # Recall, Sensitivity
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        tnr = tn / (tn + fp) if (tn + fp) > 0 else 0  # Specificity
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tpr
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        # Advanced metrics
        mcc = matthews_corrcoef(y_true, y_pred)
        kappa = cohen_kappa_score(y_true, y_pred)

        # ROC curve
        if len(set(y_true)) > 1:  # Need both classes
            fpr_curve, tpr_curve, thresholds = roc_curve(y_true, y_scores)
            roc_auc = auc(fpr_curve, tpr_curve)
        else:
            roc_auc = None

        # Likelihood ratios
        lr_positive = tpr / fpr if fpr > 0 else float('inf')
        lr_negative = fnr / tnr if tnr > 0 else 0

        return {
            'detector_id': detector_id,
            'confusion_matrix': {
                'true_positive': int(tp),
                'true_negative': int(tn),
                'false_positive': int(fp),
                'false_negative': int(fn)
            },
            'metrics': {
                'true_positive_rate': tpr,  # Sensitivity, Recall
                'false_positive_rate': fpr,
                'true_negative_rate': tnr,  # Specificity
                'false_negative_rate': fnr,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'matthews_correlation': mcc,
                'cohen_kappa': kappa,
                'likelihood_ratio_positive': lr_positive,
                'likelihood_ratio_negative': lr_negative,
                'roc_auc': roc_auc
            },
            'calibration_recommendation': {
                'true_positive_rate': round(tpr, 2),
                'false_positive_rate': round(fpr, 2),
                'base_confidence': int(precision * 100)
            }
        }

    def identify_misclassifications(self, detector_id: str) -> Dict:
        """
        Identify and categorize misclassifications for error analysis.

        Returns:
            Dictionary with false positives and false negatives
        """
        false_positives = []
        false_negatives = []

        for entity_id, gold_entity in self.gold_set.items():
            predicted = entity_id in self.predictions[detector_id]
            actual = gold_entity.binary_label == 1

            if predicted and not actual:
                # False positive
                pred = self.predictions[detector_id][entity_id]
                false_positives.append({
                    'entity_id': entity_id,
                    'canonical_name': gold_entity.canonical_name,
                    'gold_label': gold_entity.label,
                    'predicted_confidence': pred.confidence_score,
                    'evidence': pred.evidence,
                    'gold_provenance': gold_entity.provenance
                })

            elif not predicted and actual:
                # False negative
                false_negatives.append({
                    'entity_id': entity_id,
                    'canonical_name': gold_entity.canonical_name,
                    'gold_label': gold_entity.label,
                    'gold_provenance': gold_entity.provenance,
                    'reason': 'Not detected by ' + detector_id
                })

        return {
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'false_positive_count': len(false_positives),
            'false_negative_count': len(false_negatives)
        }

    def generate_cross_detector_agreement(self) -> Dict:
        """
        Calculate agreement between detectors (which pairs agree/disagree).

        Returns:
            Dictionary with pairwise agreement statistics
        """
        logging.info("Calculating cross-detector agreement...")

        detectors = list(self.detectors)
        agreement_matrix = []

        for i, det1 in enumerate(detectors):
            for j, det2 in enumerate(detectors):
                if i >= j:
                    continue

                # Calculate agreement on gold set
                agree_count = 0
                disagree_count = 0

                for entity_id in self.gold_set:
                    pred1 = entity_id in self.predictions[det1]
                    pred2 = entity_id in self.predictions[det2]

                    if pred1 == pred2:
                        agree_count += 1
                    else:
                        disagree_count += 1

                total = agree_count + disagree_count
                agreement_rate = agree_count / total if total > 0 else 0

                agreement_matrix.append({
                    'detector_1': det1,
                    'detector_2': det2,
                    'agree_count': agree_count,
                    'disagree_count': disagree_count,
                    'agreement_rate': agreement_rate
                })

        return {
            'pairwise_agreement': agreement_matrix,
            'average_agreement': np.mean([a['agreement_rate'] for a in agreement_matrix])
        }

    def write_report(self, output_dir: Path):
        """Write comprehensive validation report."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Per-detector performance
        detector_performance = {}
        for detector_id in self.detectors:
            perf = self.calculate_detector_performance(detector_id)
            detector_performance[detector_id] = perf

        performance_path = output_dir / 'detector_performance.json'
        with open(performance_path, 'w') as f:
            json.dump(detector_performance, f, indent=2)

        logging.info(f"Detector performance written to: {performance_path}")

        # 2. Misclassifications
        misclassifications = {}
        for detector_id in self.detectors:
            miscl = self.identify_misclassifications(detector_id)
            misclassifications[detector_id] = miscl

        miscl_path = output_dir / 'misclassifications.json'
        with open(miscl_path, 'w') as f:
            json.dump(misclassifications, f, indent=2)

        logging.info(f"Misclassifications written to: {miscl_path}")

        # 3. Cross-detector agreement
        agreement = self.generate_cross_detector_agreement()

        agreement_path = output_dir / 'cross_detector_agreement.json'
        with open(agreement_path, 'w') as f:
            json.dump(agreement, f, indent=2)

        logging.info(f"Cross-detector agreement written to: {agreement_path}")

        # 4. Calibration recommendations (for Bayesian fusion)
        calibrations = []
        for detector_id in self.detectors:
            perf = detector_performance[detector_id]
            calibrations.append({
                'detector_id': detector_id,
                'version': 'v2.0',  # Update as needed
                'description': f'Calibrated from gold set validation',
                'true_positive_rate': perf['calibration_recommendation']['true_positive_rate'],
                'false_positive_rate': perf['calibration_recommendation']['false_positive_rate'],
                'base_confidence': perf['calibration_recommendation']['base_confidence'],
                'notes': f"Based on {len(self.gold_set)} gold set entities"
            })

        calibrations_output = {
            'metadata': {
                'description': 'Detector calibrations from gold set validation',
                'gold_set_size': len(self.gold_set),
                'calibration_date': '2025-10-03',
                'calibration_source': 'gold_set_cross_validation'
            },
            'detectors': calibrations
        }

        calibrations_path = output_dir / 'detector_calibrations_validated.json'
        with open(calibrations_path, 'w') as f:
            json.dump(calibrations_output, f, indent=2)

        logging.info(f"Validated calibrations written to: {calibrations_path}")

        # 5. Summary report (human-readable)
        self._write_summary_report(output_dir, detector_performance)

    def _write_summary_report(self, output_dir: Path, performance: Dict):
        """Write human-readable summary report."""

        summary_path = output_dir / 'VALIDATION_SUMMARY.md'

        with open(summary_path, 'w') as f:
            f.write("# Cross-Validation Summary Report\n\n")
            f.write(f"**Gold Set Size**: {len(self.gold_set)} entities\n\n")
            f.write(f"**Detectors Evaluated**: {len(self.detectors)}\n\n")

            f.write("## Detector Performance\n\n")
            f.write("| Detector | TPR | FPR | Precision | F1 | AUC |\n")
            f.write("|----------|-----|-----|-----------|-------|-----|\n")

            for detector_id, perf in performance.items():
                metrics = perf['metrics']
                f.write(f"| {detector_id} | ")
                f.write(f"{metrics['true_positive_rate']:.3f} | ")
                f.write(f"{metrics['false_positive_rate']:.3f} | ")
                f.write(f"{metrics['precision']:.3f} | ")
                f.write(f"{metrics['f1_score']:.3f} | ")
                auc_str = f"{metrics['roc_auc']:.3f}" if metrics['roc_auc'] else "N/A"
                f.write(f"{auc_str} |\n")

            f.write("\n## Calibration Recommendations\n\n")
            f.write("Copy these values to `config/detector_calibrations.json`:\n\n")
            f.write("```json\n")

            for detector_id, perf in performance.items():
                cal = perf['calibration_recommendation']
                f.write(f'{{\n')
                f.write(f'  "detector_id": "{detector_id}",\n')
                f.write(f'  "true_positive_rate": {cal["true_positive_rate"]},\n')
                f.write(f'  "false_positive_rate": {cal["false_positive_rate"]},\n')
                f.write(f'  "base_confidence": {cal["base_confidence"]}\n')
                f.write(f'}},\n')

            f.write("```\n\n")

            f.write("## Next Steps\n\n")
            f.write("1. Review misclassifications.json for systematic errors\n")
            f.write("2. Update detector_calibrations.json with validated parameters\n")
            f.write("3. Re-run Bayesian fusion with calibrated parameters\n")
            f.write("4. Monitor performance on production data\n")

        logging.info(f"Summary report written to: {summary_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate cross-validation report for detector calibration'
    )
    parser.add_argument(
        '--gold-set',
        type=Path,
        default=Path('validation/gold_set.csv'),
        help='Path to gold set CSV'
    )
    parser.add_argument(
        '--detectors-config',
        type=Path,
        default=Path('config/detectors_registry.json'),
        help='JSON config listing detector outputs'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('data/processed/cross_validation'),
        help='Output directory for validation reports'
    )

    args = parser.parse_args()

    logging.info("=" * 80)
    logging.info("CROSS-VALIDATION REPORT GENERATOR")
    logging.info("=" * 80)

    # Initialize reporter
    reporter = CrossValidationReporter()

    # Load gold set
    if not args.gold_set.exists():
        logging.error(f"Gold set not found: {args.gold_set}")
        return

    reporter.load_gold_set(args.gold_set)

    # Load detector predictions
    if not args.detectors_config.exists():
        logging.error(f"Detectors config not found: {args.detectors_config}")
        logging.info("Please create detectors_registry.json first")
        return

    with open(args.detectors_config) as f:
        config = json.load(f)

    for detector_spec in config['detectors']:
        reporter.load_detector_predictions(
            detector_id=detector_spec['detector_id'],
            detections_path=Path(detector_spec['output_file'])
        )

    if not reporter.detectors:
        logging.error("No detector predictions loaded")
        return

    # Generate reports
    reporter.write_report(args.output_dir)

    logging.info("=" * 80)
    logging.info("CROSS-VALIDATION COMPLETE")
    logging.info("=" * 80)
    logging.info(f"Results: {args.output_dir}")
    logging.info("=" * 80)


if __name__ == '__main__':
    main()
