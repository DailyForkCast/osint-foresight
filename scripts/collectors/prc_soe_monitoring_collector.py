#!/usr/bin/env python3
"""
PRC SOE Monitoring Collector
Automated monitoring of PRC state-owned enterprise mergers and consolidations

Purpose:
- Early warning for mergers affecting US government contracting
- Cross-reference with entity_mergers database
- Generate TIER_1 alerts for strategic consolidations
- Weekly/monthly/quarterly monitoring workflows

Architecture follows established sweep patterns:
- Bucket-based organization (SASAC, Stock Exchanges, State Media, Bloomberg/Reuters)
- State management with atomic commits
- Safe access rules (Wayback for .cn domains, direct for aggregators)
- QA validation and deduplication
- Integration with osint_master.db
"""

import sys
import json
import hashlib
import sqlite3
import logging
import time
import re
import requests
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from collections import Counter
import tempfile
import os

# Platform-specific locking
try:
    import fcntl
    PLATFORM_LOCK = 'fcntl'
except ImportError:
    try:
        import msvcrt
        PLATFORM_LOCK = 'msvcrt'
    except ImportError:
        PLATFORM_LOCK = None

# Setup logging
LOG_DIR = Path('F:/PRC_SOE_Sweeps/logs')
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f'monitoring_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
STATE_FILE = Path('F:/PRC_SOE_Sweeps/STATE/prc_soe_state.json')
DATA_DIR = Path('F:/PRC_SOE_Sweeps/data')
QA_DIR = Path('F:/PRC_SOE_Sweeps/QA')
ALERTS_DIR = Path('F:/PRC_SOE_Sweeps/alerts')
WAREHOUSE_DB = Path('F:/OSINT_WAREHOUSE/osint_master.db')

# Create directories
for directory in [STATE_FILE.parent, DATA_DIR, QA_DIR, ALERTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Merger detection keywords
MERGER_KEYWORDS = [
    # English
    'merger', 'acquisition', 'consolidation', 'restructuring', 'reorganization',
    'absorbed', 'combined', 'integrated', 'unified', 'merged into',
    'state-owned enterprise', 'SOE', 'SASAC',

    # Common merger verbs
    'acquire', 'merge', 'consolidate', 'restructure', 'absorb', 'integrate',
    'takeover', 'buyout', 'combine',

    # Chinese companies (transliterated)
    'COSCO', 'CRRC', 'CNOOC', 'Sinopec', 'ChemChina', 'Sinochem',
    'China Railway', 'China Shipbuilding', 'China State Shipbuilding',
]

# Strategic sectors (high priority)
STRATEGIC_SECTORS = [
    'Semiconductors', 'Telecommunications', 'AI', 'Quantum Computing',
    'Space', 'Nuclear', 'Maritime logistics', 'Rail equipment',
    'Energy storage', 'Rare earths', 'Advanced materials',
    'Biotechnology', 'Cybersecurity', 'Aerospace'
]

# Safety rules - CRITICAL: Never access .cn domains directly
FORBIDDEN_DOMAINS = ['.gov.cn', '.edu.cn', '.cn']
ALLOWED_ACCESS_METHODS = ['wayback', 'commoncrawl', 'archive_today', 'api', 'rss', 'direct']
SAFE_AGGREGATORS = [
    'bloomberg.com', 'reuters.com', 'wsj.com',
    'scmp.com', 'caixinglobal.com', 'ft.com',
    'nikkei.com', 'economist.com'
]

# Import for URL validation
from urllib.parse import urlparse

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class SOEMergerRecord:
    """Standardized SOE merger/consolidation record"""

    # Entity Identification
    legacy_entity_name: str
    legacy_entity_name_cn: Optional[str] = None
    legacy_entity_type: str = 'unknown'  # subsidiary, parent, division, joint_venture
    current_parent: str = ''
    merged_into: str = ''

    # Merger Metadata
    merger_date_iso: str = ''
    merger_announcement_date_iso: str = ''
    merger_type: str = 'unknown'  # absorption, consolidation, restructuring, divestiture
    strategic_sector: str = ''

    # Market Impact
    pre_merger_rank_domestic: Optional[int] = None
    post_merger_rank_domestic: Optional[int] = None
    pre_merger_rank_global: Optional[int] = None
    post_merger_rank_global: Optional[int] = None
    combined_market_share_pct: Optional[float] = None

    # Intelligence Value
    importance_tier: str = 'TIER_3'  # Default to TIER_3

    # US Government Contracting
    us_contracting_history: bool = False
    us_contracting_count: int = 0
    us_contracting_value_usd: float = 0.0
    us_contracting_last_date_iso: Optional[str] = None

    # European Government/Organization Contracting (TED - Tenders Electronic Daily)
    eu_contracting_history: bool = False
    eu_contracting_count: int = 0
    eu_contracting_countries: List[str] = field(default_factory=list)  # List of EU countries contracted with
    eu_contracting_last_date_iso: Optional[str] = None

    # Detection & Classification
    detection_method: str = 'keyword'
    detection_confidence: float = 0.0
    keywords_matched: List[str] = field(default_factory=list)

    # Source Tracking
    source_url: str = ''
    source_archive_url: Optional[str] = None
    source_type: str = ''  # sasac, stock_exchange, state_media, news, filing
    source_publisher: str = ''
    source_language: str = 'en'
    source_date_iso: str = ''

    # Content
    title: str = ''
    title_en: Optional[str] = None
    summary: Optional[str] = None
    full_text_excerpt: Optional[str] = None

    # Processing Metadata
    detection_timestamp_iso: str = ''
    extraction_ok: bool = True
    extraction_notes: Optional[str] = None
    verified: bool = False
    verified_by: Optional[str] = None
    verified_date_iso: Optional[str] = None

    # Technical Metadata
    hash_sha256: str = ''
    text_hash_sha256: str = ''
    file_size_bytes: Optional[int] = None

    # Cross-References
    entity_merger_db_id: Optional[int] = None
    usaspending_transaction_ids: List[str] = field(default_factory=list)
    patent_numbers: List[str] = field(default_factory=list)
    sec_cik_numbers: List[str] = field(default_factory=list)


# ============================================================================
# SAFETY VALIDATION
# ============================================================================

class SafeAccessValidator:
    """
    Validate that all access is through safe methods only.

    CRITICAL: This class enforces the absolute rule that we NEVER
    directly access .cn domains. All Chinese government sources must
    be accessed through archives (Wayback Machine, Common Crawl, etc.)
    or safe Western aggregators (Bloomberg, Reuters, etc.).
    """

    @staticmethod
    def is_forbidden_domain(url: str) -> bool:
        """
        Check if URL is a forbidden Chinese domain.

        Returns True if URL is a .cn domain that should NOT be accessed directly.
        """
        # Ensure URL has a scheme for proper parsing
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        if not domain:
            return False  # Invalid URL

        # Check Taiwan FIRST (NOT forbidden - .tw is okay)
        if domain.endswith('.tw'):
            return False

        # Check if ends with .cn (catch-all for ANY .cn domain)
        # Use endswith() to avoid false positives like "cnbc.com"
        if domain.endswith('.cn'):
            logger.warning(f"FORBIDDEN DOMAIN DETECTED: {domain}")
            return True

        # Check specific forbidden patterns (gov.cn, edu.cn, com.cn)
        forbidden_patterns = ['.gov.cn', '.edu.cn', '.com.cn']
        for pattern in forbidden_patterns:
            if domain.endswith(pattern):
                logger.warning(f"FORBIDDEN DOMAIN DETECTED: {domain} (matched: {pattern})")
                return True

        return False

    @staticmethod
    def validate_access_method(url: str, method: str) -> Tuple[bool, str]:
        """
        Validate access method is safe.

        Returns:
            (is_valid, message)
        """
        # Check if trying to access forbidden .cn domain
        if SafeAccessValidator.is_forbidden_domain(url):
            if method not in ALLOWED_ACCESS_METHODS:
                return False, f"FORBIDDEN: Direct access to Chinese domain: {url}"
            elif method not in ['wayback', 'commoncrawl', 'archive_today']:
                return False, f"FORBIDDEN: Chinese domain must use archive access: {url}"

        # CRITICAL: If method is 'direct', domain MUST be in SAFE_AGGREGATORS
        if method == 'direct':
            # Parse domain from URL
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Check if domain is in safe aggregators
            is_safe = any(safe in domain for safe in SAFE_AGGREGATORS)
            if not is_safe:
                return False, f"FORBIDDEN: Direct access only allowed to safe aggregators (Bloomberg, Reuters, WSJ, etc.), not: {domain}"

        return True, "OK"

    @staticmethod
    def validate_source_config(source: Dict) -> Tuple[bool, str]:
        """
        Validate source configuration is safe.

        Checks:
        1. Access method is allowed
        2. If domain is .cn, access method must be archive
        3. If method is 'direct', domain must be in SAFE_AGGREGATORS
        """
        domain = source.get('domain', '')
        access_method = source.get('access_method', '')

        # Check access method is allowed
        if access_method not in ALLOWED_ACCESS_METHODS:
            return False, f"Invalid access method: {access_method}"

        # If domain ends with .cn
        if domain.endswith('.cn'):
            if access_method not in ['wayback', 'commoncrawl', 'archive_today']:
                return False, f"FORBIDDEN: .cn domain '{domain}' must use archive access (wayback/commoncrawl/archive_today), not '{access_method}'"

        # If method is 'direct', domain must be safe aggregator
        if access_method == 'direct':
            if not any(safe in domain for safe in SAFE_AGGREGATORS):
                return False, f"Direct access only allowed for safe aggregators, not '{domain}'"

        return True, "OK"


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

class StateLock:
    """Platform-specific file locking for state file"""

    def __init__(self, lock_path: Path):
        self.lock_path = lock_path
        self.lock_file = None

    def __enter__(self):
        """Acquire exclusive lock"""
        self.lock_file = open(self.lock_path, 'w')

        if PLATFORM_LOCK == 'fcntl':
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX)
        elif PLATFORM_LOCK == 'msvcrt':
            msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_LOCK, 1)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release lock"""
        if self.lock_file:
            if PLATFORM_LOCK == 'fcntl':
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
            elif PLATFORM_LOCK == 'msvcrt':
                msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_UNLCK, 1)

            self.lock_file.close()


class StateManager:
    """Manage collection state with atomic commits"""

    def __init__(self, state_path: Path):
        self.state_path = state_path
        self.lock_path = state_path.parent / '.state.lock'

    def load_state(self) -> Dict:
        """Load state from disk"""
        if not self.state_path.exists():
            logger.info("No existing state file, initializing new state")
            return self._initialize_state()

        try:
            with open(self.state_path, 'r') as f:
                state = json.load(f)
            logger.info(f"Loaded state from {self.state_path}")
            return state
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            logger.info("Initializing new state")
            return self._initialize_state()

    def commit_state(self, new_state: Dict):
        """Atomically commit state to disk"""
        with StateLock(self.lock_path):
            # Write to temp file
            tmp_fd, tmp_path = tempfile.mkstemp(
                dir=self.state_path.parent,
                prefix='.tmp_state_',
                suffix='.json'
            )

            try:
                with os.fdopen(tmp_fd, 'w') as f:
                    json.dump(new_state, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())

                # Atomic rename
                os.replace(tmp_path, self.state_path)
                logger.info(f"State committed to {self.state_path}")

            except Exception as e:
                logger.error(f"Error committing state: {e}")
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                raise

    def _initialize_state(self) -> Dict:
        """Initialize default state structure"""
        return {
            "version": "1.0",
            "last_global_run_iso": None,
            "buckets": {
                "SASAC_ANNOUNCEMENTS": {
                    "forward_watermark_iso": None,
                    "backfill_pointer_year": 2024,
                    "sources": {}
                },
                "STOCK_EXCHANGES": {
                    "forward_watermark_iso": None,
                    "backfill_pointer_year": 2024,
                    "sources": {}
                },
                "STATE_MEDIA": {
                    "forward_watermark_iso": None,
                    "backfill_pointer_year": 2024,
                    "sources": {}
                },
                "BLOOMBERG_REUTERS": {
                    "forward_watermark_iso": None,
                    "backfill_pointer_year": 2024,
                    "sources": {}
                },
                "CORPORATE_FILINGS": {
                    "forward_watermark_iso": None,
                    "backfill_pointer_year": 2024,
                    "sources": {}
                },
                "SECTOR_ANALYSIS": {
                    "forward_watermark_iso": None,
                    "backfill_pointer_year": 2024,
                    "sources": {}
                }
            }
        }


# ============================================================================
# DATABASE INTEGRATION
# ============================================================================

class EntityMergerDatabase:
    """Integration with osint_master.db entity_mergers table"""

    def __init__(self, db_path: Path = WAREHOUSE_DB):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Connect to database"""
        if not self.db_path.exists():
            logger.error(f"Database not found: {self.db_path}")
            raise FileNotFoundError(f"Database not found: {self.db_path}")

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        logger.info(f"Connected to database: {self.db_path}")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def check_existing_merger(self, legacy_entity_name: str) -> Optional[Dict]:
        """Check if merger already exists in database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM entity_mergers
            WHERE legacy_entity_name = ?
        """, (legacy_entity_name,))

        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_us_contracting_history(self, entity_name: str) -> Tuple[int, float, Optional[str]]:
        """Get US contracting history for entity"""
        cursor = self.conn.cursor()

        # Check across all usaspending tables
        tables = ['usaspending_china_305', 'usaspending_china_101', 'usaspending_china_comprehensive']

        total_count = 0
        total_value = 0.0
        last_date = None

        for table in tables:
            try:
                # Check if table exists
                cursor.execute(f"""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name=?
                """, (table,))

                if not cursor.fetchone():
                    continue

                # Get contract stats
                query = f"""
                    SELECT
                        COUNT(*) as contract_count,
                        SUM(award_amount) as total_value,
                        MAX(action_date) as last_contract_date
                    FROM {table}
                    WHERE recipient_name LIKE ? OR vendor_name LIKE ?
                """

                pattern = f"%{entity_name}%"
                cursor.execute(query, (pattern, pattern))

                row = cursor.fetchone()
                if row:
                    total_count += row['contract_count'] or 0
                    total_value += row['total_value'] or 0.0

                    if row['last_contract_date']:
                        if not last_date or row['last_contract_date'] > last_date:
                            last_date = row['last_contract_date']

            except Exception as e:
                logger.warning(f"Error querying {table}: {e}")

        return total_count, total_value, last_date

    def get_eu_contracting_history(self, entity_name: str) -> Tuple[int, List[str], Optional[str]]:
        """
        Get European contracting history for entity from TED database

        Returns:
            (contract_count, countries_list, last_contract_date)
        """
        cursor = self.conn.cursor()

        # Check TED tables
        tables = ['ted_contracts_production', 'ted_china_contracts_fixed']

        total_count = 0
        countries_set = set()
        last_date = None

        for table in tables:
            try:
                # Check if table exists
                cursor.execute(f"""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name=?
                """, (table,))

                if not cursor.fetchone():
                    continue

                # Get contract stats
                # TED uses contractor_info field for entity names
                query = f"""
                    SELECT
                        COUNT(*) as contract_count,
                        iso_country,
                        MAX(publication_date) as last_contract_date
                    FROM {table}
                    WHERE contractor_info LIKE ?
                       OR ca_name LIKE ?
                    GROUP BY iso_country
                """

                pattern = f"%{entity_name}%"
                cursor.execute(query, (pattern, pattern))

                rows = cursor.fetchall()
                for row in rows:
                    if row['contract_count']:
                        total_count += row['contract_count']
                        if row['iso_country']:
                            countries_set.add(row['iso_country'])
                        if row['last_contract_date']:
                            if not last_date or row['last_contract_date'] > last_date:
                                last_date = row['last_contract_date']

            except Exception as e:
                logger.warning(f"Error querying {table}: {e}")

        return total_count, sorted(list(countries_set)), last_date

    def insert_merger(self, record: SOEMergerRecord) -> int:
        """Insert new merger record"""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO entity_mergers (
                legacy_entity_name, legacy_entity_type, merger_date,
                merged_into, current_parent, parent_country, parent_ownership,
                parent_tier, merger_type, strategic_sector,
                pre_merger_rank, post_merger_rank, notes, source,
                created_date, updated_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            record.legacy_entity_name,
            record.legacy_entity_type,
            record.merger_date_iso,
            record.merged_into,
            record.current_parent,
            'China',  # Assuming PRC SOE
            'State-Owned Enterprise',
            record.importance_tier,
            record.merger_type,
            record.strategic_sector,
            record.pre_merger_rank_global,
            record.post_merger_rank_global,
            record.summary or f"Detected from {record.source_publisher} on {record.source_date_iso}",
            record.source_url
        ))

        merger_id = cursor.lastrowid
        self.conn.commit()

        logger.info(f"Inserted merger record: {record.legacy_entity_name} -> {record.current_parent} (ID: {merger_id})")
        return merger_id

    def add_entity_alias(self, entity_name: str, alias: str, current_parent: str):
        """Add entity alias for lookup"""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO entity_aliases (entity_name, alias, alias_type, current_parent)
            VALUES (?, ?, ?, ?)
        """, (entity_name, alias, 'Auto-detected', current_parent))

        self.conn.commit()


# ============================================================================
# MERGER DETECTION & EXTRACTION
# ============================================================================

class MergerDetector:
    """Detect and extract merger information from text"""

    def __init__(self):
        self.keywords = MERGER_KEYWORDS
        self.strategic_sectors = STRATEGIC_SECTORS

    def detect_merger(self, text: str) -> Tuple[bool, List[str], float]:
        """
        Detect if text contains merger information

        Returns:
            (is_merger, keywords_matched, confidence)
        """
        text_lower = text.lower()
        keywords_matched = []

        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                keywords_matched.append(keyword)

        # Confidence based on number of keywords
        if len(keywords_matched) >= 3:
            confidence = 0.9
        elif len(keywords_matched) >= 2:
            confidence = 0.7
        elif len(keywords_matched) >= 1:
            confidence = 0.5
        else:
            confidence = 0.0

        is_merger = len(keywords_matched) >= 1

        return is_merger, keywords_matched, confidence

    def extract_entities(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract legacy entity and new parent from text

        Returns:
            (legacy_entity_name, current_parent)
        """
        # This is a simplified extraction - in production, would use NER
        # For now, return None to indicate manual review needed
        return None, None

    def classify_sector(self, text: str) -> Optional[str]:
        """Classify strategic sector from text"""
        text_lower = text.lower()

        for sector in self.strategic_sectors:
            if sector.lower() in text_lower:
                return sector

        return None


# ============================================================================
# DEDUPLICATION ENGINE
# ============================================================================

class DeduplicationEngine:
    """Track and detect duplicate merger records"""

    def __init__(self):
        self.seen_hashes = set()
        self.seen_text_hashes = set()

    def compute_hashes(self, content: bytes, text: str) -> Tuple[str, str]:
        """Compute file and text hashes"""
        file_hash = hashlib.sha256(content).hexdigest()
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        return file_hash, text_hash

    def is_duplicate(self, record: SOEMergerRecord) -> Tuple[bool, Optional[str]]:
        """Check if record is duplicate"""
        if record.hash_sha256 in self.seen_hashes:
            return True, "Duplicate file hash"

        if record.text_hash_sha256 in self.seen_text_hashes:
            return True, "Duplicate text hash"

        return False, None

    def add_record(self, record: SOEMergerRecord):
        """Add record to dedup tracking"""
        self.seen_hashes.add(record.hash_sha256)
        self.seen_text_hashes.add(record.text_hash_sha256)


# ============================================================================
# PRC SOE MONITORING COLLECTOR
# ============================================================================

class PRCSOEMonitoringCollector:
    """Main collector for PRC SOE merger monitoring"""

    def __init__(self, mode: str = 'weekly'):
        """
        Initialize collector

        Args:
            mode: 'weekly', 'monthly', or 'quarterly'
        """
        self.mode = mode
        self.state_manager = StateManager(STATE_FILE)
        self.merger_detector = MergerDetector()
        self.dedup_engine = DeduplicationEngine()
        self.db = EntityMergerDatabase()
        self.stats = Counter()
        self.validator = SafeAccessValidator()

        # HTTP session with redirect protection
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (OSINT-Foresight/1.0; Research; +https://github.com/osint-foresight)'
        })

        logger.info(f"PRCSOEMonitoringCollector initialized in {mode} mode")

    def download_with_redirect_protection(self, url: str, original_domain: str,
                                         access_method: str) -> Tuple[Optional[str], bool, str]:
        """
        Download HTML with strict redirect protection.

        CRITICAL SECURITY: This method ensures we NEVER accidentally access
        forbidden .cn domains, even if the archive redirects.

        Args:
            url: URL to download (should be archive URL)
            original_domain: The original .cn domain we're trying to access
            access_method: 'wayback', 'commoncrawl', 'archive_today', or 'direct'

        Returns:
            (html_content, success, error_message)
        """
        try:
            # CRITICAL: Disable automatic redirects
            response = self.session.get(url, timeout=30, allow_redirects=False)

            # Check for redirects (3xx status codes)
            if 300 <= response.status_code < 400:
                redirect_url = response.headers.get('Location', '')
                logger.warning(f"REDIRECT DETECTED: {url} -> {redirect_url}")

                # CRITICAL: Validate redirect URL is NOT a forbidden domain
                if SafeAccessValidator.is_forbidden_domain(redirect_url):
                    logger.error(f"SECURITY VIOLATION: Archive redirected to forbidden domain: {redirect_url}")
                    self.stats['security_violations'] += 1
                    return None, False, f"Archive redirected to forbidden domain: {redirect_url}"

                # If redirect is to another archive URL, that's okay
                # Check if redirect is still an archive domain
                archive_domains = ['archive.org', 'web.archive.org', 'commoncrawl.org',
                                 'archive.today', 'archive.is', 'archive.ph']
                is_archive_redirect = any(domain in redirect_url.lower() for domain in archive_domains)

                if not is_archive_redirect:
                    logger.error(f"SUSPICIOUS REDIRECT: Not to known archive: {redirect_url}")
                    self.stats['suspicious_redirects'] += 1
                    return None, False, f"Redirect to non-archive URL: {redirect_url}"

                # Follow the archive redirect (but still check the result)
                logger.info(f"  Following archive redirect: {redirect_url}")
                response = self.session.get(redirect_url, timeout=30, allow_redirects=False)

            # Check status code
            if response.status_code != 200:
                logger.warning(f"  Non-200 status: {response.status_code}")
                self.stats['download_failures'] += 1
                return None, False, f"HTTP {response.status_code}"

            # CRITICAL: Check Content-Type to ensure it's not a redirect page
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type and 'application/xhtml' not in content_type:
                logger.warning(f"  Unexpected content type: {content_type}")

            # CRITICAL: Verify we didn't somehow end up at the original .cn domain
            # Check if response URL (final URL after any internal redirects) is safe
            final_url = response.url
            if SafeAccessValidator.is_forbidden_domain(final_url):
                logger.error(f"SECURITY VIOLATION: Ended up at forbidden domain: {final_url}")
                self.stats['security_violations'] += 1
                return None, False, f"Final URL is forbidden domain: {final_url}"

            # Get content
            if response.encoding is None:
                response.encoding = 'utf-8'

            html_content = response.text

            # Verify we got substantial content (not just an error page)
            if len(html_content) < 100:
                logger.warning(f"  Suspiciously short content: {len(html_content)} bytes")
                self.stats['short_content'] += 1

            logger.debug(f"  Downloaded {len(html_content)} bytes from {url[:80]}")
            self.stats['downloads_successful'] += 1

            return html_content, True, "OK"

        except requests.Timeout:
            logger.warning(f"  Timeout downloading {url[:80]}")
            self.stats['download_timeouts'] += 1
            return None, False, "Timeout"

        except requests.RequestException as e:
            logger.warning(f"  Error downloading {url[:80]}: {e}")
            self.stats['download_errors'] += 1
            return None, False, f"Request error: {e}"

        except Exception as e:
            logger.error(f"  Unexpected error downloading {url[:80]}: {e}")
            self.stats['download_errors'] += 1
            return None, False, f"Unexpected error: {e}"

    def enrich_with_contracting_history(self, record: SOEMergerRecord) -> SOEMergerRecord:
        """
        Enrich merger record with US and European contracting history.

        This cross-references the legacy entity name against:
        - US Government contracts (USAspending database)
        - European Government/Organization contracts (TED database)

        TIER_1 alerts are generated for entities with:
        - US contracting history + strategic sector, OR
        - European contracting history + strategic sector

        Args:
            record: SOEMergerRecord with basic entity information

        Returns:
            Enriched record with contracting history populated
        """
        entity_name = record.legacy_entity_name

        logger.info(f"  Enriching record for: {entity_name}")

        # Get US contracting history
        us_count, us_value, us_last_date = self.db.get_us_contracting_history(entity_name)
        if us_count > 0:
            record.us_contracting_history = True
            record.us_contracting_count = us_count
            record.us_contracting_value_usd = us_value
            record.us_contracting_last_date_iso = us_last_date
            logger.info(f"    US Contracts: {us_count} contracts, ${us_value:,.2f}, last: {us_last_date}")
            self.stats['entities_with_us_contracts'] += 1

        # Get European contracting history
        eu_count, eu_countries, eu_last_date = self.db.get_eu_contracting_history(entity_name)
        if eu_count > 0:
            record.eu_contracting_history = True
            record.eu_contracting_count = eu_count
            record.eu_contracting_countries = eu_countries
            record.eu_contracting_last_date_iso = eu_last_date
            logger.info(f"    EU Contracts: {eu_count} contracts in {len(eu_countries)} countries ({', '.join(eu_countries)}), last: {eu_last_date}")
            self.stats['entities_with_eu_contracts'] += 1

        # Determine importance tier
        # TIER_1: Strategic sector + (US or EU contracting history)
        # TIER_2: Strategic sector OR (US or EU contracting history), but not both
        # TIER_3: Neither strategic nor contracting history
        is_strategic = record.strategic_sector and record.strategic_sector in STRATEGIC_SECTORS
        has_western_contracts = record.us_contracting_history or record.eu_contracting_history

        if is_strategic and has_western_contracts:
            record.importance_tier = 'TIER_1'
            logger.info(f"    ⚠️  TIER_1: Strategic sector + Western contracting")
            self.stats['tier1_alerts'] += 1
        elif is_strategic or has_western_contracts:
            record.importance_tier = 'TIER_2'
            logger.info(f"    TIER_2: Strategic OR Western contracting")
        else:
            record.importance_tier = 'TIER_3'
            logger.info(f"    TIER_3: Neither strategic nor Western contracting")

        return record

    def generate_tier1_alert(self, record: SOEMergerRecord):
        """
        Generate TIER_1 alert for strategic merger with Western contracting history

        Args:
            record: TIER_1 merger record
        """
        alert_timestamp = datetime.now(timezone.utc).isoformat()
        alert_filename = ALERTS_DIR / f"tier1_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        alert_data = {
            'alert_type': 'TIER_1_STRATEGIC_MERGER',
            'alert_timestamp': alert_timestamp,
            'merger_info': {
                'legacy_entity_name': record.legacy_entity_name,
                'current_parent': record.current_parent,
                'merged_into': record.merged_into,
                'merger_date': record.merger_date_iso,
                'strategic_sector': record.strategic_sector,
                'merger_type': record.merger_type
            },
            'us_contracting': {
                'has_history': record.us_contracting_history,
                'contract_count': record.us_contracting_count,
                'total_value_usd': record.us_contracting_value_usd,
                'last_contract_date': record.us_contracting_last_date_iso
            },
            'eu_contracting': {
                'has_history': record.eu_contracting_history,
                'contract_count': record.eu_contracting_count,
                'countries': record.eu_contracting_countries,
                'last_contract_date': record.eu_contracting_last_date_iso
            },
            'detection_info': {
                'source_url': record.source_url,
                'source_publisher': record.source_publisher,
                'detection_confidence': record.detection_confidence,
                'keywords_matched': record.keywords_matched
            },
            'recommendation': self._generate_recommendation(record)
        }

        # Save alert to file
        with open(alert_filename, 'w') as f:
            json.dump(alert_data, f, indent=2)

        logger.warning(f"\n{'=' * 80}")
        logger.warning(f"🚨 TIER_1 ALERT GENERATED")
        logger.warning(f"{'=' * 80}")
        logger.warning(f"Entity: {record.legacy_entity_name}")
        logger.warning(f"Merged into: {record.current_parent}")
        logger.warning(f"Sector: {record.strategic_sector}")
        if record.us_contracting_history:
            logger.warning(f"US Contracts: {record.us_contracting_count} contracts (${record.us_contracting_value_usd:,.2f})")
        if record.eu_contracting_history:
            logger.warning(f"EU Contracts: {record.eu_contracting_count} contracts in {len(record.eu_contracting_countries)} countries")
        logger.warning(f"Alert saved: {alert_filename}")
        logger.warning(f"{'=' * 80}\n")

    def _generate_recommendation(self, record: SOEMergerRecord) -> str:
        """Generate recommendation text for alert"""
        recommendations = []

        recommendations.append(f"CRITICAL: Strategic SOE merger detected in {record.strategic_sector} sector")

        if record.us_contracting_history:
            recommendations.append(f"- Entity has {record.us_contracting_count} US government contracts totaling ${record.us_contracting_value_usd:,.2f}")
            recommendations.append(f"- Last US contract: {record.us_contracting_last_date_iso}")

        if record.eu_contracting_history:
            countries_str = ', '.join(record.eu_contracting_countries)
            recommendations.append(f"- Entity has {record.eu_contracting_count} European contracts across {len(record.eu_contracting_countries)} countries ({countries_str})")
            recommendations.append(f"- Last EU contract: {record.eu_contracting_last_date_iso}")

        recommendations.append(f"- Now controlled by: {record.current_parent}")
        recommendations.append("")
        recommendations.append("RECOMMENDED ACTIONS:")
        recommendations.append("1. Update entity tracking database with new parent company")
        recommendations.append("2. Review current contracts for concentration risk")

        if record.us_contracting_history:
            recommendations.append("3. Alert US contracting officers to ownership change")

        if record.eu_contracting_history:
            recommendations.append("4. Alert EU member state contracting authorities to ownership change")

        recommendations.append("5. Assess strategic implications of consolidation")

        return '\n'.join(recommendations)

    def run(self):
        """Execute collection workflow"""
        logger.info("=" * 80)
        logger.info(f"STARTING PRC SOE MONITORING - {self.mode.upper()} MODE")
        logger.info("=" * 80)

        start_time = time.time()

        # Load state
        state = self.state_manager.load_state()

        # Connect to database
        self.db.connect()

        try:
            # Determine which buckets to process based on mode
            buckets = self._get_buckets_for_mode()

            logger.info(f"Processing {len(buckets)} buckets: {', '.join(buckets)}")

            # Process each bucket
            all_records = []
            for bucket in buckets:
                logger.info(f"\n{'-' * 80}")
                logger.info(f"Processing bucket: {bucket}")
                logger.info(f"{'-' * 80}")

                # Placeholder: In production, would call actual collection methods
                # For now, demonstrate architecture
                logger.info(f"  [DEMO MODE] Would collect from {bucket}")
                logger.info(f"  [DEMO MODE] Skipping actual collection in initial implementation")

            # Save results
            self._save_results(all_records)

            # Update state
            state['last_global_run_iso'] = datetime.now(timezone.utc).isoformat()
            self.state_manager.commit_state(state)

            # Generate summary
            duration = time.time() - start_time
            self._print_summary(duration)

        finally:
            self.db.close()

    def _get_buckets_for_mode(self) -> List[str]:
        """Get buckets to process based on mode"""
        if self.mode == 'weekly':
            return ['SASAC_ANNOUNCEMENTS', 'STOCK_EXCHANGES', 'STATE_MEDIA', 'BLOOMBERG_REUTERS']
        elif self.mode == 'monthly':
            return ['SASAC_ANNOUNCEMENTS', 'STOCK_EXCHANGES', 'STATE_MEDIA',
                   'BLOOMBERG_REUTERS', 'CORPORATE_FILINGS']
        elif self.mode == 'quarterly':
            return ['SASAC_ANNOUNCEMENTS', 'STOCK_EXCHANGES', 'STATE_MEDIA',
                   'BLOOMBERG_REUTERS', 'CORPORATE_FILINGS', 'SECTOR_ANALYSIS']
        else:
            return []

    def _save_results(self, records: List[SOEMergerRecord]):
        """Save collection results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = DATA_DIR / f"{self.mode}_collection_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump({
                'metadata': {
                    'mode': self.mode,
                    'timestamp_iso': datetime.now(timezone.utc).isoformat(),
                    'records_count': len(records),
                    'stats': dict(self.stats)
                },
                'records': [asdict(r) for r in records]
            }, f, indent=2)

        logger.info(f"Results saved: {output_file}")

    def _print_summary(self, duration: float):
        """Print collection summary"""
        logger.info("\n" + "=" * 80)
        logger.info("COLLECTION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Mode: {self.mode}")
        logger.info(f"Duration: {duration:.1f}s")
        logger.info(f"Stats: {dict(self.stats)}")
        logger.info("=" * 80)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='PRC SOE Monitoring Collector')
    parser.add_argument('--mode', choices=['weekly', 'monthly', 'quarterly'],
                       default='weekly', help='Collection mode')
    parser.add_argument('--weekly', action='store_const', const='weekly', dest='mode',
                       help='Weekly monitoring (30 min)')
    parser.add_argument('--monthly', action='store_const', const='monthly', dest='mode',
                       help='Monthly deep dive (2 hr)')
    parser.add_argument('--quarterly', action='store_const', const='quarterly', dest='mode',
                       help='Quarterly sector analysis (4 hr)')

    args = parser.parse_args()

    collector = PRCSOEMonitoringCollector(mode=args.mode)
    collector.run()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
