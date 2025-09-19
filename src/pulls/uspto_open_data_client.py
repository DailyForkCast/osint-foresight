#!/usr/bin/env python3
"""USPTO Open Data Portal Client

Uses the official USPTO Open Data Portal (data.uspto.gov) API
This is the current recommended API for accessing USPTO patent data.
"""

import os
import json
import time
import requests
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import urllib.parse

class USPTOOpenDataClient:
    """Client for USPTO Open Data Portal API"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize USPTO Open Data Portal client

        Args:
            api_key: Optional API key if required
        """
        # USPTO Open Data Portal endpoints
        self.base_url = "https://data.uspto.gov"
        self.api_base = f"{self.base_url}/api"

        # Patent File Wrapper API endpoint
        self.pfw_url = f"{self.base_url}/apis/patent-file-wrapper"

        self.api_key = api_key or os.getenv('USPTO_OPEN_DATA_API_KEY') or os.getenv('USPTO_API_KEY')

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Research/1.0 (Patent Analysis)',
            'Accept': 'application/json'
        })

        # Rate limiting based on USPTO limits
        # Weekly limits: 1.2M Patent File Wrapper, 5M Metadata
        # Conservative daily targets: ~171k and ~714k respectively
        self.rate_limit = 30  # requests per minute (conservative)
        self.last_request = 0
        self.min_interval = 60 / self.rate_limit

        # Usage tracking
        self.usage_stats = {
            'patent_file_wrapper_calls': 0,
            'metadata_calls': 0,
            'session_start': datetime.now()
        }

        # Load rate limit configuration
        try:
            config_path = Path("C:/Projects/OSINT - Foresight/config/uspto_rate_limits.json")
            with open(config_path, 'r') as f:
                self.rate_config = json.load(f)['uspto_open_data_portal']
        except Exception:
            # Fallback configuration
            self.rate_config = {
                'limits': {
                    'patent_file_wrapper_documents': {'limit': 1200000, 'period': 'weekly'},
                    'meta_data_retrievals': {'limit': 5000000, 'period': 'weekly'}
                },
                'safety_thresholds': {'warning_percent': 80, 'critical_percent': 95}
            }

    def _rate_limit(self):
        """Enforce rate limiting"""
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request = time.time()

    def _track_usage(self, call_type: str):
        """Track API usage for rate limit monitoring"""
        self.usage_stats[call_type] += 1

        # Check if we're approaching limits
        if call_type == 'patent_file_wrapper_calls':
            limit = self.rate_config['limits']['patent_file_wrapper_documents']['limit']
            used = self.usage_stats[call_type]
        else:
            limit = self.rate_config['limits']['meta_data_retrievals']['limit']
            used = self.usage_stats[call_type]

        usage_percent = (used / limit) * 100
        warning_threshold = self.rate_config['safety_thresholds']['warning_percent']
        critical_threshold = self.rate_config['safety_thresholds']['critical_percent']

        if usage_percent >= critical_threshold:
            print(f"⚠️ CRITICAL: {usage_percent:.1f}% of weekly {call_type} limit used!")
        elif usage_percent >= warning_threshold:
            print(f"⚠️ WARNING: {usage_percent:.1f}% of weekly {call_type} limit used")

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        pfw_limit = self.rate_config['limits']['patent_file_wrapper_documents']['limit']
        meta_limit = self.rate_config['limits']['meta_data_retrievals']['limit']

        return {
            'session_duration': str(datetime.now() - self.usage_stats['session_start']),
            'patent_file_wrapper': {
                'calls_made': self.usage_stats['patent_file_wrapper_calls'],
                'weekly_limit': pfw_limit,
                'remaining': pfw_limit - self.usage_stats['patent_file_wrapper_calls'],
                'percent_used': (self.usage_stats['patent_file_wrapper_calls'] / pfw_limit) * 100
            },
            'metadata_retrievals': {
                'calls_made': self.usage_stats['metadata_calls'],
                'weekly_limit': meta_limit,
                'remaining': meta_limit - self.usage_stats['metadata_calls'],
                'percent_used': (self.usage_stats['metadata_calls'] / meta_limit) * 100
            }
        }

    def search_patent_file_wrapper(self,
                                  application_number: Optional[str] = None,
                                  patent_number: Optional[str] = None) -> Dict[str, Any]:
        """Search Patent File Wrapper data

        Args:
            application_number: Application number to search
            patent_number: Patent number to search

        Returns:
            Patent file wrapper data
        """
        self._rate_limit()
        self._track_usage('patent_file_wrapper_calls')

        # Build search URL
        search_url = f"{self.pfw_url}/search"

        params = {}
        if application_number:
            params['applicationNumber'] = application_number
        elif patent_number:
            params['patentNumber'] = patent_number
        else:
            print("Error: Must provide either application_number or patent_number")
            return {}

        try:
            response = self.session.get(search_url, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error {response.status_code}: {response.text[:500]}")
                return {}

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {}

    def search_bulk_data(self, dataset: str = "patents",
                        format: str = "json",
                        date_range: Optional[str] = None) -> Dict[str, Any]:
        """Search bulk data downloads

        Args:
            dataset: Type of data (patents, trademarks, etc.)
            format: Data format (json, xml, csv)
            date_range: Optional date range filter

        Returns:
            Available bulk data information
        """
        self._rate_limit()

        # Bulk data endpoint
        bulk_url = f"{self.api_base}/bulk-data/{dataset}"

        params = {'format': format}
        if date_range:
            params['dateRange'] = date_range

        try:
            response = self.session.get(bulk_url, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                # Try alternative endpoint structure
                alt_url = f"{self.base_url}/data-download/{dataset}"
                response = self.session.get(alt_url, timeout=30)
                if response.status_code == 200:
                    return {'download_url': alt_url, 'status': 'redirect'}

            print(f"Status {response.status_code}: {response.text[:200]}")
            return {}

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return {}

    def get_patent_examination_data(self,
                                   start_date: str = "2024-01-01",
                                   end_date: Optional[str] = None) -> pd.DataFrame:
        """Get Patent Examination Research Dataset

        Args:
            start_date: Start date for data
            end_date: End date (defaults to today)

        Returns:
            DataFrame with patent examination data
        """
        self._rate_limit()
        self._track_usage('metadata_calls')

        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # PEDS endpoint
        peds_url = f"{self.api_base}/patent-examination"

        params = {
            'startDate': start_date,
            'endDate': end_date,
            'format': 'json'
        }

        try:
            response = self.session.get(peds_url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    print(f"Retrieved {len(df)} patent examination records")
                    return df
                elif isinstance(data, dict) and 'results' in data:
                    df = pd.DataFrame(data['results'])
                    print(f"Retrieved {len(df)} patent examination records")
                    return df

            print(f"No data retrieved. Status: {response.status_code}")
            return pd.DataFrame()

        except Exception as e:
            print(f"Error retrieving examination data: {e}")
            return pd.DataFrame()

    def search_patent_assignment(self,
                                assignee_name: Optional[str] = None,
                                assignor_name: Optional[str] = None,
                                patent_number: Optional[str] = None) -> Dict[str, Any]:
        """Search patent assignment data

        Args:
            assignee_name: Name of assignee (buyer)
            assignor_name: Name of assignor (seller)
            patent_number: Patent number

        Returns:
            Assignment data
        """
        self._rate_limit()

        # Assignment search endpoint
        assignment_url = f"{self.api_base}/patent-assignment/search"

        params = {}
        if assignee_name:
            params['assigneeName'] = assignee_name
        if assignor_name:
            params['assignorName'] = assignor_name
        if patent_number:
            params['patentNumber'] = patent_number

        if not params:
            print("Error: Must provide at least one search parameter")
            return {}

        try:
            response = self.session.get(assignment_url, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error {response.status_code}")
                return {}

        except Exception as e:
            print(f"Assignment search failed: {e}")
            return {}

    def test_connection(self) -> bool:
        """Test connection to USPTO Open Data Portal

        Returns:
            True if connection successful
        """
        print("Testing USPTO Open Data Portal connection...")
        print(f"Base URL: {self.base_url}")

        tests = [
            {
                "name": "Main API Status",
                "url": f"{self.base_url}/api/status",
                "method": "GET"
            },
            {
                "name": "Patent File Wrapper Search",
                "url": f"{self.pfw_url}/search",
                "method": "GET",
                "params": {"patentNumber": "10000000"}
            },
            {
                "name": "Data Home Page",
                "url": self.base_url,
                "method": "GET"
            }
        ]

        success_count = 0

        for test in tests:
            print(f"\n{test['name']}:")
            print("-" * 40)

            try:
                if test['method'] == "GET":
                    response = self.session.get(
                        test['url'],
                        params=test.get('params', {}),
                        timeout=10
                    )

                print(f"Status: {response.status_code}")

                if response.status_code == 200:
                    success_count += 1

                    # Check content type
                    content_type = response.headers.get('content-type', '')
                    if 'json' in content_type:
                        data = response.json()
                        print(f"[OK] Success - JSON response received")
                        if isinstance(data, dict):
                            print(f"  Keys: {list(data.keys())[:5]}")
                    elif 'html' in content_type:
                        print(f"[OK] Success - HTML page accessible")
                    else:
                        print(f"[OK] Success - Response received")

                elif response.status_code == 404:
                    print("[X] Endpoint not found")
                elif response.status_code == 403:
                    print("[X] Access denied - API key may be required")
                else:
                    print(f"[!] Unexpected status: {response.text[:100]}")

            except Exception as e:
                print(f"[X] Connection failed: {e}")

        print("\n" + "="*60)
        if success_count > 0:
            print(f"[OK] {success_count}/{len(tests)} tests passed")
            print("\nUSPTO Open Data Portal is accessible")
            print("\nAvailable resources:")
            print("  • Patent File Wrapper data")
            print("  • Patent Assignment data")
            print("  • Patent Examination data")
            print("  • Bulk data downloads")
            return True
        else:
            print("[X] All connection tests failed")
            return False

    def get_available_datasets(self) -> Dict[str, Any]:
        """Get list of available datasets from USPTO Open Data Portal

        Returns:
            Dictionary of available datasets
        """
        print("Fetching available USPTO datasets...")

        # Try to get dataset catalog
        catalog_url = f"{self.api_base}/catalog"

        try:
            response = self.session.get(catalog_url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass

        # Return known datasets if catalog unavailable
        known_datasets = {
            "patents": {
                "description": "Patent grant and application data",
                "formats": ["XML", "JSON", "CSV"],
                "bulk_download": True
            },
            "patent_file_wrapper": {
                "description": "Patent prosecution history and documents",
                "api": f"{self.pfw_url}/search",
                "searchable": True
            },
            "patent_assignment": {
                "description": "Patent ownership and transfer records",
                "searchable": True
            },
            "patent_examination": {
                "description": "Patent examination research dataset (PEDS)",
                "formats": ["CSV", "JSON"],
                "bulk_download": True
            },
            "trademarks": {
                "description": "Trademark registration data",
                "formats": ["XML", "JSON"],
                "bulk_download": True
            }
        }

        print(f"Known USPTO datasets: {len(known_datasets)}")
        for name, info in known_datasets.items():
            print(f"  • {name}: {info['description']}")

        return known_datasets


def main():
    """Test USPTO Open Data Portal client"""
    print("="*70)
    print("USPTO Open Data Portal Client")
    print("="*70)

    # Initialize client
    client = USPTOOpenDataClient()

    # Test connection
    if not client.test_connection():
        print("\n[!] Some connection issues detected")

    print("\n" + "-"*70)
    print("Available Datasets:")
    datasets = client.get_available_datasets()

    print("\n" + "-"*70)
    print("Testing Patent File Wrapper search...")

    # Test with a known patent
    pfw_data = client.search_patent_file_wrapper(patent_number="10000000")
    if pfw_data:
        print("[OK] Patent File Wrapper data retrieved")
        print(f"  Data keys: {list(pfw_data.keys())[:5]}")

    # Save configuration for future use
    config_file = Path("C:/Projects/OSINT - Foresight/config/uspto_config.json")
    config = {
        "api_base": client.base_url,
        "endpoints": {
            "patent_file_wrapper": f"{client.pfw_url}/search",
            "bulk_data": f"{client.api_base}/bulk-data",
            "patent_examination": f"{client.api_base}/patent-examination",
            "patent_assignment": f"{client.api_base}/patent-assignment"
        },
        "datasets": datasets,
        "last_tested": datetime.now().isoformat()
    }

    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\nConfiguration saved to {config_file}")

    # Show usage statistics
    print("\n" + "="*70)
    print("Usage Statistics")
    print("="*70)
    stats = client.get_usage_stats()
    print(f"Session Duration: {stats['session_duration']}")
    print(f"\nPatent File Wrapper API:")
    print(f"  Calls Made: {stats['patent_file_wrapper']['calls_made']:,}")
    print(f"  Weekly Limit: {stats['patent_file_wrapper']['weekly_limit']:,}")
    print(f"  Remaining: {stats['patent_file_wrapper']['remaining']:,}")
    print(f"  Usage: {stats['patent_file_wrapper']['percent_used']:.2f}%")
    print(f"\nMetadata Retrieval API:")
    print(f"  Calls Made: {stats['metadata_retrievals']['calls_made']:,}")
    print(f"  Weekly Limit: {stats['metadata_retrievals']['weekly_limit']:,}")
    print(f"  Remaining: {stats['metadata_retrievals']['remaining']:,}")
    print(f"  Usage: {stats['metadata_retrievals']['percent_used']:.2f}%")

    print("\n" + "="*70)
    print("USPTO Open Data Portal client ready!")
    print("\nKey endpoints configured:")
    print(f"  • Main portal: {client.base_url}")
    print(f"  • API base: {client.api_base}")
    print(f"  • Patent File Wrapper: {client.pfw_url}")
    print("\nRate Limits (Weekly):")
    print(f"  • Patent File Wrapper: 1,200,000 calls")
    print(f"  • Metadata Retrieval: 5,000,000 calls")
    print(f"  • Safe daily target: ~171k & ~714k respectively")
    print("="*70)


if __name__ == "__main__":
    main()
