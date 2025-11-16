#!/usr/bin/env python3
"""
AidData Comprehensive Dataset Downloader
Downloads all available datasets from aiddata.org to F:/OSINT_DATA/AidData/

Priority Datasets:
1. Global Chinese Development Finance Dataset v3.0 (20,985 projects, $1.34T, 2000-2021)
2. Chinese AI Exports Database (CAIED) (155 projects, $4.5B, 2000-2017)
3. Chinese Loan Contracts Dataset v2.0 (371 contracts, 60 countries)
4. Chinese Collateralized PPG Loans Dataset (620 loans, $418B)
5. US Financial Flows to Indo-Pacific
6. Listening to Leaders Survey Data
7. Foreign Aid Mapped to SDGs
8. Project Performance Database
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/aiddata_download.log'),
        logging.StreamHandler()
    ]
)

class AidDataDownloader:
    def __init__(self, base_dir="F:/OSINT_DATA/AidData"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Known dataset URLs from AidData
        self.datasets = {
            "global_chinese_finance_v3": {
                "name": "Global Chinese Development Finance Dataset v3.0",
                "url": "https://www.aiddata.org/data/aiddatas-global-chinese-development-finance-dataset-version-3-0",
                "download_page": "https://www.aiddata.org/data/aiddatas-global-chinese-development-finance-dataset-version-3-0",
                "description": "20,985 projects across 165 countries, $1.34 trillion, 2000-2021",
                "priority": 1
            },
            "chinese_ai_exports": {
                "name": "Chinese AI Exports Database (CAIED)",
                "url": "https://www.aiddata.org/data/chinese-ai-exports-database",
                "download_page": "https://www.aiddata.org/data/chinese-ai-exports-database",
                "description": "155 AI projects across 65 countries, $4.5 billion, 2000-2017",
                "priority": 1
            },
            "chinese_loan_contracts_v2": {
                "name": "Chinese Loan Contracts Dataset v2.0",
                "url": "https://www.aiddata.org/data/chinese-loan-contracts-dataset-version-2-0",
                "download_page": "https://www.aiddata.org/data/chinese-loan-contracts-dataset-version-2-0",
                "description": "371 debt contracts across 60 countries",
                "priority": 1
            },
            "chinese_collateralized_loans": {
                "name": "Chinese Collateralized PPG Loans Dataset",
                "url": "https://www.aiddata.org/data/chinese-collateralized-ppg-loans-dataset",
                "download_page": "https://www.aiddata.org/data/chinese-collateralized-ppg-loans-dataset",
                "description": "620 loan commitments, $418 billion, 31 creditors, 57 countries",
                "priority": 1
            },
            "us_indopacific_flows": {
                "name": "U.S. Financial Flows to Indo-Pacific",
                "url": "https://www.aiddata.org/data/us-financial-flows-to-indo-pacific",
                "download_page": "https://www.aiddata.org/data/us-financial-flows-to-indo-pacific",
                "description": "US financial engagement in Indo-Pacific region",
                "priority": 2
            },
            "listening_to_leaders": {
                "name": "Listening to Leaders Survey Data",
                "url": "https://www.aiddata.org/listening-to-leaders-2024",
                "download_page": "https://www.aiddata.org/listening-to-leaders-2024",
                "description": "Survey data from government leaders on development priorities",
                "priority": 2
            },
            "aid_sdg_mapping": {
                "name": "Foreign Aid Mapped to SDGs",
                "url": "https://www.aiddata.org/data/aiddata-core-research-release-version-3-1",
                "download_page": "https://www.aiddata.org/data/aiddata-core-research-release-version-3-1",
                "description": "Foreign aid projects mapped to Sustainable Development Goals",
                "priority": 2
            },
            "project_performance": {
                "name": "Project Performance Database",
                "url": "https://www.aiddata.org/data/geocoded-economic-data-and-code-release",
                "download_page": "https://www.aiddata.org/data/geocoded-economic-data-and-code-release",
                "description": "Performance metrics for development projects",
                "priority": 2
            }
        }

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Checkpoint tracking
        self.checkpoint_file = self.base_dir / "download_checkpoint.json"
        self.checkpoint = self.load_checkpoint()

    def load_checkpoint(self):
        """Load download checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {"downloaded": [], "failed": [], "last_update": None}

    def save_checkpoint(self):
        """Save download checkpoint"""
        self.checkpoint["last_update"] = datetime.now().isoformat()
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)

    def download_file(self, url, output_path, description=""):
        """Download a file with progress tracking"""
        try:
            logging.info(f"Downloading: {description}")
            logging.info(f"URL: {url}")
            logging.info(f"Output: {output_path}")

            response = self.session.get(url, stream=True, timeout=300)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            progress = (downloaded / total_size) * 100
                            print(f"\rProgress: {progress:.1f}%", end='', flush=True)

            print()  # New line after progress
            logging.info(f"✓ Downloaded: {output_path.name} ({downloaded:,} bytes)")
            return True

        except Exception as e:
            logging.error(f"✗ Failed to download {description}: {str(e)}")
            return False

    def fetch_dataset_page(self, dataset_id, dataset_info):
        """Fetch dataset page to find download links"""
        try:
            logging.info(f"\n{'='*80}")
            logging.info(f"Processing: {dataset_info['name']}")
            logging.info(f"Priority: {dataset_info['priority']}")
            logging.info(f"Description: {dataset_info['description']}")
            logging.info(f"{'='*80}")

            if dataset_id in self.checkpoint["downloaded"]:
                logging.info(f"✓ Already downloaded: {dataset_id}")
                return True

            # Create dataset directory
            dataset_dir = self.base_dir / dataset_id
            dataset_dir.mkdir(parents=True, exist_ok=True)

            # Fetch the download page
            response = self.session.get(dataset_info['download_page'], timeout=30)
            response.raise_for_status()

            # Save the page for manual inspection if needed
            page_file = dataset_dir / "download_page.html"
            with open(page_file, 'w', encoding='utf-8') as f:
                f.write(response.text)

            logging.info(f"✓ Saved download page: {page_file}")

            # Look for common download patterns
            content = response.text.lower()

            # Common AidData download patterns
            download_indicators = [
                'download',
                '.xlsx',
                '.csv',
                '.zip',
                '.pdf',
                'data file',
                'dataset',
                'documentation'
            ]

            found_links = []
            for line in response.text.split('\n'):
                if any(indicator in line.lower() for indicator in download_indicators):
                    if 'href=' in line.lower():
                        found_links.append(line.strip())

            if found_links:
                links_file = dataset_dir / "potential_download_links.txt"
                with open(links_file, 'w', encoding='utf-8') as f:
                    f.write(f"Dataset: {dataset_info['name']}\n")
                    f.write(f"URL: {dataset_info['download_page']}\n\n")
                    f.write("Potential download links found:\n")
                    f.write("="*80 + "\n")
                    for link in found_links:
                        f.write(link + "\n")

                logging.info(f"✓ Found {len(found_links)} potential download links")
                logging.info(f"  Saved to: {links_file}")

            # Save metadata
            metadata = {
                "dataset_id": dataset_id,
                "name": dataset_info["name"],
                "description": dataset_info["description"],
                "url": dataset_info["url"],
                "download_page": dataset_info["download_page"],
                "priority": dataset_info["priority"],
                "fetch_date": datetime.now().isoformat(),
                "status": "page_fetched",
                "manual_action_required": True,
                "instructions": "Visit the download page and complete any required forms to download datasets"
            }

            metadata_file = dataset_dir / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            logging.info(f"✓ Saved metadata: {metadata_file}")

            # Mark as processed (page fetched)
            self.checkpoint["downloaded"].append(dataset_id)
            self.save_checkpoint()

            return True

        except Exception as e:
            logging.error(f"✗ Error processing {dataset_id}: {str(e)}")
            self.checkpoint["failed"].append({
                "dataset_id": dataset_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            self.save_checkpoint()
            return False

    def download_all(self):
        """Download all datasets"""
        logging.info("="*80)
        logging.info("AidData Comprehensive Dataset Downloader")
        logging.info("="*80)
        logging.info(f"Base directory: {self.base_dir}")
        logging.info(f"Total datasets: {len(self.datasets)}")
        logging.info("")

        # Sort by priority
        sorted_datasets = sorted(
            self.datasets.items(),
            key=lambda x: x[1]["priority"]
        )

        success_count = 0
        fail_count = 0

        for dataset_id, dataset_info in sorted_datasets:
            if self.fetch_dataset_page(dataset_id, dataset_info):
                success_count += 1
            else:
                fail_count += 1

            # Rate limiting
            time.sleep(2)

        # Summary
        logging.info("\n" + "="*80)
        logging.info("DOWNLOAD SUMMARY")
        logging.info("="*80)
        logging.info(f"Total datasets: {len(self.datasets)}")
        logging.info(f"Processed: {success_count}")
        logging.info(f"Failed: {fail_count}")
        logging.info(f"Output directory: {self.base_dir}")
        logging.info("")
        logging.info("NEXT STEPS:")
        logging.info("1. Review the download_page.html files in each dataset directory")
        logging.info("2. Visit the URLs and complete any registration/download forms")
        logging.info("3. Download files manually to the respective directories")
        logging.info("4. Most AidData datasets require form submission for access")
        logging.info("="*80)

        # Generate summary report
        self.generate_summary_report()

    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        report_file = self.base_dir / "AIDDATA_DOWNLOAD_GUIDE.md"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# AidData Dataset Download Guide\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Overview\n\n")
            f.write("This guide provides information on downloading AidData datasets for the OSINT Foresight project.\n\n")
            f.write("## Priority Datasets (Download First)\n\n")

            # Priority 1 datasets
            priority1 = [(k, v) for k, v in self.datasets.items() if v["priority"] == 1]
            for dataset_id, info in priority1:
                f.write(f"### {info['name']}\n\n")
                f.write(f"**Description**: {info['description']}\n\n")
                f.write(f"**URL**: {info['download_page']}\n\n")
                f.write(f"**Local Directory**: `{self.base_dir / dataset_id}`\n\n")
                f.write("**Download Instructions**:\n")
                f.write("1. Visit the URL above\n")
                f.write("2. Complete any required registration form\n")
                f.write("3. Download all available files (CSV, XLSX, PDF documentation)\n")
                f.write(f"4. Save to: `{self.base_dir / dataset_id}`\n\n")
                f.write("---\n\n")

            f.write("## Secondary Datasets\n\n")

            # Priority 2 datasets
            priority2 = [(k, v) for k, v in self.datasets.items() if v["priority"] == 2]
            for dataset_id, info in priority2:
                f.write(f"### {info['name']}\n\n")
                f.write(f"**Description**: {info['description']}\n\n")
                f.write(f"**URL**: {info['download_page']}\n\n")
                f.write(f"**Local Directory**: `{self.base_dir / dataset_id}`\n\n")
                f.write("---\n\n")

            f.write("## Integration with OSINT Master Database\n\n")
            f.write("After downloading, datasets will be processed and integrated into:\n")
            f.write("- Master Database: `F:/OSINT_WAREHOUSE/osint_master.db`\n")
            f.write("- Tables: `aiddata_chinese_finance`, `aiddata_ai_exports`, etc.\n\n")
            f.write("## Key Insights Expected\n\n")
            f.write("- Chinese development finance patterns (20,985 projects, $1.34T)\n")
            f.write("- AI technology exports (155 projects, 65 countries)\n")
            f.write("- Loan contract terms and conditions (371 contracts)\n")
            f.write("- Collateralized lending patterns ($418B in loans)\n")
            f.write("- Cross-reference with existing USPTO, OpenAlex, USAspending data\n\n")

        logging.info(f"\n✓ Generated download guide: {report_file}")

def main():
    downloader = AidDataDownloader()
    downloader.download_all()

if __name__ == "__main__":
    main()
