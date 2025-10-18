#!/usr/bin/env python3
"""
Eurostat COMEXT Data Collector
Downloads EU-China trade data from Eurostat's public API
Focuses on strategic goods and technology transfers
"""

import requests
import pandas as pd
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import time
import logging
from io import StringIO

class EurostatComextCollector:
    def __init__(self, base_path: str = "F:/OSINT_Data/Trade_Facilities/eurostat_comext"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Eurostat API endpoints
        self.api_base = "https://ec.europa.eu/eurostat/api/dissemination"
        self.bulk_base = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing"

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Research-Eurostat/1.0',
            'Accept': 'application/json, text/csv'
        })

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Create subdirectories
        self.setup_directories()

    def setup_directories(self):
        """Create directory structure for Eurostat data"""
        directories = [
            'raw_data/monthly',
            'raw_data/annual',
            'processed/china_bilateral',
            'processed/strategic_goods',
            'analysis/trade_balance',
            'analysis/tech_categories'
        ]

        for dir_name in directories:
            (self.base_path / dir_name).mkdir(parents=True, exist_ok=True)

        print(f"Created Eurostat directory structure at {self.base_path}")

    def get_dataset_metadata(self, dataset_code):
        """Get metadata for a specific dataset"""
        url = f"{self.api_base}/metadata/1.0/{dataset_code}"

        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Could not get metadata for {dataset_code}: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting metadata: {e}")
            return None

    def download_ext_st_eu27_2020sitc(self):
        """
        Download EU trade by SITC dataset
        Dataset: ext_st_eu27_2020sitc - EU trade since 1999 by SITC
        """
        print("\n" + "="*80)
        print("Downloading EU Trade by SITC (Strategic Categories)")
        print("="*80)

        dataset_code = "ext_st_eu27_2020sitc"

        # Strategic SITC codes for technology and dual-use goods
        strategic_sitc = {
            '5': 'Chemicals',  # Including pharmaceuticals
            '7': 'Machinery and transport equipment',  # Including computers, telecom
            '75': 'Office machines and automatic data processing equipment',
            '76': 'Telecommunications and sound recording apparatus',
            '77': 'Electrical machinery',
            '87': 'Professional and scientific instruments',
            '88': 'Photographic apparatus and optical goods'
        }

        results = []

        for sitc_code, description in strategic_sitc.items():
            print(f"\nFetching {description} (SITC {sitc_code})...")

            # Build API query
            params = {
                'format': 'JSON',
                'lang': 'EN',
                'freq': 'A',  # Annual
                'sitc06': sitc_code,
                'stk_flow': 'IMP,EXP',  # Imports and Exports
                'partner': 'CN',  # China
                'indicators': 'VALUE_IN_EUROS',
                'time': '2019,2020,2021,2022,2023'
            }

            url = f"{self.api_base}/statistics/1.0/data/{dataset_code}"

            try:
                response = self.session.get(url, params=params, timeout=60)

                if response.status_code == 200:
                    data = response.json()

                    # Save raw data
                    output_file = self.base_path / f'raw_data/annual/{dataset_code}_SITC{sitc_code}_China.json'
                    with open(output_file, 'w') as f:
                        json.dump(data, f, indent=2)

                    print(f"  Saved {description} data")

                    # Parse and analyze
                    parsed_data = self.parse_eurostat_json(data, sitc_code, description)
                    results.extend(parsed_data)

                else:
                    print(f"  Failed to fetch: {response.status_code}")

            except Exception as e:
                self.logger.error(f"Error fetching SITC {sitc_code}: {e}")

            time.sleep(1)  # Rate limiting

        return results

    def download_ext_lt_intratrd_2020(self):
        """
        Download detailed intra/extra EU trade data
        Dataset: ext_lt_intratrd - Detailed trade data
        """
        print("\n" + "="*80)
        print("Downloading Detailed EU-China Trade Data")
        print("="*80)

        dataset_code = "ext_lt_intratrd"

        # Use simplified parameters for broader data
        params = {
            'format': 'JSON',
            'lang': 'EN',
            'freq': 'M',  # Monthly
            'product': 'TOTAL',  # All products initially
            'stk_flow': 'IMP,EXP',
            'partner': 'CN',
            'indicators': 'QUANTITY_IN_100KG,VALUE_IN_EUROS',
            'time': '2023M01,2023M12,2024M01,2024M08'  # Recent months
        }

        url = f"{self.api_base}/statistics/1.0/data/{dataset_code}"

        try:
            response = self.session.get(url, params=params, timeout=60)

            if response.status_code == 200:
                data = response.json()

                # Save raw data
                output_file = self.base_path / f'raw_data/monthly/{dataset_code}_China_recent.json'
                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2)

                print(f"Downloaded detailed trade data")

                # Analyze trade balance
                self.analyze_trade_balance(data)

                return data
            else:
                print(f"Failed to fetch detailed data: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"Error fetching detailed trade: {e}")
            return None

    def download_cn8_product_codes(self):
        """
        Download CN8 (Combined Nomenclature) for detailed product analysis
        Focus on technology and strategic goods
        """
        print("\n" + "="*80)
        print("Downloading CN8 Product Classifications")
        print("="*80)

        # CN8 codes for strategic technology categories
        strategic_cn8_prefixes = {
            '8471': 'Automatic data processing machines (computers)',
            '8517': 'Telephones and telecommunications equipment',
            '8525': 'Transmission apparatus for radio/TV',
            '8541': 'Semiconductor devices',
            '8542': 'Electronic integrated circuits',
            '9013': 'Liquid crystal devices, lasers',
            '9027': 'Instruments for physical/chemical analysis',
            '9031': 'Measuring or checking instruments',
            '3002': 'Human blood; vaccines, toxins',
            '3004': 'Medicaments',
            '2804': 'Hydrogen, rare gases, other non-metals',
            '2844': 'Radioactive chemical elements',
            '7219': 'Flat-rolled stainless steel',
            '7601': 'Unwrought aluminum',
            '8101': 'Tungsten and articles thereof',
            '8112': 'Beryllium, chromium, germanium, vanadium'
        }

        dataset_code = "DS-045409"  # EU trade since 1988 by CN8

        results = []

        for cn8_code, description in strategic_cn8_prefixes.items():
            print(f"\nFetching {description} (CN8 {cn8_code})...")

            # Construct bulk download URL
            url = f"{self.bulk_base}?sort=1&file=data%2Fcomext%2F{dataset_code}.tsv.gz"

            # For demonstration, we'll use the API endpoint instead
            api_url = f"{self.api_base}/statistics/1.0/data/DS-045409"

            params = {
                'format': 'JSON',
                'lang': 'EN',
                'freq': 'M',
                'product': cn8_code,
                'stk_flow': 'IMP,EXP',
                'partner': 'CN',
                'indicators': 'VALUE_IN_EUROS',
                'time': '2024M01,2024M06'
            }

            try:
                response = self.session.get(api_url, params=params, timeout=60)

                if response.status_code == 200:
                    data = response.json()

                    # Save product-specific data
                    output_file = self.base_path / f'processed/strategic_goods/CN8_{cn8_code}_China.json'
                    with open(output_file, 'w') as f:
                        json.dump(data, f, indent=2)

                    print(f"  Saved {description} trade data")

                    # Extract key metrics
                    metrics = self.extract_cn8_metrics(data, cn8_code, description)
                    results.append(metrics)

                else:
                    print(f"  No data available for CN8 {cn8_code}")

            except Exception as e:
                self.logger.error(f"Error fetching CN8 {cn8_code}: {e}")

            time.sleep(1)

        return results

    def parse_eurostat_json(self, data, code, description):
        """Parse Eurostat JSON response into structured data"""
        parsed_data = []

        try:
            if 'value' in data:
                values = data['value']
                dimensions = data.get('dimension', {})

                # Extract time periods
                time_dim = dimensions.get('time', {}).get('category', {}).get('index', {})

                for idx, value in values.items():
                    if value is not None:
                        record = {
                            'product_code': code,
                            'product_description': description,
                            'value': value,
                            'index': idx
                        }
                        parsed_data.append(record)

        except Exception as e:
            self.logger.error(f"Error parsing JSON: {e}")

        return parsed_data

    def extract_cn8_metrics(self, data, cn8_code, description):
        """Extract key metrics from CN8 trade data"""
        metrics = {
            'cn8_code': cn8_code,
            'description': description,
            'total_imports': 0,
            'total_exports': 0,
            'trade_balance': 0,
            'data_points': 0
        }

        try:
            if 'value' in data:
                for value in data['value'].values():
                    if value:
                        metrics['data_points'] += 1
                        # Would need to parse flow direction from dimensions
                        metrics['total_imports'] += value if value > 0 else 0

                metrics['trade_balance'] = metrics['total_exports'] - metrics['total_imports']

        except Exception as e:
            self.logger.error(f"Error extracting metrics: {e}")

        return metrics

    def analyze_trade_balance(self, data):
        """Analyze EU-China trade balance from data"""
        print("\n" + "-"*60)
        print("EU-China Trade Balance Analysis")
        print("-"*60)

        try:
            if data and 'value' in data:
                total_value = sum(v for v in data['value'].values() if v)
                num_records = len([v for v in data['value'].values() if v])

                print(f"Total trade value: €{total_value:,.0f}")
                print(f"Number of records: {num_records}")

                # Save analysis
                analysis = {
                    'timestamp': datetime.now().isoformat(),
                    'total_value': total_value,
                    'num_records': num_records,
                    'data': data.get('dimension', {})
                }

                output_file = self.base_path / 'analysis/trade_balance/eu_china_balance.json'
                with open(output_file, 'w') as f:
                    json.dump(analysis, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in trade balance analysis: {e}")

    def create_eurostat_database(self):
        """Create SQLite database for Eurostat trade data"""
        print("\n" + "="*80)
        print("Creating Eurostat Database")
        print("="*80)

        db_path = self.base_path.parent / 'databases' / f'eurostat_comext_{datetime.now().strftime("%Y%m%d")}.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # EU-China trade flows table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS eu_china_trade (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER,
                month INTEGER,
                product_code TEXT,
                product_description TEXT,
                sitc_code TEXT,
                cn8_code TEXT,
                flow_direction TEXT,
                value_euros REAL,
                quantity_100kg REAL,
                unit_price REAL,
                data_source TEXT
            )
        ''')

        # Strategic goods tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategic_goods_trade (
                product_code TEXT PRIMARY KEY,
                product_description TEXT,
                category TEXT,
                total_imports_from_china REAL,
                total_exports_to_china REAL,
                trade_balance REAL,
                sensitivity_score INTEGER,
                dual_use_flag INTEGER,
                analysis_date TEXT
            )
        ''')

        # Monthly trade summaries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monthly_summaries (
                year_month TEXT PRIMARY KEY,
                total_imports REAL,
                total_exports REAL,
                trade_balance REAL,
                top_import_category TEXT,
                top_export_category TEXT
            )
        ''')

        # Technology transfer indicators
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tech_transfer_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_category TEXT,
                indicator_type TEXT,
                indicator_value REAL,
                trend TEXT,
                risk_assessment TEXT,
                detection_date TEXT
            )
        ''')

        conn.commit()
        conn.close()

        print(f"Created database: {db_path}")
        return db_path

    def download_bulk_datasets(self):
        """Download larger bulk datasets for comprehensive analysis"""
        print("\n" + "="*80)
        print("Downloading Bulk Trade Datasets")
        print("="*80)

        bulk_datasets = [
            {
                'code': 'ext_st_eu27_2020sitc',
                'description': 'EU trade by SITC',
                'format': 'tsv.gz'
            },
            {
                'code': 'DS-045409',
                'description': 'EU trade by CN8',
                'format': 'tsv.gz'
            },
            {
                'code': 'ext_lt_intratrd',
                'description': 'Detailed trade statistics',
                'format': 'tsv.gz'
            }
        ]

        for dataset in bulk_datasets:
            print(f"\nChecking availability of {dataset['description']}...")

            # Note: Actual bulk download would require proper URL construction
            # This is a placeholder for the structure
            url = f"{self.bulk_base}?sort=1&file=data%2Fcomext%2F{dataset['code']}.{dataset['format']}"

            print(f"  Bulk URL: {url}")
            print(f"  Note: Large bulk files available via Eurostat bulk download service")

    def run_full_collection(self):
        """Execute complete Eurostat data collection"""
        print("="*80)
        print("Eurostat COMEXT Complete Data Collection")
        print("="*80)

        results = {
            'sitc_data': [],
            'detailed_trade': None,
            'cn8_products': [],
            'database': None
        }

        try:
            # Step 1: Download SITC categorized data
            print("\nStep 1: Downloading SITC trade data...")
            results['sitc_data'] = self.download_ext_st_eu27_2020sitc()

            # Step 2: Download detailed trade data
            print("\nStep 2: Downloading detailed trade statistics...")
            results['detailed_trade'] = self.download_ext_lt_intratrd_2020()

            # Step 3: Download strategic CN8 products
            print("\nStep 3: Downloading CN8 strategic goods data...")
            results['cn8_products'] = self.download_cn8_product_codes()

            # Step 4: Information about bulk downloads
            print("\nStep 4: Bulk dataset information...")
            self.download_bulk_datasets()

            # Step 5: Create analysis database
            print("\nStep 5: Creating analysis database...")
            results['database'] = str(self.create_eurostat_database())

            print("\n" + "="*80)
            print("Eurostat Collection Complete!")
            print("="*80)
            print(f"SITC categories processed: {len(results['sitc_data'])}")
            print(f"CN8 products analyzed: {len(results['cn8_products'])}")
            print(f"Database created: {results['database']}")
            print(f"\nData location: {self.base_path}")

            # Save summary
            summary_file = self.base_path / 'collection_summary.json'
            with open(summary_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'sitc_records': len(results['sitc_data']),
                    'cn8_products': len(results['cn8_products']),
                    'database': results['database']
                }, f, indent=2)

            return results

        except Exception as e:
            self.logger.error(f"Collection failed: {e}")
            raise

if __name__ == "__main__":
    collector = EurostatComextCollector()
    results = collector.run_full_collection()

    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. For bulk downloads (GB of data), visit:")
    print("   https://ec.europa.eu/eurostat/web/international-trade-in-goods/data/database")
    print("\n2. Key datasets to explore:")
    print("   - DS-045409: Most detailed CN8 trade data")
    print("   - ext_st_eu27_2020sitc: SITC categorized trade")
    print("   - DS-018995: Extra-EU trade by partner")
    print("\n3. Analysis focus areas:")
    print("   - Technology transfers (CN8 chapters 84-85, 90)")
    print("   - Strategic materials (CN8 chapters 28-29, 72-81)")
    print("   - Dual-use goods tracking")
