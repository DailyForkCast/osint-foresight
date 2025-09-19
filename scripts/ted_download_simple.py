#!/usr/bin/env python3
"""
Simple TED downloader - no Unicode issues
"""

import requests
import time
from pathlib import Path
import sys

def download_month(year, month):
    """Download a single month of TED data"""

    # Setup paths
    base_path = Path("F:/TED_Data/monthly")
    year_path = base_path / str(year)
    year_path.mkdir(parents=True, exist_ok=True)

    # Build URL and filename
    url = f"https://ted.europa.eu/packages/monthly/{year}-{month}"
    filename = f"TED_monthly_{year}_{month:02d}.tar.gz"
    local_file = year_path / filename

    # Check if already exists
    if local_file.exists() and local_file.stat().st_size > 1000000:
        size_mb = local_file.stat().st_size / 1024 / 1024
        print(f"[SKIP] Already downloaded: {year}-{month:02d} ({size_mb:.1f}MB)")
        return True

    print(f"\n[DOWNLOADING] {year}-{month:02d}")
    print(f"  URL: {url}")

    try:
        # Download with timeout
        response = requests.get(url, stream=True, timeout=60)

        if response.status_code == 404:
            print(f"[ERROR] Not found: {year}-{month:02d}")
            return False

        response.raise_for_status()

        # Get total size
        total_size = int(response.headers.get('content-length', 0))
        total_mb = total_size / 1024 / 1024
        print(f"  Size: {total_mb:.1f}MB")

        # Download with simple progress
        downloaded = 0
        last_print = 0

        with open(local_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    # Print progress every 10MB
                    if downloaded - last_print > 10*1024*1024:
                        mb_down = downloaded / 1024 / 1024
                        percent = (downloaded / total_size * 100) if total_size > 0 else 0
                        print(f"  Progress: {percent:.0f}% ({mb_down:.0f}MB / {total_mb:.0f}MB)")
                        last_print = downloaded

        final_size_mb = local_file.stat().st_size / 1024 / 1024
        print(f"[SUCCESS] Complete: {year}-{month:02d} ({final_size_mb:.1f}MB)")
        return True

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Stopped by user")
        if local_file.exists():
            local_file.unlink()
        sys.exit(0)

    except Exception as e:
        print(f"[ERROR] {e}")
        if local_file.exists():
            local_file.unlink()
        return False

def main():
    """Main download loop"""
    print("="*60)
    print("TED Historical Data Download (2011-2014)")
    print("="*60)

    # Check what years to download
    start_year = 2011
    end_year = 2014

    if len(sys.argv) > 1:
        # Allow specifying single year
        try:
            year = int(sys.argv[1])
            if 2011 <= year <= 2014:
                start_year = year
                end_year = year
                print(f"Downloading only year {year}")
        except:
            pass

    # Track statistics
    total = 0
    success = 0
    failed = 0

    # Download specified years
    for year in range(start_year, end_year + 1):
        print(f"\n[YEAR {year}]")
        print("-"*40)

        for month in range(1, 13):
            total += 1

            if download_month(year, month):
                success += 1
            else:
                failed += 1

            # Be nice to server
            time.sleep(3)

            # Show running total
            print(f"Status: {success}/{total} downloaded, {failed} failed")

    # Final summary
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE")
    print("="*60)
    print(f"Successful: {success}/{total}")
    print(f"Failed: {failed}")

    # Calculate disk usage
    base_path = Path("F:/TED_Data/monthly")
    total_size = 0
    file_count = 0
    for year in range(2011, 2015):
        year_path = base_path / str(year)
        if year_path.exists():
            for file in year_path.glob("*.tar.gz"):
                total_size += file.stat().st_size
                file_count += 1

    print(f"Total files: {file_count}")
    print(f"Total disk usage: {total_size/1024/1024/1024:.1f}GB")
    print(f"Location: {base_path}")

if __name__ == "__main__":
    main()
