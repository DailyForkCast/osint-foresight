#!/usr/bin/env python3
"""
fs_delta_check.py - File System Delta Check Tool
Part of Universal Extraction Success Contract v2.2

Validates Non-Empty Output (NEO) contract requirements:
- If dirs created, then files must be created with bytes added
- Zero-byte burst guard (max 1 zero-byte file)
- NOOP allowance with evidence
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class FSState:
    """Represents a file system state snapshot"""
    def __init__(self, root: Path):
        self.root = Path(root)
        self.files = {}
        self.dirs = set()
        self.total_bytes = 0
        self.zero_byte_files = []

    def snapshot(self):
        """Take a snapshot of the file system state"""
        if not self.root.exists():
            return

        for item in self.root.rglob("*"):
            if item.is_file():
                size = item.stat().st_size
                self.files[str(item.relative_to(self.root))] = {
                    "size": size,
                    "mtime": item.stat().st_mtime,
                    "hash": self._quick_hash(item) if size < 1024*1024 else None
                }
                self.total_bytes += size
                if size == 0:
                    self.zero_byte_files.append(str(item.relative_to(self.root)))
            elif item.is_dir():
                self.dirs.add(str(item.relative_to(self.root)))

    def _quick_hash(self, filepath: Path) -> str:
        """Quick hash for small files"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None

class FSDeltaChecker:
    """File System Delta Checker for NEO validation"""

    def __init__(self, before_path: str, after_path: str):
        self.before_path = Path(before_path) if before_path else None
        self.after_path = Path(after_path)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "status": "UNKNOWN",
            "checks": {},
            "metrics": {},
            "failures": []
        }

    def run(self) -> Dict:
        """Execute all NEO checks"""
        # Take snapshots
        before = FSState(self.before_path) if self.before_path and self.before_path.exists() else FSState(self.after_path)
        after = FSState(self.after_path)

        if self.before_path and self.before_path.exists():
            before.snapshot()
        after.snapshot()

        # Calculate deltas
        self.results["metrics"] = {
            "created_dirs": len(after.dirs - before.dirs),
            "created_files": len(set(after.files.keys()) - set(before.files.keys())),
            "deleted_files": len(set(before.files.keys()) - set(after.files.keys())),
            "bytes_added": after.total_bytes - before.total_bytes,
            "zero_byte_files": len(after.zero_byte_files),
            "new_zero_byte_files": len(set(after.zero_byte_files) - set(before.zero_byte_files))
        }

        # Run NEO checks
        self._check_non_empty_output()
        self._check_zero_byte_burst()
        self._check_noop_allowance()

        # Determine overall status
        if self.results["failures"]:
            self.results["status"] = "FAIL"
        elif self.results["checks"].get("noop_detected"):
            self.results["status"] = "NOOP"
        else:
            self.results["status"] = "PASS"

        return self.results

    def _check_non_empty_output(self):
        """Check NEO requirement: if dirs created, files and bytes must be added"""
        metrics = self.results["metrics"]

        if metrics["created_dirs"] > 0:
            if metrics["created_files"] == 0:
                self.results["failures"].append({
                    "code": "ERROR_EMPTY_EXTRACTION",
                    "message": f"Created {metrics['created_dirs']} directories but no files"
                })
                self.results["checks"]["non_empty_output"] = False
            elif metrics["bytes_added"] <= 0:
                self.results["failures"].append({
                    "code": "ERROR_EMPTY_EXTRACTION",
                    "message": f"Created {metrics['created_dirs']} directories and {metrics['created_files']} files but no bytes added"
                })
                self.results["checks"]["non_empty_output"] = False
            else:
                self.results["checks"]["non_empty_output"] = True
        else:
            # No directories created - could be valid NOOP
            self.results["checks"]["non_empty_output"] = True

    def _check_zero_byte_burst(self):
        """Check zero-byte burst guard: max 1 zero-byte file allowed"""
        metrics = self.results["metrics"]

        if metrics["new_zero_byte_files"] > 1:
            self.results["failures"].append({
                "code": "FAIL_ZERO_BYTE_BURST",
                "message": f"Created {metrics['new_zero_byte_files']} zero-byte files (max 1 allowed)"
            })
            self.results["checks"]["zero_byte_guard"] = False
        else:
            self.results["checks"]["zero_byte_guard"] = True

    def _check_noop_allowance(self):
        """Check for legitimate NOOP scenario"""
        metrics = self.results["metrics"]

        is_noop = (
            metrics["created_dirs"] == 0 and
            metrics["created_files"] == 0 and
            metrics["bytes_added"] == 0
        )

        self.results["checks"]["noop_detected"] = is_noop

        if is_noop:
            # Look for NOOP evidence in logs (would need log path parameter)
            self.results["checks"]["noop_evidence"] = self._find_noop_evidence()

    def _find_noop_evidence(self) -> bool:
        """Look for NOOP evidence in output"""
        # Check for .noop marker file or similar
        noop_markers = [
            self.after_path / ".noop",
            self.after_path / "NOOP",
            self.after_path / ".unchanged"
        ]

        for marker in noop_markers:
            if marker.exists():
                return True

        return False

    def save_results(self, output_path: Optional[str] = None):
        """Save results to JSON file"""
        if not output_path:
            output_path = "fs_delta_results.json"

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)

    def print_summary(self):
        """Print human-readable summary"""
        print(f"\n{'='*60}")
        print(f"FS Delta Check Results - {self.results['status']}")
        print(f"{'='*60}")

        print("\nMetrics:")
        for key, value in self.results["metrics"].items():
            print(f"  {key}: {value}")

        print("\nChecks:")
        for check, result in self.results["checks"].items():
            status = "[OK]" if result else "[FAIL]"
            print(f"  {status} {check}: {result}")

        if self.results["failures"]:
            print("\nFailures:")
            for failure in self.results["failures"]:
                print(f"  - [{failure['code']}] {failure['message']}")

def main():
    parser = argparse.ArgumentParser(description="File System Delta Check for NEO validation")
    parser.add_argument("--before", help="Path to before snapshot (optional)")
    parser.add_argument("--after", required=True, help="Path to after state")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    checker = FSDeltaChecker(args.before, args.after)
    results = checker.run()

    if args.output:
        checker.save_results(args.output)

    if args.verbose:
        checker.print_summary()

    # Exit with appropriate code
    if results["status"] == "FAIL":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
