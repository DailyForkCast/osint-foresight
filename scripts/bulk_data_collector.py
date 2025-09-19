"""
Bulk Data Collector for OSINT Foresight
Downloads large datasets to external F: drive
Includes SEC EDGAR, EPO patents, and other sources
"""

import os
import time
import json
import requests
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

# External drive setup
EXTERNAL_DRIVE = Path("F:/OSINT_DATA")
EXTERNAL_DRIVE.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BulkDataCollector:
    """Collect and organize bulk data on external drive"""

    def __init__(self):
        """Initialize bulk collector"""
        self.external_base = EXTERNAL_DRIVE
        self.rate_limit_delay = 0.5  # 500ms between requests

        # Create directory structure
        self.dirs = {
            'sec_edgar': self.external_base / 'SEC_EDGAR',
            'epo_patents': self.external_base / 'EPO_PATENTS',
            'lens': self.external_base / 'THE_LENS',
            'cordis': self.external_base / 'CORDIS',
            'ted': self.external_base / 'TED_PROCUREMENT',
            'openalex': self.external_base / 'OPENALEX'
        }

        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        self.headers = {
            "User-Agent": "OSINT-Foresight research@example.com",
            "Accept": "application/json"
        }

    def download_sec_bulk_submissions(self) -> str:
        """
        Download SEC bulk submissions file
        Contains all company submission histories
        ~1.5GB compressed
        """
        logger.info("Downloading SEC bulk submissions data...")

        url = "https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip"
        output_file = self.dirs['sec_edgar'] / f"submissions_{datetime.now().strftime('%Y%m%d')}.zip"

        if output_file.exists():
            logger.info(f"File already exists: {output_file}")
            return str(output_file)

        try:
            # Download with progress tracking
            response = requests.get(url, headers=self.headers, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 8192

            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\rDownloading: {progress:.1f}% ({downloaded/1024/1024:.1f}MB / {total_size/1024/1024:.1f}MB)", end='')

            print()  # New line after progress
            logger.info(f"Downloaded SEC bulk submissions to {output_file}")

            # Extract if needed
            if input("\nExtract submissions.zip? (y/n): ").lower() == 'y':
                self.extract_zip(output_file)

            return str(output_file)

        except Exception as e:
            logger.error(f"Failed to download SEC bulk data: {e}")
            raise

    def download_sec_company_facts(self) -> str:
        """
        Download SEC company facts in XBRL
        Contains financial data for all companies
        ~500MB compressed
        """
        logger.info("Downloading SEC company facts data...")

        url = "https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip"
        output_file = self.dirs['sec_edgar'] / f"companyfacts_{datetime.now().strftime('%Y%m%d')}.zip"

        if output_file.exists():
            logger.info(f"File already exists: {output_file}")
            return str(output_file)

        try:
            response = requests.get(url, headers=self.headers, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 8192

            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\rDownloading: {progress:.1f}% ({downloaded/1024/1024:.1f}MB / {total_size/1024/1024:.1f}MB)", end='')

            print()
            logger.info(f"Downloaded SEC company facts to {output_file}")

            return str(output_file)

        except Exception as e:
            logger.error(f"Failed to download company facts: {e}")
            raise

    def download_leonardo_drs_filings(self) -> Dict:
        """
        Download all Leonardo DRS filings
        Focus on 10-K, 10-Q, 8-K, DEF 14A
        """
        logger.info("Downloading Leonardo DRS filings...")

        from scripts.sec_edgar_client import SECEdgarClient
        client = SECEdgarClient()

        cik = "0001833756"
        leonardo_dir = self.dirs['sec_edgar'] / 'Leonardo_DRS'
        leonardo_dir.mkdir(exist_ok=True)

        # Get all submissions
        submissions = client.get_company_submissions(cik)

        # Create metadata file
        metadata = {
            'company': submissions.get('name'),
            'cik': cik,
            'tickers': submissions.get('tickers'),
            'sic': submissions.get('sicDescription'),
            'download_date': datetime.now().isoformat(),
            'total_filings': 0,
            'downloaded_filings': []
        }

        # Focus on key filing types
        target_forms = ['10-K', '10-Q', '8-K', 'DEF 14A', '20-F', 'S-1']

        recent = submissions.get('filings', {}).get('recent', {})

        for i, form in enumerate(recent.get('form', [])):
            if form in target_forms:
                filing_date = recent['filingDate'][i]
                accession = recent['accessionNumber'][i]
                primary_doc = recent.get('primaryDocument', [None])[i]

                if primary_doc:
                    # Construct URL
                    clean_accession = accession.replace('-', '')
                    url = f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{clean_accession}/{primary_doc}"

                    # Create filename
                    filename = f"{form}_{filing_date}_{primary_doc}".replace('/', '_')
                    output_path = leonardo_dir / filename

                    if not output_path.exists():
                        try:
                            # Download filing
                            response = requests.get(url, headers=self.headers)
                            response.raise_for_status()

                            with open(output_path, 'wb') as f:
                                f.write(response.content)

                            metadata['downloaded_filings'].append({
                                'form': form,
                                'date': filing_date,
                                'file': filename,
                                'size': len(response.content)
                            })

                            logger.info(f"Downloaded {form} from {filing_date}")
                            time.sleep(self.rate_limit_delay)

                        except Exception as e:
                            logger.error(f"Failed to download {form} from {filing_date}: {e}")

        metadata['total_filings'] = len(metadata['downloaded_filings'])

        # Save metadata
        metadata_file = leonardo_dir / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Downloaded {metadata['total_filings']} Leonardo DRS filings to {leonardo_dir}")

        return metadata

    def download_italian_patents_from_epo(self) -> Dict:
        """
        Download Italian patent data from EPO
        """
        logger.info("Downloading Italian patent data from EPO...")

        from scripts.epo_ops_client import EPOOPSClient
        client = EPOOPSClient()

        epo_dir = self.dirs['epo_patents'] / 'Italy'
        epo_dir.mkdir(exist_ok=True)

        results = {
            'italian_patents': None,
            'leonardo_patents': None,
            'italy_china_collaborations': None
        }

        try:
            # Search Italian patents
            logger.info("Searching Italian patents (2020-2025)...")
            italian = client.search_italian_patents(date_from="20200101", date_to="20251231")

            output_file = epo_dir / f"italian_patents_{datetime.now().strftime('%Y%m%d')}.json"
            with open(output_file, 'w') as f:
                json.dump(italian, f, indent=2)
            results['italian_patents'] = str(output_file)

            # Search Leonardo patents
            logger.info("Searching Leonardo patents...")
            leonardo = client.search_leonardo_patents()

            output_file = epo_dir / f"leonardo_patents_{datetime.now().strftime('%Y%m%d')}.json"
            with open(output_file, 'w') as f:
                json.dump(leonardo, f, indent=2)
            results['leonardo_patents'] = str(output_file)

            # Search Italy-China collaborations
            logger.info("Searching Italy-China collaboration patents...")
            collaborations = client.search_italy_china_collaborations()

            output_file = epo_dir / f"italy_china_patents_{datetime.now().strftime('%Y%m%d')}.json"
            with open(output_file, 'w') as f:
                json.dump(collaborations, f, indent=2)
            results['italy_china_collaborations'] = str(output_file)

        except Exception as e:
            logger.error(f"Error downloading EPO data: {e}")

        return results

    def extract_zip(self, zip_path: Path):
        """Extract a zip file to same directory"""
        logger.info(f"Extracting {zip_path}...")

        extract_dir = zip_path.parent / zip_path.stem
        extract_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        logger.info(f"Extracted to {extract_dir}")

    def collect_all_priority_data(self):
        """
        Collect all priority datasets
        """
        logger.info("Starting bulk data collection to F: drive...")
        logger.info(f"Target directory: {self.external_base}")

        results = {
            'sec_edgar': {},
            'epo_patents': {},
            'status': 'in_progress'
        }

        # 1. SEC EDGAR data
        print("\n" + "="*50)
        print("SEC EDGAR DATA COLLECTION")
        print("="*50)

        try:
            # Download bulk submissions
            results['sec_edgar']['submissions'] = self.download_sec_bulk_submissions()

            # Download company facts
            results['sec_edgar']['company_facts'] = self.download_sec_company_facts()

            # Download Leonardo DRS specific filings
            results['sec_edgar']['leonardo_drs'] = self.download_leonardo_drs_filings()

        except Exception as e:
            logger.error(f"SEC EDGAR collection failed: {e}")
            results['sec_edgar']['error'] = str(e)

        # 2. EPO Patent data
        print("\n" + "="*50)
        print("EPO PATENT DATA COLLECTION")
        print("="*50)

        try:
            results['epo_patents'] = self.download_italian_patents_from_epo()
        except Exception as e:
            logger.error(f"EPO collection failed: {e}")
            results['epo_patents']['error'] = str(e)

        # Save collection summary
        results['status'] = 'completed'
        results['timestamp'] = datetime.now().isoformat()
        results['location'] = str(self.external_base)

        summary_file = self.external_base / f"collection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)

        print("\n" + "="*50)
        print("COLLECTION SUMMARY")
        print("="*50)
        print(f"Data saved to: {self.external_base}")
        print(f"Summary file: {summary_file}")

        return results


if __name__ == "__main__":
    collector = BulkDataCollector()

    print("BULK DATA COLLECTOR FOR OSINT FORESIGHT")
    print("="*50)
    print(f"Target: F: drive ({EXTERNAL_DRIVE})")
    print("\nData sources to collect:")
    print("1. SEC EDGAR bulk submissions (1.5GB)")
    print("2. SEC company facts (500MB)")
    print("3. Leonardo DRS filings")
    print("4. EPO Italian patents")
    print("5. Italy-China patent collaborations")

    if input("\nStart bulk collection? (y/n): ").lower() == 'y':
        results = collector.collect_all_priority_data()
        print("\n[SUCCESS] Bulk data collection completed!")
        print(json.dumps(results, indent=2))
    else:
        print("Collection cancelled")
