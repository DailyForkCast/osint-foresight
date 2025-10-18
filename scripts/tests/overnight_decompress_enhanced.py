#!/usr/bin/env python3
"""Enhanced overnight decompression with progress monitoring"""

import gzip
import shutil
import time
import json
from pathlib import Path
from datetime import datetime

def decompress_with_monitoring(file_path, log_file):
    """Decompress with progress tracking"""
    gz_file = Path(file_path)

    if not gz_file.exists():
        log_file.write(f"[{datetime.now()}] File not found: {file_path}\n")
        return False

    output = gz_file.with_suffix('')
    start_time = time.time()

    log_file.write(f"[{datetime.now()}] Starting: {gz_file.name} ({gz_file.stat().st_size / 1e9:.1f} GB)\n")
    log_file.flush()

    try:
        with gzip.open(gz_file, 'rb') as f_in:
            with open(output, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out, length=10*1024*1024)  # 10MB chunks

        elapsed = time.time() - start_time
        output_size = output.stat().st_size / 1e9

        log_file.write(f"[{datetime.now()}] Completed: {gz_file.name} -> {output_size:.1f} GB in {elapsed:.0f}s\n")
        log_file.flush()

        # Delete original to save space
        gz_file.unlink()
        return True

    except Exception as e:
        log_file.write(f"[{datetime.now()}] Error with {gz_file.name}: {e}\n")
        return False

# Main execution
large_files = [
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5801.dat.gz",  # 14.3 GB
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5836.dat.gz",  # 13.1 GB
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5847.dat.gz",  # 15.6 GB
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5848.dat.gz",  # 16.5 GB
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5862.dat.gz"   # 4.7 GB
]

print("="*60)
print("OVERNIGHT DECOMPRESSION STARTED")
print(f"Time: {datetime.now()}")
print(f"Files to process: {len(large_files)}")
print(f"Estimated time: 8-12 hours")
print("="*60)
print()

with open("overnight_progress.log", "w") as log:
    log.write(f"Started at {datetime.now()}\n")
    log.write(f"Processing {len(large_files)} files\n\n")

    success_count = 0
    for file_path in large_files:
        if decompress_with_monitoring(file_path, log):
            success_count += 1

    log.write(f"\n[{datetime.now()}] COMPLETE: {success_count}/{len(large_files)} files decompressed\n")

print(f"\nCOMPLETE: {success_count}/{len(large_files)} files successfully decompressed")
print(f"Check overnight_progress.log for details")
