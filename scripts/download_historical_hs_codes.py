#!/usr/bin/env python3
"""
Download historical strategic HS codes from 2010-2025
15 years of EU-China trade data for trend analysis
"""

import requests
import pandas as pd
import sqlite3
from pathlib import Path
import time
from datetime import datetime
import json

class HistoricalHSDownloader:
    def __init__(self):
        self.base_path = Path("F:/OSINT_Data/Trade_Facilities/historical_hs_codes")
        self.base_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.db_path = self.base_path / f"historical_trade_2010_2025_{timestamp}.db"

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
                '2805': 'Lithium'
            },
            'greentech': {
                '8501': 'Electric motors',
                '8507': 'Electric batteries',
                '854140': 'Solar cells',
                '8541': 'Solar panels'
            },
            'biotech': {
                '3002': 'Vaccines',
                '3004': 'Medicaments',
                '9018': 'Medical instruments'
            }
        }

        # Years to download (2010-2025)
        self.years = list(range(2010, 2026))

    def create_database(self):
        """Create SQL database with historical schema"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()

        cursor.execute('PRAGMA journal_mode=WAL')

        # Historical trade data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_trade (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hs_code TEXT,
                description TEXT,
                category TEXT,
                year INTEGER,
                month INTEGER,
                imports_value REAL,
                exports_value REAL,
                trade_balance REAL,
                dependency_ratio REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Annual aggregates
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS annual_summary (
                hs_code TEXT,
                year INTEGER,
                total_imports REAL,
                total_exports REAL,
                trade_deficit REAL,
                dependency_ratio REAL,
                growth_rate_imports REAL,
                growth_rate_exports REAL,
                PRIMARY KEY (hs_code, year)
            )
        ''')

        # Trend analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_analysis (
                hs_code TEXT PRIMARY KEY,
                category TEXT,
                description TEXT,
                avg_dependency_2010_2015 REAL,
                avg_dependency_2016_2020 REAL,
                avg_dependency_2021_2025 REAL,
                peak_dependency_year INTEGER,
                peak_dependency_ratio REAL,
                trend_direction TEXT,
                cagr_imports REAL,
                cagr_exports REAL,
                strategic_shift_year INTEGER,
                notes TEXT
            )
        ''')

        # Critical events tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS critical_events (
                year INTEGER,
                event TEXT,
                impact_categories TEXT,
                notes TEXT
            )
        ''')

        # Insert known events
        events = [
            (2010, 'Post-financial crisis recovery', 'all', 'Recovery phase begins'),
            (2011, 'EU debt crisis', 'all', 'Reduced import capacity'),
            (2013, 'Belt and Road Initiative launch', 'transport,infrastructure', 'China global expansion'),
            (2016, 'Brexit vote', 'all', 'EU uncertainty'),
            (2018, 'US-China trade war begins', 'semiconductors,tech', 'Supply chain shifts'),
            (2020, 'COVID-19 pandemic', 'biotech,semiconductors', 'Supply chain disruption'),
            (2021, 'Global chip shortage', 'semiconductors,automotive', 'Critical shortages'),
            (2022, 'Russia-Ukraine war', 'energy,materials', 'Energy crisis, sanctions'),
            (2023, 'EU Critical Raw Materials Act', 'materials,batteries', 'Strategic autonomy push'),
            (2024, 'EU-China EV tariffs', 'automotive,batteries', 'Trade tensions escalate')
        ]

        for event in events:
            cursor.execute('''
                INSERT OR IGNORE INTO critical_events (year, event, impact_categories, notes)
                VALUES (?, ?, ?, ?)
            ''', event)

        conn.commit()
        conn.close()

    def build_url_yearly(self, hs_code, year):
        """Build API URL for specific HS code and year"""
        # Create monthly periods for the year
        periods = ','.join([f'{year}-{str(m).zfill(2)}' for m in range(1, 13)])

        params = {
            'freq': 'M',
            'reporter': 'EU27_2020',
            'partner': 'CN',
            'product': hs_code,
            'flow': '1,2',
            'indicators': 'VALUE_IN_EUROS',
            'TIME_PERIOD': periods,
            'compress': 'false',
            'format': 'csvdata',
            'formatVersion': '2.0',
            'lang': 'en',
            'labels': 'name'
        }

        query_parts = []
        for key, value in params.items():
            if key in ['freq', 'reporter', 'partner', 'product', 'flow', 'indicators', 'TIME_PERIOD']:
                query_parts.append(f'c[{key}]={value}')
            else:
                query_parts.append(f'{key}={value}')

        return f"{self.api_base}/*.*.*.*.*.*?{'&'.join(query_parts)}"

    def download_historical_data(self, hs_code, description, category):
        """Download historical data for a specific HS code"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()

        total_imports = 0
        total_exports = 0
        yearly_data = []

        print(f"\n  {hs_code} - {description}:")

        for year in self.years:
            print(f"    {year}: ", end='')

            url = self.build_url_yearly(hs_code, year)

            try:
                response = requests.get(url, timeout=30)

                if response.status_code == 200:
                    import io
                    df = pd.read_csv(io.StringIO(response.text))

                    if len(df) > 0:
                        # Process monthly data
                        year_imports = 0
                        year_exports = 0

                        for _, row in df.iterrows():
                            period = row.get('TIME_PERIOD', '')
                            if period:
                                try:
                                    year_val = int(period.split('-')[0])
                                    month_val = int(period.split('-')[1])

                                    is_import = row.get('flow') == '1' or row.get('flow') == 1
                                    value = row.get('OBS_VALUE', 0)

                                    if is_import:
                                        year_imports += value
                                    else:
                                        year_exports += value

                                    # Store monthly data
                                    cursor.execute('''
                                        INSERT INTO historical_trade
                                        (hs_code, description, category, year, month,
                                         imports_value, exports_value, trade_balance, dependency_ratio)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    ''', (hs_code, description, category, year_val, month_val,
                                          value if is_import else 0,
                                          value if not is_import else 0,
                                          0, 0))

                                except (ValueError, IndexError):
                                    pass

                        # Store annual summary
                        if year_imports > 0 or year_exports > 0:
                            ratio = year_imports / max(year_exports, 1)
                            cursor.execute('''
                                INSERT OR REPLACE INTO annual_summary
                                (hs_code, year, total_imports, total_exports,
                                 trade_deficit, dependency_ratio)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (hs_code, year, year_imports, year_exports,
                                  year_imports - year_exports, ratio))

                            yearly_data.append({
                                'year': year,
                                'imports': year_imports,
                                'exports': year_exports,
                                'ratio': ratio
                            })

                            total_imports += year_imports
                            total_exports += year_exports

                            print(f"EUR {year_imports/1e9:.1f}B/{year_exports/1e9:.1f}B", end='')
                        else:
                            print("No data", end='')
                    else:
                        print("Empty", end='')
                else:
                    print(f"Error {response.status_code}", end='')

            except Exception as e:
                print(f"Failed: {str(e)[:20]}", end='')

            print()
            time.sleep(0.5)  # Rate limiting

        conn.commit()
        conn.close()

        return yearly_data

    def analyze_trends(self):
        """Analyze historical trends and patterns"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()

        # Calculate trend metrics for each HS code
        cursor.execute('''
            SELECT DISTINCT hs_code, category, description
            FROM historical_trade
        ''')

        products = cursor.fetchall()

        for hs_code, category, description in products:
            # Get period averages
            cursor.execute('''
                SELECT
                    AVG(CASE WHEN year BETWEEN 2010 AND 2015 THEN dependency_ratio END) as period1,
                    AVG(CASE WHEN year BETWEEN 2016 AND 2020 THEN dependency_ratio END) as period2,
                    AVG(CASE WHEN year BETWEEN 2021 AND 2025 THEN dependency_ratio END) as period3,
                    MAX(dependency_ratio) as peak_ratio,
                    year as peak_year
                FROM annual_summary
                WHERE hs_code = ?
                GROUP BY hs_code
            ''', (hs_code,))

            row = cursor.fetchone()
            if row:
                period1, period2, period3, peak_ratio, peak_year = row

                # Determine trend direction
                if period3 and period1:
                    if period3 > period1 * 1.5:
                        trend = 'INCREASING_DEPENDENCY'
                    elif period3 < period1 * 0.7:
                        trend = 'DECREASING_DEPENDENCY'
                    else:
                        trend = 'STABLE'
                else:
                    trend = 'INSUFFICIENT_DATA'

                cursor.execute('''
                    INSERT OR REPLACE INTO trend_analysis
                    (hs_code, category, description,
                     avg_dependency_2010_2015, avg_dependency_2016_2020, avg_dependency_2021_2025,
                     peak_dependency_year, peak_dependency_ratio, trend_direction)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (hs_code, category, description,
                      period1, period2, period3,
                      peak_year, peak_ratio, trend))

        conn.commit()
        conn.close()

    def generate_report(self):
        """Generate comprehensive historical analysis report"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)

        print("\n" + "="*80)
        print("15-YEAR HISTORICAL TRADE ANALYSIS (2010-2025)")
        print("="*80)

        # Products with increasing dependency
        cursor = conn.execute('''
            SELECT hs_code, description,
                   avg_dependency_2010_2015 as period1,
                   avg_dependency_2021_2025 as period3,
                   peak_dependency_ratio, peak_dependency_year
            FROM trend_analysis
            WHERE trend_direction = 'INCREASING_DEPENDENCY'
            ORDER BY period3 DESC
        ''')

        increasing = cursor.fetchall()
        if increasing:
            print("\nPRODUCTS WITH INCREASING DEPENDENCY:")
            for row in increasing[:5]:
                print(f"  {row[0]}: {row[2]:.1f}:1 (2010-15) -> {row[3]:.1f}:1 (2021-25)")
                print(f"    Peak: {row[4]:.1f}:1 in {row[5]}")

        # Critical dependency shifts
        cursor = conn.execute('''
            SELECT a.hs_code, a.year, a.dependency_ratio, e.event
            FROM annual_summary a
            LEFT JOIN critical_events e ON a.year = e.year
            WHERE a.dependency_ratio > 20
            ORDER BY a.year, a.dependency_ratio DESC
        ''')

        print("\n" + "="*80)
        print("CRITICAL DEPENDENCY PERIODS (>20:1 ratio)")
        print("="*80)

        critical_years = {}
        for row in cursor:
            year = row[1]
            if year not in critical_years:
                critical_years[year] = []
            critical_years[year].append((row[0], row[2], row[3]))

        for year, products in sorted(critical_years.items()):
            event = products[0][2] if products[0][2] else ""
            print(f"\n{year}: {event}")
            for hs, ratio, _ in products[:3]:
                print(f"  {hs}: {ratio:.1f}:1")

        # Overall statistics
        cursor = conn.execute('''
            SELECT
                COUNT(DISTINCT hs_code) as products,
                AVG(CASE WHEN year = 2010 THEN dependency_ratio END) as ratio_2010,
                AVG(CASE WHEN year = 2015 THEN dependency_ratio END) as ratio_2015,
                AVG(CASE WHEN year = 2020 THEN dependency_ratio END) as ratio_2020,
                AVG(CASE WHEN year = 2025 THEN dependency_ratio END) as ratio_2025
            FROM annual_summary
        ''')

        row = cursor.fetchone()

        print("\n" + "="*80)
        print("DEPENDENCY EVOLUTION")
        print("="*80)
        print(f"2010: {row[1]:.1f}:1 average ratio")
        print(f"2015: {row[2]:.1f}:1 average ratio")
        print(f"2020: {row[3]:.1f}:1 average ratio (COVID)")
        print(f"2025: {row[4]:.1f}:1 average ratio (Current)")

        conn.close()

        print(f"\n[COMPLETE] Database: {self.db_path}")

    def run_collection(self):
        """Execute historical data collection"""
        print("="*80)
        print("HISTORICAL HS CODES COLLECTION (2010-2025)")
        print("="*80)

        self.create_database()

        all_data = {}

        for category, codes in self.strategic_codes.items():
            print(f"\n[{category.upper()}] Downloading {len(codes)} products x {len(self.years)} years:")

            for hs_code, description in codes.items():
                yearly_data = self.download_historical_data(hs_code, description, category)
                all_data[hs_code] = yearly_data

        print("\nAnalyzing trends...")
        self.analyze_trends()

        print("\nGenerating report...")
        self.generate_report()

        return {
            'database': str(self.db_path),
            'products': len(all_data),
            'years': len(self.years),
            'total_records': sum(len(v) for v in all_data.values())
        }

if __name__ == "__main__":
    downloader = HistoricalHSDownloader()
    results = downloader.run_collection()
    print(f"\nResults: {json.dumps(results, indent=2, default=str)}")
