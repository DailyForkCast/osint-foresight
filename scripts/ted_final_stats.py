#!/usr/bin/env python3
"""
Generate final TED processing statistics
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
CHECKPOINT_PATH = "C:/Projects/OSINT - Foresight/data/ted_production_checkpoint.json"

def generate_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("="*80)
    print("TED FINAL PROCESSING STATISTICS")
    print("="*80)

    # Total contracts
    cur.execute("SELECT COUNT(*) FROM ted_contracts_production")
    total = cur.fetchone()[0]
    print(f"\nTotal contracts in database: {total:,}")

    # Date range
    cur.execute("SELECT MIN(publication_date), MAX(publication_date) FROM ted_contracts_production")
    min_date, max_date = cur.fetchone()
    print(f"Date range: {min_date} to {max_date}")

    # China-related contracts
    cur.execute("SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1")
    china_total = cur.fetchone()[0]
    print(f"\nChina-related contracts: {china_total}")
    print(f"Percentage: {(china_total/total*100):.4f}%")

    # By source archive
    print("\nContracts by year:")
    cur.execute("""
        SELECT
            SUBSTR(source_archive, 13, 4) as year,
            COUNT(*) as contracts,
            SUM(CASE WHEN is_chinese_related = 1 THEN 1 ELSE 0 END) as china_contracts
        FROM ted_contracts_production
        WHERE source_archive LIKE 'TED_monthly_%'
        GROUP BY year
        ORDER BY year
    """)

    for row in cur.fetchall():
        year, contracts, china = row
        print(f"  {year}: {contracts:,} contracts ({china} China-related)")

    # Chinese companies mentioned
    print("\nChinese companies mentioned:")
    cur.execute("""
        SELECT chinese_indicators
        FROM ted_contracts_production
        WHERE is_chinese_related = 1 AND chinese_indicators IS NOT NULL
    """)

    company_counts = {}
    for row in cur.fetchall():
        indicators = json.loads(row[0])
        if 'companies' in indicators:
            for company in indicators['companies']:
                company_counts[company] = company_counts.get(company, 0) + 1

    for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {company.title()}: {count}")

    # Load checkpoint
    if Path(CHECKPOINT_PATH).exists():
        with open(CHECKPOINT_PATH) as f:
            checkpoint = json.load(f)

        print(f"\n{'='*80}")
        print("PROCESSING STATUS")
        print(f"{'='*80}")
        print(f"Archives processed: {checkpoint['stats']['archives_processed']}/139")
        print(f"XML files processed: {checkpoint['stats']['xml_files_processed']:,}")
        print(f"Processing errors: {len(checkpoint['stats']['errors'])}")

        if checkpoint['stats']['errors']:
            print("\nFailed archives:")
            for error in checkpoint['stats']['errors']:
                print(f"  {error}")

    conn.close()

if __name__ == '__main__':
    generate_stats()
