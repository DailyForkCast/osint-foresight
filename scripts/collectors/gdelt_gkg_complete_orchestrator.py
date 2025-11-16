#!/usr/bin/env python3
"""
GDELT GKG Complete Collection Orchestrator
Systematically collects ALL GKG data from Nov 7, 2025 back to Feb 19, 2015

Strategy:
- Work backwards from present to 2015 (newest first)
- Dynamic batch sizing: 50 dates (2024+), 30 (2020-2023), 20 (2017-2019), 10 (2015-2016)
- No timeout - let batches complete naturally
- Skip already-collected dates
- Save checkpoints after each batch
- Resume-friendly

Estimated: 3,915 dates, ~207M records, ~688 GB, ~196 hours
Cost: $0.00
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
CHECKPOINT_FILE = PROJECT_ROOT / "checkpoints" / "gkg_complete_collection.json"
DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
COLLECTOR_SCRIPT = PROJECT_ROOT / "scripts" / "collectors" / "gdelt_gkg_free_collector.py"

# Collection parameters
BATCH_SIZE = 50  # Dates per batch
START_DATE = datetime(2015, 2, 19)  # GKG 2.0 launch date
END_DATE = datetime.now()

class CompleteCollectionOrchestrator:
    def __init__(self, auto_confirm=False):
        self.checkpoint_file = CHECKPOINT_FILE
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = DB_PATH
        self.auto_confirm = auto_confirm

        self.stats = {
            'start_time': datetime.now().isoformat(),
            'total_dates': 0,
            'dates_collected': 0,
            'dates_skipped': 0,
            'batches_completed': 0,
            'total_batches': 0,
            'errors': []
        }

    def load_checkpoint(self):
        """Load checkpoint if exists"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {'last_completed_date': None, 'collected_dates': []}

    def save_checkpoint(self, checkpoint):
        """Save checkpoint"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

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
        """Query database for dates already collected"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT SUBSTR(CAST(publish_date AS TEXT), 1, 8) as date
            FROM gdelt_gkg
            WHERE SUBSTR(CAST(publish_date AS TEXT), 1, 8) != ''
            ORDER BY date
        ''')

        collected = set([row[0] for row in cursor.fetchall()])
        conn.close()

        return collected

    def get_dynamic_batch_size(self, date_str):
        """Determine batch size based on year (older dates = smaller batches due to higher volume)"""
        year = int(date_str[:4])

        if year >= 2024:
            return 50  # Recent dates: low volume, large batches
        elif year >= 2020:
            return 30  # Mid-period: moderate batches
        elif year >= 2017:
            return 20  # Older: smaller batches
        else:
            return 10  # Oldest (2015-2016): smallest batches due to very high volume

    def create_batches(self, dates_to_collect):
        """Split dates into variable-sized batches based on year"""
        batches = []
        current_batch = []
        current_batch_size_limit = None

        for date_str in dates_to_collect:
            # Determine appropriate batch size for this date
            batch_size = self.get_dynamic_batch_size(date_str)

            # If we haven't started a batch or if the batch size changes, start fresh
            if current_batch_size_limit is None:
                current_batch_size_limit = batch_size

            # If batch is full or year changed (implying different batch size), finish it
            if len(current_batch) >= current_batch_size_limit or batch_size != current_batch_size_limit:
                if current_batch:
                    batches.append(current_batch)
                current_batch = [date_str]
                current_batch_size_limit = batch_size
            else:
                current_batch.append(date_str)

        # Add final batch
        if current_batch:
            batches.append(current_batch)

        return batches

    def collect_batch(self, batch, batch_num, total_batches):
        """Collect a batch of dates"""
        print(f"\n{'='*80}")
        print(f"BATCH {batch_num}/{total_batches}")
        print(f"Dates: {len(batch)} ({batch[0]} to {batch[-1]})")
        print(f"{'='*80}\n")

        # Prepare dates string
        dates_str = ','.join(batch)

        # Run collector
        cmd = [
            sys.executable,
            str(COLLECTOR_SCRIPT),
            '--dates', dates_str,
            '--db', self.db_path
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=None  # No timeout - let batch complete naturally
            )

            if result.returncode == 0:
                print(f"[SUCCESS] Batch {batch_num} completed successfully")
                return True
            else:
                print(f"[FAILED] Batch {batch_num} failed:")
                print(result.stderr[-500:] if result.stderr else "No error output")
                self.stats['errors'].append(f"Batch {batch_num} failed: {result.stderr[-200:]}")
                return False

        except subprocess.TimeoutExpired:
            print(f"[FAILED] Batch {batch_num} timed out")
            self.stats['errors'].append(f"Batch {batch_num} timed out")
            return False
        except Exception as e:
            print(f"[FAILED] Batch {batch_num} error: {e}")
            self.stats['errors'].append(f"Batch {batch_num} error: {str(e)}")
            return False

    def run_complete_collection(self):
        """Main orchestration loop"""
        print("\n" + "="*80)
        print("GDELT GKG COMPLETE COLLECTION ORCHESTRATOR")
        print("="*80)
        print(f"Date range: {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}")
        print(f"Database: {self.db_path}")
        print(f"Batch size: {BATCH_SIZE} dates")
        print("="*80)

        # Get all target dates
        all_dates = self.get_all_target_dates()
        self.stats['total_dates'] = len(all_dates)
        print(f"\nTotal dates in range: {len(all_dates):,}")

        # Check what's already collected
        print("\nChecking database for already-collected dates...")
        already_collected = self.get_already_collected_dates()
        print(f"Already collected: {len(already_collected):,} dates")

        # Determine what needs to be collected
        dates_to_collect = [d for d in all_dates if d not in already_collected]
        self.stats['dates_skipped'] = len(already_collected)

        if not dates_to_collect:
            print("\n✓ All dates already collected! Nothing to do.")
            return

        print(f"Remaining to collect: {len(dates_to_collect):,} dates")
        print(f"\nEstimated:")
        print(f"  Records: ~{len(dates_to_collect) * 53000:,}")
        print(f"  Storage: ~{len(dates_to_collect) * 180 / 1024:.1f} GB")
        print(f"  Time: ~{len(dates_to_collect) * 3 / 60:.1f} hours")

        # Create batches
        batches = self.create_batches(dates_to_collect)
        self.stats['total_batches'] = len(batches)
        print(f"  Batches: {len(batches)} (of {BATCH_SIZE} dates each)")

        # Confirmation
        print("\n" + "="*80)
        if not self.auto_confirm:
            response = input(f"Proceed with collection of {len(dates_to_collect):,} dates? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Collection cancelled.")
                return
        else:
            print(f"AUTO-CONFIRM: Proceeding with collection of {len(dates_to_collect):,} dates...")
            print("(Running in auto-confirm mode - no user input required)")

        # Process batches
        print("\n" + "="*80)
        print("STARTING COLLECTION")
        print("="*80)

        start_time = time.time()

        for i, batch in enumerate(batches, 1):
            batch_start = time.time()

            success = self.collect_batch(batch, i, len(batches))

            if success:
                self.stats['batches_completed'] += 1
                self.stats['dates_collected'] += len(batch)

            batch_duration = time.time() - batch_start
            total_duration = time.time() - start_time

            # Progress report
            pct_complete = (i / len(batches)) * 100
            dates_done = sum([len(batches[j]) for j in range(i)])
            dates_remaining = len(dates_to_collect) - dates_done

            avg_time_per_batch = total_duration / i
            est_remaining_time = avg_time_per_batch * (len(batches) - i)

            print(f"\nProgress: {pct_complete:.1f}% ({i}/{len(batches)} batches)")
            print(f"Dates collected: {dates_done:,} / {len(dates_to_collect):,}")
            print(f"Time elapsed: {total_duration/3600:.1f} hours")
            print(f"Est. remaining: {est_remaining_time/3600:.1f} hours")
            print(f"Batch duration: {batch_duration/60:.1f} minutes")

            # Save checkpoint
            checkpoint = {
                'last_completed_batch': i,
                'last_completed_date': batch[-1],
                'dates_collected': dates_done,
                'timestamp': datetime.now().isoformat()
            }
            self.save_checkpoint(checkpoint)

            # Brief pause between batches
            if i < len(batches):
                time.sleep(2)

        # Final report
        self.print_final_report(start_time)

    def print_final_report(self, start_time):
        """Print final collection report"""
        duration = time.time() - start_time

        print("\n" + "="*80)
        print("COLLECTION COMPLETE")
        print("="*80)
        print(f"Total dates processed: {self.stats['dates_collected']:,}")
        print(f"Dates skipped (already collected): {self.stats['dates_skipped']:,}")
        print(f"Batches completed: {self.stats['batches_completed']} / {self.stats['total_batches']}")
        print(f"Total time: {duration/3600:.1f} hours")
        print(f"Errors: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print("\nErrors encountered:")
            for error in self.stats['errors'][:10]:
                print(f"  - {error}")

        # Save final report
        report_file = PROJECT_ROOT / "analysis" / f"gkg_complete_collection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

        print(f"\nFinal report saved: {report_file}")
        print("="*80)

def main():
    parser = argparse.ArgumentParser(
        description='GDELT GKG Complete Collection Orchestrator - Collect all GKG data from Feb 2015 to present'
    )
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        dest='auto_confirm',
        help='Auto-confirm collection without prompting (required for background execution)'
    )

    args = parser.parse_args()

    orchestrator = CompleteCollectionOrchestrator(auto_confirm=args.auto_confirm)
    orchestrator.run_complete_collection()

if __name__ == "__main__":
    main()
