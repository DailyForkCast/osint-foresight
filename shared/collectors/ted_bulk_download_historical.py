"""
TED Bulk Package Downloader - Historical Data (2015-2024)
Downloads 10 years of historical EU procurement data
"""

from ted_bulk_download import TEDBulkDownloader
import logging
import time
from typing import List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_historical_years(start_year: int = 2015, end_year: int = 2024):
    """
    Download historical TED data for specified years

    Args:
        start_year: First year to download (default: 2015)
        end_year: Last year to download (default: 2024)
    """

    logger.info("=" * 60)
    logger.info("TED BULK DOWNLOAD - HISTORICAL DATA")
    logger.info(f"Period: {start_year} - {end_year}")
    logger.info("Target: F:/TED_Data")
    logger.info("=" * 60)

    # Initialize downloader
    downloader = TEDBulkDownloader("F:/TED_Data")

    total_successful = 0
    total_failed = 0

    # Download each year
    for year in range(start_year, end_year + 1):
        logger.info(f"\n{'='*50}")
        logger.info(f"Processing Year: {year}")
        logger.info(f"{'='*50}")

        year_successful = 0
        year_failed = 0

        # Download each month of the year
        for month in range(1, 13):
            logger.info(f"\n[{year}-{month:02d}] Downloading...")

            if downloader.download_monthly_package(year, month):
                year_successful += 1
                total_successful += 1
            else:
                year_failed += 1
                total_failed += 1

            # Be polite to the server
            time.sleep(2)

        # Year summary
        logger.info(f"\nYear {year} Complete:")
        logger.info(f"  Successful: {year_successful}/12")
        logger.info(f"  Failed: {year_failed}/12")

    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("HISTORICAL DOWNLOAD COMPLETE")
    logger.info(f"Total Successful: {total_successful}")
    logger.info(f"Total Failed: {total_failed}")
    logger.info(f"Total Size: {downloader.calculate_total_size():.2f} GB")
    logger.info("=" * 60)

    return total_successful, total_failed


def download_specific_years(years: List[int]):
    """
    Download specific years of TED data

    Args:
        years: List of years to download
    """

    logger.info("=" * 60)
    logger.info("TED BULK DOWNLOAD - SELECTED YEARS")
    logger.info(f"Years: {years}")
    logger.info("Target: F:/TED_Data")
    logger.info("=" * 60)

    downloader = TEDBulkDownloader("F:/TED_Data")

    total_successful = 0
    total_failed = 0

    for year in years:
        logger.info(f"\nProcessing Year: {year}")

        for month in range(1, 13):
            if downloader.download_monthly_package(year, month):
                total_successful += 1
            else:
                total_failed += 1

            time.sleep(2)

    logger.info(f"\nDownload complete!")
    logger.info(f"Successful: {total_successful}")
    logger.info(f"Failed: {total_failed}")

    return total_successful, total_failed


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TED HISTORICAL DATA DOWNLOADER")
    print("=" * 60)
    print("\nThis will download 10 years of TED procurement data")
    print("Period: 2015-2024 (120 monthly packages)")
    print("Estimated size: 30-50 GB compressed")
    print("Target: F:/TED_Data/monthly/")
    print("\nNote: This will take several hours to complete.")
    print("The script can be safely interrupted and resumed.")
    print("Already downloaded files will be skipped.")

    # Start downloading
    print("\nStarting download in 5 seconds...")
    print("Press Ctrl+C to cancel\n")

    try:
        time.sleep(5)
        download_historical_years(2015, 2024)
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        print("Run the script again to resume where you left off.")
