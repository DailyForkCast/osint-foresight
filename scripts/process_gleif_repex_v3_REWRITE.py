#!/usr/bin/env python3
"""
GLEIF REPEX Processor - COMPLETE REWRITE
Simple, straightforward processing with explicit type handling
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
        logging.FileHandler('gleif_repex_v3_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
GLEIF_DATA_DIR = Path("F:/GLEIF")


def get_string_value(obj):
    """Extract string from GLEIF nested structure or return empty string"""
    if obj is None:
        return ''
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        val = obj.get('$', '')
        return str(val) if val else ''
    return str(obj)


def get_array_string(arr):
    """Extract and join array values into comma-separated string"""
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


def process_repex():
    """Process GLEIF REPEX data"""

    # Find REPEX file
    repex_files = sorted(GLEIF_DATA_DIR.glob("*repex-golden-copy.json.zip"), reverse=True)
    if not repex_files:
        logger.error("No REPEX files found")
        return False

    zip_file = repex_files[0]
    logger.info(f"Processing: {zip_file}")

    # Connect to database
    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.commit()

    cursor = conn.cursor()

    # Clear existing data
    count = cursor.execute("SELECT COUNT(*) FROM gleif_repex").fetchone()[0]
    logger.info(f"Clearing {count:,} existing records...")
    cursor.execute("DELETE FROM gleif_repex")
    conn.commit()

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
                        # Extract all fields as strings explicitly
                        lei_obj = exception.get('LEI', {})
                        lei = get_string_value(lei_obj)

                        cat_obj = exception.get('ExceptionCategory', {})
                        category = get_string_value(cat_obj)

                        reason_arr = exception.get('ExceptionReason', [])
                        reason = get_array_string(reason_arr)

                        ref_obj = exception.get('ExceptionReference', {})
                        reference = get_string_value(ref_obj)

                        reg = exception.get('Registration', {})
                        status_obj = reg.get('RegistrationStatus', {})
                        status = get_string_value(status_obj)

                        date_obj = reg.get('LastUpdateDate', {})
                        last_update = get_string_value(date_obj)

                        imported = datetime.now(timezone.utc).isoformat()

                        # Create record tuple - all should be strings
                        record = (lei, category, reason, reference, status, last_update, imported)

                        # Double-check all are strings (paranoid validation)
                        for idx, val in enumerate(record):
                            if not isinstance(val, str):
                                logger.error(f"NON-STRING at position {idx}: {type(val)} = {repr(val)}")
                                # Force convert
                                record = tuple(str(v) if v is not None else '' for v in record)
                                break

                        batch.append(record)

                        # Insert batch
                        if len(batch) >= batch_size:
                            sql = """
                                INSERT OR IGNORE INTO gleif_repex
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
                INSERT OR IGNORE INTO gleif_repex
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


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("GLEIF REPEX PROCESSOR V3 - COMPLETE REWRITE")
    logger.info("=" * 80)

    success = process_repex()

    if success:
        logger.info("Processing completed successfully")
    else:
        logger.error("Processing failed")
        exit(1)
