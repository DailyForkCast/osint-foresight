#!/usr/bin/env python3
"""Verify PatentsView Chinese Patent Detection Results"""

import sqlite3

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Year distribution
cursor.execute("""
    SELECT filing_year, COUNT(*) as count
    FROM patentsview_patents_chinese
    WHERE filing_year >= 2020 AND filing_year <= 2025
    GROUP BY filing_year
    ORDER BY filing_year
""")

print("="*80)
print("PATENTSVIEW DATA VERIFICATION (2020-2025)")
print("="*80)
print("\nYear Distribution:")
total = 0
for year, count in cursor.fetchall():
    print(f"  {year}: {count:,} patents")
    total += count
print(f"\nTotal: {total:,} patents")

# Confidence distribution
cursor.execute("""
    SELECT confidence, COUNT(*) as count
    FROM patentsview_patents_chinese
    GROUP BY confidence
    ORDER BY
        CASE confidence
            WHEN 'VERY_HIGH' THEN 1
            WHEN 'HIGH' THEN 2
            WHEN 'MEDIUM' THEN 3
            ELSE 4
        END
""")

print("\nConfidence Distribution:")
for conf, count in cursor.fetchall():
    pct = (count / total * 100) if total > 0 else 0
    print(f"  {conf:12s}: {count:,} ({pct:.1f}%)")

# Sample records
cursor.execute("""
    SELECT patent_id, filing_year, assignee_organization, assignee_city, assignee_country, confidence
    FROM patentsview_patents_chinese
    WHERE filing_year IN (2020, 2021, 2022, 2023, 2024)
    ORDER BY filing_year, confidence
    LIMIT 15
""")

print("\nSample Records:")
header = f"{'Patent ID':<12} {'Year':<6} {'Organization':<40} {'City':<20} {'Country':<10} {'Confidence':<10}"
print(header)
print("-"*110)
for row in cursor.fetchall():
    patent_id, year, org, city, country, conf = row
    org_short = (org or "")[:40]
    city_short = (city or "")[:20]
    country_short = (country or "")[:10]
    print(f"{patent_id:<12} {year:<6} {org_short:<40} {city_short:<20} {country_short:<10} {conf:<10}")

conn.close()
