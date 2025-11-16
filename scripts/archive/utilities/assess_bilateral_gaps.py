#!/usr/bin/env python3
"""
Assess EU-China Bilateral Coverage and Identify Gaps
"""
import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# Priority EU countries for bilateral analysis
COUNTRIES = {
    'GRC': {'name': 'Greece', 'priority': 'HIGH', 'reason': 'COSCO port, BRI gateway'},
    'SVK': {'name': 'Slovakia', 'priority': 'HIGH', 'reason': 'CEIAS focus, -90% export drop'},
    'LTU': {'name': 'Lithuania', 'priority': 'HIGH', 'reason': 'Taiwan crisis 2021'},
    'FIN': {'name': 'Finland', 'priority': 'MEDIUM', 'reason': 'Nordic tech collaboration'},
    'SWE': {'name': 'Sweden', 'priority': 'MEDIUM', 'reason': 'Nordic tech collaboration'},
    'DNK': {'name': 'Denmark', 'priority': 'MEDIUM', 'reason': 'Nordic tech collaboration'},
    'NLD': {'name': 'Netherlands', 'priority': 'MEDIUM', 'reason': 'ASML semiconductor nexus'},
    'IRL': {'name': 'Ireland', 'priority': 'LOW', 'reason': 'Tech hub monitoring'},
    'ESP': {'name': 'Spain', 'priority': 'LOW', 'reason': 'BRI participant'},
    'DEU': {'name': 'Germany', 'priority': 'REFERENCE', 'reason': 'Major economy baseline'},
    'FRA': {'name': 'France', 'priority': 'REFERENCE', 'reason': 'EU leader baseline'},
}

YEARS = [2020, 2021, 2022, 2023, 2024, 2025]

print("\n" + "=" * 90)
print("GDELT EU-CHINA BILATERAL COVERAGE ASSESSMENT")
print("=" * 90)
print(f"Database: F:/OSINT_WAREHOUSE/osint_master.db")
print(f"Assessment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 90)

results = {}
gaps = []

for code, info in COUNTRIES.items():
    print(f"\n{info['name']} ({code}) - {info['priority']} Priority")
    print(f"Reason: {info['reason']}")
    print("-" * 90)

    yearly_counts = {}
    total_bilateral = 0

    for year in YEARS:
        start_date = int(f"{year}0101")
        end_date = int(f"{year}1231")

        cursor.execute('''
            SELECT COUNT(*)
            FROM gdelt_events
            WHERE sqldate BETWEEN ? AND ?
              AND ((actor1_country_code = ? AND actor2_country_code = 'CHN')
                OR (actor1_country_code = 'CHN' AND actor2_country_code = ?))
        ''', (start_date, end_date, code, code))

        count = cursor.fetchone()[0]
        yearly_counts[year] = count
        total_bilateral += count

        status = "OK" if count > 0 else "MISSING"
        print(f"  {year}: {count:6,} events [{status}]")

    # Determine if this country needs collection
    missing_years = [year for year, count in yearly_counts.items() if count == 0]
    coverage_pct = (len([c for c in yearly_counts.values() if c > 0]) / len(YEARS)) * 100

    results[code] = {
        'name': info['name'],
        'priority': info['priority'],
        'total': total_bilateral,
        'yearly': yearly_counts,
        'missing_years': missing_years,
        'coverage_pct': coverage_pct
    }

    print(f"\n  Total: {total_bilateral:,} bilateral events")
    print(f"  Coverage: {coverage_pct:.1f}% ({len(YEARS)-len(missing_years)}/{len(YEARS)} years)")

    if missing_years:
        gaps.append({
            'country': code,
            'name': info['name'],
            'priority': info['priority'],
            'missing_years': missing_years,
            'action': 'COLLECT' if len(missing_years) >= 3 else 'OPTIONAL'
        })
        print(f"  Status: GAPS FOUND - Missing {len(missing_years)} years: {missing_years}")
    else:
        print(f"  Status: COMPLETE")

# Summary
print("\n" + "=" * 90)
print("SUMMARY")
print("=" * 90)

complete = [c for c, r in results.items() if not r['missing_years']]
partial = [c for c, r in results.items() if r['missing_years'] and r['coverage_pct'] >= 50]
empty = [c for c, r in results.items() if r['coverage_pct'] == 0]
needs_collection = [c for c, r in results.items() if len(r['missing_years']) >= 3]

print(f"\nComplete Coverage (all 6 years): {len(complete)} countries")
if complete:
    for code in complete:
        print(f"  - {COUNTRIES[code]['name']} ({code}): {results[code]['total']:,} events")

print(f"\nPartial Coverage (50%+ years): {len(partial)} countries")
if partial:
    for code in partial:
        print(f"  - {COUNTRIES[code]['name']} ({code}): {results[code]['total']:,} events, {results[code]['coverage_pct']:.0f}% coverage")

print(f"\nNo Coverage (0 years): {len(empty)} countries")
if empty:
    for code in empty:
        print(f"  - {COUNTRIES[code]['name']} ({code}): NEEDS COLLECTION")

print(f"\n" + "=" * 90)
print("RECOMMENDED COLLECTION ACTIONS")
print("=" * 90)

if gaps:
    print(f"\n{len(gaps)} countries need data collection:\n")

    high_priority = [g for g in gaps if COUNTRIES[g['country']]['priority'] == 'HIGH']
    medium_priority = [g for g in gaps if COUNTRIES[g['country']]['priority'] == 'MEDIUM']
    low_priority = [g for g in gaps if COUNTRIES[g['country']]['priority'] in ['LOW', 'REFERENCE']]

    if high_priority:
        print("HIGH PRIORITY (collect immediately):")
        for gap in high_priority:
            print(f"  {gap['name']:15} ({gap['country']}) - Missing: {gap['missing_years']}")

    if medium_priority:
        print("\nMEDIUM PRIORITY:")
        for gap in medium_priority:
            print(f"  {gap['name']:15} ({gap['country']}) - Missing: {gap['missing_years']}")

    if low_priority:
        print("\nLOW PRIORITY:")
        for gap in low_priority:
            print(f"  {gap['name']:15} ({gap['country']}) - Missing: {gap['missing_years']}")

    # Generate collection command
    print("\n" + "=" * 90)
    print("COLLECTION COMMAND")
    print("=" * 90)

    countries_to_collect = [g['country'] for g in gaps if g['action'] == 'COLLECT']
    if countries_to_collect:
        print(f"\npython scripts/collectors/gdelt_eu_china_bilateral_collector.py \\")
        for i, country in enumerate(countries_to_collect):
            years_needed = results[country]['missing_years']
            for year in years_needed:
                suffix = " \\" if not (i == len(countries_to_collect)-1 and year == years_needed[-1]) else ""
                print(f"    --country {country} --start-date {year}0101 --end-date {year}1231{suffix}")
else:
    print("\n✓ ALL COUNTRIES HAVE COMPLETE COVERAGE!")
    print("  No collection needed - proceed to analysis.")

# Save results to JSON
output = {
    'assessment_date': datetime.now().isoformat(),
    'total_countries': len(COUNTRIES),
    'complete': complete,
    'partial': partial,
    'empty': empty,
    'gaps': gaps,
    'results': results
}

with open('analysis/gdelt_bilateral_gaps_assessment.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n\nDetailed results saved to: analysis/gdelt_bilateral_gaps_assessment.json")
print("=" * 90)
