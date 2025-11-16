#!/usr/bin/env python3
"""
Check Latest Available Patent Data in BigQuery
Determine the most recent filing date for CNIPA patents
"""

from google.cloud import bigquery

def main():
    print("=" * 80)
    print("CHECKING LATEST AVAILABLE PATENT DATA")
    print("=" * 80)

    client = bigquery.Client()

    # Check latest filing date for Chinese patents
    query = """
    SELECT
        MAX(filing_date) as latest_filing_date,
        MIN(filing_date) as earliest_filing_date,
        COUNT(*) as total_cn_patents
    FROM `patents-public-data.patents.publications`
    WHERE country_code = 'CN'
        AND filing_date IS NOT NULL
    """

    print("\nQuerying for Chinese patent date range...")

    try:
        query_job = client.query(query)
        result = list(query_job.result())

        latest = result[0]['latest_filing_date']
        earliest = result[0]['earliest_filing_date']
        total = result[0]['total_cn_patents']

        # Convert YYYYMMDD to readable format
        latest_str = str(latest)
        earliest_str = str(earliest)

        latest_formatted = f"{latest_str[:4]}-{latest_str[4:6]}-{latest_str[6:]}"
        earliest_formatted = f"{earliest_str[:4]}-{earliest_str[4:6]}-{earliest_str[6:]}"

        print(f"\n[DATA AVAILABILITY]")
        print(f"  Earliest filing date: {earliest_formatted}")
        print(f"  Latest filing date:   {latest_formatted}")
        print(f"  Total CN patents:     {total:,}")

        print(f"\n[QUERY STATISTICS]")
        print(f"  Bytes processed: {query_job.total_bytes_processed:,}")
        print(f"  Bytes billed: {query_job.total_bytes_billed:,}")

        # Determine analysis period
        latest_year = int(latest_str[:4])

        print(f"\n[RECOMMENDED ANALYSIS PERIOD]")
        print(f"  Pre-MIC2025:  2011-01-01 to 2015-05-07")
        print(f"  Post-MIC2025: 2015-05-08 to {latest_year}-12-31")
        print(f"  Total span:   {latest_year - 2011 + 1} years")

        if latest_year >= 2025:
            print(f"\n  ✓ Can analyze through 2025!")
        elif latest_year >= 2024:
            print(f"\n  ✓ Can analyze through 2024")
        else:
            print(f"\n  ⚠ Latest data is {latest_year}")

        return latest_year

    except Exception as e:
        print(f"\nERROR: {e}")
        return None

if __name__ == "__main__":
    latest_year = main()

    print("\n" + "=" * 80)
    if latest_year:
        print(f"READY TO ANALYZE: 2011-{latest_year}")
    print("=" * 80)
