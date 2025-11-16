import sqlite3
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(gdelt_gkg)")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]} ({row[2]})")
conn.close()
