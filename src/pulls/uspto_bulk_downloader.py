#!/usr/bin/env python3
"""USPTO Bulk Data Downloader

Downloads patent and trademark data from USPTO bulk data resources.
Uses the official USPTO data distribution endpoints.
"""

import os
import json
import time
import requests
import zipfile
import gzip
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from tqdm import tqdm

class USPTOBulkDownloader:
    """Downloads USPTO bulk data files"""

    def __init__(self, output_dir: str = "F:/OSINT_Data/USPTO"):
        """Initialize USPTO bulk downloader

        Args:
            output_dir: Directory to save downloaded data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # USPTO bulk data URLs
        self.bulk_urls = {
            "patents": {
                "grant_full_text": "https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/",
                "application_full_text": "https://bulkdata.uspto.gov/data/patent/application/redbook/fulltext/",
                "assignment": "https://bulkdata.uspto.gov/data/patent/assignment/",
                "classification": "https://bulkdata.uspto.gov/data/patent/classification/cpc/",
                "pair": "https://bulkdata.uspto.gov/data/patent/pair/"
            },
            "trademarks": {
                "daily": "https://bulkdata.uspto.gov/data/trademark/dailyxml/",
                "assignment": "https://bulkdata.uspto.gov/data/trademark/assignment/"
            }
        }

        # Google Patents Public Datasets (BigQuery export)
        self.google_patents_url = "https://console.cloud.google.com/marketplace/product/google_patents_public_datasets"

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Research/1.0 USPTO-Bulk-Downloader'
        })

    def get_available_files(self, data_type: str, category: str) -> List[str]:
        """Get list of available files for download

        Args:
            data_type: 'patents' or 'trademarks'
            category: Specific category within data type

        Returns:
            List of available file URLs
        """
        base_url = self.bulk_urls.get(data_type, {}).get(category)
        if not base_url:
            print(f"Unknown data type/category: {data_type}/{category}")
            return []

        try:
            response = self.session.get(base_url, timeout=30)
            if response.status_code == 200:
                # Parse HTML to find download links
                # USPTO bulk data pages have links to zip/xml files
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')

                files = []
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    # Filter for data files (zip, xml, txt)
                    if any(href.endswith(ext) for ext in ['.zip', '.xml', '.txt', '.gz']):
                        if not href.startswith('http'):
                            href = base_url + href
                        files.append(href)

                print(f"Found {len(files)} files in {data_type}/{category}")
                return files
            else:
                print(f"Failed to access {base_url}: {response.status_code}")
                return []

        except Exception as e:
            print(f"Error getting file list: {e}")
            return []

    def download_file(self, url: str, output_path: Optional[Path] = None) -> bool:
        """Download a single file with progress bar

        Args:
            url: URL to download
            output_path: Optional specific output path

        Returns:
            True if successful
        """
        if output_path is None:
            filename = url.split('/')[-1]
            output_path = self.output_dir / filename

        # Skip if already downloaded
        if output_path.exists():
            print(f"Already downloaded: {output_path.name}")
            return True

        print(f"Downloading: {url}")
        print(f"  To: {output_path}")

        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(output_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            print(f"Downloaded successfully: {output_path.name}")
            return True

        except Exception as e:
            print(f"Download failed: {e}")
            if output_path.exists():
                output_path.unlink()  # Remove partial download
            return False

    def download_recent_patents(self, weeks: int = 4) -> List[Path]:
        """Download recent patent grant full text files

        Args:
            weeks: Number of weeks of data to download

        Returns:
            List of downloaded file paths
        """
        print(f"Downloading patent grants from last {weeks} weeks...")

        # Patent grants are typically released weekly on Tuesdays
        # Files are named like: ipg240102.zip (year, month, day)

        downloaded = []
        base_url = self.bulk_urls["patents"]["grant_full_text"]
        year = datetime.now().year

        # Try to download recent files
        for week in range(weeks):
            date = datetime.now() - timedelta(weeks=week)

            # Format: ipgYYMMDD.zip
            file_pattern = f"ipg{date.strftime('%y%m%d')}.zip"
            url = f"{base_url}{year}/{file_pattern}"

            output_path = self.output_dir / "patents" / "grants" / file_pattern
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if self.download_file(url, output_path):
                downloaded.append(output_path)

        print(f"Downloaded {len(downloaded)} patent grant files")
        return downloaded

    def download_patent_assignments(self, year: int = 2024) -> List[Path]:
        """Download patent assignment data

        Args:
            year: Year to download

        Returns:
            List of downloaded files
        """
        print(f"Downloading patent assignments for {year}...")

        downloaded = []
        base_url = self.bulk_urls["patents"]["assignment"]

        # Assignment files are organized by year
        # Format: ad20240101-20240107.xml
        url = f"{base_url}{year}/"

        files = self.get_available_files("patents", "assignment")

        # Filter for the specified year
        year_files = [f for f in files if str(year) in f]

        for file_url in year_files[:5]:  # Limit to 5 files for testing
            filename = file_url.split('/')[-1]
            output_path = self.output_dir / "patents" / "assignments" / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if self.download_file(file_url, output_path):
                downloaded.append(output_path)

        print(f"Downloaded {len(downloaded)} assignment files")
        return downloaded

    def extract_files(self, file_paths: List[Path]) -> List[Path]:
        """Extract downloaded compressed files

        Args:
            file_paths: List of compressed file paths

        Returns:
            List of extracted file paths
        """
        extracted = []

        for file_path in file_paths:
            if not file_path.exists():
                continue

            output_dir = file_path.parent / file_path.stem

            if file_path.suffix == '.zip':
                print(f"Extracting ZIP: {file_path.name}")
                output_dir.mkdir(parents=True, exist_ok=True)

                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(output_dir)
                    extracted.extend([output_dir / f for f in zip_ref.namelist()])

            elif file_path.suffix == '.gz':
                print(f"Extracting GZ: {file_path.name}")
                output_file = file_path.parent / file_path.stem

                with gzip.open(file_path, 'rb') as gz_file:
                    with open(output_file, 'wb') as out_file:
                        out_file.write(gz_file.read())
                extracted.append(output_file)

        print(f"Extracted {len(extracted)} files")
        return extracted

    def download_sample_data(self) -> Dict[str, List[Path]]:
        """Download sample USPTO data for testing

        Returns:
            Dictionary of downloaded files by category
        """
        print("="*70)
        print("Downloading Sample USPTO Data")
        print("="*70)

        results = {
            "patent_grants": [],
            "patent_assignments": [],
            "extracted": []
        }

        # Download recent patent grants (1 week)
        print("\n1. Patent Grants:")
        print("-"*40)
        results["patent_grants"] = self.download_recent_patents(weeks=1)

        # Download patent assignments
        print("\n2. Patent Assignments:")
        print("-"*40)
        results["patent_assignments"] = self.download_patent_assignments(year=2024)

        # Extract compressed files
        print("\n3. Extracting Files:")
        print("-"*40)
        all_files = results["patent_grants"] + results["patent_assignments"]
        results["extracted"] = self.extract_files(all_files)

        return results

    def get_download_status(self) -> Dict[str, Any]:
        """Get status of downloaded USPTO data

        Returns:
            Status dictionary
        """
        status = {
            "output_directory": str(self.output_dir),
            "categories": {},
            "total_size_mb": 0,
            "file_count": 0
        }

        for category in ["patents/grants", "patents/assignments", "trademarks"]:
            category_path = self.output_dir / category
            if category_path.exists():
                files = list(category_path.glob("**/*"))
                file_count = len([f for f in files if f.is_file()])
                total_size = sum(f.stat().st_size for f in files if f.is_file())

                status["categories"][category] = {
                    "files": file_count,
                    "size_mb": total_size / (1024 * 1024)
                }
                status["file_count"] += file_count
                status["total_size_mb"] += total_size / (1024 * 1024)

        return status


def main():
    """Test USPTO bulk data downloader"""
    print("="*70)
    print("USPTO Bulk Data Downloader")
    print("="*70)

    # Check if BeautifulSoup is available
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("\n[!] BeautifulSoup4 not installed. Installing...")
        os.system("pip install beautifulsoup4")
        print("Please restart the script after installation.")
        return

    # Initialize downloader
    downloader = USPTOBulkDownloader()

    print(f"\nOutput directory: {downloader.output_dir}")
    print("\nAvailable data sources:")
    print("-"*40)
    print("Patents:")
    for category, url in downloader.bulk_urls["patents"].items():
        print(f"  - {category}: {url}")
    print("\nTrademarks:")
    for category, url in downloader.bulk_urls["trademarks"].items():
        print(f"  - {category}: {url}")

    # Download sample data
    print("\n" + "="*70)
    print("Starting sample download...")
    print("="*70)

    results = downloader.download_sample_data()

    # Show results
    print("\n" + "="*70)
    print("Download Summary")
    print("="*70)

    for category, files in results.items():
        if files:
            print(f"\n{category}:")
            for file_path in files[:5]:  # Show first 5
                print(f"  - {file_path.name}")

    # Get status
    status = downloader.get_download_status()
    print("\n" + "="*70)
    print("Storage Status")
    print("="*70)
    print(f"Total files: {status['file_count']}")
    print(f"Total size: {status['total_size_mb']:.2f} MB")

    for category, info in status["categories"].items():
        print(f"\n{category}:")
        print(f"  Files: {info['files']}")
        print(f"  Size: {info['size_mb']:.2f} MB")

    print("\n" + "="*70)
    print("USPTO bulk data downloader ready!")
    print("\nNote: Full downloads can be very large (GB+)")
    print("Use download_recent_patents() for recent data only")
    print("="*70)


if __name__ == "__main__":
    main()
