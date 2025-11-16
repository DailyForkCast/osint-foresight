"""
Create Comprehensive Capital Flows Database
===========================================
Implement database schema for tracking all 5 capital flow patterns.

Author: OSINT Foresight Analysis
Date: 2025-10-25
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3
from datetime import datetime
from pathlib import Path
import re

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from dynamic SQL construction.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    # Check for valid characters only (alphanumeric + underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    # Check length (SQLite limit is 1024, we use 100 for safety)
    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    # Blacklist dangerous SQL keywords
    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier

class CapitalFlowsDatabaseCreator:
    def __init__(self):
        self.db_path = 'F:/OSINT_WAREHOUSE/osint_master.db'

    def create_comprehensive_flows_table(self):
        """Create main comprehensive capital flows table"""
        print("\n" + "="*70)
        print("CREATING COMPREHENSIVE CAPITAL FLOWS TABLE")
        print("="*70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Drop existing table if it exists (for clean rebuild)
        print("\n[1/4] Checking for existing table...")
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='china_capital_flows_comprehensive'
        """)
        if cursor.fetchone():
            print("   Table exists, dropping...")
            cursor.execute('DROP TABLE china_capital_flows_comprehensive')

        # Create new table
        print("[2/4] Creating new table schema...")
        cursor.execute('''
            CREATE TABLE china_capital_flows_comprehensive (
                -- Core Identification
                flow_id TEXT PRIMARY KEY,
                detection_date DATE,
                data_source TEXT,
                source_record_id TEXT,

                -- Flow Classification
                flow_pattern INTEGER,
                flow_direction TEXT,
                flow_concern_level TEXT,

                -- Western Entity
                western_entity_name TEXT,
                western_entity_country TEXT,
                western_entity_sector TEXT,
                western_entity_is_dual_use INTEGER,

                -- Chinese Entity
                chinese_entity_name TEXT,
                chinese_entity_type TEXT,
                chinese_entity_ownership TEXT,
                chinese_entity_prc_connections TEXT,

                -- Capital Details
                capital_amount_usd REAL,
                capital_currency TEXT,
                transaction_type TEXT,
                transaction_date DATE,
                ownership_stake_pct REAL,

                -- Validation Status
                validation_status TEXT,
                validation_date DATE,
                validation_method TEXT,
                validation_confidence TEXT,
                validation_notes TEXT,

                -- Intelligence Assessment
                technology_transfer_risk TEXT,
                strategic_concern TEXT,
                requires_monitoring INTEGER,
                alert_level TEXT,

                -- Metadata
                created_timestamp DATETIME,
                updated_timestamp DATETIME,
                analyst_notes TEXT
            )
        ''')

        # Create indexes
        print("[3/4] Creating indexes...")
        indexes = [
            ('idx_flow_pattern', 'flow_pattern'),
            ('idx_flow_concern', 'flow_concern_level'),
            ('idx_validation_status', 'validation_status'),
            ('idx_western_country', 'western_entity_country'),
            ('idx_dual_use', 'western_entity_is_dual_use'),
            ('idx_transaction_date', 'transaction_date'),
            ('idx_data_source', 'data_source'),
            ('idx_alert_level', 'alert_level')
        ]

        for idx_name, idx_column in indexes:
            # SECURITY: Validate identifiers before use in SQL
            safe_idx = validate_sql_identifier(idx_name)
            safe_col = validate_sql_identifier(idx_column)
            cursor.execute(f'''
                CREATE INDEX {safe_idx}
                ON china_capital_flows_comprehensive({safe_col})
            ''')
            print(f"   Created index: {idx_name}")

        conn.commit()
        print("[4/4] Table and indexes created successfully")

        # Verify
        cursor.execute('PRAGMA table_info(china_capital_flows_comprehensive)')
        columns = cursor.fetchall()
        print(f"\n✅ Table created with {len(columns)} columns")

        conn.close()

    def create_lookup_tables(self):
        """Create lookup tables for reference data"""
        print("\n" + "="*70)
        print("CREATING LOOKUP TABLES")
        print("="*70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Flow Patterns Reference
        print("\n[1/3] Creating flow_patterns_reference table...")
        cursor.execute('DROP TABLE IF EXISTS flow_patterns_reference')
        cursor.execute('''
            CREATE TABLE flow_patterns_reference (
                pattern_id INTEGER PRIMARY KEY,
                pattern_name TEXT,
                description TEXT,
                concern_level TEXT,
                example TEXT
            )
        ''')

        patterns = [
            (1, 'Chinese VC → US/EU Dual-Use Tech', 'Chinese venture capital directly funding Western dual-use technology companies', 'HIGH', 'WuXi Healthcare Ventures → Simcha Therapeutics'),
            (2, 'US/EU → Chinese VC Funds → Asia', 'Western investors funding Chinese VC funds that invest in Asia', 'LOW', 'US institutional investors → Sequoia China Fund IV'),
            (3, 'US/EU → China Markets', 'Western investors directly accessing Chinese markets', 'NONE', 'QFII China Total Return Fund'),
            (4, 'Chinese Companies → US/EU Capital', 'Chinese companies raising capital in Western markets', 'MEDIUM', 'Lotus Technology → NYSE listing'),
            (5, 'False Positives', 'Incorrectly detected as China-related', 'NONE', 'CASI Pharmaceuticals (US company with Beijing office)')
        ]

        cursor.executemany('''
            INSERT INTO flow_patterns_reference
            (pattern_id, pattern_name, description, concern_level, example)
            VALUES (?, ?, ?, ?, ?)
        ''', patterns)

        print(f"   Inserted {len(patterns)} flow patterns")

        # Known Chinese VC Firms Reference
        print("[2/3] Creating known_chinese_vc_firms table...")
        cursor.execute('DROP TABLE IF EXISTS known_chinese_vc_firms')
        cursor.execute('''
            CREATE TABLE known_chinese_vc_firms (
                firm_id INTEGER PRIMARY KEY AUTOINCREMENT,
                firm_name TEXT UNIQUE,
                alternate_names TEXT,
                firm_type TEXT,
                ownership_type TEXT,
                prc_connections TEXT,
                founded_year INTEGER,
                headquarters TEXT,
                aum_usd_billions REAL,
                focus_sectors TEXT,
                geographic_focus TEXT,
                notes TEXT,
                added_timestamp DATETIME
            )
        ''')

        # Insert major known Chinese VCs
        known_vcs = [
            ('Sequoia Capital China', 'Sequoia China', 'VC', 'PRIVATE', 'None publicly known', 2005, 'Beijing', None, 'Technology, Healthcare', 'China, Asia', 'Major US-China cross-border VC'),
            ('IDG Capital', 'IDG China', 'VC/PE', 'PRIVATE', 'None publicly known', 1992, 'Beijing', None, 'Technology, Media, Telecom', 'China, Global', 'One of first VCs in China'),
            ('Hillhouse Capital', 'HHCG, Hillhouse Investment', 'PE/VC', 'PRIVATE', 'None publicly known', 2005, 'Beijing', 60.0, 'Technology, Healthcare, Consumer', 'China, Asia', 'Large Asia-focused fund'),
            ('GGV Capital', 'GGV', 'VC', 'PRIVATE', 'None publicly known', 2000, 'Menlo Park & Shanghai', 9.2, 'Technology, Consumer', 'US, China cross-border', 'US-China cross-border focus'),
            ('Qiming Venture Partners', 'Qiming', 'VC', 'PRIVATE', 'None publicly known', 2006, 'Shanghai', 9.5, 'Technology, Healthcare', 'China, Asia', 'Healthcare and tech focus'),
            ('Matrix Partners China', 'Matrix China', 'VC', 'PRIVATE', 'None publicly known', 2008, 'Beijing & Shanghai', None, 'Technology, Consumer', 'China', 'Affiliate of Matrix Partners'),
            ('WuXi Healthcare Ventures', 'WuXi Ventures', 'CVC', 'CORPORATE', 'WuXi AppTec (public company)', 2017, 'Shanghai', None, 'Healthcare, Biotechnology', 'China, Global', 'Corporate VC of WuXi AppTec'),
            ('Tencent Investment', 'Tencent', 'CVC', 'CORPORATE', 'Tencent Holdings (public, PRC-based)', 2011, 'Shenzhen', None, 'Gaming, Social Media, Fintech', 'China, Global', 'Strategic investments'),
            ('Alibaba Capital', 'Alibaba Investment', 'CVC', 'CORPORATE', 'Alibaba Group (public, PRC-based)', 2014, 'Hangzhou', None, 'E-commerce, Logistics, Cloud', 'China, Global', 'Strategic investments'),
            ('Baidu Ventures', 'Baidu Capital', 'CVC', 'CORPORATE', 'Baidu Inc (public, PRC-based)', 2016, 'Beijing', None, 'AI, Autonomous Driving', 'China, Global', 'Focus on AI technologies')
        ]

        cursor.executemany('''
            INSERT INTO known_chinese_vc_firms
            (firm_name, alternate_names, firm_type, ownership_type, prc_connections,
             founded_year, headquarters, aum_usd_billions, focus_sectors, geographic_focus,
             notes, added_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [(vc[0], vc[1], vc[2], vc[3], vc[4], vc[5], vc[6], vc[7], vc[8], vc[9], vc[10], datetime.now()) for vc in known_vcs])

        print(f"   Inserted {len(known_vcs)} known Chinese VC firms")

        # Dual-Use Technology Sectors
        print("[3/3] Creating dual_use_sectors_reference table...")
        cursor.execute('DROP TABLE IF EXISTS dual_use_sectors_reference')
        cursor.execute('''
            CREATE TABLE dual_use_sectors_reference (
                sector_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sector_name TEXT UNIQUE,
                description TEXT,
                concern_level TEXT,
                keywords TEXT,
                examples TEXT
            )
        ''')

        sectors = [
            ('Artificial Intelligence', 'AI and machine learning technologies', 'HIGH', 'AI, machine learning, neural networks, deep learning', 'Computer vision for autonomous weapons'),
            ('Biotechnology', 'Genetic engineering and pharmaceutical R&D', 'HIGH', 'biotech, CRISPR, gene editing, synthetic biology', 'Gain-of-function research'),
            ('Semiconductors', 'Chip design and manufacturing', 'HIGH', 'semiconductors, chips, lithography, EUV', 'Military-grade processors'),
            ('Quantum Computing', 'Quantum information processing', 'HIGH', 'quantum, qubit, quantum computing', 'Code-breaking capabilities'),
            ('Aerospace', 'Aviation and space technologies', 'HIGH', 'aerospace, aviation, space, satellite', 'Missile guidance systems'),
            ('Advanced Materials', 'Novel materials and composites', 'MEDIUM', 'materials science, composites, nanomaterials', 'Stealth coatings'),
            ('Telecommunications', '5G and network infrastructure', 'MEDIUM', '5G, telecommunications, networking', 'Surveillance infrastructure'),
            ('Cybersecurity', 'Security and encryption technologies', 'MEDIUM', 'cybersecurity, encryption, cryptography', 'Offensive cyber tools'),
            ('Robotics', 'Autonomous systems and robotics', 'MEDIUM', 'robotics, autonomous, drones', 'Military drones'),
            ('Energy Storage', 'Battery and energy technologies', 'MEDIUM', 'battery, energy storage, fuel cells', 'EV for military vehicles')
        ]

        cursor.executemany('''
            INSERT INTO dual_use_sectors_reference
            (sector_name, description, concern_level, keywords, examples)
            VALUES (?, ?, ?, ?, ?)
        ''', sectors)

        print(f"   Inserted {len(sectors)} dual-use sectors")

        conn.commit()
        conn.close()

    def create_views(self):
        """Create useful views for querying"""
        print("\n" + "="*70)
        print("CREATING ANALYTICAL VIEWS")
        print("="*70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # View 1: High Priority Flows (Flow 1 only)
        print("\n[1/4] Creating high_priority_flows view...")
        cursor.execute('DROP VIEW IF EXISTS high_priority_flows')
        cursor.execute('''
            CREATE VIEW high_priority_flows AS
            SELECT *
            FROM china_capital_flows_comprehensive
            WHERE flow_pattern = 1
            AND validation_status = 'VALIDATED'
            ORDER BY transaction_date DESC
        ''')

        # View 2: All Validated Flows
        print("[2/4] Creating all_validated_flows view...")
        cursor.execute('DROP VIEW IF EXISTS all_validated_flows')
        cursor.execute('''
            CREATE VIEW all_validated_flows AS
            SELECT *
            FROM china_capital_flows_comprehensive
            WHERE validation_status = 'VALIDATED'
            ORDER BY transaction_date DESC
        ''')

        # View 3: Flows by Country
        print("[3/4] Creating flows_by_country view...")
        cursor.execute('DROP VIEW IF EXISTS flows_by_country')
        cursor.execute('''
            CREATE VIEW flows_by_country AS
            SELECT
                western_entity_country,
                flow_pattern,
                COUNT(*) as count,
                SUM(capital_amount_usd) as total_capital_usd
            FROM china_capital_flows_comprehensive
            WHERE validation_status = 'VALIDATED'
            GROUP BY western_entity_country, flow_pattern
            ORDER BY total_capital_usd DESC
        ''')

        # View 4: Recent Activity (last 12 months)
        print("[4/4] Creating recent_activity view...")
        cursor.execute('DROP VIEW IF EXISTS recent_activity')
        cursor.execute('''
            CREATE VIEW recent_activity AS
            SELECT *
            FROM china_capital_flows_comprehensive
            WHERE transaction_date >= date('now', '-12 months')
            AND validation_status = 'VALIDATED'
            ORDER BY transaction_date DESC
        ''')

        conn.commit()
        conn.close()

        print("\n✅ All views created successfully")

    def generate_sample_queries(self):
        """Generate sample SQL queries for common use cases"""
        print("\n" + "="*70)
        print("SAMPLE QUERIES FOR COMMON USE CASES")
        print("="*70)

        queries = {
            'Flow 1 (Primary Concern) - All Validated': '''
SELECT
    flow_id,
    western_entity_name,
    western_entity_country,
    western_entity_sector,
    chinese_entity_name,
    capital_amount_usd,
    transaction_date
FROM china_capital_flows_comprehensive
WHERE flow_pattern = 1
AND validation_status = 'VALIDATED'
ORDER BY transaction_date DESC;
            ''',

            'US vs Europe Flow 1 Comparison': '''
SELECT
    CASE
        WHEN western_entity_country = 'US' THEN 'United States'
        WHEN western_entity_country IN ('GB','DE','FR','IT','ES','NL','BE','AT','SE','DK') THEN 'Europe'
        ELSE 'Other'
    END as region,
    COUNT(*) as investment_count,
    SUM(capital_amount_usd) as total_capital
FROM china_capital_flows_comprehensive
WHERE flow_pattern = 1
AND validation_status = 'VALIDATED'
GROUP BY region;
            ''',

            'Temporal Trend (Annual)': '''
SELECT
    strftime('%Y', transaction_date) as year,
    flow_pattern,
    COUNT(*) as count,
    SUM(capital_amount_usd) as total_usd
FROM china_capital_flows_comprehensive
WHERE validation_status = 'VALIDATED'
GROUP BY year, flow_pattern
ORDER BY year DESC, flow_pattern;
            ''',

            'Top Chinese VC Firms (Flow 1)': '''
SELECT
    chinese_entity_name,
    COUNT(*) as investment_count,
    SUM(capital_amount_usd) as total_capital,
    COUNT(DISTINCT western_entity_sector) as sectors_invested
FROM china_capital_flows_comprehensive
WHERE flow_pattern = 1
AND validation_status = 'VALIDATED'
GROUP BY chinese_entity_name
ORDER BY investment_count DESC;
            ''',

            'Dual-Use Technology Sectors': '''
SELECT
    western_entity_sector,
    COUNT(*) as investment_count,
    SUM(capital_amount_usd) as total_capital,
    COUNT(DISTINCT chinese_entity_name) as unique_chinese_investors
FROM china_capital_flows_comprehensive
WHERE flow_pattern = 1
AND western_entity_is_dual_use = 1
AND validation_status = 'VALIDATED'
GROUP BY western_entity_sector
ORDER BY investment_count DESC;
            '''
        }

        output_file = Path('analysis/chinese_vc_europe') / 'sample_queries.sql'
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- Sample SQL Queries for China Capital Flows Analysis\n")
            f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for query_name, query in queries.items():
                f.write(f"-- {query_name}\n")
                f.write(f"{query}\n\n")

        print(f"\n✅ Sample queries saved: {output_file}")

        # Print them
        for query_name in queries.keys():
            print(f"  - {query_name}")

    def run(self):
        """Run complete database creation"""
        print("\n" + "="*70)
        print("COMPREHENSIVE CAPITAL FLOWS DATABASE CREATION")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Step 1: Create main table
        self.create_comprehensive_flows_table()

        # Step 2: Create lookup tables
        self.create_lookup_tables()

        # Step 3: Create views
        self.create_views()

        # Step 4: Generate sample queries
        self.generate_sample_queries()

        print("\n" + "="*70)
        print("DATABASE CREATION COMPLETE")
        print("="*70)
        print("\nCreated:")
        print("  - china_capital_flows_comprehensive (main table)")
        print("  - flow_patterns_reference (lookup)")
        print("  - known_chinese_vc_firms (reference)")
        print("  - dual_use_sectors_reference (reference)")
        print("  - 4 analytical views")
        print("  - Sample SQL queries")
        print("\nNext steps:")
        print("  1. Migrate validated US Form D data (50 entities)")
        print("  2. Add European data when validated")
        print("  3. Begin ongoing monitoring and data collection")
        print("="*70)

if __name__ == '__main__':
    creator = CapitalFlowsDatabaseCreator()
    creator.run()
