#!/usr/bin/env python3
"""
Determine how USPTO distinguishes PRC (mainland) vs ROC (Taiwan)
"""

import sqlite3

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

print("=" * 80)
print("PRC vs ROC CODING ANALYSIS")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Check all unique country values that might be China-related
cur.execute("""
    SELECT DISTINCT ee_country, COUNT(*) as cnt
    FROM uspto_assignee
    WHERE ee_country LIKE '%CHINA%'
       OR ee_country LIKE '%TAIWAN%'
       OR ee_country LIKE '%HONG KONG%'
       OR ee_country LIKE '%PRC%'
       OR ee_country = 'CN'
       OR ee_country = 'CHN'
    GROUP BY ee_country
    ORDER BY cnt DESC
""")

china_variants = cur.fetchall()

print("\nAll China-related country codes:")
print(f"{'Country Code':<40s} | Count")
print("-" * 80)
for country, count in china_variants:
    print(f"{country:<40s} | {count:,}")

# Sample records from each variant
print("\n" + "=" * 80)
print("SAMPLE RECORDS BY COUNTRY CODE")
print("=" * 80)

for country, count in china_variants[:10]:
    print(f"\n--- {country} ({count:,} records) ---")

    # SECURITY: Avoid f-string in execute() - using parameterized query
    cur.execute("""
        SELECT ee_name, ee_city
        FROM uspto_assignee
        WHERE ee_country = ?
        LIMIT 3
    """, (country,))

    samples = cur.fetchall()
    for name, city in samples:
        city_str = city if city else "N/A"
        print(f"  - {name[:50]:50s} | {city_str}")

# Look for Beijing/Shanghai specifically
print("\n" + "=" * 80)
print("BEIJING ENTITIES - Country Code Distribution")
print("=" * 80)

cur.execute("""
    SELECT ee_country, COUNT(*) as cnt
    FROM uspto_assignee
    WHERE UPPER(ee_city) = 'BEIJING'
    GROUP BY ee_country
    ORDER BY cnt DESC
""")

beijing_countries = cur.fetchall()

print("\nBeijing records by country code:")
for country, count in beijing_countries:
    country_str = country if country else "NULL"
    print(f"  {country_str:30s}: {count:,}")

# Sample Beijing entities
cur.execute("""
    SELECT ee_name, ee_country
    FROM uspto_assignee
    WHERE UPPER(ee_city) = 'BEIJING'
    LIMIT 10
""")

beijing_samples = cur.fetchall()

print("\nBeijing entity samples:")
for name, country in beijing_samples:
    country_str = country if country else "NULL"
    print(f"  - {name[:60]:60s} | {country_str}")

# Check for "P.R. CHINA" or "PEOPLE'S REPUBLIC"
print("\n" + "=" * 80)
print("MAINLAND CHINA IDENTIFIERS")
print("=" * 80)

mainland_patterns = [
    ("P.R. CHINA", "ee_country LIKE '%P.R.%CHINA%'"),
    ("PEOPLE'S REPUBLIC", "ee_country LIKE '%PEOPLE%REPUBLIC%'"),
    ("PRC", "ee_country = 'PRC'"),
    ("CHINA (MAINLAND)", "ee_country LIKE '%MAINLAND%'"),
]

for label, condition in mainland_patterns:
    # SECURITY: Avoid f-string in execute() - condition is from hardcoded list above
    cur.execute("SELECT COUNT(*) FROM uspto_assignee WHERE " + condition)
    count = cur.fetchone()[0]

    if count > 0:
        print(f"\n{label}: {count:,} records")

        # SECURITY: Avoid f-string in execute() - condition is from hardcoded list above
        cur.execute("""
            SELECT ee_name, ee_city, ee_country
            FROM uspto_assignee
            WHERE """ + condition + """
            LIMIT 5
        """)

        samples = cur.fetchall()
        for name, city, country in samples:
            city_str = city if city else "N/A"
            print(f"  - {name[:45]:45s} | {city_str:15s} | {country}")

conn.close()

print("\n" + "=" * 80)
