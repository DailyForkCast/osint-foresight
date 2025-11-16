#!/usr/bin/env python3
"""
Validate GKG Cost Estimates
Test with a date we know has events to verify actual data volume
"""

from google.cloud import bigquery
import sqlite3
import json
from datetime import datetime

def get_sample_dates():
    """Get dates from our existing events to test"""
    conn = sqlite3.connect(r'F:/OSINT_WAREHOUSE/osint_master.db', uri=True)
    cursor = conn.cursor()

    # Get 3 recent dates with high event counts
    cursor.execute("""
        SELECT SUBSTR(event_date, 1, 8) as date,
               COUNT(*) as event_count
        FROM gdelt_events
        WHERE event_date >= '20241001'
        GROUP BY SUBSTR(event_date, 1, 8)
        ORDER BY date DESC
        LIMIT 3
    """)
    dates = cursor.fetchall()
    conn.close()

    return [(int(d[0]), d[1]) for d in dates]

def test_gkg_query_cost(date_int, event_count):
    """Test GKG query for specific date and measure actual cost"""

    client = bigquery.Client(project="osint-foresight-2025")

    # Query GKG for China-related content on specific date
    # This matches our collection strategy
    query = f"""
    SELECT
        COUNT(*) as gkg_records,
        COUNT(DISTINCT GKGRECORDID) as unique_records
    FROM `gdelt-bq.gdeltv2.gkg_partitioned`
    WHERE DATE = {date_int}
    AND (
        LOWER(V2Themes) LIKE '%china%'
        OR LOWER(V2Themes) LIKE '%chinese%'
        OR LOWER(V2Organizations) LIKE '%china%'
        OR LOWER(V2Organizations) LIKE '%chinese%'
        OR LOWER(V2Organizations) LIKE '%university%'
        OR LOWER(V2Organizations) LIKE '%huawei%'
        OR LOWER(V2Organizations) LIKE '%tencent%'
    )
    """

    print(f"Testing date {date_int} ({event_count:,} events in our DB)...")

    try:
        query_job = client.query(query)
        results = list(query_job.result())

        if results:
            gkg_records = results[0]['gkg_records']
            unique_records = results[0]['unique_records']
        else:
            gkg_records = 0
            unique_records = 0

        bytes_processed = query_job.total_bytes_processed
        bytes_billed = query_job.total_bytes_billed
        tb_processed = bytes_processed / (1024**4)
        tb_billed = bytes_billed / (1024**4)

        print(f"  GKG records: {gkg_records:,}")
        print(f"  Unique records: {unique_records:,}")
        print(f"  Bytes processed: {bytes_processed:,} ({tb_processed:.2f} TB)")
        print(f"  Bytes billed: {bytes_billed:,} ({tb_billed:.2f} TB)")

        return {
            'date': date_int,
            'our_event_count': event_count,
            'gkg_records_found': gkg_records,
            'unique_gkg_records': unique_records,
            'bytes_processed': bytes_processed,
            'bytes_billed': bytes_billed,
            'tb_processed': round(tb_processed, 3),
            'tb_billed': round(tb_billed, 3)
        }

    except Exception as e:
        print(f"  ERROR: {e}")
        return {
            'date': date_int,
            'error': str(e)
        }

def main():
    print("Validating GKG cost estimates with real data...\n")

    # Get sample dates
    sample_dates = get_sample_dates()
    print(f"Testing {len(sample_dates)} recent dates with high event counts:\n")

    results = []
    for date_int, event_count in sample_dates:
        result = test_gkg_query_cost(date_int, event_count)
        results.append(result)
        print()

    # Calculate average cost per day
    valid_results = [r for r in results if 'error' not in r]

    if valid_results:
        avg_tb = sum(r['tb_billed'] for r in valid_results) / len(valid_results)
        print("="*60)
        print("VALIDATED COST ESTIMATES")
        print("="*60)
        print(f"\nAverage TB billed per day: {avg_tb:.2f} TB")
        print(f"Average cost per day: ${avg_tb * 5:.2f} (at $5/TB)")

        # Recalculate options based on actual data
        print(f"\nCORRECTED OPTIONS:")

        # Option 4: 30 days
        days_30_tb = 30 * avg_tb
        days_30_cost = max(0, (days_30_tb - 1) * 5)
        print(f"\nOption 4: 30-day test")
        print(f"  Estimated scan: {days_30_tb:.1f} TB")
        print(f"  Estimated cost: ${days_30_cost:.2f}")

        # Option 2: 365 days
        days_365_tb = 365 * avg_tb
        days_365_cost = max(0, (days_365_tb - 1) * 5)
        print(f"\nOption 2: 365 days")
        print(f"  Estimated scan: {days_365_tb:.1f} TB")
        print(f"  Estimated cost: ${days_365_cost:.2f}")

        # Option 1: Full backfill (2115 days)
        days_all_tb = 2115 * avg_tb
        days_all_cost = max(0, (days_all_tb - 1) * 5)
        print(f"\nOption 1: Full backfill (2115 days)")
        print(f"  Estimated scan: {days_all_tb:.1f} TB")
        print(f"  Estimated cost: ${days_all_cost:.2f}")

        # Save validation results
        validation = {
            'validation_date': datetime.now().isoformat(),
            'test_results': results,
            'average_tb_per_day': round(avg_tb, 3),
            'corrected_estimates': {
                'test_30_days': {
                    'days': 30,
                    'estimated_tb': round(days_30_tb, 1),
                    'estimated_cost_usd': round(days_30_cost, 2)
                },
                'recent_365_days': {
                    'days': 365,
                    'estimated_tb': round(days_365_tb, 1),
                    'estimated_cost_usd': round(days_365_cost, 2)
                },
                'full_backfill': {
                    'days': 2115,
                    'estimated_tb': round(days_all_tb, 1),
                    'estimated_cost_usd': round(days_all_cost, 2)
                }
            }
        }

        with open('analysis/gkg_cost_validation.json', 'w') as f:
            json.dump(validation, f, indent=2)

        print(f"\nSaved: analysis/gkg_cost_validation.json")

if __name__ == '__main__':
    main()
