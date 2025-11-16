#!/usr/bin/env python3
"""
Generate Complete European Country Breakdown
Shows ALL European countries with China bilateral events
"""
import sqlite3
from datetime import datetime

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# Complete European country mapping
EUROPEAN_COUNTRIES = {
    # EU-27
    'AUT': {'name': 'Austria', 'group': 'EU-27'},
    'BEL': {'name': 'Belgium', 'group': 'EU-27'},
    'BGR': {'name': 'Bulgaria', 'group': 'EU-27'},
    'HRV': {'name': 'Croatia', 'group': 'EU-27'},
    'CYP': {'name': 'Cyprus', 'group': 'EU-27'},
    'CZE': {'name': 'Czech Republic', 'group': 'EU-27'},
    'DNK': {'name': 'Denmark', 'group': 'EU-27'},
    'EST': {'name': 'Estonia', 'group': 'EU-27'},
    'FIN': {'name': 'Finland', 'group': 'EU-27'},
    'FRA': {'name': 'France', 'group': 'EU-27'},
    'DEU': {'name': 'Germany', 'group': 'EU-27'},
    'GRC': {'name': 'Greece', 'group': 'EU-27'},
    'HUN': {'name': 'Hungary', 'group': 'EU-27'},
    'IRL': {'name': 'Ireland', 'group': 'EU-27'},
    'ITA': {'name': 'Italy', 'group': 'EU-27'},
    'LVA': {'name': 'Latvia', 'group': 'EU-27'},
    'LTU': {'name': 'Lithuania', 'group': 'EU-27'},
    'LUX': {'name': 'Luxembourg', 'group': 'EU-27'},
    'MLT': {'name': 'Malta', 'group': 'EU-27'},
    'NLD': {'name': 'Netherlands', 'group': 'EU-27'},
    'POL': {'name': 'Poland', 'group': 'EU-27'},
    'PRT': {'name': 'Portugal', 'group': 'EU-27'},
    'ROU': {'name': 'Romania', 'group': 'EU-27'},
    'SVK': {'name': 'Slovakia', 'group': 'EU-27'},
    'SVN': {'name': 'Slovenia', 'group': 'EU-27'},
    'ESP': {'name': 'Spain', 'group': 'EU-27'},
    'SWE': {'name': 'Sweden', 'group': 'EU-27'},

    # Post-Brexit UK
    'GBR': {'name': 'United Kingdom', 'group': 'UK (post-Brexit)'},

    # EEA/EFTA
    'NOR': {'name': 'Norway', 'group': 'EEA/EFTA'},
    'ISL': {'name': 'Iceland', 'group': 'EEA/EFTA'},
    'CHE': {'name': 'Switzerland', 'group': 'EEA/EFTA'},
    'LIE': {'name': 'Liechtenstein', 'group': 'EEA/EFTA'},

    # EU Candidates
    'TUR': {'name': 'Turkey', 'group': 'EU Candidate'},
    'MKD': {'name': 'North Macedonia', 'group': 'EU Candidate'},
    'MNE': {'name': 'Montenegro', 'group': 'EU Candidate'},
    'SRB': {'name': 'Serbia', 'group': 'EU Candidate'},
    'ALB': {'name': 'Albania', 'group': 'EU Candidate'},
    'BIH': {'name': 'Bosnia and Herzegovina', 'group': 'EU Candidate'},
    'UKR': {'name': 'Ukraine', 'group': 'EU Candidate'},
    'MDA': {'name': 'Moldova', 'group': 'EU Candidate'},
    'GEO': {'name': 'Georgia', 'group': 'EU Candidate'},

    # Other European
    'RUS': {'name': 'Russia', 'group': 'Other European'},
    'BLR': {'name': 'Belarus', 'group': 'Other European'},
    'ARM': {'name': 'Armenia', 'group': 'Other European'},
    'AZE': {'name': 'Azerbaijan', 'group': 'Other European'},
    'KOS': {'name': 'Kosovo', 'group': 'Other European'},
    'AND': {'name': 'Andorra', 'group': 'Other European'},
    'MCO': {'name': 'Monaco', 'group': 'Other European'},
    'SMR': {'name': 'San Marino', 'group': 'Other European'},
    'VAT': {'name': 'Vatican City', 'group': 'Other European'},

    # Regional code
    'EUR': {'name': 'European Union (bloc)', 'group': 'Regional Code'},
}

print("\n" + "=" * 100)
print("COMPLETE EUROPEAN-CHINA BILATERAL EVENTS BREAKDOWN")
print("=" * 100)
print(f"Database: F:/OSINT_WAREHOUSE/osint_master.db")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Period: 2020-2025")
print("=" * 100)

# Query all European bilateral events at once
all_codes = list(EUROPEAN_COUNTRIES.keys())
placeholders = ','.join(['?' for _ in all_codes])

query = f'''
    SELECT
        CASE
            WHEN actor1_country_code = 'CHN' THEN actor2_country_code
            WHEN actor2_country_code = 'CHN' THEN actor1_country_code
        END as eu_country,
        COUNT(*) as events
    FROM gdelt_events
    WHERE (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
      AND sqldate >= 20200101
      AND (actor1_country_code IN ({placeholders}) OR actor2_country_code IN ({placeholders}))
    GROUP BY eu_country
    ORDER BY events DESC
'''

print("\nQuerying database...")
cursor.execute(query, all_codes + all_codes)
results = cursor.fetchall()

# Organize by group
by_group = {}
for code, events in results:
    if code and code in EUROPEAN_COUNTRIES:
        group = EUROPEAN_COUNTRIES[code]['group']
        if group not in by_group:
            by_group[group] = []
        by_group[group].append({
            'code': code,
            'name': EUROPEAN_COUNTRIES[code]['name'],
            'events': events
        })

# Print by group
group_order = [
    'EU-27',
    'UK (post-Brexit)',
    'EEA/EFTA',
    'EU Candidate',
    'Other European',
    'Regional Code'
]

total_european = 0
countries_with_data = 0

for group in group_order:
    if group not in by_group:
        continue

    countries = sorted(by_group[group], key=lambda x: x['events'], reverse=True)
    group_total = sum(c['events'] for c in countries)

    print(f"\n{group.upper()}")
    print("-" * 100)

    for country in countries:
        total_european += country['events']
        countries_with_data += 1
        print(f"  {country['name']:30} ({country['code']}) | {country['events']:8,} events")

    print(f"  {'SUBTOTAL':30}            | {group_total:8,} events")

# Find missing countries
print("\n" + "=" * 100)
print("COUNTRIES WITH NO DATA")
print("-" * 100)

missing = []
for code, info in EUROPEAN_COUNTRIES.items():
    found = False
    for result_code, _ in results:
        if result_code == code:
            found = True
            break
    if not found:
        missing.append(f"  {info['name']:30} ({code}) | {info['group']}")

if missing:
    for m in sorted(missing):
        print(m)
else:
    print("  ALL EUROPEAN COUNTRIES HAVE DATA!")

# Summary statistics
print("\n" + "=" * 100)
print("SUMMARY STATISTICS")
print("=" * 100)

cursor.execute("SELECT COUNT(*) FROM gdelt_events WHERE actor1_country_code = 'CHN' OR actor2_country_code = 'CHN'")
total_china = cursor.fetchone()[0]

print(f"\nTotal China events in database: {total_china:,}")
print(f"Total European bilateral events: {total_european:,}")
print(f"European countries with data: {countries_with_data}")
print(f"European percentage of all China events: {100*total_european/total_china:.2f}%")

# Group breakdown
print(f"\nBy Group:")
for group in group_order:
    if group in by_group:
        group_total = sum(c['events'] for c in by_group[group])
        group_pct = 100 * group_total / total_european
        print(f"  {group:25} {group_total:8,} events ({group_pct:5.1f}%)")

print("\n" + "=" * 100)

# Save to JSON
import json
output = {
    'generated': datetime.now().isoformat(),
    'total_european_events': total_european,
    'countries_with_data': countries_with_data,
    'total_china_events': total_china,
    'european_percentage': round(100*total_european/total_china, 2),
    'by_country': {code: {'name': info['name'], 'group': info['group'], 'events': next((r[1] for r in results if r[0] == code), 0)}
                   for code, info in EUROPEAN_COUNTRIES.items()},
    'missing_countries': [{'code': code, 'name': info['name'], 'group': info['group']}
                          for code, info in EUROPEAN_COUNTRIES.items()
                          if not any(r[0] == code for r in results)]
}

with open('analysis/european_countries_complete_breakdown.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nComplete data saved to: analysis/european_countries_complete_breakdown.json")
print("=" * 100 + "\n")
