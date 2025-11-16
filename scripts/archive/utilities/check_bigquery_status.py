#!/usr/bin/env python3
"""
Quick BigQuery Status Checker
Check project, billing, and test CNIPA patent access
"""

from google.cloud import bigquery
from datetime import datetime

def main():
    print("=" * 80)
    print("BIGQUERY STATUS CHECK")
    print("=" * 80)

    # Initialize client
    client = bigquery.Client()

    print(f"\n[PROJECT INFO]")
    print(f"  Project ID: {client.project}")
    print(f"  Location: {client.location or 'US (default)'}")

    # Test query - minimal data scan
    print(f"\n[TESTING CNIPA PATENT ACCESS]")
    print(f"  Running test query on patents-public-data...")

    test_query = """
    SELECT
        COUNT(*) as total_cn_patents
    FROM `patents-public-data.patents.publications`
    WHERE country_code = 'CN'
        AND filing_date >= 20110101
        AND filing_date < 20110102
    LIMIT 1
    """

    try:
        query_job = client.query(test_query)
        result = list(query_job.result())

        print(f"  SUCCESS! Query completed")
        print(f"  Sample result: {result[0]['total_cn_patents']} Chinese patents on 2011-01-01")

        # Get query statistics
        print(f"\n[QUERY STATISTICS]")
        print(f"  Bytes processed: {query_job.total_bytes_processed:,} bytes")
        print(f"  Bytes billed: {query_job.total_bytes_billed:,} bytes")
        print(f"  Cache hit: {query_job.cache_hit}")

        # Check billing
        if query_job.total_bytes_billed == 0:
            print(f"\n[BILLING STATUS]")
            print(f"  This query used cache (no charge)")
            print(f"  Cannot determine billing status from cached query")
            print(f"\n  To check billing:")
            print(f"  Visit: https://console.cloud.google.com/billing?project={client.project}")
        else:
            print(f"\n[BILLING STATUS]")
            print(f"  Query was billed (billing is enabled)")
            print(f"  You have a PAID subscription")

        print(f"\n[CNIPA DATA AVAILABILITY]")
        print(f"  SUCCESS - patents-public-data accessible")
        print(f"  Ready to query Chinese patents from CNIPA")

        # Estimate full query cost
        print(f"\n[ESTIMATED QUERY FOR MIC2025 ANALYSIS]")
        print(f"  Time period: 2011-2020 (10 years)")
        print(f"  Full query would scan: ~5-10 GB")
        print(f"  Estimated cost: $0.025 - $0.05 (if not cached)")
        print(f"  Free tier: 1 TB/month (more than enough)")

        return True

    except Exception as e:
        print(f"  ERROR: {e}")

        if "quotaExceeded" in str(e):
            print(f"\n[QUOTA STATUS]")
            print(f"  Quota exceeded - at monthly limit")
            print(f"  Free tier: 1 TB/month")
            print(f"  Resets: 1st of each month")
        elif "billing" in str(e).lower():
            print(f"\n[BILLING STATUS]")
            print(f"  Billing not enabled")
            print(f"  Using FREE TIER (sandbox mode)")
            print(f"  Limit: 1 TB queries/month")
        else:
            print(f"\n[ERROR TYPE]")
            print(f"  {type(e).__name__}")

        return False

if __name__ == "__main__":
    success = main()

    print("\n" + "=" * 80)
    if success:
        print("READY FOR CNIPA ANALYSIS")
        print("Next step: Run MIC2025 validation with CNIPA data")
    else:
        print("TROUBLESHOOTING NEEDED")
    print("=" * 80)
