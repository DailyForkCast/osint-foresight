#!/usr/bin/env python3
"""
Identify High-Value Dates for Targeted GKG Collection
Strategy: Only collect GKG for dates with significant China-related events
This reduces costs by ~90% while preserving high-value intelligence
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict

def analyze_event_density():
    """Find dates with high concentrations of China-related events"""

    conn = sqlite3.connect(r'F:/OSINT_WAREHOUSE/osint_master.db', uri=True)
    cursor = conn.cursor()

    print("Analyzing event density to identify high-value dates...\n")

    # Get event counts by date
    cursor.execute("""
        SELECT
            SUBSTR(event_date, 1, 8) as date,
            COUNT(*) as total_events,
            COUNT(CASE WHEN actor1_country_code = 'CHN'
                      OR actor2_country_code = 'CHN' THEN 1 END) as china_events,
            COUNT(CASE WHEN event_root_code IN ('14', '15', '16', '17', '18', '19', '20') THEN 1 END) as conflict_events,
            COUNT(CASE WHEN event_root_code IN ('03', '04', '05', '06') THEN 1 END) as cooperation_events,
            AVG(goldstein_scale) as avg_goldstein,
            AVG(num_mentions) as avg_mentions
        FROM gdelt_events
        GROUP BY SUBSTR(event_date, 1, 8)
        ORDER BY date DESC
    """)

    results = cursor.fetchall()

    # Analyze patterns
    date_analysis = []
    for row in results:
        date, total, china, conflict, coop, goldstein, mentions = row

        # Calculate importance score
        # Higher score = more valuable for GKG collection
        importance_score = (
            china * 2 +  # China events weighted 2x
            conflict * 1.5 +  # Conflict events weighted 1.5x
            coop * 1.2 +  # Cooperation events weighted 1.2x
            (mentions or 0) * 0.1  # Media attention
        )

        date_analysis.append({
            'date': date,
            'total_events': total,
            'china_events': china,
            'conflict_events': conflict,
            'cooperation_events': coop,
            'avg_goldstein': goldstein,
            'avg_mentions': mentions,
            'importance_score': importance_score
        })

    # Sort by importance
    date_analysis.sort(key=lambda x: x['importance_score'], reverse=True)

    print(f"Total dates with events: {len(date_analysis):,}\n")

    # Show top dates
    print("Top 20 highest-value dates for GKG collection:")
    print(f"{'Date':<12} {'China Evt':<10} {'Total Evt':<10} {'Conflict':<10} {'Score':<10}")
    print("-" * 60)
    for i, d in enumerate(date_analysis[:20], 1):
        print(f"{d['date']:<12} {d['china_events']:<10} {d['total_events']:<10} "
              f"{d['conflict_events']:<10} {d['importance_score']:<10.0f}")

    # Strategy options
    print("\n" + "="*60)
    print("COST REDUCTION STRATEGIES")
    print("="*60)

    # Option 1: Top N days only
    for top_n in [10, 20, 50, 100]:
        cost = top_n * 8.86
        china_events = sum(d['china_events'] for d in date_analysis[:top_n])
        print(f"\nOption: Top {top_n} highest-value days")
        print(f"  Cost: ${cost:.2f} (vs $260.77 for 30 days)")
        print(f"  China events covered: {china_events:,}")
        print(f"  Savings: {(1 - cost/260.77) * 100:.1f}%")

    # Option 2: Sample strategy (1st and 15th of each month)
    monthly_samples = []
    by_month = defaultdict(list)
    for d in date_analysis:
        month = d['date'][:6]
        by_month[month].append(d)

    for month, days in by_month.items():
        # Get closest to 1st and 15th
        days_sorted = sorted(days, key=lambda x: x['date'])
        if days_sorted:
            # Pick highest-value day from first half
            first_half = [d for d in days_sorted if int(d['date'][6:8]) <= 15]
            second_half = [d for d in days_sorted if int(d['date'][6:8]) > 15]

            if first_half:
                monthly_samples.append(max(first_half, key=lambda x: x['importance_score']))
            if second_half:
                monthly_samples.append(max(second_half, key=lambda x: x['importance_score']))

    sample_cost = len(monthly_samples) * 8.86
    sample_china = sum(d['china_events'] for d in monthly_samples)
    print(f"\nOption: Strategic monthly sampling (2 days/month)")
    print(f"  Days: {len(monthly_samples)}")
    print(f"  Cost: ${sample_cost:.2f}")
    print(f"  China events covered: {sample_china:,}")
    print(f"  Savings: {(1 - sample_cost/18731.48) * 100:.1f}% vs full backfill")

    # Option 3: Recent focus only (last 3 months)
    recent_cutoff = "20240801"
    recent_dates = [d for d in date_analysis if d['date'] >= recent_cutoff]

    # Take top 10 from recent period
    recent_top = sorted(recent_dates, key=lambda x: x['importance_score'], reverse=True)[:10]
    recent_cost = len(recent_top) * 8.86
    recent_china = sum(d['china_events'] for d in recent_top)

    print(f"\nOption: Recent high-value only (Aug 2024+, top 10 days)")
    print(f"  Days: {len(recent_top)}")
    print(f"  Cost: ${recent_cost:.2f}")
    print(f"  China events covered: {recent_china:,}")
    print(f"  Dates: {', '.join(d['date'] for d in recent_top[:5])}...")

    # Option 4: Event threshold strategy
    threshold = 500  # Only collect days with 500+ China events
    threshold_dates = [d for d in date_analysis if d['china_events'] >= threshold]
    threshold_cost = len(threshold_dates) * 8.86
    threshold_china = sum(d['china_events'] for d in threshold_dates)

    print(f"\nOption: Event threshold (>={threshold} China events/day)")
    print(f"  Days: {len(threshold_dates)}")
    print(f"  Cost: ${threshold_cost:.2f}")
    print(f"  China events covered: {threshold_china:,}")

    # Save analysis
    report = {
        'analysis_date': datetime.now().isoformat(),
        'total_dates': len(date_analysis),
        'strategies': {
            'top_10_days': {
                'days': 10,
                'cost_usd': 10 * 8.86,
                'dates': [d['date'] for d in date_analysis[:10]],
                'china_events': sum(d['china_events'] for d in date_analysis[:10])
            },
            'top_20_days': {
                'days': 20,
                'cost_usd': 20 * 8.86,
                'dates': [d['date'] for d in date_analysis[:20]],
                'china_events': sum(d['china_events'] for d in date_analysis[:20])
            },
            'top_50_days': {
                'days': 50,
                'cost_usd': 50 * 8.86,
                'dates': [d['date'] for d in date_analysis[:50]],
                'china_events': sum(d['china_events'] for d in date_analysis[:50])
            },
            'monthly_sample': {
                'days': len(monthly_samples),
                'cost_usd': len(monthly_samples) * 8.86,
                'dates': [d['date'] for d in monthly_samples],
                'china_events': sample_china
            },
            'recent_top_10': {
                'days': len(recent_top),
                'cost_usd': recent_cost,
                'dates': [d['date'] for d in recent_top],
                'china_events': recent_china
            },
            'threshold_500': {
                'days': len(threshold_dates),
                'cost_usd': threshold_cost,
                'dates': [d['date'] for d in threshold_dates],
                'china_events': threshold_china
            }
        },
        'all_dates_ranked': date_analysis[:200]  # Top 200 for reference
    }

    with open('analysis/gkg_targeted_collection_strategy.json', 'w') as f:
        json.dump(report, f, indent=2)

    print("\n" + "="*60)
    print("RECOMMENDATION")
    print("="*60)
    print("\nStart with: Top 10 highest-value days (~$88.60)")
    print("  - Targets dates with most China-related activity")
    print("  - Tests GKG data quality at minimal cost")
    print("  - Can expand if valuable")
    print("\nNext step: Review top dates and select specific high-value periods")
    print("  - Policy announcements")
    print("  - Major events (Belt & Road forums, etc.)")
    print("  - Crisis periods")

    print(f"\nSaved: analysis/gkg_targeted_collection_strategy.json")

    conn.close()

if __name__ == '__main__':
    analyze_event_density()
