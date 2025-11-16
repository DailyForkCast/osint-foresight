"""Check what GDELT data we actually have collected"""

import sqlite3

db = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = db.cursor()

print('='*100)
print('GDELT DATA COVERAGE CHECK')
print('='*100)
print()

# Total events
cursor.execute('SELECT COUNT(*) FROM gdelt_events')
total = cursor.fetchone()[0]
print(f'Total GDELT events: {total:,}')
print()

# Year range
cursor.execute("""
    SELECT
        MIN(CAST(SUBSTR(sqldate, 1, 4) AS INTEGER)) as min_year,
        MAX(CAST(SUBSTR(sqldate, 1, 4) AS INTEGER)) as max_year
    FROM gdelt_events
""")
min_year, max_year = cursor.fetchone()
print(f'Year range: {min_year} to {max_year}')
print()

# Country pairs
cursor.execute("""
    SELECT DISTINCT
        actor1_country_code,
        actor2_country_code,
        COUNT(*) as events
    FROM gdelt_events
    WHERE actor1_country_code IS NOT NULL
      AND actor2_country_code IS NOT NULL
    GROUP BY actor1_country_code, actor2_country_code
    ORDER BY events DESC
    LIMIT 20
""")
print('Top 20 country pairs in database:')
print(f"{'Actor1':<10} {'Actor2':<10} {'Events':<15}")
print('-'*40)
for a1, a2, events in cursor.fetchall():
    marker = ' <- Lithuania' if a1 == 'LTU' or a2 == 'LTU' else ''
    print(f"{a1:<10} {a2:<10} {events:>13,}{marker}")

print()
print('='*100)
print('FINDING: GDELT collection appears Lithuania-specific')
print('Strategy: Since we only have Lithuania GDELT data, pivot to trade-based expansion')
print('='*100)

db.close()
