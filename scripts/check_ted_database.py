#!/usr/bin/env python3
"""Quick check of TED database contents"""

import sqlite3

db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

with sqlite3.connect(db_path) as conn:
    cur = conn.cursor()

    # Total counts
    cur.execute("SELECT COUNT(*) FROM ted_contracts_production")
    total = cur.fetchone()[0]
    print(f"Total TED contracts: {total:,}")

    # By year
    cur.execute("""
        SELECT
            strftime('%Y', publication_date) as year,
            COUNT(*) as count
        FROM ted_contracts_production
        GROUP BY year
        ORDER BY year
    """)

    print("\nBy year:")
    for year, count in cur.fetchall():
        if year:
            print(f"  {year}: {count:,}")

    # Check for legacy (pre-2023)
    cur.execute("SELECT COUNT(*) FROM ted_contracts_production WHERE publication_date < '2023-01-01'")
    legacy_count = cur.fetchone()[0]
    print(f"\nLegacy (pre-2023): {legacy_count:,}")
