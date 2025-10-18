#!/usr/bin/env python3
"""Quick status check for China scans"""
from pathlib import Path
import json
from datetime import datetime

files = ['5848', '5801', '5836', '5847', '5862']
file_sizes_gb = {'5848': 222.45, '5801': 134.85, '5836': 124.72, '5847': 126.50, '5862': 52.05}

print(f"\nChina Scan Status - {datetime.now().strftime('%H:%M:%S')}")
print("="*60)

total_china = 0
total_in_us = 0
completed = 0

for f in files:
    json_file = Path(f'smart_scan_{f}.json')
    if json_file.exists():
        with open(json_file) as jf:
            data = json.load(jf)
        china = data.get('china_references', 0)
        in_us = data.get('chinese_activity_in_us', 0)
        excluded = data.get('false_positives_excluded', 0)
        total_china += china
        total_in_us += in_us
        completed += 1
        print(f"{f}.dat: DONE - {china:,} China refs, {in_us:,} in U.S., {excluded:,} excluded")
    else:
        print(f"{f}.dat: Processing {file_sizes_gb[f]:.1f} GB...")

print("-"*60)
print(f"Completed: {completed}/5 files")
if completed > 0:
    print(f"Total China references: {total_china:,}")
    print(f"Chinese activity in U.S.: {total_in_us:,}")
