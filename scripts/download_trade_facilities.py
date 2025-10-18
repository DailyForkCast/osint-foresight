#!/usr/bin/env python3
"""
Trade Flows and Facilities Data Collector
Downloads UN/LOCODE, Open Supply Hub, UN Comtrade, and Eurostat COMEXT data
Focuses on China trade patterns and manufacturing facilities
"""

import requests
import pandas as pd
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import time
import zipfile
import io
import logging

class TradeFacilitiesCollector:
    def __init__(self, base_path: str = "F:/OSINT_Data/Trade_Facilities"):
        self.base_path = Path(base_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Research-Trade-Analysis/1.0'
        })

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Create directory structure
        self.setup_directories()

    def setup_directories(self):
        """Create directory structure for trade and facilities data"""
        directories = [
            'unlocode/raw',
            'unlocode/processed',
            'open_supply_hub/facilities',
            'open_supply_hub/chinese_facilities',
            'un_comtrade/trade_flows',
            'un_comtrade/china_bilateral',
            'eurostat_comext/eu_china_trade',
            'eurostat_comext/monthly_data',
            'analysis/trade_patterns',
            'analysis/facility_networks',
            'databases'
        ]

        for dir_name in directories:
            (self.base_path / dir_name).mkdir(parents=True, exist_ok=True)

        print(f"Created directory structure at {self.base_path}")

    def download_unlocode(self):
        """Download UN/LOCODE location codes for ports and logistics facilities"""
        print("\n" + "="*80)
        print("Downloading UN/LOCODE Data")
        print("="*80)

        # UN/LOCODE is available through UNECE
        # Latest version includes ~100,000 location codes
        unlocode_urls = {
            'main': 'https://unece.org/sites/default/files/2024-03/loc241csv.zip',
            'subdivisions': 'https://unece.org/sites/default/files/2024-03/2024-1_SubdivisionCodes.csv'
        }

        downloaded_files = []

        for name, url in unlocode_urls.items():
            try:
                print(f"Downloading {name} from {url}...")
                response = self.session.get(url, timeout=60)
                response.raise_for_status()

                if url.endswith('.zip'):
                    # Handle ZIP files
                    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                        extract_path = self.base_path / 'unlocode/raw'
                        zip_ref.extractall(extract_path)
                        print(f"  Extracted {name} to {extract_path}")

                        # Process the CSV files
                        for file in extract_path.glob('*.csv'):
                            if 'UNLOCODE' in file.name:
                                self.process_unlocode_file(file)
                else:
                    # Handle direct CSV files
                    file_path = self.base_path / 'unlocode/raw' / f'{name}.csv'
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    print(f"  Saved {name} to {file_path}")

                downloaded_files.append(name)

            except Exception as e:
                self.logger.error(f"Failed to download {name}: {e}")

        return downloaded_files

    def process_unlocode_file(self, file_path):
        """Process UN/LOCODE file to extract Chinese locations"""
        try:
            # Read CSV with proper encoding
            df = pd.read_csv(file_path, encoding='latin-1')

            # Filter for Chinese locations (CN, HK, MO, TW)
            chinese_codes = ['CN', 'HK', 'MO', 'TW']
            chinese_locations = df[df['Country'].isin(chinese_codes)] if 'Country' in df.columns else pd.DataFrame()

            if not chinese_locations.empty:
                output_file = self.base_path / 'unlocode/processed' / 'chinese_locations.csv'
                chinese_locations.to_csv(output_file, index=False)
                print(f"  Extracted {len(chinese_locations)} Chinese locations")

                # Extract key ports and logistics hubs
                if 'Function' in chinese_locations.columns:
                    ports = chinese_locations[chinese_locations['Function'].str.contains('1', na=False)]  # 1 = Port
                    print(f"  Found {len(ports)} Chinese ports")

                    airports = chinese_locations[chinese_locations['Function'].str.contains('4', na=False)]  # 4 = Airport
                    print(f"  Found {len(airports)} Chinese airports")

                    rail = chinese_locations[chinese_locations['Function'].str.contains('2', na=False)]  # 2 = Rail terminal
                    print(f"  Found {len(rail)} Chinese rail terminals")

        except Exception as e:
            self.logger.error(f"Error processing UN/LOCODE file: {e}")

    def query_open_supply_hub(self, country='CN', limit=1000):
        """Query Open Supply Hub API for manufacturing facilities"""
        print("\n" + "="*80)
        print("Querying Open Supply Hub")
        print("="*80)

        base_url = "https://opensupplyhub.org/api/facilities"

        facilities = []
        offset = 0

        try:
            while True:
                params = {
                    'country': country,
                    'limit': limit,
                    'offset': offset
                }

                print(f"Fetching facilities for {country} (offset: {offset})...")
                response = self.session.get(base_url, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()

                    if 'features' not in data or not data['features']:
                        break

                    facilities.extend(data['features'])

                    if len(data['features']) < limit:
                        break

                    offset += limit
                    time.sleep(1)  # Rate limiting

                else:
                    print(f"  API returned status {response.status_code}")
                    break

            # Save facilities data
            if facilities:
                output_file = self.base_path / 'open_supply_hub/chinese_facilities' / f'{country}_facilities.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(facilities, f, indent=2, ensure_ascii=False)

                print(f"Found {len(facilities)} facilities in {country}")

                # Extract key facility types
                self.analyze_facility_types(facilities, country)

        except Exception as e:
            self.logger.error(f"Failed to query Open Supply Hub: {e}")

        return facilities

    def analyze_facility_types(self, facilities, country):
        """Analyze types of facilities found"""
        facility_types = {}

        for facility in facilities:
            props = facility.get('properties', {})
            name = props.get('name', '').lower()

            # Categorize by keywords
            if 'electronic' in name or 'tech' in name or 'semiconductor' in name:
                facility_types.setdefault('Electronics/Tech', []).append(props.get('name'))
            elif 'chemical' in name or 'pharma' in name:
                facility_types.setdefault('Chemical/Pharma', []).append(props.get('name'))
            elif 'textile' in name or 'garment' in name or 'apparel' in name:
                facility_types.setdefault('Textile/Apparel', []).append(props.get('name'))
            elif 'metal' in name or 'steel' in name or 'aluminum' in name:
                facility_types.setdefault('Metals', []).append(props.get('name'))
            elif 'auto' in name or 'vehicle' in name or 'motor' in name:
                facility_types.setdefault('Automotive', []).append(props.get('name'))

        # Save analysis
        analysis_file = self.base_path / 'analysis/facility_networks' / f'{country}_facility_types.json'
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(facility_types, f, indent=2, ensure_ascii=False)

        print(f"\nFacility Type Analysis for {country}:")
        for ftype, names in facility_types.items():
            print(f"  {ftype}: {len(names)} facilities")

    def download_un_comtrade(self, reporter='156', partners=['all'], years=[2023, 2024]):
        """Download UN Comtrade bilateral trade data"""
        print("\n" + "="*80)
        print("Downloading UN Comtrade Data")
        print("="*80)

        # UN Comtrade API v2
        base_url = "https://comtradeapi.un.org/data/v2/get"

        # Reporter 156 = China
        # HS codes for tech/strategic goods
        strategic_hs_codes = [
            '84',  # Nuclear reactors, boilers, machinery
            '85',  # Electrical machinery and equipment
            '87',  # Vehicles
            '88',  # Aircraft, spacecraft
            '90',  # Optical, photographic, measuring instruments
            '28',  # Inorganic chemicals
            '29',  # Organic chemicals
            '72',  # Iron and steel
            '73',  # Articles of iron or steel
            '76',  # Aluminum
        ]

        trade_data = []

        for year in years:
            for hs_code in strategic_hs_codes:
                try:
                    params = {
                        'typeCode': 'C',  # Commodities
                        'freqCode': 'A',  # Annual
                        'clCode': 'HS',   # Harmonized System
                        'period': year,
                        'reporterCode': reporter,  # China
                        'partnerCode': ','.join(partners) if isinstance(partners, list) else partners,
                        'flowCode': 'X,M',  # Exports and Imports
                        'cmdCode': hs_code,
                        'customsCode': 'C00',
                        'motCode': '0'
                    }

                    print(f"Fetching {year} data for HS {hs_code}...")
                    response = self.session.get(f"{base_url}/C/A", params=params, timeout=60)

                    if response.status_code == 200:
                        data = response.json()
                        if 'data' in data:
                            trade_data.extend(data['data'])
                            print(f"  Found {len(data['data'])} trade records")

                    time.sleep(1)  # Rate limiting

                except Exception as e:
                    self.logger.error(f"Failed to fetch Comtrade data for {year} HS{hs_code}: {e}")

        # Save trade data
        if trade_data:
            output_file = self.base_path / 'un_comtrade/china_bilateral' / f'china_strategic_trade_{datetime.now().strftime("%Y%m%d")}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(trade_data, f, indent=2)

            print(f"\nTotal trade records collected: {len(trade_data)}")

            # Analyze trade patterns
            self.analyze_trade_patterns(trade_data)

        return trade_data

    def analyze_trade_patterns(self, trade_data):
        """Analyze bilateral trade patterns"""
        # Group by partner country
        partner_trade = {}

        for record in trade_data:
            partner = record.get('partnerDesc', 'Unknown')
            flow = record.get('flowDesc', '')
            value = record.get('primaryValue', 0)

            if partner not in partner_trade:
                partner_trade[partner] = {'exports': 0, 'imports': 0}

            if 'Export' in flow:
                partner_trade[partner]['exports'] += value
            elif 'Import' in flow:
                partner_trade[partner]['imports'] += value

        # Sort by total trade volume
        sorted_partners = sorted(partner_trade.items(),
                                key=lambda x: x[1]['exports'] + x[1]['imports'],
                                reverse=True)

        print("\nTop 10 Trade Partners (Strategic Goods):")
        for partner, trade in sorted_partners[:10]:
            total = trade['exports'] + trade['imports']
            print(f"  {partner}: ${total:,.0f} (Exports: ${trade['exports']:,.0f}, Imports: ${trade['imports']:,.0f})")

    def download_eurostat_comext(self):
        """Download Eurostat COMEXT EU-China trade data"""
        print("\n" + "="*80)
        print("Downloading Eurostat COMEXT Data")
        print("="*80)

        # Eurostat API endpoint
        base_url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

        # Dataset: DS-018995 - EU trade since 1988 by HS2-4-6 and CN8
        dataset = "DS-018995"

        params = {
            'format': 'JSON',
            'lang': 'EN',
            'freq': 'M',  # Monthly
            'indicators': 'QUANTITY_IN_100KG,VALUE_IN_EUROS',
            'reporter': 'EU27_2020',  # EU27
            'partner': 'CN',  # China
            'product': 'TOTAL',  # All products initially
            'flow': '1,2',  # 1=Imports, 2=Exports
            'period': '2023-01&2024-12'  # Recent period
        }

        try:
            url = f"{base_url}/{dataset}"
            print(f"Fetching EU-China trade data...")
            response = self.session.get(url, params=params, timeout=60)

            if response.status_code == 200:
                data = response.json()

                # Save raw data
                output_file = self.base_path / 'eurostat_comext/eu_china_trade' / f'eu_china_trade_{datetime.now().strftime("%Y%m%d")}.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)

                print(f"Downloaded EU-China trade data")

                # Process and analyze
                self.analyze_eu_china_trade(data)

            else:
                print(f"Failed to fetch Eurostat data: {response.status_code}")

        except Exception as e:
            self.logger.error(f"Failed to download Eurostat COMEXT: {e}")

    def analyze_eu_china_trade(self, data):
        """Analyze EU-China trade patterns"""
        print("\nEU-China Trade Analysis:")
        # This would parse the complex Eurostat JSON structure
        # and extract key trade metrics
        pass

    def create_trade_database(self):
        """Create SQLite database for trade and facilities analysis"""
        print("\n" + "="*80)
        print("Creating Trade & Facilities Database")
        print("="*80)

        db_path = self.base_path / 'databases' / f'trade_facilities_{datetime.now().strftime("%Y%m%d")}.db'

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # UN/LOCODE locations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                country TEXT,
                location TEXT,
                name TEXT,
                subdivision TEXT,
                function TEXT,
                status TEXT,
                iata TEXT,
                coordinates TEXT,
                is_port INTEGER,
                is_airport INTEGER,
                is_rail INTEGER,
                PRIMARY KEY (country, location)
            )
        ''')

        # Manufacturing facilities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facilities (
                os_id TEXT PRIMARY KEY,
                name TEXT,
                country TEXT,
                address TEXT,
                lat REAL,
                lon REAL,
                facility_type TEXT,
                products TEXT,
                certifications TEXT,
                employees INTEGER,
                chinese_owned INTEGER DEFAULT 0
            )
        ''')

        # Bilateral trade flows table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_flows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER,
                month INTEGER,
                reporter_country TEXT,
                partner_country TEXT,
                hs_code TEXT,
                product_description TEXT,
                flow_type TEXT,
                trade_value REAL,
                quantity REAL,
                unit TEXT
            )
        ''')

        # Trade patterns analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_patterns (
                partner_country TEXT PRIMARY KEY,
                total_exports_to_china REAL,
                total_imports_from_china REAL,
                trade_balance REAL,
                strategic_goods_share REAL,
                top_export_categories TEXT,
                top_import_categories TEXT,
                analysis_date TEXT
            )
        ''')

        # Supply chain links table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supply_chain_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_location TEXT,
                destination_location TEXT,
                product_type TEXT,
                transport_mode TEXT,
                frequency TEXT,
                volume_estimate REAL,
                strategic_importance TEXT
            )
        ''')

        conn.commit()
        conn.close()

        print(f"Created database: {db_path}")
        return db_path

    def run_full_collection(self):
        """Execute complete trade and facilities data collection"""
        print("="*80)
        print("Trade Flows & Facilities Complete Data Collection")
        print("="*80)

        try:
            # Step 1: Download UN/LOCODE location data
            unlocode_files = self.download_unlocode()

            # Step 2: Query Open Supply Hub for facilities
            chinese_facilities = self.query_open_supply_hub('CN')
            hk_facilities = self.query_open_supply_hub('HK')

            # Step 3: Download UN Comtrade trade data
            trade_data = self.download_un_comtrade()

            # Step 4: Download Eurostat COMEXT data
            self.download_eurostat_comext()

            # Step 5: Create analysis database
            db_path = self.create_trade_database()

            print("\n" + "="*80)
            print("Collection Complete!")
            print("="*80)
            print(f"UN/LOCODE files: {len(unlocode_files)}")
            print(f"Chinese facilities: {len(chinese_facilities)}")
            print(f"Hong Kong facilities: {len(hk_facilities)}")
            print(f"Trade records: {len(trade_data) if trade_data else 0}")
            print(f"Database: {db_path}")

            return {
                'unlocode': unlocode_files,
                'facilities': len(chinese_facilities) + len(hk_facilities),
                'trade_records': len(trade_data) if trade_data else 0,
                'database': str(db_path)
            }

        except Exception as e:
            self.logger.error(f"Collection failed: {e}")
            raise

if __name__ == "__main__":
    collector = TradeFacilitiesCollector()
    results = collector.run_full_collection()
    print(f"\nResults: {json.dumps(results, indent=2)}")
