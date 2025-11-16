#!/usr/bin/env python3
"""
GLEIF OpenCorporates Mapping Processor
Processes LEI-to-OpenCorporates mapping files
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
        logging.FileHandler('gleif_opencorporates_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
GLEIF_DATA_DIR = Path("F:/GLEIF")

class GLEIFOpenCorporatesProcessor:
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
        """Clear existing OpenCorporates mapping data"""
        logger.info("Clearing existing OpenCorporates mapping data...")
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM gleif_opencorporates_mapping")
        existing_count = cursor.fetchone()[0]
        logger.info(f"Current OpenCorporates mapping records: {existing_count:,}")

        cursor.execute("DELETE FROM gleif_opencorporates_mapping")
        self.conn.commit()
        logger.info(f"Deleted {existing_count:,} existing records")

    def process_file(self, zip_path):
        """Process OpenCorporates mapping CSV from zip file"""
        logger.info(f"Processing {zip_path.name}...")

        with zipfile.ZipFile(zip_path, 'r') as zf:
            csv_filename = [name for name in zf.namelist() if name.endswith('.csv')][0]
            logger.info(f"Found CSV file: {csv_filename}")

            with zf.open(csv_filename) as csvfile:
                import io
                text_file = io.TextIOWrapper(csvfile, encoding='utf-8')
                reader = csv.DictReader(text_file)

                batch = []
                batch_size = 10000

                for row in reader:
                    lei = row.get('LEI', '').strip()
                    oc_id = row.get('OpenCorporatesID', '').strip()

                    if lei and oc_id:
                        batch.append((lei, oc_id, datetime.utcnow().isoformat()))

                    if len(batch) >= batch_size:
                        self._insert_batch(batch)
                        batch = []

                # Insert remaining records
                if batch:
                    self._insert_batch(batch)

        logger.info(f"Completed processing {zip_path.name}: {self.processed_count:,} records")

    def _insert_batch(self, batch):
        """Insert batch of OpenCorporates mappings"""
        cursor = self.conn.cursor()
        cursor.executemany('''
            INSERT INTO gleif_opencorporates_mapping (lei, opencorporates_id, imported_date)
            VALUES (?, ?, ?)
        ''', batch)
        self.conn.commit()
        self.processed_count += len(batch)

        if self.processed_count % 50000 == 0:
            logger.info(f"Processed {self.processed_count:,} OpenCorporates mappings...")

    def create_indexes(self):
        """Create indexes for efficient querying"""
        logger.info("Creating indexes...")
        cursor = self.conn.cursor()

        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gleif_oc_lei ON gleif_opencorporates_mapping(lei)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gleif_oc_id ON gleif_opencorporates_mapping(opencorporates_id)")
            self.conn.commit()
            logger.info("Indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    def run(self):
        """Main processing workflow"""
        try:
            logger.info("=" * 80)
            logger.info("GLEIF OPENCORPORATES MAPPING PROCESSING")
            logger.info("=" * 80)

            self.connect()
            self.clear_existing_data()

            # Find most recent OpenCorporates file
            oc_files = sorted(self.data_dir.glob("oc-lei-*.zip"), reverse=True)
            if not oc_files:
                logger.error("No OpenCorporates mapping files found in F:/GLEIF/")
                return

            logger.info(f"Found {len(oc_files)} OpenCorporates mapping file(s)")
            logger.info(f"Using most recent: {oc_files[0].name}")

            # Process the most recent file
            self.process_file(oc_files[0])

            # Create indexes
            self.create_indexes()

            # Final statistics
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM gleif_opencorporates_mapping")
            final_count = cursor.fetchone()[0]

            logger.info("=" * 80)
            logger.info(f"OPENCORPORATES MAPPING PROCESSING COMPLETE")
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
    processor = GLEIFOpenCorporatesProcessor()
    processor.run()
