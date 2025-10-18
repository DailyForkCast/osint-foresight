"""USPTO TSDR (Trademark Status & Document Retrieval) API Client

This client interfaces with the USPTO Trademark API for searching and retrieving
trademark information relevant to Italian technology companies.

API Documentation: https://tsdr.uspto.gov/
"""

import os
import json
import time
import requests
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

# Load environment variables
env_path = Path("C:/Projects/OSINT - Foresight/.env.local")
load_dotenv(env_path)

class TSDRClient:
    """Client for USPTO TSDR (Trademark) API"""

    def __init__(self):
        """Initialize TSDR client with API key from environment"""
        self.api_key = os.getenv('USPTO_API_KEY')

        if not self.api_key:
            print("WARNING: No USPTO API key found in .env.local")
            self.api_key = None
        else:
            print(f"TSDR client initialized with API key")

        # TSDR API endpoints
        self.base_url = "https://tsdrapi.uspto.gov"
        self.search_url = "https://tmsearch.uspto.gov"

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Italy-Trademark-Research/1.0',
            'Accept': 'application/json, application/xml'
        })

        if self.api_key:
            self.session.headers['X-API-Key'] = self.api_key

        # Rate limiting
        self.last_request = 0
        self.min_interval = 1.0  # 1 second between requests

    def _rate_limit(self):
        """Enforce rate limiting"""
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request = time.time()

    def search_by_serial(self, serial_number: str) -> Dict:
        """Search trademark by serial number

        Args:
            serial_number: USPTO serial number

        Returns:
            Dictionary with trademark data
        """
        self._rate_limit()

        # TSDR API endpoint for serial number search
        url = f"{self.base_url}/statusview/sn{serial_number}/info.xml"

        try:
            response = self.session.get(url)

            if response.status_code == 200:
                # Parse XML response
                root = ET.fromstring(response.content)
                return self._parse_tsdr_xml(root)
            else:
                print(f"Error {response.status_code}: {response.text[:200]}")
                return {}
        except Exception as e:
            print(f"Request failed: {e}")
            return {}

    def search_by_owner(self, owner_name: str, limit: int = 100) -> pd.DataFrame:
        """Search trademarks by owner name

        Args:
            owner_name: Company/owner name to search
            limit: Maximum number of results

        Returns:
            DataFrame with trademark results
        """
        self._rate_limit()

        # Use the trademark search API
        params = {
            'searchText': f'owner:("{owner_name}")',
            'rows': min(limit, 1000)
        }

        if self.api_key:
            params['api_key'] = self.api_key

        url = f"{self.search_url}/search"

        try:
            response = self.session.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if 'trademarks' in data:
                    return pd.DataFrame(data['trademarks'])
                else:
                    print("No trademarks found")
                    return pd.DataFrame()
            else:
                print(f"Error {response.status_code}: {response.text[:200]}")
                return pd.DataFrame()
        except Exception as e:
            print(f"Search failed: {e}")
            return pd.DataFrame()

    def search_italian_companies(self, companies: List[str] = None) -> pd.DataFrame:
        """Search trademarks for Italian technology companies

        Args:
            companies: List of company names (uses default list if None)

        Returns:
            DataFrame with all trademark results
        """
        if companies is None:
            # Default Italian tech companies
            companies = [
                "Leonardo",
                "Leonardo S.p.A",
                "Finmeccanica",
                "Fincantieri",
                "STMicroelectronics",
                "Thales Alenia",
                "Telespazio",
                "Ansaldo",
                "Pirelli",
                "Iveco"
            ]

        all_results = []

        for company in companies:
            print(f"Searching trademarks for: {company}")
            results = self.search_by_owner(company, limit=50)

            if not results.empty:
                results['search_company'] = company
                all_results.append(results)
                print(f"  Found {len(results)} trademarks")
            else:
                print(f"  No trademarks found")

            # Rate limiting between searches
            time.sleep(2)

        if all_results:
            combined_df = pd.concat(all_results, ignore_index=True)
            return combined_df
        else:
            return pd.DataFrame()

    def analyze_trademark_portfolio(self, trademarks_df: pd.DataFrame) -> Dict:
        """Analyze trademark portfolio data

        Args:
            trademarks_df: DataFrame with trademark data

        Returns:
            Dictionary with portfolio analysis
        """
        if trademarks_df.empty:
            return {}

        analysis = {
            'total_trademarks': len(trademarks_df),
            'companies': {},
            'status_distribution': {},
            'class_distribution': {},
            'filing_trends': {}
        }

        # Analyze by company
        if 'search_company' in trademarks_df:
            company_counts = trademarks_df['search_company'].value_counts()
            analysis['companies'] = company_counts.to_dict()

        # Status distribution
        if 'status' in trademarks_df:
            status_counts = trademarks_df['status'].value_counts()
            analysis['status_distribution'] = status_counts.to_dict()

        # International class distribution
        if 'international_class' in trademarks_df:
            class_counts = {}
            for classes in trademarks_df['international_class'].dropna():
                for cls in str(classes).split(','):
                    cls = cls.strip()
                    class_counts[cls] = class_counts.get(cls, 0) + 1

            # Top 10 classes
            analysis['class_distribution'] = dict(
                sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            )

        # Filing trends by year
        if 'filing_date' in trademarks_df:
            trademarks_df['filing_year'] = pd.to_datetime(
                trademarks_df['filing_date'], errors='coerce'
            ).dt.year

            year_counts = trademarks_df['filing_year'].value_counts().sort_index()
            analysis['filing_trends'] = year_counts.to_dict()

        return analysis

    def find_technology_trademarks(self, trademarks_df: pd.DataFrame) -> pd.DataFrame:
        """Filter trademarks related to technology sectors

        Args:
            trademarks_df: DataFrame with trademark data

        Returns:
            DataFrame with technology-related trademarks
        """
        # Technology-related International Classes
        tech_classes = [
            '009',  # Scientific apparatus, computers, software
            '035',  # Business services, data processing
            '038',  # Telecommunications
            '042',  # Scientific and technological services
            '045'   # Security services
        ]

        if 'international_class' in trademarks_df:
            tech_mask = trademarks_df['international_class'].apply(
                lambda x: any(cls in str(x) for cls in tech_classes) if pd.notna(x) else False
            )
            return trademarks_df[tech_mask]
        else:
            return trademarks_df

    def _parse_tsdr_xml(self, root: ET.Element) -> Dict:
        """Parse TSDR XML response

        Args:
            root: XML root element

        Returns:
            Dictionary with parsed trademark data
        """
        data = {}

        # Extract key fields from XML
        # This is simplified - actual TSDR XML is complex
        for child in root:
            if child.tag == 'serial-number':
                data['serial_number'] = child.text
            elif child.tag == 'registration-number':
                data['registration_number'] = child.text
            elif child.tag == 'status':
                data['status'] = child.text
            elif child.tag == 'mark-text':
                data['mark_text'] = child.text
            elif child.tag == 'owner':
                data['owner'] = child.text
            elif child.tag == 'filing-date':
                data['filing_date'] = child.text

        return data

    def save_results(self,
                    df: pd.DataFrame,
                    filename: str,
                    analysis: Dict = None):
        """Save trademark search results

        Args:
            df: DataFrame to save
            filename: Base filename
            analysis: Optional analysis dictionary
        """
        output_dir = Path("C:/Projects/OSINT - Foresight/data/collected/trademarks")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save data
        csv_path = output_dir / f"{filename}.csv"
        df.to_csv(csv_path, index=False)
        print(f"Saved {len(df)} trademarks to {csv_path}")

        # Save analysis
        if analysis:
            json_path = output_dir / f"{filename}_analysis.json"
            with open(json_path, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            print(f"Saved analysis to {json_path}")

def test_tsdr_client():
    """Test TSDR client functionality"""
    print("="*60)
    print("USPTO TSDR (Trademark) API Test")
    print("="*60)

    client = TSDRClient()

    print("\n1. Testing trademark search for Italian companies...")

    # Test with a few companies
    test_companies = ["Leonardo", "STMicroelectronics", "Fincantieri"]

    results = client.search_italian_companies(test_companies)

    if not results.empty:
        print(f"\nTotal trademarks found: {len(results)}")

        # Analyze portfolio
        print("\n2. Analyzing trademark portfolio...")
        analysis = client.analyze_trademark_portfolio(results)

        if analysis:
            print(f"  Companies analyzed: {len(analysis.get('companies', {}))}")
            print(f"  Total trademarks: {analysis['total_trademarks']}")

            if analysis.get('class_distribution'):
                print("  Top trademark classes:")
                for cls, count in list(analysis['class_distribution'].items())[:5]:
                    print(f"    Class {cls}: {count} trademarks")

        # Filter technology trademarks
        print("\n3. Filtering technology-related trademarks...")
        tech_marks = client.find_technology_trademarks(results)
        print(f"  Found {len(tech_marks)} technology-related trademarks")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client.save_results(
            results,
            f"italian_trademarks_{timestamp}",
            analysis
        )
    else:
        print("\nNo trademarks found. The API may require different authentication.")

    print("\n" + "="*60)
    print("Note: TSDR API focuses on US trademark registrations.")
    print("Italian companies may have limited US trademark filings.")
    print("Consider also searching EU IPO (EUIPO) for European trademarks.")
    print("="*60)

if __name__ == "__main__":
    test_tsdr_client()
