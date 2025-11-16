#!/usr/bin/env python3
import sqlite3
import json

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

print("="*80)
print("ted_china_contracts_fixed schema:")
print("="*80)
cursor.execute('PRAGMA table_info(ted_china_contracts_fixed)')
for row in cursor.fetchall():
    print(f"  {row[1]:30} {row[2]}")

print("\n" + "="*80)
print("Sample ted_china_contracts_fixed records:")
print("="*80)
cursor.execute('SELECT * FROM ted_china_contracts_fixed LIMIT 3')
columns = [d[0] for d in cursor.description]
for row in cursor.fetchall():
    record = dict(zip(columns, row))
    print(json.dumps(record, indent=2, ensure_ascii=False))
    print()

# Search for CRRC/COSCO
print("="*80)
print("Searching ted_china_contracts_fixed for CRRC/COSCO:")
print("="*80)

# Get column names to search through
cursor.execute('PRAGMA table_info(ted_china_contracts_fixed)')
columns = [row[1] for row in cursor.fetchall()]
print(f"Searching columns: {columns[:10]}")

# Try different column names
possible_contractor_columns = [col for col in columns if 'contract' in col.lower() or 'vendor' in col.lower() or 'supplier' in col.lower() or 'winner' in col.lower() or 'name' in col.lower()]
print(f"\nPossible contractor columns: {possible_contractor_columns}")

conn.close()
