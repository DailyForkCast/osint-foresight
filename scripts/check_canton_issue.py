#!/usr/bin/env python3
"""
Check Canton city issue - is it a US city?
"""

import sqlite3

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=" * 80)
print("CANTON CITY ANALYSIS")
print("=" * 80)

# Check all Canton records
cur.execute("""
    SELECT ee_country, COUNT(*) as cnt
    FROM uspto_assignee
    WHERE UPPER(ee_city) = 'CANTON'
    GROUP BY ee_country
    ORDER BY cnt DESC
""")

canton_dist = cur.fetchall()

print("\nCANTON - Country Distribution:")
total_canton = sum([c[1] for c in canton_dist])
print(f"Total Canton records: {total_canton:,}\n")

for country, count in canton_dist:
    country_str = country if country else "NULL/EMPTY"
    pct = count * 100 / total_canton
    print(f"{country_str:30s}: {count:,} ({pct:.1f}%)")

# Check Canton, Ohio specifically
print("\n" + "=" * 80)
print("CANTON, OHIO SAMPLE")
print("=" * 80)

cur.execute("""
    SELECT ee_name, ee_city, ee_state, ee_country
    FROM uspto_assignee
    WHERE UPPER(ee_city) = 'CANTON'
    AND (ee_country = 'UNITED STATES' OR ee_state = 'OHIO')
    LIMIT 15
""")

canton_us = cur.fetchall()

print(f"\nFound {len(canton_us)} Canton, Ohio/US examples:")
for name, city, state, country in canton_us:
    print(f"  - {name[:50]} | {state or 'N/A'} | {country or 'NULL'}")

# Check Canton, China
print("\n" + "=" * 80)
print("CANTON, CHINA (Guangzhou)")
print("=" * 80)

cur.execute("""
    SELECT ee_name, ee_city, ee_state, ee_country
    FROM uspto_assignee
    WHERE UPPER(ee_city) = 'CANTON'
    AND ee_country LIKE '%CHINA%'
    LIMIT 15
""")

canton_china = cur.fetchall()

print(f"\nFound {len(canton_china)} Canton, China examples:")
for name, city, state, country in canton_china:
    print(f"  - {name[:50]} | {state or 'N/A'} | {country}")

conn.close()

print("\n" + "=" * 80)
print("⚠️  CONCLUSION: 'CANTON' matches US cities, NOT Guangzhou, China!")
print("    This is a FALSE POSITIVE in the city detection logic.")
print("=" * 80)
