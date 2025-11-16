#!/usr/bin/env python3
"""
Think Tank Global Collector - Regional Collector

Main script for collecting publications from think tanks in a specific region.
Implements download, hashing, QA validation, and output generation.

Usage:
    python thinktank_regional_collector.py --region US_CAN
    python thinktank_regional_collector.py --region EUROPE --dry-run
"""

import argparse
import json
import csv
import hashlib
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import yaml
import sqlite3
from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO
import re
from dateutil import parser as date_parser
from collections import Counter

# Import our modules
from thinktank_state_manager import StateManager
from thinktank_base_collector import DiscoveryEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class RegionalCollector:
    """Collects think tank publications for a specific region."""

    OUTPUT_ROOT = Path("F:/ThinkTank_Sweeps")
    SOURCE_RULES_PATH = Path("C:/Projects/OSINT - Foresight/config/thinktank_source_rules.yaml")

    # Sources to skip (handle manually)
    SKIP_SOURCES = {"csis.org"}

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
        "/how-to-", "/registration", "/annual-report"
    ]

    # Generic title patterns to skip
    SKIP_TITLE_PATTERNS = [
        "about us", "contact", "careers", "privacy policy", "terms of use",
        "our team", "our culture", "leadership", "board of trustees",
        "support", "donate", "newsletter", "subscribe",
        "past events", "upcoming events", "events",
        "for media", "press", "media",
        "benefits", "internships", "jobs", "apply",
        "sitemap", "search results", "home", "homepage"
    ]

    def __init__(self, region: str, dry_run: bool = False):
        """
        Initialize regional collector.

        Args:
            region: One of US_CAN, EUROPE, APAC, ARCTIC
            dry_run: If True, don't write outputs or update state
        """
        self.region = region
        self.dry_run = dry_run
        self.run_date = datetime.now(timezone.utc).strftime("%Y%m%d")

        # Output directory for this run
        self.output_dir = self.OUTPUT_ROOT / region / self.run_date
        self.files_dir = self.output_dir / "files"
        self.snapshots_dir = self.output_dir / "snapshots"

        # Create directories
        if not dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.files_dir.mkdir(exist_ok=True)
            self.snapshots_dir.mkdir(exist_ok=True)

        # Load source rules
        with open(self.SOURCE_RULES_PATH, 'r', encoding='utf-8') as f:
            self.source_rules = yaml.safe_load(f)

        # Tracking
        self.collected_items = []
        self.failures = []
        self.qa_issues = []
        self.metrics = {
            "requests_total": 0,
            "bandwidth_mb": 0.0,
            "http_4xx": 0,
            "http_5xx": 0,
            "items_discovered": 0,
            "items_downloaded": 0,
            "pdf_extract_errors": 0,
            "duplicates": 0
        }
        self.seen_hashes = set()

    def get_sources_for_region(self) -> List[str]:
        """Get list of source domains for this region."""
        sources = []
        for domain, rules in self.source_rules.items():
            if domain == "default":
                continue
            if rules.get("region") == self.region:
                # Skip sources in SKIP_SOURCES (e.g., CSIS - manual processing)
                if domain not in self.SKIP_SOURCES:
                    sources.append(domain)
                else:
                    logging.info(f"Skipping {domain} (marked for manual processing)")

        logging.info(f"Found {len(sources)} sources for {self.region}")
        return sources

    def should_skip_url(self, url: str) -> bool:
        """Check if URL is a non-content page that should be skipped."""
        url_lower = url.lower()
        for pattern in self.SKIP_URL_PATTERNS:
            if pattern in url_lower:
                return True
        return False

    def is_generic_title(self, title: str) -> bool:
        """Check if title is generic (website navigation, not actual content)."""
        if not title or title == "No title":
            return True

        title_lower = title.lower().strip()

        # Check if title ends with just organization name (e.g., "| Brookings")
        if re.match(r'^[^|]+\|\s*\w+\s*$', title):
            # Extract the part before the pipe
            before_pipe = title.split('|')[0].strip().lower()
            # If very short (< 20 chars), likely generic
            if len(before_pipe) < 20:
                for pattern in self.SKIP_TITLE_PATTERNS:
                    if pattern in before_pipe:
                        return True

        # Check for exact generic patterns
        for pattern in self.SKIP_TITLE_PATTERNS:
            if pattern in title_lower:
                return True

        return False

    def slugify(self, text: str, max_length: int = 80) -> str:
        """
        Convert text to URL-friendly slug.

        Args:
            text: Text to slugify
            max_length: Maximum length of slug

        Returns:
            Slugified text
        """
        if not text:
            return "untitled"

        # Remove organization suffix (e.g., "| Brookings")
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

    def get_think_tank_slug(self, domain: str) -> str:
        """
        Get short slug for think tank organization.

        Args:
            domain: Domain name (e.g., "www.brookings.edu")

        Returns:
            Short slug (e.g., "brookings")
        """
        # Remove www., .org, .edu, .com, etc.
        slug = domain.replace('www.', '')
        slug = re.sub(r'\.(org|edu|com|net|gov|int|mil)$', '', slug)

        # Take first part if multiple dots remain
        if '.' in slug:
            slug = slug.split('.')[0]

        return slug

    def generate_filename(self, item: Dict[str, Any], ext: str) -> str:
        """
        Generate human-readable filename.

        Format: YYYY-MM-DD_think-tank-slug_title-slug.ext

        Args:
            item: Item dictionary with metadata
            ext: File extension (with dot, e.g., ".pdf")

        Returns:
            Human-readable filename
        """
        # Extract date
        date_str = "0000-00-00"
        if item.get("publication_date_iso"):
            try:
                pub_date = datetime.fromisoformat(item["publication_date_iso"].replace('Z', '+00:00'))
                date_str = pub_date.strftime("%Y-%m-%d")
            except:
                # Use collection date as fallback
                date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        else:
            # Use collection date
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Get think tank slug
        think_tank_slug = self.get_think_tank_slug(item.get("publisher_org", "unknown"))

        # Get title slug
        title_slug = self.slugify(item.get("title", "untitled"))

        # Combine
        filename = f"{date_str}_{think_tank_slug}_{title_slug}{ext}"

        return filename

    def collect_from_source(self, domain: str, time_windows: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Collect publications from a single source.

        Args:
            domain: Source domain (e.g., "csis.org")
            time_windows: Lane A and Lane B time windows from state manager

        Returns:
            List of collected items
        """
        logging.info(f"\n{'='*60}")
        logging.info(f"Collecting from: {domain}")
        logging.info(f"{'='*60}")

        rules = self.source_rules.get(domain, self.source_rules["default"])

        # Initialize discovery engine
        engine = DiscoveryEngine(domain, rules)

        # Discover items
        discovered = engine.discover_all(max_pages=40)
        self.metrics["items_discovered"] += len(discovered)

        logging.info(f"Discovered {len(discovered)} potential items from {domain}")

        # WORKAROUND: CSIS has unreliable sitemap dates (all show 2025-01-30 CMS migration date)
        # Force page fetching by nullifying sitemap dates for CSIS
        if domain == "csis.org":
            logging.info(f"CSIS detected: Nullifying unreliable sitemap dates to force page fetching")
            for item in discovered:
                if item.get("fetch_mode") == "SITEMAP":
                    item["publication_date"] = None

        # Apply per-source item limit to prevent runaway processing
        MAX_ITEMS_PER_SOURCE = 1500
        if len(discovered) > MAX_ITEMS_PER_SOURCE:
            logging.warning(f"Discovered {len(discovered)} items, limiting to {MAX_ITEMS_PER_SOURCE}")
            discovered = discovered[:MAX_ITEMS_PER_SOURCE]

        # Filter by time windows using three-way logic
        items = []
        filtered_count = 0
        no_date_count = 0

        for idx, item_meta in enumerate(discovered):
            # Extract date from metadata (lightweight check)
            pub_date = self.extract_date_from_metadata(item_meta)

            should_process = False

            if pub_date:
                # We have a date from metadata - can pre-filter
                if self.date_in_time_window(pub_date, time_windows):
                    should_process = True  # Date found and matches
                else:
                    # Date found but outside window - skip (efficient pre-filtering)
                    filtered_count += 1
            else:
                # No date in metadata - must fetch page to determine
                should_process = True
                no_date_count += 1

            if should_process:
                # Log progress every 10 items
                if idx % 10 == 0:
                    logging.info(f"Processing item {idx+1}/{len(discovered)} (collected: {len(self.collected_items)})")

                # Extract full metadata and download file
                item = self.process_item(item_meta, domain, rules, engine)

                if item:
                    # For items without metadata dates, check post-fetch
                    if not pub_date:
                        if self.item_in_time_window(item, time_windows):
                            items.append(item)
                            self.collected_items.append(item)
                        else:
                            # Filtered after page fetch
                            filtered_count += 1
                    else:
                        # Had metadata date and matched - keep it
                        items.append(item)
                        self.collected_items.append(item)

        logging.info(f"Filtered out {filtered_count} items (outside time window)")
        if no_date_count > 0:
            logging.info(f"Processed {no_date_count} items without metadata dates (required page fetch)")

        return items

    def process_item(self, item_meta: Dict[str, Any], domain: str, rules: Dict[str, Any],
                     engine: DiscoveryEngine) -> Optional[Dict[str, Any]]:
        """
        Process a single discovered item: fetch page, extract metadata, download file.

        Args:
            item_meta: Basic metadata from discovery
            domain: Source domain
            rules: Source rules
            engine: Discovery engine (for fetching)

        Returns:
            Complete item dict or None if processing failed
        """
        url = item_meta.get("url")
        if not url:
            return None

        # Skip non-content URLs
        if self.should_skip_url(url):
            logging.debug(f"  Skipping non-content URL: {url}")
            return None

        # Fetch the page (with Selenium fallback for blocked sites)
        response = engine.fetch_with_selenium_fallback(url)
        if not response:
            self.failures.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "region": self.region,
                "org": domain,
                "url": url,
                "reason": "fetch_failed"
            })
            return None

        self.metrics["requests_total"] += 1
        self.metrics["bandwidth_mb"] += len(response.content) / (1024 * 1024)

        # Parse page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract metadata
        item = {
            "canonical_url": url,
            "publisher_org": domain,
            "publisher_type": "thinktank",  # Could refine based on source
            "fetch_mode": item_meta.get("fetch_mode", "UNKNOWN"),
            "region_tag": self.region,
            "extraction_notes": []
        }

        # Extract title
        item["title"] = self.extract_title(soup, item_meta)

        # Skip generic titles (navigation pages, etc.)
        if self.is_generic_title(item["title"]):
            logging.debug(f"  Skipping generic title: {item['title']}")
            return None

        # Extract publication date
        item["publication_date_iso"] = self.extract_date(soup, rules, url)

        # Detect language
        item["language"] = self.detect_language(item["title"], soup)

        # Find download URL (PDF, DOCX, etc.)
        download_url = self.find_download_url(soup, rules, url)

        if download_url:
            # Download file
            file_info = self.download_file(download_url, engine, item)
            if file_info:
                item.update(file_info)
                self.metrics["items_downloaded"] += 1
            else:
                # Download failed, save HTML snapshot
                item.update(self.save_html_snapshot(url, response.content, domain, item))
        else:
            # No file available, save HTML snapshot
            item.update(self.save_html_snapshot(url, response.content, domain, item))

        # Extract summary
        item["summary"] = self.extract_summary(soup)

        # Extract topics (simple keyword matching)
        item["topics"] = self.extract_topics(item["title"], item.get("summary", ""))

        # Run QA checks
        item["qa_issues"] = self.run_qa_checks(item)
        if item["qa_issues"]:
            self.qa_issues.extend(item["qa_issues"])

        # Check for duplicates
        if item.get("hash_sha256") in self.seen_hashes:
            item["duplicate"] = True
            self.metrics["duplicates"] += 1
        else:
            item["duplicate"] = False
            if item.get("hash_sha256"):
                self.seen_hashes.add(item["hash_sha256"])

        return item

    def extract_title(self, soup: BeautifulSoup, item_meta: Dict[str, Any]) -> str:
        """Extract title from page."""
        # Try item_meta first
        if item_meta.get("title"):
            return item_meta["title"]

        # Try meta tags
        meta_title = soup.find("meta", property="og:title")
        if meta_title and meta_title.get("content"):
            return meta_title["content"]

        # Try h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        # Fallback to page title
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)

        return "No title"

    def extract_date(self, soup: BeautifulSoup, rules: Dict[str, Any], url: str) -> Optional[str]:
        """Extract publication date from page."""
        date_selectors = rules.get("date_selectors", [])

        for selector in date_selectors:
            # Try CSS selector
            elem = soup.select_one(selector)
            if elem:
                date_str = elem.get("datetime") or elem.get("content") or elem.get_text(strip=True)
                try:
                    parsed_date = date_parser.parse(date_str, fuzzy=True)
                    return parsed_date.isoformat()
                except:
                    continue

        # Fallback: extract from URL
        url_date_match = re.search(r'/(\d{4})/(\d{2})/', url)
        if url_date_match:
            year, month = url_date_match.groups()
            return f"{year}-{month}-01T00:00:00"

        return None

    def detect_language(self, title: str, soup: BeautifulSoup) -> str:
        """Detect language (simple heuristic)."""
        # Check html lang attribute
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            lang = html_tag["lang"][:2]
            return lang

        # Default to English
        return "en"

    def find_download_url(self, soup: BeautifulSoup, rules: Dict[str, Any], base_url: str) -> Optional[str]:
        """Find PDF or document download URL on page."""
        pdf_selectors = rules.get("pdf_selectors", [])

        for selector in pdf_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get("href")
                if href:
                    # Make absolute URL
                    from urllib.parse import urljoin
                    full_url = urljoin(base_url, href)
                    return full_url

        return None

    def download_file(self, url: str, engine: DiscoveryEngine, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Download file and compute hash.

        Args:
            url: Download URL
            engine: Discovery engine for fetching
            item: Item dictionary with metadata for filename generation

        Returns:
            Dict with file info or None if download failed
        """
        response = engine.fetch_with_selenium_fallback(url)
        if not response:
            self.failures.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "region": self.region,
                "org": engine.domain,
                "url": url,
                "reason": "download_failed"
            })
            return None

        content = response.content
        self.metrics["bandwidth_mb"] += len(content) / (1024 * 1024)

        # Compute hash
        sha256_hash = hashlib.sha256(content).hexdigest()

        # Determine file extension
        ext = Path(urlparse(url).path).suffix or ".pdf"

        # Generate human-readable filename
        filename = self.generate_filename(item, ext)

        # Save file with human-readable name
        if not self.dry_run:
            file_path = self.files_dir / filename
            # Handle filename collisions by appending hash suffix
            if file_path.exists():
                filename_base = filename.rsplit('.', 1)[0]
                filename = f"{filename_base}_{sha256_hash[:8]}{ext}"
                file_path = self.files_dir / filename
            with open(file_path, 'wb') as f:
                f.write(content)
        else:
            file_path = self.files_dir / filename

        # Extract pages if PDF
        pages = None
        extraction_ok = True
        if ext == ".pdf":
            try:
                pdf_reader = PyPDF2.PdfReader(BytesIO(content))
                pages = len(pdf_reader.pages)
            except Exception as e:
                logging.warning(f"PDF extraction failed: {e}")
                extraction_ok = False
                self.metrics["pdf_extract_errors"] += 1

        return {
            "download_url": url,
            "hash_sha256": sha256_hash,
            "file_size_bytes": len(content),
            "saved_path": str(file_path),
            "pages": pages,
            "extraction_ok": extraction_ok,
            "document_type": "report" if ext == ".pdf" else "document"
        }

    def save_html_snapshot(self, url: str, content: bytes, domain: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save HTML snapshot when no file available.

        Args:
            url: Page URL
            content: HTML content bytes
            domain: Domain name
            item: Item dictionary with metadata for filename generation

        Returns:
            Dict with snapshot info
        """
        sha256_hash = hashlib.sha256(content).hexdigest()

        # Generate human-readable filename
        filename = self.generate_filename(item, ".html")

        # Create org-specific snapshot dir
        org_dir = self.snapshots_dir / domain
        if not self.dry_run:
            org_dir.mkdir(exist_ok=True)

        # Save with human-readable name
        snapshot_path = org_dir / filename
        if not self.dry_run:
            # Handle filename collisions by appending hash suffix
            if snapshot_path.exists():
                filename_base = filename.rsplit('.', 1)[0]
                filename = f"{filename_base}_{sha256_hash[:8]}.html"
                snapshot_path = org_dir / filename
            with open(snapshot_path, 'wb') as f:
                f.write(content)

        return {
            "download_url": None,
            "hash_sha256": sha256_hash,
            "file_size_bytes": len(content),
            "saved_path": str(snapshot_path),
            "pages": None,
            "extraction_ok": True,
            "document_type": "web_snapshot"
        }

    def extract_summary(self, soup: BeautifulSoup) -> str:
        """Extract summary/abstract from page."""
        # Try meta description
        meta_desc = soup.find("meta", attrs={"name": "description"}) or \
                    soup.find("meta", property="og:description")
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"][:500]

        # Try abstract/summary elements
        abstract = soup.find(class_=re.compile(r"abstract|summary", re.I))
        if abstract:
            return abstract.get_text(strip=True)[:500]

        # Fallback: first paragraph
        p = soup.find("p")
        if p:
            return p.get_text(strip=True)[:500]

        return ""

    def extract_topics(self, title: str, summary: str) -> List[str]:
        """Extract topics using keyword matching."""
        text = (title + " " + summary).lower()

        topics = []
        keywords = {
            "ai": ["artificial intelligence", "machine learning", "neural network", "ai"],
            "quantum": ["quantum computing", "quantum", "qkd"],
            "semiconductors": ["semiconductor", "chip", "microchip"],
            "space": ["space", "satellite", "orbital"],
            "cyber": ["cyber", "cybersecurity", "hacking"],
            "arctic": ["arctic", "polar", "greenland", "antarctica"],
            "china": ["china", "chinese", "prc", "belt and road"],
            "dual_use": ["dual-use", "dual use", "export control"]
        }

        for topic, kws in keywords.items():
            if any(kw in text for kw in kws):
                topics.append(topic)

        return topics

    def run_qa_checks(self, item: Dict[str, Any]) -> List[str]:
        """Run QA checks on item."""
        issues = []

        # Check if title is meaningful
        if not item.get("title") or item["title"] == "No title":
            issues.append("missing_title")

        # Check if date is present and valid
        if not item.get("publication_date_iso"):
            issues.append("missing_date")
        elif item["publication_date_iso"]:
            try:
                date = datetime.fromisoformat(item["publication_date_iso"].replace('Z', '+00:00'))
                if date.year < 2010 or date.year > 2025:
                    issues.append("date_out_of_range")
            except:
                issues.append("invalid_date")

        # Check if extraction failed
        if not item.get("extraction_ok", True):
            issues.append("pdf_extract_error")

        # Check file size
        if item.get("file_size_bytes", 0) < 100:
            issues.append("file_too_small")

        return issues

    def extract_date_from_metadata(self, item_meta: Dict[str, Any]) -> Optional[datetime]:
        """
        Extract publication date from item metadata (lightweight, no download).

        Args:
            item_meta: Item metadata from discovery (sitemap, RSS, etc.)

        Returns:
            datetime object or None if date not found
        """
        # Try publication_date (from sitemap or RSS - universal field)
        if item_meta.get("publication_date"):
            try:
                return date_parser.parse(item_meta["publication_date"])
            except:
                pass

        # Try lastmod (from sitemap)
        if item_meta.get("lastmod"):
            try:
                return date_parser.parse(item_meta["lastmod"])
            except:
                pass

        # Try published (from RSS)
        if item_meta.get("published"):
            try:
                return date_parser.parse(item_meta["published"])
            except:
                pass

        # Try pubDate (from RSS)
        if item_meta.get("pubDate"):
            try:
                return date_parser.parse(item_meta["pubDate"])
            except:
                pass

        # Try extracting from URL
        url = item_meta.get("url", "")
        url_date_match = re.search(r'/(\d{4})/(\d{2})/', url)
        if url_date_match:
            year, month = url_date_match.groups()
            try:
                return datetime(int(year), int(month), 1, tzinfo=timezone.utc)
            except:
                pass

        # No date found
        return None

    def date_in_time_window(self, pub_date: datetime, time_windows: Dict[str, Any]) -> bool:
        """
        Check if a date falls within Lane A or Lane B time windows.

        Args:
            pub_date: Publication date as datetime
            time_windows: Time windows from state manager

        Returns:
            True if date is within windows, False otherwise
        """
        # Check Lane A (forward watch)
        lane_a = time_windows["lane_a"]
        lane_a_start = datetime.fromisoformat(lane_a["start"])
        lane_a_end = datetime.fromisoformat(lane_a["end"])

        if lane_a_start <= pub_date <= lane_a_end:
            return True

        # Check Lane B (backfill)
        lane_b = time_windows["lane_b"]
        backfill_year = lane_b["year"]

        if pub_date.year == backfill_year:
            return True

        return False

    def item_in_time_window(self, item: Dict[str, Any], time_windows: Dict[str, Any]) -> bool:
        """Check if item falls within Lane A or Lane B time windows."""
        pub_date_str = item.get("publication_date_iso")
        if not pub_date_str:
            return False  # Can't determine, exclude

        try:
            pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
        except:
            return False

        return self.date_in_time_window(pub_date, time_windows)

    def write_outputs(self):
        """Write all output files."""
        logging.info(f"\nWriting outputs to {self.output_dir}")

        # 1. items.json
        items_json_path = self.output_dir / "items.json"
        with open(items_json_path, 'w', encoding='utf-8') as f:
            json.dump(self.collected_items, f, indent=2, ensure_ascii=False)
        logging.info(f"Wrote {len(self.collected_items)} items to items.json")

        # 2. items.csv
        if self.collected_items:
            items_csv_path = self.output_dir / "items.csv"
            with open(items_csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.collected_items[0].keys())
                writer.writeheader()
                writer.writerows(self.collected_items)
            logging.info(f"Wrote items.csv")

        # 3. items.sql (SQLite insert statements)
        items_sql_path = self.output_dir / "items.sql"
        with open(items_sql_path, 'w', encoding='utf-8') as f:
            f.write("-- Think Tank Publications\n")
            f.write("CREATE TABLE IF NOT EXISTS thinktank_publications (\n")
            f.write("    id INTEGER PRIMARY KEY AUTOINCREMENT,\n")
            f.write("    canonical_url TEXT UNIQUE,\n")
            f.write("    title TEXT,\n")
            f.write("    publisher_org TEXT,\n")
            f.write("    publication_date_iso TEXT,\n")
            f.write("    hash_sha256 TEXT,\n")
            f.write("    region_tag TEXT,\n")
            f.write("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n")
            f.write(");\n\n")
            # Generate INSERT statements would go here
        logging.info(f"Wrote items.sql")

        # 4. file_manifest.csv
        manifest_path = self.output_dir / "file_manifest.csv"
        with open(manifest_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["hash_sha256", "saved_path", "bytes", "source_url", "canonical_url", "publisher_org", "title"])
            for item in self.collected_items:
                if item.get("hash_sha256"):
                    writer.writerow([
                        item.get("hash_sha256", ""),
                        item.get("saved_path", ""),
                        item.get("file_size_bytes", 0),
                        item.get("download_url", ""),
                        item.get("canonical_url", ""),
                        item.get("publisher_org", ""),
                        item.get("title", "")
                    ])
        logging.info(f"Wrote file_manifest.csv")

        # 5. download_failures.md
        failures_md_path = self.output_dir / "download_failures.md"
        with open(failures_md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Download Failures - {self.region} - {self.run_date}\n\n")
            f.write(f"Total failures: {len(self.failures)}\n\n")
            f.write("## Failure Log\n\n")
            for failure in self.failures:
                f.write(f"- [{failure['timestamp']}] [{failure['region']}] [{failure['org']}] {failure['url']} ({failure['reason']})\n")

            # Summary by reason
            f.write("\n## Summary by Reason\n\n")
            reason_counts = Counter(f['reason'] for f in self.failures)
            for reason, count in reason_counts.most_common():
                f.write(f"- {reason}: {count}\n")
        logging.info(f"Wrote download_failures.md ({len(self.failures)} failures)")

        # 6. qa_report.json
        qa_report_path = self.output_dir / "qa_report.json"
        qa_summary = {
            "total_items": len(self.collected_items),
            "items_with_issues": len([i for i in self.collected_items if i.get("qa_issues")]),
            "issue_counts": Counter([issue for item in self.collected_items for issue in item.get("qa_issues", [])]),
            "duplicates": self.metrics["duplicates"]
        }
        with open(qa_report_path, 'w', encoding='utf-8') as f:
            json.dump(qa_summary, f, indent=2)
        logging.info(f"Wrote qa_report.json")

        # 7. run_summary.json
        run_summary_path = self.output_dir / "run_summary.json"
        run_summary = {
            "region": self.region,
            "run_date": self.run_date,
            "items_collected": len(self.collected_items),
            "failures": len(self.failures),
            "metrics": self.metrics,
            "qa_summary": qa_summary
        }
        with open(run_summary_path, 'w', encoding='utf-8') as f:
            json.dump(run_summary, f, indent=2)
        logging.info(f"Wrote run_summary.json")

    def run(self):
        """Main execution flow."""
        logging.info(f"\n{'='*60}")
        logging.info(f"Starting Think Tank Collection for {self.region}")
        logging.info(f"Run Date: {self.run_date}")
        logging.info(f"Dry Run: {self.dry_run}")
        logging.info(f"{'='*60}\n")

        # Initialize state manager
        with StateManager() as sm:
            # Get time windows
            time_windows = sm.get_time_windows(self.region)
            logging.info(f"Time Windows:")
            logging.info(f"  Lane A (Forward): {time_windows['lane_a']['start']} to {time_windows['lane_a']['end']}")
            logging.info(f"  Lane B (Backfill): Year {time_windows['lane_b']['year']}")

            # Get sources for region
            sources = self.get_sources_for_region()

            # Collect from each source
            for source in sources:
                try:
                    self.collect_from_source(source, time_windows)
                except Exception as e:
                    logging.error(f"Error collecting from {source}: {e}")

            # Write outputs
            if not self.dry_run:
                self.write_outputs()

                # Update state on success
                current_time = datetime.now(timezone.utc).isoformat()
                sm.update_region_watermark(self.region, current_time)
                sm.decrement_backfill_pointer(self.region)
                sm.save_state()

                # Create run journal
                run_data = {
                    "region": self.region,
                    "run_date": self.run_date,
                    "items_collected": len(self.collected_items),
                    "time_windows": time_windows,
                    "metrics": self.metrics
                }
                sm.create_run_journal(self.region, run_data)

        logging.info(f"\n{'='*60}")
        logging.info(f"Collection Complete for {self.region}")
        logging.info(f"Items Collected: {len(self.collected_items)}")
        logging.info(f"Failures: {len(self.failures)}")
        logging.info(f"{'='*60}\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Think Tank Regional Collector")
    parser.add_argument("--region", required=True, choices=["US_CAN", "EUROPE", "APAC", "ARCTIC"],
                        help="Region to collect")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run without writing outputs or updating state")

    args = parser.parse_args()

    collector = RegionalCollector(args.region, dry_run=args.dry_run)
    collector.run()


if __name__ == "__main__":
    main()
