#!/usr/bin/env python3
"""Check osint_master.db schema"""

import sqlite3
from pathlib import Path

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("="*80)
print("THINKTANK_REPORTS SCHEMA")
print("="*80)
cursor.execute("PRAGMA table_info(thinktank_reports)")
for row in cursor.fetchall():
    print(f"{row[1]:30} {row[2]:15} PK={row[5]}")

print("\n" + "="*80)
print("THINKTANK_SOURCES SCHEMA")
print("="*80)
try:
    cursor.execute("PRAGMA table_info(thinktank_sources)")
    for row in cursor.fetchall():
        print(f"{row[1]:30} {row[2]:15} PK={row[5]}")
except:
    print("Table not found")

conn.close()
