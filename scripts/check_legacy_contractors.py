#!/usr/bin/env python3
"""Check legacy TED contractor extraction quality"""

import sqlite3
import json

db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

with sqlite3.connect(db_path) as conn:
    cur = conn.cursor()

    # Total legacy contracts
    cur.execute("SELECT COUNT(*) FROM ted_contracts_production WHERE publication_date < '2023-01-01'")
    total_legacy = cur.fetchone()[0]
    print(f"Total legacy contracts (pre-2023): {total_legacy:,}")

    # With contractor names
    cur.execute("""
        SELECT COUNT(*)
        FROM ted_contracts_production
        WHERE publication_date < '2023-01-01'
        AND contractor_name IS NOT NULL
        AND contractor_name != ''
    """)
    with_contractors = cur.fetchone()[0]
    print(f"With contractor names: {with_contractors:,} ({100*with_contractors/total_legacy:.1f}%)")

    # Chinese detected
    cur.execute("""
        SELECT COUNT(*)
        FROM ted_contracts_production
        WHERE publication_date < '2023-01-01'
        AND is_chinese_related = 1
    """)
    chinese = cur.fetchone()[0]
    print(f"Chinese detected: {chinese}")

    # Sample contractors
    cur.execute("""
        SELECT contractor_name, contractor_country, publication_date
        FROM ted_contracts_production
        WHERE publication_date < '2023-01-01'
        AND contractor_name IS NOT NULL
        LIMIT 10
    """)

    print("\nSample contractors:")
    for name, country, date in cur.fetchall():
        print(f"  {name[:50]:50} | {country or 'N/A':3} | {date or 'N/A'}")

    # Check publication_date NULL rate
    cur.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN publication_date IS NULL THEN 1 ELSE 0 END) as null_dates
        FROM ted_contracts_production
        WHERE publication_date < '2023-01-01' OR publication_date IS NULL
    """)
    total, null_dates = cur.fetchone()
    print(f"\nPublication date status:")
    print(f"  Total legacy records: {total:,}")
    print(f"  NULL dates: {null_dates:,} ({100*null_dates/total:.1f}%)")
