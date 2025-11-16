#!/usr/bin/env python3
"""
Phase 1: Execute Database Cleanup
Drops 5 verified empty staging tables
"""
import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

# Tables verified as safe to drop
tables_to_drop = [
    'import_openalex_authors',
    'import_openalex_china_topics',
    'import_openalex_funders',
    'import_openalex_works',
    'bis_entity_list'
]

print("="*70)
print("PHASE 1: DATABASE CLEANUP EXECUTION")
print(f"Timestamp: {datetime.now().isoformat()}")
print("="*70)

# Create backup log
cleanup_log = {
    'timestamp': datetime.now().isoformat(),
    'tables_dropped': [],
    'errors': [],
    'before_count': 0,
    'after_count': 0
}

try:
    conn = sqlite3.connect(str(db_path), timeout=30)
    cursor = conn.cursor()

    # Count tables before
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    cleanup_log['before_count'] = cursor.fetchone()[0]
    print(f"\nTables before cleanup: {cleanup_log['before_count']}")

    # Drop each table
    print("\n[DROPPING TABLES]\n")
    for table in tables_to_drop:
        try:
            # Verify empty before dropping
            cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
            count = cursor.fetchone()[0]

            if count > 0:
                print(f"  [SKIP] {table}: Has {count:,} records - NOT SAFE")
                cleanup_log['errors'].append(f"{table}: Not empty ({count} records)")
                continue

            # Drop the table
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
            print(f"  - {table}")

    if cleanup_log['errors']:
        print("\n[ERRORS/SKIPPED]")
        for error in cleanup_log['errors']:
            print(f"  - {error}")

    # Save log
    log_path = Path("C:/Projects/OSINT - Foresight/analysis/PHASE1_CLEANUP_LOG.json")
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(cleanup_log, f, indent=2)

    print(f"\n[SAVED] Cleanup log: {log_path}")
    print("="*70)

    # Exit code
    if cleanup_log['errors']:
        print("\n[WARNING] Cleanup completed with errors")
        sys.exit(1)
    else:
        print("\n[SUCCESS] Cleanup completed successfully")
        sys.exit(0)

except Exception as e:
    print(f"\n[FATAL ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
