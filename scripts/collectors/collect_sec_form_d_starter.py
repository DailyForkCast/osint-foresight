#!/usr/bin/env python3
"""
collect_sec_form_d_starter.py - SEC Form D Venture Capital Deal Collector

Purpose:
    Collect SEC Form D filings (private placements) to track venture capital
    and private equity funding rounds. This is the core of building a
    PitchBook-like database on $0 budget.

Legal Status: ✅ 100% LEGAL
    - SEC data is public domain
    - No authentication required
    - Free to use and redistribute
    - Must respect rate limits (10 req/sec max)

Data You'll Get:
    - Company name and address
    - Total offering amount
    - Type of security (equity/debt)
    - Date of first sale
    - Industry classification
    - Revenue range
    - Use of proceeds
    - Executive officers

Usage:
    # Collect last 30 days of filings
    python collect_sec_form_d_starter.py --days 30

    # Collect specific date range
    python collect_sec_form_d_starter.py --start 2024-01-01 --end 2024-12-31

    # Dry run (don't save to database)
    python collect_sec_form_d_starter.py --days 7 --dry-run

Output:
    - Saves to: data/processed/sec_form_d/
    - Database: osint_master.db table: sec_form_d_filings
    - JSON files: One per filing for inspection

Dependencies:
    pip install requests beautifulsoup4 lxml

Last Updated: 2025-10-22
Author: OSINT Foresight
"""

import requests
import json
import sqlite3
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
import re

class SECFormDCollector:
    """
    Collect SEC Form D filings for venture capital intelligence

    Form D = Notice of Exempt Offering of Securities
    Filed by companies raising private capital (VC/PE/angel)
    """

    def __init__(self, db_path: str = 'F:/OSINT_WAREHOUSE/osint_master.db'):
        self.db_path = db_path
        self.base_url = 'https://www.sec.gov'

        # SEC requires User-Agent with contact info
        self.headers = {
            'User-Agent': 'OSINT-Foresight Research project@example.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }

        # SEC rate limit: 10 requests/second MAX
        # Be conservative: 0.2 sec between requests (5 req/sec)
        self.rate_limit_delay = 0.2

        # Output directory
        self.output_dir = Path('data/processed/sec_form_d')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            'total_found': 0,
            'downloaded': 0,
            'parsed': 0,
            'saved': 0,
            'errors': 0
        }

    def search_form_d_filings(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Search SEC EDGAR for Form D filings in date range

        Args:
            start_date: Beginning of search period
            end_date: End of search period

        Returns:
            List of filing metadata dictionaries
        """
        print(f"\n🔍 Searching Form D filings: {start_date.date()} to {end_date.date()}")

        filings = []

        # SEC EDGAR search endpoint
        search_url = f"{self.base_url}/cgi-bin/browse-edgar"

        # Note: This is a simplified version
        # Production version should paginate through all results
        params = {
            'action': 'getcompany',
            'type': 'D',  # Form D
            'dateb': end_date.strftime('%Y%m%d'),
            'owner': 'exclude',
            'output': 'atom',
            'count': 100  # Max results per page
        }

        time.sleep(self.rate_limit_delay)

        try:
            response = requests.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()

            # Parse ATOM feed (simplified)
            # Production version should use proper XML parser
            content = response.text

            # Extract accession numbers and company info
            # This is a placeholder - implement full ATOM parsing
            matches = re.findall(r'<accession-nunber>([\d-]+)</accession-nunber>', content)

            print(f"✅ Found {len(matches)} recent filings")
            self.stats['total_found'] = len(matches)

            # For demo, return mock data structure
            # Replace with actual ATOM parsing
            for accession in matches[:10]:  # Limit to 10 for demo
                filings.append({
                    'accession_number': accession,
                    'filing_date': None,  # Parse from ATOM
                    'company_name': None,  # Parse from ATOM
                    'cik': None  # Parse from ATOM
                })

        except Exception as e:
            print(f"❌ Search error: {e}")
            self.stats['errors'] += 1

        return filings

    def download_form_d(self, accession_number: str, cik: str) -> Optional[Dict]:
        """
        Download and parse a specific Form D filing

        Args:
            accession_number: SEC accession number (e.g., 0001234567-24-000001)
            cik: Central Index Key (company identifier)

        Returns:
            Parsed Form D data dictionary
        """
        print(f"  📥 Downloading {accession_number}...")

        time.sleep(self.rate_limit_delay)

        # Construct Form D XML URL
        # Form D is filed as primary_doc.xml
        accession_clean = accession_number.replace('-', '')

        # Try common Form D locations
        possible_urls = [
            f"{self.base_url}/Archives/edgar/data/{cik}/{accession_clean}/primary_doc.xml",
            f"{self.base_url}/Archives/edgar/data/{cik}/{accession_clean}/form_d.xml",
        ]

        for url in possible_urls:
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    self.stats['downloaded'] += 1
                    return self.parse_form_d_xml(response.content, accession_number)

            except Exception as e:
                continue

        print(f"    ❌ Could not download")
        self.stats['errors'] += 1
        return None

    def parse_form_d_xml(self, xml_content: bytes, accession_number: str) -> Dict:
        """
        Parse Form D XML into structured data

        Form D XML Schema:
        - Issuer information (company raising capital)
        - Offering data (amount, type, date)
        - Related persons (executives, directors)
        - Type of securities
        - Revenue/employee count ranges
        """
        print(f"    📊 Parsing XML...")

        try:
            root = ET.fromstring(xml_content)

            data = {
                'accession_number': accession_number,
                'filing_date': None,
                'issuer_name': None,
                'issuer_address': {},
                'issuer_cik': None,
                'industry_group': None,
                'total_offering_amount': None,
                'total_amount_sold': None,
                'total_remaining': None,
                'revenue_range': None,
                'aggregate_net_asset_value': None,
                'is_equity_offering': False,
                'is_debt_offering': False,
                'is_pooled_investment_fund': False,
                'date_of_first_sale': None,
                'use_of_proceeds': [],
                'executives': [],
                'raw_xml': xml_content.decode('utf-8', errors='ignore')
            }

            # Parse issuer information
            issuer = root.find('.//issuer')
            if issuer is not None:
                data['issuer_name'] = self._get_text(issuer, 'issuerName')
                data['issuer_cik'] = self._get_text(issuer, 'issuerCik')

                # Parse address
                address = issuer.find('.//issuerAddress')
                if address is not None:
                    data['issuer_address'] = {
                        'street1': self._get_text(address, 'street1'),
                        'street2': self._get_text(address, 'street2'),
                        'city': self._get_text(address, 'city'),
                        'state': self._get_text(address, 'stateOrCountry'),
                        'zip': self._get_text(address, 'zipCode')
                    }

                # Industry classification
                data['industry_group'] = self._get_text(issuer, 'industryGroupType')

            # Parse offering data
            offering = root.find('.//offeringData')
            if offering is not None:
                data['total_offering_amount'] = self._get_number(offering, 'totalOfferingAmount')
                data['total_amount_sold'] = self._get_number(offering, 'totalAmountSold')
                data['total_remaining'] = self._get_number(offering, 'totalRemaining')

            # Parse type of security
            security_type = root.find('.//typeOfSecurity')
            if security_type is not None:
                data['is_equity_offering'] = self._get_text(security_type, 'isEquityType') == 'true'
                data['is_debt_offering'] = self._get_text(security_type, 'isDebtType') == 'true'

            # Parse issuer size
            issuer_size = root.find('.//issuerSize')
            if issuer_size is not None:
                data['revenue_range'] = self._get_text(issuer_size, 'revenueRange')
                data['aggregate_net_asset_value'] = self._get_text(issuer_size, 'aggregateNetAssetValueRange')

            # Parse related persons (executives)
            for person in root.findall('.//relatedPersonInfo'):
                exec_data = {
                    'name': self._get_text(person, 'relatedPersonName'),
                    'relationship': self._get_text(person, 'relationshipList')
                }
                data['executives'].append(exec_data)

            # Parse sales compensation (investors/intermediaries)
            # Can sometimes reveal VC firms involved

            self.stats['parsed'] += 1
            print(f"    ✅ Parsed: {data['issuer_name']} - ${data['total_offering_amount']:,}" if data['total_offering_amount'] else "")

            return data

        except Exception as e:
            print(f"    ❌ Parse error: {e}")
            self.stats['errors'] += 1
            return None

    def _get_text(self, element, tag: str) -> Optional[str]:
        """Helper: safely extract text from XML element"""
        child = element.find(f'.//{tag}')
        return child.text if child is not None else None

    def _get_number(self, element, tag: str) -> Optional[float]:
        """Helper: safely extract number from XML element"""
        text = self._get_text(element, tag)
        if text:
            try:
                return float(text)
            except ValueError:
                return None
        return None

    def save_to_database(self, filing_data: Dict):
        """
        Save Form D data to SQLite database

        Table: sec_form_d_filings
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sec_form_d_filings (
                accession_number TEXT PRIMARY KEY,
                filing_date DATE,
                issuer_name TEXT,
                issuer_cik TEXT,
                industry_group TEXT,
                total_offering_amount REAL,
                total_amount_sold REAL,
                revenue_range TEXT,
                is_equity BOOLEAN,
                is_debt BOOLEAN,
                city TEXT,
                state TEXT,
                executives TEXT,
                raw_data TEXT,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert filing
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO sec_form_d_filings (
                    accession_number, filing_date, issuer_name, issuer_cik,
                    industry_group, total_offering_amount, total_amount_sold,
                    revenue_range, is_equity, is_debt,
                    city, state, executives, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                filing_data['accession_number'],
                filing_data['filing_date'],
                filing_data['issuer_name'],
                filing_data['issuer_cik'],
                filing_data['industry_group'],
                filing_data['total_offering_amount'],
                filing_data['total_amount_sold'],
                filing_data['revenue_range'],
                filing_data['is_equity_offering'],
                filing_data['is_debt_offering'],
                filing_data['issuer_address'].get('city'),
                filing_data['issuer_address'].get('state'),
                json.dumps(filing_data['executives']),
                json.dumps(filing_data)
            ))

            conn.commit()
            self.stats['saved'] += 1

        except Exception as e:
            print(f"    ❌ Database error: {e}")
            self.stats['errors'] += 1
        finally:
            conn.close()

    def save_to_json(self, filing_data: Dict):
        """Save Form D to JSON file for inspection"""
        filename = self.output_dir / f"{filing_data['accession_number'].replace('-', '_')}.json"

        with open(filename, 'w') as f:
            json.dump(filing_data, f, indent=2, default=str)

    def collect(self, start_date: datetime, end_date: datetime, dry_run: bool = False):
        """
        Main collection workflow

        Args:
            start_date: Start of collection period
            end_date: End of collection period
            dry_run: If True, don't save to database
        """
        print(f"\n{'='*60}")
        print(f"SEC FORM D COLLECTOR - Venture Capital Deal Tracker")
        print(f"{'='*60}")
        print(f"Period: {start_date.date()} to {end_date.date()}")
        print(f"Dry Run: {dry_run}")
        print(f"{'='*60}\n")

        # Step 1: Search for filings
        filings = self.search_form_d_filings(start_date, end_date)

        if not filings:
            print("\n⚠️  No filings found")
            return

        # Step 2: Download and parse each filing
        for filing in filings:
            filing_data = self.download_form_d(
                filing['accession_number'],
                filing['cik']
            )

            if filing_data:
                # Save to JSON for inspection
                self.save_to_json(filing_data)

                # Save to database (unless dry run)
                if not dry_run:
                    self.save_to_database(filing_data)

        # Print statistics
        print(f"\n{'='*60}")
        print("COLLECTION COMPLETE")
        print(f"{'='*60}")
        print(f"Found:      {self.stats['total_found']}")
        print(f"Downloaded: {self.stats['downloaded']}")
        print(f"Parsed:     {self.stats['parsed']}")
        print(f"Saved:      {self.stats['saved']}")
        print(f"Errors:     {self.stats['errors']}")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Collect SEC Form D filings (VC/PE deals)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect last 30 days
  python collect_sec_form_d_starter.py --days 30

  # Collect specific date range
  python collect_sec_form_d_starter.py --start 2024-01-01 --end 2024-12-31

  # Dry run (don't save to database)
  python collect_sec_form_d_starter.py --days 7 --dry-run

Legal Compliance:
  ✅ SEC data is public domain
  ✅ No authentication required
  ✅ Must respect 10 req/sec rate limit
  ✅ Must include User-Agent with contact info
        """
    )

    parser.add_argument('--days', type=int, help='Collect last N days of filings')
    parser.add_argument('--start', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--dry-run', action='store_true', help='Don\'t save to database')
    parser.add_argument('--db', type=str, default='F:/OSINT_WAREHOUSE/osint_master.db',
                       help='Database path')

    args = parser.parse_args()

    # Determine date range
    if args.days:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
    elif args.start and args.end:
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
    else:
        # Default: last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

    # Run collector
    collector = SECFormDCollector(db_path=args.db)
    collector.collect(start_date, end_date, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
