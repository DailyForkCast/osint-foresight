#!/usr/bin/env python3
"""
Prepare USPTO and ESTAT data for SQL database import
Creates schema, generates import scripts, and validates data
"""

import json
import pandas as pd
import psycopg2
from psycopg2 import sql
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional

class SQLImportPreparer:
    def __init__(self):
        self.base_dir = Path("C:/Projects/OSINT - Foresight")
        self.processed_dir = Path("F:/PROCESSED_DATA")
        self.decompressed_dir = Path("F:/DECOMPRESSED_DATA")

        # Database configuration
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'osint_foresight',
            'user': 'postgres',
            'password': 'postgres'  # Update this
        }

        self.setup_logging()

    def setup_logging(self):
        """Setup logging"""
        log_dir = self.base_dir / "logs"
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"sql_import_{datetime.now():%Y%m%d_%H%M%S}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            return None

    def create_schemas(self):
        """Create database schemas for USPTO and ESTAT data"""
        conn = self.connect_db()
        if not conn:
            return False

        try:
            cur = conn.cursor()

            # Create schemas
            schemas = ['uspto', 'estat', 'processed']
            for schema in schemas:
                cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema)))
                self.logger.info(f"Created schema: {schema}")

            conn.commit()
            cur.close()
            conn.close()
            return True

        except Exception as e:
            self.logger.error(f"Error creating schemas: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False

    def analyze_csv_structure(self, filepath: Path) -> Dict:
        """Analyze CSV/TSV file structure for table creation"""
        try:
            # Determine delimiter
            if filepath.suffix.lower() == '.tsv':
                delimiter = '\t'
            else:
                delimiter = ','

            # Read sample
            df_sample = pd.read_csv(filepath, delimiter=delimiter, nrows=100, on_bad_lines='skip')

            # Analyze columns
            column_info = {}
            for col in df_sample.columns:
                dtype = str(df_sample[col].dtype)
                max_length = df_sample[col].astype(str).str.len().max()

                # Map pandas dtype to PostgreSQL
                if 'int' in dtype:
                    pg_type = 'BIGINT'
                elif 'float' in dtype:
                    pg_type = 'DOUBLE PRECISION'
                elif 'bool' in dtype:
                    pg_type = 'BOOLEAN'
                elif 'datetime' in dtype:
                    pg_type = 'TIMESTAMP'
                else:
                    # Use VARCHAR with appropriate length
                    if max_length < 50:
                        pg_type = 'VARCHAR(100)'
                    elif max_length < 255:
                        pg_type = 'VARCHAR(500)'
                    else:
                        pg_type = 'TEXT'

                column_info[col] = {
                    'type': pg_type,
                    'nullable': df_sample[col].isnull().any(),
                    'sample_values': df_sample[col].dropna().head(3).tolist()
                }

            return {
                'columns': column_info,
                'row_count': len(df_sample),
                'delimiter': delimiter
            }

        except Exception as e:
            self.logger.error(f"Error analyzing {filepath}: {e}")
            return None

    def create_table_from_csv(self, filepath: Path, schema: str, table_name: str):
        """Create PostgreSQL table based on CSV structure"""
        analysis = self.analyze_csv_structure(filepath)
        if not analysis:
            return False

        conn = self.connect_db()
        if not conn:
            return False

        try:
            cur = conn.cursor()

            # Build CREATE TABLE statement
            columns = []
            for col_name, col_info in analysis['columns'].items():
                # Clean column name for PostgreSQL
                clean_name = col_name.lower().replace(' ', '_').replace('-', '_')
                nullable = '' if col_info['nullable'] else ' NOT NULL'
                columns.append(f'"{clean_name}" {col_info["type"]}{nullable}')

            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
                id SERIAL PRIMARY KEY,
                import_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                {', '.join(columns)}
            )
            """

            cur.execute(create_sql)
            conn.commit()

            self.logger.info(f"Created table: {schema}.{table_name}")

            # Save table metadata
            metadata = {
                'table': f'{schema}.{table_name}',
                'source_file': str(filepath),
                'columns': analysis['columns'],
                'created': datetime.now().isoformat()
            }

            metadata_file = self.processed_dir / f"{schema}_{table_name}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)

            cur.close()
            conn.close()
            return True

        except Exception as e:
            self.logger.error(f"Error creating table: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False

    def generate_copy_script(self, filepath: Path, schema: str, table_name: str):
        """Generate PostgreSQL COPY command for bulk import"""
        analysis = self.analyze_csv_structure(filepath)
        if not analysis:
            return None

        # Clean column names
        columns = [col.lower().replace(' ', '_').replace('-', '_')
                  for col in analysis['columns'].keys()]

        # Generate COPY command
        copy_cmd = f"""
        \\COPY {schema}.{table_name} ({','.join(columns)})
        FROM '{filepath.as_posix()}'
        WITH (FORMAT csv, DELIMITER '{analysis['delimiter']}', HEADER true, ENCODING 'UTF8');
        """

        # Save to file
        script_file = self.processed_dir / f"{schema}_{table_name}_import.sql"
        with open(script_file, 'w') as f:
            f.write(f"-- Import script for {table_name}\n")
            f.write(f"-- Generated: {datetime.now()}\n")
            f.write(f"-- Source: {filepath}\n\n")
            f.write(copy_cmd)

        self.logger.info(f"Generated import script: {script_file}")
        return script_file

    def process_uspto_files(self):
        """Process all USPTO files for SQL import"""
        uspto_dir = self.decompressed_dir / "uspto_data"
        if not uspto_dir.exists():
            self.logger.warning("USPTO data directory not found")
            return

        self.logger.info("Processing USPTO files for SQL import")

        # Find all CSV files
        csv_files = list(uspto_dir.rglob("*.csv"))
        self.logger.info(f"Found {len(csv_files)} CSV files")

        for csv_file in csv_files:
            table_name = csv_file.stem.lower().replace(' ', '_').replace('-', '_')

            # Create table
            if self.create_table_from_csv(csv_file, 'uspto', table_name):
                # Generate import script
                self.generate_copy_script(csv_file, 'uspto', table_name)

    def process_estat_files(self):
        """Process all ESTAT files for SQL import"""
        estat_dir = self.decompressed_dir / "estat_data"
        if not estat_dir.exists():
            self.logger.warning("ESTAT data directory not found")
            return

        self.logger.info("Processing ESTAT files for SQL import")

        # Find all TSV files
        tsv_files = list(estat_dir.rglob("*.tsv"))
        self.logger.info(f"Found {len(tsv_files)} TSV files")

        for tsv_file in tsv_files:
            table_name = tsv_file.stem.lower().replace(' ', '_').replace('-', '_')

            # Create table
            if self.create_table_from_csv(tsv_file, 'estat', table_name):
                # Generate import script
                self.generate_copy_script(tsv_file, 'estat', table_name)

    def generate_master_import_script(self):
        """Generate master script to import all data"""
        master_script = self.processed_dir / "master_import.sql"

        with open(master_script, 'w') as f:
            f.write("-- Master Import Script for USPTO and ESTAT Data\n")
            f.write(f"-- Generated: {datetime.now()}\n")
            f.write("-- Run this script to import all prepared data\n\n")

            f.write("-- Set client encoding\n")
            f.write("SET client_encoding = 'UTF8';\n\n")

            f.write("-- USPTO Data Import\n")
            f.write("\\echo 'Importing USPTO data...'\n")

            # Find all USPTO import scripts
            uspto_scripts = list(self.processed_dir.glob("uspto_*_import.sql"))
            for script in uspto_scripts:
                f.write(f"\\i '{script.as_posix()}'\n")

            f.write("\n-- ESTAT Data Import\n")
            f.write("\\echo 'Importing ESTAT data...'\n")

            # Find all ESTAT import scripts
            estat_scripts = list(self.processed_dir.glob("estat_*_import.sql"))
            for script in estat_scripts:
                f.write(f"\\i '{script.as_posix()}'\n")

            f.write("\n-- Verify imports\n")
            f.write("\\echo 'Verification:'\n")
            f.write("SELECT schemaname, tablename, n_live_tup as row_count\n")
            f.write("FROM pg_stat_user_tables\n")
            f.write("WHERE schemaname IN ('uspto', 'estat')\n")
            f.write("ORDER BY schemaname, tablename;\n")

        self.logger.info(f"Generated master import script: {master_script}")
        return master_script

    def validate_import_readiness(self):
        """Validate that data is ready for import"""
        issues = []

        # Check database connection
        conn = self.connect_db()
        if not conn:
            issues.append("Cannot connect to database")
        else:
            conn.close()

        # Check data directories
        if not self.decompressed_dir.exists():
            issues.append(f"Decompressed data directory not found: {self.decompressed_dir}")

        # Check for data files
        uspto_files = list((self.decompressed_dir / "uspto_data").rglob("*.csv")) if (self.decompressed_dir / "uspto_data").exists() else []
        estat_files = list((self.decompressed_dir / "estat_data").rglob("*.tsv")) if (self.decompressed_dir / "estat_data").exists() else []

        if not uspto_files:
            issues.append("No USPTO CSV files found")
        if not estat_files:
            issues.append("No ESTAT TSV files found")

        # Report results
        if issues:
            self.logger.warning("Import readiness check failed:")
            for issue in issues:
                self.logger.warning(f"  - {issue}")
            return False
        else:
            self.logger.info("Import readiness check passed")
            self.logger.info(f"  - Found {len(uspto_files)} USPTO files")
            self.logger.info(f"  - Found {len(estat_files)} ESTAT files")
            return True

    def run(self):
        """Run the complete SQL import preparation"""
        self.logger.info("Starting SQL import preparation")

        # Validate readiness
        if not self.validate_import_readiness():
            self.logger.error("System not ready for import preparation")
            return False

        # Create schemas
        if not self.create_schemas():
            self.logger.error("Failed to create database schemas")
            return False

        # Process USPTO files
        self.process_uspto_files()

        # Process ESTAT files
        self.process_estat_files()

        # Generate master import script
        master_script = self.generate_master_import_script()

        self.logger.info("SQL import preparation complete")
        self.logger.info(f"To import data, run: psql -U postgres -d osint_foresight -f {master_script}")

        return True


if __name__ == "__main__":
    preparer = SQLImportPreparer()
    preparer.run()
