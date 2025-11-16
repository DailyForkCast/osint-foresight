"""
Simple OpenAlex Structure Check
Quick assessment without expensive queries
"""

import sqlite3

DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'

print("="*80)
print("OPENALEX QUICK STRUCTURE CHECK")
print("="*80 + "\n")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check openalex_works structure
print("1. openalex_works structure:")
cursor.execute("PRAGMA table_info(openalex_works)")
cols = [col[1] for col in cursor.fetchall()]
print(f"   Columns ({len(cols)}): {', '.join(cols[:15])}")
if len(cols) > 15:
    print(f"   ... and {len(cols) - 15} more\n")

# Check one sample record
print("2. Sample record from openalex_works:")
cursor.execute("SELECT * FROM openalex_works LIMIT 1")
sample = cursor.fetchone()
if sample and len(sample) > 0:
    # Show first few fields
    cursor.execute("PRAGMA table_info(openalex_works)")
    col_info = cursor.fetchall()
    for i in range(min(10, len(col_info))):
        col_name = col_info[i][1]
        value = sample[i]
        if value and len(str(value)) > 80:
            value = str(value)[:80] + "..."
        print(f"   {col_name}: {value}")

# Check openalex_work_authors structure
print("\n3. openalex_work_authors structure:")
cursor.execute("PRAGMA table_info(openalex_work_authors)")
author_cols = [col[1] for col in cursor.fetchall()]
print(f"   Columns ({len(author_cols)}): {', '.join(author_cols)}\n")

# Sample author record
print("4. Sample author record:")
cursor.execute("SELECT * FROM openalex_work_authors LIMIT 1")
author_sample = cursor.fetchone()
if author_sample:
    cursor.execute("PRAGMA table_info(openalex_work_authors)")
    author_col_info = cursor.fetchall()
    for i, col in enumerate(author_col_info):
        print(f"   {col[1]}: {author_sample[i]}")

# Quick count check
print("\n5. Record counts:")
cursor.execute("SELECT COUNT(*) FROM openalex_works")
print(f"   openalex_works: {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM openalex_work_authors")
print(f"   openalex_work_authors: {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM openalex_work_topics")
print(f"   openalex_work_topics: {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM openalex_entities")
print(f"   openalex_entities: {cursor.fetchone()[0]:,}")

# Check if we have country codes
print("\n6. Checking for country/affiliation data:")
if 'country_code' in author_cols:
    print("   [OK] country_code found in openalex_work_authors")
    cursor.execute("SELECT DISTINCT country_code FROM openalex_work_authors WHERE country_code IS NOT NULL LIMIT 10")
    countries = [row[0] for row in cursor.fetchall()]
    print(f"   Sample countries: {', '.join(countries)}")
else:
    print("   [NO] country_code not in openalex_work_authors")

print("\n" + "="*80)
print("QUICK CHECK COMPLETE")
print("="*80)

conn.close()
