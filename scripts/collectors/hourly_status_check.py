#!/usr/bin/env python3
"""
Hourly status checker for Think Tank collection.
Logs results to a monitoring file.
"""

import json
from pathlib import Path
from datetime import datetime

LOG_FILE = Path("F:/ThinkTank_Sweeps/us_can_test_log.txt")
LOCK_FILE = Path("F:/ThinkTank_Sweeps/STATE/.lock")
OUTPUT_DIR = Path("F:/ThinkTank_Sweeps/US_CAN")
MONITOR_LOG = Path("F:/ThinkTank_Sweeps/hourly_monitoring.log")

def log_status():
    """Check and log collection status."""
    timestamp = datetime.now().isoformat()

    status_lines = []
    status_lines.append(f"\n{'='*60}")
    status_lines.append(f"Status Check: {timestamp}")
    status_lines.append(f"{'='*60}")

    # Check if running
    if LOCK_FILE.exists():
        lock_age_min = (datetime.now().timestamp() - LOCK_FILE.stat().st_mtime) / 60
        status_lines.append(f"[RUNNING] Lock age: {lock_age_min:.1f} minutes")
    else:
        status_lines.append(f"[COMPLETE] No active lock - collection finished")

    # Check log file
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        status_lines.append(f"[LOG] {len(lines)} log entries")

        # Get last line for activity check
        if lines:
            last_line = lines[-1].strip()
            status_lines.append(f"[LAST] {last_line[:100]}...")

    # Check outputs
    if OUTPUT_DIR.exists():
        date_dirs = sorted([d for d in OUTPUT_DIR.iterdir() if d.is_dir()], reverse=True)
        if date_dirs:
            latest_dir = date_dirs[0]
            items_json = latest_dir / "items.json"
            run_summary = latest_dir / "run_summary.json"

            if items_json.exists():
                try:
                    with open(items_json, 'r', encoding='utf-8') as f:
                        items = json.load(f)
                    status_lines.append(f"[ITEMS] {len(items)} items collected so far")
                except:
                    status_lines.append(f"[ITEMS] items.json exists but couldn't parse")

            if run_summary.exists():
                try:
                    with open(run_summary, 'r', encoding='utf-8') as f:
                        summary = json.load(f)
                    status_lines.append(f"[SUMMARY] Complete - {summary.get('items_collected', 0)} items, {summary.get('failures', 0)} failures")
                except:
                    status_lines.append(f"[SUMMARY] run_summary.json exists but couldn't parse")

    # Write to monitoring log
    with open(MONITOR_LOG, 'a', encoding='utf-8') as f:
        f.write('\n'.join(status_lines) + '\n')

    # Also print to console
    print('\n'.join(status_lines))

    # Return completion status
    return not LOCK_FILE.exists()

if __name__ == "__main__":
    is_complete = log_status()
    if is_complete:
        print("\n[INFO] Collection appears complete. Check outputs in F:\\ThinkTank_Sweeps\\US_CAN\\")
