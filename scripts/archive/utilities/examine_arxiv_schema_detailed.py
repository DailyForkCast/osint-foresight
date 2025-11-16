#!/usr/bin/env python3
"""Examine existing arXiv table schemas in detail."""

import sqlite3

print('=' * 80)
print('DETAILED ARXIV SCHEMA EXAMINATION')
print('=' * 80)

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

arxiv_tables = ['arxiv_papers', 'arxiv_authors', 'arxiv_categories',
                'arxiv_statistics', 'arxiv_integration_metadata']

for table in arxiv_tables:
    print(f'\n{"=" * 80}')
    print(f'{table.upper()}')
    print(f'{"=" * 80}')

    # Get schema
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table}'")
    schema = cursor.fetchone()
    if schema:
        print('\nSCHEMA:')
        print(schema[0])

    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f'\nROW COUNT: {count:,}')

    # Get sample rows
    if count > 0:
        cursor.execute(f"SELECT * FROM {table} LIMIT 2")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        print('\nSAMPLE DATA (first 2 rows):')
        print(f'Columns: {", ".join(columns)}')
        for i, row in enumerate(rows, 1):
            print(f'\nRow {i}:')
            for col, val in zip(columns, row):
                val_str = str(val)[:100] if val else 'NULL'
                print(f'  {col}: {val_str}')

# Now check Kaggle source database schema for comparison
print(f'\n{"=" * 80}')
print('KAGGLE SOURCE DATABASE SCHEMA')
print(f'{"=" * 80}')

conn_kaggle = sqlite3.connect('C:/Projects/OSINT - Foresight/data/kaggle_arxiv_processing.db')
cursor_kaggle = conn_kaggle.cursor()

cursor_kaggle.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
kaggle_tables = [row[0] for row in cursor_kaggle.fetchall()]

print(f'\nKaggle tables ({len(kaggle_tables)}):')
for table in kaggle_tables:
    cursor_kaggle.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor_kaggle.fetchone()[0]
    print(f'  - {table} ({count:,} rows)')

print(f'\n{"-" * 80}')
print('kaggle_arxiv_papers schema:')
cursor_kaggle.execute("SELECT sql FROM sqlite_master WHERE name='kaggle_arxiv_papers'")
print(cursor_kaggle.fetchone()[0])

print(f'\n{"-" * 80}')
print('kaggle_arxiv_technology schema:')
cursor_kaggle.execute("SELECT sql FROM sqlite_master WHERE name='kaggle_arxiv_technology'")
print(cursor_kaggle.fetchone()[0])

conn.close()
conn_kaggle.close()

print('\n' + '=' * 80)
print('DETAILED EXAMINATION COMPLETE')
print('=' * 80)
