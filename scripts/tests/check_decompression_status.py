#!/usr/bin/env python3
"""Check decompression status"""

from pathlib import Path
from datetime import datetime

base = "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/"
files = [
    ("5801", 14.30),  # GB compressed
    ("5836", 13.07),
    ("5847", 15.56),
    ("5848", 16.49),
    ("5862", 4.71)
]

print(f"Decompression Status Check - {datetime.now().strftime('%H:%M:%S')}")
print("=" * 60)

total_compressed = 0
total_decompressed = 0
completed = 0
in_progress = []

for name, compressed_gb in files:
    gz_file = Path(base + name + ".dat.gz")
    dat_file = Path(base + name + ".dat")

    total_compressed += compressed_gb

    if dat_file.exists():
        size = dat_file.stat().st_size / 1e9
        total_decompressed += size
        completed += 1
        status = f"DONE - {size:.2f} GB"

        # Check if .gz still exists
        if gz_file.exists():
            status += " (gz not deleted)"
    elif gz_file.exists():
        status = f"PENDING - {compressed_gb:.2f} GB to process"
    else:
        status = "MISSING"

    print(f"{name}.dat: {status}")

print("=" * 60)
print(f"Completed: {completed}/5 files")
print(f"Total decompressed: {total_decompressed:.2f} GB")
print(f"Remaining: {5-completed} files ({total_compressed - (total_decompressed/3):.2f} GB)")

if completed < 5:
    print(f"\nDecompression in progress... Check again in a few minutes.")
else:
    print(f"\nAll files decompressed!")
    print(f"Total size: {total_decompressed:.2f} GB")
