#!/usr/bin/env python3
"""
Create Performance Indexes - CORRECTED VERSION
Fixes the 5 failed indexes from initial attempt
Date: October 30, 2025
"""

import sqlite3
import time
import logging
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

def create_indexes():
    """Create corrected performance indexes"""
    logger.info("=" * 80)
    logger.info("CREATING CORRECTED PERFORMANCE INDEXES")
    logger.info("=" * 80)
    logger.info("")

    conn = sqlite3.connect(DB_PATH, timeout=120)
    cur = conn.cursor()

    # Corrected index definitions
    indexes = [
        # OpenAIRE indexes (CORRECTED)
        ('idx_openaire_research_id', 'openaire_research', 'id', 'Research product ID lookup'),
        ('idx_openaire_research_year', 'openaire_research', 'year', 'Temporal analysis'),
        ('idx_openaire_research_country', 'openaire_research', 'countries', 'Country-based analysis'),
        ('idx_openaire_research_china', 'openaire_research', 'china_related', 'China detection queries'),
        ('idx_openaire_collab_primary', 'openaire_collaborations', 'primary_country', 'Primary country queries'),
        ('idx_openaire_collab_partner', 'openaire_collaborations', 'partner_country', 'Partner country queries'),
        ('idx_openaire_collab_china', 'openaire_collaborations', 'is_china_collaboration', 'China collaboration queries'),

        # GLEIF indexes (CORRECTED)
        ('idx_gleif_rel_child', 'gleif_relationships', 'child_lei', 'Child entity lookup'),
        ('idx_gleif_rel_parent', 'gleif_relationships', 'parent_lei', 'Parent entity lookup'),
        ('idx_gleif_rel_type', 'gleif_relationships', 'relationship_type', 'Relationship type filtering'),
    ]

    created = 0
    skipped = 0
    failed = 0
    failed_list = []

    for idx_name, table, column, description in indexes:
        try:
            # SECURITY: Validate all SQL identifiers before use
            safe_idx = validate_sql_identifier(idx_name)
            safe_table = validate_sql_identifier(table)
            safe_column = validate_sql_identifier(column)

            logger.info(f"Creating {idx_name}...")
            logger.info(f"  Table: {table}")
            logger.info(f"  Column: {column}")
            logger.info(f"  Purpose: {description}")

            # Check if index already exists - use parameterized query for name value
            cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND name=?", (safe_idx,))
            if cur.fetchone():
                logger.info(f"  Status: SKIPPED (already exists)")
                skipped += 1
            else:
                start = time.time()
                cur.execute(f"CREATE INDEX {safe_idx} ON {safe_table}({safe_column})")
                conn.commit()
                elapsed = time.time() - start

                logger.info(f"  Status: CREATED ({elapsed:.2f}s)")
                created += 1

            logger.info("")

        except Exception as e:
            logger.error(f"  Status: FAILED - {str(e)}")
            logger.error("")
            failed += 1
            failed_list.append((idx_name, str(e)))

    # Run ANALYZE to update query planner statistics
    logger.info("Running ANALYZE to update query planner statistics...")
    try:
        cur.execute("ANALYZE")
        conn.commit()
        logger.info("ANALYZE complete!")
    except Exception as e:
        logger.error(f"ANALYZE failed: {e}")

    conn.close()

    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("INDEX CREATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Created: {created}")
    logger.info(f"Skipped: {skipped}")
    logger.info(f"Failed: {failed}")
    logger.info("")

    if failed_list:
        logger.error("Failed indexes:")
        for idx_name, error in failed_list:
            logger.error(f"  - {idx_name}: {error[:80]}")
        logger.info("")

    if failed == 0:
        logger.info("✅ ALL INDEXES CREATED SUCCESSFULLY!")
    else:
        logger.warning(f"⚠️ {failed} indexes failed to create")

    logger.info("")
    logger.info("=" * 80)

    return failed == 0

if __name__ == "__main__":
    success = create_indexes()
    exit(0 if success else 1)
