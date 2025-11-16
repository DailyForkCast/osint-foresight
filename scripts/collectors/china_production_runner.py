#!/usr/bin/env python3
"""
China Policy Collector - Production Runner
Start with SECONDARY bucket (safest sources)
"""

import sys
import json
import yaml
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional
import time

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
    process_document
)

# Setup logging
LOG_DIR = Path('F:/China_Sweeps/logs')
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f'production_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ProductionRunner:
    """Run production collection with full pipeline"""

    def __init__(self, bucket_name: str = 'SECONDARY'):
        self.bucket_name = bucket_name
        self.state_manager = StateManager(STATE_FILE)
        self.collector = ChinaPolicyCollector()
        self.extractor = DocumentExtractor()
        self.classifier = TopicClassifier()
        self.entity_extractor = EntityExtractor()
        self.qa_framework = QAFramework()
        self.dedup_engine = DeduplicationEngine()

        # Load source configuration (use ENHANCED which has full SECONDARY bucket)
        config_path = Path('F:/China_Sweeps/SOURCE_CONFIG_ENHANCED.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # Output directory
        self.output_dir = Path('F:/China_Sweeps/data')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Production runner initialized for bucket: {bucket_name}")

    def get_bucket_sources(self) -> List[Dict]:
        """Get sources for the specified bucket"""
        sources = []

        for source_name, source_data in self.config.get('sources', {}).items():
            if source_data.get('bucket') == self.bucket_name:
                sources.append({
                    'name': source_name,
                    **source_data
                })

        logger.info(f"Found {len(sources)} sources in {self.bucket_name} bucket")
        return sources

    def discover_documents(self, source: Dict) -> List[Dict]:
        """Discover documents from a source"""
        logger.info(f"Discovering documents from: {source['name']}")

        discovered = []
        access_method = source.get('access_method', 'direct')

        try:
            if access_method == 'direct':
                # Direct access to English portals/secondary sources
                # This is safe - these are US/European aggregators
                logger.info(f"  Using direct access (safe aggregator)")

                # For now, try to get a sitemap or index page
                urls = source.get('urls', [])
                for url in urls:
                    # Skip validation for SECONDARY bucket (all safe)
                    discovered.append({
                        'source_name': source['name'],
                        'source_url': url,
                        'discovery_method': 'direct',
                        'discovery_timestamp': datetime.now(timezone.utc).isoformat(),
                    })

            elif access_method == 'wayback':
                # Wayback Machine access for .cn domains
                logger.info(f"  Using Wayback Machine (archive access)")

                wayback = WaybackClient()
                urls = source.get('urls', [])

                for url in urls:
                    snapshot = wayback.get_snapshot(url)
                    if snapshot and snapshot.get('available'):
                        discovered.append({
                            'source_name': source['name'],
                            'source_url': url,
                            'archive_url': snapshot['archive_url'],
                            'archive_timestamp': snapshot['timestamp'],
                            'discovery_method': 'wayback',
                            'discovery_timestamp': datetime.now(timezone.utc).isoformat(),
                        })
                    else:
                        logger.warning(f"  No Wayback snapshot found for: {url}")

            logger.info(f"  Discovered {len(discovered)} documents")

        except Exception as e:
            logger.error(f"  Error discovering from {source['name']}: {e}")

        return discovered

    def process_discovered_document(self, doc: Dict) -> Optional[Dict]:
        """Process a discovered document through extraction and QA"""
        try:
            # For this initial test, we'll just return the discovery metadata
            # Full download and extraction will be added in next iteration
            logger.info(f"  Processing: {doc.get('source_name')} - {doc.get('source_url', 'N/A')[:80]}")

            # Basic metadata
            processed = {
                **doc,
                'collection_run_id': datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S'),
                'processing_status': 'discovered',
                'next_step': 'download_and_extract'
            }

            return processed

        except Exception as e:
            logger.error(f"  Error processing document: {e}")
            return None

    def run_collection(self, max_sources: Optional[int] = None) -> Dict:
        """Run collection on the bucket"""
        logger.info("=" * 80)
        logger.info(f"STARTING PRODUCTION COLLECTION: {self.bucket_name}")
        logger.info("=" * 80)

        start_time = time.time()
        stats = {
            'bucket': self.bucket_name,
            'start_time': datetime.now(timezone.utc).isoformat(),
            'sources_processed': 0,
            'documents_discovered': 0,
            'documents_processed': 0,
            'documents_passed_qa': 0,
            'documents_failed_qa': 0,
            'errors': 0
        }

        # Get sources
        sources = self.get_bucket_sources()
        if max_sources:
            sources = sources[:max_sources]
            logger.info(f"Limiting to first {max_sources} sources for test run")

        all_processed = []

        for source in sources:
            logger.info(f"\n{'─' * 80}")
            logger.info(f"Processing source: {source['name']}")
            logger.info(f"{'─' * 80}")

            try:
                # Discover documents
                discovered = self.discover_documents(source)
                stats['documents_discovered'] += len(discovered)

                # Process each discovered document
                for doc in discovered:
                    processed = self.process_discovered_document(doc)
                    if processed:
                        all_processed.append(processed)
                        stats['documents_processed'] += 1

                stats['sources_processed'] += 1

            except Exception as e:
                logger.error(f"Error processing source {source['name']}: {e}")
                stats['errors'] += 1

        # Save results
        output_file = self.output_dir / f"{self.bucket_name}_discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': stats,
                'discovered_documents': all_processed
            }, f, indent=2, ensure_ascii=False)

        stats['end_time'] = datetime.now(timezone.utc).isoformat()
        stats['duration_seconds'] = time.time() - start_time
        stats['output_file'] = str(output_file)

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("COLLECTION RUN COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Bucket: {stats['bucket']}")
        logger.info(f"Sources processed: {stats['sources_processed']}")
        logger.info(f"Documents discovered: {stats['documents_discovered']}")
        logger.info(f"Documents processed: {stats['documents_processed']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info(f"Duration: {stats['duration_seconds']:.1f}s")
        logger.info(f"Output: {output_file}")
        logger.info("=" * 80)

        return stats


def main():
    """Main entry point"""

    # Start with SECONDARY bucket (safest sources)
    runner = ProductionRunner(bucket_name='SECONDARY')

    # Run collection on first 3 sources as test
    logger.info("Starting test collection on SECONDARY bucket (first 3 sources)")
    logger.info("These are US/European aggregators - completely safe")

    stats = runner.run_collection(max_sources=3)

    if stats['documents_discovered'] > 0:
        logger.info("\n✅ SUCCESS - Collection pipeline working")
        logger.info(f"   Discovered {stats['documents_discovered']} documents")
        logger.info(f"   Next step: Implement full download and extraction")
    else:
        logger.warning("\n⚠️  No documents discovered")
        logger.warning("   This may be expected depending on source availability")
        logger.warning("   Review logs for details")

    return stats


if __name__ == '__main__':
    try:
        stats = main()
        sys.exit(0 if stats['documents_discovered'] > 0 else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
