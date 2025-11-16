#!/usr/bin/env python3
"""
Check All 5 Missing Countries Using Comprehensive Geographic Field Search
Quick count query to estimate total recoverable events
"""
from google.cloud import bigquery
import json
from datetime import datetime

project_id = "osint-foresight-2025"
client = bigquery.Client(project=project_id)

print("\n" + "=" * 100)
print("COMPREHENSIVE GEOGRAPHIC FIELD CHECK: ALL 5 MISSING COUNTRIES")
print("=" * 100)

countries = {
    'Romania': {
        'codes': ['ROM', 'ROU'],
        'search_terms': ['romania', 'romanian']
    },
    'Slovenia': {
        'codes': ['SVN', 'SLO'],
        'search_terms': ['slovenia', 'slovenian']
    },
    'Bosnia and Herzegovina': {
        'codes': ['BIH', 'BOS'],
        'search_terms': ['bosnia', 'bosnian', 'herzegovina']
    },
    'Montenegro': {
        'codes': ['MNE', 'MNG', 'MNT'],
        'search_terms': ['montenegro', 'montenegrin']
    },
    'Kosovo': {
        'codes': ['KOS', 'KSV', 'XK', 'XKX'],
        'search_terms': ['kosovo', 'kosovar']
    }
}

results = {}

for country_name, config in countries.items():
    print(f"\n{'=' * 100}")
    print(f"CHECKING: {country_name}")
    print(f"{'=' * 100}")

    codes = config['codes']
    search_terms = config['search_terms']

    # Build comprehensive WHERE clause
    code_conditions = []
    for code in codes:
        code_conditions.append(f"Actor1CountryCode = '{code}'")
        code_conditions.append(f"Actor2CountryCode = '{code}'")
        code_conditions.append(f"Actor1Geo_CountryCode = '{code}'")
        code_conditions.append(f"Actor2Geo_CountryCode = '{code}'")
        code_conditions.append(f"ActionGeo_CountryCode = '{code}'")

    name_conditions = []
    for term in search_terms:
        name_conditions.append(f"LOWER(Actor1Name) LIKE '%{term}%'")
        name_conditions.append(f"LOWER(Actor2Name) LIKE '%{term}%'")
        name_conditions.append(f"LOWER(Actor1Geo_FullName) LIKE '%{term}%'")
        name_conditions.append(f"LOWER(Actor2Geo_FullName) LIKE '%{term}%'")
        name_conditions.append(f"LOWER(ActionGeo_FullName) LIKE '%{term}%'")

    all_conditions = code_conditions + name_conditions
    where_clause = " OR ".join(all_conditions)

    # Comprehensive count query
    query = f"""
        SELECT COUNT(DISTINCT GLOBALEVENTID) as count
        FROM `gdelt-bq.gdeltv2.events`
        WHERE ({where_clause})
          AND (Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN')
          AND SQLDATE >= 20200101
          AND SQLDATE <= 20251231
    """

    print(f"Querying BigQuery for comprehensive count...")

    try:
        query_job = client.query(query)
        result = query_job.result()

        for row in result:
            count = row.count
            results[country_name] = {
                'comprehensive_count': count,
                'codes_checked': codes,
                'search_terms': search_terms
            }

            print(f"\nCOMPREHENSIVE TOTAL: {count:,} events")
            print(f"  (Using all 6 geographic systems)")

            # For comparison, also check actor names only
            name_only_conditions = [f"LOWER(Actor1Name) LIKE '%{term}%' OR LOWER(Actor2Name) LIKE '%{term}%'"
                                  for term in search_terms]
            name_where = " OR ".join(name_only_conditions)

            name_query = f"""
                SELECT COUNT(DISTINCT GLOBALEVENTID) as count
                FROM `gdelt-bq.gdeltv2.events`
                WHERE ({name_where})
                  AND (Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN')
                  AND SQLDATE >= 20200101
            """

            name_job = client.query(name_query)
            name_result = name_job.result()

            for name_row in name_result:
                name_count = name_row.count
                results[country_name]['name_only_count'] = name_count

                print(f"\n  Breakdown:")
                print(f"    Actor names only: {name_count:,} events")
                print(f"    Additional from geo fields: {count - name_count:,} events")
                if name_count > 0:
                    multiplier = count / name_count
                    print(f"    Multiplier: {multiplier:.2f}x")

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        results[country_name] = {'error': str(e)}

# Summary
print("\n" + "=" * 100)
print("SUMMARY: ALL 5 COUNTRIES")
print("=" * 100)

total_comprehensive = 0
total_names_only = 0

for country, data in results.items():
    if 'comprehensive_count' in data:
        comp = data['comprehensive_count']
        names = data.get('name_only_count', 0)
        total_comprehensive += comp
        total_names_only += names

        multiplier = comp / names if names > 0 else 0
        print(f"\n{country:30s}: {comp:6,} events (names: {names:6,}, multiplier: {multiplier:.2f}x)")

print(f"\n{'=' * 100}")
print(f"TOTAL RECOVERABLE EVENTS: {total_comprehensive:,}")
print(f"  (vs {total_names_only:,} if only using actor names)")
print(f"  Additional recovery: {total_comprehensive - total_names_only:,} events")
print(f"{'=' * 100}")

# Save results
output = {
    'timestamp': datetime.now().isoformat(),
    'total_comprehensive_events': total_comprehensive,
    'total_name_only_events': total_names_only,
    'additional_recovery': total_comprehensive - total_names_only,
    'countries': results
}

with open('analysis/missing_countries_comprehensive_counts.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to: analysis/missing_countries_comprehensive_counts.json")
