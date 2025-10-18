#!/usr/bin/env python3
"""Quick test to verify decompression setup"""

from pathlib import Path

files = [
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5801.dat.gz",
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5836.dat.gz",
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5847.dat.gz",
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5848.dat.gz",
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5862.dat.gz"
]

print("Checking files for decompression...")
print("=" * 50)

total_size = 0
for file_path in files:
    p = Path(file_path)
    if p.exists():
        size = p.stat().st_size / 1e9
        total_size += size
        print(f"[OK] {p.name}: {size:.2f} GB")

        # Check if already decompressed
        decompressed = p.with_suffix('')
        if decompressed.exists():
            print(f"     -> Already decompressed: {decompressed.name}")
    else:
        print(f"[!!] {p.name}: NOT FOUND")

print("=" * 50)
print(f"Total to decompress: {total_size:.2f} GB")
print(f"Estimated time: {total_size * 10:.0f} minutes")
print("\nReady to start decompression!")
