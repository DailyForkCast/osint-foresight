#!/usr/bin/env python3
"""
DATABASE AUDIT SCRIPT - Trust Nothing Approach
Verifies all claims about osint_master.db
"""

import sqlite3
import sys
from pathlib import Path

def audit_database(db_path):
    """Comprehensive database audit"""

    results = {
        "success": False,
        "errors": [],
        "findings": {}
    }

    try:
        # Convert to Windows path if needed
        if not Path(db_path).exists():
            # Try F: drive path
            db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
            if not Path(db_path).exists():
                results["errors"].append(f"Database not found at {db_path}")
                return results

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get table count
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        # Get total record count and table sizes
        total_records = 0
        table_sizes = []
        empty_tables = []
        failed_tables = []

        for table in tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                count = cursor.fetchone()[0]
                total_records += count
                if count > 0:
                    table_sizes.append((table, count))
                else:
                    empty_tables.append(table)
            except Exception as e:
                failed_tables.append((table, str(e)))

        # Sort by size descending
        table_sizes.sort(key=lambda x: x[1], reverse=True)

        # Store findings
        results["findings"] = {
            "table_count": {
                "claimed": 137,
                "actual": table_count,
                "match": table_count == 137
            },
            "record_count": {
                "claimed": "16.8M",
                "actual": total_records,
                "actual_formatted": f"{total_records:,}",
                "match": 16_000_000 <= total_records <= 17_000_000
            },
            "top_15_tables": table_sizes[:15],
            "empty_tables_count": len(empty_tables),
            "empty_tables": empty_tables[:20],  # First 20
            "failed_tables_count": len(failed_tables),
            "failed_tables": failed_tables[:10],  # First 10
            "all_table_names": tables
        }

        results["success"] = True
        conn.close()

    except Exception as e:
        results["errors"].append(f"Audit failed: {str(e)}")

    return results


def print_audit_results(results):
    """Pretty print audit results"""

    if not results["success"]:
        print("=== DATABASE AUDIT FAILED ===")
        for error in results["errors"]:
            print(f"ERROR: {error}")
        return

    f = results["findings"]

    print("=" * 80)
    print("DATABASE AUDIT RESULTS - osint_master.db")
    print("=" * 80)
    print()

    # Table count
    print("TABLE COUNT:")
    print(f"  Claimed: {f['table_count']['claimed']}")
    print(f"  Actual:  {f['table_count']['actual']}")
    print(f"  Status:  {'MATCH' if f['table_count']['match'] else 'MISMATCH'}")
    print()

    # Record count
    print("RECORD COUNT:")
    print(f"  Claimed: {f['record_count']['claimed']}")
    print(f"  Actual:  {f['record_count']['actual_formatted']}")
    print(f"  Status:  {'MATCH' if f['record_count']['match'] else 'MISMATCH'}")
    print()

    # Top tables
    print("TOP 15 TABLES BY SIZE:")
    for table, count in f['top_15_tables']:
        print(f"  {table:50} {count:>15,} rows")
    print()

    # Empty tables
    print(f"EMPTY TABLES: {f['empty_tables_count']}")
    if f['empty_tables']:
        for table in f['empty_tables']:
            print(f"  - {table}")
    print()

    # Failed tables
    if f['failed_tables_count'] > 0:
        print(f"FAILED TO QUERY: {f['failed_tables_count']}")
        for table, error in f['failed_tables']:
            print(f"  - {table}: {error}")
        print()


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "F:/OSINT_WAREHOUSE/osint_master.db"

    results = audit_database(db_path)
    print_audit_results(results)

    # Also save JSON
    import json
    with open("analysis/DATABASE_AUDIT_RESULTS.json", "w") as f:
        json.dump(results, f, indent=2)

    print()
    print("Full results saved to: analysis/DATABASE_AUDIT_RESULTS.json")
