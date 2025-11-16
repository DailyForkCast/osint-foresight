#!/usr/bin/env python3
"""
GLEIF Relationship Reprocessing Script
Focuses only on processing the 464K relationship records that were lost to database locks
Includes retry logic and WAL mode for reliability
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
        logging.FileHandler('gleif_relationships_reprocessing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
GLEIF_DATA_DIR = Path("F:/GLEIF")

class GLEIFRelationshipReprocessor:
    def __init__(self):
        self.db_path = DB_PATH
        self.data_dir = GLEIF_DATA_DIR
        self.conn = None
        self.max_retries = 5

    def connect_with_wal(self):
        """Connect to database and enable WAL mode for better concurrency"""
        logger.info("Connecting to database...")
        self.conn = sqlite3.connect(self.db_path, timeout=60)
        self.conn.row_factory = sqlite3.Row

        # Enable WAL mode for better concurrent access
        logger.info("Enabling WAL mode for better concurrency...")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.commit()
        logger.info("WAL mode enabled")

    def extract_nested_value(self, obj, default=''):
        """Extract value from nested GLEIF JSON structure"""
        if isinstance(obj, dict):
            return obj.get('$', default)
        return obj if obj is not None else default

    def execute_with_retry(self, cursor, sql, params=None):
        """Execute SQL with exponential backoff retry on database locks"""
        for attempt in range(self.max_retries):
            try:
                if params:
                    if isinstance(params, list):
                        cursor.executemany(sql, params)
                    else:
                        cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                self.conn.commit()
                return True
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s, 8s, 16s
                    logger.warning(f"Database locked, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Failed after {attempt + 1} attempts: {e}")
                    raise
        return False

    def clear_existing_relationships(self):
        """Clear the existing (broken) relationship data"""
        logger.info("Clearing existing relationship data...")
        cursor = self.conn.cursor()

        # Check current count
        current_count = cursor.execute("SELECT COUNT(*) FROM gleif_relationships").fetchone()[0]
        logger.info(f"Current relationship records: {current_count}")

        if current_count > 0:
            self.execute_with_retry(cursor, "DELETE FROM gleif_relationships")
            logger.info(f"Deleted {current_count} existing records")
        else:
            logger.info("No existing records to delete")

    def process_relationships_streaming(self):
        """Process RR relationship records using streaming parser with retry logic"""
        logger.info("Starting GLEIF relationship reprocessing...")

        zip_file = self.data_dir / "20251011-0800-gleif-goldencopy-rr-golden-copy.json.zip"
        if not zip_file.exists():
            logger.error(f"Relationship file not found: {zip_file}")
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
                # Use ijson to stream parse the relations array
                relations = ijson.items(f, 'relations.item')

                for relation in relations:
                    try:
                        relationship_record = relation.get('RelationshipRecord', {})
                        relationship_data = relationship_record.get('Relationship', {})

                        child_lei = self.extract_nested_value(
                            relationship_data.get('StartNode', {}).get('NodeID', {})
                        )
                        parent_lei = self.extract_nested_value(
                            relationship_data.get('EndNode', {}).get('NodeID', {})
                        )
                        rel_type = self.extract_nested_value(
                            relationship_data.get('RelationshipType', {})
                        )
                        rel_status = self.extract_nested_value(
                            relationship_data.get('RelationshipStatus', {})
                        )

                        periods = relationship_data.get('RelationshipPeriods', [])
                        start_date = ''
                        last_update = ''
                        if periods and len(periods) > 0:
                            period = periods[0] if isinstance(periods, list) else periods
                            if isinstance(period, dict):
                                start_date = self.extract_nested_value(period.get('StartDate', {}))
                                last_update = self.extract_nested_value(period.get('PeriodLastUpdateDate', {}))

                        validation_docs = self.extract_nested_value(
                            relationship_data.get('RelationshipQualifier', {})
                            .get('QualifierDimension', {})
                            .get('ValidationDocuments', {})
                        )

                        validation_ref = ''

                        rel_record = (
                            child_lei,
                            parent_lei,
                            rel_type,
                            rel_status,
                            start_date,
                            last_update,
                            validation_docs,
                            validation_ref,
                            datetime.now(timezone.utc).isoformat()
                        )

                        batch.append(rel_record)

                        if len(batch) >= batch_size:
                            # Try to insert batch with retry logic
                            sql = """
                                INSERT OR IGNORE INTO gleif_relationships
                                (child_lei, parent_lei, relationship_type, relationship_status,
                                 start_date, last_update_date, validation_documents, validation_reference, processed_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """

                            try:
                                self.execute_with_retry(cursor, sql, batch)
                                processed += len(batch)
                            except Exception as e:
                                logger.error(f"Failed to insert batch after all retries: {e}")
                                errors += len(batch)

                            # Log progress every 30 seconds
                            now = time.time()
                            if now - last_log_time >= 30:
                                elapsed = now - start_time
                                rate = processed / elapsed if elapsed > 0 else 0
                                logger.info(
                                    f"Processed {processed:,} relationships "
                                    f"({rate:.0f}/sec, {elapsed/60:.1f}min elapsed, {errors} errors)"
                                )
                                last_log_time = now

                            batch = []

                    except Exception as e:
                        logger.warning(f"Error processing relationship: {e}")
                        errors += 1
                        continue

                # Final batch
                if batch:
                    sql = """
                        INSERT OR IGNORE INTO gleif_relationships
                        (child_lei, parent_lei, relationship_type, relationship_status,
                         start_date, last_update_date, validation_documents, validation_reference, processed_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    try:
                        self.execute_with_retry(cursor, sql, batch)
                        processed += len(batch)
                    except Exception as e:
                        logger.error(f"Failed to insert final batch: {e}")
                        errors += len(batch)

        elapsed = time.time() - start_time
        logger.info(f"\n{'='*80}")
        logger.info(f"RELATIONSHIP REPROCESSING COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Processed: {processed:,} relationships")
        logger.info(f"Errors: {errors}")
        logger.info(f"Time: {elapsed/60:.1f} minutes ({processed/elapsed:.0f} rec/sec)")
        logger.info(f"{'='*80}")

        return processed > 0

    def verify_results(self):
        """Verify the reprocessed data"""
        logger.info("\nVerifying results...")
        cursor = self.conn.cursor()

        total = cursor.execute("SELECT COUNT(*) FROM gleif_relationships").fetchone()[0]
        logger.info(f"Total relationships in database: {total:,}")

        # Check relationship types
        rel_types = cursor.execute("""
            SELECT relationship_type, COUNT(*) as cnt
            FROM gleif_relationships
            WHERE relationship_type IS NOT NULL AND relationship_type != ''
            GROUP BY relationship_type
            ORDER BY cnt DESC
        """).fetchall()

        logger.info("\nRelationship types:")
        for rel_type, cnt in rel_types:
            logger.info(f"  - {rel_type}: {cnt:,}")

        # Check for China-related relationships
        cn_relationships = cursor.execute("""
            SELECT COUNT(DISTINCT r.child_lei)
            FROM gleif_relationships r
            JOIN gleif_entities e ON r.child_lei = e.lei
            WHERE e.legal_address_country = 'CN'
        """).fetchone()[0]

        logger.info(f"\nCN entities with relationships: {cn_relationships:,}")

        # Expected count
        expected = 464_565
        if total > expected * 0.99:
            logger.info(f"\n✅ SUCCESS: {total:,} relationships processed (>99% of expected {expected:,})")
        elif total > expected * 0.95:
            logger.info(f"\n⚠️  WARNING: {total:,} relationships processed (>95% of expected {expected:,})")
        else:
            logger.error(f"\n❌ ISSUE: Only {total:,} relationships processed (<95% of expected {expected:,})")

    def run(self):
        """Execute relationship reprocessing"""
        try:
            logger.info("="*80)
            logger.info("GLEIF RELATIONSHIP REPROCESSING")
            logger.info("="*80)
            start_time = time.time()

            self.connect_with_wal()
            self.clear_existing_relationships()
            success = self.process_relationships_streaming()

            if success:
                self.verify_results()

            elapsed = time.time() - start_time
            logger.info(f"\nTotal execution time: {elapsed/60:.1f} minutes")

            return success

        except Exception as e:
            logger.error(f"Reprocessing failed: {e}", exc_info=True)
            return False
        finally:
            if self.conn:
                self.conn.close()
                logger.info("Database connection closed")

if __name__ == "__main__":
    reprocessor = GLEIFRelationshipReprocessor()
    success = reprocessor.run()

    if success:
        logger.info("\n✅ Reprocessing completed successfully")
    else:
        logger.error("\n❌ Reprocessing failed")
        exit(1)
