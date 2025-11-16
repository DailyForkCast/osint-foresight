#!/usr/bin/env python3
"""
BRI Quick Analysis - Simplified version
Direct extraction and analysis of 872 BRI contracts
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

print("\n" + "="*80)
print("BRI QUICK ANALYSIS")
print("="*80)
print()

# Extract BRI contracts
print("Extracting BRI contracts...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

bri_data = cursor.execute("""
    SELECT
        id, notice_number, publication_date,
        ca_name, ca_country,
        contractor_name,
        contract_title,
        value_total, currency,
        detection_rationale
    FROM ted_contracts_production
    WHERE influence_category = 'BRI_RELATED'
    ORDER BY publication_date DESC
""").fetchall()

print(f"Found {len(bri_data)} BRI contracts")
print()

# Analyze
by_year = defaultdict(int)
by_country = defaultdict(int)
by_ca = defaultdict(int)
chinese_contractor_count = 0
total_value_eur = 0

contracts = []
for row in bri_data:
    contract_id, notice, pub_date, ca_name, ca_country, contractor, title, value, currency, detection = row

    # Parse year
    if pub_date:
        year = pub_date[:4]
        by_year[year] += 1

    # Country
    if ca_country:
        by_country[ca_country] += 1

    # CA
    if ca_name:
        by_ca[ca_name[:50]] += 1

    # Chinese contractor
    if detection:
        chinese_contractor_count += 1

    # Value (rough conversion to track)
    if value and value > 0:
        if currency == 'EUR':
            total_value_eur += value

    contracts.append({
        'id': contract_id,
        'notice': notice,
        'date': pub_date,
        'ca_name': ca_name,
        'ca_country': ca_country,
        'contractor': contractor,
        'title': title,
        'value': value,
        'currency': currency,
        'has_chinese_contractor': bool(detection)
    })

conn.close()

# Print results
print("="*80)
print("TEMPORAL DISTRIBUTION")
print("="*80)
for year in sorted(by_year.keys()):
    print(f"{year}: {by_year[year]:4d} contracts ({by_year[year]/len(bri_data)*100:5.1f}%)")

print()
print("="*80)
print("GEOGRAPHIC DISTRIBUTION (Top 15)")
print("="*80)
for country, count in sorted(by_country.items(), key=lambda x: x[1], reverse=True)[:15]:
    print(f"{country:3s}: {count:4d} contracts ({count/len(bri_data)*100:5.1f}%)")

print()
print("="*80)
print("TOP CONTRACTING AUTHORITIES (Top 15)")
print("="*80)
for ca, count in sorted(by_ca.items(), key=lambda x: x[1], reverse=True)[:15]:
    print(f"{ca[:45]:45s} {count:4d}")

print()
print("="*80)
print("KEY STATISTICS")
print("="*80)
print(f"Total BRI Contracts: {len(bri_data)}")
print(f"With Chinese Contractors: {chinese_contractor_count} ({chinese_contractor_count/len(bri_data)*100:.1f}%)")
print(f"Countries: {len(by_country)}")
print(f"Years: {min(by_year.keys())} - {max(by_year.keys())}")
print(f"Peak Year: {max(by_year.items(), key=lambda x: x[1])[0]} ({max(by_year.values())} contracts)")

# Save data
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
json_file = Path(f"analysis/bri_contracts_quick_{timestamp}.json")

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump({
        'timestamp': timestamp,
        'total': len(bri_data),
        'by_year': dict(by_year),
        'by_country': dict(by_country),
        'chinese_contractors': chinese_contractor_count,
        'contracts': contracts
    }, f, indent=2, default=str)

print()
print(f"Data saved to: {json_file}")
print()
print("="*80)
print("ANALYSIS COMPLETE")
print("="*80)
