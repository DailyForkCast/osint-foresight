#!/usr/bin/env python3
"""Overnight decompression of large files"""

import gzip
import shutil
from pathlib import Path
from datetime import datetime

large_files = [
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5801.dat.gz",
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5836.dat.gz",
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5847.dat.gz",
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5848.dat.gz",
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5862.dat.gz"
]

print(f"Starting decompression at {datetime.now()}")

for file_path in large_files:
    gz_file = Path(file_path)
    if gz_file.exists():
        output = gz_file.with_suffix('')
        print(f"Decompressing {gz_file.name} ({gz_file.stat().st_size / 1e9:.1f} GB)...")

        with gzip.open(gz_file, 'rb') as f_in:
            with open(output, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out, length=10*1024*1024)  # 10MB chunks

        print(f"  Done! Output: {output.stat().st_size / 1e9:.1f} GB")
        gz_file.unlink()  # Remove original to save space

print(f"Completed at {datetime.now()}")
