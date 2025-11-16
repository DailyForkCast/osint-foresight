#!/usr/bin/env python3
"""
USPTO CPC Processing Monitor
Tracks progress of CPC classification data import
"""

import sqlite3
import os
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
LOG_FILE = "C:/Projects/OSINT - Foresight/uspto_cpc_processing_log.txt"
CPC_DIR = "F:/USPTO Data/US_PGPub_CPC_MCF_XML_2025-09-01/"

def check_process_running(process_name="process_uspto_cpc"):
    """Check if the USPTO CPC process is running"""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return process_name in result.stdout
    except:
        return False

def get_database_stats():
    """Get current CPC classification statistics"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='uspto_cpc_classifications'
        """)

        if not cursor.fetchone():
            conn.close()
            return None

        # Total records
        cursor.execute("SELECT COUNT(*) FROM uspto_cpc_classifications")
        total = cursor.fetchone()[0]

        # Strategic technology records
        cursor.execute("""
            SELECT COUNT(*) FROM uspto_cpc_classifications
            WHERE is_strategic = 1
        """)
        strategic = cursor.fetchone()[0]

        # Unique publications
        cursor.execute("""
            SELECT COUNT(DISTINCT publication_number)
            FROM uspto_cpc_classifications
        """)
        unique_pubs = cursor.fetchone()[0]

        # Top 5 strategic technologies
        cursor.execute("""
            SELECT technology_area, COUNT(*) as count
            FROM uspto_cpc_classifications
            WHERE is_strategic = 1 AND technology_area IS NOT NULL
            GROUP BY technology_area
            ORDER BY count DESC
            LIMIT 5
        """)
        top_tech = cursor.fetchall()

        # Latest processed date
        cursor.execute("""
            SELECT MAX(processed_date) FROM uspto_cpc_classifications
        """)
        latest = cursor.fetchone()[0]

        conn.close()

        return {
            'total': total,
            'strategic': strategic,
            'unique_publications': unique_pubs,
            'top_technologies': top_tech,
            'latest_processed': latest
        }

    except sqlite3.OperationalError as e:
        if "locked" in str(e).lower():
            return "DATABASE_LOCKED"
        return None
    except Exception as e:
        return None

def count_xml_files():
    """Count total XML files to process"""
    try:
        xml_files = list(Path(CPC_DIR).glob("US_PGPub_CPC_MCF_*.xml"))
        return len(xml_files)
    except:
        return 177  # Known count

def get_log_tail(lines=20):
    """Get last N lines from log file"""
    try:
        if not os.path.exists(LOG_FILE):
            return None

        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            return all_lines[-lines:] if all_lines else None
    except:
        return None

def estimate_completion(stats, total_files):
    """Estimate completion time based on current progress"""
    if not stats or stats == "DATABASE_LOCKED":
        return None

    if stats['total'] == 0:
        return None

    # Rough estimate: ~500K classifications per file on average
    avg_per_file = 500000
    estimated_total = total_files * avg_per_file
    current = stats['total']

    progress_pct = (current / estimated_total) * 100 if estimated_total > 0 else 0

    return {
        'progress_pct': progress_pct,
        'files_estimated': int(current / avg_per_file) if avg_per_file > 0 else 0,
        'total_files': total_files
    }

def display_status():
    """Display comprehensive status"""
    print("=" * 80)
    print("USPTO CPC PROCESSING MONITOR")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check if process is running
    is_running = check_process_running()
    print(f"Process Status: {'[RUNNING]' if is_running else '[NOT RUNNING]'}")
    print()

    # Get database statistics
    print("Database Statistics:")
    print("-" * 80)

    stats = get_database_stats()

    if stats == "DATABASE_LOCKED":
        print("  [OK] Database is LOCKED (actively writing - good sign!)")
        print("  [IN PROGRESS] Processing in progress...")
    elif stats is None:
        print("  [WARNING] Unable to query database")
        print("  (Table may not exist yet - processing may be starting)")
    else:
        print(f"  Total Classifications: {stats['total']:,}")
        print(f"  Strategic Technology Classifications: {stats['strategic']:,}")
        print(f"  Unique Publications: {stats['unique_publications']:,}")
        print(f"  Latest Processed: {stats['latest_processed']}")

        if stats['top_technologies']:
            print(f"\n  Top 5 Strategic Technologies:")
            for tech, count in stats['top_technologies']:
                print(f"    - {tech}: {count:,}")

        # Estimate progress
        total_files = count_xml_files()
        est = estimate_completion(stats, total_files)
        if est:
            print(f"\n  Progress Estimate:")
            print(f"    Files processed: ~{est['files_estimated']}/{est['total_files']}")
            print(f"    Completion: ~{est['progress_pct']:.1f}%")

    print()
    print("Recent Log Output:")
    print("-" * 80)

    log_tail = get_log_tail(15)
    if log_tail:
        for line in log_tail:
            print(f"  {line.rstrip()}")
    else:
        print("  (Log file empty or buffered - check back in a few minutes)")

    print()
    print("=" * 80)

    if is_running:
        print("[OK] Processing is active. Check back periodically for updates.")
        print("     Estimated total time: Several hours (177 files x ~2-3 min/file)")
    else:
        print("[WARNING] Process appears to have stopped.")
        print("          Check log file for errors or completion message.")

    print("=" * 80)

def monitor_loop(interval=300):
    """Continuous monitoring with interval (default 5 minutes)"""
    print("Starting continuous monitoring...")
    print(f"Update interval: {interval} seconds ({interval//60} minutes)")
    print("Press Ctrl+C to stop\n")

    try:
        iteration = 0
        while True:
            iteration += 1
            print(f"\n{'='*80}")
            print(f"UPDATE #{iteration}")
            print(f"{'='*80}\n")

            display_status()

            print(f"\nNext update in {interval//60} minutes...")
            print(f"Time: {(datetime.now() + timedelta(seconds=interval)).strftime('%H:%M:%S')}")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
        print("Processing continues in background.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--loop":
            # Continuous monitoring mode
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
            monitor_loop(interval)
        elif sys.argv[1] == "--help":
            print("USPTO CPC Processing Monitor")
            print("\nUsage:")
            print("  python monitor_uspto_cpc_progress.py           # Single status check")
            print("  python monitor_uspto_cpc_progress.py --loop    # Continuous monitoring (5 min)")
            print("  python monitor_uspto_cpc_progress.py --loop 60 # Continuous monitoring (1 min)")
    else:
        # Single status check
        display_status()
