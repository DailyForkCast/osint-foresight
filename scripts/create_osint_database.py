#!/usr/bin/env python3
"""
OSINT SQL Database Creator
Create and populate SQL database with all collected intelligence data
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import hashlib
from typing import Dict, List, Any
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

class OSINTDatabaseCreator:
    """Create and manage OSINT SQL database"""

    def __init__(self):
        self.start_time = datetime.now()

        # Database location
        self.db_path = Path("F:/OSINT_DATA/osint_intelligence.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Data sources
        self.epo_patents_dir = Path("F:/OSINT_DATA/epo_targeted_patents")
        self.epo_collection_dir = Path("F:/OSINT_DATA/epo_provenance_collection")
        self.cordis_dir = Path("data/processed/cordis_comprehensive")
        self.openalex_dir = Path("data/processed/openalex_real_data")
        self.ted_dir = Path("F:/TED_Data")

        # Connect to database
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

        print(f"Creating database: {self.db_path}")

    def create_schema(self):
        """Create database schema with all tables"""

        print("\n1. Creating database schema...")

        # Drop existing tables for clean slate
        tables_to_drop = [
            'patents', 'patent_applicants', 'patent_classifications',
            'patent_abstracts', 'patent_claims',
            'organizations', 'collaborations',
            'technology_areas', 'risk_indicators',
            'cordis_projects', 'cordis_participants',
            'openalex_publications', 'openalex_authors',
            'data_provenance', 'cross_references'
        ]

        for table in tables_to_drop:
            # SECURITY: Validate table name before use in SQL
            safe_table = validate_sql_identifier(table)
            self.cursor.execute(f"DROP TABLE IF EXISTS {safe_table}")

        # Core Patents table
        self.cursor.execute("""
        CREATE TABLE patents (
            patent_id TEXT PRIMARY KEY,
            country_code TEXT,
            doc_number TEXT,
            kind_code TEXT,
            title TEXT,
            publication_date TEXT,
            priority_date TEXT,
            category TEXT,
            abstract_available BOOLEAN,
            claims_count INTEGER,
            data_source TEXT,
            collection_time TEXT,
            sha256_hash TEXT
        )
        """)

        # Patent Applicants
        self.cursor.execute("""
        CREATE TABLE patent_applicants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patent_id TEXT,
            applicant_name TEXT,
            applicant_country TEXT,
            applicant_type TEXT,
            is_chinese BOOLEAN,
            is_european BOOLEAN,
            FOREIGN KEY(patent_id) REFERENCES patents(patent_id)
        )
        """)

        # Patent Classifications
        self.cursor.execute("""
        CREATE TABLE patent_classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patent_id TEXT,
            classification_code TEXT,
            classification_text TEXT,
            technology_area TEXT,
            FOREIGN KEY(patent_id) REFERENCES patents(patent_id)
        )
        """)

        # Patent Abstracts
        self.cursor.execute("""
        CREATE TABLE patent_abstracts (
            patent_id TEXT PRIMARY KEY,
            abstract_text TEXT,
            language TEXT,
            FOREIGN KEY(patent_id) REFERENCES patents(patent_id)
        )
        """)

        # Patent Claims
        self.cursor.execute("""
        CREATE TABLE patent_claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patent_id TEXT,
            claim_number INTEGER,
            claim_text TEXT,
            FOREIGN KEY(patent_id) REFERENCES patents(patent_id)
        )
        """)

        # Organizations master table
        self.cursor.execute("""
        CREATE TABLE organizations (
            org_id TEXT PRIMARY KEY,
            org_name TEXT,
            org_type TEXT,
            country TEXT,
            is_chinese BOOLEAN,
            is_european BOOLEAN,
            first_seen TEXT,
            patent_count INTEGER,
            project_count INTEGER,
            publication_count INTEGER,
            risk_score INTEGER
        )
        """)

        # Collaborations table
        self.cursor.execute("""
        CREATE TABLE collaborations (
            collab_id TEXT PRIMARY KEY,
            org1_id TEXT,
            org2_id TEXT,
            collaboration_type TEXT,
            evidence_type TEXT,
            evidence_id TEXT,
            start_date TEXT,
            technology_area TEXT,
            is_eu_china BOOLEAN,
            risk_level TEXT,
            FOREIGN KEY(org1_id) REFERENCES organizations(org_id),
            FOREIGN KEY(org2_id) REFERENCES organizations(org_id)
        )
        """)

        # Technology Areas
        self.cursor.execute("""
        CREATE TABLE technology_areas (
            tech_id TEXT PRIMARY KEY,
            tech_name TEXT,
            tech_category TEXT,
            ipc_codes TEXT,
            critical_technology BOOLEAN,
            china_activity_level INTEGER,
            eu_activity_level INTEGER,
            collaboration_count INTEGER
        )
        """)

        # Risk Indicators
        self.cursor.execute("""
        CREATE TABLE risk_indicators (
            risk_id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicator_type TEXT,
            severity TEXT,
            entity_type TEXT,
            entity_id TEXT,
            description TEXT,
            evidence TEXT,
            detection_date TEXT,
            mitigation_status TEXT
        )
        """)

        # CORDIS Projects
        self.cursor.execute("""
        CREATE TABLE cordis_projects (
            project_id TEXT PRIMARY KEY,
            acronym TEXT,
            title TEXT,
            start_date TEXT,
            end_date TEXT,
            total_cost REAL,
            eu_contribution REAL,
            coordinator_country TEXT,
            participant_count INTEGER,
            has_chinese_participant BOOLEAN,
            topics TEXT,
            objectives TEXT
        )
        """)

        # CORDIS Participants
        self.cursor.execute("""
        CREATE TABLE cordis_participants (
            participant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            org_name TEXT,
            org_country TEXT,
            org_type TEXT,
            role TEXT,
            contribution REAL,
            is_coordinator BOOLEAN,
            FOREIGN KEY(project_id) REFERENCES cordis_projects(project_id)
        )
        """)

        # OpenAlex Publications
        self.cursor.execute("""
        CREATE TABLE openalex_publications (
            publication_id TEXT PRIMARY KEY,
            doi TEXT,
            title TEXT,
            publication_date TEXT,
            journal TEXT,
            citation_count INTEGER,
            has_chinese_author BOOLEAN,
            has_eu_author BOOLEAN,
            is_collaboration BOOLEAN,
            topics TEXT,
            abstract TEXT
        )
        """)

        # OpenAlex Authors
        self.cursor.execute("""
        CREATE TABLE openalex_authors (
            author_id TEXT PRIMARY KEY,
            author_name TEXT,
            institution TEXT,
            institution_country TEXT,
            publication_count INTEGER,
            h_index INTEGER,
            collaboration_countries TEXT
        )
        """)

        # Data Provenance
        self.cursor.execute("""
        CREATE TABLE data_provenance (
            provenance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_type TEXT,
            source_api TEXT,
            collection_timestamp TEXT,
            query_used TEXT,
            records_collected INTEGER,
            sha256_verification TEXT,
            raw_file_path TEXT
        )
        """)

        # Cross References
        self.cursor.execute("""
        CREATE TABLE cross_references (
            ref_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT,
            source_id TEXT,
            target_type TEXT,
            target_id TEXT,
            confidence_score REAL,
            match_type TEXT,
            verification_status TEXT
        )
        """)

        # Create indexes for performance
        indexes = [
            "CREATE INDEX idx_patent_country ON patents(country_code)",
            "CREATE INDEX idx_patent_category ON patents(category)",
            "CREATE INDEX idx_applicant_name ON patent_applicants(applicant_name)",
            "CREATE INDEX idx_applicant_chinese ON patent_applicants(is_chinese)",
            "CREATE INDEX idx_org_chinese ON organizations(is_chinese)",
            "CREATE INDEX idx_collab_eu_china ON collaborations(is_eu_china)",
            "CREATE INDEX idx_risk_severity ON risk_indicators(severity)",
            "CREATE INDEX idx_cordis_chinese ON cordis_projects(has_chinese_participant)"
        ]

        for index in indexes:
            self.cursor.execute(index)

        self.conn.commit()
        print("   Schema created successfully")

    def import_epo_patents(self):
        """Import EPO patent data"""

        print("\n2. Importing EPO patent data...")
        patent_count = 0

        # Import detailed patents
        for patent_file in self.epo_patents_dir.glob("*.json"):
            if 'summary' not in patent_file.name:
                with open(patent_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                patent_id = data.get('patent_id', '')
                extracted = data.get('extracted_info', {})

                # Generate SHA256 hash
                content = json.dumps(data, sort_keys=True)
                sha256 = hashlib.sha256(content.encode()).hexdigest()

                # Insert patent
                self.cursor.execute("""
                INSERT OR REPLACE INTO patents
                (patent_id, country_code, doc_number, kind_code, title,
                 category, abstract_available, claims_count, data_source,
                 collection_time, sha256_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    patent_id,
                    patent_id[:2] if len(patent_id) > 2 else '',
                    patent_id[2:-2] if len(patent_id) > 4 else '',
                    patent_id[-2:] if len(patent_id) > 2 else '',
                    extracted.get('title', ''),
                    extracted.get('category', ''),
                    bool(extracted.get('abstract', '')),
                    extracted.get('claims_count', 0),
                    'EPO OPS',
                    data.get('retrieval_time', ''),
                    sha256
                ))

                # Insert applicants
                for applicant in extracted.get('applicants', []):
                    name = applicant.get('name', '')
                    country = applicant.get('country', '')

                    self.cursor.execute("""
                    INSERT INTO patent_applicants
                    (patent_id, applicant_name, applicant_country, is_chinese, is_european)
                    VALUES (?, ?, ?, ?, ?)
                    """, (
                        patent_id,
                        name,
                        country,
                        country == 'CN',
                        country in ['DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'PL']
                    ))

                # Insert classifications
                for classification in extracted.get('classifications', []):
                    tech_area = self.map_technology_area(classification)

                    self.cursor.execute("""
                    INSERT INTO patent_classifications
                    (patent_id, classification_code, classification_text, technology_area)
                    VALUES (?, ?, ?, ?)
                    """, (
                        patent_id,
                        classification[:4] if len(classification) >= 4 else classification,
                        classification,
                        tech_area
                    ))

                # Insert abstract if available
                if extracted.get('abstract'):
                    self.cursor.execute("""
                    INSERT OR REPLACE INTO patent_abstracts
                    (patent_id, abstract_text, language)
                    VALUES (?, ?, ?)
                    """, (
                        patent_id,
                        extracted['abstract'],
                        'en'
                    ))

                patent_count += 1

        self.conn.commit()
        print(f"   Imported {patent_count} patents")

    def map_technology_area(self, classification: str) -> str:
        """Map IPC classification to technology area"""

        tech_map = {
            'H04': '5G/Telecommunications',
            'G06': 'Computing/AI',
            'H01': 'Electronic Components',
            'B29': 'Advanced Materials',
            'C07': 'Organic Chemistry/Pharma',
            'G01': 'Measurement/Testing',
            'H03': 'Electronic Circuits',
            'F16': 'Mechanical Engineering'
        }

        for code, area in tech_map.items():
            if classification.startswith(code):
                return area

        return 'Other'

    def identify_organizations(self):
        """Extract and consolidate organizations"""

        print("\n3. Identifying organizations...")

        # Extract from patents
        self.cursor.execute("""
        INSERT OR IGNORE INTO organizations (org_id, org_name, country, is_chinese, is_european, patent_count)
        SELECT
            LOWER(REPLACE(applicant_name, ' ', '_')) as org_id,
            applicant_name as org_name,
            applicant_country as country,
            is_chinese,
            is_european,
            COUNT(DISTINCT patent_id) as patent_count
        FROM patent_applicants
        GROUP BY applicant_name, applicant_country
        """)

        self.conn.commit()

        # Count organizations
        self.cursor.execute("SELECT COUNT(*) FROM organizations")
        org_count = self.cursor.fetchone()[0]
        print(f"   Identified {org_count} organizations")

    def identify_collaborations(self):
        """Identify collaboration patterns"""

        print("\n4. Identifying collaborations...")

        # Find patents with multiple applicants from different countries
        self.cursor.execute("""
        SELECT
            p1.patent_id,
            p1.applicant_name as org1,
            p1.applicant_country as country1,
            p2.applicant_name as org2,
            p2.applicant_country as country2
        FROM patent_applicants p1
        JOIN patent_applicants p2 ON p1.patent_id = p2.patent_id
        WHERE p1.applicant_name < p2.applicant_name
        AND p1.applicant_country != p2.applicant_country
        """)

        collabs = self.cursor.fetchall()
        collab_count = 0

        for patent_id, org1, country1, org2, country2 in collabs:
            is_eu_china = (
                (country1 == 'CN' and country2 in ['DE', 'FR', 'IT']) or
                (country2 == 'CN' and country1 in ['DE', 'FR', 'IT'])
            )

            risk_level = 'CRITICAL' if is_eu_china else 'MEDIUM'

            collab_id = f"{org1}_{org2}_{patent_id}"

            self.cursor.execute("""
            INSERT OR IGNORE INTO collaborations
            (collab_id, org1_id, org2_id, collaboration_type, evidence_type,
             evidence_id, is_eu_china, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                collab_id,
                org1.lower().replace(' ', '_'),
                org2.lower().replace(' ', '_'),
                'Patent Co-Application',
                'Patent',
                patent_id,
                is_eu_china,
                risk_level
            ))

            collab_count += 1

        self.conn.commit()
        print(f"   Identified {collab_count} collaborations")

    def calculate_risk_indicators(self):
        """Calculate and store risk indicators"""

        print("\n5. Calculating risk indicators...")

        # Chinese entities with EU patents
        self.cursor.execute("""
        SELECT org_name, patent_count
        FROM organizations
        WHERE is_chinese = 1 AND patent_count > 0
        """)

        for org_name, count in self.cursor.fetchall():
            self.cursor.execute("""
            INSERT INTO risk_indicators
            (indicator_type, severity, entity_type, entity_id, description, evidence, detection_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                'Chinese IP Activity',
                'HIGH' if count > 1 else 'MEDIUM',
                'Organization',
                org_name,
                f'Chinese entity {org_name} has {count} EU patents',
                f'{count} patents filed',
                datetime.now().isoformat()
            ))

        # EU-China collaborations
        self.cursor.execute("""
        SELECT collab_id, org1_id, org2_id
        FROM collaborations
        WHERE is_eu_china = 1
        """)

        for collab_id, org1, org2 in self.cursor.fetchall():
            self.cursor.execute("""
            INSERT INTO risk_indicators
            (indicator_type, severity, entity_type, entity_id, description, evidence, detection_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                'EU-China Collaboration',
                'CRITICAL',
                'Collaboration',
                collab_id,
                f'Direct EU-China collaboration between {org1} and {org2}',
                'Joint patent application',
                datetime.now().isoformat()
            ))

        self.conn.commit()

        # Count risk indicators
        self.cursor.execute("SELECT COUNT(*) FROM risk_indicators")
        risk_count = self.cursor.fetchone()[0]
        print(f"   Generated {risk_count} risk indicators")

    def create_intelligence_views(self):
        """Create views for intelligence analysis"""

        print("\n6. Creating intelligence views...")

        # EU-China collaboration overview
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_eu_china_collaborations AS
        SELECT
            c.collab_id,
            o1.org_name as chinese_entity,
            o2.org_name as eu_entity,
            o2.country as eu_country,
            c.evidence_type,
            c.risk_level
        FROM collaborations c
        JOIN organizations o1 ON c.org1_id = o1.org_id
        JOIN organizations o2 ON c.org2_id = o2.org_id
        WHERE c.is_eu_china = 1
        """)

        # Technology transfer patterns
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_technology_transfer AS
        SELECT
            pc.technology_area,
            COUNT(DISTINCT p.patent_id) as patent_count,
            COUNT(DISTINCT CASE WHEN pa.is_chinese = 1 THEN p.patent_id END) as chinese_patents,
            COUNT(DISTINCT CASE WHEN pa.is_european = 1 THEN p.patent_id END) as eu_patents
        FROM patents p
        JOIN patent_classifications pc ON p.patent_id = pc.patent_id
        JOIN patent_applicants pa ON p.patent_id = pa.patent_id
        GROUP BY pc.technology_area
        """)

        # High risk entities
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_high_risk_entities AS
        SELECT
            o.org_name,
            o.country,
            o.patent_count,
            COUNT(DISTINCT c.collab_id) as collaboration_count,
            COUNT(DISTINCT r.risk_id) as risk_indicator_count
        FROM organizations o
        LEFT JOIN collaborations c ON o.org_id = c.org1_id OR o.org_id = c.org2_id
        LEFT JOIN risk_indicators r ON o.org_name = r.entity_id
        WHERE o.is_chinese = 1 OR r.severity IN ('HIGH', 'CRITICAL')
        GROUP BY o.org_id
        HAVING risk_indicator_count > 0
        ORDER BY risk_indicator_count DESC
        """)

        self.conn.commit()
        print("   Intelligence views created")

    def generate_summary_report(self):
        """Generate summary statistics"""

        print("\n" + "="*60)
        print("DATABASE SUMMARY")
        print("="*60)

        # Patent statistics
        self.cursor.execute("SELECT COUNT(*) FROM patents")
        patent_count = self.cursor.fetchone()[0]
        print(f"\nPatents: {patent_count}")

        # Organization statistics
        self.cursor.execute("SELECT COUNT(*) FROM organizations WHERE is_chinese = 1")
        chinese_orgs = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM organizations WHERE is_european = 1")
        eu_orgs = self.cursor.fetchone()[0]
        print(f"Chinese organizations: {chinese_orgs}")
        print(f"European organizations: {eu_orgs}")

        # Collaboration statistics
        self.cursor.execute("SELECT COUNT(*) FROM collaborations WHERE is_eu_china = 1")
        eu_china_collabs = self.cursor.fetchone()[0]
        print(f"EU-China collaborations: {eu_china_collabs}")

        # Risk indicators
        self.cursor.execute("SELECT severity, COUNT(*) FROM risk_indicators GROUP BY severity")
        risks = self.cursor.fetchall()
        print("\nRisk Indicators:")
        for severity, count in risks:
            print(f"  {severity}: {count}")

        # Technology areas
        self.cursor.execute("""
        SELECT technology_area, COUNT(*)
        FROM patent_classifications
        GROUP BY technology_area
        ORDER BY COUNT(*) DESC
        LIMIT 5
        """)
        techs = self.cursor.fetchall()
        print("\nTop Technology Areas:")
        for tech, count in techs:
            print(f"  {tech}: {count} patents")

    def export_queries(self):
        """Export useful SQL queries to file"""

        queries_file = Path("F:/OSINT_DATA/useful_queries.sql")

        queries = """
-- OSINT Intelligence Database - Useful Queries
-- Generated: {timestamp}
-- Database: F:/OSINT_DATA/osint_intelligence.db

-- 1. Find all Chinese entities with EU patents
SELECT org_name, country, patent_count
FROM organizations
WHERE is_chinese = 1 AND patent_count > 0
ORDER BY patent_count DESC;

-- 2. List EU-China collaborations
SELECT * FROM v_eu_china_collaborations;

-- 3. Technology transfer analysis
SELECT * FROM v_technology_transfer
ORDER BY chinese_patents DESC;

-- 4. High risk entities
SELECT * FROM v_high_risk_entities;

-- 5. Patents by category
SELECT category, COUNT(*) as count
FROM patents
GROUP BY category
ORDER BY count DESC;

-- 6. Cross-border patent applications
SELECT
    p.patent_id,
    p.title,
    GROUP_CONCAT(DISTINCT pa.applicant_country) as countries
FROM patents p
JOIN patent_applicants pa ON p.patent_id = pa.patent_id
GROUP BY p.patent_id
HAVING COUNT(DISTINCT pa.applicant_country) > 1;

-- 7. Critical technology patents
SELECT
    p.patent_id,
    p.title,
    pc.technology_area,
    pa.applicant_name
FROM patents p
JOIN patent_classifications pc ON p.patent_id = pc.patent_id
JOIN patent_applicants pa ON p.patent_id = pa.patent_id
WHERE pc.technology_area IN ('5G/Telecommunications', 'Computing/AI', 'Electronic Components')
AND pa.is_chinese = 1;

-- 8. Risk assessment summary
SELECT
    indicator_type,
    severity,
    COUNT(*) as count
FROM risk_indicators
GROUP BY indicator_type, severity
ORDER BY
    CASE severity
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        ELSE 4
    END;
        """.format(timestamp=datetime.now().isoformat())

        with open(queries_file, 'w') as f:
            f.write(queries)

        print(f"\nUseful queries saved to: {queries_file}")

    def run_complete_import(self):
        """Run complete database creation and import"""

        try:
            # Create schema
            self.create_schema()

            # Import data
            self.import_epo_patents()

            # Analysis
            self.identify_organizations()
            self.identify_collaborations()
            self.calculate_risk_indicators()

            # Create views
            self.create_intelligence_views()

            # Generate reports
            self.generate_summary_report()
            self.export_queries()

            print(f"\nDatabase created successfully: {self.db_path}")
            print(f"Size: {self.db_path.stat().st_size / 1024 / 1024:.2f} MB")

        finally:
            self.conn.close()

def main():
    creator = OSINTDatabaseCreator()
    creator.run_complete_import()

if __name__ == "__main__":
    main()
