#!/usr/bin/env python3
"""Examine master warehouse schema for Kaggle arXiv integration."""

import sqlite3

print('=' * 80)
print('MASTER WAREHOUSE SCHEMA EXAMINATION')
print('=' * 80)

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

print(f'\nTotal tables in warehouse: {len(tables)}')
print('\nTables (showing first 30):')
for i, table in enumerate(tables[:30], 1):
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f'  {i:2d}. {table:<40} ({count:>12,} rows)')

if len(tables) > 30:
    print(f'\n  ... and {len(tables) - 30} more tables')

# Check for existing Kaggle/arXiv tables
arxiv_tables = [t for t in tables if 'arxiv' in t.lower() or 'kaggle' in t.lower()]
print(f'\n{"-" * 80}')
print(f'Existing arXiv/Kaggle tables: {len(arxiv_tables)}')
if arxiv_tables:
    for table in arxiv_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f'  - {table} ({count:,} rows)')
else:
    print('  [NONE] - This will be a fresh integration')

# Check for generic papers/authors tables
generic_tables = ['papers', 'authors', 'technology_classifications', 'detections']
print(f'\n{"-" * 80}')
print('Generic table structures:')
for table in generic_tables:
    if table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table}'")
        schema = cursor.fetchone()[0]
        print(f'\n{table.upper()} ({count:,} rows):')
        print(f'{schema[:200]}...' if len(schema) > 200 else schema)
    else:
        print(f'\n{table.upper()}: [DOES NOT EXIST]')

conn.close()

print('\n' + '=' * 80)
print('SCHEMA EXAMINATION COMPLETE')
print('=' * 80)
