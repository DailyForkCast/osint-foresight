#!/usr/bin/env python3
"""
OSINT Master Database Creator
Unified intelligence database integrating all sources
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import hashlib
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OSINTMasterDatabase:
    """Create and manage unified OSINT intelligence database"""

    def __init__(self):
        self.start_time = datetime.now()

        # Database location
        self.db_path = Path("F:/OSINT_DATA/osint_master.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Data source paths
        self.china_config = Path("C:/Projects/OSINT - Foresight/config/china_institutions_comprehensive.json")
        self.epo_dir = Path("F:/OSINT_DATA/epo_targeted_patents")
        self.openaire_dir = Path("F:/OSINT_DATA/openaire_china_verified")
        self.ted_db = Path("F:/OSINT_DATA/ted_analysis.db")

        # Connect to database
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")

        logger.info(f"Creating master database: {self.db_path}")

    def create_core_schema(self):
        """Create core database schema"""

        logger.info("Creating core schema...")

        # Master entities table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            entity_id TEXT PRIMARY KEY,
            entity_name TEXT NOT NULL,
            entity_type TEXT, -- organization, person, program, technology
            country_origin TEXT,
            country_operation TEXT,
            is_chinese BOOLEAN DEFAULT 0,
            is_european BOOLEAN DEFAULT 0,
            is_sanctioned BOOLEAN DEFAULT 0,
            risk_level TEXT, -- CRITICAL, HIGH, MEDIUM, LOW
            first_seen DATE,
            last_updated DATE,
            confidence_score REAL,
            notes TEXT,
            metadata JSON
        )
        """)

        # Entity aliases for name variations
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS entity_aliases (
            alias_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id TEXT,
            alias_name TEXT,
            alias_type TEXT, -- abbreviation, translation, alternate
            source TEXT,
            FOREIGN KEY(entity_id) REFERENCES entities(entity_id)
        )
        """)

        # Collaborations table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS collaborations (
            collab_id TEXT PRIMARY KEY,
            entity1_id TEXT,
            entity2_id TEXT,
            collaboration_type TEXT, -- research, patent, commercial, funding
            start_date DATE,
            end_date DATE,
            status TEXT, -- active, completed, suspended
            evidence_source TEXT,
            evidence_id TEXT,
            confidence_score REAL,
            is_china_related BOOLEAN DEFAULT 0,
            technology_area TEXT,
            risk_assessment TEXT,
            FOREIGN KEY(entity1_id) REFERENCES entities(entity_id),
            FOREIGN KEY(entity2_id) REFERENCES entities(entity_id)
        )
        """)

        # Technologies table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS technologies (
            tech_id TEXT PRIMARY KEY,
            technology_name TEXT,
            technology_category TEXT, -- 5G, AI, Quantum, Biotech, etc.
            ipc_codes TEXT,
            cpc_codes TEXT,
            keywords TEXT,
            is_critical BOOLEAN DEFAULT 0,
            is_dual_use BOOLEAN DEFAULT 0,
            china_activity_level INTEGER, -- 1-10 scale
            eu_activity_level INTEGER,
            us_restrictions TEXT,
            export_control_status TEXT
        )
        """)

        # Research publications
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS publications (
            publication_id TEXT PRIMARY KEY,
            doi TEXT UNIQUE,
            title TEXT,
            abstract TEXT,
            publication_date DATE,
            journal TEXT,
            authors JSON,
            affiliations JSON,
            keywords TEXT,
            citation_count INTEGER,
            has_chinese_author BOOLEAN DEFAULT 0,
            has_eu_author BOOLEAN DEFAULT 0,
            technology_areas TEXT,
            data_source TEXT,
            collection_date DATE
        )
        """)

        # Patents
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS patents (
            patent_id TEXT PRIMARY KEY,
            patent_number TEXT,
            title TEXT,
            abstract TEXT,
            filing_date DATE,
            publication_date DATE,
            grant_date DATE,
            applicants JSON,
            inventors JSON,
            ipc_codes TEXT,
            cpc_codes TEXT,
            claims_count INTEGER,
            citations_made INTEGER,
            citations_received INTEGER,
            legal_status TEXT,
            technology_category TEXT,
            has_chinese_entity BOOLEAN DEFAULT 0,
            has_eu_entity BOOLEAN DEFAULT 0,
            data_source TEXT
        )
        """)

        # Funding and grants
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS funding (
            funding_id TEXT PRIMARY KEY,
            program_name TEXT,
            funding_source TEXT,
            funding_type TEXT, -- grant, contract, investment
            amount REAL,
            currency TEXT,
            start_date DATE,
            end_date DATE,
            recipient_id TEXT,
            topic TEXT,
            objectives TEXT,
            deliverables TEXT,
            has_chinese_participation BOOLEAN DEFAULT 0,
            risk_indicators TEXT,
            FOREIGN KEY(recipient_id) REFERENCES entities(entity_id)
        )
        """)

        # Procurement and contracts
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS procurement (
            contract_id TEXT PRIMARY KEY,
            contract_number TEXT,
            title TEXT,
            description TEXT,
            buyer_entity TEXT,
            supplier_entity TEXT,
            contract_value REAL,
            currency TEXT,
            award_date DATE,
            start_date DATE,
            end_date DATE,
            cpv_codes TEXT,
            has_chinese_supplier BOOLEAN DEFAULT 0,
            security_clearance_required BOOLEAN DEFAULT 0,
            technology_transfer_risk TEXT,
            data_source TEXT
        )
        """)

        # Risk indicators
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_indicators (
            indicator_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id TEXT,
            indicator_type TEXT,
            indicator_name TEXT,
            severity TEXT, -- CRITICAL, HIGH, MEDIUM, LOW
            description TEXT,
            evidence TEXT,
            detection_date DATE,
            mitigation_status TEXT,
            mitigation_actions TEXT,
            FOREIGN KEY(entity_id) REFERENCES entities(entity_id)
        )
        """)

        # Intelligence events/alerts
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS intelligence_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT, -- new_collaboration, technology_transfer, personnel_move
            event_date DATE,
            entities_involved JSON,
            description TEXT,
            significance TEXT, -- CRITICAL, HIGH, MEDIUM, LOW
            source TEXT,
            verified BOOLEAN DEFAULT 0,
            analyst_notes TEXT,
            action_required BOOLEAN DEFAULT 0,
            action_taken TEXT
        )
        """)

        # Data provenance
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_provenance (
            provenance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_type TEXT,
            source_api TEXT,
            source_url TEXT,
            collection_timestamp DATETIME,
            collection_method TEXT,
            query_used TEXT,
            records_collected INTEGER,
            sha256_hash TEXT,
            raw_file_path TEXT,
            processing_status TEXT,
            error_log TEXT
        )
        """)

        # Cross references between data sources
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS cross_references (
            ref_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source1_type TEXT,
            source1_id TEXT,
            source2_type TEXT,
            source2_id TEXT,
            match_confidence REAL,
            match_method TEXT,
            verified BOOLEAN DEFAULT 0,
            notes TEXT
        )
        """)

        # China-specific tracking
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS china_entities (
            entity_id TEXT PRIMARY KEY,
            entity_name_chinese TEXT,
            entity_name_english TEXT,
            entity_type TEXT, -- university, company, institute, government
            parent_organization TEXT,
            location_province TEXT,
            location_city TEXT,
            established_date DATE,
            key_personnel JSON,
            research_areas TEXT,
            international_partnerships JSON,
            us_entity_list BOOLEAN DEFAULT 0,
            eu_sanctions BOOLEAN DEFAULT 0,
            military_civil_fusion BOOLEAN DEFAULT 0,
            belt_and_road BOOLEAN DEFAULT 0,
            thousand_talents BOOLEAN DEFAULT 0,
            made_in_china_2025 BOOLEAN DEFAULT 0,
            FOREIGN KEY(entity_id) REFERENCES entities(entity_id)
        )
        """)

        self.conn.commit()
        logger.info("Core schema created")

    def create_analysis_views(self):
        """Create views for analysis and reporting"""

        logger.info("Creating analysis views...")

        # EU-China collaboration overview
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_eu_china_collaborations AS
        SELECT
            c.collab_id,
            e1.entity_name as entity1_name,
            e1.country_origin as entity1_country,
            e2.entity_name as entity2_name,
            e2.country_origin as entity2_country,
            c.collaboration_type,
            c.technology_area,
            c.start_date,
            c.risk_assessment,
            c.confidence_score
        FROM collaborations c
        JOIN entities e1 ON c.entity1_id = e1.entity_id
        JOIN entities e2 ON c.entity2_id = e2.entity_id
        WHERE c.is_china_related = 1
        AND (e1.is_european = 1 OR e2.is_european = 1)
        """)

        # Technology transfer risks
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_technology_transfer_risks AS
        SELECT
            t.technology_name,
            t.technology_category,
            t.china_activity_level,
            t.eu_activity_level,
            COUNT(DISTINCT p.patent_id) as patent_count,
            COUNT(DISTINCT pub.publication_id) as publication_count,
            t.is_critical,
            t.is_dual_use,
            t.export_control_status
        FROM technologies t
        LEFT JOIN patents p ON t.technology_category = p.technology_category
        LEFT JOIN publications pub ON t.technology_name LIKE '%' || pub.keywords || '%'
        WHERE t.china_activity_level > 5
        GROUP BY t.tech_id
        ORDER BY t.china_activity_level DESC
        """)

        # High risk entities
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_high_risk_entities AS
        SELECT
            e.entity_id,
            e.entity_name,
            e.entity_type,
            e.country_origin,
            e.risk_level,
            COUNT(DISTINCT r.indicator_id) as risk_indicator_count,
            COUNT(DISTINCT c.collab_id) as collaboration_count,
            ce.military_civil_fusion,
            ce.us_entity_list,
            ce.eu_sanctions
        FROM entities e
        LEFT JOIN risk_indicators r ON e.entity_id = r.entity_id
        LEFT JOIN collaborations c ON e.entity_id IN (c.entity1_id, c.entity2_id)
        LEFT JOIN china_entities ce ON e.entity_id = ce.entity_id
        WHERE e.risk_level IN ('CRITICAL', 'HIGH')
        OR ce.military_civil_fusion = 1
        OR ce.us_entity_list = 1
        GROUP BY e.entity_id
        ORDER BY risk_indicator_count DESC
        """)

        # Research collaboration network
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_research_network AS
        SELECT
            pub.publication_id,
            pub.title,
            pub.publication_date,
            pub.has_chinese_author,
            pub.has_eu_author,
            pub.citation_count,
            pub.technology_areas,
            COUNT(DISTINCT json_extract(value, '$.affiliation')) as institution_count
        FROM publications pub,
             json_each(pub.authors)
        WHERE pub.has_chinese_author = 1
        AND pub.has_eu_author = 1
        GROUP BY pub.publication_id
        ORDER BY pub.citation_count DESC
        """)

        # Patent landscape
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_patent_landscape AS
        SELECT
            p.technology_category,
            COUNT(*) as total_patents,
            SUM(p.has_chinese_entity) as chinese_patents,
            SUM(p.has_eu_entity) as eu_patents,
            SUM(p.has_chinese_entity AND p.has_eu_entity) as joint_patents,
            AVG(p.citations_received) as avg_citations,
            MIN(p.filing_date) as earliest_filing,
            MAX(p.filing_date) as latest_filing
        FROM patents p
        GROUP BY p.technology_category
        ORDER BY total_patents DESC
        """)

        # Funding flows
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_funding_flows AS
        SELECT
            f.program_name,
            f.funding_source,
            e.entity_name as recipient_name,
            e.country_origin as recipient_country,
            f.amount,
            f.currency,
            f.start_date,
            f.has_chinese_participation,
            f.risk_indicators
        FROM funding f
        JOIN entities e ON f.recipient_id = e.entity_id
        WHERE f.has_chinese_participation = 1
        OR e.is_chinese = 1
        ORDER BY f.amount DESC
        """)

        self.conn.commit()
        logger.info("Analysis views created")

    def create_indexes(self):
        """Create indexes for performance"""

        logger.info("Creating indexes...")

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_entities_country ON entities(country_origin)",
            "CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type)",
            "CREATE INDEX IF NOT EXISTS idx_entities_risk ON entities(risk_level)",
            "CREATE INDEX IF NOT EXISTS idx_entities_chinese ON entities(is_chinese)",
            "CREATE INDEX IF NOT EXISTS idx_collab_china ON collaborations(is_china_related)",
            "CREATE INDEX IF NOT EXISTS idx_collab_dates ON collaborations(start_date, end_date)",
            "CREATE INDEX IF NOT EXISTS idx_patents_tech ON patents(technology_category)",
            "CREATE INDEX IF NOT EXISTS idx_patents_chinese ON patents(has_chinese_entity)",
            "CREATE INDEX IF NOT EXISTS idx_pub_chinese ON publications(has_chinese_author)",
            "CREATE INDEX IF NOT EXISTS idx_pub_date ON publications(publication_date)",
            "CREATE INDEX IF NOT EXISTS idx_risk_severity ON risk_indicators(severity)",
            "CREATE INDEX IF NOT EXISTS idx_china_entities_mcf ON china_entities(military_civil_fusion)",
            "CREATE INDEX IF NOT EXISTS idx_china_entities_sanctions ON china_entities(us_entity_list, eu_sanctions)"
        ]

        for index in indexes:
            self.cursor.execute(index)

        self.conn.commit()
        logger.info(f"Created {len(indexes)} indexes")

    def load_chinese_entities(self):
        """Load Chinese entities from configuration"""

        logger.info("Loading Chinese entities...")

        if not self.china_config.exists():
            logger.warning(f"China config not found: {self.china_config}")
            return

        with open(self.china_config, 'r', encoding='utf-8') as f:
            china_data = json.load(f)

        entity_count = 0

        # Load universities
        for category, universities in china_data.get('universities', {}).items():
            for uni_name in universities:
                entity_id = hashlib.md5(uni_name.encode()).hexdigest()[:16]

                self.cursor.execute("""
                INSERT OR IGNORE INTO entities
                (entity_id, entity_name, entity_type, country_origin, is_chinese, risk_level)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (entity_id, uni_name, 'university', 'CN', 1, 'MEDIUM'))

                self.cursor.execute("""
                INSERT OR IGNORE INTO china_entities
                (entity_id, entity_name_english, entity_type)
                VALUES (?, ?, ?)
                """, (entity_id, uni_name, 'university'))

                entity_count += 1

        # Load research institutions
        for category, institutions in china_data.get('research_institutions', {}).items():
            for inst_name in institutions:
                entity_id = hashlib.md5(inst_name.encode()).hexdigest()[:16]

                risk_level = 'HIGH' if 'military' in inst_name.lower() else 'MEDIUM'

                self.cursor.execute("""
                INSERT OR IGNORE INTO entities
                (entity_id, entity_name, entity_type, country_origin, is_chinese, risk_level)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (entity_id, inst_name, 'research_institute', 'CN', 1, risk_level))

                entity_count += 1

        # Load companies
        for category, companies in china_data.get('companies', {}).items():
            for company_name in companies:
                entity_id = hashlib.md5(company_name.encode()).hexdigest()[:16]

                # Higher risk for certain companies
                risk_level = 'CRITICAL' if company_name in ['Huawei', 'ZTE', 'SMIC', 'Hikvision'] else 'HIGH'

                self.cursor.execute("""
                INSERT OR IGNORE INTO entities
                (entity_id, entity_name, entity_type, country_origin, is_chinese, risk_level)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (entity_id, company_name, 'company', 'CN', 1, risk_level))

                # Check if on entity list
                us_list = 1 if company_name in ['Huawei', 'ZTE', 'SMIC', 'Hikvision', 'DJI'] else 0

                self.cursor.execute("""
                INSERT OR IGNORE INTO china_entities
                (entity_id, entity_name_english, entity_type, us_entity_list)
                VALUES (?, ?, ?, ?)
                """, (entity_id, company_name, 'company', us_list))

                entity_count += 1

        self.conn.commit()
        logger.info(f"Loaded {entity_count} Chinese entities")

    def create_triggers(self):
        """Create triggers for automatic updates"""

        logger.info("Creating triggers...")

        # Update last_modified timestamp
        self.cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_entity_timestamp
        AFTER UPDATE ON entities
        BEGIN
            UPDATE entities SET last_updated = datetime('now')
            WHERE entity_id = NEW.entity_id;
        END
        """)

        # Auto-flag China-related collaborations
        self.cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS flag_china_collaborations
        AFTER INSERT ON collaborations
        BEGIN
            UPDATE collaborations
            SET is_china_related = 1
            WHERE collab_id = NEW.collab_id
            AND (
                EXISTS (SELECT 1 FROM entities WHERE entity_id = NEW.entity1_id AND is_chinese = 1)
                OR EXISTS (SELECT 1 FROM entities WHERE entity_id = NEW.entity2_id AND is_chinese = 1)
            );
        END
        """)

        self.conn.commit()
        logger.info("Triggers created")

    def generate_summary_stats(self):
        """Generate summary statistics"""

        logger.info("\n" + "="*60)
        logger.info("DATABASE SUMMARY STATISTICS")
        logger.info("="*60)

        # Entity counts
        self.cursor.execute("SELECT COUNT(*) FROM entities WHERE is_chinese = 1")
        chinese_entities = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM entities WHERE is_european = 1")
        eu_entities = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM collaborations WHERE is_china_related = 1")
        china_collabs = self.cursor.fetchone()[0]

        logger.info(f"Chinese entities: {chinese_entities}")
        logger.info(f"European entities: {eu_entities}")
        logger.info(f"China-related collaborations: {china_collabs}")

        # Risk distribution
        self.cursor.execute("""
        SELECT risk_level, COUNT(*)
        FROM entities
        WHERE risk_level IS NOT NULL
        GROUP BY risk_level
        """)

        logger.info("\nRisk Distribution:")
        for level, count in self.cursor.fetchall():
            logger.info(f"  {level}: {count}")

        # Technology areas
        self.cursor.execute("SELECT COUNT(*) FROM technologies WHERE is_critical = 1")
        critical_tech = self.cursor.fetchone()[0]
        logger.info(f"\nCritical technologies tracked: {critical_tech}")

    def initialize_database(self):
        """Initialize the complete database"""

        try:
            # Create schema
            self.create_core_schema()

            # Create views
            self.create_analysis_views()

            # Create indexes
            self.create_indexes()

            # Create triggers
            self.create_triggers()

            # Load Chinese entities
            self.load_chinese_entities()

            # Generate statistics
            self.generate_summary_stats()

            logger.info(f"\nDatabase created successfully: {self.db_path}")
            logger.info(f"Size: {self.db_path.stat().st_size / 1024 / 1024:.2f} MB")

        finally:
            self.conn.close()

def main():
    db_creator = OSINTMasterDatabase()
    db_creator.initialize_database()

if __name__ == "__main__":
    main()
