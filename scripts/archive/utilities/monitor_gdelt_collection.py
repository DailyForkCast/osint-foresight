#!/usr/bin/env python3
"""
Monitor GDELT Background Collections
Quick status check for all running GDELT collections
"""

import json
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("GDELT COLLECTION STATUS - Phase 1 (2020-2025)")
print("=" * 80)
print(f"Checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

checkpoints = [
    "checkpoints/gdelt_2020.json",
    "checkpoints/gdelt_2021_full_year.json",
    "checkpoints/gdelt_2022.json",
    "checkpoints/gdelt_2023.json",
    "checkpoints/gdelt_2024.json",
    "checkpoints/gdelt_2025.json"
]

total_events = 0
total_months = 0
completed_months = 0

for checkpoint_file in checkpoints:
    path = Path(checkpoint_file)
    year = checkpoint_file.split('_')[1].split('.')[0]

    if not path.exists():
        print(f"{year}: [NOT STARTED]")
        continue

    with open(path) as f:
        data = json.load(f)

    status = data.get('status', 'unknown')
    completed = len(data.get('completed_ranges', []))
    failed = len(data.get('failed_ranges', []))
    events = data.get('total_events', 0)

    total_events += events
    completed_months += completed

    # Expected months for each year
    expected = {
        '2020': 12,
        '2021': 12,
        '2022': 12,
        '2023': 12,
        '2024': 12,
        '2025': 11  # Jan-Nov
    }

    total_months += expected.get(year, 12)

    if status == 'completed':
        status_icon = "[COMPLETE]"
    elif status == 'in_progress':
        status_icon = "[RUNNING]"
    else:
        status_icon = "[STARTED]"

    progress = (completed / expected.get(year, 12)) * 100 if year in expected else 0

    print(f"{year}: {status_icon} {completed}/{expected.get(year, 12)} months | {events:>10,} events | {progress:>5.1f}%")

    if failed > 0:
        print(f"       [WARNING] {failed} failed ranges")

print("\n" + "=" * 80)
print(f"TOTAL PROGRESS: {completed_months}/{total_months} months ({(completed_months/total_months*100):.1f}%)")
print(f"TOTAL EVENTS COLLECTED: {total_events:,}")
print("=" * 80)

print("\nLOG FILES:")
print("  tail -f logs/gdelt_2020_collection.log")
print("  tail -f logs/gdelt_2021_collection.log")
print("  tail -f logs/gdelt_2022_collection.log")
print("  tail -f logs/gdelt_2023_collection.log")
print("  tail -f logs/gdelt_2024_collection.log")
print("  tail -f logs/gdelt_2025_collection.log")
