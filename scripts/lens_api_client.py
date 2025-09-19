"""
The Lens API Client for OSINT Foresight
Handles patent and scholarly data retrieval with patent-to-science linkage
"""

import os
import time
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv('.env.local')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LensAPIClient:
    """Client for interacting with The Lens API"""

    def __init__(self):
        """Initialize The Lens API client"""
        self.api_token = os.getenv('LENS_API_TOKEN')
        self.base_url = "https://api.lens.org"

        if not self.api_token:
            logger.warning("LENS_API_TOKEN not found. Please add to .env.local file")

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        # Rate limiting: 50,000 requests/month for scholarly, 1,000 for patents
        self.rate_limit_delay = 0.1  # 100ms between requests

        # Output directory
        self.output_dir = Path('./data/collected/lens')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def search_patents(self,
                      query: Optional[str] = None,
                      applicant: Optional[str] = None,
                      inventor_country: Optional[str] = None,
                      applicant_country: Optional[str] = None,
                      cpc_code: Optional[str] = None,
                      date_from: Optional[str] = None,
                      date_to: Optional[str] = None,
                      size: int = 100,
                      offset: int = 0) -> Dict:
        """
        Search patents with various filters

        Args:
            query: Free text search
            applicant: Applicant/owner name (e.g., "Leonardo")
            inventor_country: Inventor country code (e.g., "IT")
            applicant_country: Applicant country code (e.g., "CN")
            cpc_code: Cooperative Patent Classification code
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            size: Number of results (max 1000)
            offset: Pagination offset

        Returns:
            API response with patent data
        """

        # Build query
        must_clauses = []

        if query:
            must_clauses.append({"match": {"_all": query}})

        if applicant:
            must_clauses.append({"match": {"applicant.name": applicant}})

        if inventor_country:
            must_clauses.append({"term": {"inventor.country": inventor_country}})

        if applicant_country:
            must_clauses.append({"term": {"applicant.country": applicant_country}})

        if cpc_code:
            must_clauses.append({"prefix": {"cpc.symbol": cpc_code}})

        if date_from or date_to:
            date_range = {}
            if date_from:
                date_range["gte"] = date_from
            if date_to:
                date_range["lte"] = date_to
            must_clauses.append({"range": {"date_published": date_range}})

        request_body = {
            "query": {
                "bool": {
                    "must": must_clauses
                }
            },
            "size": min(size, 1000),
            "from": offset
        }

        return self._make_request("patent/search", request_body)

    def search_scholarly(self,
                        query: Optional[str] = None,
                        author_country: Optional[str] = None,
                        institution: Optional[str] = None,
                        year_from: Optional[int] = None,
                        year_to: Optional[int] = None,
                        size: int = 100,
                        offset: int = 0) -> Dict:
        """
        Search scholarly literature

        Args:
            query: Free text search
            author_country: Author country code
            institution: Institution name
            year_from: Start year
            year_to: End year
            size: Number of results (max 1000)
            offset: Pagination offset

        Returns:
            API response with scholarly data
        """

        must_clauses = []

        if query:
            must_clauses.append({"match": {"_all": query}})

        if author_country:
            must_clauses.append({"term": {"author.affiliation.country": author_country}})

        if institution:
            must_clauses.append({"match": {"author.affiliation.name": institution}})

        if year_from or year_to:
            year_range = {}
            if year_from:
                year_range["gte"] = year_from
            if year_to:
                year_range["lte"] = year_to
            must_clauses.append({"range": {"year_published": year_range}})

        request_body = {
            "query": {
                "bool": {
                    "must": must_clauses
                }
            },
            "size": min(size, 1000),
            "from": offset
        }

        return self._make_request("scholarly/search", request_body)

    def get_patent_citations(self, patent_id: str) -> Dict:
        """
        Get scholarly works cited by a patent (PatCite functionality)

        Args:
            patent_id: Lens patent ID

        Returns:
            Citations data
        """

        request_body = {
            "query": {
                "term": {
                    "referenced_by_patent": patent_id
                }
            },
            "size": 100
        }

        return self._make_request("scholarly/search", request_body)

    def find_italy_china_collaborations(self) -> Dict:
        """
        Search for Italy-China patent collaborations

        Returns:
            Patents with both Italian and Chinese involvement
        """

        results = {}

        # Italian inventors with Chinese applicants
        results['it_inventor_cn_applicant'] = self.search_patents(
            inventor_country="IT",
            applicant_country="CN",
            size=500
        )

        # Chinese inventors with Italian applicants
        results['cn_inventor_it_applicant'] = self.search_patents(
            inventor_country="CN",
            applicant_country="IT",
            size=500
        )

        # Leonardo patents with any Chinese connection
        results['leonardo_china'] = self.search_patents(
            applicant="Leonardo",
            applicant_country="CN",
            size=500
        )

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"italy_china_collaborations_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Saved Italy-China collaboration data to {output_file}")

        return results

    def export_bulk_results(self,
                           query_type: str,
                           query_params: Dict,
                           max_records: int = 50000,
                           output_format: str = "json") -> str:
        """
        Export up to 50,000 records (registered user limit)

        Args:
            query_type: 'patent' or 'scholarly'
            query_params: Parameters for the search
            max_records: Maximum records to export (up to 50,000)
            output_format: 'json' or 'csv'

        Returns:
            Path to exported file
        """

        all_results = []
        batch_size = 1000  # API limit per request

        for offset in range(0, min(max_records, 50000), batch_size):
            logger.info(f"Fetching records {offset} to {offset + batch_size}")

            query_params['size'] = batch_size
            query_params['offset'] = offset

            if query_type == 'patent':
                response = self.search_patents(**query_params)
            else:
                response = self.search_scholarly(**query_params)

            if 'data' in response:
                all_results.extend(response['data'])

            # Check if we've retrieved all available results
            if len(response.get('data', [])) < batch_size:
                break

            time.sleep(self.rate_limit_delay)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"bulk_export_{query_type}_{timestamp}.{output_format}"

        if output_format == "json":
            with open(output_file, 'w') as f:
                json.dump(all_results, f, indent=2)
        else:
            # CSV export would require pandas or csv module
            logger.warning("CSV export not yet implemented")

        logger.info(f"Exported {len(all_results)} records to {output_file}")

        return str(output_file)

    def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """
        Make API request with error handling

        Args:
            endpoint: API endpoint
            data: Request body

        Returns:
            API response
        """

        if not self.api_token:
            raise ValueError("API token not configured. Please set LENS_API_TOKEN in .env.local")

        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error("Rate limit exceeded. Please wait before retrying.")
            elif e.response.status_code == 401:
                logger.error("Authentication failed. Please check your API token.")
            else:
                logger.error(f"HTTP error: {e}")
            raise

        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise


if __name__ == "__main__":
    # Example usage
    client = LensAPIClient()

    # Search for Leonardo patents
    print("Searching for Leonardo patents...")
    leonardo_patents = client.search_patents(
        applicant="Leonardo",
        date_from="2020-01-01",
        size=10
    )

    if leonardo_patents:
        print(f"Found {leonardo_patents.get('total', 0)} Leonardo patents")

    # Find Italy-China collaborations
    print("\nSearching for Italy-China collaborations...")
    collaborations = client.find_italy_china_collaborations()

    print("\nSetup complete! Add LENS_API_TOKEN to .env.local to enable API access.")
