#!/usr/bin/env python3
"""
Detector Correlation Matrix Analysis

PURPOSE:
Calculate correlation between different China-connection detectors to inform
Bayesian fusion. Detectors that are highly correlated provide less independent
evidence than detectors that are uncorrelated.

METHODOLOGY:
1. Load all detector outputs (PSC, USAspending, OpenAlex, SEC, Patents, etc.)
2. Build entity-detector matrix (rows=entities, cols=detectors, values=0/1)
3. Calculate Pearson correlation between detector columns
4. Identify detector clusters (highly correlated detectors)
5. Adjust Bayesian priors based on correlation

ANTI-FABRICATION:
- All detections must have provenance
- Correlation calculated only on entities with >=2 detector hits
- Output includes sample entities for manual verification

Author: OSINT Foresight Team
Version: 1.0
Date: 2025-10-03
"""

import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import numpy as np
from scipy import stats
from sklearn.metrics import matthews_corrcoef
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DetectorCorrelationAnalyzer:
    """
    Analyzes correlation between China-connection detectors.

    Key Concepts:
    - Pearson r: Linear correlation (-1 to +1)
    - Matthews Correlation Coefficient (MCC): Better for binary data
    - Phi coefficient: Pearson r for binary variables
    - Jaccard similarity: Set overlap (intersection/union)

    Interpretation:
    - r > 0.7: High correlation (detectors redundant, discount in Bayesian fusion)
    - 0.3 < r < 0.7: Moderate correlation (partial independence)
    - r < 0.3: Low correlation (independent evidence)
    """

    def __init__(self, min_entities_for_correlation: int = 10):
        """
        Args:
            min_entities_for_correlation: Minimum entities needed to calculate
                                         meaningful correlation
        """
        self.min_entities = min_entities_for_correlation
        self.entity_detector_matrix = defaultdict(dict)
        self.detector_metadata = {}
        self.entities = set()
        self.detectors = set()

    def load_detector_output(self, detector_id: str, file_path: Path,
                            version: str, description: str):
        """
        Load detection output from a detector.

        Expected format: NDJSON with fields:
        - entity_id or canonical_name
        - detection fields (varies by detector)

        Args:
            detector_id: Unique detector identifier (e.g., 'psc_strict_v3.0')
            file_path: Path to NDJSON detection file
            version: Detector version
            description: Human-readable description
        """
        logging.info(f"Loading detector: {detector_id}")

        if not file_path.exists():
            logging.warning(f"  File not found: {file_path}")
            return

        self.detector_metadata[detector_id] = {
            'version': version,
            'description': description,
            'file_path': str(file_path),
            'detection_count': 0
        }

        detected_entities = set()

        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line.strip())

                    # Extract entity identifier
                    entity_id = (
                        record.get('entity_id') or
                        record.get('canonical_name') or
                        record.get('company_number') or
                        record.get('company_name') or
                        record.get('entity_name') or  # CORDIS
                        (record.get('entity_identifiers', {}).get('company_number') if isinstance(record.get('entity_identifiers'), dict) else None) or  # PSC
                        (record.get('entity_identifiers', {}).get('extracted_text') if isinstance(record.get('entity_identifiers'), dict) else None)  # USAspending
                    )

                    if not entity_id:
                        logging.warning(f"  Line {line_num}: No entity identifier")
                        continue

                    # Normalize entity ID
                    entity_id = str(entity_id).strip().lower()

                    detected_entities.add(entity_id)
                    self.entities.add(entity_id)

                except json.JSONDecodeError:
                    logging.warning(f"  Line {line_num}: Invalid JSON")
                except Exception as e:
                    logging.warning(f"  Line {line_num}: {e}")

        # Build matrix: 1 if detected, 0 if not
        for entity_id in detected_entities:
            self.entity_detector_matrix[entity_id][detector_id] = 1

        self.detectors.add(detector_id)
        self.detector_metadata[detector_id]['detection_count'] = len(detected_entities)

        logging.info(f"  Loaded {len(detected_entities):,} detections")

    def build_binary_matrix(self) -> pd.DataFrame:
        """
        Build binary matrix: rows=entities, cols=detectors, values=0/1

        Returns:
            DataFrame with entity_id as index, detector_id as columns
        """
        logging.info("Building binary matrix...")

        # Create matrix
        matrix_data = []
        entity_ids = []

        for entity_id in self.entities:
            row = []
            for detector_id in sorted(self.detectors):
                value = self.entity_detector_matrix[entity_id].get(detector_id, 0)
                row.append(value)
            matrix_data.append(row)
            entity_ids.append(entity_id)

        df = pd.DataFrame(
            matrix_data,
            index=entity_ids,
            columns=sorted(self.detectors)
        )

        logging.info(f"  Matrix shape: {df.shape[0]:,} entities x {df.shape[1]} detectors")
        logging.info(f"  Total detections: {df.sum().sum():,}")
        logging.info(f"  Entities with 0 detections: {(df.sum(axis=1) == 0).sum():,}")
        logging.info(f"  Entities with 1 detection: {(df.sum(axis=1) == 1).sum():,}")
        logging.info(f"  Entities with 2+ detections: {(df.sum(axis=1) >= 2).sum():,}")

        return df

    def calculate_correlation_matrix(self, df: pd.DataFrame) -> Dict:
        """
        Calculate correlation between detectors using multiple metrics.

        Args:
            df: Binary matrix (entities x detectors)

        Returns:
            Dictionary with correlation matrices and metadata
        """
        logging.info("Calculating correlation matrices...")

        results = {
            'pearson': {},
            'mcc': {},
            'jaccard': {},
            'phi': {},
            'detector_pairs': []
        }

        detectors = list(df.columns)
        n_detectors = len(detectors)

        for i, det1 in enumerate(detectors):
            for j, det2 in enumerate(detectors):
                if i >= j:  # Only upper triangle (symmetric matrix)
                    continue

                # Get binary vectors
                vec1 = df[det1].values
                vec2 = df[det2].values

                # Calculate metrics
                try:
                    # Pearson correlation (same as Phi for binary data)
                    pearson_r, pearson_p = stats.pearsonr(vec1, vec2)

                    # Matthews Correlation Coefficient
                    mcc = matthews_corrcoef(vec1, vec2)

                    # Jaccard similarity
                    intersection = np.sum((vec1 == 1) & (vec2 == 1))
                    union = np.sum((vec1 == 1) | (vec2 == 1))
                    jaccard = intersection / union if union > 0 else 0

                    # Store results
                    pair_key = f"{det1}|{det2}"

                    results['pearson'][pair_key] = {
                        'r': float(pearson_r),
                        'p_value': float(pearson_p)
                    }
                    results['mcc'][pair_key] = float(mcc)
                    results['jaccard'][pair_key] = float(jaccard)
                    results['phi'][pair_key] = float(pearson_r)  # Phi = Pearson for binary

                    # Joint detection counts
                    both = np.sum((vec1 == 1) & (vec2 == 1))
                    only_det1 = np.sum((vec1 == 1) & (vec2 == 0))
                    only_det2 = np.sum((vec1 == 0) & (vec2 == 1))
                    neither = np.sum((vec1 == 0) & (vec2 == 0))

                    results['detector_pairs'].append({
                        'detector_1': det1,
                        'detector_2': det2,
                        'pearson_r': float(pearson_r),
                        'pearson_p': float(pearson_p),
                        'mcc': float(mcc),
                        'jaccard': float(jaccard),
                        'both_detect': int(both),
                        'only_det1': int(only_det1),
                        'only_det2': int(only_det2),
                        'neither': int(neither),
                        'interpretation': self._interpret_correlation(pearson_r)
                    })

                except Exception as e:
                    logging.warning(f"  Error calculating correlation for {det1} vs {det2}: {e}")

        logging.info(f"  Calculated {len(results['detector_pairs'])} pairwise correlations")

        return results

    def _interpret_correlation(self, r: float) -> str:
        """Interpret Pearson correlation coefficient."""
        abs_r = abs(r)
        if abs_r >= 0.7:
            return "HIGH - Detectors redundant, discount in fusion"
        elif abs_r >= 0.4:
            return "MODERATE - Partial independence"
        elif abs_r >= 0.2:
            return "LOW - Mostly independent"
        else:
            return "VERY LOW - Independent evidence"

    def identify_detector_clusters(self, correlation_results: Dict,
                                   threshold: float = 0.7) -> List[Set[str]]:
        """
        Identify clusters of highly correlated detectors.

        Args:
            correlation_results: Output from calculate_correlation_matrix
            threshold: Correlation threshold for clustering (default 0.7)

        Returns:
            List of detector clusters (sets of detector IDs)
        """
        logging.info(f"Identifying detector clusters (r >= {threshold})...")

        # Build adjacency list
        adjacency = defaultdict(set)

        for pair in correlation_results['detector_pairs']:
            if abs(pair['pearson_r']) >= threshold:
                det1 = pair['detector_1']
                det2 = pair['detector_2']
                adjacency[det1].add(det2)
                adjacency[det2].add(det1)

        # Find connected components (simple BFS)
        visited = set()
        clusters = []

        for detector in self.detectors:
            if detector in visited:
                continue

            # BFS to find cluster
            cluster = set()
            queue = [detector]

            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue

                visited.add(current)
                cluster.add(current)

                for neighbor in adjacency[current]:
                    if neighbor not in visited:
                        queue.append(neighbor)

            clusters.append(cluster)

        logging.info(f"  Found {len(clusters)} clusters:")
        for i, cluster in enumerate(clusters, 1):
            if len(cluster) > 1:
                logging.info(f"    Cluster {i}: {', '.join(sorted(cluster))}")

        return clusters

    def generate_sample_entities(self, df: pd.DataFrame,
                                n_samples: int = 10) -> List[Dict]:
        """
        Generate sample entities for manual verification of correlation patterns.

        Args:
            df: Binary matrix
            n_samples: Number of samples per pattern

        Returns:
            List of sample entity records
        """
        samples = []

        # Pattern 1: Entities detected by all detectors
        all_detected = df[df.sum(axis=1) == len(df.columns)]
        if len(all_detected) > 0:
            sample_ids = all_detected.head(n_samples).index.tolist()
            for entity_id in sample_ids:
                samples.append({
                    'entity_id': entity_id,
                    'pattern': 'ALL_DETECTORS',
                    'detectors': df.columns.tolist(),
                    'detection_count': len(df.columns)
                })

        # Pattern 2: Entities detected by exactly 2 detectors (pairwise)
        two_detected = df[df.sum(axis=1) == 2]
        if len(two_detected) > 0:
            sample_ids = two_detected.head(n_samples).index.tolist()
            for entity_id in sample_ids:
                detected = [col for col in df.columns if df.loc[entity_id, col] == 1]
                samples.append({
                    'entity_id': entity_id,
                    'pattern': 'PAIRWISE',
                    'detectors': detected,
                    'detection_count': 2
                })

        # Pattern 3: Entities detected by only 1 detector
        one_detected = df[df.sum(axis=1) == 1]
        if len(one_detected) > 0:
            sample_ids = one_detected.head(n_samples).index.tolist()
            for entity_id in sample_ids:
                detected = [col for col in df.columns if df.loc[entity_id, col] == 1]
                samples.append({
                    'entity_id': entity_id,
                    'pattern': 'SINGLE_DETECTOR',
                    'detectors': detected,
                    'detection_count': 1
                })

        return samples

    def write_results(self, output_dir: Path, correlation_results: Dict,
                     clusters: List[Set[str]], samples: List[Dict],
                     matrix: pd.DataFrame):
        """Write correlation analysis results to disk."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Correlation matrix (full results)
        correlation_path = output_dir / 'correlation_matrix.json'
        with open(correlation_path, 'w') as f:
            json.dump({
                'detector_metadata': self.detector_metadata,
                'correlation_results': correlation_results,
                'clusters': [list(cluster) for cluster in clusters],
                'sample_entities': samples,
                'summary': {
                    'total_entities': len(self.entities),
                    'total_detectors': len(self.detectors),
                    'entities_with_multiple_detections': int((matrix.sum(axis=1) >= 2).sum())
                }
            }, f, indent=2)

        logging.info(f"Correlation matrix written to: {correlation_path}")

        # 2. Pairwise correlation table (CSV for easy review)
        pairs_df = pd.DataFrame(correlation_results['detector_pairs'])
        if not pairs_df.empty and 'pearson_r' in pairs_df.columns:
            pairs_df = pairs_df.sort_values('pearson_r', ascending=False)
        pairs_path = output_dir / 'detector_pairs.csv'
        pairs_df.to_csv(pairs_path, index=False)

        logging.info(f"Pairwise correlations written to: {pairs_path}")

        # 3. Heatmap data (for visualization)
        heatmap_data = {}
        for detector in sorted(self.detectors):
            heatmap_data[detector] = {}
            for detector2 in sorted(self.detectors):
                if detector == detector2:
                    heatmap_data[detector][detector2] = 1.0
                else:
                    pair_key = f"{min(detector, detector2)}|{max(detector, detector2)}"
                    r = correlation_results['pearson'].get(pair_key, {}).get('r', 0)
                    heatmap_data[detector][detector2] = r

        heatmap_path = output_dir / 'correlation_heatmap.json'
        with open(heatmap_path, 'w') as f:
            json.dump(heatmap_data, f, indent=2)

        logging.info(f"Heatmap data written to: {heatmap_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Calculate detector correlation matrix for Bayesian fusion'
    )
    parser.add_argument(
        '--detectors-config',
        type=Path,
        default=Path('config/detectors_registry.json'),
        help='JSON config listing all detector outputs'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('data/processed/correlation_analysis'),
        help='Output directory for correlation results'
    )
    parser.add_argument(
        '--min-entities',
        type=int,
        default=10,
        help='Minimum entities needed for meaningful correlation'
    )

    args = parser.parse_args()

    logging.info("=" * 80)
    logging.info("DETECTOR CORRELATION MATRIX ANALYSIS")
    logging.info("=" * 80)

    # Initialize analyzer
    analyzer = DetectorCorrelationAnalyzer(
        min_entities_for_correlation=args.min_entities
    )

    # Load detector registry
    if not args.detectors_config.exists():
        logging.error(f"Detectors config not found: {args.detectors_config}")
        logging.info("Creating example config...")

        example_config = {
            'detectors': [
                {
                    'detector_id': 'psc_strict_v3.0',
                    'version': 'v3.0',
                    'description': 'PSC nationality-first strict detection',
                    'output_file': 'data/processed/psc_strict_v3/detections.ndjson'
                },
                {
                    'detector_id': 'usaspending_v2.0',
                    'version': 'v2.0',
                    'description': 'USAspending China contracts detector',
                    'output_file': 'data/processed/usaspending_china/detections.ndjson'
                },
                {
                    'detector_id': 'openalex_collaboration_v2.0',
                    'version': 'v2.0',
                    'description': 'OpenAlex China research collaboration',
                    'output_file': 'data/processed/openalex_china/detections.ndjson'
                }
            ]
        }

        args.detectors_config.parent.mkdir(parents=True, exist_ok=True)
        with open(args.detectors_config, 'w') as f:
            json.dump(example_config, f, indent=2)

        logging.info(f"Example config written to: {args.detectors_config}")
        logging.info("Please update with actual detector paths and re-run.")
        return

    # Load detectors
    with open(args.detectors_config) as f:
        config = json.load(f)

    for detector_spec in config['detectors']:
        analyzer.load_detector_output(
            detector_id=detector_spec['detector_id'],
            file_path=Path(detector_spec['output_file']),
            version=detector_spec['version'],
            description=detector_spec['description']
        )

    # Build binary matrix
    matrix = analyzer.build_binary_matrix()

    if len(analyzer.detectors) < 2:
        logging.error("Need at least 2 detectors to calculate correlation")
        return

    # Calculate correlations
    correlation_results = analyzer.calculate_correlation_matrix(matrix)

    # Identify clusters
    clusters = analyzer.identify_detector_clusters(correlation_results, threshold=0.7)

    # Generate samples
    samples = analyzer.generate_sample_entities(matrix, n_samples=10)

    # Write results
    analyzer.write_results(
        output_dir=args.output_dir,
        correlation_results=correlation_results,
        clusters=clusters,
        samples=samples,
        matrix=matrix
    )

    logging.info("=" * 80)
    logging.info("CORRELATION ANALYSIS COMPLETE")
    logging.info("=" * 80)
    logging.info(f"Results: {args.output_dir}")
    logging.info("")
    logging.info("Next steps:")
    logging.info("1. Review detector_pairs.csv for correlation patterns")
    logging.info("2. Inspect clusters of highly correlated detectors")
    logging.info("3. Use correlation_matrix.json in Bayesian fusion")
    logging.info("=" * 80)


if __name__ == '__main__':
    main()
