"""
TED Bulk Package Downloader - Automatic Version
Downloads last 12 months without prompts
"""

from ted_bulk_download import TEDBulkDownloader
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_automatically():
    """Download last 12 months automatically to F:/TED_Data"""

    logger.info("=" * 60)
    logger.info("TED BULK DOWNLOAD - AUTOMATIC MODE")
    logger.info("Target: F:/TED_Data")
    logger.info("Period: Last 12 months")
    logger.info("=" * 60)

    # Initialize downloader
    downloader = TEDBulkDownloader("F:/TED_Data")

    # Start downloads
    successful, failed = downloader.download_last_12_months()

    logger.info(f"\n✅ Download complete!")
    logger.info(f"Successful: {successful} packages")
    logger.info(f"Failed: {failed} packages")
    logger.info(f"Location: F:/TED_Data")

    return successful, failed


if __name__ == "__main__":
    download_automatically()
