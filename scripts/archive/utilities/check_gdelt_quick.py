#!/usr/bin/env python3
"""Quick GDELT status check"""
import sqlite3

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# EU countries we care about
eu_countries = ['GRC', 'SVK', 'LTU', 'FIN', 'SWE', 'DNK', 'NLD', 'IRL', 'ESP', 'DEU', 'FRA']

print('\nGDELT EU-CHINA BILATERAL COLLECTION STATUS')
print('=' * 70)

for country in eu_countries:
    cursor.execute('''
        SELECT COUNT(*)
        FROM gdelt_events
        WHERE ((actor1_country_code = ? AND actor2_country_code = 'CHN')
           OR (actor1_country_code = 'CHN' AND actor2_country_code = ?))
    ''', (country, country))

    count = cursor.fetchone()[0]
    status = 'COLLECTED' if count > 0 else 'PENDING'
    print(f'{country:5} | {count:8,} events | {status}')

print('=' * 70)

# Total bilateral
cursor.execute('''
    SELECT COUNT(*)
    FROM gdelt_events
    WHERE (actor1_country_code IN ('GRC','SVK','LTU','FIN','SWE','DNK','NLD','IRL','ESP','DEU','FRA')
           AND actor2_country_code = 'CHN')
       OR (actor1_country_code = 'CHN'
           AND actor2_country_code IN ('GRC','SVK','LTU','FIN','SWE','DNK','NLD','IRL','ESP','DEU','FRA'))
''')
total_bilateral = cursor.fetchone()[0]

# Total China events
cursor.execute('SELECT COUNT(*) FROM gdelt_events WHERE actor1_country_code = "CHN" OR actor2_country_code = "CHN"')
total_china = cursor.fetchone()[0]

print(f'\nTotal EU-China bilateral: {total_bilateral:,}')
print(f'Total China events: {total_china:,}')
print(f'Bilateral percentage: {100*total_bilateral/total_china if total_china > 0 else 0:.2f}%')
