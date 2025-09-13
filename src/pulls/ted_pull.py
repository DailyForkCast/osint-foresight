#!/usr/bin/env python3
"""
TED (Tenders Electronic Daily) API Pull Script
Retrieves EU public procurement data from TED API v3
Documentation: https://ted.europa.eu/en/api
"""

import argparse
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import requests
from urllib.parse import urlencode

class TEDPuller:
    """Pull procurement data from TED API v3"""
    
    BASE_URL = "https://api.ted.europa.eu/v3"
    NOTICES_ENDPOINT = f"{BASE_URL}/notices/search"
    DETAIL_ENDPOINT = f"{BASE_URL}/notices"
    
    # Country codes mapping
    COUNTRY_CODES = {
        'AT': 'AUT',  # Austria
        'PT': 'PRT',  # Portugal
        'IE': 'IRL',  # Ireland
        'SK': 'SVK',  # Slovakia
    }
    
    # CPV codes for technology sectors (Common Procurement Vocabulary)
    TECH_CPV_CODES = [
        '72000000',  # IT services
        '73000000',  # Research and development
        '48000000',  # Software
        '32000000',  # Radio, television, communication
        '30200000',  # Computer equipment
        '38000000',  # Laboratory equipment
        '31000000',  # Electrical machinery
    ]
    
    def __init__(self, country: str, start_date: str, end_date: str, output_dir: Path):
        """Initialize TED puller"""
        self.country = country.upper()
        self.country_code = self.COUNTRY_CODES.get(self.country, self.country)
        self.start_date = start_date
        self.end_date = end_date
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting
        self.request_delay = 0.5  # seconds between requests
        self.last_request = 0
        
    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request = time.time()
        
    def search_notices(self, 
                      query: Optional[str] = None,
                      cpv_codes: Optional[List[str]] = None,
                      page_size: int = 100,
                      max_pages: int = 10) -> List[Dict]:
        """Search for procurement notices"""
        
        notices = []
        
        # Build query
        query_parts = []
        
        # Country filter
        query_parts.append(f"country:{self.country_code}")
        
        # Date range filter
        query_parts.append(f"publicationDate:[{self.start_date} TO {self.end_date}]")
        
        # CPV codes filter (if specified)
        if cpv_codes:
            cpv_query = " OR ".join([f"cpvMain:{code}*" for code in cpv_codes])
            query_parts.append(f"({cpv_query})")
        
        # Additional query terms
        if query:
            query_parts.append(query)
        
        full_query = " AND ".join(query_parts)
        
        print(f"Searching TED notices for {self.country}")
        print(f"Query: {full_query}")
        
        # Paginate through results
        for page in range(max_pages):
            request_body = {
                'query': full_query,
                'size': page_size,
                'page': page
            }
            
            self._rate_limit()
            
            try:
                response = requests.post(
                    self.NOTICES_ENDPOINT,
                    json=request_body,
                    headers={'Accept': 'application/json', 'Content-Type': 'application/json'}
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Extract notices
                page_notices = data.get('results', [])
                if not page_notices:
                    break
                    
                notices.extend(page_notices)
                
                print(f"  Page {page + 1}: Retrieved {len(page_notices)} notices")
                
                # Check if we've reached the end
                total = data.get('totalResults', 0)
                if len(notices) >= total:
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"Error fetching page {page}: {e}")
                break
                
        print(f"Total notices retrieved: {len(notices)}")
        return notices
    
    def get_notice_detail(self, notice_id: str) -> Optional[Dict]:
        """Get detailed information for a specific notice"""
        
        self._rate_limit()
        
        try:
            response = requests.get(
                f"{self.DETAIL_ENDPOINT}/{notice_id}",
                headers={'Accept': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching notice {notice_id}: {e}")
            return None
    
    def extract_key_fields(self, notice: Dict) -> Dict:
        """Extract key fields from a notice"""
        
        # Extract key information
        extracted = {
            'notice_id': notice.get('id'),
            'publication_date': notice.get('publicationDate'),
            'title': notice.get('title', {}).get('en', ''),
            'country': notice.get('country'),
            'contracting_authority': notice.get('buyerName', ''),
            'procedure_type': notice.get('procedureType'),
            'contract_type': notice.get('contractNature'),
            'cpv_codes': notice.get('cpvCodes', []),
            'value': notice.get('value', {}).get('amount'),
            'currency': notice.get('value', {}).get('currency'),
            'deadline': notice.get('deadline'),
            'nuts_codes': notice.get('nutsCodes', []),
            'ted_url': f"https://ted.europa.eu/notice/{notice.get('id')}",
        }
        
        # Extract description if available
        if 'description' in notice:
            extracted['description'] = notice['description'].get('en', '')
        
        # Extract awarded vendor if it's a contract award notice
        if notice.get('noticeType') == 'CONTRACT_AWARD':
            extracted['awarded_to'] = notice.get('awardedTo', '')
            
        return extracted
    
    def save_results(self, notices: List[Dict], suffix: str = ''):
        """Save notices to JSON and CSV files"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save raw JSON
        json_file = self.output_dir / f"ted_notices_{self.country}{suffix}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(notices, f, indent=2, ensure_ascii=False)
        print(f"Saved raw data to {json_file}")
        
        # Extract and save key fields as CSV
        if notices:
            import csv
            
            extracted = [self.extract_key_fields(n) for n in notices]
            
            csv_file = self.output_dir / f"ted_notices_{self.country}{suffix}_{timestamp}.csv"
            
            fieldnames = extracted[0].keys()
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(extracted)
            
            print(f"Saved CSV to {csv_file}")
            
            # Generate summary
            self.generate_summary(extracted)
    
    def generate_summary(self, notices: List[Dict]):
        """Generate summary statistics"""
        
        print("\n=== Summary Statistics ===")
        print(f"Total notices: {len(notices)}")
        
        # Contract types
        contract_types = {}
        for n in notices:
            ct = n.get('contract_type', 'Unknown')
            contract_types[ct] = contract_types.get(ct, 0) + 1
        
        print("\nContract Types:")
        for ct, count in sorted(contract_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {ct}: {count}")
        
        # Top contracting authorities
        authorities = {}
        for n in notices:
            auth = n.get('contracting_authority', 'Unknown')
            if auth:
                authorities[auth] = authorities.get(auth, 0) + 1
        
        print("\nTop 10 Contracting Authorities:")
        for auth, count in sorted(authorities.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {auth}: {count}")
        
        # Total value (if available)
        total_value = 0
        value_count = 0
        for n in notices:
            if n.get('value'):
                try:
                    total_value += float(n['value'])
                    value_count += 1
                except (ValueError, TypeError):
                    pass
        
        if value_count > 0:
            print(f"\nTotal Contract Value: €{total_value:,.2f} ({value_count} contracts with values)")
    
    def run(self, tech_focus: bool = True):
        """Main execution method"""
        
        print(f"Starting TED data pull for {self.country}")
        print(f"Date range: {self.start_date} to {self.end_date}")
        print(f"Output directory: {self.output_dir}")
        
        if tech_focus:
            # Search for technology-related contracts
            print("\nSearching for technology-related contracts...")
            tech_notices = self.search_notices(
                cpv_codes=self.TECH_CPV_CODES,
                max_pages=20
            )
            
            if tech_notices:
                self.save_results(tech_notices, '_tech')
        
        # Also do a general search
        print("\nSearching for all contracts...")
        all_notices = self.search_notices(
            max_pages=5  # Limit for general search
        )
        
        if all_notices:
            self.save_results(all_notices, '_all')
        
        print("\nTED data pull complete!")


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description='Pull EU procurement data from TED')
    parser.add_argument('--country', required=True, 
                       choices=['AT', 'PT', 'IE', 'SK'],
                       help='Country code (AT, PT, IE, SK)')
    parser.add_argument('--start-date', default='2023-01-01',
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', 
                       default=datetime.now().strftime('%Y-%m-%d'),
                       help='End date (YYYY-MM-DD)')
    parser.add_argument('--out', default=None,
                       help='Output directory')
    parser.add_argument('--tech-only', action='store_true',
                       help='Only search for technology contracts')
    
    args = parser.parse_args()
    
    # Set output directory
    if args.out:
        output_dir = Path(args.out)
    else:
        output_dir = Path('data/raw/source=ted') / f'country={args.country}' / f'date={datetime.now().strftime("%Y-%m-%d")}'
    
    # Create puller and run
    puller = TEDPuller(
        country=args.country,
        start_date=args.start_date,
        end_date=args.end_date,
        output_dir=output_dir
    )
    
    puller.run(tech_focus=not args.tech_only)


if __name__ == '__main__':
    main()