#!/usr/bin/env python3
"""
Cleanup False Positives from USAspending Chinese Entity Detection Database
REMOVES 9,468 false positive records identified in manual review
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("analysis")

def backup_before_cleanup(conn):
    """Create backup record of what will be deleted"""
    cursor = conn.cursor()

    backup_data = {
        'timestamp': datetime.now().isoformat(),
        'database_path': DB_PATH,
        'operation': 'false_positive_cleanup',
        'categories': {}
    }

    # Backup Homer Laughlin records
    cursor.execute("""
        SELECT transaction_id, recipient_name, vendor_name, award_amount
        FROM usaspending_china_305
        WHERE recipient_name LIKE '%HOMER LAUGHLIN%'
           OR vendor_name LIKE '%HOMER LAUGHLIN%'
    """)
    backup_data['categories']['homer_laughlin'] = [
        {'transaction_id': r[0], 'recipient': r[1], 'vendor': r[2], 'amount': r[3]}
        for r in cursor.fetchall()
    ]

    # Backup Aztec records
    cursor.execute("""
        SELECT transaction_id, recipient_name, vendor_name, award_amount
        FROM usaspending_china_305
        WHERE (recipient_name LIKE '%AZTEC%' OR vendor_name LIKE '%AZTEC%')
          AND recipient_name NOT LIKE '%ZTE %'
          AND vendor_name NOT LIKE '%ZTE %'
    """)
    backup_data['categories']['aztec'] = [
        {'transaction_id': r[0], 'recipient': r[1], 'vendor': r[2], 'amount': r[3]}
        for r in cursor.fetchall()
    ]

    # Backup China Company ceramics
    cursor.execute("""
        SELECT transaction_id, recipient_name, vendor_name, award_amount
        FROM usaspending_china_305
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
    backup_data['categories']['china_company_ceramics'] = [
        {'transaction_id': r[0], 'recipient': r[1], 'vendor': r[2], 'amount': r[3]}
        for r in cursor.fetchall()
    ]

    # Save backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = OUTPUT_DIR / f"false_positive_cleanup_backup_{timestamp}.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)

    print(f"  Backup saved to: {backup_file}")
    return backup_file

def cleanup_false_positives(dry_run=True):
    """
    Remove false positive records from database

    Args:
        dry_run: If True, only report what would be deleted (default)
                 If False, actually delete records
    """

    print("=" * 80)
    if dry_run:
        print("FALSE POSITIVE CLEANUP - DRY RUN MODE")
        print("(No records will actually be deleted)")
    else:
        print("FALSE POSITIVE CLEANUP - DELETION MODE")
        print("**WARNING: Records will be permanently deleted**")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get initial count
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    initial_count = cursor.fetchone()[0]
    print(f"\nInitial record count: {initial_count:,}")

    deletion_summary = {}

    # Create backup
    if not dry_run:
        print("\n[0/3] Creating backup of records to be deleted...")
        backup_file = backup_before_cleanup(conn)
        print(f"  [OK] Backup created: {backup_file}")

    # Category 1: Homer Laughlin (American ceramics)
    print("\n[1/3] Homer Laughlin China Company (American ceramics manufacturer)...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE recipient_name LIKE '%HOMER LAUGHLIN%'
           OR vendor_name LIKE '%HOMER LAUGHLIN%'
    """)
    homer_count = cursor.fetchone()[0]
    print(f"  Records to delete: {homer_count:,}")

    if not dry_run and homer_count > 0:
        cursor.execute("""
            DELETE FROM usaspending_china_305
            WHERE recipient_name LIKE '%HOMER LAUGHLIN%'
               OR vendor_name LIKE '%HOMER LAUGHLIN%'
        """)
        print(f"  [OK] Deleted {homer_count:,} records")

    deletion_summary['homer_laughlin'] = homer_count

    # Category 2: Aztec companies (substring match)
    print("\n[2/3] Aztec companies (substring matches ZTE)...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE (recipient_name LIKE '%AZTEC%' OR vendor_name LIKE '%AZTEC%')
          AND recipient_name NOT LIKE '%ZTE %'
          AND vendor_name NOT LIKE '%ZTE %'
    """)
    aztec_count = cursor.fetchone()[0]
    print(f"  Records to delete: {aztec_count:,}")

    if not dry_run and aztec_count > 0:
        cursor.execute("""
            DELETE FROM usaspending_china_305
            WHERE (recipient_name LIKE '%AZTEC%' OR vendor_name LIKE '%AZTEC%')
              AND recipient_name NOT LIKE '%ZTE %'
              AND vendor_name NOT LIKE '%ZTE %'
        """)
        print(f"  [OK] Deleted {aztec_count:,} records")

    deletion_summary['aztec'] = aztec_count

    # Category 3: China Company ceramics (US manufacturers)
    print("\n[3/3] 'China Company' ceramics manufacturers (US companies)...")
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

    if not dry_run and china_co_count > 0:
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

    # Get final count
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    final_count = cursor.fetchone()[0]

    total_deleted = homer_count + aztec_count + china_co_count

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
    print("CLEANUP SUMMARY")
    print("=" * 80)

    print(f"\nMode: {'DRY RUN (no changes made)' if dry_run else 'DELETION (changes committed)'}")
    print(f"\nInitial Records: {initial_count:,}")
    print(f"Final Records:   {final_count:,}")
    print(f"Total {'Would Be ' if dry_run else ''}Deleted: {total_deleted:,}")

    print(f"\nBreakdown:")
    print(f"  - Homer Laughlin: {deletion_summary['homer_laughlin']:,}")
    print(f"  - Aztec companies: {deletion_summary['aztec']:,}")
    print(f"  - China Company ceramics: {deletion_summary['china_company_ceramics']:,}")

    false_positive_rate = (total_deleted / initial_count) * 100
    print(f"\nFalse Positive Rate: {false_positive_rate:.2f}%")

    if dry_run:
        print("\n" + "=" * 80)
        print("TO ACTUALLY DELETE THESE RECORDS:")
        print("=" * 80)
        print("\nRun this script with: cleanup_false_positives(dry_run=False)")
        print("\nWARNING: This action cannot be undone (backup will be created)")

    # Save cleanup log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = OUTPUT_DIR / f"false_positive_cleanup_log_{timestamp}.json"

    cleanup_log = {
        'timestamp': datetime.now().isoformat(),
        'database_path': DB_PATH,
        'dry_run': dry_run,
        'initial_count': initial_count,
        'final_count': final_count,
        'total_deleted': total_deleted,
        'deletion_summary': deletion_summary,
        'false_positive_rate': round(false_positive_rate, 2)
    }

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(cleanup_log, f, indent=2, ensure_ascii=False)

    print(f"\nCleanup log saved to: {log_file}")

    return cleanup_log

if __name__ == "__main__":
    import sys

    # Check command line arguments
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        print("\n" + "=" * 80)
        print("WARNING: --execute flag detected")
        print("This will PERMANENTLY DELETE 9,468 false positive records")
        print("=" * 80)
        response = input("\nType 'DELETE' to confirm: ")
        if response == "DELETE":
            dry_run = False
            print("\n[OK] Confirmed - proceeding with deletion\n")
        else:
            print("\n[X] Confirmation failed - running in dry run mode\n")
            dry_run = True

    try:
        cleanup_log = cleanup_false_positives(dry_run=dry_run)
        print("\n" + "=" * 80)
        print("[SUCCESS] False positive cleanup complete")
        print("=" * 80)
    except Exception as e:
        print(f"\n[ERROR] Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
