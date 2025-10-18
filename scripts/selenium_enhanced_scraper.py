#!/usr/bin/env python3
"""
Enhanced Selenium-based scraper for Eastern European procurement portals.
Properly waits for JavaScript content to load and extracts actual results.
"""

import logging
import json
import time
import re
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedProcurementScraper:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.results = []
        self.stats = {
            'pages_loaded': 0,
            'searches_performed': 0,
            'results_found': 0,
            'chinese_entities': 0,
            'errors': 0
        }

        # Chinese company patterns with word boundaries
        self.chinese_patterns = [
            r'\bhuawei\b', r'\bzte\b', r'\blenovo\b', r'\bhikvision\b',
            r'\bdji\b', r'\bdahua\b', r'\bxiaomi\b', r'\balibaba\b',
            r'\bbyd\b', r'\bcrrc\b', r'\btcl\b', r'\bhaier\b',
            r'\bchina\b', r'\bchinese\b', r'\bbeijing\b', r'\bshanghai\b',
            r'\bshenzhen\b', r'\bguangzhou\b', r'\bhong kong\b',
            r"\bpeople's republic of china\b", r'\bprc\b',
            r'\bsinopec\b', r'\bsinochem\b', r'\bsmic\b', r'\bcatl\b',
            r'\bnio\b', r'\boppo\b', r'\bvivo\b', r'\bboe\b',
            r'\bcomac\b', r'\bcosco\b', r'\bweibo\b', r'\bsina\b'
        ]

    def setup_driver(self):
        """Initialize Chrome WebDriver with anti-detection measures"""
        try:
            logger.info("Setting up Chrome WebDriver...")
            chrome_options = Options()

            if self.headless:
                logger.info("Running in headless mode")
                chrome_options.add_argument("--headless")

            # Anti-detection measures
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)

            logger.info("Chrome WebDriver initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to setup Chrome WebDriver: {e}")
            return False

    def check_chinese_entity(self, text):
        """Check if text contains Chinese entity references"""
        if not text:
            return False
        text_lower = text.lower()
        for pattern in self.chinese_patterns:
            if re.search(pattern, text_lower):
                return True
        return False

    def scrape_czech_portal_enhanced(self):
        """Enhanced scraping for Czech portal with proper result extraction"""
        portal_url = "https://nen.nipez.cz/en/"
        logger.info("\n" + "="*70)
        logger.info("CZECH PORTAL ENHANCED SCRAPING")
        logger.info(f"Portal: {portal_url}")
        logger.info("="*70)

        try:
            self.driver.get(portal_url)
            time.sleep(3)
            self.stats['pages_loaded'] += 1
            logger.info("Czech portal loaded")

            # Accept cookies if present
            try:
                cookie_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Souhlasím')]")
                cookie_button.click()
                time.sleep(1)
            except:
                pass

            # Search terms
            search_terms = ['Huawei', 'ZTE', 'Lenovo', 'Hikvision', 'DJI', 'China', 'Chinese']

            for term in search_terms:
                logger.info(f"\nSearching for: {term}")

                try:
                    # Method 1: Try the main search box
                    search_selectors = [
                        "input[type='search']",
                        "input[placeholder*='Search']",
                        "input[placeholder*='Hledat']",
                        "#search-input",
                        "input[name='q']",
                        "input[name='search']"
                    ]

                    search_box = None
                    for selector in search_selectors:
                        try:
                            search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                            break
                        except:
                            continue

                    if not search_box:
                        # Method 2: Navigate directly to search URL
                        search_url = f"{portal_url}search?q={term}"
                        self.driver.get(search_url)
                        time.sleep(3)
                        logger.info(f"  Navigated to search URL: {search_url}")
                    else:
                        search_box.clear()
                        search_box.send_keys(term)
                        search_box.send_keys(Keys.RETURN)
                        time.sleep(3)

                    self.stats['searches_performed'] += 1

                    # Wait for results to load
                    result_selectors = [
                        ".search-results",
                        ".result-item",
                        ".tender-row",
                        ".contract-item",
                        "[class*='result']",
                        "table tbody tr",
                        ".list-group-item"
                    ]

                    results_found = False
                    for selector in result_selectors:
                        try:
                            WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            result_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                            if result_elements:
                                logger.info(f"  Found {len(result_elements)} results using selector: {selector}")
                                results_found = True

                                for idx, element in enumerate(result_elements[:10]):  # Limit to first 10
                                    try:
                                        text = element.text.strip()
                                        if text and len(text) > 50:  # Skip navigation elements
                                            result_data = {
                                                'search_term': term,
                                                'text': text[:1000],  # Limit text length
                                                'has_chinese_entity': self.check_chinese_entity(text),
                                                'portal': 'nen.nipez.cz',
                                                'country': 'CZ',
                                                'extracted_at': datetime.now().isoformat(),
                                                'selector_used': selector,
                                                'id': hashlib.md5(text.encode()).hexdigest()[:12]
                                            }

                                            self.results.append(result_data)
                                            self.stats['results_found'] += 1

                                            if result_data['has_chinese_entity']:
                                                self.stats['chinese_entities'] += 1
                                                logger.info(f"    ✓ Found Chinese entity in result {idx+1}")

                                    except Exception as e:
                                        logger.debug(f"    Error extracting result {idx}: {e}")

                                break  # Found results with this selector

                        except TimeoutException:
                            continue

                    if not results_found:
                        # Try to extract any content from the page
                        page_text = self.driver.find_element(By.TAG_NAME, "body").text
                        if "No results found" in page_text or "Žádné výsledky" in page_text:
                            logger.info(f"  No results found for: {term}")
                        else:
                            logger.warning(f"  Could not extract structured results for: {term}")

                except Exception as e:
                    logger.error(f"  Error searching for {term}: {e}")
                    self.stats['errors'] += 1

        except Exception as e:
            logger.error(f"Fatal error scraping Czech portal: {e}")
            self.stats['errors'] += 1

    def scrape_polish_portal_enhanced(self):
        """Enhanced scraping for Polish portal"""
        portal_url = "https://ezamowienia.gov.pl/"
        logger.info("\n" + "="*70)
        logger.info("POLISH PORTAL ENHANCED SCRAPING")
        logger.info(f"Portal: {portal_url}")
        logger.info("="*70)

        try:
            self.driver.get(portal_url)
            time.sleep(3)
            self.stats['pages_loaded'] += 1
            logger.info("Polish portal loaded")

            # Accept cookies if present
            try:
                cookie_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Akceptuj')]")
                cookie_button.click()
                time.sleep(1)
            except:
                pass

            # Try to find the search functionality
            search_terms = ['Huawei', 'Chiny', 'Lenovo']  # Including Polish for China

            for term in search_terms:
                logger.info(f"\nSearching for: {term}")

                try:
                    # Look for search box
                    search_selectors = [
                        "input[type='search']",
                        "input[placeholder*='Szukaj']",
                        "input[placeholder*='Search']",
                        "#search",
                        "input[name='q']",
                        "input[name='query']"
                    ]

                    search_box = None
                    for selector in search_selectors:
                        try:
                            search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                            logger.info(f"  Found search box with selector: {selector}")
                            break
                        except:
                            continue

                    if search_box:
                        search_box.clear()
                        search_box.send_keys(term)
                        search_box.send_keys(Keys.RETURN)
                        time.sleep(3)
                        self.stats['searches_performed'] += 1

                        # Extract results
                        self.extract_polish_results(term)
                    else:
                        logger.warning("  Could not find search functionality")

                except Exception as e:
                    logger.error(f"  Error searching for {term}: {e}")
                    self.stats['errors'] += 1

        except Exception as e:
            logger.error(f"Fatal error scraping Polish portal: {e}")
            self.stats['errors'] += 1

    def extract_polish_results(self, search_term):
        """Extract results from Polish portal"""
        result_selectors = [
            ".search-results",
            ".result",
            ".announcement",
            "table tbody tr",
            "[class*='ogloszenie']",  # Polish for announcement
            "[class*='wynik']"  # Polish for result
        ]

        for selector in result_selectors:
            try:
                result_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if result_elements:
                    logger.info(f"  Found {len(result_elements)} results")

                    for idx, element in enumerate(result_elements[:10]):
                        text = element.text.strip()
                        if text and len(text) > 50:
                            result_data = {
                                'search_term': search_term,
                                'text': text[:1000],
                                'has_chinese_entity': self.check_chinese_entity(text),
                                'portal': 'ezamowienia.gov.pl',
                                'country': 'PL',
                                'extracted_at': datetime.now().isoformat(),
                                'id': hashlib.md5(text.encode()).hexdigest()[:12]
                            }

                            self.results.append(result_data)
                            self.stats['results_found'] += 1

                            if result_data['has_chinese_entity']:
                                self.stats['chinese_entities'] += 1
                    break

            except Exception as e:
                logger.debug(f"Could not extract with selector {selector}: {e}")

    def scrape_slovak_portal_enhanced(self):
        """Enhanced scraping for Slovak portal with better extraction"""
        portal_url = "https://www.uvo.gov.sk/vyhladavanie-zakaziek"
        logger.info("\n" + "="*70)
        logger.info("SLOVAK PORTAL ENHANCED SCRAPING")
        logger.info(f"Portal: {portal_url}")
        logger.info("="*70)

        try:
            self.driver.get(portal_url)
            time.sleep(3)
            self.stats['pages_loaded'] += 1
            logger.info("Slovak portal loaded - search page")

            search_terms = ['Huawei', 'ZTE', 'Lenovo']

            for term in search_terms:
                logger.info(f"\nSearching for: {term}")

                try:
                    # Look for the search input on the dedicated search page
                    search_selectors = [
                        "input[name='fulltext']",
                        "input[type='text']",
                        "#fulltext",
                        "input[placeholder*='Vyhľadávanie']"
                    ]

                    search_box = None
                    for selector in search_selectors:
                        try:
                            search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                            logger.info(f"  Found search box with selector: {selector}")
                            break
                        except:
                            continue

                    if search_box:
                        search_box.clear()
                        search_box.send_keys(term)

                        # Find and click search button
                        search_button_selectors = [
                            "button[type='submit']",
                            "input[type='submit']",
                            "button[class*='search']",
                            "button[class*='hladat']"  # Slovak for search
                        ]

                        for button_selector in search_button_selectors:
                            try:
                                search_button = self.driver.find_element(By.CSS_SELECTOR, button_selector)
                                search_button.click()
                                break
                            except:
                                continue

                        time.sleep(3)
                        self.stats['searches_performed'] += 1

                        # Extract results
                        self.extract_slovak_results(term)

                except Exception as e:
                    logger.error(f"  Error searching for {term}: {e}")
                    self.stats['errors'] += 1

        except Exception as e:
            logger.error(f"Fatal error scraping Slovak portal: {e}")
            self.stats['errors'] += 1

    def extract_slovak_results(self, search_term):
        """Extract results from Slovak portal"""
        result_selectors = [
            ".search-result",
            ".result-row",
            "table.results tbody tr",
            "[class*='vysledok']",  # Slovak for result
            ".tender-item"
        ]

        for selector in result_selectors:
            try:
                result_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if result_elements:
                    logger.info(f"  Found {len(result_elements)} results")

                    for idx, element in enumerate(result_elements[:10]):
                        text = element.text.strip()
                        if text and len(text) > 50:
                            result_data = {
                                'search_term': search_term,
                                'text': text[:1000],
                                'has_chinese_entity': self.check_chinese_entity(text),
                                'portal': 'uvo.gov.sk',
                                'country': 'SK',
                                'extracted_at': datetime.now().isoformat(),
                                'id': hashlib.md5(text.encode()).hexdigest()[:12]
                            }

                            self.results.append(result_data)
                            self.stats['results_found'] += 1

                            if result_data['has_chinese_entity']:
                                self.stats['chinese_entities'] += 1
                    break

            except Exception as e:
                logger.debug(f"Could not extract with selector {selector}: {e}")

    def run(self):
        """Run enhanced scraping on all portals"""
        if not self.setup_driver():
            return

        try:
            # Run scrapers
            self.scrape_czech_portal_enhanced()
            self.scrape_polish_portal_enhanced()
            self.scrape_slovak_portal_enhanced()

            # Save results
            self.save_results()

            # Print summary
            self.print_summary()

        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Chrome WebDriver closed")

    def save_results(self):
        """Save results to JSON files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path("data/processed/selenium_enhanced")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save by country
        countries = {}
        for result in self.results:
            country = result['country']
            if country not in countries:
                countries[country] = []
            countries[country].append(result)

        for country, country_results in countries.items():
            output_file = output_dir / f"{country}_enhanced_{timestamp}.json"

            chinese_count = sum(1 for r in country_results if r['has_chinese_entity'])

            output_data = {
                'country': country,
                'scrape_date': datetime.now().isoformat(),
                'total_results': len(country_results),
                'ted_procurement_chinese_entities_found': chinese_count,
                'results': country_results
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ Saved {len(country_results)} results to {output_file.name}")
            logger.info(f"  Chinese entities found: {chinese_count}")

    def print_summary(self):
        """Print scraping summary"""
        print("\n" + "="*70)
        print("ENHANCED SELENIUM SCRAPING SUMMARY")
        print("="*70)
        print(f"Pages loaded: {self.stats['pages_loaded']}")
        print(f"Searches performed: {self.stats['searches_performed']}")
        print(f"Total results found: {self.stats['results_found']}")
        print(f"Chinese entities identified: {self.stats['chinese_entities']}")
        print(f"Errors: {self.stats['errors']}")

        # By country breakdown
        countries = {}
        for result in self.results:
            country = result['country']
            if country not in countries:
                countries[country] = {'total': 0, 'chinese': 0}
            countries[country]['total'] += 1
            if result['has_chinese_entity']:
                countries[country]['chinese'] += 1

        print("\nBy Country:")
        for country, counts in countries.items():
            print(f"  {country}: {counts['total']} results, {counts['chinese']} with Chinese entities")
        print("="*70)


if __name__ == "__main__":
    import sys

    # Check for headless mode argument
    headless = '--headless' in sys.argv

    logger.info("\n" + "="*70)
    logger.info("ENHANCED SELENIUM PROCUREMENT PORTAL SCRAPING")
    logger.info(f"Mode: {'Headless' if headless else 'Visible'}")
    logger.info("="*70)

    scraper = EnhancedProcurementScraper(headless=headless)
    scraper.run()
