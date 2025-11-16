import sqlite3
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM cultural_institutions')
total_ci = cur.fetchone()[0]
print(f'Total CIs: {total_ci}')

cur.execute('SELECT COUNT(*) FROM academic_partnerships')
total_partnerships = cur.fetchone()[0]
print(f'Total partnerships: {total_partnerships}')

print('\nBy country:')
cur.execute('SELECT country_code, COUNT(*) FROM cultural_institutions GROUP BY country_code')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]} CIs')

print('\nPartnerships by country:')
cur.execute('SELECT country_code, COUNT(*) FROM academic_partnerships GROUP BY country_code')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]} partnerships')

print('\nPLA-affiliated partnerships by country:')
cur.execute('SELECT country_code, COUNT(*) FROM academic_partnerships WHERE military_involvement = 1 GROUP BY country_code')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]} PLA partnerships')

conn.close()
