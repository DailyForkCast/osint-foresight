#!/usr/bin/env python3
"""Quick schema check for sampling"""

import sqlite3

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
conn = sqlite3.connect(DB_PATH)

tables = [
    'usaspending_china_305',
    'ted_contracts_production',
    'uspto_patents_chinese',
    'openalex_works'
]

for table in tables:
    try:
        cursor = conn.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"\n{table}:")
        print(f"  Columns: {', '.join(columns[:10])}")  # First 10
        if len(columns) > 10:
            print(f"  ... and {len(columns) - 10} more")
    except:
        print(f"\n{table}: NOT FOUND")

conn.close()
