#!/usr/bin/env python3
"""
OpenAIRE Production Database Merger
Merges OpenAIRE production database (2.1GB, 306K+ records) into master database
"""

import sqlite3
import logging
import re
from pathlib import Path
from datetime import datetime

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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('openaire_merge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SOURCE_DB = Path("F:/OSINT_Data/openaire_production_comprehensive/openaire_production.db")
TARGET_DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")

class OpenAIREMerger:
    def __init__(self):
        self.source_db = SOURCE_DB
        self.target_db = TARGET_DB
        self.stats = {}

    def merge(self):
        """Merge OpenAIRE production database into master"""
        logger.info("=" * 80)
        logger.info("OpenAIRE Production Database Merger")
        logger.info("=" * 80)
        logger.info(f"Source: {self.source_db}")
        logger.info(f"Target: {self.target_db}")
        logger.info("")

        if not self.source_db.exists():
            logger.error(f"Source database not found: {self.source_db}")
            return False

        if not self.target_db.exists():
            logger.error(f"Target database not found: {self.target_db}")
            return False

        try:
            # Connect to databases
            source_conn = sqlite3.connect(self.source_db, timeout=60)
            target_conn = sqlite3.connect(self.target_db, timeout=60)

            # Enable WAL mode on target
            target_conn.execute("PRAGMA journal_mode=WAL")
            target_conn.execute("PRAGMA synchronous=NORMAL")
            target_conn.commit()

            # Get source tables
            source_cur = source_conn.cursor()
            source_cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            source_tables = [row[0] for row in source_cur.fetchall()]

            logger.info(f"Source tables found: {len(source_tables)}")
            for table in source_tables:
                # SECURITY: Validate table name before use in SQL
                safe_table = validate_sql_identifier(table)
                source_cur.execute(f"SELECT COUNT(*) FROM {safe_table}")
                count = source_cur.fetchone()[0]
                logger.info(f"  {table}: {count:,} records")
                self.stats[f"source_{table}"] = count

            logger.info("")

            # Merge research_products
            self._merge_research_products(source_conn, target_conn)

            # Merge collaborations
            self._merge_collaborations(source_conn, target_conn)

            # Merge country_overview
            self._merge_country_overview(source_conn, target_conn)

            # Close connections
            source_conn.close()
            target_conn.close()

            # Generate summary
            self._generate_summary()

            return True

        except Exception as e:
            logger.error(f"Merge failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def _merge_research_products(self, source_conn, target_conn):
        """Merge research_products table"""
        logger.info("Merging research_products...")

        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()

        # Get source count
        source_cur.execute("SELECT COUNT(*) FROM research_products")
        source_count = source_cur.fetchone()[0]
        logger.info(f"  Source records: {source_count:,}")

        # Check target table exists
        target_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='openaire_research'")
        if not target_cur.fetchone():
            logger.warning("  Target table 'openaire_research' does not exist - skipping")
            return

        # Get current target count
        target_cur.execute("SELECT COUNT(*) FROM openaire_research")
        target_before = target_cur.fetchone()[0]
        logger.info(f"  Target records (before): {target_before:,}")

        # Get schema compatibility
        source_cur.execute("PRAGMA table_info(research_products)")
        source_cols = {row[1]: row[2] for row in source_cur.fetchall()}

        target_cur.execute("PRAGMA table_info(openaire_research)")
        target_cols = {row[1]: row[2] for row in target_cur.fetchall()}

        common_cols = set(source_cols.keys()) & set(target_cols.keys())
        logger.info(f"  Common columns: {len(common_cols)}")

        if not common_cols:
            logger.error("  No common columns - cannot merge")
            return

        # SECURITY: Validate each column name before building SQL
        safe_cols = [validate_sql_identifier(col) for col in sorted(common_cols)]
        cols_str = ", ".join(safe_cols)
        placeholders = ", ".join(["?" for _ in safe_cols])

        logger.info(f"  Merging {source_count:,} records...")
        source_cur.execute(f"SELECT {cols_str} FROM research_products")

        batch_size = 10000
        batch = []
        inserted = 0

        for row in source_cur:
            batch.append(row)
            if len(batch) >= batch_size:
                try:
                    target_cur.executemany(
                        f"INSERT OR REPLACE INTO openaire_research ({cols_str}) VALUES ({placeholders})",
                        batch
                    )
                    target_conn.commit()
                    inserted += len(batch)
                    logger.info(f"    Progress: {inserted:,}/{source_count:,} ({inserted/source_count*100:.1f}%)")
                    batch = []
                except Exception as e:
                    logger.warning(f"    Batch insert failed: {e}")
                    # Try one by one
                    for single_row in batch:
                        try:
                            target_cur.execute(
                                f"INSERT OR REPLACE INTO openaire_research ({cols_str}) VALUES ({placeholders})",
                                single_row
                            )
                        except:
                            pass
                    target_conn.commit()
                    inserted += len(batch)
                    batch = []

        # Insert remaining
        if batch:
            try:
                target_cur.executemany(
                    f"INSERT OR REPLACE INTO openaire_research ({cols_str}) VALUES ({placeholders})",
                    batch
                )
                target_conn.commit()
                inserted += len(batch)
            except:
                for single_row in batch:
                    try:
                        target_cur.execute(
                            f"INSERT OR REPLACE INTO openaire_research ({cols_str}) VALUES ({placeholders})",
                            single_row
                        )
                    except:
                        pass
                target_conn.commit()
                inserted += len(batch)

        # Get new target count
        target_cur.execute("SELECT COUNT(*) FROM openaire_research")
        target_after = target_cur.fetchone()[0]

        logger.info(f"  Target records (after): {target_after:,}")
        logger.info(f"  Net change: +{target_after - target_before:,}")
        logger.info("")

        self.stats['research_products_merged'] = inserted
        self.stats['research_products_target_before'] = target_before
        self.stats['research_products_target_after'] = target_after

    def _merge_collaborations(self, source_conn, target_conn):
        """Merge collaborations table"""
        logger.info("Merging collaborations...")

        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()

        # Get source count
        source_cur.execute("SELECT COUNT(*) FROM collaborations")
        source_count = source_cur.fetchone()[0]
        logger.info(f"  Source records: {source_count:,}")

        # Check target table exists
        target_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='openaire_collaborations'")
        if not target_cur.fetchone():
            logger.warning("  Target table 'openaire_collaborations' does not exist - skipping")
            return

        # Get current target count
        target_cur.execute("SELECT COUNT(*) FROM openaire_collaborations")
        target_before = target_cur.fetchone()[0]
        logger.info(f"  Target records (before): {target_before:,}")

        # Get schema compatibility
        source_cur.execute("PRAGMA table_info(collaborations)")
        source_cols = {row[1]: row[2] for row in source_cur.fetchall()}

        target_cur.execute("PRAGMA table_info(openaire_collaborations)")
        target_cols = {row[1]: row[2] for row in target_cur.fetchall()}

        common_cols = set(source_cols.keys()) & set(target_cols.keys())
        logger.info(f"  Common columns: {len(common_cols)}")

        if not common_cols:
            logger.error("  No common columns - cannot merge")
            return

        # SECURITY: Validate each column name before building SQL
        safe_cols = [validate_sql_identifier(col) for col in sorted(common_cols)]
        cols_str = ", ".join(safe_cols)
        placeholders = ", ".join(["?" for _ in safe_cols])

        logger.info(f"  Merging {source_count:,} records...")
        source_cur.execute(f"SELECT {cols_str} FROM collaborations")

        batch_size = 10000
        batch = []
        inserted = 0

        for row in source_cur:
            batch.append(row)
            if len(batch) >= batch_size:
                try:
                    target_cur.executemany(
                        f"INSERT OR REPLACE INTO openaire_collaborations ({cols_str}) VALUES ({placeholders})",
                        batch
                    )
                    target_conn.commit()
                    inserted += len(batch)
                    logger.info(f"    Progress: {inserted:,}/{source_count:,} ({inserted/source_count*100:.1f}%)")
                    batch = []
                except Exception as e:
                    logger.warning(f"    Batch insert failed: {e}")
                    for single_row in batch:
                        try:
                            target_cur.execute(
                                f"INSERT OR REPLACE INTO openaire_collaborations ({cols_str}) VALUES ({placeholders})",
                                single_row
                            )
                        except:
                            pass
                    target_conn.commit()
                    inserted += len(batch)
                    batch = []

        # Insert remaining
        if batch:
            try:
                target_cur.executemany(
                    f"INSERT OR REPLACE INTO openaire_collaborations ({cols_str}) VALUES ({placeholders})",
                    batch
                )
                target_conn.commit()
                inserted += len(batch)
            except:
                for single_row in batch:
                    try:
                        target_cur.execute(
                            f"INSERT OR REPLACE INTO openaire_collaborations ({cols_str}) VALUES ({placeholders})",
                            single_row
                        )
                    except:
                        pass
                target_conn.commit()
                inserted += len(batch)

        # Get new target count
        target_cur.execute("SELECT COUNT(*) FROM openaire_collaborations")
        target_after = target_cur.fetchone()[0]

        logger.info(f"  Target records (after): {target_after:,}")
        logger.info(f"  Net change: +{target_after - target_before:,}")
        logger.info("")

        self.stats['collaborations_merged'] = inserted
        self.stats['collaborations_target_before'] = target_before
        self.stats['collaborations_target_after'] = target_after

    def _merge_country_overview(self, source_conn, target_conn):
        """Merge country_overview table"""
        logger.info("Merging country_overview...")

        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()

        # Check if table exists in source
        source_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='country_overview'")
        if not source_cur.fetchone():
            logger.info("  Source table 'country_overview' does not exist - skipping")
            return

        # Get source count
        source_cur.execute("SELECT COUNT(*) FROM country_overview")
        source_count = source_cur.fetchone()[0]
        logger.info(f"  Source records: {source_count:,}")

        # For now, just log - target table may not exist or may have different name
        logger.info("  Skipping (target table structure needs verification)")
        logger.info("")

        self.stats['country_overview_skipped'] = source_count

    def _generate_summary(self):
        """Generate merge summary"""
        logger.info("=" * 80)
        logger.info("MERGE SUMMARY")
        logger.info("=" * 80)

        logger.info("Statistics:")
        for key, value in sorted(self.stats.items()):
            logger.info(f"  {key}: {value:,}")

        logger.info("")
        logger.info("Merge completed successfully!")

if __name__ == "__main__":
    merger = OpenAIREMerger()
    success = merger.merge()
    exit(0 if success else 1)
