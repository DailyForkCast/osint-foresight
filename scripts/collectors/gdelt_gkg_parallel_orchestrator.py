#!/usr/bin/env python3
"""
GDELT GKG Parallel Collection Orchestrator
Collects ALL GKG data using multiple parallel collectors with separate database shards

Strategy:
- 5 parallel collectors, each with own database shard
- Work backwards from present to 2015 (newest first)
- Smaller batch size: 15 dates per batch
- Each collector handles 1/5 of remaining dates
- No timeout - let batches complete naturally
- Merge shards to main database later

Estimated: 3,751 dates, ~198M records, ~659 GB
Speed improvement: ~3-5x faster than single collector
"""

import sys
import sqlite3
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import time
import multiprocessing as mp

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CHECKPOINT_DIR = PROJECT_ROOT / "checkpoints"
DB_BASE_PATH = "F:/OSINT_WAREHOUSE/osint_master_shard"
MAIN_DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
COLLECTOR_SCRIPT = PROJECT_ROOT / "scripts" / "collectors" / "gdelt_gkg_free_collector.py"

# Collection parameters
BATCH_SIZE = 15  # Reduced from 50 for better parallelization
NUM_SHARDS = 5  # Number of parallel collectors
START_DATE = datetime(2015, 2, 19)  # GKG 2.0 launch date
END_DATE = datetime.now()

class ParallelOrchestrator:
    def __init__(self, auto_confirm=False):
        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        self.auto_confirm = auto_confirm
        self.main_db_path = MAIN_DB_PATH

    def get_all_target_dates(self):
        """Generate list of all dates from START_DATE to END_DATE (reversed - newest first)"""
        dates = []
        current = START_DATE
        while current <= END_DATE:
            dates.append(current.strftime('%Y%m%d'))
            current += timedelta(days=1)
        # Reverse so we collect newest dates first (Nov 2025 -> Feb 2015)
        dates.reverse()
        return dates

    def get_already_collected_dates(self):
        """Query main database + all shards for dates already collected"""
        all_collected = set()

        # Check main database
        if Path(self.main_db_path).exists():
            conn = sqlite3.connect(self.main_db_path, timeout=60.0)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT SUBSTR(CAST(publish_date AS TEXT), 1, 8) as date
                FROM gdelt_gkg
                WHERE SUBSTR(CAST(publish_date AS TEXT), 1, 8) != ''
            ''')
            all_collected.update([row[0] for row in cursor.fetchall()])
            conn.close()

        # Check all shards
        for shard_id in range(1, NUM_SHARDS + 1):
            shard_db = f"{DB_BASE_PATH}{shard_id}.db"
            if Path(shard_db).exists():
                conn = sqlite3.connect(shard_db, timeout=60.0)
                cursor = conn.cursor()
                # Check if table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='gdelt_gkg'
                """)
                if cursor.fetchone():
                    cursor.execute('''
                        SELECT DISTINCT SUBSTR(CAST(publish_date AS TEXT), 1, 8) as date
                        FROM gdelt_gkg
                        WHERE SUBSTR(CAST(publish_date AS TEXT), 1, 8) != ''
                    ''')
                    all_collected.update([row[0] for row in cursor.fetchall()])
                conn.close()

        return all_collected

    def divide_dates_among_shards(self, remaining_dates):
        """Divide remaining dates into chunks for each shard"""
        chunk_size = len(remaining_dates) // NUM_SHARDS

        shard_assignments = {}
        for shard_id in range(1, NUM_SHARDS + 1):
            start_idx = (shard_id - 1) * chunk_size

            # Last shard gets any remainder
            if shard_id == NUM_SHARDS:
                shard_assignments[shard_id] = remaining_dates[start_idx:]
            else:
                end_idx = start_idx + chunk_size
                shard_assignments[shard_id] = remaining_dates[start_idx:end_idx]

        return shard_assignments

    def run_collector_for_shard(self, shard_id, dates, batch_size=15):
        """Run collector for a specific shard"""
        shard_db = f"{DB_BASE_PATH}{shard_id}.db"

        # Create checkpoint file for this shard
        checkpoint_file = CHECKPOINT_DIR / f"gkg_shard{shard_id}_checkpoint.json"

        # Build date list argument
        dates_str = ','.join(dates)

        # Build command - run collector with specific database and date list
        cmd = [
            sys.executable,
            str(COLLECTOR_SCRIPT),
            '--db', shard_db,
            '--dates', dates_str
        ]

        print(f"\n[SHARD {shard_id}] Starting collection")
        print(f"  Database: {shard_db}")
        print(f"  Dates: {len(dates)}")
        print(f"  Range: {dates[0]} to {dates[-1]}")

        # Run in subprocess
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        return process

    def run_parallel_collection(self):
        """Main orchestration - run all shards in parallel"""
        print("="*80)
        print("GDELT GKG PARALLEL COLLECTION ORCHESTRATOR")
        print("="*80)
        print(f"Date range: {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}")
        print(f"Main database: {self.main_db_path}")
        print(f"Shard databases: {DB_BASE_PATH}[1-{NUM_SHARDS}].db")
        print(f"Batch size: {BATCH_SIZE} dates")
        print(f"Parallel shards: {NUM_SHARDS}")
        print("="*80)
        print()

        # Get all target dates
        all_dates = self.get_all_target_dates()
        print(f"Total dates in range: {len(all_dates):,}")

        # Check what's already collected
        print("\nChecking all databases for already-collected dates...")
        collected = self.get_already_collected_dates()
        print(f"Already collected: {len(collected)} dates")

        # Get remaining dates
        remaining = [d for d in all_dates if d not in collected]
        print(f"Remaining to collect: {len(remaining):,} dates")

        if not remaining:
            print("\n✓ All dates already collected!")
            return

        # Estimates
        est_records = len(remaining) * 53000
        est_storage_gb = est_records * 3500 / 1e9
        est_hours = len(remaining) * 9.0 / 60  # ~9 min per date based on current performance

        print(f"\nEstimated:")
        print(f"  Records: ~{est_records:,}")
        print(f"  Storage: ~{est_storage_gb:.1f} GB")
        print(f"  Time: ~{est_hours:.1f} hours (with {NUM_SHARDS} parallel collectors)")

        # Divide among shards
        print(f"\nDividing {len(remaining):,} dates among {NUM_SHARDS} shards...")
        shard_assignments = self.divide_dates_among_shards(remaining)

        for shard_id, dates in shard_assignments.items():
            print(f"  Shard {shard_id}: {len(dates):,} dates ({dates[0]} to {dates[-1]})")

        # Confirm
        if not self.auto_confirm:
            print("\n" + "="*80)
            response = input(f"Start parallel collection with {NUM_SHARDS} collectors? [y/N]: ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
        else:
            print("\n" + "="*80)
            print(f"AUTO-CONFIRM: Proceeding with collection using {NUM_SHARDS} parallel collectors...")
            print("(Running in auto-confirm mode - no user input required)")

        print("\n" + "="*80)
        print("STARTING PARALLEL COLLECTION")
        print("="*80)

        # Launch all collectors in parallel
        processes = {}
        for shard_id, dates in shard_assignments.items():
            # Split into batches for this shard
            batches = [dates[i:i+BATCH_SIZE] for i in range(0, len(dates), BATCH_SIZE)]
            print(f"\n[SHARD {shard_id}] Will collect {len(dates)} dates in {len(batches)} batches")

            # For now, just assign all dates to the collector
            # The collector will handle batching internally
            process = self.run_collector_for_shard(shard_id, dates, BATCH_SIZE)
            processes[shard_id] = {
                'process': process,
                'dates': dates,
                'batches': len(batches)
            }

        print("\n" + "="*80)
        print(f"All {NUM_SHARDS} collectors launched!")
        print("="*80)
        print("\nMonitoring progress...")
        print("(Check individual shard log files for detailed progress)")
        print()

        # Monitor processes
        start_time = datetime.now()
        while any(p['process'].poll() is None for p in processes.values()):
            time.sleep(60)  # Check every minute

            elapsed = (datetime.now() - start_time).total_seconds() / 3600
            print(f"\n[{elapsed:.1f}h elapsed] Status:")

            for shard_id, pinfo in processes.items():
                if pinfo['process'].poll() is None:
                    print(f"  Shard {shard_id}: RUNNING ({len(pinfo['dates'])} dates)")
                else:
                    returncode = pinfo['process'].returncode
                    status = "COMPLETED" if returncode == 0 else f"FAILED (code {returncode})"
                    print(f"  Shard {shard_id}: {status}")

        # All done
        print("\n" + "="*80)
        print("PARALLEL COLLECTION COMPLETE")
        print("="*80)

        total_elapsed = (datetime.now() - start_time).total_seconds() / 3600
        print(f"\nTotal time: {total_elapsed:.1f} hours")
        print(f"\nShard databases created:")
        for shard_id in range(1, NUM_SHARDS + 1):
            shard_db = f"{DB_BASE_PATH}{shard_id}.db"
            if Path(shard_db).exists():
                size_mb = Path(shard_db).stat().st_size / 1024 / 1024
                print(f"  {shard_db}: {size_mb:.1f} MB")

        print(f"\nNext step: Run merge script to consolidate shards into {self.main_db_path}")

def main():
    parser = argparse.ArgumentParser(description='GDELT GKG Parallel Collection Orchestrator')
    parser.add_argument('--yes', action='store_true', help='Auto-confirm (no prompts)')
    args = parser.parse_args()

    orchestrator = ParallelOrchestrator(auto_confirm=args.yes)
    orchestrator.run_parallel_collection()

if __name__ == '__main__':
    main()
