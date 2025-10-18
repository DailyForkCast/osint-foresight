#!/usr/bin/env python3
"""USPTO PatentSearch API Client

Uses the new PatentSearch API that replaced the legacy PatentsView API.
Based on current 2025 documentation and working endpoints.
"""

import os
import json
import time
import requests
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

class USPTOPatentSearchClient:
    """Client for USPTO PatentSearch API (2025 version)"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize USPTO PatentSearch client

        Args:
            api_key: Optional API key for higher rate limits (45/min with key, lower without)
        """
        # Use the correct 2025 endpoint
        self.base_url = "https://api.patentsview.org"
        self.api_key = api_key or os.getenv('USPTO_API_KEY')

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Research/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

        # Rate limiting
        if self.api_key:
            self.rate_limit = 45  # per minute with key
        else:
            self.rate_limit = 10  # conservative without key

        self.last_request = 0
        self.min_interval = 60 / self.rate_limit

    def _rate_limit(self):
        """Enforce rate limiting"""
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request = time.time()

    def search_patents(self,
                      query: Dict[str, Any],
                      fields: Optional[List[str]] = None,
                      per_page: int = 100,
                      page: int = 1) -> Dict[str, Any]:
        """Search patents using the PatentSearch API

        Args:
            query: Query dictionary in PatentsView format
            fields: List of fields to return
            per_page: Results per page (max 1000)
            page: Page number

        Returns:
            API response dictionary
        """
        self._rate_limit()

        # Default fields if none specified
        if fields is None:
            fields = [
                "patent_number",
                "patent_title",
                "patent_date",
                "inventor_first_name",
                "inventor_last_name",
                "inventor_country",
                "assignee_organization",
                "assignee_country",
                "cpc_category",
                "patent_abstract"
            ]

        # Build request parameters
        params = {
            'q': json.dumps(query),
            'f': json.dumps(fields),
            'per_page': min(per_page, 1000),
            'page': page
        }

        # Add API key if available
        if self.api_key:
            params['api_key'] = self.api_key

        url = f"{self.base_url}/patents/query"

        try:
            # Try GET first (simpler for debugging)
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                print(f"Access denied (403). Trying without API key...")
                # Try without API key
                params.pop('api_key', None)
                response = self.session.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Error {response.status_code}: {response.text[:500]}")
                    return {}
            else:
                print(f"Error {response.status_code}: {response.text[:500]}")
                return {}

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {}

    def search_by_country(self,
                         country_code: str,
                         start_date: str = "2020-01-01",
                         end_date: Optional[str] = None,
                         limit: int = 100) -> pd.DataFrame:
        """Search patents by inventor or assignee country

        Args:
            country_code: ISO country code (e.g., 'IT' for Italy, 'CN' for China)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date (defaults to today)
            limit: Maximum results to return

        Returns:
            DataFrame with patent data
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # Build query for country involvement
        query = {
            "_and": [
                {
                    "_or": [
                        {"inventor_country": country_code},
                        {"assignee_country": country_code}
                    ]
                },
                {"_gte": {"patent_date": start_date}},
                {"_lte": {"patent_date": end_date}}
            ]
        }

        results = self.search_patents(query, per_page=min(limit, 1000))

        if results and 'patents' in results:
            df = pd.DataFrame(results['patents'])
            print(f"Found {len(df)} patents for country {country_code}")
            return df
        else:
            print(f"No patents found for country {country_code}")
            return pd.DataFrame()

    def find_collaborations(self,
                           country1: str,
                           country2: str,
                           start_date: str = "2020-01-01",
                           limit: int = 100) -> pd.DataFrame:
        """Find collaborative patents between two countries

        Args:
            country1: First country code
            country2: Second country code
            start_date: Start date for search
            limit: Maximum results

        Returns:
            DataFrame with collaborative patents
        """
        # Query for patents with inventors/assignees from both countries
        query = {
            "_and": [
                {
                    "_or": [
                        {"inventor_country": country1},
                        {"assignee_country": country1}
                    ]
                },
                {
                    "_or": [
                        {"inventor_country": country2},
                        {"assignee_country": country2}
                    ]
                },
                {"_gte": {"patent_date": start_date}}
            ]
        }

        results = self.search_patents(query, per_page=min(limit, 1000))

        if results and 'patents' in results:
            df = pd.DataFrame(results['patents'])
            print(f"Found {len(df)} potential {country1}-{country2} collaborations")
            return df
        else:
            print(f"No collaborative patents found")
            return pd.DataFrame()

    def search_by_technology(self,
                           cpc_section: str,
                           country: Optional[str] = None,
                           start_date: str = "2020-01-01",
                           limit: int = 100) -> pd.DataFrame:
        """Search patents by CPC technology classification

        Args:
            cpc_section: CPC section code (e.g., 'H' for Electricity)
            country: Optional country filter
            start_date: Start date
            limit: Maximum results

        Returns:
            DataFrame with patent data
        """
        query = {
            "_and": [
                {"cpc_section_id": cpc_section},
                {"_gte": {"patent_date": start_date}}
            ]
        }

        if country:
            query["_and"].append({
                "_or": [
                    {"inventor_country": country},
                    {"assignee_country": country}
                ]
            })

        results = self.search_patents(query, per_page=min(limit, 1000))

        if results and 'patents' in results:
            df = pd.DataFrame(results['patents'])
            print(f"Found {len(df)} patents in CPC section {cpc_section}")
            return df
        else:
            print(f"No patents found")
            return pd.DataFrame()

    def test_connection(self) -> bool:
        """Test API connection with a simple query

        Returns:
            True if connection successful
        """
        print("Testing USPTO PatentSearch API connection...")
        print(f"Endpoint: {self.base_url}/patents/query")

        # Simple test query - search for a specific recent patent
        test_query = {"patent_number": "11000000"}

        results = self.search_patents(
            test_query,
            fields=["patent_number", "patent_title", "patent_date"],
            per_page=1
        )

        if results:
            if 'patents' in results and len(results['patents']) > 0:
                patent = results['patents'][0]
                print(f"✓ Connection successful!")
                print(f"  Sample patent: {patent.get('patent_number', 'N/A')}")
                print(f"  Title: {patent.get('patent_title', 'N/A')[:60]}...")
                print(f"  Date: {patent.get('patent_date', 'N/A')}")
                return True
            elif 'total_patent_count' in results:
                print(f"✓ API responding (found {results['total_patent_count']} total patents)")
                return True
            else:
                print(f"⚠ API responded but no patents found")
                print(f"Response keys: {list(results.keys())}")
                return False
        else:
            print("✗ Connection failed")
            return False


def main():
    """Test the USPTO PatentSearch API client"""
    print("="*70)
    print("USPTO PatentSearch API Client Test")
    print("="*70)

    # Initialize client
    client = USPTOPatentSearchClient()

    # Test connection
    if not client.test_connection():
        print("\n⚠ Connection issues detected. Continuing with limited testing...")

    print("\n" + "-"*70)
    print("Testing Italy patent search...")
    italy_patents = client.search_by_country("IT", start_date="2024-01-01", limit=5)

    if not italy_patents.empty:
        print(f"\nFound {len(italy_patents)} Italian patents")
        print("\nSample patents:")
        for idx, row in italy_patents.head(3).iterrows():
            print(f"  • {row.get('patent_number', 'N/A')}: {row.get('patent_title', 'N/A')[:50]}")

    print("\n" + "-"*70)
    print("Testing Italy-China collaborations...")
    collaborations = client.find_collaborations("IT", "CN", start_date="2023-01-01", limit=10)

    if not collaborations.empty:
        print(f"\nFound {len(collaborations)} potential collaborations")

    # Save results if found
    output_dir = Path("C:/Projects/OSINT - Foresight/data/collected/uspto")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not italy_patents.empty:
        output_file = output_dir / f"italy_patents_{datetime.now():%Y%m%d}.csv"
        italy_patents.to_csv(output_file, index=False)
        print(f"\nResults saved to {output_file}")

    print("\n" + "="*70)
    print("Test complete!")
    print("\nNote: If you're getting 403 errors, the API may require:")
    print("  1. Email verification of your API key")
    print("  2. Registration at https://patentsview.org")
    print("  3. Or the API may be temporarily unavailable")
    print("="*70)


if __name__ == "__main__":
    main()
