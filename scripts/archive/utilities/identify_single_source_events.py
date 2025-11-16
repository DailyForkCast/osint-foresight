#!/usr/bin/env python3
"""
Identify and remediate single-source events
"""

import sqlite3
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect("F:/OSINT_WAREHOUSE/osint_master.db", timeout=30.0)
cur = conn.cursor()

print("="*80)
print("SINGLE-SOURCE EVENTS INVESTIGATION")
print("="*80 + "\n")

# Find events with only 1 source
cur.execute("""
    SELECT
        cl.linked_record_id,
        COUNT(*) as source_count,
        be.event_title,
        be.event_year,
        be.event_category,
        be.country_code
    FROM citation_links cl
    JOIN bilateral_events be ON cl.linked_record_id = be.event_id
    GROUP BY cl.linked_record_id
    HAVING COUNT(*) < 2
    ORDER BY be.event_year DESC, be.country_code
""")

single_source_events = cur.fetchall()

print(f"Found {len(single_source_events)} events with single source:\n")

print(f"{'Event ID':<40} {'Year':<6} {'Country':<8} {'Category':<25} {'Title':<50}")
print("-" * 140)

for event_id, sources, title, year, category, country in single_source_events:
    title_short = (title[:47] + '...') if len(title) > 50 else title
    print(f"{event_id:<40} {year:<6} {country:<8} {category:<25} {title_short:<50}")

# Check if these are recently added events
print("\n" + "="*80)
print("ANALYSIS: Are these newly integrated academic events?")
print("="*80 + "\n")

academic_events_single_source = [e for e in single_source_events if e[4] in ['academic_collaboration', 'academic_restriction']]

print(f"Academic events with single source: {len(academic_events_single_source)}/{len(single_source_events)}")

if len(academic_events_single_source) > 0:
    print("\n✓ Explanation: Academic events just integrated (2025-10-23)")
    print("  These were added with event() helper function that creates 1 citation")
    print("  Need to add second corroborating source for each\n")

# Recommend remediation
print("="*80)
print("REMEDIATION RECOMMENDATIONS")
print("="*80 + "\n")

print("To achieve 100% multi-source coverage, add second source for:\n")

for event_id, sources, title, year, category, country in single_source_events:
    print(f"  {event_id}")
    print(f"    Title: {title}")
    print(f"    Need: 1 additional corroborating source")
    print()

print("Recommended action: Create add_second_sources.py to systematically")
print("add corroborating sources for these 14 events.")

conn.close()
