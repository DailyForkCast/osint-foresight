#!/usr/bin/env python3
"""
Collect UK-China Events - Comprehensive Geographic Search
Second largest European partner - 225K missing events
"""
from google.cloud import bigquery
import json
from datetime import datetime

project_id = "osint-foresight-2025"
client = bigquery.Client(project=project_id)

print("\n" + "=" * 100)
print("UK-CHINA COMPREHENSIVE COLLECTION")
print("=" * 100)
print("Expected: 367,239 total events (currently have 141,650 - missing 225,589)")
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
        Actor1CountryCode IN ('GBR', 'GB', 'UK') OR Actor2CountryCode IN ('GBR', 'GB', 'UK')
        OR LOWER(Actor1Name) LIKE '%united kingdom%' OR LOWER(Actor2Name) LIKE '%united kingdom%'
        OR LOWER(Actor1Name) LIKE '%britain%' OR LOWER(Actor2Name) LIKE '%britain%'
        OR LOWER(Actor1Name) LIKE '%british%' OR LOWER(Actor2Name) LIKE '%british%'
        OR LOWER(Actor1Name) LIKE '%london%' OR LOWER(Actor2Name) LIKE '%london%'
        OR Actor1Geo_CountryCode IN ('GBR', 'GB', 'UK') OR Actor2Geo_CountryCode IN ('GBR', 'GB', 'UK')
        OR LOWER(Actor1Geo_FullName) LIKE '%united kingdom%' OR LOWER(Actor2Geo_FullName) LIKE '%united kingdom%'
        OR LOWER(Actor1Geo_FullName) LIKE '%britain%' OR LOWER(Actor2Geo_FullName) LIKE '%britain%'
        OR LOWER(Actor1Geo_FullName) LIKE '%london%' OR LOWER(Actor2Geo_FullName) LIKE '%london%'
        OR ActionGeo_CountryCode IN ('GBR', 'GB', 'UK')
        OR LOWER(ActionGeo_FullName) LIKE '%united kingdom%'
        OR LOWER(ActionGeo_FullName) LIKE '%britain%'
        OR LOWER(ActionGeo_FullName) LIKE '%london%'
    )
    AND (Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN')
    AND SQLDATE >= 20200101 AND SQLDATE <= 20251231
    ORDER BY SQLDATE DESC
"""

print(f"\nQuerying BigQuery...")
results = list(client.query(query).result())
print(f"Found {len(results):,} UK-China events")

events = []
field_stats = {'actor_country_code': 0, 'actor_name': 0, 'actor_geo_country_code': 0,
               'actor_geo_full_name': 0, 'action_geo_country_code': 0, 'action_geo_full_name': 0}

for row in results:
    matched_fields = []
    if row.Actor1CountryCode in ('GBR', 'GB', 'UK') or row.Actor2CountryCode in ('GBR', 'GB', 'UK'):
        matched_fields.append('actor_country_code')
        field_stats['actor_country_code'] += 1
    if (row.Actor1Name and any(x in row.Actor1Name.lower() for x in ['united kingdom', 'britain', 'british', 'london'])) or \
       (row.Actor2Name and any(x in row.Actor2Name.lower() for x in ['united kingdom', 'britain', 'british', 'london'])):
        matched_fields.append('actor_name')
        field_stats['actor_name'] += 1
    if row.Actor1Geo_CountryCode in ('GBR', 'GB', 'UK') or row.Actor2Geo_CountryCode in ('GBR', 'GB', 'UK'):
        matched_fields.append('actor_geo_country_code')
        field_stats['actor_geo_country_code'] += 1
    if (row.Actor1Geo_FullName and any(x in row.Actor1Geo_FullName.lower() for x in ['united kingdom', 'britain', 'london'])) or \
       (row.Actor2Geo_FullName and any(x in row.Actor2Geo_FullName.lower() for x in ['united kingdom', 'britain', 'london'])):
        matched_fields.append('actor_geo_full_name')
        field_stats['actor_geo_full_name'] += 1
    if row.ActionGeo_CountryCode in ('GBR', 'GB', 'UK'):
        matched_fields.append('action_geo_country_code')
        field_stats['action_geo_country_code'] += 1
    if row.ActionGeo_FullName and any(x in row.ActionGeo_FullName.lower() for x in ['united kingdom', 'britain', 'london']):
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

output_file = 'analysis/uk_china_comprehensive_events.json'
with open(output_file, 'w') as f:
    json.dump({'collection_timestamp': datetime.now().isoformat(), 'country': 'UK',
               'total_events': len(events), 'field_statistics': field_stats, 'events': events}, f, indent=2)

print(f"\nData saved to: {output_file}")
print(f"\nField Match Statistics:")
for field, count in field_stats.items():
    pct = 100 * count / len(events) if len(events) > 0 else 0
    print(f"  {field:30s}: {count:,} ({pct:.1f}%)")
print(f"\nUK COLLECTION COMPLETE: {len(events):,} events")
