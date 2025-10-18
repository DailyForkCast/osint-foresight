#!/usr/bin/env python3
"""
Download expanded set of strategic HS codes and store in SQL database
Includes dual-use, emerging tech, and critical infrastructure codes
"""

import requests
import pandas as pd
import sqlite3
from pathlib import Path
import time
from datetime import datetime
import json

class ExpandedHSDownloader:
    def __init__(self):
        self.base_path = Path("F:/OSINT_Data/Trade_Facilities/strategic_hs_codes")
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.db_path = self.base_path / f"strategic_trade_{datetime.now().strftime('%Y%m%d')}.db"

        # API base URL
        self.api_base = "https://ec.europa.eu/eurostat/api/comext/dissemination/sdmx/3.0/data/dataflow/ESTAT/ds-045409/1.0"

        # EXPANDED strategic HS codes - comprehensive coverage
        self.strategic_codes = {
            # Original categories
            'semiconductors': {
                '8541': 'Semiconductor devices',
                '8542': 'Electronic integrated circuits',
                '8471': 'Computers',
                '8517': 'Telecommunications equipment',
                '8529': 'Parts for telecom equipment',
                '8523': 'Solid-state storage devices',
                '8543': 'Electrical machines with individual functions'
            },
            'manufacturing': {
                '8486': 'Semiconductor manufacturing equipment',
                '9031': 'Measuring/checking instruments',
                '9027': 'Physical/chemical analysis instruments',
                '9030': 'Oscilloscopes, spectrum analyzers',
                '8479': 'Machines for electronic assembly',
                '8456': 'Machine tools using laser/plasma',
                '8457': 'Machining centres',
                '8458': 'Lathes for metal',
                '8459': 'Machine tools for drilling/milling',
                '8460': 'Machine tools for grinding/sharpening'
            },
            'aerospace': {
                '8802': 'Aircraft, spacecraft',
                '8803': 'Parts of aircraft/spacecraft',
                '8526': 'Radar apparatus',
                '8805': 'Aircraft launch gear',
                '8801': 'Balloons, airships, gliders',
                '8804': 'Parachutes, rotochutes',
                '8807': 'Parts for balloons/airships'
            },
            'materials': {
                '2844': 'Radioactive elements',
                '8112': 'Beryllium, germanium',
                '8105': 'Cobalt',
                '8108': 'Titanium',
                '2805': 'Alkali metals (lithium)',
                '8103': 'Tantalum',
                '8109': 'Zirconium',
                '8110': 'Antimony',
                '8113': 'Cermets',
                '2846': 'Rare earth compounds',
                '2850': 'Hydrides, nitrides (semiconductors)',
                '7202': 'Ferroalloys',
                '8104': 'Magnesium'
            },
            'greentech': {
                '8501': 'Electric motors',
                '8507': 'Electric batteries',
                '854140': 'Photosensitive semiconductors',
                '8502': 'Electric generating sets',
                '8504': 'Electrical transformers',
                '8506': 'Primary cells and batteries',
                '8514': 'Industrial furnaces',
                '8541': 'Solar panels and cells',
                '8546': 'Electrical insulators',
                '8548': 'Electrical parts and waste'
            },
            'biotech': {
                '3002': 'Vaccines, blood products',
                '3004': 'Medicaments',
                '9018': 'Medical instruments',
                '9022': 'X-ray equipment',
                '3822': 'Diagnostic reagents',
                '9019': 'Mechano-therapy appliances',
                '9021': 'Orthopedic appliances',
                '9027': 'Instruments for medical analysis'
            },
            # NEW CATEGORIES
            'dual_use': {
                '8411': 'Turbojet engines',
                '8412': 'Other engines and motors',
                '8413': 'Pumps for liquids',
                '8414': 'Air/vacuum pumps',
                '8419': 'Heat exchange units',
                '8421': 'Centrifuges',
                '8424': 'Mechanical appliances for projecting',
                '8463': 'Machine tools for working metal',
                '8464': 'Machine tools for stone/ceramics',
                '8477': 'Machinery for rubber/plastics',
                '8543': 'Electrical machines (lasers)',
                '9013': 'Lasers and optical appliances',
                '9014': 'Navigational instruments',
                '9015': 'Surveying instruments',
                '9026': 'Flow/pressure measuring instruments',
                '9032': 'Automatic regulating instruments'
            },
            'quantum_ai': {
                '8471': 'Quantum computers',
                '9031': 'Quantum measuring devices',
                '8543': 'Quantum communication devices',
                '8517': 'Quantum encryption equipment',
                '8523': 'Quantum storage media',
                '9027': 'Quantum sensors'
            },
            'robotics': {
                '8479': 'Industrial robots',
                '8428': 'Lifting/handling machinery',
                '8429': 'Self-propelled machinery',
                '8430': 'Earth moving machinery',
                '8465': 'Machine tools for wood/plastics',
                '8466': 'Parts for machine tools',
                '8468': 'Machinery for soldering/welding',
                '8515': 'Electric soldering/welding machines'
            },
            'cybersecurity': {
                '8517': 'Encryption devices',
                '8471': 'Security hardware',
                '8523': 'Encrypted storage',
                '8543': 'Signal processing equipment',
                '9031': 'Network monitoring equipment'
            },
            'energy_infrastructure': {
                '8402': 'Steam generating boilers',
                '8403': 'Central heating boilers',
                '8404': 'Auxiliary plant for boilers',
                '8405': 'Producer gas generators',
                '8406': 'Steam turbines',
                '8410': 'Hydraulic turbines',
                '8535': 'Electrical apparatus >1000V',
                '8536': 'Electrical apparatus <=1000V',
                '8537': 'Boards for electric control',
                '8544': 'Insulated wire and cables',
                '8545': 'Carbon electrodes',
                '8547': 'Insulating fittings'
            },
            'transport_infrastructure': {
                '8601': 'Rail locomotives',
                '8602': 'Other rail locomotives',
                '8603': 'Self-propelled railway',
                '8604': 'Railway maintenance vehicles',
                '8605': 'Railway passenger coaches',
                '8606': 'Railway freight wagons',
                '8607': 'Parts of railway vehicles',
                '8608': 'Railway fixtures',
                '8609': 'Containers',
                '8701': 'Tractors',
                '8702': 'Buses',
                '8703': 'Motor cars',
                '8704': 'Motor vehicles for transport',
                '8705': 'Special purpose vehicles',
                '8706': 'Chassis with engines',
                '8707': 'Bodies for vehicles',
                '8708': 'Parts for motor vehicles',
                '8709': 'Self-propelled trucks',
                '8716': 'Trailers'
            },
            'chemicals_pharma': {
                '2933': 'Heterocyclic compounds',
                '2934': 'Nucleic acids',
                '2935': 'Sulphonamides',
                '2936': 'Vitamins',
                '2937': 'Hormones',
                '2938': 'Glycosides',
                '2939': 'Alkaloids',
                '2940': 'Sugars',
                '2941': 'Antibiotics',
                '2942': 'Other organic compounds',
                '3001': 'Glands for therapy',
                '3003': 'Medicaments not in doses',
                '3005': 'Wadding, gauze, bandages',
                '3006': 'Pharmaceutical goods',
                '3301': 'Essential oils',
                '3302': 'Odoriferous substances',
                '3303': 'Perfumes',
                '3304': 'Beauty products',
                '3305': 'Hair products',
                '3306': 'Oral hygiene',
                '3307': 'Shaving products'
            },
            'optics_photonics': {
                '9001': 'Optical fibres',
                '9002': 'Lenses and prisms',
                '9003': 'Frames for spectacles',
                '9004': 'Spectacles',
                '9005': 'Binoculars and telescopes',
                '9006': 'Photographic cameras',
                '9007': 'Cinematographic cameras',
                '9008': 'Image projectors',
                '9009': 'Photocopying apparatus',
                '9010': 'Apparatus for photographic labs',
                '9011': 'Optical microscopes',
                '9012': 'Electron microscopes'
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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Main trade data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hs_code TEXT,
                hs_description TEXT,
                category TEXT,
                subcategory TEXT,
                reporter TEXT,
                partner TEXT,
                flow TEXT,
                period TEXT,
                value_euros REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Summary statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hs_code TEXT UNIQUE,
                hs_description TEXT,
                category TEXT,
                total_imports REAL,
                total_exports REAL,
                trade_balance REAL,
                dependency_ratio REAL,
                records_count INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Category totals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS category_totals (
                category TEXT PRIMARY KEY,
                total_imports REAL,
                total_exports REAL,
                trade_deficit REAL,
                dependency_ratio REAL,
                products_count INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Risk assessment table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_assessment (
                hs_code TEXT PRIMARY KEY,
                category TEXT,
                dependency_score REAL,
                strategic_importance TEXT,
                substitution_difficulty TEXT,
                risk_level TEXT,
                notes TEXT,
                assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        print(f"  {code}: {description[:40]}...", end='')

        url = self.build_url(code)

        try:
            response = requests.get(url, timeout=60)

            if response.status_code == 200:
                # Parse CSV data
                import io
                df = pd.read_csv(io.StringIO(response.text))

                if len(df) > 0:
                    # Calculate totals
                    imports = df[df['flow'] == '1']['OBS_VALUE'].sum() if 'flow' in df.columns else 0
                    exports = df[df['flow'] == '2']['OBS_VALUE'].sum() if 'flow' in df.columns else 0

                    # Store in database
                    self.store_trade_data(code, description, category, df, imports, exports)

                    ratio = imports/max(exports, 1)
                    print(f" [OK] EUR {imports/1e9:.1f}B imports, {ratio:.1f}:1")

                    return True, {'code': code, 'imports': imports, 'exports': exports, 'records': len(df)}
                else:
                    print(" [NO DATA]")
                    return False, None

            else:
                print(f" [ERROR {response.status_code}]")
                return False, None

        except Exception as e:
            print(f" [FAILED: {str(e)[:30]}]")
            return False, None

    def store_trade_data(self, hs_code, description, category, df, imports, exports):
        """Store trade data in SQL database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Store detailed records
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT INTO trade_data (hs_code, hs_description, category, reporter, partner, flow, period, value_euros)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (hs_code, description, category,
                  row.get('reporter', 'EU27'),
                  row.get('partner', 'CN'),
                  row.get('flow', ''),
                  row.get('TIME_PERIOD', ''),
                  row.get('OBS_VALUE', 0)))

        # Update summary
        cursor.execute('''
            INSERT OR REPLACE INTO trade_summary
            (hs_code, hs_description, category, total_imports, total_exports, trade_balance, dependency_ratio, records_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (hs_code, description, category, imports, exports, imports-exports, imports/max(exports,1), len(df)))

        # Assess risk
        dependency_ratio = imports / max(exports, 1)
        if dependency_ratio > 20:
            risk_level = 'CRITICAL'
        elif dependency_ratio > 10:
            risk_level = 'HIGH'
        elif dependency_ratio > 5:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'

        cursor.execute('''
            INSERT OR REPLACE INTO risk_assessment
            (hs_code, category, dependency_score, risk_level)
            VALUES (?, ?, ?, ?)
        ''', (hs_code, category, dependency_ratio, risk_level))

        conn.commit()
        conn.close()

    def run_collection(self):
        """Download all strategic HS codes"""
        print("="*80)
        print("EXPANDED STRATEGIC HS CODES COLLECTION")
        print("="*80)

        self.create_database()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        total_imports = 0
        total_exports = 0
        total_processed = 0

        for category, codes in self.strategic_codes.items():
            print(f"\n[{category.upper()}] Processing {len(codes)} codes:")

            category_imports = 0
            category_exports = 0
            successful = 0

            for code, description in codes.items():
                success, data = self.download_hs_code(code, description, category)

                if success and data:
                    category_imports += data['imports']
                    category_exports += data['exports']
                    successful += 1
                    total_processed += 1

                time.sleep(0.5)  # Rate limiting

            # Store category totals
            if successful > 0:
                cursor.execute('''
                    INSERT OR REPLACE INTO category_totals
                    (category, total_imports, total_exports, trade_deficit, dependency_ratio, products_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (category, category_imports, category_exports,
                      category_imports-category_exports,
                      category_imports/max(category_exports,1),
                      successful))

                total_imports += category_imports
                total_exports += category_exports

                print(f"  Subtotal: EUR {category_imports/1e9:.1f}B imports, {category_exports/1e9:.1f}B exports")

        conn.commit()

        # Generate reports
        print("\n" + "="*80)
        print("DATABASE SUMMARY")
        print("="*80)

        # Top dependencies
        cursor.execute('''
            SELECT hs_code, hs_description, category, dependency_ratio, total_imports/1e9 as imports_b
            FROM trade_summary
            WHERE dependency_ratio > 10
            ORDER BY dependency_ratio DESC
            LIMIT 20
        ''')

        critical_deps = cursor.fetchall()

        print(f"\nCRITICAL DEPENDENCIES (>10:1 ratio):")
        for row in critical_deps:
            print(f"  {row[0]} ({row[2]}): {row[3]:.1f}:1 - EUR {row[4]:.1f}B")

        # Risk summary
        cursor.execute('''
            SELECT risk_level, COUNT(*) as count
            FROM risk_assessment
            GROUP BY risk_level
        ''')

        risk_summary = cursor.fetchall()

        print(f"\nRISK DISTRIBUTION:")
        for level, count in risk_summary:
            print(f"  {level}: {count} products")

        print(f"\nTOTAL TRADE VOLUME:")
        print(f"  Imports: EUR {total_imports/1e9:.1f}B")
        print(f"  Exports: EUR {total_exports/1e9:.1f}B")
        print(f"  Deficit: EUR {(total_imports-total_exports)/1e9:.1f}B")
        print(f"  Products processed: {total_processed}")

        print(f"\nDatabase saved to: {self.db_path}")

        conn.close()

        return {
            'database': str(self.db_path),
            'products': total_processed,
            'imports': total_imports,
            'exports': total_exports,
            'critical_dependencies': len(critical_deps)
        }

if __name__ == "__main__":
    downloader = ExpandedHSDownloader()
    results = downloader.run_collection()
    print(f"\n[COMPLETE] Results: {json.dumps(results, indent=2)}")
