#!/usr/bin/env python3
"""
Quick USAspending Download Monitor
Checks download progress every 30 seconds
"""

import os
import time
from datetime import datetime

def check_download():
    """Check download file size"""
    file_path = "F:/OSINT_Data/USAspending/usaspending-db_20250906.zip"

    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        size_gb = size_bytes / (1024**3)

        progress = (size_gb / 174) * 100

        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"Downloaded: {size_gb:.2f} GB / 174 GB ({progress:.1f}%)")

        return size_gb
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] File not found yet...")
        return 0

def main():
    print("=" * 60)
    print("USAspending Download Monitor")
    print("Target: 174 GB")
    print("=" * 60)

    last_size = 0

    while True:
        current_size = check_download()

        # Calculate speed
        speed_gb = current_size - last_size
        if speed_gb > 0:
            eta_hours = (174 - current_size) / (speed_gb * 2)  # Speed per 30 sec * 2 = per minute * 60 = per hour
            print(f"  Speed: {speed_gb*2:.2f} GB/min | ETA: {eta_hours:.1f} hours")

        if current_size >= 174:
            print("\n✅ Download complete!")
            break

        last_size = current_size
        time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
