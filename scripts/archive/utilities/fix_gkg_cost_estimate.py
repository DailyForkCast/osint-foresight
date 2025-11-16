#!/usr/bin/env python3
"""
Fix GKG Cost Estimate
Recalculate based on actual unique DAYS, not timestamps
"""

import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect(r'F:/OSINT_WAREHOUSE/osint_master.db', uri=True)
cursor = conn.cursor()

print("Recalculating GKG cost estimate...\n")

# Get actual unique DAYS (first 8 chars = YYYYMMDD)
cursor.execute("""
    SELECT
        MIN(SUBSTR(event_date, 1, 8)) as earliest_day,
        MAX(SUBSTR(event_date, 1, 8)) as latest_day,
        COUNT(DISTINCT SUBSTR(event_date, 1, 8)) as unique_days,
        COUNT(*) as total_events
    FROM gdelt_events
""")
result = cursor.fetchone()

earliest = result[0]
latest = result[1]
unique_days = result[2]
total_events = result[3]

print(f"Date Coverage:")
print(f"  Earliest: {earliest} (YYYYMMDD)")
print(f"  Latest: {latest} (YYYYMMDD)")
print(f"  Unique days: {unique_days:,}")
print(f"  Total events: {total_events:,}")

# Calculate actual date range in days
earliest_dt = datetime.strptime(earliest, "%Y%m%d")
latest_dt = datetime.strptime(latest, "%Y%m%d")
calendar_days = (latest_dt - earliest_dt).days + 1

print(f"  Calendar days span: {calendar_days:,}")
print(f"  Coverage ratio: {unique_days / calendar_days * 100:.1f}%")

# Recalculate costs
# From test: 3 TB scanned for one day query
# With 10% filtering efficiency for China-related content

print(f"\n" + "="*60)
print("CORRECTED COST ESTIMATES")
print("="*60)

print(f"\nTest query metrics:")
print(f"  - Scanned 3 TB for single-day query")
print(f"  - With China/university filters")
print(f"  - Returned 0 records (Nov 1 might be future/invalid date)")

print(f"\nOption 1: Full backfill ({unique_days} days)")
full_tb = unique_days * 3 * 0.10  # 10% after filtering
full_cost = max(0, (full_tb - 1) * 5)  # $5/TB after 1 TB free
print(f"  Estimated scan: {full_tb:.1f} TB")
print(f"  Estimated cost: ${full_cost:,.2f}")
print(f"  Time estimate: ~{unique_days / 10:.0f} minutes (10 days/min)")

print(f"\nOption 2: Recent 365 days only")
recent_days = min(365, unique_days)
recent_tb = recent_days * 3 * 0.10
recent_cost = max(0, (recent_tb - 1) * 5)
print(f"  Days: {recent_days}")
print(f"  Estimated scan: {recent_tb:.1f} TB")
print(f"  Estimated cost: ${recent_cost:,.2f}")
print(f"  Time estimate: ~{recent_days / 10:.0f} minutes")

print(f"\nOption 3: Strategic sample (1 week per month)")
sample_days = unique_days // 4  # Roughly 1 week per month
sample_tb = sample_days * 3 * 0.10
sample_cost = max(0, (sample_tb - 1) * 5)
print(f"  Days: {sample_days}")
print(f"  Estimated scan: {sample_tb:.1f} TB")
print(f"  Estimated cost: ${sample_cost:,.2f}")
print(f"  Time estimate: ~{sample_days / 10:.0f} minutes")

print(f"\nOption 4: Minimal test (30 days)")
test_days = 30
test_tb = test_days * 3 * 0.10
test_cost = max(0, (test_tb - 1) * 5)
print(f"  Days: {test_days}")
print(f"  Estimated scan: {test_tb:.1f} TB")
print(f"  Estimated cost: ${test_cost:,.2f}")
print(f"  Time estimate: ~{test_days / 10:.0f} minutes")

# Check specific high-value periods
print(f"\n" + "="*60)
print("RECOMMENDED APPROACH")
print("="*60)

print(f"\nGiven 187K timestamps but only {unique_days} actual days:")
print(f"  - Our events are densely sampled (multiple events per day)")
print(f"  - GKG queries are partitioned by day, not timestamp")
print(f"  - Actual cost will be based on {unique_days} days, not 187K")

print(f"\nRECOMMENDATION: Start with Option 4 (30-day test)")
print(f"  1. Test on recent 30 days ({test_cost:.2f} cost)")
print(f"  2. Verify data quality and coverage")
print(f"  3. If useful, expand to Option 2 (365 days)")
print(f"  4. Avoid Option 1 (full backfill) unless critical need")

# Save corrected estimates
strategy = {
    'analysis_date': datetime.now().isoformat(),
    'date_coverage': {
        'earliest': earliest,
        'latest': latest,
        'unique_days': unique_days,
        'calendar_days': calendar_days,
        'coverage_ratio': round(unique_days / calendar_days * 100, 1)
    },
    'cost_estimates': {
        'full_backfill': {
            'days': unique_days,
            'estimated_tb': round(full_tb, 1),
            'estimated_cost_usd': round(full_cost, 2),
            'estimated_minutes': round(unique_days / 10)
        },
        'recent_365': {
            'days': recent_days,
            'estimated_tb': round(recent_tb, 1),
            'estimated_cost_usd': round(recent_cost, 2),
            'estimated_minutes': round(recent_days / 10)
        },
        'strategic_sample': {
            'days': sample_days,
            'estimated_tb': round(sample_tb, 1),
            'estimated_cost_usd': round(sample_cost, 2),
            'estimated_minutes': round(sample_days / 10)
        },
        'test_30_days': {
            'days': test_days,
            'estimated_tb': round(test_tb, 1),
            'estimated_cost_usd': round(test_cost, 2),
            'estimated_minutes': round(test_days / 10)
        }
    },
    'recommendation': 'test_30_days',
    'notes': [
        'Start with 30-day test to validate approach',
        'GKG queries scan ~3TB per day with filtering',
        'Free tier (1TB) covers ~3 days of queries',
        'After validation, expand to 365-day collection'
    ]
}

with open('analysis/gkg_cost_estimate_corrected.json', 'w') as f:
    json.dump(strategy, f, indent=2)

print(f"\nSaved: analysis/gkg_cost_estimate_corrected.json")

conn.close()
