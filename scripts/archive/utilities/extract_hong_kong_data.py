#!/usr/bin/env python3
"""
Extract Hong Kong Data to Separate Database
Maintains Hong Kong records separately from mainland China focus
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
HK_DB = "F:/OSINT_WAREHOUSE/osint_hong_kong.db"
OUTPUT_DIR = Path("analysis")

def extract_hong_kong_data():
    """Extract all Hong Kong records to separate database"""

    print("=" * 80)
    print("EXTRACTING HONG KONG DATA TO SEPARATE DATABASE")
    print("=" * 80)

    # Connect to main database
    print(f"\n[1/5] Connecting to main database...")
    main_conn = sqlite3.connect(MAIN_DB)
    main_cursor = main_conn.cursor()

    # Count Hong Kong records
    print(f"[2/5] Counting Hong Kong records...")
    main_cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%hong_kong%'
           OR pop_country_code = 'HKG'
           OR pop_country_name LIKE '%HONG KONG%'
    """)
    hk_count = main_cursor.fetchone()[0]
    print(f"  Found {hk_count:,} Hong Kong records")

    # Create Hong Kong database
    print(f"[3/5] Creating Hong Kong database: {HK_DB}")
    hk_conn = sqlite3.connect(HK_DB)
    hk_cursor = hk_conn.cursor()

    # Create table with same schema
    print(f"  Creating table schema...")
    main_cursor.execute("PRAGMA table_info(usaspending_china_305)")
    columns = main_cursor.fetchall()

    column_defs = []
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        column_defs.append(f"{col_name} {col_type}")

    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS usaspending_hong_kong (
            {', '.join(column_defs)}
        )
    """
    hk_cursor.execute(create_table_sql)

    # Copy Hong Kong records
    print(f"[4/5] Copying {hk_count:,} Hong Kong records...")
    main_cursor.execute("""
        SELECT * FROM usaspending_china_305
        WHERE detection_types LIKE '%hong_kong%'
           OR pop_country_code = 'HKG'
           OR pop_country_name LIKE '%HONG KONG%'
    """)

    column_names = [description[0] for description in main_cursor.description]
    placeholders = ', '.join(['?' for _ in column_names])
    insert_sql = f"INSERT INTO usaspending_hong_kong VALUES ({placeholders})"

    batch_size = 1000
    records_copied = 0

    while True:
        batch = main_cursor.fetchmany(batch_size)
        if not batch:
            break
        hk_cursor.executemany(insert_sql, batch)
        records_copied += len(batch)
        if records_copied % 5000 == 0:
            print(f"  Copied {records_copied:,} / {hk_count:,} records...")

    hk_conn.commit()
    print(f"  ✓ Copied {records_copied:,} records")

    # Create indexes
    print(f"  Creating indexes...")
    hk_cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_hk_transaction_id
        ON usaspending_hong_kong(transaction_id)
    """)
    hk_cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_hk_recipient
        ON usaspending_hong_kong(recipient_name)
    """)
    hk_cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_hk_vendor
        ON usaspending_hong_kong(vendor_name)
    """)
    hk_conn.commit()

    # Generate summary statistics
    print(f"[5/5] Generating summary statistics...")

    # Get top vendors
    hk_cursor.execute("""
        SELECT vendor_name, COUNT(*) as count, SUM(CAST(award_amount AS REAL)) as total_amount
        FROM usaspending_hong_kong
        WHERE vendor_name IS NOT NULL
        GROUP BY vendor_name
        ORDER BY count DESC
        LIMIT 10
    """)
    top_vendors = hk_cursor.fetchall()

    # Get detection type breakdown
    hk_cursor.execute("""
        SELECT detection_types, COUNT(*) as count
        FROM usaspending_hong_kong
        GROUP BY detection_types
        ORDER BY count DESC
        LIMIT 10
    """)
    detection_breakdown = hk_cursor.fetchall()

    # Close connections
    hk_conn.close()
    main_conn.close()

    # Save metadata
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    metadata_file = OUTPUT_DIR / f"hong_kong_extraction_{timestamp}.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metadata = {
        'timestamp': datetime.now().isoformat(),
        'source_database': MAIN_DB,
        'destination_database': HK_DB,
        'records_extracted': records_copied,
        'top_vendors': [
            {
                'vendor': v[0],
                'transaction_count': v[1],
                'total_amount': v[2]
            }
            for v in top_vendors
        ],
        'detection_type_breakdown': [
            {
                'detection_types': d[0],
                'count': d[1]
            }
            for d in detection_breakdown
        ]
    }

    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "=" * 80)
    print("HONG KONG DATA EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"\nExtracted: {records_copied:,} Hong Kong records")
    print(f"Destination: {HK_DB}")
    print(f"Metadata: {metadata_file}")

    print("\nTop Hong Kong Vendors:")
    for i, (vendor, count, amount) in enumerate(top_vendors[:5], 1):
        print(f"  {i}. {vendor}")
        print(f"     Transactions: {count:,}")
        print(f"     Total Amount: ${amount:,.2f}")

    print("\n" + "=" * 80)
    print("NEXT STEP: Remove Hong Kong records from main database")
    print("=" * 80)

    return records_copied, HK_DB, metadata_file

if __name__ == "__main__":
    try:
        count, db_path, metadata = extract_hong_kong_data()
        print(f"\n[SUCCESS] Hong Kong data extracted to: {db_path}")
    except Exception as e:
        print(f"\n[ERROR] Extraction failed: {e}")
        import traceback
        traceback.print_exc()
