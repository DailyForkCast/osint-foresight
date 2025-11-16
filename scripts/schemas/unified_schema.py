#!/usr/bin/env python3
"""
Unified Document Schema - Pydantic Models
Global Tech Intelligence System

Unifies schemas from:
- US_Gov collector (30 fields)
- ThinkTank collector (20 fields)
- China collector (30 fields)

Target: 40+ fields with full provenance tracking and Safe Mode support
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import hashlib
import re


# ============================================================================
# ENUMS - Controlled Vocabularies
# ============================================================================

class PublisherType(str, Enum):
    """Type of document publisher"""
    GOVERNMENT = "government"
    ACADEMIC = "academic"
    THINK_TANK = "think_tank"
    INDUSTRY = "industry"
    STANDARDS_BODY = "standards_body"
    INTERNATIONAL_ORG = "international_org"
    NGO = "ngo"
    MEDIA = "media"
    SECONDARY = "secondary"  # Aggregators like ChinaFile, MERICS
    UNKNOWN = "unknown"


class DocumentType(str, Enum):
    """Type of document"""
    POLICY = "policy"
    REGULATION = "regulation"
    GUIDANCE = "guidance"
    REPORT = "report"
    PRESS_RELEASE = "press_release"
    SPEECH = "speech"
    ANALYSIS = "analysis"
    RESEARCH_PAPER = "research_paper"
    STANDARD = "standard"
    PATENT = "patent"
    PROCUREMENT = "procurement"
    LEGISLATION = "legislation"
    COURT_CASE = "court_case"
    TREATY = "treaty"
    ARTICLE = "article"
    BLOG_POST = "blog_post"
    UNKNOWN = "unknown"


class MirrorSourceType(str, Enum):
    """Type of mirror/archive source (Safe Mode)"""
    DIRECT = "direct"  # Direct access (safe domains only)
    COMMONCRAWL = "commoncrawl"  # Common Crawl archive
    WAYBACK = "wayback"  # Internet Archive Wayback Machine
    ARCHIVE_TODAY = "archive_today"  # Archive.today/Archive.is
    UNKNOWN = "unknown"


class ConfidenceLevel(str, Enum):
    """Confidence in extracted data"""
    HIGH = "high"  # 3/3 agreement or verified
    MEDIUM = "medium"  # 2/3 agreement
    LOW = "low"  # 1/3 or inferred
    NONE = "none"  # Missing or unverified


class LanguageCode(str, Enum):
    """ISO 639-1 language codes"""
    EN = "en"
    ZH = "zh"  # Chinese
    ES = "es"
    FR = "fr"
    DE = "de"
    RU = "ru"
    AR = "ar"
    JA = "ja"
    KO = "ko"
    PT = "pt"
    UNKNOWN = "unknown"


class TopicCategory(str, Enum):
    """High-level topic categories"""
    SCIENCE_TECHNOLOGY = "science_technology"
    INDUSTRIAL_POLICY = "industrial_policy"
    STANDARDS = "standards"
    INTERNATIONAL_COOPERATION = "international_cooperation"
    DUAL_USE = "dual_use"
    BELT_ROAD = "belt_road"
    ENERGY = "energy"
    AI_TECHNOLOGY = "ai_technology"
    SEMICONDUCTORS = "semiconductors"
    BIOTECHNOLOGY = "biotechnology"
    QUANTUM = "quantum"
    SPACE = "space"
    DEFENSE = "defense"
    TRADE = "trade"
    CYBERSECURITY = "cybersecurity"
    UNKNOWN = "unknown"


# ============================================================================
# SUB-MODELS
# ============================================================================

class ProvenanceChain(BaseModel):
    """Tracks document provenance for Safe Mode compliance"""

    discovery_method: str = Field(
        description="How document was discovered (api, rss, sitemap, html, direct)"
    )
    discovery_timestamp: datetime = Field(
        description="When document was discovered (ISO 8601)"
    )
    fetch_url: str = Field(
        description="URL used to fetch content"
    )
    archive_url: Optional[str] = Field(
        default=None,
        description="Archive URL if using mirror (Wayback, Common Crawl, Archive.today)"
    )
    archive_timestamp: Optional[str] = Field(
        default=None,
        description="Timestamp of archive snapshot"
    )
    mirror_source_type: MirrorSourceType = Field(
        default=MirrorSourceType.DIRECT,
        description="Type of mirror source used"
    )
    safe_access_validated: bool = Field(
        default=False,
        description="Whether Safe Mode validation passed"
    )
    blocked_domain_detected: bool = Field(
        default=False,
        description="Whether blocked domain (.gov.cn, .edu.cn, .cn) was detected"
    )
    redirect_chain: List[str] = Field(
        default_factory=list,
        description="HTTP redirect chain if applicable"
    )

    @field_validator('fetch_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """
        Ensure URL is valid and safe

        Security Note: We don't execute shell commands with these URLs,
        so shell metacharacters are safe. Protection focuses on:
        - Valid HTTP/HTTPS protocol
        - No null byte injection
        - Basic URL structure validation
        """
        from urllib.parse import urlparse

        if not v or not v.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL: {v}")

        # Parse URL to validate structure
        try:
            parsed = urlparse(v)
            if not parsed.netloc:
                raise ValueError("URL missing domain")
        except Exception as e:
            raise ValueError(f"Invalid URL format: {e}")

        # Block null bytes (null byte injection protection)
        if '\x00' in v:
            raise ValueError("URL contains null byte")

        # Note: Shell metacharacters like &, ;, |, etc. are allowed because:
        # 1. We don't execute shell commands with these URLs
        # 2. Database uses parameterized queries (SQL injection safe)
        # 3. Frontend handles HTML escaping (XSS safe)
        # 4. URLs like usaspending.gov legitimately use & in path components

        return v


class PublisherInfo(BaseModel):
    """Information about document publisher"""

    publisher_org: str = Field(
        description="Organization name"
    )
    publisher_type: PublisherType = Field(
        description="Type of publisher organization"
    )
    publisher_country: Optional[str] = Field(
        default=None,
        description="ISO 3166-1 alpha-2 country code (US, CN, GB, etc.)"
    )
    publisher_domain: Optional[str] = Field(
        default=None,
        description="Primary domain of publisher"
    )
    verified_publisher: bool = Field(
        default=False,
        description="Whether publisher identity has been verified"
    )

    @field_validator('publisher_country')
    @classmethod
    def validate_country_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate ISO 3166-1 alpha-2 country code"""
        if v:
            if len(v) != 2:
                raise ValueError(f"Country code must be 2 characters: {v}")
            if not v.isalpha():
                raise ValueError(f"Country code must contain only letters: {v}")
            return v.upper()
        return None


class ExtractionMetadata(BaseModel):
    """Metadata about extraction and QA process"""

    extraction_timestamp: datetime = Field(
        description="When content was extracted (ISO 8601)"
    )
    extraction_ok: bool = Field(
        default=False,
        description="Whether extraction succeeded"
    )
    extraction_notes: List[str] = Field(
        default_factory=list,
        description="Notes about extraction process"
    )
    qa_passed: bool = Field(
        default=False,
        description="Whether document passed QA validation"
    )
    qa_issues: List[str] = Field(
        default_factory=list,
        description="List of QA validation issues"
    )
    redteam_reviewed: bool = Field(
        default=False,
        description="Whether document has been reviewed by red team for safety"
    )
    verified_safe_source: bool = Field(
        default=False,
        description="Whether source is verified safe (e.g., US/EU aggregator)"
    )
    reliability_weight: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Reliability weight for fusion (0.0-1.0)"
    )
    duplicate_detected: bool = Field(
        default=False,
        description="Whether this is a duplicate document"
    )
    duplicate_of: Optional[str] = Field(
        default=None,
        description="SHA256 hash of original if duplicate"
    )

    @model_validator(mode='after')
    def validate_extraction_logic(self) -> 'ExtractionMetadata':
        """Validate extraction metadata logic"""

        # QA passed must not have issues
        if self.qa_passed and self.qa_issues:
            raise ValueError("QA passed=True but has issues")

        # If duplicate detected, must have original hash
        if self.duplicate_detected and not self.duplicate_of:
            raise ValueError("duplicate_detected=True but no duplicate_of hash")

        return self


class DateMetadata(BaseModel):
    """Publication date with confidence tracking"""

    publication_date_iso: str = Field(
        description="Publication date in ISO 8601 format (YYYY-MM-DD)"
    )
    date_source: Optional[str] = Field(
        default=None,
        description="Source of date (sitemap, http_header, document_metadata, inferred)"
    )
    date_confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.NONE,
        description="Confidence level in publication date"
    )
    date_validation_sources: List[str] = Field(
        default_factory=list,
        description="Sources used for 3-way date validation"
    )
    last_modified: Optional[str] = Field(
        default=None,
        description="Last modified date in ISO 8601 format"
    )

    @field_validator('publication_date_iso')
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validate ISO 8601 date format"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError(f"Invalid ISO 8601 date: {v}")


class ContentMetadata(BaseModel):
    """Metadata about document content"""

    content_text: str = Field(
        description="Extracted text content"
    )
    content_length: int = Field(
        ge=0,
        description="Length of extracted content in characters"
    )
    language: LanguageCode = Field(
        description="ISO 639-1 language code"
    )
    title: str = Field(
        description="Document title"
    )
    title_en: Optional[str] = Field(
        default=None,
        description="English translation of title if original not English"
    )
    description: Optional[str] = Field(
        default=None,
        description="Short description or abstract"
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Keywords or tags"
    )
    topics: List[TopicCategory] = Field(
        default_factory=list,
        description="High-level topic categories"
    )
    subtopics: List[str] = Field(
        default_factory=list,
        description="Granular subtopics"
    )
    entities: List[str] = Field(
        default_factory=list,
        description="Named entities extracted (organizations, people, places)"
    )

    @field_validator('content_length')
    @classmethod
    def validate_content_length(cls, v: int, info) -> int:
        """Ensure content_length matches actual content"""
        if 'content_text' in info.data:
            actual_length = len(info.data['content_text'])
            if abs(v - actual_length) > 100:  # Allow 100 char tolerance
                raise ValueError(f"Content length mismatch: {v} vs {actual_length}")
        return v


class FileMetadata(BaseModel):
    """File and storage metadata"""

    hash_sha256: str = Field(
        description="SHA256 hash of full content for deduplication"
    )
    text_hash_sha256: Optional[str] = Field(
        default=None,
        description="SHA256 hash of text content only (excluding metadata)"
    )
    file_size_bytes: Optional[int] = Field(
        default=None,
        ge=0,
        description="File size in bytes"
    )
    file_format: Optional[str] = Field(
        default=None,
        description="File format (html, pdf, txt, xml, json)"
    )
    canonical_url: str = Field(
        description="Canonical URL for this document"
    )
    alternate_urls: List[str] = Field(
        default_factory=list,
        description="Alternate URLs for this document"
    )

    @field_validator('hash_sha256', 'text_hash_sha256')
    @classmethod
    def validate_sha256(cls, v: Optional[str]) -> Optional[str]:
        """Validate SHA256 hash format"""
        if v and not re.match(r'^[a-f0-9]{64}$', v.lower()):
            raise ValueError(f"Invalid SHA256 hash: {v}")
        return v.lower() if v else None


# ============================================================================
# MAIN MODEL
# ============================================================================

class UnifiedDocument(BaseModel):
    """
    Unified document schema for Global Tech Intelligence System

    Supports all collectors: US_Gov, ThinkTank, China, Europe, etc.
    Includes full provenance tracking for Safe Mode compliance
    """

    # Core identification
    document_id: Optional[str] = Field(
        default=None,
        description="Unique identifier (auto-generated if not provided)"
    )
    document_type: DocumentType = Field(
        description="Type of document"
    )

    # Publisher information
    publisher: PublisherInfo = Field(
        description="Publisher information"
    )

    # Date metadata
    dates: DateMetadata = Field(
        description="Publication date with confidence tracking"
    )

    # Content
    content: ContentMetadata = Field(
        description="Document content and metadata"
    )

    # File metadata
    file_metadata: FileMetadata = Field(
        description="File and storage metadata"
    )

    # Provenance (Safe Mode)
    provenance: ProvenanceChain = Field(
        description="Document provenance for Safe Mode compliance"
    )

    # Extraction metadata
    extraction: ExtractionMetadata = Field(
        description="Extraction and QA metadata"
    )

    # Collection metadata
    collection_run_id: Optional[str] = Field(
        default=None,
        description="ID of collection run that fetched this document"
    )
    collector_name: str = Field(
        description="Name of collector that fetched this document"
    )
    collector_version: str = Field(
        default="1.0.0",
        description="Version of collector"
    )

    # Optional extensions
    extensions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Collector-specific extensions (flexible schema)"
    )

    @model_validator(mode='after')
    def validate_document(self) -> 'UnifiedDocument':
        """Cross-field validations"""

        # Ensure content length matches
        if len(self.content.content_text) < 10:
            raise ValueError("Content text too short (< 10 characters)")

        # Safe Mode validation
        if self.provenance.blocked_domain_detected and not self.provenance.archive_url:
            raise ValueError("Blocked domain detected but no archive URL provided")

        # QA validation
        if self.extraction.qa_passed and self.extraction.qa_issues:
            raise ValueError("Document passed QA but has QA issues")

        # Duplicate validation
        if self.extraction.duplicate_detected and not self.extraction.duplicate_of:
            raise ValueError("Duplicate detected but no original hash provided")

        return self

    def generate_document_id(self) -> str:
        """Generate unique document ID from hash and timestamp"""
        base = f"{self.file_metadata.hash_sha256[:16]}_{self.dates.publication_date_iso}"
        return hashlib.md5(base.encode()).hexdigest()

    def calculate_sha256(self) -> str:
        """Calculate SHA256 hash of content"""
        content_bytes = self.content.content_text.encode('utf-8')
        return hashlib.sha256(content_bytes).hexdigest()

    def to_legacy_format(self, format_type: str) -> Dict[str, Any]:
        """Convert to legacy format for backward compatibility"""
        if format_type == "us_gov":
            return self._to_us_gov_format()
        elif format_type == "thinktank":
            return self._to_thinktank_format()
        elif format_type == "china":
            return self._to_china_format()
        else:
            raise ValueError(f"Unknown format type: {format_type}")

    def _to_us_gov_format(self) -> Dict[str, Any]:
        """Convert to US_Gov collector format"""
        return {
            'title': self.content.title,
            'publisher_org': self.publisher.publisher_org,
            'publisher_type': self.publisher.publisher_type.value,
            'document_type': self.document_type.value,
            'publication_date_iso': self.dates.publication_date_iso,
            'content_text': self.content.content_text,
            'content_length': self.content.content_length,
            'language': self.content.language.value,
            'keywords': self.content.keywords,
            'topics': [t.value for t in self.content.topics],
            'hash_sha256': self.file_metadata.hash_sha256,
            'canonical_url': self.file_metadata.canonical_url,
            'extraction_ok': self.extraction.extraction_ok,
            'qa_passed': self.extraction.qa_passed,
            'qa_issues': self.extraction.qa_issues,
            'collection_run_id': self.collection_run_id,
        }

    def _to_thinktank_format(self) -> Dict[str, Any]:
        """Convert to ThinkTank collector format"""
        return {
            'title': self.content.title,
            'organization': self.publisher.publisher_org,
            'document_type': self.document_type.value,
            'publication_date': self.dates.publication_date_iso,
            'url': self.file_metadata.canonical_url,
            'content': self.content.content_text,
            'topics': [t.value for t in self.content.topics],
            'hash': self.file_metadata.hash_sha256,
            'extracted_at': self.extraction.extraction_timestamp.isoformat(),
        }

    def _to_china_format(self) -> Dict[str, Any]:
        """Convert to China collector format"""
        return {
            'source_name': self.publisher.publisher_org,
            'source_url': self.provenance.fetch_url,
            'discovery_method': self.provenance.discovery_method,
            'discovery_timestamp': self.provenance.discovery_timestamp.isoformat(),
            'access_method': self.provenance.mirror_source_type.value,
            'fetch_url': self.provenance.fetch_url,
            'archive_url': self.provenance.archive_url,
            'archive_timestamp': self.provenance.archive_timestamp,
            'title': self.content.title,
            'title_en': self.content.title_en,
            'publication_date': self.dates.publication_date_iso,
            'date_source': self.dates.date_source,
            'date_confidence': self.dates.date_confidence.value,
            'language': self.content.language.value,
            'description': self.content.description,
            'keywords': self.content.keywords,
            'content_text': self.content.content_text,
            'content_length': self.content.content_length,
            'topics': [t.value for t in self.content.topics],
            'subtopics': self.content.subtopics,
            'entities': self.content.entities,
            'hash_sha256': self.file_metadata.hash_sha256,
            'text_hash_sha256': self.file_metadata.text_hash_sha256,
            'file_size_bytes': self.file_metadata.file_size_bytes,
            'publisher_org': self.publisher.publisher_org,
            'publisher_type': self.publisher.publisher_type.value,
            'canonical_url': self.file_metadata.canonical_url,
            'verified_safe_source': self.extraction.verified_safe_source,
            'fetch_mode': self.provenance.mirror_source_type.value,
            'extraction_status': 'success' if self.extraction.extraction_ok else 'failed',
            'extraction_timestamp': self.extraction.extraction_timestamp.isoformat(),
            'extraction_ok': self.extraction.extraction_ok,
            'extraction_notes': self.extraction.extraction_notes,
            'qa_passed': self.extraction.qa_passed,
            'qa_issues': self.extraction.qa_issues,
        }

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        validate_assignment = True
        use_enum_values = False


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def compute_title_similarity(title1: str, title2: str) -> float:
    """
    Compute similarity between two titles using character-level matching

    Args:
        title1: First title
        title2: Second title

    Returns:
        Similarity score (0.0-1.0)
    """
    # Normalize titles
    t1 = title1.lower().strip()
    t2 = title2.lower().strip()

    if not t1 or not t2:
        return 0.0

    # Character-level matching
    matches = sum(c1 == c2 for c1, c2 in zip(t1, t2))
    max_len = max(len(t1), len(t2))

    return matches / max_len if max_len > 0 else 0.0


def validate_safe_mode_url(url: str) -> Dict[str, Any]:
    """
    Validate URL for Safe Mode compliance with proper domain parsing

    Args:
        url: URL to validate

    Returns:
        Dict with validation result
    """
    from urllib.parse import urlparse

    BLOCKED_TLDS = ['.gov.cn', '.edu.cn', '.cn']
    ALLOWED_TLDS = ['.tw']  # Taiwan OK

    try:
        parsed = urlparse(url.lower())
        domain = parsed.netloc

        # Check if domain ENDS with allowed TLD (not just contains)
        for allowed in ALLOWED_TLDS:
            if domain.endswith(allowed):
                return {'safe': True, 'reason': f'Allowed TLD: {allowed}'}

        # Check if domain ENDS with blocked TLD (not just contains)
        for blocked in BLOCKED_TLDS:
            if domain.endswith(blocked):
                return {'safe': False, 'reason': f'Blocked TLD: {blocked}'}

        return {'safe': True, 'reason': 'Domain OK'}

    except Exception as e:
        return {'safe': False, 'reason': f'URL parsing error: {e}'}


# ============================================================================
# SCHEMA VERSION
# ============================================================================

SCHEMA_VERSION = "1.1.0"
SCHEMA_DATE = "2025-10-13"

__all__ = [
    'UnifiedDocument',
    'PublisherInfo',
    'DateMetadata',
    'ContentMetadata',
    'FileMetadata',
    'ProvenanceChain',
    'ExtractionMetadata',
    'PublisherType',
    'DocumentType',
    'MirrorSourceType',
    'ConfidenceLevel',
    'LanguageCode',
    'TopicCategory',
    'compute_title_similarity',
    'validate_safe_mode_url',
    'SCHEMA_VERSION',
    'SCHEMA_DATE',
]
