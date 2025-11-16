#!/usr/bin/env python3
"""
Monitor USAspending Production Run - Terminal C

Real-time monitoring of the production processing job.
Tracks progress, detection rates, database growth, and estimated completion.
"""

import json
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timedelta


def format_duration(seconds):
    """Format seconds into readable duration."""
    hours = seconds / 3600
    if hours < 1:
        return f"{seconds/60:.1f} minutes"
    else:
        return f"{hours:.2f} hours"


def get_database_size(db_path):
    """Get database size in GB."""
    if db_path.exists():
        return db_path.stat().st_size / (1024**3)
    return 0.0


def get_detection_count(db_path):
    """Get count of detections in database."""
    if not db_path.exists():
        return 0

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM usaspending_china_comprehensive')
        count = cur.fetchone()[0]
        conn.close()
        return count
    except:
        return 0


def monitor_production():
    """Monitor production run progress."""

    checkpoint_file = Path("data/processed/usaspending_production_full/checkpoint.json")
    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
    data_dir = Path("F:/OSINT_DATA/USAspending/extracted_data")

    total_files = len(list(data_dir.glob("*.dat.gz")))

    print("="*80)
    print("TERMINAL C - USASPENDING PRODUCTION MONITOR")
    print("="*80)
    print(f"Monitor started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total files to process: {total_files}")
    print(f"Checkpoint file: {checkpoint_file}")
    print(f"Database: {db_path}")
    print("="*80)
    print("\nPress Ctrl+C to stop monitoring\n")

    # Initial state
    last_detections = 0
    last_check_time = time.time()

    try:
        while True:
            # Check if checkpoint exists
            if not checkpoint_file.exists():
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting for production run to start...")
                time.sleep(10)
                continue

            # Load checkpoint
            with open(checkpoint_file, 'r') as f:
                checkpoint = json.load(f)

            # Calculate progress
            files_processed = checkpoint.get('files_processed', 0)
            total_records = checkpoint.get('total_records', 0)
            total_detections = checkpoint.get('total_detections', 0)
            total_value = checkpoint.get('total_value', 0.0)
            processing_times = checkpoint.get('processing_times', [])

            # Calculate rates
            if total_records > 0:
                detection_rate = (total_detections / total_records) * 100
            else:
                detection_rate = 0.0

            # Calculate ETA
            if len(processing_times) > 0:
                avg_time_per_file = sum(processing_times) / len(processing_times)
                remaining_files = total_files - files_processed
                estimated_remaining_seconds = avg_time_per_file * remaining_files

                start_time_str = checkpoint.get('start_time')
                if start_time_str:
                    start_time = datetime.fromisoformat(start_time_str)
                    elapsed = (datetime.now() - start_time).total_seconds()
                else:
                    elapsed = sum(processing_times)

                eta = datetime.now() + timedelta(seconds=estimated_remaining_seconds)
                eta_str = eta.strftime('%Y-%m-%d %H:%M')
            else:
                elapsed = 0
                estimated_remaining_seconds = 0
                eta_str = "Calculating..."

            # Database stats
            db_size = get_database_size(db_path)
            db_count = get_detection_count(db_path)

            # Detection rate since last check
            current_time = time.time()
            time_since_last = current_time - last_check_time
            detections_since_last = total_detections - last_detections
            if time_since_last > 0:
                detections_per_minute = (detections_since_last / time_since_last) * 60
            else:
                detections_per_minute = 0

            # Update last check
            last_detections = total_detections
            last_check_time = current_time

            # Print status
            print(f"\n{'='*80}")
            print(f"STATUS UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}")
            print(f"Progress: {files_processed}/{total_files} files ({files_processed/total_files*100:.1f}%)")
            print(f"")
            print(f"Records Processed: {total_records:,}")
            print(f"Detections Found: {total_detections:,}")
            print(f"Detection Rate: {detection_rate:.4f}%")
            print(f"Total Value: ${total_value:,.2f}")
            print(f"")
            print(f"Elapsed Time: {format_duration(elapsed)}")
            print(f"Estimated Remaining: {format_duration(estimated_remaining_seconds)}")
            print(f"Estimated Completion: {eta_str}")
            print(f"")
            print(f"Database Size: {db_size:.2f} GB")
            print(f"Database Records: {db_count:,}")
            print(f"")
            print(f"Current Detection Rate: {detections_per_minute:.1f} detections/minute")
            print(f"{'='*80}")

            # Check if complete
            if files_processed >= total_files:
                print("\n[COMPLETE] Production run finished!")
                print(f"Final Statistics:")
                print(f"  Total Records: {total_records:,}")
                print(f"  Total Detections: {total_detections:,}")
                print(f"  Detection Rate: {detection_rate:.4f}%")
                print(f"  Total Value: ${total_value:,.2f}")
                print(f"  Total Time: {format_duration(elapsed)}")
                break

            # Wait before next check
            time.sleep(30)  # Check every 30 seconds

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
        print(f"Last status: {files_processed}/{total_files} files, {total_detections:,} detections")


if __name__ == '__main__':
    monitor_production()
