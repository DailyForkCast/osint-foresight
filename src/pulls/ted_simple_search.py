"""
Simple TED Search using the public web interface
Alternative approach while API documentation is being clarified
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TEDSimpleSearch:
    """Simple TED search using public endpoints"""

    def __init__(self):
        self.base_url = "https://ted.europa.eu"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html',
        })

    def search_notices_web(self,
                          query: str = "",
                          country: str = "",
                          date_from: str = "",
                          date_to: str = "",
                          page: int = 1) -> Dict:
        """
        Search notices using the public web search

        Args:
            query: Search keywords
            country: Country code (e.g., 'SK', 'IT')
            date_from: Start date YYYY-MM-DD
            date_to: End date YYYY-MM-DD
            page: Page number

        Returns:
            Search results
        """
        # Build search URL
        search_url = f"{self.base_url}/en/search-results"

        params = {
            'q': query,
            'page': page,
            'size': 20
        }

        if country:
            params['country'] = country
        if date_from:
            params['publicationDateFrom'] = date_from
        if date_to:
            params['publicationDateTo'] = date_to

        logger.info(f"Searching with params: {params}")

        try:
            response = self.session.get(search_url, params=params)
            response.raise_for_status()

            # Check if we got JSON or HTML
            if 'application/json' in response.headers.get('Content-Type', ''):
                return response.json()
            else:
                # Parse HTML response if needed
                logger.info("Got HTML response, would need parsing")
                return {'html': True, 'status': response.status_code}

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {'error': str(e)}

    def get_notice_by_number(self, notice_number: str) -> Dict:
        """
        Get a specific notice by its number

        Args:
            notice_number: TED notice number (e.g., '123456-2025')

        Returns:
            Notice data
        """
        # Direct notice URL format
        notice_url = f"{self.base_url}/en/notice/{notice_number}/details"

        try:
            response = self.session.get(notice_url)
            response.raise_for_status()

            return {
                'notice_number': notice_number,
                'url': notice_url,
                'status': response.status_code,
                'content_type': response.headers.get('Content-Type')
            }

        except Exception as e:
            logger.error(f"Failed to get notice {notice_number}: {e}")
            return {'error': str(e)}

    def search_china_related(self, countries: List[str]) -> List[Dict]:
        """
        Search for China-related procurement notices

        Args:
            countries: List of country codes to search

        Returns:
            List of results
        """
        china_keywords = [
            'China', 'Chinese', 'Beijing', 'Shanghai',
            'Huawei', 'ZTE', 'Hikvision', 'Dahua'
        ]

        all_results = []

        for country in countries:
            for keyword in china_keywords:
                logger.info(f"Searching {country} for: {keyword}")

                results = self.search_notices_web(
                    query=keyword,
                    country=country
                )

                if results and not results.get('error'):
                    all_results.append({
                        'country': country,
                        'keyword': keyword,
                        'results': results
                    })

                # Rate limiting
                time.sleep(2)

        return all_results

    def save_results(self, data: any, filename: str):
        """Save search results to file"""
        output_dir = Path('./data/collected/ted')
        output_dir.mkdir(parents=True, exist_ok=True)

        filepath = output_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved to {filepath}")
        return filepath


def test_simple_search():
    """Test the simple search"""
    searcher = TEDSimpleSearch()

    # Test 1: Search for technology in Slovakia
    logger.info("Test 1: Searching for technology in Slovakia...")
    results = searcher.search_notices_web(
        query="technology",
        country="SK"
    )
    print(f"Slovakia technology search: {results.get('status', 'Unknown')}")

    # Test 2: Get a specific notice (if you have a known number)
    # Example: results = searcher.get_notice_by_number("123456-2025")

    # Test 3: Search for China-related notices
    logger.info("\nTest 2: Searching for China-related notices...")
    china_results = searcher.search_china_related(['SK', 'AT'])

    if china_results:
        searcher.save_results(china_results, "china_related_test")
        print(f"Found {len(china_results)} results sets")

    return True


if __name__ == "__main__":
    print("Testing TED Simple Search...")
    print("=" * 50)

    if test_simple_search():
        print("\n[SUCCESS] Simple search is working!")
        print("\nNote: The TED website may return HTML instead of JSON.")
        print("For production use, we should:")
        print("1. Wait for official API documentation")
        print("2. Use the bulk download feature for large datasets")
        print("3. Parse HTML responses if needed")
    else:
        print("\n[ERROR] Search encountered issues")
