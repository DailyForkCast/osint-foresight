#!/usr/bin/env python3
"""
TED Europa Historical Data Downloader V2
Downloads TED procurement data from 2006-2014 using data.europa.eu APIs

Alternative approach using HTTP downloads instead of FTP
"""

import os
import sys
import time
import requests
from pathlib import Path
from datetime import datetime
import json
import logging
import zipfile
import gzip
import shutil
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ted_historical_download_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TEDHistoricalDownloaderV2:
    def __init__(self, base_path: str = "F:/TED_Data"):
        """Initialize TED historical data downloader"""
        self.base_path = Path(base_path)
        self.historical_path = self.base_path / "historical"
        self.csv_path = self.historical_path / "csv"
        self.xml_path = self.historical_path / "xml"

        # Create directories
        self.csv_path.mkdir(parents=True, exist_ok=True)
        self.xml_path.mkdir(parents=True, exist_ok=True)

        # Known download URLs based on search results and data.europa.eu
        self.csv_urls = {
            # TED CSV data from data.europa.eu
            "2006-2021": "https://data.europa.eu/api/hub/store/data/ted-csv.zip",
            "contract-notices": "https://data.europa.eu/api/hub/store/data/ted-contract-notices.csv",
            "contract-awards": "https://data.europa.eu/api/hub/store/data/ted-contract-awards.csv",
        }

        # Alternative XML sources from TED open data
        self.xml_monthly_pattern = "https://ted.europa.eu/packages/monthly/{year:04d}/{month:02d}/TED_monthly_{year}_{month:02d}.tar.gz"

        # Track downloads
        self.download_log = self.historical_path / "download_log.json"
        self.completed_downloads = self.load_download_log()

    def load_download_log(self) -> Dict:
        """Load download history"""
        if self.download_log.exists():
            with open(self.download_log, 'r') as f:
                return json.load(f)
        return {"csv": {}, "xml": {}, "attempts": []}

    def save_download_log(self):
        """Save download history"""
        with open(self.download_log, 'w') as f:
            json.dump(self.completed_downloads, f, indent=2)

    def download_file(self, url: str, local_path: Path, description: str = "") -> bool:
        """Generic file downloader with progress tracking"""
        try:
            # Skip if already downloaded
            if local_path.exists() and local_path.stat().st_size > 1000:
                logger.info(f"Already downloaded: {local_path.name}")
                return True

            logger.info(f"Downloading: {description or local_path.name}")
            logger.info(f"URL: {url}")

            response = requests.get(url, stream=True, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            if response.status_code == 404:
                logger.warning(f"Not found (404): {url}")
                return False

            response.raise_for_status()

            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rProgress: {percent:.1f}% ({downloaded/1024/1024:.1f}MB)", end='')

            print()  # New line after progress
            size_mb = local_path.stat().st_size / 1024 / 1024
            logger.info(f"Downloaded: {local_path.name} ({size_mb:.1f}MB)")
            return True

        except requests.exceptions.Timeout:
            logger.error(f"Timeout downloading: {url}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading {url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        # Clean up partial download
        if local_path.exists():
            local_path.unlink()
        return False

    def download_bulk_csv(self) -> bool:
        """Download bulk CSV data covering 2006-2021"""
        logger.info("\n" + "="*60)
        logger.info("Downloading TED CSV Data (2006-2021)")
        logger.info("="*60)

        # Main CSV dataset
        csv_file = self.csv_path / "ted-csv-2006-2021.zip"
        url = self.csv_urls["2006-2021"]

        if self.download_file(url, csv_file, "TED CSV 2006-2021"):
            # Extract if it's a zip
            if csv_file.suffix == '.zip':
                logger.info(f"Extracting {csv_file.name}...")
                extract_path = self.csv_path / "extracted"
                extract_path.mkdir(exist_ok=True)

                with zipfile.ZipFile(csv_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                logger.info(f"Extracted to {extract_path}")

            self.completed_downloads["csv"]["2006-2021"] = True
            self.save_download_log()
            return True

        return False

    def try_monthly_xml_http(self, year: int, month: int) -> bool:
        """Try to download monthly XML via HTTP"""
        month_str = f"{month:02d}"
        filename = f"TED_monthly_{year}_{month_str}.tar.gz"

        year_path = self.xml_path / str(year)
        year_path.mkdir(exist_ok=True)
        local_file = year_path / filename

        # Try different URL patterns
        url_patterns = [
            f"https://ted.europa.eu/packages/monthly/{year:04d}/{month_str}/{filename}",
            f"https://data.europa.eu/api/hub/store/data/ted-monthly-{year}-{month_str}.tar.gz",
            f"https://ted.europa.eu/archives/monthly/{year}/{month_str}/{filename}",
        ]

        for url in url_patterns:
            if self.download_file(url, local_file, f"{year}-{month_str} XML"):
                # Record success
                if str(year) not in self.completed_downloads["xml"]:
                    self.completed_downloads["xml"][str(year)] = []
                self.completed_downloads["xml"][str(year)].append(month)
                self.save_download_log()
                return True

        return False

    def search_europa_data_portal(self, year: int) -> List[str]:
        """Search data.europa.eu for TED data for specific year"""
        logger.info(f"Searching data.europa.eu for {year} TED data...")

        search_url = "https://data.europa.eu/api/hub/search/datasets"
        params = {
            "q": f"TED {year}",
            "filter": "publisher.name:Publications Office",
            "limit": 10
        }

        try:
            response = requests.get(search_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                urls = []
                if "result" in data:
                    for item in data["result"]:
                        if "distributions" in item:
                            for dist in item["distributions"]:
                                if "access_url" in dist:
                                    urls.append(dist["access_url"])
                return urls
            else:
                logger.warning(f"Search returned status {response.status_code}")
        except Exception as e:
            logger.error(f"Search failed: {e}")

        return []

    def download_year_alternative(self, year: int) -> bool:
        """Try alternative methods to download data for a specific year"""
        logger.info(f"\nTrying alternative downloads for {year}")

        # Search for available data
        urls = self.search_europa_data_portal(year)

        if urls:
            logger.info(f"Found {len(urls)} potential URLs for {year}")
            for url in urls:
                filename = url.split('/')[-1] or f"ted_{year}_data"
                local_file = self.historical_path / filename

                if self.download_file(url, local_file, f"{year} data"):
                    self.completed_downloads["csv"][str(year)] = True
                    self.save_download_log()
                    return True

        # Try annual archives
        annual_urls = [
            f"https://data.europa.eu/api/hub/store/data/ted-{year}.csv",
            f"https://data.europa.eu/api/hub/store/data/ted-contract-notices-{year}.csv",
            f"https://data.europa.eu/api/hub/store/data/ted-{year}.zip",
        ]

        for url in annual_urls:
            filename = url.split('/')[-1]
            local_file = self.csv_path / filename

            if self.download_file(url, local_file, f"{year} annual data"):
                self.completed_downloads["csv"][str(year)] = True
                self.save_download_log()
                return True

        logger.warning(f"No data found for {year}")
        return False

    def download_all_historical(self):
        """Main method to download all historical data"""
        logger.info("="*60)
        logger.info("TED Historical Data Download V2")
        logger.info("Target: 2006-2014 to extend current 2015-2025 collection")
        logger.info("="*60)

        # Phase 1: Try bulk CSV download (most efficient)
        logger.info("\nPhase 1: Attempting bulk CSV download (2006-2021)")
        self.download_bulk_csv()

        # Phase 2: Try monthly XML for 2011-2014
        logger.info("\nPhase 2: Attempting monthly XML downloads (2011-2014)")
        for year in range(2011, 2015):
            logger.info(f"\n--- Year {year} ---")
            success_count = 0

            for month in range(1, 13):
                if self.try_monthly_xml_http(year, month):
                    success_count += 1
                    time.sleep(1)  # Be polite
                else:
                    # Try alternative if monthly fails
                    if month == 12 and success_count == 0:
                        self.download_year_alternative(year)

            logger.info(f"Year {year}: {success_count}/12 months")

        # Phase 3: Fill gaps for 2006-2010
        logger.info("\nPhase 3: Filling gaps for 2006-2010")
        for year in range(2006, 2011):
            if str(year) not in self.completed_downloads["csv"]:
                self.download_year_alternative(year)
                time.sleep(1)

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print download summary"""
        logger.info("\n" + "="*60)
        logger.info("Download Summary")
        logger.info("="*60)

        # CSV downloads
        csv_years = self.completed_downloads.get("csv", {})
        if csv_years:
            logger.info("\nCSV Data:")
            for year in sorted(csv_years.keys()):
                logger.info(f"  {year}: ✓ Downloaded")

        # XML downloads
        xml_years = self.completed_downloads.get("xml", {})
        if xml_years:
            logger.info("\nXML Monthly Data:")
            for year in sorted(xml_years.keys()):
                months = xml_years[year]
                logger.info(f"  {year}: {len(months)}/12 months")

        # Coverage check
        logger.info("\nCoverage Analysis (2006-2014):")
        for year in range(2006, 2015):
            year_str = str(year)
            has_csv = year_str in csv_years or "2006-2021" in csv_years
            has_xml = year_str in xml_years

            if has_csv or has_xml:
                sources = []
                if has_csv:
                    sources.append("CSV")
                if has_xml:
                    months = len(xml_years.get(year_str, []))
                    sources.append(f"XML({months}/12)")
                logger.info(f"  {year}: ✓ {', '.join(sources)}")
            else:
                logger.warning(f"  {year}: ✗ MISSING")

        # Disk usage
        total_size = 0
        for file in self.historical_path.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size

        logger.info(f"\nTotal disk usage: {total_size/1024/1024:.1f} MB")
        logger.info(f"Location: {self.historical_path}")

def main():
    """Main execution function"""
    downloader = TEDHistoricalDownloaderV2()

    try:
        # Check for test mode
        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            logger.info("TEST MODE: Attempting single download")
            # Try bulk CSV first as test
            success = downloader.download_bulk_csv()
            if success:
                logger.info("✅ Test successful!")
            else:
                # Try single month
                success = downloader.try_monthly_xml_http(2014, 12)
                if success:
                    logger.info("✅ Monthly download works!")
                else:
                    logger.warning("⚠️ Downloads may be restricted")
            return

        # Full download
        downloader.download_all_historical()

        logger.info("\n" + "="*60)
        logger.info("✅ Historical download process completed!")
        logger.info("\nNext steps:")
        logger.info("1. Check F:/TED_Data/historical/ for downloaded files")
        logger.info("2. Extract and process CSV/XML data")
        logger.info("3. Run analysis on 2006-2014 data")
        logger.info("4. Integrate with existing 2015-2025 pipeline")

    except KeyboardInterrupt:
        logger.info("\n⚠️ Download interrupted by user")
        downloader.save_download_log()

    except Exception as e:
        logger.error(f"\n❌ Download failed: {e}")
        import traceback
        traceback.print_exc()
        downloader.save_download_log()

if __name__ == "__main__":
    main()
