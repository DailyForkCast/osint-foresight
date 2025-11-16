#!/usr/bin/env python3
"""
Check Database Status - Critical Tables
Quick check of what data we have and what's missing
"""

import sqlite3

print("=" * 80)
print("OSINT WAREHOUSE DATABASE STATUS CHECK")
print("=" * 80)

db = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = db.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
all_tables = [r[0] for r in cursor.fetchall()]

print(f"\nTotal tables: {len(all_tables)}")

# Check bilateral tables (from knowledge gap analysis)
print("\n" + "=" * 80)
print("BILATERAL LINKAGE TABLES (Critical for cross-source intelligence)")
print("=" * 80)

bilateral_critical = [
    'bilateral_academic_links',
    'bilateral_agreements',
    'bilateral_corporate_links',
    'bilateral_investments',
    'bilateral_trade',
    'bilateral_patent_links',
    'bilateral_procurement_links',
    'bilateral_sanctions_links'
]

for table in bilateral_critical:
    if table in all_tables:
        count = cursor.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
        status = "[OK] HAS DATA" if count > 0 else "[EMPTY]"
        print(f"  {table:<40} {count:>10,} {status}")
    else:
        print(f"  {table:<40} {'N/A':>10} [MISSING]")

# Check major data sources
print("\n" + "=" * 80)
print("MAJOR DATA SOURCES")
print("=" * 80)

major_sources = [
    ('openalex_works', 'OpenAlex research papers'),
    ('openalex_institutions', 'OpenAlex institutions'),
    ('ted_contracts', 'TED EU procurement'),
    ('usaspending_contracts', 'USAspending contracts'),
    ('uspto_patents', 'USPTO patents'),
    ('gdelt_events', 'GDELT global events'),
    ('entities', 'Master entity list'),
    ('academic_partnerships', 'CEIAS partnerships'),
    ('bilateral_countries', 'Country bilateral data'),
    ('bilateral_events', 'Diplomatic events')
]

for table, description in major_sources:
    if table in all_tables:
        try:
            count = cursor.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            status = "[OK]" if count > 0 else "[EMPTY]"
            print(f"  {status} {table:<30} {count:>12,}  ({description})")
        except Exception as e:
            print(f"  [ERR] {table:<30} {'ERROR':>12}  ({description})")
    else:
        print(f"  [MISS] {table:<30} {'MISSING':>12}  ({description})")

# Check GDELT specifically since we just collected it
print("\n" + "=" * 80)
print("GDELT COLLECTION STATUS (Just collected 2020-2025)")
print("=" * 80)

if 'gdelt_events' in all_tables:
    try:
        total = cursor.execute("SELECT COUNT(*) FROM gdelt_events").fetchone()[0]
        print(f"Total GDELT events: {total:,}")

        # Check by year
        years = cursor.execute("""
            SELECT
                CAST(SUBSTR(sqldate, 1, 4) AS INT) as year,
                COUNT(*) as count
            FROM gdelt_events
            GROUP BY year
            ORDER BY year
        """).fetchall()

        print("\nBy year:")
        for year, count in years:
            print(f"  {year}: {count:>12,} events")

        # Check countries with most events
        print("\nTop 10 countries (Actor1):")
        countries = cursor.execute("""
            SELECT
                actor1_country_code,
                COUNT(*) as count
            FROM gdelt_events
            WHERE actor1_country_code IS NOT NULL
            GROUP BY actor1_country_code
            ORDER BY count DESC
            LIMIT 10
        """).fetchall()

        for country, count in countries:
            print(f"  {country}: {count:>12,} events")

    except Exception as e:
        print(f"ERROR querying GDELT: {e}")
else:
    print("GDELT table not found!")

# Summary
print("\n" + "=" * 80)
print("PRIORITY GAPS SUMMARY")
print("=" * 80)

empty_bilateral = sum(1 for table in bilateral_critical if table in all_tables and cursor.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] == 0)
missing_bilateral = sum(1 for table in bilateral_critical if table not in all_tables)

print(f"\nBilateral linkage tables:")
print(f"  Empty: {empty_bilateral}/{len(bilateral_critical)}")
print(f"  Missing: {missing_bilateral}/{len(bilateral_critical)}")

if empty_bilateral + missing_bilateral > 0:
    print("\n  IMPACT: Cannot correlate data across sources")
    print("  - Cannot link TED contracts to diplomatic events")
    print("  - Cannot link patents to academic partnerships")
    print("  - Cannot track investments alongside trade flows")
    print("\n  RECOMMENDATION: Populate bilateral linkage tables (Tier 1 Priority)")

db.close()

print("\n" + "=" * 80)
