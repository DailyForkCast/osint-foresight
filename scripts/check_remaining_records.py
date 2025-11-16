#!/usr/bin/env python3
"""Check what records remain in database"""

import sqlite3

db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

with sqlite3.connect(db_path) as conn:
    cur = conn.cursor()

    # Total count
    cur.execute("SELECT COUNT(*) FROM ted_contracts_production")
    total = cur.fetchone()[0]
    print(f"Total records: {total:,}")

    # By publication date ranges
    cur.execute("""
        SELECT
            CASE
                WHEN publication_date IS NULL THEN 'NULL'
                WHEN publication_date < '2023-01-01' THEN 'Pre-2023'
                ELSE '2023+'
            END as date_range,
            COUNT(*) as count
        FROM ted_contracts_production
        GROUP BY date_range
        ORDER BY date_range
    """)

    print("\nBy date range:")
    for date_range, count in cur.fetchall():
        print(f"  {date_range}: {count:,}")

    # Sample document IDs with NULL dates
    cur.execute("""
        SELECT document_id, source_archive, publication_date
        FROM ted_contracts_production
        WHERE publication_date IS NULL OR publication_date < '2023-01-01'
        LIMIT 10
    """)

    print("\nSample legacy/NULL records:")
    for doc_id, archive, pub_date in cur.fetchall():
        print(f"  {doc_id[:16]} | {archive[:30]:30} | {pub_date or 'NULL'}")
