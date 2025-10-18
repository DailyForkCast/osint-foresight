#!/usr/bin/env python3
"""
Integrate OpenAlex China data into master OSINT database
Creates entity linkages and updates risk scores
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class OpenAlexMasterIntegrator:
    def __init__(self):
        self.openalex_db = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.master_db = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.stats = {
            'entities_integrated': 0,
            'linkages_created': 0,
            'risk_scores_updated': 0,
            'new_critical_entities': 0
        }

    def create_master_tables(self):
        """Create comprehensive OpenAlex tables in master database"""
        logging.info("Creating OpenAlex tables in master database")

        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Main OpenAlex entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openalex_entities (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT,
                name TEXT,
                normalized_name TEXT,
                country_code TEXT,
                city TEXT,
                region TEXT,
                works_count INTEGER,
                cited_by_count INTEGER,
                h_index INTEGER,
                risk_indicators TEXT,
                risk_score INTEGER,
                data_source TEXT DEFAULT 'OpenAlex',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Entity linkage table for cross-source matching
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_linkages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                openalex_id TEXT,
                cordis_id TEXT,
                sanctions_id TEXT,
                openaire_id TEXT,
                sec_edgar_id TEXT,
                master_entity_id TEXT,
                confidence_score REAL,
                match_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Research metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openalex_research_metrics (
                entity_id TEXT PRIMARY KEY,
                total_publications INTEGER,
                total_citations INTEGER,
                h_index INTEGER,
                i10_index INTEGER,
                avg_citations_per_work REAL,
                international_collaboration_rate REAL,
                top_research_areas TEXT,
                key_collaborators TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Geographic intelligence table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS china_geographic_intelligence (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                region TEXT,
                country TEXT DEFAULT 'China',
                entity_count INTEGER,
                high_risk_count INTEGER,
                defense_count INTEGER,
                nuclear_count INTEGER,
                ai_count INTEGER,
                semiconductor_count INTEGER,
                total_works INTEGER,
                total_citations INTEGER,
                strategic_importance TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Master risk assessment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_risk_assessment (
                entity_id TEXT PRIMARY KEY,
                entity_name TEXT,
                risk_score INTEGER,
                risk_category TEXT,
                data_sources TEXT,
                openalex_indicators TEXT,
                cordis_involvement TEXT,
                sanctions_status TEXT,
                trade_volume REAL,
                patent_count INTEGER,
                collaboration_countries TEXT,
                assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_openalex_name ON openalex_entities(normalized_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_openalex_risk ON openalex_entities(risk_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_openalex_city ON openalex_entities(city)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_linkage_master ON entity_linkages(master_entity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_risk_score ON master_risk_assessment(risk_score)")

        conn.commit()
        conn.close()
        logging.info("Master tables created successfully")

    def normalize_name(self, name):
        """Normalize entity names for matching"""
        if not name:
            return ''

        # Convert to lowercase
        name = name.lower()

        # Remove common suffixes
        suffixes = [
            'university', 'institute', 'academy', 'college', 'center', 'centre',
            'laboratory', 'research', 'technology', 'science', 'engineering',
            'co.', 'ltd.', 'inc.', 'corp.', 'corporation', 'company', 'group'
        ]

        for suffix in suffixes:
            name = name.replace(suffix, '')

        # Remove special characters and extra spaces
        name = re.sub(r'[^\w\s]', ' ', name)
        name = ' '.join(name.split())

        return name.strip()

    def calculate_risk_score(self, indicators, works_count, citations):
        """Calculate comprehensive risk score"""
        score = 0

        # Base score from indicators
        if not indicators:
            return score

        indicators = indicators.upper()

        # Critical indicators
        if 'NUCLEAR' in indicators:
            score += 100
        if 'DEFENSE' in indicators or 'MILITARY' in indicators:
            score += 90
        if 'SEVEN_SONS' in indicators:
            score += 85
        if 'QUANTUM' in indicators:
            score += 80
        if 'SEMICONDUCTOR' in indicators:
            score += 75
        if 'AEROSPACE' in indicators:
            score += 70
        if 'CAS' in indicators:
            score += 70
        if 'AI' in indicators:
            score += 60

        # Adjust for research impact
        if citations > 1000000:
            score += 20
        elif citations > 500000:
            score += 15
        elif citations > 100000:
            score += 10
        elif citations > 50000:
            score += 5

        # Adjust for research volume
        if works_count > 100000:
            score += 15
        elif works_count > 50000:
            score += 10
        elif works_count > 10000:
            score += 5

        return min(score, 500)  # Cap at 500

    def integrate_openalex_data(self):
        """Transfer and enhance OpenAlex data to master database"""
        logging.info("Integrating OpenAlex data into master database")

        conn_source = sqlite3.connect(self.openalex_db)
        conn_master = sqlite3.connect(self.master_db)

        cursor_source = conn_source.cursor()
        cursor_master = conn_master.cursor()

        # Get all Chinese entities
        cursor_source.execute("""
            SELECT entity_id, entity_type, name, country_code, city, region,
                   works_count, cited_by_count, h_index, risk_indicators
            FROM import_openalex_china_entities
        """)

        entities = cursor_source.fetchall()
        logging.info(f"Processing {len(entities):,} OpenAlex entities")

        batch_data = []
        for entity in entities:
            entity_id, entity_type, name, country, city, region, works, citations, h_index, indicators = entity

            # Normalize name for matching
            normalized = self.normalize_name(name)

            # Calculate risk score
            risk_score = self.calculate_risk_score(indicators, works or 0, citations or 0)

            batch_data.append((
                entity_id, entity_type, name, normalized, country, city, region,
                works, citations, h_index, indicators, risk_score
            ))

            if len(batch_data) >= 1000:
                cursor_master.executemany("""
                    INSERT OR REPLACE INTO openalex_entities
                    (entity_id, entity_type, name, normalized_name, country_code,
                     city, region, works_count, cited_by_count, h_index,
                     risk_indicators, risk_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, batch_data)
                conn_master.commit()
                self.stats['entities_integrated'] += len(batch_data)
                logging.info(f"Integrated {self.stats['entities_integrated']:,} entities")
                batch_data = []

        # Insert remaining
        if batch_data:
            cursor_master.executemany("""
                INSERT OR REPLACE INTO openalex_entities
                (entity_id, entity_type, name, normalized_name, country_code,
                 city, region, works_count, cited_by_count, h_index,
                 risk_indicators, risk_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_data)
            conn_master.commit()
            self.stats['entities_integrated'] += len(batch_data)

        conn_source.close()
        conn_master.close()

        logging.info(f"Integrated {self.stats['entities_integrated']:,} total entities")

    def create_entity_linkages(self):
        """Link OpenAlex entities with other data sources"""
        logging.info("Creating entity linkages across data sources")

        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        linkages_cordis = 0
        linkages_sanctions = 0

        # Try to link with CORDIS projects (using org_name as ID since org_id doesn't exist)
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO entity_linkages
                (openalex_id, cordis_id, confidence_score, match_method)
                SELECT
                    o.entity_id,
                    c.org_name,
                    CASE
                        WHEN LOWER(o.name) = LOWER(c.org_name) THEN 1.0
                        WHEN o.normalized_name = LOWER(c.org_name) THEN 0.9
                        ELSE 0.7
                    END as confidence,
                    'name_match'
                FROM openalex_entities o
                INNER JOIN cordis_chinese_orgs c
                    ON (LOWER(o.name) LIKE '%' || LOWER(c.org_name) || '%'
                        OR LOWER(c.org_name) LIKE '%' || LOWER(o.name) || '%')
                WHERE o.country_code = 'CN'
            """)
            linkages_cordis = cursor.rowcount
            logging.info(f"Created {linkages_cordis} CORDIS linkages")
        except Exception as e:
            logging.warning(f"Could not create CORDIS linkages: {e}")

        # Try to link with sanctioned entities
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO entity_linkages
                (openalex_id, sanctions_id, confidence_score, match_method)
                SELECT
                    o.entity_id,
                    s.entity_id,
                    CASE
                        WHEN LOWER(o.name) = LOWER(s.name) THEN 0.95
                        WHEN o.normalized_name LIKE '%' || LOWER(s.name) || '%' THEN 0.8
                        ELSE 0.6
                    END as confidence,
                    'sanctions_match'
                FROM openalex_entities o
                INNER JOIN opensanctions_entities s
                    ON (o.normalized_name LIKE '%' || LOWER(s.name) || '%'
                        OR LOWER(s.aliases) LIKE '%' || LOWER(o.name) || '%')
                WHERE s.country = 'CN' OR s.country = 'China'
            """)
            linkages_sanctions = cursor.rowcount
            logging.info(f"Created {linkages_sanctions} sanctions linkages")
        except Exception as e:
            logging.warning(f"Could not create sanctions linkages: {e}")

        conn.commit()

        self.stats['linkages_created'] = linkages_cordis + linkages_sanctions

        conn.close()

    def update_geographic_intelligence(self):
        """Aggregate geographic intelligence"""
        logging.info("Updating geographic intelligence")

        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Aggregate by city
        cursor.execute("""
            INSERT OR REPLACE INTO china_geographic_intelligence
            (city, region, entity_count, high_risk_count, defense_count,
             nuclear_count, ai_count, semiconductor_count, total_works, total_citations)
            SELECT
                city,
                region,
                COUNT(*) as entity_count,
                SUM(CASE WHEN risk_score > 70 THEN 1 ELSE 0 END) as high_risk_count,
                SUM(CASE WHEN risk_indicators LIKE '%DEFENSE%' THEN 1 ELSE 0 END) as defense_count,
                SUM(CASE WHEN risk_indicators LIKE '%NUCLEAR%' THEN 1 ELSE 0 END) as nuclear_count,
                SUM(CASE WHEN risk_indicators LIKE '%AI%' THEN 1 ELSE 0 END) as ai_count,
                SUM(CASE WHEN risk_indicators LIKE '%SEMICONDUCTOR%' THEN 1 ELSE 0 END) as semiconductor_count,
                SUM(works_count) as total_works,
                SUM(cited_by_count) as total_citations
            FROM openalex_entities
            WHERE city != '' AND country_code = 'CN'
            GROUP BY city, region
            ORDER BY entity_count DESC
        """)

        cities_updated = cursor.rowcount

        # Mark strategic cities
        strategic_cities = ['Beijing', 'Shanghai', 'Shenzhen', 'Wuhan', 'Chengdu', 'Xi\'an']

        for city in strategic_cities:
            cursor.execute("""
                UPDATE china_geographic_intelligence
                SET strategic_importance = 'CRITICAL'
                WHERE city = ?
            """, (city,))

        conn.commit()
        conn.close()

        logging.info(f"Updated geographic intelligence for {cities_updated} cities")

    def create_master_risk_assessment(self):
        """Create unified risk assessment combining all sources"""
        logging.info("Creating master risk assessment")

        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Combine high-risk entities from all sources
        cursor.execute("""
            INSERT OR REPLACE INTO master_risk_assessment
            (entity_id, entity_name, risk_score, risk_category, data_sources,
             openalex_indicators, cordis_involvement, sanctions_status)
            SELECT
                o.entity_id,
                o.name,
                o.risk_score,
                CASE
                    WHEN o.risk_score >= 200 THEN 'CRITICAL'
                    WHEN o.risk_score >= 100 THEN 'HIGH'
                    WHEN o.risk_score >= 50 THEN 'MEDIUM'
                    ELSE 'LOW'
                END as risk_category,
                'OpenAlex' ||
                    CASE WHEN el.cordis_id IS NOT NULL THEN ',CORDIS' ELSE '' END ||
                    CASE WHEN el.sanctions_id IS NOT NULL THEN ',Sanctions' ELSE '' END as data_sources,
                o.risk_indicators,
                CASE WHEN el.cordis_id IS NOT NULL THEN 'Yes' ELSE 'No' END,
                CASE WHEN el.sanctions_id IS NOT NULL THEN 'SANCTIONED' ELSE 'Clear' END
            FROM openalex_entities o
            LEFT JOIN entity_linkages el ON o.entity_id = el.openalex_id
            WHERE o.risk_score > 0
        """)

        assessments_created = cursor.rowcount
        self.stats['risk_scores_updated'] = assessments_created

        # Count new critical entities
        cursor.execute("""
            SELECT COUNT(*) FROM master_risk_assessment
            WHERE risk_category = 'CRITICAL'
        """)
        self.stats['new_critical_entities'] = cursor.fetchone()[0]

        conn.commit()
        conn.close()

        logging.info(f"Created {assessments_created} risk assessments")

    def generate_integration_report(self):
        """Generate comprehensive integration report"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        report = []
        report.append("=" * 80)
        report.append("OPENALEX MASTER DATABASE INTEGRATION REPORT")
        report.append("=" * 80)
        report.append(f"\nIntegration Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Integration statistics
        report.append("\n### Integration Statistics:")
        report.append(f"  Entities Integrated: {self.stats['entities_integrated']:,}")
        report.append(f"  Cross-Source Linkages: {self.stats['linkages_created']:,}")
        report.append(f"  Risk Assessments Updated: {self.stats['risk_scores_updated']:,}")
        report.append(f"  New Critical Entities: {self.stats['new_critical_entities']:,}")

        # Top critical risk entities
        cursor.execute("""
            SELECT entity_name, risk_score, openalex_indicators, sanctions_status
            FROM master_risk_assessment
            WHERE risk_category = 'CRITICAL'
            ORDER BY risk_score DESC
            LIMIT 20
        """)
        critical_entities = cursor.fetchall()

        if critical_entities:
            report.append("\n### Top Critical Risk Entities:")
            for i, (name, score, indicators, sanctions) in enumerate(critical_entities, 1):
                sanctions_str = f" [SANCTIONED]" if sanctions == 'SANCTIONED' else ""
                report.append(f"  {i:2}. {name[:50]:<50} Score: {score:3} [{indicators}]{sanctions_str}")

        # Geographic distribution
        cursor.execute("""
            SELECT city, entity_count, high_risk_count, defense_count, nuclear_count
            FROM china_geographic_intelligence
            WHERE strategic_importance = 'CRITICAL'
            ORDER BY high_risk_count DESC
        """)
        strategic_cities = cursor.fetchall()

        if strategic_cities:
            report.append("\n### Strategic Cities Analysis:")
            for city, total, high_risk, defense, nuclear in strategic_cities:
                report.append(f"  {city:<15} Total: {total:4} High-Risk: {high_risk:3} Defense: {defense:2} Nuclear: {nuclear:2}")

        # Cross-source matches
        cursor.execute("""
            SELECT
                COUNT(DISTINCT openalex_id) as openalex_matches,
                COUNT(DISTINCT cordis_id) as cordis_matches,
                COUNT(DISTINCT sanctions_id) as sanctions_matches,
                AVG(confidence_score) as avg_confidence
            FROM entity_linkages
        """)
        matches = cursor.fetchone()

        if matches:
            report.append("\n### Cross-Source Intelligence Fusion:")
            report.append(f"  OpenAlex entities with matches: {matches[0]:,}")
            report.append(f"  CORDIS organizations linked: {matches[1]:,}")
            report.append(f"  Sanctioned entities linked: {matches[2]:,}")
            report.append(f"  Average match confidence: {matches[3]:.2%}" if matches[3] else "  Average match confidence: N/A")

        # Risk distribution
        cursor.execute("""
            SELECT risk_category, COUNT(*) as count
            FROM master_risk_assessment
            GROUP BY risk_category
            ORDER BY
                CASE risk_category
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    WHEN 'LOW' THEN 4
                END
        """)
        risk_dist = cursor.fetchall()

        if risk_dist:
            report.append("\n### Risk Distribution:")
            for category, count in risk_dist:
                report.append(f"  {category:<10} {count:,} entities")

        # Research impact summary
        cursor.execute("""
            SELECT
                SUM(works_count) as total_works,
                SUM(cited_by_count) as total_citations,
                COUNT(*) as institution_count,
                AVG(h_index) as avg_h_index
            FROM openalex_entities
            WHERE entity_type = 'institution' AND risk_score > 50
        """)
        research_impact = cursor.fetchone()

        if research_impact and research_impact[0]:
            report.append("\n### High-Risk Research Impact:")
            report.append(f"  Institutions: {research_impact[2]:,}")
            report.append(f"  Total Works: {research_impact[0]:,}")
            report.append(f"  Total Citations: {research_impact[1]:,}")
            report.append(f"  Average H-Index: {research_impact[3]:.1f}" if research_impact[3] else "  Average H-Index: N/A")

        conn.close()
        return "\n".join(report)

def main():
    """Execute complete integration"""
    integrator = OpenAlexMasterIntegrator()

    try:
        # Create tables
        integrator.create_master_tables()

        # Integrate data
        integrator.integrate_openalex_data()

        # Create linkages
        integrator.create_entity_linkages()

        # Update geographic intelligence
        integrator.update_geographic_intelligence()

        # Create risk assessments
        integrator.create_master_risk_assessment()

        # Generate report
        report = integrator.generate_integration_report()
        print(report)

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/OPENALEX_INTEGRATION_COMPLETE.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        logging.info(f"Integration complete. Report saved to {report_path}")

        return integrator.stats

    except Exception as e:
        logging.error(f"Integration failed: {e}")
        raise

if __name__ == "__main__":
    results = main()
    print(f"\n" + "=" * 80)
    print("Integration Summary:")
    for key, value in results.items():
        print(f"  {key}: {value:,}")
