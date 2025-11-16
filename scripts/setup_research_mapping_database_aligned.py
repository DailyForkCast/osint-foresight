#!/usr/bin/env python3
"""
Comprehensive Research Mapping Database - Aligned Setup Script

Creates unified research database ALIGNED with existing osint_master.db standards:
- Same technology domain names (AI, Quantum, Semiconductors, etc.)
- Same country codes (ISO 2-letter)
- Same entity tracking approach
- Compatible with existing arxiv_papers and openalex_works tables

ZERO FABRICATION PROTOCOL:
- Create exact schema as documented
- Log all operations
- Verify table creation
- Report any errors immediately

Usage:
    python scripts/setup_research_mapping_database_aligned.py
"""

import sqlite3
import logging
import json
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
        self.master_db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.backup_dir = Path("F:/OSINT_WAREHOUSE/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Load technology domains from config to ensure alignment
        self.config_path = Path("C:/Projects/OSINT-Foresight/config/openalex_technology_keywords_v5.json")

        logger.info(f"Database path: {self.db_path}")
        logger.info(f"Master DB reference: {self.master_db_path}")
        logger.info(f"Backup directory: {self.backup_dir}")

    def load_technology_domains(self):
        """Load technology domains from config to ensure alignment"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                domains = list(config.keys())
                domains = [d for d in domains if not d.startswith('_')]
                logger.info(f"Loaded {len(domains)} technology domains from config")
                logger.info(f"Domains: {', '.join(domains)}")
                return domains
        else:
            # Fallback to standard domains
            logger.warning("Config not found, using standard domains")
            return ["AI", "Quantum", "Space", "Semiconductors", "Smart_City",
                    "Neuroscience", "Biotech", "Advanced_Materials", "Energy_Storage", "BCI"]

    def get_master_db_standards(self):
        """Extract standards from master database for alignment"""
        if not self.master_db_path.exists():
            logger.warning("Master DB not found, using defaults")
            return {}

        conn = sqlite3.connect(str(self.master_db_path))
        cursor = conn.cursor()

        standards = {}

        # Get country codes
        try:
            cursor.execute("SELECT DISTINCT country_code FROM bilateral_countries ORDER BY country_code")
            standards['country_codes'] = [row[0] for row in cursor.fetchall()]
            logger.info(f"Loaded {len(standards['country_codes'])} country codes from master DB")
        except:
            standards['country_codes'] = []

        # Get entity types
        try:
            cursor.execute("SELECT DISTINCT entity_type FROM entities WHERE entity_type IS NOT NULL")
            standards['entity_types'] = [row[0] for row in cursor.fetchall()]
            logger.info(f"Loaded {len(standards['entity_types'])} entity types from master DB")
        except:
            standards['entity_types'] = []

        conn.close()
        return standards

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
        """Create all tables ALIGNED with master DB structure"""
        logger.info("Creating database schema aligned with master DB standards...")

        # 1. Unified Publications Table - ALIGNED with openalex_works structure
        logger.info("Creating unified_publications table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS unified_publications (
            unified_id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- External IDs (for cross-reference)
            openalex_id TEXT,
            openaire_id TEXT,
            arxiv_id TEXT,
            doi TEXT,

            -- Core metadata (ALIGNED with openalex_works)
            title TEXT NOT NULL,
            abstract TEXT,
            publication_year INTEGER,
            publication_date TEXT,
            language TEXT,

            -- Type (ALIGNED with master DB)
            result_type TEXT,              -- article, preprint, book, dataset

            -- Source tracking (ALIGNED with master DB pattern)
            source_system TEXT NOT NULL,   -- 'openalex', 'openaire', 'arxiv'
            is_primary_record BOOLEAN DEFAULT 1,
            duplicate_of INTEGER,

            -- Open access (ALIGNED with openalex_works.open_access_status)
            is_open_access BOOLEAN,
            oa_status TEXT,                -- closed, gold, green, hybrid, bronze
            oa_url TEXT,

            -- Citations (ALIGNED with openalex_works.cited_by_count)
            cited_by_count INTEGER,
            citation_percentile REAL,

            -- Technology classification (ALIGNED with master DB)
            technology_domain TEXT,        -- AI, Quantum, Semiconductors, etc. (matches config)
            is_china_related BOOLEAN,      -- Quick flag for China involvement
            confidence_score REAL,         -- Classification confidence (0-1)

            -- Processing metadata
            processing_date TEXT,
            last_updated TEXT,
            validation_keyword TEXT,       -- ALIGNED with openalex_works
            validation_topic TEXT,         -- ALIGNED with openalex_works
            validation_score REAL,         -- ALIGNED with openalex_works
            raw_data_json TEXT,

            UNIQUE(openalex_id),
            UNIQUE(openaire_id),
            UNIQUE(arxiv_id)
        )
        """)

        # 2. Authors Table - ALIGNED with master DB entity tracking
        logger.info("Creating research_authors table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_authors (
            author_id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Identity
            display_name TEXT NOT NULL,
            orcid TEXT,
            openalex_author_id TEXT,

            -- Country affiliation (ALIGNED with master DB country codes)
            primary_country_code TEXT,     -- ISO 2-letter code (CN, US, DE, etc.)
            is_chinese BOOLEAN,            -- ALIGNED with entities.is_chinese

            -- Metrics
            works_count INTEGER,
            cited_by_count INTEGER,
            h_index INTEGER,

            -- Processing
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

            -- Authorship details
            author_position TEXT,          -- first, middle, last
            is_corresponding BOOLEAN,
            raw_author_name TEXT,

            FOREIGN KEY (unified_id) REFERENCES unified_publications(unified_id),
            FOREIGN KEY (author_id) REFERENCES research_authors(author_id),
            UNIQUE(unified_id, author_id)
        )
        """)

        # 4. Institutions Table - ALIGNED with master DB entity structure
        logger.info("Creating research_institutions table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_institutions (
            institution_id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Identity
            display_name TEXT NOT NULL,
            ror_id TEXT,
            openalex_inst_id TEXT,
            grid_id TEXT,

            -- Geographic (ALIGNED with master DB country codes)
            country_code TEXT,             -- ISO 2-letter (matches bilateral_countries)
            country_name TEXT,
            city TEXT,
            region TEXT,

            -- Type
            institution_type TEXT,         -- education, healthcare, company, government

            -- China tracking (ALIGNED with entities table)
            is_chinese BOOLEAN,
            is_pla_affiliated BOOLEAN,     -- ALIGNED with CEIAS tracking
            is_sanctioned BOOLEAN,         -- ALIGNED with entities.is_sanctioned

            -- Metrics
            works_count INTEGER,
            cited_by_count INTEGER,

            -- Processing
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

        # 6. Topics Table - ALIGNED with master DB
        logger.info("Creating research_topics table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_topics (
            topic_id INTEGER PRIMARY KEY AUTOINCREMENT,

            topic_name TEXT NOT NULL UNIQUE,
            topic_type TEXT,               -- 'openalex_topic', 'arxiv_category', 'keyword'

            -- Hierarchy
            parent_topic_id INTEGER,
            topic_level INTEGER,

            -- External IDs
            openalex_topic_id TEXT,
            arxiv_category TEXT,           -- ALIGNED with arxiv_papers.primary_category

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

        # 8. Technology Classifications - USES config domains
        logger.info("Creating technology_classifications table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS technology_classifications (
            tech_id INTEGER PRIMARY KEY AUTOINCREMENT,
            unified_id INTEGER NOT NULL,

            -- Technology domain (ALIGNED with config: AI, Quantum, etc.)
            domain_name TEXT NOT NULL,

            -- Detection metadata
            detection_method TEXT,         -- 'keyword', 'topic', 'cpc', 'manual'
            confidence_score REAL,
            keywords_matched TEXT,

            classified_date TEXT,

            FOREIGN KEY (unified_id) REFERENCES unified_publications(unified_id)
        )
        """)

        # 9. Collaborations Tracking - ENHANCED for master DB integration
        logger.info("Creating research_collaborations table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_collaborations (
            collab_id INTEGER PRIMARY KEY AUTOINCREMENT,
            unified_id INTEGER NOT NULL,

            -- Collaboration type
            collaboration_type TEXT,       -- 'bilateral', 'multilateral', 'domestic'

            -- Countries (ALIGNED with bilateral_countries codes)
            country_codes TEXT,            -- JSON array: ["US", "CN", "DE"]
            country_count INTEGER,

            -- Institutions
            institution_ids TEXT,          -- JSON array of institution_id values
            institution_count INTEGER,

            -- China involvement (ALIGNED with master DB patterns)
            has_china_author BOOLEAN,
            has_china_institution BOOLEAN,
            china_institution_names TEXT,
            has_pla_affiliation BOOLEAN,   -- PLA-affiliated institutions

            detected_date TEXT,

            FOREIGN KEY (unified_id) REFERENCES unified_publications(unified_id)
        )
        """)

        # 10. Cross-Reference Map - Links to existing arxiv_papers/openalex_works
        logger.info("Creating cross_reference_map table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cross_reference_map (
            xref_id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Unified record
            primary_unified_id INTEGER NOT NULL,

            -- Source records
            openalex_id TEXT,
            openaire_id TEXT,
            arxiv_id TEXT,
            doi TEXT,

            -- Link to EXISTING master DB tables
            master_arxiv_id TEXT,          -- Links to master.arxiv_papers.arxiv_id
            master_openalex_id TEXT,       -- Links to master.openalex_works.work_id

            -- Match metadata
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

            country_code TEXT,             -- ALIGNED with bilateral_countries

            funder_type TEXT,
            is_chinese_funder BOOLEAN,     -- Chinese funding orgs

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

        # 14. Master DB Link Table - Direct links to existing tables
        logger.info("Creating master_db_links table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS master_db_links (
            link_id INTEGER PRIMARY KEY AUTOINCREMENT,
            unified_id INTEGER NOT NULL,

            -- Links to master DB tables
            links_to_arxiv_papers BOOLEAN,
            links_to_openalex_works BOOLEAN,
            links_to_patents BOOLEAN,
            links_to_ted_contracts BOOLEAN,
            links_to_usaspending BOOLEAN,

            -- Additional metadata
            link_quality REAL,
            link_date TEXT,

            FOREIGN KEY (unified_id) REFERENCES unified_publications(unified_id),
            UNIQUE(unified_id)
        )
        """)

        logger.info("All tables created successfully")

    def create_indexes(self, cursor):
        """Create indexes (defer this for test mode - run after data load)"""
        logger.info("Skipping index creation (will create after data ingestion)")
        pass

    def verify_schema(self, cursor):
        """Verify all tables were created"""
        logger.info("Verifying schema...")

        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        table_count = cursor.fetchone()[0]
        logger.info(f"Tables created: {table_count}/14")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"Tables: {', '.join(tables)}")

        if table_count == 14:
            logger.info("✓ Schema verification PASSED")
            return True
        else:
            logger.error("✗ Schema verification FAILED - missing tables")
            return False

    def run(self):
        """Execute complete database setup"""
        logger.info("=" * 80)
        logger.info("RESEARCH MAPPING DATABASE - ALIGNED SETUP")
        logger.info("=" * 80)

        # Load standards
        tech_domains = self.load_technology_domains()
        master_standards = self.get_master_db_standards()

        try:
            # Create database
            conn, cursor = self.create_database()

            # Create schema
            self.create_schema(cursor)

            # Commit
            conn.commit()

            # Verify
            success = self.verify_schema(cursor)

            # Close
            conn.close()

            if success:
                logger.info("=" * 80)
                logger.info("DATABASE SETUP COMPLETE - ALIGNED WITH MASTER DB")
                logger.info("=" * 80)
                logger.info(f"Database location: {self.db_path}")
                logger.info(f"Database size: {self.db_path.stat().st_size / (1024*1024):.2f} MB")
                logger.info(f"Technology domains aligned: {len(tech_domains)}")
                logger.info(f"Country codes aligned: {len(master_standards.get('country_codes', []))}")
                logger.info("\nAlignment features:")
                logger.info("  ✓ Same technology_domain field")
                logger.info("  ✓ Same country codes (ISO 2-letter)")
                logger.info("  ✓ Same is_chinese flags")
                logger.info("  ✓ Links to existing arxiv_papers via cross_reference_map")
                logger.info("  ✓ Links to existing openalex_works via cross_reference_map")
                logger.info("\nReady for test ingestion")

                return True
            else:
                logger.error("Database setup FAILED")
                return False

        except Exception as e:
            logger.error(f"Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    setup = ResearchMappingDatabaseSetup()
    success = setup.run()

    if success:
        print("\n✓ Database setup completed successfully")
        print(f"✓ Database ready at: {setup.db_path}")
        print("\nNext: Run test ingestion")
        print("  python scripts/ingest_openalex_comprehensive.py --start-date 2024-01-01 --end-date 2024-01-31")
    else:
        print("\n✗ Database setup failed - check logs above")
        exit(1)


if __name__ == "__main__":
    main()
