"""
SEC EDGAR API Client for OSINT Foresight
Free access to US securities filings for Italian companies
No API key required - completely free public access
"""

import os
import time
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SECEdgarClient:
    """Client for SEC EDGAR public API - no authentication required"""

    def __init__(self):
        """Initialize SEC EDGAR client"""
        # SEC EDGAR base URLs
        self.data_api_base = "https://data.sec.gov"
        self.archives_base = "https://www.sec.gov/Archives/edgar"

        # Rate limiting: 10 requests per second max
        self.rate_limit_delay = 0.11  # 110ms between requests for safety
        self.last_request_time = 0

        # User agent required by SEC
        self.headers = {
            "User-Agent": "OSINT-Foresight research@example.com",
            "Accept": "application/json"
        }

        # Output directory
        self.output_dir = Path('./data/collected/sec_edgar')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Key Italian entities
        self.italian_entities = {
            "Leonardo DRS": {
                "cik": "0001833756",  # Correct CIK
                "ticker": "DRS",
                "parent": "Leonardo S.p.A",
                "critical": True
            },
            "STMicroelectronics": {
                "cik": "0000932787",
                "ticker": "STM",
                "parent": "STMicroelectronics N.V.",
                "critical": True
            },
            "CNH Industrial": {
                "cik": "0001565153",
                "ticker": "CNHI",
                "parent": "CNH Industrial N.V.",
                "critical": False
            },
            "Stellantis": {
                "cik": "0001605484",
                "ticker": "STLA",
                "italian_connection": "Fiat Chrysler merger",
                "critical": False
            }
        }

    def _rate_limit(self):
        """Implement SEC rate limiting (10 req/sec max)"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def get_company_submissions(self, cik: str) -> Dict:
        """
        Get all submission history for a company

        Args:
            cik: Central Index Key (10 digits, zero-padded)

        Returns:
            Company submission data
        """
        self._rate_limit()

        # Ensure CIK is 10 digits with leading zeros
        cik = cik.zfill(10)

        url = f"{self.data_api_base}/submissions/CIK{cik}.json"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.error(f"Company CIK {cik} not found")
            else:
                logger.error(f"HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

    def get_company_facts(self, cik: str) -> Dict:
        """
        Get XBRL financial facts for a company

        Args:
            cik: Central Index Key

        Returns:
            Financial facts data
        """
        self._rate_limit()

        cik = cik.zfill(10)
        url = f"{self.data_api_base}/api/xbrl/companyfacts/CIK{cik}.json"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get company facts: {e}")
            raise

    def get_recent_filings(self, cik: str, form_types: List[str] = None) -> List[Dict]:
        """
        Get recent filings for a company

        Args:
            cik: Central Index Key
            form_types: Filter by form types (e.g., ['10-K', '10-Q', '8-K'])

        Returns:
            List of recent filings
        """
        if form_types is None:
            form_types = ['10-K', '10-Q', '8-K', '20-F', '6-K', 'DEF 14A']

        submissions = self.get_company_submissions(cik)

        recent_filings = []

        if 'filings' in submissions and 'recent' in submissions['filings']:
            for i, form in enumerate(submissions['filings']['recent']['form']):
                if form in form_types:
                    filing = {
                        'form': form,
                        'filingDate': submissions['filings']['recent']['filingDate'][i],
                        'accessionNumber': submissions['filings']['recent']['accessionNumber'][i],
                        'primaryDocument': submissions['filings']['recent']['primaryDocument'][i],
                        'url': f"{self.archives_base}/data/{cik.lstrip('0')}/{submissions['filings']['recent']['accessionNumber'][i].replace('-', '')}/{submissions['filings']['recent']['primaryDocument'][i]}"
                    }
                    recent_filings.append(filing)

        return recent_filings

    def analyze_leonardo_drs(self) -> Dict:
        """
        Comprehensive analysis of Leonardo DRS filings

        Returns:
            Analysis results
        """
        logger.info("Analyzing Leonardo DRS (US subsidiary of Leonardo S.p.A)...")

        cik = "0001833756"  # Correct Leonardo DRS CIK

        # Get company overview
        submissions = self.get_company_submissions(cik)

        # Extract key information
        analysis = {
            "company_name": submissions.get('name', 'Leonardo DRS, Inc.'),
            "cik": cik,
            "ticker": submissions.get('tickers', ['DRS']),
            "sic_description": submissions.get('sicDescription'),
            "business_address": submissions.get('addresses', {}).get('business', {}),
            "fiscal_year_end": submissions.get('fiscalYearEnd'),
            "total_filings": len(submissions.get('filings', {}).get('recent', {}).get('form', [])),
            "recent_filings": self.get_recent_filings(cik, ['10-K', '10-Q', '8-K', 'DEF 14A'])[:10]
        }

        # Get financial facts
        try:
            facts = self.get_company_facts(cik)

            # Extract revenue and key metrics
            if 'facts' in facts and 'us-gaap' in facts['facts']:
                us_gaap = facts['facts']['us-gaap']

                # Revenue
                if 'Revenues' in us_gaap:
                    analysis['revenue_history'] = us_gaap['Revenues']

                # R&D expenses
                if 'ResearchAndDevelopmentExpense' in us_gaap:
                    analysis['rd_expenses'] = us_gaap['ResearchAndDevelopmentExpense']

                # Government contract info often in custom facts
                if 'dei' in facts['facts']:
                    analysis['dei_facts'] = facts['facts']['dei']

        except Exception as e:
            logger.warning(f"Could not retrieve financial facts: {e}")

        # Save analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"leonardo_drs_analysis_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)

        logger.info(f"Saved Leonardo DRS analysis to {output_file}")

        return analysis

    def search_italian_connections(self) -> Dict:
        """
        Search for all Italian company connections in SEC filings

        Returns:
            Italian connection analysis
        """
        logger.info("Searching for Italian company connections in SEC filings...")

        results = {}

        for company_name, company_info in self.italian_entities.items():
            if 'cik' not in company_info:
                continue

            logger.info(f"Analyzing {company_name}...")

            try:
                # Get submissions
                submissions = self.get_company_submissions(company_info['cik'])

                # Extract key data
                results[company_name] = {
                    'cik': company_info['cik'],
                    'ticker': company_info.get('ticker'),
                    'parent': company_info.get('parent'),
                    'name': submissions.get('name'),
                    'sic_description': submissions.get('sicDescription'),
                    'exchanges': submissions.get('exchanges'),
                    'fiscal_year_end': submissions.get('fiscalYearEnd'),
                    'recent_filings_count': len(submissions.get('filings', {}).get('recent', {}).get('form', [])),
                    'latest_10k': None,
                    'latest_10q': None
                }

                # Find latest 10-K and 10-Q
                recent = submissions.get('filings', {}).get('recent', {})
                for i, form in enumerate(recent.get('form', [])):
                    if form == '10-K' and not results[company_name]['latest_10k']:
                        results[company_name]['latest_10k'] = {
                            'date': recent['filingDate'][i],
                            'accession': recent['accessionNumber'][i]
                        }
                    elif form in ['10-Q', '20-F'] and not results[company_name]['latest_10q']:
                        results[company_name]['latest_10q'] = {
                            'date': recent['filingDate'][i],
                            'accession': recent['accessionNumber'][i]
                        }

                time.sleep(self.rate_limit_delay)

            except Exception as e:
                logger.error(f"Error analyzing {company_name}: {e}")
                results[company_name] = {'error': str(e)}

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"italian_connections_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Saved Italian connections analysis to {output_file}")

        return results

    def extract_china_mentions(self, cik: str, num_filings: int = 5) -> List[Dict]:
        """
        Search recent filings for China/Chinese mentions

        Args:
            cik: Company CIK
            num_filings: Number of recent filings to check

        Returns:
            China mentions analysis
        """
        logger.info(f"Searching for China mentions in CIK {cik} filings...")

        # This would require downloading and parsing filing content
        # For now, return filing URLs where manual review can be done

        recent_filings = self.get_recent_filings(cik, ['10-K', '10-Q', '8-K'])[:num_filings]

        china_search_urls = []
        for filing in recent_filings:
            china_search_urls.append({
                'form': filing['form'],
                'date': filing['filingDate'],
                'url': filing['url'],
                'search_terms': ['China', 'Chinese', 'PRC', 'People\'s Republic']
            })

        return china_search_urls


def test_connection():
    """Test SEC EDGAR API connection"""

    client = SECEdgarClient()

    print("SEC EDGAR API Client Test")
    print("=" * 50)

    try:
        # Test with Leonardo DRS
        print("\nTesting with Leonardo DRS (CIK: 0001833756)...")
        submissions = client.get_company_submissions("0001833756")

        print(f"[SUCCESS] Retrieved data for: {submissions.get('name')}")
        print(f"  SIC: {submissions.get('sicDescription')}")
        print(f"  Tickers: {submissions.get('tickers')}")
        print(f"  Total filings: {len(submissions.get('filings', {}).get('recent', {}).get('form', []))}")

        return True

    except Exception as e:
        print(f"[ERROR] Connection test failed: {e}")
        return False


if __name__ == "__main__":
    if test_connection():
        print("\n[SUCCESS] SEC EDGAR API is ready to use!")
        print("\nNo API key required - this is free public data")
        print("\nExample usage:")
        print("  client = SECEdgarClient()")
        print("  leonardo = client.analyze_leonardo_drs()")
        print("  italian_companies = client.search_italian_connections()")
    else:
        print("\n[ERROR] Could not connect to SEC EDGAR")
