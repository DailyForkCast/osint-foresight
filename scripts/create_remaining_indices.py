#!/usr/bin/env python3
import re

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from dynamic SQL construction.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    # Check for valid characters only (alphanumeric + underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    # Check length (SQLite limit is 1024, we use 100 for safety)
    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    # Blacklist dangerous SQL keywords
    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier


"""
Create Remaining Performance Indices
Based on actual schema investigation results
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('create_remaining_indices.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

# Corrected index definitions based on actual schema
# Format: (index_name, table, column, purpose)
INDICES_TO_CREATE = [
    # Geographic indices - CORRECTED
    ('idx_gleif_legal_country', 'gleif_entities', 'legal_address_country', 'GLEIF legal country filter (3.1M records)'),
    ('idx_gleif_hq_country', 'gleif_entities', 'hq_address_country', 'GLEIF HQ country filter (3.1M records)'),
    ('idx_gleif_jurisdiction', 'gleif_entities', 'legal_jurisdiction', 'GLEIF jurisdiction filter (3.1M records)'),
    ('idx_uspto_assignee_country', 'uspto_assignee', 'ee_country', 'USPTO assignee country (2.8M records)'),
    ('idx_ted_iso_country', 'ted_contracts_production', 'iso_country', 'TED contract country (1.1M records)'),
    ('idx_sec_state', 'sec_edgar_companies', 'state_of_incorporation', 'SEC company state (805 records)'),
    ('idx_entities_origin', 'entities', 'country_origin', 'Entity country origin (238 records)'),
    ('idx_entities_operation', 'entities', 'country_operation', 'Entity country operation (238 records)'),

    # Temporal indices - CORRECTED
    ('idx_arxiv_year', 'arxiv_papers', 'year', 'arXiv temporal analysis (1.4M records)'),
    ('idx_uspto_chinese_year', 'uspto_patents_chinese', 'year', 'USPTO patents year (425K records)'),
    ('idx_openalex_works_year', 'openalex_works', 'publication_year', 'OpenAlex works year (496K records)'),
    ('idx_usaspending_date', 'usaspending_contracts', 'contract_date', 'USAspending temporal (250K records)'),

    # Value/financial indices - NEW
    ('idx_ted_value_total', 'ted_contracts_production', 'value_total', 'TED contract value (1.1M records)'),
    ('idx_usaspending_value', 'usaspending_contracts', 'contract_value', 'USAspending contract value (250K records)'),
]


class RemainingIndexCreator:
    def __init__(self):
        self.db_path = DB_PATH
        self.stats = {
            'created': 0,
            'skipped': 0,
            'failed': 0,
            'timings': []
        }

    def table_column_exists(self, cursor, table, column):
        """Check if table and column exist"""
        try:
            # Check table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cursor.fetchone():
                return False, "Table not found"

            # Check column exists
            # SECURITY: Validate table name before use in PRAGMA
            safe_table = validate_sql_identifier(table)
            cursor.execute(f"PRAGMA table_info({safe_table})")
            columns = [row[1] for row in cursor.fetchall()]

            if column not in columns:
                return False, f"Column '{column}' not found (available: {', '.join(columns[:5])}...)"

            return True, "OK"
        except Exception as e:
            return False, str(e)

    def index_exists(self, cursor, index_name):
        """Check if index already exists"""
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name=?", (index_name,))
        return cursor.fetchone() is not None

    def create_indices(self):
        """Create all remaining indices"""
        logger.info("=" * 80)
        logger.info("CREATING REMAINING PERFORMANCE INDICES")
        logger.info("=" * 80)
        logger.info(f"Database: {self.db_path}")
        logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("")

        conn = sqlite3.connect(self.db_path, timeout=60)
        cursor = conn.cursor()

        # Enable WAL mode
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.commit()

        logger.info(f"Total indices to create: {len(INDICES_TO_CREATE)}")
        logger.info("")

        for index_name, table, column, purpose in INDICES_TO_CREATE:
            logger.info(f"Creating {index_name}...")
            logger.info(f"  Table: {table}")
            logger.info(f"  Column: {column}")
            logger.info(f"  Purpose: {purpose}")

            # Check if index already exists
            if self.index_exists(cursor, index_name):
                logger.info(f"  Status: ALREADY EXISTS (skipping)")
                logger.info("")
                self.stats['skipped'] += 1
                continue

            # Check table and column exist
            exists, message = self.table_column_exists(cursor, table, column)
            if not exists:
                logger.warning(f"  Status: SKIPPED ({message})")
                logger.info("")
                self.stats['skipped'] += 1
                continue

            # Create index
            try:
                # SECURITY: Validate all identifiers before use in SQL
                safe_index = validate_sql_identifier(index_name)
                safe_table = validate_sql_identifier(table)
                safe_column = validate_sql_identifier(column)

                start = datetime.now()
                cursor.execute(f"CREATE INDEX {safe_index} ON {safe_table}({safe_column})")
                conn.commit()
                elapsed = (datetime.now() - start).total_seconds()

                logger.info(f"  Status: CREATED ({elapsed:.2f}s)")
                logger.info("")
                self.stats['created'] += 1
                self.stats['timings'].append((index_name, elapsed))

            except Exception as e:
                logger.error(f"  Status: FAILED ({str(e)})")
                logger.info("")
                self.stats['failed'] += 1

        # Run ANALYZE
        logger.info("=" * 80)
        logger.info("Running ANALYZE to update query planner statistics...")
        logger.info("")
        start = datetime.now()
        cursor.execute("ANALYZE")
        conn.commit()
        analyze_time = (datetime.now() - start).total_seconds()
        logger.info(f"ANALYZE complete ({analyze_time:.1f}s)")
        logger.info("")

        conn.close()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print creation summary"""
        logger.info("=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Created: {self.stats['created']}")
        logger.info(f"Skipped: {self.stats['skipped']}")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info("")

        if self.stats['timings']:
            logger.info("Index creation times:")
            total_time = 0
            for idx_name, elapsed in self.stats['timings']:
                logger.info(f"  {idx_name:40} {elapsed:>6.2f}s")
                total_time += elapsed
            logger.info(f"  {'TOTAL':40} {total_time:>6.2f}s")
            logger.info("")

        logger.info("=" * 80)
        logger.info(f"COMPLETE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)


if __name__ == '__main__':
    creator = RemainingIndexCreator()
    creator.create_indices()
