#!/usr/bin/env python3
"""
GDELT GKG Shard Merger
Consolidates data from multiple shard databases into the main database

Strategy:
- Attach each shard database
- Copy all GKG records to main database
- Use INSERT OR IGNORE to avoid duplicates
- Track progress and report statistics
- Optionally delete shards after successful merge
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import argparse

# Paths
DB_BASE_PATH = "F:/OSINT_WAREHOUSE/osint_master_shard"
MAIN_DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
NUM_SHARDS = 5

class ShardMerger:
    def __init__(self, keep_shards=False):
        self.main_db_path = MAIN_DB_PATH
        self.keep_shards = keep_shards
        self.stats = {
            'start_time': datetime.now(),
            'shards_processed': 0,
            'records_merged': 0,
            'duplicates_skipped': 0,
            'errors': []
        }

    def ensure_main_db_indexes(self, conn):
        """Ensure main database has proper indexes"""
        cursor = conn.cursor()

        # Check if indexes exist
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name='idx_gdelt_gkg_date_prefix'
        """)

        if not cursor.fetchone():
            print("Creating index on main database (this may take a while)...")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_gdelt_gkg_date_prefix
                ON gdelt_gkg(SUBSTR(CAST(publish_date AS TEXT), 1, 8))
            """)
            conn.commit()
            print("✓ Index created")

    def get_shard_stats(self, shard_db):
        """Get record count from a shard"""
        if not Path(shard_db).exists():
            return 0

        try:
            conn = sqlite3.connect(shard_db, timeout=60.0)
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='gdelt_gkg'
            """)

            if not cursor.fetchone():
                conn.close()
                return 0

            cursor.execute("SELECT COUNT(*) FROM gdelt_gkg")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Error reading shard {shard_db}: {e}")
            return 0

    def merge_shard(self, conn, shard_id):
        """Merge a single shard into main database"""
        shard_db = f"{DB_BASE_PATH}{shard_id}.db"

        if not Path(shard_db).exists():
            print(f"[SHARD {shard_id}] Not found - skipping")
            return 0

        # Get shard record count
        shard_count = self.get_shard_stats(shard_db)
        if shard_count == 0:
            print(f"[SHARD {shard_id}] Empty - skipping")
            return 0

        print(f"\n[SHARD {shard_id}] Merging {shard_count:,} records...")

        try:
            cursor = conn.cursor()

            # Attach shard database
            cursor.execute(f"ATTACH DATABASE '{shard_db}' AS shard{shard_id}")

            # Get count before merge
            cursor.execute("SELECT COUNT(*) FROM gdelt_gkg")
            count_before = cursor.fetchone()[0]

            # Merge data with INSERT OR IGNORE to skip duplicates
            cursor.execute(f"""
                INSERT OR IGNORE INTO gdelt_gkg
                SELECT * FROM shard{shard_id}.gdelt_gkg
            """)

            # Get count after merge
            cursor.execute("SELECT COUNT(*) FROM gdelt_gkg")
            count_after = cursor.fetchone()[0]

            records_added = count_after - count_before
            duplicates = shard_count - records_added

            # Detach shard
            cursor.execute(f"DETACH DATABASE shard{shard_id}")

            conn.commit()

            print(f"[SHARD {shard_id}] ✓ Complete")
            print(f"  Records added: {records_added:,}")
            if duplicates > 0:
                print(f"  Duplicates skipped: {duplicates:,}")

            self.stats['records_merged'] += records_added
            self.stats['duplicates_skipped'] += duplicates
            self.stats['shards_processed'] += 1

            return records_added

        except Exception as e:
            error_msg = f"[SHARD {shard_id}] Error: {e}"
            print(error_msg)
            self.stats['errors'].append(error_msg)
            return 0

    def merge_all_shards(self):
        """Merge all shards into main database"""
        print("="*80)
        print("GDELT GKG SHARD MERGER")
        print("="*80)
        print(f"Main database: {self.main_db_path}")
        print(f"Shard databases: {DB_BASE_PATH}[1-{NUM_SHARDS}].db")
        print("="*80)

        # Check which shards exist
        existing_shards = []
        total_shard_records = 0

        for shard_id in range(1, NUM_SHARDS + 1):
            shard_db = f"{DB_BASE_PATH}{shard_id}.db"
            if Path(shard_db).exists():
                count = self.get_shard_stats(shard_db)
                if count > 0:
                    existing_shards.append(shard_id)
                    total_shard_records += count
                    size_mb = Path(shard_db).stat().st_size / 1024 / 1024
                    print(f"  Shard {shard_id}: {count:,} records, {size_mb:.1f} MB")

        if not existing_shards:
            print("\nNo shard databases found!")
            return

        print(f"\nTotal shard records: {total_shard_records:,}")

        # Check main database
        main_exists = Path(self.main_db_path).exists()
        if main_exists:
            conn = sqlite3.connect(self.main_db_path, timeout=300.0)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM gdelt_gkg")
            main_count = cursor.fetchone()[0]
            print(f"Main database records: {main_count:,}")
            conn.close()
        else:
            print(f"Main database: Will be created")

        # Confirm
        print("\n" + "="*80)
        response = input(f"Merge {len(existing_shards)} shards into main database? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled.")
            return

        print("\n" + "="*80)
        print("STARTING MERGE")
        print("="*80)

        # Connect to main database
        conn = sqlite3.connect(self.main_db_path, timeout=300.0)

        # Ensure indexes exist
        self.ensure_main_db_indexes(conn)

        # Merge each shard
        for shard_id in existing_shards:
            self.merge_shard(conn, shard_id)

        # Final statistics
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM gdelt_gkg")
        final_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(DISTINCT SUBSTR(CAST(publish_date AS TEXT), 1, 8))
            FROM gdelt_gkg
        """)
        unique_dates = cursor.fetchone()[0]

        conn.close()

        # Report
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()

        print("\n" + "="*80)
        print("MERGE COMPLETE")
        print("="*80)
        print(f"Shards processed: {self.stats['shards_processed']}/{len(existing_shards)}")
        print(f"Records merged: {self.stats['records_merged']:,}")
        print(f"Duplicates skipped: {self.stats['duplicates_skipped']:,}")
        print(f"Final record count: {final_count:,}")
        print(f"Unique dates: {unique_dates:,}")
        print(f"Time elapsed: {elapsed/60:.1f} minutes")

        if self.stats['errors']:
            print(f"\nErrors: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                print(f"  {error}")

        # Optionally delete shards
        if not self.keep_shards:
            print("\n" + "="*80)
            response = input(f"Delete shard databases? [y/N]: ")
            if response.lower() == 'y':
                for shard_id in existing_shards:
                    shard_db = f"{DB_BASE_PATH}{shard_id}.db"
                    try:
                        Path(shard_db).unlink()
                        print(f"  Deleted: {shard_db}")
                    except Exception as e:
                        print(f"  Failed to delete {shard_db}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Merge GDELT GKG shard databases')
    parser.add_argument('--keep-shards', action='store_true',
                       help='Keep shard databases after merge')
    args = parser.parse_args()

    merger = ShardMerger(keep_shards=args.keep_shards)
    merger.merge_all_shards()

if __name__ == '__main__':
    main()
