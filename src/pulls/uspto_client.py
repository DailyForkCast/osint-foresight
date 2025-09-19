"""USPTO API Client for Patent Data Analysis

This module provides access to USPTO patent data through multiple APIs:
1. PatentsView API - Free, comprehensive patent search
2. USPTO Open Data Portal - Various datasets
3. Patent Examination Data System (PEDS) - Application status
"""

import os
import json
import time
import yaml
import requests
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

class USPTOClient:
    """Client for USPTO patent data APIs"""

    def __init__(self, config_path: str = None):
        """Initialize USPTO client with configuration"""
        if config_path is None:
            config_path = "C:/Projects/OSINT - Foresight/config/uspto_config.yaml"

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Foresight-Research/1.0 (Patent Analysis)'
        })

        # Rate limiting
        self.last_request_time = 0
        self.request_interval = 60 / self.config['usp_api']['patentsview']['rate_limit']

    def _rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_interval:
            time.sleep(self.request_interval - time_since_last)
        self.last_request_time = time.time()

    def search_patents(self,
                      assignee: str = None,
                      inventor_country: str = None,
                      cpc_codes: List[str] = None,
                      date_range: tuple = None,
                      keywords: str = None,
                      limit: int = 100) -> pd.DataFrame:
        """
        Search patents using PatentsView API

        Args:
            assignee: Company/organization name
            inventor_country: Country code (e.g., 'IT')
            cpc_codes: List of CPC classification codes
            date_range: Tuple of (start_date, end_date) as strings
            keywords: Keywords to search in title/abstract
            limit: Maximum number of results

        Returns:
            DataFrame with patent data
        """

        # Build query
        query_parts = []

        if assignee:
            query_parts.append(json.dumps({"assignee_organization": assignee}))

        if inventor_country:
            query_parts.append(json.dumps({"inventor_country": inventor_country}))

        if cpc_codes:
            cpc_query = {"_or": [{"cpc_subgroup_id": code} for code in cpc_codes]}
            query_parts.append(json.dumps(cpc_query))

        if date_range:
            date_query = {
                "_gte": {"patent_date": date_range[0]},
                "_lte": {"patent_date": date_range[1]}
            }
            query_parts.append(json.dumps(date_query))

        if keywords:
            keyword_query = {
                "_text_any": {
                    "patent_title": keywords,
                    "patent_abstract": keywords
                }
            }
            query_parts.append(json.dumps(keyword_query))

        # Combine query parts
        if len(query_parts) > 1:
            query = json.dumps({"_and": [json.loads(q) for q in query_parts]})
        elif query_parts:
            query = query_parts[0]
        else:
            query = '{}'

        # Prepare API request
        url = self.config['usp_api']['patentsview']['base_url'] + self.config['usp_api']['patentsview']['endpoints']['patents']

        payload = {
            'q': query,
            'f': json.dumps([
                "patent_number",
                "patent_title",
                "patent_date",
                "patent_abstract",
                "assignee_organization",
                "inventor_country",
                "cpc_subgroup_id",
                "cited_patent_number",
                "app_date"
            ]),
            'o': json.dumps({
                "per_page": limit
            })
        }

        # Make request with rate limiting
        self._rate_limit()
        response = self.session.post(url, data=payload)

        if response.status_code == 200:
            data = response.json()
            if 'patents' in data:
                return pd.DataFrame(data['patents'])
            else:
                print(f"No patents found for query: {query}")
                return pd.DataFrame()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return pd.DataFrame()

    def get_italy_patents(self,
                         start_date: str = "2020-01-01",
                         end_date: str = None) -> pd.DataFrame:
        """
        Get patents from Italian inventors/assignees

        Args:
            start_date: Start date for patent search
            end_date: End date (defaults to today)

        Returns:
            DataFrame with Italian patent data
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # Search for Italian patents
        italy_patents = self.search_patents(
            inventor_country="IT",
            date_range=(start_date, end_date),
            limit=500
        )

        return italy_patents

    def get_company_patents(self, company_name: str,
                          start_date: str = "2020-01-01") -> pd.DataFrame:
        """
        Get patents for a specific company

        Args:
            company_name: Name of the company
            start_date: Start date for search

        Returns:
            DataFrame with company patent data
        """
        end_date = datetime.now().strftime("%Y-%m-%d")

        return self.search_patents(
            assignee=company_name,
            date_range=(start_date, end_date),
            limit=500
        )

    def analyze_technology_areas(self,
                                patents_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze technology areas from patent data

        Args:
            patents_df: DataFrame with patent data

        Returns:
            Dictionary with technology area analysis
        """
        if patents_df.empty:
            return {}

        # Count patents by CPC code
        cpc_counts = {}
        for _, row in patents_df.iterrows():
            if pd.notna(row.get('cpc_subgroup_id')):
                cpc = str(row['cpc_subgroup_id'])[:3]  # Get main category
                cpc_counts[cpc] = cpc_counts.get(cpc, 0) + 1

        # Map to technology areas
        tech_areas = self.config['search_config']['technology_areas']
        area_counts = {}

        for area_name, cpc_list in tech_areas.items():
            count = sum(cpc_counts.get(cpc, 0) for cpc in cpc_list)
            if count > 0:
                area_counts[area_name] = count

        # Calculate statistics
        total_patents = len(patents_df)

        return {
            'total_patents': total_patents,
            'technology_areas': area_counts,
            'top_cpc_codes': dict(sorted(cpc_counts.items(),
                                       key=lambda x: x[1],
                                       reverse=True)[:10]),
            'date_range': {
                'earliest': patents_df['patent_date'].min() if 'patent_date' in patents_df else None,
                'latest': patents_df['patent_date'].max() if 'patent_date' in patents_df else None
            }
        }

    def find_china_collaborations(self,
                                 italy_patents_df: pd.DataFrame) -> pd.DataFrame:
        """
        Find patents with Italy-China collaboration

        Args:
            italy_patents_df: DataFrame with Italian patents

        Returns:
            DataFrame with collaborative patents
        """
        # This would require additional API calls to get full inventor data
        # For now, we'll search for patents with both IT and CN inventors

        china_collabs = self.search_patents(
            inventor_country="CN",
            date_range=("2020-01-01", datetime.now().strftime("%Y-%m-%d")),
            limit=500
        )

        # Find overlaps (would need more sophisticated matching in production)
        if not italy_patents_df.empty and not china_collabs.empty:
            # Check for same assignees
            italy_assignees = set(italy_patents_df['assignee_organization'].dropna())
            china_assignees = set(china_collabs['assignee_organization'].dropna())
            common_assignees = italy_assignees.intersection(china_assignees)

            if common_assignees:
                print(f"Found {len(common_assignees)} organizations with patents in both Italy and China")
                return china_collabs[china_collabs['assignee_organization'].isin(common_assignees)]

        return pd.DataFrame()

    def save_results(self,
                    data: pd.DataFrame,
                    filename: str,
                    output_dir: str = "C:/Projects/OSINT - Foresight/data/collected/uspto"):
        """
        Save patent search results

        Args:
            data: DataFrame to save
            filename: Output filename
            output_dir: Output directory
        """
        os.makedirs(output_dir, exist_ok=True)

        # Save as CSV
        csv_path = os.path.join(output_dir, f"{filename}.csv")
        data.to_csv(csv_path, index=False)
        print(f"Saved {len(data)} records to {csv_path}")

        # Save as JSON for detailed analysis
        json_path = os.path.join(output_dir, f"{filename}.json")
        data.to_json(json_path, orient='records', indent=2)
        print(f"Saved JSON to {json_path}")

def test_connection():
    """Test USPTO API connection"""
    print("Testing USPTO API connection...")
    print("="*50)

    client = USPTOClient()

    # Test with a simple search
    print("\n1. Testing basic patent search...")
    test_patents = client.search_patents(
        inventor_country="IT",
        date_range=("2024-01-01", "2024-12-31"),
        limit=5
    )

    if not test_patents.empty:
        print(f"✓ Successfully retrieved {len(test_patents)} patents")
        print(f"\nSample patent:")
        if len(test_patents) > 0:
            first_patent = test_patents.iloc[0]
            print(f"  Number: {first_patent.get('patent_number', 'N/A')}")
            print(f"  Title: {first_patent.get('patent_title', 'N/A')[:80]}...")
            print(f"  Date: {first_patent.get('patent_date', 'N/A')}")
            print(f"  Assignee: {first_patent.get('assignee_organization', 'N/A')}")
    else:
        print("✗ No patents found or connection failed")

    # Test Italian companies
    print("\n2. Testing search for Italian defense companies...")
    leonardo_patents = client.search_patents(
        assignee="Leonardo",
        date_range=("2023-01-01", "2024-12-31"),
        limit=5
    )

    if not leonardo_patents.empty:
        print(f"✓ Found {len(leonardo_patents)} Leonardo patents")
    else:
        print("✗ No Leonardo patents found (this may be normal)")

    print("\n" + "="*50)
    print("USPTO API connection test complete!")

    return client

if __name__ == "__main__":
    test_connection()
