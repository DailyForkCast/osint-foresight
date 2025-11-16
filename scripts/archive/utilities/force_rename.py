#!/usr/bin/env python3
"""
Force rename by dropping all views first
"""

import sqlite3

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

conn = sqlite3.connect(MAIN_DB, timeout=120)
cursor = conn.cursor()

# Get ALL views
cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
views = cursor.fetchall()

print(f"Found {len(views)} views in database")
print("\nDropping all views...")
for view_name, in views:
    try:
        cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
        print(f"  Dropped: {view_name}")
    except Exception as e:
        print(f"  Error dropping {view_name}: {e}")

conn.commit()

# Now rename
print("\nRenaming table...")
cursor.execute("ALTER TABLE usaspending_china_305_clean RENAME TO usaspending_china_305")
print("[OK] Table renamed")

cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
count = cursor.fetchone()[0]
print(f"Final count: {count:,} records")

conn.commit()
conn.close()

print("\n[SUCCESS] Table recovered")
