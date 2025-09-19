#!/usr/bin/env python3
"""
Monitor TED processing progress
"""

import json
from pathlib import Path
from datetime import datetime
import time

def monitor_progress():
    """Monitor TED processing progress"""

    output_dir = Path("data/processed/ted_complete_analysis")
    checkpoint_file = output_dir / "processing_checkpoint.json"

    if not checkpoint_file.exists():
        print("No checkpoint file found - processing may not have started yet")
        return

    try:
        with open(checkpoint_file, 'r') as f:
            data = json.load(f)
            processed = data.get('processed', [])

        print(f"\nTED Processing Status - {datetime.now().strftime('%H:%M:%S')}")
        print("="*50)
        print(f"Files processed: {len(processed)}")

        # Group by year
        by_year = {}
        for file in processed:
            year = file.split('_')[2]
            by_year[year] = by_year.get(year, 0) + 1

        print("\nProgress by year:")
        for year in sorted(by_year.keys()):
            print(f"  {year}: {by_year[year]}/12 months")

        # Check for results
        for year in range(2015, 2026):
            year_dir = output_dir / str(year)
            if year_dir.exists():
                contract_file = year_dir / f"china_contracts_{year}.json"
                stats_file = year_dir / f"statistics_{year}.json"

                if contract_file.exists():
                    with open(contract_file, 'r') as f:
                        contracts = json.load(f)
                    print(f"  {year}: {len(contracts)} China contracts found")

        print("\nProcessing continues in background...")

    except Exception as e:
        print(f"Error reading checkpoint: {e}")

if __name__ == "__main__":
    monitor_progress()
