import sqlite3
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cur = conn.cursor()

cur.execute('PRAGMA table_info(source_citations)')
print('source_citations schema:')
for row in cur.fetchall():
    print(f'  {row[1]} ({row[2]})')

conn.close()
