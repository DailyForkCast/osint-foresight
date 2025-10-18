#!/usr/bin/env python3
"""
Import USPTO and ESTAT data into SQLite database
Uses the existing osint_master.db at F:/OSINT_WAREHOUSE/
"""

import sqlite3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional
import csv

class SQLiteImporter:
    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.decompressed_dir = Path("F:/DECOMPRESSED_DATA")
        self.processed_dir = Path("F:/PROCESSED_DATA")
        self.base_dir = Path("C:/Projects/OSINT - Foresight")

        self.setup_logging()
        self.conn = None

    def setup_logging(self):
        """Setup logging"""
        log_dir = self.base_dir / "logs"
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"sqlite_import_{datetime.now():%Y%m%d_%H%M%S}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def connect_db(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            return False

    def create_tables(self):
        """Create tables for USPTO and ESTAT data"""
        if not self.conn:
            return False

        cursor = self.conn.cursor()

        # Create USPTO metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uspto_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT UNIQUE,
                source_file TEXT,
                rows INTEGER,
                columns INTEGER,
                import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create ESTAT metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estat_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT UNIQUE,
                source_file TEXT,
                rows INTEGER,
                columns INTEGER,
                import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()
        self.logger.info("Created metadata tables")
        return True

    def clean_table_name(self, filename: str) -> str:
        """Clean filename to create valid table name"""
        table_name = filename.lower()
        table_name = table_name.replace('.csv', '').replace('.tsv', '').replace('.txt', '')
        table_name = table_name.replace(' ', '_').replace('-', '_').replace('.', '_')
        table_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in table_name)
        return table_name

    def import_csv_to_sqlite(self, filepath: Path, table_prefix: str) -> bool:
        """Import CSV/TSV file to SQLite"""
        try:
            table_name = f"{table_prefix}_{self.clean_table_name(filepath.stem)}"

            # Check if already imported
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if cursor.fetchone():
                self.logger.info(f"Table {table_name} already exists, skipping")
                return True

            # Determine delimiter
            if filepath.suffix.lower() == '.tsv':
                delimiter = '\t'
            else:
                delimiter = ','

            # Read file in chunks for large files
            chunk_size = 100000
            total_rows = 0

            self.logger.info(f"Importing {filepath.name} to table {table_name}")

            # Read first chunk to create table
            try:
                first_chunk = pd.read_csv(
                    filepath,
                    delimiter=delimiter,
                    nrows=chunk_size,
                    low_memory=False,
                    on_bad_lines='skip',
                    encoding='utf-8',
                    encoding_errors='ignore'
                )

                # Clean column names
                first_chunk.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in first_chunk.columns]

                # Create table with first chunk
                first_chunk.to_sql(table_name, self.conn, if_exists='replace', index=False)
                total_rows += len(first_chunk)

                # Read remaining chunks
                for chunk in pd.read_csv(
                    filepath,
                    delimiter=delimiter,
                    chunksize=chunk_size,
                    skiprows=range(1, chunk_size + 1),
                    header=None,
                    names=first_chunk.columns,
                    low_memory=False,
                    on_bad_lines='skip',
                    encoding='utf-8',
                    encoding_errors='ignore'
                ):
                    chunk.to_sql(table_name, self.conn, if_exists='append', index=False)
                    total_rows += len(chunk)

                    if total_rows % 500000 == 0:
                        self.logger.info(f"  Imported {total_rows:,} rows...")

                # Record metadata
                metadata_table = f"{table_prefix}_metadata"
                cursor.execute(f"""
                    INSERT OR REPLACE INTO {metadata_table}
                    (table_name, source_file, rows, columns, import_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (table_name, str(filepath), total_rows, len(first_chunk.columns), datetime.now()))

                self.conn.commit()
                self.logger.info(f"Successfully imported {table_name}: {total_rows:,} rows, {len(first_chunk.columns)} columns")
                return True

            except pd.errors.EmptyDataError:
                self.logger.warning(f"Empty file: {filepath}")
                return False

        except Exception as e:
            self.logger.error(f"Error importing {filepath}: {e}")
            return False

    def import_uspto_data(self):
        """Import all USPTO data files"""
        uspto_dir = self.decompressed_dir / "uspto_data"
        if not uspto_dir.exists():
            self.logger.warning("USPTO data directory not found")
            return

        self.logger.info("Importing USPTO data")

        # Find all CSV files (including in subdirectories)
        csv_files = list(uspto_dir.rglob("*.csv"))
        txt_files = list(uspto_dir.rglob("*.txt"))
        all_files = csv_files + txt_files

        self.logger.info(f"Found {len(all_files)} files to import ({len(csv_files)} CSV, {len(txt_files)} TXT)")

        success_count = 0
        for data_file in all_files:
            # Skip if file is too small (likely empty or header only)
            if data_file.stat().st_size < 100:
                self.logger.warning(f"Skipping small file: {data_file.name} ({data_file.stat().st_size} bytes)")
                continue

            if self.import_csv_to_sqlite(data_file, "uspto"):
                success_count += 1

        self.logger.info(f"Imported {success_count}/{len(all_files)} USPTO files")

    def import_estat_data(self):
        """Import all ESTAT data files"""
        estat_dir = self.decompressed_dir / "estat_data"
        if not estat_dir.exists():
            self.logger.warning("ESTAT data directory not found")
            return

        self.logger.info("Importing ESTAT data")

        # Find all TSV files
        tsv_files = list(estat_dir.glob("*.tsv"))
        self.logger.info(f"Found {len(tsv_files)} TSV files to import")

        success_count = 0
        for tsv_file in tsv_files:
            if self.import_csv_to_sqlite(tsv_file, "estat"):
                success_count += 1

        self.logger.info(f"Imported {success_count}/{len(tsv_files)} ESTAT files")

    def create_indexes(self):
        """Create indexes for better query performance"""
        try:
            cursor = self.conn.cursor()

            # Get all tables
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table'
                AND (name LIKE 'uspto_%' OR name LIKE 'estat_%')
                AND name NOT LIKE '%_metadata'
            """)

            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]

                # Get first column (usually an ID or key field)
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                if columns:
                    first_col = columns[0][1]  # Get column name
                    index_name = f"idx_{table_name}_{first_col}"

                    try:
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({first_col})")
                        self.logger.info(f"Created index on {table_name}.{first_col}")
                    except Exception as e:
                        self.logger.warning(f"Could not create index on {table_name}: {e}")

            self.conn.commit()

        except Exception as e:
            self.logger.error(f"Error creating indexes: {e}")

    def generate_summary(self):
        """Generate import summary"""
        if not self.conn:
            return

        cursor = self.conn.cursor()

        # Get USPTO stats
        cursor.execute("SELECT COUNT(*) FROM uspto_metadata")
        uspto_tables = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(rows) FROM uspto_metadata")
        uspto_rows = cursor.fetchone()[0] or 0

        # Get ESTAT stats
        cursor.execute("SELECT COUNT(*) FROM estat_metadata")
        estat_tables = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(rows) FROM estat_metadata")
        estat_rows = cursor.fetchone()[0] or 0

        # Get database size
        cursor.execute("SELECT page_count * page_size / 1024 / 1024 FROM pragma_page_count(), pragma_page_size()")
        db_size_mb = cursor.fetchone()[0]

        print("\n" + "="*60)
        print("SQLITE IMPORT SUMMARY")
        print("="*60)
        print(f"Database: {self.db_path}")
        print(f"Size: {db_size_mb:.2f} MB")
        print(f"\nUSPTO Data:")
        print(f"  Tables: {uspto_tables}")
        print(f"  Total Rows: {uspto_rows:,}")
        print(f"\nESTAT Data:")
        print(f"  Tables: {estat_tables}")
        print(f"  Total Rows: {estat_rows:,}")
        print("="*60)

    def run(self):
        """Run the complete import process"""
        self.logger.info("Starting SQLite import process")

        # Connect to database
        if not self.connect_db():
            self.logger.error("Failed to connect to database")
            return False

        try:
            # Create tables
            self.create_tables()

            # Import USPTO data
            self.import_uspto_data()

            # Import ESTAT data
            self.import_estat_data()

            # Create indexes
            self.create_indexes()

            # Generate summary
            self.generate_summary()

            self.logger.info("Import process complete")
            return True

        except Exception as e:
            self.logger.error(f"Import failed: {e}")
            return False

        finally:
            if self.conn:
                self.conn.close()


if __name__ == "__main__":
    importer = SQLiteImporter()
    importer.run()
