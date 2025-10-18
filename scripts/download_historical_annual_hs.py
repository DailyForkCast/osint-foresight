#!/usr/bin/env python3
"""
Download historical strategic HS codes from 2010-2023 (annual data)
Faster version using annual aggregates instead of monthly
"""

import requests
import pandas as pd
import sqlite3
from pathlib import Path
import time
from datetime import datetime
import json
import io

class HistoricalAnnualHSDownloader:
    def __init__(self):
        self.base_path = Path("F:/OSINT_Data/Trade_Facilities/historical_hs_codes")
        self.base_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.db_path = self.base_path / f"historical_trade_2010_2023_{timestamp}.db"

        # API base URL
        self.api_base = "https://ec.europa.eu/eurostat/api/comext/dissemination/sdmx/3.0/data/dataflow/ESTAT/ds-045409/1.0"

        # Key strategic HS codes for historical analysis
        self.strategic_codes = {
            'semiconductors': {
                '8541': 'Semiconductor devices',
                '8542': 'Electronic integrated circuits',
                '8471': 'Computers',
                '8517': 'Telecommunications equipment',
                '8523': 'Data storage devices'
            },
            'manufacturing': {
                '8486': 'Semiconductor manufacturing equipment',
                '9031': 'Measuring instruments',
                '9027': 'Analysis instruments',
                '8479': 'Electronic assembly machines'
            },
            'aerospace': {
                '8802': 'Aircraft',
                '8803': 'Aircraft parts',
                '8526': 'Radar apparatus'
            },
            'materials': {
                '2846': 'Rare earth compounds',
                '8112': 'Beryllium, germanium',
                '8105': 'Cobalt',
                '2805': 'Lithium',
                '8108': 'Titanium'
            },
            'greentech': {
                '8501': 'Electric motors',
                '8507': 'Electric batteries',
                '8504': 'Transformers',
                '8502': 'Electric generating sets'
            },
            'biotech': {
                '3002': 'Vaccines',
                '3004': 'Medicaments',
                '9018': 'Medical instruments',
                '9022': 'X-ray equipment'
            },
            'dual_use': {
                '8421': 'Centrifuges',
                '9013': 'Lasers',
                '9014': 'Navigation instruments',
                '9026': 'Flow meters',
                '8411': 'Turbojet engines'
            }
        }

    def create_database(self):
        """Create SQL database with historical schema"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()

        cursor.execute('PRAGMA journal_mode=WAL')

        # Annual trade data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS annual_trade (
                hs_code TEXT,
                description TEXT,
                category TEXT,
                year INTEGER,
                imports_value REAL,
                exports_value REAL,
                trade_balance REAL,
                dependency_ratio REAL,
                PRIMARY KEY (hs_code, year)
            )
        ''')

        # Trend analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_analysis (
                hs_code TEXT PRIMARY KEY,
                category TEXT,
                description TEXT,
                imports_2010 REAL,
                imports_2015 REAL,
                imports_2020 REAL,
                imports_2023 REAL,
                exports_2010 REAL,
                exports_2015 REAL,
                exports_2020 REAL,
                exports_2023 REAL,
                ratio_2010 REAL,
                ratio_2015 REAL,
                ratio_2020 REAL,
                ratio_2023 REAL,
                peak_year INTEGER,
                peak_ratio REAL,
                trend_direction TEXT,
                cagr_imports REAL,
                cagr_exports REAL
            )
        ''')

        # Category evolution
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS category_evolution (
                category TEXT,
                year INTEGER,
                total_imports REAL,
                total_exports REAL,
                avg_dependency REAL,
                PRIMARY KEY (category, year)
            )
        ''')

        # Critical periods
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS critical_periods (
                hs_code TEXT,
                critical_year INTEGER,
                dependency_ratio REAL,
                event TEXT,
                PRIMARY KEY (hs_code, critical_year)
            )
        ''')

        conn.commit()
        conn.close()

    def download_product_history(self, hs_code, description, category):
        """Download complete history for one product"""
        # Build URL for all years at once
        years = ','.join([str(y) for y in range(2010, 2024)])

        params = {
            'freq': 'A',  # Annual
            'reporter': 'EU27_2020',
            'partner': 'CN',
            'product': hs_code,
            'flow': '1,2',
            'indicators': 'VALUE_IN_EUROS',
            'TIME_PERIOD': years,
            'compress': 'false',
            'format': 'csvdata',
            'formatVersion': '2.0'
        }

        query_parts = []
        for key, value in params.items():
            if key in ['freq', 'reporter', 'partner', 'product', 'flow', 'indicators', 'TIME_PERIOD']:
                query_parts.append(f'c[{key}]={value}')
            else:
                query_parts.append(f'{key}={value}')

        url = f"{self.api_base}/*.*.*.*.*.*?{'&'.join(query_parts)}"

        try:
            response = requests.get(url, timeout=60)

            if response.status_code == 200:
                df = pd.read_csv(io.StringIO(response.text))

                if len(df) > 0:
                    conn = sqlite3.connect(self.db_path, timeout=30.0)
                    cursor = conn.cursor()

                    yearly_data = {}

                    for _, row in df.iterrows():
                        year = int(row['TIME_PERIOD'])
                        is_import = row['flow'] == '1' or row['flow'] == 1
                        value = row['OBS_VALUE']

                        if year not in yearly_data:
                            yearly_data[year] = {'imports': 0, 'exports': 0}

                        if is_import:
                            yearly_data[year]['imports'] = value
                        else:
                            yearly_data[year]['exports'] = value

                    # Store annual data
                    for year, data in yearly_data.items():
                        ratio = data['imports'] / max(data['exports'], 1)
                        balance = data['imports'] - data['exports']

                        cursor.execute('''
                            INSERT OR REPLACE INTO annual_trade
                            (hs_code, description, category, year, imports_value,
                             exports_value, trade_balance, dependency_ratio)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (hs_code, description, category, year,
                              data['imports'], data['exports'], balance, ratio))

                        # Mark critical periods (>20:1 ratio)
                        if ratio > 20:
                            event = self.get_event_for_year(year)
                            cursor.execute('''
                                INSERT OR REPLACE INTO critical_periods
                                (hs_code, critical_year, dependency_ratio, event)
                                VALUES (?, ?, ?, ?)
                            ''', (hs_code, year, ratio, event))

                    conn.commit()
                    conn.close()

                    return yearly_data

        except Exception as e:
            print(f"Error downloading {hs_code}: {e}")

        return None

    def get_event_for_year(self, year):
        """Get major event for a given year"""
        events = {
            2010: 'Post-financial crisis recovery',
            2011: 'EU debt crisis',
            2013: 'Belt and Road Initiative launch',
            2016: 'Brexit vote',
            2018: 'US-China trade war begins',
            2020: 'COVID-19 pandemic',
            2021: 'Global chip shortage',
            2022: 'Russia-Ukraine war',
            2023: 'EU Critical Raw Materials Act'
        }
        return events.get(year, '')

    def analyze_trends(self):
        """Analyze historical trends"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()

        # Get all products
        cursor.execute('SELECT DISTINCT hs_code, description, category FROM annual_trade')
        products = cursor.fetchall()

        for hs_code, description, category in products:
            # Get key year data
            cursor.execute('''
                SELECT year, imports_value, exports_value, dependency_ratio
                FROM annual_trade
                WHERE hs_code = ?
                ORDER BY year
            ''', (hs_code,))

            data = cursor.fetchall()
            yearly_dict = {row[0]: row for row in data}

            # Extract specific years
            y2010 = yearly_dict.get(2010, [2010, 0, 0, 0])
            y2015 = yearly_dict.get(2015, [2015, 0, 0, 0])
            y2020 = yearly_dict.get(2020, [2020, 0, 0, 0])
            y2023 = yearly_dict.get(2023, [2023, 0, 0, 0])

            # Find peak dependency
            peak_ratio = max(row[3] for row in data) if data else 0
            peak_year = next((row[0] for row in data if row[3] == peak_ratio), None)

            # Calculate CAGR
            if y2010[1] > 0 and y2023[1] > 0:
                cagr_imports = ((y2023[1] / y2010[1]) ** (1/13) - 1) * 100
            else:
                cagr_imports = 0

            if y2010[2] > 0 and y2023[2] > 0:
                cagr_exports = ((y2023[2] / y2010[2]) ** (1/13) - 1) * 100
            else:
                cagr_exports = 0

            # Determine trend
            if y2023[3] > y2010[3] * 1.5:
                trend = 'INCREASING'
            elif y2023[3] < y2010[3] * 0.7:
                trend = 'DECREASING'
            else:
                trend = 'STABLE'

            cursor.execute('''
                INSERT OR REPLACE INTO trend_analysis
                (hs_code, category, description,
                 imports_2010, imports_2015, imports_2020, imports_2023,
                 exports_2010, exports_2015, exports_2020, exports_2023,
                 ratio_2010, ratio_2015, ratio_2020, ratio_2023,
                 peak_year, peak_ratio, trend_direction,
                 cagr_imports, cagr_exports)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (hs_code, category, description,
                  y2010[1], y2015[1], y2020[1], y2023[1],
                  y2010[2], y2015[2], y2020[2], y2023[2],
                  y2010[3], y2015[3], y2020[3], y2023[3],
                  peak_year, peak_ratio, trend,
                  cagr_imports, cagr_exports))

        # Category evolution
        cursor.execute('''
            INSERT OR REPLACE INTO category_evolution
            SELECT category, year,
                   SUM(imports_value) as total_imports,
                   SUM(exports_value) as total_exports,
                   AVG(dependency_ratio) as avg_dependency
            FROM annual_trade
            GROUP BY category, year
        ''')

        conn.commit()
        conn.close()

    def generate_report(self):
        """Generate comprehensive report"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)

        print("\n" + "="*80)
        print("EU-CHINA STRATEGIC TRADE: 14-YEAR ANALYSIS (2010-2023)")
        print("="*80)

        # Most dramatic increases
        cursor = conn.execute('''
            SELECT hs_code, description, ratio_2010, ratio_2023,
                   (ratio_2023 - ratio_2010) as increase
            FROM trend_analysis
            WHERE trend_direction = 'INCREASING'
            ORDER BY increase DESC
            LIMIT 5
        ''')

        print("\nTOP DEPENDENCY INCREASES:")
        for row in cursor:
            print(f"  {row[0]} - {row[1][:40]}")
            print(f"    2010: {row[2]:.1f}:1 → 2023: {row[3]:.1f}:1 (+{row[4]:.1f})")

        # Critical dependencies by year
        cursor = conn.execute('''
            SELECT critical_year, COUNT(*) as count, AVG(dependency_ratio) as avg_ratio
            FROM critical_periods
            GROUP BY critical_year
            ORDER BY critical_year
        ''')

        print("\nCRITICAL DEPENDENCY YEARS (>20:1 products):")
        for row in cursor:
            print(f"  {row[0]}: {row[1]} products, avg {row[2]:.1f}:1")

        # Category evolution
        cursor = conn.execute('''
            SELECT category,
                   SUM(CASE WHEN year = 2010 THEN total_imports END)/1e9 as imports_2010,
                   SUM(CASE WHEN year = 2023 THEN total_imports END)/1e9 as imports_2023,
                   SUM(CASE WHEN year = 2010 THEN avg_dependency END) as dep_2010,
                   SUM(CASE WHEN year = 2023 THEN avg_dependency END) as dep_2023
            FROM category_evolution
            GROUP BY category
        ''')

        print("\nCATEGORY EVOLUTION (2010 vs 2023):")
        for row in cursor:
            print(f"\n{row[0].upper()}:")
            print(f"  Imports: EUR {row[1]:.1f}B → EUR {row[2]:.1f}B")
            print(f"  Dependency: {row[3]:.1f}:1 → {row[4]:.1f}:1")

        # Overall summary
        cursor = conn.execute('''
            SELECT
                COUNT(DISTINCT hs_code) as products,
                SUM(CASE WHEN year = 2010 THEN imports_value END)/1e9 as imports_2010,
                SUM(CASE WHEN year = 2023 THEN imports_value END)/1e9 as imports_2023,
                SUM(CASE WHEN year = 2010 THEN exports_value END)/1e9 as exports_2010,
                SUM(CASE WHEN year = 2023 THEN exports_value END)/1e9 as exports_2023
            FROM annual_trade
        ''')

        row = cursor.fetchone()
        if row:
            print("\n" + "="*80)
            print("OVERALL TRADE EVOLUTION")
            print("="*80)
            print(f"Products analyzed: {row[0]}")
            print(f"2010: EUR {row[1]:.1f}B imports / EUR {row[3]:.1f}B exports")
            print(f"2023: EUR {row[2]:.1f}B imports / EUR {row[4]:.1f}B exports")

            if row[1] and row[2]:
                import_growth = ((row[2] / row[1]) - 1) * 100
                print(f"Import growth: {import_growth:.1f}%")
            if row[3] and row[4]:
                export_growth = ((row[4] / row[3]) - 1) * 100
                print(f"Export growth: {export_growth:.1f}%")

        conn.close()

        print(f"\n[COMPLETE] Database saved: {self.db_path}")

    def run_collection(self):
        """Execute data collection and analysis"""
        print("="*80)
        print("DOWNLOADING HISTORICAL HS DATA (2010-2023)")
        print("="*80)

        self.create_database()

        total_products = 0
        successful = 0

        for category, codes in self.strategic_codes.items():
            print(f"\n[{category.upper()}] Processing {len(codes)} products:")

            for hs_code, description in codes.items():
                print(f"  {hs_code}: {description[:35]}...", end=' ')

                data = self.download_product_history(hs_code, description, category)
                total_products += 1

                if data:
                    successful += 1
                    # Show 2023 data as confirmation
                    if 2023 in data:
                        y2023 = data[2023]
                        ratio = y2023['imports'] / max(y2023['exports'], 1)
                        print(f"[OK] 2023: {ratio:.1f}:1")
                    else:
                        print("[OK]")
                else:
                    print("[FAILED]")

                time.sleep(0.5)  # Rate limiting

        print(f"\n\nDownloaded: {successful}/{total_products} products")

        print("\nAnalyzing trends...")
        self.analyze_trends()

        print("Generating report...")
        self.generate_report()

        return {
            'database': str(self.db_path),
            'products': successful,
            'years': 14
        }

if __name__ == "__main__":
    downloader = HistoricalAnnualHSDownloader()
    results = downloader.run_collection()
    print(f"\nResults: {json.dumps(results, indent=2, default=str)}")
