#!/usr/bin/env python3
"""
Sophisticated Risk Scoring System for Chinese Entities
Based on multiple intelligence indicators and data sources
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RiskScoringSystem:
    def __init__(self):
        self.master_db = "F:/OSINT_WAREHOUSE/osint_master.db"

        # Define risk indicators and weights
        self.risk_indicators = {
            # Entity Lists (Highest Weight)
            'us_entity_list': 100,
            'eu_sanctions': 100,
            'mcf_entity': 90,  # Military-Civil Fusion
            'state_owned': 70,

            # Technology Criticality
            'quantum_computing': 80,
            'ai_ml_military': 85,
            'semiconductor_advanced': 75,
            '5g_6g_infrastructure': 70,
            'hypersonics': 90,
            'biotech_dual_use': 75,
            'space_technology': 70,

            # Behavioral Indicators
            'patent_surge': 40,  # >100% increase YoY
            'ownership_obfuscation': 60,
            'shell_company_network': 70,
            'rapid_acquisition': 50,

            # Network Connections
            'pla_university_link': 80,
            'defense_contractor_jv': 75,
            'belt_road_participant': 30,
            'thousand_talents': 60,

            # Geographic/Operational
            'xinjiang_operations': 50,
            'south_china_sea': 40,
            'critical_infrastructure': 65,

            # Financial Indicators
            'state_funding_ratio': 45,  # >50% state funding
            'rapid_growth': 35,  # >200% revenue growth
            'opaque_financing': 55
        }

        # Critical entities list (known high-risk)
        self.critical_entities = {
            # Telecom/5G
            'HUAWEI': ['mcf_entity', '5g_6g_infrastructure', 'us_entity_list'],
            'ZTE': ['mcf_entity', '5g_6g_infrastructure', 'us_entity_list'],

            # Surveillance
            'HIKVISION': ['us_entity_list', 'xinjiang_operations', 'critical_infrastructure'],
            'DAHUA': ['us_entity_list', 'xinjiang_operations'],
            'SENSETIME': ['us_entity_list', 'ai_ml_military'],
            'MEGVII': ['us_entity_list', 'ai_ml_military'],
            'IFLYTEK': ['us_entity_list', 'ai_ml_military'],
            'YITU': ['us_entity_list', 'ai_ml_military'],

            # Defense/Aerospace
            'AVIC': ['mcf_entity', 'state_owned', 'defense_contractor_jv'],
            'NORINCO': ['mcf_entity', 'state_owned', 'defense_contractor_jv'],
            'CASIC': ['mcf_entity', 'state_owned', 'space_technology'],
            'CASC': ['mcf_entity', 'state_owned', 'space_technology'],
            'CETC': ['mcf_entity', 'state_owned', 'defense_contractor_jv'],
            'CSSC': ['mcf_entity', 'state_owned', 'south_china_sea'],
            'CSIC': ['mcf_entity', 'state_owned', 'south_china_sea'],

            # Computing/AI
            'SUGON': ['us_entity_list', 'semiconductor_advanced'],
            'INSPUR': ['mcf_entity', 'semiconductor_advanced'],
            'PHYTIUM': ['us_entity_list', 'semiconductor_advanced'],
            'HYGON': ['us_entity_list', 'semiconductor_advanced'],

            # Nuclear/Energy
            'CGN': ['us_entity_list', 'state_owned', 'critical_infrastructure'],
            'CNNC': ['state_owned', 'critical_infrastructure'],

            # Universities (Seven Sons of National Defense)
            'BEIHANG UNIVERSITY': ['pla_university_link', 'mcf_entity'],
            'BEIJING INSTITUTE OF TECHNOLOGY': ['pla_university_link', 'mcf_entity'],
            'HARBIN INSTITUTE OF TECHNOLOGY': ['pla_university_link', 'mcf_entity'],
            'HARBIN ENGINEERING UNIVERSITY': ['pla_university_link', 'mcf_entity'],
            'NORTHWESTERN POLYTECHNICAL': ['pla_university_link', 'mcf_entity'],
            'NANJING UNIVERSITY OF AERONAUTICS': ['pla_university_link', 'mcf_entity'],
            'NANJING UNIVERSITY OF SCIENCE': ['pla_university_link', 'mcf_entity'],

            # Research Institutes
            'CHINESE ACADEMY OF SCIENCES': ['state_owned', 'quantum_computing', 'ai_ml_military'],
            'CHINA ACADEMY OF ENGINEERING PHYSICS': ['mcf_entity', 'hypersonics'],

            # Other High Risk
            'NUCTECH': ['us_entity_list', 'critical_infrastructure'],
            'BGI': ['biotech_dual_use', 'state_owned'],
            'HYTERA': ['us_entity_list', '5g_6g_infrastructure'],
            'DJI': ['critical_infrastructure', 'dual_use_concerns'],
            'BYTEDANCE': ['data_security_concerns'],
            'TENCENT': ['data_security_concerns'],
            'ALIBABA': ['critical_infrastructure', 'cloud_computing']
        }

    def create_risk_tables(self):
        """Create sophisticated risk assessment tables"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Main risk scoring table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_risk_scores (
                entity_name TEXT PRIMARY KEY,
                risk_score INTEGER,
                risk_level TEXT,
                risk_factors TEXT,
                data_sources TEXT,
                technology_areas TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Risk indicators table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_indicators (
                indicator_name TEXT PRIMARY KEY,
                weight INTEGER,
                category TEXT,
                description TEXT
            )
        """)

        # Insert risk indicators
        for indicator, weight in self.risk_indicators.items():
            category = self._get_indicator_category(indicator)
            cursor.execute("""
                INSERT OR REPLACE INTO risk_indicators
                (indicator_name, weight, category)
                VALUES (?, ?, ?)
            """, (indicator, weight, category))

        # Entity risk factors junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_risk_factors (
                entity_name TEXT,
                risk_indicator TEXT,
                evidence TEXT,
                source TEXT,
                confidence REAL,
                PRIMARY KEY (entity_name, risk_indicator)
            )
        """)

        conn.commit()
        conn.close()
        logging.info("Created risk scoring tables")

    def _get_indicator_category(self, indicator):
        """Categorize risk indicators"""
        categories = {
            'entity_list': ['us_entity_list', 'eu_sanctions'],
            'mcf': ['mcf_entity', 'state_owned', 'pla_university_link'],
            'technology': ['quantum_computing', 'ai_ml_military', 'semiconductor_advanced',
                          '5g_6g_infrastructure', 'hypersonics', 'biotech_dual_use', 'space_technology'],
            'behavioral': ['patent_surge', 'ownership_obfuscation', 'shell_company_network', 'rapid_acquisition'],
            'network': ['defense_contractor_jv', 'belt_road_participant', 'thousand_talents'],
            'geographic': ['xinjiang_operations', 'south_china_sea', 'critical_infrastructure'],
            'financial': ['state_funding_ratio', 'rapid_growth', 'opaque_financing']
        }

        for cat, indicators in categories.items():
            if indicator in indicators:
                return cat
        return 'other'

    def calculate_entity_risk(self, entity_name):
        """Calculate risk score for a specific entity"""
        risk_score = 0
        risk_factors = []

        # Check against critical entities
        entity_upper = entity_name.upper()
        for critical_entity, indicators in self.critical_entities.items():
            if critical_entity in entity_upper or entity_upper in critical_entity:
                for indicator in indicators:
                    if indicator in self.risk_indicators:
                        risk_score += self.risk_indicators[indicator]
                        risk_factors.append(indicator)

        # Additional pattern matching
        if 'UNIVERSITY' in entity_upper:
            risk_score += 20
            risk_factors.append('academic_institution')

        if any(term in entity_upper for term in ['INSTITUTE', 'ACADEMY', 'LABORATORY']):
            risk_score += 15
            risk_factors.append('research_institution')

        if any(term in entity_upper for term in ['CHINA', 'CHINESE', 'PRC']):
            risk_score += 10
            risk_factors.append('chinese_entity')

        # Determine risk level
        if risk_score >= 200:
            risk_level = 'CRITICAL'
        elif risk_score >= 100:
            risk_level = 'HIGH'
        elif risk_score >= 50:
            risk_level = 'MEDIUM'
        elif risk_score > 0:
            risk_level = 'LOW'
        else:
            risk_level = 'MINIMAL'

        return {
            'entity_name': entity_name,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors
        }

    def scan_all_entities(self):
        """Scan all entities in the database and calculate risk scores"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Get all unique entities from various sources
        entities = set()

        # From patents
        try:
            cursor.execute("SELECT DISTINCT company_name FROM patents WHERE company_name IS NOT NULL")
            entities.update([row[0] for row in cursor.fetchall()])
        except:
            pass

        # From SEC EDGAR
        try:
            cursor.execute("SELECT DISTINCT company_name FROM sec_edgar_chinese")
            entities.update([row[0] for row in cursor.fetchall()])
        except:
            pass

        # From CORDIS
        try:
            cursor.execute("SELECT DISTINCT org_name FROM cordis_chinese_orgs")
            entities.update([row[0] for row in cursor.fetchall()])
        except:
            pass

        logging.info(f"Scanning {len(entities)} unique entities")

        # Calculate risk for each entity
        high_risk_count = 0
        critical_count = 0

        for entity in entities:
            risk_data = self.calculate_entity_risk(entity)

            # Store in database
            cursor.execute("""
                INSERT OR REPLACE INTO entity_risk_scores
                (entity_name, risk_score, risk_level, risk_factors)
                VALUES (?, ?, ?, ?)
            """, (
                risk_data['entity_name'],
                risk_data['risk_score'],
                risk_data['risk_level'],
                json.dumps(risk_data['risk_factors'])
            ))

            if risk_data['risk_level'] == 'CRITICAL':
                critical_count += 1
            elif risk_data['risk_level'] == 'HIGH':
                high_risk_count += 1

        conn.commit()

        # Create enhanced view
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS china_risk_assessment AS
            SELECT
                ers.entity_name,
                ers.risk_score,
                ers.risk_level,
                ers.risk_factors,
                COUNT(DISTINCT cem.source) as source_count,
                GROUP_CONCAT(DISTINCT cem.source) as data_sources
            FROM entity_risk_scores ers
            LEFT JOIN china_entities_master cem ON ers.entity_name = cem.entity_name
            GROUP BY ers.entity_name
            ORDER BY ers.risk_score DESC
        """)

        conn.commit()
        conn.close()

        logging.info(f"Risk assessment complete:")
        logging.info(f"  - Critical risk entities: {critical_count}")
        logging.info(f"  - High risk entities: {high_risk_count}")
        logging.info(f"  - Total entities assessed: {len(entities)}")

        return {
            'total_entities': len(entities),
            'critical_risk': critical_count,
            'high_risk': high_risk_count
        }

if __name__ == "__main__":
    risk_system = RiskScoringSystem()
    risk_system.create_risk_tables()
    results = risk_system.scan_all_entities()
    print(f"\nRisk Assessment Results:")
    print(f"Total Entities: {results['total_entities']}")
    print(f"Critical Risk: {results['critical_risk']}")
    print(f"High Risk: {results['high_risk']}")
