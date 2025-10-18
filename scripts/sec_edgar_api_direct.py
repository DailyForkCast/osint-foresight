#!/usr/bin/env python3
"""
SEC EDGAR Direct API Fetcher
Fetches Chinese company data directly from SEC EDGAR API
"""

import os
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
import time
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sec_edgar_api_direct.log'),
        logging.StreamHandler()
    ]
)

class SECEdgarAPIFetcher:
    """Fetch SEC EDGAR data directly from API with rate limiting"""

    def __init__(self, output_dir: str = "data/processed/sec_edgar_comprehensive"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.headers = {
            "User-Agent": "OSINT-Foresight Research (research@example.com)",
            "Accept": "application/json"
        }

        # Known Chinese companies on US exchanges
        self.chinese_tickers = {
            # Major Tech
            "BABA": "Alibaba Group", "BIDU": "Baidu", "JD": "JD.com", "PDD": "PDD Holdings",
            "TME": "Tencent Music", "BILI": "Bilibili", "IQ": "iQIYI", "VIPS": "Vipshop",
            "NTES": "NetEase", "WB": "Weibo", "ATHM": "Autohome", "MOMO": "Hello Group",

            # EVs
            "NIO": "NIO Inc", "XPEV": "XPeng", "LI": "Li Auto",

            # Finance
            "FUTU": "Futu Holdings", "TIGR": "UP Fintech", "LU": "Lufax", "QFIN": "360 DigiTech",

            # Education
            "EDU": "New Oriental", "TAL": "TAL Education", "GOTU": "Gaotu Techedu",

            # Healthcare
            "ZLAB": "Zai Lab", "BGNE": "BeiGene", "SVA": "Sinovac",

            # Others
            "DIDI": "DiDi", "BEKE": "KE Holdings", "TUYA": "Tuya", "YMM": "Full Truck Alliance",
            "RLX": "RLX Technology", "MNSO": "MINISO", "DDL": "Dingdong", "API": "Agora"
        }

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "companies_processed": 0,
            "chinese_companies": [],
            "filings": [],
            "errors": []
        }

    def get_company_cik(self, ticker: str) -> Optional[str]:
        """Get CIK for a ticker symbol"""
        try:
            # SEC ticker lookup endpoint
            url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                tickers = response.json()

                # Search for ticker in the data
                for cik_str, company in tickers.items():
                    if isinstance(company, dict) and company.get('ticker') == ticker.upper():
                        return str(company.get('cik_str', '')).zfill(10)

                # Alternative structure (sometimes SEC returns list)
                if isinstance(tickers, dict):
                    for key, company in tickers.items():
                        if isinstance(company, dict) and company.get('ticker') == ticker.upper():
                            return str(company.get('cik_str', '')).zfill(10)

            logging.warning(f"Could not find CIK for ticker {ticker}")
            return None

        except Exception as e:
            logging.error(f"Error getting CIK for {ticker}: {e}")
            return None

    def fetch_company_data(self, cik: str, ticker: str) -> Optional[Dict]:
        """Fetch company data from SEC EDGAR API"""
        try:
            # Format CIK with leading zeros
            cik_padded = str(cik).zfill(10)

            # SEC EDGAR API endpoint
            url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"

            logging.info(f"Fetching data for {ticker} (CIK: {cik_padded})")

            response = requests.get(url, headers=self.headers, timeout=15)

            if response.status_code == 200:
                data = response.json()

                # Extract key information
                company_info = {
                    "cik": cik_padded,
                    "ticker": ticker,
                    "name": data.get('name', ''),
                    "sic": data.get('sic', ''),
                    "sicDescription": data.get('sicDescription', ''),
                    "category": data.get('category', ''),
                    "entityType": data.get('entityType', ''),
                    "ein": data.get('ein', ''),
                    "stateOfIncorporation": data.get('stateOfIncorporation', ''),
                    "addresses": data.get('addresses', {}),
                    "phone": data.get('phone', ''),
                    "flags": data.get('flags', ''),
                    "website": data.get('website', ''),
                    "investorWebsite": data.get('investorWebsite', ''),
                    "filings": {
                        "recent": data.get('filings', {}).get('recent', {})
                    }
                }

                # Check for recent 10-K or 20-F filings
                recent_filings = data.get('filings', {}).get('recent', {})
                if recent_filings:
                    forms = recent_filings.get('form', [])
                    dates = recent_filings.get('filingDate', [])

                    # Get most recent annual report
                    for i, form in enumerate(forms[:10]):  # Check last 10 filings
                        if form in ['10-K', '20-F', '10-Q', '8-K']:
                            company_info['latest_filing'] = {
                                "form": form,
                                "date": dates[i] if i < len(dates) else None
                            }
                            break

                return company_info

            elif response.status_code == 429:
                logging.warning("Rate limited, waiting 60 seconds...")
                time.sleep(60)
                return self.fetch_company_data(cik, ticker)  # Retry

            elif response.status_code == 404:
                logging.warning(f"No data found for {ticker} (CIK: {cik_padded})")
                return None

            else:
                logging.warning(f"Failed to fetch {ticker}: {response.status_code}")
                return None

        except Exception as e:
            logging.error(f"Error fetching data for {ticker}: {e}")
            self.results["errors"].append({
                "ticker": ticker,
                "cik": cik,
                "error": str(e)
            })
            return None

    def run(self):
        """Process all Chinese companies"""
        logging.info(f"Starting SEC EDGAR API fetch for {len(self.chinese_tickers)} companies")

        # First get CIKs for all tickers
        ticker_cik_map = {}

        logging.info("Fetching company CIK mappings...")
        url = "https://www.sec.gov/files/company_tickers.json"

        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                all_tickers = response.json()

                # Match our tickers with CIKs
                for item in all_tickers.values():
                    if isinstance(item, dict):
                        ticker = item.get('ticker', '')
                        if ticker in self.chinese_tickers:
                            ticker_cik_map[ticker] = str(item.get('cik_str', '')).zfill(10)
                            logging.info(f"Found CIK for {ticker}: {ticker_cik_map[ticker]}")

        except Exception as e:
            logging.error(f"Error fetching ticker list: {e}")

        # Process each company
        for ticker, company_name in self.chinese_tickers.items():
            cik = ticker_cik_map.get(ticker)

            if not cik:
                logging.warning(f"No CIK found for {ticker} - {company_name}")
                continue

            # Fetch company data
            company_data = self.fetch_company_data(cik, ticker)

            if company_data:
                # Save individual company file
                output_file = self.output_dir / f"{ticker}_{cik}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(company_data, f, indent=2)

                self.results["companies_processed"] += 1
                self.results["chinese_companies"].append({
                    "ticker": ticker,
                    "cik": cik,
                    "name": company_data.get('name', company_name),
                    "state": company_data.get('stateOfIncorporation', ''),
                    "latest_filing": company_data.get('latest_filing', {})
                })

                logging.info(f"Saved data for {ticker} to {output_file}")

            # Rate limiting - wait between requests
            time.sleep(0.5)

        # Save summary results
        self.save_results()

        logging.info(f"Processing complete. Processed {self.results['companies_processed']} companies")

    def save_results(self):
        """Save processing results"""
        # Save summary
        summary_file = self.output_dir / "sec_edgar_chinese_companies.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)

        # Save company list
        company_list_file = self.output_dir / "chinese_companies_list.json"
        with open(company_list_file, 'w', encoding='utf-8') as f:
            json.dump(self.results["chinese_companies"], f, indent=2)

        logging.info(f"Results saved to {summary_file}")

def main():
    """Main execution function"""
    fetcher = SECEdgarAPIFetcher()
    fetcher.run()

if __name__ == "__main__":
    main()
