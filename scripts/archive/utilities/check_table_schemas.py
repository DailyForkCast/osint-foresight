#!/usr/bin/env python3
import sqlite3
from pathlib import Path

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(db_path))

tables = ['usaspending_china_101', 'usaspending_china_305', 'usaspending_china_comprehensive']

for table in tables:
    print(f"\n{'='*80}")
    print(f"TABLE: {table}")
    print(f"{'='*80}")

    # Get schema
    cursor = conn.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()

    print("\nColumns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

    # Get sample row
    cursor = conn.execute(f"SELECT * FROM {table} LIMIT 1")
    sample = cursor.fetchone()

    if sample:
        print("\nSample values:")
        for i, col in enumerate(columns):
            print(f"  {col[1]}: {sample[i]}")

conn.close()
