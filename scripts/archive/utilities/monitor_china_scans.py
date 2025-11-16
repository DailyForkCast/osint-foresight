#!/usr/bin/env python3
"""Monitor progress of all 5 concurrent China scans"""
import time
from datetime import datetime
import json
from pathlib import Path
import subprocess

def check_progress():
    files = ['5848', '5801', '5836', '5847', '5862']

    print("\033[2J\033[H")  # Clear screen
    print("="*80)
    print(" CHINA SCAN PROGRESS - REFINED ANALYSIS ".center(80))
    print(f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ".center(80))
    print("="*80)
    print("\nExcluding: China Lake, China Spring, China Grove (U.S. locations)")
    print("Including: Chinese companies/government/investment IN the U.S.")
    print("-"*80)

    total_china_found = 0
    total_china_in_us = 0
    files_complete = 0

    for file_num in files:
        # Check for completed refined scan
        json_file = Path(f'smart_scan_{file_num}.json')
        if json_file.exists():
            try:
                with open(json_file) as f:
                    data = json.load(f)
                china_refs = data.get('china_references', 0)
                china_in_us = data.get('chinese_activity_in_us', 0)
                total_lines = data.get('total_lines', 0)
                pct = data.get('percentage', 0)
                excluded = data.get('false_positives_excluded', 0)

                print(f"\n[{file_num}.dat] COMPLETE")
                print(f"  Lines: {total_lines:,}")
                print(f"  China refs: {china_refs:,} ({pct:.4f}%)")
                print(f"  China IN U.S.: {china_in_us:,}")
                print(f"  Excluded (U.S. locations): {excluded:,}")

                if 'mcf_entities' in data and data['mcf_entities']:
                    top_mcf = list(data['mcf_entities'].items())[:3]
                    print(f"  Top MCF: {', '.join([f'{k}({v})' for k,v in top_mcf])}")

                if 'activity_types' in data:
                    acts = data['activity_types']
                    if acts.get('embassy_consulate', 0) > 0:
                        print(f"  Embassy/Consulate: {acts['embassy_consulate']:,}")
                    if acts.get('trade_import_export', 0) > 0:
                        print(f"  Trade/Import/Export: {acts['trade_import_export']:,}")
                    if acts.get('ownership_investment', 0) > 0:
                        print(f"  Ownership/Investment: {acts['ownership_investment']:,}")

                total_china_found += china_refs
                total_china_in_us += china_in_us
                files_complete += 1
            except Exception as e:
                print(f"\n[{file_num}.dat] ERROR reading results: {e}")
        else:
            # Check if process is running
            try:
                # Try to find the process
                result = subprocess.run(['tasklist', '/FI', f'WINDOWTITLE eq *{file_num}*'],
                                      capture_output=True, text=True)
                if 'python' in result.stdout.lower():
                    print(f"\n[{file_num}.dat] SCANNING...")
                    print(f"  Status: Processing all lines")
                    print(f"  Output: smart_scan_{file_num}.json")
                else:
                    print(f"\n[{file_num}.dat] NOT STARTED or CRASHED")
            except:
                print(f"\n[{file_num}.dat] PENDING")
                print(f"  Waiting to start...")

    print("\n" + "="*80)
    print(f"Files complete: {files_complete}/5")
    print(f"Total China references found: {total_china_found:,}")
    print(f"Chinese activity IN U.S.: {total_china_in_us:,}")

    if files_complete == 5:
        print("\n✓ ALL FILES PROCESSED - ANALYSIS COMPLETE!")
        print("\nKey Findings:")
        print(f"  • Total China references (excluding U.S. locations): {total_china_found:,}")
        print(f"  • Chinese activity specifically IN the U.S.: {total_china_in_us:,}")
        return True
    else:
        # Estimate completion based on file sizes
        file_sizes = {
            '5848': 222.45,  # GB
            '5801': 134.85,
            '5836': 124.72,
            '5847': 126.50,
            '5862': 52.05
        }

        print(f"\nEstimated processing times (based on ~100 MB/sec):")
        for f in files:
            if not Path(f'smart_scan_{f}.json').exists():
                est_minutes = file_sizes[f] * 10 / 60  # Rough estimate
                print(f"  {f}.dat: ~{est_minutes:.0f} minutes")

    return False

if __name__ == "__main__":
    while True:
        complete = check_progress()
        if complete:
            break
        time.sleep(30)  # Check every 30 seconds
