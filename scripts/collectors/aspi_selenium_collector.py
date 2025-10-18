#!/usr/bin/env python3
"""
ASPI MCF Collector with Selenium Browser Automation
Handles 403 blocking issues using real browser rendering
"""

import re
import time
import logging
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sys
import os
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collectors.mcf_base_collector import MCFBaseCollector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ASPISeleniumCollector(MCFBaseCollector):
    """ASPI collector using Selenium to bypass blocking"""

    def __init__(self):
        super().__init__()
        self.source_id = "aspi_selenium"
        self.base_url = "https://www.aspi.org.au"
        self.driver = None
        self.wait = None

        # ASPI-specific search terms
        self.search_queries = [
            "military civil fusion",
            "China defense technology",
            "PLA modernization",
            "Chinese military companies",
            "dual-use technology China",
            "technology transfer China",
            "Made in China 2025",
            "strategic competition",
            "critical technology tracker"
        ]

        # Key ASPI sections for MCF content
        self.key_sections = [
            "/report",
            "/publication",
            "/article",
            "/policy-brief",
            "/analysis",
            "/topics/china",
            "/topics/defence-strategy",
            "/topics/technology"
        ]

    def setup_driver(self):
        """Setup Chrome driver with anti-detection measures"""
        try:
            chrome_options = Options()

            # Anti-detection options
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # Performance options
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-images")  # Don't load images for speed

            # User agent to appear more human-like
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
            ]
            chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')

            # Headless mode for production
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--window-size=1920,1080")

            # Setup driver with automatic driver management
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Setup wait
            self.wait = WebDriverWait(self.driver, 20)

            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            logger.info("Chrome driver setup complete")
            return True

        except Exception as e:
            logger.error(f"Error setting up Chrome driver: {e}")
            return False

    def close_driver(self):
        """Safely close the driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

    def human_like_delay(self, min_seconds=1, max_seconds=3):
        """Add human-like delays between actions"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def scroll_page(self):
        """Scroll page in a human-like manner"""
        try:
            # Scroll down gradually
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")

            current_position = 0
            while current_position < total_height:
                scroll_to = min(current_position + random.randint(300, 700), total_height)
                self.driver.execute_script(f"window.scrollTo(0, {scroll_to})")
                self.human_like_delay(0.5, 1.5)
                current_position = scroll_to

        except Exception as e:
            logger.debug(f"Error scrolling: {e}")

    def search_aspi(self, query: str, limit: int = 20) -> list:
        """Search ASPI using Selenium"""
        results = []

        try:
            # Try multiple search URL formats
            search_urls = [
                f"{self.base_url}/search?query={query}",
                f"{self.base_url}/search/{query}",
                f"{self.base_url}/?s={query}"
            ]

            for search_url in search_urls:
                logger.info(f"Searching ASPI: {search_url}")
                self.driver.get(search_url)
                self.human_like_delay(2, 4)

                # Check if we got results
                page_source = self.driver.page_source
                if "no results" in page_source.lower() or "404" in page_source:
                    continue

                # Scroll to load dynamic content
                self.scroll_page()

                # Find search results - try multiple selectors
                selectors = [
                    "article a[href]",
                    ".search-result a",
                    ".result-item a",
                    "h2 a",
                    "h3 a",
                    ".entry-title a"
                ]

                links_found = []
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements[:limit]:
                            href = element.get_attribute('href')
                            title = element.text

                            if href and self._is_mcf_relevant(title + " " + href):
                                links_found.append({
                                    'url': href,
                                    'title': title
                                })
                    except:
                        continue

                if links_found:
                    results.extend(links_found[:limit])
                    break

        except Exception as e:
            logger.error(f"Error searching ASPI for '{query}': {e}")

        return results

    def collect_article(self, url: str) -> dict:
        """Collect a single article using Selenium"""
        try:
            logger.info(f"Collecting article: {url}")
            self.driver.get(url)
            self.human_like_delay(2, 4)

            # Wait for content to load
            try:
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))
            except TimeoutException:
                # Try alternative content containers
                try:
                    self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "content")))
                except:
                    pass

            # Scroll to load all content
            self.scroll_page()

            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract content
            content = self.extract_main_content(soup)
            if not content or len(content) < 500:
                return None

            # Calculate MCF relevance
            relevance_score = self.calculate_mcf_relevance(content)
            if relevance_score < 0.2:  # Lower threshold for ASPI
                return None

            # Extract metadata
            metadata = self._extract_metadata(soup, url)

            # Extract entities
            entities = self.extract_chinese_entities(content)

            document = {
                'url': url,
                'title': metadata['title'],
                'content': content[:10000],
                'relevance_score': relevance_score,
                'entities': entities,
                'metadata': metadata,
                'source': 'ASPI',
                'collection_timestamp': datetime.now().isoformat(),
                'collector': self.source_id
            }

            return document

        except Exception as e:
            logger.error(f"Error collecting article {url}: {e}")
            return None

    def extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML page"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()

        # Try to find main content area
        content_selectors = [
            'main',
            'article',
            '.content',
            '.main-content',
            '#content',
            '.post-content',
            '.entry-content',
            '.article-content',
            'div[role="main"]',
            '.strategist-content',  # ASPI specific
            '.publication-content'  # ASPI specific
        ]

        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        # If no main content area found, use body
        if not main_content:
            main_content = soup.find('body')

        if main_content:
            # Get text and clean it up
            text = main_content.get_text(separator=' ', strip=True)
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            return text

        return ""

    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract metadata from ASPI page"""
        metadata = {
            'title': 'Unknown Title',
            'publication_date': None,
            'authors': [],
            'document_type': 'article',
            'tags': []
        }

        # Extract title
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            metadata['title'] = title_elem.get_text(strip=True)

        # Extract authors
        author_selectors = ['.author', '.by-author', '.authors', 'span[rel="author"]']
        for selector in author_selectors:
            author_elems = soup.select(selector)
            if author_elems:
                metadata['authors'] = [elem.get_text(strip=True) for elem in author_elems]
                break

        # Extract date
        date_selectors = ['.date', '.publish-date', 'time[datetime]', '.entry-date']
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                metadata['publication_date'] = date_text
                break

        # Extract tags
        tag_elems = soup.select('.tag, .topic, .category')
        metadata['tags'] = [elem.get_text(strip=True) for elem in tag_elems]

        # Determine document type
        if '/report' in url:
            metadata['document_type'] = 'report'
        elif '/policy-brief' in url:
            metadata['document_type'] = 'policy_brief'
        elif '/analysis' in url:
            metadata['document_type'] = 'analysis'

        return metadata

    def _is_mcf_relevant(self, text: str) -> bool:
        """Check if text is MCF-relevant"""
        mcf_keywords = [
            'china', 'chinese', 'pla', 'military', 'defense', 'defence',
            'technology', 'dual-use', 'dual use', 'mcf', 'fusion',
            'strategic', 'competition', 'xi jinping', 'beijing',
            'huawei', 'zte', 'artificial intelligence', 'quantum'
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in mcf_keywords)

    def browse_sections(self, limit_per_section: int = 10) -> list:
        """Browse key ASPI sections for MCF content"""
        all_documents = []

        for section in self.key_sections:
            try:
                section_url = urljoin(self.base_url, section)
                logger.info(f"Browsing section: {section_url}")

                self.driver.get(section_url)
                self.human_like_delay(2, 4)

                # Check if page loaded successfully
                if "404" in self.driver.page_source or "not found" in self.driver.page_source.lower():
                    continue

                # Scroll to load content
                self.scroll_page()

                # Find article links
                links = self.driver.find_elements(By.CSS_SELECTOR, 'article a[href], .entry a[href], h2 a[href], h3 a[href]')

                collected_count = 0
                for link in links:
                    if collected_count >= limit_per_section:
                        break

                    try:
                        href = link.get_attribute('href')
                        title = link.text

                        if href and self._is_mcf_relevant(title):
                            doc = self.collect_article(href)
                            if doc:
                                all_documents.append(doc)
                                collected_count += 1
                                self.human_like_delay(3, 6)  # Longer delay between articles

                    except Exception as e:
                        logger.debug(f"Error processing link: {e}")
                        continue

            except Exception as e:
                logger.error(f"Error browsing section {section}: {e}")
                continue

        return all_documents

    def run_collection(self, limit: int = 20) -> dict:
        """Run ASPI collection using Selenium"""
        if not self.setup_driver():
            return {
                'source': self.source_id,
                'documents_collected': 0,
                'error': 'Failed to setup Chrome driver'
            }

        try:
            logger.info("Starting ASPI Selenium collection")
            all_documents = []

            # 1. Search for MCF content
            for query in self.search_queries[:3]:  # Limit queries
                search_results = self.search_aspi(query, limit=10)

                for result in search_results:
                    doc = self.collect_article(result['url'])
                    if doc:
                        all_documents.append(doc)

                        if len(all_documents) >= limit:
                            break

                if len(all_documents) >= limit:
                    break

                self.human_like_delay(5, 10)  # Longer delay between searches

            # 2. Browse sections if needed
            if len(all_documents) < limit:
                section_docs = self.browse_sections(limit_per_section=5)
                all_documents.extend(section_docs[:limit - len(all_documents)])

            # Save to database
            saved_count = 0
            for doc in all_documents:
                if self.save_to_database(doc):
                    saved_count += 1

            result = {
                'source': self.source_id,
                'documents_collected': len(all_documents),
                'documents_saved': saved_count,
                'high_relevance': len([d for d in all_documents if d['relevance_score'] > 0.7]),
                'timestamp': datetime.now().isoformat()
            }

            logger.info(f"ASPI Selenium collection complete: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in ASPI collection: {e}")
            return {
                'source': self.source_id,
                'documents_collected': 0,
                'error': str(e)
            }

        finally:
            self.close_driver()


if __name__ == "__main__":
    collector = ASPISeleniumCollector()
    result = collector.run_collection(limit=10)
    print(f"Collection result: {result}")
