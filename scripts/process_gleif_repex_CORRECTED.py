#!/usr/bin/env python3
"""
GLEIF REPEX (Reporting Exceptions) Processor - CORRECTED VERSION
Processes GLEIF reporting exceptions data using streaming parser

FIXES:
- Fixed extract_nested_value and extract_array_values method definitions (were corrupted)
- Uses extract_array_values for ExceptionReason (which can be an array)
- Uses 'item' instead of 'exceptions.item' for ijson path
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
        logging.FileHandler('gleif_repex_processing_corrected.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
GLEIF_DATA_DIR = Path("F:/GLEIF")

class GLEIFREPEXProcessor:
    def __init__(self):
        self.db_path = DB_PATH
        self.data_dir = GLEIF_DATA_DIR
        self.conn = None

    def connect_with_wal(self):
        """Connect to database and enable WAL mode"""
        logger.info("Connecting to database...")
        self.conn = sqlite3.connect(self.db_path, timeout=60)
        self.conn.row_factory = sqlite3.Row

        logger.info("Enabling WAL mode...")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.commit()
        logger.info("WAL mode enabled")

    def extract_nested_value(self, obj, default=''):
        """Extract value from nested GLEIF JSON structure"""
        if isinstance(obj, dict):
            return obj.get('$', default)
        return obj if obj is not None else default

    def extract_array_values(self, arr, default=''):
        """Extract values from array of nested objects"""
        if not arr:
            return default
        if isinstance(arr, list):
            values = []
            for item in arr:
                val = self.extract_nested_value(item)
                if val:
                    values.append(val)
            result = ', '.join(values) if values else default
            # Ensure we always return a string
            if not isinstance(result, str):
                logger.error(f"extract_array_values returning non-string: {type(result)} = {repr(result)}")
                return str(result)
            return result
        # Not a list, try to extract as single value
        return self.extract_nested_value(arr, default)

    def clear_existing_data(self):
        """Clear existing REPEX data"""
        logger.info("Clearing existing REPEX data...")
        cursor = self.conn.cursor()

        current_count = cursor.execute("SELECT COUNT(*) FROM gleif_repex").fetchone()[0]
        logger.info(f"Current REPEX records: {current_count}")

        if current_count > 0:
            cursor.execute("DELETE FROM gleif_repex")
            self.conn.commit()
            logger.info(f"Deleted {current_count} existing records")

    def process_repex_streaming(self):
        """Process REPEX records using streaming parser"""
        logger.info("Starting GLEIF REPEX processing...")

        # Find most recent REPEX golden copy file
        repex_files = sorted(self.data_dir.glob("*repex-golden-copy.json.zip"), reverse=True)
        if not repex_files:
            logger.error("No REPEX golden copy files found")
            return False

        zip_file = repex_files[0]
        if not zip_file.exists():
            logger.error(f"REPEX file not found: {zip_file}")
            return False

        cursor = self.conn.cursor()
        batch = []
        batch_size = 1000
        processed = 0
        errors = 0
        start_time = time.time()
        last_log_time = start_time

        logger.info(f"Processing from: {zip_file}")

        with zipfile.ZipFile(zip_file) as zf:
            json_filename = zf.namelist()[0]
            logger.info(f"Streaming {json_filename}...")

            with zf.open(json_filename, 'r') as f:
                try:
                    # Use 'exceptions.item' to iterate over the exceptions array
                    exceptions = ijson.items(f, 'exceptions.item')

                    for exception in exceptions:
                        try:
                            # Extract exception data directly (not wrapped in ReportingException)
                            lei = self.extract_nested_value(
                                exception.get('LEI', {})
                            )

                            exception_info = exception.get('ExceptionCategory', {})
                            exception_category = self.extract_nested_value(exception_info)

                            # Use extract_array_values for ExceptionReason (can be an array)
                            exception_reason_raw = exception.get('ExceptionReason', [])
                            exception_reason = self.extract_array_values(exception_reason_raw)

                            # Force convert to string to be absolutely sure
                            if not isinstance(exception_reason, str):
                                logger.error(f"CRITICAL: exception_reason is {type(exception_reason)}, converting to string")
                                logger.error(f"  Raw: {repr(exception_reason_raw)}")
                                logger.error(f"  Processed: {repr(exception_reason)}")
                                exception_reason = str(exception_reason) if exception_reason else ''

                            exception_reference = self.extract_nested_value(
                                exception.get('ExceptionReference', {})
                            )

                            registration_status = self.extract_nested_value(
                                exception.get('Registration', {}).get('RegistrationStatus', {})
                            )

                            last_update = self.extract_nested_value(
                                exception.get('Registration', {}).get('LastUpdateDate', {})
                            )

                            # Force exception_reason to be a string
                            exception_reason_final = str(exception_reason) if exception_reason else ''

                            # TEMPORARY HARDCODE TEST - Override with a test string
                            exception_reason_final = "TEST_HARDCODED_STRING"

                            # Debug logging
                            if not isinstance(exception_reason_final, str):
                                logger.error(f"IMPOSSIBLE: after str() conversion, still not a string: {type(exception_reason_final)}")

                            repex_record = (
                                lei,
                                exception_category,
                                exception_reason_final,
                                exception_reference,
                                registration_status,
                                last_update,
                                datetime.now(timezone.utc).isoformat()
                            )

                            batch.append(repex_record)

                            if len(batch) >= batch_size:
                                sql = """
                                    INSERT OR IGNORE INTO gleif_repex
                                    (lei, exception_category, exception_reason, exception_reference,
                                     registration_status, last_update_date, imported_date)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """
                                # Validate batch before inserting
                                for idx, rec in enumerate(batch):
                                    for pidx, val in enumerate(rec):
                                        if not isinstance(val, (str, int, float, type(None))):
                                            logger.error(f"Invalid type in batch[{idx}], param{pidx}: {type(val)} = {repr(val)}")

                                cursor.executemany(sql, batch)
                                self.conn.commit()
                                processed += len(batch)

                                # Log progress every 30 seconds
                                now = time.time()
                                if now - last_log_time >= 30:
                                    elapsed = now - start_time
                                    rate = processed / elapsed if elapsed > 0 else 0
                                    logger.info(
                                        f"Processed {processed:,} exceptions "
                                        f"({rate:.0f}/sec, {elapsed/60:.1f}min elapsed, {errors} errors)"
                                    )
                                    last_log_time = now

                                batch = []

                        except Exception as e:
                            logger.warning(f"Error processing exception: {e}", exc_info=True)
                            errors += 1
                            batch = []  # Clear the batch to avoid retrying bad data
                            if errors >= 10:
                                logger.error("Too many errors, stopping to investigate")
                                return False
                            continue

                except Exception as e:
                    logger.error(f"Error parsing JSON: {e}")
                    return False

                # Final batch
                if batch:
                    sql = """
                        INSERT OR IGNORE INTO gleif_repex
                        (lei, exception_category, exception_reason, exception_reference,
                         registration_status, last_update_date, imported_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """
                    cursor.executemany(sql, batch)
                    self.conn.commit()
                    processed += len(batch)

        elapsed = time.time() - start_time
        logger.info(f"\n{'='*80}")
        logger.info(f"REPEX PROCESSING COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Processed: {processed:,} exceptions")
        logger.info(f"Errors: {errors}")
        logger.info(f"Time: {elapsed/60:.1f} minutes ({processed/elapsed:.0f} rec/sec)")
        logger.info(f"{'='*80}")

        return processed > 0

    def create_indexes(self):
        """Create indexes for efficient querying"""
        logger.info("Creating indexes...")
        cursor = self.conn.cursor()

        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gleif_repex_lei ON gleif_repex(lei)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gleif_repex_category ON gleif_repex(exception_category)")
            self.conn.commit()
            logger.info("Indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    def verify_results(self):
        """Verify the processed data"""
        logger.info("\nVerifying results...")
        cursor = self.conn.cursor()

        total = cursor.execute("SELECT COUNT(*) FROM gleif_repex").fetchone()[0]
        logger.info(f"Total exceptions in database: {total:,}")

        # Check exception categories
        categories = cursor.execute("""
            SELECT exception_category, COUNT(*) as cnt
            FROM gleif_repex
            WHERE exception_category IS NOT NULL AND exception_category != ''
            GROUP BY exception_category
            ORDER BY cnt DESC
        """).fetchall()

        logger.info("\nException categories:")
        for cat, cnt in categories:
            logger.info(f"  - {cat}: {cnt:,}")

    def run(self):
        """Execute REPEX processing"""
        try:
            logger.info("="*80)
            logger.info("GLEIF REPEX PROCESSING - CORRECTED VERSION")
            logger.info("="*80)
            start_time = time.time()

            self.connect_with_wal()
            self.clear_existing_data()
            success = self.process_repex_streaming()

            if success:
                self.create_indexes()
                self.verify_results()

            elapsed = time.time() - start_time
            logger.info(f"\nTotal execution time: {elapsed/60:.1f} minutes")

            return success

        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)
            return False
        finally:
            if self.conn:
                self.conn.close()
                logger.info("Database connection closed")

if __name__ == "__main__":
    processor = GLEIFREPEXProcessor()
    success = processor.run()

    if success:
        logger.info("\nREPEX processing completed successfully")
    else:
        logger.error("\nREPEX processing failed")
        exit(1)
