#!/usr/bin/env python3
"""
Monitor Batch 3 completion and automatically switch to parallel collection

This script:
1. Checks the checkpoint file for Batch 3 completion
2. When complete, terminates the single collector
3. Launches the parallel orchestrator
"""

import time
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

CHECKPOINT_FILE = Path("checkpoints/gkg_complete_collection.json")
PARALLEL_SCRIPT = "scripts/collectors/gdelt_gkg_parallel_orchestrator.py"

print("="*80)
print("BATCH 3 MONITOR - Waiting for completion to switch to parallel collection")
print("="*80)
print()
print("Current status: Batch 3/179 in progress (50 dates)")
print("Estimated completion: ~7.5 hours from start")
print()
print("When Batch 3 completes:")
print("  1. Single collector will be terminated")
print("  2. Parallel orchestrator (5 shards) will launch")
print("  3. Collection will continue ~5x faster")
print()
print("Monitoring checkpoint file...")
print()

check_count = 0
last_batch = 2  # We know batches 1 and 2 are complete

while True:
    check_count += 1

    # Check checkpoint file
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                checkpoint = json.load(f)

            current_batch = checkpoint.get('last_completed_batch', 0)

            if current_batch > last_batch:
                last_batch = current_batch
                dates_collected = checkpoint.get('dates_collected', 0)
                timestamp = checkpoint.get('timestamp', '')

                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] BATCH {current_batch} COMPLETED!")
                print(f"  Dates collected: {dates_collected}")
                print(f"  Timestamp: {timestamp}")

                if current_batch >= 3:
                    print("\n" + "="*80)
                    print("BATCH 3 COMPLETE - Switching to parallel collection!")
                    print("="*80)

                    # Give it a moment to finalize
                    time.sleep(5)

                    # Kill the single collector
                    print("\nTerminating single collector...")
                    try:
                        # Find and kill python process running gdelt_gkg_complete_orchestrator.py
                        result = subprocess.run(
                            ['taskkill', '/F', '/FI', 'IMAGENAME eq python.exe', '/FI', 'WINDOWTITLE eq gdelt_gkg_complete_orchestrator*'],
                            capture_output=True,
                            text=True
                        )
                        print(f"  {result.stdout}")
                    except Exception as e:
                        print(f"  Note: {e}")
                        print("  (Process may have already exited)")

                    # Launch parallel orchestrator
                    print("\nLaunching parallel orchestrator (5 shards, 15 dates/batch)...")
                    print(f"  Script: {PARALLEL_SCRIPT}")
                    print()

                    subprocess.Popen(
                        [sys.executable, PARALLEL_SCRIPT, '--yes'],
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )

                    print("✓ Parallel orchestrator launched!")
                    print()
                    print("="*80)
                    print("TRANSITION COMPLETE")
                    print("="*80)
                    print()
                    print(f"Total dates collected by single collector: {dates_collected}")
                    print(f"Remaining dates: ~{3751 - dates_collected}")
                    print()
                    print("The 5 parallel collectors will now handle the remaining dates.")
                    print("Expected completion: ~11 days (vs ~56 days with single collector)")
                    print()
                    print("You can monitor progress with:")
                    print("  - Check shard databases: F:/OSINT_WAREHOUSE/osint_master_shard[1-5].db")
                    print("  - View shard checkpoints: checkpoints/gkg_shard*_checkpoint.json")
                    print()

                    sys.exit(0)

        except Exception as e:
            print(f"[ERROR] Reading checkpoint: {e}")

    # Status update every 30 minutes
    if check_count % 60 == 0:
        elapsed_hours = check_count * 30 / 3600
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Still monitoring... ({elapsed_hours:.1f}h elapsed, last completed: Batch {last_batch})")

    # Check every 30 seconds
    time.sleep(30)
