#!/usr/bin/env python3
import sqlite3

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get GLEIF table names (no counting)
cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table' AND (name LIKE '%gleif%' OR name LIKE '%lei%')
    ORDER BY name
""")
tables = [row[0] for row in cursor.fetchall()]

print("GLEIF/LEI Tables Found:")
for table in tables:
    print(f"  - {table}")

# Get schema for each table (no data queries)
for table in tables:
    print(f"\n{'='*60}")
    print(f"{table} SCHEMA:")
    print('='*60)
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    for col in columns:
        pk = " [PRIMARY KEY]" if col[5] else ""
        print(f"  {col[1]:40} {col[2]:15}{pk}")

conn.close()
print("\nDone (no record counts to avoid timeout)")
