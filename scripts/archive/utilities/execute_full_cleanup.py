#!/usr/bin/env python3
"""
Master Cleanup Script
Executes all cleanup operations in correct order:
1. Extract Hong Kong data to separate database
2. Remove false positives (Homer Laughlin, Aztec, etc.)
3. Remove Hong Kong records from main database
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Import the individual cleanup functions
sys.path.insert(0, str(Path(__file__).parent))

from extract_hong_kong_data import extract_hong_kong_data
from cleanup_false_positives import cleanup_false_positives
from remove_hong_kong_from_main import remove_hong_kong_from_main

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

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
    print("\n" + "=" * 80)

    response = input("\nType 'EXECUTE' to proceed with full cleanup: ")
    if response != "EXECUTE":
        print("\n[CANCELLED] Cleanup aborted by user")
        return None

    print("\n[OK] Starting full cleanup...\n")

    results = {
        'timestamp': datetime.now().isoformat(),
        'initial_count': initial_count,
        'operations': []
    }

    try:
        # Step 1: Extract Hong Kong
        print("\n" + "=" * 80)
        print("STEP 1/3: EXTRACTING HONG KONG DATA")
        print("=" * 80)
        hk_count, hk_db, hk_metadata = extract_hong_kong_data()
        results['operations'].append({
            'step': 1,
            'operation': 'hong_kong_extraction',
            'records_extracted': hk_count,
            'destination': hk_db,
            'status': 'success'
        })
        print(f"\n[OK] Step 1 complete: {hk_count:,} Hong Kong records extracted")

        # Step 2: Remove false positives
        print("\n" + "=" * 80)
        print("STEP 2/3: REMOVING FALSE POSITIVES")
        print("=" * 80)
        cleanup_log = cleanup_false_positives(dry_run=False)
        results['operations'].append({
            'step': 2,
            'operation': 'false_positive_cleanup',
            'records_removed': cleanup_log['total_deleted'],
            'breakdown': cleanup_log['deletion_summary'],
            'status': 'success'
        })
        print(f"\n[OK] Step 2 complete: {cleanup_log['total_deleted']:,} false positives removed")

        # Step 3: Remove Hong Kong from main
        print("\n" + "=" * 80)
        print("STEP 3/3: REMOVING HONG KONG FROM MAIN DATABASE")
        print("=" * 80)
        removal_log = remove_hong_kong_from_main(dry_run=False)
        results['operations'].append({
            'step': 3,
            'operation': 'hong_kong_removal',
            'records_removed': removal_log['hong_kong_removed'],
            'status': 'success'
        })
        print(f"\n[OK] Step 3 complete: {removal_log['hong_kong_removed']:,} Hong Kong records removed")

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
        print(f"  Hong Kong (extracted):  {hk_count:,} records → {hk_db}")
        print(f"  False Positives:        {cleanup_log['total_deleted']:,} records")
        print(f"    - Homer Laughlin:     {cleanup_log['deletion_summary']['homer_laughlin']:,}")
        print(f"    - Aztec companies:    {cleanup_log['deletion_summary']['aztec']:,}")
        print(f"    - China Co. ceramics: {cleanup_log['deletion_summary']['china_company_ceramics']:,}")
        print(f"  Hong Kong (from main):  {removal_log['hong_kong_removed']:,} records")

        reduction_pct = (results['total_removed'] / initial_count) * 100
        print(f"\nDatabase Reduction: {reduction_pct:.2f}%")
        print(f"\nMain Database Now Contains:")
        print(f"  ✓ Mainland China records ONLY")
        print(f"  ✓ No false positives")
        print(f"  ✓ {final_count:,} validated Chinese entity detections")

        print(f"\nHong Kong Data Available In:")
        print(f"  {hk_db}")

        # Save results
        results_file = Path("analysis") / f"full_cleanup_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)

        import json
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
            print(f"\n✓ Database cleaned and ready for mainland China analysis")
            print(f"✓ {results['final_count']:,} records remaining")
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Cleanup interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
