#!/usr/bin/env python3
"""
GLEIF REPEX Processor - ROBUST VERSION
Handles database locks and large WAL files
"""

import sqlite3
import ijson
import zipfile
import logging
import time
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gleif_repex_v4_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
GLEIF_DATA_DIR = Path("F:/GLEIF")


def get_string_value(obj):
    """Extract string from GLEIF nested structure"""
    if obj is None:
        return ''
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        val = obj.get('$', '')
        return str(val) if val else ''
    return str(obj)


def get_array_string(arr):
    """Extract and join array values"""
    if not arr:
        return ''
    if not isinstance(arr, list):
        return get_string_value(arr)

    values = []
    for item in arr:
        val = get_string_value(item)
        if val:
            values.append(val)

    return ', '.join(values) if values else ''


def connect_with_retry(max_attempts=5):
    """Connect to database with retry logic"""
    for attempt in range(max_attempts):
        try:
            logger.info(f"Database connection attempt {attempt + 1}/{max_attempts}...")
            conn = sqlite3.connect(DB_PATH, timeout=120)

            # Try a simple query to verify connection
            conn.execute("SELECT 1").fetchone()
            logger.info("Connected successfully!")

            # Enable WAL mode
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")

            # Try to checkpoint WAL if it's large
            logger.info("Attempting WAL checkpoint...")
            conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
            conn.commit()
            logger.info("Checkpoint complete")

            return conn

        except sqlite3.OperationalError as e:
            logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                wait_time = 10 * (attempt + 1)
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                raise

    return None


def process_repex():
    """Process GLEIF REPEX data"""

    # Find REPEX file
    repex_files = sorted(GLEIF_DATA_DIR.glob("*repex-golden-copy.json.zip"), reverse=True)
    if not repex_files:
        logger.error("No REPEX files found")
        return False

    zip_file = repex_files[0]
    logger.info(f"Processing: {zip_file}")

    # Connect to database with retry
    conn = connect_with_retry()
    if not conn:
        logger.error("Failed to connect to database")
        return False

    cursor = conn.cursor()

    # Skip clearing - will use INSERT OR REPLACE instead
    logger.info("Skipping delete, will use INSERT OR REPLACE to update existing records")

    # Process file
    batch = []
    batch_size = 1000
    processed = 0
    errors = 0
    start_time = time.time()
    last_log = start_time

    try:
        with zipfile.ZipFile(zip_file) as zf:
            json_file = zf.namelist()[0]
            logger.info(f"Streaming: {json_file}")

            with zf.open(json_file, 'r') as f:
                for exception in ijson.items(f, 'exceptions.item'):
                    try:
                        # Extract all fields as strings
                        lei = get_string_value(exception.get('LEI', {}))
                        category = get_string_value(exception.get('ExceptionCategory', {}))
                        reason = get_array_string(exception.get('ExceptionReason', []))
                        reference = get_string_value(exception.get('ExceptionReference', {}))

                        reg = exception.get('Registration', {})
                        status = get_string_value(reg.get('RegistrationStatus', {}))
                        last_update = get_string_value(reg.get('LastUpdateDate', {}))
                        imported = datetime.now(timezone.utc).isoformat()

                        # Create record - force all to strings
                        record = (
                            str(lei), str(category), str(reason), str(reference),
                            str(status), str(last_update), str(imported)
                        )

                        batch.append(record)

                        # Insert batch
                        if len(batch) >= batch_size:
                            sql = """
                                INSERT OR REPLACE INTO gleif_repex
                                (lei, exception_category, exception_reason, exception_reference,
                                 registration_status, last_update_date, imported_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """
                            cursor.executemany(sql, batch)
                            conn.commit()
                            processed += len(batch)
                            batch = []

                            # Progress logging
                            now = time.time()
                            if now - last_log >= 30:
                                elapsed = now - start_time
                                rate = processed / elapsed if elapsed > 0 else 0
                                logger.info(
                                    f"Processed: {processed:,} records "
                                    f"({rate:.0f}/sec, {elapsed/60:.1f}min, {errors} errors)"
                                )
                                last_log = now

                    except Exception as e:
                        logger.warning(f"Error processing record: {e}")
                        errors += 1
                        if errors >= 100:
                            logger.error("Too many errors, stopping")
                            return False
                        continue

        # Insert final batch
        if batch:
            sql = """
                INSERT OR REPLACE INTO gleif_repex
                (lei, exception_category, exception_reason, exception_reference,
                 registration_status, last_update_date, imported_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.executemany(sql, batch)
            conn.commit()
            processed += len(batch)

        # Summary
        elapsed = time.time() - start_time
        logger.info("=" * 80)
        logger.info("REPEX PROCESSING COMPLETE")
        logger.info(f"Processed: {processed:,} records")
        logger.info(f"Errors: {errors}")
        logger.info(f"Time: {elapsed/60:.1f} minutes ({processed/elapsed:.0f} rec/sec)")
        logger.info("=" * 80)

        # Create indexes
        logger.info("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gleif_repex_lei ON gleif_repex(lei)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gleif_repex_category ON gleif_repex(exception_category)")
        conn.commit()

        # Verify
        total = cursor.execute("SELECT COUNT(*) FROM gleif_repex").fetchone()[0]
        logger.info(f"Total in database: {total:,}")

        return True

    finally:
        conn.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("GLEIF REPEX PROCESSOR V4 - ROBUST WITH DB LOCK HANDLING")
    logger.info("=" * 80)

    success = process_repex()

    if success:
        logger.info("Processing completed successfully")
    else:
        logger.error("Processing failed")
        exit(1)
