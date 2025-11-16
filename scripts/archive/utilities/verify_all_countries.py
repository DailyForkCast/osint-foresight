#!/usr/bin/env python3
"""Final Verification: All Countries Multi-Source Status"""

import sqlite3
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

conn = sqlite3.connect(str(DB_PATH))
cur = conn.cursor()

print("="*80)
print("MULTI-COUNTRY BILATERAL RELATIONS - FINAL VERIFICATION")
print("="*80 + "\n")

# Get all countries with data
cur.execute("""
    SELECT DISTINCT country_code
    FROM (
        SELECT country_code FROM major_acquisitions
        UNION
        SELECT country_code FROM bilateral_events
    )
    ORDER BY country_code
""")

countries = [row[0] for row in cur.fetchall()]

total_records = 0
total_citations = 0
total_multi_source = 0

for country in countries:
    print(f"\n{'='*80}")
    print(f"COUNTRY: {country}")
    print("="*80)

    # Count acquisitions
    cur.execute("SELECT COUNT(*) FROM major_acquisitions WHERE country_code = ?", (country,))
    acq_count = cur.fetchone()[0]

    # Count events
    cur.execute("SELECT COUNT(*) FROM bilateral_events WHERE country_code = ?", (country,))
    event_count = cur.fetchone()[0]

    country_total = acq_count + event_count
    total_records += country_total

    print(f"\nRecords: {acq_count} acquisitions, {event_count} events = {country_total} total")

    # Get citation counts per record
    # Handle UK/GB special case (events use UK_ prefix but country_code is GB)
    search_prefix = 'UK' if country == 'GB' else country
    cur.execute("""
        SELECT linked_record_id, COUNT(*) as source_count
        FROM citation_links
        WHERE linked_record_id LIKE ? || '_%'
        GROUP BY linked_record_id
        ORDER BY source_count DESC, linked_record_id
    """, (search_prefix,))

    records = cur.fetchall()

    print(f"\nMulti-source validation:")
    country_multi = 0
    country_citations = 0
    for rid, count in records:
        country_citations += count
        if count >= 2:
            country_multi += 1
        status = "✅" if count >= 2 else "⚠"
        print(f"  {status} {rid}: {count} sources")

    total_citations += country_citations
    total_multi_source += country_multi

    coverage = (country_multi / country_total * 100) if country_total > 0 else 0
    print(f"\nCountry Summary:")
    print(f"  Total citations: {country_citations}")
    print(f"  Multi-source records: {country_multi}/{country_total}")
    print(f"  Coverage: {coverage:.1f}%")

# Overall summary
print(f"\n\n{'='*80}")
print("OVERALL SUMMARY - ALL COUNTRIES")
print("="*80)

print(f"\nCountries: {len(countries)}")
print(f"Total records: {total_records}")
print(f"Total citations: {total_citations}")
print(f"Multi-source records: {total_multi_source}/{total_records}")
print(f"Overall coverage: {total_multi_source/total_records*100:.1f}%")

# Citation quality
cur.execute("""
    SELECT source_reliability, COUNT(*) as count
    FROM source_citations
    WHERE citation_id IN (
        SELECT DISTINCT citation_id FROM citation_links
        WHERE linked_table IN ('major_acquisitions', 'bilateral_events')
    )
    GROUP BY source_reliability
    ORDER BY source_reliability
""")

print(f"\n{'='*80}")
print("CITATION QUALITY DISTRIBUTION")
print("="*80)
for reliability, count in cur.fetchall():
    labels = {1: 'Primary official', 2: 'Verified secondary', 3: 'Credible', 4: 'Unverified'}
    label = labels.get(reliability, 'Unknown')
    pct = count / total_citations * 100
    print(f"  Level {reliability} ({label}): {count} ({pct:.1f}%)")

# Source distribution
cur.execute("""
    SELECT publication_name, COUNT(*) as count
    FROM source_citations
    WHERE citation_id IN (
        SELECT DISTINCT citation_id FROM citation_links
        WHERE linked_table IN ('major_acquisitions', 'bilateral_events')
    )
    GROUP BY publication_name
    ORDER BY count DESC
    LIMIT 15
""")

print(f"\n{'='*80}")
print("TOP 15 SOURCE PUBLICATIONS")
print("="*80)
for pub, count in cur.fetchall():
    print(f"  {pub or 'Unknown'}: {count} citations")

print(f"\n\n{'='*80}")
print("✓ VERIFICATION COMPLETE")
print("="*80)
print(f"\n{len(countries)} countries with {total_records} records and {total_citations} citations")
print(f"Multi-source coverage: {total_multi_source/total_records*100:.1f}%")
print("\n✓ Production-ready bilateral relations framework deployed!")

conn.close()
