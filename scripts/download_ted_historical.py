#!/usr/bin/env python3
"""
TED Europa Historical Data Downloader
Downloads TED procurement data from 2006-2014 to extend current 2015-2025 collection

Data sources:
- 2011-2014: Monthly XML packages from FTP
- 2006-2010: CSV format from data.europa.eu
"""

import os
import sys
import time
import ftplib
import requests
from pathlib import Path
from datetime import datetime
import hashlib
import json
from typing import Dict, List, Tuple
import logging
from urllib.parse import urlparse
import zipfile
import tarfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ted_historical_download.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TEDHistoricalDownloader:
    def __init__(self, base_path: str = "F:/TED_Data"):
        """Initialize TED historical data downloader"""
        self.base_path = Path(base_path)
        self.monthly_path = self.base_path / "monthly"
        self.csv_path = self.base_path / "csv_historical"

        # Create directories
        self.monthly_path.mkdir(parents=True, exist_ok=True)
        self.csv_path.mkdir(parents=True, exist_ok=True)

        # FTP settings for XML data
        self.ftp_host = "ted.europa.eu"
        self.ftp_user = "guest"
        self.ftp_pass = "guest"

        # Track downloads
        self.download_log = self.base_path / "download_log.json"
        self.completed_downloads = self.load_download_log()

    def load_download_log(self) -> Dict:
        """Load download history"""
        if self.download_log.exists():
            with open(self.download_log, 'r') as f:
                return json.load(f)
        return {"xml": {}, "csv": {}}

    def save_download_log(self):
        """Save download history"""
        with open(self.download_log, 'w') as f:
            json.dump(self.completed_downloads, f, indent=2)

    def download_xml_monthly(self, year: int, month: int) -> bool:
        """
        Download monthly XML package from TED FTP
        Format: TED_monthly_YYYY_MM.tar.gz
        """
        month_str = f"{month:02d}"
        filename = f"TED_monthly_{year}_{month_str}.tar.gz"
        year_path = self.monthly_path / str(year)
        year_path.mkdir(exist_ok=True)

        local_file = year_path / filename

        # Check if already downloaded
        if local_file.exists():
            size = local_file.stat().st_size
            if size > 1000000:  # At least 1MB
                logger.info(f"Already downloaded: {filename} ({size/1024/1024:.1f}MB)")
                return True

        logger.info(f"Downloading: {filename}")

        try:
            # Connect to FTP
            ftp = ftplib.FTP(self.ftp_host)
            ftp.login(self.ftp_user, self.ftp_pass)

            # Navigate to monthly directory
            ftp_path = f"/monthly/{year:04d}/{month_str}"
            try:
                ftp.cwd(ftp_path)
            except:
                logger.warning(f"Directory not found: {ftp_path}")
                ftp.quit()
                return False

            # Download file
            with open(local_file, 'wb') as f:
                ftp.retrbinary(f'RETR {filename}', f.write, blocksize=8192)

            ftp.quit()

            size = local_file.stat().st_size
            logger.info(f"Downloaded: {filename} ({size/1024/1024:.1f}MB)")

            # Record successful download
            if str(year) not in self.completed_downloads["xml"]:
                self.completed_downloads["xml"][str(year)] = []
            self.completed_downloads["xml"][str(year)].append(month)
            self.save_download_log()

            return True

        except Exception as e:
            logger.error(f"Failed to download {filename}: {e}")
            if local_file.exists():
                local_file.unlink()
            return False

    def download_csv_data(self, start_year: int = 2006, end_year: int = 2010) -> bool:
        """
        Download CSV format data from data.europa.eu
        Covers 2006-2010 period before monthly XML became available
        """
        csv_urls = {
            # These are example URLs - actual URLs would need to be verified
            "2006-2010": "https://data.europa.eu/api/hub/store/data/ted-contract-notices-2006-2010.csv",
            "2006": "https://data.europa.eu/api/hub/store/data/ted-contract-notices-2006.csv",
            "2007": "https://data.europa.eu/api/hub/store/data/ted-contract-notices-2007.csv",
            "2008": "https://data.europa.eu/api/hub/store/data/ted-contract-notices-2008.csv",
            "2009": "https://data.europa.eu/api/hub/store/data/ted-contract-notices-2009.csv",
            "2010": "https://data.europa.eu/api/hub/store/data/ted-contract-notices-2010.csv",
        }

        logger.info(f"Downloading CSV data for {start_year}-{end_year}")

        for year in range(start_year, end_year + 1):
            year_str = str(year)
            local_file = self.csv_path / f"TED_notices_{year}.csv"

            # Check if already downloaded
            if local_file.exists():
                size = local_file.stat().st_size
                if size > 1000000:  # At least 1MB
                    logger.info(f"Already downloaded: {year} CSV ({size/1024/1024:.1f}MB)")
                    continue

            # Try year-specific URL
            if year_str in csv_urls:
                url = csv_urls[year_str]
                logger.info(f"Downloading {year} CSV from {url}")

                try:
                    response = requests.get(url, stream=True, timeout=30)
                    response.raise_for_status()

                    with open(local_file, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    size = local_file.stat().st_size
                    logger.info(f"Downloaded: {year} CSV ({size/1024/1024:.1f}MB)")

                    # Record successful download
                    if "csv" not in self.completed_downloads:
                        self.completed_downloads["csv"] = {}
                    self.completed_downloads["csv"][year_str] = True
                    self.save_download_log()

                except Exception as e:
                    logger.error(f"Failed to download {year} CSV: {e}")
                    if local_file.exists():
                        local_file.unlink()

        return True

    def download_ftp_alternative(self, year: int) -> bool:
        """
        Alternative method to download annual data via FTP
        Some years may have annual archives instead of monthly
        """
        filename = f"TED_{year}.tar.gz"
        year_path = self.monthly_path / str(year)
        year_path.mkdir(exist_ok=True)

        local_file = year_path / filename

        if local_file.exists() and local_file.stat().st_size > 1000000:
            logger.info(f"Already downloaded: {filename}")
            return True

        try:
            ftp = ftplib.FTP(self.ftp_host)
            ftp.login(self.ftp_user, self.ftp_pass)

            # Try different paths
            paths_to_try = [
                f"/archives/{year}",
                f"/annual/{year}",
                f"/{year}",
            ]

            for ftp_path in paths_to_try:
                try:
                    ftp.cwd(ftp_path)
                    logger.info(f"Found directory: {ftp_path}")

                    # List files
                    files = []
                    ftp.dir(files.append)

                    for file_line in files:
                        if '.tar.gz' in file_line or '.zip' in file_line:
                            parts = file_line.split()
                            if parts:
                                file_name = parts[-1]
                                logger.info(f"Found archive: {file_name}")

                                # Download
                                local_archive = year_path / file_name
                                with open(local_archive, 'wb') as f:
                                    ftp.retrbinary(f'RETR {file_name}', f.write)

                                logger.info(f"Downloaded: {file_name}")
                                ftp.quit()
                                return True
                except:
                    continue

            ftp.quit()
            logger.warning(f"No archives found for {year}")
            return False

        except Exception as e:
            logger.error(f"FTP alternative failed for {year}: {e}")
            return False

    def download_all_historical(self):
        """
        Main method to download all historical data
        """
        logger.info("="*60)
        logger.info("TED Historical Data Download")
        logger.info("="*60)

        # Phase 1: Download 2011-2014 monthly XML (same format as current)
        logger.info("\nPhase 1: Downloading 2011-2014 monthly XML packages")
        logger.info("-"*40)

        for year in range(2011, 2015):
            logger.info(f"\nProcessing year {year}")
            success_count = 0

            for month in range(1, 13):
                if self.download_xml_monthly(year, month):
                    success_count += 1
                time.sleep(2)  # Be polite to the FTP server

            logger.info(f"Year {year}: {success_count}/12 months downloaded")

        # Phase 2: Download 2006-2010 data
        logger.info("\nPhase 2: Downloading 2006-2010 historical data")
        logger.info("-"*40)

        # Try CSV format first
        self.download_csv_data(2006, 2010)

        # Try FTP alternatives for any missing years
        for year in range(2006, 2011):
            if str(year) not in self.completed_downloads.get("csv", {}):
                logger.info(f"Trying FTP alternative for {year}")
                self.download_ftp_alternative(year)
                time.sleep(2)

        logger.info("\n" + "="*60)
        logger.info("Download Summary")
        logger.info("="*60)
        self.print_summary()

    def print_summary(self):
        """Print download summary"""
        # Count XML downloads
        xml_years = self.completed_downloads.get("xml", {})
        total_xml_months = sum(len(months) for months in xml_years.values())

        # Count CSV downloads
        csv_years = self.completed_downloads.get("csv", {})

        logger.info(f"\nXML Monthly Data (2011-2014):")
        for year in sorted(xml_years.keys()):
            months = xml_years[year]
            logger.info(f"  {year}: {len(months)} months")
        logger.info(f"  Total: {total_xml_months} monthly packages")

        logger.info(f"\nCSV/Other Data (2006-2010):")
        for year in sorted(csv_years.keys()):
            logger.info(f"  {year}: Downloaded")

        # Calculate total size
        total_size = 0
        for path in [self.monthly_path, self.csv_path]:
            if path.exists():
                for file in path.rglob("*"):
                    if file.is_file():
                        total_size += file.stat().st_size

        logger.info(f"\nTotal disk usage: {total_size/1024/1024/1024:.2f} GB")

        # Check for gaps
        logger.info("\nData Coverage Check:")
        for year in range(2006, 2015):
            if year <= 2010:
                if str(year) in csv_years:
                    logger.info(f"  {year}: ✓ (CSV/Archive)")
                else:
                    logger.warning(f"  {year}: ✗ MISSING")
            else:
                if str(year) in xml_years:
                    months = len(xml_years[str(year)])
                    if months == 12:
                        logger.info(f"  {year}: ✓ (12/12 months)")
                    else:
                        logger.warning(f"  {year}: ⚠ ({months}/12 months)")
                else:
                    logger.warning(f"  {year}: ✗ MISSING")

def main():
    """Main execution function"""
    downloader = TEDHistoricalDownloader()

    # Check if we want to do a test run first
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        logger.info("TEST MODE: Downloading single month (January 2011)")
        success = downloader.download_xml_monthly(2011, 1)
        if success:
            logger.info("Test successful! Run without --test to download all data")
        else:
            logger.error("Test failed. Check connection and credentials")
        return

    # Full download
    try:
        downloader.download_all_historical()
        logger.info("\n✅ Historical download completed!")
        logger.info("Next steps:")
        logger.info("1. Verify downloaded files")
        logger.info("2. Extract and process XML/CSV data")
        logger.info("3. Integrate with existing 2015-2025 analysis")

    except KeyboardInterrupt:
        logger.info("\n⚠️ Download interrupted by user")
        downloader.save_download_log()

    except Exception as e:
        logger.error(f"\n❌ Download failed: {e}")
        downloader.save_download_log()

if __name__ == "__main__":
    main()
