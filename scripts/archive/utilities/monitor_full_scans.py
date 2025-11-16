#!/usr/bin/env python3
"""Monitor progress of all 5 concurrent full file scans"""
import time
from datetime import datetime
import json
from pathlib import Path

def check_progress():
    files = ['5848', '5801', '5836', '5847', '5862']

    print("\033[2J\033[H")  # Clear screen
    print("="*80)
    print(" FULL FILE CHINA SCAN - PROGRESS MONITOR ".center(80))
    print(f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ".center(80))
    print("="*80)

    total_china_found = 0
    files_complete = 0

    for file_num in files:
        json_file = Path(f'complete_{file_num}_china.json')
        if json_file.exists():
            # Scan completed
            with open(json_file) as f:
                data = json.load(f)
            china_refs = data.get('china_references', 0)
            total_lines = data.get('total_lines', 0)
            pct = data.get('percentage', 0)

            print(f"\n[{file_num}.dat] COMPLETE")
            print(f"  Lines: {total_lines:,}")
            print(f"  China refs: {china_refs:,} ({pct:.4f}%)")

            if 'mcf_entities' in data and data['mcf_entities']:
                print(f"  MCF entities: {', '.join(list(data['mcf_entities'].keys())[:3])}")

            total_china_found += china_refs
            files_complete += 1
        else:
            # Still scanning or not started
            print(f"\n[{file_num}.dat] SCANNING...")
            print(f"  Status: Processing all lines")
            print(f"  Output: complete_{file_num}_china.json")

    print("\n" + "="*80)
    print(f"Files complete: {files_complete}/5")
    print(f"Total China references found so far: {total_china_found:,}")

    if files_complete == 5:
        print("\n ALL FILES PROCESSED - ANALYSIS COMPLETE!")
        return True
    else:
        expected_time = {
            '5848': 30,  # 222 GB
            '5801': 20,  # 135 GB
            '5836': 20,  # 125 GB
            '5847': 20,  # 127 GB
            '5862': 15   # 52 GB
        }
        print(f"\nEstimated completion times (minutes from start):")
        for f in files:
            if not Path(f'complete_{f}_china.json').exists():
                print(f"  {f}.dat: ~{expected_time[f]} min")

    return False

if __name__ == "__main__":
    while True:
        complete = check_progress()
        if complete:
            break
        time.sleep(30)  # Check every 30 seconds
