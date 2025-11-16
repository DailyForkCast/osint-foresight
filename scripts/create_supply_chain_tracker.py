#!/usr/bin/env python3
"""
create_supply_chain_tracker.py - Supply Chain Entity Tracking System

Creates a dedicated tracking system for Chinese commercial entities that are:
- Legitimate IT/equipment suppliers (Lenovo, etc.)
- Not strategic defense concerns
- Need monitoring for supply chain awareness
- Should be separated from TIER_1 strategic threats

Usage:
    python create_supply_chain_tracker.py --input importance_tier_sample_20251018_075329.csv

Output:
    - Creates supply_chain_entities table in database
    - Generates supply_chain_tracker.csv
    - Populates with entities like Lenovo, commercial IT suppliers
"""

import sqlite3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

class SupplyChainTracker:
    """Manages supply chain entity tracking"""

    # Known commercial IT suppliers that should be tracked separately
    KNOWN_SUPPLIERS = [
        'Lenovo',
        'Huawei Technologies USA',  # US subsidiary, commercial products
        'ZTE Corporation',
        'TP-Link',
        'Haier',
        'Hisense',
        'TCL',
        'Xiaomi',
        'DJI',
        'Hikvision',
        'Dahua Technology'
    ]

    # Categories for supply chain tracking
    SUPPLY_CHAIN_CATEGORIES = {
        'IT_EQUIPMENT': ['computer', 'laptop', 'server', 'printer', 'monitor', 'tablet'],
        'NETWORKING': ['router', 'switch', 'modem', 'network', 'telecommunications'],
        'CONSUMER_ELECTRONICS': ['phone', 'television', 'tv', 'camera', 'drone'],
        'APPLIANCES': ['refrigerator', 'washer', 'dryer', 'microwave', 'air conditioner'],
        'SURVEILLANCE': ['camera', 'cctv', 'surveillance', 'security system', 'monitoring'],
        'COMPONENTS': ['circuit board', 'chip', 'processor', 'memory', 'hard drive', 'ssd']
    }

    def __init__(self, db_path="F:/OSINT_WAREHOUSE/osint_master.db"):
        """Initialize tracker"""
        self.db_path = db_path
        self.conn = None

    def connect_db(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        print(f"[OK] Connected to database: {self.db_path}")

    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("[OK] Database connection closed")

    def create_supply_chain_table(self):
        """Create supply chain tracking table in database"""
        schema = """
        CREATE TABLE IF NOT EXISTS supply_chain_entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            entity_name TEXT NOT NULL,
            vendor_name TEXT,
            category TEXT,
            subcategory TEXT,
            award_description TEXT,
            award_amount REAL,
            contract_date TEXT,
            contracting_agency TEXT,
            country_code TEXT,

            -- Supply chain risk factors
            supply_chain_risk_level TEXT DEFAULT 'MEDIUM',
            is_known_supplier BOOLEAN DEFAULT 0,
            has_alternatives BOOLEAN DEFAULT 1,
            criticality TEXT DEFAULT 'STANDARD',

            -- Tracking metadata
            first_detected DATE,
            last_updated DATE DEFAULT CURRENT_TIMESTAMP,
            total_contracts INTEGER DEFAULT 1,
            total_value REAL,

            -- Notes
            notes TEXT,
            alternatives TEXT,

            UNIQUE(transaction_id)
        );

        CREATE INDEX IF NOT EXISTS idx_supply_chain_entity
        ON supply_chain_entities(entity_name);

        CREATE INDEX IF NOT EXISTS idx_supply_chain_category
        ON supply_chain_entities(category);

        CREATE INDEX IF NOT EXISTS idx_supply_chain_risk
        ON supply_chain_entities(supply_chain_risk_level);
        """

        cursor = self.conn.cursor()
        cursor.executescript(schema)
        self.conn.commit()
        print("[OK] Supply chain tracking table created")

    def categorize_entity(self, description, vendor_name):
        """Categorize entity based on products/services"""
        if pd.isna(description):
            description = ""

        text = f"{description} {vendor_name}".lower()

        for category, keywords in self.SUPPLY_CHAIN_CATEGORIES.items():
            for keyword in keywords:
                if keyword in text:
                    return category, keyword

        return 'GENERAL', None

    def assess_supply_chain_risk(self, entity_name, category):
        """Assess supply chain risk level"""

        # Check if known supplier
        is_known = any(supplier.lower() in entity_name.lower()
                      for supplier in self.KNOWN_SUPPLIERS)

        # Critical categories
        critical_categories = ['SURVEILLANCE', 'NETWORKING', 'IT_EQUIPMENT']

        if category in critical_categories:
            if is_known:
                risk_level = 'HIGH'
                criticality = 'CRITICAL'
            else:
                risk_level = 'MEDIUM'
                criticality = 'IMPORTANT'
        else:
            risk_level = 'MEDIUM'
            criticality = 'STANDARD'

        return {
            'risk_level': risk_level,
            'is_known_supplier': is_known,
            'criticality': criticality,
            'has_alternatives': True  # Assume alternatives exist unless specified
        }

    def identify_supply_chain_entities(self, csv_path):
        """Identify entities that should be tracked as supply chain"""
        print(f"\nIdentifying supply chain entities in: {csv_path}")

        df = pd.read_csv(csv_path)
        print(f"[OK] Loaded {len(df)} records")

        supply_chain_entities = []

        for idx, row in df.iterrows():
            recipient_name = str(row.get('Recipient_Name', ''))
            vendor_name = str(row.get('Vendor_Name', ''))
            description = str(row.get('Award_Description', ''))

            # Check if this is a supply chain entity
            # Criteria: TIER_2/3 commercial product suppliers
            current_tier = row.get('Importance_Tier')

            # Known suppliers are always supply chain
            is_known = any(supplier.lower() in recipient_name.lower() or
                          supplier.lower() in vendor_name.lower()
                          for supplier in self.KNOWN_SUPPLIERS)

            # Categorize
            category, subcategory = self.categorize_entity(description, vendor_name)

            # Commercial IT/electronics in TIER_2/3
            is_commercial = category in ['IT_EQUIPMENT', 'NETWORKING', 'CONSUMER_ELECTRONICS',
                                        'APPLIANCES', 'COMPONENTS']

            if is_known or (is_commercial and current_tier in ['TIER_2', 'TIER_3']):
                # Assess risk
                risk_assessment = self.assess_supply_chain_risk(recipient_name, category)

                entity = {
                    'transaction_id': row.get('Transaction_ID'),
                    'entity_name': recipient_name,
                    'vendor_name': vendor_name,
                    'category': category,
                    'subcategory': subcategory if subcategory else 'general',
                    'award_description': description[:500],
                    'award_amount': row.get('Award_Amount'),
                    'country_code': row.get('Country_Code'),
                    'supply_chain_risk_level': risk_assessment['risk_level'],
                    'is_known_supplier': risk_assessment['is_known_supplier'],
                    'has_alternatives': risk_assessment['has_alternatives'],
                    'criticality': risk_assessment['criticality'],
                    'first_detected': datetime.now().date().isoformat(),
                    'notes': f"Original tier: {current_tier}"
                }

                supply_chain_entities.append(entity)
                print(f"  >> {recipient_name}: {category} ({risk_assessment['risk_level']} risk)")

        return supply_chain_entities

    def populate_database(self, entities):
        """Add supply chain entities to database"""
        if not entities:
            print("No supply chain entities to add")
            return

        cursor = self.conn.cursor()

        insert_sql = """
        INSERT OR REPLACE INTO supply_chain_entities (
            transaction_id, entity_name, vendor_name, category, subcategory,
            award_description, award_amount, country_code,
            supply_chain_risk_level, is_known_supplier, has_alternatives,
            criticality, first_detected, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        for entity in entities:
            cursor.execute(insert_sql, (
                entity['transaction_id'],
                entity['entity_name'],
                entity['vendor_name'],
                entity['category'],
                entity['subcategory'],
                entity['award_description'],
                entity['award_amount'],
                entity['country_code'],
                entity['supply_chain_risk_level'],
                entity['is_known_supplier'],
                entity['has_alternatives'],
                entity['criticality'],
                entity['first_detected'],
                entity['notes']
            ))

        self.conn.commit()
        print(f"[OK] Added {len(entities)} entities to supply chain tracking database")

    def generate_excel_tracker(self, entities, output_path="analysis/supply_chain_tracker.xlsx"):
        """Generate Excel tracker with multiple sheets"""
        if not entities:
            print("No entities to export")
            return

        Path(output_path).parent.mkdir(exist_ok=True)

        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Main tracking sheet
            df_all = pd.DataFrame(entities)
            df_all.to_excel(writer, sheet_name='All Entities', index=False)

            # High-risk entities
            df_high_risk = df_all[df_all['supply_chain_risk_level'] == 'HIGH']
            df_high_risk.to_excel(writer, sheet_name='High Risk', index=False)

            # By category
            for category in df_all['category'].unique():
                df_category = df_all[df_all['category'] == category]
                sheet_name = category[:31]  # Excel sheet name limit
                df_category.to_excel(writer, sheet_name=sheet_name, index=False)

            # Known suppliers
            df_known = df_all[df_all['is_known_supplier'] == True]
            df_known.to_excel(writer, sheet_name='Known Suppliers', index=False)

        print(f"[OK] Excel tracker saved: {output_path}")

    def generate_summary_report(self, entities):
        """Print summary statistics"""
        if not entities:
            print("No entities to summarize")
            return

        df = pd.DataFrame(entities)

        print("\n" + "="*60)
        print("SUPPLY CHAIN TRACKER SUMMARY")
        print("="*60)

        print(f"\nTotal Entities: {len(df)}")

        print(f"\nBy Category:")
        for category, count in df['category'].value_counts().items():
            print(f"  {category}: {count}")

        print(f"\nBy Risk Level:")
        for risk, count in df['supply_chain_risk_level'].value_counts().items():
            print(f"  {risk}: {count}")

        print(f"\nKnown Suppliers: {df['is_known_supplier'].sum()}")

        if df['is_known_supplier'].sum() > 0:
            print(f"\nKnown Supplier List:")
            for name in df[df['is_known_supplier'] == True]['entity_name'].unique():
                print(f"  - {name}")

        total_value = df['award_amount'].sum()
        print(f"\nTotal Contract Value: ${total_value:,.2f}")

        print("\n" + "="*60)

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Create supply chain tracking system')
    parser.add_argument('--input',
                       default='data/processed/usaspending_manual_review/importance_tier_sample_20251018_075329.csv',
                       help='Input CSV file')
    parser.add_argument('--db',
                       default='F:/OSINT_WAREHOUSE/osint_master.db',
                       help='Database path')
    parser.add_argument('--output',
                       default='analysis/supply_chain_tracker.xlsx',
                       help='Output Excel file')

    args = parser.parse_args()

    print("="*60)
    print("SUPPLY CHAIN TRACKER SETUP")
    print("="*60)

    tracker = SupplyChainTracker(db_path=args.db)
    tracker.connect_db()

    # Create table
    tracker.create_supply_chain_table()

    # Identify entities
    entities = tracker.identify_supply_chain_entities(args.input)

    # Populate database
    tracker.populate_database(entities)

    # Generate Excel tracker
    tracker.generate_excel_tracker(entities, output_path=args.output)

    # Generate summary
    tracker.generate_summary_report(entities)

    tracker.close_db()

    print("\n[SUCCESS] Supply chain tracking system created!")
    print(f"\nDatabase table: supply_chain_entities")
    print(f"Excel tracker: {args.output}")

if __name__ == "__main__":
    main()
