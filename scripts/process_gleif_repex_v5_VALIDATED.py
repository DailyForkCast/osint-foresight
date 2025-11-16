#!/usr/bin/env python3
"""
GLEIF REPEX Processor - FULLY VALIDATED VERSION
Comprehensive data quality validation and safeguards
"""

import sqlite3
import ijson
import zipfile
import logging
import time
import re
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gleif_repex_v5_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
GLEIF_DATA_DIR = Path("F:/GLEIF")

# Known GLEIF Exception Categories (from GLEIF documentation)
VALID_EXCEPTION_CATEGORIES = {
    'DIRECT_ACCOUNTING_CONSOLIDATION_PARENT',
    'ULTIMATE_ACCOUNTING_CONSOLIDATION_PARENT',
    'NO_LEI',
    'NATURAL_PERSONS',
    'NON_CONSOLIDATING',
    'BINDING_LEGAL_COMMITMENTS'
}

# Known Exception Reasons
VALID_EXCEPTION_REASONS = {
    'NON_CONSOLIDATING',
    'NO_KNOWN_PERSON',
    'NATURAL_PERSONS',
    'NO_LEI',
    'BINDING_LEGAL_COMMITMENTS',
    'CONSENT_NOT_OBTAINED',
    'DETRIMENT_NOT_EXCLUDED',
    'LEGAL_OBSTACLES',
    'DISCLOSURE_DETRIMENTAL'
}

# LEI format: exactly 20 alphanumeric characters
LEI_PATTERN = re.compile(r'^[A-Z0-9]{20}$')

# Data quality statistics
class DataQualityStats:
    def __init__(self):
        self.total_records = 0
        self.valid_records = 0
        self.invalid_lei_format = 0
        self.missing_lei = 0
        self.missing_category = 0
        self.unknown_category = 0
        self.unknown_reason = 0
        self.empty_reason = 0
        self.unexpected_structure = 0
        self.category_counts = defaultdict(int)
        self.reason_counts = defaultdict(int)
        self.sample_records = []

    def log_summary(self):
        """Log comprehensive data quality summary"""
        logger.info("=" * 80)
        logger.info("DATA QUALITY SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total records processed: {self.total_records:,}")
        logger.info(f"Valid records: {self.valid_records:,} ({self.valid_records/self.total_records*100:.2f}%)")
        logger.info("")
        logger.info("VALIDATION ISSUES:")
        logger.info(f"  Invalid LEI format: {self.invalid_lei_format:,}")
        logger.info(f"  Missing LEI: {self.missing_lei:,}")
        logger.info(f"  Missing category: {self.missing_category:,}")
        logger.info(f"  Unknown category: {self.unknown_category:,}")
        logger.info(f"  Unknown reason: {self.unknown_reason:,}")
        logger.info(f"  Empty reason: {self.empty_reason:,}")
        logger.info(f"  Unexpected structure: {self.unexpected_structure:,}")
        logger.info("")
        logger.info("TOP EXCEPTION CATEGORIES:")
        for cat, count in sorted(self.category_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {cat}: {count:,}")
        logger.info("")
        logger.info("TOP EXCEPTION REASONS:")
        for reason, count in sorted(self.reason_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {reason}: {count:,}")
        logger.info("=" * 80)


def validate_lei(lei):
    """Validate LEI format"""
    if not lei:
        return False, "empty"
    if not isinstance(lei, str):
        return False, f"wrong_type:{type(lei).__name__}"
    if not LEI_PATTERN.match(lei):
        return False, f"invalid_format:{len(lei)}chars"
    return True, None


def validate_category(category):
    """Validate exception category"""
    if not category:
        return False, "empty"
    if category not in VALID_EXCEPTION_CATEGORIES:
        return False, f"unknown:{category}"
    return True, None


def validate_reason(reason):
    """Validate exception reason"""
    if not reason:
        return False, "empty"
    # Reason can be comma-separated list
    reasons = [r.strip() for r in reason.split(',')]
    unknown = []
    for r in reasons:
        if r and r not in VALID_EXCEPTION_REASONS:
            # Check if it's a freeform text reason (non-standard but allowed)
            if len(r) > 100:  # Likely descriptive text
                continue
            unknown.append(r)
    if unknown:
        return False, f"unknown:{','.join(unknown[:3])}"
    return True, None


def get_string_value(obj, field_name="unknown"):
    """Extract string from GLEIF nested structure with validation"""
    if obj is None:
        return '', 'null'

    if isinstance(obj, str):
        return obj, None

    if isinstance(obj, dict):
        # Empty dict {} is normal for missing optional fields in GLEIF
        if not obj or len(obj) == 0:
            return '', None  # No error - this is expected for optional fields

        if '$' not in obj:
            # Don't log warnings - non-empty unexpected dicts are rare
            return '', 'missing_dollar_key'
        val = obj.get('$', '')
        return str(val) if val else '', None

    # Unexpected type - don't log, just track in error return
    return str(obj), f'unexpected_type:{type(obj).__name__}'


def get_array_string(arr, field_name="unknown"):
    """Extract and join array values with validation"""
    if not arr:
        return '', 'empty'

    if not isinstance(arr, list):
        # Not an array, try single value
        val, err = get_string_value(arr, field_name)
        return val, err

    values = []
    errors = []
    for idx, item in enumerate(arr):
        val, err = get_string_value(item, f"{field_name}[{idx}]")
        if err:
            errors.append(err)
        if val:
            values.append(val)

    result = ', '.join(values) if values else ''
    error = errors[0] if errors else None
    return result, error


def connect_with_retry(max_attempts=5):
    """Connect to database with retry logic"""
    for attempt in range(max_attempts):
        try:
            logger.info(f"Database connection attempt {attempt + 1}/{max_attempts}...")
            conn = sqlite3.connect(DB_PATH, timeout=120)
            conn.execute("SELECT 1").fetchone()
            logger.info("Connected successfully!")

            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")

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
    """Process GLEIF REPEX data with full validation"""

    stats = DataQualityStats()

    # Find REPEX file
    repex_files = sorted(GLEIF_DATA_DIR.glob("*repex-golden-copy.json.zip"), reverse=True)
    if not repex_files:
        logger.error("No REPEX files found")
        return False

    zip_file = repex_files[0]
    logger.info(f"Processing: {zip_file}")

    # Connect to database
    conn = connect_with_retry()
    if not conn:
        logger.error("Failed to connect to database")
        return False

    cursor = conn.cursor()
    logger.info("Skipping delete, will use INSERT OR REPLACE to update existing records")

    # Process file
    batch = []
    batch_size = 1000
    processed = 0
    rejected = 0
    start_time = time.time()
    last_log = start_time

    try:
        with zipfile.ZipFile(zip_file) as zf:
            json_file = zf.namelist()[0]
            logger.info(f"Streaming: {json_file}")

            with zf.open(json_file, 'r') as f:
                for exception in ijson.items(f, 'exceptions.item'):
                    stats.total_records += 1

                    try:
                        # Extract fields with validation
                        lei_obj = exception.get('LEI', {})
                        lei, lei_err = get_string_value(lei_obj, 'LEI')

                        cat_obj = exception.get('ExceptionCategory', {})
                        category, cat_err = get_string_value(cat_obj, 'ExceptionCategory')

                        reason_arr = exception.get('ExceptionReason', [])
                        reason, reason_err = get_array_string(reason_arr, 'ExceptionReason')

                        ref_obj = exception.get('ExceptionReference', {})
                        reference, ref_err = get_string_value(ref_obj, 'ExceptionReference')

                        reg = exception.get('Registration', {})
                        status_obj = reg.get('RegistrationStatus', {})
                        status, status_err = get_string_value(status_obj, 'RegistrationStatus')

                        date_obj = reg.get('LastUpdateDate', {})
                        last_update, date_err = get_string_value(date_obj, 'LastUpdateDate')

                        imported = datetime.now(timezone.utc).isoformat()

                        # Track extraction errors
                        if lei_err or cat_err or reason_err:
                            stats.unexpected_structure += 1

                        # Validate LEI
                        lei_valid, lei_issue = validate_lei(lei)
                        if not lei_valid:
                            if lei_issue == "empty":
                                stats.missing_lei += 1
                            else:
                                stats.invalid_lei_format += 1
                            # Only log first 10 LEI issues
                            if (stats.missing_lei + stats.invalid_lei_format) <= 10:
                                logger.warning(f"Record {stats.total_records}: Invalid LEI: {lei} ({lei_issue})")

                        # Validate category
                        cat_valid, cat_issue = validate_category(category)
                        if not cat_valid:
                            if cat_issue == "empty":
                                stats.missing_category += 1
                            else:
                                stats.unknown_category += 1
                            # Only log first 10 category issues
                            if (stats.missing_category + stats.unknown_category) <= 10:
                                logger.warning(f"Record {stats.total_records}: Category issue: {category} ({cat_issue})")

                        # Validate reason
                        reason_valid, reason_issue = validate_reason(reason)
                        if not reason_valid:
                            if reason_issue == "empty":
                                stats.empty_reason += 1
                            else:
                                stats.unknown_reason += 1
                            # Only log first 10 reason issues
                            if (stats.empty_reason + stats.unknown_reason) <= 10:
                                logger.warning(f"Record {stats.total_records}: Reason issue: {reason[:50]} ({reason_issue})")

                        # Track statistics
                        if category:
                            stats.category_counts[category] += 1
                        if reason:
                            # Track each reason separately if comma-separated
                            for r in reason.split(','):
                                r = r.strip()
                                if r:
                                    stats.reason_counts[r] += 1

                        # Sample first 20 records
                        if stats.total_records <= 20:
                            stats.sample_records.append({
                                'lei': lei,
                                'category': category,
                                'reason': reason,
                                'reference': reference,
                                'lei_valid': lei_valid,
                                'cat_valid': cat_valid
                            })

                        # Decide whether to accept record
                        # Require at minimum: valid LEI and valid category
                        if lei_valid and cat_valid:
                            stats.valid_records += 1

                            # Create record - force all to strings
                            record = (
                                str(lei), str(category), str(reason), str(reference),
                                str(status), str(last_update), str(imported)
                            )

                            batch.append(record)
                        else:
                            rejected += 1
                            # Log first 20 rejections
                            if rejected <= 20:
                                logger.error(
                                    f"REJECTED record {stats.total_records}: "
                                    f"LEI={lei}({lei_valid}), "
                                    f"Category={category}({cat_valid})"
                                )

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
                                rate = stats.total_records / elapsed if elapsed > 0 else 0
                                logger.info(
                                    f"Processed: {processed:,} valid records from {stats.total_records:,} total "
                                    f"({rate:.0f}/sec, {elapsed/60:.1f}min, {rejected} rejected)"
                                )
                                last_log = now

                    except Exception as e:
                        logger.error(f"Error processing record {stats.total_records}: {e}", exc_info=True)
                        rejected += 1
                        if rejected >= 1000:
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

        # Processing summary
        elapsed = time.time() - start_time
        logger.info("=" * 80)
        logger.info("REPEX PROCESSING COMPLETE")
        logger.info(f"Processed: {processed:,} valid records inserted")
        logger.info(f"Rejected: {rejected:,} records")
        logger.info(f"Time: {elapsed/60:.1f} minutes ({stats.total_records/elapsed:.0f} rec/sec)")
        logger.info("=" * 80)

        # Data quality summary
        stats.log_summary()

        # Log sample records
        logger.info("")
        logger.info("SAMPLE RECORDS (first 10):")
        for i, rec in enumerate(stats.sample_records[:10], 1):
            logger.info(f"  {i}. LEI={rec['lei'][:10]}... Category={rec['category']} Valid={rec['lei_valid'] and rec['cat_valid']}")

        # Create indexes
        logger.info("")
        logger.info("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gleif_repex_lei ON gleif_repex(lei)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gleif_repex_category ON gleif_repex(exception_category)")
        conn.commit()
        logger.info("Indexes created")

        # Final verification
        total = cursor.execute("SELECT COUNT(*) FROM gleif_repex").fetchone()[0]
        logger.info(f"")
        logger.info(f"Total records in database: {total:,}")

        return True

    finally:
        conn.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("GLEIF REPEX PROCESSOR V5 - FULLY VALIDATED")
    logger.info("=" * 80)

    success = process_repex()

    if success:
        logger.info("")
        logger.info("✓ Processing completed successfully with data quality validation")
    else:
        logger.error("")
        logger.error("✗ Processing failed")
        exit(1)
