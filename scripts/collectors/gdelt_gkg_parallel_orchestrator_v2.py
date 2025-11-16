#!/usr/bin/env python3
"""
GDELT GKG Parallel Collection Orchestrator V2
FAST START - No database scanning required!

Key Innovation:
- Skips the 3+ hour database scan entirely
- Divides ALL dates among shards (doesn't check what's collected)
- Relies on INSERT OR IGNORE to skip duplicates automatically
- Starts collecting immediately

Strategy:
- 5 parallel collectors, each with own database shard
- Work backwards from present to 2015 (newest first)
- Batch size: 20 dates per batch
- Each collector handles 1/5 of ALL dates
- Duplicate handling via SQL INSERT OR IGNORE (fast)

Estimated: 3,917 dates, ~207M records, ~688 GB
Speed improvement: ~5x faster than single collector
"""

import sys
import sqlite3
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import time

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CHECKPOINT_DIR = PROJECT_ROOT / "checkpoints"
DB_BASE_PATH = "F:/OSINT_WAREHOUSE/osint_master_shard"
MAIN_DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
COLLECTOR_SCRIPT = PROJECT_ROOT / "scripts" / "collectors" / "gdelt_gkg_free_collector.py"

# Collection parameters
BATCH_SIZE = 20  # Dates per batch for collector
NUM_SHARDS = 5  # Number of parallel collectors
START_DATE = datetime(2015, 2, 19)  # GKG 2.0 launch date
END_DATE = datetime.now()

class FastParallelOrchestrator:
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

    def divide_dates_among_shards(self, all_dates):
        """Divide ALL dates into chunks for each shard"""
        chunk_size = len(all_dates) // NUM_SHARDS

        shard_assignments = {}
        for shard_id in range(1, NUM_SHARDS + 1):
            start_idx = (shard_id - 1) * chunk_size

            # Last shard gets any remainder
            if shard_id == NUM_SHARDS:
                shard_assignments[shard_id] = all_dates[start_idx:]
            else:
                end_idx = start_idx + chunk_size
                shard_assignments[shard_id] = all_dates[start_idx:end_idx]

        return shard_assignments

    def run_collector_for_shard(self, shard_id, dates):
        """Run collector for a specific shard"""
        shard_db = f"{DB_BASE_PATH}{shard_id}.db"

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
        print("GDELT GKG FAST PARALLEL COLLECTION ORCHESTRATOR V2")
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
        print()

        print("FAST START MODE:")
        print("  [*] Skipping database scan (saves 3+ hours!)")
        print("  [*] Each shard will collect all assigned dates")
        print("  [*] INSERT OR IGNORE handles duplicates automatically")
        print("  [*] Collection starts immediately")
        print()

        # Estimates
        est_records = len(all_dates) * 53000
        est_storage_gb = est_records * 3500 / 1e9
        # With 5 parallel shards, divide time by 5
        est_hours = (len(all_dates) * 9.0 / 60) / NUM_SHARDS

        print(f"Estimated:")
        print(f"  Records: ~{est_records:,}")
        print(f"  Storage: ~{est_storage_gb:.1f} GB")
        print(f"  Time: ~{est_hours:.1f} hours (with {NUM_SHARDS} parallel collectors)")
        print(f"  vs {(len(all_dates) * 9.0 / 60):.1f} hours (single collector)")
        print()

        # Divide among shards
        print(f"Dividing {len(all_dates):,} dates among {NUM_SHARDS} shards...")
        shard_assignments = self.divide_dates_among_shards(all_dates)

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
            print(f"\n[SHARD {shard_id}] Launching collector for {len(dates)} dates")
            process = self.run_collector_for_shard(shard_id, dates)
            processes[shard_id] = {
                'process': process,
                'dates': dates,
                'start_time': datetime.now()
            }

        print("\n" + "="*80)
        print(f"All {NUM_SHARDS} collectors launched!")
        print("="*80)
        print("\nCollection started immediately (no database scan needed)!")
        print()
        print("Monitoring progress...")
        print("(Collectors will skip already-collected dates via INSERT OR IGNORE)")
        print()

        # Monitor processes
        start_time = datetime.now()
        last_check = time.time()

        while any(p['process'].poll() is None for p in processes.values()):
            time.sleep(60)  # Check every minute

            # Status update every 5 minutes
            if time.time() - last_check >= 300:
                last_check = time.time()
                elapsed = (datetime.now() - start_time).total_seconds() / 3600
                print(f"\n[{elapsed:.1f}h elapsed] Status:")

                for shard_id, pinfo in processes.items():
                    if pinfo['process'].poll() is None:
                        shard_elapsed = (datetime.now() - pinfo['start_time']).total_seconds() / 3600
                        print(f"  Shard {shard_id}: RUNNING ({shard_elapsed:.1f}h, {len(pinfo['dates'])} dates)")
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
                size_gb = Path(shard_db).stat().st_size / (1024**3)
                print(f"  {shard_db}: {size_gb:.2f} GB")

        print(f"\nNext step: Run merge script to consolidate shards into {self.main_db_path}")

def main():
    parser = argparse.ArgumentParser(description='GDELT GKG Fast Parallel Collection Orchestrator V2')
    parser.add_argument('--yes', action='store_true', help='Auto-confirm (no prompts)')
    args = parser.parse_args()

    orchestrator = FastParallelOrchestrator(auto_confirm=args.yes)
    orchestrator.run_parallel_collection()

if __name__ == '__main__':
    main()
