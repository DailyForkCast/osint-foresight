#!/usr/bin/env python3
"""
Eurostat Bulk Data Downloader - Alternative to failing COMEXT API
Downloads bulk trade data files directly from Eurostat
"""

import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import gzip
import shutil
import time

class EurostatBulkDownloader:
    def __init__(self):
        """Initialize downloader with bulk data URLs"""
        self.output_path = Path("F:/OSINT_Data/Eurostat_Bulk")
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Eurostat bulk download base URL
        self.bulk_base = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing"

        # Key trade datasets for EU-China analysis
        self.datasets = {
            'ext_st_eu27_2020sitc': {
                'name': 'EU27 trade by SITC',
                'description': 'Trade statistics by SITC classification',
                'url': f'{self.bulk_base}?file=data%2Fext_st_eu27_2020sitc.tsv.gz'
            },
            'DS-045409': {
                'name': 'EU trade by CN8',
                'description': 'Detailed trade by CN8 product codes',
                'url': f'{self.bulk_base}?file=data%2FDS-045409.tsv.gz'
            },
            'DS-016890': {
                'name': 'EU trade by HS6',
                'description': 'Trade statistics by HS6 classification',
                'url': f'{self.bulk_base}?file=data%2FDS-016890.tsv.gz'
            },
            'DS-018995': {
                'name': 'EU trade by partner country',
                'description': 'Bilateral trade flows with China',
                'url': f'{self.bulk_base}?file=data%2FDS-018995.tsv.gz'
            }
        }

        # Direct download URLs for smaller critical datasets
        self.direct_downloads = [
            {
                'name': 'china_trade_monthly',
                'url': 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/EXT_LT_INTRATRD?PARTNER=CN&TIME_PERIOD=2023-01..2025-09',
                'format': 'json'
            }
        ]

    def download_bulk_file(self, dataset_key, dataset_info):
        """Download a single bulk dataset"""
        print(f"\nDownloading: {dataset_info['name']}")
        print(f"Description: {dataset_info['description']}")

        output_file = self.output_path / f"{dataset_key}_{datetime.now().strftime('%Y%m%d')}.tsv.gz"

        try:
            print(f"URL: {dataset_info['url']}")
            print("This may take several minutes for large files...")

            # Download with streaming to handle large files
            response = requests.get(dataset_info['url'], stream=True, timeout=300)

            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                print(f"\rProgress: {progress:.1f}% ({downloaded/1024/1024:.1f}MB/{total_size/1024/1024:.1f}MB)", end='')

                print(f"\n[OK] Downloaded to: {output_file}")
                print(f"File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")

                # Extract and analyze if file is not too large
                if output_file.stat().st_size < 500 * 1024 * 1024:  # Less than 500MB
                    self.analyze_bulk_file(output_file, dataset_key)

                return True, output_file

            else:
                print(f"[ERROR] HTTP {response.status_code}")
                return False, None

        except Exception as e:
            print(f"[ERROR] Download failed: {str(e)[:200]}")
            return False, None

    def analyze_bulk_file(self, gz_file, dataset_key):
        """Analyze downloaded bulk file for China-related trade"""
        print(f"\nAnalyzing {dataset_key} for China trade data...")

        try:
            # Extract to TSV
            tsv_file = gz_file.with_suffix('')
            with gzip.open(gz_file, 'rb') as f_in:
                with open(tsv_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Read first 1000 rows to understand structure
            df_sample = pd.read_csv(tsv_file, sep='\t', nrows=1000, encoding='utf-8-sig')

            print(f"Dataset structure:")
            print(f"  Columns: {', '.join(df_sample.columns[:5])}...")
            print(f"  Sample rows: {len(df_sample)}")

            # Look for China-related data
            china_indicators = ['CN', 'CHN', 'CHINA', '156']  # Country codes for China
            china_found = False

            for col in df_sample.columns:
                if df_sample[col].astype(str).str.contains('|'.join(china_indicators), case=False, na=False).any():
                    china_found = True
                    china_rows = df_sample[df_sample[col].astype(str).str.contains('|'.join(china_indicators), case=False, na=False)]
                    print(f"  [OK] China data found in column '{col}': {len(china_rows)} rows")

            if not china_found:
                print("  [WARNING] No China data found in sample")

            # Clean up TSV file to save space
            tsv_file.unlink()

        except Exception as e:
            print(f"  [ERROR] Analysis failed: {str(e)[:200]}")

    def download_direct_apis(self):
        """Try direct API endpoints for specific China trade data"""
        print("\n" + "="*60)
        print("ATTEMPTING DIRECT API DOWNLOADS")
        print("="*60)

        for endpoint in self.direct_downloads:
            print(f"\nTrying: {endpoint['name']}")

            try:
                response = requests.get(endpoint['url'], timeout=60)

                if response.status_code == 200:
                    filename = f"{endpoint['name']}_{datetime.now().strftime('%Y%m%d')}.{endpoint['format']}"
                    output_file = self.output_path / filename

                    with open(output_file, 'wb') as f:
                        f.write(response.content)

                    print(f"  [OK] Downloaded to: {output_file}")
                    print(f"  Size: {len(response.content) / 1024:.2f} KB")

                else:
                    print(f"  [ERROR] HTTP {response.status_code}")

            except Exception as e:
                print(f"  [ERROR] Failed: {str(e)[:100]}")

    def download_alternative_sources(self):
        """Download from alternative sources"""
        print("\n" + "="*60)
        print("ALTERNATIVE DATA SOURCES")
        print("="*60)

        alternatives = [
            {
                'name': 'UN Comtrade China-EU',
                'url': 'https://comtrade.un.org/api/get?r=all&p=156&ps=2023&cc=AG6&fmt=csv',
                'description': 'UN Comtrade database for China trade'
            },
            {
                'name': 'World Bank WITS',
                'url': 'https://wits.worldbank.org/API/V1/SDMX/V21/datasource/tradestats-trade/reporter/chn/year/2023/partner/all/product/total/indicator/XPRT-TRD-VL',
                'description': 'World Bank trade statistics'
            }
        ]

        for source in alternatives:
            print(f"\nTrying: {source['name']}")
            print(f"Description: {source['description']}")

            try:
                response = requests.get(source['url'], timeout=60)

                if response.status_code == 200:
                    filename = f"{source['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
                    output_file = self.output_path / 'alternatives' / filename
                    output_file.parent.mkdir(exist_ok=True)

                    with open(output_file, 'wb') as f:
                        f.write(response.content)

                    print(f"  [OK] Downloaded to: {output_file}")

                else:
                    print(f"  [ERROR] HTTP {response.status_code}")

            except Exception as e:
                print(f"  [ERROR] Failed: {str(e)[:100]}")

            time.sleep(2)  # Rate limiting

    def generate_download_report(self, results):
        """Generate report of download results"""
        print("\n" + "="*80)
        print("EUROSTAT BULK DOWNLOAD SUMMARY")
        print("="*80)

        successful = [k for k, v in results.items() if v['success']]
        failed = [k for k, v in results.items() if not v['success']]

        print(f"\nSuccessful downloads: {len(successful)}")
        for dataset in successful:
            print(f"  ✓ {dataset}: {results[dataset]['file']}")

        if failed:
            print(f"\nFailed downloads: {len(failed)}")
            for dataset in failed:
                print(f"  ✗ {dataset}")

        # Save report
        report = {
            'timestamp': datetime.now().isoformat(),
            'successful_downloads': successful,
            'failed_downloads': failed,
            'output_directory': str(self.output_path),
            'results': results
        }

        report_file = self.output_path / f"download_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        import json
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to: {report_file}")

        return report

    def run_bulk_download(self):
        """Run complete bulk download process"""
        print("="*80)
        print("EUROSTAT BULK DATA DOWNLOAD")
        print("="*80)
        print("Alternative to failing COMEXT API")
        print(f"Output directory: {self.output_path}")

        results = {}

        # 1. Try bulk downloads
        print("\n" + "="*60)
        print("DOWNLOADING BULK TRADE DATASETS")
        print("="*60)

        for key, info in self.datasets.items():
            success, file_path = self.download_bulk_file(key, info)
            results[key] = {
                'success': success,
                'file': str(file_path) if file_path else None
            }
            time.sleep(5)  # Be polite to Eurostat servers

        # 2. Try direct API endpoints
        self.download_direct_apis()

        # 3. Try alternative sources
        self.download_alternative_sources()

        # 4. Generate report
        report = self.generate_download_report(results)

        print("\n" + "="*80)
        print("BULK DOWNLOAD COMPLETE")
        print("="*80)

        return report

if __name__ == "__main__":
    print("Starting Eurostat Bulk Data Download...")
    print("This will download large files - ensure sufficient disk space")

    downloader = EurostatBulkDownloader()
    report = downloader.run_bulk_download()

    print("\n[COMPLETE] Eurostat bulk download finished")
    print("Check output directory for downloaded files")
