#!/usr/bin/env python3
"""
Load Collected Data into Existing Warehouse
Integrates all our collected databases into F:/OSINT_WAREHOUSE/osint_research.db
Following the existing schema structure
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import hashlib

class WarehouseLoader:
    def __init__(self):
        self.warehouse_path = Path("F:/OSINT_WAREHOUSE/osint_research.db")

        # Source databases
        self.sources = {
            'trade_historical': Path("F:/OSINT_Data/Trade_Facilities/historical_hs_codes/historical_trade_2010_2023_20250922_161544.db"),
            'trade_strategic': Path("F:/OSINT_Data/Trade_Facilities/strategic_hs_codes/strategic_trade_analysis_20250922.db"),
            'gleif': Path("F:/OSINT_Data/GLEIF/databases/gleif_analysis_20250921.db"),
            'sanctions': Path("F:/OSINT_Data/OpenSanctions/processed/sanctions.db"),
            'facilities': Path("F:/OSINT_Data/Trade_Facilities/databases/trade_facilities_20250921.db")
        }

    def detect_china_involvement(self, text):
        """Standard China detection function as per guide"""
        if not text:
            return 0.0

        text_lower = str(text).lower()

        strong = ['china', 'chinese', 'beijing', 'shanghai', 'tsinghua',
                  'huawei', 'cas', 'xinjiang', 'tibet', 'shenzhen', 'guangzhou',
                  'wuhan', 'hangzhou', 'alibaba', 'tencent', 'baidu']

        for term in strong:
            if term in text_lower:
                return 0.9

        medium = ['asia', 'sino-', 'prc', 'hong kong', 'macau']
        for term in medium:
            if term in text_lower:
                return 0.5

        return 0.0

    def load_trade_data(self):
        """Load historical trade data into core_f_trade_flow"""
        print("\n[TRADE] Loading historical trade data...")

        if not self.sources['trade_historical'].exists():
            print("  Historical trade database not found")
            return 0

        warehouse_conn = sqlite3.connect(self.warehouse_path)
        source_conn = sqlite3.connect(self.sources['trade_historical'])

        # Load annual trade data
        query = '''
            SELECT hs_code, description, year, imports_value, exports_value,
                   trade_balance, dependency_ratio
            FROM annual_trade
            WHERE dependency_ratio IS NOT NULL AND year >= 2020
        '''

        df = pd.read_sql_query(query, source_conn)
        records_loaded = 0

        for _, row in df.iterrows():
            flow_id = hashlib.md5(f"EU_CN_{row['hs_code']}_{row['year']}_import".encode()).hexdigest()[:16]

            # Insert import flow
            warehouse_conn.execute('''
                INSERT OR REPLACE INTO core_f_trade_flow (
                    flow_id, reporter_country, partner_country, hs6_code,
                    year, flow_direction, trade_value_usd, is_strategic_product,
                    involves_china, source_system, retrieved_at, confidence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                flow_id,
                'EU27',
                'CN',
                row['hs_code'][:6],  # Take first 6 digits for HS6
                row['year'],
                'import',
                row['imports_value'] * 1.1,  # Convert EUR to USD approx
                True,
                True,
                'Eurostat_Historical',
                datetime.now().isoformat(),
                0.95
            ))

            records_loaded += 1

        source_conn.close()
        warehouse_conn.commit()
        warehouse_conn.close()

        print(f"  Loaded {records_loaded} trade flow records")
        return records_loaded

    def load_entity_data(self):
        """Load entity data into core_dim_organization"""
        print("\n[ENTITY] Loading entity data...")

        warehouse_conn = sqlite3.connect(self.warehouse_path)
        entities_loaded = 0

        # Load GLEIF data
        if self.sources['gleif'].exists():
            print("  Loading GLEIF entities...")
            source_conn = sqlite3.connect(self.sources['gleif'])

            try:
                # Try different table names
                for table_name in ['china_entities', 'lei_records', 'entities']:
                    try:
                        query = f'SELECT * FROM {table_name} LIMIT 1000'
                        df = pd.read_sql_query(query, source_conn)

                        for _, row in df.iterrows():
                            org_id = row.get('lei', hashlib.md5(str(row.get('legal_name', '')).encode()).hexdigest()[:16])

                            china_score = self.detect_china_involvement(row.get('legal_name', ''))
                            is_chinese = china_score > 0.5 or 'CN' in str(row.get('legal_jurisdiction', ''))

                            warehouse_conn.execute('''
                                INSERT OR REPLACE INTO core_dim_organization (
                                    org_id, org_name, org_type, country,
                                    is_chinese_entity, china_collaboration_score, source_system
                                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                org_id,
                                row.get('legal_name', ''),
                                row.get('entity_category', 'company'),
                                str(row.get('legal_jurisdiction', ''))[:2],
                                is_chinese,
                                china_score,
                                'GLEIF'
                            ))

                            entities_loaded += 1

                        print(f"    Loaded {len(df)} entities from {table_name}")
                        break

                    except Exception as e:
                        continue

            except Exception as e:
                print(f"    Could not load GLEIF data: {e}")

            source_conn.close()

        # Load sanctions data
        if self.sources['sanctions'].exists():
            print("  Loading sanctions entities...")
            source_conn = sqlite3.connect(self.sources['sanctions'])

            try:
                query = '''
                    SELECT id, name, schema, countries, birth_date, death_date
                    FROM entities
                    WHERE countries LIKE '%CN%' OR countries LIKE '%China%'
                    LIMIT 1000
                '''
                df = pd.read_sql_query(query, source_conn)

                for _, row in df.iterrows():
                    org_id = f"sanc_{row.get('id', '')[:10]}"

                    warehouse_conn.execute('''
                        INSERT OR REPLACE INTO core_dim_organization (
                            org_id, org_name, org_type, country,
                            is_chinese_entity, china_collaboration_score, source_system
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        org_id,
                        row.get('name', ''),
                        row.get('schema', 'sanctioned'),
                        'CN',
                        True,
                        1.0,  # Sanctioned entities have maximum China score
                        'OpenSanctions'
                    ))

                    entities_loaded += 1

                print(f"    Loaded {len(df)} sanctioned entities")

            except Exception as e:
                print(f"    Could not load sanctions data: {e}")

            source_conn.close()

        warehouse_conn.commit()
        warehouse_conn.close()

        print(f"  Total entities loaded: {entities_loaded}")
        return entities_loaded

    def load_product_data(self):
        """Load product definitions into core_dim_product"""
        print("\n[PRODUCT] Loading product data...")

        warehouse_conn = sqlite3.connect(self.warehouse_path)

        if self.sources['trade_strategic'].exists():
            source_conn = sqlite3.connect(self.sources['trade_strategic'])

            try:
                query = 'SELECT hs_code, description, category FROM hs_summary'
                df = pd.read_sql_query(query, source_conn)

                for _, row in df.iterrows():
                    warehouse_conn.execute('''
                        INSERT OR REPLACE INTO core_dim_product (
                            product_id, hs6_code, product_name, category,
                            is_strategic, source_system
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        row['hs_code'],
                        row['hs_code'][:6],
                        row['description'],
                        row['category'],
                        True,
                        'Strategic_Analysis'
                    ))

                print(f"  Loaded {len(df)} strategic products")
                source_conn.close()

            except Exception as e:
                print(f"  Could not load product data: {e}")

        warehouse_conn.commit()
        warehouse_conn.close()

    def update_warehouse_status(self):
        """Log the integration session"""
        print("\n[STATUS] Updating warehouse status...")

        conn = sqlite3.connect(self.warehouse_path)

        # Log research session
        session_id = f"data_load_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        conn.execute('''
            INSERT INTO research_session (
                session_id, session_type, start_time, notes
            ) VALUES (?, ?, ?, ?)
        ''', (
            session_id,
            'database_integration',
            datetime.now().isoformat(),
            'Integrated collected databases: trade, entities, products'
        ))

        # Count current records
        counts = {}
        for table in ['core_f_trade_flow', 'core_dim_organization', 'core_dim_product']:
            cursor = conn.execute(f'SELECT COUNT(*) FROM {table}')
            counts[table] = cursor.fetchone()[0]

        print(f"  Current warehouse status:")
        for table, count in counts.items():
            print(f"    {table}: {count:,} records")

        # Check China involvement
        cursor = conn.execute('''
            SELECT COUNT(*) FROM core_f_trade_flow WHERE involves_china = 1
        ''')
        china_trade = cursor.fetchone()[0]

        cursor = conn.execute('''
            SELECT COUNT(*) FROM core_dim_organization WHERE is_chinese_entity = 1
        ''')
        china_orgs = cursor.fetchone()[0]

        print(f"  China-related records:")
        print(f"    Trade flows: {china_trade:,}")
        print(f"    Organizations: {china_orgs:,}")

        conn.commit()
        conn.close()

    def run_integration(self):
        """Execute complete integration"""
        print("INTEGRATING COLLECTED DATA INTO WAREHOUSE")
        print("=" * 50)
        print(f"Target: {self.warehouse_path}")
        print("=" * 50)

        # Check if warehouse exists
        if not self.warehouse_path.exists():
            print("ERROR: Warehouse database not found!")
            return

        # Load data
        trade_records = self.load_trade_data()
        entity_records = self.load_entity_data()
        self.load_product_data()

        # Update status
        self.update_warehouse_status()

        print("\n[COMPLETE] Integration finished!")
        print(f"  Trade records: {trade_records}")
        print(f"  Entity records: {entity_records}")
        print(f"  Warehouse: {self.warehouse_path}")

if __name__ == "__main__":
    loader = WarehouseLoader()
    loader.run_integration()
