"""
Master Fusion Integrator - Combines all collected data sources
Integrates: Export Control, VC, Scientific, Trade, Academic data
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MasterFusionIntegrator:
    """Integrates all collected data sources into unified intelligence"""

    def __init__(self):
        self.f_drive = Path("F:/OSINT_DATA")
        self.output_dir = self.f_drive / "fusion_analysis"
        self.output_dir.mkdir(exist_ok=True)

        # Initialize fusion database
        self.db_path = self.output_dir / "master_fusion.db"
        self.init_database()

        # Data source directories
        self.source_dirs = {
            "export_control": self.f_drive / "EXPORT_CONTROL",
            "sanctions": self.f_drive / "SANCTIONS",
            "venture_capital": self.f_drive / "VENTURE_CAPITAL",
            "trade": self.f_drive / "TRADE_DATA",
            "academic": self.f_drive / "ACADEMIC",
            "standards": self.f_drive / "STANDARDS",
            "companies": self.f_drive / "COMPANIES",
            "supercomputers": self.f_drive / "SUPERCOMPUTERS",
            "dual_use": self.f_drive / "DUAL_USE"
        }

        self.china_indicators = {
            "companies": ["Huawei", "ZTE", "Alibaba", "Tencent", "Baidu", "ByteDance"],
            "universities": ["Tsinghua", "Beihang", "NUDT", "CAS", "Harbin"],
            "keywords": ["China", "Chinese", "PRC", "Beijing", "Shanghai"],
            "domains": [".cn", ".com.cn", ".org.cn"]
        }

    def init_database(self):
        """Initialize SQLite database for fusion tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Entity resolution table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                name TEXT,
                type TEXT,
                country TEXT,
                lei_code TEXT,
                cage_code TEXT,
                duns_number TEXT,
                cik_number TEXT,
                china_linked INTEGER DEFAULT 0,
                risk_score REAL DEFAULT 0,
                last_updated TEXT
            )
        ''')

        # Cross-source correlations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS correlations (
                correlation_id TEXT PRIMARY KEY,
                entity_id TEXT,
                source_type TEXT,
                source_file TEXT,
                data_point TEXT,
                china_indicator TEXT,
                confidence REAL,
                timestamp TEXT,
                FOREIGN KEY (entity_id) REFERENCES entities (entity_id)
            )
        ''')

        # Risk indicators
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_indicators (
                indicator_id TEXT PRIMARY KEY,
                entity_id TEXT,
                indicator_type TEXT,
                indicator_value TEXT,
                severity TEXT,
                source TEXT,
                detected_date TEXT,
                FOREIGN KEY (entity_id) REFERENCES entities (entity_id)
            )
        ''')

        conn.commit()
        conn.close()

    def integrate_export_control_data(self) -> Dict:
        """Integrate export control and sanctions lists"""
        logger.info("Integrating export control data...")

        entities_on_lists = []

        try:
            # Process Entity List
            entity_list_files = list(self.source_dirs["sanctions"].glob("*Entity_List*.json"))
            for file in entity_list_files:
                with open(file, 'r') as f:
                    data = json.load(f)
                    if 'results' in data:
                        for entity in data.get('results', []):
                            entities_on_lists.append({
                                "name": entity.get("name", ""),
                                "list": "Entity List",
                                "country": entity.get("country", ""),
                                "reason": entity.get("license_requirement", "")
                            })

            # Process Consolidated Screening List
            csl_files = list(self.source_dirs["sanctions"].glob("*Consolidated_Screening*.json"))
            for file in csl_files:
                with open(file, 'r') as f:
                    data = json.load(f)
                    if 'results' in data:
                        for entity in data.get('results', []):
                            entities_on_lists.append({
                                "name": entity.get("name", ""),
                                "list": entity.get("source", ""),
                                "country": entity.get("country", ""),
                                "reason": entity.get("remarks", "")
                            })

            # Store in database
            self._store_export_control_entities(entities_on_lists)

            return {
                "status": "success",
                "entities_found": len(entities_on_lists),
                "lists_processed": len(entity_list_files) + len(csl_files)
            }

        except Exception as e:
            logger.error(f"Export control integration error: {e}")
            return {"status": "failed", "error": str(e)}

    def integrate_venture_capital_data(self) -> Dict:
        """Integrate VC and investment data"""
        logger.info("Integrating venture capital data...")

        china_investments = []

        try:
            vc_files = list(self.source_dirs["venture_capital"].glob("*.json"))

            for file in vc_files:
                with open(file, 'r') as f:
                    data = json.load(f)

                    # Look for China-related investments
                    content = json.dumps(data).lower()
                    for keyword in ["china", "chinese", "beijing", "shanghai", "shenzhen"]:
                        if keyword in content:
                            china_investments.append({
                                "source_file": file.name,
                                "keyword_found": keyword,
                                "data": data
                            })
                            break

            return {
                "status": "success",
                "files_processed": len(vc_files),
                "china_related": len(china_investments)
            }

        except Exception as e:
            logger.error(f"VC integration error: {e}")
            return {"status": "failed", "error": str(e)}

    def integrate_academic_data(self) -> Dict:
        """Integrate academic papers and research data"""
        logger.info("Integrating academic data...")

        china_collaborations = []

        try:
            # Process Semantic Scholar data
            semantic_files = list(self.source_dirs["academic"].glob("*Semantic_Scholar*.json"))

            for file in semantic_files:
                with open(file, 'r') as f:
                    data = json.load(f)

                    if 'data' in data:
                        for paper in data.get('data', []):
                            # Check for China affiliations
                            authors = paper.get('authors', [])
                            for author in authors:
                                if author and 'china' in str(author).lower():
                                    china_collaborations.append({
                                        "title": paper.get('title'),
                                        "year": paper.get('year'),
                                        "venue": paper.get('venue'),
                                        "citations": paper.get('citationCount', 0)
                                    })
                                    break

            # Process arXiv data
            arxiv_files = list(self.source_dirs["academic"].glob("*arXiv*.xml"))
            logger.info(f"Found {len(arxiv_files)} arXiv files")

            return {
                "status": "success",
                "semantic_papers": len(semantic_files),
                "arxiv_papers": len(arxiv_files),
                "china_collaborations": len(china_collaborations)
            }

        except Exception as e:
            logger.error(f"Academic integration error: {e}")
            return {"status": "failed", "error": str(e)}

    def integrate_trade_data(self) -> Dict:
        """Integrate UN Comtrade and other trade data"""
        logger.info("Integrating trade data...")

        critical_commodities = []

        try:
            comtrade_files = list(self.source_dirs["trade"].glob("*UN_Comtrade*.json"))

            for file in comtrade_files:
                with open(file, 'r') as f:
                    data = json.load(f)

                    commodity = data.get('commodity_code')
                    description = data.get('description')

                    if commodity in ['9027', '9031', '8471', '8541']:
                        critical_commodities.append({
                            "code": commodity,
                            "description": description,
                            "data": data.get('data', {})
                        })

            return {
                "status": "success",
                "files_processed": len(comtrade_files),
                "critical_commodities": len(critical_commodities)
            }

        except Exception as e:
            logger.error(f"Trade integration error: {e}")
            return {"status": "failed", "error": str(e)}

    def integrate_company_data(self) -> Dict:
        """Integrate GLEIF and company registry data"""
        logger.info("Integrating company data...")

        chinese_entities = []

        try:
            gleif_files = list(self.source_dirs["companies"].glob("*GLEIF*.json"))

            for file in gleif_files:
                with open(file, 'r') as f:
                    data = json.load(f)

                    if 'data' in data:
                        for entity in data.get('data', []):
                            attributes = entity.get('attributes', {})
                            if attributes.get('entity', {}).get('legalAddress', {}).get('country') == 'CN':
                                chinese_entities.append({
                                    "lei": attributes.get('lei'),
                                    "name": attributes.get('entity', {}).get('legalName', {}).get('name'),
                                    "status": attributes.get('registration', {}).get('status')
                                })

            # Store in database
            self._store_company_entities(chinese_entities)

            return {
                "status": "success",
                "files_processed": len(gleif_files),
                "chinese_entities": len(chinese_entities)
            }

        except Exception as e:
            logger.error(f"Company integration error: {e}")
            return {"status": "failed", "error": str(e)}

    def cross_correlate_sources(self) -> Dict:
        """Perform cross-source correlation analysis"""
        logger.info("Performing cross-source correlation...")

        correlations = []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Find entities appearing in multiple sources
            cursor.execute('''
                SELECT e.entity_id, e.name, COUNT(DISTINCT c.source_type) as source_count
                FROM entities e
                JOIN correlations c ON e.entity_id = c.entity_id
                GROUP BY e.entity_id
                HAVING source_count > 1
            ''')

            multi_source_entities = cursor.fetchall()

            for entity_id, name, count in multi_source_entities:
                # Get all correlations for this entity
                cursor.execute('''
                    SELECT source_type, data_point, china_indicator, confidence
                    FROM correlations
                    WHERE entity_id = ?
                ''', (entity_id,))

                entity_correlations = cursor.fetchall()

                correlations.append({
                    "entity_id": entity_id,
                    "name": name,
                    "source_count": count,
                    "correlations": entity_correlations
                })

            return {
                "status": "success",
                "entities_correlated": len(correlations),
                "correlations": correlations[:10]  # Top 10
            }

        except Exception as e:
            logger.error(f"Correlation error: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            conn.close()

    def calculate_risk_scores(self) -> Dict:
        """Calculate composite risk scores for entities"""
        logger.info("Calculating risk scores...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Update risk scores based on indicators
            cursor.execute('''
                UPDATE entities
                SET risk_score = (
                    SELECT COALESCE(
                        SUM(CASE
                            WHEN ri.severity = 'CRITICAL' THEN 10
                            WHEN ri.severity = 'HIGH' THEN 7
                            WHEN ri.severity = 'MEDIUM' THEN 4
                            WHEN ri.severity = 'LOW' THEN 1
                            ELSE 0
                        END), 0
                    )
                    FROM risk_indicators ri
                    WHERE ri.entity_id = entities.entity_id
                )
            ''')

            # Get high-risk entities
            cursor.execute('''
                SELECT entity_id, name, risk_score, china_linked
                FROM entities
                WHERE risk_score > 0
                ORDER BY risk_score DESC
                LIMIT 20
            ''')

            high_risk = cursor.fetchall()

            conn.commit()

            return {
                "status": "success",
                "high_risk_entities": len(high_risk),
                "top_risks": [
                    {
                        "entity_id": r[0],
                        "name": r[1],
                        "risk_score": r[2],
                        "china_linked": bool(r[3])
                    }
                    for r in high_risk
                ]
            }

        except Exception as e:
            logger.error(f"Risk calculation error: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            conn.close()

    def _store_export_control_entities(self, entities: List[Dict]):
        """Store export control entities in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for entity in entities:
            entity_id = f"EC_{entity['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Insert entity
            cursor.execute('''
                INSERT OR REPLACE INTO entities (entity_id, name, type, country, china_linked, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (entity_id, entity['name'], 'EXPORT_CONTROL', entity.get('country', ''),
                  1 if 'china' in entity.get('country', '').lower() else 0,
                  datetime.now().isoformat()))

            # Add risk indicator
            cursor.execute('''
                INSERT INTO risk_indicators (indicator_id, entity_id, indicator_type, indicator_value, severity, source, detected_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (f"RI_{entity_id}", entity_id, 'EXPORT_CONTROL_LIST', entity['list'],
                  'HIGH', entity['list'], datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def _store_company_entities(self, entities: List[Dict]):
        """Store company entities in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for entity in entities:
            entity_id = f"LEI_{entity['lei']}"

            cursor.execute('''
                INSERT OR REPLACE INTO entities (entity_id, name, type, country, lei_code, china_linked, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (entity_id, entity['name'], 'COMPANY', 'CN', entity['lei'], 1, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def generate_fusion_report(self) -> Dict:
        """Generate comprehensive fusion intelligence report"""
        logger.info("Generating fusion intelligence report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "data_sources": {},
            "cross_correlations": {},
            "risk_assessment": {},
            "china_exposure": {},
            "recommendations": []
        }

        # Integrate all sources
        report["data_sources"]["export_control"] = self.integrate_export_control_data()
        report["data_sources"]["venture_capital"] = self.integrate_venture_capital_data()
        report["data_sources"]["academic"] = self.integrate_academic_data()
        report["data_sources"]["trade"] = self.integrate_trade_data()
        report["data_sources"]["companies"] = self.integrate_company_data()

        # Cross-correlate
        report["cross_correlations"] = self.cross_correlate_sources()

        # Calculate risks
        report["risk_assessment"] = self.calculate_risk_scores()

        # China exposure analysis
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM entities WHERE china_linked = 1
        ''')
        china_linked_count = cursor.fetchone()[0]

        cursor.execute('''
            SELECT COUNT(*) FROM correlations WHERE china_indicator IS NOT NULL
        ''')
        china_indicators_count = cursor.fetchone()[0]

        conn.close()

        report["china_exposure"]["entities_linked"] = china_linked_count
        report["china_exposure"]["indicators_found"] = china_indicators_count

        # Generate recommendations
        if china_linked_count > 100:
            report["recommendations"].append("HIGH ALERT: Significant China exposure detected across multiple data sources")

        if report["risk_assessment"].get("high_risk_entities", 0) > 10:
            report["recommendations"].append("Multiple high-risk entities identified - prioritize for enhanced due diligence")

        # Save report
        report_file = self.output_dir / f"fusion_intelligence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Fusion report saved: {report_file}")

        return report

    def run_full_integration(self) -> Dict:
        """Run complete integration pipeline"""
        logger.info("Starting full data fusion integration...")

        start_time = datetime.now()

        # Generate comprehensive report
        report = self.generate_fusion_report()

        # Print summary
        print("\n" + "=" * 60)
        print("MASTER FUSION INTEGRATION COMPLETE")
        print("=" * 60)

        for source, result in report["data_sources"].items():
            if result.get("status") == "success":
                print(f"[SUCCESS] {source}: Processed successfully")
            else:
                print(f"[FAILED] {source}: {result.get('error', 'Unknown error')}")

        print(f"\nChina Exposure:")
        print(f"  - Entities linked: {report['china_exposure']['entities_linked']}")
        print(f"  - Indicators found: {report['china_exposure']['indicators_found']}")

        print(f"\nRisk Assessment:")
        print(f"  - High-risk entities: {report['risk_assessment'].get('high_risk_entities', 0)}")

        if report["recommendations"]:
            print(f"\nKey Recommendations:")
            for rec in report["recommendations"]:
                print(f"  - {rec}")

        duration = (datetime.now() - start_time).total_seconds()
        print(f"\nCompleted in {duration:.2f} seconds")

        return report


if __name__ == "__main__":
    integrator = MasterFusionIntegrator()

    print("[MASTER FUSION INTEGRATOR]")
    print("Integrating all collected data sources...")
    print(f"Database: F:/OSINT_DATA/fusion_analysis/master_fusion.db\n")

    report = integrator.run_full_integration()

    print(f"\nFusion analysis complete!")
    print(f"Check F:/OSINT_DATA/fusion_analysis/ for detailed reports")
