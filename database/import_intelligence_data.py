#!/usr/bin/env python3
"""
OSINT Data Importer
Import all collected intelligence into master database
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import hashlib
import logging
from typing import Dict, List, Any
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OSINTDataImporter:
    """Import all intelligence data into master database"""

    def __init__(self):
        self.master_db = Path("F:/OSINT_DATA/osint_master.db")
        self.conn = sqlite3.connect(str(self.master_db))
        self.cursor = self.conn.cursor()

        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")

        self.stats = {
            'patents_imported': 0,
            'publications_imported': 0,
            'collaborations_found': 0,
            'entities_added': 0,
            'risks_identified': 0
        }

    def import_epo_patents(self):
        """Import EPO patent data"""

        logger.info("Importing EPO patents...")

        epo_dir = Path("F:/OSINT_DATA/epo_targeted_patents")
        if not epo_dir.exists():
            logger.warning(f"EPO directory not found: {epo_dir}")
            return

        for patent_file in epo_dir.glob("*.json"):
            if 'summary' in patent_file.name:
                continue

            try:
                with open(patent_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                patent_id = data.get('patent_id', '')
                extracted = data.get('extracted_info', {})

                # Insert patent
                self.cursor.execute("""
                INSERT OR IGNORE INTO patents
                (patent_id, title, abstract, publication_date, applicants,
                 claims_count, technology_category, has_chinese_entity, has_eu_entity, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    patent_id,
                    extracted.get('title', ''),
                    extracted.get('abstract', ''),
                    data.get('retrieval_time', ''),
                    json.dumps(extracted.get('applicants', [])),
                    extracted.get('claims_count', 0),
                    extracted.get('category', ''),
                    self._has_chinese_entity(extracted.get('applicants', [])),
                    self._has_eu_entity(extracted.get('applicants', [])),
                    'EPO OPS'
                ))

                # Process applicants as entities
                for applicant in extracted.get('applicants', []):
                    self._process_entity(
                        name=applicant.get('name', ''),
                        entity_type='organization',
                        country=applicant.get('country', ''),
                        source='EPO Patent'
                    )

                # Check for collaborations
                if len(extracted.get('applicants', [])) > 1:
                    self._identify_collaboration(
                        applicants=extracted.get('applicants', []),
                        evidence_type='patent',
                        evidence_id=patent_id,
                        technology=extracted.get('category', '')
                    )

                self.stats['patents_imported'] += 1

            except Exception as e:
                logger.error(f"Error importing patent {patent_file}: {e}")

        self.conn.commit()
        logger.info(f"Imported {self.stats['patents_imported']} patents")

    def import_openaire_publications(self):
        """Import OpenAIRE research publications"""

        logger.info("Importing OpenAIRE publications...")

        # Import the China collaboration data we found
        china_data_file = Path("F:/OSINT_DATA/openaire_china_verified/china_collaborations_verified_20250922_113003.json")

        if china_data_file.exists():
            with open(china_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for country_code, country_data in data.get('countries', {}).items():
                for result in country_data.get('search_results', []):
                    # Generate publication ID
                    pub_id = hashlib.md5(
                        f"{result.get('title', '')}_{result.get('year', '')}".encode()
                    ).hexdigest()[:16]

                    # Analyze organizations for Chinese involvement
                    has_chinese = False
                    has_eu = False

                    for org in result.get('organizations', []):
                        org_name = org.get('name', '').lower()
                        org_country = org.get('country', '')

                        if 'china' in org_name or 'chinese' in org_name or org_country == 'CN':
                            has_chinese = True
                        if org_country in ['IT', 'DE', 'FR', 'ES', 'NL', 'BE']:
                            has_eu = True

                        # Add organization as entity
                        self._process_entity(
                            name=org.get('name', ''),
                            entity_type='organization',
                            country=org_country,
                            source='OpenAIRE'
                        )

                    # Insert publication
                    self.cursor.execute("""
                    INSERT OR IGNORE INTO publications
                    (publication_id, title, publication_date, has_chinese_author,
                     has_eu_author, technology_areas, data_source, collection_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        pub_id,
                        result.get('title', ''),
                        result.get('year', ''),
                        has_chinese,
                        has_eu,
                        result.get('search_term', ''),
                        'OpenAIRE',
                        datetime.now().isoformat()
                    ))

                    self.stats['publications_imported'] += 1

                    # Record collaboration if both Chinese and EU
                    if has_chinese and has_eu:
                        self._record_research_collaboration(
                            organizations=result.get('organizations', []),
                            evidence_id=pub_id,
                            year=result.get('year', '')
                        )

        # Import statistics from our keyword search
        stats_data = {
            'IT': 191314,  # Italy China-related
            'DE': 355765,  # Germany China-related
            'FR': 223663,  # France China-related
            'ES': 133291,  # Spain China-related
            'NL': 148101,  # Netherlands China-related
        }

        for country, count in stats_data.items():
            # Record as intelligence event
            self.cursor.execute("""
            INSERT INTO intelligence_events
            (event_type, event_date, description, significance, source, verified)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                'china_collaboration_volume',
                datetime.now().isoformat(),
                f'{country} has {count:,} China-related research publications',
                'HIGH',
                'OpenAIRE Keyword Analysis',
                1
            ))

        self.conn.commit()
        logger.info(f"Imported {self.stats['publications_imported']} publications")

    def import_existing_databases(self):
        """Import data from existing SQLite databases"""

        logger.info("Importing from existing databases...")

        # Import from original osint_intelligence.db
        original_db = Path("F:/OSINT_DATA/osint_intelligence.db")
        if original_db.exists():
            orig_conn = sqlite3.connect(str(original_db))
            orig_cursor = orig_conn.cursor()

            # Import organizations
            try:
                orig_cursor.execute("SELECT * FROM organizations")
                for row in orig_cursor.fetchall():
                    self._process_entity(
                        name=row[1] if len(row) > 1 else 'Unknown',
                        entity_type='organization',
                        country=row[2] if len(row) > 2 else '',
                        source='Original Database'
                    )
            except Exception as e:
                logger.warning(f"Could not import organizations: {e}")

            orig_conn.close()

        logger.info("Existing database import complete")

    def _process_entity(self, name: str, entity_type: str, country: str, source: str):
        """Process and add an entity"""

        if not name or name == '':
            return

        # Generate entity ID
        entity_id = hashlib.md5(name.encode()).hexdigest()[:16]

        # Determine if Chinese
        is_chinese = self._is_chinese_entity(name, country)
        is_european = country in ['IT', 'DE', 'FR', 'ES', 'NL', 'BE', 'AT', 'PL', 'GR', 'PT']

        # Determine risk level
        risk_level = self._assess_risk_level(name, is_chinese, entity_type)

        try:
            self.cursor.execute("""
            INSERT OR IGNORE INTO entities
            (entity_id, entity_name, entity_type, country_origin, is_chinese, is_european,
             risk_level, first_seen, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity_id, name, entity_type, country, is_chinese, is_european,
                risk_level, datetime.now().isoformat(), 0.8
            ))

            self.stats['entities_added'] += 1

        except Exception as e:
            logger.debug(f"Entity already exists or error: {name} - {e}")

    def _identify_collaboration(self, applicants: List[Dict], evidence_type: str,
                               evidence_id: str, technology: str):
        """Identify and record collaborations"""

        if len(applicants) < 2:
            return

        # Check for China-EU collaboration
        countries = [a.get('country', '') for a in applicants]
        has_chinese = any(self._is_chinese_entity(a.get('name', ''), a.get('country', ''))
                         for a in applicants)
        has_eu = any(c in ['IT', 'DE', 'FR', 'ES', 'NL', 'BE'] for c in countries)

        if has_chinese and has_eu:
            # Record collaboration
            for i, app1 in enumerate(applicants):
                for app2 in applicants[i+1:]:
                    entity1_id = hashlib.md5(app1.get('name', '').encode()).hexdigest()[:16]
                    entity2_id = hashlib.md5(app2.get('name', '').encode()).hexdigest()[:16]
                    collab_id = f"{entity1_id}_{entity2_id}_{evidence_id}"

                    self.cursor.execute("""
                    INSERT OR IGNORE INTO collaborations
                    (collab_id, entity1_id, entity2_id, collaboration_type,
                     evidence_source, evidence_id, is_china_related, technology_area,
                     risk_assessment, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        collab_id, entity1_id, entity2_id, evidence_type,
                        'Patent Application', evidence_id, 1, technology,
                        'HIGH', 0.9
                    ))

                    self.stats['collaborations_found'] += 1

                    # Add risk indicator
                    self._add_risk_indicator(entity1_id, 'China-EU Collaboration', 'HIGH')
                    self._add_risk_indicator(entity2_id, 'China-EU Collaboration', 'HIGH')

    def _record_research_collaboration(self, organizations: List[Dict],
                                      evidence_id: str, year: str):
        """Record research collaboration"""

        for i, org1 in enumerate(organizations):
            for org2 in organizations[i+1:]:
                if self._is_china_eu_pair(org1, org2):
                    entity1_id = hashlib.md5(org1.get('name', '').encode()).hexdigest()[:16]
                    entity2_id = hashlib.md5(org2.get('name', '').encode()).hexdigest()[:16]
                    collab_id = f"research_{entity1_id}_{entity2_id}_{evidence_id}"

                    self.cursor.execute("""
                    INSERT OR IGNORE INTO collaborations
                    (collab_id, entity1_id, entity2_id, collaboration_type,
                     start_date, evidence_source, evidence_id, is_china_related,
                     risk_assessment, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        collab_id, entity1_id, entity2_id, 'research',
                        year, 'OpenAIRE Publication', evidence_id, 1,
                        'MEDIUM', 0.85
                    ))

                    self.stats['collaborations_found'] += 1

    def _is_chinese_entity(self, name: str, country: str) -> bool:
        """Determine if entity is Chinese"""

        if country in ['CN', 'CHN', 'China']:
            return True

        name_lower = name.lower()
        chinese_indicators = [
            'china', 'chinese', 'beijing', 'shanghai', 'shenzhen',
            'huawei', 'tsinghua', 'peking', 'cas', 'guangzhou',
            'wuhan', 'hangzhou', 'nanjing', 'chengdu', 'xi\'an',
            'harbin', 'changsha', 'suzhou', 'xinjiang'
        ]

        return any(indicator in name_lower for indicator in chinese_indicators)

    def _is_china_eu_pair(self, org1: Dict, org2: Dict) -> bool:
        """Check if one org is Chinese and other is EU"""

        org1_chinese = self._is_chinese_entity(org1.get('name', ''), org1.get('country', ''))
        org2_chinese = self._is_chinese_entity(org2.get('name', ''), org2.get('country', ''))

        org1_eu = org1.get('country', '') in ['IT', 'DE', 'FR', 'ES', 'NL', 'BE']
        org2_eu = org2.get('country', '') in ['IT', 'DE', 'FR', 'ES', 'NL', 'BE']

        return (org1_chinese and org2_eu) or (org2_chinese and org1_eu)

    def _has_chinese_entity(self, applicants: List[Dict]) -> bool:
        """Check if any applicant is Chinese"""
        return any(self._is_chinese_entity(a.get('name', ''), a.get('country', ''))
                  for a in applicants)

    def _has_eu_entity(self, applicants: List[Dict]) -> bool:
        """Check if any applicant is from EU"""
        eu_countries = ['IT', 'DE', 'FR', 'ES', 'NL', 'BE', 'AT', 'PL', 'GR', 'PT']
        return any(a.get('country', '') in eu_countries for a in applicants)

    def _assess_risk_level(self, name: str, is_chinese: bool, entity_type: str) -> str:
        """Assess risk level of entity"""

        name_lower = name.lower()

        # Critical risk entities
        critical = ['huawei', 'zte', 'hikvision', 'dahua', 'smic', 'military', 'defense']
        if any(term in name_lower for term in critical):
            return 'CRITICAL'

        # High risk
        if is_chinese and entity_type == 'company':
            return 'HIGH'

        if 'institute' in name_lower and is_chinese:
            return 'HIGH'

        # Medium risk
        if is_chinese:
            return 'MEDIUM'

        return 'LOW'

    def _add_risk_indicator(self, entity_id: str, indicator_type: str, severity: str):
        """Add risk indicator for entity"""

        self.cursor.execute("""
        INSERT OR IGNORE INTO risk_indicators
        (entity_id, indicator_type, severity, description, detection_date)
        VALUES (?, ?, ?, ?, ?)
        """, (
            entity_id, indicator_type, severity,
            f'{indicator_type} detected', datetime.now().isoformat()
        ))

        self.stats['risks_identified'] += 1

    def import_critical_technologies(self):
        """Import critical technology definitions"""

        logger.info("Importing critical technologies...")

        critical_techs = [
            ('5G', '5G/6G Telecommunications', True, True, 9, 7),
            ('AI', 'Artificial Intelligence/ML', True, True, 10, 8),
            ('QUANTUM', 'Quantum Computing', True, True, 8, 6),
            ('SEMI', 'Semiconductors', True, True, 9, 7),
            ('BIOTECH', 'Biotechnology', True, True, 8, 8),
            ('SPACE', 'Space Technology', True, True, 7, 7),
            ('CYBER', 'Cybersecurity', True, False, 8, 8),
            ('MATERIALS', 'Advanced Materials', True, True, 7, 6),
            ('NUCLEAR', 'Nuclear Technology', True, True, 6, 5),
            ('HYPERSONIC', 'Hypersonic Systems', True, True, 7, 4)
        ]

        for tech_id, name, is_critical, is_dual_use, china_level, eu_level in critical_techs:
            self.cursor.execute("""
            INSERT OR IGNORE INTO technologies
            (tech_id, technology_name, technology_category, is_critical, is_dual_use,
             china_activity_level, eu_activity_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tech_id, name, name, is_critical, is_dual_use, china_level, eu_level))

        self.conn.commit()
        logger.info("Critical technologies imported")

    def generate_import_report(self):
        """Generate import statistics report"""

        logger.info("\n" + "="*60)
        logger.info("DATA IMPORT SUMMARY")
        logger.info("="*60)

        for key, value in self.stats.items():
            logger.info(f"{key}: {value}")

        # Query current totals
        queries = [
            ("Total entities", "SELECT COUNT(*) FROM entities"),
            ("Chinese entities", "SELECT COUNT(*) FROM entities WHERE is_chinese = 1"),
            ("EU entities", "SELECT COUNT(*) FROM entities WHERE is_european = 1"),
            ("Collaborations", "SELECT COUNT(*) FROM collaborations"),
            ("China-related collaborations", "SELECT COUNT(*) FROM collaborations WHERE is_china_related = 1"),
            ("Patents", "SELECT COUNT(*) FROM patents"),
            ("Publications", "SELECT COUNT(*) FROM publications"),
            ("Risk indicators", "SELECT COUNT(*) FROM risk_indicators"),
            ("Critical technologies", "SELECT COUNT(*) FROM technologies WHERE is_critical = 1")
        ]

        logger.info("\nDatabase Totals:")
        for label, query in queries:
            self.cursor.execute(query)
            count = self.cursor.fetchone()[0]
            logger.info(f"  {label}: {count}")

    def run_import(self):
        """Run complete data import"""

        try:
            # Import EPO patents
            self.import_epo_patents()

            # Import OpenAIRE publications
            self.import_openaire_publications()

            # Import from existing databases
            self.import_existing_databases()

            # Import critical technologies
            self.import_critical_technologies()

            # Generate report
            self.generate_import_report()

            # Commit all changes
            self.conn.commit()
            logger.info("\nData import completed successfully")

        except Exception as e:
            logger.error(f"Import error: {e}")
            self.conn.rollback()

        finally:
            self.conn.close()

def main():
    importer = OSINTDataImporter()
    importer.run_import()

if __name__ == "__main__":
    main()
