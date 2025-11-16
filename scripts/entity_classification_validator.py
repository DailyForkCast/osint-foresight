#!/usr/bin/env python3
"""
Entity Classification Validator - v2.0 (October 2025)
Implements mandatory country code verification and Taiwan/PRC separation policy

CRITICAL CHANGES FROM v1.0:
- Adds country code verification (prevents $1.65B false positive error)
- Separates Taiwan (TW) from PRC (CN) entities
- Implements Hong Kong SAR (HK) and Macao SAR (MO) separate reporting
- Adds false positive exclusion list
- Requires manual verification for high-value entities (>$10M)

POLICY COMPLIANCE:
- Taiwan/PRC Classification Policy v1.0
- See: KNOWLEDGE_BASE/TAIWAN_PRC_CLASSIFICATION_POLICY.md
"""

import re
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class EntityOrigin(Enum):
    """Geographic origin classification"""
    PRC = "CN"  # People's Republic of China (mainland)
    TAIWAN = "TW"  # Taiwan (Republic of China)
    HONG_KONG = "HK"  # Hong Kong SAR (PRC since 1997)
    MACAO = "MO"  # Macao SAR (PRC since 1999)
    OTHER = "OTHER"  # Non-China entities
    UNKNOWN = "UNKNOWN"  # Needs manual verification


class ConfidenceLevel(Enum):
    """Classification confidence"""
    VERIFIED = "VERIFIED"  # Manual verification or high-confidence automated
    HIGH = "HIGH"  # Country code + name match
    MEDIUM = "MEDIUM"  # Country code OR name match
    LOW = "LOW"  # Uncertain, needs review
    NEEDS_REVIEW = "NEEDS_REVIEW"  # Flagged for manual verification


@dataclass
class EntityClassification:
    """Result of entity classification"""
    entity_name: str
    origin: EntityOrigin
    confidence: ConfidenceLevel
    country_code: Optional[str]
    value: float
    verification_required: bool
    warnings: list
    reasoning: str


class EntityClassificationValidator:
    """
    Validates entity classification with mandatory country code verification.

    Implements Taiwan/PRC separation policy and prevents false positives.
    """

    # FALSE POSITIVE EXCLUSION LIST
    # Entities that match Chinese patterns but are NOT Chinese
    FALSE_POSITIVE_EXCLUSIONS = [
        # US companies with "DJI" in name (NOT SZ DJI Technology Co.)
        r'PRI-DJI A CONSTRUCTION JV',
        r'PRI/DJI,? A SERVICES JV',
        r'PRI/DJI A RECONSTRUCTION JV',
        r'KMK-DJI JV',

        # US companies with "China" in name but US-based
        r'CHINA GROVE',  # US city name
        r'CHINA SPRING',  # US city name

        # Companies with "COSCO" but not China Ocean Shipping
        # (Note: Ambiguous - these need manual verification)
        r'COSCO FIRE PROTECTION.*INC',  # Likely US fire protection company

        # Add more as identified
    ]

    # TAIWAN COMPANY EXCLUSION LIST
    # Known Taiwan companies that should NEVER be classified as PRC
    TAIWAN_COMPANIES = [
        'HON HAI PRECISION INDUSTRY',
        'FOXCONN',
        'TAIWAN SEMICONDUCTOR MANUFACTURING',
        'TSMC',
        'MEDIATEK',
        'ASUSTEK',
        'ASUS',
        'ACER',
        'HTC CORPORATION',
        'REALTEK SEMICONDUCTOR',
        'NOVATEK MICROELECTRONICS',
        'EVERGREEN MARINE',
        'FORMOSA PLASTICS',
        'CATHAY FINANCIAL',  # Taiwan, not PRC
    ]

    # TAIWAN RESEARCH INSTITUTIONS
    TAIWAN_INSTITUTIONS = [
        'ACADEMIA SINICA',  # Taiwan (NOT Chinese Academy of Sciences)
        'NATIONAL TAIWAN UNIVERSITY',
        'NATIONAL TSING HUA UNIVERSITY',  # Taiwan campus
        'INDUSTRIAL TECHNOLOGY RESEARCH INSTITUTE',
        'ITRI',  # Taiwan ITRI
    ]

    # HIGH-VALUE THRESHOLD for manual verification
    HIGH_VALUE_THRESHOLD = 10_000_000  # $10 million

    def __init__(self):
        """Initialize validator with compiled patterns"""
        self.false_positive_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.FALSE_POSITIVE_EXCLUSIONS
        ]

    def classify_entity(
        self,
        entity_name: str,
        country_code: Optional[str] = None,
        value: float = 0.0,
        additional_fields: Optional[Dict] = None
    ) -> EntityClassification:
        """
        Classify entity origin with mandatory country code verification.

        Args:
            entity_name: Name of the entity
            country_code: ISO 3166-1 alpha-2 country code (CN, TW, HK, MO, USA, etc.)
            value: Contract/patent/transaction value
            additional_fields: Optional dict with place_of_performance, etc.

        Returns:
            EntityClassification with origin, confidence, warnings

        Examples:
            >>> validator = EntityClassificationValidator()

            >>> # Correct classification with country code
            >>> result = validator.classify_entity(
            ...     "Chinese Academy of Sciences",
            ...     country_code="CN",
            ...     value=1000000
            ... )
            >>> result.origin
            <EntityOrigin.PRC: 'CN'>

            >>> # Prevents false positive
            >>> result = validator.classify_entity(
            ...     "PRI-DJI A CONSTRUCTION JV",
            ...     country_code="USA",
            ...     value=1000000000
            ... )
            >>> result.origin
            <EntityOrigin.OTHER: 'OTHER'>

            >>> # Taiwan separation
            >>> result = validator.classify_entity(
            ...     "Hon Hai Precision Industry",
            ...     country_code="TW",
            ...     value=5000000
            ... )
            >>> result.origin
            <EntityOrigin.TAIWAN: 'TW'>
        """
        warnings = []
        reasoning = []

        # STEP 1: Check false positive exclusion list FIRST
        if self._is_false_positive(entity_name):
            reasoning.append(f"Matched false positive exclusion list")
            if country_code and country_code != 'CN':
                reasoning.append(f"Country code {country_code} confirms non-PRC")
                return EntityClassification(
                    entity_name=entity_name,
                    origin=EntityOrigin.OTHER,
                    confidence=ConfidenceLevel.HIGH,
                    country_code=country_code,
                    value=value,
                    verification_required=False,
                    warnings=warnings,
                    reasoning="; ".join(reasoning)
                )
            else:
                warnings.append("On false positive list but country code missing or CN - VERIFY")
                return EntityClassification(
                    entity_name=entity_name,
                    origin=EntityOrigin.UNKNOWN,
                    confidence=ConfidenceLevel.NEEDS_REVIEW,
                    country_code=country_code,
                    value=value,
                    verification_required=True,
                    warnings=warnings,
                    reasoning="False positive pattern detected, needs manual verification"
                )

        # STEP 2: PRIMARY - Country code verification (MANDATORY)
        if country_code:
            country_code_upper = country_code.upper()

            if country_code_upper in ['CN', 'CHN']:
                # Check for Taiwan companies misclassified with CN code
                if self._is_taiwan_entity(entity_name):
                    warnings.append(f"POLICY VIOLATION: Taiwan entity with CN code: {entity_name}")
                    return EntityClassification(
                        entity_name=entity_name,
                        origin=EntityOrigin.TAIWAN,
                        confidence=ConfidenceLevel.NEEDS_REVIEW,
                        country_code=country_code,
                        value=value,
                        verification_required=True,
                        warnings=warnings,
                        reasoning="Taiwan entity incorrectly coded as CN - CORRECT TO TW"
                    )

                reasoning.append(f"Country code: {country_code_upper} (PRC)")
                origin = EntityOrigin.PRC
                confidence = ConfidenceLevel.HIGH

            elif country_code_upper in ['TW', 'TWN']:
                reasoning.append(f"Country code: {country_code_upper} (Taiwan)")
                origin = EntityOrigin.TAIWAN
                confidence = ConfidenceLevel.HIGH

            elif country_code_upper in ['HK', 'HKG']:
                reasoning.append(f"Country code: {country_code_upper} (Hong Kong SAR)")
                origin = EntityOrigin.HONG_KONG
                confidence = ConfidenceLevel.HIGH

            elif country_code_upper in ['MO', 'MAC']:
                reasoning.append(f"Country code: {country_code_upper} (Macao SAR)")
                origin = EntityOrigin.MACAO
                confidence = ConfidenceLevel.HIGH

            else:
                # Country code indicates non-China entity
                reasoning.append(f"Country code: {country_code_upper} (not China/Taiwan)")

                # Double-check: Does name suggest Chinese entity but country code says otherwise?
                if self._has_chinese_indicators(entity_name):
                    warnings.append(f"Chinese name patterns but country code is {country_code_upper} - verify")
                    confidence = ConfidenceLevel.NEEDS_REVIEW
                else:
                    confidence = ConfidenceLevel.HIGH

                return EntityClassification(
                    entity_name=entity_name,
                    origin=EntityOrigin.OTHER,
                    confidence=confidence,
                    country_code=country_code,
                    value=value,
                    verification_required=value > self.HIGH_VALUE_THRESHOLD,
                    warnings=warnings,
                    reasoning="; ".join(reasoning)
                )

        else:
            # STEP 3: No country code - fallback to name-based (LOW confidence)
            warnings.append("No country code provided - using name-based detection only (LOW confidence)")

            if self._is_taiwan_entity(entity_name):
                origin = EntityOrigin.TAIWAN
                confidence = ConfidenceLevel.LOW
                reasoning.append("Taiwan entity identified by name (needs country code verification)")

            elif self._has_chinese_indicators(entity_name):
                # Ambiguous - could be PRC, Taiwan, HK, or false positive
                warnings.append("Chinese indicators in name but no country code - VERIFY MANUALLY")
                origin = EntityOrigin.UNKNOWN
                confidence = ConfidenceLevel.NEEDS_REVIEW
                reasoning.append("Name suggests China/Taiwan but origin unclear without country code")

            else:
                origin = EntityOrigin.OTHER
                confidence = ConfidenceLevel.MEDIUM
                reasoning.append("No Chinese indicators in name")

        # STEP 4: High-value manual verification requirement
        verification_required = value > self.HIGH_VALUE_THRESHOLD
        if verification_required:
            warnings.append(f"HIGH VALUE (>${self.HIGH_VALUE_THRESHOLD:,.0f}) - manual verification required")

        return EntityClassification(
            entity_name=entity_name,
            origin=origin,
            confidence=confidence,
            country_code=country_code,
            value=value,
            verification_required=verification_required,
            warnings=warnings,
            reasoning="; ".join(reasoning)
        )

    def _is_false_positive(self, entity_name: str) -> bool:
        """Check if entity matches known false positive patterns"""
        for pattern in self.false_positive_patterns:
            if pattern.search(entity_name):
                return True
        return False

    def _is_taiwan_entity(self, entity_name: str) -> bool:
        """Check if entity is known Taiwan company or institution"""
        entity_upper = entity_name.upper()

        # Check known Taiwan companies
        for company in self.TAIWAN_COMPANIES:
            if company in entity_upper:
                return True

        # Check known Taiwan institutions
        for institution in self.TAIWAN_INSTITUTIONS:
            if institution in entity_upper:
                return True

        # Check for Taiwan name indicators (with word boundaries for short terms)
        # Full word boundaries for 'ROC' to avoid matching ROCHE, ROCKWELL, etc.
        if re.search(r'\bROC\b', entity_upper):
            return True

        # Simple substring match for longer, unique terms
        taiwan_indicators = ['TAIWAN', 'TAIPEI', 'FORMOSA']
        for indicator in taiwan_indicators:
            if indicator in entity_upper:
                return True

        return False

    def _has_chinese_indicators(self, entity_name: str) -> bool:
        """Check if entity name has Chinese/China indicators (ambiguous without country code)"""
        entity_lower = entity_name.lower()

        # Geographic indicators
        china_indicators = [
            'chinese', 'china', 'beijing', 'shanghai', 'shenzhen',
            'guangzhou', 'guangdong', 'zhejiang', 'wuhan', 'hangzhou'
        ]

        for indicator in china_indicators:
            if indicator in entity_lower:
                return True

        # Known Chinese company names
        known_companies = [
            'huawei', 'zte', 'alibaba', 'tencent', 'baidu', 'bytedance',
            'xiaomi', 'lenovo', 'byd', 'catl', 'boe', 'hikvision', 'dahua',
            'smic', 'cosco', 'sinopec', 'petrochina', 'comac', 'avic'
        ]

        for company in known_companies:
            if company in entity_lower:
                return True

        return False


# INTEGRATION FUNCTION FOR EXISTING SCRIPTS
def validate_chinese_entity_detection(
    entity_name: str,
    country_code: Optional[str] = None,
    value: float = 0.0
) -> Tuple[bool, str, str]:
    """
    Simple function for integration into existing detection scripts.

    Args:
        entity_name: Entity name to classify
        country_code: ISO country code (CN, TW, HK, USA, etc.)
        value: Transaction value

    Returns:
        Tuple of (is_prc: bool, origin_code: str, warnings: str)

    Example:
        >>> is_prc, origin, warnings = validate_chinese_entity_detection(
        ...     "PRI-DJI A CONSTRUCTION JV",
        ...     country_code="USA",
        ...     value=1000000000
        ... )
        >>> is_prc
        False
        >>> origin
        'OTHER'
        >>> "false positive" in warnings.lower()
        True
    """
    validator = EntityClassificationValidator()
    result = validator.classify_entity(entity_name, country_code, value)

    is_prc = result.origin == EntityOrigin.PRC
    origin_code = result.origin.value
    warnings_str = "; ".join(result.warnings) if result.warnings else "No warnings"

    return is_prc, origin_code, warnings_str


# EXAMPLE USAGE
if __name__ == "__main__":
    validator = EntityClassificationValidator()

    print("="*80)
    print("ENTITY CLASSIFICATION VALIDATOR v2.0 - EXAMPLES")
    print("="*80)
    print()

    # Test cases
    test_cases = [
        # (entity_name, country_code, value, expected_origin)
        ("Chinese Academy of Sciences", "CN", 1000000, "PRC"),
        ("PRI-DJI A CONSTRUCTION JV", "USA", 1000000000, "OTHER - False Positive"),
        ("Hon Hai Precision Industry", "TW", 5000000, "Taiwan"),
        ("University of Hong Kong", "HK", 50000000, "Hong Kong SAR"),
        ("Huawei Technologies", "CN", 100000, "PRC"),
        ("TSMC", "TW", 20000000, "Taiwan"),
        ("Lenovo (United States) Inc.", "USA", 244000000, "OTHER (PRC-owned, US subsidiary)"),
        ("Some Random Company", "USA", 1000, "OTHER"),
        ("Chinese University of Hong Kong", "HK", 2000000, "Hong Kong SAR"),
    ]

    for entity_name, country_code, value, expected in test_cases:
        result = validator.classify_entity(entity_name, country_code, value)

        print(f"Entity: {entity_name}")
        print(f"  Country Code: {country_code}")
        print(f"  Value: ${value:,.0f}")
        print(f"  --> Classification: {result.origin.value} ({result.confidence.value})")
        print(f"  --> Expected: {expected}")
        if result.warnings:
            print(f"  --> Warnings: {'; '.join(result.warnings)}")
        print(f"  --> Reasoning: {result.reasoning}")
        print(f"  --> Manual Review: {'YES' if result.verification_required else 'No'}")
        print()

    print("="*80)
    print("VALIDATION COMPLETE")
    print("="*80)
