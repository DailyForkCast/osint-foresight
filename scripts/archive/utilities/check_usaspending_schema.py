#!/usr/bin/env python3
"""Check USAspending table schema"""

import sqlite3
from pathlib import Path

MASTER_DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

conn = sqlite3.connect(MASTER_DB_PATH)
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(usaspending_china_comprehensive)")
columns = cursor.fetchall()

print("USAspending table columns:")
print()
for col in columns:
    print(f"{col[1]:40} {col[2]}")

# Get sample row
cursor.execute("SELECT * FROM usaspending_china_comprehensive WHERE recipient_name LIKE '%DJI%' LIMIT 1")
row = cursor.fetchone()

if row:
    print("\nSample DJI record:")
    for i, col in enumerate(columns):
        print(f"{col[1]:40} {row[i]}")

conn.close()
