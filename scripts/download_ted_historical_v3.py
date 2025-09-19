#!/usr/bin/env python3
"""
TED Europa Historical Data Downloader V3
Downloads TED procurement data from 2006-2014 using correct URL patterns

Based on official TED documentation:
- Monthly packages: https://ted.europa.eu/packages/monthly/{yyyy-n}
- Available from January 2011 onwards
"""

import os
import sys
import time
import requests
from pathlib import Path
from datetime import datetime
import json
import logging
from typing import Dict, List
import tarfile
import gzip

# Configure logging with UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ted_historical_download.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TEDHistoricalDownloaderV3:
    def __init__(self, base_path: str = "F:/TED_Data"):
        """Initialize TED historical data downloader"""
        self.base_path = Path(base_path)
        self.monthly_path = self.base_path / "monthly"

        # Create directories for years
        for year in range(2006, 2015):
            (self.monthly_path / str(year)).mkdir(parents=True, exist_ok=True)

        # Track downloads
        self.download_log = self.base_path / "download_history.json"
        self.completed_downloads = self.load_download_log()

        # Session for connection reuse
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def load_download_log(self) -> Dict:
        """Load download history"""
        if self.download_log.exists():
            with open(self.download_log, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"completed": {}, "failed": {}, "statistics": {}}

    def save_download_log(self):
        """Save download history"""
        with open(self.download_log, 'w', encoding='utf-8') as f:
            json.dump(self.completed_downloads, f, indent=2, ensure_ascii=False)

    def download_monthly_package(self, year: int, month: int) -> bool:
        """
        Download monthly XML package from TED
        URL format: https://ted.europa.eu/packages/monthly/{yyyy-n}
        where n is month without leading zero (1-12)
        """
        # Build URL - note: month without leading zero for URL
        url = f"https://ted.europa.eu/packages/monthly/{year}-{month}"

        # But filename uses zero-padded month
        month_str = f"{month:02d}"
        filename = f"TED_monthly_{year}_{month_str}.tar.gz"
        year_path = self.monthly_path / str(year)
        local_file = year_path / filename

        # Check if already downloaded
        if local_file.exists():
            size_mb = local_file.stat().st_size / 1024 / 1024
            if size_mb > 1:  # At least 1MB
                logger.info(f"Already exists: {filename} ({size_mb:.1f}MB)")
                return True
            else:
                logger.warning(f"Incomplete file found, re-downloading: {filename}")
                local_file.unlink()

        logger.info(f"Downloading: {year}-{month:02d}")
        logger.info(f"URL: {url}")

        try:
            # Make request
            response = self.session.get(url, stream=True, timeout=60)

            # Check if successful
            if response.status_code == 404:
                logger.warning(f"Not found (404): {year}-{month:02d}")
                self.record_failure(year, month, "404 Not Found")
                return False

            response.raise_for_status()

            # Check content type - should be tar.gz or octet-stream
            content_type = response.headers.get('Content-Type', '')
            if 'html' in content_type.lower():
                logger.warning(f"Got HTML instead of file for {year}-{month:02d}")
                self.record_failure(year, month, "HTML response")
                return False

            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(local_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            mb_down = downloaded / 1024 / 1024
                            mb_total = total_size / 1024 / 1024
                            print(f"\r{year}-{month:02d}: {percent:.1f}% ({mb_down:.1f}/{mb_total:.1f}MB)", end='', flush=True)

            print()  # New line after progress

            # Verify download
            final_size = local_file.stat().st_size
            size_mb = final_size / 1024 / 1024

            if final_size < 1000:  # Less than 1KB probably means error
                logger.error(f"Downloaded file too small: {filename} ({final_size} bytes)")
                local_file.unlink()
                self.record_failure(year, month, "File too small")
                return False

            logger.info(f"Success: {filename} ({size_mb:.1f}MB)")

            # Record success
            self.record_success(year, month, size_mb)
            return True

        except requests.exceptions.Timeout:
            logger.error(f"Timeout for {year}-{month:02d}")
            self.record_failure(year, month, "Timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {year}-{month:02d}: {e}")
            self.record_failure(year, month, str(e))
        except Exception as e:
            logger.error(f"Unexpected error for {year}-{month:02d}: {e}")
            self.record_failure(year, month, str(e))

        # Clean up partial download
        if local_file.exists():
            local_file.unlink()
        return False

    def record_success(self, year: int, month: int, size_mb: float):
        """Record successful download"""
        year_str = str(year)
        if year_str not in self.completed_downloads["completed"]:
            self.completed_downloads["completed"][year_str] = {}

        self.completed_downloads["completed"][year_str][str(month)] = {
            "timestamp": datetime.now().isoformat(),
            "size_mb": round(size_mb, 2)
        }

        # Update statistics
        if "statistics" not in self.completed_downloads:
            self.completed_downloads["statistics"] = {}

        stats = self.completed_downloads["statistics"]
        stats["last_update"] = datetime.now().isoformat()
        stats["total_downloads"] = sum(
            len(months) for months in self.completed_downloads["completed"].values()
        )

        self.save_download_log()

    def record_failure(self, year: int, month: int, reason: str):
        """Record failed download"""
        year_str = str(year)
        if year_str not in self.completed_downloads["failed"]:
            self.completed_downloads["failed"][year_str] = {}

        self.completed_downloads["failed"][year_str][str(month)] = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason
        }

        self.save_download_log()

    def download_year_range(self, start_year: int, end_year: int):
        """Download data for a range of years"""
        logger.info("="*60)
        logger.info(f"TED Historical Download: {start_year}-{end_year}")
        logger.info("="*60)

        total_months = (end_year - start_year + 1) * 12
        completed = 0
        failed = 0

        for year in range(start_year, end_year + 1):
            logger.info(f"\n--- Processing Year {year} ---")
            year_success = 0
            year_failed = 0

            for month in range(1, 13):
                # Check if already completed
                if (str(year) in self.completed_downloads.get("completed", {}) and
                    str(month) in self.completed_downloads["completed"][str(year)]):
                    logger.info(f"Skipping {year}-{month:02d} (already downloaded)")
                    year_success += 1
                    completed += 1
                    continue

                # Try download
                if self.download_monthly_package(year, month):
                    year_success += 1
                    completed += 1
                else:
                    year_failed += 1
                    failed += 1

                # Be polite to the server
                time.sleep(2)

            logger.info(f"Year {year} complete: {year_success}/12 successful, {year_failed} failed")

        # Final summary
        logger.info("\n" + "="*60)
        logger.info("Download Complete")
        logger.info("="*60)
        logger.info(f"Total: {completed}/{total_months} months downloaded successfully")
        logger.info(f"Failed: {failed} months")

        self.print_detailed_summary()

    def print_detailed_summary(self):
        """Print detailed download summary"""
        logger.info("\n" + "-"*40)
        logger.info("Detailed Summary")
        logger.info("-"*40)

        # Calculate total size
        total_size_mb = 0

        # Show completed downloads
        if self.completed_downloads.get("completed"):
            logger.info("\nSuccessfully Downloaded:")
            for year in sorted(self.completed_downloads["completed"].keys()):
                months = self.completed_downloads["completed"][year]
                year_size = sum(m.get("size_mb", 0) for m in months.values())
                total_size_mb += year_size
                logger.info(f"  {year}: {len(months)}/12 months ({year_size:.1f}MB)")

                # List missing months
                downloaded_months = set(int(m) for m in months.keys())
                missing_months = set(range(1, 13)) - downloaded_months
                if missing_months:
                    missing_str = ", ".join(str(m) for m in sorted(missing_months))
                    logger.info(f"    Missing: {missing_str}")

        # Show failed downloads
        if self.completed_downloads.get("failed"):
            logger.info("\nFailed Downloads:")
            for year in sorted(self.completed_downloads["failed"].keys()):
                months = self.completed_downloads["failed"][year]
                logger.info(f"  {year}: {len(months)} failures")
                for month, details in months.items():
                    logger.info(f"    Month {month}: {details['reason']}")

        logger.info(f"\nTotal disk usage: {total_size_mb/1024:.2f}GB")
        logger.info(f"Data location: {self.monthly_path}")

    def verify_downloads(self):
        """Verify downloaded files are valid tar.gz archives"""
        logger.info("\n" + "="*60)
        logger.info("Verifying Downloaded Files")
        logger.info("="*60)

        valid = 0
        invalid = 0

        for year in range(2006, 2015):
            year_path = self.monthly_path / str(year)
            if not year_path.exists():
                continue

            for file in year_path.glob("*.tar.gz"):
                try:
                    # Try to open as tar.gz
                    with tarfile.open(file, 'r:gz') as tar:
                        # Just check it can be opened
                        members = tar.getmembers()
                        if members:
                            valid += 1
                            logger.info(f"Valid: {file.name} ({len(members)} files)")
                        else:
                            invalid += 1
                            logger.warning(f"Empty archive: {file.name}")
                except Exception as e:
                    invalid += 1
                    logger.error(f"Invalid archive: {file.name} - {e}")

        logger.info(f"\nVerification complete: {valid} valid, {invalid} invalid")

def main():
    """Main execution function"""
    downloader = TEDHistoricalDownloaderV3()

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # Test mode - try one month
            logger.info("TEST MODE: Downloading January 2014")
            success = downloader.download_monthly_package(2014, 1)
            if success:
                logger.info("Test successful! Use --download to get all data")
            else:
                logger.error("Test failed. Check logs for details")
            return

        elif sys.argv[1] == "--verify":
            # Verify existing downloads
            downloader.verify_downloads()
            return

        elif sys.argv[1] == "--status":
            # Show current status
            downloader.print_detailed_summary()
            return

    # Default action - download all historical data
    logger.info("Starting historical TED data download")
    logger.info("Target: 2011-2014 (monthly XML packages)")
    logger.info("Note: Data before 2011 may not be available in monthly format")

    try:
        # Download 2011-2014 (XML monthly packages confirmed available)
        downloader.download_year_range(2011, 2014)

        # Try 2006-2010 (may not be available in same format)
        logger.info("\nAttempting 2006-2010 (may not be available):")
        downloader.download_year_range(2006, 2010)

        logger.info("\nDownload process complete!")
        logger.info("Run with --verify to check file integrity")
        logger.info("Run with --status to see download summary")

    except KeyboardInterrupt:
        logger.info("\nDownload interrupted by user")
        downloader.save_download_log()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        downloader.save_download_log()

if __name__ == "__main__":
    main()
