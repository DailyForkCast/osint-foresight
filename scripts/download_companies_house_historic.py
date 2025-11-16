#!/usr/bin/env python3
"""
Companies House Historic Accounts Data Downloader
Downloads all historic monthly accounts data (2008-2024)
Total: 144 files (~200GB estimated)
"""

import urllib.request
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Target directory
DOWNLOAD_DIR = Path("F:/OSINT_DATA/CompaniesHouse_UK/raw/historic_accounts")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Log file
LOG_FILE = DOWNLOAD_DIR / "download_log.txt"

def log(message):
    """Log to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")

def download_file(url, dest_path):
    """Download file with progress reporting"""
    try:
        # Check if file already exists
        if dest_path.exists():
            file_size = dest_path.stat().st_size
            log(f"  ✓ Already downloaded ({file_size:,} bytes): {dest_path.name}")
            return True

        log(f"  Downloading: {url}")

        # Download with timeout
        start_time = time.time()
        urllib.request.urlretrieve(url, dest_path)
        elapsed = time.time() - start_time

        file_size = dest_path.stat().st_size
        log(f"  ✓ Downloaded ({file_size:,} bytes, {elapsed:.1f}s): {dest_path.name}")
        return True

    except Exception as e:
        log(f"  ✗ ERROR: {e}")
        # Remove partial download
        if dest_path.exists():
            dest_path.unlink()
        return False

def main():
    """Download all historic accounts files"""

    log("=" * 80)
    log("COMPANIES HOUSE HISTORIC ACCOUNTS DATA DOWNLOAD")
    log("=" * 80)
    log(f"Target directory: {DOWNLOAD_DIR}")
    log(f"Expected files: 144 (2008-2024, 12 per year)")
    log("")

    # Generate all URLs
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    years = range(2008, 2025)  # 2008-2024

    base_url = "https://resources.companieshouse.gov.uk/archive"

    total_files = 0
    successful = 0
    failed = 0
    skipped = 0

    for year in years:
        log(f"\n{'=' * 80}")
        log(f"YEAR: {year}")
        log(f"{'=' * 80}")

        for month in months:
            total_files += 1

            filename = f"Accounts_Monthly_Data-{month}{year}.zip"
            url = f"{base_url}/{filename}"
            dest_path = DOWNLOAD_DIR / filename

            log(f"\n[{total_files}/144] {filename}")

            if dest_path.exists():
                file_size = dest_path.stat().st_size
                log(f"  ↷ SKIP: Already exists ({file_size:,} bytes)")
                skipped += 1
                successful += 1  # Count as successful
                continue

            success = download_file(url, dest_path)

            if success:
                successful += 1
            else:
                failed += 1

            # Brief pause between downloads (be nice to servers)
            time.sleep(2)

    # Final summary
    log("\n" + "=" * 80)
    log("DOWNLOAD SUMMARY")
    log("=" * 80)
    log(f"Total files: {total_files}")
    log(f"Successful: {successful}")
    log(f"Failed: {failed}")
    log(f"Skipped (already downloaded): {skipped}")
    log(f"Success rate: {(successful/total_files*100):.1f}%")

    # Calculate total size
    total_size = sum(f.stat().st_size for f in DOWNLOAD_DIR.glob("*.zip"))
    log(f"Total downloaded: {total_size:,} bytes ({total_size/1024/1024/1024:.2f} GB)")

    log("\n✅ DOWNLOAD COMPLETE")
    log(f"Files stored in: {DOWNLOAD_DIR}")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("\n\n⚠️  INTERRUPTED BY USER")
        sys.exit(130)
    except Exception as e:
        log(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
