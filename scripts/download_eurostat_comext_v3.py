#!/usr/bin/env python3
"""
Eurostat COMEXT Data Downloader - SDMX 3.0 API
Downloads EU-China trade data using the new API endpoint
"""

import os
import requests
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
import time
import gzip
import io
from urllib.parse import quote

class EurostatCOMEXTv3Downloader:
    def __init__(self):
        self.base_path = Path("F:/OSINT_Data/Trade_Facilities/eurostat_comext_v3")
        self.base_path.mkdir(parents=True, exist_ok=True)

        # New SDMX 3.0 API base URL
        self.api_base = "https://ec.europa.eu/eurostat/api/comext/dissemination/sdmx/3.0/data/dataflow/ESTAT"

        # Priority datasets with China focus
        self.datasets = {
            'DS-045409': {
                'name': 'EU trade by CN8 (8-digit products)',
                'params': {
                    'freq': 'M',  # Monthly data
                    'partner': 'CN',  # China
                    'reporter': 'EU27_2020',  # EU27
                    'flow': ['IMPORT', 'EXPORT'],
                    'period': ['2023', '2024']  # Recent data
                }
            },
            'DS-059329': {
                'name': 'EU trade by BEC rev.5',
                'params': {
                    'freq': 'M',
                    'partner': 'CN',
                    'reporter': 'EU27_2020',
                    'flow': ['IMPORT', 'EXPORT'],
                    'period': ['2023', '2024']
                }
            },
            'DS-059331': {
                'name': 'International trade by SITC',
                'params': {
                    'freq': 'A',  # Annual
                    'partner': 'CN',
                    'reporter': 'EU27_2020',
                    'flow': ['IMP', 'EXP'],
                    'period': ['2020', '2021', '2022', '2023']
                }
            },
            'DS-059341': {
                'name': 'Trade by HS2-4-6',
                'params': {
                    'freq': 'M',
                    'partner': 'CN',
                    'reporter': 'EU27_2020',
                    'flow': ['IMPORT', 'EXPORT'],
                    'period': ['2023', '2024']
                }
            }
        }

        # Strategic product codes to focus on
        self.strategic_products = {
            '8542': 'Electronic integrated circuits',
            '8541': 'Semiconductor devices',
            '8517': 'Telephone/telecom equipment',
            '8471': 'Computers/data processing',
            '9027': 'Scientific instruments',
            '8525': 'Transmission apparatus',
            '3002': 'Vaccines, blood products',
            '2844': 'Radioactive elements',
            '8802': 'Aircraft',
            '8803': 'Aircraft parts'
        }

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def build_api_url(self, dataset_id, filters=None):
        """Build SDMX 3.0 API URL with filters"""

        # Base URL format: /dataflow/ESTAT/{dataset_id}$defaultview/1.0
        url = f"{self.api_base}/{dataset_id.lower()}$defaultview/1.0"

        # Build query parameters
        params = []

        # Add standard parameters
        params.append('compress=true')
        params.append('format=csvdata')
        params.append('formatVersion=2.0')
        params.append('lang=en')
        params.append('labels=name')

        # Add filters
        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    value_str = '+'.join(str(v) for v in value)
                else:
                    value_str = str(value)
                params.append(f'c[{key}]={value_str}')

        # Combine URL with parameters
        if params:
            url += '?' + '&'.join(params)

        return url

    def download_dataset(self, dataset_id, config):
        """Download a specific dataset with China filters"""

        print(f"\n" + "="*80)
        print(f"Downloading: {dataset_id} - {config['name']}")
        print("="*80)

        # Build filters for China trade
        filters = config.get('params', {})

        # Try different filter combinations if the first fails
        filter_sets = [
            filters,  # Full filters
            {k: v for k, v in filters.items() if k in ['freq', 'partner', 'reporter']},  # Basic filters
            {'freq': filters.get('freq', 'M')}  # Minimal filters
        ]

        for i, filter_set in enumerate(filter_sets):
            url = self.build_api_url(dataset_id, filter_set)

            print(f"\nAttempt {i+1}: Downloading with {'full' if i==0 else 'reduced'} filters...")
            print(f"URL: {url[:100]}...")

            try:
                # Download with streaming for large files
                response = requests.get(url, stream=True, timeout=120)

                if response.status_code == 200:
                    # Check if response is compressed
                    if response.headers.get('Content-Encoding') == 'gzip' or url.find('compress=true') > -1:
                        content = gzip.decompress(response.content)
                    else:
                        content = response.content

                    # Save to file
                    filename = f"{dataset_id}_china_trade_{datetime.now().strftime('%Y%m%d')}.csv"
                    filepath = self.base_path / filename

                    with open(filepath, 'wb') as f:
                        f.write(content)

                    file_size_mb = len(content) / 1024 / 1024
                    print(f"[OK] Downloaded {file_size_mb:.1f} MB to {filename}")

                    # Quick analysis of the data
                    self.analyze_downloaded_data(filepath, dataset_id)

                    return True

                elif response.status_code == 413:
                    print(f"[WARNING] Response too large, trying with time filter...")
                    # Try with just 2024 data
                    filter_set['period'] = '2024'
                    continue

                elif response.status_code == 404:
                    print(f"[ERROR] Dataset not found or filters invalid")
                    continue

                else:
                    print(f"[ERROR] HTTP {response.status_code}: {response.text[:200]}")
                    continue

            except requests.exceptions.Timeout:
                print(f"[ERROR] Request timed out")
                continue

            except Exception as e:
                print(f"[ERROR] Download failed: {e}")
                continue

            time.sleep(2)  # Rate limiting

        return False

    def analyze_downloaded_data(self, filepath, dataset_id):
        """Quick analysis of downloaded data"""

        try:
            # Read first 1000 rows for analysis
            df = pd.read_csv(filepath, nrows=1000)

            print(f"\n  Data Analysis:")
            print(f"  - Rows: {len(df)}")
            print(f"  - Columns: {list(df.columns)[:5]}...")

            # Check for China data
            china_cols = [col for col in df.columns if 'China' in str(col) or 'CN' in str(col)]
            if china_cols:
                print(f"  - China-related columns found: {china_cols[:3]}")

            # Check for strategic products
            for code, desc in self.strategic_products.items():
                matching_cols = [col for col in df.columns if code in str(col)]
                if matching_cols:
                    print(f"  - Strategic product {code} ({desc}) found")

        except Exception as e:
            print(f"  [WARNING] Could not analyze data: {e}")

    def download_strategic_products(self):
        """Download data for specific strategic product codes"""

        print(f"\n" + "="*80)
        print("Downloading Strategic Product Data")
        print("="*80)

        # Focus on DS-045409 (CN8 detailed) for strategic products
        dataset_id = 'DS-045409'

        for product_code, description in list(self.strategic_products.items())[:5]:  # Top 5
            print(f"\nFetching: {product_code} - {description}")

            filters = {
                'freq': 'M',
                'partner': 'CN',
                'reporter': 'EU27_2020',
                'product': product_code,
                'flow': 'IMPORT+EXPORT',
                'period': '2023+2024'
            }

            url = self.build_api_url(dataset_id, filters)

            try:
                response = requests.get(url, timeout=60)

                if response.status_code == 200:
                    filename = f"strategic_{product_code}_{datetime.now().strftime('%Y%m%d')}.csv"
                    filepath = self.base_path / filename

                    with open(filepath, 'wb') as f:
                        f.write(response.content)

                    print(f"  [OK] Saved to {filename}")
                else:
                    print(f"  [ERROR] Failed: HTTP {response.status_code}")

            except Exception as e:
                print(f"  [ERROR] {e}")

            time.sleep(1)

    def run_collection(self):
        """Run complete data collection"""

        results = {}

        # Test with basic request first
        print("\n" + "="*80)
        print("Testing COMEXT SDMX 3.0 API")
        print("="*80)

        test_url = f"{self.api_base}/ds-059329$defaultview/1.0?c[freq]=M&compress=false&format=csvdata&formatVersion=2.0&lang=en&labels=name"

        try:
            response = requests.head(test_url, timeout=10)
            if response.status_code in [200, 405]:  # 405 is OK for HEAD request
                print("[OK] API is accessible")
            else:
                print(f"[WARNING] API returned {response.status_code}")
        except Exception as e:
            print(f"[ERROR] API test failed: {e}")

        # Download priority datasets
        for dataset_id in ['DS-045409', 'DS-059329']:  # Start with most important
            if dataset_id in self.datasets:
                success = self.download_dataset(dataset_id, self.datasets[dataset_id])
                results[dataset_id] = "Downloaded" if success else "Failed"

        # Download strategic products
        self.download_strategic_products()

        # Summary
        print("\n" + "="*80)
        print("COMEXT Collection Summary")
        print("="*80)

        for dataset_id, status in results.items():
            print(f"{dataset_id}: {status}")

        print(f"\nData location: {self.base_path}")

        # Create manual download instructions
        self.create_manual_instructions()

        return results

    def create_manual_instructions(self):
        """Create instructions for manual download"""

        instructions_file = self.base_path / "MANUAL_DOWNLOAD_INSTRUCTIONS.txt"

        with open(instructions_file, 'w') as f:
            f.write("EUROSTAT COMEXT MANUAL DOWNLOAD INSTRUCTIONS\n")
            f.write("="*50 + "\n\n")

            f.write("If automated download fails, use these URLs in your browser:\n\n")

            for dataset_id, config in self.datasets.items():
                f.write(f"{dataset_id}: {config['name']}\n")
                f.write(f"URL: https://ec.europa.eu/eurostat/databrowser/view/{dataset_id}/default/table\n")
                f.write("Filters to apply:\n")
                f.write("  - Partner: China (CN)\n")
                f.write("  - Reporter: EU27_2020\n")
                f.write("  - Period: 2023-2024\n")
                f.write("  - Flow: Import and Export\n")
                f.write("Download as: SDMX-CSV 2.0\n\n")

        print(f"\n[OK] Created manual download instructions: {instructions_file}")

if __name__ == "__main__":
    downloader = EurostatCOMEXTv3Downloader()
    results = downloader.run_collection()
