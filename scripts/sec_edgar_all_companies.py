#!/usr/bin/env python3
"""
SEC EDGAR Complete Company Fetcher
Fetches ALL companies from SEC EDGAR, not just Chinese ones
"""

import os
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
import time
from typing import Dict, List, Optional
import pickle

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sec_edgar_all_companies.log'),
        logging.StreamHandler()
    ]
)

class SECEdgarCompleteFetcher:
    """Fetch ALL companies from SEC EDGAR with checkpoint support"""

    def __init__(self, output_dir: str = "data/processed/sec_edgar_comprehensive"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Checkpoint file
        self.checkpoint_file = self.output_dir / "processing_checkpoint.json"
        self.checkpoint = self.load_checkpoint()

        self.headers = {
            "User-Agent": "OSINT-Foresight Research (research@example.com)",
            "Accept": "application/json"
        }

        # China/foreign indicators for flagging
        self.foreign_indicators = {
            "china": ["china", "chinese", "prc", "beijing", "shanghai", "shenzhen", "guangzhou", "hangzhou"],
            "cayman": ["cayman", "ky"],
            "bermuda": ["bermuda", "bm"],
            "bvi": ["british virgin", "vg"],
            "hong_kong": ["hong kong", "hk"],
            "singapore": ["singapore", "sg"],
            "israel": ["israel", "il", "tel aviv"],
            "canada": ["canada", "ca", "ontario", "british columbia", "quebec"],
            "uk": ["united kingdom", "uk", "england", "london"],
            "japan": ["japan", "jp", "tokyo"],
            "germany": ["germany", "de", "frankfurt", "munich"],
            "france": ["france", "fr", "paris"],
            "netherlands": ["netherlands", "nl", "amsterdam"],
            "switzerland": ["switzerland", "ch", "zurich"],
            "ireland": ["ireland", "ie", "dublin"]
        }

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total_companies": 0,
            "companies_processed": 0,
            "foreign_companies": {},
            "errors": [],
            "statistics": {}
        }

    def load_checkpoint(self) -> Dict:
        """Load checkpoint for resuming processing"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    return json.load(f)
            except:
                return {"processed_ciks": [], "last_cik": None, "total_companies": 0}
        return {"processed_ciks": [], "last_cik": None, "total_companies": 0}

    def save_checkpoint(self):
        """Save checkpoint after processing batch"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)

    def fetch_all_company_tickers(self) -> Dict:
        """Fetch complete list of all companies with tickers"""
        logging.info("Fetching complete company list from SEC...")

        # Check if we have a cached version
        cache_file = self.output_dir / "all_company_tickers.json"

        # Use cache if it's less than 24 hours old
        if cache_file.exists():
            age_hours = (time.time() - cache_file.stat().st_mtime) / 3600
            if age_hours < 24:
                logging.info(f"Using cached company list ({age_hours:.1f} hours old)")
                with open(cache_file, 'r') as f:
                    return json.load(f)

        try:
            url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, headers=self.headers, timeout=30)

            if response.status_code == 200:
                companies = response.json()

                # Save cache
                with open(cache_file, 'w') as f:
                    json.dump(companies, f, indent=2)

                logging.info(f"Fetched {len(companies)} companies from SEC")
                return companies
            else:
                logging.error(f"Failed to fetch company list: {response.status_code}")
                return {}

        except Exception as e:
            logging.error(f"Error fetching company list: {e}")
            return {}

    def classify_company_origin(self, company_data: Dict) -> List[str]:
        """Classify company by country/region of origin"""
        origins = []

        # Convert to string for searching
        search_text = json.dumps(company_data).lower()

        for origin, keywords in self.foreign_indicators.items():
            for keyword in keywords:
                if keyword in search_text:
                    origins.append(origin)
                    break

        # Check state of incorporation
        state = company_data.get('stateOfIncorporation', '').lower()
        if state in ['e9', 'f4', 'd0']:  # Foreign incorporation codes
            if not origins:
                origins.append('foreign_other')

        return origins

    def fetch_company_details(self, cik: str) -> Optional[Dict]:
        """Fetch detailed company information"""
        try:
            cik_padded = str(cik).zfill(10)
            url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"

            response = requests.get(url, headers=self.headers, timeout=15)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logging.warning("Rate limited, waiting 60 seconds...")
                time.sleep(60)
                return self.fetch_company_details(cik)  # Retry
            elif response.status_code == 404:
                return None
            else:
                logging.warning(f"Failed to fetch CIK {cik}: {response.status_code}")
                return None

        except Exception as e:
            logging.error(f"Error fetching CIK {cik}: {e}")
            return None

    def process_batch(self, companies: List[Dict], batch_size: int = 100):
        """Process companies in batches"""
        total = len(companies)

        for i in range(0, total, batch_size):
            batch = companies[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size

            logging.info(f"Processing batch {batch_num}/{total_batches}")

            for company in batch:
                cik = str(company.get('cik_str', '')).zfill(10)

                # Skip if already processed
                if cik in self.checkpoint["processed_ciks"]:
                    continue

                ticker = company.get('ticker', 'NOTICKER')
                title = company.get('title', 'Unknown')

                # Fetch detailed data
                details = self.fetch_company_details(cik)

                if details:
                    # Classify origin
                    origins = self.classify_company_origin(details)

                    # Save company data
                    company_info = {
                        "cik": cik,
                        "ticker": ticker,
                        "name": details.get('name', title),
                        "sic": details.get('sic', ''),
                        "sicDescription": details.get('sicDescription', ''),
                        "category": details.get('category', ''),
                        "entityType": details.get('entityType', ''),
                        "stateOfIncorporation": details.get('stateOfIncorporation', ''),
                        "origins": origins,
                        "ein": details.get('ein', ''),
                        "phone": details.get('phone', ''),
                        "website": details.get('website', ''),
                        "addresses": details.get('addresses', {}),
                        "filings_count": len(details.get('filings', {}).get('recent', {}).get('form', []))
                    }

                    # Save individual file
                    output_file = self.output_dir / f"{ticker}_{cik}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(company_info, f, indent=2)

                    # Track foreign companies
                    for origin in origins:
                        if origin not in self.results["foreign_companies"]:
                            self.results["foreign_companies"][origin] = []
                        self.results["foreign_companies"][origin].append({
                            "cik": cik,
                            "ticker": ticker,
                            "name": company_info["name"]
                        })

                    self.results["companies_processed"] += 1

                    # Update checkpoint
                    self.checkpoint["processed_ciks"].append(cik)
                    self.checkpoint["last_cik"] = cik

                    # Log progress
                    if self.results["companies_processed"] % 10 == 0:
                        logging.info(f"Processed {self.results['companies_processed']} companies")

                # Rate limiting
                time.sleep(0.1)  # 100ms between requests

            # Save checkpoint after each batch
            self.save_checkpoint()
            self.save_results()

            logging.info(f"Batch {batch_num} complete. Total processed: {self.results['companies_processed']}")

    def run(self, limit: Optional[int] = None):
        """Run the complete extraction"""
        logging.info("Starting complete SEC EDGAR extraction")

        # Get all companies
        all_companies = self.fetch_all_company_tickers()

        if not all_companies:
            logging.error("Failed to fetch company list")
            return

        # Convert to list for processing
        companies_list = []
        for key, company in all_companies.items():
            if isinstance(company, dict):
                companies_list.append(company)

        logging.info(f"Total companies to process: {len(companies_list)}")
        self.results["total_companies"] = len(companies_list)
        self.checkpoint["total_companies"] = len(companies_list)

        # Filter out already processed
        unprocessed = [c for c in companies_list
                      if str(c.get('cik_str', '')).zfill(10) not in self.checkpoint["processed_ciks"]]

        logging.info(f"Already processed: {len(companies_list) - len(unprocessed)}")
        logging.info(f"To process: {len(unprocessed)}")

        if limit:
            unprocessed = unprocessed[:limit]
            logging.info(f"Limited to {limit} companies")

        # Process in batches
        self.process_batch(unprocessed)

        # Final save
        self.save_results()

        # Print statistics
        logging.info("=" * 60)
        logging.info("EXTRACTION COMPLETE")
        logging.info(f"Total companies: {self.results['total_companies']}")
        logging.info(f"Companies processed: {self.results['companies_processed']}")
        logging.info(f"Foreign companies by region:")
        for origin, companies in self.results["foreign_companies"].items():
            logging.info(f"  {origin}: {len(companies)}")
        logging.info("=" * 60)

    def save_results(self):
        """Save processing results"""
        # Save summary
        summary_file = self.output_dir / "sec_edgar_all_companies_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)

        # Save foreign companies lists
        for origin, companies in self.results["foreign_companies"].items():
            origin_file = self.output_dir / f"companies_{origin}.json"
            with open(origin_file, 'w', encoding='utf-8') as f:
                json.dump(companies, f, indent=2)

def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Fetch ALL SEC EDGAR companies")
    parser.add_argument("--limit", type=int, help="Limit number of companies (for testing)")
    parser.add_argument("--reset", action="store_true", help="Reset checkpoint and start fresh")

    args = parser.parse_args()

    fetcher = SECEdgarCompleteFetcher()

    if args.reset:
        if fetcher.checkpoint_file.exists():
            fetcher.checkpoint_file.unlink()
            logging.info("Checkpoint reset")
        fetcher.checkpoint = {"processed_ciks": [], "last_cik": None, "total_companies": 0}

    fetcher.run(limit=args.limit)

if __name__ == "__main__":
    main()
