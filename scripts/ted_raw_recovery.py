#!/usr/bin/env python3
"""
Raw recovery from corrupted archives
Read gzip streams until EOF, extract what we can before corruption
"""

import gzip
import io
import tarfile
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
log_dir = Path("C:/Projects/OSINT - Foresight/logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"ted_raw_recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CORRUPTED_ARCHIVES = [
    "F:/TED_Data/monthly/2011/TED_monthly_2011_01.tar.gz",
    "F:/TED_Data/monthly/2014/TED_monthly_2014_01.tar.gz",
    "F:/TED_Data/monthly/2024/TED_monthly_2024_08.tar.gz"
]

TEMP_BASE = Path("C:/Projects/OSINT - Foresight/data/temp/raw_recovery")
TEMP_BASE.mkdir(parents=True, exist_ok=True)

def extract_until_corruption(archive_path):
    """Read gzip stream until corruption, save what we can"""
    archive_name = Path(archive_path).name
    logger.info(f"\n{'='*80}")
    logger.info(f"RAW RECOVERY: {archive_name}")
    logger.info(f"{'='*80}")

    # Read gzip stream into memory buffer
    buffer = io.BytesIO()
    bytes_read = 0

    try:
        with gzip.open(archive_path, 'rb') as gz:
            while True:
                try:
                    chunk = gz.read(8192)
                    if not chunk:
                        break
                    buffer.write(chunk)
                    bytes_read += len(chunk)

                    if bytes_read % (1024 * 1024) == 0:
                        logger.info(f"  Read {bytes_read / (1024*1024):.1f} MB...")

                except EOFError:
                    logger.info(f"  Hit EOF at {bytes_read / (1024*1024):.1f} MB")
                    break

    except Exception as e:
        logger.error(f"  Failed during decompression: {e}")
        if bytes_read == 0:
            return None

    if bytes_read == 0:
        logger.error(f"  No data recovered")
        return None

    logger.info(f"  Recovered {bytes_read / (1024*1024):.2f} MB of decompressed data")

    # Try to parse as tar
    buffer.seek(0)
    temp_dir = TEMP_BASE / archive_name.replace('.tar.gz', '')
    temp_dir.mkdir(parents=True, exist_ok=True)

    members_extracted = 0
    last_good_offset = 0

    try:
        # Try to read tar members from buffer
        with tarfile.open(fileobj=buffer, mode='r|') as tar:
            for member in tar:
                try:
                    # Track position
                    last_good_offset = buffer.tell()

                    # Extract member
                    tar.extract(member, temp_dir)
                    members_extracted += 1

                    if members_extracted % 10 == 0:
                        logger.info(f"    Extracted {members_extracted} members...")

                except Exception as e:
                    logger.warning(f"    Failed to extract {member.name}: {e}")
                    # Try to continue
                    try:
                        buffer.seek(last_good_offset + 512)  # Skip to next tar block
                    except:
                        break

    except Exception as e:
        logger.warning(f"  Tar parsing stopped: {e}")

    logger.info(f"  Total members extracted: {members_extracted}")

    if members_extracted > 0:
        return temp_dir
    else:
        return None

def main():
    """Process all corrupted archives"""
    stats = {
        'attempted': 0,
        'recovered': 0,
        'members_extracted': 0,
        'bytes_recovered': 0
    }

    for archive_path in CORRUPTED_ARCHIVES:
        stats['attempted'] += 1

        temp_dir = extract_until_corruption(archive_path)

        if temp_dir and temp_dir.exists():
            stats['recovered'] += 1

            # Count files
            all_files = list(temp_dir.rglob("*"))
            file_count = len([f for f in all_files if f.is_file()])
            stats['members_extracted'] += file_count

            logger.info(f"  Saved to: {temp_dir}")
            logger.info(f"  Files extracted: {file_count}")

            # Show some examples
            tar_files = list(temp_dir.rglob("*.tar.gz"))[:5]
            if tar_files:
                logger.info(f"  Sample files:")
                for f in tar_files:
                    logger.info(f"    {f.name}")

    logger.info(f"\n{'='*80}")
    logger.info("RAW RECOVERY SUMMARY")
    logger.info(f"{'='*80}")
    logger.info(f"Archives attempted: {stats['attempted']}")
    logger.info(f"Archives recovered: {stats['recovered']}")
    logger.info(f"Members extracted: {stats['members_extracted']}")

if __name__ == '__main__':
    main()
