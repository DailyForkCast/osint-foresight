#!/usr/bin/env python3
"""
Investigate GKG table structure
Figure out why queries return 0 results despite scanning TB of data
"""

from google.cloud import bigquery
import json
from datetime import datetime

def investigate_gkg():
    client = bigquery.Client(project="osint-foresight-2025")

    print("Investigating GDELT GKG table structure...\n")

    # Check what dates actually exist in GKG
    print("1. Checking available date range in GKG...")
    date_range_query = """
    SELECT
        MIN(DATE) as min_date,
        MAX(DATE) as max_date,
        COUNT(*) as total_records,
        COUNT(DISTINCT DATE) as unique_dates
    FROM `gdelt-bq.gdeltv2.gkg_partitioned`
    """

    try:
        print("   Running query (this may take a moment)...")
        job = client.query(date_range_query)
        results = list(job.result())

        if results:
            row = results[0]
            print(f"   Min date: {row['min_date']}")
            print(f"   Max date: {row['max_date']}")
            print(f"   Total records: {row['total_records']:,}")
            print(f"   Unique dates: {row['unique_dates']:,}")
            print(f"   Bytes scanned: {job.total_bytes_billed / (1024**4):.2f} TB")

        # Check recent dates availability
        print("\n2. Checking if recent dates exist...")
        recent_check = """
        SELECT DATE, COUNT(*) as count
        FROM `gdelt-bq.gdeltv2.gkg_partitioned`
        WHERE DATE >= 20241101
        GROUP BY DATE
        ORDER BY DATE DESC
        LIMIT 10
        """

        job2 = client.query(recent_check)
        results2 = list(job2.result())

        if results2:
            print(f"   Found {len(results2)} recent dates:")
            for row in results2:
                print(f"     {row['DATE']}: {row['count']:,} records")
        else:
            print("   No records found for Nov 2024+")

        # Check 2024 dates
        print("\n3. Checking 2024 dates availability...")
        dates_2024 = """
        SELECT DATE, COUNT(*) as count
        FROM `gdelt-bq.gdeltv2.gkg_partitioned`
        WHERE DATE >= 20240501
        AND DATE < 20240520
        GROUP BY DATE
        ORDER BY DATE
        LIMIT 20
        """

        job3 = client.query(dates_2024)
        results3 = list(job3.result())

        if results3:
            print(f"   Found {len(results3)} dates in May 2024:")
            for row in results3[:5]:
                print(f"     {row['DATE']}: {row['count']:,} records")
        else:
            print("   No records found for May 2024")

        # Get sample record to see structure
        print("\n4. Getting sample GKG record...")
        sample_query = """
        SELECT *
        FROM `gdelt-bq.gdeltv2.gkg_partitioned`
        LIMIT 1
        """

        job4 = client.query(sample_query)
        results4 = list(job4.result())

        if results4:
            sample = results4[0]
            print(f"   Sample record found:")
            print(f"     Date: {sample['DATE']}")
            print(f"     Source: {sample['SourceCommonName']}")
            print(f"     Has themes: {bool(sample['V2Themes'])}")
            print(f"     Has orgs: {bool(sample['V2Organizations'])}")

        # Save investigation results
        investigation = {
            'investigation_date': datetime.now().isoformat(),
            'findings': {
                'date_range': {
                    'min': results[0]['min_date'] if results else None,
                    'max': results[0]['max_date'] if results else None,
                    'total_records': results[0]['total_records'] if results else 0,
                    'unique_dates': results[0]['unique_dates'] if results else 0
                },
                'recent_dates': [
                    {'date': r['DATE'], 'count': r['count']}
                    for r in results2
                ] if results2 else [],
                'may_2024_dates': [
                    {'date': r['DATE'], 'count': r['count']}
                    for r in results3
                ] if results3 else [],
                'sample_record_found': len(results4) > 0
            }
        }

        with open('analysis/gkg_structure_investigation.json', 'w') as f:
            json.dump(investigation, f, indent=2)

        print("\n" + "="*60)
        print("DIAGNOSIS")
        print("="*60)

        if not results or results[0]['total_records'] == 0:
            print("\nCRITICAL: GKG table appears empty or inaccessible")
            print("Possible causes:")
            print("  - Wrong table name (check if gkg vs gkg_partitioned)")
            print("  - Permissions issue")
            print("  - GKG data not available in free tier")
        elif not results3:
            print("\nISSUE: GKG data doesn't exist for May 2024 dates")
            print("Need to use dates that actually have GKG data")
        else:
            print("\nGKG data appears available")
            print("Issue may be with our query filters or date format")

        print(f"\nSaved: analysis/gkg_structure_investigation.json")

    except Exception as e:
        print(f"ERROR: {e}")
        with open('analysis/gkg_structure_investigation.json', 'w') as f:
            json.dump({
                'investigation_date': datetime.now().isoformat(),
                'error': str(e)
            }, f, indent=2)

if __name__ == '__main__':
    investigate_gkg()
