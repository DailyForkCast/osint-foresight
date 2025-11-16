#!/usr/bin/env python3
"""
Download PatentsView Bulk Data for Chinese Patent Analysis (2021-2025 Extension)
Downloads key TSV files for patent, assignee, inventor, and CPC data
"""

import os
import requests
from datetime import datetime
import hashlib

# Base URLs for PatentsView data
PATENTSVIEW_BASE = "https://s3.amazonaws.com/data.patentsview.org/download"

# Download directory
DOWNLOAD_DIR = "F:/USPTO_PATENTSVIEW"

# Files to download (name, URL suffix, description)
FILES_TO_DOWNLOAD = [
    ("patent.tsv.zip", "patent.tsv.zip", "Core patent data (patent_id, date, title, abstract)"),
    ("assignee.tsv.zip", "assignee.tsv.zip", "Assignee names and IDs"),
    ("location_assignee.tsv.zip", "location_assignee.tsv.zip", "Assignee locations (CRITICAL for Chinese detection)"),
    ("patent_assignee.tsv.zip", "patent_assignee.tsv.zip", "Patent-to-assignee linkage"),
    ("inventor.tsv.zip", "inventor.tsv.zip", "Inventor information"),
    ("location_inventor.tsv.zip", "location_inventor.tsv.zip", "Inventor locations"),
    ("patent_inventor.tsv.zip", "patent_inventor.tsv.zip", "Patent-to-inventor linkage"),
    ("cpc_current.tsv.zip", "cpc_current.tsv.zip", "CPC classifications (for strategic tech)"),
    ("application.tsv.zip", "application.tsv.zip", "Application data"),
]

def get_file_size_mb(filepath):
    """Get file size in MB"""
    if os.path.exists(filepath):
        return os.path.getsize(filepath) / (1024 * 1024)
    return 0

def download_file(url, filepath, description):
    """Download file with progress indication"""
    print(f"\n{'='*80}")
    print(f"Downloading: {description}")
    print(f"URL: {url}")
    print(f"Destination: {filepath}")
    print(f"{'='*80}")

    # Check if file already exists
    if os.path.exists(filepath):
        existing_size = get_file_size_mb(filepath)
        print(f"⚠️  File already exists ({existing_size:.1f} MB)")
        response = input("Download again? (y/n): ")
        if response.lower() != 'y':
            print("Skipping download")
            return True

    try:
        # Stream download with progress
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        total_mb = total_size / (1024 * 1024)

        print(f"Total size: {total_mb:.1f} MB")
        print(f"Downloading...")

        downloaded = 0
        chunk_size = 8192  # 8KB chunks

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    # Progress update every 50 MB
                    if downloaded % (50 * 1024 * 1024) < chunk_size:
                        progress_mb = downloaded / (1024 * 1024)
                        if total_size > 0:
                            pct = (downloaded / total_size) * 100
                            print(f"  Progress: {progress_mb:.1f} MB / {total_mb:.1f} MB ({pct:.1f}%)")
                        else:
                            print(f"  Progress: {progress_mb:.1f} MB")

        final_size = get_file_size_mb(filepath)
        print(f"✅ Download complete: {final_size:.1f} MB")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Download failed: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return False
    except KeyboardInterrupt:
        print("\n⚠️  Download interrupted by user")
        if os.path.exists(filepath):
            os.remove(filepath)
        return False

def main():
    print("="*80)
    print("PATENTSVIEW BULK DATA DOWNLOADER")
    print("="*80)
    print(f"Target directory: {DOWNLOAD_DIR}")
    print(f"Files to download: {len(FILES_TO_DOWNLOAD)}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Create download directory
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Summary
    print(f"\n{'='*80}")
    print("FILES TO DOWNLOAD:")
    print(f"{'='*80}")
    for i, (filename, url_suffix, description) in enumerate(FILES_TO_DOWNLOAD, 1):
        print(f"{i:2d}. {filename:30s} - {description}")

    print(f"\n{'='*80}")
    response = input("\nProceed with download? (y/n): ")
    if response.lower() != 'y':
        print("Download cancelled")
        return

    # Download files
    success_count = 0
    failed_files = []

    for i, (filename, url_suffix, description) in enumerate(FILES_TO_DOWNLOAD, 1):
        print(f"\n[{i}/{len(FILES_TO_DOWNLOAD)}]")

        url = f"{PATENTSVIEW_BASE}/{url_suffix}"
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        if download_file(url, filepath, description):
            success_count += 1
        else:
            failed_files.append(filename)

    # Final summary
    print(f"\n{'='*80}")
    print("DOWNLOAD SUMMARY")
    print(f"{'='*80}")
    print(f"Successful: {success_count}/{len(FILES_TO_DOWNLOAD)}")
    print(f"Failed: {len(failed_files)}/{len(FILES_TO_DOWNLOAD)}")

    if failed_files:
        print(f"\nFailed files:")
        for f in failed_files:
            print(f"  - {f}")

    # Calculate total size
    total_size = 0
    for filename, _, _ in FILES_TO_DOWNLOAD:
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        total_size += get_file_size_mb(filepath)

    print(f"\nTotal downloaded: {total_size:.1f} MB ({total_size/1024:.2f} GB)")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\n{'='*80}")
    print("NEXT STEPS:")
    print(f"{'='*80}")
    print("1. Extract the ZIP files:")
    print(f"   cd {DOWNLOAD_DIR}")
    print("   unzip '*.zip'")
    print("\n2. Run the PatentsView processor:")
    print("   python scripts/process_patentsview_chinese.py")

if __name__ == '__main__':
    main()
