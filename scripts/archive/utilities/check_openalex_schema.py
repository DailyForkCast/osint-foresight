import sqlite3
from pathlib import Path

db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check openalex_works schema
print("=" * 80)
print("OPENALEX_WORKS TABLE SCHEMA")
print("=" * 80)
cursor.execute("PRAGMA table_info(openalex_works)")
cols = cursor.fetchall()
for col in cols:
    print(f"  {col[1]} ({col[2]})")

# Sample data
print("\nSample data:")
cursor.execute("SELECT * FROM openalex_works LIMIT 1")
row = cursor.fetchone()
if row:
    for i, col in enumerate(cols):
        print(f"  {col[1]}: {row[i]}")

# Check institutions table
print("\n" + "=" * 80)
print("OPENALEX_INSTITUTIONS TABLE SCHEMA")
print("=" * 80)
cursor.execute("PRAGMA table_info(openalex_institutions)")
cols = cursor.fetchall()
for col in cols:
    print(f"  {col[1]} ({col[2]})")

# Check work_authors
print("\n" + "=" * 80)
print("OPENALEX_WORK_AUTHORS TABLE SCHEMA")
print("=" * 80)
cursor.execute("PRAGMA table_info(openalex_work_authors)")
cols = cursor.fetchall()
for col in cols:
    print(f"  {col[1]} ({col[2]})")

# Count quantum works
print("\n" + "=" * 80)
print("QUANTUM RESEARCH COUNT")
print("=" * 80)

cursor.execute("""
SELECT COUNT(*) FROM openalex_works
WHERE title LIKE '%quantum%'
OR abstract LIKE '%quantum%'
""")
count = cursor.fetchone()[0]
print(f"Total quantum works: {count:,}")

# Check country_code presence
cursor.execute("""
SELECT country_code, COUNT(*) as count
FROM openalex_works
WHERE (title LIKE '%quantum%' OR abstract LIKE '%quantum%')
AND country_code IS NOT NULL
GROUP BY country_code
ORDER BY count DESC
LIMIT 20
""")
print("\nQuantum works by country:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]:,}")

conn.close()
