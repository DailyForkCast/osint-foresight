#!/usr/bin/env python3
"""
Monitor decompression and run all phases in order
Automatically executes Phase 1-6 once decompression completes
"""

import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
import sys

class PhaseOrchestrator:
    def __init__(self):
        self.decompressed_root = Path("F:/DECOMPRESSED_DATA")
        self.stats_file = Path("C:/Projects/OSINT - Foresight/decompression_to_f_stats.json")
        self.phase_results = {}

    def check_decompression_status(self):
        """Check if decompression is complete"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)

            if 'completed' in stats:
                print(f"Decompression COMPLETE at {stats['completed']}")
                print(f"Files created: {stats['files_created']:,}")
                print(f"Total size: {stats['total_decompressed_bytes'] / 1e9:.2f} GB")
                return True
            else:
                print(f"Decompression IN PROGRESS...")
                print(f"Files so far: {stats.get('files_created', 0):,}")
                return False
        else:
            print("No decompression stats file found")
            return False

    def wait_for_decompression(self, check_interval=300):
        """Wait for decompression to complete"""
        print("\n" + "="*70)
        print("WAITING FOR DECOMPRESSION TO COMPLETE")
        print("="*70)
        print(f"Checking every {check_interval} seconds...\n")

        while True:
            if self.check_decompression_status():
                print("\n[SUCCESS] Decompression complete! Starting phases...")
                return True

            print(f"Waiting {check_interval} seconds before next check...")
            time.sleep(check_interval)

    def run_phase(self, phase_num, script_name, description):
        """Run a single phase"""
        print("\n" + "="*70)
        print(f"PHASE {phase_num}: {description}")
        print("="*70)

        script_path = Path(f"C:/Projects/OSINT - Foresight/scripts/{script_name}")

        if not script_path.exists():
            print(f"Script not found: {script_path}")
            return False

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            if result.returncode == 0:
                print(f"[SUCCESS] Phase {phase_num} completed successfully")
                self.phase_results[f"phase_{phase_num}"] = {
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                }
                return True
            else:
                print(f"[FAILED] Phase {phase_num} failed with code {result.returncode}")
                print(f"Error: {result.stderr[:500]}")
                self.phase_results[f"phase_{phase_num}"] = {
                    'status': 'failed',
                    'error': result.stderr[:500],
                    'timestamp': datetime.now().isoformat()
                }
                return False

        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] Phase {phase_num} timed out")
            self.phase_results[f"phase_{phase_num}"] = {
                'status': 'timeout',
                'timestamp': datetime.now().isoformat()
            }
            return False
        except Exception as e:
            print(f"[ERROR] Error running Phase {phase_num}: {e}")
            self.phase_results[f"phase_{phase_num}"] = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False

    def run_all_phases(self):
        """Run all phases in order"""
        phases = [
            (1, "phase1_complete_profiling.py", "Complete Content Profiling"),
            (2, "phase2_schema_harmonization.py", "Schema Harmonization"),
            (3, "phase3_signal_verification.py", "China Signal Verification"),
            (4, "phase4_integration_complete.py", "Progressive Integration"),
            (5, "phase5_entity_resolution.py", "Entity Resolution"),
            (6, "phase6_monitoring_validation.py", "Monitoring Validation")
        ]

        print("\n" + "="*70)
        print("RUNNING ALL PHASES IN ORDER")
        print("="*70)

        for phase_num, script_name, description in phases:
            if not self.run_phase(phase_num, script_name, description):
                print(f"\n[WARNING] Stopping at Phase {phase_num} due to failure")
                break

        # Save results
        with open("C:/Projects/OSINT - Foresight/phase_execution_results.json", 'w') as f:
            json.dump(self.phase_results, f, indent=2)

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate execution summary"""
        print("\n" + "="*70)
        print("EXECUTION SUMMARY")
        print("="*70)

        for phase, result in self.phase_results.items():
            status_icon = "[OK]" if result['status'] == 'success' else "[FAIL]"
            print(f"{status_icon} {phase}: {result['status']}")

        # Count successes
        successes = sum(1 for r in self.phase_results.values() if r['status'] == 'success')
        total = len(self.phase_results)

        print(f"\nCompleted: {successes}/{total} phases")

        # Generate report
        report = "# Phase Execution Report\n\n"
        report += f"Generated: {datetime.now().isoformat()}\n\n"

        report += "## Results\n\n"
        for phase, result in self.phase_results.items():
            report += f"- **{phase}**: {result['status']}\n"
            if 'error' in result:
                report += f"  - Error: {result['error'][:200]}\n"

        report += f"\n## Summary\n\n"
        report += f"- Phases completed: {successes}/{total}\n"
        report += f"- Success rate: {successes/total*100:.1f}%\n"

        with open("C:/Projects/OSINT - Foresight/phase_execution_report.md", 'w') as f:
            f.write(report)

        print(f"\nReport saved: phase_execution_report.md")

    def run(self, wait_for_completion=True):
        """Main orchestration logic"""
        print("\n" + "="*70)
        print("PHASE ORCHESTRATOR")
        print("="*70)

        # Check decompression status
        if wait_for_completion:
            if not self.check_decompression_status():
                self.wait_for_decompression()
        else:
            print("Skipping decompression wait (assuming complete)")

        # Verify decompressed data exists
        if not self.decompressed_root.exists():
            print(f"[ERROR] Decompressed data not found at {self.decompressed_root}")
            return 1

        file_count = sum(1 for _ in self.decompressed_root.rglob('*') if _.is_file())
        print(f"\nFound {file_count:,} decompressed files")

        if file_count == 0:
            print("[ERROR] No files found in decompressed directory")
            return 1

        # Run all phases
        self.run_all_phases()

        return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Monitor and run all phases')
    parser.add_argument('--no-wait', action='store_true',
                        help='Skip waiting for decompression')
    parser.add_argument('--check-interval', type=int, default=300,
                        help='Seconds between decompression checks')

    args = parser.parse_args()

    orchestrator = PhaseOrchestrator()
    sys.exit(orchestrator.run(wait_for_completion=not args.no_wait))
