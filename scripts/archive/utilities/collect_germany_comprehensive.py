#!/usr/bin/env python3
"""
Collect Germany-China Events - Comprehensive Geographic Search
Fifth largest European partner - 98K missing events
"""
from google.cloud import bigquery
import json
from datetime import datetime

project_id = "osint-foresight-2025"
client = bigquery.Client(project=project_id)

print("\n" + "=" * 100)
print("GERMANY-CHINA COMPREHENSIVE COLLECTION")
print("=" * 100)
print("Expected: 170,020 total events (currently have 72,283 - missing 97,737)")
print("=" * 100)

query = """
    SELECT
        GLOBALEVENTID, SQLDATE,
        Actor1Code, Actor1Name, Actor1CountryCode, Actor1Type1Code,
        Actor1Geo_CountryCode, Actor1Geo_FullName,
        Actor2Code, Actor2Name, Actor2CountryCode, Actor2Type1Code,
        Actor2Geo_CountryCode, Actor2Geo_FullName,
        IsRootEvent, EventCode, EventBaseCode, EventRootCode,
        QuadClass, GoldsteinScale, NumMentions, NumSources, NumArticles, AvgTone,
        ActionGeo_CountryCode, ActionGeo_FullName, SOURCEURL
    FROM `gdelt-bq.gdeltv2.events`
    WHERE (
        Actor1CountryCode IN ('DEU', 'DE', 'GER') OR Actor2CountryCode IN ('DEU', 'DE', 'GER')
        OR LOWER(Actor1Name) LIKE '%germany%' OR LOWER(Actor2Name) LIKE '%germany%'
        OR LOWER(Actor1Name) LIKE '%german%' OR LOWER(Actor2Name) LIKE '%german%'
        OR LOWER(Actor1Name) LIKE '%berlin%' OR LOWER(Actor2Name) LIKE '%berlin%'
        OR Actor1Geo_CountryCode IN ('DEU', 'DE', 'GER') OR Actor2Geo_CountryCode IN ('DEU', 'DE', 'GER')
        OR LOWER(Actor1Geo_FullName) LIKE '%germany%' OR LOWER(Actor2Geo_FullName) LIKE '%germany%'
        OR LOWER(Actor1Geo_FullName) LIKE '%berlin%' OR LOWER(Actor2Geo_FullName) LIKE '%berlin%'
        OR ActionGeo_CountryCode IN ('DEU', 'DE', 'GER')
        OR LOWER(ActionGeo_FullName) LIKE '%germany%'
        OR LOWER(ActionGeo_FullName) LIKE '%berlin%'
    )
    AND (Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN')
    AND SQLDATE >= 20200101 AND SQLDATE <= 20251231
    ORDER BY SQLDATE DESC
"""

print(f"\nQuerying BigQuery...")
results = list(client.query(query).result())
print(f"Found {len(results):,} Germany-China events")

events = []
field_stats = {'actor_country_code': 0, 'actor_name': 0, 'actor_geo_country_code': 0,
               'actor_geo_full_name': 0, 'action_geo_country_code': 0, 'action_geo_full_name': 0}

for row in results:
    matched_fields = []
    if row.Actor1CountryCode in ('DEU', 'DE', 'GER') or row.Actor2CountryCode in ('DEU', 'DE', 'GER'):
        matched_fields.append('actor_country_code')
        field_stats['actor_country_code'] += 1
    if (row.Actor1Name and any(x in row.Actor1Name.lower() for x in ['germany', 'german', 'berlin'])) or \
       (row.Actor2Name and any(x in row.Actor2Name.lower() for x in ['germany', 'german', 'berlin'])):
        matched_fields.append('actor_name')
        field_stats['actor_name'] += 1
    if row.Actor1Geo_CountryCode in ('DEU', 'DE', 'GER') or row.Actor2Geo_CountryCode in ('DEU', 'DE', 'GER'):
        matched_fields.append('actor_geo_country_code')
        field_stats['actor_geo_country_code'] += 1
    if (row.Actor1Geo_FullName and any(x in row.Actor1Geo_FullName.lower() for x in ['germany', 'berlin'])) or \
       (row.Actor2Geo_FullName and any(x in row.Actor2Geo_FullName.lower() for x in ['germany', 'berlin'])):
        matched_fields.append('actor_geo_full_name')
        field_stats['actor_geo_full_name'] += 1
    if row.ActionGeo_CountryCode in ('DEU', 'DE', 'GER'):
        matched_fields.append('action_geo_country_code')
        field_stats['action_geo_country_code'] += 1
    if row.ActionGeo_FullName and any(x in row.ActionGeo_FullName.lower() for x in ['germany', 'berlin']):
        matched_fields.append('action_geo_full_name')
        field_stats['action_geo_full_name'] += 1

    events.append({
        'global_event_id': row.GLOBALEVENTID, 'sqldate': row.SQLDATE,
        'actor1_code': row.Actor1Code, 'actor1_name': row.Actor1Name,
        'actor1_country_code': row.Actor1CountryCode, 'actor1_type1_code': row.Actor1Type1Code,
        'actor1_geo_country_code': row.Actor1Geo_CountryCode, 'actor1_geo_full_name': row.Actor1Geo_FullName,
        'actor2_code': row.Actor2Code, 'actor2_name': row.Actor2Name,
        'actor2_country_code': row.Actor2CountryCode, 'actor2_type1_code': row.Actor2Type1Code,
        'actor2_geo_country_code': row.Actor2Geo_CountryCode, 'actor2_geo_full_name': row.Actor2Geo_FullName,
        'is_root_event': row.IsRootEvent, 'event_code': row.EventCode,
        'event_base_code': row.EventBaseCode, 'event_root_code': row.EventRootCode,
        'quad_class': row.QuadClass, 'goldstein_scale': row.GoldsteinScale,
        'num_mentions': row.NumMentions, 'num_sources': row.NumSources,
        'num_articles': row.NumArticles, 'avg_tone': row.AvgTone,
        'action_geo_country_code': row.ActionGeo_CountryCode,
        'action_geo_full_name': row.ActionGeo_FullName,
        'source_url': row.SOURCEURL, 'matched_fields': matched_fields
    })

output_file = 'analysis/germany_china_comprehensive_events.json'
with open(output_file, 'w') as f:
    json.dump({'collection_timestamp': datetime.now().isoformat(), 'country': 'Germany',
               'total_events': len(events), 'field_statistics': field_stats, 'events': events}, f, indent=2)

print(f"\nData saved to: {output_file}")
print(f"\nField Match Statistics:")
for field, count in field_stats.items():
    pct = 100 * count / len(events) if len(events) > 0 else 0
    print(f"  {field:30s}: {count:,} ({pct:.1f}%)")
print(f"\nGERMANY COLLECTION COMPLETE: {len(events):,} events")
