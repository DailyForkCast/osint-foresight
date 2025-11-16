#!/usr/bin/env python3
"""
Collect Romania-China Events by Actor NAME (not country code)
GDELT fails to assign country codes to Romania, so we need name-based matching
"""
from google.cloud import bigquery
import sqlite3
from datetime import datetime

project_id = "osint-foresight-2025"
client = bigquery.Client(project=project_id)

print("\n" + "=" * 100)
print("COLLECTING ROMANIA-CHINA EVENTS BY ACTOR NAME")
print("=" * 100)
print(f"Reason: GDELT assigns CHN code to China but NULL code to Romania")
print(f"Solution: Match on actor NAME containing 'romania' instead")
print("=" * 100)

# Query for Romania-China events by actor name
query = """
    SELECT
        SQLDATE,
        Actor1Code, Actor1Name, Actor1CountryCode, Actor1Type1Code,
        Actor2Code, Actor2Name, Actor2CountryCode, Actor2Type1Code,
        IsRootEvent, EventCode, EventBaseCode, EventRootCode,
        QuadClass, GoldsteinScale, NumMentions, NumSources, NumArticles,
        AvgTone,
        SOURCEURL
    FROM `gdelt-bq.gdeltv2.events`
    WHERE (
        -- Romania as Actor1 or Actor2 (by name, since country code is NULL)
        (LOWER(Actor1Name) LIKE '%romania%' OR LOWER(Actor2Name) LIKE '%romania%')
        -- AND China as Actor1 or Actor2 (by country code)
        AND (Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN')
    )
    AND SQLDATE >= 20200101
    AND SQLDATE <= 20251231
    ORDER BY SQLDATE DESC
"""

print(f"\nQuerying BigQuery...")
print(f"Date range: 2020-01-01 to 2025-12-31")
print("=" * 100)

query_job = client.query(query)
results = list(query_job.result())

print(f"\nFound {len(results):,} Romania-China events")

if len(results) == 0:
    print("No events found. Exiting.")
    exit()

# Connect to local database
print(f"\nConnecting to local database...")
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# Create a special table for name-matched events if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS gdelt_events_name_matched (
        sqldate INTEGER,
        actor1_code TEXT,
        actor1_name TEXT,
        actor1_country_code TEXT,
        actor1_type1_code TEXT,
        actor2_code TEXT,
        actor2_name TEXT,
        actor2_country_code TEXT,
        actor2_type1_code TEXT,
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
        source_url TEXT,
        match_type TEXT,
        PRIMARY KEY (sqldate, actor1_code, actor2_code, event_code, source_url)
    )
''')

print(f"Inserting events into gdelt_events_name_matched table...")

inserted = 0
skipped = 0

for row in results:
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO gdelt_events_name_matched VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            row.SQLDATE,
            row.Actor1Code,
            row.Actor1Name,
            row.Actor1CountryCode,
            row.Actor1Type1Code,
            row.Actor2Code,
            row.Actor2Name,
            row.Actor2CountryCode,
            row.Actor2Type1Code,
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
            row.SOURCEURL,
            'romania_name_match'
        ))

        if cursor.rowcount > 0:
            inserted += 1
        else:
            skipped += 1

    except Exception as e:
        print(f"Error inserting event: {e}")
        skipped += 1

conn.commit()

print(f"\nResults:")
print(f"  Inserted: {inserted:,} new events")
print(f"  Skipped: {skipped:,} (duplicates)")
print(f"  Total in BigQuery: {len(results):,}")

# Show sample events
print(f"\nSample events:")
print("-" * 100)
cursor.execute('''
    SELECT sqldate, actor1_name, actor1_country_code, actor2_name, actor2_country_code, source_url
    FROM gdelt_events_name_matched
    WHERE match_type = 'romania_name_match'
    ORDER BY sqldate DESC
    LIMIT 10
''')

for row in cursor.fetchall():
    date, a1name, a1code, a2name, a2code, url = row
    print(f"{date}: {a1name} ({a1code or 'NULL'}) <-> {a2name} ({a2code or 'NULL'})")
    if url:
        print(f"  Source: {url[:80]}...")

print("\n" + "=" * 100)
print("COLLECTION COMPLETE")
print("=" * 100)
print(f"Events stored in: gdelt_events_name_matched table")
print(f"Match type: romania_name_match")
print()
print("NOTE: These events have Romania in actor NAME but NULL country code")
print("This is a GDELT entity recognition limitation, not a data collection error.")
print("=" * 100)

conn.close()
