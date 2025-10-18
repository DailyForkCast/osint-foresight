#!/usr/bin/env python3
"""
Download critical additional HS codes and store in SQL database
Focus on dual-use, critical infrastructure, and emerging tech
"""

import requests
import pandas as pd
import sqlite3
from pathlib import Path
import time
from datetime import datetime
import json

class CriticalHSDownloader:
    def __init__(self):
        self.base_path = Path("F:/OSINT_Data/Trade_Facilities/critical_hs_codes")
        self.base_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.db_path = self.base_path / f"critical_trade_{timestamp}.db"

        # API base URL
        self.api_base = "https://ec.europa.eu/eurostat/api/comext/dissemination/sdmx/3.0/data/dataflow/ESTAT/ds-045409/1.0"

        # CRITICAL HS codes not in original list
        self.critical_codes = {
            'dual_use_tech': {
                '8421': 'Centrifuges (uranium enrichment)',
                '9013': 'Lasers and optical appliances',
                '9014': 'Navigational instruments (GPS)',
                '9026': 'Flow/pressure measuring (nuclear)',
                '9032': 'Automatic regulating instruments',
                '8411': 'Turbojet engines',
                '8413': 'Pumps for liquids (nuclear)',
                '8419': 'Heat exchange units',
                '8463': 'Machine tools for metal',
                '8543': 'Electrical machines (particle accelerators)'
            },
            'critical_materials': {
                '2846': 'Rare earth compounds',
                '2850': 'Hydrides, nitrides (semiconductors)',
                '7202': 'Ferroalloys',
                '8103': 'Tantalum',
                '8109': 'Zirconium',
                '8110': 'Antimony',
                '8113': 'Cermets',
                '8104': 'Magnesium',
                '2612': 'Uranium ores',
                '2825': 'Hydrazine compounds'
            },
            'energy_infrastructure': {
                '8402': 'Steam generating boilers',
                '8406': 'Steam turbines',
                '8410': 'Hydraulic turbines',
                '8535': 'Electrical apparatus >1000V',
                '8536': 'Electrical apparatus <=1000V',
                '8537': 'Boards for electric control',
                '8544': 'Insulated wire and cables',
                '7306': 'Oil/gas pipelines',
                '7311': 'Compressed gas containers',
                '2711': 'Natural gas'
            },
            'quantum_photonics': {
                '9001': 'Optical fibres',
                '9002': 'Lenses and prisms',
                '9011': 'Optical microscopes',
                '9012': 'Electron microscopes',
                '8543': 'Quantum communication devices',
                '9027': 'Quantum sensors',
                '8523': 'Quantum storage media'
            },
            'robotics_ai': {
                '8479': 'Industrial robots',
                '8428': 'Lifting/handling machinery',
                '8465': 'Machine tools for wood/plastics',
                '8466': 'Parts for machine tools',
                '8515': 'Electric welding machines',
                '9031': 'AI measuring devices',
                '8471': 'AI processing hardware'
            },
            'transport_critical': {
                '8609': 'Containers (intermodal)',
                '8708': 'Parts for motor vehicles',
                '8803': 'Aircraft parts',
                '8607': 'Railway vehicle parts',
                '8905': 'Light vessels, dredgers',
                '8906': 'Warships and lifeboats',
                '8901': 'Cruise ships and cargo vessels'
            },
            'chemicals_precursors': {
                '2804': 'Hydrogen, rare gases',
                '2814': 'Ammonia',
                '2815': 'Sodium/potassium hydroxide',
                '2833': 'Sulphates',
                '2834': 'Nitrites and nitrates',
                '2835': 'Phosphinates and phosphonates',
                '2903': 'Halogenated hydrocarbons',
                '2904': 'Sulphonated derivatives'
            },
            'biotech_advanced': {
                '3822': 'Diagnostic reagents',
                '3821': 'Culture media',
                '2934': 'Nucleic acids',
                '2937': 'Hormones',
                '2941': 'Antibiotics',
                '3001': 'Glands for therapy',
                '3003': 'Medicaments not in doses'
            }
        }

        self.base_params = {
            'freq': 'M',
            'reporter': 'EU27_2020',
            'partner': 'CN',
            'flow': '1,2',
            'indicators': 'VALUE_IN_EUROS',
            'TIME_PERIOD': ','.join([f'2024-{str(i).zfill(2)}' for i in range(1,10)]),
            'compress': 'false',
            'format': 'csvdata',
            'formatVersion': '2.0',
            'lang': 'en',
            'labels': 'name'
        }

    def create_database(self):
        """Create SQL database with proper schema"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()

        cursor.execute('PRAGMA journal_mode=WAL')  # Prevent locking issues

        # Main trade data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hs_code TEXT,
                hs_description TEXT,
                category TEXT,
                imports_value REAL,
                exports_value REAL,
                trade_balance REAL,
                dependency_ratio REAL,
                risk_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Category summary table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS category_summary (
                category TEXT PRIMARY KEY,
                total_imports REAL,
                total_exports REAL,
                trade_deficit REAL,
                avg_dependency REAL,
                critical_products INTEGER,
                high_risk_products INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Critical dependencies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS critical_dependencies (
                hs_code TEXT PRIMARY KEY,
                description TEXT,
                category TEXT,
                imports_billions REAL,
                dependency_ratio REAL,
                strategic_importance TEXT,
                alternatives TEXT,
                notes TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def build_url(self, hs_code):
        """Build API URL for specific HS code"""
        params = self.base_params.copy()
        params['product'] = hs_code

        query_parts = []
        for key, value in params.items():
            if key in ['freq', 'reporter', 'partner', 'product', 'flow', 'indicators', 'TIME_PERIOD']:
                query_parts.append(f'c[{key}]={value}')
            else:
                query_parts.append(f'{key}={value}')

        return f"{self.api_base}/*.*.*.*.*.*?{'&'.join(query_parts)}"

    def download_hs_code(self, code, description, category):
        """Download data for a specific HS code"""
        url = self.build_url(code)

        try:
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                import io
                df = pd.read_csv(io.StringIO(response.text))

                if len(df) > 0:
                    imports = df[df['flow'] == '1']['OBS_VALUE'].sum() if 'flow' in df.columns else 0
                    exports = df[df['flow'] == '2']['OBS_VALUE'].sum() if 'flow' in df.columns else 0

                    return True, {
                        'code': code,
                        'description': description,
                        'category': category,
                        'imports': float(imports),
                        'exports': float(exports),
                        'balance': float(imports - exports),
                        'ratio': float(imports/max(exports, 1))
                    }

            return False, None

        except Exception as e:
            return False, None

    def store_results(self, results):
        """Store all results in database"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()

        category_totals = {}
        critical_deps = []

        for data in results:
            # Determine risk level
            ratio = data['ratio']
            if ratio > 20:
                risk_level = 'CRITICAL'
            elif ratio > 10:
                risk_level = 'HIGH'
            elif ratio > 5:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'

            # Store trade data
            cursor.execute('''
                INSERT INTO trade_data
                (hs_code, hs_description, category, imports_value, exports_value,
                 trade_balance, dependency_ratio, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data['code'], data['description'], data['category'],
                  data['imports'], data['exports'], data['balance'],
                  data['ratio'], risk_level))

            # Track category totals
            cat = data['category']
            if cat not in category_totals:
                category_totals[cat] = {
                    'imports': 0, 'exports': 0, 'products': 0,
                    'critical': 0, 'high': 0
                }

            category_totals[cat]['imports'] += data['imports']
            category_totals[cat]['exports'] += data['exports']
            category_totals[cat]['products'] += 1

            if risk_level == 'CRITICAL':
                category_totals[cat]['critical'] += 1
                critical_deps.append(data)
            elif risk_level == 'HIGH':
                category_totals[cat]['high'] += 1

        # Store category summaries
        for cat, totals in category_totals.items():
            cursor.execute('''
                INSERT OR REPLACE INTO category_summary
                (category, total_imports, total_exports, trade_deficit,
                 avg_dependency, critical_products, high_risk_products)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (cat, totals['imports'], totals['exports'],
                  totals['imports'] - totals['exports'],
                  totals['imports']/max(totals['exports'], 1),
                  totals['critical'], totals['high']))

        # Store critical dependencies
        for dep in sorted(critical_deps, key=lambda x: x['ratio'], reverse=True)[:20]:
            cursor.execute('''
                INSERT OR REPLACE INTO critical_dependencies
                (hs_code, description, category, imports_billions, dependency_ratio)
                VALUES (?, ?, ?, ?, ?)
            ''', (dep['code'], dep['description'], dep['category'],
                  dep['imports']/1e9, dep['ratio']))

        conn.commit()
        conn.close()

    def run_collection(self):
        """Download all critical HS codes"""
        print("="*80)
        print("CRITICAL HS CODES COLLECTION FOR SQL DATABASE")
        print("="*80)

        self.create_database()

        all_results = []
        total_imports = 0
        total_exports = 0

        for category, codes in self.critical_codes.items():
            print(f"\n[{category.upper()}] Downloading {len(codes)} codes:")

            for code, description in codes.items():
                print(f"  {code}: {description[:35]}...", end=' ')

                success, data = self.download_hs_code(code, description, category)

                if success and data:
                    all_results.append(data)
                    total_imports += data['imports']
                    total_exports += data['exports']

                    ratio = data['ratio']
                    status = "CRITICAL" if ratio > 20 else "HIGH" if ratio > 10 else "OK"
                    print(f"[{status}] {ratio:.1f}:1")
                else:
                    print("[NO DATA]")

                time.sleep(0.3)

        # Store all results
        if all_results:
            self.store_results(all_results)

        # Print summary
        print("\n" + "="*80)
        print("COLLECTION COMPLETE")
        print("="*80)

        print(f"\nDatabase: {self.db_path}")
        print(f"Products processed: {len(all_results)}")
        print(f"Total imports: EUR {total_imports/1e9:.1f}B")
        print(f"Total exports: EUR {total_exports/1e9:.1f}B")
        print(f"Trade deficit: EUR {(total_imports-total_exports)/1e9:.1f}B")

        # Show critical dependencies
        critical = [r for r in all_results if r['ratio'] > 20]
        if critical:
            print(f"\nCRITICAL DEPENDENCIES (>20:1 ratio): {len(critical)}")
            for item in sorted(critical, key=lambda x: x['ratio'], reverse=True)[:5]:
                print(f"  {item['code']}: {item['ratio']:.1f}:1 - {item['description'][:40]}")

        return {
            'database': str(self.db_path),
            'products': len(all_results),
            'imports': total_imports,
            'exports': total_exports,
            'critical': len(critical)
        }

if __name__ == "__main__":
    downloader = CriticalHSDownloader()
    results = downloader.run_collection()
    print(f"\nResults: {json.dumps(results, indent=2, default=str)}")
