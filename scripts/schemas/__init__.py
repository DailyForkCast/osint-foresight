"""
Schema Package - Unified Document Schema and Converters
Global Tech Intelligence System
"""

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
    compute_title_similarity,
    validate_safe_mode_url,
    SCHEMA_VERSION,
    SCHEMA_DATE,
)

from .converters import (
    BaseConverter,
    USGovConverter,
    ThinkTankConverter,
    ChinaConverter,
    ConverterFactory,
    convert_batch,
)

__version__ = "1.0.0"
__all__ = [
    # Schema models
    'UnifiedDocument',
    'PublisherInfo',
    'DateMetadata',
    'ContentMetadata',
    'FileMetadata',
    'ProvenanceChain',
    'ExtractionMetadata',
    # Enums
    'PublisherType',
    'DocumentType',
    'MirrorSourceType',
    'ConfidenceLevel',
    'LanguageCode',
    'TopicCategory',
    # Utilities
    'compute_title_similarity',
    'validate_safe_mode_url',
    # Converters
    'BaseConverter',
    'USGovConverter',
    'ThinkTankConverter',
    'ChinaConverter',
    'ConverterFactory',
    'convert_batch',
    # Constants
    'SCHEMA_VERSION',
    'SCHEMA_DATE',
]
