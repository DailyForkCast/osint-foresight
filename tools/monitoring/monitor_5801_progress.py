#!/usr/bin/env python3
"""
Monitor the progress of 5801.dat re-decompression
"""

import time
from pathlib import Path
from datetime import datetime

def monitor_progress():
    base_path = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/")
    dat_file = base_path / "5801.dat"
    gz_file = base_path / "5801.dat.gz"

    if not gz_file.exists():
        print("ERROR: 5801.dat.gz not found!")
        return

    gz_size = gz_file.stat().st_size / 1e9
    print(f"Monitoring re-decompression of 5801.dat.gz ({gz_size:.2f} GB)")
    print(f"Expected output: ~130 GB based on 9-13x compression ratio")
    print("-" * 60)

    start_size = dat_file.stat().st_size if dat_file.exists() else 0
    start_time = time.time()
    last_size = start_size

    print(f"Time     | Size (GB) | Speed (GB/min) | Est. Remaining | Progress")
    print("-" * 60)

    while True:
        if dat_file.exists():
            current_size = dat_file.stat().st_size
            size_gb = current_size / 1e9
            elapsed = time.time() - start_time

            if elapsed > 0 and current_size > start_size:
                speed = (current_size - start_size) / 1e9 / (elapsed / 60)

                # Estimate based on expected 130 GB
                expected_size = 130 * 1e9
                remaining_bytes = max(0, expected_size - current_size)
                remaining_time = (remaining_bytes / 1e9) / speed if speed > 0 else 0

                progress_pct = (size_gb / 130) * 100

                # Check if file is still growing
                if current_size > last_size:
                    status = "ACTIVE"
                else:
                    status = "STALLED"

                print(f"{datetime.now().strftime('%H:%M:%S')} | {size_gb:9.2f} | {speed:14.2f} | {remaining_time:5.1f} min      | {progress_pct:5.1f}% {status}")
                last_size = current_size

                # Check for completion (no growth for 10 seconds)
                if current_size == last_size:
                    time.sleep(10)
                    if dat_file.stat().st_size == current_size:
                        print("\n" + "=" * 60)
                        print(f"Decompression appears complete at {size_gb:.2f} GB")

                        # Check for PostgreSQL end marker
                        with open(dat_file, 'rb') as f:
                            f.seek(max(0, current_size - 1000))
                            last_bytes = f.read(1000)
                            if b'\\.' in last_bytes or last_bytes.strip().endswith(b'\\.'):
                                print("[SUCCESS] PostgreSQL end marker found!")
                            else:
                                print("[WARNING] No PostgreSQL end marker found")
                        break
            else:
                print(f"{datetime.now().strftime('%H:%M:%S')} | {size_gb:9.2f} | Starting...    | Calculating... | {0:5.1f}%")
        else:
            print(f"{datetime.now().strftime('%H:%M:%S')} | Waiting for file to be created...")

        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    monitor_progress()
