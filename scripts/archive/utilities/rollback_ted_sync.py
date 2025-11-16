#!/usr/bin/env python3
"""
Rollback TED Sync to Pre-Sync State
Created: October 19, 2025
Purpose: Restore database from backup created before TED entity synchronization
"""

import sqlite3
import shutil
import os
from datetime import datetime

# Paths
CURRENT_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
BACKUP_DB = "F:/OSINT_WAREHOUSE/osint_master_backup_20251019_105606.db"
ROLLBACK_SNAPSHOT = "F:/OSINT_WAREHOUSE/osint_master_before_rollback_20251019.db"

def main():
    print("=" * 80)
    print("TED SYNC ROLLBACK - RESTORE FROM BACKUP")
    print("=" * 80)
    print()
    print("This will restore the database to its pre-sync state:")
    print(f"  - Current state: 51,139 contracts flagged as Chinese")
    print(f"  - After rollback: 295 contracts flagged (pre-sync state)")
    print(f"  - Performance optimizations (VACUUM, indexes) preserved")
    print()

    # Verify backup exists
    if not os.path.exists(BACKUP_DB):
        print(f"ERROR: Backup not found at {BACKUP_DB}")
        print("Cannot proceed with rollback.")
        return 1

    backup_size = os.path.getsize(BACKUP_DB) / (1024**3)
    current_size = os.path.getsize(CURRENT_DB) / (1024**3)

    print(f"Backup database: {BACKUP_DB}")
    print(f"  Size: {backup_size:.2f} GB")
    print(f"  Created: October 19, 2025, 10:56 AM")
    print()
    print(f"Current database: {CURRENT_DB}")
    print(f"  Size: {current_size:.2f} GB")
    print()

    # Verify backup integrity
    print("[1/5] Verifying backup integrity...")
    try:
        conn = sqlite3.connect(BACKUP_DB, timeout=60)
        cursor = conn.cursor()

        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]

        if integrity != "ok":
            print(f"  ERROR: Backup integrity check failed: {integrity}")
            conn.close()
            return 1

        # Check TED flagged count in backup
        cursor.execute("SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1")
        backup_flagged = cursor.fetchone()[0]

        # Check total contracts
        cursor.execute("SELECT COUNT(*) FROM ted_contracts_production")
        backup_total = cursor.fetchone()[0]

        conn.close()

        print(f"  Backup integrity: OK")
        print(f"  Backup TED flagged contracts: {backup_flagged:,}")
        print(f"  Backup total contracts: {backup_total:,}")

        if backup_flagged != 295:
            print(f"  WARNING: Expected 295 flagged contracts, found {backup_flagged:,}")
            print(f"  This may not be the correct backup!")
            response = input("  Continue anyway? (yes/no): ")
            if response.lower() != 'yes':
                print("  Rollback cancelled.")
                return 0

        print()

    except Exception as e:
        print(f"  ERROR: Failed to verify backup: {e}")
        return 1

    # Create snapshot of current state (before rollback)
    print("[2/5] Creating snapshot of current state...")
    try:
        if os.path.exists(ROLLBACK_SNAPSHOT):
            print(f"  Removing existing snapshot...")
            os.remove(ROLLBACK_SNAPSHOT)

        print(f"  Creating: {ROLLBACK_SNAPSHOT}")
        shutil.copy2(CURRENT_DB, ROLLBACK_SNAPSHOT)
        snapshot_size = os.path.getsize(ROLLBACK_SNAPSHOT) / (1024**3)
        print(f"  Snapshot created: {snapshot_size:.2f} GB")
        print(f"  (In case you need to restore the 51,139 flagged state)")
        print()

    except Exception as e:
        print(f"  ERROR: Failed to create snapshot: {e}")
        return 1

    # Close all connections
    print("[3/5] Preparing for rollback...")
    print("  Ensuring no active connections to database...")
    print("  (Waiting 5 seconds for any connections to close)")
    import time
    time.sleep(5)
    print()

    # Perform rollback
    print("[4/5] Performing rollback...")
    try:
        # Remove current database
        print(f"  Removing current database...")
        if os.path.exists(CURRENT_DB):
            os.remove(CURRENT_DB)

        # Copy backup to current location
        print(f"  Restoring from backup...")
        shutil.copy2(BACKUP_DB, CURRENT_DB)

        restored_size = os.path.getsize(CURRENT_DB) / (1024**3)
        print(f"  Database restored: {restored_size:.2f} GB")
        print()

    except Exception as e:
        print(f"  ERROR: Rollback failed: {e}")
        print(f"  CRITICAL: Attempting to restore from snapshot...")
        try:
            if os.path.exists(ROLLBACK_SNAPSHOT):
                shutil.copy2(ROLLBACK_SNAPSHOT, CURRENT_DB)
                print(f"  Snapshot restored successfully")
            else:
                print(f"  ERROR: Snapshot not found!")
        except Exception as e2:
            print(f"  CRITICAL ERROR: Failed to restore snapshot: {e2}")
            print(f"  Manual intervention required!")
        return 1

    # Verify rollback
    print("[5/5] Verifying rollback...")
    try:
        conn = sqlite3.connect(CURRENT_DB, timeout=60)
        cursor = conn.cursor()

        # Check integrity
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        print(f"  Database integrity: {integrity}")

        # Check TED flagged count
        cursor.execute("SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1")
        flagged = cursor.fetchone()[0]

        # Check total contracts
        cursor.execute("SELECT COUNT(*) FROM ted_contracts_production")
        total = cursor.fetchone()[0]

        # Check indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indexes = cursor.fetchall()

        conn.close()

        print(f"  TED flagged contracts: {flagged:,} (expected 295)")
        print(f"  Total contracts: {total:,}")
        print(f"  Performance indexes: {len(indexes)} found")
        print()

        if flagged == 295:
            print("  ✓ Rollback verified successfully!")
        else:
            print(f"  WARNING: Expected 295 flagged, found {flagged:,}")

        print()

    except Exception as e:
        print(f"  ERROR: Verification failed: {e}")
        return 1

    # Summary
    print("=" * 80)
    print("ROLLBACK COMPLETE")
    print("=" * 80)
    print()
    print("Database Status:")
    print(f"  TED Chinese-related contracts: {flagged:,}")
    print(f"  Total TED contracts: {total:,}")
    print(f"  Performance optimizations: PRESERVED")
    print(f"  Database size: {restored_size:.2f} GB")
    print()
    print("Data Preserved for Analysis:")
    print(f"  Analysis database: F:/OSINT_WAREHOUSE/ted_sync_analysis_20251019.db")
    print(f"  Contains: 51,139 flagged contracts for manual review")
    print()
    print("Snapshots Available:")
    print(f"  Original backup: {BACKUP_DB}")
    print(f"  Pre-rollback state: {ROLLBACK_SNAPSHOT}")
    print()
    print("Next Steps:")
    print("  1. Review analysis database to identify true vs false positives")
    print("  2. Fix ted_procurement_chinese_entities_found table")
    print("  3. Re-run sync with proper validation")
    print()

    return 0

if __name__ == "__main__":
    exit(main())
