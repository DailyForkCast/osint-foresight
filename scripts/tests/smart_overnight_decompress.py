#!/usr/bin/env python3
"""
Smart Overnight Decompression - Skips completed files
"""

import gzip
import shutil
from pathlib import Path
from datetime import datetime
import time

def decompress_remaining():
    files = [
        "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5801.dat.gz",
        "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5836.dat.gz",
        "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5847.dat.gz",
        "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5848.dat.gz",
        "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5862.dat.gz"
    ]

    print("="*70)
    print("SMART OVERNIGHT DECOMPRESSION")
    print("="*70)
    print(f"Start time: {datetime.now()}")
    print()

    completed = []
    to_process = []

    # Check what's already done
    for file_path in files:
        gz_file = Path(file_path)
        dat_file = gz_file.with_suffix('')

        if dat_file.exists():
            size = dat_file.stat().st_size / 1e9
            print(f"[SKIP] {gz_file.name} - Already decompressed ({size:.2f} GB)")
            completed.append(gz_file.name)
        elif gz_file.exists():
            size = gz_file.stat().st_size / 1e9
            print(f"[TODO] {gz_file.name} - Ready to decompress ({size:.2f} GB)")
            to_process.append(file_path)
        else:
            print(f"[MISS] {gz_file.name} - File not found")

    print(f"\nCompleted: {len(completed)}")
    print(f"To process: {len(to_process)}")

    if not to_process:
        print("\nAll files already decompressed!")
        return

    total_gb = sum(Path(f).stat().st_size / 1e9 for f in to_process)
    print(f"Total to decompress: {total_gb:.2f} GB")
    print(f"Estimated time: {total_gb * 10:.0f} minutes")
    print("\n" + "-"*70)

    # Process remaining files
    for i, file_path in enumerate(to_process, 1):
        gz_file = Path(file_path)
        dat_file = gz_file.with_suffix('')

        print(f"\n[File {i}/{len(to_process)}] {gz_file.name}")
        print(f"  Size: {gz_file.stat().st_size / 1e9:.2f} GB")
        print(f"  Starting at {datetime.now().strftime('%H:%M:%S')}")

        start = time.time()

        try:
            # Decompress with progress
            with gzip.open(gz_file, 'rb') as f_in:
                with open(dat_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out, length=10*1024*1024)

            elapsed = time.time() - start
            final_size = dat_file.stat().st_size / 1e9

            print(f"  Completed in {elapsed/60:.1f} minutes")
            print(f"  Decompressed size: {final_size:.2f} GB")
            print(f"  Compression ratio: {final_size / (gz_file.stat().st_size / 1e9):.1f}x")

            # Remove original
            print(f"  Removing {gz_file.name}...")
            gz_file.unlink()

        except Exception as e:
            print(f"  ERROR: {str(e)[:100]}")

        # Estimate remaining
        if i < len(to_process):
            avg_rate = elapsed / (gz_file.stat().st_size / 1e9)  # seconds per GB
            remaining_gb = sum(Path(f).stat().st_size / 1e9 for f in to_process[i:])
            est_minutes = remaining_gb * avg_rate / 60
            print(f"\n  Estimated time remaining: {est_minutes:.0f} minutes")

    print("\n" + "="*70)
    print("DECOMPRESSION COMPLETE")
    print(f"End time: {datetime.now()}")
    print("="*70)

if __name__ == "__main__":
    decompress_remaining()
