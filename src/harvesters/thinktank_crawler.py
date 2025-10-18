#!/usr/bin/env python3
"""
Think Tank Crawler - Web Crawling with Robots.txt Compliance

This module handles web crawling of think tank websites with proper
robots.txt compliance, rate limiting, and error handling.

Key Features:
- Robots.txt compliance checking and enforcement
- Configurable rate limiting with exponential backoff
- User-agent rotation and header management
- Session management with connection pooling
- Retry logic with intelligent backoff
- Content type detection and filtering
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from urllib.robotparser import RobotFileParser
import time
import random
import re
from bs4 import BeautifulSoup
import hashlib


@dataclass
class CrawlResult:
    """Result of crawling a single URL"""
    url: str
    success: bool
    status_code: Optional[int] = None
    content: Optional[bytes] = None
    content_type: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    robots_compliant: bool = True
    error: Optional[str] = None
    crawl_timestamp: datetime = None
    response_time: float = 0.0

    def __post_init__(self):
        if self.crawl_timestamp is None:
            self.crawl_timestamp = datetime.utcnow()


@dataclass
class RateLimitState:
    """Track rate limiting state for a domain"""
    domain: str
    last_request_time: float = 0.0
    request_count: int = 0
    window_start: float = 0.0
    consecutive_errors: int = 0
    backoff_until: float = 0.0


class ThinkTankCrawler:
    """Web crawler with robots.txt compliance and intelligent rate limiting"""

    def __init__(self, max_concurrent: int = 10, min_delay: float = 1.0, max_retries: int = 3):
        self.max_concurrent = max_concurrent
        self.min_delay = min_delay
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)

        # Rate limiting and robots.txt state
        self.rate_limit_states: Dict[str, RateLimitState] = {}
        self.robots_cache: Dict[str, RobotFileParser] = {}
        self.robots_cache_time: Dict[str, float] = {}

        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]

        # Content type filters
        self.allowed_content_types = {
            'text/html',
            'application/pdf',
            'application/json',
            'application/xml',
            'text/xml'
        }

    async def __aenter__(self):
        """Async context manager entry"""
        await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_session()

    async def _create_session(self):
        """Create HTTP session with appropriate configuration"""
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=10,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )

        timeout = aiohttp.ClientTimeout(
            total=60,
            connect=10,
            sock_read=30
        )

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )

    async def _close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        return urlparse(url).netloc.lower()

    def _get_rate_limit_state(self, domain: str) -> RateLimitState:
        """Get or create rate limit state for domain"""
        if domain not in self.rate_limit_states:
            self.rate_limit_states[domain] = RateLimitState(domain=domain)
        return self.rate_limit_states[domain]

    async def _check_robots_txt(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt"""
        domain = self._get_domain(url)
        current_time = time.time()

        # Check cache (refresh every 24 hours)
        if domain in self.robots_cache:
            if current_time - self.robots_cache_time.get(domain, 0) > 86400:
                # Cache expired, remove entry
                del self.robots_cache[domain]
                if domain in self.robots_cache_time:
                    del self.robots_cache_time[domain]

        # Load robots.txt if not cached
        if domain not in self.robots_cache:
            robots_url = urljoin(f"https://{domain}", "/robots.txt")
            try:
                rp = RobotFileParser()
                rp.set_url(robots_url)

                # Try to read robots.txt
                async with self.session.get(robots_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Parse robots.txt content
                        lines = content.split('\n')
                        rp.read_lines(lines)
                    else:
                        # If robots.txt not found, allow all
                        rp = None

                self.robots_cache[domain] = rp
                self.robots_cache_time[domain] = current_time

            except Exception as e:
                self.logger.debug(f"Failed to fetch robots.txt for {domain}: {e}")
                # On error, allow crawling but log
                self.robots_cache[domain] = None
                self.robots_cache_time[domain] = current_time

        # Check if URL is allowed
        rp = self.robots_cache[domain]
        if rp is None:
            return True  # No robots.txt or error loading it

        # Use a generic user agent for robots.txt checking
        user_agent = "ThinkTankHarvester/1.0"
        return rp.can_fetch(user_agent, url)

    async def _wait_for_rate_limit(self, domain: str):
        """Wait for rate limiting constraints"""
        state = self._get_rate_limit_state(domain)
        current_time = time.time()

        # Check if we're in backoff period
        if current_time < state.backoff_until:
            wait_time = state.backoff_until - current_time
            self.logger.debug(f"Waiting {wait_time:.2f}s for backoff on {domain}")
            await asyncio.sleep(wait_time)

        # Check minimum delay between requests
        time_since_last = current_time - state.last_request_time
        if time_since_last < self.min_delay:
            wait_time = self.min_delay - time_since_last
            self.logger.debug(f"Rate limiting: waiting {wait_time:.2f}s for {domain}")
            await asyncio.sleep(wait_time)

        # Add some jitter to avoid thundering herd
        jitter = random.uniform(0, 0.5)
        await asyncio.sleep(jitter)

        state.last_request_time = time.time()

    def _update_rate_limit_state(self, domain: str, success: bool):
        """Update rate limiting state after request"""
        state = self._get_rate_limit_state(domain)

        if success:
            state.consecutive_errors = 0
            state.backoff_until = 0.0
        else:
            state.consecutive_errors += 1
            # Exponential backoff: 2^errors seconds, max 300 seconds
            backoff_time = min(2 ** state.consecutive_errors, 300)
            state.backoff_until = time.time() + backoff_time
            self.logger.warning(f"Setting backoff for {domain}: {backoff_time}s")

    def _get_random_user_agent(self) -> str:
        """Get a random user agent string"""
        return random.choice(self.user_agents)

    def _is_allowed_content_type(self, content_type: str) -> bool:
        """Check if content type is allowed for processing"""
        if not content_type:
            return False

        # Extract main content type (before semicolon)
        main_type = content_type.split(';')[0].strip().lower()
        return main_type in self.allowed_content_types

    async def crawl_url(self, url: str, source_config: Dict[str, Any]) -> Optional[CrawlResult]:
        """Crawl a single URL with full error handling and compliance checking"""
        domain = self._get_domain(url)

        async with self.semaphore:
            # Check robots.txt compliance
            if not await self._check_robots_txt(url):
                self.logger.warning(f"URL blocked by robots.txt: {url}")
                return CrawlResult(
                    url=url,
                    success=False,
                    robots_compliant=False,
                    error="Blocked by robots.txt"
                )

            # Apply rate limiting
            await self._wait_for_rate_limit(domain)

            # Attempt crawl with retries
            for attempt in range(self.max_retries + 1):
                try:
                    result = await self._attempt_crawl(url, source_config)
                    self._update_rate_limit_state(domain, result.success)
                    return result

                except Exception as e:
                    self.logger.warning(f"Crawl attempt {attempt + 1} failed for {url}: {e}")
                    if attempt < self.max_retries:
                        # Wait before retry with exponential backoff
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        await asyncio.sleep(wait_time)
                    else:
                        self._update_rate_limit_state(domain, False)
                        return CrawlResult(
                            url=url,
                            success=False,
                            error=f"Max retries exceeded: {str(e)}"
                        )

    async def _attempt_crawl(self, url: str, source_config: Dict[str, Any]) -> CrawlResult:
        """Attempt to crawl a single URL"""
        start_time = time.time()

        headers = {
            'User-Agent': self._get_random_user_agent()
        }

        # Add any custom headers from source config
        if 'headers' in source_config:
            headers.update(source_config['headers'])

        async with self.session.get(url, headers=headers) as response:
            response_time = time.time() - start_time

            # Check if content type is allowed
            content_type = response.headers.get('content-type', '')
            if not self._is_allowed_content_type(content_type):
                return CrawlResult(
                    url=url,
                    success=False,
                    status_code=response.status,
                    content_type=content_type,
                    error=f"Unsupported content type: {content_type}",
                    response_time=response_time
                )

            # Check response status
            if response.status != 200:
                return CrawlResult(
                    url=url,
                    success=False,
                    status_code=response.status,
                    content_type=content_type,
                    error=f"HTTP {response.status}",
                    response_time=response_time
                )

            # Read content
            content = await response.read()

            # Check content size limits
            max_size = source_config.get('max_content_size', 50 * 1024 * 1024)  # 50MB default
            if len(content) > max_size:
                return CrawlResult(
                    url=url,
                    success=False,
                    status_code=response.status,
                    content_type=content_type,
                    error=f"Content too large: {len(content)} bytes",
                    response_time=response_time
                )

            return CrawlResult(
                url=url,
                success=True,
                status_code=response.status,
                content=content,
                content_type=content_type.split(';')[0].strip(),
                headers=dict(response.headers),
                response_time=response_time
            )

    async def discover_urls(self, base_url: str, discovery_config: Dict[str, Any]) -> List[str]:
        """Discover URLs from a base page using various strategies"""
        discovered_urls = set()

        try:
            # Crawl the discovery page
            result = await self.crawl_url(base_url, {})
            if not result or not result.success:
                self.logger.warning(f"Failed to crawl discovery page: {base_url}")
                return []

            # Parse HTML content
            if result.content_type == 'text/html':
                soup = BeautifulSoup(result.content, 'html.parser')

                # Find links based on CSS selectors
                selectors = discovery_config.get('link_selectors', ['a[href]'])
                for selector in selectors:
                    links = soup.select(selector)
                    for link in links:
                        href = link.get('href')
                        if href:
                            # Convert relative URLs to absolute
                            full_url = urljoin(base_url, href)

                            # Apply URL filters
                            if self._should_include_url(full_url, discovery_config):
                                discovered_urls.add(full_url)

                # Handle pagination
                pagination_config = discovery_config.get('pagination')
                if pagination_config:
                    pagination_urls = await self._discover_pagination_urls(
                        base_url, soup, pagination_config
                    )
                    discovered_urls.update(pagination_urls)

        except Exception as e:
            self.logger.error(f"Error discovering URLs from {base_url}: {e}")

        return list(discovered_urls)

    def _should_include_url(self, url: str, discovery_config: Dict[str, Any]) -> bool:
        """Check if URL should be included based on filters"""
        # Check include patterns
        include_patterns = discovery_config.get('include_patterns', [])
        if include_patterns:
            if not any(re.search(pattern, url, re.IGNORECASE) for pattern in include_patterns):
                return False

        # Check exclude patterns
        exclude_patterns = discovery_config.get('exclude_patterns', [])
        if exclude_patterns:
            if any(re.search(pattern, url, re.IGNORECASE) for pattern in exclude_patterns):
                return False

        # Check URL path depth limit
        max_depth = discovery_config.get('max_path_depth')
        if max_depth:
            path_parts = urlparse(url).path.strip('/').split('/')
            if len([p for p in path_parts if p]) > max_depth:
                return False

        return True

    async def _discover_pagination_urls(self, base_url: str, soup: BeautifulSoup,
                                      pagination_config: Dict[str, Any]) -> Set[str]:
        """Discover URLs from pagination"""
        pagination_urls = set()

        try:
            # Look for pagination links
            pagination_selector = pagination_config.get('selector', '.pagination a')
            page_links = soup.select(pagination_selector)

            for link in page_links:
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    pagination_urls.add(full_url)

            # Handle numbered pagination
            max_pages = pagination_config.get('max_pages', 10)
            page_param = pagination_config.get('page_parameter', 'page')

            if max_pages > 1:
                base_parsed = urlparse(base_url)
                query_params = parse_qs(base_parsed.query)

                for page_num in range(2, max_pages + 1):
                    query_params[page_param] = [str(page_num)]
                    new_query = urlencode(query_params, doseq=True)

                    paginated_url = base_parsed._replace(query=new_query).geturl()
                    pagination_urls.add(paginated_url)

        except Exception as e:
            self.logger.error(f"Error discovering pagination URLs: {e}")

        return pagination_urls

    async def bulk_crawl(self, urls: List[str], source_config: Dict[str, Any]) -> List[CrawlResult]:
        """Crawl multiple URLs concurrently"""
        self.logger.info(f"Starting bulk crawl of {len(urls)} URLs")

        if not self.session:
            await self._create_session()

        tasks = []
        for url in urls:
            task = self.crawl_url(url, source_config)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Exception crawling {urls[i]}: {result}")
            elif result:
                valid_results.append(result)

        success_count = sum(1 for r in valid_results if r.success)
        self.logger.info(f"Bulk crawl completed: {success_count}/{len(valid_results)} successful")

        return valid_results

    def get_crawl_statistics(self) -> Dict[str, Any]:
        """Get crawling statistics and rate limit states"""
        stats = {
            'rate_limit_states': {},
            'robots_cache_size': len(self.robots_cache),
            'active_domains': len(self.rate_limit_states)
        }

        for domain, state in self.rate_limit_states.items():
            stats['rate_limit_states'][domain] = {
                'consecutive_errors': state.consecutive_errors,
                'in_backoff': time.time() < state.backoff_until,
                'backoff_remaining': max(0, state.backoff_until - time.time())
            }

        return stats


# Utility functions for URL validation and normalization
class URLValidator:
    """Utility class for URL validation and normalization"""

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL for deduplication"""
        parsed = urlparse(url.lower())

        # Remove common tracking parameters
        tracking_params = {
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'fbclid', 'gclid', 'ref', 'source', 'campaign'
        }

        if parsed.query:
            query_params = parse_qs(parsed.query)
            filtered_params = {
                k: v for k, v in query_params.items()
                if k.lower() not in tracking_params
            }
            new_query = urlencode(filtered_params, doseq=True)
        else:
            new_query = ''

        # Remove fragment
        normalized = parsed._replace(query=new_query, fragment='').geturl()

        # Remove trailing slash for consistency
        if normalized.endswith('/') and normalized.count('/') > 2:
            normalized = normalized.rstrip('/')

        return normalized

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid and crawlable"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False

            if parsed.scheme not in ('http', 'https'):
                return False

            # Check for common non-crawlable patterns
            non_crawlable_patterns = [
                r'\.(?:jpg|jpeg|png|gif|ico|css|js|zip|pdf)(?:\?|$)',
                r'#',  # Fragment-only URLs
                r'javascript:',
                r'mailto:',
                r'tel:',
                r'ftp:'
            ]

            for pattern in non_crawlable_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return False

            return True

        except Exception:
            return False


if __name__ == "__main__":
    import asyncio

    async def test_crawler():
        """Test the crawler functionality"""
        crawler = ThinkTankCrawler(max_concurrent=3, min_delay=1.0)

        test_urls = [
            "https://www.csis.org/programs/china-power",
            "https://www.aspi.org.au/research/critical-technology",
        ]

        async with crawler:
            results = await crawler.bulk_crawl(test_urls, {})

            for result in results:
                print(f"URL: {result.url}")
                print(f"Success: {result.success}")
                print(f"Status: {result.status_code}")
                print(f"Content Type: {result.content_type}")
                print(f"Size: {len(result.content) if result.content else 0} bytes")
                print(f"Response Time: {result.response_time:.2f}s")
                print("---")

    # Run test
    # asyncio.run(test_crawler())
