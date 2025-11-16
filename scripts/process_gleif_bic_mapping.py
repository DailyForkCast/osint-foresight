#!/usr/bin/env python3
"""
GLEIF BIC Mapping Processor
Processes LEI-to-BIC (Chinese corporate registry) mapping files
Critical for linking GLEIF entities to Chinese company codes
"""

import sqlite3
import zipfile
import csv
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gleif_bic_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
GLEIF_DATA_DIR = Path("F:/GLEIF")

class GLEIFBICProcessor:
    def __init__(self):
        self.db_path = DB_PATH
        self.data_dir = GLEIF_DATA_DIR
        self.conn = None
        self.processed_count = 0

    def connect(self):
        """Connect to database with WAL mode"""
        logger.info("Connecting to database...")
        self.conn = sqlite3.connect(self.db_path, timeout=60)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.commit()
        logger.info("Database connected with WAL mode")

    def clear_existing_data(self):
        """Clear existing BIC mapping data"""
        logger.info("Clearing existing BIC mapping data...")
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM gleif_bic_mapping")
        existing_count = cursor.fetchone()[0]
        logger.info(f"Current BIC mapping records: {existing_count:,}")

        cursor.execute("DELETE FROM gleif_bic_mapping")
        self.conn.commit()
        logger.info(f"Deleted {existing_count:,} existing records")

    def process_bic_file(self, zip_path):
        """Process BIC mapping CSV from zip file"""
        logger.info(f"Processing {zip_path.name}...")

        with zipfile.ZipFile(zip_path, 'r') as zf:
            csv_filename = [name for name in zf.namelist() if name.endswith('.csv')][0]
            logger.info(f"Found CSV file: {csv_filename}")

            with zf.open(csv_filename) as csvfile:
                # Wrap in TextIOWrapper for csv module
                import io
                text_file = io.TextIOWrapper(csvfile, encoding='utf-8')
                reader = csv.DictReader(text_file)

                batch = []
                batch_size = 10000

                for row in reader:
                    # Extract LEI and BIC from CSV
                    # CSV format: LEI,BIC (typically)
                    lei = row.get('LEI', '').strip()
                    bic = row.get('BIC', '').strip() or row.get('bic', '').strip()

                    # Handle different CSV column names
                    if not bic:
                        # Try other possible column names
                        for key in row.keys():
                            if 'bic' in key.lower() and key.upper() != 'LEI':
                                bic = row[key].strip()
                                break

                    if lei and bic:
                        batch.append((lei, bic, datetime.utcnow().isoformat()))

                    if len(batch) >= batch_size:
                        self._insert_batch(batch)
                        batch = []

                # Insert remaining records
                if batch:
                    self._insert_batch(batch)

        logger.info(f"Completed processing {zip_path.name}: {self.processed_count:,} records")

    def _insert_batch(self, batch):
        """Insert batch of BIC mappings"""
        cursor = self.conn.cursor()
        cursor.executemany('''
            INSERT INTO gleif_bic_mapping (lei, bic, imported_date)
            VALUES (?, ?, ?)
        ''', batch)
        self.conn.commit()
        self.processed_count += len(batch)

        if self.processed_count % 50000 == 0:
            logger.info(f"Processed {self.processed_count:,} BIC mappings...")

    def create_indexes(self):
        """Create indexes for efficient querying"""
        logger.info("Creating indexes...")
        cursor = self.conn.cursor()

        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gleif_bic_lei ON gleif_bic_mapping(lei)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gleif_bic_bic ON gleif_bic_mapping(bic)")
            self.conn.commit()
            logger.info("Indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    def run(self):
        """Main processing workflow"""
        try:
            logger.info("=" * 80)
            logger.info("GLEIF BIC MAPPING PROCESSING")
            logger.info("=" * 80)

            self.connect()
            self.clear_existing_data()

            # Find most recent BIC file
            bic_files = sorted(self.data_dir.glob("LEI-BIC-*.zip"), reverse=True)
            if not bic_files:
                logger.error("No BIC mapping files found in F:/GLEIF/")
                return

            logger.info(f"Found {len(bic_files)} BIC mapping file(s)")
            logger.info(f"Using most recent: {bic_files[0].name}")

            # Process the most recent file
            self.process_bic_file(bic_files[0])

            # Create indexes
            self.create_indexes()

            # Final statistics
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM gleif_bic_mapping")
            final_count = cursor.fetchone()[0]

            logger.info("=" * 80)
            logger.info(f"BIC MAPPING PROCESSING COMPLETE")
            logger.info(f"Total records in database: {final_count:,}")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)
            raise
        finally:
            if self.conn:
                self.conn.close()
                logger.info("Database connection closed")

if __name__ == "__main__":
    processor = GLEIFBICProcessor()
    processor.run()
