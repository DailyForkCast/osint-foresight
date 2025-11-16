#!/usr/bin/env python3
"""
Create Composite Indices for Multi-Filter Queries
Optimizes common query patterns that filter on multiple columns
"""

import sqlite3
import re
import logging
import time
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('composite_indices.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")


def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier


# Composite indices to create
# Format: (index_name, table, columns_list, description)
COMPOSITE_INDICES = [
    # Geographic + Value queries
    (
        'idx_ted_country_value',
        'ted_contracts_production',
        ['iso_country', 'value_total'],
        'TED contracts by country and value (1.1M records)'
    ),
    (
        'idx_ted_country_date',
        'ted_contracts_production',
        ['iso_country', 'award_date'],
        'TED contracts by country and date (1.1M records)'
    ),

    # Multi-filter USAspending
    (
        'idx_usaspending_country_date',
        'usaspending_contracts',
        ['recipient_country', 'contract_date'],
        'USAspending by country and date (250K records)'
    ),
    (
        'idx_usaspending_country_value',
        'usaspending_contracts',
        ['recipient_country', 'contract_value'],
        'USAspending by country and value (250K records)'
    ),

    # GLEIF composite queries
    (
        'idx_gleif_country_category',
        'gleif_entities',
        ['legal_address_country', 'entity_category'],
        'GLEIF by country and category (3.1M records)'
    ),

    # OpenAlex year + type
    (
        'idx_openalex_year_type',
        'openalex_works',
        ['publication_year', 'work_type'],
        'OpenAlex by year and type (496K records)'
    ),

    # arXiv year + category
    (
        'idx_arxiv_year_category',
        'arxiv_papers',
        ['year', 'primary_category'],
        'arXiv by year and category (1.4M records)'
    ),
]


class CompositeIndexCreator:
    def __init__(self):
        self.db_path = DB_PATH
        self.stats = {
            'created': 0,
            'skipped': 0,
            'failed': 0,
            'timings': []
        }

    def index_exists(self, cursor, index_name):
        """Check if index already exists"""
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name=?",
            (index_name,)
        )
        return cursor.fetchone() is not None

    def table_exists(self, cursor, table):
        """Check if table exists"""
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        )
        return cursor.fetchone() is not None

    def columns_exist(self, cursor, table, columns):
        """Check if all columns exist in table"""
        # Validate table name
        safe_table = validate_sql_identifier(table)

        cursor.execute(f"PRAGMA table_info({safe_table})")
        existing_columns = {row[1] for row in cursor.fetchall()}

        missing = [col for col in columns if col not in existing_columns]

        if missing:
            return False, f"Missing columns: {', '.join(missing)}"

        return True, "OK"

    def create_indices(self):
        """Create all composite indices"""
        logger.info("="*80)
        logger.info("CREATING COMPOSITE INDICES")
        logger.info("="*80)
        logger.info(f"Database: {self.db_path}")
        logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"\nTotal composite indices to create: {len(COMPOSITE_INDICES)}")
        logger.info("")

        conn = sqlite3.connect(self.db_path, timeout=120)
        cursor = conn.cursor()

        # Enable WAL mode
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.commit()

        for index_name, table, columns, description in COMPOSITE_INDICES:
            logger.info(f"\nCreating {index_name}...")
            logger.info(f"  Table: {table}")
            logger.info(f"  Columns: {', '.join(columns)}")
            logger.info(f"  Description: {description}")

            # Check if index already exists
            if self.index_exists(cursor, index_name):
                logger.info(f"  Status: ALREADY EXISTS (skipping)")
                self.stats['skipped'] += 1
                continue

            # Check if table exists
            if not self.table_exists(cursor, table):
                logger.warning(f"  Status: SKIPPED (table '{table}' not found)")
                self.stats['skipped'] += 1
                continue

            # Check if columns exist
            exists, message = self.columns_exist(cursor, table, columns)
            if not exists:
                logger.warning(f"  Status: SKIPPED ({message})")
                self.stats['skipped'] += 1
                continue

            # Create composite index
            try:
                # SECURITY: Validate all identifiers
                safe_index = validate_sql_identifier(index_name)
                safe_table = validate_sql_identifier(table)
                safe_columns = [validate_sql_identifier(col) for col in columns]

                columns_str = ', '.join(safe_columns)

                start = datetime.now()
                cursor.execute(f"CREATE INDEX {safe_index} ON {safe_table}({columns_str})")
                conn.commit()
                elapsed = (datetime.now() - start).total_seconds()

                logger.info(f"  Status: CREATED ({elapsed:.2f}s)")
                self.stats['created'] += 1
                self.stats['timings'].append((index_name, elapsed))

            except Exception as e:
                logger.error(f"  Status: FAILED ({str(e)})")
                self.stats['failed'] += 1

        # Run ANALYZE to update query planner statistics
        logger.info("\n" + "="*80)
        logger.info("Running ANALYZE to update query planner statistics...")
        start = datetime.now()
        cursor.execute("ANALYZE")
        conn.commit()
        analyze_time = (datetime.now() - start).total_seconds()
        logger.info(f"ANALYZE complete ({analyze_time:.1f}s)")

        conn.close()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print creation summary"""
        logger.info("\n" + "="*80)
        logger.info("SUMMARY")
        logger.info("="*80)
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

        if self.stats['created'] > 0:
            logger.info("[SUCCESS] Composite indices created successfully!")
            logger.info("")
            logger.info("Expected performance improvements:")
            logger.info("  - Multi-filter queries: 3-5x faster")
            logger.info("  - Complex WHERE clauses: 2-4x faster")
            logger.info("  - Reduces need for multiple index lookups")

        logger.info("\n" + "="*80)
        logger.info(f"COMPLETE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)


if __name__ == '__main__':
    creator = CompositeIndexCreator()
    creator.create_indices()
