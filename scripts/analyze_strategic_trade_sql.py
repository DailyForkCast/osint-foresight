#!/usr/bin/env python3
"""
Analyze strategic HS code trade data and create comprehensive SQL database
Combines all CSV files into structured database with risk assessment
"""

import pandas as pd
import sqlite3
from pathlib import Path
import glob
from datetime import datetime

class StrategicTradeAnalyzer:
    def __init__(self):
        self.data_path = Path("F:/OSINT_Data/Trade_Facilities/strategic_hs_codes")
        self.db_path = self.data_path / f"strategic_trade_analysis_{datetime.now().strftime('%Y%m%d')}.db"

    def create_database(self):
        """Create comprehensive SQL database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Enable WAL mode for better concurrency
        cursor.execute('PRAGMA journal_mode=WAL')

        # Main trade flows table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_flows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hs_code TEXT,
                category TEXT,
                period TEXT,
                flow_type TEXT,
                value_euros REAL,
                reporter TEXT DEFAULT 'EU27',
                partner TEXT DEFAULT 'CN',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Aggregated summary by HS code
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hs_summary (
                hs_code TEXT PRIMARY KEY,
                description TEXT,
                category TEXT,
                total_imports REAL,
                total_exports REAL,
                trade_balance REAL,
                dependency_ratio REAL,
                monthly_avg_imports REAL,
                monthly_avg_exports REAL,
                volatility_score REAL,
                risk_level TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Category analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS category_analysis (
                category TEXT PRIMARY KEY,
                total_imports REAL,
                total_exports REAL,
                trade_deficit REAL,
                dependency_ratio REAL,
                products_count INTEGER,
                critical_products INTEGER,
                high_risk_products INTEGER,
                medium_risk_products INTEGER,
                strategic_importance TEXT,
                notes TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Critical dependencies tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS critical_dependencies (
                hs_code TEXT PRIMARY KEY,
                category TEXT,
                description TEXT,
                dependency_ratio REAL,
                imports_billions REAL,
                exports_billions REAL,
                deficit_billions REAL,
                substitutability TEXT,
                strategic_importance TEXT,
                recommended_action TEXT,
                priority_level INTEGER,
                notes TEXT
            )
        ''')

        # Time series analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monthly_trends (
                hs_code TEXT,
                period TEXT,
                imports REAL,
                exports REAL,
                balance REAL,
                ratio REAL,
                PRIMARY KEY (hs_code, period)
            )
        ''')

        # Risk matrix
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_matrix (
                hs_code TEXT PRIMARY KEY,
                category TEXT,
                dependency_score REAL,
                volume_score REAL,
                strategic_score REAL,
                overall_risk_score REAL,
                risk_classification TEXT,
                mitigation_priority INTEGER
            )
        ''')

        conn.commit()
        conn.close()

    def load_csv_data(self):
        """Load all CSV files and process them"""
        conn = sqlite3.connect(self.db_path)

        # HS code descriptions
        hs_descriptions = {
            '8541': 'Semiconductor devices (diodes, transistors)',
            '8542': 'Electronic integrated circuits (chips)',
            '8471': 'Computers and data processing equipment',
            '8517': 'Telecommunications equipment (5G)',
            '8529': 'Parts for telecom/broadcast equipment',
            '8486': 'Semiconductor manufacturing equipment',
            '9031': 'Measuring/checking instruments',
            '9027': 'Physical/chemical analysis instruments',
            '9030': 'Oscilloscopes, spectrum analyzers',
            '8479': 'Machines for electronic assembly',
            '8802': 'Aircraft, spacecraft',
            '8803': 'Parts of aircraft/spacecraft',
            '8526': 'Radar apparatus, radio navigation',
            '8805': 'Aircraft launch gear, simulators',
            '2844': 'Radioactive elements (uranium)',
            '8112': 'Beryllium, germanium (semiconductor materials)',
            '8105': 'Cobalt (batteries)',
            '8108': 'Titanium (aerospace)',
            '2805': 'Alkali metals (lithium)',
            '8501': 'Electric motors and generators',
            '8507': 'Electric accumulators (batteries)',
            '854140': 'Photosensitive semiconductors (solar)',
            '8502': 'Electric generating sets',
            '3002': 'Vaccines, blood products',
            '3004': 'Medicaments',
            '9018': 'Medical instruments',
            '9022': 'X-ray equipment, CT scanners'
        }

        csv_files = glob.glob(str(self.data_path / "*.csv.csv"))

        category_totals = {}
        hs_totals = {}

        for csv_file in csv_files:
            filename = Path(csv_file).name

            # Parse filename to get category and HS code
            parts = filename.replace('.csv.csv', '').split('_')
            if len(parts) >= 2:
                category = parts[0]
                hs_code = parts[1]

                try:
                    df = pd.read_csv(csv_file)

                    if len(df) > 0:
                        # Store raw data
                        for _, row in df.iterrows():
                            conn.execute('''
                                INSERT INTO trade_flows (hs_code, category, period, flow_type, value_euros)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (hs_code, category,
                                  row.get('TIME_PERIOD', ''),
                                  'import' if row.get('flow') == '1' else 'export',
                                  row.get('OBS_VALUE', 0)))

                        # Calculate totals
                        imports = df[df['flow'] == '1']['OBS_VALUE'].sum() if 'flow' in df.columns else 0
                        exports = df[df['flow'] == '2']['OBS_VALUE'].sum() if 'flow' in df.columns else 0

                        if hs_code not in hs_totals:
                            hs_totals[hs_code] = {
                                'category': category,
                                'description': hs_descriptions.get(hs_code, 'Unknown'),
                                'imports': 0,
                                'exports': 0,
                                'records': 0
                            }

                        hs_totals[hs_code]['imports'] += imports
                        hs_totals[hs_code]['exports'] += exports
                        hs_totals[hs_code]['records'] += len(df)

                        if category not in category_totals:
                            category_totals[category] = {
                                'imports': 0,
                                'exports': 0,
                                'products': set(),
                                'critical': 0,
                                'high': 0,
                                'medium': 0
                            }

                        category_totals[category]['imports'] += imports
                        category_totals[category]['exports'] += exports
                        category_totals[category]['products'].add(hs_code)

                except Exception as e:
                    print(f"Error processing {csv_file}: {e}")

        # Store HS summaries
        for hs_code, data in hs_totals.items():
            ratio = data['imports'] / max(data['exports'], 1)

            # Determine risk level
            if ratio > 20:
                risk_level = 'CRITICAL'
                category_totals[data['category']]['critical'] += 1
            elif ratio > 10:
                risk_level = 'HIGH'
                category_totals[data['category']]['high'] += 1
            elif ratio > 5:
                risk_level = 'MEDIUM'
                category_totals[data['category']]['medium'] += 1
            else:
                risk_level = 'LOW'

            conn.execute('''
                INSERT OR REPLACE INTO hs_summary
                (hs_code, description, category, total_imports, total_exports,
                 trade_balance, dependency_ratio, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (hs_code, data['description'], data['category'],
                  data['imports'], data['exports'],
                  data['imports'] - data['exports'],
                  ratio, risk_level))

            # Add to critical dependencies if ratio > 10
            if ratio > 10:
                conn.execute('''
                    INSERT OR REPLACE INTO critical_dependencies
                    (hs_code, category, description, dependency_ratio,
                     imports_billions, exports_billions, deficit_billions,
                     priority_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (hs_code, data['category'], data['description'],
                      ratio, data['imports']/1e9, data['exports']/1e9,
                      (data['imports']-data['exports'])/1e9,
                      1 if ratio > 20 else 2))

            # Calculate risk scores
            dependency_score = min(ratio / 20 * 100, 100)
            volume_score = min(data['imports'] / 50e9 * 100, 100)
            strategic_score = 80 if data['category'] in ['semiconductors', 'aerospace', 'materials'] else 60
            overall_risk = (dependency_score + volume_score + strategic_score) / 3

            risk_class = 'CRITICAL' if overall_risk > 75 else 'HIGH' if overall_risk > 50 else 'MEDIUM' if overall_risk > 25 else 'LOW'

            conn.execute('''
                INSERT OR REPLACE INTO risk_matrix
                (hs_code, category, dependency_score, volume_score,
                 strategic_score, overall_risk_score, risk_classification)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (hs_code, data['category'], dependency_score,
                  volume_score, strategic_score, overall_risk, risk_class))

        # Store category summaries
        for category, data in category_totals.items():
            ratio = data['imports'] / max(data['exports'], 1)

            # Determine strategic importance
            if category in ['semiconductors', 'aerospace', 'materials']:
                strategic_importance = 'CRITICAL'
            elif category in ['manufacturing', 'greentech']:
                strategic_importance = 'HIGH'
            else:
                strategic_importance = 'MEDIUM'

            conn.execute('''
                INSERT OR REPLACE INTO category_analysis
                (category, total_imports, total_exports, trade_deficit,
                 dependency_ratio, products_count, critical_products,
                 high_risk_products, medium_risk_products, strategic_importance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (category, data['imports'], data['exports'],
                  data['imports'] - data['exports'], ratio,
                  len(data['products']), data['critical'],
                  data['high'], data['medium'], strategic_importance))

        conn.commit()
        conn.close()

        return len(hs_totals), len(category_totals)

    def generate_reports(self):
        """Generate analysis reports from database"""
        conn = sqlite3.connect(self.db_path)

        # Top dependencies
        print("\n" + "="*80)
        print("CRITICAL DEPENDENCIES ANALYSIS")
        print("="*80)

        cursor = conn.execute('''
            SELECT hs_code, description, dependency_ratio, imports_billions
            FROM critical_dependencies
            ORDER BY dependency_ratio DESC
            LIMIT 10
        ''')

        print("\nTop 10 Critical Dependencies:")
        for row in cursor:
            print(f"  {row[0]}: {row[2]:.1f}:1 ratio - EUR {row[3]:.1f}B imports")
            print(f"    {row[1]}")

        # Category risk summary
        cursor = conn.execute('''
            SELECT category, total_imports/1e9 as imports_b,
                   total_exports/1e9 as exports_b,
                   dependency_ratio, critical_products,
                   strategic_importance
            FROM category_analysis
            ORDER BY dependency_ratio DESC
        ''')

        print("\n" + "="*80)
        print("CATEGORY RISK ASSESSMENT")
        print("="*80)

        for row in cursor:
            print(f"\n{row[0].upper()}:")
            print(f"  Imports: EUR {row[1]:.1f}B | Exports: EUR {row[2]:.1f}B")
            print(f"  Dependency: {row[3]:.1f}:1 | Critical Products: {row[4]}")
            print(f"  Strategic Importance: {row[5]}")

        # Overall statistics
        cursor = conn.execute('''
            SELECT
                COUNT(DISTINCT hs_code) as products,
                SUM(total_imports)/1e9 as total_imports_b,
                SUM(total_exports)/1e9 as total_exports_b,
                COUNT(CASE WHEN risk_level = 'CRITICAL' THEN 1 END) as critical,
                COUNT(CASE WHEN risk_level = 'HIGH' THEN 1 END) as high
            FROM hs_summary
        ''')

        row = cursor.fetchone()

        print("\n" + "="*80)
        print("OVERALL STRATEGIC TRADE SUMMARY")
        print("="*80)
        print(f"\nProducts analyzed: {row[0]}")
        print(f"Total imports: EUR {row[1]:.1f}B")
        print(f"Total exports: EUR {row[2]:.1f}B")
        print(f"Trade deficit: EUR {row[1]-row[2]:.1f}B")
        print(f"Critical dependencies: {row[3]}")
        print(f"High risk products: {row[4]}")

        conn.close()

        print(f"\n[COMPLETE] Database saved to: {self.db_path}")

    def run_analysis(self):
        """Execute complete analysis pipeline"""
        print("Creating database...")
        self.create_database()

        print("Loading CSV data...")
        products, categories = self.load_csv_data()

        print(f"Processed {products} products across {categories} categories")

        print("\nGenerating reports...")
        self.generate_reports()

if __name__ == "__main__":
    analyzer = StrategicTradeAnalyzer()
    analyzer.run_analysis()
