#!/usr/bin/env python3
"""
EPO Automated Patent Collection Scheduler
Runs every 2-3 hours to collect the next batch of 2000 patents
Manages session resets and continues from checkpoints
"""

import schedule
import time
import subprocess
import json
import os
from datetime import datetime
import random

class EPOAutomatedScheduler:
    def __init__(self):
        self.checkpoint_dir = "F:/OSINT_DATA/epo_checkpoints"
        self.log_file = "F:/OSINT_DATA/epo_scheduler.log"
        self.collection_script = "scripts/epo_paginated_collector.py"
        self.expanded_script = "scripts/epo_expanded_collector.py"

    def log(self, message):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)

        with open(self.log_file, 'a') as f:
            f.write(log_message + '\n')

    def check_progress(self):
        """Check collection progress from checkpoints"""
        progress = {}

        if os.path.exists(self.checkpoint_dir):
            for file in os.listdir(self.checkpoint_dir):
                if file.endswith('_checkpoint.json'):
                    with open(os.path.join(self.checkpoint_dir, file), 'r') as f:
                        data = json.load(f)
                        query_id = data['query_id']
                        progress[query_id] = {
                            'retrieved': data.get('total_retrieved', 0),
                            'total': data.get('total_found', 'Unknown'),
                            'status': data.get('status', 'unknown'),
                            'last_offset': data.get('last_offset', 0)
                        }

        return progress

    def run_collection(self):
        """Run patent collection"""
        self.log("="*60)
        self.log("Starting scheduled patent collection")

        # Check current progress
        progress = self.check_progress()
        self.log(f"Current progress: {len(progress)} queries tracked")

        for query_id, stats in progress.items():
            if stats['total'] != 'Unknown':
                percentage = (stats['retrieved'] / stats['total']) * 100
                self.log(f"  {query_id}: {stats['retrieved']}/{stats['total']} ({percentage:.1f}%)")
            else:
                self.log(f"  {query_id}: {stats['retrieved']} collected")

        # Run the paginated collector
        self.log("Executing paginated collector...")
        try:
            result = subprocess.run(
                ['python', self.collection_script],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                self.log("Collection completed successfully")
                # Parse output for results
                output_lines = result.stdout.split('\n')
                for line in output_lines[-20:]:  # Check last 20 lines for results
                    if 'Retrieved:' in line or 'Total' in line:
                        self.log(f"  {line.strip()}")
            else:
                self.log(f"Collection failed with error: {result.stderr[:200]}")

        except subprocess.TimeoutExpired:
            self.log("Collection timed out after 5 minutes")
        except Exception as e:
            self.log(f"Collection error: {e}")

        # Check progress after collection
        new_progress = self.check_progress()
        self.log("Updated progress:")

        patents_collected = 0
        for query_id, stats in new_progress.items():
            old_count = progress.get(query_id, {}).get('retrieved', 0)
            new_count = stats['retrieved']
            if new_count > old_count:
                self.log(f"  {query_id}: +{new_count - old_count} new patents (total: {new_count})")
                patents_collected += (new_count - old_count)

        if patents_collected > 0:
            self.log(f"Total new patents collected: {patents_collected}")
        else:
            self.log("No new patents collected (may need session reset)")

        self.log("="*60)
        return patents_collected

    def run_expanded_collection(self):
        """Run expanded collection for new companies"""
        self.log("Running expanded collection for additional companies...")

        try:
            result = subprocess.run(
                ['python', self.expanded_script],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode == 0:
                self.log("Expanded collection completed")
            else:
                self.log(f"Expanded collection failed: {result.stderr[:200]}")

        except Exception as e:
            self.log(f"Expanded collection error: {e}")

    def scheduled_job(self):
        """Job to run on schedule"""
        self.log("\n" + "="*70)
        self.log("SCHEDULED PATENT COLLECTION STARTING")
        self.log("="*70)

        # Run main collection
        patents = self.run_collection()

        # If we didn't get many patents, might be at session limit
        if patents < 100:
            self.log("Low collection count - session may need reset")
            self.log("Waiting for session to reset...")
            # Add random jitter to avoid exact timing
            wait_time = random.randint(10, 30)
            self.log(f"Waiting {wait_time} minutes before retry...")
            time.sleep(wait_time * 60)

            # Try again
            self.log("Retrying after session reset...")
            self.run_collection()

        # Occasionally run expanded collection
        if random.random() < 0.3:  # 30% chance
            self.log("Running expanded collection for variety...")
            time.sleep(60)  # Wait 1 minute
            self.run_expanded_collection()

        self.log("Scheduled job complete\n")

    def start_scheduler(self):
        """Start the automated scheduler"""
        self.log("="*70)
        self.log("EPO AUTOMATED PATENT COLLECTION SCHEDULER")
        self.log("="*70)
        self.log("Schedule: Every 2-3 hours with random variation")
        self.log("Session reset handling: Automatic")
        self.log("Checkpoint recovery: Enabled")
        self.log("="*70)

        # Run immediately
        self.scheduled_job()

        # Schedule regular runs
        schedule.every(2).to(3).hours.do(self.scheduled_job)

        self.log("Scheduler started. Next run will be in 2-3 hours.")
        self.log("Press Ctrl+C to stop.")

        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    scheduler = EPOAutomatedScheduler()

    # Check if running as one-time or continuous
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run once and exit
        scheduler.scheduled_job()
    else:
        # Start continuous scheduler
        try:
            scheduler.start_scheduler()
        except KeyboardInterrupt:
            scheduler.log("\nScheduler stopped by user")

if __name__ == "__main__":
    main()
