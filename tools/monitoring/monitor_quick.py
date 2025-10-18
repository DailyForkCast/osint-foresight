#!/usr/bin/env python3
"""Quick monitor for both processes"""
import time
from pathlib import Path
from datetime import datetime

for i in range(10):
    f = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5801.dat")
    if f.exists():
        size = f.stat().st_size / 1e9
        pct = (size / 130) * 100
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 5801.dat: {size:.2f} GB ({pct:.1f}%)")

        # Check for end marker
        with open(f, 'rb') as file:
            file.seek(max(0, f.stat().st_size - 100))
            if b'\\.' in file.read(100):
                print("COMPLETE - PostgreSQL end marker found!")
                break
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] File not found")

    if i < 9:
        time.sleep(30)
