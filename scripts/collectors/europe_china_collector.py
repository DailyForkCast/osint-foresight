#!/usr/bin/env python3
"""
Europe-China Policy & Research Collector
Safe Mode (Mirrors Only, Incremental, Revised v2)

Purpose: Safely collect archived documents from Chinese sources discussing
Europe, Arctic, and China-Europe policy intersections.

Safety: SAFE_MODE_MIRROR_ONLY enforced - zero live .cn domain access
"""

import json
import os
import sys
import hashlib
import time
import re
import csv
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Tuple, Set
import logging

# Third-party imports
try:
    import requests
    from bs4 import BeautifulSoup
    import langdetect
    from langdetect import detect, detect_langs
except ImportError as e:
    print(f"ERROR: Missing required package: {e}")
    print("Install with: pip install requests beautifulsoup4 langdetect lxml")
    sys.exit(1)

# Configuration
ROOT_DIR = Path("F:/Europe_China_Sweeps")
STATE_FILE = ROOT_DIR / "STATE" / "europe_china_state.json"
CONFIG_FILE = ROOT_DIR / "STATE" / "europe_china_sources_config.json"
COUNTRY_ALIASES = ROOT_DIR / "STATE" / "aliases_country.json"
REGION_ALIASES = ROOT_DIR / "STATE" / "aliases_region.json"
LOCK_FILE = ROOT_DIR / "STATE" / "europe_china_state.lock"

# Safety constants - NON-NEGOTIABLE
SAFE_MODE_MIRROR_ONLY = True
ALLOWED_ARCHIVE_HOSTS = {
    "web.archive.org",
    "archive.org",
    "archive.today",
    "archive.is",
    "arweave.net"
}
BLOCKED_TLDS = {".cn", ".gov.cn", ".edu.cn", ".org.cn", ".com.cn"}

# URL patterns to skip (non-content pages)
SKIP_URL_PATTERNS = [
    "/about", "/about-us", "/contact", "/careers", "/jobs",
    "/privacy", "/terms", "/legal", "/cookies", "/disclaimer",
    "/support", "/help", "/faq", "/our-team", "/leadership",
    "/board", "/staff", "/fellows", "/experts",
    "/newsletter", "/subscribe", "/donate", "/support-", "/join",
    "/events/past", "/event/", "/upcoming-event",
    "/sitemap", "/search", "/category/", "/tag/",
    "/media", "/press", "/for-media",
    "/our-culture", "/benefits", "/internship", "/apply",
    "/how-to-", "/registration", "/annual-report",
    # Chinese-specific patterns
    "/yxdl/",  # email login
    "/gyygk/",  # about us
    "/yjry/",  # research staff/personnel
    "/english"  # language switcher
]

# Generic title patterns to skip (navigation pages, not actual content)
SKIP_TITLE_PATTERNS = [
    "about us", "contact", "careers", "privacy policy", "terms of use",
    "our team", "our culture", "leadership", "board of trustees",
    "support", "donate", "newsletter", "subscribe",
    "past events", "upcoming events", "events",
    "for media", "press", "media",
    "benefits", "internships", "jobs", "apply",
    "sitemap", "search results", "home", "homepage",
    # Chinese equivalents
    "关于我们", "联系我们", "加入我们", "招聘", "网站地图"
]

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(ROOT_DIR / "logs" / f"europe_china_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SafetyViolationError(Exception):
    """Raised when SAFE_MODE_MIRROR_ONLY policy is violated"""
    pass


class StateLockError(Exception):
    """Raised when state file lock cannot be acquired"""
    pass


class SafetyEnforcer:
    """Enforces SAFE_MODE_MIRROR_ONLY policy - zero tolerance for violations"""

    def __init__(self):
        self.violations = []
        self.fatal_violation_occurred = False

    def check_url(self, url: str) -> Tuple[bool, str]:
        """
        Check if URL is safe (archive-only).
        Returns: (is_safe, reason)
        """
        if not url:
            return False, "Empty URL"

        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            return False, "No hostname in URL"

        # Check if archive host
        if hostname in ALLOWED_ARCHIVE_HOSTS:
            return True, "Archive host approved"

        # Check for any ALLOWED_ARCHIVE_HOSTS as substring (e.g., web.archive.org)
        if any(archive_host in hostname for archive_host in ALLOWED_ARCHIVE_HOSTS):
            return True, "Archive host approved (substring match)"

        # Check for blocked TLDs
        for blocked_tld in BLOCKED_TLDS:
            if hostname.endswith(blocked_tld):
                violation = f"FATAL: Blocked TLD detected: {hostname} ends with {blocked_tld}"
                self.violations.append({
                    "url": url,
                    "hostname": hostname,
                    "violation_type": "blocked_tld",
                    "timestamp": datetime.utcnow().isoformat()
                })
                return False, violation

        # Not an archive, not blocked, but not explicitly allowed
        violation = f"VIOLATION: Non-archive host not allowed: {hostname}"
        self.violations.append({
            "url": url,
            "hostname": hostname,
            "violation_type": "non_archive_host",
            "timestamp": datetime.utcnow().isoformat()
        })
        return False, violation

    def abort_run(self, reason: str):
        """Write fatal_violation.json and abort"""
        self.fatal_violation_occurred = True
        violation_file = ROOT_DIR / "fatal_violation.json"

        violation_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
            "violations": self.violations,
            "safe_mode_mirror_only": SAFE_MODE_MIRROR_ONLY,
            "allowed_hosts": list(ALLOWED_ARCHIVE_HOSTS),
            "blocked_tlds": list(BLOCKED_TLDS)
        }

        with open(violation_file, 'w', encoding='utf-8') as f:
            json.dump(violation_data, f, indent=2, ensure_ascii=False)

        logger.critical(f"FATAL VIOLATION: {reason}")
        logger.critical(f"Violation report written to: {violation_file}")
        raise SafetyViolationError(reason)


class StateManager:
    """Manages incremental state with file locking"""

    def __init__(self):
        self.state = None
        self.lock_acquired = False

    def acquire_lock(self, timeout: int = 30):
        """Acquire exclusive lock on state file"""
        wait_time = 0
        while LOCK_FILE.exists() and wait_time < timeout:
            logger.warning(f"State file locked, waiting... ({wait_time}s)")
            time.sleep(1)
            wait_time += 1

        if LOCK_FILE.exists():
            raise StateLockError(f"Could not acquire lock after {timeout}s")

        # Create lock file
        LOCK_FILE.write_text(json.dumps({
            "locked_at": datetime.utcnow().isoformat(),
            "pid": os.getpid()
        }))

        self.lock_acquired = True
        logger.info("State lock acquired")

    def release_lock(self):
        """Release state file lock"""
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
        self.lock_acquired = False
        logger.info("State lock released")

    def load_state(self) -> Dict:
        """Load state from file, initialize if missing"""
        if not STATE_FILE.exists():
            logger.warning("State file not found, initializing...")
            self.state = self._initialize_state()
            self.save_state()
        else:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                self.state = json.load(f)

        logger.info(f"State loaded: version {self.state.get('version')}")
        return self.state

    def save_state(self):
        """Save state atomically"""
        temp_file = STATE_FILE.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

        # Atomic rename
        temp_file.replace(STATE_FILE)
        logger.info("State saved successfully")

    def _initialize_state(self) -> Dict:
        """Initialize fresh state"""
        return {
            "version": "1.0",
            "last_global_run_iso": None,
            "buckets": {
                "CHINA_SOURCES": {
                    "forward_watermark_iso": None,
                    "backfill_pointer_year": 2024,
                    "sources": {}
                },
                "ARCHIVED_MEDIA": {
                    "forward_watermark_iso": None,
                    "backfill_pointer_year": 2024,
                    "sources": {}
                },
                "THINK_TANKS": {
                    "forward_watermark_iso": None,
                    "backfill_pointer_year": 2024,
                    "sources": {}
                },
                "ACADEMIA": {
                    "forward_watermark_iso": None,
                    "backfill_pointer_year": 2024,
                    "sources": {}
                },
                "OPEN_DATA": {
                    "forward_watermark_iso": None,
                    "backfill_pointer_year": 2024,
                    "sources": {}
                }
            }
        }


class WaybackDiscovery:
    """Discover snapshots via Wayback Machine CDX API"""

    def __init__(self, safety_enforcer: SafetyEnforcer):
        self.safety = safety_enforcer
        self.base_url = "https://web.archive.org/cdx/search/cdx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Europe-China-Research-Collector/1.0 (Educational Research; Safe Archive Access Only)'
        })

    def discover_snapshots(self, original_url: str, from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Discover Wayback snapshots for a URL.

        Args:
            original_url: The original URL to search for
            from_date: Start date (YYYYMMDD format)
            to_date: End date (YYYYMMDD format)

        Returns:
            List of snapshot dictionaries
        """
        logger.info(f"Discovering Wayback snapshots for: {original_url}")

        params = {
            'url': original_url,
            'output': 'json',
            'fl': 'timestamp,original,statuscode,mimetype,length,digest',
            'filter': 'statuscode:200',
            'collapse': 'digest'
        }

        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date

        try:
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            if not data or len(data) < 2:  # First row is header
                logger.warning(f"No snapshots found for {original_url}")
                return []

            headers = data[0]
            snapshots = []

            for row in data[1:]:
                snapshot = dict(zip(headers, row))

                # Build archive URL
                timestamp = snapshot['timestamp']
                archive_url = f"https://web.archive.org/web/{timestamp}/{snapshot['original']}"

                # Safety check
                is_safe, reason = self.safety.check_url(archive_url)
                if not is_safe:
                    logger.error(f"Safety violation in Wayback URL: {reason}")
                    continue

                snapshots.append({
                    'archive_url': archive_url,
                    'archive_timestamp': timestamp,
                    'original_url': snapshot['original'],
                    'status_code': snapshot.get('statuscode'),
                    'mimetype': snapshot.get('mimetype'),
                    'length': snapshot.get('length'),
                    'digest': snapshot.get('digest'),
                    'archive_platform': 'wayback'
                })

            logger.info(f"Found {len(snapshots)} valid snapshots")
            return snapshots

        except Exception as e:
            logger.error(f"Error discovering snapshots: {e}")
            return []


class DocumentExtractor:
    """Extract and normalize documents from archives"""

    def __init__(self, safety_enforcer: SafetyEnforcer):
        self.safety = safety_enforcer
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Europe-China-Research-Collector/1.0 (Educational Research; Safe Archive Access Only)'
        })

    def should_skip_url(self, url: str) -> bool:
        """Check if URL is a non-content page that should be skipped."""
        url_lower = url.lower()
        for pattern in SKIP_URL_PATTERNS:
            if pattern in url_lower:
                return True
        return False

    def extract_article_links(self, homepage_snapshot: Dict, base_domain: str, keywords: List[str] = None) -> Set[str]:
        """
        Extract article/report links from homepage snapshot.

        Args:
            homepage_snapshot: Homepage snapshot dictionary
            base_domain: Base domain to filter links (e.g., 'ciis.org.cn')
            keywords: Optional keywords to filter article URLs by title/text

        Returns:
            Set of article URLs found on homepage
        """
        archive_url = homepage_snapshot['archive_url']
        article_urls = set()

        logger.info(f"Extracting article links from: {archive_url}")

        try:
            # CRITICAL SAFETY: Disable redirect following
            response = self.session.get(archive_url, timeout=60, allow_redirects=False)

            # Handle redirects safely (same as extract_document)
            if response.status_code in (301, 302, 303, 307, 308):
                redirect_location = response.headers.get('Location', '')
                is_safe, reason = self.safety.check_url(redirect_location)
                if not is_safe:
                    logger.error(f"BLOCKED REDIRECT to unsafe URL: {redirect_location}")
                    return article_urls
                response = self.session.get(redirect_location, timeout=60, allow_redirects=False)

            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')

            # Remove scripts, styles, etc.
            for tag in soup(['script', 'style', 'iframe']):
                tag.decompose()

            # DEBUG: Track parsing stats
            total_links = 0
            constructed_urls = 0
            skipped_domain = 0
            skipped_patterns = 0
            matched_patterns = 0

            # Find all links
            for link in soup.find_all('a', href=True):
                total_links += 1
                href = link.get('href')

                # CRITICAL FIX: Wayback Machine rewrites ALL hrefs to include full archive URLs
                # Pattern: https://web.archive.org/web/20250102125229/http://www.qstheory.cn/zt2024/20szqh/index.htm
                # Extract the original URL before processing
                wayback_pattern = r'https?://web\.archive\.org/web/\d{14}/(.*)'
                wayback_match = re.match(wayback_pattern, href)
                if wayback_match:
                    href = wayback_match.group(1)  # Extract original URL (e.g., http://www.qstheory.cn/zt2024/20szqh/index.htm)

                # Make absolute URL
                if href.startswith('/'):
                    # Absolute path - construct from base domain
                    parsed_original = urlparse(homepage_snapshot['original_url'])
                    abs_url = f"{parsed_original.scheme}://{parsed_original.netloc}{href}"
                elif href.startswith('http'):
                    # Full URL
                    abs_url = href
                elif href.startswith('./'):
                    # Relative path with ./ prefix (e.g., ./yjcg/sspl/)
                    parsed_original = urlparse(homepage_snapshot['original_url'])
                    abs_url = f"{parsed_original.scheme}://{parsed_original.netloc}/{href[2:]}"
                elif not href.startswith(('#', 'javascript:', 'mailto:')):
                    # Plain relative path (e.g., economy/index.htm, qswp.htm)
                    # Common on Qiushi, People's Daily, and other Chinese sites
                    parsed_original = urlparse(homepage_snapshot['original_url'])
                    # Strip any trailing slash from netloc to avoid double slashes
                    base = f"{parsed_original.scheme}://{parsed_original.netloc}"
                    if not href.startswith('/'):
                        abs_url = f"{base}/{href}"
                    else:
                        abs_url = f"{base}{href}"
                else:
                    # Skip anchor links, javascript, mailto
                    continue

                constructed_urls += 1

                # Check if URL is from same domain
                parsed_url = urlparse(abs_url)
                if not parsed_url.hostname:
                    skipped_domain += 1
                    continue

                if base_domain not in parsed_url.hostname:
                    skipped_domain += 1
                    continue

                # Filter out navigation/non-article links
                # Skip homepage, search, login, etc.
                skip_patterns = [
                    '/search', '/login', '/contact', '/about',
                    '/sitemap', '/rss', '/feed', '.xml', '.pdf',
                    'javascript:', 'mailto:', '#', '/yxdl/',  # email login
                    '/gyygk/',  # about us
                    '/yjry/',  # research staff/personnel
                    '/english'  # language switcher
                ]

                if any(pattern in abs_url.lower() for pattern in skip_patterns):
                    skipped_patterns += 1
                    continue

                # Look for article patterns (English + Chinese think tank patterns)
                article_patterns = [
                    # English patterns
                    '/article/', '/articles/', '/research/', '/report/',
                    '/analysis/', '/commentary/', '/publication/',
                    '/view/', '/detail/', '/content/', '/show/',
                    '/info/', '/news/', '/insights/',
                    # Chinese think tank patterns
                    '/xwdt/',     # 新闻动态 (News)
                    '/yjcg/',     # 研究成果 (Research Outputs)
                    '/gjwtyj/',   # 国际问题研究 (International Issues Research)
                    '/sspl/',     # 时事评论 (Current Affairs Commentary)
                    '/zzybg/',    # 著作与报告 (Publications & Reports)
                    '/xslw/',     # 学术论文 (Academic Papers)
                ]

                # Check if link text contains keywords (if provided)
                link_text = link.get_text(strip=True).lower()
                if keywords and link_text:
                    # Check if any keyword appears in link text
                    if any(kw.lower() in link_text for kw in keywords):
                        article_urls.add(abs_url)
                        continue

                # Check if URL matches article patterns
                if any(pattern in abs_url.lower() for pattern in article_patterns):
                    article_urls.add(abs_url)
                    continue

                # Check for date-based article URLs (common in Chinese sites)
                # Pattern: /20XX/ (4-digit year like /2024/) or /20XXXX/ (year+month like /202412/)
                if re.search(r'/20\d{2}', abs_url):
                    article_urls.add(abs_url)
                    continue

                # Check for .html files that might be articles
                if '.html' in abs_url.lower() and abs_url != homepage_snapshot['original_url']:
                    article_urls.add(abs_url)

            logger.info(f"Found {len(article_urls)} potential article links")
            return article_urls

        except Exception as e:
            logger.error(f"Error extracting article links: {e}")
            return article_urls

    def extract_document(self, snapshot: Dict, keywords: List[str]) -> Optional[Dict]:
        """
        Extract document from archive snapshot.

        Args:
            snapshot: Snapshot dictionary from discovery
            keywords: Keywords to check for relevance

        Returns:
            Extracted document dictionary or None
        """
        archive_url = snapshot['archive_url']

        # Safety check
        is_safe, reason = self.safety.check_url(archive_url)
        if not is_safe:
            logger.error(f"Safety check failed: {reason}")
            self.safety.abort_run(f"Attempted to access unsafe URL: {archive_url}")
            return None

        logger.info(f"Extracting from: {archive_url}")

        try:
            # CRITICAL SAFETY: Disable redirect following
            response = self.session.get(archive_url, timeout=60, allow_redirects=False)

            # Check for HTTP redirects (301, 302, 303, 307, 308)
            if response.status_code in (301, 302, 303, 307, 308):
                redirect_location = response.headers.get('Location', '')
                is_safe, reason = self.safety.check_url(redirect_location)
                if not is_safe:
                    logger.error(f"BLOCKED REDIRECT to unsafe URL: {redirect_location}")
                    self.safety.abort_run(f"Attempted redirect to unsafe URL: {redirect_location} from {archive_url}")
                    return None
                # If redirect is to another archive URL, follow it manually
                logger.warning(f"Safe redirect detected to: {redirect_location}")
                response = self.session.get(redirect_location, timeout=60, allow_redirects=False)

            response.raise_for_status()

            # Verify final URL is still safe (in case of server-side redirect)
            final_url = response.url
            is_safe, reason = self.safety.check_url(final_url)
            if not is_safe:
                logger.error(f"Final URL is unsafe: {final_url}")
                self.safety.abort_run(f"Response URL changed to unsafe location: {final_url}")
                return None

            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')

            # Check for meta-refresh redirects (before removing tags)
            meta_refresh = soup.find('meta', attrs={'http-equiv': re.compile('refresh', re.I)})
            if meta_refresh:
                content = meta_refresh.get('content', '')
                # Extract URL from meta refresh (format: "0;URL=http://example.com")
                url_match = re.search(r'url\s*=\s*["\']?([^"\'>\s]+)', content, re.I)
                if url_match:
                    refresh_url = url_match.group(1)
                    # Make absolute if relative
                    if not refresh_url.startswith('http'):
                        refresh_url = urljoin(final_url, refresh_url)
                    is_safe, reason = self.safety.check_url(refresh_url)
                    if not is_safe:
                        logger.error(f"BLOCKED meta-refresh to unsafe URL: {refresh_url}")
                        self.safety.abort_run(f"Meta-refresh redirect to unsafe URL: {refresh_url}")
                        return None

            # Extract text
            # Remove scripts, styles, etc.
            for tag in soup(['script', 'style', 'iframe', 'nav', 'footer']):
                tag.decompose()

            text = soup.get_text(separator='\n', strip=True)

            # Check keyword relevance
            text_lower = text.lower()
            keyword_matches = [kw for kw in keywords if kw.lower() in text_lower]

            if not keyword_matches:
                logger.info(f"No keywords matched, skipping")
                return None

            # Extract title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else "No Title"

            # Check if title is generic (navigation page)
            title_lower = title_text.lower().strip()
            is_generic = False

            # Check for generic patterns
            for pattern in SKIP_TITLE_PATTERNS:
                if pattern in title_lower:
                    logger.info(f"Skipping generic title: {title_text[:100]}")
                    is_generic = True
                    break

            if is_generic:
                return None

            # Detect language
            try:
                lang_detections = detect_langs(text[:1000])  # First 1000 chars
                primary_lang = lang_detections[0]
                language = primary_lang.lang
                language_confidence = primary_lang.prob
            except:
                language = "unknown"
                language_confidence = 0.0

            # Compute hashes
            hash_sha256 = hashlib.sha256(response.content).hexdigest()
            text_hash_sha256 = hashlib.sha256(text.encode('utf-8')).hexdigest()

            # Build provenance chain
            provenance_chain = [
                {
                    "type": "archive",
                    "platform": snapshot['archive_platform'],
                    "snapshot_url": archive_url,
                    "timestamp_utc": self._parse_wayback_timestamp(snapshot['archive_timestamp']),
                    "status": snapshot.get('status_code'),
                    "sha256": hash_sha256
                },
                {
                    "type": "origin",
                    "url": snapshot['original_url'],
                    "domain_tld": self._extract_tld(snapshot['original_url'])
                }
            ]

            # Build document
            document = {
                "title": title_text,
                "canonical_url": snapshot['original_url'],
                "archive_url": archive_url,
                "archive_timestamp": snapshot['archive_timestamp'],
                "provenance_chain": provenance_chain,
                "file_size_bytes": len(response.content),
                "hash_sha256": hash_sha256,
                "text_hash_sha256": text_hash_sha256,
                "language": language,
                "language_confidence": language_confidence,
                "keywords_matched": keyword_matches,
                "text_preview": text[:500],
                "extraction_ok": True,
                "extraction_notes": f"Extracted via {snapshot['archive_platform']}, {len(keyword_matches)} keywords matched",
                "verified_safe_source": True,
                "requires_review": False,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully extracted: {title_text[:100]}")
            return document

        except Exception as e:
            logger.error(f"Error extracting document: {e}")
            return None

    def _parse_wayback_timestamp(self, timestamp: str) -> str:
        """Convert Wayback timestamp (YYYYMMDDhhmmss) to ISO format"""
        try:
            dt = datetime.strptime(timestamp, '%Y%m%d%H%M%S')
            return dt.isoformat() + 'Z'
        except:
            return timestamp

    def _extract_tld(self, url: str) -> str:
        """Extract TLD from URL"""
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        parts = hostname.split('.')
        if len(parts) >= 2:
            return '.' + '.'.join(parts[-2:])
        return hostname


class EuropeChinaCollector:
    """Main collector orchestrator"""

    def __init__(self):
        self.safety = SafetyEnforcer()
        self.state_mgr = StateManager()
        self.wayback = WaybackDiscovery(self.safety)
        self.extractor = DocumentExtractor(self.safety)
        self.config = None
        self.country_aliases = None
        self.region_aliases = None
        self.all_documents = []  # Track all documents for CSV export

    def slugify(self, text: str, max_length: int = 80) -> str:
        """Convert text to URL-friendly slug."""
        if not text:
            return "untitled"

        # Remove organization suffix (e.g., "| CIIS")
        text = re.sub(r'\s*[|\-–]\s*\w+\s*$', '', text)

        # Convert to lowercase
        text = text.lower()

        # Replace non-alphanumeric with hyphens
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)

        # Trim hyphens from ends
        text = text.strip('-')

        # Truncate to max length
        if len(text) > max_length:
            text = text[:max_length].rsplit('-', 1)[0]

        return text or "untitled"

    def get_source_slug(self, domain: str) -> str:
        """Get short slug for source organization."""
        # Remove www., .org.cn, .edu.cn, .gov.cn, .cn, etc.
        slug = domain.replace('www.', '')
        slug = re.sub(r'\.(org|edu|gov|com|net|int|mil)(\.(cn|uk|de|fr))?$', '', slug)

        # Take first part if multiple dots remain
        if '.' in slug:
            slug = slug.split('.')[0]

        return slug

    def is_generic_title(self, title: str) -> bool:
        """Check if title is generic (website navigation, not actual content)."""
        if not title or title == "No Title":
            return True

        title_lower = title.lower().strip()

        # Check if title ends with just organization name (e.g., "CIIS")
        if re.match(r'^[^|]+\|\s*\w+\s*$', title):
            before_pipe = title.split('|')[0].strip().lower()
            if len(before_pipe) < 20:
                for pattern in SKIP_TITLE_PATTERNS:
                    if pattern in before_pipe:
                        return True

        # Check for generic title patterns
        for pattern in SKIP_TITLE_PATTERNS:
            if pattern in title_lower:
                return True

        return False

    def generate_human_readable_filename(self, doc: Dict, source_id: str) -> str:
        """
        Generate human-readable filename.
        Format: YYYY-MM-DD_source-slug_title-slug.json
        """
        # Extract date from archive timestamp
        archive_timestamp = doc.get('archive_timestamp', '')
        try:
            if archive_timestamp:
                dt = datetime.strptime(archive_timestamp, '%Y%m%d%H%M%S')
                date_str = dt.strftime("%Y-%m-%d")
            else:
                date_str = datetime.utcnow().strftime("%Y-%m-%d")
        except:
            date_str = datetime.utcnow().strftime("%Y-%m-%d")

        # Get source slug
        source_slug = self.get_source_slug(source_id)

        # Get title slug
        title_slug = self.slugify(doc.get("title", "untitled"))

        # Combine
        filename = f"{date_str}_{source_slug}_{title_slug}.json"

        return filename

    def run(self, bucket_name: Optional[str] = None):
        """
        Run collection for specified bucket or all buckets.

        Args:
            bucket_name: Bucket to collect from (e.g., 'THINK_TANKS'), or None for all
        """
        logger.info("=" * 80)
        logger.info("Europe-China Policy & Research Collector - SAFE MODE")
        logger.info("=" * 80)
        logger.info(f"SAFE_MODE_MIRROR_ONLY: {SAFE_MODE_MIRROR_ONLY}")
        logger.info(f"Allowed archive hosts: {ALLOWED_ARCHIVE_HOSTS}")
        logger.info(f"Blocked TLDs: {BLOCKED_TLDS}")
        logger.info("=" * 80)

        try:
            # Load configuration
            self._load_config()

            # Acquire state lock
            self.state_mgr.acquire_lock()

            # Load state
            state = self.state_mgr.load_state()

            # Run preflight red-team tests
            self._run_preflight_tests()

            # Determine buckets to process
            if bucket_name:
                if bucket_name not in self.config['buckets']:
                    raise ValueError(f"Unknown bucket: {bucket_name}")
                buckets = {bucket_name: self.config['buckets'][bucket_name]}
            else:
                buckets = self.config['buckets']

            # Process each bucket
            results = {}
            for bucket_name, bucket_config in buckets.items():
                logger.info(f"\n{'=' * 80}")
                logger.info(f"Processing bucket: {bucket_name}")
                logger.info(f"{'=' * 80}")

                bucket_results = self._process_bucket(bucket_name, bucket_config, state)
                results[bucket_name] = bucket_results

            # Update state
            state['last_global_run_iso'] = datetime.utcnow().isoformat()
            self.state_mgr.save_state()

            # Generate reports
            self._generate_reports(results)

            logger.info("\n" + "=" * 80)
            logger.info("Collection completed successfully")
            logger.info("=" * 80)

        except SafetyViolationError as e:
            logger.critical(f"FATAL SAFETY VIOLATION: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Collection failed: {e}", exc_info=True)
            raise
        finally:
            # Always release lock
            if self.state_mgr.lock_acquired:
                self.state_mgr.release_lock()

    def _load_config(self):
        """Load configuration files"""
        logger.info("Loading configuration files...")

        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        with open(COUNTRY_ALIASES, 'r', encoding='utf-8') as f:
            self.country_aliases = json.load(f)

        with open(REGION_ALIASES, 'r', encoding='utf-8') as f:
            self.region_aliases = json.load(f)

        # Verify SAFE_MODE_MIRROR_ONLY
        if not self.config.get('safe_mode_mirror_only', False):
            raise SafetyViolationError("Configuration does not have safe_mode_mirror_only=true")

        logger.info("Configuration loaded successfully")

    def _run_preflight_tests(self):
        """Run preflight red-team safety tests"""
        logger.info("\nRunning preflight red-team tests...")

        tests = [
            ("Archive host approved", "https://web.archive.org/web/20250101000000/http://example.com", True),
            ("Blocked .cn TLD", "http://example.cn", False),
            ("Blocked .gov.cn TLD", "http://ministry.gov.cn", False),
            ("Non-archive host", "http://example.com", False),
        ]

        passed = 0
        failed = 0

        for test_name, test_url, expected_safe in tests:
            is_safe, reason = self.safety.check_url(test_url)
            if is_safe == expected_safe:
                logger.info(f"✓ PASS: {test_name}")
                passed += 1
            else:
                logger.error(f"✗ FAIL: {test_name} - Expected {expected_safe}, got {is_safe}")
                failed += 1

        logger.info(f"\nPreflight tests: {passed} passed, {failed} failed")

        if failed > 0:
            raise SafetyViolationError("Preflight tests failed - aborting run")

    def _process_bucket(self, bucket_name: str, bucket_config: Dict, state: Dict) -> Dict:
        """Process a single bucket using Option C: discover article links then extract"""
        sources = bucket_config.get('sources', [])
        logger.info(f"Found {len(sources)} sources in {bucket_name}")

        documents = []
        errors = []

        for source in sources:  # Process all configured sources
            source_id = source['id']
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Processing source: {source_id} - {source['name']}")
            logger.info(f"{'=' * 60}")

            try:
                # STAGE 1: Discover homepage snapshots
                logger.info(f"STAGE 1: Discovering homepage snapshots...")
                homepage_snapshots = self.wayback.discover_snapshots(
                    source['original_url'],
                    from_date='20250101'  # 2025 forward
                )

                if not homepage_snapshots:
                    logger.warning(f"No homepage snapshots found for {source_id}")
                    continue

                logger.info(f"Found {len(homepage_snapshots)} homepage snapshots")

                # STAGE 2: Extract article links from most recent homepage
                logger.info(f"STAGE 2: Extracting article links from homepage...")
                # Use most recent snapshot
                most_recent_homepage = homepage_snapshots[0]

                # Extract base domain
                parsed_url = urlparse(source['original_url'])
                base_domain = parsed_url.netloc

                # Extract article links (NO keyword filtering - filter happens at document extraction)
                article_urls = self.extractor.extract_article_links(
                    most_recent_homepage,
                    base_domain,
                    keywords=None  # Don't filter by keywords yet - links don't contain keywords
                )

                if not article_urls:
                    logger.warning(f"No article links found for {source_id}")
                    continue

                logger.info(f"Found {len(article_urls)} article URLs")

                # STAGE 3: Discover snapshots for article URLs and extract content
                logger.info(f"STAGE 3: Discovering snapshots for article URLs...")

                # Limit article URLs for test
                article_urls_list = list(article_urls)[:10]  # Max 10 articles per source for test

                for article_url in article_urls_list:
                    logger.info(f"Processing article: {article_url}")

                    # Discover snapshots for this article
                    article_snapshots = self.wayback.discover_snapshots(
                        article_url,
                        from_date='20250101'
                    )

                    if not article_snapshots:
                        logger.debug(f"No snapshots for article: {article_url}")
                        continue

                    # Extract from most recent snapshot of this article
                    article_snapshot = article_snapshots[0]
                    doc = self.extractor.extract_document(article_snapshot, source['keywords'])

                    if doc:
                        doc['source_id'] = source_id
                        doc['source_name'] = source['name']
                        doc['bucket'] = bucket_name
                        doc['publisher_type'] = bucket_config.get('publisher_type')
                        documents.append(doc)

                        # Save individual document
                        self._save_document(doc, bucket_name, source_id)

            except Exception as e:
                logger.error(f"Error processing source {source_id}: {e}")
                errors.append({
                    "source_id": source_id,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })

        return {
            "bucket": bucket_name,
            "sources_processed": len(sources),
            "documents_extracted": len(documents),
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _save_document(self, doc: Dict, bucket: str, source_id: str):
        """Save individual document with human-readable filename."""
        # Generate human-readable filename
        filename = self.generate_human_readable_filename(doc, source_id)

        # Save to RAW
        raw_dir = ROOT_DIR / "RAW" / bucket / source_id
        raw_dir.mkdir(parents=True, exist_ok=True)

        doc_file = raw_dir / filename

        # Handle filename collisions
        if doc_file.exists():
            # Append hash suffix
            hash_suffix = doc['hash_sha256'][:8]
            filename_base = filename.rsplit('.', 1)[0]
            filename = f"{filename_base}_{hash_suffix}.json"
            doc_file = raw_dir / filename

        # Add saved_path to document
        doc['saved_path'] = str(doc_file)

        # Save
        with open(doc_file, 'w', encoding='utf-8') as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved document: {doc_file}")

        # Track for CSV export
        self.all_documents.append(doc)

    def _generate_reports(self, results: Dict):
        """Generate collection reports"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

        report = {
            "run_timestamp": datetime.utcnow().isoformat(),
            "safe_mode_mirror_only": SAFE_MODE_MIRROR_ONLY,
            "buckets_processed": len(results),
            "total_documents": sum(r['documents_extracted'] for r in results.values()),
            "total_errors": sum(len(r['errors']) for r in results.values()),
            "results": results,
            "safety_violations": self.safety.violations
        }

        report_file = ROOT_DIR / "QA" / f"run_report_{timestamp}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Generate CSV exports
        self._generate_csv_exports(timestamp)

        logger.info(f"\nReport saved: {report_file}")
        logger.info(f"Total documents extracted: {report['total_documents']}")
        logger.info(f"Total errors: {report['total_errors']}")
        logger.info(f"Safety violations: {len(self.safety.violations)}")

    def _generate_csv_exports(self, timestamp: str):
        """Generate CSV exports for all collected documents."""
        if not self.all_documents:
            logger.warning("No documents to export to CSV")
            return

        merged_dir = ROOT_DIR / "MERGED" / timestamp[:8]  # YYYYMMDD
        merged_dir.mkdir(parents=True, exist_ok=True)

        # Generate items.csv
        items_csv_path = merged_dir / "items.csv"
        if self.all_documents:
            with open(items_csv_path, 'w', newline='', encoding='utf-8') as f:
                # Get all unique field names
                fieldnames = set()
                for doc in self.all_documents:
                    fieldnames.update(doc.keys())
                fieldnames = sorted(fieldnames)

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.all_documents)

            logger.info(f"CSV export created: {items_csv_path}")

        # Generate file_manifest.csv
        manifest_csv_path = merged_dir / "file_manifest.csv"
        with open(manifest_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "hash_sha256", "saved_path", "bytes", "archive_url",
                "canonical_url", "source_name", "title", "language"
            ])
            for doc in self.all_documents:
                writer.writerow([
                    doc.get("hash_sha256", ""),
                    doc.get("saved_path", ""),
                    doc.get("file_size_bytes", 0),
                    doc.get("archive_url", ""),
                    doc.get("canonical_url", ""),
                    doc.get("source_name", ""),
                    doc.get("title", ""),
                    doc.get("language", "")
                ])

        logger.info(f"File manifest created: {manifest_csv_path}")
        logger.info(f"Total documents exported: {len(self.all_documents)}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Europe-China Policy & Research Collector (Safe Mode)')
    parser.add_argument('--bucket', type=str, help='Bucket to process (default: all)')
    parser.add_argument('--test', action='store_true', help='Run in test mode (limited collection)')

    args = parser.parse_args()

    collector = EuropeChinaCollector()
    collector.run(bucket_name=args.bucket)


if __name__ == '__main__':
    main()
