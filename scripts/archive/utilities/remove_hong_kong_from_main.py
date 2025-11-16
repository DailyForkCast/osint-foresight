#!/usr/bin/env python3
"""
Remove Hong Kong Records from Main Database
After extraction to separate database, remove from mainland China focus
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("analysis")

def remove_hong_kong_from_main(dry_run=True):
    """Remove Hong Kong records from main database"""

    print("=" * 80)
    if dry_run:
        print("REMOVE HONG KONG FROM MAIN DATABASE - DRY RUN")
        print("(No records will actually be deleted)")
    else:
        print("REMOVE HONG KONG FROM MAIN DATABASE - DELETION MODE")
        print("**WARNING: Records will be permanently deleted from main DB**")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB)
    cursor = conn.cursor()

    # Get initial count
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    initial_count = cursor.fetchone()[0]
    print(f"\nInitial record count: {initial_count:,}")

    # Count Hong Kong records
    print("\nCounting Hong Kong records to remove...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%hong_kong%'
           OR pop_country_code = 'HKG'
           OR pop_country_name LIKE '%HONG KONG%'
    """)
    hk_count = cursor.fetchone()[0]
    print(f"  Hong Kong records: {hk_count:,}")

    if not dry_run and hk_count > 0:
        print("\n  Deleting Hong Kong records from main database...")
        cursor.execute("""
            DELETE FROM usaspending_china_305
            WHERE detection_types LIKE '%hong_kong%'
               OR pop_country_code = 'HKG'
               OR pop_country_name LIKE '%HONG KONG%'
        """)
        print(f"  [OK] Deleted {hk_count:,} records")

    # Get final count
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    final_count = cursor.fetchone()[0]

    # Commit or rollback
    if not dry_run:
        conn.commit()
        print("\n[OK] Changes committed to database")
    else:
        conn.rollback()
        print("\n[OK] No changes made (dry run mode)")

    conn.close()

    # Summary
    print("\n" + "=" * 80)
    print("HONG KONG REMOVAL SUMMARY")
    print("=" * 80)

    print(f"\nMode: {'DRY RUN (no changes made)' if dry_run else 'DELETION (changes committed)'}")
    print(f"\nInitial Records: {initial_count:,}")
    print(f"Final Records:   {final_count:,}")
    print(f"{'Would Remove' if dry_run else 'Removed'}: {hk_count:,} Hong Kong records")

    hk_percentage = (hk_count / initial_count) * 100 if initial_count > 0 else 0
    print(f"Percentage: {hk_percentage:.2f}%")

    # Save log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = OUTPUT_DIR / f"hong_kong_removal_log_{timestamp}.json"

    removal_log = {
        'timestamp': datetime.now().isoformat(),
        'database_path': MAIN_DB,
        'dry_run': dry_run,
        'initial_count': initial_count,
        'final_count': final_count,
        'hong_kong_removed': hk_count,
        'hk_percentage': round(hk_percentage, 2)
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(removal_log, f, indent=2, ensure_ascii=False)

    print(f"\nLog saved to: {log_file}")

    return removal_log

if __name__ == "__main__":
    import sys

    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        print("\n" + "=" * 80)
        print("WARNING: --execute flag detected")
        print("This will remove Hong Kong records from main database")
        print("=" * 80)
        response = input("\nType 'REMOVE' to confirm: ")
        if response == "REMOVE":
            dry_run = False
            print("\n[OK] Confirmed - proceeding with removal\n")
        else:
            print("\n[X] Confirmation failed - running in dry run mode\n")
            dry_run = True

    try:
        removal_log = remove_hong_kong_from_main(dry_run=dry_run)
        print("\n" + "=" * 80)
        print("[SUCCESS] Hong Kong removal complete")
        print("=" * 80)
    except Exception as e:
        print(f"\n[ERROR] Removal failed: {e}")
        import traceback
        traceback.print_exc()
