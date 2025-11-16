#!/usr/bin/env python3
"""
Verify Missing Countries in GDELT BigQuery
Query the source to confirm if Romania, Slovenia, Bosnia, Montenegro, Kosovo truly have no events
"""
from google.cloud import bigquery
import os
from datetime import datetime

# Set up BigQuery client
project_id = "osint-foresight-2025"
client = bigquery.Client(project=project_id)

print("\n" + "=" * 100)
print("VERIFYING MISSING COUNTRIES IN GDELT BIGQUERY SOURCE")
print("=" * 100)
print(f"Project: {project_id}")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)

# Countries to check
missing_countries = {
    'ROU': 'Romania',
    'SVN': 'Slovenia',
    'BIH': 'Bosnia and Herzegovina',
    'MNE': 'Montenegro',
    'KOS': 'Kosovo'
}

# Also check alternative codes
alternative_codes = {
    'ROM': 'Romania (alt)',
    'SLO': 'Slovenia (alt)',
    'BOS': 'Bosnia (alt)',
    'MNG': 'Montenegro (alt)',
    'MNT': 'Montenegro (alt2)',
    'KSV': 'Kosovo (alt)',
    'XK': 'Kosovo (alt2)',
    'XKX': 'Kosovo (alt3)'
}

all_codes = {**missing_countries, **alternative_codes}

print("\nQuerying GDELT BigQuery for each country...")
print("-" * 100)

results = {}

for code, name in all_codes.items():
    print(f"\nChecking {code} ({name})...")

    # Query GDELT events table
    query = f"""
        SELECT COUNT(*) as event_count
        FROM `gdelt-bq.gdeltv2.events`
        WHERE (Actor1CountryCode = '{code}' OR Actor2CountryCode = '{code}')
          AND SQLDATE >= 20200101
          AND SQLDATE <= 20251231
    """

    try:
        query_job = client.query(query)
        result = query_job.result()

        for row in result:
            count = row.event_count
            results[code] = {'name': name, 'count': count}

            if count > 0:
                print(f"  FOUND: {count:,} events in BigQuery!")

                # Get sample events
                sample_query = f"""
                    SELECT SQLDATE, Actor1CountryCode, Actor1Name, Actor2CountryCode, Actor2Name, EventCode
                    FROM `gdelt-bq.gdeltv2.events`
                    WHERE (Actor1CountryCode = '{code}' OR Actor2CountryCode = '{code}')
                      AND SQLDATE >= 20200101
                    LIMIT 5
                """
                sample_job = client.query(sample_query)
                samples = sample_job.result()

                print(f"  Sample events:")
                for sample in samples:
                    print(f"    {sample.SQLDATE}: {sample.Actor1CountryCode}/{sample.Actor1Name} <-> {sample.Actor2CountryCode}/{sample.Actor2Name}")
            else:
                print(f"  NOT FOUND: 0 events in BigQuery")

    except Exception as e:
        print(f"  ERROR: {str(e)}")
        results[code] = {'name': name, 'count': None, 'error': str(e)}

# Summary
print("\n" + "=" * 100)
print("SUMMARY RESULTS")
print("=" * 100)

found_codes = []
still_missing = []

for code, data in results.items():
    if data.get('count', 0) > 0:
        found_codes.append(f"{code} ({data['name']}): {data['count']:,} events")
    else:
        still_missing.append(f"{code} ({data['name']})")

if found_codes:
    print("\nCOUNTRIES FOUND IN BIGQUERY:")
    print("-" * 100)
    for item in found_codes:
        print(f"  {item}")
    print("\n  >> THESE COUNTRIES EXIST IN GDELT BUT ARE MISSING FROM OUR LOCAL DATABASE!")
    print("  >> WE NEED TO COLLECT THIS DATA!")
else:
    print("\n  NO MISSING COUNTRIES FOUND IN BIGQUERY")

if still_missing:
    print("\nCOUNTRIES STILL MISSING:")
    print("-" * 100)
    for item in still_missing:
        print(f"  {item}")
    print("\n  >> These countries truly don't exist in GDELT 2020-2025")

# Check China-specific bilateral events
print("\n" + "=" * 100)
print("CHINA BILATERAL CHECK")
print("=" * 100)

for code, name in missing_countries.items():
    if results.get(code, {}).get('count', 0) > 0:
        query = f"""
            SELECT COUNT(*) as bilateral_count
            FROM `gdelt-bq.gdeltv2.events`
            WHERE ((Actor1CountryCode = '{code}' AND Actor2CountryCode = 'CHN')
                OR (Actor1CountryCode = 'CHN' AND Actor2CountryCode = '{code}'))
              AND SQLDATE >= 20200101
        """

        try:
            query_job = client.query(query)
            result = query_job.result()

            for row in result:
                bilateral = row.bilateral_count
                print(f"\n{name} ({code}):")
                print(f"  Total events: {results[code]['count']:,}")
                print(f"  China bilateral: {bilateral:,}")
                if bilateral > 0:
                    pct = 100 * bilateral / results[code]['count']
                    print(f"  Percentage with China: {pct:.1f}%")
        except Exception as e:
            print(f"  Error checking bilateral: {str(e)}")

print("\n" + "=" * 100)
print("Query complete")
print("=" * 100)

# Save results
import json
output = {
    'timestamp': datetime.now().isoformat(),
    'query_type': 'bigquery_verification',
    'countries_checked': list(all_codes.keys()),
    'results': results,
    'found_in_bigquery': [code for code, data in results.items() if data.get('count', 0) > 0],
    'still_missing': [code for code, data in results.items() if data.get('count', 0) == 0]
}

with open('analysis/bigquery_verification_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to: analysis/bigquery_verification_results.json")
