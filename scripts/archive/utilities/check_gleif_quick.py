#!/usr/bin/env python3
import sqlite3

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check what GLEIF tables exist
cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table' AND (name LIKE '%gleif%' OR name LIKE '%lei%')
    ORDER BY name
""")
tables = cursor.fetchall()

print("GLEIF/LEI Tables:")
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  {table_name}: {count:,} records")

# Check gleif_entities schema specifically
if any('gleif_entities' in t[0] for t in tables):
    print("\ngleif_entities columns:")
    cursor.execute("PRAGMA table_info(gleif_entities)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
else:
    print("\nNo gleif_entities table found")

# Check gleif_relationships schema if exists
if any('relationship' in t[0].lower() for t in tables):
    rel_table = [t[0] for t in tables if 'relationship' in t[0].lower()][0]
    print(f"\n{rel_table} columns:")
    cursor.execute(f"PRAGMA table_info({rel_table})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

conn.close()
