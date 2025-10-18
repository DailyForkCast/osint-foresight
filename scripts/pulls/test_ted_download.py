"""
Test TED download with one month
"""

from ted_bulk_download import TEDBulkDownloader
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test with August 2024
downloader = TEDBulkDownloader("F:/TED_Data")

logger.info("Testing download for August 2024...")
success = downloader.download_monthly_package(2024, 8)

if success:
    logger.info("✅ Test download successful!")
    logger.info("Check F:/TED_Data/monthly/2024/ for the file")
else:
    logger.info("❌ Test download failed")
