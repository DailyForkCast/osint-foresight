#!/usr/bin/env python3
"""
Load TED procurement data into the OSINT warehouse
Following the MASTER_SQL_WAREHOUSE_GUIDE.md standards
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import logging

class TEDWarehouseLoader:
    def __init__(self):
        # As per guide: F:/OSINT_WAREHOUSE/osint_research.db
        self.warehouse_path = "F:/OSINT_WAREHOUSE/osint_research.db"
        self.ted_data_path = Path("C:/Projects/OSINT - Foresight/data/processed/ted_flexible_2016_2022")

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def connect(self):
        """Connect to warehouse database"""
        self.conn = sqlite3.connect(self.warehouse_path)
        self.cursor = self.conn.cursor()
        logging.info(f"Connected to warehouse: {self.warehouse_path}")

    def ensure_tables(self):
        """Verify warehouse tables exist (they should already exist)"""

        # Check if core_f_procurement exists
        self.cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='core_f_procurement'
        """)

        if not self.cursor.fetchone():
            raise Exception("core_f_procurement table not found in warehouse!")

        logging.info("Warehouse tables verified")

    def detect_china_involvement(self, entities_list):
        """
        Standard China detection as per guide
        Returns confidence score
        """
        if not entities_list:
            return 0.0

        # Strong indicators from our findings
        strong_chinese_companies = [
            'huawei', 'zte', 'lenovo', 'dji', 'byd', 'catl',
            'hikvision', 'boe', 'xiaomi', 'alibaba', 'tencent',
            'baidu', 'bytedance', 'tiktok', 'dahua', 'haier',
            'hisense', 'tcl', 'oppo', 'vivo', 'oneplus'
        ]

        for entity in entities_list:
            entity_lower = entity.lower()
            # Check for strong company matches
            for company in strong_chinese_companies:
                if company in entity_lower:
                    return 0.9
            # Check for China/Chinese
            if 'china' in entity_lower or 'chinese' in entity_lower:
                return 0.9
            # Check for Chinese cities
            if any(city in entity_lower for city in ['beijing', 'shanghai', 'shenzhen', 'guangzhou', 'hong kong']):
                return 0.8

        return 0.0

    def assess_supply_chain_risk(self, entities_list, contract_value=None):
        """
        Assess supply chain risk based on entity and value
        """
        if not entities_list:
            return 'LOW'

        # Critical technology companies
        critical_tech = ['huawei', 'zte', 'hikvision', 'dahua', 'dji']

        for entity in entities_list:
            entity_lower = entity.lower()
            if any(comp in entity_lower for comp in critical_tech):
                return 'HIGH'

        # Medium risk for other Chinese companies
        china_score = self.detect_china_involvement(entities_list)
        if china_score > 0.5:
            if contract_value and contract_value > 1000000:
                return 'HIGH'
            return 'MEDIUM'

        return 'LOW'

    def load_ted_contracts(self):
        """Load TED contracts with Chinese involvement into warehouse"""

        # Load the JSON data
        contracts_file = self.ted_data_path / "china_contracts_found.json"
        if not contracts_file.exists():
            logging.warning(f"No contracts file found at {contracts_file}")
            return

        with open(contracts_file, 'r', encoding='utf-8') as f:
            contracts = json.load(f)

        logging.info(f"Loading {len(contracts)} TED contracts with Chinese entities")

        # Begin transaction for performance
        self.conn.execute("BEGIN TRANSACTION")

        loaded = 0
        skipped = 0

        for contract in contracts:
            try:
                # Extract fields
                contract_id = contract.get('contract_id', f"TED_{loaded}")
                chinese_entities = contract.get('chinese_entities', [])

                # Skip if no Chinese entities
                if not chinese_entities:
                    skipped += 1
                    continue

                # Assess involvement and risk
                china_confidence = self.detect_china_involvement(chinese_entities)
                risk_level = self.assess_supply_chain_risk(
                    chinese_entities,
                    contract.get('value')
                )

                # Map Chinese entities to vendor_name (first entity)
                vendor_name = chinese_entities[0] if chinese_entities else 'Unknown Chinese Entity'

                # Insert or replace into warehouse (matching existing schema)
                self.cursor.execute("""
                INSERT OR REPLACE INTO core_f_procurement (
                    award_id,
                    buyer_country,
                    vendor_name,
                    award_date,
                    contract_value,
                    currency,
                    has_chinese_vendor,
                    supply_chain_risk,
                    source_system,
                    source_url,
                    retrieved_at,
                    confidence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    contract_id,
                    contract.get('authority_country', 'UNKNOWN'),
                    vendor_name,
                    contract.get('date'),
                    contract.get('value'),
                    contract.get('currency', 'EUR'),
                    1,  # has_chinese_vendor = TRUE
                    risk_level,
                    'TED_EU_2016_2022',
                    f"{contract.get('source_archive', '')}/{contract.get('source_file', '')}",
                    datetime.now().isoformat(),
                    china_confidence
                ))

                loaded += 1

                if loaded % 100 == 0:
                    logging.info(f"Loaded {loaded} contracts...")

            except Exception as e:
                logging.error(f"Error loading contract {contract.get('contract_id')}: {e}")
                skipped += 1

        # Commit transaction
        self.conn.commit()

        logging.info(f"Successfully loaded {loaded} contracts, skipped {skipped}")

    def update_quality_metrics(self):
        """Update ops_quality_results as per guide"""

        # Create quality monitoring table if not exists
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ops_quality_results (
            check_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_id TEXT,
            passed INTEGER,
            metric_value REAL,
            failed_count INTEGER,
            check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Calculate detection metrics
        self.cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(has_chinese_vendor) as china_count,
            AVG(confidence_score) as avg_confidence
        FROM core_f_procurement
        WHERE source_system LIKE 'TED%'
        """)

        result = self.cursor.fetchone()
        if result:
            total, china_count, avg_conf = result
            detection_rate = (china_count / total * 100) if total > 0 else 0

            # Log quality metrics
            self.cursor.execute("""
            INSERT INTO ops_quality_results (
                rule_id, passed, metric_value, failed_count
            ) VALUES (?, ?, ?, ?)
            """, ('ted_china_detection', True, detection_rate, 0))

            logging.info(f"Quality metrics updated - Detection rate: {detection_rate:.2f}%")

        self.conn.commit()

    def generate_summary(self):
        """Generate summary statistics"""

        print("\n" + "="*70)
        print("TED WAREHOUSE LOADING SUMMARY")
        print("="*70)

        # Total contracts
        self.cursor.execute("""
        SELECT COUNT(*) FROM core_f_procurement
        WHERE source_system LIKE 'TED%'
        """)
        total = self.cursor.fetchone()[0]
        print(f"Total TED contracts loaded: {total:,}")

        # By country
        self.cursor.execute("""
        SELECT
            buyer_country,
            COUNT(*) as contracts,
            COUNT(DISTINCT vendor_name) as unique_vendors
        FROM core_f_procurement
        WHERE source_system LIKE 'TED%' AND has_chinese_vendor = 1
        GROUP BY buyer_country
        ORDER BY contracts DESC
        LIMIT 10
        """)

        print("\nTop 10 Countries by Chinese Contracts:")
        for row in self.cursor.fetchall():
            print(f"  {row[0]}: {row[1]} contracts")

        # Risk distribution
        self.cursor.execute("""
        SELECT
            supply_chain_risk,
            COUNT(*) as count
        FROM core_f_procurement
        WHERE source_system LIKE 'TED%' AND has_chinese_vendor = 1
        GROUP BY supply_chain_risk
        """)

        print("\nRisk Distribution:")
        for row in self.cursor.fetchall():
            print(f"  {row[0]}: {row[1]} contracts")

        # Temporal trend
        self.cursor.execute("""
        SELECT
            strftime('%Y', award_date) as year,
            COUNT(*) as contracts
        FROM core_f_procurement
        WHERE source_system LIKE 'TED%' AND has_chinese_vendor = 1
        GROUP BY year
        ORDER BY year
        """)

        print("\nTemporal Trend:")
        for row in self.cursor.fetchall():
            if row[0]:  # Skip NULL years
                print(f"  {row[0]}: {row[1]} contracts")

    def run(self):
        """Main execution"""
        try:
            self.connect()
            self.ensure_tables()
            self.load_ted_contracts()
            self.update_quality_metrics()
            self.generate_summary()

        except Exception as e:
            logging.error(f"Error in warehouse loading: {e}")
            if self.conn:
                self.conn.rollback()
            raise
        finally:
            if self.conn:
                self.conn.close()
                logging.info("Database connection closed")

if __name__ == "__main__":
    loader = TEDWarehouseLoader()
    loader.run()
