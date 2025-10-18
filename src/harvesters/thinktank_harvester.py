#!/usr/bin/env python3
"""
Think Tank Harvester - Main Orchestrator

This module coordinates the harvesting and analysis of think tank research
on China's S&T policies, focusing on key technology domains and policy levers.

Key Features:
- Orchestrates crawling, parsing, classification, and summarization
- Handles deduplication and canonicalization
- Manages full provenance tracking
- Supports multi-language content with translation
- Generates structured outputs (XLSX/CSV/JSONL)
"""

import asyncio
import logging
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from urllib.parse import urljoin
import pandas as pd
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed

from .thinktank_crawler import ThinkTankCrawler
from .thinktank_parser import ThinkTankParser
from .thinktank_classifier import ThinkTankClassifier
from .thinktank_summarizer import ThinkTankSummarizer


@dataclass
class HarvestConfig:
    """Configuration for think tank harvesting"""
    output_dir: Path
    max_concurrent_sites: int = 3
    max_concurrent_pages: int = 10
    min_delay_between_requests: float = 1.0
    max_retries: int = 3
    content_age_limit_days: int = 1095  # 3 years
    enable_translation: bool = True
    include_pdf: bool = True
    include_html: bool = True
    deduplication_threshold: float = 0.85
    save_raw_files: bool = True


@dataclass
class ThinkTankDocument:
    """Represents a harvested think tank document"""
    source_id: str
    title: str
    url: str
    publish_date: Optional[datetime]
    authors: List[str]
    content_text: str
    content_html: Optional[str]
    abstract: Optional[str]
    document_type: str  # report, briefing, article, etc.
    language: str
    file_hash: str
    file_size: int
    raw_file_path: Optional[Path]

    # Analysis results
    summary: Optional[str] = None
    relevance_note: Optional[str] = None
    classification_scores: Optional[Dict[str, float]] = None
    tech_domains: Optional[List[str]] = None
    policy_levers: Optional[List[str]] = None
    china_focus_score: Optional[float] = None
    arctic_focus_score: Optional[float] = None
    mcf_dualuse_score: Optional[float] = None

    # Provenance
    crawl_timestamp: datetime = None
    archive_url: Optional[str] = None
    robots_txt_compliant: bool = True

    def __post_init__(self):
        if self.crawl_timestamp is None:
            self.crawl_timestamp = datetime.utcnow()


class ThinkTankHarvester:
    """Main orchestrator for think tank research harvesting"""

    def __init__(self, config: HarvestConfig, sources_config_path: Path):
        self.config = config
        self.sources_config_path = sources_config_path
        self.logger = self._setup_logging()

        # Initialize components
        self.crawler = ThinkTankCrawler(
            max_concurrent=config.max_concurrent_pages,
            min_delay=config.min_delay_between_requests,
            max_retries=config.max_retries
        )
        self.parser = ThinkTankParser()
        self.classifier = ThinkTankClassifier()
        self.summarizer = ThinkTankSummarizer(
            enable_translation=config.enable_translation
        )

        # Storage
        self.documents: List[ThinkTankDocument] = []
        self.document_hashes: Set[str] = set()
        self.duplicate_count = 0

        # Load sources configuration
        self.sources = self._load_sources_config()

        # Ensure output directories exist
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        (self.config.output_dir / "raw_files").mkdir(exist_ok=True)
        (self.config.output_dir / "processed").mkdir(exist_ok=True)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("thinktank_harvester")
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # File handler
        log_file = self.config.output_dir / "harvest.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    def _load_sources_config(self) -> Dict[str, Any]:
        """Load think tank sources configuration"""
        try:
            with open(self.sources_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load sources config: {e}")
            raise

    def _calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content for deduplication"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _is_duplicate(self, content_hash: str) -> bool:
        """Check if content is duplicate based on hash"""
        return content_hash in self.document_hashes

    def _is_content_recent(self, publish_date: Optional[datetime]) -> bool:
        """Check if content is within the age limit"""
        if not publish_date:
            return True  # Include undated content

        cutoff_date = datetime.utcnow() - timedelta(days=self.config.content_age_limit_days)
        return publish_date >= cutoff_date

    async def harvest_all_sources(self) -> List[ThinkTankDocument]:
        """Harvest content from all configured think tank sources"""
        self.logger.info(f"Starting harvest of {len(self.sources['think_tanks'])} think tank sources")

        # Create semaphore to limit concurrent site processing
        semaphore = asyncio.Semaphore(self.config.max_concurrent_sites)

        # Process all sources concurrently
        tasks = []
        for source_id, source_config in self.sources['think_tanks'].items():
            task = self._harvest_source_with_semaphore(semaphore, source_id, source_config)
            tasks.append(task)

        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        # Post-processing
        await self._post_process_documents()

        self.logger.info(f"Harvest completed. Collected {len(self.documents)} documents")
        self.logger.info(f"Duplicates found and skipped: {self.duplicate_count}")

        return self.documents

    async def _harvest_source_with_semaphore(self, semaphore: asyncio.Semaphore,
                                           source_id: str, source_config: Dict[str, Any]):
        """Harvest a single source with semaphore control"""
        async with semaphore:
            try:
                await self._harvest_single_source(source_id, source_config)
            except Exception as e:
                self.logger.error(f"Failed to harvest source {source_id}: {e}")

    async def _harvest_single_source(self, source_id: str, source_config: Dict[str, Any]):
        """Harvest content from a single think tank source"""
        self.logger.info(f"Harvesting source: {source_id}")

        base_url = source_config['base_url']
        search_urls = source_config.get('search_urls', [])
        publication_urls = source_config.get('publication_urls', [])

        # Collect all URLs to crawl
        urls_to_crawl = []
        urls_to_crawl.extend(search_urls)
        urls_to_crawl.extend(publication_urls)

        # Add any additional discovery URLs
        if source_config.get('discover_urls'):
            discovered_urls = await self.crawler.discover_urls(
                base_url, source_config['discover_urls']
            )
            urls_to_crawl.extend(discovered_urls)

        # Crawl and process each URL
        for url in urls_to_crawl:
            try:
                await self._process_url(source_id, url, source_config)
            except Exception as e:
                self.logger.warning(f"Failed to process URL {url}: {e}")

    async def _process_url(self, source_id: str, url: str, source_config: Dict[str, Any]):
        """Process a single URL and extract documents"""
        # Crawl the page
        crawl_result = await self.crawler.crawl_url(url, source_config)
        if not crawl_result or not crawl_result.success:
            return

        # Parse content based on type
        if crawl_result.content_type == 'text/html':
            documents = await self._parse_html_page(source_id, crawl_result, source_config)
        elif crawl_result.content_type == 'application/pdf':
            documents = await self._parse_pdf_document(source_id, crawl_result, source_config)
        else:
            self.logger.debug(f"Skipping unsupported content type: {crawl_result.content_type}")
            return

        # Process each extracted document
        for doc in documents:
            await self._process_document(doc)

    async def _parse_html_page(self, source_id: str, crawl_result, source_config: Dict[str, Any]) -> List[ThinkTankDocument]:
        """Parse HTML page and extract documents"""
        if not self.config.include_html:
            return []

        parsed_content = await self.parser.parse_html(
            crawl_result.content, crawl_result.url, source_config
        )

        documents = []
        for content_item in parsed_content:
            # Create document hash
            content_hash = self._calculate_content_hash(content_item['text'])

            doc = ThinkTankDocument(
                source_id=source_id,
                title=content_item.get('title', 'Untitled'),
                url=content_item.get('url', crawl_result.url),
                publish_date=content_item.get('publish_date'),
                authors=content_item.get('authors', []),
                content_text=content_item['text'],
                content_html=content_item.get('html'),
                abstract=content_item.get('abstract'),
                document_type=content_item.get('document_type', 'article'),
                language=content_item.get('language', 'en'),
                file_hash=content_hash,
                file_size=len(content_item['text'].encode('utf-8')),
                raw_file_path=None,
                crawl_timestamp=datetime.utcnow(),
                robots_txt_compliant=crawl_result.robots_compliant
            )
            documents.append(doc)

        return documents

    async def _parse_pdf_document(self, source_id: str, crawl_result, source_config: Dict[str, Any]) -> List[ThinkTankDocument]:
        """Parse PDF document"""
        if not self.config.include_pdf:
            return []

        parsed_content = await self.parser.parse_pdf(
            crawl_result.content, crawl_result.url, source_config
        )

        if not parsed_content:
            return []

        # Create document hash
        content_hash = self._calculate_content_hash(parsed_content['text'])

        # Save raw PDF file if configured
        raw_file_path = None
        if self.config.save_raw_files:
            filename = f"{source_id}_{content_hash[:16]}.pdf"
            raw_file_path = self.config.output_dir / "raw_files" / filename
            with open(raw_file_path, 'wb') as f:
                f.write(crawl_result.content)

        doc = ThinkTankDocument(
            source_id=source_id,
            title=parsed_content.get('title', 'Untitled'),
            url=crawl_result.url,
            publish_date=parsed_content.get('publish_date'),
            authors=parsed_content.get('authors', []),
            content_text=parsed_content['text'],
            content_html=None,
            abstract=parsed_content.get('abstract'),
            document_type='report',
            language=parsed_content.get('language', 'en'),
            file_hash=content_hash,
            file_size=len(crawl_result.content),
            raw_file_path=raw_file_path,
            crawl_timestamp=datetime.utcnow(),
            robots_txt_compliant=crawl_result.robots_compliant
        )

        return [doc]

    async def _process_document(self, doc: ThinkTankDocument):
        """Process a document through the analysis pipeline"""
        # Check for duplicates
        if self._is_duplicate(doc.file_hash):
            self.duplicate_count += 1
            self.logger.debug(f"Skipping duplicate document: {doc.title}")
            return

        # Check content age
        if not self._is_content_recent(doc.publish_date):
            self.logger.debug(f"Skipping old document: {doc.title}")
            return

        # Apply keyword pre-filter
        if not await self.classifier.keyword_prefilter(doc.content_text):
            self.logger.debug(f"Document failed keyword pre-filter: {doc.title}")
            return

        # Classify document
        classification_result = await self.classifier.classify_document(doc.content_text)
        doc.classification_scores = classification_result['scores']
        doc.tech_domains = classification_result['tech_domains']
        doc.policy_levers = classification_result['policy_levers']
        doc.china_focus_score = classification_result['china_focus_score']
        doc.arctic_focus_score = classification_result['arctic_focus_score']
        doc.mcf_dualuse_score = classification_result['mcf_dualuse_score']

        # Check if document passes classification threshold
        if not self._passes_classification_threshold(classification_result):
            self.logger.debug(f"Document failed classification threshold: {doc.title}")
            return

        # Generate summary and relevance note
        summary_result = await self.summarizer.generate_summary(
            doc.content_text, doc.title, classification_result
        )
        doc.summary = summary_result['summary']
        doc.relevance_note = summary_result['relevance_note']

        # Add to collection
        self.document_hashes.add(doc.file_hash)
        self.documents.append(doc)

        self.logger.info(f"Added document: {doc.title} (Score: {doc.china_focus_score:.2f})")

    def _passes_classification_threshold(self, classification_result: Dict[str, Any]) -> bool:
        """Check if document passes classification thresholds"""
        # Minimum China focus score
        if classification_result['china_focus_score'] < 0.3:
            return False

        # Must have at least one relevant tech domain or policy lever
        if not classification_result['tech_domains'] and not classification_result['policy_levers']:
            return False

        return True

    async def _post_process_documents(self):
        """Post-process documents for final quality checks and enhancements"""
        self.logger.info("Starting post-processing of documents")

        # Sort documents by relevance score
        self.documents.sort(
            key=lambda x: (x.china_focus_score or 0), reverse=True
        )

        # Apply advanced deduplication based on content similarity
        if self.config.deduplication_threshold < 1.0:
            self.documents = await self._deduplicate_by_similarity()

        self.logger.info(f"Post-processing completed. Final count: {len(self.documents)}")

    async def _deduplicate_by_similarity(self) -> List[ThinkTankDocument]:
        """Remove near-duplicate documents based on content similarity"""
        self.logger.info("Performing similarity-based deduplication")

        # For now, implement basic title-based deduplication
        # In a full implementation, this would use embedding similarity
        seen_titles = set()
        deduplicated = []

        for doc in self.documents:
            title_normalized = doc.title.lower().strip()
            if title_normalized not in seen_titles:
                seen_titles.add(title_normalized)
                deduplicated.append(doc)
            else:
                self.logger.debug(f"Removed similar document: {doc.title}")

        return deduplicated

    def export_results(self, formats: List[str] = None) -> Dict[str, Path]:
        """Export harvested documents in specified formats"""
        if formats is None:
            formats = ['xlsx', 'csv', 'jsonl']

        exported_files = {}
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

        # Prepare data for export
        export_data = []
        for doc in self.documents:
            doc_dict = asdict(doc)
            # Convert Path objects to strings
            if doc_dict['raw_file_path']:
                doc_dict['raw_file_path'] = str(doc_dict['raw_file_path'])
            # Convert datetime objects to ISO strings
            for key, value in doc_dict.items():
                if isinstance(value, datetime):
                    doc_dict[key] = value.isoformat()
            export_data.append(doc_dict)

        # Export in each requested format
        for format_type in formats:
            try:
                if format_type.lower() == 'xlsx':
                    file_path = self.config.output_dir / f"thinktank_harvest_{timestamp}.xlsx"
                    df = pd.DataFrame(export_data)
                    df.to_excel(file_path, index=False)
                    exported_files['xlsx'] = file_path

                elif format_type.lower() == 'csv':
                    file_path = self.config.output_dir / f"thinktank_harvest_{timestamp}.csv"
                    df = pd.DataFrame(export_data)
                    df.to_csv(file_path, index=False)
                    exported_files['csv'] = file_path

                elif format_type.lower() == 'jsonl':
                    file_path = self.config.output_dir / f"thinktank_harvest_{timestamp}.jsonl"
                    with open(file_path, 'w', encoding='utf-8') as f:
                        for item in export_data:
                            f.write(json.dumps(item, ensure_ascii=False) + '\n')
                    exported_files['jsonl'] = file_path

                self.logger.info(f"Exported {format_type.upper()}: {file_path}")

            except Exception as e:
                self.logger.error(f"Failed to export {format_type}: {e}")

        return exported_files

    def generate_harvest_report(self) -> Dict[str, Any]:
        """Generate a comprehensive harvest report"""
        report = {
            'harvest_summary': {
                'total_documents': len(self.documents),
                'duplicates_removed': self.duplicate_count,
                'sources_processed': len(self.sources['think_tanks']),
                'harvest_timestamp': datetime.utcnow().isoformat()
            },
            'source_breakdown': {},
            'classification_stats': {
                'tech_domains': {},
                'policy_levers': {},
                'avg_china_focus_score': 0,
                'avg_arctic_focus_score': 0,
                'avg_mcf_dualuse_score': 0
            },
            'content_stats': {
                'by_language': {},
                'by_document_type': {},
                'by_publication_year': {}
            }
        }

        # Calculate statistics
        china_scores = []
        arctic_scores = []
        mcf_scores = []

        for doc in self.documents:
            # Source breakdown
            if doc.source_id not in report['source_breakdown']:
                report['source_breakdown'][doc.source_id] = 0
            report['source_breakdown'][doc.source_id] += 1

            # Classification stats
            if doc.china_focus_score:
                china_scores.append(doc.china_focus_score)
            if doc.arctic_focus_score:
                arctic_scores.append(doc.arctic_focus_score)
            if doc.mcf_dualuse_score:
                mcf_scores.append(doc.mcf_dualuse_score)

            # Tech domains
            for domain in (doc.tech_domains or []):
                if domain not in report['classification_stats']['tech_domains']:
                    report['classification_stats']['tech_domains'][domain] = 0
                report['classification_stats']['tech_domains'][domain] += 1

            # Policy levers
            for lever in (doc.policy_levers or []):
                if lever not in report['classification_stats']['policy_levers']:
                    report['classification_stats']['policy_levers'][lever] = 0
                report['classification_stats']['policy_levers'][lever] += 1

            # Content stats
            lang = doc.language or 'unknown'
            if lang not in report['content_stats']['by_language']:
                report['content_stats']['by_language'][lang] = 0
            report['content_stats']['by_language'][lang] += 1

            doc_type = doc.document_type or 'unknown'
            if doc_type not in report['content_stats']['by_document_type']:
                report['content_stats']['by_document_type'][doc_type] = 0
            report['content_stats']['by_document_type'][doc_type] += 1

            if doc.publish_date:
                year = str(doc.publish_date.year)
                if year not in report['content_stats']['by_publication_year']:
                    report['content_stats']['by_publication_year'][year] = 0
                report['content_stats']['by_publication_year'][year] += 1

        # Calculate averages
        if china_scores:
            report['classification_stats']['avg_china_focus_score'] = sum(china_scores) / len(china_scores)
        if arctic_scores:
            report['classification_stats']['avg_arctic_focus_score'] = sum(arctic_scores) / len(arctic_scores)
        if mcf_scores:
            report['classification_stats']['avg_mcf_dualuse_score'] = sum(mcf_scores) / len(mcf_scores)

        # Save report
        report_path = self.config.output_dir / f"harvest_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Harvest report saved: {report_path}")
        return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Think Tank Research Harvester")
    parser.add_argument("--config", type=Path, required=True, help="Sources configuration file")
    parser.add_argument("--output", type=Path, required=True, help="Output directory")
    parser.add_argument("--formats", nargs="+", default=['xlsx', 'csv', 'jsonl'],
                       help="Export formats")

    args = parser.parse_args()

    # Create configuration
    config = HarvestConfig(output_dir=args.output)

    # Run harvester
    harvester = ThinkTankHarvester(config, args.config)

    # Run the async harvest
    loop = asyncio.get_event_loop()
    documents = loop.run_until_complete(harvester.harvest_all_sources())

    # Export results
    exported_files = harvester.export_results(args.formats)
    report = harvester.generate_harvest_report()

    print(f"Harvest completed successfully!")
    print(f"Documents collected: {len(documents)}")
    print(f"Files exported: {list(exported_files.keys())}")
