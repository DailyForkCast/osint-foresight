"""USPTO Client that reads API key from environment file"""

import os
import json
import time
import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path("C:/Projects/OSINT - Foresight/.env.local")
load_dotenv(env_path)

class USPTOEnvClient:
    """USPTO Client with environment-based configuration"""

    def __init__(self):
        """Initialize client with API key from environment"""
        self.api_key = os.getenv('USPTO_API_KEY')

        if not self.api_key or self.api_key == 'your_api_key_here':
            print("WARNING: No valid USPTO API key found in .env.local")
            print("Please update USPTO_API_KEY in .env.local with your actual API key")
            print("Get your free API key at: https://search.patentsview.org/")
            self.api_key = None

        self.base_url = "https://search.patentsview.org"
        self.session = requests.Session()

        # Set headers
        self.session.headers.update({
            'User-Agent': 'OSINT-Italy-Research/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

        if self.api_key:
            self.session.headers['X-API-Key'] = self.api_key  # Changed to uppercase API
            self.rate_limit = int(os.getenv('USPTO_RATE_LIMIT', 45))
            print(f"USPTO client initialized with API key (rate limit: {self.rate_limit}/min)")
        else:
            self.rate_limit = 10  # Lower limit without key
            print("USPTO client initialized without API key (limited functionality)")

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
                      query: Dict = None,
                      fields: List[str] = None,
                      options: Dict = None,
                      size: int = 25) -> pd.DataFrame:
        """Search patents using PatentSearch API

        Args:
            query: Query dictionary
            fields: List of fields to return
            options: Additional options
            size: Number of results

        Returns:
            DataFrame with patent data
        """
        self._rate_limit()

        # Default fields if not specified
        if fields is None:
            fields = [
                "patent_number",
                "patent_title",
                "patent_date",
                "patent_abstract",
                "inventor_first_name",
                "inventor_last_name",
                "inventor_country",
                "assignee_organization",
                "assignee_country",
                "cpc_group_id"
            ]

        # Build request payload
        payload = {
            'q': json.dumps(query) if query else '{}',
            'f': json.dumps(fields),
            'o': json.dumps({"per_page": min(size, 100)})
        }

        # Use GET request with query parameters for the new API
        url = f"{self.base_url}/api/v1/patent/"

        # Convert POST payload to GET parameters
        params = {
            'q': query if isinstance(query, str) else json.dumps(query) if query else '{}',
            'f': json.dumps(fields),
            'o': json.dumps({"per_page": min(size, 100)})
        }

        try:
            response = self.session.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if 'patents' in data:
                    df = pd.DataFrame(data['patents'])
                    return df
                else:
                    print("No patents found")
                    return pd.DataFrame()
            else:
                print(f"Error {response.status_code}: {response.text[:200]}")
                return pd.DataFrame()
        except Exception as e:
            print(f"Request failed: {e}")
            return pd.DataFrame()

    def get_italian_patents(self,
                          start_date: str = "2024-01-01",
                          end_date: str = None,
                          limit: int = 100) -> pd.DataFrame:
        """Get patents from Italian inventors/assignees

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum results

        Returns:
            DataFrame with Italian patents
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        query = {
            "_and": [
                {"_or": [
                    {"inventor_country": "IT"},
                    {"assignee_country": "IT"}
                ]},
                {"_gte": {"patent_date": start_date}},
                {"_lte": {"patent_date": end_date}}
            ]
        }

        print(f"Searching Italian patents from {start_date} to {end_date}...")
        df = self.search_patents(query=query, size=limit)

        if not df.empty:
            print(f"Found {len(df)} Italian patents")
        return df

    def search_by_company(self,
                         company_name: str,
                         start_date: str = "2020-01-01",
                         limit: int = 100) -> pd.DataFrame:
        """Search patents by company name

        Args:
            company_name: Company/assignee name
            start_date: Start date
            limit: Maximum results

        Returns:
            DataFrame with company patents
        """
        end_date = datetime.now().strftime("%Y-%m-%d")

        query = {
            "_and": [
                {"assignee_organization": company_name},
                {"_gte": {"patent_date": start_date}},
                {"_lte": {"patent_date": end_date}}
            ]
        }

        print(f"Searching {company_name} patents from {start_date}...")
        df = self.search_patents(query=query, size=limit)

        if not df.empty:
            print(f"Found {len(df)} {company_name} patents")
        return df

    def find_italy_china_collaborations(self,
                                       start_date: str = "2020-01-01",
                                       limit: int = 200) -> pd.DataFrame:
        """Find patents with Italy-China collaboration

        Args:
            start_date: Start date
            limit: Maximum results

        Returns:
            DataFrame with collaborative patents
        """
        end_date = datetime.now().strftime("%Y-%m-%d")

        # First get Italian patents
        italy_df = self.get_italian_patents(start_date, end_date, limit)

        if italy_df.empty:
            return pd.DataFrame()

        # Filter for those with Chinese involvement
        # This is simplified - would need more sophisticated analysis
        collabs = []

        for idx, row in italy_df.iterrows():
            # Check if any Chinese involvement
            inventors = str(row.get('inventor_country', '')).split(';')
            assignees = str(row.get('assignee_country', '')).split(';')

            if 'CN' in inventors or 'CN' in assignees:
                collabs.append(row)

        collab_df = pd.DataFrame(collabs)

        if not collab_df.empty:
            print(f"Found {len(collab_df)} potential Italy-China collaborations")
        else:
            print("No Italy-China collaborations found")

        return collab_df

    def analyze_technology_trends(self,
                                 patents_df: pd.DataFrame) -> Dict:
        """Analyze technology trends from patent data

        Args:
            patents_df: DataFrame with patent data

        Returns:
            Dictionary with trend analysis
        """
        if patents_df.empty:
            return {}

        analysis = {
            'total_patents': len(patents_df),
            'date_range': {
                'earliest': patents_df['patent_date'].min() if 'patent_date' in patents_df else None,
                'latest': patents_df['patent_date'].max() if 'patent_date' in patents_df else None
            },
            'top_assignees': {},
            'technology_areas': {},
            'collaboration_countries': {}
        }

        # Top assignees
        if 'assignee_organization' in patents_df:
            top_assignees = patents_df['assignee_organization'].value_counts().head(10)
            analysis['top_assignees'] = top_assignees.to_dict()

        # Technology areas (CPC codes)
        if 'cpc_group_id' in patents_df:
            cpc_counts = {}
            for cpcs in patents_df['cpc_group_id'].dropna():
                for cpc in str(cpcs).split(';'):
                    cpc = cpc.strip()[:3]  # Get main category
                    cpc_counts[cpc] = cpc_counts.get(cpc, 0) + 1
            analysis['technology_areas'] = dict(sorted(cpc_counts.items(),
                                                      key=lambda x: x[1],
                                                      reverse=True)[:10])

        # Collaboration countries
        if 'inventor_country' in patents_df:
            country_counts = {}
            for countries in patents_df['inventor_country'].dropna():
                for country in str(countries).split(';'):
                    country = country.strip()
                    if country and country != 'IT':  # Exclude Italy itself
                        country_counts[country] = country_counts.get(country, 0) + 1
            analysis['collaboration_countries'] = dict(sorted(country_counts.items(),
                                                            key=lambda x: x[1],
                                                            reverse=True)[:10])

        return analysis

    def save_results(self,
                    df: pd.DataFrame,
                    filename: str,
                    analysis: Dict = None):
        """Save search results and analysis

        Args:
            df: DataFrame to save
            filename: Base filename (without extension)
            analysis: Optional analysis dictionary
        """
        output_dir = Path("C:/Projects/OSINT - Foresight/data/collected/uspto")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save data
        csv_path = output_dir / f"{filename}.csv"
        df.to_csv(csv_path, index=False)
        print(f"Saved {len(df)} patents to {csv_path}")

        # Save analysis if provided
        if analysis:
            json_path = output_dir / f"{filename}_analysis.json"
            with open(json_path, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            print(f"Saved analysis to {json_path}")

def test_client():
    """Test the USPTO client with environment configuration"""
    print("="*60)
    print("USPTO PatentSearch API Test (with Environment Config)")
    print("="*60)

    # Initialize client
    client = USPTOEnvClient()

    if not client.api_key or client.api_key == 'your_api_key_here':
        print("\nPlease add your USPTO API key to .env.local:")
        print("  1. Open C:/Projects/OSINT - Foresight/.env.local")
        print("  2. Replace 'your_api_key_here' with your actual API key")
        print("  3. Get a free key at: https://search.patentsview.org/")
        return

    print("\n1. Testing Italian patent search...")
    italian_patents = client.get_italian_patents(
        start_date="2024-01-01",
        end_date="2024-12-31",
        limit=10
    )

    if not italian_patents.empty:
        print("\nSample results:")
        for idx, row in italian_patents.head(3).iterrows():
            print(f"  - {row.get('patent_number', 'N/A')}: {row.get('patent_title', 'N/A')[:50]}...")

        # Analyze trends
        print("\n2. Analyzing technology trends...")
        analysis = client.analyze_technology_trends(italian_patents)

        if analysis:
            print(f"  Total patents: {analysis['total_patents']}")
            print(f"  Date range: {analysis['date_range']['earliest']} to {analysis['date_range']['latest']}")

            if analysis['technology_areas']:
                print("  Top technology areas:")
                for cpc, count in list(analysis['technology_areas'].items())[:3]:
                    print(f"    - {cpc}: {count} patents")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client.save_results(italian_patents, f"italian_patents_{timestamp}", analysis)

    print("\n" + "="*60)
    print("Test complete!")

if __name__ == "__main__":
    # Install python-dotenv if needed
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("Installing python-dotenv...")
        import subprocess
        subprocess.check_call(["pip", "install", "python-dotenv"])
        from dotenv import load_dotenv

    test_client()
