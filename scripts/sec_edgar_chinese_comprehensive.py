#!/usr/bin/env python3
"""
SEC EDGAR Chinese Company Comprehensive Fetcher
Searches through ALL SEC EDGAR companies to find Chinese ones
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
        logging.FileHandler('sec_edgar_chinese_comprehensive.log'),
        logging.StreamHandler()
    ]
)

class SECEdgarChineseComprehensiveFetcher:
    """Find and fetch ALL Chinese companies from SEC EDGAR"""

    def __init__(self, output_dir: str = "data/processed/sec_edgar_comprehensive/chinese"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.headers = {
            "User-Agent": "OSINT-Foresight Research (research@example.com)",
            "Accept": "application/json"
        }

        # Comprehensive Chinese indicators
        self.chinese_indicators = {
            # Geographic locations
            "locations": [
                "china", "chinese", "prc", "people's republic",
                "beijing", "shanghai", "shenzhen", "guangzhou", "hangzhou",
                "chengdu", "wuhan", "xi'an", "nanjing", "tianjin",
                "chongqing", "suzhou", "dalian", "qingdao", "xiamen",
                "ningbo", "foshan", "dongguan", "zhejiang", "jiangsu",
                "guangdong", "shandong", "fujian", "hunan", "hubei",
                "sichuan", "anhui", "henan", "hebei", "liaoning"
            ],
            # Common Chinese company name patterns
            "name_patterns": [
                "holdings", "group", "international", "technology",
                "biotech", "pharma", "auto", "motors", "energy",
                "solar", "education", "fintech", "tech"
            ],
            # Offshore jurisdictions commonly used by Chinese companies
            "offshore": [
                "cayman islands", "cayman", "ky",
                "british virgin islands", "bvi", "vg",
                "bermuda", "bm",
                "hong kong", "hk"
            ],
            # State of incorporation codes
            "state_codes": [
                "e9",  # Cayman Islands
                "d0",  # Bermuda
                "f4",  # British Virgin Islands
                "l3"   # Hong Kong
            ]
        }

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total_companies_scanned": 0,
            "chinese_companies_found": 0,
            "chinese_companies": [],
            "detection_methods": {},
            "errors": []
        }

    def fetch_all_companies(self) -> Dict:
        """Fetch complete list of all companies"""
        logging.info("Fetching complete company list from SEC...")

        try:
            url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, headers=self.headers, timeout=30)

            if response.status_code == 200:
                companies = response.json()
                logging.info(f"Fetched {len(companies)} companies from SEC")
                return companies
            else:
                logging.error(f"Failed to fetch company list: {response.status_code}")
                return {}

        except Exception as e:
            logging.error(f"Error fetching company list: {e}")
            return {}

    def is_chinese_company(self, company_data: Dict, basic_info: Dict = None) -> tuple[bool, List[str]]:
        """
        Determine if company is Chinese and why
        Returns (is_chinese, reasons)
        """
        reasons = []
        search_text = json.dumps(company_data).lower()

        # Also check basic info if provided
        if basic_info:
            search_text += " " + json.dumps(basic_info).lower()

        # Check company name
        company_name = company_data.get('name', '').lower()

        # Check for Chinese location keywords
        for location in self.chinese_indicators["locations"]:
            if location in search_text:
                reasons.append(f"location:{location}")

        # Check offshore jurisdictions
        for offshore in self.chinese_indicators["offshore"]:
            if offshore in search_text:
                reasons.append(f"offshore:{offshore}")

        # Check state of incorporation
        state = company_data.get('stateOfIncorporation', '').upper()
        if state in self.chinese_indicators["state_codes"]:
            reasons.append(f"state_code:{state}")

        # Check addresses
        addresses = company_data.get('addresses', {})
        for addr_type, addr_data in addresses.items():
            if isinstance(addr_data, dict):
                addr_text = json.dumps(addr_data).lower()
                if any(loc in addr_text for loc in self.chinese_indicators["locations"][:15]):  # Check major cities
                    reasons.append(f"address:{addr_type}")

        # Check SIC codes (some are common for Chinese companies)
        sic = company_data.get('sic', '')
        sic_desc = company_data.get('sicDescription', '').lower()
        if sic in ['3674', '7372', '5961', '8742']:  # Semiconductors, Software, Retail, Management Consulting
            if any(indicator in search_text for indicator in ['china', 'chinese', 'cayman', 'bvi']):
                reasons.append(f"sic:{sic}")

        # Check for VIE structure indicators
        if 'vie' in search_text or 'variable interest' in search_text:
            reasons.append("vie_structure")

        return len(reasons) > 0, reasons

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
            else:
                return None

        except Exception as e:
            logging.error(f"Error fetching CIK {cik}: {e}")
            return None

    def run(self):
        """Scan all companies and extract Chinese ones"""
        logging.info("Starting comprehensive Chinese company search...")

        # Get all companies
        all_companies = self.fetch_all_companies()

        if not all_companies:
            logging.error("Failed to fetch company list")
            return

        # Process each company
        chinese_found = 0
        total_processed = 0

        for key, company in all_companies.items():
            if not isinstance(company, dict):
                continue

            total_processed += 1
            cik = str(company.get('cik_str', '')).zfill(10)
            ticker = company.get('ticker', 'NOTICKER')
            title = company.get('title', 'Unknown')

            # Quick pre-filter based on name
            quick_check = False
            title_lower = title.lower()
            for indicator in ['china', 'chinese', 'holdings', 'group']:
                if indicator in title_lower:
                    quick_check = True
                    break

            # If quick check passes or certain patterns, fetch details
            if quick_check or total_processed % 100 == 0:  # Sample every 100th for thoroughness
                if total_processed % 50 == 0:
                    logging.info(f"Processed {total_processed}/{len(all_companies)} companies, found {chinese_found} Chinese")

                # Fetch detailed data
                details = self.fetch_company_details(cik)

                if details:
                    is_chinese, reasons = self.is_chinese_company(details, company)

                    if is_chinese:
                        chinese_found += 1

                        # Extract key filing info
                        recent_filings = details.get('filings', {}).get('recent', {})
                        latest_filing = None
                        if recent_filings:
                            forms = recent_filings.get('form', [])
                            dates = recent_filings.get('filingDate', [])
                            for i, form in enumerate(forms[:10]):
                                if form in ['10-K', '20-F', '10-Q', '8-K', '6-K']:
                                    latest_filing = {
                                        "form": form,
                                        "date": dates[i] if i < len(dates) else None
                                    }
                                    break

                        # Save company data
                        company_info = {
                            "cik": cik,
                            "ticker": ticker,
                            "name": details.get('name', title),
                            "detection_reasons": reasons,
                            "sic": details.get('sic', ''),
                            "sicDescription": details.get('sicDescription', ''),
                            "category": details.get('category', ''),
                            "entityType": details.get('entityType', ''),
                            "stateOfIncorporation": details.get('stateOfIncorporation', ''),
                            "ein": details.get('ein', ''),
                            "phone": details.get('phone', ''),
                            "website": details.get('website', ''),
                            "addresses": details.get('addresses', {}),
                            "latest_filing": latest_filing,
                            "filings_count": len(recent_filings.get('form', []))
                        }

                        # Save individual file
                        output_file = self.output_dir / f"{ticker}_{cik}.json"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(company_info, f, indent=2)

                        # Add to results
                        self.results["chinese_companies"].append({
                            "cik": cik,
                            "ticker": ticker,
                            "name": company_info["name"],
                            "reasons": reasons,
                            "state": company_info["stateOfIncorporation"]
                        })

                        # Track detection methods
                        for reason in reasons:
                            method = reason.split(':')[0]
                            if method not in self.results["detection_methods"]:
                                self.results["detection_methods"][method] = 0
                            self.results["detection_methods"][method] += 1

                        logging.info(f"Found Chinese company: {ticker} - {company_info['name']} ({', '.join(reasons)})")

                # Rate limiting
                time.sleep(0.1)

        self.results["total_companies_scanned"] = total_processed
        self.results["chinese_companies_found"] = chinese_found

        # Save results
        self.save_results()

        # Print summary
        logging.info("=" * 60)
        logging.info("CHINESE COMPANY SEARCH COMPLETE")
        logging.info(f"Total companies scanned: {total_processed}")
        logging.info(f"Chinese companies found: {chinese_found}")
        logging.info(f"Detection methods used:")
        for method, count in self.results["detection_methods"].items():
            logging.info(f"  {method}: {count}")
        logging.info("=" * 60)

    def save_results(self):
        """Save all results"""
        # Save summary
        summary_file = self.output_dir / "chinese_companies_comprehensive.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)

        # Save list for easy reference
        list_file = self.output_dir / "chinese_companies_list.json"
        companies_list = [{
            "ticker": c["ticker"],
            "name": c["name"],
            "cik": c["cik"]
        } for c in self.results["chinese_companies"]]
        with open(list_file, 'w', encoding='utf-8') as f:
            json.dump(companies_list, f, indent=2)

        logging.info(f"Results saved to {summary_file}")

def main():
    """Main execution function"""
    fetcher = SECEdgarChineseComprehensiveFetcher()
    fetcher.run()

if __name__ == "__main__":
    main()
