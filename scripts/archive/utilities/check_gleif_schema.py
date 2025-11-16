#!/usr/bin/env python3
import sqlite3

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("="*80)
print("GLEIF SCHEMA INSPECTION")
print("="*80)

# Check what GLEIF tables exist
cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table' AND (name LIKE '%gleif%' OR name LIKE '%lei%')
    ORDER BY name
""")
tables = cursor.fetchall()

print("\nGLEIF/LEI Tables Found:")
for table in tables:
    print(f"  - {table[0]}")

# For each table, show schema and sample
for table in tables:
    table_name = table[0]
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name}")
    print('='*80)

    # Schema
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print("\nColumns:")
    for col in columns:
        print(f"  {col[1]:30} {col[2]:15} {'PRIMARY KEY' if col[5] else ''}")

    # Count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\nRecord count: {count:,}")

    # Sample (first 2 rows, first 5 columns)
    if count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
        rows = cursor.fetchall()
        print(f"\nSample data (first 2 rows, showing up to 5 columns):")
        for i, row in enumerate(rows, 1):
            print(f"\n  Row {i}:")
            for j, val in enumerate(row[:5]):  # First 5 columns only
                col_name = columns[j][1] if j < len(columns) else f"col_{j}"
                val_str = str(val)[:50] if val else "NULL"
                print(f"    {col_name}: {val_str}")

conn.close()
print("\n" + "="*80)
print("SCHEMA INSPECTION COMPLETE")
print("="*80)
