import sqlite3

db = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = db.cursor()

# Check all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("All tables in database:")
for t in tables:
    print(f"  - {t[0]}")

# Check TED tables specifically
ted_tables = [t for t in tables if 'ted' in t[0].lower()]
print(f"\nTED-related tables: {len(ted_tables)}")
for t in ted_tables:
    table_name = t[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  - {table_name}: {count} records")

db.close()
