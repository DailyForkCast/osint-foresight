#!/usr/bin/env python3
"""
Master Database Integration Script
Integrates all collected databases into the OSINT Warehouse
Following the MASTER_SQL_WAREHOUSE_GUIDE.md specifications
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import hashlib

class MasterWarehouseIntegrator:
    def __init__(self):
        # Master warehouse location as specified in guide
        self.warehouse_path = Path("F:/OSINT_WAREHOUSE/osint_research.db")
        self.warehouse_path.parent.mkdir(parents=True, exist_ok=True)

        # Source databases collected today
        self.source_databases = {
            'trade_historical': Path("F:/OSINT_Data/Trade_Facilities/historical_hs_codes/historical_trade_2010_2023_20250922_161544.db"),
            'trade_strategic': Path("F:/OSINT_Data/Trade_Facilities/strategic_hs_codes/strategic_trade_analysis_20250922.db"),
            'trade_critical': Path("F:/OSINT_Data/Trade_Facilities/critical_hs_codes/critical_trade_20250922_134317.db"),
            'gleif': Path("F:/OSINT_Data/GLEIF/databases/gleif_analysis_20250921.db"),
            'sanctions': Path("F:/OSINT_Data/OpenSanctions/processed/sanctions.db"),
            'trade_facilities': Path("F:/OSINT_Data/Trade_Facilities/databases/trade_facilities_20250921.db"),
            'uspto': Path("F:/OSINT_Data/USPTO/uspto_patents_20250922.db"),
            'wipo': Path("F:/OSINT_Data/WIPO_Brands/wipo_brands_20250922.db"),
            'companies_uk': Path("F:/OSINT_Data/CompaniesHouse_UK/uk_companies_20250922.db")
        }

    def detect_china_involvement(self, text):
        """Standard China detection function as per guide"""
        if not text:
            return 0.0

        text_lower = str(text).lower()

        # Strong indicators (return 0.9)
        strong = ['china', 'chinese', 'beijing', 'shanghai', 'tsinghua',
                  'huawei', 'cas', 'xinjiang', 'tibet', 'shenzhen', 'guangzhou',
                  'wuhan', 'hangzhou', 'alibaba', 'tencent', 'baidu']

        for term in strong:
            if term in text_lower:
                return 0.9

        # Medium indicators (return 0.5)
        medium = ['asia', 'sino-', 'prc', 'hong kong', 'macau']
        for term in medium:
            if term in text_lower:
                return 0.5

        return 0.0

    def create_warehouse_schema(self):
        """Create warehouse schema as per guide specifications"""
        conn = sqlite3.connect(self.warehouse_path)
        cursor = conn.cursor()

        # Enable WAL mode
        cursor.execute('PRAGMA journal_mode=WAL')

        print("Creating warehouse schema layers...")

        # 1. RAW LAYER - Immutable original data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_trade_data (
                record_id TEXT PRIMARY KEY,
                hs_code TEXT,
                description TEXT,
                year INTEGER,
                month INTEGER,
                imports_value REAL,
                exports_value REAL,
                dependency_ratio REAL,
                source_file TEXT,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_entity_data (
                lei TEXT PRIMARY KEY,
                legal_name TEXT,
                jurisdiction TEXT,
                entity_type TEXT,
                raw_json TEXT,
                source_file TEXT,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. STAGE LAYER - Cleaned and validated
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stage_trade (
                trade_id TEXT PRIMARY KEY,
                hs_code TEXT,
                product_category TEXT,
                period TEXT,
                imports_eur REAL,
                exports_eur REAL,
                trade_balance REAL,
                dependency_ratio REAL,
                china_dependency_flag BOOLEAN,
                validated_at TIMESTAMP
            )
        ''')

        # 3. CORE LAYER - Conformed facts and dimensions

        # Core fact: Trade flows
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS core_f_trade_flow (
                flow_id TEXT PRIMARY KEY,
                hs_code TEXT,
                product_desc TEXT,
                period_year INTEGER,
                period_month INTEGER,
                reporter_country TEXT DEFAULT 'EU27',
                partner_country TEXT DEFAULT 'CN',
                imports_value_eur REAL,
                exports_value_eur REAL,
                trade_balance_eur REAL,
                dependency_ratio REAL,
                involves_china BOOLEAN,
                is_strategic_product BOOLEAN,
                is_critical_dependency BOOLEAN,
                source_system TEXT,
                source_file TEXT,
                confidence_score REAL,
                retrieved_at TIMESTAMP,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Core fact: Collaborations (for future CORDIS/OpenAIRE)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS core_f_collaboration (
                collab_id TEXT PRIMARY KEY,
                project_name TEXT,
                project_type TEXT,
                start_date TEXT,
                end_date TEXT,
                total_budget REAL,
                eu_contribution REAL,
                has_chinese_partner BOOLEAN,
                china_collaboration_score REAL,
                partner_countries TEXT,
                technology_areas TEXT,
                source_system TEXT,
                source_file TEXT,
                confidence_score REAL,
                retrieved_at TIMESTAMP,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Core fact: Patents
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS core_f_patent (
                patent_id TEXT PRIMARY KEY,
                patent_number TEXT,
                patent_title TEXT,
                filing_date TEXT,
                grant_date TEXT,
                assignee_name TEXT,
                assignee_country TEXT,
                technology_category TEXT,
                cpc_codes TEXT,
                has_chinese_applicant BOOLEAN,
                china_involvement_score REAL,
                technology_transfer_risk TEXT,
                cited_by_count INTEGER,
                source_system TEXT,
                confidence_score REAL,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Core fact: Procurement
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS core_f_procurement (
                award_id TEXT PRIMARY KEY,
                contract_title TEXT,
                contracting_authority TEXT,
                vendor_name TEXT,
                vendor_country TEXT,
                contract_value_eur REAL,
                award_date TEXT,
                cpv_codes TEXT,
                has_chinese_vendor BOOLEAN,
                china_involvement_score REAL,
                supply_chain_risk TEXT,
                source_system TEXT,
                confidence_score REAL,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Core dimension: Organizations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS core_dim_organization (
                org_id TEXT PRIMARY KEY,
                org_name TEXT,
                org_type TEXT,
                country TEXT,
                city TEXT,
                lei TEXT,
                is_chinese_entity BOOLEAN,
                china_connection_score REAL,
                parent_org_id TEXT,
                sector TEXT,
                employee_count INTEGER,
                revenue_eur REAL,
                first_seen DATE,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Core dimension: Products
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS core_dim_product (
                product_id TEXT PRIMARY KEY,
                hs_code TEXT UNIQUE,
                product_name TEXT,
                product_category TEXT,
                is_strategic BOOLEAN,
                is_dual_use BOOLEAN,
                technology_level TEXT,
                substitutability TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 4. MARTS LAYER - Subject area views

        # Supply chain intelligence mart
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS marts_supply_chain (
                hs_code TEXT PRIMARY KEY,
                product_name TEXT,
                dependency_ratio_current REAL,
                dependency_ratio_2010 REAL,
                dependency_trend TEXT,
                alternative_suppliers INTEGER,
                switching_cost_estimate TEXT,
                strategic_importance TEXT,
                risk_level TEXT,
                mitigation_status TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Risk assessment mart
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS marts_risk_assessment (
                entity_id TEXT PRIMARY KEY,
                entity_name TEXT,
                entity_type TEXT,
                china_exposure_score REAL,
                sanctions_risk_score REAL,
                technology_risk_score REAL,
                supply_chain_risk_score REAL,
                composite_risk_score REAL,
                risk_classification TEXT,
                monitoring_priority INTEGER,
                last_assessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 5. OPS LAYER - Operations and quality

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ops_quality_results (
                check_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT,
                rule_name TEXT,
                passed BOOLEAN,
                metric_value REAL,
                failed_count INTEGER,
                total_count INTEGER,
                check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ops_false_negative_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_system TEXT,
                query_method TEXT,
                original_results INTEGER,
                corrected_results INTEGER,
                correction_factor REAL,
                notes TEXT,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ops_alert_history (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                severity TEXT,
                entity_id TEXT,
                alert_message TEXT,
                triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                resolution_notes TEXT
            )
        ''')

        # 6. RESEARCH LAYER - Reproducibility

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS research_session (
                session_id TEXT PRIMARY KEY,
                session_type TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                records_processed INTEGER,
                china_records_found INTEGER,
                confidence_avg REAL,
                notes TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS research_findings (
                finding_id TEXT PRIMARY KEY,
                finding_type TEXT,
                entity_involved TEXT,
                description TEXT,
                evidence TEXT,
                confidence_score REAL,
                impact_assessment TEXT,
                documented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                documented_by TEXT DEFAULT 'system'
            )
        ''')

        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trade_hs ON core_f_trade_flow(hs_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trade_china ON core_f_trade_flow(involves_china)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trade_critical ON core_f_trade_flow(is_critical_dependency)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_collab_china ON core_f_collaboration(has_chinese_partner)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patent_china ON core_f_patent(has_chinese_applicant)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_org_china ON core_dim_organization(is_chinese_entity)')

        conn.commit()
        conn.close()

        print(f"[OK] Warehouse schema created at: {self.warehouse_path}")

    def integrate_trade_data(self):
        """Integrate historical and strategic trade data"""
        print("\n[TRADE] Integrating trade data...")

        warehouse_conn = sqlite3.connect(self.warehouse_path)
        session_id = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        total_records = 0
        china_records = 0

        # Process historical trade data
        if self.source_databases['trade_historical'].exists():
            print(f"  Loading historical trade data...")
            source_conn = sqlite3.connect(self.source_databases['trade_historical'])

            # Load annual trade data
            query = '''
                SELECT * FROM annual_trade
                WHERE dependency_ratio IS NOT NULL
            '''
            df = pd.read_sql_query(query, source_conn)

            for _, row in df.iterrows():
                flow_id = hashlib.md5(f"{row['hs_code']}_{row['year']}".encode()).hexdigest()

                # Check for China dependency
                is_critical = row['dependency_ratio'] > 20
                involves_china = True  # EU-China trade data

                warehouse_conn.execute('''
                    INSERT OR REPLACE INTO core_f_trade_flow (
                        flow_id, hs_code, product_desc, period_year,
                        imports_value_eur, exports_value_eur, trade_balance_eur,
                        dependency_ratio, involves_china, is_strategic_product,
                        is_critical_dependency, source_system, confidence_score,
                        retrieved_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    flow_id,
                    row['hs_code'],
                    row['description'],
                    row['year'],
                    row['imports_value'],
                    row['exports_value'],
                    row['trade_balance'],
                    row['dependency_ratio'],
                    involves_china,
                    True,  # All tracked products are strategic
                    is_critical,
                    'Eurostat_Historical',
                    0.95,
                    datetime.now().isoformat()
                ))

                total_records += 1
                if is_critical:
                    china_records += 1

            source_conn.close()
            print(f"    Loaded {total_records} historical trade records")

        # Process strategic trade data
        if self.source_databases['trade_strategic'].exists():
            print(f"  Loading strategic trade analysis...")
            source_conn = sqlite3.connect(self.source_databases['trade_strategic'])

            # Load critical dependencies
            query = '''
                SELECT * FROM critical_dependencies
            '''
            df = pd.read_sql_query(query, source_conn)

            for _, row in df.iterrows():
                # Update supply chain mart
                warehouse_conn.execute('''
                    INSERT OR REPLACE INTO marts_supply_chain (
                        hs_code, product_name, dependency_ratio_current,
                        strategic_importance, risk_level
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    row['hs_code'],
                    row['description'],
                    row['dependency_ratio'],
                    row.get('strategic_importance', 'HIGH'),
                    'CRITICAL' if row['dependency_ratio'] > 20 else 'HIGH'
                ))

            source_conn.close()
            print(f"    Updated supply chain mart with critical dependencies")

        # Log session
        warehouse_conn.execute('''
            INSERT INTO research_session (
                session_id, session_type, start_time, records_processed,
                china_records_found, confidence_avg, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            'trade_integration',
            datetime.now().isoformat(),
            total_records,
            china_records,
            0.95,
            'Historical trade data 2010-2023 integration'
        ))

        warehouse_conn.commit()
        warehouse_conn.close()

        print(f"  [OK] Integrated {total_records} trade records ({china_records} critical)")

    def integrate_entity_data(self):
        """Integrate GLEIF and sanctions entity data"""
        print("\n Integrating entity data...")

        warehouse_conn = sqlite3.connect(self.warehouse_path)
        total_entities = 0
        china_entities = 0

        # Process GLEIF data
        if self.source_databases['gleif'].exists():
            print(f"  Loading GLEIF entities...")
            source_conn = sqlite3.connect(self.source_databases['gleif'])

            query = '''
                SELECT * FROM china_entities
                LIMIT 10000
            '''

            try:
                df = pd.read_sql_query(query, source_conn)

                for _, row in df.iterrows():
                    org_id = row.get('lei', hashlib.md5(row.get('legal_name', '').encode()).hexdigest())

                    china_score = self.detect_china_involvement(row.get('legal_name', ''))
                    is_chinese = china_score > 0.5 or 'CN' in str(row.get('legal_jurisdiction', ''))

                    warehouse_conn.execute('''
                        INSERT OR REPLACE INTO core_dim_organization (
                            org_id, org_name, org_type, country, lei,
                            is_chinese_entity, china_connection_score
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        org_id,
                        row.get('legal_name'),
                        row.get('entity_category'),
                        row.get('legal_jurisdiction', '')[:2],
                        row.get('lei'),
                        is_chinese,
                        china_score
                    ))

                    total_entities += 1
                    if is_chinese:
                        china_entities += 1

                source_conn.close()
                print(f"    Loaded {total_entities} GLEIF entities ({china_entities} Chinese)")
            except Exception as e:
                print(f"    Note: GLEIF table structure different than expected: {e}")
                source_conn.close()

        # Process sanctions data
        if self.source_databases['sanctions'].exists():
            print(f"  Loading sanctions entities...")
            source_conn = sqlite3.connect(self.source_databases['sanctions'])

            query = '''
                SELECT * FROM entities
                WHERE countries LIKE '%CN%' OR countries LIKE '%China%'
                LIMIT 5000
            '''

            try:
                df = pd.read_sql_query(query, source_conn)

                for _, row in df.iterrows():
                    entity_id = row.get('id', hashlib.md5(row.get('name', '').encode()).hexdigest())

                    # Create risk assessment
                    warehouse_conn.execute('''
                        INSERT OR REPLACE INTO marts_risk_assessment (
                            entity_id, entity_name, entity_type,
                            china_exposure_score, sanctions_risk_score,
                            composite_risk_score, risk_classification
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        entity_id,
                        row.get('name'),
                        row.get('schema'),
                        0.9,  # High China exposure (from sanctions list)
                        1.0,  # Maximum sanctions risk
                        0.95,  # High composite risk
                        'CRITICAL'
                    ))

                source_conn.close()
                print(f"    Loaded sanctions risk assessments")
            except Exception as e:
                print(f"    Note: Sanctions table structure different: {e}")
                source_conn.close()

        warehouse_conn.commit()
        warehouse_conn.close()

        print(f"   Integrated {total_entities} entities ({china_entities} China-related)")

    def integrate_facilities(self):
        """Integrate trade facilities data"""
        print("\n Integrating trade facilities...")

        warehouse_conn = sqlite3.connect(self.warehouse_path)

        if self.source_databases['trade_facilities'].exists():
            source_conn = sqlite3.connect(self.source_databases['trade_facilities'])

            query = '''
                SELECT COUNT(*) as china_facilities
                FROM facilities
                WHERE country_code = 'CN'
            '''

            try:
                result = source_conn.execute(query).fetchone()
                china_facilities = result[0] if result else 0

                # Log the integration
                warehouse_conn.execute('''
                    INSERT INTO research_findings (
                        finding_id, finding_type, description,
                        evidence, confidence_score
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    f"facilities_{datetime.now().strftime('%Y%m%d')}",
                    'infrastructure_mapping',
                    f'Identified {china_facilities} Chinese trade facilities',
                    'UN/LOCODE database',
                    0.99
                ))

                source_conn.close()
                print(f"   Mapped {china_facilities} Chinese trade facilities")
            except Exception as e:
                print(f"    Note: Facilities table structure different: {e}")
                source_conn.close()

        warehouse_conn.commit()
        warehouse_conn.close()

    def run_quality_checks(self):
        """Run data quality checks as per guide"""
        print("\n Running quality checks...")

        conn = sqlite3.connect(self.warehouse_path)

        # Check 1: China detection rate
        cursor = conn.execute('''
            SELECT
                COUNT(*) as total,
                SUM(involves_china) as china_count
            FROM core_f_trade_flow
        ''')
        result = cursor.fetchone()
        total, china_count = result if result else (0, 0)
        detection_rate = (china_count / max(total, 1)) * 100

        conn.execute('''
            INSERT INTO ops_quality_results (
                rule_id, rule_name, passed, metric_value, total_count
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            'china_detection_trade',
            'China Trade Detection Rate',
            detection_rate > 5,
            detection_rate,
            total
        ))

        print(f"  China detection rate: {detection_rate:.1f}%")

        # Check 2: Critical dependencies
        cursor = conn.execute('''
            SELECT COUNT(*) FROM core_f_trade_flow
            WHERE is_critical_dependency = 1
        ''')
        critical_count = cursor.fetchone()[0]

        print(f"  Critical dependencies found: {critical_count}")

        # Check 3: Data freshness
        cursor = conn.execute('''
            SELECT MAX(retrieved_at) as latest FROM core_f_trade_flow
        ''')
        latest = cursor.fetchone()[0]
        print(f"  Latest data timestamp: {latest}")

        conn.commit()
        conn.close()

    def generate_summary_report(self):
        """Generate integration summary"""
        print("\n INTEGRATION SUMMARY REPORT")
        print("=" * 60)

        conn = sqlite3.connect(self.warehouse_path)

        # Count records by table
        tables = [
            'core_f_trade_flow',
            'core_f_collaboration',
            'core_f_patent',
            'core_f_procurement',
            'core_dim_organization',
            'marts_supply_chain',
            'marts_risk_assessment'
        ]

        for table in tables:
            cursor = conn.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]

            # Get China-related count where applicable
            china_count = 0
            if table == 'core_f_trade_flow':
                cursor = conn.execute(f'SELECT COUNT(*) FROM {table} WHERE involves_china = 1')
                china_count = cursor.fetchone()[0]
            elif table == 'core_dim_organization':
                cursor = conn.execute(f'SELECT COUNT(*) FROM {table} WHERE is_chinese_entity = 1')
                china_count = cursor.fetchone()[0]

            if china_count > 0:
                print(f"{table}: {count:,} records ({china_count:,} China-related)")
            else:
                print(f"{table}: {count:,} records")

        # Get key metrics
        print("\n KEY INTELLIGENCE METRICS:")

        # Critical dependencies
        cursor = conn.execute('''
            SELECT COUNT(*) FROM core_f_trade_flow
            WHERE is_critical_dependency = 1
        ''')
        print(f"  Critical dependencies: {cursor.fetchone()[0]}")

        # High risk entities
        cursor = conn.execute('''
            SELECT COUNT(*) FROM marts_risk_assessment
            WHERE risk_classification = 'CRITICAL'
        ''')
        print(f"  Critical risk entities: {cursor.fetchone()[0]}")

        # Latest data year
        cursor = conn.execute('''
            SELECT MAX(period_year) FROM core_f_trade_flow
        ''')
        print(f"  Latest trade data year: {cursor.fetchone()[0]}")

        conn.close()

        print("\n INTEGRATION COMPLETE!")
        print(f" Warehouse location: {self.warehouse_path}")

    def run_integration(self):
        """Execute complete integration pipeline"""
        print("STARTING MASTER DATA WAREHOUSE INTEGRATION")
        print("=" * 60)
        print(f"Warehouse: {self.warehouse_path}")
        print("=" * 60)

        # Step 1: Create schema
        self.create_warehouse_schema()

        # Step 2: Integrate data sources
        self.integrate_trade_data()
        self.integrate_entity_data()
        self.integrate_facilities()

        # Step 3: Run quality checks
        self.run_quality_checks()

        # Step 4: Generate report
        self.generate_summary_report()

        return str(self.warehouse_path)

if __name__ == "__main__":
    integrator = MasterWarehouseIntegrator()
    warehouse_path = integrator.run_integration()
    print(f"\n Master warehouse ready at: {warehouse_path}")
    print(" Follow MASTER_SQL_WAREHOUSE_GUIDE.md for query examples")
