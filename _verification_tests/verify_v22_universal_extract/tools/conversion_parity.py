#!/usr/bin/env python3
"""
conversion_parity.py - Format Conversion Validation Tool
Part of Universal Extraction Success Contract v2.2

Validates that format conversions preserve data integrity.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ConversionParityChecker:
    """Conversion Parity Checker for MRP validation"""

    def __init__(self, src_path: str, dst_path: str, src_format: str, dst_format: str):
        self.src_path = Path(src_path)
        self.dst_path = Path(dst_path)
        self.src_format = src_format.lower()
        self.dst_format = dst_format.lower()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "status": "UNKNOWN",
            "source": str(self.src_path),
            "destination": str(self.dst_path),
            "src_format": src_format,
            "dst_format": dst_format,
            "checks": {},
            "metrics": {},
            "failures": []
        }

    def run(self) -> Dict:
        """Execute conversion parity checks"""
        # Check if source exists
        if not self.src_path.exists():
            self.results["status"] = "FAIL"
            self.results["failures"].append({
                "code": "ERROR_SOURCE_NOT_FOUND",
                "message": f"Source file not found: {self.src_path}"
            })
            return self.results

        # Check if destination exists
        if not self.dst_path.exists():
            self.results["status"] = "FAIL"
            self.results["failures"].append({
                "code": "ERROR_EMPTY_CONVERSION",
                "message": f"Destination file not found: {self.dst_path}"
            })
            return self.results

        # Check for empty destination
        if self.dst_path.stat().st_size == 0:
            self.results["status"] = "FAIL"
            self.results["failures"].append({
                "code": "ERROR_EMPTY_CONVERSION",
                "message": "Destination file is empty (0 bytes)"
            })
            return self.results

        # Get file sizes
        src_size = self.src_path.stat().st_size
        dst_size = self.dst_path.stat().st_size

        self.results["metrics"]["src_size"] = src_size
        self.results["metrics"]["dst_size"] = dst_size
        self.results["metrics"]["size_ratio"] = dst_size / src_size if src_size > 0 else 0

        # Check based on conversion type
        if self.src_format == "json" and self.dst_format == "parquet":
            success = self._check_json_to_parquet()
        elif self.src_format == "csv" and self.dst_format == "parquet":
            success = self._check_csv_to_parquet()
        elif self.src_format == "xml" and self.dst_format == "json":
            success = self._check_xml_to_json()
        elif self.src_format == "json" and self.dst_format == "csv":
            success = self._check_json_to_csv()
        else:
            # Generic size-based check
            success = self._check_generic_conversion()

        # Set overall status
        if not self.results["failures"]:
            self.results["status"] = "PASS"
        else:
            self.results["status"] = "FAIL"

        return self.results

    def _check_json_to_parquet(self) -> bool:
        """Check JSON to Parquet conversion"""
        try:
            # Count records in JSON
            with open(self.src_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    src_records = len(data)
                else:
                    src_records = 1

            self.results["metrics"]["src_records"] = src_records

            # For Parquet, we'd need pyarrow or pandas
            # Simple check: parquet files are typically smaller than JSON
            if self.results["metrics"]["dst_size"] > 0:
                self.results["checks"]["conversion_complete"] = True

                # Parquet should be smaller than JSON (usually 20-80% of original)
                if 0.1 < self.results["metrics"]["size_ratio"] < 1.2:
                    self.results["checks"]["size_reasonable"] = True
                else:
                    self.results["checks"]["size_reasonable"] = False
                    self.results["failures"].append({
                        "code": "WARN_SIZE_UNEXPECTED",
                        "message": f"Unusual size ratio: {self.results['metrics']['size_ratio']:.2f}"
                    })
                return True
            else:
                self.results["checks"]["conversion_complete"] = False
                self.results["failures"].append({
                    "code": "ERROR_EMPTY_CONVERSION",
                    "message": "Parquet file has no content"
                })
                return False

        except Exception as e:
            self.results["failures"].append({
                "code": "ERROR_CONVERSION_CHECK",
                "message": f"Error checking conversion: {str(e)}"
            })
            return False

    def _check_csv_to_parquet(self) -> bool:
        """Check CSV to Parquet conversion"""
        try:
            # Count lines in CSV
            with open(self.src_path, 'r', encoding='utf-8') as f:
                src_lines = sum(1 for _ in f)

            self.results["metrics"]["src_lines"] = src_lines

            if self.results["metrics"]["dst_size"] > 0:
                self.results["checks"]["conversion_complete"] = True
                return True
            else:
                self.results["checks"]["conversion_complete"] = False
                self.results["failures"].append({
                    "code": "ERROR_EMPTY_CONVERSION",
                    "message": "Parquet file has no content"
                })
                return False

        except Exception as e:
            self.results["failures"].append({
                "code": "ERROR_CONVERSION_CHECK",
                "message": f"Error checking conversion: {str(e)}"
            })
            return False

    def _check_xml_to_json(self) -> bool:
        """Check XML to JSON conversion"""
        try:
            # Check JSON validity
            with open(self.dst_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.results["checks"]["json_valid"] = True

            if isinstance(data, (dict, list)) and data:
                self.results["checks"]["conversion_complete"] = True
                return True
            else:
                self.results["checks"]["conversion_complete"] = False
                self.results["failures"].append({
                    "code": "ERROR_EMPTY_CONVERSION",
                    "message": "JSON file has no content"
                })
                return False

        except json.JSONDecodeError as e:
            self.results["checks"]["json_valid"] = False
            self.results["failures"].append({
                "code": "ERROR_INVALID_JSON",
                "message": f"Invalid JSON in destination: {str(e)}"
            })
            return False

    def _check_json_to_csv(self) -> bool:
        """Check JSON to CSV conversion"""
        try:
            # Count records in JSON
            with open(self.src_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    src_records = len(data)
                else:
                    src_records = 1

            # Count lines in CSV (minus header)
            with open(self.dst_path, 'r', encoding='utf-8') as f:
                dst_lines = sum(1 for _ in f) - 1  # Subtract header

            self.results["metrics"]["src_records"] = src_records
            self.results["metrics"]["dst_lines"] = dst_lines

            # Check parity
            if abs(src_records - dst_lines) <= 1:  # Allow 1 record difference
                self.results["checks"]["record_parity"] = True
                self.results["checks"]["conversion_complete"] = True
                return True
            else:
                self.results["checks"]["record_parity"] = False
                self.results["failures"].append({
                    "code": "ERROR_RECORD_MISMATCH",
                    "message": f"Record count mismatch: {src_records} JSON records vs {dst_lines} CSV lines"
                })
                return False

        except Exception as e:
            self.results["failures"].append({
                "code": "ERROR_CONVERSION_CHECK",
                "message": f"Error checking conversion: {str(e)}"
            })
            return False

    def _check_generic_conversion(self) -> bool:
        """Generic conversion check based on size"""
        if self.results["metrics"]["dst_size"] > 0:
            self.results["checks"]["conversion_complete"] = True

            # Check for reasonable size relationship
            if 0.01 < self.results["metrics"]["size_ratio"] < 100:
                self.results["checks"]["size_reasonable"] = True
                return True
            else:
                self.results["checks"]["size_reasonable"] = False
                self.results["failures"].append({
                    "code": "WARN_SIZE_UNEXPECTED",
                    "message": f"Unusual size ratio: {self.results['metrics']['size_ratio']:.2f}"
                })
                return True
        else:
            self.results["checks"]["conversion_complete"] = False
            self.results["failures"].append({
                "code": "ERROR_EMPTY_CONVERSION",
                "message": "Destination file is empty"
            })
            return False

    def save_results(self, output_path: Optional[str] = None):
        """Save results to JSON file"""
        if not output_path:
            output_path = "conversion_parity_results.json"

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)

    def print_summary(self):
        """Print human-readable summary"""
        print(f"\n{'='*60}")
        print(f"Conversion Parity Check Results - {self.results['status']}")
        print(f"{'='*60}")

        print(f"\nConversion: {self.src_format} -> {self.dst_format}")
        print(f"Source: {self.results['source']}")
        print(f"Destination: {self.results['destination']}")

        if "metrics" in self.results:
            print("\nMetrics:")
            for key, value in self.results["metrics"].items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")

        if "checks" in self.results:
            print("\nChecks:")
            for check, result in self.results["checks"].items():
                status = "[OK]" if result else "[FAIL]"
                print(f"  {status} {check}: {result}")

        if self.results["failures"]:
            print("\nFailures:")
            for failure in self.results["failures"]:
                print(f"  - [{failure['code']}] {failure['message']}")

def main():
    parser = argparse.ArgumentParser(description="Conversion Parity Check for MRP validation")
    parser.add_argument("--src", required=True, help="Source file path")
    parser.add_argument("--dst", required=True, help="Destination file path")
    parser.add_argument("--src-format", required=True, help="Source format (json, csv, xml)")
    parser.add_argument("--dst-format", required=True, help="Destination format (parquet, json, csv)")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    checker = ConversionParityChecker(args.src, args.dst, args.src_format, args.dst_format)
    results = checker.run()

    if args.output:
        checker.save_results(args.output)

    if args.verbose:
        checker.print_summary()
    else:
        print(f"Conversion Parity Check: {results['status']}")

    # Exit with appropriate code
    if results["status"] == "FAIL":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
