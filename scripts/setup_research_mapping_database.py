#!/usr/bin/env python3
"""
Comprehensive Research Mapping Database - Setup Script

Creates the unified research database consolidating OpenAlex, OpenAIRE, and arXiv.

ZERO FABRICATION PROTOCOL:
- Create exact schema as documented
- Log all operations
- Verify table creation
- Report any errors immediately

Usage:
    python scripts/setup_research_mapping_database.py
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ResearchMappingDatabaseSetup:
    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/research_mapping_comprehensive.db")
        self.backup_dir = Path("F:/OSINT_WAREHOUSE/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Database path: {self.db_path}")
        logger.info(f"Backup directory: {self.backup_dir}")

    def create_database(self):
        """Create database with optimized settings"""
        logger.info("Creating database and setting performance parameters...")

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Performance optimizations
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-2000000")  # 2GB cache
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA mmap_size=30000000000")  # 30GB memory map

        logger.info("Performance parameters set successfully")

        return conn, cursor

    def create_schema(self, cursor):
        """Create all tables and indexes"""
        logger.info("Creating database schema...")

        # 1. Unified Publications Table
        logger.info("Creating unified_publications table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS unified_publications (
            unified_id INTEGER PRIMARY KEY AUTOINCREMENT,

            openalex_id TEXT,
            openaire_id TEXT,
            arxiv_id TEXT,
            doi TEXT,

            title TEXT NOT NULL,
            abstract TEXT,
            publication_year INTEGER,
            publication_date TEXT,
            language TEXT,

            result_type TEXT,

            source_system TEXT NOT NULL,
            is_primary_record BOOLEAN DEFAULT 1,
            duplicate_of INTEGER,

            is_open_access BOOLEAN,
            oa_status TEXT,
            oa_url TEXT,

            cited_by_count INTEGER,
            citation_percentile REAL,

            processing_date TEXT,
            last_updated TEXT,
            raw_data_json TEXT,

            UNIQUE(openalex_id),
            UNIQUE(openaire_id),
            UNIQUE(arxiv_id)
        )
        """)

        # 2. Authors Table
        logger.info("Creating research_authors table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_authors (
            author_id INTEGER PRIMARY KEY AUTOINCREMENT,

            display_name TEXT NOT NULL,
            orcid TEXT,
            openalex_author_id TEXT,

            works_count INTEGER,
            cited_by_count INTEGER,
            h_index INTEGER,

            first_seen TEXT,
            last_updated TEXT,

            UNIQUE(orcid),
            UNIQUE(openalex_author_id)
        )
        """)

        # 3. Publication-Author Junction
        logger.info("Creating publication_authors table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS publication_authors (
            pub_author_id INTEGER PRIMARY KEY AUTOINCREMENT,
            unified_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,

            author_position TEXT,
            is_corresponding BOOLEAN,
            raw_author_name TEXT,

            FOREIGN KEY (unified_id) REFERENCES unified_publications(unified_id),
            FOREIGN KEY (author_id) REFERENCES research_authors(author_id),
            UNIQUE(unified_id, author_id)
        )
        """)

        # 4. Institutions Table
        logger.info("Creating research_institutions table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_institutions (
            institution_id INTEGER PRIMARY KEY AUTOINCREMENT,

            display_name TEXT NOT NULL,
            ror_id TEXT,
            openalex_inst_id TEXT,
            grid_id TEXT,

            country_code TEXT,
            country_name TEXT,
            city TEXT,
            region TEXT,

            institution_type TEXT,

            works_count INTEGER,
            cited_by_count INTEGER,

            first_seen TEXT,
            last_updated TEXT,

            UNIQUE(ror_id),
            UNIQUE(openalex_inst_id)
        )
        """)

        # 5. Publication-Institution Junction
        logger.info("Creating publication_institutions table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS publication_institutions (
            pub_inst_id INTEGER PRIMARY KEY AUTOINCREMENT,
            unified_id INTEGER NOT NULL,
            institution_id INTEGER NOT NULL,
            author_id INTEGER,

            raw_affiliation_string TEXT,

            FOREIGN KEY (unified_id) REFERENCES unified_publications(unified_id),
            FOREIGN KEY (institution_id) REFERENCES research_institutions(institution_id),
            FOREIGN KEY (author_id) REFERENCES research_authors(author_id),
            UNIQUE(unified_id, institution_id, author_id)
        )
        """)

        # 6. Topics and Keywords
        logger.info("Creating research_topics table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_topics (
            topic_id INTEGER PRIMARY KEY AUTOINCREMENT,

            topic_name TEXT NOT NULL UNIQUE,
            topic_type TEXT,

            parent_topic_id INTEGER,
            topic_level INTEGER,

            openalex_topic_id TEXT,
            arxiv_category TEXT,

            description TEXT,

            FOREIGN KEY (parent_topic_id) REFERENCES research_topics(topic_id)
        )
        """)

        # 7. Publication-Topic Junction
        logger.info("Creating publication_topics table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS publication_topics (
            pub_topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
            unified_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,

            score REAL,
            is_primary BOOLEAN,

            FOREIGN KEY (unified_id) REFERENCES unified_publications(unified_id),
            FOREIGN KEY (topic_id) REFERENCES research_topics(topic_id),
            UNIQUE(unified_id, topic_id)
        )
        """)

        # 8. Technology Classifications
        logger.info("Creating technology_classifications table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS technology_classifications (
            tech_id INTEGER PRIMARY KEY AUTOINCREMENT,
            unified_id INTEGER NOT NULL,

            domain_name TEXT NOT NULL,

            detection_method TEXT,
            confidence_score REAL,
            keywords_matched TEXT,

            classified_date TEXT,

            FOREIGN KEY (unified_id) REFERENCES unified_publications(unified_id)
        )
        """)

        # 9. Collaborations Tracking
        logger.info("Creating research_collaborations table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_collaborations (
            collab_id INTEGER PRIMARY KEY AUTOINCREMENT,
            unified_id INTEGER NOT NULL,

            collaboration_type TEXT,

            country_codes TEXT,
            country_count INTEGER,

            institution_ids TEXT,
            institution_count INTEGER,

            has_china_author BOOLEAN,
            has_china_institution BOOLEAN,
            china_institution_names TEXT,

            detected_date TEXT,

            FOREIGN KEY (unified_id) REFERENCES unified_publications(unified_id)
        )
        """)

        # 10. Cross-Reference Map
        logger.info("Creating cross_reference_map table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cross_reference_map (
            xref_id INTEGER PRIMARY KEY AUTOINCREMENT,

            primary_unified_id INTEGER NOT NULL,

            openalex_id TEXT,
            openaire_id TEXT,
            arxiv_id TEXT,
            doi TEXT,

            match_confidence REAL,
            match_method TEXT,
            match_date TEXT,

            FOREIGN KEY (primary_unified_id) REFERENCES unified_publications(unified_id)
        )
        """)

        # 11. Processing Status
        logger.info("Creating processing_status table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS processing_status (
            status_id INTEGER PRIMARY KEY AUTOINCREMENT,

            source_system TEXT NOT NULL,
            source_file TEXT,
            source_date TEXT,

            status TEXT,
            records_processed INTEGER,
            records_inserted INTEGER,
            records_skipped INTEGER,
            duplicates_found INTEGER,

            started_at TEXT,
            completed_at TEXT,
            processing_duration_seconds INTEGER,

            error_message TEXT,
            retry_count INTEGER DEFAULT 0,

            UNIQUE(source_system, source_file)
        )
        """)

        # 12. Funders Table
        logger.info("Creating research_funders table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_funders (
            funder_id INTEGER PRIMARY KEY AUTOINCREMENT,

            display_name TEXT NOT NULL,
            openalex_funder_id TEXT,
            ror_id TEXT,
            doi TEXT,

            country_code TEXT,

            funder_type TEXT,

            works_funded INTEGER,

            UNIQUE(openalex_funder_id)
        )
        """)

        # 13. Publication-Funder Junction
        logger.info("Creating publication_funders table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS publication_funders (
            pub_funder_id INTEGER PRIMARY KEY AUTOINCREMENT,
            unified_id INTEGER NOT NULL,
            funder_id INTEGER NOT NULL,

            award_id TEXT,

            FOREIGN KEY (unified_id) REFERENCES unified_publications(unified_id),
            FOREIGN KEY (funder_id) REFERENCES research_funders(funder_id),
            UNIQUE(unified_id, funder_id, award_id)
        )
        """)

        logger.info("All tables created successfully")

    def create_indexes(self, cursor):
        """Create indexes for query performance (run AFTER bulk loading)"""
        logger.info("Creating indexes (this may take a while)...")

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

        for index_name, table_name, column_name in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})")
                logger.info(f"Created index: {index_name}")
            except Exception as e:
                logger.error(f"Error creating index {index_name}: {e}")

        logger.info("All indexes created successfully")

    def verify_schema(self, cursor):
        """Verify all tables and indexes were created"""
        logger.info("Verifying schema...")

        # Count tables
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        table_count = cursor.fetchone()[0]
        logger.info(f"Tables created: {table_count}/13")

        # Count indexes
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
        index_count = cursor.fetchone()[0]
        logger.info(f"Indexes created: {index_count}")

        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"Tables: {', '.join(tables)}")

        if table_count == 13:
            logger.info("✓ Schema verification PASSED")
            return True
        else:
            logger.error("✗ Schema verification FAILED - missing tables")
            return False

    def create_setup_log(self):
        """Create log of database setup"""
        log_path = self.backup_dir / f"setup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(log_path, 'w') as f:
            f.write("Research Mapping Database Setup Log\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Database: {self.db_path}\n")
            f.write(f"Setup Time: {datetime.now().isoformat()}\n")
            f.write(f"Schema Version: 1.0\n\n")
            f.write("Status: Database created successfully\n")
            f.write("Ready for data ingestion\n")

        logger.info(f"Setup log written to: {log_path}")

    def run(self, create_indexes_now=False):
        """Execute complete database setup"""
        logger.info("=" * 80)
        logger.info("COMPREHENSIVE RESEARCH MAPPING DATABASE - SETUP")
        logger.info("=" * 80)

        try:
            # Create database
            conn, cursor = self.create_database()

            # Create schema
            self.create_schema(cursor)

            # Create indexes (optional - can defer until after bulk loading)
            if create_indexes_now:
                self.create_indexes(cursor)
                logger.info("Note: Indexes created now. This is optimal for small datasets.")
            else:
                logger.info("Note: Indexes NOT created yet. Run create_indexes() after bulk loading for better performance.")

            # Commit changes
            conn.commit()

            # Verify
            success = self.verify_schema(cursor)

            # Close connection
            conn.close()

            if success:
                # Create log
                self.create_setup_log()

                logger.info("=" * 80)
                logger.info("DATABASE SETUP COMPLETE")
                logger.info("=" * 80)
                logger.info(f"Database location: {self.db_path}")
                logger.info(f"Database size: {self.db_path.stat().st_size / (1024*1024):.2f} MB")
                logger.info("Ready for data ingestion")
                logger.info("Next steps:")
                logger.info("  1. Run OpenAlex ingestion: python scripts/ingest_openalex.py")
                logger.info("  2. Run arXiv ingestion: python scripts/ingest_arxiv.py")
                logger.info("  3. Run OpenAIRE ingestion: python scripts/ingest_openaire.py")
                logger.info("  4. Create indexes: python scripts/create_research_db_indexes.py")

                return True
            else:
                logger.error("Database setup FAILED - see errors above")
                return False

        except Exception as e:
            logger.error(f"Fatal error during setup: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main execution"""
    setup = ResearchMappingDatabaseSetup()

    # Create database WITHOUT indexes initially (faster bulk loading)
    # Run with create_indexes_now=True only for testing with small datasets
    success = setup.run(create_indexes_now=False)

    if success:
        print("\n✓ Database setup completed successfully")
        print(f"✓ Database ready at: {setup.db_path}")
    else:
        print("\n✗ Database setup failed - check logs above")
        exit(1)


if __name__ == "__main__":
    main()
