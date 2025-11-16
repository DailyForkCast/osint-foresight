#!/usr/bin/env python3
"""
Extract Place-of-Performance-Only Records to Separate Database
Separates US/EU companies manufacturing in China from actual Chinese entities
"""

import sqlite3
from pathlib import Path
from datetime import datetime

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
SUPPLY_CHAIN_DB = "F:/OSINT_WAREHOUSE/osint_china_supply_chain.db"

def extract_supply_chain_data():
    """Extract place-of-performance-only records to separate database"""

    print("=" * 80)
    print("EXTRACTING CHINA SUPPLY CHAIN DATA")
    print("=" * 80)
    print("\nExtracting US/EU companies manufacturing in China")
    print("Destination: osint_china_supply_chain.db")
    print("=" * 80)

    main_conn = sqlite3.connect(MAIN_DB)
    main_cursor = main_conn.cursor()

    # Count place-of-performance-only records
    print("\n[1/5] Counting place-of-performance-only records...")
    main_cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%pop_country_china%'
          AND detection_types NOT LIKE '%chinese_name_recipient%'
          AND detection_types NOT LIKE '%chinese_name_vendor%'
    """)
    pop_count = main_cursor.fetchone()[0]
    print(f"  Found {pop_count:,} place-of-performance-only records")

    # Create supply chain database
    print(f"\n[2/5] Creating supply chain database: {SUPPLY_CHAIN_DB}")
    supply_conn = sqlite3.connect(SUPPLY_CHAIN_DB)
    supply_cursor = supply_conn.cursor()

    # Get schema from main database
    print("\n[3/5] Copying table schema...")
    main_cursor.execute("PRAGMA table_info(usaspending_china_305)")
    columns = main_cursor.fetchall()
    column_defs = [f"{col[1]} {col[2]}" for col in columns]

    # Create table in supply chain database
    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS usaspending_china_supply_chain (
            {', '.join(column_defs)}
        )
    """
    supply_cursor.execute(create_table_sql)

    # Copy records
    print(f"\n[4/5] Copying {pop_count:,} records to supply chain database...")
    main_cursor.execute("""
        SELECT * FROM usaspending_china_305
        WHERE detection_types LIKE '%pop_country_china%'
          AND detection_types NOT LIKE '%chinese_name_recipient%'
          AND detection_types NOT LIKE '%chinese_name_vendor%'
    """)

    column_names = [description[0] for description in main_cursor.description]
    placeholders = ', '.join(['?' for _ in column_names])
    insert_sql = f"INSERT INTO usaspending_china_supply_chain VALUES ({placeholders})"

    records_copied = 0
    batch_size = 1000
    batch_count = 0

    while True:
        batch = main_cursor.fetchmany(batch_size)
        if not batch:
            break
        supply_cursor.executemany(insert_sql, batch)
        records_copied += len(batch)
        batch_count += 1

        if batch_count % 10 == 0:
            print(f"  Progress: {records_copied:,} / {pop_count:,} records...")

    supply_conn.commit()

    # Create indexes
    print(f"\n[5/5] Creating indexes on supply chain database...")
    supply_cursor.execute("CREATE INDEX IF NOT EXISTS idx_sc_transaction_id ON usaspending_china_supply_chain(transaction_id)")
    supply_cursor.execute("CREATE INDEX IF NOT EXISTS idx_sc_recipient ON usaspending_china_supply_chain(recipient_name)")
    supply_cursor.execute("CREATE INDEX IF NOT EXISTS idx_sc_vendor ON usaspending_china_supply_chain(vendor_name)")
    supply_cursor.execute("CREATE INDEX IF NOT EXISTS idx_sc_pop_country ON usaspending_china_supply_chain(pop_country_code)")
    supply_conn.commit()

    # Verify count
    supply_cursor.execute("SELECT COUNT(*) FROM usaspending_china_supply_chain")
    final_count = supply_cursor.fetchone()[0]

    supply_conn.close()
    main_conn.close()

    # Summary
    print("\n" + "=" * 80)
    print("SUPPLY CHAIN DATA EXTRACTION COMPLETE")
    print("=" * 80)

    print(f"\nRecords Extracted: {records_copied:,}")
    print(f"Database Location: {SUPPLY_CHAIN_DB}")
    print(f"Table: usaspending_china_supply_chain")

    print(f"\nWhat's in this database:")
    print(f"  - US/EU companies manufacturing in China")
    print(f"  - American contractors sourcing from China")
    print(f"  - European companies with China supply chain")
    print(f"  - NOT Chinese-owned entities")

    print(f"\nUse Cases:")
    print(f"  - Supply chain risk analysis")
    print(f"  - US government dependency on China manufacturing")
    print(f"  - COVID-19 procurement patterns (iHealth, Siemens)")
    print(f"  - Strategic supply chain vulnerabilities")

    if final_count == pop_count:
        print(f"\n[OK] Extraction successful - {final_count:,} records verified")
    else:
        print(f"\n[WARNING] Count mismatch - expected {pop_count:,}, got {final_count:,}")

    return records_copied, SUPPLY_CHAIN_DB

if __name__ == "__main__":
    try:
        count, db_path = extract_supply_chain_data()
        print(f"\n[SUCCESS] Extracted {count:,} supply chain records")
        print(f"Location: {db_path}")
    except Exception as e:
        print(f"\n[ERROR] Extraction failed: {e}")
        import traceback
        traceback.print_exc()
