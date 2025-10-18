#!/usr/bin/env python3
"""
Web scraper component for EU-China Agreements Harvester
Uses Selenium for dynamic content and search engine interaction
"""

import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import quote_plus, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class WebSearchScraper:
    """Scrape search results from multiple sources"""

    def __init__(self, headless: bool = True):
        """Initialize the web scraper"""
        self.setup_driver(headless)

    def setup_driver(self, headless: bool):
        """Setup Chrome driver with options"""
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        # Try to initialize driver
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize Chrome driver: {e}")
            logger.info("Falling back to requests-based scraping")
            self.driver = None
            self.wait = None

    def search_google(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search Google and extract results"""
        results = []

        if not self.driver:
            return self._search_google_requests(query, num_results)

        try:
            # Build Google search URL
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}"

            logger.info(f"Searching Google: {query}")
            self.driver.get(search_url)

            # Wait for results
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#search')))

            # Extract search results
            search_results = self.driver.find_elements(By.CSS_SELECTOR, 'div.g')

            for result in search_results[:num_results]:
                try:
                    # Extract title
                    title_elem = result.find_element(By.CSS_SELECTOR, 'h3')
                    title = title_elem.text if title_elem else ""

                    # Extract URL
                    link_elem = result.find_element(By.CSS_SELECTOR, 'a')
                    url = link_elem.get_attribute('href') if link_elem else ""

                    # Extract snippet
                    snippet_elem = result.find_element(By.CSS_SELECTOR, 'span.st, div.VwiC3b')
                    snippet = snippet_elem.text if snippet_elem else ""

                    if url and title:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'source': 'google'
                        })

                except Exception as e:
                    logger.debug(f"Error extracting result: {e}")
                    continue

            logger.info(f"Found {len(results)} results from Google")

        except Exception as e:
            logger.error(f"Error searching Google: {e}")

        return results

    def _search_google_requests(self, query: str, num_results: int = 10) -> List[Dict]:
        """Fallback Google search using requests (limited functionality)"""
        # Note: This is a simplified version and may not work reliably
        # Google actively blocks automated requests
        results = []

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            params = {
                'q': query,
                'num': num_results
            }

            response = requests.get(
                'https://www.google.com/search',
                params=params,
                headers=headers
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                for g in soup.find_all('div', class_='g'):
                    anchor = g.find('a')
                    if anchor:
                        url = anchor.get('href', '')
                        title = g.find('h3')
                        title = title.text if title else ''

                        if url and title:
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': '',
                                'source': 'google_requests'
                            })

        except Exception as e:
            logger.error(f"Error with requests-based Google search: {e}")

        return results

    def scrape_official_site(self, url: str, search_terms: List[str]) -> List[Dict]:
        """Scrape an official government site for agreements"""
        results = []

        try:
            if self.driver:
                self.driver.get(url)
                time.sleep(2)  # Allow page to load

                # Try to find search box
                search_box = None
                for selector in ['input[type="search"]', 'input[name="search"]', 'input[name="q"]', 'input.search']:
                    try:
                        search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue

                if search_box:
                    for term in search_terms:
                        search_box.clear()
                        search_box.send_keys(term)
                        search_box.submit()
                        time.sleep(2)

                        # Extract results from current page
                        page_results = self._extract_page_results()
                        results.extend(page_results)
                else:
                    # No search box, try to navigate site structure
                    results = self._crawl_site_pages(url, search_terms)
            else:
                # Use requests fallback
                results = self._scrape_site_requests(url, search_terms)

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")

        return results

    def _extract_page_results(self) -> List[Dict]:
        """Extract results from current page"""
        results = []

        if not self.driver:
            return results

        try:
            # Common patterns for result containers
            selectors = [
                'div.result', 'div.search-result', 'article',
                'div.item', 'li.result-item', 'div.content-item'
            ]

            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for elem in elements:
                        try:
                            # Extract link
                            link = elem.find_element(By.CSS_SELECTOR, 'a')
                            url = link.get_attribute('href')
                            title = link.text

                            # Extract text
                            text = elem.text

                            if url and title:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'snippet': text[:200],
                                    'source': 'official_site'
                                })
                        except:
                            continue
                    break
        except Exception as e:
            logger.debug(f"Error extracting page results: {e}")

        return results

    def _crawl_site_pages(self, base_url: str, search_terms: List[str]) -> List[Dict]:
        """Crawl site pages looking for agreements"""
        results = []
        visited = set()
        to_visit = [base_url]

        # Common agreement-related URL patterns
        patterns = [
            'agreement', 'treaty', 'mou', 'memorandum', 'partnership',
            'cooperation', 'china', 'prc', 'bilateral'
        ]

        max_pages = 20  # Limit crawl depth

        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)

            if url in visited:
                continue

            visited.add(url)

            try:
                if self.driver:
                    self.driver.get(url)
                    time.sleep(1)

                    # Check page content for search terms
                    page_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()

                    for term in search_terms:
                        if term.lower() in page_text:
                            # Page contains search term, extract info
                            title = self.driver.title
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': page_text[:200],
                                'source': 'crawled_page'
                            })
                            break

                    # Find more links to visit
                    links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href]')
                    for link in links:
                        href = link.get_attribute('href')
                        if href and any(pattern in href.lower() for pattern in patterns):
                            if href.startswith('http') and href not in visited:
                                to_visit.append(href)

            except Exception as e:
                logger.debug(f"Error crawling {url}: {e}")
                continue

        return results

    def _scrape_site_requests(self, url: str, search_terms: List[str]) -> List[Dict]:
        """Scrape site using requests library"""
        results = []

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all links
                links = soup.find_all('a', href=True)

                for link in links:
                    href = link['href']
                    text = link.get_text(strip=True)

                    # Check if link text or URL contains search terms
                    for term in search_terms:
                        if term.lower() in text.lower() or term.lower() in href.lower():
                            full_url = href if href.startswith('http') else urljoin(url, href)
                            results.append({
                                'title': text or 'Untitled',
                                'url': full_url,
                                'snippet': '',
                                'source': 'requests_scrape'
                            })
                            break

        except Exception as e:
            logger.error(f"Error scraping {url} with requests: {e}")

        return results

    def fetch_and_save_content(self, url: str, output_dir: Path) -> Optional[str]:
        """Fetch full content from URL and save"""
        try:
            # Create filename from URL
            domain = urlparse(url).netloc
            path = urlparse(url).path.replace('/', '_')
            filename = f"{domain}{path}.html"
            if not filename.endswith('.html'):
                filename += '.html'

            filepath = output_dir / filename

            # Fetch content
            if self.driver:
                self.driver.get(url)
                time.sleep(2)
                content = self.driver.page_source
            else:
                response = requests.get(url, timeout=10)
                content = response.text

            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Saved content from {url} to {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()

class OfficialSiteSearcher:
    """Search official government sites for agreements"""

    def __init__(self, config_path: str):
        """Initialize with country configuration"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.scraper = WebSearchScraper(headless=True)

    def search_country_sites(self, country_code: str) -> List[Dict]:
        """Search all official sites for a country"""
        if country_code not in self.config['countries']:
            raise ValueError(f"Country {country_code} not configured")

        country = self.config['countries'][country_code]
        all_results = []

        # Search each official domain
        for domain in country['official_domains']:
            url = f"https://{domain}"
            logger.info(f"Searching {url}")

            # Get relevant search terms
            search_terms = []
            for lang in country['languages']:
                terms = country['search_terms'].get(lang, [])
                search_terms.extend(terms[:3])  # Top 3 terms per language

            # Add "China" in local language
            search_terms.append('China')
            if country_code == 'IT':
                search_terms.append('Cina')
            elif country_code == 'DE':
                search_terms.append('China')
            elif country_code == 'FR':
                search_terms.append('Chine')
            elif country_code == 'PL':
                search_terms.append('Chiny')
            elif country_code == 'ES':
                search_terms.append('China')

            # Search the site
            results = self.scraper.scrape_official_site(url, search_terms)
            all_results.extend(results)

        # Also do Google searches with site restrictions
        for domain in country['official_domains'][:2]:  # Top 2 domains
            for term in ['agreement China', 'MoU China', 'partnership China']:
                query = f"site:{domain} {term} 2020..2025"
                google_results = self.scraper.search_google(query, num_results=10)
                all_results.extend(google_results)

        logger.info(f"Found {len(all_results)} total results for {country_code}")
        return all_results

    def search_chinese_sites(self, country_code: str) -> List[Dict]:
        """Search Chinese government sites for agreements with a country"""
        results = []

        # Get country name in Chinese
        country_names_zh = {
            'IT': '意大利',
            'DE': '德国',
            'FR': '法国',
            'PL': '波兰',
            'ES': '西班牙'
        }

        country_zh = country_names_zh.get(country_code, '')
        if not country_zh:
            return results

        # Search Chinese MFA
        queries = [
            f"site:fmprc.gov.cn {country_zh} 协议",
            f"site:fmprc.gov.cn {country_zh} 备忘录",
            f"site:fmprc.gov.cn {country_zh} 合作"
        ]

        for query in queries:
            google_results = self.scraper.search_google(query, num_results=10)
            results.extend(google_results)

        # Search Chinese embassy site
        embassy = self.config['chinese_sources']['embassies'].get(country_code)
        if embassy:
            query = f"site:{embassy} agreement OR 协议 OR memorandum OR 备忘录"
            google_results = self.scraper.search_google(query, num_results=10)
            results.extend(google_results)

        logger.info(f"Found {len(results)} results from Chinese sites for {country_code}")
        return results

    def collect_agreements(self, country_code: str, output_dir: Path) -> Dict:
        """Collect all agreements for a country"""
        logger.info(f"Collecting agreements for {country_code}")

        # Create output directory
        country_dir = output_dir / country_code
        raw_dir = country_dir / 'raw'
        raw_dir.mkdir(parents=True, exist_ok=True)

        # Search official sites
        official_results = self.search_country_sites(country_code)

        # Search Chinese sites
        chinese_results = self.search_chinese_sites(country_code)

        # Combine results
        all_results = official_results + chinese_results

        # Remove duplicates by URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)

        logger.info(f"Total unique results: {len(unique_results)}")

        # Fetch and save content for top results
        saved_files = []
        for result in unique_results[:20]:  # Limit to top 20 for pilot
            filepath = self.scraper.fetch_and_save_content(result['url'], raw_dir)
            if filepath:
                result['local_file'] = filepath
                saved_files.append(result)

        # Save results metadata
        metadata_file = country_dir / 'search_results.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                'country': country_code,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_results': len(unique_results),
                'saved_files': len(saved_files),
                'results': unique_results
            }, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved metadata to {metadata_file}")

        return {
            'country': country_code,
            'total_results': len(unique_results),
            'saved_files': len(saved_files),
            'results': unique_results
        }

    def close(self):
        """Clean up resources"""
        self.scraper.close()

def main():
    """Test the web scraper"""
    logging.basicConfig(level=logging.INFO)

    # Setup paths
    base_dir = Path(__file__).parent.parent
    config_path = base_dir / 'config' / 'countries.json'
    output_dir = base_dir / 'out' / 'scraped'

    # Create searcher
    searcher = OfficialSiteSearcher(str(config_path))

    try:
        # Test with Italy
        results = searcher.collect_agreements('IT', output_dir)

        print(f"\nResults for Italy:")
        print(f"Total results: {results['total_results']}")
        print(f"Saved files: {results['saved_files']}")

        if results['results']:
            print("\nSample results:")
            for result in results['results'][:5]:
                print(f"- {result['title']}")
                print(f"  URL: {result['url']}")
                print(f"  Source: {result['source']}")
                print()

    finally:
        searcher.close()

if __name__ == "__main__":
    main()
