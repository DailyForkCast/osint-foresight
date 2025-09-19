"""
TED Europe API Client for OSINT Foresight
Handles authentication and data retrieval from TED API
"""

import os
import time
import json
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


class TEDAPIClient:
    """Client for interacting with TED Europe API"""

    def __init__(self):
        """Initialize TED API client with configuration from environment"""
        self.api_key = os.getenv('TED_API_KEY')
        self.base_url = os.getenv('TED_API_BASE_URL', 'https://api.ted.europa.eu')
        self.api_version = os.getenv('TED_API_VERSION', 'v3')
        self.environment = os.getenv('TED_ENVIRONMENT', 'preview')
        self.rate_limit = float(os.getenv('TED_RATE_LIMIT', '1'))

        # Note: Search API doesn't require authentication
        # API key is for other endpoints (submit, validate, etc.)

        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'OSINT-Foresight/1.0'
        })

        # Add auth header only for non-search endpoints
        if self.api_key and self.api_key != 'your_api_key_here':
            self.auth_headers = {'Authorization': f'Bearer {self.api_key}'}
        else:
            self.auth_headers = {}

        # Cache directory
        self.cache_dir = Path('./data/cache/ted')
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Rate limiting
        self.last_request_time = 0

    def _rate_limit(self):
        """Implement rate limiting"""
        elapsed = time.time() - self.last_request_time
        sleep_time = (1.0 / self.rate_limit) - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with error handling and rate limiting"""
        self._rate_limit()

        url = f"{self.base_url}/{self.api_version}/{endpoint}"

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning("Rate limit hit, backing off...")
                time.sleep(10)
                return self._make_request(endpoint, params)
            else:
                logger.error(f"HTTP error: {e}")
                raise
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

    def search_notices(self,
                      query: Optional[str] = None,
                      country_codes: Optional[List[str]] = None,
                      cpv_codes: Optional[List[str]] = None,
                      date_from: Optional[str] = None,
                      date_to: Optional[str] = None,
                      notice_type: Optional[str] = None,
                      page: int = 1,
                      page_size: int = 100) -> Dict:
        """
        Search for procurement notices

        Args:
            query: Free text search query
            country_codes: List of country codes (e.g., ['IT', 'DE'])
            cpv_codes: List of CPV codes for categories
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            notice_type: Type of notice
            page: Page number
            page_size: Results per page

        Returns:
            Search results dictionary
        """
        params = {
            'page': page,
            'pageSize': page_size
        }

        if query:
            params['q'] = query
        if country_codes:
            params['country'] = ','.join(country_codes)
        if cpv_codes:
            params['cpv'] = ','.join(cpv_codes)
        if date_from:
            params['dateFrom'] = date_from
        if date_to:
            params['dateTo'] = date_to
        if notice_type:
            params['noticeType'] = notice_type

        logger.info(f"Searching notices with params: {params}")
        return self._make_request('notices/search', params)

    def get_notice(self, notice_id: str) -> Dict:
        """
        Get detailed information about a specific notice

        Args:
            notice_id: TED notice identifier

        Returns:
            Notice details dictionary
        """
        logger.info(f"Fetching notice: {notice_id}")
        return self._make_request(f'notices/{notice_id}')

    def search_organizations(self,
                           name: Optional[str] = None,
                           country: Optional[str] = None,
                           organization_type: Optional[str] = None) -> Dict:
        """
        Search for organizations in TED database

        Args:
            name: Organization name or partial name
            country: Country code
            organization_type: Type of organization

        Returns:
            Organization search results
        """
        params = {}
        if name:
            params['name'] = name
        if country:
            params['country'] = country
        if organization_type:
            params['type'] = organization_type

        logger.info(f"Searching organizations: {params}")
        return self._make_request('organizations/search', params)

    def get_china_related_notices(self,
                                 countries: List[str],
                                 keywords: List[str] = None,
                                 date_from: str = None) -> List[Dict]:
        """
        Search for notices potentially involving Chinese entities

        Args:
            countries: List of target country codes
            keywords: China-related keywords
            date_from: Start date for search

        Returns:
            List of relevant notices
        """
        if keywords is None:
            keywords = [
                'China', 'Chinese', 'Beijing', 'Shanghai', 'Shenzhen',
                'Huawei', 'ZTE', 'Alibaba', 'Tencent', 'Baidu',
                'Belt and Road', 'BRI', 'Silk Road'
            ]

        all_results = []

        for keyword in keywords:
            logger.info(f"Searching for keyword: {keyword}")
            try:
                results = self.search_notices(
                    query=keyword,
                    country_codes=countries,
                    date_from=date_from,
                    page_size=100
                )
                if results.get('results'):
                    all_results.extend(results['results'])
            except Exception as e:
                logger.error(f"Error searching for {keyword}: {e}")
                continue

        # Deduplicate by notice ID
        unique_notices = {n['id']: n for n in all_results}
        return list(unique_notices.values())

    def get_technology_procurements(self,
                                   countries: List[str],
                                   tech_categories: Optional[List[str]] = None,
                                   date_from: str = None) -> List[Dict]:
        """
        Get technology-related procurement notices

        Args:
            countries: List of country codes
            tech_categories: Technology CPV codes
            date_from: Start date

        Returns:
            Technology procurement notices
        """
        # Default technology CPV codes if not provided
        if tech_categories is None:
            tech_categories = [
                '30000000',  # Office and computing machinery
                '32000000',  # Radio, television, communication
                '48000000',  # Software and systems
                '72000000',  # IT services
                '73000000',  # Research and development
            ]

        all_results = []

        for country in countries:
            logger.info(f"Fetching tech procurements for {country}")
            try:
                results = self.search_notices(
                    country_codes=[country],
                    cpv_codes=tech_categories,
                    date_from=date_from,
                    page_size=100
                )
                if results.get('results'):
                    all_results.extend(results['results'])
            except Exception as e:
                logger.error(f"Error fetching for {country}: {e}")
                continue

        return all_results

    def save_results(self, data: Any, filename: str, subdir: str = 'notices'):
        """Save results to JSON file"""
        output_dir = Path(f'./data/collected/ted/{subdir}')
        output_dir.mkdir(parents=True, exist_ok=True)

        filepath = output_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved results to {filepath}")
        return filepath


def test_connection():
    """Test TED API connection"""
    try:
        client = TEDAPIClient()

        # Test search with minimal parameters
        logger.info("Testing TED API connection...")
        results = client.search_notices(
            country_codes=['SK'],  # Slovakia as test
            page_size=1
        )

        if results:
            logger.info("✅ TED API connection successful!")
            logger.info(f"Found {results.get('totalResults', 0)} total results")
            return True
        else:
            logger.error("❌ No response from TED API")
            return False

    except Exception as e:
        logger.error(f"❌ TED API connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test the connection
    if test_connection():
        print("\nTED API client is ready to use!")
        print("\nNext steps:")
        print("1. Replace 'your_api_key_here' in .env.local with your actual API key")
        print("2. Run: python src/pulls/ted_collection.py to start collecting data")
    else:
        print("\nPlease check your API key in .env.local")
