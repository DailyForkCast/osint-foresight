#!/usr/bin/env python3
"""
Refined Chinese Entity Detection
Fixes false positive problem in original pattern matching
Uses word boundaries and context-aware matching
"""

import sqlite3
import json
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ChineseDetectionResult:
    """Result of Chinese entity detection"""
    is_chinese: bool
    confidence: float
    evidence: List[str]
    method: str
    patterns_found: List[str]

class RefinedChineseDetector:
    """Improved Chinese entity detection with false positive prevention"""

    def __init__(self):
        # HIGH CONFIDENCE: Country codes (definitive)
        self.country_codes = ['CN', 'CHN']

        # HIGH CONFIDENCE: Complete company names (word boundaries required)
        self.chinese_company_names = [
            'Huawei Technologies', 'ZTE Corporation', 'Alibaba Group',
            'Tencent Holdings', 'Baidu', 'ByteDance', 'DJI',
            'Hikvision', 'Dahua Technology', 'BYD Company',
            'Xiaomi Corporation', 'Lenovo Group', 'SMIC',
            'CRRC Corporation', 'COSCO Shipping', 'China Mobile',
            'China Telecom', 'China Unicom', 'Sinopec',
            'PetroChina', 'State Grid Corporation',
            'Aviation Industry Corporation', 'China Aerospace',
            'Chongqing Taishan Cable', 'JiangFeng Pipeline Group'
        ]

        # MEDIUM CONFIDENCE: Geographic indicators (word boundaries required)
        self.chinese_cities = [
            'Beijing', 'Shanghai', 'Shenzhen', 'Guangzhou', 'Hangzhou',
            'Tianjin', 'Chengdu', 'Wuhan', 'Nanjing', 'Xi\'an',
            'Suzhou', 'Qingdao', 'Dalian', 'Chongqing', 'Shenyang'
        ]

        # MEDIUM CONFIDENCE: Chinese terms (word boundaries required)
        self.chinese_terms = [
            'China National', 'China State', 'Chinese Academy',
            'People\'s Republic', 'Mainland China'
        ]

        # LOW CONFIDENCE: Universities (require additional context)
        self.chinese_universities = [
            'Tsinghua University', 'Peking University', 'Fudan University',
            'Shanghai Jiao Tong University', 'Zhejiang University',
            'University of Science and Technology of China',
            'Beijing Institute of Technology', 'Harbin Institute'
        ]

        # EXCLUDE: Common false positive patterns
        self.false_positive_patterns = [
            r'\bmo\b',  # Polish "Sp. z o.o." (limited liability company)
            r'\bnio\b', # Common in Polish words
            r'\bcn\b',  # Common abbreviation in many languages
            r'\bgac\b', # Common abbreviation
            r'\bhk\b'   # Could be many things
        ]

        # Compile regex patterns for efficiency
        self.company_regex = self._compile_word_boundary_patterns(self.chinese_company_names)
        self.city_regex = self._compile_word_boundary_patterns(self.chinese_cities)
        self.terms_regex = self._compile_word_boundary_patterns(self.chinese_terms)
        self.university_regex = self._compile_word_boundary_patterns(self.chinese_universities)

    def _compile_word_boundary_patterns(self, patterns: List[str]) -> List[re.Pattern]:
        """Compile patterns with word boundaries"""
        compiled = []
        for pattern in patterns:
            # Use word boundaries and case insensitive
            regex = re.compile(r'\b' + re.escape(pattern) + r'\b', re.IGNORECASE)
            compiled.append((pattern, regex))
        return compiled

    def check_country_code(self, contractor_country: str) -> ChineseDetectionResult:
        """Check if contractor country is Chinese"""
        if not contractor_country:
            return ChineseDetectionResult(False, 0.0, [], "country_code", [])

        if contractor_country.upper() in self.country_codes:
            return ChineseDetectionResult(
                is_chinese=True,
                confidence=1.0,
                evidence=[f"Country code: {contractor_country}"],
                method="country_code",
                patterns_found=[contractor_country]
            )

        # Special handling for Hong Kong and Macau
        if contractor_country.upper() in ['HK', 'MO']:
            return ChineseDetectionResult(
                is_chinese=True,
                confidence=0.9,
                evidence=[f"SAR country code: {contractor_country}"],
                method="country_code",
                patterns_found=[contractor_country]
            )

        return ChineseDetectionResult(False, 0.0, [], "country_code", [])

    def check_company_name(self, text: str) -> ChineseDetectionResult:
        """Check for known Chinese company names"""
        if not text:
            return ChineseDetectionResult(False, 0.0, [], "company_name", [])

        evidence = []
        patterns_found = []

        for pattern, regex in self.company_regex:
            if regex.search(text):
                evidence.append(f"Company name: {pattern}")
                patterns_found.append(pattern)

        if patterns_found:
            return ChineseDetectionResult(
                is_chinese=True,
                confidence=0.95,
                evidence=evidence,
                method="company_name",
                patterns_found=patterns_found
            )

        return ChineseDetectionResult(False, 0.0, [], "company_name", [])

    def check_geographic_indicators(self, text: str) -> ChineseDetectionResult:
        """Check for Chinese cities and geographic terms"""
        if not text:
            return ChineseDetectionResult(False, 0.0, [], "geographic", [])

        evidence = []
        patterns_found = []

        # Check cities
        for pattern, regex in self.city_regex:
            if regex.search(text):
                evidence.append(f"Chinese city: {pattern}")
                patterns_found.append(pattern)

        # Check Chinese terms
        for pattern, regex in self.terms_regex:
            if regex.search(text):
                evidence.append(f"Chinese term: {pattern}")
                patterns_found.append(pattern)

        if patterns_found:
            confidence = 0.8 if len(patterns_found) > 1 else 0.6
            return ChineseDetectionResult(
                is_chinese=True,
                confidence=confidence,
                evidence=evidence,
                method="geographic",
                patterns_found=patterns_found
            )

        return ChineseDetectionResult(False, 0.0, [], "geographic", [])

    def check_universities(self, text: str) -> ChineseDetectionResult:
        """Check for Chinese universities (lower confidence, needs context)"""
        if not text:
            return ChineseDetectionResult(False, 0.0, [], "university", [])

        evidence = []
        patterns_found = []

        for pattern, regex in self.university_regex:
            if regex.search(text):
                evidence.append(f"Chinese university: {pattern}")
                patterns_found.append(pattern)

        if patterns_found:
            return ChineseDetectionResult(
                is_chinese=True,
                confidence=0.7,
                evidence=evidence,
                method="university",
                patterns_found=patterns_found
            )

        return ChineseDetectionResult(False, 0.0, [], "university", [])

    def detect_chinese_entity(self, contractor_name: str, contractor_country: str,
                            contracting_authority: str, contract_text: str = "") -> ChineseDetectionResult:
        """
        Comprehensive Chinese entity detection
        Returns highest confidence result
        """

        # Combine all text for analysis
        full_text = f"{contractor_name or ''} {contracting_authority or ''} {contract_text or ''}"

        results = []

        # 1. Check country code (highest priority)
        country_result = self.check_country_code(contractor_country)
        if country_result.is_chinese:
            results.append(country_result)

        # 2. Check company name
        company_result = self.check_company_name(full_text)
        if company_result.is_chinese:
            results.append(company_result)

        # 3. Check geographic indicators
        geo_result = self.check_geographic_indicators(full_text)
        if geo_result.is_chinese:
            results.append(geo_result)

        # 4. Check universities (only if no higher confidence match)
        if not results:
            uni_result = self.check_universities(full_text)
            if uni_result.is_chinese:
                results.append(uni_result)

        # Return highest confidence result
        if results:
            best_result = max(results, key=lambda x: x.confidence)

            # Combine evidence from all methods
            all_evidence = []
            all_patterns = []
            for result in results:
                all_evidence.extend(result.evidence)
                all_patterns.extend(result.patterns_found)

            return ChineseDetectionResult(
                is_chinese=True,
                confidence=best_result.confidence,
                evidence=all_evidence,
                method=best_result.method,
                patterns_found=list(set(all_patterns))
            )

        return ChineseDetectionResult(False, 0.0, [], "none", [])


def test_refined_detector():
    """Test the refined detector on known cases"""
    detector = RefinedChineseDetector()

    test_cases = [
        # True positives
        ("Huawei Technologies Co., Ltd.", "CN", "", "Should detect: Chinese company in China"),
        ("Beijing University", "", "", "Should detect: Chinese university"),
        ("China National Petroleum", "", "", "Should detect: Chinese state enterprise"),
        ("Chongqing Taishan Cable Co., Ltd", "CN", "", "Should detect: Known Chinese company"),

        # False positives from original system
        ("Dietz Automation & Umwelttechnik GmbH", "DE", "", "Should NOT detect: German automation company"),
        ("Torpol S.A.", "PL", "", "Should NOT detect: Polish company"),
        ("Konsorcjum CIS", "PL", "", "Should NOT detect: Polish consortium"),
        ("Oktan Energy Sp. z o.o.", "PL", "", "Should NOT detect: Polish energy company"),

        # Edge cases
        ("", "HK", "", "Should detect: Hong Kong entity"),
        ("Company with Beijing office", "", "", "Should detect: Has Chinese city"),
        ("Monaco Tech Solutions", "MC", "", "Should NOT detect: Monaco company with MO pattern"),
        ("Automotive Solutions", "DE", "", "Should NOT detect: German automotive")
    ]

    print("=== TESTING REFINED CHINESE DETECTOR ===\n")

    for contractor, country, authority, expected in test_cases:
        result = detector.detect_chinese_entity(contractor, country, authority)

        status = "✓ PASS" if ("Should detect" in expected and result.is_chinese) or \
                           ("Should NOT detect" in expected and not result.is_chinese) else "✗ FAIL"

        print(f"{status} | Conf: {result.confidence:.2f} | {contractor} ({country})")
        print(f"     Expected: {expected}")
        print(f"     Result: {result.is_chinese} via {result.method}")
        if result.evidence:
            print(f"     Evidence: {result.evidence}")
        print()


def reanalyze_ted_database():
    """Re-analyze TED database with refined detection"""
    detector = RefinedChineseDetector()

    conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
    cursor = conn.cursor()

    # Get sample of current "Chinese" matches
    cursor.execute('''
        SELECT contract_id, contractor_name, contractor_country,
               contracting_authority, china_patterns_found
        FROM ted_china_contracts
        WHERE china_linked = 1
        LIMIT 100
    ''')

    results = {
        'confirmed_chinese': 0,
        'false_positives': 0,
        'high_confidence': [],
        'medium_confidence': [],
        'false_positives_list': []
    }

    for row in cursor.fetchall():
        contract_id, contractor, country, authority, old_patterns = row

        # Apply refined detection
        result = detector.detect_chinese_entity(contractor, country, authority)

        if result.is_chinese:
            if result.confidence >= 0.9:
                results['confirmed_chinese'] += 1
                results['high_confidence'].append({
                    'contract_id': contract_id,
                    'contractor': contractor,
                    'country': country,
                    'confidence': result.confidence,
                    'evidence': result.evidence
                })
            elif result.confidence >= 0.6:
                results['medium_confidence'].append({
                    'contract_id': contract_id,
                    'contractor': contractor,
                    'country': country,
                    'confidence': result.confidence,
                    'evidence': result.evidence
                })
        else:
            results['false_positives'] += 1
            results['false_positives_list'].append({
                'contract_id': contract_id,
                'contractor': contractor,
                'country': country,
                'old_patterns': json.loads(old_patterns) if old_patterns else []
            })

    conn.close()

    return results


if __name__ == "__main__":
    # Test the detector
    test_refined_detector()

    # Analyze current database
    print("\n" + "="*60)
    print("ANALYZING CURRENT TED DATABASE WITH REFINED DETECTION")
    print("="*60)

    analysis = reanalyze_ted_database()

    print(f"\nRESULTS FROM 100 SAMPLE CONTRACTS:")
    print(f"High Confidence Chinese: {len(analysis['high_confidence'])}")
    print(f"Medium Confidence Chinese: {len(analysis['medium_confidence'])}")
    print(f"False Positives Eliminated: {analysis['false_positives']}")

    print(f"\nHIGH CONFIDENCE MATCHES:")
    for match in analysis['high_confidence'][:5]:
        print(f"- {match['contractor']} ({match['country']}) - {match['confidence']:.2f}")
        print(f"  Evidence: {'; '.join(match['evidence'])}")

    print(f"\nFALSE POSITIVES ELIMINATED:")
    for fp in analysis['false_positives_list'][:5]:
        print(f"- {fp['contractor']} ({fp['country']})")
        print(f"  Old patterns: {fp['old_patterns']}")
