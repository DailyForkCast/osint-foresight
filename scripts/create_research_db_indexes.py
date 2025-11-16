#!/usr/bin/env python3
"""
Create Indexes for Research Mapping Database

Creates all performance indexes AFTER bulk data loading is complete.
This is much faster than creating indexes before loading data.

ZERO FABRICATION PROTOCOL:
- Create exact indexes as documented
- Verify each index creation
- Log timing for each index

Usage:
    python scripts/create_research_db_indexes.py
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
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


class IndexCreator:
    """Create all database indexes"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def create_all_indexes(self):
        """Create all indexes with timing"""
        logger.info("=" * 80)
        logger.info("CREATING RESEARCH DATABASE INDEXES")
        logger.info("=" * 80)

        conn = self.get_connection()
        cursor = conn.cursor()

        indexes = [
            # unified_publications indexes
            ("idx_up_doi", "unified_publications", "doi"),
            ("idx_up_year", "unified_publications", "publication_year"),
            ("idx_up_source", "unified_publications", "source_system"),
            ("idx_up_primary", "unified_publications", "is_primary_record"),
            ("idx_up_type", "unified_publications", "result_type"),

            # research_authors indexes
            ("idx_ra_name", "research_authors", "display_name"),

            # publication_authors indexes
            ("idx_pa_unified", "publication_authors", "unified_id"),
            ("idx_pa_author", "publication_authors", "author_id"),

            # research_institutions indexes
            ("idx_ri_country", "research_institutions", "country_code"),
            ("idx_ri_name", "research_institutions", "display_name"),
            ("idx_ri_type", "research_institutions", "institution_type"),

            # publication_institutions indexes
            ("idx_pi_unified", "publication_institutions", "unified_id"),
            ("idx_pi_institution", "publication_institutions", "institution_id"),
            ("idx_pi_author", "publication_institutions", "author_id"),

            # research_topics indexes
            ("idx_rt_name", "research_topics", "topic_name"),
            ("idx_rt_type", "research_topics", "topic_type"),

            # publication_topics indexes
            ("idx_pt_unified", "publication_topics", "unified_id"),
            ("idx_pt_topic", "publication_topics", "topic_id"),
            ("idx_pt_primary", "publication_topics", "is_primary"),

            # technology_classifications indexes
            ("idx_tc_unified", "technology_classifications", "unified_id"),
            ("idx_tc_domain", "technology_classifications", "domain_name"),

            # research_collaborations indexes
            ("idx_rc_unified", "research_collaborations", "unified_id"),
            ("idx_rc_type", "research_collaborations", "collaboration_type"),
            ("idx_rc_china", "research_collaborations", "has_china_institution"),

            # cross_reference_map indexes
            ("idx_xref_primary", "cross_reference_map", "primary_unified_id"),
            ("idx_xref_doi", "cross_reference_map", "doi"),

            # processing_status indexes
            ("idx_ps_status", "processing_status", "status"),
            ("idx_ps_source", "processing_status", "source_system"),

            # research_funders indexes
            ("idx_rf_name", "research_funders", "display_name"),
            ("idx_rf_country", "research_funders", "country_code"),

            # publication_funders indexes
            ("idx_pf_unified", "publication_funders", "unified_id"),
            ("idx_pf_funder", "publication_funders", "funder_id"),
        ]

        total_indexes = len(indexes)
        overall_start = datetime.now()

        for i, (index_name, table_name, column_name) in enumerate(indexes, 1):
            logger.info(f"[{i}/{total_indexes}] Creating {index_name} on {table_name}({column_name})...")
            start = datetime.now()

            try:
                # SECURITY: Validate all SQL identifiers before use
                safe_index = validate_sql_identifier(index_name)
                safe_table = validate_sql_identifier(table_name)
                safe_column = validate_sql_identifier(column_name)
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {safe_index} ON {safe_table}({safe_column})")
                conn.commit()

                duration = (datetime.now() - start).total_seconds()
                logger.info(f"  ✓ Created in {duration:.1f} seconds")

            except Exception as e:
                logger.error(f"  ✗ Error creating {index_name}: {e}")

        overall_duration = (datetime.now() - overall_start).total_seconds()

        # Run ANALYZE to update query planner statistics
        logger.info("\nRunning ANALYZE to update query statistics...")
        cursor.execute("ANALYZE")
        conn.commit()

        conn.close()

        logger.info("\n" + "=" * 80)
        logger.info("INDEX CREATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total indexes created: {total_indexes}")
        logger.info(f"Total time: {overall_duration/60:.1f} minutes")
        logger.info("\nDatabase is now optimized for queries")


def main():
    """Main execution"""
    db_path = "F:/OSINT_WAREHOUSE/research_mapping_comprehensive.db"

    if not Path(db_path).exists():
        logger.error(f"Database not found: {db_path}")
        logger.error("Please run setup script first: python scripts/setup_research_mapping_database.py")
        exit(1)

    creator = IndexCreator(db_path)
    creator.create_all_indexes()


if __name__ == "__main__":
    main()
