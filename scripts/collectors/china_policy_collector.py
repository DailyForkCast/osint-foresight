#!/usr/bin/env python3
"""
China Policy & Research Collector — Safe Mode
STRICT RULES:
- NEVER access .gov.cn, .edu.cn, or .cn domains directly
- Use Common Crawl, Wayback, Archive.today only
- Taiwan (.tw) IS NOT CHINA
"""

import json
import time
import hashlib
import logging
import requests
import yaml
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from urllib.parse import urlparse
import tempfile
import os
import platform

# Platform-specific file locking
if platform.system() == 'Windows':
    import msvcrt
    USE_FCNTL = False
else:
    import fcntl
    USE_FCNTL = True

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
OUTPUT_ROOT = Path("F:/China_Sweeps")
STATE_FILE = OUTPUT_ROOT / "STATE" / "china_state.json"
POLICY_OVERRIDES_FILE = OUTPUT_ROOT / "POLICY_OVERRIDES.yaml"
QA_DIR = OUTPUT_ROOT / "QA"

# Safety rules
FORBIDDEN_DOMAINS = ['.gov.cn', '.edu.cn', '.cn']
FORBIDDEN_TLD = ['.cn']
ALLOWED_METHODS = ['commoncrawl', 'wayback', 'archive_today', 'api', 'rss']

# Buckets
BUCKETS = [
    'CENTRAL_GOV', 'MINISTRIES', 'ACADEMIA', 'STANDARDS',
    'SOE_SASAC', 'PROVINCIAL', 'SECONDARY', 'FOREIGN_COOP'
]

# Publisher types
PUBLISHER_TYPES = [
    'central', 'ministry', 'agency', 'academia', 'standards',
    'soe', 'provincial', 'secondary', 'foreign_coop'
]

# Document types
DOCUMENT_TYPES = [
    'white_paper', 'plan', 'notice', 'regulation_summary',
    'program_brief', 'press_release', 'research_note',
    'mou', 'international_plan'
]


@dataclass
class PolicyDocument:
    """Normalized policy document record"""
    title: str
    publisher_org: str
    publisher_type: str
    document_type: str
    publication_date_iso: str
    date_source: str  # meta|inline|archive|inferred
    date_confidence: str  # high|medium|low
    manual_validated: bool
    canonical_url: str
    archive_url: Optional[str] = None
    archive_timestamp: Optional[str] = None
    provenance_chain: List[str] = field(default_factory=list)
    download_url: Optional[str] = None
    saved_path: Optional[str] = None
    file_ext: Optional[str] = None
    file_size_bytes: Optional[int] = None
    hash_sha256: Optional[str] = None
    text_hash_sha256: Optional[str] = None
    pages: Optional[int] = None
    language: str = 'en'
    title_en: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    subtopics: List[str] = field(default_factory=list)
    region_or_province: Optional[str] = None
    plan_type: Optional[str] = None  # sectoral|provincial|thematic
    entities: List[str] = field(default_factory=list)
    foreign_equivalent_id: Optional[str] = None
    identifiers: Dict[str, str] = field(default_factory=dict)
    fetch_mode: str = ''
    extraction_ok: bool = True
    extraction_notes: str = ''
    redteam_reviewed: bool = False
    verified_safe_source: bool = False
    qa_issues: List[str] = field(default_factory=list)


class StateLock:
    """Atomic state file locking"""
    def __init__(self, state_path: Path):
        self.state_path = state_path
        self.lock_path = state_path.with_suffix('.lock')
        self.lock_file = None

    def __enter__(self):
        """Acquire exclusive lock"""
        self.lock_file = open(self.lock_path, 'w')
        fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX)
        logger.info(f"Acquired lock: {self.lock_path}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release lock"""
        if self.lock_file:
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
            self.lock_file.close()
            logger.info(f"Released lock: {self.lock_path}")


class StateManager:
    """Manage collection state with atomic commits"""

    def __init__(self, state_path: Path):
        self.state_path = state_path
        self.state = self.load_state()

    def load_state(self) -> Dict:
        """Load state from disk"""
        if self.state_path.exists():
            with open(self.state_path, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"State file not found: {self.state_path}")
            return self._init_state()

    def _init_state(self) -> Dict:
        """Initialize empty state"""
        return {
            "version": "1.0",
            "last_global_run_iso": None,
            "buckets": {
                bucket: {
                    "forward_watermark_iso": None,
                    "backfill_pointer_year": 2024,
                    "sources": {}
                }
                for bucket in BUCKETS
            }
        }

    def commit_state(self, new_state: Dict):
        """Atomically commit state to disk"""
        # Write to temp file
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=self.state_path.parent,
            prefix='.tmp_state_'
        )
        try:
            with os.fdopen(tmp_fd, 'w') as f:
                json.dump(new_state, f, indent=2)
                f.flush()
                os.fsync(f.fileno())

            # Atomic rename
            os.replace(tmp_path, self.state_path)
            logger.info(f"State committed: {self.state_path}")
            self.state = new_state
        except Exception as e:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise e

    def get_time_windows(self, bucket: str) -> Tuple[Optional[datetime], int]:
        """Get forward watermark and backfill year for bucket"""
        bucket_state = self.state['buckets'][bucket]

        watermark_iso = bucket_state.get('forward_watermark_iso')
        watermark = datetime.fromisoformat(watermark_iso) if watermark_iso else None
        backfill_year = bucket_state.get('backfill_pointer_year', 2024)

        return watermark, backfill_year


class SafeAccessValidator:
    """Validate that all access is through safe methods only"""

    @staticmethod
    def is_forbidden_domain(url: str) -> bool:
        """Check if URL is a forbidden Chinese domain"""
        # Ensure URL has a scheme for proper parsing
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        if not domain:
            return False  # Invalid URL

        # Check Taiwan FIRST (NOT forbidden)
        if domain.endswith('.tw'):
            return False

        # Check if ends with .cn (catch-all)
        if domain.endswith('.cn'):
            return True

        # Check forbidden domains (redundant but explicit)
        for forbidden in FORBIDDEN_DOMAINS:
            if forbidden in domain:
                return True

        return False

    @staticmethod
    def validate_access_method(url: str, method: str) -> Tuple[bool, str]:
        """Validate access method is safe"""
        if SafeAccessValidator.is_forbidden_domain(url):
            if method not in ALLOWED_METHODS:
                return False, f"FORBIDDEN: Direct access to Chinese domain: {url}"

        return True, "OK"

    @staticmethod
    def make_safe_url(url: str, method: str = 'wayback') -> Optional[str]:
        """Convert direct URL to safe archive URL"""
        if not SafeAccessValidator.is_forbidden_domain(url):
            return url  # Already safe

        if method == 'wayback':
            # Wayback Machine format: https://web.archive.org/web/{timestamp}id_/{url}
            return f"https://web.archive.org/web/id_/{url}"
        elif method == 'archive_today':
            # Archive.today format: https://archive.today/{url}
            return f"https://archive.today/{url}"
        else:
            logger.warning(f"Cannot make safe URL for method: {method}")
            return None


class CommonCrawlClient:
    """Query Common Crawl index for safe offline access"""

    CC_INDEX_SERVER = "https://index.commoncrawl.org"

    def __init__(self):
        self.session = requests.Session()

    def search_domain(self, domain: str, start_date: str = '2010',
                     end_date: str = '2025') -> List[Dict]:
        """Search Common Crawl index for domain snapshots"""
        results = []

        # Get available indexes
        indexes = self._get_available_indexes()

        for index in indexes:
            # Query index for domain
            query_url = f"{self.CC_INDEX_SERVER}/{index}-index"
            params = {
                'url': f"*.{domain}/*",
                'matchType': 'domain',
                'output': 'json'
            }

            try:
                response = self.session.get(query_url, params=params, timeout=30)
                if response.status_code == 200:
                    for line in response.text.strip().split('\n'):
                        if line:
                            record = json.loads(line)
                            results.append({
                                'url': record.get('url'),
                                'timestamp': record.get('timestamp'),
                                'status': record.get('status'),
                                'mime': record.get('mime'),
                                'length': record.get('length'),
                                'filename': record.get('filename'),
                                'offset': record.get('offset'),
                                'index': index
                            })
            except Exception as e:
                logger.error(f"Common Crawl query error for {domain}: {e}")

        return results

    def _get_available_indexes(self) -> List[str]:
        """Get list of available Common Crawl indexes"""
        try:
            response = self.session.get(
                f"{self.CC_INDEX_SERVER}/collinfo.json",
                timeout=10
            )
            if response.status_code == 200:
                indexes = response.json()
                return [idx['id'] for idx in indexes]
        except Exception as e:
            logger.error(f"Failed to fetch CC indexes: {e}")

        # Fallback to recent indexes
        return [
            'CC-MAIN-2024-10', 'CC-MAIN-2024-22',
            'CC-MAIN-2023-50', 'CC-MAIN-2023-14'
        ]


class WaybackClient:
    """Access Wayback Machine snapshots"""

    WAYBACK_API = "https://archive.org/wayback/available"

    def __init__(self):
        self.session = requests.Session()

    def get_snapshot(self, url: str, timestamp: Optional[str] = None) -> Optional[Dict]:
        """Get Wayback Machine snapshot for URL"""
        params = {'url': url}
        if timestamp:
            params['timestamp'] = timestamp

        try:
            response = self.session.get(self.WAYBACK_API, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('archived_snapshots', {}).get('closest'):
                    snapshot = data['archived_snapshots']['closest']
                    return {
                        'archive_url': snapshot['url'],
                        'timestamp': snapshot['timestamp'],
                        'status': snapshot.get('status', '200'),
                        'available': snapshot.get('available', True)
                    }
        except Exception as e:
            logger.error(f"Wayback API error for {url}: {e}")

        return None


class SitemapValidator:
    """Validate sitemap dates against page metadata"""

    def __init__(self, qa_dir: Path):
        self.qa_dir = qa_dir
        self.validation_log = []

    def validate_date(self, domain: str, sitemap_date: str,
                     page_html: str, url: str) -> Dict:
        """Cross-check sitemap date against page metadata"""
        page_date = self._extract_page_date(page_html)

        if page_date:
            sitemap_dt = datetime.fromisoformat(sitemap_date)
            page_dt = datetime.fromisoformat(page_date)
            diff_days = abs((sitemap_dt - page_dt).days)

            verified = diff_days <= 7  # Within 1 week
            mismatch = diff_days > 30  # More than 1 month

            result = {
                'domain': domain,
                'url': url,
                'sitemap_date': sitemap_date,
                'page_date': page_date,
                'diff_days': diff_days,
                'verified': verified,
                'mismatch': mismatch
            }

            self.validation_log.append(result)
            return result

        return {
            'domain': domain,
            'url': url,
            'sitemap_date': sitemap_date,
            'page_date': None,
            'diff_days': None,
            'verified': False,
            'mismatch': False
        }

    def _extract_page_date(self, html: str) -> Optional[str]:
        """Extract date from page HTML"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Check meta tags
        date_meta = soup.find('meta', {'name': 'date'})
        if date_meta and date_meta.get('content'):
            return date_meta['content']

        pub_meta = soup.find('meta', {'property': 'article:published_time'})
        if pub_meta and pub_meta.get('content'):
            return pub_meta['content']

        # Check schema.org
        ld_json = soup.find('script', {'type': 'application/ld+json'})
        if ld_json:
            try:
                data = json.loads(ld_json.string)
                if 'datePublished' in data:
                    return data['datePublished']
            except:
                pass

        return None

    def save_log(self, run_date: str):
        """Save validation log to CSV"""
        log_file = self.qa_dir / f"sitemap_validation_{run_date}.csv"

        if self.validation_log:
            import csv
            with open(log_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'domain', 'url', 'sitemap_date', 'page_date',
                    'diff_days', 'verified', 'mismatch'
                ])
                writer.writeheader()
                writer.writerows(self.validation_log)

            logger.info(f"Saved sitemap validation log: {log_file}")


class ChinaPolicyCollector:
    """Main collector with safe-mode enforcement"""

    def __init__(self):
        self.output_root = OUTPUT_ROOT
        self.state_manager = StateManager(STATE_FILE)
        self.safe_validator = SafeAccessValidator()
        self.cc_client = CommonCrawlClient()
        self.wayback_client = WaybackClient()
        self.sitemap_validator = SitemapValidator(QA_DIR)

        self.documents = []
        self.failures = []
        self.run_stats = {
            'start_time': datetime.now(timezone.utc).isoformat(),
            'requests_total': 0,
            'requests_safe': 0,
            'requests_blocked': 0,
            'documents_found': 0,
            'documents_saved': 0
        }

    def collect_bucket(self, bucket: str):
        """Collect documents for a bucket"""
        logger.info(f"Starting collection for bucket: {bucket}")

        # Get time windows
        watermark, backfill_year = self.state_manager.get_time_windows(bucket)

        # Lane A: Forward from watermark (2025+)
        lane_a_start = watermark if watermark else datetime(2025, 1, 1, tzinfo=timezone.utc)

        # Lane B: Backfill one year
        lane_b_start = datetime(backfill_year, 1, 1, tzinfo=timezone.utc)
        lane_b_end = datetime(backfill_year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

        logger.info(f"Lane A: {lane_a_start.isoformat()} → present")
        logger.info(f"Lane B: {lane_b_start.isoformat()} → {lane_b_end.isoformat()}")

        # TODO: Implement discovery and collection
        # This is a placeholder for the full implementation

        return self.documents

    def save_outputs(self, bucket: str, run_date: str):
        """Save all outputs for a bucket"""
        bucket_dir = self.output_root / bucket / run_date
        bucket_dir.mkdir(parents=True, exist_ok=True)

        # Save items.json
        items_file = bucket_dir / "items.json"
        with open(items_file, 'w') as f:
            json.dump([asdict(doc) for doc in self.documents], f, indent=2)

        logger.info(f"Saved {len(self.documents)} documents to {items_file}")

        # Save failures
        if self.failures:
            failures_file = bucket_dir / "download_failures.md"
            with open(failures_file, 'w') as f:
                f.write("# Download Failures\n\n")
                for failure in self.failures:
                    f.write(f"- [{failure['timestamp']}] {failure['url']}: {failure['reason']}\n")

        # Save run summary
        summary_file = bucket_dir / "run_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(self.run_stats, f, indent=2)

        logger.info(f"Saved run summary to {summary_file}")


def main():
    """Main execution"""
    logger.info("China Policy Collector — Safe Mode")
    logger.info("=" * 60)
    logger.info("SAFETY RULES:")
    logger.info("- NEVER access .gov.cn, .edu.cn, or .cn domains directly")
    logger.info("- Use Common Crawl, Wayback, Archive.today only")
    logger.info("- Taiwan (.tw) IS NOT CHINA")
    logger.info("=" * 60)

    collector = ChinaPolicyCollector()

    # Test bucket
    run_date = datetime.now(timezone.utc).strftime('%Y%m%d')

    with StateLock(STATE_FILE):
        collector.collect_bucket('SECONDARY')
        collector.save_outputs('SECONDARY', run_date)
        collector.sitemap_validator.save_log(run_date)


if __name__ == '__main__':
    main()
