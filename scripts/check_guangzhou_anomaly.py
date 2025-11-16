#!/usr/bin/env python3
"""
Check Guangzhou Anomaly - Why 1,103 records?
"""

import sqlite3

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=" * 80)
print("GUANGZHOU ANOMALY INVESTIGATION")
print("=" * 80)

# Check Guangzhou records
cur.execute("""
    SELECT ee_name, ee_city, ee_state, ee_country
    FROM uspto_assignee
    WHERE UPPER(ee_city) = 'GUANGZHOU'
    LIMIT 30
""")

records = cur.fetchall()

print(f"\nTotal Guangzhou records: {len(records)}")
print("\nFirst 30 Guangzhou records:")
for i, (name, city, state, country) in enumerate(records, 1):
    print(f"{i:2d}. {name[:60]:60s} | {city:15s} | {state or 'N/A':10s} | {country or 'NULL'}")

# Check country distribution
cur.execute("""
    SELECT ee_country, COUNT(*) as cnt
    FROM uspto_assignee
    WHERE UPPER(ee_city) = 'GUANGZHOU'
    GROUP BY ee_country
    ORDER BY cnt DESC
""")

print("\n" + "=" * 80)
print("GUANGZHOU - COUNTRY DISTRIBUTION")
print("=" * 80)

country_dist = cur.fetchall()
for country, count in country_dist:
    country_str = country if country else "NULL/EMPTY"
    print(f"{country_str:30s}: {count:,}")

# Now check if there's a US city called Guangzhou
cur.execute("""
    SELECT ee_name, ee_city, ee_state, ee_country
    FROM uspto_assignee
    WHERE UPPER(ee_city) = 'GUANGZHOU'
    AND ee_country LIKE '%UNITED STATES%'
    LIMIT 10
""")

us_guangzhou = cur.fetchall()

if us_guangzhou:
    print("\n⚠️  WARNING: Found US records with city 'GUANGZHOU':")
    for name, city, state, country in us_guangzhou:
        print(f"  - {name[:50]} | {state} | {country}")

conn.close()
