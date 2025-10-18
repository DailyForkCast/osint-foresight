#!/usr/bin/env python3
"""
Monitor both 5801 decompression and China analysis progress
"""

from pathlib import Path
from datetime import datetime

def monitor():
    print("=" * 70)
    print("USASPENDING CHINA ANALYSIS - STATUS DASHBOARD")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    base_path = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/")

    # 1. Check 5801 decompression status
    print("\n[1] 5801.dat Decompression Status:")
    print("-" * 40)

    dat_5801 = base_path / "5801.dat"
    gz_5801 = base_path / "5801.dat.gz"

    if dat_5801.exists():
        size = dat_5801.stat().st_size / 1e9
        progress = (size / 130) * 100
        remaining = (130 - size) / 5  # Assume 5 GB/min

        print(f"  Current size: {size:.2f} GB")
        print(f"  Progress: {progress:.1f}%")

        # Check for end marker
        with open(dat_5801, 'rb') as f:
            f.seek(max(0, dat_5801.stat().st_size - 100))
            last = f.read(100)
            if b'\\.' in last:
                print("  Status: COMPLETE (end marker found)")
                remaining = 0
            else:
                print(f"  Status: DECOMPRESSING (~{remaining:.0f} min remaining)")
    else:
        print("  Status: NOT STARTED")

    # 2. Check all file status
    print("\n[2] All USASpending Files:")
    print("-" * 40)

    files = ['5801', '5836', '5847', '5848', '5862']
    total_size = 0
    complete_count = 0

    for name in files:
        dat = base_path / f"{name}.dat"
        if dat.exists():
            size = dat.stat().st_size / 1e9
            total_size += size

            # Check completion
            with open(dat, 'rb') as f:
                f.seek(max(0, dat.stat().st_size - 100))
                is_complete = b'\\.' in f.read(100)

            if is_complete:
                complete_count += 1
                status = "COMPLETE"
            else:
                status = "PROCESSING"

            print(f"  {name}.dat: {size:7.2f} GB [{status}]")

    print(f"\n  Total: {total_size:.2f} GB")
    print(f"  Files complete: {complete_count}/5")

    # 3. Check China analysis
    print("\n[3] China Pattern Analysis:")
    print("-" * 40)

    results_file = Path("china_pattern_analysis_results.json")
    if results_file.exists():
        import json
        with open(results_file) as f:
            results = json.load(f)
        print(f"  Results found: {len(results)} files analyzed")

        total_mentions = sum(r.get('estimated_total_china_mentions', 0)
                           for r in results.values())
        print(f"  Total China mentions: {total_mentions:,}")
    else:
        print("  Analysis in progress or not started...")

    # 4. Summary
    print("\n" + "=" * 70)
    print("SUMMARY:")

    if complete_count == 5:
        print("✓ All files decompressed successfully!")
        print("✓ Ready for full China pattern analysis")
    else:
        print(f"⏳ Decompression in progress ({complete_count}/5 complete)")

    print("=" * 70)

if __name__ == "__main__":
    monitor()
