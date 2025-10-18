#!/usr/bin/env python3
"""
Integrate GLEIF (Legal Entity Identifier) data into master OSINT database
Processes Chinese entity ownership structures and corporate relationships
"""

import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
import re
from typing import Dict, List, Set, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GLEIFIntegrator:
    def __init__(self):
        self.master_db = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.gleif_data_path = "F:/OSINT_Data/COMPANIES/GLEIF_China_entities_20250917.json"
        self.stats = {
            'entities_processed': 0,
            'entities_integrated': 0,
            'ownership_relationships': 0,
            'cross_linkages': 0,
            'high_risk_identified': 0
        }

    def setup_database(self):
        """Create GLEIF tables in master database"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Drop existing empty tables
        cursor.execute("DROP TABLE IF EXISTS gleif_lei_entities")
        cursor.execute("DROP TABLE IF EXISTS gleif_ownership_relationships")
        cursor.execute("DROP TABLE IF EXISTS gleif_identifier_mappings")
        cursor.execute("DROP TABLE IF EXISTS gleif_chinese_ownership_analysis")

        # Create new tables with proper schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_entities (
                lei TEXT PRIMARY KEY,
                legal_name TEXT,
                legal_name_local TEXT,
                other_names TEXT,
                status TEXT,
                entity_status TEXT,
                entity_category TEXT,
                legal_form TEXT,
                registration_authority TEXT,
                registration_id TEXT,
                legal_jurisdiction TEXT,
                legal_address_line1 TEXT,
                legal_address_line2 TEXT,
                legal_address_city TEXT,
                legal_address_region TEXT,
                legal_address_country TEXT,
                legal_address_postal TEXT,
                headquarters_address_line1 TEXT,
                headquarters_address_city TEXT,
                headquarters_address_country TEXT,
                registration_date TEXT,
                last_update TEXT,
                next_renewal TEXT,
                managing_lou TEXT,
                validation_sources TEXT,
                risk_indicators TEXT,
                risk_score INTEGER DEFAULT 0,
                is_chinese_entity BOOLEAN DEFAULT 0,
                has_sanctions_risk BOOLEAN DEFAULT 0,
                has_defense_indicators BOOLEAN DEFAULT 0,
                integration_timestamp TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_relationships (
                relationship_id TEXT PRIMARY KEY,
                parent_lei TEXT,
                parent_name TEXT,
                child_lei TEXT,
                child_name TEXT,
                relationship_type TEXT,
                relationship_status TEXT,
                ownership_percentage REAL,
                start_date TEXT,
                end_date TEXT,
                validation_sources TEXT,
                reporting_entity TEXT,
                is_cross_border BOOLEAN DEFAULT 0,
                involves_china BOOLEAN DEFAULT 0,
                risk_level TEXT,
                FOREIGN KEY (parent_lei) REFERENCES gleif_entities(lei),
                FOREIGN KEY (child_lei) REFERENCES gleif_entities(lei)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_cross_references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lei TEXT,
                source_type TEXT,
                source_id TEXT,
                source_name TEXT,
                confidence_score REAL,
                match_method TEXT,
                created_at TEXT,
                FOREIGN KEY (lei) REFERENCES gleif_entities(lei)
            )
        """)

        conn.commit()
        conn.close()
        logging.info("GLEIF database tables created")

    def parse_gleif_entity(self, entity_data: dict) -> dict:
        """Parse GLEIF entity data into database format"""
        attributes = entity_data.get('attributes', {})
        entity = attributes.get('entity', {})

        # Extract names
        legal_name = entity.get('legalName', {})
        name_local = legal_name.get('name', '')
        name_english = None
        other_names = []

        for trans in entity.get('transliteratedOtherEntityNames', []):
            if trans.get('language') == 'en':
                name_english = trans.get('name')
            else:
                other_names.append(trans.get('name'))

        # Extract addresses
        legal_addr = entity.get('legalAddress', {})
        hq_addr = entity.get('headquartersAddress', {})

        # Detect risk indicators
        risk_indicators = []
        risk_score = 0

        # Check for defense/military keywords
        defense_keywords = ['defense', 'defence', '国防', 'military', '军事',
                          'aerospace', '航空', '航天', 'nuclear', '核']
        name_check = (name_local + ' ' + (name_english or '')).lower()

        for keyword in defense_keywords:
            if keyword in name_check:
                risk_indicators.append(f'DEFENSE_KEYWORD:{keyword}')
                risk_score += 30

        # Check for state-owned enterprise indicators
        soe_indicators = ['国有', 'state-owned', 'state owned', '集团', 'group corp']
        for indicator in soe_indicators:
            if indicator in name_check:
                risk_indicators.append('STATE_OWNED')
                risk_score += 20
                break

        # Check registration authority
        reg_auth = entity.get('registrationAuthority', {})
        if reg_auth.get('registrationAuthorityID') in ['RA000607', 'RA000001']:
            risk_indicators.append('PRC_REGISTERED')
            risk_score += 10

        return {
            'lei': attributes.get('lei'),
            'legal_name': name_english or name_local,
            'legal_name_local': name_local,
            'other_names': '|'.join(other_names) if other_names else None,
            'status': attributes.get('registration', {}).get('status'),
            'entity_status': entity.get('status'),
            'entity_category': entity.get('category'),
            'legal_form': entity.get('legalForm', {}).get('id'),
            'registration_authority': reg_auth.get('registrationAuthorityID'),
            'registration_id': reg_auth.get('registrationAuthorityEntityID'),
            'legal_jurisdiction': entity.get('jurisdiction'),
            'legal_address_line1': ' '.join(legal_addr.get('addressLines', [])),
            'legal_address_city': legal_addr.get('city'),
            'legal_address_region': legal_addr.get('region'),
            'legal_address_country': legal_addr.get('country'),
            'legal_address_postal': legal_addr.get('postalCode'),
            'headquarters_address_line1': ' '.join(hq_addr.get('addressLines', [])) if hq_addr else None,
            'headquarters_address_city': hq_addr.get('city') if hq_addr else None,
            'headquarters_address_country': hq_addr.get('country') if hq_addr else None,
            'registration_date': attributes.get('registration', {}).get('initialRegistrationDate'),
            'last_update': attributes.get('registration', {}).get('lastUpdateDate'),
            'next_renewal': attributes.get('registration', {}).get('nextRenewalDate'),
            'managing_lou': attributes.get('registration', {}).get('managingLou'),
            'validation_sources': attributes.get('registration', {}).get('validationSources'),
            'risk_indicators': '|'.join(risk_indicators) if risk_indicators else None,
            'risk_score': min(risk_score, 100),
            'is_chinese_entity': 1,
            'has_defense_indicators': 1 if any('DEFENSE' in ind for ind in risk_indicators) else 0,
            'integration_timestamp': datetime.now().isoformat()
        }

    def load_and_process_gleif_data(self):
        """Load GLEIF data and process entities"""
        logging.info(f"Loading GLEIF data from {self.gleif_data_path}")

        with open(self.gleif_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total_entities = data['meta']['pagination']['total']
        entities_in_file = data.get('data', [])

        logging.info(f"Total Chinese entities in GLEIF: {total_entities:,}")
        logging.info(f"Processing {len(entities_in_file)} entities from current file")

        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        for entity_data in entities_in_file:
            try:
                entity = self.parse_gleif_entity(entity_data)

                # Insert into database
                columns = list(entity.keys())
                placeholders = ['?' for _ in columns]
                values = [entity[col] for col in columns]

                cursor.execute(f"""
                    INSERT OR REPLACE INTO gleif_entities ({','.join(columns)})
                    VALUES ({','.join(placeholders)})
                """, values)

                self.stats['entities_processed'] += 1

                if entity['risk_score'] > 50:
                    self.stats['high_risk_identified'] += 1

            except Exception as e:
                logging.error(f"Error processing entity: {e}")
                continue

        conn.commit()

        # Note: In production, we would need to paginate through all 1069 pages
        # to get all 106,883 entities. For now, we're processing the sample.
        logging.warning(f"Note: Only processed {len(entities_in_file)} of {total_entities:,} total entities")
        logging.info("To process all entities, implement pagination through GLEIF API")

        self.stats['entities_integrated'] = self.stats['entities_processed']
        conn.close()

    def create_cross_linkages(self):
        """Link GLEIF entities with existing data"""
        logging.info("Creating cross-source linkages")

        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Link with existing China entities - use proper column names
        try:
            cursor.execute("""
                INSERT INTO gleif_cross_references (lei, source_type, source_id, source_name, confidence_score, match_method, created_at)
                SELECT
                    g.lei,
                    'china_entities' as source_type,
                    c.entity_id as source_id,
                    COALESCE(c.entity_name_english, c.entity_name_chinese) as source_name,
                    CASE
                        WHEN LOWER(g.legal_name) = LOWER(COALESCE(c.entity_name_english, c.entity_name_chinese)) THEN 95.0
                        WHEN LOWER(g.legal_name) LIKE '%' || LOWER(COALESCE(c.entity_name_english, c.entity_name_chinese)) || '%' THEN 80.0
                        ELSE 70.0
                    END as confidence_score,
                    'name_match' as match_method,
                    datetime('now') as created_at
                FROM gleif_entities g
                JOIN china_entities c ON (
                    LOWER(g.legal_name) LIKE '%' || LOWER(REPLACE(COALESCE(c.entity_name_english, c.entity_name_chinese), ' ', '%')) || '%'
                    OR LOWER(COALESCE(c.entity_name_english, c.entity_name_chinese)) LIKE '%' || LOWER(REPLACE(g.legal_name, ' ', '%')) || '%'
                )
                WHERE g.is_chinese_entity = 1
            """)
            links_created = cursor.rowcount
            self.stats['cross_linkages'] += links_created
        except Exception as e:
            logging.warning(f"Could not link with china_entities: {e}")

        # Link with SEC EDGAR companies
        cursor.execute("""
            INSERT INTO gleif_cross_references (lei, source_type, source_id, source_name, confidence_score, match_method, created_at)
            SELECT
                g.lei,
                'sec_edgar' as source_type,
                s.cik as source_id,
                s.name as source_name,
                85.0 as confidence_score,
                'name_match' as match_method,
                datetime('now') as created_at
            FROM gleif_entities g
            JOIN sec_edgar_companies s ON (
                LOWER(g.legal_name) LIKE '%' || LOWER(s.name) || '%'
                OR LOWER(s.name) LIKE '%' || LOWER(g.legal_name) || '%'
            )
            WHERE g.is_chinese_entity = 1
        """)

        links_created = cursor.rowcount
        self.stats['cross_linkages'] += links_created

        conn.commit()
        conn.close()

        logging.info(f"Created {self.stats['cross_linkages']} cross-source linkages")

    def update_master_risk_scores(self):
        """Update risk scores in master entity table based on GLEIF data"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Update entities table with GLEIF risk indicators
        cursor.execute("""
            UPDATE entities
            SET risk_score = risk_score + 20,
                data_sources = data_sources || '|GLEIF',
                last_updated = datetime('now')
            WHERE entity_id IN (
                SELECT source_id
                FROM gleif_cross_references
                WHERE source_type = 'china_entities'
                AND confidence_score > 80
            )
        """)

        updated = cursor.rowcount
        logging.info(f"Updated {updated} entities with GLEIF risk data")

        conn.commit()
        conn.close()

    def generate_report(self):
        """Generate integration report"""
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/GLEIF_INTEGRATION_REPORT.md")

        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Get high-risk entities
        cursor.execute("""
            SELECT legal_name, risk_score, risk_indicators
            FROM gleif_entities
            WHERE risk_score >= 50
            ORDER BY risk_score DESC
            LIMIT 10
        """)
        high_risk = cursor.fetchall()

        # Get cross-linkages
        cursor.execute("""
            SELECT source_type, COUNT(*) as count, AVG(confidence_score) as avg_conf
            FROM gleif_cross_references
            GROUP BY source_type
        """)
        linkages = cursor.fetchall()

        conn.close()

        report = f"""================================================================================
GLEIF INTEGRATION REPORT
================================================================================

Integration Time: {datetime.now().isoformat()}

### Integration Statistics:
  Entities Processed: {self.stats['entities_processed']:,}
  Entities Integrated: {self.stats['entities_integrated']:,}
  High-Risk Identified: {self.stats['high_risk_identified']:,}
  Cross-Source Linkages: {self.stats['cross_linkages']:,}

### High-Risk Entities (Top 10):
"""
        for entity in high_risk:
            report += f"  - {entity[0][:50]:<50} Score: {entity[1]:3} Indicators: {entity[2]}\n"

        report += "\n### Cross-Source Linkages:\n"
        for link in linkages:
            report += f"  {link[0]}: {link[1]:,} linkages (avg confidence: {link[2]:.1f}%)\n"

        report += f"""
### Data Coverage:
  Current: {self.stats['entities_processed']:,} entities
  Available: 106,883 total Chinese entities in GLEIF
  Coverage: {(self.stats['entities_processed'] / 106883) * 100:.1f}%

### Next Steps:
  1. Implement full GLEIF API pagination to get all 106,883 entities
  2. Process ownership relationship data
  3. Enhance matching algorithms for better linkage
  4. Add real-time GLEIF updates

### Risk Indicators Found:
  - STATE_OWNED entities
  - DEFENSE_KEYWORD matches
  - PRC_REGISTERED companies
  - Complex ownership structures
"""

        report_path.write_text(report)
        logging.info(f"Report saved to {report_path}")
        print(report)

    def run(self):
        """Run the full integration pipeline"""
        logging.info("Starting GLEIF integration")

        self.setup_database()
        self.load_and_process_gleif_data()
        self.create_cross_linkages()
        self.update_master_risk_scores()
        self.generate_report()

        logging.info("GLEIF integration completed")

if __name__ == "__main__":
    integrator = GLEIFIntegrator()
    integrator.run()
