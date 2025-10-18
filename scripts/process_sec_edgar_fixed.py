#!/usr/bin/env python3
"""
SEC EDGAR Fixed Processor with Checkpoint Support
Processes SEC EDGAR submissions ZIP file with proper error handling
"""

import os
import json
import logging
import zipfile
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sec_edgar_fixed.log'),
        logging.StreamHandler()
    ]
)

class SECEdgarProcessor:
    """Fixed SEC EDGAR processor with checkpoint support"""

    def __init__(self, zip_path: str, output_dir: str = "data/processed/sec_edgar_comprehensive"):
        self.zip_path = Path(zip_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Checkpoint file for resuming
        self.checkpoint_file = self.output_dir / "checkpoint.json"
        self.checkpoint = self.load_checkpoint()

        # API settings
        self.headers = {
            "User-Agent": "OSINT-Foresight Research (osint-research@example.com)"
        }

        # Chinese company indicators
        self.china_keywords = [
            "china", "chinese", "prc", "beijing", "shanghai", "shenzhen",
            "hong kong", "cayman", "bermuda", "bvi", "british virgin"
        ]

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "source_file": str(self.zip_path),
            "companies_processed": 0,
            "chinese_companies": [],
            "errors": [],
            "filings": []
        }

    def load_checkpoint(self) -> Dict:
        """Load checkpoint for resuming processing"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    return json.load(f)
            except:
                return {"processed_ciks": [], "last_cik": None}
        return {"processed_ciks": [], "last_cik": None}

    def save_checkpoint(self, cik: str):
        """Save checkpoint after processing each company"""
        self.checkpoint["processed_ciks"].append(cik)
        self.checkpoint["last_cik"] = cik
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f)

    def extract_zip_data(self) -> Dict:
        """Extract and parse submissions from ZIP file"""
        logging.info(f"Extracting ZIP file: {self.zip_path}")

        if not self.zip_path.exists():
            raise FileNotFoundError(f"ZIP file not found: {self.zip_path}")

        submissions = {}

        try:
            with zipfile.ZipFile(self.zip_path, 'r') as z:
                # List all files in the ZIP
                file_list = z.namelist()
                logging.info(f"Found {len(file_list)} files in ZIP")

                # Look for submissions JSON file
                for filename in file_list:
                    if 'submissions' in filename.lower() and filename.endswith('.json'):
                        logging.info(f"Processing {filename}")
                        with z.open(filename) as f:
                            data = json.load(f)

                            # Process each submission
                            if isinstance(data, list):
                                for item in data:
                                    cik = item.get('cik', 'unknown')
                                    submissions[cik] = item
                            elif isinstance(data, dict):
                                # Could be a single submission or dict of submissions
                                if 'cik' in data:
                                    submissions[data['cik']] = data
                                else:
                                    submissions = data

                            logging.info(f"Loaded {len(submissions)} submissions")
                            break

                # If no JSON found, try extracting text files
                if not submissions:
                    logging.warning("No submissions JSON found, trying text files")
                    for filename in file_list[:100]:  # Check first 100 files
                        if filename.endswith('.txt'):
                            with z.open(filename) as f:
                                content = f.read().decode('utf-8', errors='ignore')
                                # Parse CIK from filename or content
                                cik = filename.split('/')[-1].split('.')[0]
                                submissions[cik] = {
                                    'cik': cik,
                                    'filename': filename,
                                    'content': content[:1000]  # First 1000 chars
                                }

        except Exception as e:
            logging.error(f"Error extracting ZIP: {e}")
            raise

        return submissions

    def is_chinese_company(self, company_data: Dict) -> bool:
        """Check if company has Chinese connections"""
        text_to_check = json.dumps(company_data).lower()

        for keyword in self.china_keywords:
            if keyword in text_to_check:
                return True

        # Check specific fields
        if isinstance(company_data, dict):
            # Check company name
            name = company_data.get('name', '').lower()
            for keyword in self.china_keywords:
                if keyword in name:
                    return True

            # Check addresses
            for addr_field in ['addresses', 'businessAddress', 'mailingAddress']:
                if addr_field in company_data:
                    addr_text = json.dumps(company_data[addr_field]).lower()
                    for keyword in self.china_keywords:
                        if keyword in addr_text:
                            return True

        return False

    def process_company(self, cik: str, company_data: Dict) -> Optional[Dict]:
        """Process a single company's data"""
        try:
            # Check if Chinese company
            is_chinese = self.is_chinese_company(company_data)

            result = {
                "cik": cik,
                "name": company_data.get('name', 'Unknown'),
                "is_chinese": is_chinese,
                "data": company_data
            }

            if is_chinese:
                self.results["chinese_companies"].append({
                    "cik": cik,
                    "name": company_data.get('name', 'Unknown')
                })
                logging.info(f"Found Chinese company: {company_data.get('name', 'Unknown')}")

            return result

        except Exception as e:
            logging.error(f"Error processing CIK {cik}: {e}")
            self.results["errors"].append({
                "cik": cik,
                "error": str(e)
            })
            return None

    def fetch_additional_data(self, cik: str) -> Optional[Dict]:
        """Fetch additional filing data from SEC EDGAR API"""
        try:
            # Format CIK with leading zeros (10 digits)
            cik_padded = str(cik).zfill(10)

            # SEC EDGAR API endpoint for company filings
            url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"

            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logging.warning("Rate limited, waiting 60 seconds...")
                time.sleep(60)
                return None
            else:
                logging.warning(f"Failed to fetch data for CIK {cik}: {response.status_code}")
                return None

        except Exception as e:
            logging.error(f"Error fetching data for CIK {cik}: {e}")
            return None

    def run(self, limit: int = None):
        """Process SEC EDGAR data with checkpoint support"""
        logging.info("Starting SEC EDGAR processing")

        # Extract submissions from ZIP
        submissions = self.extract_zip_data()

        if not submissions:
            logging.error("No submissions found in ZIP file")
            return

        # Filter out already processed CIKs
        ciks_to_process = [cik for cik in submissions.keys()
                          if cik not in self.checkpoint["processed_ciks"]]

        logging.info(f"Total companies: {len(submissions)}")
        logging.info(f"Already processed: {len(self.checkpoint['processed_ciks'])}")
        logging.info(f"To process: {len(ciks_to_process)}")

        if limit:
            ciks_to_process = ciks_to_process[:limit]

        # Process each company
        for i, cik in enumerate(ciks_to_process, 1):
            logging.info(f"Processing {i}/{len(ciks_to_process)}: CIK {cik}")

            company_data = submissions[cik]
            result = self.process_company(cik, company_data)

            if result:
                # Save individual company file
                output_file = self.output_dir / f"company_{cik}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)

                self.results["companies_processed"] += 1

            # Save checkpoint
            self.save_checkpoint(cik)

            # Brief delay to avoid overwhelming the system
            time.sleep(0.1)

        # Save final results
        self.save_results()

        logging.info(f"Processing complete. Processed {self.results['companies_processed']} companies")
        logging.info(f"Found {len(self.results['chinese_companies'])} Chinese companies")

    def save_results(self):
        """Save processing results"""
        output_file = self.output_dir / "sec_edgar_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)

        # Save Chinese companies list
        if self.results["chinese_companies"]:
            chinese_file = self.output_dir / "chinese_companies.json"
            with open(chinese_file, 'w', encoding='utf-8') as f:
                json.dump(self.results["chinese_companies"], f, indent=2)

        logging.info(f"Results saved to {output_file}")

def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Process SEC EDGAR submissions")
    parser.add_argument("--zip", default="F:/OSINT_Data/SEC_EDGAR/submissions_20250916.zip",
                       help="Path to SEC EDGAR ZIP file")
    parser.add_argument("--output", default="data/processed/sec_edgar_comprehensive",
                       help="Output directory")
    parser.add_argument("--limit", type=int, help="Limit number of companies to process")
    parser.add_argument("--reset", action="store_true", help="Reset checkpoint and start fresh")

    args = parser.parse_args()

    processor = SECEdgarProcessor(args.zip, args.output)

    if args.reset:
        if processor.checkpoint_file.exists():
            processor.checkpoint_file.unlink()
            logging.info("Checkpoint reset")
        processor.checkpoint = {"processed_ciks": [], "last_cik": None}

    processor.run(limit=args.limit)

if __name__ == "__main__":
    main()
