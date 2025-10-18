#!/usr/bin/env python3
"""
Simple status check for 5801.dat re-decompression
"""

from pathlib import Path
from datetime import datetime

def check_status():
    base_path = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/")

    print("=" * 70)
    print("5801.dat RE-DECOMPRESSION STATUS")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Check all relevant files
    files = {
        '5801.dat': 'CURRENT (re-decompressing)',
        '5801.dat.gz': 'SOURCE',
        '5801.dat.truncated': 'BACKUP (old truncated)',
        '5801_decompressed.dat': 'OLD PARTIAL'
    }

    for filename, desc in files.items():
        f = base_path / filename
        if f.exists():
            size_gb = f.stat().st_size / 1e9
            print(f"{filename:25} | {size_gb:10.2f} GB | {desc}")
        else:
            print(f"{filename:25} | NOT FOUND  | {desc}")

    print("-" * 70)

    # Current progress estimate
    current = base_path / "5801.dat"
    if current.exists():
        size = current.stat().st_size / 1e9
        progress = (size / 130) * 100  # Assuming ~130 GB target

        print(f"Progress: {size:.2f} GB / ~130 GB ({progress:.1f}%)")

        if progress < 100:
            remaining = 130 - size
            # Assuming ~5 GB/min based on observed speed
            time_remaining = remaining / 5
            print(f"Estimated time remaining: {time_remaining:.0f} minutes")

        # Check last bytes for completion marker
        with open(current, 'rb') as f:
            f.seek(max(0, current.stat().st_size - 100))
            last_bytes = f.read(100)
            if b'\\.' in last_bytes:
                print("[!] PostgreSQL end marker detected - file may be complete")

    print("=" * 70)

    # Summary of all USASpending files
    print("\nAll USASpending Large Files Status:")
    large_files = ['5801', '5836', '5847', '5848', '5862']
    total_size = 0

    for name in large_files:
        dat = base_path / f"{name}.dat"
        if dat.exists():
            size = dat.stat().st_size / 1e9
            total_size += size
            status = "RE-DECOMPRESSING" if name == "5801" else "COMPLETE"
            print(f"  {name}.dat: {size:7.2f} GB  [{status}]")

    print(f"\nTotal data ready: {total_size:.2f} GB")
    print(f"Expected total after 5801 complete: ~655 GB")

if __name__ == "__main__":
    check_status()
