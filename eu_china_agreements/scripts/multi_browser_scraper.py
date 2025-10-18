#!/usr/bin/env python3
"""
Multi-browser web scraper for EU-China Agreements Harvester
Supports Chrome, Edge, and Firefox for better compatibility
"""

import json
import time
import logging
import platform
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import quote_plus, urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class MultiBrowserScraper:
    """Web scraper with support for multiple browsers"""

    def __init__(self, browser: str = 'auto', headless: bool = True):
        """
        Initialize scraper with specified browser

        Args:
            browser: 'chrome', 'edge', 'firefox', or 'auto' (tries all)
            headless: Run browser in headless mode
        """
        self.driver = None
        self.wait = None
        self.browser_name = None

        if browser == 'auto':
            self._auto_setup_driver(headless)
        else:
            self._setup_specific_browser(browser, headless)

    def _auto_setup_driver(self, headless: bool):
        """Try to set up any available browser automatically"""
        browsers_to_try = ['edge', 'firefox', 'chrome']

        for browser in browsers_to_try:
            try:
                logger.info(f"Attempting to initialize {browser} driver...")
                self._setup_specific_browser(browser, headless)
                if self.driver:
                    logger.info(f"Successfully initialized {browser} driver")
                    return
            except Exception as e:
                logger.debug(f"Could not initialize {browser}: {e}")
                continue

        logger.warning("Could not initialize any browser driver, falling back to requests")

    def _setup_specific_browser(self, browser: str, headless: bool):
        """Set up a specific browser driver"""
        try:
            if browser.lower() == 'edge':
                self._setup_edge(headless)
            elif browser.lower() == 'firefox':
                self._setup_firefox(headless)
            elif browser.lower() == 'chrome':
                self._setup_chrome(headless)
            else:
                raise ValueError(f"Unsupported browser: {browser}")
        except Exception as e:
            logger.error(f"Failed to set up {browser}: {e}")
            raise

    def _setup_edge(self, headless: bool):
        """Set up Microsoft Edge driver"""
        options = EdgeOptions()
        options.use_chromium = True

        if headless:
            options.add_argument('--headless')

        # Common options for stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # User agent to appear more legitimate
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')

        try:
            # Try to use Edge driver
            self.driver = webdriver.Edge(options=options)
            self.wait = WebDriverWait(self.driver, 10)
            self.browser_name = 'edge'

            # Execute script to hide webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        except Exception as e:
            logger.error(f"Edge initialization failed: {e}")
            raise

    def _setup_firefox(self, headless: bool):
        """Set up Firefox driver"""
        options = FirefoxOptions()

        if headless:
            options.add_argument('--headless')

        # Firefox specific options
        options.add_argument('--width=1920')
        options.add_argument('--height=1080')

        # Preferences to avoid detection
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference('useAutomationExtension', False)
        options.set_preference("general.useragent.override",
                              "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0")

        try:
            self.driver = webdriver.Firefox(options=options)
            self.wait = WebDriverWait(self.driver, 10)
            self.browser_name = 'firefox'

            # Execute script to hide webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        except Exception as e:
            logger.error(f"Firefox initialization failed: {e}")
            raise

    def _setup_chrome(self, headless: bool):
        """Set up Chrome driver"""
        options = ChromeOptions()

        if headless:
            options.add_argument('--headless=new')  # New headless mode

        # Chrome options for stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # User agent
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 10)
            self.browser_name = 'chrome'

            # Execute script to hide webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        except Exception as e:
            logger.error(f"Chrome initialization failed: {e}")
            raise

    def search_with_browser(self, query: str, search_engine: str = 'bing') -> List[Dict]:
        """
        Search using browser automation

        Args:
            query: Search query
            search_engine: 'google', 'bing', or 'duckduckgo'
        """
        if not self.driver:
            return self._fallback_search(query)

        results = []

        try:
            if search_engine == 'bing':
                results = self._search_bing(query)
            elif search_engine == 'duckduckgo':
                results = self._search_duckduckgo(query)
            elif search_engine == 'google':
                results = self._search_google(query)
            else:
                logger.warning(f"Unknown search engine: {search_engine}")

        except Exception as e:
            logger.error(f"Browser search failed: {e}")
            results = self._fallback_search(query)

        return results

    def _search_bing(self, query: str) -> List[Dict]:
        """Search using Bing (more lenient with automation)"""
        results = []

        try:
            # Bing is generally more tolerant of automated searches
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}"
            logger.info(f"Searching Bing: {query}")

            self.driver.get(search_url)
            time.sleep(2)  # Give page time to load

            # Wait for results
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.b_algo')))

            # Extract search results
            search_results = self.driver.find_elements(By.CSS_SELECTOR, 'li.b_algo')

            for result in search_results[:10]:
                try:
                    # Extract title and URL
                    title_elem = result.find_element(By.CSS_SELECTOR, 'h2 a')
                    title = title_elem.text
                    url = title_elem.get_attribute('href')

                    # Extract snippet
                    snippet_elem = result.find_element(By.CSS_SELECTOR, 'div.b_caption p')
                    snippet = snippet_elem.text if snippet_elem else ""

                    if url and title:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'source': f'bing_{self.browser_name}'
                        })

                except Exception as e:
                    logger.debug(f"Error extracting Bing result: {e}")
                    continue

            logger.info(f"Found {len(results)} results from Bing")

        except Exception as e:
            logger.error(f"Error searching Bing: {e}")

        return results

    def _search_duckduckgo(self, query: str) -> List[Dict]:
        """Search using DuckDuckGo (privacy-focused, no tracking)"""
        results = []

        try:
            search_url = f"https://duckduckgo.com/?q={quote_plus(query)}"
            logger.info(f"Searching DuckDuckGo: {query}")

            self.driver.get(search_url)
            time.sleep(3)  # DuckDuckGo can be slower

            # Wait for results
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="result"]')))

            # Extract search results
            search_results = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="result"]')

            for result in search_results[:10]:
                try:
                    # Extract title and URL
                    title_elem = result.find_element(By.CSS_SELECTOR, 'h2 a')
                    title = title_elem.text
                    url = title_elem.get_attribute('href')

                    # Extract snippet
                    snippet_elem = result.find_element(By.CSS_SELECTOR, 'div[data-result="snippet"]')
                    snippet = snippet_elem.text if snippet_elem else ""

                    if url and title:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'source': f'duckduckgo_{self.browser_name}'
                        })

                except Exception as e:
                    logger.debug(f"Error extracting DuckDuckGo result: {e}")
                    continue

            logger.info(f"Found {len(results)} results from DuckDuckGo")

        except Exception as e:
            logger.error(f"Error searching DuckDuckGo: {e}")

        return results

    def _search_google(self, query: str) -> List[Dict]:
        """Search Google (may require more anti-detection measures)"""
        results = []

        try:
            # Add random delay to appear more human
            time.sleep(2)

            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            logger.info(f"Searching Google: {query}")

            self.driver.get(search_url)
            time.sleep(3)  # Longer delay for Google

            # Check for CAPTCHA
            if "sorry" in self.driver.current_url or "captcha" in self.driver.page_source.lower():
                logger.warning("Google detected automation, CAPTCHA may be required")
                return results

            # Wait for results
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.g')))

            # Extract search results
            search_results = self.driver.find_elements(By.CSS_SELECTOR, 'div.g')

            for result in search_results[:10]:
                try:
                    # Extract title
                    title_elem = result.find_element(By.CSS_SELECTOR, 'h3')
                    title = title_elem.text if title_elem else ""

                    # Extract URL
                    link_elem = result.find_element(By.CSS_SELECTOR, 'a')
                    url = link_elem.get_attribute('href') if link_elem else ""

                    # Extract snippet
                    snippet_elem = result.find_element(By.CSS_SELECTOR, 'span.aCOpRe, div.VwiC3b')
                    snippet = snippet_elem.text if snippet_elem else ""

                    if url and title:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'source': f'google_{self.browser_name}'
                        })

                except Exception as e:
                    logger.debug(f"Error extracting Google result: {e}")
                    continue

            logger.info(f"Found {len(results)} results from Google")

        except Exception as e:
            logger.error(f"Error searching Google: {e}")

        return results

    def _fallback_search(self, query: str) -> List[Dict]:
        """Fallback search using requests (limited functionality)"""
        results = []

        # Try to search using a simple HTTP request to DuckDuckGo HTML version
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            # DuckDuckGo HTML version (no JavaScript required)
            response = requests.get(
                f'https://html.duckduckgo.com/html/?q={quote_plus(query)}',
                headers=headers
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                for result in soup.find_all('div', class_='result'):
                    link = result.find('a', class_='result__a')
                    if link:
                        title = link.text.strip()
                        url = link.get('href', '')

                        snippet_elem = result.find('a', class_='result__snippet')
                        snippet = snippet_elem.text.strip() if snippet_elem else ''

                        if url and title:
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'source': 'duckduckgo_html'
                            })

                logger.info(f"Found {len(results)} results from DuckDuckGo HTML")

        except Exception as e:
            logger.error(f"Fallback search failed: {e}")

        return results

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content using browser or requests"""
        try:
            if self.driver:
                self.driver.get(url)
                time.sleep(2)
                return self.driver.page_source
            else:
                response = requests.get(url, timeout=10)
                return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def close(self):
        """Close the browser driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info(f"Closed {self.browser_name} driver")
            except:
                pass

def test_multi_browser():
    """Test the multi-browser scraper"""
    logging.basicConfig(level=logging.INFO)

    # Test queries for Italy-China agreements
    test_queries = [
        'site:esteri.it accordo Cina',
        'site:governo.it memorandum China',
        'Italy China agreement 2020..2025'
    ]

    # Try with auto browser selection
    scraper = MultiBrowserScraper(browser='auto', headless=False)

    try:
        print(f"Using browser: {scraper.browser_name or 'requests fallback'}")

        for query in test_queries:
            print(f"\nTesting query: {query}")

            # Try different search engines
            for engine in ['bing', 'duckduckgo']:
                print(f"  Using {engine}:")
                results = scraper.search_with_browser(query, search_engine=engine)

                if results:
                    for i, result in enumerate(results[:3], 1):
                        print(f"    {i}. {result['title'][:60]}...")
                        print(f"       URL: {result['url'][:80]}...")
                else:
                    print(f"    No results found")

                time.sleep(2)  # Rate limiting

    finally:
        scraper.close()

if __name__ == "__main__":
    test_multi_browser()
