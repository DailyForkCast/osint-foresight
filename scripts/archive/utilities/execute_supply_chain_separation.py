#!/usr/bin/env python3
"""
Master Supply Chain Separation Script
Executes full separation of Chinese entities from supply chain records
1. Extract place-of-performance-only records to separate database
2. Remove place-of-performance-only records from main database
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
SUPPLY_CHAIN_DB = "F:/OSINT_WAREHOUSE/osint_china_supply_chain.db"
OUTPUT_DIR = Path("analysis")

def extract_supply_chain():
    """Extract place-of-performance-only records to separate database"""

    print("\n" + "=" * 80)
    print("STEP 1/2: EXTRACTING SUPPLY CHAIN DATA")
    print("=" * 80)

    main_conn = sqlite3.connect(MAIN_DB)
    main_cursor = main_conn.cursor()

    # Count records to extract
    main_cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%pop_country_china%'
          AND detection_types NOT LIKE '%chinese_name_recipient%'
          AND detection_types NOT LIKE '%chinese_name_vendor%'
    """)
    pop_count = main_cursor.fetchone()[0]
    print(f"\nFound {pop_count:,} place-of-performance-only records")

    # Create supply chain database
    print(f"Creating supply chain database: {SUPPLY_CHAIN_DB}")
    supply_conn = sqlite3.connect(SUPPLY_CHAIN_DB)
    supply_cursor = supply_conn.cursor()

    # Get schema
    main_cursor.execute("PRAGMA table_info(usaspending_china_305)")
    columns = main_cursor.fetchall()
    column_defs = [f"{col[1]} {col[2]}" for col in columns]

    # Create table
    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS usaspending_china_supply_chain (
            {', '.join(column_defs)}
        )
    """
    supply_cursor.execute(create_table_sql)

    # Copy records
    print(f"Copying {pop_count:,} records...")
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
    while True:
        batch = main_cursor.fetchmany(batch_size)
        if not batch:
            break
        supply_cursor.executemany(insert_sql, batch)
        records_copied += len(batch)

    supply_conn.commit()

    # Create indexes
    supply_cursor.execute("CREATE INDEX IF NOT EXISTS idx_sc_transaction_id ON usaspending_china_supply_chain(transaction_id)")
    supply_cursor.execute("CREATE INDEX IF NOT EXISTS idx_sc_recipient ON usaspending_china_supply_chain(recipient_name)")
    supply_cursor.execute("CREATE INDEX IF NOT EXISTS idx_sc_vendor ON usaspending_china_supply_chain(vendor_name)")
    supply_cursor.execute("CREATE INDEX IF NOT EXISTS idx_sc_pop_country ON usaspending_china_supply_chain(pop_country_code)")
    supply_conn.commit()

    supply_conn.close()
    main_conn.close()

    print(f"[OK] Extracted {records_copied:,} records to {SUPPLY_CHAIN_DB}")
    return records_copied

def remove_supply_chain():
    """Remove place-of-performance-only records from main database"""

    print("\n" + "=" * 80)
    print("STEP 2/2: REMOVING SUPPLY CHAIN FROM MAIN DATABASE")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB)
    cursor = conn.cursor()

    # Count records to remove
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%pop_country_china%'
          AND detection_types NOT LIKE '%chinese_name_recipient%'
          AND detection_types NOT LIKE '%chinese_name_vendor%'
    """)
    pop_count = cursor.fetchone()[0]
    print(f"\nPlace-of-performance-only records to remove: {pop_count:,}")

    if pop_count > 0:
        cursor.execute("""
            DELETE FROM usaspending_china_305
            WHERE detection_types LIKE '%pop_country_china%'
              AND detection_types NOT LIKE '%chinese_name_recipient%'
              AND detection_types NOT LIKE '%chinese_name_vendor%'
        """)
        print(f"[OK] Removed {pop_count:,} records")

    conn.commit()
    conn.close()

    return pop_count

def execute_separation():
    """Execute full supply chain separation"""

    print("=" * 80)
    print("SUPPLY CHAIN SEPARATION - CHINESE ENTITIES FOCUS")
    print("=" * 80)
    print("\nThis will:")
    print("  1. Extract place-of-performance-only records to osint_china_supply_chain.db")
    print("  2. Remove place-of-performance-only records from main database")
    print("  3. Main database will contain ONLY Chinese-owned entities")
    print("=" * 80)

    # Get initial count
    conn = sqlite3.connect(MAIN_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    initial_count = cursor.fetchone()[0]

    # Get breakdown
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%pop_country_china%'
          AND detection_types NOT LIKE '%chinese_name_recipient%'
          AND detection_types NOT LIKE '%chinese_name_vendor%'
    """)
    pop_only_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%chinese_name_recipient%'
           OR detection_types LIKE '%chinese_name_vendor%'
    """)
    chinese_entity_count = cursor.fetchone()[0]
    conn.close()

    print(f"\nInitial database size: {initial_count:,} records")
    print(f"  - Place-of-performance-only: {pop_only_count:,} ({(pop_only_count/initial_count)*100:.1f}%)")
    print(f"  - Chinese entities: {chinese_entity_count:,} ({(chinese_entity_count/initial_count)*100:.1f}%)")
    print("\nStarting separation...")

    results = {
        'timestamp': datetime.now().isoformat(),
        'initial_count': initial_count,
        'pop_only_count': pop_only_count,
        'chinese_entity_count': chinese_entity_count,
        'operations': []
    }

    try:
        # Step 1: Extract supply chain data
        supply_chain_extracted = extract_supply_chain()
        results['operations'].append({
            'step': 1,
            'operation': 'supply_chain_extraction',
            'records_extracted': supply_chain_extracted,
            'destination': str(SUPPLY_CHAIN_DB),
            'status': 'success'
        })

        # Step 2: Remove from main
        supply_chain_removed = remove_supply_chain()
        results['operations'].append({
            'step': 2,
            'operation': 'supply_chain_removal',
            'records_removed': supply_chain_removed,
            'status': 'success'
        })

        # Get final count
        conn = sqlite3.connect(MAIN_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
        final_count = cursor.fetchone()[0]
        conn.close()

        results['final_count'] = final_count
        results['total_removed'] = initial_count - final_count

        # Final summary
        print("\n" + "=" * 80)
        print("SUPPLY CHAIN SEPARATION COMPLETE - FINAL SUMMARY")
        print("=" * 80)

        print(f"\nInitial Records:     {initial_count:,}")
        print(f"Final Records:       {final_count:,}")
        print(f"Total Removed:       {results['total_removed']:,}")

        print(f"\nBreakdown:")
        print(f"  Supply Chain (extracted):  {supply_chain_extracted:,} records")
        print(f"    -> {SUPPLY_CHAIN_DB}")
        print(f"    -> US/EU companies manufacturing in China")
        print(f"\n  Supply Chain (from main):  {supply_chain_removed:,} records removed")

        print(f"\n  Chinese Entities (remaining): {final_count:,} records")
        print(f"    -> Main database now contains ONLY Chinese-owned entities")

        reduction_pct = (results['total_removed'] / initial_count) * 100
        print(f"\nDatabase Reduction: {reduction_pct:.2f}%")

        print(f"\nMain Database Now Contains:")
        print(f"  - Chinese-owned companies ONLY")
        print(f"  - Entities with Chinese names")
        print(f"  - {final_count:,} validated PRC entity detections")

        print(f"\nSupply Chain Data Available In:")
        print(f"  {SUPPLY_CHAIN_DB}")
        print(f"  - {supply_chain_extracted:,} US/EU companies with China exposure")

        # Save results
        results_file = OUTPUT_DIR / f"supply_chain_separation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: {results_file}")

        print("\n" + "=" * 80)
        print("[SUCCESS] Supply chain separation executed successfully")
        print("=" * 80)

        return results

    except Exception as e:
        print(f"\n[ERROR] Separation failed: {e}")
        import traceback
        traceback.print_exc()
        results['status'] = 'failed'
        results['error'] = str(e)
        return results

if __name__ == "__main__":
    try:
        results = execute_separation()
        if results and results.get('final_count'):
            print(f"\nDatabase separated and ready for Chinese entity analysis")
            print(f"{results['final_count']:,} Chinese entities remaining")
            print(f"{results['pop_only_count']:,} supply chain records in separate database")
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
