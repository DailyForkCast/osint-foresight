#!/usr/bin/env python3
"""
USPTO Continuous Backfill - Process all existing records
Assess data quality for existing USPTO patent records
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from core.data_quality_assessor import DataQualityAssessor

def continuous_backfill(batch_size=50000):
    """Continuously backfill data quality flags until all records processed"""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return False

    print("="*80)
    print("USPTO CONTINUOUS BACKFILL - NULL DATA HANDLING")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Batch size: {batch_size:,} records")
    print("="*80)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get total records
    cur.execute("SELECT COUNT(*) FROM uspto_patents_chinese")
    total_records = cur.fetchone()[0]

    # Get records already processed
    cur.execute("""
        SELECT COUNT(*) FROM uspto_patents_chinese
        WHERE data_quality_flag IS NOT NULL
    """)
    already_processed = cur.fetchone()[0]

    remaining = total_records - already_processed

    print(f"\nTotal records: {total_records:,}")
    print(f"Already processed: {already_processed:,}")
    print(f"Remaining: {remaining:,}\n")

    if remaining == 0:
        print("All records already processed!")
        conn.close()
        return True

    # Initialize assessor
    assessor = DataQualityAssessor()

    batch_num = 0
    total_processed = 0

    while True:
        batch_num += 1

        # Get next batch of unprocessed records
        # USPTO fields: assignee_country, assignee_city, assignee_name
        cur.execute("""
            SELECT application_number, assignee_country, assignee_city, assignee_name
            FROM uspto_patents_chinese
            WHERE data_quality_flag IS NULL
            LIMIT ?
        """, (batch_size,))

        records = cur.fetchall()
        batch_count = len(records)

        if batch_count == 0:
            print("\n" + "="*80)
            print("ALL RECORDS PROCESSED!")
            print("="*80)
            break

        print(f"\nBatch {batch_num}: Processing {batch_count:,} records...")
        start_time = datetime.now()

        processed_in_batch = 0
        for record in records:
            app_num, country, city, name = record

            # Assess data quality
            quality_record = {
                'country': country,
                'city': city,
                'name': name,
                'address': None  # USPTO doesn't have address in this table
            }

            # key_fields must match the keys in quality_record
            key_fields = ['country', 'city', 'name']
            assessment = assessor.assess(quality_record, key_fields)

            # Update record
            cur.execute("""
                UPDATE uspto_patents_chinese
                SET data_quality_flag = ?,
                    fields_with_data_count = ?
                WHERE application_number = ?
            """, (
                assessment.data_quality_flag,
                assessment.fields_with_data_count,
                app_num
            ))

            processed_in_batch += 1

            # Progress updates within batch
            if processed_in_batch % 10000 == 0:
                conn.commit()
                print(f"  ... {processed_in_batch:,} / {batch_count:,} ...")

        conn.commit()
        total_processed += processed_in_batch

        elapsed = (datetime.now() - start_time).total_seconds()
        rate = processed_in_batch / elapsed if elapsed > 0 else 0

        print(f"  Batch complete: {processed_in_batch:,} records in {elapsed:.1f}s ({rate:.0f} rec/sec)")
        print(f"  Total progress: {already_processed + total_processed:,} / {total_records:,} ({((already_processed + total_processed) / total_records * 100):.1f}%)")

    # Final distribution
    print("\n" + "="*80)
    print("FINAL DATA QUALITY DISTRIBUTION:")
    print("="*80)

    cur.execute("""
        SELECT data_quality_flag, COUNT(*) as count
        FROM uspto_patents_chinese
        WHERE data_quality_flag IS NOT NULL
        GROUP BY data_quality_flag
        ORDER BY count DESC
    """)

    distribution = {}
    for flag, count in cur.fetchall():
        percentage = (count / total_records) * 100
        distribution[flag] = count
        print(f"  {flag:30} {count:>10,} ({percentage:>6.2f}%)")

    # Show samples for each category
    print("\n" + "="*80)
    print("SAMPLE RECORDS BY QUALITY FLAG:")
    print("="*80)

    for flag in distribution.keys():
        print(f"\n{flag}:")
        cur.execute(f"""
            SELECT assignee_name, assignee_country, assignee_city
            FROM uspto_patents_chinese
            WHERE data_quality_flag = '{flag}'
            LIMIT 3
        """)
        for name, country, city in cur.fetchall():
            print(f"  - {name or 'NULL'} | {country or 'NULL'} | {city or 'NULL'}")

    conn.close()

    print("\n" + "="*80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total records processed: {total_processed:,}")
    print("="*80)

    return True


if __name__ == '__main__':
    # Default batch size is 50,000
    batch_size = 50000

    # Allow custom batch size from command line
    if len(sys.argv) > 1:
        try:
            batch_size = int(sys.argv[1])
        except ValueError:
            print(f"Invalid batch size: {sys.argv[1]}")
            sys.exit(1)

    continuous_backfill(batch_size)
