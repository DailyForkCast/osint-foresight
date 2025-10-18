#!/usr/bin/env python3
"""
Selenium-Based National Procurement Portal Scraper
Handles JavaScript-rendered content for Czech, Polish, and Slovak procurement portals
"""

import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import hashlib

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SeleniumProcurementScraper:
    """Selenium-based scraper for JavaScript-heavy procurement portals"""

    def __init__(self, headless=False):
        self.output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/selenium_procurement")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.headless = headless
        self.driver = None
        self.wait = None

        # Priority Chinese companies
        self.chinese_companies = [
            'Huawei', 'ZTE', 'Lenovo', 'Hikvision', 'DJI',
            'Dahua', 'Xiaomi', 'Alibaba', 'BYD', 'CRRC',
            'TCL', 'OPPO', 'Vivo', 'OnePlus', 'BOE'
        ]

        # Country-specific terms
        self.china_terms = {
            'CZ': ['Čína', 'čínský', 'čínská', 'Peking', 'Šanghaj'],
            'PL': ['Chiny', 'chiński', 'chińska', 'Pekin', 'Szanghaj'],
            'SK': ['Čína', 'čínsky', 'čínska', 'Peking', 'Šanghaj']
        }

        self.results = {
            'CZ': [],
            'PL': [],
            'SK': []
        }

        self.stats = {
            'pages_loaded': 0,
            'searches_performed': 0,
            'results_found': 0,
            'ted_procurement_chinese_entities_found': 0,
            'errors': 0
        }

    def setup_driver(self):
        """Initialize Selenium WebDriver with Chrome"""
        logger.info("Setting up Chrome WebDriver...")

        chrome_options = Options()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        if self.headless:
            chrome_options.add_argument("--headless")
            logger.info("Running in headless mode")

        # Add user agent to appear more human-like
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        try:
            # Use webdriver-manager to automatically download correct ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)

            # Set page load timeout
            self.driver.set_page_load_timeout(30)

            logger.info("Chrome WebDriver initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            return False

    def close_driver(self):
        """Close Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("Chrome WebDriver closed")

    def scrape_czech_portal(self):
        """
        Scrape Czech NEN portal (nen.nipez.cz) using Selenium
        This portal has English interface
        """
        logger.info("\n" + "="*70)
        logger.info("CZECH PORTAL SELENIUM SCRAPING")
        logger.info("Portal: nen.nipez.cz")
        logger.info("="*70)

        base_url = "https://nen.nipez.cz"
        results = []

        try:
            # Navigate to English version
            self.driver.get(f"{base_url}/en/")
            time.sleep(3)
            self.stats['pages_loaded'] += 1

            logger.info("Czech portal loaded successfully")

            # Accept cookies if present
            try:
                cookie_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'OK')]")
                cookie_button.click()
                time.sleep(1)
            except NoSuchElementException:
                pass

            # Search for each Chinese company
            for company in self.chinese_companies[:5]:  # Start with top 5
                logger.info(f"\nSearching for: {company}")

                try:
                    # Find search box
                    search_box = self._find_search_box()
                    if not search_box:
                        logger.warning("Could not find search box")
                        continue

                    # Clear and enter search term
                    search_box.clear()
                    search_box.send_keys(company)
                    search_box.send_keys(Keys.RETURN)

                    # Wait for results to load
                    time.sleep(3)
                    self.stats['searches_performed'] += 1

                    # Extract results
                    page_results = self._extract_czech_results(company)

                    if page_results:
                        logger.info(f"  Found {len(page_results)} results for {company}")
                        results.extend(page_results)
                        self.stats['results_found'] += len(page_results)
                    else:
                        logger.info(f"  No results found for {company}")

                    # Return to search page
                    self.driver.get(f"{base_url}/en/")
                    time.sleep(2)

                except Exception as e:
                    logger.error(f"  Error searching for {company}: {e}")
                    self.stats['errors'] += 1

            # Also search for China-related terms
            for term in self.china_terms['CZ'][:2]:
                logger.info(f"\nSearching for China term: {term}")

                try:
                    search_box = self._find_search_box()
                    if search_box:
                        search_box.clear()
                        search_box.send_keys(term)
                        search_box.send_keys(Keys.RETURN)
                        time.sleep(3)

                        page_results = self._extract_czech_results(term)
                        if page_results:
                            results.extend(page_results)
                            self.stats['results_found'] += len(page_results)

                        self.driver.get(f"{base_url}/en/")
                        time.sleep(2)

                except Exception as e:
                    logger.error(f"  Error searching for {term}: {e}")

        except Exception as e:
            logger.error(f"Major error scraping Czech portal: {e}")

        self.results['CZ'] = results
        self._save_results('CZ', results)
        return results

    def _find_search_box(self):
        """Find search input box on the page"""
        search_selectors = [
            "//input[@type='search']",
            "//input[@type='text'][@placeholder]",
            "//input[contains(@name, 'search') or contains(@name, 'query') or contains(@name, 'q')]",
            "//input[contains(@id, 'search') or contains(@id, 'query')]",
            "//input[contains(@class, 'search')]"
        ]

        for selector in search_selectors:
            try:
                search_box = self.driver.find_element(By.XPATH, selector)
                if search_box.is_displayed():
                    return search_box
            except NoSuchElementException:
                continue

        return None

    def _extract_czech_results(self, search_term: str) -> List[Dict]:
        """Extract search results from Czech portal"""
        results = []

        # Wait for results to load
        try:
            # Common result container selectors
            result_selectors = [
                "//div[contains(@class, 'result') or contains(@class, 'item') or contains(@class, 'tender')]",
                "//article[contains(@class, 'result') or contains(@class, 'procurement')]",
                "//tr[contains(@class, 'result') or contains(@class, 'row')]",
                "//div[@class='search-result']",
                "//div[@data-result]"
            ]

            containers = []
            for selector in result_selectors:
                try:
                    containers = self.driver.find_elements(By.XPATH, selector)
                    if containers:
                        logger.info(f"  Found {len(containers)} result containers")
                        break
                except:
                    continue

            if not containers:
                # Try to find any substantial text blocks
                containers = self.driver.find_elements(By.XPATH, "//div[string-length(text()) > 100]")

            for container in containers[:20]:  # Limit to first 20 results
                try:
                    text = container.text.strip()
                    if len(text) < 20:  # Skip too short texts
                        continue

                    # Check for Chinese entity indicators
                    has_chinese = self._check_chinese_entity(text)

                    result = {
                        'search_term': search_term,
                        'text': text[:1000],  # Limit text length
                        'has_chinese_entity': has_chinese,
                        'portal': 'nen.nipez.cz',
                        'country': 'CZ',
                        'extracted_at': datetime.now().isoformat()
                    }

                    # Try to extract title
                    try:
                        title = container.find_element(By.XPATH, ".//h1 | .//h2 | .//h3 | .//h4 | .//a").text
                        result['title'] = title
                    except:
                        pass

                    # Try to extract link
                    try:
                        link = container.find_element(By.XPATH, ".//a[@href]").get_attribute('href')
                        result['url'] = link
                    except:
                        pass

                    # Try to extract value
                    value_pattern = re.compile(r'[\d\s,.]+\s*(EUR|CZK|Kč)', re.I)
                    value_match = value_pattern.search(text)
                    if value_match:
                        result['value'] = value_match.group(0)

                    # Generate unique ID
                    result['id'] = hashlib.md5(text.encode()).hexdigest()[:12]

                    results.append(result)

                    if has_chinese:
                        self.stats['ted_procurement_chinese_entities_found'] += 1
                        logger.info(f"    ✓ Found Chinese entity: {result.get('title', 'N/A')[:50]}")

                except Exception as e:
                    logger.debug(f"Error extracting result: {e}")

        except TimeoutException:
            logger.warning("Timeout waiting for results")
        except Exception as e:
            logger.error(f"Error extracting results: {e}")

        return results

    def scrape_polish_portal(self):
        """
        Scrape Polish e-Procurement portal using Selenium
        More complex due to Polish language
        """
        logger.info("\n" + "="*70)
        logger.info("POLISH PORTAL SELENIUM SCRAPING")
        logger.info("Portal: ezamowienia.gov.pl")
        logger.info("="*70)

        results = []

        try:
            # Try the main page
            self.driver.get("https://ezamowienia.gov.pl")
            time.sleep(3)
            self.stats['pages_loaded'] += 1

            logger.info("Polish portal loaded")

            # Accept cookies/consent if needed
            self._accept_cookies()

            # Search for Chinese companies
            for company in self.chinese_companies[:3]:  # Top 3 for Polish portal
                logger.info(f"\nSearching for: {company}")

                try:
                    # Try different search approaches
                    search_performed = self._perform_polish_search(company)

                    if search_performed:
                        time.sleep(3)
                        page_results = self._extract_polish_results(company)

                        if page_results:
                            logger.info(f"  Found {len(page_results)} results")
                            results.extend(page_results)
                            self.stats['results_found'] += len(page_results)

                        # Return to main page
                        self.driver.get("https://ezamowienia.gov.pl")
                        time.sleep(2)

                except Exception as e:
                    logger.error(f"  Error searching for {company}: {e}")
                    self.stats['errors'] += 1

        except Exception as e:
            logger.error(f"Major error scraping Polish portal: {e}")

        self.results['PL'] = results
        self._save_results('PL', results)
        return results

    def _perform_polish_search(self, term: str) -> bool:
        """Perform search on Polish portal"""
        try:
            # Try to find search box
            search_box = self._find_search_box()

            if not search_box:
                # Try navigation to search page
                search_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'search') or contains(@href, 'szukaj')]")
                if search_links:
                    search_links[0].click()
                    time.sleep(2)
                    search_box = self._find_search_box()

            if search_box:
                search_box.clear()
                search_box.send_keys(term)
                search_box.send_keys(Keys.RETURN)
                self.stats['searches_performed'] += 1
                return True

        except Exception as e:
            logger.debug(f"Search failed: {e}")

        return False

    def _extract_polish_results(self, search_term: str) -> List[Dict]:
        """Extract results from Polish portal"""
        results = []

        try:
            # Get all text containers
            containers = self.driver.find_elements(By.XPATH, "//div | //article | //tr")

            for container in containers[:30]:
                try:
                    text = container.text.strip()
                    if len(text) < 50:
                        continue

                    # Check for procurement-related keywords
                    if any(word in text.lower() for word in ['zamówienie', 'przetarg', 'oferta', 'kontrakt']):

                        has_chinese = self._check_chinese_entity(text)

                        result = {
                            'search_term': search_term,
                            'text': text[:1000],
                            'has_chinese_entity': has_chinese,
                            'portal': 'ezamowienia.gov.pl',
                            'country': 'PL',
                            'extracted_at': datetime.now().isoformat(),
                            'id': hashlib.md5(text.encode()).hexdigest()[:12]
                        }

                        results.append(result)

                        if has_chinese:
                            self.stats['ted_procurement_chinese_entities_found'] += 1

                except Exception as e:
                    logger.debug(f"Error extracting Polish result: {e}")

        except Exception as e:
            logger.error(f"Error extracting Polish results: {e}")

        return results

    def scrape_slovak_portal(self):
        """
        Scrape Slovak UVO portal using Selenium
        """
        logger.info("\n" + "="*70)
        logger.info("SLOVAK PORTAL SELENIUM SCRAPING")
        logger.info("Portal: uvo.gov.sk")
        logger.info("="*70)

        results = []

        try:
            self.driver.get("https://www.uvo.gov.sk")
            time.sleep(3)
            self.stats['pages_loaded'] += 1

            logger.info("Slovak portal loaded")

            # Accept cookies
            self._accept_cookies()

            # Search for companies
            for company in self.chinese_companies[:3]:
                logger.info(f"\nSearching for: {company}")

                try:
                    # Navigate to search
                    search_url = f"https://www.uvo.gov.sk/vyhladavanie?q={company}"
                    self.driver.get(search_url)
                    time.sleep(3)

                    page_results = self._extract_slovak_results(company)

                    if page_results:
                        logger.info(f"  Found {len(page_results)} results")
                        results.extend(page_results)
                        self.stats['results_found'] += len(page_results)

                except Exception as e:
                    logger.error(f"  Error: {e}")
                    self.stats['errors'] += 1

        except Exception as e:
            logger.error(f"Major error scraping Slovak portal: {e}")

        self.results['SK'] = results
        self._save_results('SK', results)
        return results

    def _extract_slovak_results(self, search_term: str) -> List[Dict]:
        """Extract results from Slovak portal"""
        results = []

        try:
            containers = self.driver.find_elements(By.XPATH, "//div | //article | //tr")

            for container in containers[:30]:
                try:
                    text = container.text.strip()
                    if len(text) < 50:
                        continue

                    # Check for Slovak procurement keywords
                    if any(word in text.lower() for word in ['verejné', 'obstarávanie', 'zákazka', 'tender']):

                        has_chinese = self._check_chinese_entity(text)

                        result = {
                            'search_term': search_term,
                            'text': text[:1000],
                            'has_chinese_entity': has_chinese,
                            'portal': 'uvo.gov.sk',
                            'country': 'SK',
                            'extracted_at': datetime.now().isoformat(),
                            'id': hashlib.md5(text.encode()).hexdigest()[:12]
                        }

                        results.append(result)

                        if has_chinese:
                            self.stats['ted_procurement_chinese_entities_found'] += 1

                except Exception as e:
                    logger.debug(f"Error extracting Slovak result: {e}")

        except Exception as e:
            logger.error(f"Error extracting Slovak results: {e}")

        return results

    def _check_chinese_entity(self, text: str) -> bool:
        """Check if text contains Chinese entity references"""
        text_lower = text.lower()

        # Check for Chinese companies
        for company in self.chinese_companies:
            if company.lower() in text_lower:
                return True

        # Check for China-related terms
        china_indicators = [
            'china', 'chinese', 'beijing', 'shanghai', 'shenzhen',
            'čína', 'čínský', 'čínská', 'chiny', 'chiński', 'chińska'
        ]

        for indicator in china_indicators:
            if indicator in text_lower:
                return True

        return False

    def _accept_cookies(self):
        """Accept cookies/consent dialogs"""
        try:
            # Common cookie accept button patterns
            cookie_xpaths = [
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'OK')]",
                "//button[contains(text(), 'Zgoda')]",  # Polish
                "//button[contains(text(), 'Souhlasím')]",  # Czech
                "//button[contains(text(), 'Súhlasím')]",  # Slovak
                "//button[contains(@class, 'accept')]",
                "//button[contains(@class, 'consent')]"
            ]

            for xpath in cookie_xpaths:
                try:
                    button = self.driver.find_element(By.XPATH, xpath)
                    if button.is_displayed():
                        button.click()
                        time.sleep(1)
                        break
                except:
                    continue

        except Exception as e:
            logger.debug(f"No cookie banner found or error: {e}")

    def _save_results(self, country: str, results: List[Dict]):
        """Save scraped results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{country}_selenium_results_{timestamp}.json"

        summary = {
            'country': country,
            'scrape_date': datetime.now().isoformat(),
            'total_results': len(results),
            'ted_procurement_chinese_entities_found': sum(1 for r in results if r.get('has_chinese_entity')),
            'search_terms': self.chinese_companies[:5],
            'results': results
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"\n✓ Saved {len(results)} results to {output_file.name}")
        logger.info(f"  Chinese entities found: {summary['ted_procurement_chinese_entities_found']}")

    def run_all_scrapers(self):
        """Run all portal scrapers"""
        logger.info("\n" + "="*70)
        logger.info("SELENIUM PROCUREMENT PORTAL SCRAPING")
        logger.info(f"Mode: {'Headless' if self.headless else 'Visible'}")
        logger.info("="*70)

        if not self.setup_driver():
            logger.error("Failed to setup WebDriver. Exiting.")
            return None

        try:
            # Run scrapers
            czech_results = self.scrape_czech_portal()
            polish_results = self.scrape_polish_portal()
            slovak_results = self.scrape_slovak_portal()

            # Generate summary
            self.generate_final_summary()

        finally:
            # Always close driver
            self.close_driver()

        return self.results

    def generate_final_summary(self):
        """Generate final summary of all scraping"""
        summary = {
            'scrape_date': datetime.now().isoformat(),
            'statistics': {
                'pages_loaded': self.stats['pages_loaded'],
                'searches_performed': self.stats['searches_performed'],
                'total_results_found': self.stats['results_found'],
                'chinese_entities_identified': self.stats['ted_procurement_chinese_entities_found'],
                'errors': self.stats['errors']
            },
            'by_country': {}
        }

        for country in ['CZ', 'PL', 'SK']:
            country_results = self.results[country]
            summary['by_country'][country] = {
                'total': len(country_results),
                'with_chinese_entities': sum(1 for r in country_results if r.get('has_chinese_entity'))
            }

        summary_file = self.output_dir / f"selenium_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        # Print summary
        print("\n" + "="*70)
        print("SELENIUM SCRAPING SUMMARY")
        print("="*70)
        print(f"Pages loaded: {self.stats['pages_loaded']}")
        print(f"Searches performed: {self.stats['searches_performed']}")
        print(f"Total results found: {self.stats['results_found']}")
        print(f"Chinese entities identified: {self.stats['ted_procurement_chinese_entities_found']}")
        print(f"Errors: {self.stats['errors']}")
        print("\nBy Country:")
        for country, data in summary['by_country'].items():
            print(f"  {country}: {data['total']} results, {data['with_chinese_entities']} with Chinese entities")
        print("="*70)

def main():
    """Main execution"""
    # Set headless=True for background execution, False to see browser
    scraper = SeleniumProcurementScraper(headless=True)

    try:
        results = scraper.run_all_scrapers()
        print("\n✅ Selenium scraping complete!")
        print("Check output directory for detailed results")

    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
