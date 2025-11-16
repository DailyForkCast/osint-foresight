#!/usr/bin/env python3
"""
Schema Converters - Convert legacy formats to Unified Schema
Global Tech Intelligence System

Converts from:
- US_Gov collector format (30 fields) → UnifiedDocument
- ThinkTank collector format (20 fields) → UnifiedDocument
- China collector format (30 fields) → UnifiedDocument
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import logging

from .unified_schema import (
    UnifiedDocument,
    PublisherInfo,
    DateMetadata,
    ContentMetadata,
    FileMetadata,
    ProvenanceChain,
    ExtractionMetadata,
    PublisherType,
    DocumentType,
    MirrorSourceType,
    ConfidenceLevel,
    LanguageCode,
    TopicCategory,
)

logger = logging.getLogger(__name__)


# ============================================================================
# BASE CONVERTER
# ============================================================================

class BaseConverter:
    """Base class for schema converters"""

    def __init__(self):
        self.conversion_stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }

    def safe_get(self, data: Dict, key: str, default: Any = None) -> Any:
        """Safely get value from dict with default"""
        return data.get(key, default)

    def parse_datetime(self, date_str: Optional[str]) -> datetime:
        """Parse datetime string to datetime object"""
        if not date_str:
            return datetime.now()

        try:
            # Try ISO format
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            # Try common formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue

        logger.warning(f"Could not parse date: {date_str}, using current time")
        return datetime.now()

    def parse_enum(self, value: str, enum_class, default):
        """Parse string to enum with default fallback"""
        if not value:
            return default

        try:
            # Try direct value
            return enum_class(value)
        except ValueError:
            # Try uppercase
            try:
                return enum_class(value.upper())
            except ValueError:
                # Try lowercase
                try:
                    return enum_class(value.lower())
                except ValueError:
                    logger.warning(f"Could not parse {value} as {enum_class.__name__}, using {default}")
                    return default

    def calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()


# ============================================================================
# US_GOV CONVERTER
# ============================================================================

class USGovConverter(BaseConverter):
    """
    Convert US_Gov collector format to UnifiedDocument

    US_Gov Schema (30 fields):
    - title, publisher_org, publisher_type, document_type
    - publication_date_iso, content_text, content_length
    - language, keywords, topics, hash_sha256, canonical_url
    - extraction_ok, qa_passed, qa_issues, collection_run_id
    - Missing: provenance chain, archive URLs
    """

    def convert(self, us_gov_doc: Dict[str, Any]) -> UnifiedDocument:
        """
        Convert US_Gov document to UnifiedDocument

        Args:
            us_gov_doc: Document in US_Gov format

        Returns:
            UnifiedDocument instance

        Raises:
            ValueError: If required fields are missing
        """
        self.conversion_stats['total'] += 1

        try:
            # Publisher info
            publisher = PublisherInfo(
                publisher_org=us_gov_doc['publisher_org'],
                publisher_type=self.parse_enum(
                    self.safe_get(us_gov_doc, 'publisher_type', 'government'),
                    PublisherType,
                    PublisherType.GOVERNMENT
                ),
                publisher_country='US',  # US_Gov collector is US-only
                publisher_domain=self._extract_domain(
                    self.safe_get(us_gov_doc, 'canonical_url', '')
                ),
                verified_publisher=True  # US gov sources are verified
            )

            # Date metadata
            dates = DateMetadata(
                publication_date_iso=us_gov_doc['publication_date_iso'],
                date_source='document_metadata',
                date_confidence=ConfidenceLevel.HIGH,  # US gov sources reliable
                date_validation_sources=['document_metadata'],
                last_modified=None
            )

            # Content metadata
            topics_list = [
                self.parse_enum(t, TopicCategory, TopicCategory.UNKNOWN)
                for t in self.safe_get(us_gov_doc, 'topics', [])
            ]

            content = ContentMetadata(
                content_text=us_gov_doc['content_text'],
                content_length=self.safe_get(
                    us_gov_doc, 'content_length', len(us_gov_doc['content_text'])
                ),
                language=self.parse_enum(
                    self.safe_get(us_gov_doc, 'language', 'en'),
                    LanguageCode,
                    LanguageCode.EN
                ),
                title=us_gov_doc['title'],
                title_en=us_gov_doc['title'],  # Already English
                description=self.safe_get(us_gov_doc, 'description'),
                keywords=self.safe_get(us_gov_doc, 'keywords', []),
                topics=topics_list,
                subtopics=self.safe_get(us_gov_doc, 'subtopics', []),
                entities=self.safe_get(us_gov_doc, 'entities', [])
            )

            # File metadata
            canonical_url = us_gov_doc['canonical_url']
            hash_val = self.safe_get(us_gov_doc, 'hash_sha256')
            if not hash_val:
                hash_val = self.calculate_hash(us_gov_doc['content_text'])

            file_metadata = FileMetadata(
                hash_sha256=hash_val,
                text_hash_sha256=self.calculate_hash(us_gov_doc['content_text']),
                file_size_bytes=self.safe_get(us_gov_doc, 'file_size_bytes'),
                file_format=self._detect_format(canonical_url),
                canonical_url=canonical_url,
                alternate_urls=self.safe_get(us_gov_doc, 'alternate_urls', [])
            )

            # Provenance (US_Gov does direct access - safe)
            provenance = ProvenanceChain(
                discovery_method=self.safe_get(us_gov_doc, 'discovery_method', 'api'),
                discovery_timestamp=self.parse_datetime(
                    self.safe_get(us_gov_doc, 'discovery_timestamp')
                ),
                fetch_url=canonical_url,
                archive_url=None,  # Direct access
                archive_timestamp=None,
                mirror_source_type=MirrorSourceType.DIRECT,
                safe_access_validated=True,  # US gov domains are safe
                blocked_domain_detected=False,
                redirect_chain=self.safe_get(us_gov_doc, 'redirect_chain', [])
            )

            # Extraction metadata
            extraction = ExtractionMetadata(
                extraction_timestamp=self.parse_datetime(
                    self.safe_get(us_gov_doc, 'extraction_timestamp')
                ),
                extraction_ok=self.safe_get(us_gov_doc, 'extraction_ok', False),
                extraction_notes=self.safe_get(us_gov_doc, 'extraction_notes', []),
                qa_passed=self.safe_get(us_gov_doc, 'qa_passed', False),
                qa_issues=self.safe_get(us_gov_doc, 'qa_issues', []),
                redteam_reviewed=False,  # Default
                verified_safe_source=True,  # US gov is verified safe
                reliability_weight=1.0,  # US gov sources highly reliable
                duplicate_detected=self.safe_get(us_gov_doc, 'duplicate_detected', False),
                duplicate_of=self.safe_get(us_gov_doc, 'duplicate_of')
            )

            # Create unified document
            unified = UnifiedDocument(
                document_id=self.safe_get(us_gov_doc, 'document_id'),
                document_type=self.parse_enum(
                    self.safe_get(us_gov_doc, 'document_type', 'policy'),
                    DocumentType,
                    DocumentType.POLICY
                ),
                publisher=publisher,
                dates=dates,
                content=content,
                file_metadata=file_metadata,
                provenance=provenance,
                extraction=extraction,
                collection_run_id=self.safe_get(us_gov_doc, 'collection_run_id'),
                collector_name='us_gov_tech_sweep',
                collector_version='1.0.0',
                extensions={'source_format': 'us_gov'}
            )

            self.conversion_stats['successful'] += 1
            return unified

        except Exception as e:
            self.conversion_stats['failed'] += 1
            self.conversion_stats['errors'].append(str(e))
            logger.error(f"Error converting US_Gov document: {e}")
            raise

    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        if not url:
            return None
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return None

    def _detect_format(self, url: str) -> str:
        """Detect file format from URL"""
        if '.pdf' in url.lower():
            return 'pdf'
        elif '.xml' in url.lower():
            return 'xml'
        elif '.json' in url.lower():
            return 'json'
        else:
            return 'html'


# ============================================================================
# THINKTANK CONVERTER
# ============================================================================

class ThinkTankConverter(BaseConverter):
    """
    Convert ThinkTank collector format to UnifiedDocument

    ThinkTank Schema (20 fields):
    - title, organization, document_type, publication_date
    - url, content, topics, hash, extracted_at
    - Missing: many unified fields (provenance, QA, etc.)
    """

    def convert(self, thinktank_doc: Dict[str, Any]) -> UnifiedDocument:
        """
        Convert ThinkTank document to UnifiedDocument

        Args:
            thinktank_doc: Document in ThinkTank format

        Returns:
            UnifiedDocument instance

        Raises:
            ValueError: If required fields are missing
        """
        self.conversion_stats['total'] += 1

        try:
            # Publisher info
            publisher = PublisherInfo(
                publisher_org=thinktank_doc['organization'],
                publisher_type=PublisherType.THINK_TANK,
                publisher_country=self.safe_get(thinktank_doc, 'country'),
                publisher_domain=self._extract_domain(thinktank_doc['url']),
                verified_publisher=self.safe_get(thinktank_doc, 'verified', True)
            )

            # Date metadata
            dates = DateMetadata(
                publication_date_iso=thinktank_doc['publication_date'],
                date_source='document_metadata',
                date_confidence=ConfidenceLevel.MEDIUM,
                date_validation_sources=['document_metadata'],
                last_modified=None
            )

            # Content metadata
            topics_list = [
                self.parse_enum(t, TopicCategory, TopicCategory.UNKNOWN)
                for t in self.safe_get(thinktank_doc, 'topics', [])
            ]

            content = ContentMetadata(
                content_text=thinktank_doc['content'],
                content_length=len(thinktank_doc['content']),
                language=self.parse_enum(
                    self.safe_get(thinktank_doc, 'language', 'en'),
                    LanguageCode,
                    LanguageCode.EN
                ),
                title=thinktank_doc['title'],
                title_en=thinktank_doc['title'],
                description=self.safe_get(thinktank_doc, 'description'),
                keywords=self.safe_get(thinktank_doc, 'keywords', []),
                topics=topics_list,
                subtopics=self.safe_get(thinktank_doc, 'subtopics', []),
                entities=self.safe_get(thinktank_doc, 'entities', [])
            )

            # File metadata
            url = thinktank_doc['url']
            hash_val = self.safe_get(thinktank_doc, 'hash')
            if not hash_val:
                hash_val = self.calculate_hash(thinktank_doc['content'])

            file_metadata = FileMetadata(
                hash_sha256=hash_val,
                text_hash_sha256=self.calculate_hash(thinktank_doc['content']),
                file_size_bytes=self.safe_get(thinktank_doc, 'file_size'),
                file_format=self._detect_format(url),
                canonical_url=url,
                alternate_urls=[]
            )

            # Provenance (ThinkTank does direct access)
            provenance = ProvenanceChain(
                discovery_method=self.safe_get(thinktank_doc, 'discovery_method', 'rss'),
                discovery_timestamp=self.parse_datetime(
                    self.safe_get(thinktank_doc, 'discovered_at')
                ),
                fetch_url=url,
                archive_url=None,
                archive_timestamp=None,
                mirror_source_type=MirrorSourceType.DIRECT,
                safe_access_validated=True,
                blocked_domain_detected=False,
                redirect_chain=[]
            )

            # Extraction metadata
            extraction = ExtractionMetadata(
                extraction_timestamp=self.parse_datetime(
                    self.safe_get(thinktank_doc, 'extracted_at')
                ),
                extraction_ok=True,  # Assume success if doc exists
                extraction_notes=[],
                qa_passed=self.safe_get(thinktank_doc, 'qa_passed', False),
                qa_issues=self.safe_get(thinktank_doc, 'qa_issues', []),
                redteam_reviewed=False,
                verified_safe_source=True,
                reliability_weight=0.8,  # Think tanks generally reliable
                duplicate_detected=False,
                duplicate_of=None
            )

            # Create unified document
            unified = UnifiedDocument(
                document_id=self.safe_get(thinktank_doc, 'id'),
                document_type=self.parse_enum(
                    self.safe_get(thinktank_doc, 'document_type', 'report'),
                    DocumentType,
                    DocumentType.REPORT
                ),
                publisher=publisher,
                dates=dates,
                content=content,
                file_metadata=file_metadata,
                provenance=provenance,
                extraction=extraction,
                collection_run_id=self.safe_get(thinktank_doc, 'collection_id'),
                collector_name='thinktank_global',
                collector_version='1.0.0',
                extensions={'source_format': 'thinktank'}
            )

            self.conversion_stats['successful'] += 1
            return unified

        except Exception as e:
            self.conversion_stats['failed'] += 1
            self.conversion_stats['errors'].append(str(e))
            logger.error(f"Error converting ThinkTank document: {e}")
            raise

    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        if not url:
            return None
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return None

    def _detect_format(self, url: str) -> str:
        """Detect file format from URL"""
        if '.pdf' in url.lower():
            return 'pdf'
        elif '.html' in url.lower() or '.htm' in url.lower():
            return 'html'
        else:
            return 'html'  # Default


# ============================================================================
# CHINA CONVERTER
# ============================================================================

class ChinaConverter(BaseConverter):
    """
    Convert China collector format to UnifiedDocument

    China Schema (30 fields with full provenance):
    - Has most fields including archive URLs, provenance chain
    - Best coverage of unified schema (75%)
    - Full Safe Mode compliance
    """

    def convert(self, china_doc: Dict[str, Any]) -> UnifiedDocument:
        """
        Convert China document to UnifiedDocument

        Args:
            china_doc: Document in China format

        Returns:
            UnifiedDocument instance

        Raises:
            ValueError: If required fields are missing
        """
        self.conversion_stats['total'] += 1

        try:
            # Publisher info
            publisher = PublisherInfo(
                publisher_org=china_doc['publisher_org'],
                publisher_type=self.parse_enum(
                    self.safe_get(china_doc, 'publisher_type', 'government'),
                    PublisherType,
                    PublisherType.GOVERNMENT
                ),
                publisher_country='CN',  # China collector
                publisher_domain=self._extract_domain(
                    self.safe_get(china_doc, 'canonical_url', '')
                ),
                verified_publisher=self.safe_get(china_doc, 'verified_publisher', False)
            )

            # Date metadata
            date_list = self.safe_get(china_doc, 'publication_date', [None, None])
            if isinstance(date_list, list) and len(date_list) >= 2:
                pub_date = date_list[0] if date_list[0] else date_list[1]
            else:
                pub_date = date_list

            dates = DateMetadata(
                publication_date_iso=pub_date or datetime.now().isoformat()[:10],
                date_source=self.safe_get(china_doc, 'date_source'),
                date_confidence=self.parse_enum(
                    self.safe_get(china_doc, 'date_confidence', 'low'),
                    ConfidenceLevel,
                    ConfidenceLevel.LOW
                ),
                date_validation_sources=self.safe_get(china_doc, 'date_validation_sources', []),
                last_modified=None
            )

            # Content metadata
            topics_list = [
                self.parse_enum(t, TopicCategory, TopicCategory.UNKNOWN)
                for t in self.safe_get(china_doc, 'topics', [])
            ]

            content = ContentMetadata(
                content_text=china_doc['content_text'],
                content_length=self.safe_get(
                    china_doc, 'content_length', len(china_doc['content_text'])
                ),
                language=self.parse_enum(
                    self.safe_get(china_doc, 'language', 'zh'),
                    LanguageCode,
                    LanguageCode.ZH
                ),
                title=china_doc['title'],
                title_en=self.safe_get(china_doc, 'title_en'),
                description=self.safe_get(china_doc, 'description'),
                keywords=self.safe_get(china_doc, 'keywords', []),
                topics=topics_list,
                subtopics=self.safe_get(china_doc, 'subtopics', []),
                entities=self.safe_get(china_doc, 'entities', [])
            )

            # File metadata
            hash_val = self.safe_get(china_doc, 'hash_sha256')
            if not hash_val:
                hash_val = self.calculate_hash(china_doc['content_text'])

            file_metadata = FileMetadata(
                hash_sha256=hash_val,
                text_hash_sha256=self.safe_get(china_doc, 'text_hash_sha256'),
                file_size_bytes=self.safe_get(china_doc, 'file_size_bytes'),
                file_format=self.safe_get(china_doc, 'file_format', 'html'),
                canonical_url=china_doc['canonical_url'],
                alternate_urls=[]
            )

            # Provenance (China has full provenance!)
            provenance = ProvenanceChain(
                discovery_method=self.safe_get(china_doc, 'discovery_method', 'direct'),
                discovery_timestamp=self.parse_datetime(
                    self.safe_get(china_doc, 'discovery_timestamp')
                ),
                fetch_url=self.safe_get(china_doc, 'fetch_url', china_doc['canonical_url']),
                archive_url=self.safe_get(china_doc, 'archive_url'),
                archive_timestamp=self.safe_get(china_doc, 'archive_timestamp'),
                mirror_source_type=self.parse_enum(
                    self.safe_get(china_doc, 'fetch_mode', 'direct'),
                    MirrorSourceType,
                    MirrorSourceType.DIRECT
                ),
                safe_access_validated=True,  # China collector enforces Safe Mode
                blocked_domain_detected=self.safe_get(china_doc, 'blocked_domain', False),
                redirect_chain=[]
            )

            # Extraction metadata
            extraction = ExtractionMetadata(
                extraction_timestamp=self.parse_datetime(
                    self.safe_get(china_doc, 'extraction_timestamp')
                ),
                extraction_ok=self.safe_get(china_doc, 'extraction_ok', False),
                extraction_notes=self.safe_get(china_doc, 'extraction_notes', []),
                qa_passed=self.safe_get(china_doc, 'qa_passed', False),
                qa_issues=self.safe_get(china_doc, 'qa_issues', []),
                redteam_reviewed=False,
                verified_safe_source=self.safe_get(china_doc, 'verified_safe_source', False),
                reliability_weight=self.safe_get(china_doc, 'reliability_weight', 0.6),
                duplicate_detected=False,
                duplicate_of=None
            )

            # Create unified document
            unified = UnifiedDocument(
                document_id=self.safe_get(china_doc, 'document_id'),
                document_type=self.parse_enum(
                    self.safe_get(china_doc, 'document_type', 'policy'),
                    DocumentType,
                    DocumentType.POLICY
                ),
                publisher=publisher,
                dates=dates,
                content=content,
                file_metadata=file_metadata,
                provenance=provenance,
                extraction=extraction,
                collection_run_id=self.safe_get(china_doc, 'collection_run_id'),
                collector_name='china_policy',
                collector_version='1.0.0',
                extensions={'source_format': 'china'}
            )

            self.conversion_stats['successful'] += 1
            return unified

        except Exception as e:
            self.conversion_stats['failed'] += 1
            self.conversion_stats['errors'].append(str(e))
            logger.error(f"Error converting China document: {e}")
            raise

    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        if not url:
            return None
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return None


# ============================================================================
# OPENALEX CONVERTER
# ============================================================================

class OpenAlexConverter(BaseConverter):
    """
    Convert OpenAlex collaboration format to UnifiedDocument

    OpenAlex Schema (research collaboration records):
    - paper_id, doi, title, publication_year, publication_date
    - collaborating_countries, validations, cited_by_count
    - source_file, provenance, record_hash
    - Full validation and provenance tracking
    """

    def convert(self, openalex_doc: Dict[str, Any]) -> UnifiedDocument:
        """
        Convert OpenAlex collaboration document to UnifiedDocument

        Args:
            openalex_doc: Document in OpenAlex format

        Returns:
            UnifiedDocument instance

        Raises:
            ValueError: If required fields are missing
        """
        self.conversion_stats['total'] += 1

        try:
            # Determine primary country (first in collaborating_countries)
            countries = self.safe_get(openalex_doc, 'collaborating_countries', [])
            primary_country = countries[0] if countries else None

            # Get validation info for primary country
            validations = self.safe_get(openalex_doc, 'validations', {})
            if validations is None:
                validations = {}
            primary_validation = validations.get(primary_country, {}) if primary_country else {}
            if primary_validation is None:
                primary_validation = {}

            # Publisher info (research institution from primary country)
            # For OpenAlex, we don't have explicit organization names, so use generic
            publisher = PublisherInfo(
                publisher_org=f"Research Institution ({primary_validation.get('country_name', primary_country)})",
                publisher_type=PublisherType.ACADEMIC,
                publisher_country=primary_country,
                publisher_domain='openalex.org',  # OpenAlex as aggregator
                verified_publisher=True  # OpenAlex data is verified
            )

            # Date metadata
            pub_date = self.safe_get(openalex_doc, 'publication_date')
            if not pub_date:
                pub_year = self.safe_get(openalex_doc, 'publication_year')
                pub_date = f"{pub_year}-01-01" if pub_year else datetime.now().isoformat()[:10]

            # Validate date format - if invalid, use year or fallback
            try:
                datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                # Invalid date - try using year
                pub_year = self.safe_get(openalex_doc, 'publication_year')
                pub_date = f"{pub_year}-01-01" if pub_year else datetime.now().isoformat()[:10]

            dates = DateMetadata(
                publication_date_iso=pub_date,
                date_source='openalex_metadata',
                date_confidence=ConfidenceLevel.HIGH,  # OpenAlex dates are reliable
                date_validation_sources=['openalex_api'],
                last_modified=None
            )

            # Content metadata
            # Build content text from available fields
            title = openalex_doc['title']
            abstract = self.safe_get(openalex_doc, 'abstract', '')

            # Extract topics from validations
            topics = []
            keywords = []
            entities = []

            for country_code, validation in validations.items():
                # Skip if validation is None
                if validation is None:
                    continue

                matches = validation.get('matches', [])
                for match in matches:
                    match_text = match.get('text', '')
                    match_type = match.get('type', '')

                    if match_type == 'chinese_location':
                        entities.append(match_text)
                    else:
                        keywords.append(match_text)

            # Deduplicate
            keywords = list(set(keywords))[:20]  # Limit to 20
            entities = list(set(entities))[:20]

            # Detect language from validation
            languages_detected = []
            for validation in validations.values():
                # Skip if validation is None
                if validation is None:
                    continue
                lang_codes = validation.get('languages_detected', [])
                languages_detected.extend(lang_codes)

            primary_lang = languages_detected[0] if languages_detected else 'en'

            # Build content text - ensure minimum length
            content_text = f"{title}\n\n{abstract}" if abstract else title
            # Pad if too short (schema requires >=10 chars)
            if len(content_text) < 10:
                content_text = f"{title}\n\n[No abstract available]"

            content = ContentMetadata(
                content_text=content_text,
                content_length=len(content_text),
                language=self.parse_enum(primary_lang, LanguageCode, LanguageCode.EN),
                title=title,
                title_en=title,  # OpenAlex titles are typically English
                description=abstract,
                keywords=keywords,
                topics=[TopicCategory.SCIENCE_TECHNOLOGY],  # OpenAlex is research/science
                subtopics=self.safe_get(openalex_doc, 'topics', []),
                entities=entities
            )

            # File metadata
            paper_id = openalex_doc['paper_id']
            doi = self.safe_get(openalex_doc, 'doi')

            canonical_url = doi if doi else paper_id

            # Calculate proper SHA256 hash (record_hash is truncated, only 16 chars)
            # Use paper_id + title for uniqueness
            hash_val = self.calculate_hash(f"{paper_id}:{title}")

            file_metadata = FileMetadata(
                hash_sha256=hash_val,
                text_hash_sha256=self.calculate_hash(content_text),
                file_size_bytes=None,
                file_format='json',
                canonical_url=canonical_url,
                alternate_urls=[paper_id, doi] if doi else [paper_id]
            )

            # Provenance
            prov_data = self.safe_get(openalex_doc, 'provenance', {})

            provenance = ProvenanceChain(
                discovery_method='openalex_api',
                discovery_timestamp=self.parse_datetime(
                    prov_data.get('timestamp')
                ),
                fetch_url=paper_id,
                archive_url=None,  # OpenAlex is the archive
                archive_timestamp=None,
                mirror_source_type=MirrorSourceType.DIRECT,
                safe_access_validated=True,
                blocked_domain_detected=False,
                redirect_chain=[]
            )

            # Extraction metadata
            # Check fabrication status
            fabrication_check = prov_data.get('fabrication_check', 'UNKNOWN')
            qa_passed = fabrication_check == 'VERIFIED'

            extraction = ExtractionMetadata(
                extraction_timestamp=self.parse_datetime(
                    prov_data.get('timestamp')
                ),
                extraction_ok=True,  # If we have the doc, extraction succeeded
                extraction_notes=[],
                qa_passed=qa_passed,
                qa_issues=[] if qa_passed else ['fabrication_check_not_verified'],
                redteam_reviewed=False,
                verified_safe_source=True,  # OpenAlex is verified safe
                reliability_weight=0.9,  # OpenAlex is highly reliable
                duplicate_detected=False,
                duplicate_of=None
            )

            # Create unified document
            unified = UnifiedDocument(
                document_id=paper_id,
                document_type=DocumentType.RESEARCH_PAPER,
                publisher=publisher,
                dates=dates,
                content=content,
                file_metadata=file_metadata,
                provenance=provenance,
                extraction=extraction,
                collection_run_id=self.safe_get(openalex_doc, 'collection_run_id'),
                collector_name='openalex_production',
                collector_version=prov_data.get('validator', '3.0'),
                extensions={
                    'source_format': 'openalex',
                    'source_file': self.safe_get(openalex_doc, 'source_file'),
                    'cited_by_count': self.safe_get(openalex_doc, 'cited_by_count', 0),
                    'collaborating_countries': countries,
                    'validations': validations
                }
            )

            self.conversion_stats['successful'] += 1
            return unified

        except Exception as e:
            self.conversion_stats['failed'] += 1
            self.conversion_stats['errors'].append(str(e))
            logger.error(f"Error converting OpenAlex document: {e}")
            raise


# ============================================================================
# USASPENDING CONVERTER
# ============================================================================

class USASpendingConverter(BaseConverter):
    """
    Convert USASpending procurement detection format to UnifiedDocument

    USASpending Schema (procurement transactions):
    - transaction_id, piid, fain, recipient info, sub-awardee info
    - financial data, agency info, NAICS/PSC codes
    - detection metadata, processed_date
    """

    def convert(self, usaspending_doc: Dict[str, Any]) -> UnifiedDocument:
        """
        Convert USASpending detection to UnifiedDocument

        Args:
            usaspending_doc: Document in USASpending format

        Returns:
            UnifiedDocument instance

        Raises:
            ValueError: If required fields are missing
        """
        self.conversion_stats['total'] += 1

        try:
            # Determine primary entity
            recipient_name = self.safe_get(usaspending_doc, 'recipient_name', 'Unknown')
            recipient_country = self.safe_get(usaspending_doc, 'recipient_country', 'US')
            awarding_agency = self.safe_get(usaspending_doc, 'awarding_agency', 'Unknown')

            # Publisher info (US government agency)
            publisher = PublisherInfo(
                publisher_org=awarding_agency,
                publisher_type=PublisherType.GOVERNMENT,
                publisher_country='US',  # Always US for USASpending
                publisher_domain='usaspending.gov',
                verified_publisher=True  # Official US data
            )

            # Date metadata
            action_date = self.safe_get(usaspending_doc, 'action_date')
            if not action_date:
                action_date = datetime.now().isoformat()[:10]

            dates = DateMetadata(
                publication_date_iso=action_date,
                date_source='transaction_metadata',
                date_confidence=ConfidenceLevel.HIGH,  # USASpending dates are official
                date_validation_sources=['usaspending_api'],
                last_modified=self.safe_get(usaspending_doc, 'processed_date')
            )

            # Build content from procurement data
            award_desc = self.safe_get(usaspending_doc, 'award_description', '')
            subaward_desc = self.safe_get(usaspending_doc, 'subaward_description', '')
            naics_desc = self.safe_get(usaspending_doc, 'naics_description', '')
            psc_desc = self.safe_get(usaspending_doc, 'psc_description', '')

            # Create title from key info
            piid = self.safe_get(usaspending_doc, 'piid', '')
            fiscal_year = self.safe_get(usaspending_doc, 'fiscal_year', '')
            title = f"{fiscal_year} Procurement: {recipient_name} - {award_desc[:100]}"

            # Build structured content text
            obligation = self.safe_get(usaspending_doc, 'federal_action_obligation', 0)
            total_value = self.safe_get(usaspending_doc, 'total_dollars_obligated', 0)

            content_text = f"""Procurement Transaction {piid}

Recipient: {recipient_name}
Parent Company: {self.safe_get(usaspending_doc, 'recipient_parent_name', 'N/A')}
Recipient Country: {recipient_country}

Awarding Agency: {awarding_agency}
Funding Agency: {self.safe_get(usaspending_doc, 'funding_agency', 'N/A')}

Financial Details:
- Federal Action Obligation: ${obligation:,.2f}
- Total Dollars Obligated: ${total_value:,.2f}

Classification:
- NAICS: {self.safe_get(usaspending_doc, 'naics_code', '')} - {naics_desc}
- PSC: {self.safe_get(usaspending_doc, 'psc_code', '')} - {psc_desc}

Award Description: {award_desc}
Subaward Description: {subaward_desc}

Place of Performance: {self.safe_get(usaspending_doc, 'pop_country', 'N/A')}

Detection Metadata:
- Detection Types: {', '.join(self.safe_get(usaspending_doc, 'detection_types', []))}
- Confidence: {self.safe_get(usaspending_doc, 'highest_confidence', 'UNKNOWN')}
- Detection Count: {self.safe_get(usaspending_doc, 'detection_count', 0)}

End of Procurement Record.
"""

            # Extract keywords
            keywords = []
            if naics_desc:
                keywords.append(naics_desc)
            if psc_desc:
                keywords.append(psc_desc)
            keywords.extend(self.safe_get(usaspending_doc, 'detection_types', []))
            keywords = list(set(keywords))[:20]  # Deduplicate and limit

            # Extract entities
            entities = []
            if recipient_name:
                entities.append(recipient_name)
            parent_name = self.safe_get(usaspending_doc, 'recipient_parent_name')
            if parent_name:
                entities.append(parent_name)
            sub_awardee = self.safe_get(usaspending_doc, 'sub_awardee_name')
            if sub_awardee:
                entities.append(sub_awardee)

            content = ContentMetadata(
                content_text=content_text,
                content_length=len(content_text),
                language=LanguageCode.EN,
                title=title,
                title_en=title,
                description=f"Federal procurement transaction with {recipient_name}",
                keywords=keywords,
                topics=[TopicCategory.TRADE, TopicCategory.DEFENSE],
                subtopics=[naics_desc, psc_desc] if naics_desc or psc_desc else [],
                entities=entities
            )

            # File metadata
            transaction_id = usaspending_doc['transaction_id']
            canonical_url = f"https://www.usaspending.gov/award/{piid}" if piid else f"https://www.usaspending.gov/transaction/{transaction_id}"

            # Calculate hash from transaction ID + action date
            hash_val = self.calculate_hash(f"{transaction_id}:{action_date}:{recipient_name}")

            file_metadata = FileMetadata(
                hash_sha256=hash_val,
                text_hash_sha256=self.calculate_hash(content_text),
                file_size_bytes=None,
                file_format='json',
                canonical_url=canonical_url,
                alternate_urls=[f"https://www.usaspending.gov/transaction/{transaction_id}"]
            )

            # Provenance (USASpending API data)
            processed_date = self.safe_get(usaspending_doc, 'processed_date')

            provenance = ProvenanceChain(
                discovery_method='usaspending_api',
                discovery_timestamp=self.parse_datetime(processed_date),
                fetch_url=canonical_url,
                archive_url=None,
                archive_timestamp=None,
                mirror_source_type=MirrorSourceType.DIRECT,
                safe_access_validated=True,  # Official US gov data
                blocked_domain_detected=False,
                redirect_chain=[]
            )

            # Extraction metadata
            # QA based on detection confidence
            confidence = self.safe_get(usaspending_doc, 'highest_confidence', 'UNKNOWN')
            qa_passed = confidence in ['HIGH', 'MEDIUM']

            extraction = ExtractionMetadata(
                extraction_timestamp=self.parse_datetime(processed_date),
                extraction_ok=True,  # If we have the record, extraction succeeded
                extraction_notes=[],
                qa_passed=qa_passed,
                qa_issues=[] if qa_passed else ['low_confidence_detection'],
                redteam_reviewed=False,
                verified_safe_source=True,  # Official US gov source
                reliability_weight=0.95,  # USASpending is highly reliable
                duplicate_detected=False,
                duplicate_of=None
            )

            # Create unified document
            unified = UnifiedDocument(
                document_id=transaction_id,
                document_type=DocumentType.PROCUREMENT,
                publisher=publisher,
                dates=dates,
                content=content,
                file_metadata=file_metadata,
                provenance=provenance,
                extraction=extraction,
                collection_run_id=self.safe_get(usaspending_doc, 'collection_run_id'),
                collector_name='usaspending_production',
                collector_version='1.0.0',
                extensions={
                    'source_format': 'usaspending',
                    'piid': piid,
                    'fain': self.safe_get(usaspending_doc, 'fain'),
                    'recipient_uei': self.safe_get(usaspending_doc, 'recipient_uei'),
                    'federal_action_obligation': obligation,
                    'total_dollars_obligated': total_value,
                    'naics_code': self.safe_get(usaspending_doc, 'naics_code'),
                    'psc_code': self.safe_get(usaspending_doc, 'psc_code'),
                    'fiscal_year': fiscal_year,
                    'detection_details': self.safe_get(usaspending_doc, 'detection_details', [])
                }
            )

            self.conversion_stats['successful'] += 1
            return unified

        except Exception as e:
            self.conversion_stats['failed'] += 1
            self.conversion_stats['errors'].append(str(e))
            logger.error(f"Error converting USASpending document: {e}")
            raise


# ============================================================================
# CONVERTER FACTORY
# ============================================================================

class ConverterFactory:
    """Factory for creating appropriate converter"""

    @staticmethod
    def get_converter(source_format: str) -> BaseConverter:
        """
        Get converter for source format

        Args:
            source_format: One of 'us_gov', 'thinktank', 'china'

        Returns:
            Appropriate converter instance

        Raises:
            ValueError: If format unknown
        """
        converters = {
            'us_gov': USGovConverter,
            'thinktank': ThinkTankConverter,
            'china': ChinaConverter,
            'openalex': OpenAlexConverter,
            'usaspending': USASpendingConverter,
        }

        if source_format not in converters:
            raise ValueError(f"Unknown source format: {source_format}. Must be one of {list(converters.keys())}")

        return converters[source_format]()

    @staticmethod
    def auto_detect_format(doc: Dict[str, Any]) -> str:
        """
        Auto-detect document format

        Args:
            doc: Document to analyze

        Returns:
            Detected format string
        """
        # USASpending has transaction_id and detection_types
        if 'transaction_id' in doc and 'detection_types' in doc:
            return 'usaspending'

        # OpenAlex has paper_id and collaborating_countries
        if 'paper_id' in doc and 'collaborating_countries' in doc:
            return 'openalex'

        # US_Gov has publisher_type and canonical_url
        if 'publisher_type' in doc and 'canonical_url' in doc and 'collection_run_id' in doc:
            return 'us_gov'

        # ThinkTank has organization and extracted_at
        if 'organization' in doc and 'extracted_at' in doc:
            return 'thinktank'

        # China has archive_url and provenance fields
        if 'archive_url' in doc or 'fetch_mode' in doc or 'verified_safe_source' in doc:
            return 'china'

        # Default to us_gov if can't determine
        logger.warning("Could not auto-detect format, defaulting to us_gov")
        return 'us_gov'


# ============================================================================
# BATCH CONVERTER
# ============================================================================

def convert_batch(documents: List[Dict[str, Any]], source_format: Optional[str] = None) -> List[UnifiedDocument]:
    """
    Convert batch of documents to unified format

    Args:
        documents: List of documents to convert
        source_format: Source format (auto-detect if None)

    Returns:
        List of UnifiedDocument instances
    """
    converted = []
    factory = ConverterFactory()

    for doc in documents:
        try:
            # Auto-detect format if not specified
            fmt = source_format or factory.auto_detect_format(doc)

            # Get converter
            converter = factory.get_converter(fmt)

            # Convert
            unified = converter.convert(doc)
            converted.append(unified)

        except Exception as e:
            logger.error(f"Error converting document: {e}")
            continue

    return converted


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'BaseConverter',
    'USGovConverter',
    'ThinkTankConverter',
    'ChinaConverter',
    'OpenAlexConverter',
    'USASpendingConverter',
    'ConverterFactory',
    'convert_batch',
]
