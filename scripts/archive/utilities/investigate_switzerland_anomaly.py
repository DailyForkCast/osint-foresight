#!/usr/bin/env python3
"""
Investigate Switzerland Anomaly - 8.6M events seems impossible
"""
from google.cloud import bigquery

project_id = "osint-foresight-2025"
client = bigquery.Client(project=project_id)

print("\n" + "=" * 100)
print("SWITZERLAND ANOMALY INVESTIGATION")
print("=" * 100)

# Check basic Switzerland-China count with ONLY country codes
query1 = """
    SELECT COUNT(DISTINCT GLOBALEVENTID) as count
    FROM `gdelt-bq.gdeltv2.events`
    WHERE (Actor1CountryCode IN ('CHE', 'CH') OR Actor2CountryCode IN ('CHE', 'CH'))
      AND (Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN')
      AND SQLDATE >= 20200101
      AND SQLDATE <= 20251231
"""

print("\nTest 1: Country codes only (CHE, CH)")
result = client.query(query1).result()
for row in result:
    print(f"  Events: {row.count:,}")

# Check what happens when we add name searches
query2 = """
    SELECT COUNT(DISTINCT GLOBALEVENTID) as count
    FROM `gdelt-bq.gdeltv2.events`
    WHERE (
        LOWER(Actor1Name) LIKE '%switzerland%' OR LOWER(Actor2Name) LIKE '%switzerland%'
        OR LOWER(Actor1Name) LIKE '%swiss%' OR LOWER(Actor2Name) LIKE '%swiss%'
    )
    AND (Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN')
    AND SQLDATE >= 20200101
    AND SQLDATE <= 20251231
"""

print("\nTest 2: Name search only (switzerland, swiss)")
result = client.query(query2).result()
for row in result:
    print(f"  Events: {row.count:,}")

# Sample some events to see what's being matched
query3 = """
    SELECT
        GLOBALEVENTID,
        SQLDATE,
        Actor1Name,
        Actor2Name,
        Actor1CountryCode,
        Actor2CountryCode,
        ActionGeo_FullName
    FROM `gdelt-bq.gdeltv2.events`
    WHERE (
        LOWER(Actor1Name) LIKE '%swiss%' OR LOWER(Actor2Name) LIKE '%swiss%'
    )
    AND (Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN')
    AND SQLDATE >= 20200101
    LIMIT 20
"""

print("\nTest 3: Sample events matching 'swiss' in actor names")
print("-" * 100)
result = client.query(query3).result()
for row in result:
    print(f"Date: {row.SQLDATE} | {row.Actor1Name} ({row.Actor1CountryCode}) <-> {row.Actor2Name} ({row.Actor2CountryCode})")

print("\n" + "=" * 100)
print("If Test 2 shows millions of events, 'swiss' is matching false positives")
print("(e.g., 'Swiss Re', 'Credit Suisse', etc. - financial institutions)")
print("=" * 100)
