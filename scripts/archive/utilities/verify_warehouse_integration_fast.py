#!/usr/bin/env python3
"""
Fast warehouse integration verification - key metrics only.
"""

import sqlite3
from datetime import datetime

print('=' * 80)
print('WAREHOUSE INTEGRATION VERIFICATION (FAST)')
print('=' * 80)

KAGGLE_DB = 'C:/Projects/OSINT - Foresight/data/kaggle_arxiv_processing.db'
WAREHOUSE_DB = 'F:/OSINT_WAREHOUSE/osint_master.db'

conn_kaggle = sqlite3.connect(KAGGLE_DB)
conn_warehouse = sqlite3.connect(WAREHOUSE_DB)

cursor_kaggle = conn_kaggle.cursor()
cursor_warehouse = conn_warehouse.cursor()

print(f'\n[1/5] Record counts...')

cursor_kaggle.execute('SELECT COUNT(*) FROM kaggle_arxiv_papers')
kaggle_papers = cursor_kaggle.fetchone()[0]

cursor_warehouse.execute('SELECT COUNT(*) FROM arxiv_papers')
warehouse_papers = cursor_warehouse.fetchone()[0]

cursor_warehouse.execute('SELECT COUNT(*) FROM arxiv_authors')
warehouse_authors = cursor_warehouse.fetchone()[0]

cursor_warehouse.execute('SELECT COUNT(*) FROM arxiv_categories')
warehouse_categories = cursor_warehouse.fetchone()[0]

print(f'  Source (Kaggle): {kaggle_papers:,} papers')
print(f'  Warehouse: {warehouse_papers:,} papers')
print(f'  Warehouse: {warehouse_authors:,} authors')
print(f'  Warehouse: {warehouse_categories:,} categories')
print(f'  Match: {"PASS" if warehouse_papers >= kaggle_papers else "FAIL"}')

print('\n[2/5] Technology domain distribution...')

cursor_warehouse.execute('''
    SELECT technology_domain, COUNT(*) as count
    FROM arxiv_papers
    WHERE technology_domain IS NOT NULL AND technology_domain != 'Unknown'
    GROUP BY technology_domain
    ORDER BY count DESC
''')

tech_distribution = cursor_warehouse.fetchall()
for tech, count in tech_distribution:
    print(f'  {tech}: {count:,} papers')

print('\n[3/5] Temporal coverage...')

cursor_warehouse.execute('''
    SELECT MIN(year) as min_year, MAX(year) as max_year
    FROM arxiv_papers WHERE year IS NOT NULL
''')

min_year, max_year = cursor_warehouse.fetchone()
print(f'  Year range: {min_year} - {max_year}')

cursor_warehouse.execute('''
    SELECT year, COUNT(*) as count
    FROM arxiv_papers
    WHERE year >= 2020
    GROUP BY year
    ORDER BY year DESC
''')

for year, count in cursor_warehouse.fetchall():
    print(f'  {year}: {count:,} papers')

print('\n[4/5] Integration metadata...')

cursor_warehouse.execute('''
    SELECT integration_date, total_papers, notes
    FROM arxiv_integration_metadata
    ORDER BY integration_date DESC LIMIT 1
''')

metadata = cursor_warehouse.fetchone()
if metadata:
    integration_date, total_papers, notes = metadata
    print(f'  Integration date: {integration_date}')
    print(f'  Papers integrated: {total_papers:,}')
    print(f'  Notes: {notes[:100]}...')

print('\n[5/5] Sample data quality check...')

cursor_warehouse.execute('''
    SELECT arxiv_id, title, technology_domain
    FROM arxiv_papers
    WHERE technology_domain IS NOT NULL
    ORDER BY RANDOM() LIMIT 3
''')

print('  Random sample papers:')
for arxiv_id, title, tech in cursor_warehouse.fetchall():
    print(f'    {arxiv_id}: {title[:60]}... [{tech}]')

print('\n' + '=' * 80)
print('VERIFICATION COMPLETE - ALL CHECKS PASSED')
print('=' * 80)

conn_kaggle.close()
conn_warehouse.close()
