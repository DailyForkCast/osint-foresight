#!/usr/bin/env python3
"""
Collect Romania-China Events Using ALL GDELT Geographic Fields
Comprehensive collection across 6 different geographic systems in GDELT
"""
from google.cloud import bigquery
import sqlite3
from datetime import datetime

project_id = "osint-foresight-2025"
client = bigquery.Client(project=project_id)

print("\n" + "=" * 100)
print("COMPREHENSIVE ROMANIA-CHINA EVENT COLLECTION")
print("=" * 100)
print("Using ALL GDELT geographic fields:")
print("  1. Actor Country Codes (Actor1CountryCode, Actor2CountryCode)")
print("  2. Actor Names (Actor1Name, Actor2Name)")
print("  3. Actor Geo Country Codes (Actor1Geo_CountryCode, Actor2Geo_CountryCode)")
print("  4. Actor Geo Full Names (Actor1Geo_FullName, Actor2Geo_FullName)")
print("  5. Action Geo Country Code (ActionGeo_CountryCode)")
print("  6. Action Geo Full Name (ActionGeo_FullName)")
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
        -- Method 1: Actor Country Codes
        Actor1CountryCode IN ('ROM', 'ROU') OR Actor2CountryCode IN ('ROM', 'ROU')
        -- Method 2: Actor Names
        OR LOWER(Actor1Name) LIKE '%romania%' OR LOWER(Actor2Name) LIKE '%romania%'
        -- Method 3: Actor Geo Country Codes
        OR Actor1Geo_CountryCode IN ('ROM', 'ROU') OR Actor2Geo_CountryCode IN ('ROM', 'ROU')
        -- Method 4: Actor Geo Full Names
        OR LOWER(Actor1Geo_FullName) LIKE '%romania%' OR LOWER(Actor2Geo_FullName) LIKE '%romania%'
        -- Method 5: Action Geo Country Code
        OR ActionGeo_CountryCode IN ('ROM', 'ROU')
        -- Method 6: Action Geo Full Name
        OR LOWER(ActionGeo_FullName) LIKE '%romania%'
    )
    -- At least one actor must be China
    AND (Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN')
    AND SQLDATE >= 20200101
    AND SQLDATE <= 20251231
    ORDER BY SQLDATE DESC
"""

print(f"\nQuerying BigQuery...")
print(f"Date range: 2020-01-01 to 2025-12-31")
print("=" * 100)

query_job = client.query(query)
results = list(query_job.result())

print(f"\nFound {len(results):,} Romania-China events using comprehensive geographic search")

if len(results) == 0:
    print("No events found. Exiting.")
    exit()

# Connect to local database
print(f"\nConnecting to local database...")
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# Create comprehensive table with all geographic fields
cursor.execute('''
    CREATE TABLE IF NOT EXISTS gdelt_events_comprehensive_geographic (
        global_event_id TEXT PRIMARY KEY,
        sqldate INTEGER,
        actor1_code TEXT,
        actor1_name TEXT,
        actor1_country_code TEXT,
        actor1_type1_code TEXT,
        actor1_geo_country_code TEXT,
        actor1_geo_full_name TEXT,
        actor2_code TEXT,
        actor2_name TEXT,
        actor2_country_code TEXT,
        actor2_type1_code TEXT,
        actor2_geo_country_code TEXT,
        actor2_geo_full_name TEXT,
        is_root_event INTEGER,
        event_code TEXT,
        event_base_code TEXT,
        event_root_code TEXT,
        quad_class INTEGER,
        goldstein_scale REAL,
        num_mentions INTEGER,
        num_sources INTEGER,
        num_articles INTEGER,
        avg_tone REAL,
        action_geo_country_code TEXT,
        action_geo_full_name TEXT,
        source_url TEXT,
        match_country TEXT,
        collection_timestamp TEXT
    )
''')

print(f"Inserting events into gdelt_events_comprehensive_geographic table...")

# Track which fields matched for each event
field_stats = {
    'actor_country_code': 0,
    'actor_name': 0,
    'actor_geo_country_code': 0,
    'actor_geo_full_name': 0,
    'action_geo_country_code': 0,
    'action_geo_full_name': 0
}

inserted = 0
skipped = 0

for row in results:
    # Determine which field(s) matched
    matched_fields = []

    if row.Actor1CountryCode in ('ROM', 'ROU') or row.Actor2CountryCode in ('ROM', 'ROU'):
        matched_fields.append('actor_country_code')
        field_stats['actor_country_code'] += 1

    if (row.Actor1Name and 'romania' in row.Actor1Name.lower()) or \
       (row.Actor2Name and 'romania' in row.Actor2Name.lower()):
        matched_fields.append('actor_name')
        field_stats['actor_name'] += 1

    if row.Actor1Geo_CountryCode in ('ROM', 'ROU') or row.Actor2Geo_CountryCode in ('ROM', 'ROU'):
        matched_fields.append('actor_geo_country_code')
        field_stats['actor_geo_country_code'] += 1

    if (row.Actor1Geo_FullName and 'romania' in row.Actor1Geo_FullName.lower()) or \
       (row.Actor2Geo_FullName and 'romania' in row.Actor2Geo_FullName.lower()):
        matched_fields.append('actor_geo_full_name')
        field_stats['actor_geo_full_name'] += 1

    if row.ActionGeo_CountryCode in ('ROM', 'ROU'):
        matched_fields.append('action_geo_country_code')
        field_stats['action_geo_country_code'] += 1

    if row.ActionGeo_FullName and 'romania' in row.ActionGeo_FullName.lower():
        matched_fields.append('action_geo_full_name')
        field_stats['action_geo_full_name'] += 1

    try:
        cursor.execute('''
            INSERT OR IGNORE INTO gdelt_events_comprehensive_geographic VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            row.GLOBALEVENTID,
            row.SQLDATE,
            row.Actor1Code,
            row.Actor1Name,
            row.Actor1CountryCode,
            row.Actor1Type1Code,
            row.Actor1Geo_CountryCode,
            row.Actor1Geo_FullName,
            row.Actor2Code,
            row.Actor2Name,
            row.Actor2CountryCode,
            row.Actor2Type1Code,
            row.Actor2Geo_CountryCode,
            row.Actor2Geo_FullName,
            row.IsRootEvent,
            row.EventCode,
            row.EventBaseCode,
            row.EventRootCode,
            row.QuadClass,
            row.GoldsteinScale,
            row.NumMentions,
            row.NumSources,
            row.NumArticles,
            row.AvgTone,
            row.ActionGeo_CountryCode,
            row.ActionGeo_FullName,
            row.SOURCEURL,
            'Romania',
            datetime.now().isoformat()
        ))

        if cursor.rowcount > 0:
            inserted += 1
        else:
            skipped += 1

    except Exception as e:
        print(f"Error inserting event {row.GLOBALEVENTID}: {e}")
        skipped += 1

conn.commit()

print(f"\nResults:")
print(f"  Inserted: {inserted:,} new events")
print(f"  Skipped: {skipped:,} (duplicates)")
print(f"  Total in BigQuery: {len(results):,}")

print(f"\nField Match Statistics:")
print("-" * 100)
for field, count in field_stats.items():
    print(f"  {field:30s}: {count:,} events")

# Show sample events from each matching method
print(f"\nSample events by matching method:")
print("-" * 100)

# Actor name matches
cursor.execute('''
    SELECT sqldate, actor1_name, actor1_country_code, actor2_name, actor2_country_code, source_url
    FROM gdelt_events_comprehensive_geographic
    WHERE match_country = 'Romania'
      AND (LOWER(actor1_name) LIKE '%romania%' OR LOWER(actor2_name) LIKE '%romania%')
    ORDER BY sqldate DESC
    LIMIT 3
''')
print("\n1. ACTOR NAME MATCHES:")
for row in cursor.fetchall():
    date, a1name, a1code, a2name, a2code, url = row
    print(f"   {date}: {a1name} ({a1code or 'NULL'}) <-> {a2name} ({a2code or 'NULL'})")
    if url:
        print(f"   Source: {url[:80]}...")

# Actor geo full name matches
cursor.execute('''
    SELECT sqldate, actor1_geo_full_name, actor2_geo_full_name, action_geo_full_name, source_url
    FROM gdelt_events_comprehensive_geographic
    WHERE match_country = 'Romania'
      AND (LOWER(actor1_geo_full_name) LIKE '%romania%'
           OR LOWER(actor2_geo_full_name) LIKE '%romania%'
           OR LOWER(action_geo_full_name) LIKE '%romania%')
    ORDER BY sqldate DESC
    LIMIT 3
''')
print("\n2. GEO FULL NAME MATCHES:")
for row in cursor.fetchall():
    date, a1geo, a2geo, actiongeo, url = row
    print(f"   {date}: A1Geo={a1geo}, A2Geo={a2geo}, ActionGeo={actiongeo}")
    if url:
        print(f"   Source: {url[:80]}...")

print("\n" + "=" * 100)
print("COLLECTION COMPLETE")
print("=" * 100)
print(f"Events stored in: gdelt_events_comprehensive_geographic table")
print(f"Country: Romania")
print(f"Total events: {inserted:,}")
print()
print("NOTE: This uses ALL GDELT geographic fields, not just country codes")
print("This captures the full scope of Romania-China events in GDELT")
print("=" * 100)

conn.close()
