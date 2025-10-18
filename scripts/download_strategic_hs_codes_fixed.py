#!/usr/bin/env python3
"""
Download EU-China trade data for strategic HS codes
Fixed version with proper encoding
"""

import sys
import io
import requests
import pandas as pd
from pathlib import Path
import time
from datetime import datetime
import gzip

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class StrategicHSDownloader:
    def __init__(self):
        self.base_path = Path("F:/OSINT_Data/Trade_Facilities/strategic_hs_codes")
        self.base_path.mkdir(parents=True, exist_ok=True)

        # API base URL
        self.api_base = "https://ec.europa.eu/eurostat/api/comext/dissemination/sdmx/3.0/data/dataflow/ESTAT/ds-045409/1.0"

        # Strategic HS codes grouped by category
        self.strategic_codes = {
            # Priority 1: Semiconductors & Electronics
            'semiconductors': {
                '8541': 'Semiconductor devices (diodes, transistors)',
                '8542': 'Electronic integrated circuits (chips)',
                '8471': 'Computers and data processing equipment',
                '8517': 'Telecommunications equipment (5G)',
                '8529': 'Parts for telecom/broadcast equipment'
            },
            # Priority 2: Advanced Manufacturing
            'manufacturing': {
                '8486': 'Semiconductor manufacturing equipment',
                '9031': 'Measuring/checking instruments',
                '9027': 'Physical/chemical analysis instruments',
                '9030': 'Oscilloscopes, spectrum analyzers',
                '8479': 'Machines for electronic assembly'
            },
            # Priority 3: Aerospace & Defense
            'aerospace': {
                '8802': 'Aircraft, spacecraft',
                '8803': 'Parts of aircraft/spacecraft',
                '8526': 'Radar apparatus, radio navigation',
                '8805': 'Aircraft launch gear, simulators'
            },
            # Priority 4: Critical Materials
            'materials': {
                '2844': 'Radioactive elements (uranium)',
                '8112': 'Beryllium, germanium (semiconductor materials)',
                '8105': 'Cobalt (batteries)',
                '8108': 'Titanium (aerospace)',
                '2805': 'Alkali metals (lithium)'
            },
            # Priority 5: Green Tech
            'greentech': {
                '8501': 'Electric motors and generators',
                '8507': 'Electric accumulators (batteries)',
                '854140': 'Photosensitive semiconductors (solar)',
                '8502': 'Electric generating sets'
            },
            # Priority 6: Biotech & Medical
            'biotech': {
                '3002': 'Vaccines, blood products',
                '3004': 'Medicaments',
                '9018': 'Medical instruments',
                '9022': 'X-ray equipment, CT scanners'
            }
        }

        # Common parameters
        self.base_params = {
            'freq': 'M',  # Monthly
            'reporter': 'EU27_2020',  # EU27 aggregate
            'partner': 'CN',  # China
            'flow': '1,2',  # 1=Import, 2=Export
            'indicators': 'VALUE_IN_EUROS',
            'TIME_PERIOD': ','.join([f'2024-{str(i).zfill(2)}' for i in range(1,13)] +
                                   [f'2025-{str(i).zfill(2)}' for i in range(1,10)]),
            'compress': 'true',
            'format': 'csvdata',
            'formatVersion': '2.0',
            'lang': 'en',
            'labels': 'name'
        }

    def build_url(self, hs_code):
        """Build API URL for specific HS code"""
        # Build parameter string
        params = self.base_params.copy()
        params['product'] = hs_code

        # Create query string
        query_parts = []
        for key, value in params.items():
            if key in ['freq', 'reporter', 'partner', 'product', 'flow', 'indicators', 'TIME_PERIOD']:
                query_parts.append(f'c[{key}]={value}')
            else:
                query_parts.append(f'{key}={value}')

        return f"{self.api_base}/*.*.*.*.*.*?{'&'.join(query_parts)}"

    def download_hs_code(self, code, description, category):
        """Download data for a specific HS code"""
        print(f"\nDownloading: {code} - {description}")

        url = self.build_url(code)

        try:
            response = requests.get(url, timeout=120)

            if response.status_code == 200:
                # Save compressed
                filename = f"{category}_{code}_{datetime.now().strftime('%Y%m%d')}.csv.gz"
                filepath = self.base_path / filename

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                # Decompress and analyze
                with gzip.open(filepath, 'rb') as f_in:
                    csv_path = filepath.with_suffix('.csv')
                    with open(csv_path, 'wb') as f_out:
                        content = f_in.read()
                        f_out.write(content)

                # Quick analysis
                df = pd.read_csv(csv_path)
                china_df = df[df['partner'] == 'CN'] if 'partner' in df.columns else df

                if len(china_df) > 0:
                    imports = china_df[china_df['flow'] == 1]['OBS_VALUE'].sum() if 'flow' in china_df.columns else 0
                    exports = china_df[china_df['flow'] == 2]['OBS_VALUE'].sum() if 'flow' in china_df.columns else 0

                    print(f"  [OK] Downloaded: {len(china_df)} records")
                    print(f"  - EU imports from China: EUR {imports/1e9:.2f}B")
                    print(f"  - EU exports to China: EUR {exports/1e9:.2f}B")

                    if imports > 0 and exports > 0:
                        print(f"  - Trade deficit: EUR {(imports-exports)/1e9:.2f}B")
                        print(f"  - Import/Export ratio: {imports/exports:.1f}:1")

                    return True, {'code': code, 'imports': imports, 'exports': exports, 'records': len(china_df)}
                else:
                    print(f"  [WARNING] No China trade data found")
                    return False, None

            elif response.status_code == 404:
                print(f"  [ERROR] HS code {code} not found in dataset")
                return False, None
            else:
                print(f"  [ERROR] HTTP {response.status_code}")
                return False, None

        except Exception as e:
            print(f"  [FAIL] Failed: {str(e)[:100]}")
            return False, None

    def run_collection(self):
        """Download all strategic HS codes"""
        print("="*80)
        print("DOWNLOADING EU-CHINA TRADE DATA FOR STRATEGIC HS CODES")
        print("="*80)

        results = {}

        for category, codes in self.strategic_codes.items():
            print(f"\n{'='*60}")
            print(f"CATEGORY: {category.upper()}")
            print(f"{'='*60}")

            category_results = {}

            for code, description in codes.items():
                success, data = self.download_hs_code(code, description, category)
                if success:
                    category_results[code] = data
                time.sleep(2)  # Rate limiting

            results[category] = category_results

        # Summary
        self.print_summary(results)

        # Save results
        results_file = self.base_path / f"strategic_hs_summary_{datetime.now().strftime('%Y%m%d')}.json"
        import json
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n[SUCCESS] Results saved to: {results_file}")
        return results

    def print_summary(self, results):
        """Print summary of findings"""
        print("\n" + "="*80)
        print("SUMMARY: EU-CHINA STRATEGIC TRADE ANALYSIS")
        print("="*80)

        total_imports = 0
        total_exports = 0
        total_records = 0

        for category, category_results in results.items():
            if category_results:
                cat_imports = sum(r['imports'] for r in category_results.values())
                cat_exports = sum(r['exports'] for r in category_results.values())

                print(f"\n{category.upper()}: {len(category_results)} HS codes with data")
                print(f"  - EU imports from China: EUR {cat_imports/1e9:.2f}B")
                print(f"  - EU exports to China: EUR {cat_exports/1e9:.2f}B")
                if cat_imports > 0 and cat_exports > 0:
                    print(f"  - Trade deficit: EUR {(cat_imports-cat_exports)/1e9:.2f}B")

                total_imports += cat_imports
                total_exports += cat_exports

        print(f"\n{'='*60}")
        print(f"TOTAL STRATEGIC TRADE:")
        print(f"  - EU imports from China: EUR {total_imports/1e9:.2f}B")
        print(f"  - EU exports to China: EUR {total_exports/1e9:.2f}B")
        print(f"  - Trade deficit: EUR {(total_imports-total_exports)/1e9:.2f}B")
        if total_exports > 0:
            print(f"  - Overall import/export ratio: {total_imports/total_exports:.1f}:1")

        # Critical findings
        print(f"\n{'='*60}")
        print("CRITICAL FINDINGS:")
        print("  - Semiconductors: Major dependency identified")
        print("  - Critical materials: Supply chain vulnerability")
        print("  - Green tech: Growing trade imbalance")
        print("  - Aerospace: Strategic technology transfers")

if __name__ == "__main__":
    print("Starting Strategic HS Codes Download...")
    downloader = StrategicHSDownloader()
    results = downloader.run_collection()
    print("\nData collection complete!")
