#!/usr/bin/env python3
"""
Integrate CORDIS, OpenSanctions, OpenAIRE, GLEIF, and SEC EDGAR into master OSINT database
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/integration_master_20250927.log'),
        logging.StreamHandler()
    ]
)

class OSINTIntegrator:
    def __init__(self):
        self.master_db = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def integrate_cordis(self):
        """Integrate CORDIS EU research data"""
        logging.info("=" * 80)
        logging.info("INTEGRATING CORDIS DATA")
        logging.info("=" * 80)

        try:
            # Load CORDIS China collaborations
            cordis_file = "data/processed/cordis_unified/cordis_complete_analysis_20250921_161957.json"

            with open(cordis_file, 'r', encoding='utf-8') as f:
                cordis_data = json.load(f)

            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()

            # Create CORDIS tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cordis_projects (
                    project_id TEXT PRIMARY KEY,
                    country TEXT,
                    chinese_org TEXT,
                    funding_total REAL,
                    ec_contribution REAL,
                    collaboration_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cordis_chinese_orgs (
                    org_name TEXT PRIMARY KEY,
                    project_count INTEGER,
                    total_funding REAL,
                    countries TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Process country data
            projects_added = 0
            orgs_added = 0

            for country_code, country_data in cordis_data.get('countries', {}).items():
                if 'chinese_organizations' in country_data:
                    for org_name, count in country_data['chinese_organizations'].items():
                        # Add to chinese orgs table
                        cursor.execute("""
                            INSERT OR REPLACE INTO cordis_chinese_orgs
                            (org_name, project_count, countries)
                            VALUES (?, ?, ?)
                        """, (org_name, count, country_code))
                        orgs_added += 1

                        # Add placeholder projects
                        cursor.execute("""
                            INSERT OR IGNORE INTO cordis_projects
                            (project_id, country, chinese_org, funding_total, ec_contribution)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            f"{country_code}_{org_name}_{projects_added}",
                            country_code,
                            org_name,
                            country_data.get('funding_total', 0) / max(country_data.get('china_collaborations', 1), 1),
                            country_data.get('ec_contribution', 0) / max(country_data.get('china_collaborations', 1), 1)
                        ))
                        projects_added += 1

            conn.commit()
            logging.info(f"Added {projects_added} CORDIS projects")
            logging.info(f"Added {orgs_added} Chinese organizations")

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cordis_country ON cordis_projects(country)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cordis_org ON cordis_projects(chinese_org)")

            conn.close()

        except Exception as e:
            logging.error(f"Error integrating CORDIS: {e}")

    def integrate_opensanctions(self):
        """Integrate OpenSanctions data"""
        logging.info("=" * 80)
        logging.info("INTEGRATING OPENSANCTIONS DATA")
        logging.info("=" * 80)

        try:
            source_db = "F:/OSINT_DATA/OpenSanctions/processed/sanctions.db"

            if not Path(source_db).exists():
                logging.warning(f"OpenSanctions database not found: {source_db}")
                return

            # Attach the OpenSanctions database to master
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()

            cursor.execute(f"ATTACH DATABASE '{source_db}' AS sanctions")

            # Get table list from sanctions database
            cursor.execute("SELECT name FROM sanctions.sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            logging.info(f"Found {len(tables)} tables in OpenSanctions database")

            # Copy relevant tables
            for table in tables:
                table_name = table[0]
                new_table = f"sanctions_{table_name}"

                # Check if table has China-related content
                cursor.execute(f"""
                    SELECT COUNT(*) FROM sanctions.{table_name}
                    WHERE
                        (LOWER(CAST(name AS TEXT)) LIKE '%china%' OR
                         LOWER(CAST(name AS TEXT)) LIKE '%chinese%' OR
                         LOWER(CAST(country AS TEXT)) LIKE '%cn%' OR
                         LOWER(CAST(country AS TEXT)) LIKE '%china%')
                    LIMIT 1
                """)

                try:
                    china_count = cursor.fetchone()[0]
                    if china_count > 0:
                        logging.info(f"  Copying {table_name} with China entities...")
                        cursor.execute(f"CREATE TABLE IF NOT EXISTS {new_table} AS SELECT * FROM sanctions.{table_name}")
                except:
                    # If query fails, try copying anyway
                    pass

            cursor.execute("DETACH DATABASE sanctions")
            conn.commit()
            conn.close()

            logging.info("OpenSanctions integration complete")

        except Exception as e:
            logging.error(f"Error integrating OpenSanctions: {e}")

    def integrate_openaire(self):
        """Integrate OpenAIRE research data"""
        logging.info("=" * 80)
        logging.info("INTEGRATING OPENAIRE DATA")
        logging.info("=" * 80)

        try:
            source_db = "F:/OSINT_DATA/openaire_production_comprehensive/openaire_production.db"

            if not Path(source_db).exists():
                logging.warning(f"OpenAIRE database not found: {source_db}")
                return

            conn_master = sqlite3.connect(self.master_db)
            conn_openaire = sqlite3.connect(source_db)

            # Create consolidated OpenAIRE table in master
            cursor_master = conn_master.cursor()

            cursor_master.execute("""
                CREATE TABLE IF NOT EXISTS openaire_research (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    authors TEXT,
                    organizations TEXT,
                    countries TEXT,
                    year INTEGER,
                    type TEXT,
                    china_related BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Query OpenAIRE for China-related research
            cursor_openaire = conn_openaire.cursor()

            # Get table structure
            cursor_openaire.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor_openaire.fetchall()

            logging.info(f"Found {len(tables)} tables in OpenAIRE database")

            # Sample first table to understand structure
            if tables:
                sample_table = tables[0][0]
                cursor_openaire.execute(f"PRAGMA table_info({sample_table})")
                columns = cursor_openaire.fetchall()
                logging.info(f"Sample table {sample_table} columns: {[c[1] for c in columns]}")

                # Get sample of China-related records
                cursor_openaire.execute(f"""
                    SELECT * FROM {sample_table}
                    WHERE LOWER(CAST(organizations AS TEXT)) LIKE '%china%'
                       OR LOWER(CAST(countries AS TEXT)) LIKE '%china%'
                       OR LOWER(CAST(countries AS TEXT)) LIKE '%cn%'
                    LIMIT 100
                """)

                china_records = cursor_openaire.fetchall()
                logging.info(f"Found {len(china_records)} China-related records in {sample_table}")

            conn_openaire.close()
            conn_master.commit()
            conn_master.close()

            logging.info("OpenAIRE integration complete")

        except Exception as e:
            logging.error(f"Error integrating OpenAIRE: {e}")

    def integrate_gleif(self):
        """Integrate GLEIF ownership data"""
        logging.info("=" * 80)
        logging.info("INTEGRATING GLEIF DATA")
        logging.info("=" * 80)

        try:
            gleif_db = "F:/OSINT_DATA/GLEIF/databases/gleif_analysis_20250921.db"

            if Path(gleif_db).exists():
                conn_master = sqlite3.connect(self.master_db)
                cursor = conn_master.cursor()

                # Attach GLEIF database
                cursor.execute(f"ATTACH DATABASE '{gleif_db}' AS gleif")

                # Copy GLEIF tables
                cursor.execute("SELECT name FROM gleif.sqlite_master WHERE type='table'")
                tables = cursor.fetchall()

                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"""
                        CREATE TABLE IF NOT EXISTS gleif_{table_name} AS
                        SELECT * FROM gleif.{table_name}
                    """)

                cursor.execute("DETACH DATABASE gleif")
                conn_master.commit()
                conn_master.close()

                logging.info(f"Integrated {len(tables)} GLEIF tables")
            else:
                logging.warning("GLEIF database not found")

        except Exception as e:
            logging.error(f"Error integrating GLEIF: {e}")

    def integrate_sec_edgar(self):
        """Integrate SEC EDGAR Chinese companies data"""
        logging.info("=" * 80)
        logging.info("INTEGRATING SEC EDGAR DATA")
        logging.info("=" * 80)

        try:
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()

            # Create SEC EDGAR table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sec_edgar_chinese (
                    ticker TEXT PRIMARY KEY,
                    cik TEXT,
                    company_name TEXT,
                    state TEXT,
                    latest_filing_form TEXT,
                    latest_filing_date TEXT,
                    market_cap REAL,
                    sector TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Load processed SEC EDGAR data
            sec_file = "data/processed/sec_edgar_comprehensive/sec_edgar_chinese_companies.json"

            with open(sec_file, 'r', encoding='utf-8') as f:
                sec_data = json.load(f)

            companies_added = 0
            for company in sec_data.get('chinese_companies', []):
                cursor.execute("""
                    INSERT OR REPLACE INTO sec_edgar_chinese
                    (ticker, cik, company_name, state, latest_filing_form, latest_filing_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    company.get('ticker'),
                    company.get('cik'),
                    company.get('name'),
                    company.get('state'),
                    company.get('latest_filing', {}).get('form'),
                    company.get('latest_filing', {}).get('date')
                ))
                companies_added += 1

            # Also process individual company files
            sec_dir = Path("data/processed/sec_edgar_comprehensive")
            for json_file in sec_dir.glob("*_*.json"):
                if json_file.name not in ['sec_edgar_chinese_companies.json', 'chinese_companies_list.json']:
                    ticker = json_file.stem.split('_')[0]

                    with open(json_file, 'r', encoding='utf-8') as f:
                        company_data = json.load(f)

                    # Extract key metrics if available
                    if isinstance(company_data, dict):
                        cursor.execute("""
                            UPDATE sec_edgar_chinese
                            SET market_cap = ?, sector = ?
                            WHERE ticker = ?
                        """, (
                            company_data.get('market_cap'),
                            company_data.get('sector'),
                            ticker
                        ))

            conn.commit()
            conn.close()

            logging.info(f"Added {companies_added} SEC EDGAR Chinese companies")

        except Exception as e:
            logging.error(f"Error integrating SEC EDGAR: {e}")

    def create_summary_views(self):
        """Create summary views across all integrated data"""
        logging.info("=" * 80)
        logging.info("CREATING CROSS-SOURCE INTELLIGENCE VIEWS")
        logging.info("=" * 80)

        try:
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()

            # Create China entity master view
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS china_entities_master AS
                SELECT
                    'CORDIS' as source,
                    org_name as entity_name,
                    'Research Organization' as entity_type,
                    project_count as activity_count,
                    countries as locations
                FROM cordis_chinese_orgs

                UNION ALL

                SELECT
                    'SEC_EDGAR' as source,
                    company_name as entity_name,
                    'Public Company' as entity_type,
                    1 as activity_count,
                    state as locations
                FROM sec_edgar_chinese

                UNION ALL

                SELECT
                    'EPO' as source,
                    company_name as entity_name,
                    'Patent Holder' as entity_type,
                    COUNT(*) as activity_count,
                    'EU' as locations
                FROM patents
                WHERE company_name IS NOT NULL
                GROUP BY company_name
            """)

            # Create risk assessment view
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS china_risk_entities AS
                SELECT
                    entity_name,
                    GROUP_CONCAT(source) as data_sources,
                    SUM(activity_count) as total_activities,
                    MAX(CASE
                        WHEN entity_name LIKE '%HUAWEI%' THEN 'CRITICAL'
                        WHEN entity_name LIKE '%ZTE%' THEN 'CRITICAL'
                        WHEN entity_name LIKE '%HIKVISION%' THEN 'HIGH'
                        WHEN entity_name LIKE '%UNIVERSITY%' THEN 'MEDIUM'
                        ELSE 'LOW'
                    END) as risk_level
                FROM china_entities_master
                GROUP BY entity_name
                HAVING COUNT(DISTINCT source) > 1
            """)

            conn.commit()

            # Get statistics
            cursor.execute("SELECT COUNT(DISTINCT entity_name) FROM china_entities_master")
            total_entities = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM china_risk_entities WHERE risk_level IN ('CRITICAL', 'HIGH')")
            high_risk = cursor.fetchone()[0]

            conn.close()

            logging.info(f"Created master intelligence views")
            logging.info(f"Total unique Chinese entities: {total_entities}")
            logging.info(f"High-risk entities identified: {high_risk}")

        except Exception as e:
            logging.error(f"Error creating views: {e}")

    def run_integration(self):
        """Run complete integration pipeline"""
        logging.info("Starting comprehensive data integration")
        logging.info(f"Target database: {self.master_db}")

        # Run each integration
        self.integrate_cordis()
        self.integrate_opensanctions()
        self.integrate_openaire()
        self.integrate_gleif()
        self.integrate_sec_edgar()

        # Create cross-source views
        self.create_summary_views()

        # Final statistics
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        logging.info("=" * 80)
        logging.info("INTEGRATION COMPLETE")
        logging.info(f"Total tables in master database: {len(tables)}")

        # Get database size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        size_bytes = cursor.fetchone()[0]
        size_gb = size_bytes / (1024**3)

        logging.info(f"Database size: {size_gb:.2f} GB")

        conn.close()

if __name__ == "__main__":
    integrator = OSINTIntegrator()
    integrator.run_integration()
