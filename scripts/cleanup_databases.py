#!/usr/bin/env python3
"""
Clean up redundant databases based on analysis results
"""

import shutil
import os
from pathlib import Path
from datetime import datetime
import json

def cleanup_databases():
    warehouse_dir = Path("F:/OSINT_WAREHOUSE")
    archive_dir = warehouse_dir / "archived_databases_20250929"
    archive_dir.mkdir(exist_ok=True)

    # Load analysis results
    with open("C:/Projects/OSINT - Foresight/data/metadata/database_consolidation_analysis.json") as f:
        analysis = json.load(f)

    # Databases to delete (empty or trivial)
    to_delete = analysis['recommendations']['delete']

    # Track operations
    operations = {
        'archived': [],
        'deleted': [],
        'errors': []
    }

    print("="*60)
    print("DATABASE CLEANUP OPERATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*60)

    # Process databases to delete
    for db_name in to_delete:
        db_path = warehouse_dir / db_name

        if not db_path.exists():
            print(f"Skip: {db_name} - already removed")
            continue

        try:
            # Check if it's empty (0 bytes)
            if db_path.stat().st_size == 0:
                # Delete empty files
                os.remove(db_path)
                operations['deleted'].append(db_name)
                print(f"Deleted (empty): {db_name}")
            else:
                # Archive non-empty files before deletion
                archive_path = archive_dir / db_name
                shutil.move(str(db_path), str(archive_path))
                operations['archived'].append(db_name)
                print(f"Archived: {db_name} --> archived_databases_20250929/")

        except Exception as e:
            operations['errors'].append(f"{db_name}: {str(e)}")
            print(f"Error processing {db_name}: {e}")

    # Save cleanup log
    log_file = Path("C:/Projects/OSINT - Foresight/data/metadata/database_cleanup_log.json")
    with open(log_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'operations': operations,
            'summary': {
                'archived': len(operations['archived']),
                'deleted': len(operations['deleted']),
                'errors': len(operations['errors'])
            }
        }, f, indent=2)

    # Summary
    print("\n" + "="*60)
    print("CLEANUP SUMMARY")
    print("="*60)
    print(f"Archived: {len(operations['archived'])} databases")
    print(f"Deleted:  {len(operations['deleted'])} empty databases")
    print(f"Errors:   {len(operations['errors'])}")

    # List remaining databases
    remaining = list(warehouse_dir.glob("*.db"))
    remaining = [db for db in remaining if 'archived' not in str(db)]

    print(f"\nRemaining databases in F:/OSINT_WAREHOUSE:")
    for db in sorted(remaining):
        size_mb = db.stat().st_size / (1024 * 1024)
        print(f"  - {db.name} ({size_mb:.2f} MB)")

    print(f"\nCleanup log saved to: {log_file}")

    return operations

if __name__ == "__main__":
    cleanup_databases()