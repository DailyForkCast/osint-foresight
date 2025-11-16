#!/usr/bin/env python3
"""
China Policy Collector - Production Runner (FULL EXTRACTION)
Complete pipeline: discovery → download → extraction → QA
"""

import sys
import json
import yaml
import logging
import requests
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import collectors
from scripts.collectors.china_policy_collector import (
    ChinaPolicyCollector,
    StateLock,
    StateManager,
    SafeAccessValidator,
    WaybackClient,
    CommonCrawlClient,
    STATE_FILE
)

from scripts.collectors.china_extraction_qa import (
    DocumentExtractor,
    TopicClassifier,
    EntityExtractor,
    QAFramework,
    DeduplicationEngine,
    process_document,
    compute_hashes
)

# Setup logging
LOG_DIR = Path('F:/China_Sweeps/logs')
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f'full_extraction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FullExtractionRunner:
    """Run production collection with FULL download and extraction pipeline"""

    def __init__(self, bucket_name: str = 'SECONDARY'):
        self.bucket_name = bucket_name
        self.state_manager = StateManager(STATE_FILE)
        self.extractor = DocumentExtractor()
        self.classifier = TopicClassifier()
        self.entity_extractor = EntityExtractor()
        self.qa_framework = QAFramework()
        self.dedup_engine = DeduplicationEngine()
        self.wayback = WaybackClient()

        # HTTP session for downloads
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (OSINT-Foresight/1.0; Research; +https://github.com/osint-foresight)'
        })

        # Load source configuration
        config_path = Path('F:/China_Sweeps/SOURCE_CONFIG_COMPLETE.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # Output directory
        self.output_dir = Path('F:/China_Sweeps/data')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Stats tracking (including security violations)
        self.stats = {
            'security_violations': 0,
            'suspicious_redirects': 0,
            'downloads_succeeded': 0,
            'downloads_failed': 0
        }

        logger.info(f"Full extraction runner initialized for bucket: {bucket_name}")

    def get_bucket_sources(self) -> List[Dict]:
        """Get sources for the specified bucket"""
        sources = self.config.get(self.bucket_name, [])

        if not sources:
            logger.warning(f"No sources found for bucket: {self.bucket_name}")
            logger.warning(f"Available buckets: {list(self.config.keys())}")
        else:
            logger.info(f"Found {len(sources)} sources in {self.bucket_name} bucket")

        return sources

    def download_html(self, url: str, is_archive: bool = False) -> Optional[str]:
        """
        Download HTML content from URL with redirect protection.

        CRITICAL SECURITY: This method ensures we NEVER accidentally access
        forbidden .cn domains, even if the archive redirects.
        """
        try:
            logger.debug(f"    Downloading: {url[:100]}...")

            # CRITICAL: Disable automatic redirects to prevent .cn access
            response = self.session.get(url, timeout=30, allow_redirects=False)

            # Check for redirects (3xx status codes)
            if 300 <= response.status_code < 400:
                redirect_url = response.headers.get('Location', '')
                logger.warning(f"    REDIRECT DETECTED: {url[:80]} -> {redirect_url[:80]}")

                # CRITICAL: Validate redirect URL is NOT a forbidden domain
                if SafeAccessValidator.is_forbidden_domain(redirect_url):
                    logger.error(f"    SECURITY VIOLATION: Archive redirected to forbidden domain: {redirect_url[:80]}")
                    self.stats['security_violations'] += 1
                    self.stats['downloads_failed'] += 1
                    return None

                # Check if redirect is to another archive URL
                archive_domains = ['archive.org', 'web.archive.org', 'commoncrawl.org',
                                 'archive.today', 'archive.is', 'archive.ph']
                is_archive_redirect = any(domain in redirect_url.lower() for domain in archive_domains)

                if not is_archive_redirect:
                    logger.error(f"    SUSPICIOUS REDIRECT: Not to known archive: {redirect_url[:80]}")
                    self.stats['suspicious_redirects'] += 1
                    self.stats['downloads_failed'] += 1
                    return None

                # Follow the archive redirect (but still check the result)
                logger.info(f"    Following archive redirect: {redirect_url[:80]}")
                response = self.session.get(redirect_url, timeout=30, allow_redirects=False)

            # Check for successful response
            response.raise_for_status()

            # CRITICAL: Verify we didn't somehow end up at the original .cn domain
            final_url = response.url
            if SafeAccessValidator.is_forbidden_domain(final_url):
                logger.error(f"    SECURITY VIOLATION: Ended up at forbidden domain: {final_url[:80]}")
                self.stats['security_violations'] += 1
                self.stats['downloads_failed'] += 1
                return None

            # Get encoding
            if response.encoding is None:
                response.encoding = 'utf-8'

            html_content = response.text
            logger.debug(f"    Downloaded {len(html_content)} bytes")
            self.stats['downloads_succeeded'] += 1

            return html_content

        except requests.Timeout:
            logger.warning(f"    Timeout downloading {url[:80]}")
            self.stats['downloads_failed'] += 1
            return None
        except requests.RequestException as e:
            logger.warning(f"    Error downloading {url[:80]}: {e}")
            self.stats['downloads_failed'] += 1
            return None
        except Exception as e:
            logger.error(f"    Unexpected error downloading {url[:80]}: {e}")
            self.stats['downloads_failed'] += 1
            return None

    def discover_documents(self, source: Dict) -> List[Dict]:
        """Discover documents from a source"""
        logger.info(f"Discovering documents from: {source['name']}")

        discovered = []
        access_method = source.get('access_method', 'direct')
        domain = source.get('domain', '')
        url_patterns = source.get('url_patterns', [])

        # Construct full URLs from domain + url_patterns
        urls = []
        if domain and url_patterns:
            for pattern in url_patterns:
                if pattern.startswith('http'):
                    urls.append(pattern)
                else:
                    full_url = f"https://{domain}{pattern}"
                    urls.append(full_url)

        logger.info(f"  Constructed {len(urls)} URLs from patterns")

        try:
            if access_method == 'direct':
                # Direct access to English portals/secondary sources
                logger.info(f"  Using direct access (safe aggregator)")

                for url in urls:
                    discovered.append({
                        'source_name': source['name'],
                        'source_url': url,
                        'discovery_method': 'direct',
                        'discovery_timestamp': datetime.now(timezone.utc).isoformat(),
                        'access_method': 'direct',
                        'fetch_url': url  # Direct URL to fetch
                    })

            elif access_method == 'wayback':
                # Wayback Machine access for .cn domains
                logger.info(f"  Using Wayback Machine (archive access)")

                for url in urls:
                    snapshot = self.wayback.get_snapshot(url)
                    if snapshot and snapshot.get('available'):
                        discovered.append({
                            'source_name': source['name'],
                            'source_url': url,
                            'archive_url': snapshot['archive_url'],
                            'archive_timestamp': snapshot['timestamp'],
                            'discovery_method': 'wayback',
                            'discovery_timestamp': datetime.now(timezone.utc).isoformat(),
                            'access_method': 'wayback',
                            'fetch_url': snapshot['archive_url']  # Archive URL to fetch
                        })
                    else:
                        logger.warning(f"  No Wayback snapshot found for: {url}")

            logger.info(f"  Discovered {len(discovered)} documents")

        except Exception as e:
            logger.error(f"  Error discovering from {source['name']}: {e}")

        return discovered

    def extract_document(self, doc: Dict, source: Dict) -> Optional[Dict]:
        """Download and extract a document through full pipeline"""
        try:
            logger.info(f"  Extracting: {doc.get('source_name')} - {doc.get('source_url', 'N/A')[:60]}")

            # Download HTML
            fetch_url = doc.get('fetch_url')
            if not fetch_url:
                logger.error("    No fetch_url provided")
                return None

            is_archive = doc.get('access_method') == 'wayback'
            html_content = self.download_html(fetch_url, is_archive=is_archive)

            if not html_content:
                logger.warning("    Failed to download HTML")
                return {
                    **doc,
                    'extraction_status': 'download_failed',
                    'extraction_timestamp': datetime.now(timezone.utc).isoformat()
                }

            # Extract metadata and content
            logger.debug("    Extracting metadata...")
            extracted = self.extractor.extract_from_html(html_content, doc.get('source_url'))

            # Classify topics
            title = extracted.get('title', '')
            content = extracted.get('content_text', '')

            if not title and not content:
                logger.warning("    No title or content extracted")
                return {
                    **doc,
                    'extraction_status': 'no_content',
                    'extraction_timestamp': datetime.now(timezone.utc).isoformat()
                }

            logger.debug(f"    Title: {title[:80] if title else 'N/A'}")
            logger.debug(f"    Content length: {len(content)} chars")

            topics, subtopics = self.classifier.classify(title, content)
            logger.debug(f"    Topics: {topics[:3] if topics else 'none'}")

            # Extract entities
            entities = self.entity_extractor.extract(title, content)
            logger.debug(f"    Entities: {len(entities)}")

            # Compute hashes
            file_hash, text_hash = compute_hashes(html_content.encode('utf-8'), content)

            # Check for duplicates
            temp_doc = {'hash_sha256': file_hash, 'title': title}
            is_duplicate, dup_reason = self.dedup_engine.is_duplicate(temp_doc)

            if is_duplicate:
                logger.info(f"    DUPLICATE: {dup_reason}")
                return {
                    **doc,
                    'extraction_status': 'duplicate',
                    'duplicate_reason': dup_reason,
                    'extraction_timestamp': datetime.now(timezone.utc).isoformat()
                }

            # Build complete document
            complete_doc = {
                # Discovery metadata
                **doc,

                # Extraction results
                'title': title,
                'title_en': title if extracted.get('language') == 'en' else None,
                'publication_date': extracted.get('publication_date'),
                'date_source': extracted.get('date_source'),
                'date_confidence': extracted.get('date_confidence'),
                'language': extracted.get('language'),
                'description': extracted.get('description'),
                'keywords': extracted.get('keywords', []),
                'content_text': content[:5000],  # First 5000 chars only
                'content_length': extracted.get('content_length'),

                # Classification
                'topics': topics,
                'subtopics': subtopics,
                'entities': entities,

                # Technical metadata
                'hash_sha256': file_hash,
                'text_hash_sha256': text_hash,
                'file_size_bytes': len(html_content),

                # Provenance
                'publisher_org': source.get('name'),
                'publisher_type': source.get('publisher_type', 'secondary'),
                'canonical_url': doc.get('source_url'),
                'verified_safe_source': doc.get('access_method') in ['direct', 'wayback'],
                'fetch_mode': doc.get('access_method'),

                # Processing metadata
                'extraction_status': 'success',
                'extraction_timestamp': datetime.now(timezone.utc).isoformat(),
                'extraction_ok': extracted.get('extraction_ok', True),
                'extraction_notes': extracted.get('extraction_notes', [])
            }

            # Run QA checks
            # Note: QA will flag some issues (missing fields) since we don't have all required fields yet
            # This is expected for initial extraction
            is_valid, qa_issues = self.qa_framework.validate_document(complete_doc)
            complete_doc['qa_passed'] = is_valid
            complete_doc['qa_issues'] = qa_issues

            if qa_issues:
                logger.debug(f"    QA issues: {len(qa_issues)}")

            # Add to dedup engine
            self.dedup_engine.add_document(complete_doc)

            logger.info(f"    SUCCESS: {title[:60] if title else 'Untitled'}")
            return complete_doc

        except Exception as e:
            logger.error(f"    Error extracting document: {e}", exc_info=True)
            return {
                **doc,
                'extraction_status': 'error',
                'extraction_error': str(e),
                'extraction_timestamp': datetime.now(timezone.utc).isoformat()
            }

    def run_collection(self, max_sources: Optional[int] = None,
                      max_docs_per_source: Optional[int] = None) -> Dict:
        """Run collection on the bucket with FULL extraction"""
        logger.info("=" * 80)
        logger.info(f"STARTING FULL EXTRACTION: {self.bucket_name}")
        logger.info("=" * 80)

        start_time = time.time()
        stats = {
            'bucket': self.bucket_name,
            'start_time': datetime.now(timezone.utc).isoformat(),
            'sources_processed': 0,
            'documents_discovered': 0,
            'documents_downloaded': 0,
            'documents_extracted': 0,
            'documents_passed_qa': 0,
            'documents_failed_qa': 0,
            'duplicates_skipped': 0,
            'download_failures': 0,
            'errors': 0
        }

        # Get sources
        sources = self.get_bucket_sources()
        if max_sources:
            sources = sources[:max_sources]
            logger.info(f"Limiting to first {max_sources} sources for test run")

        all_extracted = []

        for source in sources:
            logger.info(f"\n{'─' * 80}")
            logger.info(f"Processing source: {source['name']}")
            logger.info(f"{'─' * 80}")

            try:
                # Discover documents
                discovered = self.discover_documents(source)
                stats['documents_discovered'] += len(discovered)

                # Limit docs per source if specified
                if max_docs_per_source:
                    discovered = discovered[:max_docs_per_source]
                    if len(discovered) > 0:
                        logger.info(f"  Limiting to first {max_docs_per_source} documents for test")

                # Extract each discovered document
                for doc in discovered:
                    extracted = self.extract_document(doc, source)

                    if extracted:
                        all_extracted.append(extracted)

                        # Update stats
                        status = extracted.get('extraction_status')
                        if status == 'success':
                            stats['documents_extracted'] += 1
                            if extracted.get('qa_passed'):
                                stats['documents_passed_qa'] += 1
                            else:
                                stats['documents_failed_qa'] += 1
                        elif status == 'duplicate':
                            stats['duplicates_skipped'] += 1
                        elif status == 'download_failed':
                            stats['download_failures'] += 1

                    # Rate limiting
                    time.sleep(1)  # Be polite to servers

                stats['sources_processed'] += 1

            except Exception as e:
                logger.error(f"Error processing source {source['name']}: {e}")
                stats['errors'] += 1

        # Save results
        output_file = self.output_dir / f"{self.bucket_name}_extracted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': stats,
                'extracted_documents': all_extracted
            }, f, indent=2, ensure_ascii=False)

        stats['end_time'] = datetime.now(timezone.utc).isoformat()
        stats['duration_seconds'] = time.time() - start_time
        stats['output_file'] = str(output_file)

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("EXTRACTION RUN COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Bucket: {stats['bucket']}")
        logger.info(f"Sources processed: {stats['sources_processed']}")
        logger.info(f"Documents discovered: {stats['documents_discovered']}")
        logger.info(f"Documents extracted: {stats['documents_extracted']}")
        logger.info(f"Documents passed QA: {stats['documents_passed_qa']}")
        logger.info(f"Documents failed QA: {stats['documents_failed_qa']}")
        logger.info(f"Duplicates skipped: {stats['duplicates_skipped']}")
        logger.info(f"Download failures: {stats['download_failures']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info(f"Duration: {stats['duration_seconds']:.1f}s")
        logger.info(f"Output: {output_file}")
        logger.info("=" * 80)

        return stats


def main():
    """Main entry point"""

    # Start with SECONDARY bucket (safest sources)
    runner = FullExtractionRunner(bucket_name='SECONDARY')

    # Run full collection on ALL sources, ALL documents
    logger.info("Starting FULL EXTRACTION - PRODUCTION MODE on SECONDARY bucket")
    logger.info("Processing ALL sources, ALL documents")
    logger.info("These are US/European aggregators - completely safe")

    stats = runner.run_collection()  # No limits - full production run

    if stats['documents_extracted'] > 0:
        logger.info("\nSUCCESS - Full extraction pipeline working")
        logger.info(f"   Extracted {stats['documents_extracted']} documents")
        logger.info(f"   Passed QA: {stats['documents_passed_qa']}")
        logger.info(f"   Ready for production deployment")
    else:
        logger.warning("\nWARNING - No documents extracted")
        logger.warning("   Review logs for details")

    # Security stats reporting
    logger.info("\n" + "=" * 80)
    logger.info("SECURITY AUDIT")
    logger.info("=" * 80)
    logger.info(f"Security violations: {runner.stats.get('security_violations', 0)}")
    logger.info(f"Suspicious redirects: {runner.stats.get('suspicious_redirects', 0)}")
    logger.info(f"Downloads succeeded: {runner.stats.get('downloads_succeeded', 0)}")
    logger.info(f"Downloads failed: {runner.stats.get('downloads_failed', 0)}")

    if runner.stats.get('security_violations', 0) > 0:
        logger.error("\n[CRITICAL] Security violations detected!")
        logger.error("   Archive services redirected to forbidden .cn domains")
        logger.error("   Review logs for details")
    else:
        logger.info("\n[OK] No security violations - all .cn access properly blocked")

    return stats


if __name__ == '__main__':
    try:
        stats = main()
        sys.exit(0 if stats['documents_extracted'] > 0 else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
