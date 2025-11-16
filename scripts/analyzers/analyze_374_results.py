#!/usr/bin/env python3
"""Analyze 374-column processing results."""

import sqlite3
from pathlib import Path

db = Path('F:/OSINT_WAREHOUSE/osint_master.db')
conn = sqlite3.connect(db)
cur = conn.cursor()

print('='*80)
print('TERMINAL C - 374-COLUMN PROCESSING RESULTS')
print('='*80)

# Total statistics
cur.execute('SELECT COUNT(*), SUM(federal_action_obligation) FROM usaspending_china_374')
total_count, total_value = cur.fetchone()
print(f'\nTotal detections: {total_count:,}')
print(f'Total value: ${total_value:,.2f}')

# Top detections by value
print('\n' + '='*80)
print('TOP 10 DETECTIONS BY VALUE:')
print('='*80)
cur.execute('''
    SELECT recipient_name, recipient_country_name, federal_action_obligation,
           action_date
    FROM usaspending_china_374
    ORDER BY federal_action_obligation DESC
    LIMIT 10
''')

for name, country, amount, date in cur.fetchall():
    name_trunc = name[:45] if name else 'N/A'
    country_short = (country[:10] if country else 'N/A')
    print(f'{name_trunc:45s} | {country_short:10s} | ${amount:>15,.2f} | {date[:10]}')

# Detection breakdown by country
print('\n' + '='*80)
print('DETECTION BREAKDOWN BY COUNTRY:')
print('='*80)
cur.execute('''
    SELECT recipient_country_name, COUNT(*), SUM(federal_action_obligation)
    FROM usaspending_china_374
    GROUP BY recipient_country_name
    ORDER BY COUNT(*) DESC
    LIMIT 10
''')

for country, count, total in cur.fetchall():
    country_name = country if country else 'UNKNOWN'
    print(f'{country_name:20s} | {count:>6,} detections | ${total:>18,.2f}')

# Date range
print('\n' + '='*80)
print('DATE RANGE:')
print('='*80)
cur.execute('SELECT MIN(action_date), MAX(action_date) FROM usaspending_china_374')
min_date, max_date = cur.fetchone()
print(f'Earliest transaction: {min_date}')
print(f'Latest transaction: {max_date}')

conn.close()
print('\n' + '='*80)
