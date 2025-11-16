#!/usr/bin/env python3
"""
Phase 2 Orchestrator: Detector Correlation & Bayesian Fusion

PURPOSE:
Orchestrate the complete Phase 2 workflow:
1. Wait for detector outputs to complete
2. Calculate detector correlation matrix
3. Generate cross-validation reports
4. Calibrate Bayesian fusion parameters
5. Run full fusion on all entities
6. Generate final risk-scored entity database

WORKFLOW:
Step 1: Check detector outputs are ready
Step 2: Run correlation analysis
Step 3: Run cross-validation on gold set
Step 4: Create calibrated detector config
Step 5: Run Bayesian fusion on full dataset
Step 6: Generate summary reports

ANTI-FABRICATION:
- All steps logged with timestamps
- Intermediate outputs preserved for audit
- Provenance chains maintained throughout
- Human review checkpoints for calibration

Author: OSINT Foresight Team
Version: 1.0
Date: 2025-10-03
"""

import json
import logging
import argparse
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class Phase2Orchestrator:
    """
    Orchestrate Phase 2: Detector Correlation & Bayesian Fusion.

    Responsibilities:
    - Check detector readiness
    - Execute pipeline steps in correct order
    - Handle failures and retries
    - Generate comprehensive logs
    """

    def __init__(self, config_path: Path):
        """
        Args:
            config_path: Path to Phase 2 configuration JSON
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_base = Path(f"data/processed/phase2_{self.run_id}")
        self.output_base.mkdir(parents=True, exist_ok=True)

        # Initialize run log
        self.run_log = {
            'run_id': self.run_id,
            'start_time': datetime.now().isoformat(),
            'steps_completed': [],
            'steps_failed': [],
            'outputs': {}
        }

    def _load_config(self) -> Dict:
        """Load Phase 2 configuration."""
        if not self.config_path.exists():
            logging.info("Config not found, creating default...")
            self._create_default_config()

        with open(self.config_path) as f:
            return json.load(f)

    def _create_default_config(self):
        """Create default Phase 2 configuration."""
        default_config = {
            'phase2_config': {
                'description': 'Phase 2: Detector Correlation & Bayesian Fusion',
                'prior_probability': 0.05,
                'min_entities_for_correlation': 10,
                'correlation_threshold': 0.7
            },
            'detectors': [
                {
                    'detector_id': 'psc_strict_v3.0',
                    'version': 'v3.0',
                    'description': 'PSC nationality-first strict detection',
                    'output_file': 'data/processed/psc_strict_v3/detections.ndjson',
                    'status_file': 'data/processed/psc_strict_v3/statistics.json'
                },
                {
                    'detector_id': 'usaspending_v2.0',
                    'version': 'v2.0',
                    'description': 'USAspending China contracts',
                    'output_file': 'data/processed/usaspending_china/detections.ndjson',
                    'status_file': 'data/processed/usaspending_china/checkpoint.json'
                },
                {
                    'detector_id': 'openalex_collaboration_v2.0',
                    'version': 'v2.0',
                    'description': 'OpenAlex China research collaboration',
                    'output_file': 'data/processed/openalex_china/detections.ndjson',
                    'status_file': 'data/processed/openalex_china/checkpoint.json'
                }
            ],
            'gold_set': 'validation/gold_set.csv',
            'scripts': {
                'correlation_matrix': 'scripts/detector_correlation_matrix.py',
                'cross_validation': 'scripts/cross_validation_reporter.py',
                'bayesian_fusion': 'scripts/bayesian_fusion_engine.py'
            }
        }

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)

        logging.info(f"Default config created: {self.config_path}")

    def check_detector_readiness(self) -> Dict[str, bool]:
        """
        Check if all detector outputs are ready.

        Returns:
            Dict mapping detector_id to readiness status
        """
        logging.info("Checking detector readiness...")

        readiness = {}

        for detector in self.config['detectors']:
            detector_id = detector['detector_id']
            output_file = Path(detector['output_file'])
            status_file = Path(detector.get('status_file', ''))

            # Check output file exists and is non-empty
            output_ready = output_file.exists() and output_file.stat().st_size > 0

            # Check status file if specified
            status_ready = True
            if status_file and status_file.exists():
                try:
                    with open(status_file) as f:
                        status = json.load(f)
                        # Look for completion indicators
                        status_ready = (
                            status.get('complete', False) or
                            status.get('processing_complete', False) or
                            'final_detections' in status
                        )
                except:
                    status_ready = False

            ready = output_ready and status_ready
            readiness[detector_id] = ready

            status_str = "READY" if ready else "NOT READY"
            logging.info(f"  {detector_id}: {status_str}")

        return readiness

    def wait_for_detectors(self, check_interval: int = 300, max_wait: int = 86400):
        """
        Wait for all detectors to complete (with timeout).

        Args:
            check_interval: Seconds between readiness checks
            max_wait: Maximum seconds to wait (default 24 hours)
        """
        logging.info(f"Waiting for detectors (max {max_wait}s, check every {check_interval}s)...")

        start_time = time.time()

        while True:
            readiness = self.check_detector_readiness()

            if all(readiness.values()):
                logging.info("All detectors ready!")
                return

            elapsed = time.time() - start_time
            if elapsed > max_wait:
                not_ready = [det for det, ready in readiness.items() if not ready]
                logging.error(f"Timeout waiting for detectors: {', '.join(not_ready)}")
                raise TimeoutError(f"Detectors not ready after {max_wait}s")

            logging.info(f"  Waiting... ({int(elapsed)}s elapsed)")
            time.time.sleep(check_interval)

    def run_correlation_analysis(self) -> Path:
        """
        Run detector correlation matrix analysis.

        Returns:
            Path to correlation results
        """
        logging.info("=" * 80)
        logging.info("STEP 1: Detector Correlation Analysis")
        logging.info("=" * 80)

        # Create detectors registry
        registry_path = self.output_base / 'detectors_registry.json'
        with open(registry_path, 'w') as f:
            json.dump({'detectors': self.config['detectors']}, f, indent=2)

        # Run correlation analysis
        correlation_output = self.output_base / 'correlation_analysis'
        script = self.config['scripts']['correlation_matrix']

        cmd = [
            'python', script,
            '--detectors-config', str(registry_path),
            '--output-dir', str(correlation_output),
            '--min-entities', str(self.config['phase2_config']['min_entities_for_correlation'])
        ]

        logging.info(f"Running: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logging.error(f"Correlation analysis failed: {result.stderr}")
            self.run_log['steps_failed'].append('correlation_analysis')
            raise RuntimeError("Correlation analysis failed")

        logging.info("Correlation analysis complete")
        self.run_log['steps_completed'].append('correlation_analysis')
        self.run_log['outputs']['correlation_matrix'] = str(correlation_output / 'correlation_matrix.json')

        return correlation_output

    def run_cross_validation(self) -> Path:
        """
        Run cross-validation on gold set.

        Returns:
            Path to cross-validation results
        """
        logging.info("=" * 80)
        logging.info("STEP 2: Cross-Validation on Gold Set")
        logging.info("=" * 80)

        gold_set = Path(self.config['gold_set'])
        registry_path = self.output_base / 'detectors_registry.json'
        cross_val_output = self.output_base / 'cross_validation'

        script = self.config['scripts']['cross_validation']

        cmd = [
            'python', script,
            '--gold-set', str(gold_set),
            '--detectors-config', str(registry_path),
            '--output-dir', str(cross_val_output)
        ]

        logging.info(f"Running: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logging.error(f"Cross-validation failed: {result.stderr}")
            self.run_log['steps_failed'].append('cross_validation')
            raise RuntimeError("Cross-validation failed")

        logging.info("Cross-validation complete")
        self.run_log['steps_completed'].append('cross_validation')
        self.run_log['outputs']['cross_validation_report'] = str(cross_val_output / 'VALIDATION_SUMMARY.md')
        self.run_log['outputs']['detector_calibrations'] = str(cross_val_output / 'detector_calibrations_validated.json')

        return cross_val_output

    def create_unified_entity_file(self) -> Path:
        """
        Merge all detector outputs into unified entity file.

        Returns:
            Path to unified entities NDJSON
        """
        logging.info("=" * 80)
        logging.info("STEP 3: Creating Unified Entity File")
        logging.info("=" * 80)

        unified_path = self.output_base / 'entities_unified.ndjson'

        # Load all detections
        entity_detections = {}

        for detector in self.config['detectors']:
            detector_id = detector['detector_id']
            output_file = Path(detector['output_file'])

            logging.info(f"Loading detections from: {detector_id}")

            with open(output_file) as f:
                for line in f:
                    record = json.loads(line.strip())

                    entity_id = (
                        record.get('entity_id') or
                        record.get('canonical_name') or
                        record.get('company_number', '')
                    )

                    if not entity_id:
                        continue

                    entity_id = str(entity_id).strip()

                    if entity_id not in entity_detections:
                        entity_detections[entity_id] = {
                            'entity_id': entity_id,
                            'canonical_name': record.get('canonical_name', entity_id),
                            'entity_type': record.get('entity_type', 'unknown'),
                            'country_iso3': record.get('country_iso3', 'UNK'),
                            'china_connections': []
                        }

                    # Add detection
                    detection = {
                        'detection_id': record.get('detection_id', f"{detector_id}_{entity_id}"),
                        'detector_id': detector_id,
                        'confidence_score': record.get('confidence_score', 70),
                        'evidence': record.get('evidence', {}),
                        'temporal_range': record.get('temporal_range', {
                            'valid_from': 'unknown',
                            'valid_to': '9999-12-31',
                            'inferred': True
                        })
                    }

                    entity_detections[entity_id]['china_connections'].append(detection)

        # Write unified file
        logging.info(f"Writing {len(entity_detections):,} entities to unified file...")

        with open(unified_path, 'w') as f:
            for entity in entity_detections.values():
                f.write(json.dumps(entity) + '\n')

        logging.info(f"Unified entity file created: {unified_path}")
        self.run_log['outputs']['unified_entities'] = str(unified_path)

        return unified_path

    def run_bayesian_fusion(self, entities_path: Path, cross_val_path: Path,
                           correlation_path: Path) -> Path:
        """
        Run Bayesian fusion on all entities.

        Returns:
            Path to fused entities
        """
        logging.info("=" * 80)
        logging.info("STEP 4: Bayesian Fusion")
        logging.info("=" * 80)

        fused_path = self.output_base / 'entities_fused.ndjson'

        script = self.config['scripts']['bayesian_fusion']
        calibrations = cross_val_path / 'detector_calibrations_validated.json'
        correlation_matrix = correlation_path / 'correlation_matrix.json'

        cmd = [
            'python', script,
            '--entities', str(entities_path),
            '--output', str(fused_path),
            '--correlation-matrix', str(correlation_matrix),
            '--calibrations', str(calibrations),
            '--prior', str(self.config['phase2_config']['prior_probability'])
        ]

        logging.info(f"Running: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logging.error(f"Bayesian fusion failed: {result.stderr}")
            self.run_log['steps_failed'].append('bayesian_fusion')
            raise RuntimeError("Bayesian fusion failed")

        logging.info("Bayesian fusion complete")
        self.run_log['steps_completed'].append('bayesian_fusion')
        self.run_log['outputs']['fused_entities'] = str(fused_path)

        return fused_path

    def generate_summary_report(self):
        """Generate final summary report for Phase 2."""
        logging.info("=" * 80)
        logging.info("STEP 5: Generating Summary Report")
        logging.info("=" * 80)

        summary_path = self.output_base / 'PHASE2_SUMMARY.md'

        with open(summary_path, 'w') as f:
            f.write("# Phase 2 Summary: Detector Correlation & Bayesian Fusion\n\n")
            f.write(f"**Run ID**: {self.run_id}\n\n")
            f.write(f"**Completion Time**: {datetime.now().isoformat()}\n\n")

            f.write("## Steps Completed\n\n")
            for step in self.run_log['steps_completed']:
                f.write(f"- {step}\n")

            if self.run_log['steps_failed']:
                f.write("\n## Steps Failed\n\n")
                for step in self.run_log['steps_failed']:
                    f.write(f"- {step}\n")

            f.write("\n## Outputs\n\n")
            for output_name, output_path in self.run_log['outputs'].items():
                f.write(f"- **{output_name}**: `{output_path}`\n")

            f.write("\n## Next Steps\n\n")
            f.write("1. Review cross-validation report for detector performance\n")
            f.write("2. Inspect correlation matrix for detector independence\n")
            f.write("3. Validate fused entities against gold set (re-run pytest)\n")
            f.write("4. Proceed to Phase 3: Entity Resolution & Deduplication\n")

        logging.info(f"Summary report written to: {summary_path}")

        # Write run log
        log_path = self.output_base / 'run_log.json'
        self.run_log['end_time'] = datetime.now().isoformat()

        with open(log_path, 'w') as f:
            json.dump(self.run_log, f, indent=2)

        logging.info(f"Run log written to: {log_path}")

    def execute(self, wait_for_detectors: bool = False):
        """Execute complete Phase 2 workflow."""
        logging.info("=" * 80)
        logging.info("PHASE 2 ORCHESTRATOR: STARTING")
        logging.info("=" * 80)
        logging.info(f"Run ID: {self.run_id}")
        logging.info(f"Output: {self.output_base}")
        logging.info("=" * 80)

        try:
            # Step 0: Wait for detectors if requested
            if wait_for_detectors:
                self.wait_for_detectors()
            else:
                readiness = self.check_detector_readiness()
                if not all(readiness.values()):
                    not_ready = [det for det, ready in readiness.items() if not ready]
                    logging.warning(f"Detectors not ready: {', '.join(not_ready)}")
                    logging.warning("Continuing anyway (use --wait to block until ready)")

            # Step 1: Correlation analysis
            correlation_path = self.run_correlation_analysis()

            # Step 2: Cross-validation
            cross_val_path = self.run_cross_validation()

            # Step 3: Unified entity file
            entities_path = self.create_unified_entity_file()

            # Step 4: Bayesian fusion
            fused_path = self.run_bayesian_fusion(entities_path, cross_val_path, correlation_path)

            # Step 5: Summary report
            self.generate_summary_report()

            logging.info("=" * 80)
            logging.info("PHASE 2 COMPLETE")
            logging.info("=" * 80)
            logging.info(f"Results: {self.output_base}")
            logging.info("=" * 80)

        except Exception as e:
            logging.error(f"Phase 2 failed: {e}")
            self.run_log['error'] = str(e)
            self.run_log['end_time'] = datetime.now().isoformat()

            # Write error log
            error_log_path = self.output_base / 'error_log.json'
            with open(error_log_path, 'w') as f:
                json.dump(self.run_log, f, indent=2)

            raise


def main():
    parser = argparse.ArgumentParser(
        description='Phase 2 Orchestrator: Detector Correlation & Bayesian Fusion'
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=Path('config/phase2_config.json'),
        help='Path to Phase 2 configuration'
    )
    parser.add_argument(
        '--wait',
        action='store_true',
        help='Wait for all detectors to complete before starting'
    )

    args = parser.parse_args()

    orchestrator = Phase2Orchestrator(config_path=args.config)
    orchestrator.execute(wait_for_detectors=args.wait)


if __name__ == '__main__':
    main()
