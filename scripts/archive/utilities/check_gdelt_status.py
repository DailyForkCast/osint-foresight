#!/usr/bin/env python3
"""Check current GDELT collection status"""
import sqlite3
from collections import defaultdict

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# Get country breakdown
cursor.execute('''
    SELECT
        CASE
            WHEN actor1_country_code = 'CHN' THEN actor2_country_code
            WHEN actor2_country_code = 'CHN' THEN actor1_country_code
            ELSE 'OTHER'
        END as eu_country,
        CAST(sqldate/10000 AS INT) as year,
        COUNT(*) as events
    FROM gdelt_events
    WHERE (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
    GROUP BY eu_country, year
    ORDER BY eu_country, year
''')

results = cursor.fetchall()

# Organize by country
by_country = defaultdict(dict)
for country, year, count in results:
    if country and country != 'CHN':
        by_country[country][year] = count

# Print summary
print('CURRENT GDELT BILATERAL COLLECTION STATUS')
print('=' * 60)
for country in sorted(by_country.keys()):
    years = by_country[country]
    total = sum(years.values())
    year_range = f"{min(years.keys())}-{max(years.keys())}"
    print(f'{country:8} | {year_range:9} | {total:6,} events | Years: {len(years)}')

cursor.execute('SELECT COUNT(*) FROM gdelt_events')
total = cursor.fetchone()[0]
print('=' * 60)
print(f'TOTAL EVENTS: {total:,}')
