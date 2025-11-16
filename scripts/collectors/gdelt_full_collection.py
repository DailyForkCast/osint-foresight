#!/usr/bin/env python3
"""
GDELT Full Collection Script
Re-collects Lithuania 2021 crisis data with 100,000 event limit per month
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from gdelt_bigquery_collector import GDELTCollector

def main():
    """Collect full GDELT data for Lithuania 2021 crisis (no 10k limit)"""

    # Initialize collector
    collector = GDELTCollector(
        master_db="F:/OSINT_WAREHOUSE/osint_master.db",
        use_bigquery=True
    )

    # Months to collect
    months = [
        ("20210701", "20210731", "July 2021 (Taiwan office announcement)"),
        ("20210801", "20210831", "August 2021 (Ambassador recall, sanctions)"),
        ("20210901", "20210930", "September 2021 (sustained tensions)"),
        ("20211001", "20211031", "October 2021 (continued fallout)"),
        ("20211101", "20211130", "November 2021 (economic pressure)")
    ]

    print("=" * 80)
    print("GDELT FULL COLLECTION - Lithuania 2021 Crisis")
    print("=" * 80)
    print(f"\nUsing 100,000 event limit per month (up from 10,000)")
    print(f"Target: Complete coverage of Lithuania-Taiwan-China crisis\n")

    try:
        # Connect and setup
        collector.connect()
        collector.create_tables()

        if not collector.setup_bigquery():
            print("ERROR: BigQuery setup failed")
            return

        # Collect each month with high limit
        for start_date, end_date, description in months:
            print(f"\n{'=' * 80}")
            print(f"Collecting: {description}")
            print(f"Date range: {start_date} - {end_date}")
            print(f"Limit: 100,000 events")
            print(f"{'=' * 80}\n")

            # Call with 100k batch size
            collector.collect_china_events(start_date, end_date, batch_size=100000)

            # Generate report for this month
            report = collector.generate_report()

            print(f"\n[OK] {description}: {report['statistics']['events_collected']:,} events")

            # Reset stats for next month
            collector.stats["events_collected"] = 0

        print(f"\n{'=' * 80}")
        print("COLLECTION COMPLETE")
        print(f"{'=' * 80}")

    finally:
        if collector.conn:
            collector.conn.close()

if __name__ == "__main__":
    main()
