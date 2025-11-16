#!/usr/bin/env python3
"""
Check if Think Tank collection is complete and show results.
"""

import os
import json
from pathlib import Path
from datetime import datetime

LOG_FILE = Path("F:/ThinkTank_Sweeps/us_can_test_log.txt")
STATE_FILE = Path("F:/ThinkTank_Sweeps/STATE/thinktanks_state.json")
LOCK_FILE = Path("F:/ThinkTank_Sweeps/STATE/.lock")
OUTPUT_DIR = Path("F:/ThinkTank_Sweeps/US_CAN")

def check_status():
    """Check collection status."""
    print("="*60)
    print("Think Tank Collection Status Check")
    print("="*60)
    print()

    # Check if lock exists
    if LOCK_FILE.exists():
        print("[RUNNING] Collection in progress (lock file exists)")
        lock_age = (datetime.now().timestamp() - LOCK_FILE.stat().st_mtime) / 60
        print(f"          Lock age: {lock_age:.1f} minutes")
    else:
        print("[COMPLETE] No active collection (no lock file)")

    print()

    # Check log file
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print(f"[LOG] Log file: {len(lines)} lines")
        print()
        print("Last 10 log entries:")
        print("-" * 60)
        for line in lines[-10:]:
            print(line.rstrip())
        print("-" * 60)
    else:
        print("[ERROR] No log file found")

    print()

    # Check for outputs
    if OUTPUT_DIR.exists():
        date_dirs = sorted([d for d in OUTPUT_DIR.iterdir() if d.is_dir()], reverse=True)
        if date_dirs:
            latest_dir = date_dirs[0]
            print(f"[OUTPUT] Latest output: {latest_dir.name}")

            # Check for key files
            items_json = latest_dir / "items.json"
            if items_json.exists():
                with open(items_json, 'r', encoding='utf-8') as f:
                    items = json.load(f)
                print(f"         [OK] items.json: {len(items)} items collected")

            run_summary = latest_dir / "run_summary.json"
            if run_summary.exists():
                with open(run_summary, 'r', encoding='utf-8') as f:
                    summary = json.load(f)
                print(f"         [OK] run_summary.json exists")
                print(f"              Items collected: {summary.get('items_collected', 0)}")
                print(f"              Failures: {summary.get('failures', 0)}")

            failures_md = latest_dir / "download_failures.md"
            if failures_md.exists():
                print(f"         [OK] download_failures.md exists")

            qa_report = latest_dir / "qa_report.json"
            if qa_report.exists():
                print(f"         [OK] qa_report.json exists")
        else:
            print("[PENDING] No output directories found yet")
    else:
        print("[PENDING] Output directory not created yet")

    print()
    print("="*60)

if __name__ == "__main__":
    check_status()
