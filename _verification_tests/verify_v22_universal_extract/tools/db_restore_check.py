#!/usr/bin/env python3
"""
db_restore_check.py - Database Restore Validation Tool
Part of Universal Extraction Success Contract v2.2

Validates that database restores produce non-empty tables with data.
"""

import os
import sys
import json
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class DBRestoreChecker:
    """Database Restore Checker for MRP validation"""

    def __init__(self, db_path: str, min_tables: int = 1, min_rows: int = 1):
        self.db_path = Path(db_path)
        self.min_tables = min_tables
        self.min_rows = min_rows
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "status": "UNKNOWN",
            "database": str(self.db_path),
            "checks": {},
            "metrics": {},
            "failures": []
        }

    def run(self) -> Dict:
        """Execute database validation checks"""
        if not self.db_path.exists():
            self.results["status"] = "FAIL"
            self.results["failures"].append({
                "code": "ERROR_DB_NOT_FOUND",
                "message": f"Database file not found: {self.db_path}"
            })
            return self.results

        if self.db_path.stat().st_size == 0:
            self.results["status"] = "FAIL"
            self.results["failures"].append({
                "code": "ERROR_EMPTY_DB_RESTORE",
                "message": "Database file is empty (0 bytes)"
            })
            return self.results

        try:
            # Connect to database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Get table list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            self.results["metrics"]["table_count"] = len(tables)
            self.results["metrics"]["tables"] = tables

            # Check minimum tables requirement
            if len(tables) < self.min_tables:
                self.results["status"] = "FAIL"
                self.results["failures"].append({
                    "code": "ERROR_EMPTY_DB_RESTORE",
                    "message": f"Database has {len(tables)} tables, minimum {self.min_tables} required"
                })
                self.results["checks"]["min_tables"] = False
            else:
                self.results["checks"]["min_tables"] = True

            # Check row counts
            total_rows = 0
            table_rows = {}

            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_rows[table] = count
                    total_rows += count
                except Exception as e:
                    table_rows[table] = f"Error: {str(e)}"

            self.results["metrics"]["total_rows"] = total_rows
            self.results["metrics"]["table_rows"] = table_rows

            # Check minimum rows requirement
            if total_rows < self.min_rows:
                self.results["status"] = "FAIL"
                self.results["failures"].append({
                    "code": "ERROR_EMPTY_DB_RESTORE",
                    "message": f"Database has {total_rows} total rows, minimum {self.min_rows} required"
                })
                self.results["checks"]["min_rows"] = False
            else:
                self.results["checks"]["min_rows"] = True

            # Get sample schema info
            if tables:
                sample_table = tables[0]
                cursor.execute(f"PRAGMA table_info({sample_table})")
                columns = cursor.fetchall()
                self.results["metrics"]["sample_schema"] = {
                    "table": sample_table,
                    "columns": [{"name": col[1], "type": col[2]} for col in columns]
                }

            conn.close()

            # Set overall status
            if not self.results["failures"]:
                self.results["status"] = "PASS"

        except sqlite3.Error as e:
            self.results["status"] = "FAIL"
            self.results["failures"].append({
                "code": "ERROR_DB_INVALID",
                "message": f"Database error: {str(e)}"
            })

        return self.results

    def save_results(self, output_path: Optional[str] = None):
        """Save results to JSON file"""
        if not output_path:
            output_path = "db_restore_results.json"

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)

    def print_summary(self):
        """Print human-readable summary"""
        print(f"\n{'='*60}")
        print(f"DB Restore Check Results - {self.results['status']}")
        print(f"{'='*60}")

        print(f"\nDatabase: {self.results['database']}")

        if "metrics" in self.results:
            print("\nMetrics:")
            for key, value in self.results["metrics"].items():
                if key != "table_rows" and key != "sample_schema":
                    print(f"  {key}: {value}")

            if "table_rows" in self.results["metrics"]:
                print("\nTable Row Counts:")
                for table, count in self.results["metrics"]["table_rows"].items():
                    print(f"  {table}: {count}")

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
    parser = argparse.ArgumentParser(description="Database Restore Check for MRP validation")
    parser.add_argument("--db", required=True, help="Path to database file")
    parser.add_argument("--min-tables", type=int, default=1, help="Minimum number of tables")
    parser.add_argument("--min-rows", type=int, default=1, help="Minimum total rows")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    checker = DBRestoreChecker(args.db, args.min_tables, args.min_rows)
    results = checker.run()

    if args.output:
        checker.save_results(args.output)

    if args.verbose:
        checker.print_summary()
    else:
        print(f"DB Restore Check: {results['status']}")

    # Exit with appropriate code
    if results["status"] == "FAIL":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
