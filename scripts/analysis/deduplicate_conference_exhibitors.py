#!/usr/bin/env python3
"""
Conference Exhibitor Deduplication Analysis
===========================================
Identifies unique companies vs total participation records.

Created: 2025-10-27
"""

import sqlite3
from pathlib import Path
from collections import defaultdict

DB_PATH = Path('F:/OSINT_WAREHOUSE/osint_master.db')

def analyze_deduplication():
    """Analyze unique companies vs total participations."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("="*70)
    print("CONFERENCE EXHIBITOR DEDUPLICATION ANALYSIS")
    print("="*70)

    # Get all Chinese exhibitors
    query = """
        SELECT
            entity_name,
            event_id,
            entity_country_code,
            chinese_entity
        FROM event_participants
        WHERE chinese_entity = 1
        ORDER BY entity_name, event_id
    """

    results = cursor.execute(query).fetchall()

    # Track participations per company
    company_participations = defaultdict(list)
    total_records = 0

    for entity_name, event_id, country_code, chinese_entity in results:
        company_participations[entity_name].append(event_id)
        total_records += 1

    # Count unique companies
    unique_companies = len(company_participations)

    print(f"\n[1] OVERVIEW")
    print("-" * 70)
    print(f"  Total participation records: {total_records}")
    print(f"  Unique Chinese companies: {unique_companies}")
    print(f"  Deduplication ratio: {total_records}/{unique_companies} = {total_records/unique_companies:.2f}x")

    # Find companies appearing at multiple conferences
    multi_conference = {name: events for name, events in company_participations.items() if len(events) > 1}

    print(f"\n[2] MULTI-CONFERENCE EXHIBITORS")
    print("-" * 70)
    print(f"  Companies at 1 conference: {unique_companies - len(multi_conference)}")
    print(f"  Companies at 2+ conferences: {len(multi_conference)}")

    # Detail multi-conference companies
    print(f"\n[3] COMPANIES AT MULTIPLE CONFERENCES")
    print("-" * 70)

    # Sort by number of conferences (descending)
    sorted_multi = sorted(multi_conference.items(), key=lambda x: len(x[1]), reverse=True)

    for company_name, event_ids in sorted_multi:
        event_count = len(event_ids)
        events_str = ", ".join(event_ids)
        print(f"  [{event_count}x] {company_name}")
        print(f"       Conferences: {events_str}")

    # Conference-level statistics
    print(f"\n[4] CONFERENCE-LEVEL PARTICIPATION")
    print("-" * 70)

    conference_query = """
        SELECT
            te.event_id,
            te.event_name,
            te.start_date,
            COUNT(ep.participant_id) as chinese_exhibitors
        FROM technology_events te
        LEFT JOIN event_participants ep ON te.event_id = ep.event_id AND ep.chinese_entity = 1
        GROUP BY te.event_id
        ORDER BY te.start_date DESC
    """

    conf_results = cursor.execute(conference_query).fetchall()

    for event_id, event_name, start_date, count in conf_results:
        print(f"  {event_name[:40]:40} | {start_date} | {count} exhibitors")

    # Top companies by conference count
    print(f"\n[5] TOP 10 MOST ACTIVE COMPANIES")
    print("-" * 70)

    top_10 = sorted_multi[:10]
    for i, (company_name, event_ids) in enumerate(top_10, 1):
        event_count = len(event_ids)
        print(f"  {i:2}. {company_name:35} | {event_count} conferences")

    # Summary statistics
    print(f"\n[6] SUMMARY STATISTICS")
    print("-" * 70)

    appearances = [len(events) for events in company_participations.values()]
    avg_appearances = sum(appearances) / len(appearances)
    max_appearances = max(appearances)

    print(f"  Average conferences per company: {avg_appearances:.2f}")
    print(f"  Maximum conferences (single company): {max_appearances}")
    print(f"  Companies appearing once: {sum(1 for a in appearances if a == 1)} ({sum(1 for a in appearances if a == 1)/len(appearances)*100:.1f}%)")
    print(f"  Companies appearing 2x: {sum(1 for a in appearances if a == 2)}")
    print(f"  Companies appearing 3x: {sum(1 for a in appearances if a == 3)}")
    print(f"  Companies appearing 4+x: {sum(1 for a in appearances if a >= 4)}")

    conn.close()

    print("\n" + "="*70)
    print("[OK] DEDUPLICATION ANALYSIS COMPLETE")
    print("="*70)

    return {
        'total_records': total_records,
        'unique_companies': unique_companies,
        'multi_conference': len(multi_conference),
        'avg_appearances': avg_appearances,
        'max_appearances': max_appearances
    }

if __name__ == '__main__':
    analyze_deduplication()
