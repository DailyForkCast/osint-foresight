#!/usr/bin/env python3
"""
Phase 2: Drop 3 Superseded TED Tables
Removes old TED tables that have been replaced by *_fixed versions
"""
import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

# Tables to drop - superseded by *_fixed versions
tables_to_drop = [
    'ted_china_contracts',      # Superseded by ted_china_contracts_fixed
    'ted_china_entities',       # Superseded by ted_china_entities_fixed
    'ted_china_statistics'      # Superseded by ted_china_statistics_fixed
]

print("="*70)
print("PHASE 2: DROP SUPERSEDED TED TABLES")
print(f"Timestamp: {datetime.now().isoformat()}")
print("="*70)

cleanup_log = {
    'timestamp': datetime.now().isoformat(),
    'tables_dropped': [],
    'errors': [],
    'before_count': 0,
    'after_count': 0,
    'verification': {}
}

try:
    conn = sqlite3.connect(str(db_path), timeout=30)
    cursor = conn.cursor()

    # Count tables before
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    cleanup_log['before_count'] = cursor.fetchone()[0]
    print(f"\nTables before cleanup: {cleanup_log['before_count']}")

    # Verify replacement tables exist and have data
    print("\n[VERIFYING REPLACEMENT TABLES]\n")
    for old_table in tables_to_drop:
        new_table = old_table + '_fixed'

        # Check new table exists
        cursor.execute(f'SELECT COUNT(*) FROM sqlite_master WHERE type="table" AND name="{new_table}"')
        if cursor.fetchone()[0] == 0:
            print(f"  [WARNING] {new_table} does not exist - cannot verify replacement")
            cleanup_log['errors'].append(f"{old_table}: Replacement {new_table} missing")
            continue

        # Check new table has data
        cursor.execute(f'SELECT COUNT(*) FROM "{new_table}"')
        new_count = cursor.fetchone()[0]

        # Check old table status
        cursor.execute(f'SELECT COUNT(*) FROM "{old_table}"')
        old_count = cursor.fetchone()[0]

        cleanup_log['verification'][old_table] = {
            'old_count': old_count,
            'new_count': new_count,
            'replacement': new_table
        }

        if new_count > 0:
            print(f"  [OK] {new_table}: {new_count:,} records (replaces {old_table}: {old_count:,} records)")
        else:
            print(f"  [WARNING] {new_table} is empty - no replacement data")

    # Drop each table
    print("\n[DROPPING TABLES]\n")
    for table in tables_to_drop:
        try:
            cursor.execute(f'DROP TABLE IF EXISTS "{table}"')
            conn.commit()
            print(f"  [OK] Dropped: {table}")
            cleanup_log['tables_dropped'].append(table)
        except Exception as e:
            print(f"  [ERROR] {table}: {e}")
            cleanup_log['errors'].append(f"{table}: {str(e)}")

    # Count tables after
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    cleanup_log['after_count'] = cursor.fetchone()[0]

    # Vacuum to reclaim space
    print("\n[VACUUM DATABASE]")
    print("  Reclaiming space...")
    cursor.execute("VACUUM")
    print("  [OK] Database optimized")

    conn.close()

    print("\n" + "="*70)
    print("CLEANUP SUMMARY")
    print("="*70)
    print(f"\nTables before:  {cleanup_log['before_count']}")
    print(f"Tables after:   {cleanup_log['after_count']}")
    print(f"Tables dropped: {len(cleanup_log['tables_dropped'])}")

    if cleanup_log['tables_dropped']:
        print("\n[DROPPED SUCCESSFULLY]")
        for table in cleanup_log['tables_dropped']:
            verify = cleanup_log['verification'].get(table, {})
            print(f"  - {table} (had {verify.get('old_count', 0):,} records)")
            print(f"    Replaced by: {verify.get('replacement', 'N/A')} ({verify.get('new_count', 0):,} records)")

    if cleanup_log['errors']:
        print("\n[ERRORS/WARNINGS]")
        for error in cleanup_log['errors']:
            print(f"  - {error}")

    # Save log
    log_path = Path("C:/Projects/OSINT - Foresight/analysis/PHASE2_TED_CLEANUP_LOG.json")
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(cleanup_log, f, indent=2)

    print(f"\n[SAVED] Cleanup log: {log_path}")
    print("="*70)

    if cleanup_log['errors']:
        print("\n[WARNING] Cleanup completed with warnings")
        sys.exit(1)
    else:
        print("\n[SUCCESS] Cleanup completed successfully")
        sys.exit(0)

except Exception as e:
    print(f"\n[FATAL ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
