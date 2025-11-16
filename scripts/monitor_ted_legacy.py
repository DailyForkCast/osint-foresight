#!/usr/bin/env python3
"""
Monitor TED Legacy Processing Progress
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
stats_file = Path("C:/Projects/OSINT - Foresight/data/ted_legacy_processing_stats.json")

print("="*80)
print("TED LEGACY PROCESSING MONITOR")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# Check database
try:
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        # Total contracts by year
        cur.execute("""
            SELECT
                CAST(strftime('%Y', publication_date) AS INTEGER) as year,
                COUNT(*) as contracts,
                SUM(CASE WHEN is_chinese_related = 1 THEN 1 ELSE 0 END) as chinese
            FROM ted_contracts_production
            WHERE year BETWEEN 2006 AND 2022
            GROUP BY year
            ORDER BY year
        """)

        print("\nContracts by Year:")
        print("-" * 40)
        total_contracts = 0
        total_chinese = 0
        for year, contracts, chinese in cur.fetchall():
            print(f"{year}: {contracts:>8,} contracts, {chinese:>4} Chinese")
            total_contracts += contracts
            total_chinese += chinese

        print("-" * 40)
        print(f"Total: {total_contracts:>7,} contracts, {total_chinese:>4} Chinese")

except Exception as e:
    print(f"Database error: {e}")

# Check stats file
print("\n" + "="*80)
if stats_file.exists():
    with open(stats_file) as f:
        stats = json.load(f)
    print("Processing Stats:")
    print(f"  Archives processed: {stats['archives_processed']}/204")
    print(f"  Contracts: {stats['total_contracts']:,}")
    print(f"  Chinese: {stats['total_chinese']}")
    print(f"  Errors: {stats['total_errors']}")
else:
    print("Stats file not yet created - processing may still be starting")

print("="*80)
