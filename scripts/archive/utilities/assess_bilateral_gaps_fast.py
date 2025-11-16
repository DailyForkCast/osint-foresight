#!/usr/bin/env python3
"""Fast bilateral gap assessment using single query"""
import sqlite3
import json
from datetime import datetime
from collections import defaultdict

print("Connecting to database...")
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

COUNTRIES = {
    'GRC': {'name': 'Greece', 'priority': 'HIGH'},
    'SVK': {'name': 'Slovakia', 'priority': 'HIGH'},
    'LTU': {'name': 'Lithuania', 'priority': 'HIGH'},
    'FIN': {'name': 'Finland', 'priority': 'MEDIUM'},
    'SWE': {'name': 'Sweden', 'priority': 'MEDIUM'},
    'DNK': {'name': 'Denmark', 'priority': 'MEDIUM'},
    'NLD': {'name': 'Netherlands', 'priority': 'MEDIUM'},
    'IRL': {'name': 'Ireland', 'priority': 'LOW'},
    'ESP': {'name': 'Spain', 'priority': 'LOW'},
    'DEU': {'name': 'Germany', 'priority': 'REFERENCE'},
    'FRA': {'name': 'France', 'priority': 'REFERENCE'},
}

YEARS = [2020, 2021, 2022, 2023, 2024, 2025]

print("Running optimized query (this may take 30-60 seconds on 8.4M rows)...")

# Single optimized query - get all bilateral events at once
cursor.execute('''
    SELECT
        CASE
            WHEN actor1_country_code = 'CHN' THEN actor2_country_code
            WHEN actor2_country_code = 'CHN' THEN actor1_country_code
        END as eu_country,
        CAST(sqldate/10000 AS INT) as year,
        COUNT(*) as events
    FROM gdelt_events
    WHERE (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
      AND sqldate >= 20200101
      AND sqldate <= 20251231
      AND (
          (actor1_country_code IN ('GRC','SVK','LTU','FIN','SWE','DNK','NLD','IRL','ESP','DEU','FRA'))
          OR
          (actor2_country_code IN ('GRC','SVK','LTU','FIN','SWE','DNK','NLD','IRL','ESP','DEU','FRA'))
      )
    GROUP BY eu_country, year
    ORDER BY eu_country, year
''')

results_raw = cursor.fetchall()

# Organize results
results = defaultdict(lambda: defaultdict(int))
for country, year, count in results_raw:
    if country and country in COUNTRIES:
        results[country][year] = count

print("\n" + "=" * 80)
print("GDELT EU-CHINA BILATERAL COVERAGE ASSESSMENT (FAST)")
print("=" * 80)

gaps_to_collect = []

for code in sorted(COUNTRIES.keys()):
    info = COUNTRIES[code]
    yearly = results.get(code, {})
    total = sum(yearly.values())
    missing = [y for y in YEARS if yearly.get(y, 0) == 0]
    coverage = len([y for y in YEARS if yearly.get(y, 0) > 0])

    print(f"\n{info['name']:15} ({code}) - {info['priority']:9} Priority")
    print("-" * 80)

    for year in YEARS:
        count = yearly.get(year, 0)
        status = "OK      " if count > 0 else "MISSING "
        print(f"  {year}: {count:6,} events [{status}]")

    print(f"  Total: {total:,} events, Coverage: {coverage}/{len(YEARS)} years ({coverage/len(YEARS)*100:.0f}%)")

    if missing:
        print(f"  STATUS: NEEDS COLLECTION - Missing {len(missing)} years: {missing}")
        gaps_to_collect.append({
            'country': code,
            'name': info['name'],
            'priority': info['priority'],
            'missing_years': missing
        })
    else:
        print(f"  STATUS: COMPLETE")

# Summary
print("\n" + "=" * 80)
print("COLLECTION PLAN")
print("=" * 80)

if gaps_to_collect:
    high = [g for g in gaps_to_collect if COUNTRIES[g['country']]['priority'] == 'HIGH']
    medium = [g for g in gaps_to_collect if COUNTRIES[g['country']]['priority'] == 'MEDIUM']
    low = [g for g in gaps_to_collect if COUNTRIES[g['country']]['priority'] in ['LOW', 'REFERENCE']]

    print(f"\n{len(gaps_to_collect)} countries need collection\n")

    all_countries_to_collect = []

    if high:
        print("HIGH PRIORITY:")
        for g in high:
            print(f"  {g['name']:15} ({g['country']}) - Years: {g['missing_years']}")
            all_countries_to_collect.append(g)

    if medium:
        print("\nMEDIUM PRIORITY:")
        for g in medium:
            print(f"  {g['name']:15} ({g['country']}) - Years: {g['missing_years']}")
            all_countries_to_collect.append(g)

    if low:
        print("\nLOW PRIORITY:")
        for g in low:
            print(f"  {g['name']:15} ({g['country']}) - Years: {g['missing_years']}")
            all_countries_to_collect.append(g)

    # Generate collection script
    print("\n" + "=" * 80)
    print("AUTOMATED COLLECTION SCRIPT")
    print("=" * 80)

    script_file = 'collect_missing_bilateral.py'
    with open(script_file, 'w') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('"""Automated collection of missing EU-China bilateral events"""\n')
        f.write('import subprocess\n')
        f.write('import sys\n\n')
        f.write('collections = [\n')

        for gap in all_countries_to_collect:
            for year in gap['missing_years']:
                f.write(f"    {{'country': '{gap['country']}', 'year': {year}, 'name': '{gap['name']}'}},\n")

        f.write(']\n\n')
        f.write('print(f"Collecting {len(collections)} country-year combinations...\\\\n")\n\n')
        f.write('for i, item in enumerate(collections, 1):\n')
        f.write('    print(f"[{i}/{len(collections)}] {item[\'name\']} ({item[\'country\']}) - {item[\'year\']}")\n')
        f.write('    cmd = [\n')
        f.write('        "python", "scripts/collectors/gdelt_eu_china_bilateral_collector.py",\n')
        f.write('        "--country", item["country"],\n')
        f.write('        "--start-date", f"{item[\'year\']}0101",\n')
        f.write('        "--end-date", f"{item[\'year\']}1231",\n')
        f.write('        "--db", "F:/OSINT_WAREHOUSE/osint_master.db"\n')
        f.write('    ]\n')
        f.write('    result = subprocess.run(cmd)\n')
        f.write('    if result.returncode != 0:\n')
        f.write('        print(f"ERROR: Collection failed for {item[\'name\']} {item[\'year\']}")\n')
        f.write('        sys.exit(1)\n')
        f.write('    print()\n\n')
        f.write('print("\\\\nCOLLECTION COMPLETE!")\n')

    print(f"\nGenerated automated collection script: {script_file}")
    print(f"\nTo execute:\n  python {script_file}")
    print(f"\nEstimated time: ~{len(all_countries_to_collect)*2} minutes")
    print(f"Estimated cost: ${len(all_countries_to_collect)*0.15:.2f}")

    # Save JSON summary
    summary = {
        'assessment_date': datetime.now().isoformat(),
        'total_gaps': len(gaps_to_collect),
        'collections_needed': len(all_countries_to_collect),
        'gaps': gaps_to_collect
    }

    with open('analysis/gdelt_bilateral_gaps.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nGap summary saved to: analysis/gdelt_bilateral_gaps.json")

else:
    print("\nALL COUNTRIES HAVE COMPLETE COVERAGE!")
    print("No collection needed - proceed to analysis.")

print("=" * 80)
