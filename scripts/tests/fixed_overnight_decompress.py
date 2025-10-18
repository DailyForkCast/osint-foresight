#!/usr/bin/env python3
"""
Fixed Overnight Decompression - Handles file deletion properly
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
    print("FIXED OVERNIGHT DECOMPRESSION")
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
            print(f"[DONE] {gz_file.name} - Completed and .gz removed")
            if dat_file.exists():
                completed.append(gz_file.name)

    print(f"\nCompleted: {len(completed)}")
    print(f"To process: {len(to_process)}")

    if not to_process:
        print("\nAll files already decompressed!")

        # Show final sizes
        print("\nFinal decompressed sizes:")
        total = 0
        for file_path in files:
            dat_file = Path(file_path).with_suffix('')
            if dat_file.exists():
                size = dat_file.stat().st_size / 1e9
                total += size
                print(f"  {dat_file.name}: {size:.2f} GB")
        print(f"\nTotal decompressed: {total:.2f} GB")
        return

    total_gb = sum(Path(f).stat().st_size / 1e9 for f in to_process)
    print(f"Total to decompress: {total_gb:.2f} GB")
    print(f"Estimated time: {total_gb * 1.5:.0f} minutes (based on 5836.dat rate)")
    print("\n" + "-"*70)

    # Process remaining files
    for i, file_path in enumerate(to_process, 1):
        gz_file = Path(file_path)
        dat_file = gz_file.with_suffix('')

        print(f"\n[File {i}/{len(to_process)}] {gz_file.name}")
        gz_size = gz_file.stat().st_size / 1e9
        print(f"  Compressed size: {gz_size:.2f} GB")
        print(f"  Starting at {datetime.now().strftime('%H:%M:%S')}")

        start = time.time()

        try:
            # Decompress with progress
            bytes_processed = 0
            with gzip.open(gz_file, 'rb') as f_in:
                with open(dat_file, 'wb') as f_out:
                    while True:
                        chunk = f_in.read(10*1024*1024)  # 10MB chunks
                        if not chunk:
                            break
                        f_out.write(chunk)
                        bytes_processed += len(chunk)

                        # Progress every 5GB
                        if bytes_processed % (5*1024*1024*1024) == 0:
                            print(f"    Progress: {bytes_processed/1e9:.1f} GB decompressed...")

            elapsed = time.time() - start
            final_size = dat_file.stat().st_size / 1e9

            print(f"  Completed in {elapsed/60:.1f} minutes")
            print(f"  Decompressed size: {final_size:.2f} GB")
            print(f"  Compression ratio: {final_size / gz_size:.1f}x")
            print(f"  Speed: {gz_size / (elapsed/60):.1f} GB/min")

            # Remove original AFTER we're done with stats
            print(f"  Removing {gz_file.name}...")
            gz_file.unlink()

        except Exception as e:
            print(f"  ERROR: {str(e)[:100]}")

        # Estimate remaining (using safe calculation)
        if i < len(to_process):
            remaining_files = len(to_process) - i
            avg_minutes = elapsed / 60
            est_minutes = remaining_files * avg_minutes
            print(f"\n  Estimated time remaining: {est_minutes:.0f} minutes for {remaining_files} files")

    print("\n" + "="*70)
    print("DECOMPRESSION COMPLETE")
    print(f"End time: {datetime.now()}")

    # Final summary
    print("\nFinal decompressed sizes:")
    total = 0
    for file_path in files:
        dat_file = Path(file_path).with_suffix('')
        if dat_file.exists():
            size = dat_file.stat().st_size / 1e9
            total += size
            print(f"  {dat_file.name}: {size:.2f} GB")
    print(f"\nTotal decompressed: {total:.2f} GB")
    print("="*70)

if __name__ == "__main__":
    decompress_remaining()
