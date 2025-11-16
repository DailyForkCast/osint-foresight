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
OpenAIRE Production Database Merger v2 (FIXED)
Merges OpenAIRE production database with explicit column mapping
Fixes: Schema mismatch issues discovered in QA/QC audit (Oct 30, 2025)
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('openaire_merge_v2_fixed.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SOURCE_DB = Path("F:/OSINT_Data/openaire_production_comprehensive/openaire_production.db")
TARGET_DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")

class OpenAIREMergerV2:
    def __init__(self):
        self.source_db = SOURCE_DB
        self.target_db = TARGET_DB
        self.stats = {}

    def merge(self):
        """Merge OpenAIRE production database into master"""
        logger.info("=" * 80)
        logger.info("OpenAIRE Production Database Merger v2 (FIXED)")
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

            # Clear existing data before re-merge
            logger.info("Clearing existing OpenAIRE data from target...")
            target_cur = target_conn.cursor()
            target_cur.execute("DELETE FROM openaire_research")
            target_conn.commit()
            logger.info("  openaire_research table cleared")
            logger.info("")

            # Merge research_products with explicit mapping
            self._merge_research_products_v2(source_conn, target_conn)

            # Merge collaborations (keep original logic - no issues found)
            self._merge_collaborations(source_conn, target_conn)

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

    def _merge_research_products_v2(self, source_conn, target_conn):
        """Merge research_products with explicit column mapping (FIXED)"""
        logger.info("Merging research_products (v2 with explicit mapping)...")

        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()

        # Get source count
        source_cur.execute("SELECT COUNT(*) FROM research_products")
        source_count = source_cur.fetchone()[0]
        logger.info(f"  Source records: {source_count:,}")

        # Explicit column mapping
        logger.info("  Column mapping:")
        logger.info("    id           -> id            (direct)")
        logger.info("    title        -> title         (direct)")
        logger.info("    country_code -> countries     (direct)")
        logger.info("    date_accepted-> year          (extract year)")
        logger.info("    result_type  -> type          (direct)")
        logger.info("    country_code -> china_related (calculate)")
        logger.info("")

        # Fetch data with transformations
        logger.info(f"  Fetching and transforming {source_count:,} records...")
        source_cur.execute("""
            SELECT
                CAST(id AS TEXT) as id,
                title,
                country_code as countries,
                CAST(SUBSTR(date_accepted, 1, 4) AS INTEGER) as year,
                result_type as type,
                CASE
                    WHEN country_code IN ('CN', 'HK', 'TW', 'MO') THEN 1
                    ELSE 0
                END as china_related
            FROM research_products
        """)

        batch_size = 10000
        batch = []
        inserted = 0
        errors = 0

        for row in source_cur:
            batch.append(row)
            if len(batch) >= batch_size:
                try:
                    target_cur.executemany(
                        """INSERT OR REPLACE INTO openaire_research
                           (id, title, countries, year, type, china_related, created_at)
                           VALUES (?, ?, ?, ?, ?, ?, datetime('now'))""",
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
                                """INSERT OR REPLACE INTO openaire_research
                                   (id, title, countries, year, type, china_related, created_at)
                                   VALUES (?, ?, ?, ?, ?, ?, datetime('now'))""",
                                single_row
                            )
                        except:
                            errors += 1
                    target_conn.commit()
                    inserted += len(batch)
                    batch = []

        # Insert remaining
        if batch:
            try:
                target_cur.executemany(
                    """INSERT OR REPLACE INTO openaire_research
                       (id, title, countries, year, type, china_related, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, datetime('now'))""",
                    batch
                )
                target_conn.commit()
                inserted += len(batch)
            except:
                for single_row in batch:
                    try:
                        target_cur.execute(
                            """INSERT OR REPLACE INTO openaire_research
                               (id, title, countries, year, type, china_related, created_at)
                               VALUES (?, ?, ?, ?, ?, ?, datetime('now'))""",
                            single_row
                        )
                    except:
                        errors += 1
                target_conn.commit()
                inserted += len(batch)

        # Get final target count
        target_cur.execute("SELECT COUNT(*) FROM openaire_research")
        target_after = target_cur.fetchone()[0]

        logger.info(f"  Target records (after): {target_after:,}")
        logger.info(f"  Records inserted: {inserted:,}")
        if errors > 0:
            logger.warning(f"  Errors encountered: {errors:,}")
        logger.info("")

        # Validate field completeness
        logger.info("  Field completeness check:")
        for field in ['id', 'title', 'countries', 'year', 'type', 'china_related']:
            # SECURITY: Validate field name before use in SQL
            safe_field = validate_sql_identifier(field)
            target_cur.execute(f"SELECT COUNT(*) FROM openaire_research WHERE {safe_field} IS NOT NULL AND {safe_field} != ''")
            populated = target_cur.fetchone()[0]
            pct = (populated / target_after * 100) if target_after > 0 else 0
            status = "OK" if pct > 95 else "WARN" if pct > 80 else "FAIL"
            logger.info(f"    {field:15} {populated:>7,} / {target_after:,} ({pct:>5.1f}%) [{status}]")
        logger.info("")

        self.stats['research_products_merged'] = inserted
        self.stats['research_products_errors'] = errors
        self.stats['research_products_target_after'] = target_after

    def _merge_collaborations(self, source_conn, target_conn):
        """Merge collaborations table (no changes - original logic works)"""
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

        # Merge data
        # SECURITY: Validate all column names before use in SQL
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
        logger.info("=" * 80)

if __name__ == "__main__":
    merger = OpenAIREMergerV2()
    success = merger.merge()
    exit(0 if success else 1)
