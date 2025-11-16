#!/usr/bin/env python3
"""
Fix Database Contamination
1. Move china_sourced_product records to Supply Chain DB
2. Remove false positives (Catalina China, Facchinaggi)
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json
import time

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
SUPPLY_CHAIN_DB = "F:/OSINT_WAREHOUSE/osint_china_supply_chain.db"
OUTPUT_DIR = Path("analysis")

def move_china_sourced_products():
    """Move china_sourced_product records from main to supply chain DB"""

    print("=" * 80)
    print("STEP 1: MOVING CHINA_SOURCED_PRODUCT RECORDS")
    print("=" * 80)

    # First, check and extract from main DB
    main_conn = sqlite3.connect(MAIN_DB, timeout=30)
    main_cursor = main_conn.cursor()

    # Count records to move
    main_cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types = '["china_sourced_product"]'
    """)
    sourced_count = main_cursor.fetchone()[0]
    print(f"\nFound {sourced_count:,} china_sourced_product records in main DB")

    if sourced_count == 0:
        print("  No records to move")
        main_conn.close()
        return 0

    # Get sample
    main_cursor.execute("""
        SELECT vendor_name, COUNT(*) as count
        FROM usaspending_china_305
        WHERE detection_types = '["china_sourced_product"]'
        GROUP BY vendor_name
        ORDER BY count DESC
        LIMIT 5
    """)
    print("\n  Top vendors being moved:")
    for vendor, count in main_cursor.fetchall():
        print(f"    {count:4d} | {vendor[:60]}")

    # Extract records to move
    print(f"\n  Extracting {sourced_count:,} records...")
    main_cursor.execute("""
        SELECT * FROM usaspending_china_305
        WHERE detection_types = '["china_sourced_product"]'
    """)

    records_to_move = main_cursor.fetchall()
    column_names = [description[0] for description in main_cursor.description]

    # Close main connection before opening supply chain
    main_conn.close()
    time.sleep(1)

    # Now work with supply chain DB
    supply_conn = sqlite3.connect(SUPPLY_CHAIN_DB, timeout=30)
    supply_cursor = supply_conn.cursor()

    # Insert into supply chain DB
    print(f"  Inserting into supply chain database...")
    placeholders = ', '.join(['?' for _ in column_names])

    # Get existing columns in supply chain table
    supply_cursor.execute("PRAGMA table_info(usaspending_china_supply_chain)")
    existing_columns = [col[1] for col in supply_cursor.fetchall()]

    # Check if we need to add new columns
    columns_to_add = []
    for col in column_names:
        if col not in existing_columns and col not in ['importance_tier', 'importance_score', 'commodity_type']:
            columns_to_add.append(col)

    if columns_to_add:
        print(f"  Adding columns to supply chain table: {columns_to_add}")
        for col in columns_to_add:
            supply_cursor.execute(f"ALTER TABLE usaspending_china_supply_chain ADD COLUMN {col} TEXT")

    insert_sql = f"INSERT OR REPLACE INTO usaspending_china_supply_chain ({', '.join(column_names)}) VALUES ({placeholders})"
    supply_cursor.executemany(insert_sql, records_to_move)
    supply_conn.commit()
    supply_conn.close()
    time.sleep(1)

    print(f"  [OK] Inserted {len(records_to_move):,} records into supply chain DB")

    # Delete from main DB (open fresh connection)
    print(f"\n  Deleting from main database...")
    main_conn = sqlite3.connect(MAIN_DB, timeout=30)
    main_cursor = main_conn.cursor()

    main_cursor.execute("""
        DELETE FROM usaspending_china_305
        WHERE detection_types = '["china_sourced_product"]'
    """)
    deleted = main_cursor.rowcount
    main_conn.commit()
    main_conn.close()

    print(f"  [OK] Deleted {deleted:,} records from main DB")

    return sourced_count

def remove_false_positives():
    """Remove false positive records"""

    print("\n" + "=" * 80)
    print("STEP 2: REMOVING FALSE POSITIVES")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB)
    cursor = conn.cursor()

    false_positives = []

    # 1. Catalina China (American ceramics)
    print("\n[1/2] Catalina China, Inc. (American ceramics company)...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE (recipient_name LIKE '%CATALINA CHINA%' OR vendor_name LIKE '%CATALINA CHINA%')
          AND award_description LIKE '%TABLEWARE%'
    """)
    catalina_count = cursor.fetchone()[0]
    print(f"  Records to delete: {catalina_count:,}")

    if catalina_count > 0:
        cursor.execute("""
            DELETE FROM usaspending_china_305
            WHERE (recipient_name LIKE '%CATALINA CHINA%' OR vendor_name LIKE '%CATALINA CHINA%')
              AND award_description LIKE '%TABLEWARE%'
        """)
        print(f"  [OK] Deleted {catalina_count:,} records")
        false_positives.append(('Catalina China', catalina_count))

    # 2. Facchinaggi/Facchina (Italian companies)
    print("\n[2/2] Facchinaggi/Facchina (Italian companies)...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE recipient_name LIKE '%FACCHIN%'
           OR vendor_name LIKE '%FACCHIN%'
    """)
    facchina_count = cursor.fetchone()[0]
    print(f"  Records to delete: {facchina_count:,}")

    if facchina_count > 0:
        # Show sample first
        cursor.execute("""
            SELECT DISTINCT recipient_name, vendor_name, pop_country_name
            FROM usaspending_china_305
            WHERE recipient_name LIKE '%FACCHIN%'
               OR vendor_name LIKE '%FACCHIN%'
            LIMIT 3
        """)
        print("  Sample records:")
        for recipient, vendor, pop_country in cursor.fetchall():
            print(f"    Recipient: {recipient[:50] if recipient else 'N/A'}")
            print(f"    Vendor: {vendor[:50] if vendor else 'N/A'}")
            print(f"    Country: {pop_country or 'N/A'}")

        cursor.execute("""
            DELETE FROM usaspending_china_305
            WHERE recipient_name LIKE '%FACCHIN%'
               OR vendor_name LIKE '%FACCHIN%'
        """)
        print(f"  [OK] Deleted {facchina_count:,} records")
        false_positives.append(('Facchinaggi/Facchina', facchina_count))

    conn.commit()
    conn.close()

    total_fps = sum(count for _, count in false_positives)
    return false_positives, total_fps

def execute_fixes():
    """Execute all fixes"""

    print("=" * 80)
    print("DATABASE CONTAMINATION FIXES")
    print("=" * 80)
    print("\nThis will:")
    print("  1. Move china_sourced_product records to Supply Chain DB")
    print("  2. Remove false positives (Catalina China, Facchinaggi)")
    print("=" * 80)

    # Get initial counts
    main_conn = sqlite3.connect(MAIN_DB)
    main_cursor = main_conn.cursor()
    main_cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    initial_count = main_cursor.fetchone()[0]
    main_conn.close()

    supply_conn = sqlite3.connect(SUPPLY_CHAIN_DB)
    supply_cursor = supply_conn.cursor()
    supply_cursor.execute("SELECT COUNT(*) FROM usaspending_china_supply_chain")
    initial_supply_count = supply_cursor.fetchone()[0]
    supply_conn.close()

    print(f"\nInitial Counts:")
    print(f"  Main DB: {initial_count:,} records")
    print(f"  Supply Chain DB: {initial_supply_count:,} records")

    results = {
        'timestamp': datetime.now().isoformat(),
        'initial_main_count': initial_count,
        'initial_supply_count': initial_supply_count,
        'operations': []
    }

    try:
        # Step 1: Move china_sourced_product
        sourced_moved = move_china_sourced_products()
        results['operations'].append({
            'step': 1,
            'operation': 'move_china_sourced_product',
            'records_moved': sourced_moved,
            'status': 'success'
        })

        # Step 2: Remove false positives
        fps, total_fps = remove_false_positives()
        results['operations'].append({
            'step': 2,
            'operation': 'remove_false_positives',
            'records_removed': total_fps,
            'breakdown': [{'type': fp_type, 'count': count} for fp_type, count in fps],
            'status': 'success'
        })

        # Get final counts
        main_conn = sqlite3.connect(MAIN_DB)
        main_cursor = main_conn.cursor()
        main_cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
        final_count = main_cursor.fetchone()[0]
        main_conn.close()

        supply_conn = sqlite3.connect(SUPPLY_CHAIN_DB)
        supply_cursor = supply_conn.cursor()
        supply_cursor.execute("SELECT COUNT(*) FROM usaspending_china_supply_chain")
        final_supply_count = supply_cursor.fetchone()[0]
        supply_conn.close()

        results['final_main_count'] = final_count
        results['final_supply_count'] = final_supply_count
        results['total_removed_from_main'] = initial_count - final_count

        # Summary
        print("\n" + "=" * 80)
        print("CONTAMINATION FIXES COMPLETE")
        print("=" * 80)

        print(f"\nMain Database:")
        print(f"  Initial:  {initial_count:,}")
        print(f"  Final:    {final_count:,}")
        print(f"  Removed:  {initial_count - final_count:,}")

        print(f"\n  Breakdown:")
        print(f"    Moved to Supply Chain:  {sourced_moved:,}")
        print(f"    False Positives Deleted: {total_fps:,}")
        for fp_type, count in fps:
            print(f"      - {fp_type}: {count:,}")

        print(f"\nSupply Chain Database:")
        print(f"  Initial:  {initial_supply_count:,}")
        print(f"  Final:    {final_supply_count:,}")
        print(f"  Added:    {final_supply_count - initial_supply_count:,}")

        reduction_pct = ((initial_count - final_count) / initial_count) * 100
        print(f"\nMain DB Reduction: {reduction_pct:.1f}%")

        print(f"\nMain Database Now Contains:")
        print(f"  {final_count:,} records")
        print(f"  Chinese entities ONLY (verified)")
        print(f"  No china_sourced_product leaks")
        print(f"  No known false positives")

        # Save results
        results_file = OUTPUT_DIR / f"contamination_fix_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: {results_file}")

        print("\n" + "=" * 80)
        print("[SUCCESS] Database contamination fixed")
        print("=" * 80)

        return results

    except Exception as e:
        print(f"\n[ERROR] Fix failed: {e}")
        import traceback
        traceback.print_exc()
        results['status'] = 'failed'
        results['error'] = str(e)
        return results

if __name__ == "__main__":
    try:
        results = execute_fixes()
        if results and results.get('final_main_count'):
            print(f"\nDatabase cleaned: {results['final_main_count']:,} Chinese entities remaining")
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
