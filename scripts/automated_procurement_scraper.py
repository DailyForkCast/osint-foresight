#!/usr/bin/env python3
"""
Automated National Procurement Portal Scraper
Searches Czech, Polish, and Slovak procurement portals for Chinese entities
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
from urllib.parse import urlencode, quote, urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutomatedProcurementScraper:
    """Automated scraper for national procurement portals"""

    def __init__(self, use_selenium=False):
        self.output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/national_procurement_automated")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.use_selenium = use_selenium
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Chinese companies to search
        self.priority_companies = [
            'Huawei', 'ZTE', 'Lenovo', 'Hikvision', 'DJI',
            'Dahua', 'Xiaomi', 'Alibaba', 'BYD', 'CRRC'
        ]

        self.results = {
            'CZ': [],
            'PL': [],
            'SK': []
        }

        self.stats = {
            'total_searches': 0,
            'contracts_found': 0,
            'chinese_contracts': 0,
            'errors': 0
        }

    def setup_selenium(self):
        """Setup Selenium WebDriver for JavaScript-heavy sites"""
        if not self.use_selenium:
            return

        try:
            # Try Chrome first
            from selenium.webdriver.chrome.options import Options
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')

            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Selenium WebDriver initialized (Chrome)")
        except Exception as e:
            logger.error(f"Could not initialize Selenium: {e}")
            logger.info("Falling back to requests-based scraping")
            self.use_selenium = False

    def cleanup_selenium(self):
        """Clean up Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver closed")

    def search_czech_portal_automated(self):
        """
        Automated search of Czech NEN portal (nen.nipez.cz)
        This portal has English interface and better structure
        """
        logger.info("="*70)
        logger.info("AUTOMATED CZECH PORTAL SEARCH")
        logger.info("Portal: nen.nipez.cz (English interface)")
        logger.info("="*70)

        base_url = "https://nen.nipez.cz"
        search_url = f"{base_url}/en/search"

        country_results = []

        for company in self.priority_companies:
            logger.info(f"\nSearching for: {company}")

            try:
                # Try direct HTTP request first
                search_params = {
                    'q': company,
                    'type': 'all',
                    'status': 'all',
                    'dateFrom': '2019-01-01',
                    'dateTo': '2025-12-31'
                }

                response = self.session.get(search_url, params=search_params, timeout=30)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Look for result containers (adjust selectors based on actual HTML)
                    results = self._parse_czech_results(soup, company)

                    if results:
                        logger.info(f"  Found {len(results)} potential contracts")
                        country_results.extend(results)
                        self.stats['contracts_found'] += len(results)
                    else:
                        logger.info(f"  No results found for {company}")

                else:
                    logger.warning(f"  HTTP {response.status_code} for {company}")

                self.stats['total_searches'] += 1
                time.sleep(2)  # Rate limiting

            except requests.RequestException as e:
                logger.error(f"  Request error for {company}: {e}")
                self.stats['errors'] += 1

                # Try Selenium if requests fail
                if self.use_selenium:
                    results = self._search_with_selenium_czech(company)
                    if results:
                        country_results.extend(results)

        self.results['CZ'] = country_results
        self._save_results('CZ', country_results)

        return country_results

    def _parse_czech_results(self, soup: BeautifulSoup, search_term: str) -> List[Dict]:
        """Parse Czech portal search results"""
        parsed_results = []

        # Common patterns for procurement results
        # These selectors would need to be adjusted based on actual HTML structure

        # Try different possible result containers
        result_containers = soup.find_all(['div', 'article', 'li'], class_=re.compile(
            r'(result|tender|contract|procurement|item)', re.I
        ))

        if not result_containers:
            # Try table rows
            result_containers = soup.select('table tbody tr')

        for container in result_containers[:50]:  # Limit to first 50 results
            try:
                result = self._extract_contract_info(container, search_term)
                if result:
                    parsed_results.append(result)
            except Exception as e:
                logger.debug(f"Could not parse result container: {e}")

        return parsed_results

    def _extract_contract_info(self, container, search_term: str) -> Optional[Dict]:
        """Extract contract information from HTML container"""
        try:
            # Extract text content
            text_content = container.get_text(separator=' ', strip=True)

            # Skip if no meaningful content
            if len(text_content) < 20:
                return None

            # Look for Chinese entity indicators
            chinese_indicators = [
                'Huawei', 'ZTE', 'Lenovo', 'Hikvision', 'DJI', 'Dahua',
                'Xiaomi', 'Alibaba', 'China', 'Chinese', 'Beijing', 'Shanghai'
            ]

            has_chinese_entity = any(indicator.lower() in text_content.lower()
                                    for indicator in chinese_indicators)

            # Try to extract structured data
            result = {
                'search_term': search_term,
                'text_content': text_content[:500],  # First 500 chars
                'has_chinese_entity': has_chinese_entity,
                'extracted_at': datetime.now().isoformat()
            }

            # Try to extract specific fields
            # Title
            title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'a'], class_=re.compile(r'title', re.I))
            if title_elem:
                result['title'] = title_elem.get_text(strip=True)

            # Contract value
            value_pattern = re.compile(r'(\d+[\s,\.]\d+)\s*(EUR|CZK|USD)', re.I)
            value_match = value_pattern.search(text_content)
            if value_match:
                result['value'] = value_match.group(0)

            # Date
            date_pattern = re.compile(r'\d{1,2}[\./-]\d{1,2}[\./-]\d{2,4}')
            date_match = date_pattern.search(text_content)
            if date_match:
                result['date'] = date_match.group(0)

            # URL/Link
            link_elem = container.find('a', href=True)
            if link_elem:
                result['url'] = urljoin('https://nen.nipez.cz', link_elem['href'])

            # Generate unique ID
            result['id'] = hashlib.md5(text_content.encode()).hexdigest()[:12]

            if has_chinese_entity:
                self.stats['chinese_contracts'] += 1
                logger.info(f"    ✓ Found Chinese entity in contract: {result.get('title', 'N/A')[:50]}")

            return result

        except Exception as e:
            logger.debug(f"Error extracting contract info: {e}")
            return None

    def _search_with_selenium_czech(self, company: str) -> List[Dict]:
        """Fallback Selenium-based search for Czech portal"""
        if not self.driver:
            self.setup_selenium()
            if not self.driver:
                return []

        results = []

        try:
            logger.info(f"  Using Selenium for {company}")

            # Navigate to search page
            self.driver.get(f"https://nen.nipez.cz/en/search?q={quote(company)}")

            # Wait for results to load
            wait = WebDriverWait(self.driver, 10)

            # Wait for result containers (adjust selector as needed)
            results_loaded = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".results, .search-results, table"))
            )

            # Parse the loaded page
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            results = self._parse_czech_results(soup, company)

        except TimeoutException:
            logger.warning(f"  Timeout waiting for results for {company}")
        except Exception as e:
            logger.error(f"  Selenium error for {company}: {e}")

        return results

    def search_poland_portal_automated(self):
        """
        Automated search of Polish e-Procurement portal
        More challenging due to Polish language interface
        """
        logger.info("="*70)
        logger.info("AUTOMATED POLISH PORTAL SEARCH")
        logger.info("Portal: ezamowienia.gov.pl")
        logger.info("="*70)

        base_url = "https://ezamowienia.gov.pl"
        country_results = []

        # Polish translations for search
        polish_search_terms = {
            'Huawei': 'Huawei',
            'ZTE': 'ZTE',
            'Lenovo': 'Lenovo',
            'China': 'Chiny',
            'Chinese': 'Chiński'
        }

        for company in self.priority_companies[:5]:  # Start with top 5
            logger.info(f"\nSearching Polish portal for: {company}")

            try:
                # Construct search URL (hypothetical structure)
                search_url = f"{base_url}/mp-srv/search/list"

                search_data = {
                    'searchText': company,
                    'dateFrom': '01.01.2019',
                    'dateTo': '31.12.2025',
                    'searchType': 'all'
                }

                response = self.session.post(search_url, data=search_data, timeout=30)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    results = self._parse_polish_results(soup, company)

                    if results:
                        logger.info(f"  Found {len(results)} results")
                        country_results.extend(results)
                        self.stats['contracts_found'] += len(results)

                else:
                    logger.warning(f"  HTTP {response.status_code}")

                self.stats['total_searches'] += 1
                time.sleep(3)  # Longer delay for Polish portal

            except Exception as e:
                logger.error(f"  Error searching for {company}: {e}")
                self.stats['errors'] += 1

        self.results['PL'] = country_results
        self._save_results('PL', country_results)

        return country_results

    def _parse_polish_results(self, soup: BeautifulSoup, search_term: str) -> List[Dict]:
        """Parse Polish portal results"""
        parsed_results = []

        # Look for result containers
        result_containers = soup.find_all(['div', 'tr'], class_=re.compile(
            r'(ogloszenie|przetarg|zamowienie)', re.I  # Polish: announcement, tender, order
        ))

        for container in result_containers[:30]:
            try:
                text_content = container.get_text(separator=' ', strip=True)

                # Check for Chinese entities (including Polish terms)
                chinese_indicators = [
                    'Huawei', 'ZTE', 'Lenovo', 'DJI', 'Chiny', 'Chiński', 'Chińska'
                ]

                has_chinese = any(ind.lower() in text_content.lower()
                                for ind in chinese_indicators)

                if text_content:
                    result = {
                        'search_term': search_term,
                        'text_content': text_content[:500],
                        'has_chinese_entity': has_chinese,
                        'country': 'PL',
                        'portal': 'ezamowienia.gov.pl',
                        'extracted_at': datetime.now().isoformat()
                    }

                    if has_chinese:
                        self.stats['chinese_contracts'] += 1
                        logger.info(f"    ✓ Found Chinese reference")

                    parsed_results.append(result)

            except Exception as e:
                logger.debug(f"Parse error: {e}")

        return parsed_results

    def search_slovakia_portal_automated(self):
        """
        Automated search of Slovak UVO portal
        Public database with search functionality
        """
        logger.info("="*70)
        logger.info("AUTOMATED SLOVAK PORTAL SEARCH")
        logger.info("Portal: uvo.gov.sk")
        logger.info("="*70)

        base_url = "https://www.uvo.gov.sk"
        search_url = f"{base_url}/vyhladavanie-zakaziek"

        country_results = []

        for company in self.priority_companies[:5]:
            logger.info(f"\nSearching Slovak portal for: {company}")

            try:
                # Slovak portal search parameters
                params = {
                    'query': company,
                    'from': '2019',
                    'to': '2025'
                }

                response = self.session.get(search_url, params=params, timeout=30)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    results = self._parse_slovak_results(soup, company)

                    if results:
                        logger.info(f"  Found {len(results)} results")
                        country_results.extend(results)
                        self.stats['contracts_found'] += len(results)

                self.stats['total_searches'] += 1
                time.sleep(2)

            except Exception as e:
                logger.error(f"  Error: {e}")
                self.stats['errors'] += 1

        self.results['SK'] = country_results
        self._save_results('SK', country_results)

        return country_results

    def _parse_slovak_results(self, soup: BeautifulSoup, search_term: str) -> List[Dict]:
        """Parse Slovak portal results"""
        parsed_results = []

        # Slovak result patterns
        containers = soup.find_all(['div', 'article'], class_=re.compile(
            r'(vysledok|zakazka|tender)', re.I  # Slovak: result, order, tender
        ))

        for container in containers[:30]:
            try:
                text = container.get_text(separator=' ', strip=True)

                # Check for Chinese entities
                chinese_indicators = [
                    'Huawei', 'ZTE', 'Lenovo', 'Čína', 'Čínsky', 'čínsk'
                ]

                has_chinese = any(ind.lower() in text.lower()
                                for ind in chinese_indicators)

                if text:
                    result = {
                        'search_term': search_term,
                        'text_content': text[:500],
                        'has_chinese_entity': has_chinese,
                        'country': 'SK',
                        'portal': 'uvo.gov.sk',
                        'extracted_at': datetime.now().isoformat()
                    }

                    if has_chinese:
                        self.stats['chinese_contracts'] += 1

                    parsed_results.append(result)

            except Exception as e:
                logger.debug(f"Parse error: {e}")

        return parsed_results

    def _save_results(self, country: str, results: List[Dict]):
        """Save search results for a country"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{country}_automated_results_{timestamp}.json"

        summary = {
            'country': country,
            'search_date': datetime.now().isoformat(),
            'total_results': len(results),
            'ted_procurement_chinese_entities_found': sum(1 for r in results if r.get('has_chinese_entity')),
            'companies_searched': self.priority_companies[:5],
            'results': results
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"\n✓ Saved {len(results)} results to {output_file.name}")
        logger.info(f"  Chinese entities found: {summary['ted_procurement_chinese_entities_found']}")

    def run_all_automated_searches(self):
        """Run automated searches for all three countries"""
        logger.info("\n" + "="*70)
        logger.info("STARTING AUTOMATED PROCUREMENT SEARCHES")
        logger.info(f"Countries: Czech Republic, Poland, Slovakia")
        logger.info(f"Companies: {', '.join(self.priority_companies[:5])}")
        logger.info("="*70)

        # Setup Selenium if needed
        if self.use_selenium:
            self.setup_selenium()

        # Run searches
        czech_results = self.search_czech_portal_automated()
        polish_results = self.search_poland_portal_automated()
        slovak_results = self.search_slovakia_portal_automated()

        # Generate final summary
        self.generate_final_summary()

        # Cleanup
        if self.use_selenium:
            self.cleanup_selenium()

        return self.results

    def generate_final_summary(self):
        """Generate comprehensive summary of all searches"""
        summary = {
            'search_date': datetime.now().isoformat(),
            'statistics': {
                'total_searches': self.stats['total_searches'],
                'total_contracts_found': self.stats['contracts_found'],
                'chinese_contracts_identified': self.stats['chinese_contracts'],
                'errors': self.stats['errors']
            },
            'by_country': {
                'CZ': {
                    'total': len(self.results['CZ']),
                    'chinese': sum(1 for r in self.results['CZ'] if r.get('has_chinese_entity'))
                },
                'PL': {
                    'total': len(self.results['PL']),
                    'chinese': sum(1 for r in self.results['PL'] if r.get('has_chinese_entity'))
                },
                'SK': {
                    'total': len(self.results['SK']),
                    'chinese': sum(1 for r in self.results['SK'] if r.get('has_chinese_entity'))
                }
            },
            'companies_searched': self.priority_companies[:5],
            'method': 'automated_scraping'
        }

        summary_file = self.output_dir / f"automated_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        # Print summary
        print("\n" + "="*70)
        print("AUTOMATED SEARCH SUMMARY")
        print("="*70)
        print(f"Total searches performed: {self.stats['total_searches']}")
        print(f"Total results found: {self.stats['contracts_found']}")
        print(f"Chinese entities identified: {self.stats['chinese_contracts']}")
        print(f"Errors encountered: {self.stats['errors']}")
        print("\nBy Country:")
        for country in ['CZ', 'PL', 'SK']:
            total = len(self.results[country])
            chinese = sum(1 for r in self.results[country] if r.get('has_chinese_entity'))
            print(f"  {country}: {total} results, {chinese} with Chinese entities")
        print("="*70)

def main():
    """Main execution"""
    # Initialize scraper
    # Set use_selenium=True if you have Selenium/Chrome installed
    scraper = AutomatedProcurementScraper(use_selenium=False)

    # Run automated searches
    results = scraper.run_all_automated_searches()

    print("\n✅ Automated search complete!")
    print("Check the output directory for detailed results:")
    print("  data/processed/national_procurement_automated/")

if __name__ == "__main__":
    main()
