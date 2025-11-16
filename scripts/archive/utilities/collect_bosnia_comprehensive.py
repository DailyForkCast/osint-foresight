#!/usr/bin/env python3
"""
Collect Bosnia and Herzegovina-China Events - Comprehensive Geographic Search
"""
from google.cloud import bigquery
import json
from datetime import datetime

project_id = "osint-foresight-2025"
client = bigquery.Client(project=project_id)

print("\n" + "=" * 100)
print("BOSNIA AND HERZEGOVINA-CHINA COMPREHENSIVE COLLECTION")
print("=" * 100)

# Comprehensive query using ALL geographic fields
query = """
    SELECT
        GLOBALEVENTID,
        SQLDATE,
        Actor1Code, Actor1Name, Actor1CountryCode, Actor1Type1Code,
        Actor1Geo_CountryCode, Actor1Geo_FullName,
        Actor2Code, Actor2Name, Actor2CountryCode, Actor2Type1Code,
        Actor2Geo_CountryCode, Actor2Geo_FullName,
        IsRootEvent, EventCode, EventBaseCode, EventRootCode,
        QuadClass, GoldsteinScale, NumMentions, NumSources, NumArticles,
        AvgTone,
        ActionGeo_CountryCode, ActionGeo_FullName,
        SOURCEURL
    FROM `gdelt-bq.gdeltv2.events`
    WHERE (
        -- Country codes
        Actor1CountryCode IN ('BIH', 'BOS') OR Actor2CountryCode IN ('BIH', 'BOS')
        -- Actor names
        OR LOWER(Actor1Name) LIKE '%bosnia%' OR LOWER(Actor2Name) LIKE '%bosnia%'
        OR LOWER(Actor1Name) LIKE '%bosnian%' OR LOWER(Actor2Name) LIKE '%bosnian%'
        OR LOWER(Actor1Name) LIKE '%herzegovina%' OR LOWER(Actor2Name) LIKE '%herzegovina%'
        -- Actor geo codes
        OR Actor1Geo_CountryCode IN ('BIH', 'BOS') OR Actor2Geo_CountryCode IN ('BIH', 'BOS')
        -- Actor geo full names
        OR LOWER(Actor1Geo_FullName) LIKE '%bosnia%' OR LOWER(Actor2Geo_FullName) LIKE '%bosnia%'
        OR LOWER(Actor1Geo_FullName) LIKE '%herzegovina%' OR LOWER(Actor2Geo_FullName) LIKE '%herzegovina%'
        -- Action geo code
        OR ActionGeo_CountryCode IN ('BIH', 'BOS')
        -- Action geo full name
        OR LOWER(ActionGeo_FullName) LIKE '%bosnia%'
        OR LOWER(ActionGeo_FullName) LIKE '%herzegovina%'
    )
    AND (Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN')
    AND SQLDATE >= 20200101
    AND SQLDATE <= 20251231
    ORDER BY SQLDATE DESC
"""

print(f"Querying BigQuery for Bosnia-China events...")
query_job = client.query(query)
results = list(query_job.result())

print(f"Found {len(results):,} Bosnia-China events")

# Convert to JSON-serializable format
events = []
field_stats = {
    'actor_country_code': 0,
    'actor_name': 0,
    'actor_geo_country_code': 0,
    'actor_geo_full_name': 0,
    'action_geo_country_code': 0,
    'action_geo_full_name': 0
}

for row in results:
    # Track which fields matched
    matched_fields = []

    if row.Actor1CountryCode in ('BIH', 'BOS') or row.Actor2CountryCode in ('BIH', 'BOS'):
        matched_fields.append('actor_country_code')
        field_stats['actor_country_code'] += 1

    if (row.Actor1Name and ('bosnia' in row.Actor1Name.lower() or 'bosnian' in row.Actor1Name.lower() or 'herzegovina' in row.Actor1Name.lower())) or \
       (row.Actor2Name and ('bosnia' in row.Actor2Name.lower() or 'bosnian' in row.Actor2Name.lower() or 'herzegovina' in row.Actor2Name.lower())):
        matched_fields.append('actor_name')
        field_stats['actor_name'] += 1

    if row.Actor1Geo_CountryCode in ('BIH', 'BOS') or row.Actor2Geo_CountryCode in ('BIH', 'BOS'):
        matched_fields.append('actor_geo_country_code')
        field_stats['actor_geo_country_code'] += 1

    if (row.Actor1Geo_FullName and ('bosnia' in row.Actor1Geo_FullName.lower() or 'herzegovina' in row.Actor1Geo_FullName.lower())) or \
       (row.Actor2Geo_FullName and ('bosnia' in row.Actor2Geo_FullName.lower() or 'herzegovina' in row.Actor2Geo_FullName.lower())):
        matched_fields.append('actor_geo_full_name')
        field_stats['actor_geo_full_name'] += 1

    if row.ActionGeo_CountryCode in ('BIH', 'BOS'):
        matched_fields.append('action_geo_country_code')
        field_stats['action_geo_country_code'] += 1

    if row.ActionGeo_FullName and ('bosnia' in row.ActionGeo_FullName.lower() or 'herzegovina' in row.ActionGeo_FullName.lower()):
        matched_fields.append('action_geo_full_name')
        field_stats['action_geo_full_name'] += 1

    event = {
        'global_event_id': row.GLOBALEVENTID,
        'sqldate': row.SQLDATE,
        'actor1_code': row.Actor1Code,
        'actor1_name': row.Actor1Name,
        'actor1_country_code': row.Actor1CountryCode,
        'actor1_type1_code': row.Actor1Type1Code,
        'actor1_geo_country_code': row.Actor1Geo_CountryCode,
        'actor1_geo_full_name': row.Actor1Geo_FullName,
        'actor2_code': row.Actor2Code,
        'actor2_name': row.Actor2Name,
        'actor2_country_code': row.Actor2CountryCode,
        'actor2_type1_code': row.Actor2Type1Code,
        'actor2_geo_country_code': row.Actor2Geo_CountryCode,
        'actor2_geo_full_name': row.Actor2Geo_FullName,
        'is_root_event': row.IsRootEvent,
        'event_code': row.EventCode,
        'event_base_code': row.EventBaseCode,
        'event_root_code': row.EventRootCode,
        'quad_class': row.QuadClass,
        'goldstein_scale': row.GoldsteinScale,
        'num_mentions': row.NumMentions,
        'num_sources': row.NumSources,
        'num_articles': row.NumArticles,
        'avg_tone': row.AvgTone,
        'action_geo_country_code': row.ActionGeo_CountryCode,
        'action_geo_full_name': row.ActionGeo_FullName,
        'source_url': row.SOURCEURL,
        'matched_fields': matched_fields
    }
    events.append(event)

# Save to JSON
output = {
    'collection_timestamp': datetime.now().isoformat(),
    'country': 'Bosnia and Herzegovina',
    'total_events': len(events),
    'field_statistics': field_stats,
    'events': events
}

output_file = 'analysis/bosnia_china_comprehensive_events.json'
with open(output_file, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nData saved to: {output_file}")
print(f"\nField Match Statistics:")
print("-" * 100)
for field, count in field_stats.items():
    pct = 100 * count / len(events) if len(events) > 0 else 0
    print(f"  {field:30s}: {count:,} events ({pct:.1f}%)")

print("\n" + "=" * 100)
print("BOSNIA AND HERZEGOVINA COLLECTION COMPLETE")
print("=" * 100)
print(f"Total events: {len(events):,}")
print(f"File: {output_file}")
print("=" * 100)
