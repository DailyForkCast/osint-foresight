#!/usr/bin/env python3
"""
Remove Place-of-Performance-Only Records from Main Database
After extraction to supply chain database, remove from main to focus on Chinese entities
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("analysis")

def remove_supply_chain_from_main(dry_run=True):
    """Remove place-of-performance-only records from main database"""

    print("=" * 80)
    if dry_run:
        print("REMOVE SUPPLY CHAIN RECORDS FROM MAIN DATABASE - DRY RUN")
        print("(No records will actually be deleted)")
    else:
        print("REMOVE SUPPLY CHAIN RECORDS FROM MAIN DATABASE - DELETION MODE")
        print("**WARNING: Records will be permanently deleted from main DB**")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB)
    cursor = conn.cursor()

    # Get initial count
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    initial_count = cursor.fetchone()[0]
    print(f"\nInitial record count: {initial_count:,}")

    # Count place-of-performance-only records to remove
    print("\nCounting place-of-performance-only records to remove...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%pop_country_china%'
          AND detection_types NOT LIKE '%chinese_name_recipient%'
          AND detection_types NOT LIKE '%chinese_name_vendor%'
    """)
    pop_count = cursor.fetchone()[0]
    print(f"  Place-of-performance-only records: {pop_count:,}")

    # Count what will remain (actual Chinese entities)
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%chinese_name_recipient%'
           OR detection_types LIKE '%chinese_name_vendor%'
    """)
    chinese_entity_count = cursor.fetchone()[0]
    print(f"  Will remain (Chinese entities): {chinese_entity_count:,}")

    if not dry_run and pop_count > 0:
        print(f"\n  Deleting {pop_count:,} place-of-performance-only records from main database...")
        cursor.execute("""
            DELETE FROM usaspending_china_305
            WHERE detection_types LIKE '%pop_country_china%'
              AND detection_types NOT LIKE '%chinese_name_recipient%'
              AND detection_types NOT LIKE '%chinese_name_vendor%'
        """)
        print(f"  [OK] Deleted {pop_count:,} records")

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
    print("SUPPLY CHAIN REMOVAL SUMMARY")
    print("=" * 80)

    print(f"\nMode: {'DRY RUN (no changes made)' if dry_run else 'DELETION (changes committed)'}")
    print(f"\nInitial Records: {initial_count:,}")
    print(f"Final Records:   {final_count:,}")
    print(f"{'Would Remove' if dry_run else 'Removed'}: {pop_count:,} place-of-performance-only records")

    pop_percentage = (pop_count / initial_count) * 100 if initial_count > 0 else 0
    chinese_percentage = (chinese_entity_count / initial_count) * 100 if initial_count > 0 else 0

    print(f"\nPercentage removed: {pop_percentage:.2f}%")
    print(f"Percentage remaining: {chinese_percentage:.2f}%")

    print(f"\nMain Database Now Contains:")
    print(f"  - Actual Chinese-owned entities ONLY")
    print(f"  - Companies with Chinese names")
    print(f"  - {final_count:,} records focused on PRC entities")

    print(f"\nWhat Was Removed:")
    print(f"  - US/EU companies manufacturing in China")
    print(f"  - American contractors sourcing from China")
    print(f"  - {pop_count:,} supply chain records")
    print(f"  - Now in separate database: osint_china_supply_chain.db")

    # Save log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = OUTPUT_DIR / f"supply_chain_removal_log_{timestamp}.json"

    removal_log = {
        'timestamp': datetime.now().isoformat(),
        'database_path': MAIN_DB,
        'dry_run': dry_run,
        'initial_count': initial_count,
        'final_count': final_count,
        'supply_chain_removed': pop_count,
        'chinese_entities_remaining': chinese_entity_count,
        'pop_percentage': round(pop_percentage, 2),
        'chinese_percentage': round(chinese_percentage, 2)
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
        print("This will remove place-of-performance records from main database")
        print("=" * 80)
        response = input("\nType 'REMOVE' to confirm: ")
        if response == "REMOVE":
            dry_run = False
            print("\n[OK] Confirmed - proceeding with removal\n")
        else:
            print("\n[X] Confirmation failed - running in dry run mode\n")
            dry_run = True

    try:
        removal_log = remove_supply_chain_from_main(dry_run=dry_run)
        print("\n" + "=" * 80)
        print("[SUCCESS] Supply chain removal complete")
        print("=" * 80)
    except Exception as e:
        print(f"\n[ERROR] Removal failed: {e}")
        import traceback
        traceback.print_exc()
