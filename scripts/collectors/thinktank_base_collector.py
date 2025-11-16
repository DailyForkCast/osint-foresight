#!/usr/bin/env python3
"""
Think Tank Global Collector - Base Collector Class

Implements discovery engines and fetching logic with politeness controls.
Discovery order: API -> RSS -> Sitemap -> HTML
"""

import requests
import time
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Dict, Optional, Generator, Any
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
import hashlib
from pathlib import Path
import feedparser
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Try to import Selenium helper (optional dependency)
try:
    from thinktank_selenium_helper import SeleniumHelper
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium not available - install 'selenium' and ChromeDriver for fallback support")


class DiscoveryEngine:
    """
    Multi-mode discovery engine for think tank publications.

    Discovery priority:
    1. API/JSON (if available)
    2. RSS/Atom feeds
    3. Sitemap.xml
    4. HTML crawl (within allowed paths)
    """

    # Global request throttling
    MAX_CONCURRENT_GLOBAL = 6
    MAX_CONCURRENT_PER_DOMAIN = 2
    DEFAULT_DELAY_SECONDS = 1.5
    MAX_RETRIES = 3
    RETRY_BACKOFFS = [2, 5, 15]  # seconds

    # Request budgets per run
    MAX_PAGES_FORWARD = 40
    MAX_PAGES_BACKFILL = 60
    MAX_ITEMS_PER_SOURCE = 1500

    def __init__(self, source_domain: str, source_rules: Dict[str, Any]):
        """
        Initialize discovery engine for a source.

        Args:
            source_domain: e.g., "csis.org"
            source_rules: Configuration from source_rules registry
        """
        self.domain = source_domain
        self.base_url = f"https://{source_domain}"
        self.rules = source_rules

        # Tracking
        self.request_count = 0
        self.fail_count = 0
        self.last_request_time = defaultdict(float)  # per domain
        self.discovered_items = []

        # Failure tracking for comprehensive reporting
        self.failures = []  # List of failure details for reporting

        # Rate limiting
        self.delay = self.DEFAULT_DELAY_SECONDS

        # Check if source should use Selenium by default
        self.use_selenium = self.rules.get("use_selenium", False)

        # Robots.txt parser
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(f"{self.base_url}/robots.txt")
        try:
            self.robot_parser.read()
            logging.info(f"Loaded robots.txt for {self.domain}")
        except Exception as e:
            logging.warning(f"Could not load robots.txt for {self.domain}: {e}")

    def can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched per robots.txt."""
        try:
            return self.robot_parser.can_fetch("*", url)
        except:
            return True  # Default to allowing if parser fails

    def throttle(self):
        """Apply rate limiting delay."""
        elapsed = time.time() - self.last_request_time[self.domain]
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time[self.domain] = time.time()

    def fetch_with_retry(self, url: str, headers: Optional[Dict] = None) -> Optional[requests.Response]:
        """
        Fetch URL with retry logic and exponential backoff.

        Returns:
            Response object or None if all retries failed
        """
        if not self.can_fetch(url):
            logging.warning(f"Blocked by robots.txt: {url}")
            return None

        if headers is None:
            headers = {
                "User-Agent": "ThinkTankCollector/1.0 (OSINT Research; +https://github.com/osint-foresight)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }

        for attempt in range(self.MAX_RETRIES):
            try:
                self.throttle()
                response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
                self.request_count += 1

                if response.status_code == 200:
                    return response
                elif response.status_code in [404, 403, 401]:
                    logging.warning(f"HTTP {response.status_code} for {url}")
                    self.fail_count += 1
                    return None
                else:
                    logging.warning(f"HTTP {response.status_code} for {url}, retrying...")
                    self.fail_count += 1

            except requests.RequestException as e:
                logging.warning(f"Request failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                self.fail_count += 1

                if attempt < self.MAX_RETRIES - 1:
                    backoff = self.RETRY_BACKOFFS[attempt]
                    logging.info(f"Backing off for {backoff}s...")
                    time.sleep(backoff)

        logging.error(f"All retries exhausted for {url}")
        return None

    def _record_failure(self, url: str, method: str, error_type: str, error_details: str):
        """Record a failure for comprehensive reporting."""
        failure_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "domain": self.domain,
            "url": url,
            "method": method,  # "HTTP" or "SELENIUM"
            "error_type": error_type,  # "403", "timeout", "blocked_by_robots", etc.
            "error_details": error_details
        }
        self.failures.append(failure_record)
        logging.warning(f"Recorded failure: {self.domain} - {url} - {error_type}")

    def fetch_with_selenium_fallback(self, url: str, use_selenium: bool = None) -> Optional[requests.Response]:
        """
        Fetch URL with Selenium fallback for blocked sites.

        Args:
            url: URL to fetch
            use_selenium: If True, skip HTTP and use Selenium directly
                         If None, use self.use_selenium (source default)

        Returns:
            Response object (or mock response from Selenium) or None if failed
        """
        if use_selenium is None:
            use_selenium = self.use_selenium

        # If use_selenium is False, try HTTP first
        if not use_selenium:
            response = self.fetch_with_retry(url)
            if response:
                return response

            # Record HTTP failure
            self._record_failure(url, "HTTP", "all_retries_failed", "HTTP fetch failed after all retries")

        # HTTP failed or use_selenium=True - try Selenium fallback
        if not SELENIUM_AVAILABLE:
            logging.error(f"Selenium not available, cannot fallback for {url}")
            self._record_failure(url, "SELENIUM", "not_available", "Selenium not installed")
            return None

        logging.info(f"Attempting Selenium fallback for {url}")

        try:
            with SeleniumHelper(headless=True, timeout=30) as helper:
                result = helper.fetch(url)

                if result:
                    logging.info(f"✓ Selenium successfully fetched {url}")

                    # Create a mock Response object compatible with requests
                    class SeleniumResponse:
                        def __init__(self, content, text, url, status_code=200):
                            self.content = content
                            self.text = text
                            self.url = url
                            self.status_code = status_code

                        def json(self):
                            """Support JSON parsing."""
                            import json
                            return json.loads(self.text)

                    return SeleniumResponse(
                        content=result['content'],
                        text=result['text'],
                        url=result['url'],
                        status_code=200
                    )
                else:
                    logging.error(f"✗ Selenium fallback failed for {url}")
                    self._record_failure(url, "SELENIUM", "fetch_failed", "Selenium fetch returned None")
                    return None

        except Exception as e:
            logging.error(f"✗ Selenium error for {url}: {e}")
            self._record_failure(url, "SELENIUM", "exception", str(e))
            return None

    def discover_api(self) -> Generator[Dict[str, Any], None, None]:
        """
        Discover publications via API/JSON endpoint.

        Yields:
            Publication metadata dicts
        """
        api_endpoint = self.rules.get("api_endpoint")
        if not api_endpoint:
            logging.debug(f"No API endpoint configured for {self.domain}")
            return

        logging.info(f"Discovering via API: {api_endpoint}")
        response = self.fetch_with_retry(api_endpoint)

        if not response:
            return

        try:
            data = response.json()
            # Parse based on API structure (customize per source)
            items = data.get("items", data.get("results", data))

            for item in items:
                yield {
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "publication_date": item.get("date"),
                    "fetch_mode": "API"
                }
        except Exception as e:
            logging.error(f"Failed to parse API response: {e}")

    def discover_rss(self) -> Generator[Dict[str, Any], None, None]:
        """
        Discover publications via RSS/Atom feeds.

        Yields:
            Publication metadata dicts
        """
        # Try common feed URLs
        feed_urls = self.rules.get("rss_feeds", [
            "/feed", "/rss", "/atom", "/feed.xml", "/rss.xml", "/atom.xml"
        ])

        for feed_path in feed_urls:
            feed_url = urljoin(self.base_url, feed_path)
            response = self.fetch_with_retry(feed_url)

            if not response:
                continue

            try:
                feed = feedparser.parse(response.text)

                if not feed.entries:
                    continue

                logging.info(f"Found {len(feed.entries)} entries in RSS feed: {feed_url}")

                for entry in feed.entries:
                    yield {
                        "title": entry.get("title"),
                        "url": entry.get("link"),
                        "publication_date": entry.get("published", entry.get("updated")),
                        "summary": entry.get("summary"),
                        "fetch_mode": "RSS"
                    }

                break  # Stop after first successful feed

            except Exception as e:
                logging.error(f"Failed to parse RSS feed {feed_url}: {e}")

    def discover_sitemap(self) -> Generator[Dict[str, Any], None, None]:
        """
        Discover publications via sitemap.xml.

        Yields:
            Publication metadata dicts
        """
        sitemap_urls = self.rules.get("sitemaps", ["/sitemap.xml"])

        for sitemap_path in sitemap_urls:
            sitemap_url = urljoin(self.base_url, sitemap_path)
            response = self.fetch_with_retry(sitemap_url)

            if not response:
                continue

            try:
                root = ET.fromstring(response.content)

                # Handle sitemap index (links to other sitemaps)
                if "sitemapindex" in root.tag:
                    for sitemap in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
                        sub_sitemap_url = sitemap.text
                        yield from self._parse_sitemap(sub_sitemap_url)
                else:
                    # Regular sitemap
                    for url_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
                        loc = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                        lastmod = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")

                        if loc is not None:
                            yield {
                                "url": loc.text,
                                "publication_date": lastmod.text if lastmod is not None else None,
                                "fetch_mode": "SITEMAP"
                            }

            except Exception as e:
                logging.error(f"Failed to parse sitemap {sitemap_url}: {e}")

    def _parse_sitemap(self, sitemap_url: str) -> Generator[Dict[str, Any], None, None]:
        """Helper to parse a single sitemap."""
        response = self.fetch_with_retry(sitemap_url)
        if not response:
            return

        try:
            root = ET.fromstring(response.content)
            for url_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
                loc = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                lastmod = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")

                if loc is not None:
                    yield {
                        "url": loc.text,
                        "publication_date": lastmod.text if lastmod is not None else None,
                        "fetch_mode": "SITEMAP"
                    }
        except Exception as e:
            logging.error(f"Failed to parse sitemap {sitemap_url}: {e}")

    def discover_html(self, max_pages: int = 40) -> Generator[Dict[str, Any], None, None]:
        """
        Discover publications via HTML crawling within allowed paths.

        Args:
            max_pages: Maximum number of pages to crawl

        Yields:
            Publication metadata dicts
        """
        publication_paths = self.rules.get("publications_paths", [
            "/publications", "/research", "/reports", "/documents"
        ])

        pages_crawled = 0

        for pub_path in publication_paths:
            if pages_crawled >= max_pages:
                logging.warning(f"Reached max pages limit ({max_pages})")
                break

            start_url = urljoin(self.base_url, pub_path)
            response = self.fetch_with_retry(start_url)

            if not response:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find publication links
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(start_url, href)

                # Check if URL is within allowed publication paths
                parsed = urlparse(full_url)
                if not any(parsed.path.startswith(path) for path in publication_paths):
                    continue

                # Extract metadata from link and surrounding context
                title = link.get_text(strip=True) or link.get('title', '')

                yield {
                    "url": full_url,
                    "title": title,
                    "fetch_mode": "HTML"
                }

            pages_crawled += 1

    def discover_all(self, max_pages: int = 40) -> List[Dict[str, Any]]:
        """
        Run full discovery pipeline: API -> RSS -> Sitemap -> HTML.

        Returns:
            List of discovered publication metadata
        """
        items = []

        # Try each discovery method in priority order
        logging.info(f"Starting discovery for {self.domain}")

        # 1. API
        try:
            items.extend(list(self.discover_api()))
            if items:
                logging.info(f"Discovered {len(items)} items via API")
        except Exception as e:
            logging.error(f"API discovery failed: {e}")

        # 2. RSS (if API didn't yield much)
        if len(items) < 10:
            try:
                rss_items = list(self.discover_rss())
                items.extend(rss_items)
                if rss_items:
                    logging.info(f"Discovered {len(rss_items)} items via RSS")
            except Exception as e:
                logging.error(f"RSS discovery failed: {e}")

        # 3. Sitemap (if still not enough)
        if len(items) < 50:
            try:
                sitemap_items = list(self.discover_sitemap())
                items.extend(sitemap_items)
                if sitemap_items:
                    logging.info(f"Discovered {len(sitemap_items)} items via Sitemap")
            except Exception as e:
                logging.error(f"Sitemap discovery failed: {e}")

        # 4. HTML crawl (fallback)
        if len(items) < 20:
            try:
                html_items = list(self.discover_html(max_pages=max_pages))
                items.extend(html_items)
                if html_items:
                    logging.info(f"Discovered {len(html_items)} items via HTML")
            except Exception as e:
                logging.error(f"HTML discovery failed: {e}")

        logging.info(f"Total items discovered for {self.domain}: {len(items)}")
        return items

    def get_failure_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive failure report.

        Returns:
            Dict with failure statistics and detailed failure records
        """
        total_failures = len(self.failures)
        http_failures = [f for f in self.failures if f["method"] == "HTTP"]
        selenium_failures = [f for f in self.failures if f["method"] == "SELENIUM"]

        # Group failures by error type
        error_types = {}
        for failure in self.failures:
            error_type = failure["error_type"]
            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1

        return {
            "domain": self.domain,
            "summary": {
                "total_failures": total_failures,
                "http_failures": len(http_failures),
                "selenium_failures": len(selenium_failures),
                "error_types": error_types
            },
            "failures": self.failures
        }


# Example usage
if __name__ == "__main__":
    # Test discovery engine
    source_rules = {
        "publications_paths": ["/analysis", "/features/reports"],
        "date_selectors": ["time[datetime]", ".published-date"],
        "pdf_selectors": ["a[href$='.pdf']"]
    }

    engine = DiscoveryEngine("csis.org", source_rules)
    items = engine.discover_all(max_pages=5)

    print(f"\nDiscovered {len(items)} items")
    for item in items[:5]:
        print(f"- {item.get('title', 'No title')}: {item.get('url')}")
