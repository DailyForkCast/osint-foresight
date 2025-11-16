#!/usr/bin/env python3
"""
Simple PatentsView downloader using requests library
May handle DNS differently than curl
"""

import os
import requests
from datetime import datetime

DOWNLOAD_DIR = "F:/USPTO_PATENTSVIEW"
BASE_URL = "https://s3.amazonaws.com/data.patentsview.org/download"

# Updated for disambiguated PatentsView schema (Sept 2025)
FILES = [
    "g_application.tsv.zip",              # Patent application data
    "g_assignee_disambiguated.tsv.zip",   # Disambiguated assignees (CRITICAL)
    "g_location_disambiguated.tsv.zip",   # Disambiguated locations (CRITICAL)
    "g_cpc_current.tsv.zip",              # CPC classifications for strategic tech
    "g_inventor_disambiguated.tsv.zip"    # Disambiguated inventors
]

def download_file(filename):
    """Download single file with requests"""
    url = f"{BASE_URL}/{filename}"
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    print(f"\n{'='*80}")
    print(f"Downloading: {filename}")
    print(f"URL: {url}")
    print(f"{'='*80}")

    if os.path.exists(filepath):
        size_mb = os.path.getsize(filepath) / (1024*1024)
        print(f"WARNING: File exists ({size_mb:.1f} MB) - skipping")
        return True

    try:
        response = requests.get(url, stream=True, timeout=120)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        total_mb = total_size / (1024*1024)

        print(f"Size: {total_mb:.1f} MB")
        print("Downloading...")

        downloaded = 0
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    if downloaded % (50*1024*1024) < 8192:
                        progress_mb = downloaded / (1024*1024)
                        pct = (downloaded / total_size * 100) if total_size > 0 else 0
                        print(f"  {progress_mb:.1f} MB / {total_mb:.1f} MB ({pct:.1f}%)")

        final_mb = os.path.getsize(filepath) / (1024*1024)
        print(f"SUCCESS: Complete - {final_mb:.1f} MB")
        return True

    except Exception as e:
        print(f"ERROR: Failed - {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return False

def main():
    print("="*80)
    print("PATENTSVIEW DOWNLOADER (PYTHON/REQUESTS)")
    print("="*80)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    success = 0
    failed = []

    for i, filename in enumerate(FILES, 1):
        print(f"\n[{i}/{len(FILES)}]")
        if download_file(filename):
            success += 1
        else:
            failed.append(filename)

    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Success: {success}/{len(FILES)}")
    print(f"Failed: {len(failed)}/{len(FILES)}")

    if failed:
        print("\nFailed files:")
        for f in failed:
            print(f"  - {f}")

    print(f"\nEnd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
