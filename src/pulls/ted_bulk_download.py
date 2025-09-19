"""
TED Bulk Package Downloader
Downloads monthly procurement data packages from TED
FREE - No authentication required
"""

import os
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TEDBulkDownloader:
    """Download TED monthly and daily packages"""

    def __init__(self, base_path: str = "F:/TED_Data"):
        """
        Initialize downloader

        Args:
            base_path: Where to save downloads (default: F:/TED_Data)
        """
        self.base_url = "https://ted.europa.eu/packages"
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Foresight/1.0 TED-Bulk-Downloader'
        })

    def get_last_n_months(self, n: int = 12) -> List[Tuple[int, int]]:
        """
        Get list of last N months as (year, month) tuples

        Args:
            n: Number of months to go back

        Returns:
            List of (year, month) tuples
        """
        months = []
        current = datetime.now()

        for i in range(n):
            # Calculate the target month
            month = current.month - i
            year = current.year

            # Handle year boundary
            while month <= 0:
                month += 12
                year -= 1

            months.append((year, month))

        return months

    def download_monthly_package(self, year: int, month: int) -> bool:
        """
        Download a monthly package

        Args:
            year: Year (e.g., 2024)
            month: Month (1-12)

        Returns:
            Success status
        """
        # Format: yyyy-mm (note: month without leading zero for 1-9)
        package_name = f"{year}-{month}"
        url = f"{self.base_url}/monthly/{package_name}"

        # Create year directory
        year_dir = self.base_path / "monthly" / str(year)
        year_dir.mkdir(parents=True, exist_ok=True)

        # Output filename
        filename = f"TED_monthly_{year}_{month:02d}.tar.gz"
        filepath = year_dir / filename

        # Check if already downloaded
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            logger.info(f"Already exists: {filename} ({size_mb:.1f} MB)")
            return True

        logger.info(f"Downloading: {package_name} from {url}")

        try:
            # Stream download for large files
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()

            # Get total size if available
            total_size = int(response.headers.get('content-length', 0))

            # Download with progress
            downloaded = 0
            chunk_size = 8192  # 8KB chunks

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Progress update every MB
                        if downloaded % (1024 * 1024) == 0:
                            mb_downloaded = downloaded / (1024 * 1024)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                logger.info(f"  Progress: {mb_downloaded:.1f} MB ({percent:.1f}%)")
                            else:
                                logger.info(f"  Downloaded: {mb_downloaded:.1f} MB")

            final_size_mb = filepath.stat().st_size / (1024 * 1024)
            logger.info(f"✓ Completed: {filename} ({final_size_mb:.1f} MB)")
            return True

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Package not found: {package_name} (might be too recent)")
            else:
                logger.error(f"HTTP Error downloading {package_name}: {e}")
            return False

        except Exception as e:
            logger.error(f"Error downloading {package_name}: {e}")
            # Clean up partial download
            if filepath.exists():
                filepath.unlink()
            return False

    def download_last_12_months(self):
        """Download the last 12 months of TED data"""

        logger.info("=" * 60)
        logger.info("TED BULK DOWNLOAD - Last 12 Months")
        logger.info(f"Target directory: {self.base_path}")
        logger.info("=" * 60)

        months = self.get_last_n_months(12)

        logger.info(f"Will download {len(months)} monthly packages:")
        for year, month in months:
            logger.info(f"  - {year}-{month:02d}")

        print("\nStarting downloads...\n")

        successful = 0
        failed = 0

        for i, (year, month) in enumerate(months, 1):
            logger.info(f"\n[{i}/{len(months)}] Processing {year}-{month:02d}")

            if self.download_monthly_package(year, month):
                successful += 1
            else:
                failed += 1

            # Be polite to the server
            if i < len(months):
                time.sleep(2)

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("DOWNLOAD SUMMARY")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Total size: {self.calculate_total_size():.1f} GB")
        logger.info("=" * 60)

        return successful, failed

    def calculate_total_size(self) -> float:
        """Calculate total size of downloaded files in GB"""
        total_bytes = 0
        monthly_dir = self.base_path / "monthly"

        if monthly_dir.exists():
            for file in monthly_dir.rglob("*.tar.gz"):
                total_bytes += file.stat().st_size

        return total_bytes / (1024 * 1024 * 1024)  # Convert to GB

    def download_specific_countries_recent(self, countries: List[str], months: int = 3):
        """
        Download recent data for specific countries
        Note: This requires parsing the full monthly packages

        Args:
            countries: List of country codes (e.g., ['SK', 'AT', 'IT'])
            months: Number of recent months
        """
        logger.info(f"Downloading last {months} months for countries: {countries}")

        month_list = self.get_last_n_months(months)

        for year, month in month_list:
            self.download_monthly_package(year, month)


def main():
    """Main download function"""

    print("\n" + "=" * 60)
    print("TED BULK PACKAGE DOWNLOADER")
    print("=" * 60)
    print("\nThis will download the last 12 months of TED procurement data")
    print("Target location: F:/TED_Data")
    print("Estimated size: 15-30 GB (compressed)")
    print("Cost: FREE (EU Open Data)")
    print("\nPackages contain:")
    print("- All procurement notices")
    print("- Contract awards")
    print("- Prior information notices")
    print("- XML format with full details")

    # Check if F: drive exists
    if not Path("F:/").exists():
        print("\n⚠️  WARNING: F:/ drive not found!")
        print("Please ensure your external drive is connected.")
        alt_path = input("\nEnter alternative path (or press Enter to exit): ").strip()
        if not alt_path:
            return
        downloader = TEDBulkDownloader(alt_path)
    else:
        # Check available space
        import shutil
        free_gb = shutil.disk_usage("F:/").free / (1024**3)
        print(f"\nF:/ drive available space: {free_gb:.1f} GB")

        if free_gb < 50:
            print("⚠️  WARNING: Less than 50 GB free space")

        proceed = input("\nProceed with download? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Download cancelled.")
            return

        downloader = TEDBulkDownloader("F:/TED_Data")

    # Start download
    print("\nStarting downloads...")
    successful, failed = downloader.download_last_12_months()

    if successful > 0:
        print(f"\n✅ Downloaded {successful} packages successfully!")
        print(f"Location: {downloader.base_path}")
        print("\nNext steps:")
        print("1. Extract packages: tar -xzf filename.tar.gz")
        print("2. Parse XML files for specific data")
        print("3. Filter by country, CPV codes, or keywords")

    if failed > 0:
        print(f"\n⚠️  {failed} downloads failed - check logs for details")


if __name__ == "__main__":
    main()
