#!/usr/bin/env python3
"""
Enhanced State Department MCF Collector with Dynamic URL Discovery
Collects Military-Civil Fusion content using sitemaps and search
"""

import re
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote
import sys
import os
import xml.etree.ElementTree as ET

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collectors.mcf_base_collector import MCFBaseCollector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StateDeptMCFCollectorEnhanced(MCFBaseCollector):
    """Enhanced State Department collector with dynamic discovery"""

    def __init__(self):
        super().__init__()
        self.source_id = "state_dept_enhanced"
        self.base_url = "https://www.state.gov"
        self.search_base = "https://www.state.gov/search"

        # Cache discovered URLs
        self.discovered_urls = set()
        self.processed_urls = set()

        # Enhanced search terms for dynamic discovery
        self.search_queries = [
            "military civil fusion",
            "MCF China",
            "dual use technology China",
            "technology transfer China defense",
            "Chinese military companies",
            "PLA modernization",
            "export controls China technology",
            "CFIUS China",
            "Entity List China",
            "defense industrial base China",
            "strategic competition China",
            "emerging technologies China military"
        ]

    def discover_urls_from_sitemap(self) -> list:
        """Discover fresh URLs from State Dept sitemap"""
        sitemap_urls = [
            f"{self.base_url}/sitemap_index.xml",
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/post-sitemap.xml",
            f"{self.base_url}/news-sitemap.xml"
        ]

        discovered = []

        for sitemap_url in sitemap_urls:
            try:
                response = self.fetch_url_with_retry(sitemap_url)
                if not response:
                    continue

                # Parse XML sitemap
                root = ET.fromstring(response.content)

                # Handle different sitemap formats
                namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

                # Look for URLs in sitemap
                for url_elem in root.findall('.//sm:url/sm:loc', namespaces):
                    url = url_elem.text

                    # Check if URL might be MCF-relevant
                    if self._is_mcf_relevant_url(url):
                        discovered.append(url)
                        self.discovered_urls.add(url)

                # Also check for nested sitemaps
                for sitemap_elem in root.findall('.//sm:sitemap/sm:loc', namespaces):
                    nested_sitemap = sitemap_elem.text
                    if nested_sitemap not in sitemap_urls:
                        sitemap_urls.append(nested_sitemap)

            except Exception as e:
                logger.debug(f"Error parsing sitemap {sitemap_url}: {e}")
                continue

        logger.info(f"Discovered {len(discovered)} URLs from sitemaps")
        return discovered[:50]  # Limit to prevent overwhelming

    def discover_urls_from_search(self, query: str, limit: int = 20) -> list:
        """Discover URLs using State Dept search functionality"""
        discovered = []

        try:
            # Format search URL - State Dept uses different search endpoints
            search_urls = [
                f"{self.base_url}/search/?q={quote(query)}",
                f"{self.base_url}/?s={quote(query)}",
                f"{self.search_base}?q={quote(query)}"
            ]

            for search_url in search_urls:
                response = self.fetch_url_with_retry(search_url)
                if not response:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find search results - State Dept uses various formats
                result_selectors = [
                    'article a[href]',
                    '.search-result a',
                    '.content-list a',
                    '.entry-title a',
                    'h2 a',
                    'h3 a'
                ]

                for selector in result_selectors:
                    results = soup.select(selector)
                    for result in results[:limit]:
                        href = result.get('href')
                        if href:
                            # Make absolute URL
                            if href.startswith('/'):
                                href = urljoin(self.base_url, href)

                            # Check relevance and add
                            if self._is_mcf_relevant_url(href) and href not in self.discovered_urls:
                                discovered.append(href)
                                self.discovered_urls.add(href)

                                if len(discovered) >= limit:
                                    break

                    if discovered:
                        break

                if discovered:
                    break

        except Exception as e:
            logger.error(f"Error searching for '{query}': {e}")

        logger.info(f"Found {len(discovered)} URLs for query '{query}'")
        return discovered

    def discover_recent_content(self, days_back: int = 30) -> list:
        """Discover recent MCF-related content from news/press sections"""
        discovered = []

        # Recent content sections
        sections = [
            '/press-releases/',
            '/media-notes/',
            '/briefings-foreign-press-centers/',
            '/reports/',
            '/fact-sheets/',
            '/speeches/',
            '/remarks/',
            '/readouts/'
        ]

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        for section in sections:
            section_url = urljoin(self.base_url, section)

            try:
                response = self.fetch_url_with_retry(section_url)
                if not response:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find article links with dates
                articles = soup.select('article') or soup.select('.entry') or soup.select('.post')

                for article in articles[:50]:  # Limit per section
                    # Get article link
                    link_elem = article.find('a', href=True)
                    if not link_elem:
                        continue

                    href = link_elem['href']
                    if href.startswith('/'):
                        href = urljoin(self.base_url, href)

                    # Check if MCF-relevant
                    article_text = article.get_text(strip=True).lower()
                    if any(term in article_text for term in ['china', 'military', 'technology', 'defense', 'dual-use', 'export']):
                        if href not in self.discovered_urls:
                            discovered.append(href)
                            self.discovered_urls.add(href)

            except Exception as e:
                logger.debug(f"Error checking section {section}: {e}")
                continue

        logger.info(f"Found {len(discovered)} recent articles")
        return discovered

    def _is_mcf_relevant_url(self, url: str) -> bool:
        """Check if URL is likely MCF-relevant"""
        # Keywords that indicate MCF relevance
        mcf_indicators = [
            'china', 'chinese', 'prc', 'beijing',
            'military', 'defense', 'defence', 'security',
            'technology', 'tech', 'export', 'control',
            'dual-use', 'dual_use', 'mcf', 'fusion',
            'competition', 'strategic', 'industrial',
            'sanctions', 'entity-list', 'cfius'
        ]

        url_lower = url.lower()
        return any(indicator in url_lower for indicator in mcf_indicators)

    def collect_dynamic(self, limit_per_method: int = 20) -> list:
        """Collect using dynamic URL discovery"""
        all_documents = []

        # 1. Discover from sitemaps
        sitemap_urls = self.discover_urls_from_sitemap()
        for url in sitemap_urls[:limit_per_method]:
            if url in self.processed_urls:
                continue

            doc = self.collect_document(url)
            if doc and doc['relevance_score'] > 0.3:
                all_documents.append(doc)
                self.processed_urls.add(url)
                time.sleep(1)  # Rate limiting

        # 2. Discover from search queries
        for query in self.search_queries[:5]:  # Limit queries per run
            search_urls = self.discover_urls_from_search(query, limit=10)

            for url in search_urls:
                if url in self.processed_urls:
                    continue

                doc = self.collect_document(url)
                if doc and doc['relevance_score'] > 0.3:
                    all_documents.append(doc)
                    self.processed_urls.add(url)
                    time.sleep(1)

                if len(all_documents) >= limit_per_method:
                    break

        # 3. Discover recent content
        recent_urls = self.discover_recent_content(days_back=7)
        for url in recent_urls[:limit_per_method]:
            if url in self.processed_urls:
                continue

            doc = self.collect_document(url)
            if doc and doc['relevance_score'] > 0.3:
                all_documents.append(doc)
                self.processed_urls.add(url)
                time.sleep(1)

        logger.info(f"Collected {len(all_documents)} documents dynamically")
        return all_documents

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
            '.body-content',  # State Dept specific
            '.article-body'    # State Dept specific
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

    def collect_document(self, url: str) -> dict:
        """Collect and analyze a single document"""
        try:
            response = self.fetch_url_with_retry(url)
            if not response:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract content
            content = self.extract_main_content(soup)
            if not content or len(content) < 500:
                return None

            # Calculate MCF relevance
            relevance_score = self.calculate_mcf_relevance(content)

            # Extract metadata
            metadata = self.extract_document_metadata(soup, url)

            # Extract entities
            entities = self.extract_chinese_entities(content)

            document = {
                'url': url,
                'title': metadata['title'],
                'content': content[:10000],  # Limit content size
                'relevance_score': relevance_score,
                'entities': entities,
                'metadata': metadata,
                'source': 'State Department',
                'collection_timestamp': datetime.now().isoformat(),
                'collector': self.source_id
            }

            return document

        except Exception as e:
            logger.error(f"Error collecting {url}: {e}")
            return None

    def run_collection(self, limit: int = 20) -> dict:
        """Run dynamic collection"""
        logger.info("Starting State Dept dynamic collection")

        documents = self.collect_dynamic(limit_per_method=limit)

        # Save to database
        saved_count = 0
        for doc in documents:
            if self.save_to_database(doc):
                saved_count += 1

        result = {
            'source': self.source_id,
            'documents_collected': len(documents),
            'documents_saved': saved_count,
            'high_relevance': len([d for d in documents if d['relevance_score'] > 0.7]),
            'timestamp': datetime.now().isoformat()
        }

        logger.info(f"State Dept collection complete: {result}")
        return result


if __name__ == "__main__":
    collector = StateDeptMCFCollectorEnhanced()
    result = collector.run_collection(limit=20)
    print(f"Collection result: {result}")
