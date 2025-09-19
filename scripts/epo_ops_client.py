"""
EPO OPS (Open Patent Services) API Client for OSINT Foresight
Handles European Patent Office data retrieval
"""

import os
import time
import json
import base64
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv('.env.local')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EPOOPSClient:
    """Client for interacting with EPO OPS API v3.2"""

    def __init__(self):
        """Initialize EPO OPS client with OAuth2 authentication"""
        self.consumer_key = os.getenv('EPO_CONSUMER_KEY')
        self.consumer_secret = os.getenv('EPO_CONSUMER_SECRET')

        if not self.consumer_key or not self.consumer_secret:
            logger.warning("EPO credentials not found. Please add to .env.local file")

        # EPO OPS endpoints
        self.auth_url = "https://ops.epo.org/3.2/auth/accesstoken"
        self.base_url = "https://ops.epo.org/3.2/rest-services"

        # Token management
        self.access_token = None
        self.token_expiry = None

        # Rate limiting (EPO has strict limits)
        self.last_request_time = 0
        self.rate_limit_delay = 0.2  # 200ms between requests (5 req/sec max)

        # Output directory
        self.output_dir = Path('./data/collected/epo')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Session for connection pooling
        self.session = requests.Session()

    def _get_access_token(self) -> str:
        """
        Get OAuth2 access token using consumer key and secret
        EPO tokens are valid for 20 minutes
        """

        # Check if we have a valid token
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token

        # Create base64 encoded credentials
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "client_credentials"
        }

        try:
            response = self.session.post(self.auth_url, headers=headers, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data['access_token']
            # Token expires in 20 minutes, refresh at 19 minutes
            self.token_expiry = datetime.now() + timedelta(seconds=1140)

            logger.info("Successfully obtained EPO OPS access token")
            return self.access_token

        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            raise

    def search_patents(self,
                      query: Optional[str] = None,
                      applicant: Optional[str] = None,
                      inventor: Optional[str] = None,
                      title: Optional[str] = None,
                      cpc_class: Optional[str] = None,
                      country: Optional[str] = None,
                      date_from: Optional[str] = None,
                      date_to: Optional[str] = None,
                      max_results: int = 100) -> Dict:
        """
        Search for patents using EPO OPS

        Args:
            query: CQL query string
            applicant: Applicant name
            inventor: Inventor name
            title: Title keywords
            cpc_class: CPC classification
            country: Country code (e.g., 'IT')
            date_from: Start date (YYYYMMDD)
            date_to: End date (YYYYMMDD)
            max_results: Maximum number of results

        Returns:
            Search results
        """

        # Build CQL query
        cql_parts = []

        if applicant:
            cql_parts.append(f'pa="{applicant}"')

        if inventor:
            cql_parts.append(f'in="{inventor}"')

        if title:
            cql_parts.append(f'ti="{title}"')

        if cpc_class:
            cql_parts.append(f'cpc="{cpc_class}"')

        if country:
            cql_parts.append(f'pn="{country}"')

        if date_from and date_to:
            cql_parts.append(f'pd within "{date_from},{date_to}"')

        if query:
            cql_query = query
        else:
            cql_query = " and ".join(cql_parts)

        # Make request
        endpoint = f"{self.base_url}/published-data/search"
        params = {
            "q": cql_query,
            "Range": f"1-{max_results}"
        }

        return self._make_request(endpoint, params)

    def get_patent_details(self, patent_number: str, format: str = "epodoc") -> Dict:
        """
        Get detailed information for a specific patent

        Args:
            patent_number: Patent number
            format: Number format (epodoc, docdb, original)

        Returns:
            Patent details
        """

        endpoint = f"{self.base_url}/published-data/publication/{format}/{patent_number}"
        return self._make_request(endpoint)

    def get_patent_family(self, patent_number: str, format: str = "epodoc") -> Dict:
        """
        Get patent family information

        Args:
            patent_number: Patent number
            format: Number format

        Returns:
            Patent family data
        """

        endpoint = f"{self.base_url}/family/publication/{format}/{patent_number}"
        return self._make_request(endpoint)

    def search_italian_patents(self, date_from: str = "20200101", date_to: str = "20251231") -> Dict:
        """
        Search for Italian patents

        Args:
            date_from: Start date (YYYYMMDD)
            date_to: End date (YYYYMMDD)

        Returns:
            Italian patent results
        """

        logger.info(f"Searching Italian patents from {date_from} to {date_to}")

        # Search for Italian patents
        results = self.search_patents(
            country="IT",
            date_from=date_from,
            date_to=date_to,
            max_results=500
        )

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"italian_patents_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Saved Italian patent data to {output_file}")

        return results

    def search_leonardo_patents(self) -> Dict:
        """
        Search for Leonardo company patents

        Returns:
            Leonardo patent results
        """

        logger.info("Searching Leonardo patents...")

        # Try different variations of Leonardo name
        leonardo_names = [
            "Leonardo",
            "Leonardo S.p.A",
            "Leonardo SpA",
            "Finmeccanica",
            "Alenia",
            "AgustaWestland"
        ]

        all_results = []

        for name in leonardo_names:
            try:
                results = self.search_patents(
                    applicant=name,
                    max_results=100
                )
                if results:
                    all_results.append(results)
                time.sleep(self.rate_limit_delay)
            except Exception as e:
                logger.error(f"Error searching for {name}: {e}")

        # Save combined results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"leonardo_patents_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        logger.info(f"Saved Leonardo patent data to {output_file}")

        return {"searches": leonardo_names, "results": all_results}

    def search_italy_china_collaborations(self) -> Dict:
        """
        Search for patents with Italian and Chinese collaboration

        Returns:
            Collaboration patent results
        """

        logger.info("Searching Italy-China collaboration patents...")

        # Search for patents with Italian applicants and Chinese inventors
        results_it_cn = self.search_patents(
            query='pa="IT" and in="CN"',
            max_results=200
        )

        time.sleep(self.rate_limit_delay)

        # Search for patents with Chinese applicants and Italian inventors
        results_cn_it = self.search_patents(
            query='pa="CN" and in="IT"',
            max_results=200
        )

        results = {
            "italian_applicant_chinese_inventor": results_it_cn,
            "chinese_applicant_italian_inventor": results_cn_it
        }

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"italy_china_patents_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Saved Italy-China collaboration data to {output_file}")

        return results

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make authenticated request to EPO OPS API

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response
        """

        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)

        # Get access token
        token = self._get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        try:
            response = self.session.get(endpoint, headers=headers, params=params)
            response.raise_for_status()

            self.last_request_time = time.time()

            # EPO returns XML by default, try to parse JSON
            try:
                return response.json()
            except:
                # Return raw text if not JSON
                return {"raw_response": response.text}

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.error("Access forbidden. Check your API credentials and permissions.")
            elif e.response.status_code == 429:
                logger.error("Rate limit exceeded. Please wait before retrying.")
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
            raise

        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise


def test_connection():
    """Test EPO OPS API connection"""

    client = EPOOPSClient()

    if not client.consumer_key or not client.consumer_secret:
        print("\n[ERROR] EPO credentials not configured!")
        print("Please add to .env.local:")
        print("EPO_CONSUMER_KEY=your_consumer_key_here")
        print("EPO_CONSUMER_SECRET=your_consumer_secret_here")
        return False

    try:
        # Test authentication
        token = client._get_access_token()
        print(f"[SUCCESS] Successfully authenticated with EPO OPS")
        print(f"   Access token obtained: {token[:20]}...")

        # Test simple search
        print("\n[SEARCH] Testing search functionality...")
        results = client.search_patents(
            applicant="Leonardo",
            max_results=5
        )
        print(f"[SUCCESS] Search successful!")

        return True

    except Exception as e:
        print(f"\n[ERROR] Connection test failed: {e}")
        return False


if __name__ == "__main__":
    print("EPO OPS API Client for OSINT Foresight")
    print("=" * 50)

    # Test connection
    if test_connection():
        print("\n[SUCCESS] EPO OPS API is ready to use!")
        print("\nExample usage:")
        print("  client = EPOOPSClient()")
        print("  results = client.search_leonardo_patents()")
        print("  results = client.search_italy_china_collaborations()")
    else:
        print("\n[WARNING] Please configure EPO credentials in .env.local")
