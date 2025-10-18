"""Simple USPTO Client for Patent Searches

Uses the new PatentSearch API that replaced the legacy PatentsView API.
Works without API key but with lower rate limits.
"""

import os
import json
import time
import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

class SimpleUSPTOClient:
    """Simple client for USPTO PatentSearch API"""

    def __init__(self, api_key: str = None):
        """Initialize client

        Args:
            api_key: Optional API key for higher rate limits
        """
        self.base_url = "https://search.patentsview.org"
        self.api_key = api_key
        self.session = requests.Session()

        # Set headers
        self.session.headers.update({
            'User-Agent': 'OSINT-Italy-Research/1.0',
            'Accept': 'application/json'
        })

        if api_key:
            self.session.headers['X-Api-Key'] = api_key
            self.rate_limit = 45  # per minute with key
        else:
            self.rate_limit = 10  # per minute without key

        self.last_request = 0
        self.min_interval = 60 / self.rate_limit

    def _rate_limit(self):
        """Enforce rate limiting"""
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request = time.time()

    def search_patents_simple(self, query: str, size: int = 25) -> Dict:
        """Simple patent search using GET request

        Args:
            query: Search query string
            size: Number of results (max 100)

        Returns:
            Dictionary with search results
        """
        self._rate_limit()

        # Use GET endpoint for simple queries
        url = f"{self.base_url}/api/v1/patent/"

        params = {
            'q': query,
            'per_page': min(size, 100)
        }

        try:
            response = self.session.get(url, params=params)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error {response.status_code}: {response.text[:200]}")
                return {}
        except Exception as e:
            print(f"Request failed: {e}")
            return {}

    def get_italian_patents(self,
                          year: int = 2024,
                          limit: int = 100) -> pd.DataFrame:
        """Get patents from Italian inventors

        Args:
            year: Year to search
            limit: Maximum results

        Returns:
            DataFrame with patent data
        """
        # Search for patents with Italian inventors
        query = f"inventor_country:IT AND patent_date:[{year}-01-01 TO {year}-12-31]"

        results = self.search_patents_simple(query, limit)

        if results and 'patents' in results:
            df = pd.DataFrame(results['patents'])
            print(f"Found {len(df)} Italian patents for {year}")
            return df
        else:
            print(f"No results found for query: {query}")
            return pd.DataFrame()

    def search_by_assignee(self,
                          company: str,
                          start_year: int = 2020) -> pd.DataFrame:
        """Search patents by company/assignee name

        Args:
            company: Company name
            start_year: Start year for search

        Returns:
            DataFrame with patent data
        """
        current_year = datetime.now().year
        query = f'assignee_organization:"{company}" AND patent_date:[{start_year}-01-01 TO {current_year}-12-31]'

        results = self.search_patents_simple(query, 100)

        if results and 'patents' in results:
            df = pd.DataFrame(results['patents'])
            print(f"Found {len(df)} patents for {company}")
            return df
        else:
            print(f"No patents found for {company}")
            return pd.DataFrame()

    def find_italy_china_collaborations(self, year: int = 2023) -> pd.DataFrame:
        """Find patents with both Italian and Chinese involvement

        Args:
            year: Year to search

        Returns:
            DataFrame with collaborative patents
        """
        # This is a simplified search - more complex analysis would be needed
        query = f"(inventor_country:IT OR assignee_country:IT) AND (inventor_country:CN OR assignee_country:CN) AND patent_date:[{year}-01-01 TO {year}-12-31]"

        results = self.search_patents_simple(query, 100)

        if results and 'patents' in results:
            df = pd.DataFrame(results['patents'])
            print(f"Found {len(df)} potential Italy-China collaborative patents for {year}")
            return df
        else:
            print("No collaborative patents found")
            return pd.DataFrame()

    def test_connection(self) -> bool:
        """Test API connection

        Returns:
            True if connection successful
        """
        print("Testing PatentSearch API connection...")

        # Try a simple query
        query = "patent_number:10000000"  # Specific patent
        results = self.search_patents_simple(query, 1)

        if results:
            print("[OK] Connection successful!")
            if 'patents' in results and len(results['patents']) > 0:
                patent = results['patents'][0]
                print(f"  Sample patent: {patent.get('patent_number', 'N/A')}")
                print(f"  Title: {patent.get('patent_title', 'N/A')[:60]}...")
            return True
        else:
            print("[ERROR] Connection failed")
            return False

def main():
    """Main function for testing"""
    print("="*60)
    print("USPTO PatentSearch API Test")
    print("="*60)

    # Create client (no API key needed for basic searches)
    client = SimpleUSPTOClient()

    # Test connection
    if not client.test_connection():
        print("\nConnection test failed. Please check your internet connection.")
        return

    print("\n" + "-"*60)
    print("\n1. Searching for recent Italian patents...")
    italian_patents = client.get_italian_patents(year=2024, limit=5)

    if not italian_patents.empty:
        print("\nSample Italian patents:")
        for idx, row in italian_patents.head(3).iterrows():
            print(f"  - {row.get('patent_number', 'N/A')}: {row.get('patent_title', 'N/A')[:50]}")

    print("\n" + "-"*60)
    print("\n2. Searching for Leonardo patents...")
    leonardo_patents = client.search_by_assignee("Leonardo", start_year=2022)

    if not leonardo_patents.empty:
        print(f"\nFound {len(leonardo_patents)} Leonardo patents since 2022")

    print("\n" + "-"*60)
    print("\n3. Searching for Italy-China collaborations...")
    collabs = client.find_italy_china_collaborations(year=2023)

    if not collabs.empty:
        print(f"\nFound {len(collabs)} potential collaborations in 2023")

    print("\n" + "="*60)
    print("Test complete!")

    # Save results if any found
    output_dir = "C:/Projects/OSINT - Foresight/data/collected/uspto"
    if not italian_patents.empty:
        os.makedirs(output_dir, exist_ok=True)
        italian_patents.to_csv(f"{output_dir}/italian_patents_sample.csv", index=False)
        print(f"\nResults saved to {output_dir}/italian_patents_sample.csv")

if __name__ == "__main__":
    main()
