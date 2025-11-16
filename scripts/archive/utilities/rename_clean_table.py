#!/usr/bin/env python3
"""
Simple rename of clean table - recovery from partial execution
"""

import sqlite3

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

conn = sqlite3.connect(MAIN_DB, timeout=120)
cursor = conn.cursor()

# Check what tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%usaspending_china%'")
tables = cursor.fetchall()

print("Existing tables:")
for table, in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  {table}: {count:,} records")

# Drop any problematic views first
print("\nDropping dependent views...")
cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type = 'view' AND sql LIKE '%usaspending_china_305%'
""")
views = cursor.fetchall()
for view_name, in views:
    print(f"  Dropping view: {view_name}")
    cursor.execute(f"DROP VIEW IF EXISTS {view_name}")

# Rename the clean table
if any('usaspending_china_305_clean' in table for table, in tables):
    print("\nRenaming usaspending_china_305_clean to usaspending_china_305...")
    cursor.execute("ALTER TABLE usaspending_china_305_clean RENAME TO usaspending_china_305")
    print("  [OK] Renamed")

    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    count = cursor.fetchone()[0]
    print(f"  Final count: {count:,} records")

conn.commit()
conn.close()

print("\n[SUCCESS] Table recovered and renamed")
