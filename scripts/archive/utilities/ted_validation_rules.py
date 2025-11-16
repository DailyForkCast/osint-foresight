#!/usr/bin/env python3
"""
TED Entity Validation Rules
Created: October 20, 2025
Purpose: Validation framework to prevent false positives in Chinese entity detection
"""

import re
from typing import Dict, List, Tuple, Optional

class TEDEntityValidator:
    """
    Validates potential Chinese entities against multiple criteria to prevent false positives.
    """

    # European legal entity suffixes (definitive exclusions)
    EUROPEAN_LEGAL_SUFFIXES = {
        # German
        'GmbH', 'AG', 'KG', 'GmbH & Co. KG', 'GmbH & Co.KG',

        # Polish
        'Sp. z o.o.', 'S.A.',

        # Czech/Slovak
        'a.s.', 's.r.o.', 'spol. s r.o.',

        # Nordic
        'AB', 'AS', 'Oy', 'OY', 'ASA', 'Oyj',

        # Italian
        'S.p.A.', 'SpA', 'S.r.l.', 'Srl',

        # Dutch
        'B.V.', 'NV', 'N.V.',

        # British/Irish
        'Ltd', 'PLC', 'Limited', 'LLP',

        # French
        'SAS', 'SARL', 'SA',

        # Spanish
        'SL', 'S.L.',

        # Belgian
        'BVBA', 'NV',

        # Other European
        'OÜ',     # Estonian
        'UAB',    # Lithuanian
        'SIA',    # Latvian
        'Sàrl',   # Luxembourg
        'SE',     # Societas Europaea (European Company)
    }

    # Valid Chinese/Hong Kong country codes
    CHINESE_COUNTRY_CODES = {'CN', 'CHN', 'HK', 'HKG', 'MO', 'MAC'}

    # Known Chinese company suffixes (for positive identification)
    CHINESE_COMPANY_SUFFIXES = {
        'Co., Ltd.', 'Co., Ltd', 'Co. Ltd.', 'Co. Ltd',
        'Ltd.', 'Ltd', 'Limited',
        'Group Co., Ltd.', 'Group Co., Ltd',
        'Corporation', 'Corp.',
        'Company Limited', 'Co. Limited',
        'Holdings Limited', 'Holdings Ltd.',
        '有限公司',  # Limited Company
        '股份有限公司',  # Stock Company Limited
        '集团',  # Group
        '公司',  # Company
    }

    def __init__(self):
        """Initialize validator with compiled regex patterns for efficiency."""
        # Compile European suffix patterns for faster matching
        self.european_suffix_patterns = [
            re.compile(r'\b' + re.escape(suffix) + r'\b', re.IGNORECASE)
            for suffix in self.EUROPEAN_LEGAL_SUFFIXES
        ]

        # Chinese characters regex
        self.chinese_char_pattern = re.compile(r'[\u4e00-\u9fff]')

    def is_european_entity(self, entity_name: str) -> Tuple[bool, Optional[str]]:
        """
        Check if entity has European legal suffix.

        Returns:
            (is_european, matched_suffix)
        """
        for suffix in self.EUROPEAN_LEGAL_SUFFIXES:
            if suffix in entity_name:
                return True, suffix

        return False, None

    def has_chinese_characters(self, text: str) -> bool:
        """Check if text contains Chinese characters."""
        if not text:
            return False
        return bool(self.chinese_char_pattern.search(text))

    def validate_country_code(self, country_code: Optional[str]) -> bool:
        """
        Validate if country code indicates Chinese/Hong Kong entity.

        Args:
            country_code: ISO country code (e.g., 'CN', 'HK', 'DE')

        Returns:
            True if country code is Chinese/Hong Kong, False otherwise
        """
        if not country_code:
            return False  # No country code = cannot confirm

        return country_code.upper() in self.CHINESE_COUNTRY_CODES

    def calculate_chinese_confidence(
        self,
        entity_name: str,
        contractor_country: Optional[str] = None,
        contractor_address: Optional[str] = None,
        detection_method: Optional[str] = None
    ) -> Tuple[float, List[str]]:
        """
        Calculate confidence score that entity is actually Chinese.

        Args:
            entity_name: Name of the entity
            contractor_country: Country code from contract data
            contractor_address: Address from contract data
            detection_method: Method used for original detection

        Returns:
            (confidence_score, indicators_list)
            confidence_score: 0-100 scale
            indicators_list: List of positive/negative indicators found
        """
        score = 0.0
        indicators = []

        # EXCLUSION CHECKS (automatic disqualification)

        # Check for European legal suffix (instant exclusion)
        is_european, european_suffix = self.is_european_entity(entity_name)
        if is_european:
            indicators.append(f"EXCLUSION: European legal entity ({european_suffix})")
            return 0.0, indicators

        # Check country code (strong negative if European)
        if contractor_country:
            country_upper = contractor_country.upper()
            if country_upper in self.CHINESE_COUNTRY_CODES:
                score += 40.0
                indicators.append(f"STRONG: Country code is Chinese/HK ({contractor_country})")
            elif len(country_upper) == 2:  # Valid ISO code but not Chinese
                score -= 30.0
                indicators.append(f"NEGATIVE: Non-Chinese country code ({contractor_country})")

        # POSITIVE INDICATORS

        # Chinese characters in name (very strong indicator)
        if self.has_chinese_characters(entity_name):
            score += 35.0
            indicators.append("STRONG: Contains Chinese characters")

        # Chinese company suffix patterns
        for suffix in self.CHINESE_COMPANY_SUFFIXES:
            if suffix in entity_name:
                score += 15.0
                indicators.append(f"MODERATE: Chinese company suffix ({suffix})")
                break  # Only count once

        # Address contains Chinese indicators
        if contractor_address:
            if self.has_chinese_characters(contractor_address):
                score += 20.0
                indicators.append("STRONG: Address contains Chinese characters")

            # Check for Chinese city/province names
            chinese_locations = ['Beijing', 'Shanghai', 'Shenzhen', 'Guangzhou',
                               'Chengdu', 'Hangzhou', 'Wuhan', 'Chongqing',
                               'Hong Kong', 'Macau', 'Taiwan']
            for location in chinese_locations:
                if location.lower() in contractor_address.lower():
                    score += 15.0
                    indicators.append(f"MODERATE: Address mentions {location}")
                    break

        # Entity name patterns suggesting Chinese origin
        chinese_name_patterns = [
            'China', 'Chinese', 'Sino-', 'Beijing', 'Shanghai',
            'Shenzhen', 'Guangzhou', 'Hong Kong', 'Huawei', 'ZTE'
        ]
        for pattern in chinese_name_patterns:
            if pattern.lower() in entity_name.lower():
                score += 10.0
                indicators.append(f"MODERATE: Name contains '{pattern}'")
                break

        # Normalize score to 0-100 range
        score = max(0.0, min(100.0, score))

        return score, indicators

    def validate_entity(
        self,
        entity_name: str,
        contractor_country: Optional[str] = None,
        contractor_address: Optional[str] = None,
        min_confidence: float = 60.0
    ) -> Dict:
        """
        Perform comprehensive validation of potential Chinese entity.

        Args:
            entity_name: Name of entity to validate
            contractor_country: Country code from contract
            contractor_address: Address from contract
            min_confidence: Minimum confidence threshold (default 60%)

        Returns:
            Dictionary with validation results
        """
        # Calculate confidence
        confidence, indicators = self.calculate_chinese_confidence(
            entity_name,
            contractor_country,
            contractor_address
        )

        # Check for European exclusion
        is_european, european_suffix = self.is_european_entity(entity_name)

        # Check country code validation
        country_validated = self.validate_country_code(contractor_country)

        # Determine if entity should be flagged
        should_flag = (
            confidence >= min_confidence and
            not is_european and
            (country_validated or self.has_chinese_characters(entity_name))
        )

        return {
            'entity_name': entity_name,
            'is_valid_chinese': should_flag,
            'confidence_score': confidence,
            'is_european_exclusion': is_european,
            'european_suffix': european_suffix,
            'country_code': contractor_country,
            'country_validated': country_validated,
            'has_chinese_chars': self.has_chinese_characters(entity_name),
            'indicators': indicators,
            'validation_passed': should_flag
        }


# Singleton instance for easy import
validator = TEDEntityValidator()
