import sqlite3
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# Get actually detected Chinese contractors
result = cursor.execute("""
    SELECT COUNT(DISTINCT contractor_name)
    FROM ted_contracts_production
    WHERE contractor_country IN ('CN', 'CHN', 'HK', 'HKG', 'MAC')
    AND contractor_name IS NOT NULL
    AND contractor_name != ''
""").fetchone()

print(f'Chinese contractors (by country code): {result[0]}')

# Sample
samples = cursor.execute("""
    SELECT DISTINCT contractor_name, contractor_country, COUNT(*) as cnt
    FROM ted_contracts_production
    WHERE contractor_country IN ('CN', 'CHN', 'HK', 'HKG', 'MAC')
    AND contractor_name IS NOT NULL
    AND contractor_name != ''
    GROUP BY contractor_name, contractor_country
    ORDER BY cnt DESC
    LIMIT 20
""").fetchall()

print()
print('Top 20 Chinese contractors:')
for name, country, count in samples:
    safe_name = name[:60].encode('ascii', errors='replace').decode('ascii')
    print(f'  {country}: {safe_name} ({count} contracts)')

conn.close()
