#!/usr/bin/env python3
"""
Sync Chinese entity flags from ted_procurement_chinese_entities_found
to ted_contracts_production table.

Fixes critical data integrity issue where 6,470 detections exist in
analysis table but only 290 flagged in production table.

Usage:
    python sync_ted_chinese_entities.py

Created: October 18, 2025
"""

import sqlite3
import time
from datetime import datetime
from pathlib import Path

def sync_ted_entities():
    print("TED Chinese Entity Synchronization")
    print("="*70)
    print()

    conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db', timeout=30.0)
    cursor = conn.cursor()

    try:
        # Step 1: Count current state
        print("Step 1: Checking current state...")
        cursor.execute('SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1')
        before_count = cursor.fetchone()[0]
        print(f"  Current flagged contracts: {before_count:,}")

        cursor.execute('SELECT COUNT(*) FROM ted_procurement_chinese_entities_found')
        detection_count = cursor.fetchone()[0]
        print(f"  Detections in analysis table: {detection_count:,}")

        gap = detection_count - before_count
        print(f"  Gap to fix: {gap:,} records")
        print()

        # Step 2: Identify records to update
        print("Step 2: Identifying records to update...")
        cursor.execute('''
            SELECT COUNT(DISTINCT tcp.notice_number)
            FROM ted_contracts_production tcp
            JOIN ted_procurement_chinese_entities_found tpcef
                ON tcp.notice_number = tpcef.notice_number
            WHERE tcp.is_chinese_related != 1 OR tcp.is_chinese_related IS NULL
        ''')
        to_update = cursor.fetchone()[0]
        print(f"  Records to update: {to_update:,}")
        print()

        # Step 3: Update flags
        print("Step 3: Updating is_chinese_related flags...")
        print("  This may take several minutes...")
        start_time = time.time()

        cursor.execute('''
            UPDATE ted_contracts_production
            SET is_chinese_related = 1
            WHERE notice_number IN (
                SELECT DISTINCT notice_number
                FROM ted_procurement_chinese_entities_found
            )
            AND (is_chinese_related != 1 OR is_chinese_related IS NULL)
        ''')

        updated_count = cursor.rowcount
        elapsed = time.time() - start_time
        print(f"  Updated {updated_count:,} records in {elapsed:.1f} seconds")
        print()

        # Step 4: Verify update
        print("Step 4: Verifying update...")
        cursor.execute('SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1')
        after_count = cursor.fetchone()[0]
        print(f"  Flagged contracts after update: {after_count:,}")

        difference = after_count - before_count
        print(f"  Net change: +{difference:,} records")
        print()

        # Step 5: Commit changes
        print("Step 5: Committing changes...")
        conn.commit()
        print("  SUCCESS: Changes committed")
        print()

        # Step 6: Final statistics
        print("Final Statistics:")
        print("-"*70)
        print(f"  Before: {before_count:,} flagged")
        print(f"  After:  {after_count:,} flagged")
        print(f"  Added:  {difference:,} flags")
        print(f"  Target: {detection_count:,} detections")

        if after_count >= detection_count:
            print()
            print("SUCCESS: All Chinese entities properly flagged!")
        else:
            remaining_gap = detection_count - after_count
            print()
            print(f"WARNING: {remaining_gap:,} records still not synced")

        # Create log file
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f'ted_entity_sync_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

        with open(log_file, 'w') as f:
            f.write(f"TED Entity Sync - {datetime.now()}\n")
            f.write(f"Before: {before_count:,}\n")
            f.write(f"After: {after_count:,}\n")
            f.write(f"Updated: {updated_count:,}\n")
            f.write(f"Elapsed: {elapsed:.1f}s\n")

        print()
        print(f"Log saved to: {log_file}")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        print("Rolling back changes...")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = sync_ted_entities()
    exit(0 if success else 1)
