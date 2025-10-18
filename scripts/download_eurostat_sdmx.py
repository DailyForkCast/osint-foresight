#!/usr/bin/env python3
"""
Eurostat SDMX Data Downloader
Downloads trade datasets using the official SDMX REST API
"""

import os
import requests
import pandas as pd
from pathlib import Path
import json
import logging
from datetime import datetime
import time
import gzip
import io

class EurostatSDMXDownloader:
    def __init__(self):
        self.base_path = Path("F:/OSINT_Data/Trade_Facilities/eurostat_sdmx")
        self.base_path.mkdir(parents=True, exist_ok=True)

        # SDMX API endpoint
        self.api_base = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1"

        # Key datasets from the XML file
        self.priority_datasets = {
            'DS-045409': 'EU trade since 1988 by HS2-4-6 and CN8',
            'DS-059331': 'International trade of EU and non-EU countries by SITC',
            'DS-059329': 'EU trade since 2017 by BEC/rev.5',
            'DS-059341': 'International trade by HS2-4-6',
            'DS-059334': 'Extra-EU trade by mode of transport',
            'DS-059328': 'EU trade since 2002 by BEC/rev.4',
            'DS-056120': 'Sold production, exports and imports (PRODCOM)',
            'DS-059327': 'EU trade since 2002 by CPA 2.1',
            'DS-059366': 'EU trade since 2002 by CPA 2.2'
        }

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def test_connection(self):
        """Test SDMX API connection"""
        print("\n" + "="*80)
        print("Testing Eurostat SDMX API Connection")
        print("="*80)

        # Test with a simple metadata request
        test_url = f"{self.api_base}/dataflow/ESTAT"

        try:
            response = requests.get(test_url, timeout=30)
            if response.status_code == 200:
                print("[OK] SDMX API connection successful!")
                return True
            else:
                print(f"[ERROR] API returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False

    def get_china_trade_data(self, dataset_id, dataset_name):
        """Download China-specific trade data from a dataset"""
        print(f"\n" + "="*80)
        print(f"Downloading: {dataset_id} - {dataset_name}")
        print("="*80)

        # Build SDMX query for China trade
        # Format: /data/{flowRef}/{key}
        # Key format depends on dataset, but generally includes:
        # FREQ.REPORTER.PARTNER.PRODUCT.FLOW

        # Try different query formats based on dataset type
        queries = []

        if 'CN8' in dataset_name or 'HS' in dataset_name:
            # For product-based datasets
            queries = [
                f"{self.api_base}/data/{dataset_id}/A.EU27_2020.CN.TOTAL.?.M",  # EU imports from China
                f"{self.api_base}/data/{dataset_id}/A.EU27_2020.CN.TOTAL.?.X",  # EU exports to China
                f"{self.api_base}/data/{dataset_id}/A.CN.EU27_2020.TOTAL.?.M",  # China imports from EU
                f"{self.api_base}/data/{dataset_id}/A.CN.EU27_2020.TOTAL.?.X"   # China exports to EU
            ]
        elif 'SITC' in dataset_name:
            # For SITC classification
            queries = [
                f"{self.api_base}/data/{dataset_id}/A.EU27_2020.CN.SITC_TOT.?.IMP",
                f"{self.api_base}/data/{dataset_id}/A.EU27_2020.CN.SITC_TOT.?.EXP"
            ]
        elif 'BEC' in dataset_name:
            # For BEC classification
            queries = [
                f"{self.api_base}/data/{dataset_id}/A.EU27_2020.CN.TOTAL.?.IMPORTS",
                f"{self.api_base}/data/{dataset_id}/A.EU27_2020.CN.TOTAL.?.EXPORTS"
            ]
        else:
            # Generic query
            queries = [
                f"{self.api_base}/data/{dataset_id}/?updatedAfter=2023-01-01&detail=dataonly"
            ]

        successful_downloads = 0

        for query_url in queries:
            try:
                print(f"\nTrying: {query_url.split('/')[-1][:50]}...")

                headers = {
                    'Accept': 'application/vnd.sdmx.data+csv;version=1.0.0'
                }

                response = requests.get(query_url, headers=headers, timeout=60)

                if response.status_code == 200:
                    # Save the data
                    filename = f"{dataset_id}_{successful_downloads}.csv"
                    filepath = self.base_path / filename

                    with open(filepath, 'wb') as f:
                        f.write(response.content)

                    print(f"  [OK] Saved {len(response.content)/1024:.1f} KB to {filename}")
                    successful_downloads += 1

                elif response.status_code == 404:
                    print(f"  [INFO] No data available for this query")
                elif response.status_code == 413:
                    print(f"  [WARNING] Response too large, trying with filters...")
                    # Try with year filter
                    filtered_url = query_url + "&startPeriod=2023&endPeriod=2024"
                    response = requests.get(filtered_url, headers=headers, timeout=60)
                    if response.status_code == 200:
                        filename = f"{dataset_id}_{successful_downloads}_2023_2024.csv"
                        filepath = self.base_path / filename
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        print(f"  [OK] Saved filtered data to {filename}")
                        successful_downloads += 1
                else:
                    print(f"  [ERROR] Status {response.status_code}")

                time.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"  [ERROR] Failed: {e}")

        return successful_downloads

    def download_bulk_dataset(self, dataset_id):
        """Download complete dataset in bulk format"""
        print(f"\nDownloading bulk dataset: {dataset_id}")

        # Bulk download URL format
        bulk_url = f"https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing"

        params = {
            'sort': '1',
            'file': f'data/comext/{dataset_id}.tsv.gz'
        }

        try:
            response = requests.get(bulk_url, params=params, stream=True, timeout=60)

            if response.status_code == 200:
                filename = f"{dataset_id}_bulk.tsv.gz"
                filepath = self.base_path / filename

                # Download in chunks
                chunk_size = 8192
                total_size = 0

                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            total_size += len(chunk)

                            # Progress indicator
                            if total_size % (chunk_size * 100) == 0:
                                print(f"  Downloaded {total_size / 1024 / 1024:.1f} MB...", end='\r')

                print(f"\n  [OK] Downloaded {total_size / 1024 / 1024:.1f} MB to {filename}")
                return True

            else:
                print(f"  [ERROR] Bulk download failed with status {response.status_code}")
                return False

        except Exception as e:
            print(f"  [ERROR] Bulk download failed: {e}")
            return False

    def get_dataset_structure(self, dataset_id):
        """Get dataset structure/metadata"""
        print(f"\nFetching structure for {dataset_id}...")

        # Get data structure definition
        dsd_url = f"{self.api_base}/datastructure/ESTAT/{dataset_id}"

        try:
            response = requests.get(dsd_url, timeout=30)

            if response.status_code == 200:
                # Save structure
                filepath = self.base_path / f"{dataset_id}_structure.xml"
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"  [OK] Saved structure to {filepath.name}")
                return True
            else:
                print(f"  [ERROR] Failed to get structure: {response.status_code}")
                return False

        except Exception as e:
            print(f"  [ERROR] Failed to get structure: {e}")
            return False

    def run_collection(self):
        """Run complete data collection"""
        # Test connection
        if not self.test_connection():
            print("\n[ERROR] Failed to connect to Eurostat SDMX API")
            return

        # Priority datasets for China analysis
        critical_datasets = [
            'DS-045409',  # CN8 detailed trade - MOST IMPORTANT
            'DS-059331',  # SITC classification
            'DS-059329'   # BEC classification
        ]

        results = {}

        print("\n" + "="*80)
        print("Downloading Critical Datasets")
        print("="*80)

        for dataset_id in critical_datasets:
            if dataset_id in self.priority_datasets:
                dataset_name = self.priority_datasets[dataset_id]

                # Get structure first
                self.get_dataset_structure(dataset_id)

                # Try SDMX API download
                count = self.get_china_trade_data(dataset_id, dataset_name)

                if count > 0:
                    results[dataset_id] = f"Downloaded {count} files via API"
                else:
                    # Try bulk download as fallback
                    if self.download_bulk_dataset(dataset_id):
                        results[dataset_id] = "Downloaded bulk file"
                    else:
                        results[dataset_id] = "Failed to download"

        # Summary
        print("\n" + "="*80)
        print("Eurostat SDMX Collection Summary")
        print("="*80)

        for dataset_id, status in results.items():
            print(f"{dataset_id}: {status}")

        print(f"\nData location: {self.base_path}")

        # Create download script for manual bulk downloads
        self.create_bulk_download_script()

        return results

    def create_bulk_download_script(self):
        """Create a batch script for manual bulk downloads"""
        script_path = self.base_path / "download_bulk.bat"

        with open(script_path, 'w') as f:
            f.write("@echo off\n")
            f.write("REM Eurostat Bulk Download Script\n")
            f.write("REM Run this to download large datasets\n\n")

            for dataset_id in self.priority_datasets:
                url = f"https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=data%%2Fcomext%%2F{dataset_id}.tsv.gz"
                f.write(f"echo Downloading {dataset_id}...\n")
                f.write(f'curl -L "{url}" -o "{dataset_id}.tsv.gz"\n')
                f.write(f"echo.\n\n")

            f.write("echo All downloads complete!\n")
            f.write("pause\n")

        print(f"\n[OK] Created bulk download script: {script_path}")
        print("     Run this script to download large datasets manually")

if __name__ == "__main__":
    downloader = EurostatSDMXDownloader()
    results = downloader.run_collection()
