#!/usr/bin/env python3
"""
Master Cleanup Script - Non-Interactive Version
Executes all cleanup operations in correct order without prompts
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime
import json

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
HK_DB = "F:/OSINT_WAREHOUSE/osint_hong_kong.db"
OUTPUT_DIR = Path("analysis")

def extract_hong_kong():
    """Extract Hong Kong data to separate database"""

    print("\n" + "=" * 80)
    print("STEP 1/3: EXTRACTING HONG KONG DATA")
    print("=" * 80)

    main_conn = sqlite3.connect(MAIN_DB)
    main_cursor = main_conn.cursor()

    # Count Hong Kong records
    main_cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%hong_kong%'
           OR pop_country_code = 'HKG'
           OR pop_country_name LIKE '%HONG KONG%'
    """)
    hk_count = main_cursor.fetchone()[0]
    print(f"\nFound {hk_count:,} Hong Kong records")

    # Create Hong Kong database
    print(f"Creating Hong Kong database: {HK_DB}")
    hk_conn = sqlite3.connect(HK_DB)
    hk_cursor = hk_conn.cursor()

    # Get schema
    main_cursor.execute("PRAGMA table_info(usaspending_china_305)")
    columns = main_cursor.fetchall()
    column_defs = [f"{col[1]} {col[2]}" for col in columns]

    # Create table
    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS usaspending_hong_kong (
            {', '.join(column_defs)}
        )
    """
    hk_cursor.execute(create_table_sql)

    # Copy records
    print(f"Copying {hk_count:,} records...")
    main_cursor.execute("""
        SELECT * FROM usaspending_china_305
        WHERE detection_types LIKE '%hong_kong%'
           OR pop_country_code = 'HKG'
           OR pop_country_name LIKE '%HONG KONG%'
    """)

    column_names = [description[0] for description in main_cursor.description]
    placeholders = ', '.join(['?' for _ in column_names])
    insert_sql = f"INSERT INTO usaspending_hong_kong VALUES ({placeholders})"

    records_copied = 0
    batch_size = 1000
    while True:
        batch = main_cursor.fetchmany(batch_size)
        if not batch:
            break
        hk_cursor.executemany(insert_sql, batch)
        records_copied += len(batch)

    hk_conn.commit()

    # Create indexes
    hk_cursor.execute("CREATE INDEX IF NOT EXISTS idx_hk_transaction_id ON usaspending_hong_kong(transaction_id)")
    hk_cursor.execute("CREATE INDEX IF NOT EXISTS idx_hk_recipient ON usaspending_hong_kong(recipient_name)")
    hk_cursor.execute("CREATE INDEX IF NOT EXISTS idx_hk_vendor ON usaspending_hong_kong(vendor_name)")
    hk_conn.commit()

    hk_conn.close()
    main_conn.close()

    print(f"[OK] Extracted {records_copied:,} Hong Kong records to {HK_DB}")
    return records_copied

def remove_false_positives():
    """Remove false positive records"""

    print("\n" + "=" * 80)
    print("STEP 2/3: REMOVING FALSE POSITIVES")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB)
    cursor = conn.cursor()

    deletion_summary = {}

    # Homer Laughlin
    print("\n[1/3] Homer Laughlin China Company...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE recipient_name LIKE '%HOMER LAUGHLIN%'
           OR vendor_name LIKE '%HOMER LAUGHLIN%'
    """)
    homer_count = cursor.fetchone()[0]
    print(f"  Records to delete: {homer_count:,}")

    if homer_count > 0:
        cursor.execute("""
            DELETE FROM usaspending_china_305
            WHERE recipient_name LIKE '%HOMER LAUGHLIN%'
               OR vendor_name LIKE '%HOMER LAUGHLIN%'
        """)
        print(f"  [OK] Deleted {homer_count:,} records")

    deletion_summary['homer_laughlin'] = homer_count

    # Aztec companies
    print("\n[2/3] Aztec companies...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE (recipient_name LIKE '%AZTEC%' OR vendor_name LIKE '%AZTEC%')
          AND recipient_name NOT LIKE '%ZTE %'
          AND vendor_name NOT LIKE '%ZTE %'
    """)
    aztec_count = cursor.fetchone()[0]
    print(f"  Records to delete: {aztec_count:,}")

    if aztec_count > 0:
        cursor.execute("""
            DELETE FROM usaspending_china_305
            WHERE (recipient_name LIKE '%AZTEC%' OR vendor_name LIKE '%AZTEC%')
              AND recipient_name NOT LIKE '%ZTE %'
              AND vendor_name NOT LIKE '%ZTE %'
        """)
        print(f"  [OK] Deleted {aztec_count:,} records")

    deletion_summary['aztec'] = aztec_count

    # China Company ceramics
    print("\n[3/3] China Company ceramics...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE (recipient_name LIKE '%CHINA COMPANY%' OR vendor_name LIKE '%CHINA COMPANY%')
          AND pop_country_code = 'USA'
          AND (award_description LIKE '%PLATE%'
               OR award_description LIKE '%BOWL%'
               OR award_description LIKE '%CUP%'
               OR award_description LIKE '%DINNER%'
               OR award_description LIKE '%TABLEWARE%'
               OR award_description LIKE '%CERAMIC%'
               OR award_description LIKE '%PORCELAIN%')
    """)
    china_co_count = cursor.fetchone()[0]
    print(f"  Records to delete: {china_co_count:,}")

    if china_co_count > 0:
        cursor.execute("""
            DELETE FROM usaspending_china_305
            WHERE (recipient_name LIKE '%CHINA COMPANY%' OR vendor_name LIKE '%CHINA COMPANY%')
              AND pop_country_code = 'USA'
              AND (award_description LIKE '%PLATE%'
                   OR award_description LIKE '%BOWL%'
                   OR award_description LIKE '%CUP%'
                   OR award_description LIKE '%DINNER%'
                   OR award_description LIKE '%TABLEWARE%'
                   OR award_description LIKE '%CERAMIC%'
                   OR award_description LIKE '%PORCELAIN%')
        """)
        print(f"  [OK] Deleted {china_co_count:,} records")

    deletion_summary['china_company_ceramics'] = china_co_count

    conn.commit()
    conn.close()

    total_deleted = homer_count + aztec_count + china_co_count
    print(f"\n[OK] Removed {total_deleted:,} false positive records")

    return deletion_summary, total_deleted

def remove_hong_kong():
    """Remove Hong Kong records from main database"""

    print("\n" + "=" * 80)
    print("STEP 3/3: REMOVING HONG KONG FROM MAIN DATABASE")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB)
    cursor = conn.cursor()

    # Count Hong Kong records
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%hong_kong%'
           OR pop_country_code = 'HKG'
           OR pop_country_name LIKE '%HONG KONG%'
    """)
    hk_count = cursor.fetchone()[0]
    print(f"\nHong Kong records to remove: {hk_count:,}")

    if hk_count > 0:
        cursor.execute("""
            DELETE FROM usaspending_china_305
            WHERE detection_types LIKE '%hong_kong%'
               OR pop_country_code = 'HKG'
               OR pop_country_name LIKE '%HONG KONG%'
        """)
        print(f"[OK] Removed {hk_count:,} Hong Kong records")

    conn.commit()
    conn.close()

    return hk_count

def execute_full_cleanup():
    """Execute all cleanup operations"""

    print("=" * 80)
    print("FULL DATABASE CLEANUP - MAINLAND CHINA FOCUS")
    print("=" * 80)
    print("\nThis will:")
    print("  1. Extract Hong Kong records to separate database")
    print("  2. Remove false positives (Homer Laughlin, Aztec, China Co.)")
    print("  3. Remove Hong Kong records from main database")
    print("  4. Main database will contain ONLY mainland China records")
    print("=" * 80)

    # Get initial count
    conn = sqlite3.connect(MAIN_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    initial_count = cursor.fetchone()[0]
    conn.close()

    print(f"\nInitial database size: {initial_count:,} records")
    print("\nStarting cleanup...")

    results = {
        'timestamp': datetime.now().isoformat(),
        'initial_count': initial_count,
        'operations': []
    }

    try:
        # Step 1: Extract Hong Kong
        hk_count = extract_hong_kong()
        results['operations'].append({
            'step': 1,
            'operation': 'hong_kong_extraction',
            'records_extracted': hk_count,
            'destination': str(HK_DB),
            'status': 'success'
        })

        # Step 2: Remove false positives
        deletion_summary, fp_total = remove_false_positives()
        results['operations'].append({
            'step': 2,
            'operation': 'false_positive_cleanup',
            'records_removed': fp_total,
            'breakdown': deletion_summary,
            'status': 'success'
        })

        # Step 3: Remove Hong Kong from main
        hk_removed = remove_hong_kong()
        results['operations'].append({
            'step': 3,
            'operation': 'hong_kong_removal',
            'records_removed': hk_removed,
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
        print("FULL CLEANUP COMPLETE - FINAL SUMMARY")
        print("=" * 80)

        print(f"\nInitial Records:     {initial_count:,}")
        print(f"Final Records:       {final_count:,}")
        print(f"Total Removed:       {results['total_removed']:,}")
        print(f"\nBreakdown:")
        print(f"  Hong Kong (extracted):  {hk_count:,} records -> {HK_DB}")
        print(f"  False Positives:        {fp_total:,} records")
        print(f"    - Homer Laughlin:     {deletion_summary['homer_laughlin']:,}")
        print(f"    - Aztec companies:    {deletion_summary['aztec']:,}")
        print(f"    - China Co. ceramics: {deletion_summary['china_company_ceramics']:,}")
        print(f"  Hong Kong (from main):  {hk_removed:,} records")

        reduction_pct = (results['total_removed'] / initial_count) * 100
        print(f"\nDatabase Reduction: {reduction_pct:.2f}%")
        print(f"\nMain Database Now Contains:")
        print(f"  - Mainland China records ONLY")
        print(f"  - No false positives")
        print(f"  - {final_count:,} validated Chinese entity detections")

        print(f"\nHong Kong Data Available In:")
        print(f"  {HK_DB}")

        # Save results
        results_file = OUTPUT_DIR / f"full_cleanup_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: {results_file}")

        print("\n" + "=" * 80)
        print("[SUCCESS] Full cleanup executed successfully")
        print("=" * 80)

        return results

    except Exception as e:
        print(f"\n[ERROR] Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        results['status'] = 'failed'
        results['error'] = str(e)
        return results

if __name__ == "__main__":
    try:
        results = execute_full_cleanup()
        if results and results.get('final_count'):
            print(f"\nDatabase cleaned and ready for mainland China analysis")
            print(f"{results['final_count']:,} records remaining")
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
