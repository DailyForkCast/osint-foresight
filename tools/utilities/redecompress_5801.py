#!/usr/bin/env python3
"""
Re-decompress 5801.dat.gz which was truncated at 2.95 GB
Expected output size: ~130 GB based on compression ratios from other files
"""

import gzip
import shutil
from pathlib import Path
import time
from datetime import datetime

def redecompress_5801():
    base_path = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/")
    gz_file = base_path / "5801.dat.gz"
    dat_file = base_path / "5801.dat"
    backup_file = base_path / "5801.dat.truncated"

    print("="*70)
    print("RE-DECOMPRESSING 5801.dat.gz")
    print("="*70)
    print(f"Start time: {datetime.now()}")

    # Check gz file exists
    if not gz_file.exists():
        print(f"ERROR: {gz_file} not found!")
        return

    gz_size = gz_file.stat().st_size / 1e9
    print(f"Compressed size: {gz_size:.2f} GB")
    print(f"Expected decompressed size: ~130 GB (based on 9-13x expansion)")

    # Backup existing truncated file
    if dat_file.exists():
        current_size = dat_file.stat().st_size / 1e9
        print(f"\nCurrent truncated file: {current_size:.2f} GB")
        print(f"Backing up to: {backup_file}")
        dat_file.rename(backup_file)

    # Start decompression
    print(f"\nStarting decompression at {datetime.now().strftime('%H:%M:%S')}")
    print("This will take approximately 20-25 minutes...")
    print("-" * 40)

    start_time = time.time()
    bytes_written = 0
    last_report = 0

    try:
        with gzip.open(gz_file, 'rb') as f_in:
            with open(dat_file, 'wb') as f_out:
                while True:
                    chunk = f_in.read(10*1024*1024)  # 10MB chunks
                    if not chunk:
                        break

                    f_out.write(chunk)
                    bytes_written += len(chunk)

                    # Report progress every 5GB
                    if bytes_written - last_report >= 5*1024*1024*1024:
                        gb_written = bytes_written / 1e9
                        elapsed = time.time() - start_time
                        speed = (bytes_written / 1e9) / (elapsed / 60) if elapsed > 0 else 0
                        print(f"  Progress: {gb_written:.1f} GB decompressed (speed: {speed:.1f} GB/min)...")
                        last_report = bytes_written

    except Exception as e:
        print(f"\nERROR during decompression: {e}")
        return

    # Final stats
    elapsed_time = time.time() - start_time
    final_size = dat_file.stat().st_size / 1e9
    compression_ratio = final_size / gz_size

    print("-" * 40)
    print(f"Completed in {elapsed_time/60:.1f} minutes")
    print(f"Decompressed size: {final_size:.2f} GB")
    print(f"Compression ratio: {compression_ratio:.1f}x")
    print(f"Average speed: {gz_size/(elapsed_time/60):.1f} GB/min")

    # Verify file integrity
    print("\nVerifying file integrity...")
    with open(dat_file, 'rb') as f:
        # Check beginning
        f.seek(0)
        first_bytes = f.read(100)

        # Check end for PostgreSQL marker
        f.seek(max(0, dat_file.stat().st_size - 1000))
        last_bytes = f.read(1000)

        has_end_marker = b'\\.' in last_bytes or last_bytes.strip().endswith(b'\\.')

        print(f"First 50 bytes: {first_bytes[:50]}")
        print(f"Last 50 bytes: {last_bytes[-50:]}")

        if has_end_marker:
            print("[SUCCESS] PostgreSQL end marker found!")
        else:
            print("[WARNING] No PostgreSQL end marker found - file might be incomplete")

    if final_size < 100:
        print("\n[WARNING] File is smaller than expected (~130 GB)")
        print("This might indicate an issue with the decompression")
    else:
        print(f"\n[SUCCESS] File decompressed to expected size range")
        print("You can now proceed with PostgreSQL import")

    print("="*70)
    print(f"End time: {datetime.now()}")

if __name__ == "__main__":
    redecompress_5801()
