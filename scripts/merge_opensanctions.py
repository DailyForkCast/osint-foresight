#!/usr/bin/env python3
"""
OpenSanctions Database Merger
Merges OpenSanctions database (183K+ entities) into master database
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
        logging.FileHandler('opensanctions_merge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SOURCE_DB = Path("F:/OSINT_Data/OpenSanctions/processed/sanctions.db")
TARGET_DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")

class OpenSanctionsMerger:
    def __init__(self):
        self.source_db = SOURCE_DB
        self.target_db = TARGET_DB
        self.stats = {}

    def merge(self):
        """Merge OpenSanctions database into master"""
        logger.info("=" * 80)
        logger.info("OpenSanctions Database Merger")
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

            # Merge entities table
            self._merge_entities(source_conn, target_conn)

            # Merge chinese_analysis if it has data
            if self.stats.get('source_chinese_analysis', 0) > 0:
                self._merge_chinese_analysis(source_conn, target_conn)

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

    def _merge_entities(self, source_conn, target_conn):
        """Merge entities table"""
        logger.info("Merging entities...")

        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()

        # Get source count
        source_cur.execute("SELECT COUNT(*) FROM entities")
        source_count = source_cur.fetchone()[0]
        logger.info(f"  Source records: {source_count:,}")

        # Check target table exists
        target_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='opensanctions_entities'")
        if not target_cur.fetchone():
            logger.warning("  Target table 'opensanctions_entities' does not exist - skipping")
            return

        # Get current target count
        target_cur.execute("SELECT COUNT(*) FROM opensanctions_entities")
        target_before = target_cur.fetchone()[0]
        logger.info(f"  Target records (before): {target_before:,}")

        # Get schema compatibility
        source_cur.execute("PRAGMA table_info(entities)")
        source_cols = {row[1]: row[2] for row in source_cur.fetchall()}

        target_cur.execute("PRAGMA table_info(opensanctions_entities)")
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
        source_cur.execute(f"SELECT {cols_str} FROM entities")

        batch_size = 10000
        batch = []
        inserted = 0

        for row in source_cur:
            batch.append(row)
            if len(batch) >= batch_size:
                try:
                    target_cur.executemany(
                        f"INSERT OR REPLACE INTO opensanctions_entities ({cols_str}) VALUES ({placeholders})",
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
                                f"INSERT OR REPLACE INTO opensanctions_entities ({cols_str}) VALUES ({placeholders})",
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
                    f"INSERT OR REPLACE INTO opensanctions_entities ({cols_str}) VALUES ({placeholders})",
                    batch
                )
                target_conn.commit()
                inserted += len(batch)
            except:
                for single_row in batch:
                    try:
                        target_cur.execute(
                            f"INSERT OR REPLACE INTO opensanctions_entities ({cols_str}) VALUES ({placeholders})",
                            single_row
                        )
                    except:
                        pass
                target_conn.commit()
                inserted += len(batch)

        # Get new target count
        target_cur.execute("SELECT COUNT(*) FROM opensanctions_entities")
        target_after = target_cur.fetchone()[0]

        logger.info(f"  Target records (after): {target_after:,}")
        logger.info(f"  Net change: +{target_after - target_before:,}")
        logger.info("")

        self.stats['entities_merged'] = inserted
        self.stats['entities_target_before'] = target_before
        self.stats['entities_target_after'] = target_after

    def _merge_chinese_analysis(self, source_conn, target_conn):
        """Merge chinese_analysis table if target exists"""
        logger.info("Merging chinese_analysis...")

        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()

        # Get source count
        source_cur.execute("SELECT COUNT(*) FROM chinese_analysis")
        source_count = source_cur.fetchone()[0]
        logger.info(f"  Source records: {source_count:,}")

        # Check if target table exists
        target_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='opensanctions_chinese_analysis'")
        if not target_cur.fetchone():
            logger.info("  Target table 'opensanctions_chinese_analysis' does not exist - skipping")
            logger.info("")
            self.stats['chinese_analysis_skipped'] = source_count
            return

        # Get schema and merge (similar pattern)
        logger.info("  Target table exists - merging...")
        source_cur.execute("PRAGMA table_info(chinese_analysis)")
        source_cols = {row[1]: row[2] for row in source_cur.fetchall()}

        target_cur.execute("PRAGMA table_info(opensanctions_chinese_analysis)")
        target_cols = {row[1]: row[2] for row in target_cur.fetchall()}

        common_cols = set(source_cols.keys()) & set(target_cols.keys())
        logger.info(f"  Common columns: {len(common_cols)}")

        if not common_cols:
            logger.warning("  No common columns - skipping")
            logger.info("")
            return

        # SECURITY: Validate each column name before building SQL
        safe_cols = [validate_sql_identifier(col) for col in sorted(common_cols)]
        cols_str = ", ".join(safe_cols)
        placeholders = ", ".join(["?" for _ in safe_cols])

        source_cur.execute(f"SELECT {cols_str} FROM chinese_analysis")
        rows = source_cur.fetchall()

        try:
            target_cur.executemany(
                f"INSERT OR REPLACE INTO opensanctions_chinese_analysis ({cols_str}) VALUES ({placeholders})",
                rows
            )
            target_conn.commit()
            logger.info(f"  Merged {len(rows):,} records")
            self.stats['chinese_analysis_merged'] = len(rows)
        except Exception as e:
            logger.warning(f"  Merge failed: {e}")
            self.stats['chinese_analysis_failed'] = True

        logger.info("")

    def _generate_summary(self):
        """Generate merge summary"""
        logger.info("=" * 80)
        logger.info("MERGE SUMMARY")
        logger.info("=" * 80)

        logger.info("Statistics:")
        for key, value in sorted(self.stats.items()):
            if isinstance(value, bool):
                logger.info(f"  {key}: {value}")
            else:
                logger.info(f"  {key}: {value:,}")

        logger.info("")
        logger.info("Merge completed successfully!")

if __name__ == "__main__":
    merger = OpenSanctionsMerger()
    success = merger.merge()
    exit(0 if success else 1)
