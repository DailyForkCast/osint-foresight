#!/usr/bin/env python3
"""
Design GKG Collection Strategy
Analyze existing events to determine optimal GKG collection approach
"""

import sqlite3
import json
from datetime import datetime

def analyze_existing_coverage():
    """Check what dates/countries we have in events table"""

    conn = sqlite3.connect(r'F:/OSINT_WAREHOUSE/osint_master.db', uri=True)
    cursor = conn.cursor()

    print("Analyzing existing GDELT Events coverage...\n")

    # Date range
    cursor.execute("""
        SELECT
            MIN(event_date) as earliest_date,
            MAX(event_date) as latest_date,
            COUNT(*) as total_events,
            COUNT(DISTINCT event_date) as unique_dates
        FROM gdelt_events
    """)
    date_range = cursor.fetchone()

    print(f"Date Coverage:")
    print(f"  Earliest: {date_range[0]}")
    print(f"  Latest: {date_range[1]}")
    print(f"  Total events: {date_range[2]:,}")
    print(f"  Unique dates: {date_range[3]:,}")

    # Country coverage - using action_geo_country_code
    cursor.execute("""
        SELECT
            action_geo_country_code,
            COUNT(*) as event_count,
            MIN(event_date) as earliest,
            MAX(event_date) as latest
        FROM gdelt_events
        WHERE action_geo_country_code IS NOT NULL
        GROUP BY action_geo_country_code
        ORDER BY event_count DESC
    """)
    countries = cursor.fetchall()

    print(f"\nCountry Coverage ({len(countries)} countries):")
    for country in countries[:10]:
        print(f"  {country[0]}: {country[1]:,} events ({country[2]} to {country[3]})")

    # Theme analysis - check if we have any themes
    cursor.execute("""
        SELECT COUNT(*)
        FROM gdelt_gkg
    """)
    gkg_count = cursor.fetchone()[0]
    print(f"\nCurrent GKG records: {gkg_count:,}")

    # Event types distribution
    cursor.execute("""
        SELECT
            event_root_code,
            COUNT(*) as count
        FROM gdelt_events
        GROUP BY event_root_code
        ORDER BY count DESC
        LIMIT 10
    """)
    event_types = cursor.fetchall()

    print(f"\nTop Event Types:")
    for et in event_types:
        print(f"  Code {et[0]}: {et[1]:,} events")

    # Save analysis
    analysis = {
        'analysis_date': datetime.now().isoformat(),
        'date_range': {
            'earliest': date_range[0],
            'latest': date_range[1],
            'total_events': date_range[2],
            'unique_dates': date_range[3]
        },
        'countries': [
            {
                'code': c[0],
                'events': c[1],
                'earliest': c[2],
                'latest': c[3]
            }
            for c in countries
        ],
        'current_gkg_records': gkg_count,
        'event_types': [{'code': et[0], 'count': et[1]} for et in event_types]
    }

    with open('analysis/gkg_strategy_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)

    conn.close()

    return analysis

def design_collection_strategy(analysis):
    """Design optimal GKG collection strategy"""

    print("\n" + "="*60)
    print("GKG COLLECTION STRATEGY DESIGN")
    print("="*60)

    earliest = analysis['date_range']['earliest']
    latest = analysis['date_range']['latest']
    total_events = analysis['date_range']['total_events']
    unique_dates = analysis['date_range']['unique_dates']

    print(f"\nBased on existing events coverage:")
    print(f"  Date range: {earliest} to {latest}")
    print(f"  {total_events:,} events across {unique_dates:,} days")

    # Cost estimation
    # BigQuery GKG is ~3 TB per single-day query (from test)
    # But we can optimize by:
    # 1. Filtering by date ranges
    # 2. Filtering by China-related themes/orgs upfront
    # 3. Using partition pruning

    print(f"\n--- COST ANALYSIS ---")
    print(f"Naive approach (scan all GKG data):")
    print(f"  ~3 TB scanned per day tested")
    print(f"  {unique_dates} days = ~{unique_dates * 3:,} TB total")
    print(f"  BigQuery cost: $5/TB after free 1TB = ${(unique_dates * 3 - 1) * 5:,}")
    print(f"  NOT FEASIBLE")

    print(f"\nOptimized approach (targeted collection):")
    print(f"  1. Use date partition pruning (already doing this)")
    print(f"  2. Filter by China-related keywords in WHERE clause")
    print(f"  3. Collect in batches by date range")
    print(f"  4. Focus on high-value themes:")
    print(f"     - SCIENCE_TECH (quantum, AI, semiconductors)")
    print(f"     - EDUCATION (universities, research)")
    print(f"     - TRADE/INVESTMENT")
    print(f"     - MILITARY/SECURITY")

    # Estimate optimized cost
    # With targeted filtering, expect to scan ~10% of full data
    estimated_tb = (unique_dates * 3 * 0.10)
    estimated_cost = max(0, (estimated_tb - 1) * 5)

    print(f"\n  Estimated data scanned: {estimated_tb:.1f} TB")
    print(f"  Estimated cost: ${estimated_cost:.2f}")
    print(f"  (after 1 TB free tier)")

    print(f"\n--- RECOMMENDED STRATEGY ---")
    print(f"Option 1: Full backfill")
    print(f"  - Collect GKG for all {unique_dates} days")
    print(f"  - Filter: China-related themes/orgs")
    print(f"  - Cost: ~${estimated_cost:.2f}")
    print(f"  - Time: ~{unique_dates / 10:.0f} minutes (10 days/min)")

    print(f"\nOption 2: Recent priority (2024-2025)")
    print(f"  - Collect GKG for recent 365 days only")
    recent_tb = (365 * 3 * 0.10)
    recent_cost = max(0, (recent_tb - 1) * 5)
    print(f"  - Filter: China-related themes/orgs")
    print(f"  - Cost: ~${recent_cost:.2f}")
    print(f"  - Time: ~37 minutes")

    print(f"\nOption 3: Strategic sample")
    print(f"  - Collect 1 week per month for trend analysis")
    sample_days = unique_dates // 4  # Roughly 1 week per month
    sample_tb = (sample_days * 3 * 0.10)
    sample_cost = max(0, (sample_tb - 1) * 5)
    print(f"  - Sample: {sample_days} days")
    print(f"  - Cost: ~${sample_cost:.2f}")
    print(f"  - Time: ~{sample_days / 10:.0f} minutes")

    strategy = {
        'date_range': {
            'earliest': earliest,
            'latest': latest,
            'unique_dates': unique_dates
        },
        'options': {
            'full_backfill': {
                'days': unique_dates,
                'estimated_tb': round(estimated_tb, 1),
                'estimated_cost_usd': round(estimated_cost, 2),
                'estimated_minutes': round(unique_dates / 10)
            },
            'recent_priority': {
                'days': 365,
                'estimated_tb': round(recent_tb, 1),
                'estimated_cost_usd': round(recent_cost, 2),
                'estimated_minutes': 37
            },
            'strategic_sample': {
                'days': sample_days,
                'estimated_tb': round(sample_tb, 1),
                'estimated_cost_usd': round(sample_cost, 2),
                'estimated_minutes': round(sample_days / 10)
            }
        },
        'target_filters': {
            'themes': [
                'SCIENCE',
                'TECH',
                'QUANTUM',
                'AI',
                'SEMICONDUCTOR',
                'UNIVERSITY',
                'RESEARCH',
                'EDUCATION',
                'TRADE',
                'INVESTMENT',
                'MILITARY',
                'SECURITY'
            ],
            'organizations': [
                'CHINA',
                'CHINESE',
                'UNIVERSITY',
                'HUAWEI',
                'TENCENT',
                'ALIBABA'
            ],
            'country_focus': [c['code'] for c in analysis['countries'][:20]]
        }
    }

    with open('analysis/gkg_collection_strategy.json', 'w') as f:
        json.dump(strategy, f, indent=2)

    print(f"\n--- KEY SEARCH CAPABILITIES ENABLED ---")
    print(f"After GKG collection, you can search by:")
    print(f"  - Themes: 'quantum research', 'semiconductor supply chain'")
    print(f"  - Organizations: specific universities, companies")
    print(f"  - Cross-reference with existing events")
    print(f"  - Sentiment/tone analysis")

    return strategy

if __name__ == '__main__':
    analysis = analyze_existing_coverage()
    strategy = design_collection_strategy(analysis)

    print("\n" + "="*60)
    print("Analysis complete. Files saved:")
    print("  - analysis/gkg_strategy_analysis.json")
    print("  - analysis/gkg_collection_strategy.json")
    print("="*60)
