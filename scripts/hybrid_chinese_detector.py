#!/usr/bin/env python3
"""
Hybrid Chinese Entity Detection with Multiple Confidence Levels
Provides granular confidence scoring from CRITICAL to POSSIBLE
Balances precision and recall for comprehensive intelligence analysis
"""

import sqlite3
import json
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class ConfidenceLevel(Enum):
    CRITICAL = "CRITICAL"      # 0.95-1.0: Definitive Chinese entity
    HIGH = "HIGH"             # 0.80-0.94: Very likely Chinese
    MEDIUM = "MEDIUM"         # 0.60-0.79: Probably Chinese
    LOW = "LOW"               # 0.40-0.59: Possibly Chinese
    MINIMAL = "MINIMAL"       # 0.20-0.39: Weak indicators
    NONE = "NONE"            # 0.0-0.19: Not Chinese

@dataclass
class HybridDetectionResult:
    """Enhanced detection result with detailed confidence breakdown"""
    is_chinese: bool
    confidence_score: float
    confidence_level: ConfidenceLevel
    evidence_breakdown: Dict[str, float]  # Evidence type -> confidence contribution
    detected_patterns: List[str]
    risk_factors: List[str]
    certainty_factors: List[str]
    recommendation: str

class HybridChineseDetector:
    """Multi-level Chinese entity detection with confidence scoring"""

    def __init__(self):
        # CRITICAL CONFIDENCE (0.95-1.0): Definitive indicators
        self.critical_indicators = {
            'country_codes': {
                'patterns': ['CN', 'CHN'],
                'confidence': 1.0,
                'description': 'Definitive Chinese country code'
            },
            'major_companies': {
                'patterns': [
                    r'\bHuawei\s+Technologies?\b',
                    r'\bZTE\s+Corporation\b',
                    r'\bAlibaba\s+Group\b',
                    r'\bTencent\s+Holdings?\b',
                    r'\bChina\s+Mobile\b',
                    r'\bChina\s+Telecom\b',
                    r'\bSinopec\b',
                    r'\bPetroChina\b',
                    r'\bCRRC\s+Corporation\b',
                    r'\bCOSCO\s+Shipping\b'
                ],
                'confidence': 0.98,
                'description': 'Major Chinese corporation'
            }
        }

        # HIGH CONFIDENCE (0.80-0.94): Very strong indicators
        self.high_indicators = {
            'sar_regions': {
                'patterns': ['HK', 'MO', 'Hong Kong', 'Macau'],
                'confidence': 0.90,
                'description': 'Hong Kong/Macau entity'
            },
            'chinese_companies': {
                'patterns': [
                    r'\bBYD\s+Company\b', r'\bXiaomi\s+Corporation\b',
                    r'\bLenovo\s+Group\b', r'\bDJI\s+Technology\b',
                    r'\bHikvision\b', r'\bDahua\s+Technology\b',
                    r'\bBaidu\b', r'\bByteDance\b',
                    r'\bChongqing\s+\w+\s+Cable\b',
                    r'\bJiangFeng\s+Pipeline\b'
                ],
                'confidence': 0.95,
                'description': 'Known Chinese company'
            },
            'state_enterprises': {
                'patterns': [
                    r'\bChina\s+National\s+\w+\b',
                    r'\bChina\s+State\s+\w+\b',
                    r'\bAviation\s+Industry\s+Corporation\b',
                    r'\bChina\s+Aerospace\b'
                ],
                'confidence': 0.92,
                'description': 'Chinese state enterprise'
            },
            'geographic_strong': {
                'patterns': [
                    r'\bBeijing\s+\w+\s+(University|Institute|Corporation|Company)\b',
                    r'\bShanghai\s+\w+\s+(University|Institute|Corporation|Company)\b',
                    r'\bShenzhen\s+\w+\s+(Corporation|Company|Technology)\b',
                    r'\bGuangzhou\s+\w+\s+(Corporation|Company)\b'
                ],
                'confidence': 0.85,
                'description': 'Chinese city + institutional context'
            }
        }

        # MEDIUM CONFIDENCE (0.60-0.79): Probable indicators
        self.medium_indicators = {
            'universities': {
                'patterns': [
                    r'\bTsinghua\s+University\b',
                    r'\bPeking\s+University\b',
                    r'\bFudan\s+University\b',
                    r'\bShanghai\s+Jiao\s+Tong\b',
                    r'\bZhejiang\s+University\b',
                    r'\bBeijing\s+Institute\s+of\s+Technology\b',
                    r'\bHarbin\s+Institute\b'
                ],
                'confidence': 0.75,
                'description': 'Chinese university'
            },
            'geographic_medium': {
                'patterns': [
                    r'\bBeijing\b', r'\bShanghai\b', r'\bShenzhen\b',
                    r'\bGuangzhou\b', r'\bHangzhou\b', r'\bChengdu\b',
                    r'\bWuhan\b', r'\bNanjing\b', r'\bTianjin\b'
                ],
                'confidence': 0.65,
                'description': 'Major Chinese city mentioned'
            },
            'business_indicators': {
                'patterns': [
                    r'\bChina\s+\w+\s+Co\.?,?\s+Ltd\.?\b',
                    r'\b\w+\s+\(China\)\s+(Co\.?,?\s+)?Ltd\.?\b',
                    r'\b\w+\s+Shanghai\s+Co\.?\b',
                    r'\b\w+\s+Beijing\s+Co\.?\b'
                ],
                'confidence': 0.70,
                'description': 'Chinese business format'
            }
        }

        # LOW CONFIDENCE (0.40-0.59): Possible indicators
        self.low_indicators = {
            'weak_geographic': {
                'patterns': [
                    r'\bXi\'an\b', r'\bSuzhou\b', r'\bQingdao\b',
                    r'\bDalian\b', r'\bChongqing\b', r'\bShenyang\b'
                ],
                'confidence': 0.50,
                'description': 'Secondary Chinese city'
            },
            'general_terms': {
                'patterns': [
                    r'\bPeople\'s\s+Republic\b',
                    r'\bMainland\s+China\b',
                    r'\bChinese\s+\w+\s+(Academy|Institute)\b'
                ],
                'confidence': 0.45,
                'description': 'General Chinese terms'
            }
        }

        # MINIMAL CONFIDENCE (0.20-0.39): Weak indicators (for research)
        self.minimal_indicators = {
            'domain_indicators': {
                'patterns': [r'\.cn\b', r'\.com\.cn\b'],
                'confidence': 0.30,
                'description': 'Chinese domain'
            },
            'cultural_indicators': {
                'patterns': [
                    r'\bMandarin\b', r'\bCantonese\b',
                    r'\bTraditional\s+Chinese\b',
                    r'\bSimplified\s+Chinese\b'
                ],
                'confidence': 0.25,
                'description': 'Chinese cultural reference'
            }
        }

        # Compile all patterns for efficiency
        self.all_indicators = {
            'critical': self.critical_indicators,
            'high': self.high_indicators,
            'medium': self.medium_indicators,
            'low': self.low_indicators,
            'minimal': self.minimal_indicators
        }

        # Compile regex patterns
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile all regex patterns for efficiency"""
        for level_name, level_indicators in self.all_indicators.items():
            for indicator_name, indicator_data in level_indicators.items():
                compiled_patterns = []
                for pattern in indicator_data['patterns']:
                    if pattern.startswith('\\b') or '\\s+' in pattern:
                        # Regex pattern
                        compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
                    else:
                        # Simple string - convert to word boundary regex
                        escaped = re.escape(pattern)
                        compiled_patterns.append(re.compile(f'\\b{escaped}\\b', re.IGNORECASE))

                indicator_data['compiled'] = compiled_patterns

    def detect_chinese_entity(self, contractor_name: str, contractor_country: str,
                            contracting_authority: str, contract_text: str = "") -> HybridDetectionResult:
        """
        Comprehensive Chinese entity detection with confidence levels
        """

        # Combine all text for analysis
        full_text = f"{contractor_name or ''} {contracting_authority or ''} {contract_text or ''}"

        evidence_breakdown = {}
        detected_patterns = []
        certainty_factors = []
        risk_factors = []

        # Check country code first (highest priority)
        if contractor_country and contractor_country.upper() in ['CN', 'CHN']:
            evidence_breakdown['country_code'] = 1.0
            detected_patterns.append(f"Country: {contractor_country}")
            certainty_factors.append(f"Definitive country code: {contractor_country}")
        elif contractor_country and contractor_country.upper() in ['HK', 'MO']:
            evidence_breakdown['sar_region'] = 0.90
            detected_patterns.append(f"SAR Region: {contractor_country}")
            certainty_factors.append(f"Hong Kong/Macau region: {contractor_country}")

        # Check all indicator levels
        for level_name, level_indicators in self.all_indicators.items():
            for indicator_name, indicator_data in level_indicators.items():
                for pattern_obj in indicator_data['compiled']:
                    matches = pattern_obj.findall(full_text)
                    if matches:
                        # Record evidence
                        evidence_key = f"{level_name}_{indicator_name}"
                        current_confidence = evidence_breakdown.get(evidence_key, 0)
                        evidence_breakdown[evidence_key] = max(current_confidence, indicator_data['confidence'])

                        # Record patterns
                        for match in matches:
                            if isinstance(match, tuple):
                                match = ' '.join(match)
                            detected_patterns.append(f"{indicator_data['description']}: {match}")

                        # Add to appropriate factor list
                        if indicator_data['confidence'] >= 0.8:
                            certainty_factors.append(f"{indicator_data['description']}: {matches[0]}")
                        elif indicator_data['confidence'] >= 0.4:
                            risk_factors.append(f"{indicator_data['description']}: {matches[0]}")

        # Calculate overall confidence
        if not evidence_breakdown:
            total_confidence = 0.0
        else:
            # Weighted combination - higher confidence evidence gets more weight
            weights_sum = 0
            weighted_confidence = 0

            for evidence_type, confidence in evidence_breakdown.items():
                weight = confidence  # Higher confidence = higher weight
                weighted_confidence += confidence * weight
                weights_sum += weight

            total_confidence = weighted_confidence / weights_sum if weights_sum > 0 else 0.0

        # Determine confidence level
        if total_confidence >= 0.95:
            confidence_level = ConfidenceLevel.CRITICAL
        elif total_confidence >= 0.80:
            confidence_level = ConfidenceLevel.HIGH
        elif total_confidence >= 0.60:
            confidence_level = ConfidenceLevel.MEDIUM
        elif total_confidence >= 0.40:
            confidence_level = ConfidenceLevel.LOW
        elif total_confidence >= 0.20:
            confidence_level = ConfidenceLevel.MINIMAL
        else:
            confidence_level = ConfidenceLevel.NONE

        # Generate recommendation
        is_chinese = total_confidence >= 0.40  # Threshold for "Chinese" classification

        if confidence_level == ConfidenceLevel.CRITICAL:
            recommendation = "IMMEDIATE ATTENTION: Confirmed Chinese entity"
        elif confidence_level == ConfidenceLevel.HIGH:
            recommendation = "HIGH PRIORITY: Very likely Chinese entity"
        elif confidence_level == ConfidenceLevel.MEDIUM:
            recommendation = "INVESTIGATE: Probably Chinese entity"
        elif confidence_level == ConfidenceLevel.LOW:
            recommendation = "MONITOR: Possibly Chinese entity"
        elif confidence_level == ConfidenceLevel.MINIMAL:
            recommendation = "RESEARCH: Weak Chinese indicators"
        else:
            recommendation = "NO ACTION: No significant Chinese indicators"

        return HybridDetectionResult(
            is_chinese=is_chinese,
            confidence_score=total_confidence,
            confidence_level=confidence_level,
            evidence_breakdown=evidence_breakdown,
            detected_patterns=detected_patterns,
            risk_factors=risk_factors,
            certainty_factors=certainty_factors,
            recommendation=recommendation
        )

def test_hybrid_detector():
    """Test the hybrid detector on various cases"""
    detector = HybridChineseDetector()

    test_cases = [
        # Critical confidence cases
        ("Huawei Technologies Co., Ltd.", "CN", "", "Should be CRITICAL"),
        ("China Mobile Communications", "CN", "", "Should be CRITICAL"),

        # High confidence cases
        ("BYD Company Limited", "", "", "Should be HIGH"),
        ("Beijing Institute of Technology", "", "", "Should be HIGH"),
        ("", "HK", "", "Should be HIGH"),

        # Medium confidence cases
        ("Tsinghua University", "", "", "Should be MEDIUM"),
        ("Shanghai Automotive Corporation", "", "", "Should be MEDIUM"),

        # Low confidence cases
        ("Suzhou Manufacturing Co.", "", "", "Should be LOW"),
        ("", "", "People's Republic partnership", "Should be LOW"),

        # Minimal confidence cases
        ("Tech Solutions Ltd", "", "website: www.example.cn", "Should be MINIMAL"),

        # Should be NONE
        ("Dietz Automation GmbH", "DE", "", "Should be NONE"),
        ("GOPA Worldwide Consultants GmbH", "CN", "", "Should be CRITICAL - was missed before"),

        # Edge cases from our database
        ("Torpol S.A.", "PL", "", "Should be NONE"),
        ("Monaco Solutions", "MC", "", "Should be NONE")
    ]

    print("=== HYBRID CHINESE DETECTOR TEST ===\n")

    for contractor, country, authority, expected in test_cases:
        result = detector.detect_chinese_entity(contractor, country, authority)

        print(f"Entity: {contractor or '[empty]'} ({country or 'no country'})")
        print(f"Expected: {expected}")
        print(f"Result: {result.confidence_level.value} ({result.confidence_score:.3f})")
        print(f"Chinese: {result.is_chinese}")
        print(f"Recommendation: {result.recommendation}")
        if result.certainty_factors:
            print(f"Certainty: {result.certainty_factors[0]}")
        elif result.risk_factors:
            print(f"Risk Factor: {result.risk_factors[0]}")
        print("-" * 50)

def analyze_ted_with_hybrid():
    """Analyze TED database with hybrid detection"""
    detector = HybridChineseDetector()

    conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
    cursor = conn.cursor()

    # Add hybrid detection columns
    try:
        cursor.execute('ALTER TABLE ted_china_contracts ADD COLUMN hybrid_confidence_score REAL DEFAULT 0.0')
        cursor.execute('ALTER TABLE ted_china_contracts ADD COLUMN hybrid_confidence_level TEXT DEFAULT "NONE"')
        cursor.execute('ALTER TABLE ted_china_contracts ADD COLUMN hybrid_evidence TEXT')
        cursor.execute('ALTER TABLE ted_china_contracts ADD COLUMN hybrid_recommendation TEXT')
        print("Added hybrid detection columns")
    except sqlite3.OperationalError:
        print("Hybrid columns already exist")

    # Test on sample of previously flagged contracts
    cursor.execute('''
        SELECT contract_id, contractor_name, contractor_country, contracting_authority
        FROM ted_china_contracts
        WHERE china_linked = 1
        ORDER BY RANDOM()
        LIMIT 100
    ''')

    results_by_level = {level.value: 0 for level in ConfidenceLevel}
    sample_entities = {level.value: [] for level in ConfidenceLevel}

    for row in cursor.fetchall():
        contract_id, contractor, country, authority = row

        result = detector.detect_chinese_entity(contractor, country, authority)

        # Update database
        cursor.execute('''
            UPDATE ted_contracts
            SET hybrid_confidence_score = ?,
                hybrid_confidence_level = ?,
                hybrid_evidence = ?,
                hybrid_recommendation = ?
            WHERE contract_id = ?
        ''', (
            result.confidence_score,
            result.confidence_level.value,
            json.dumps(result.evidence_breakdown),
            result.recommendation,
            contract_id
        ))

        # Collect statistics
        level = result.confidence_level.value
        results_by_level[level] += 1

        if len(sample_entities[level]) < 3:
            try:
                name_clean = (contractor or '').encode('ascii', 'ignore').decode('ascii')[:50]
                sample_entities[level].append({
                    'name': name_clean,
                    'country': country or 'N/A',
                    'confidence': result.confidence_score,
                    'evidence': result.certainty_factors[0] if result.certainty_factors else
                               result.risk_factors[0] if result.risk_factors else 'No evidence'
                })
            except:
                pass

    conn.commit()
    conn.close()

    print("\n=== HYBRID DETECTION ANALYSIS RESULTS ===")
    print(f"Sample size: 100 previously flagged contracts\n")

    for level in ConfidenceLevel:
        count = results_by_level[level.value]
        print(f"{level.value}: {count} entities")
        for entity in sample_entities[level.value]:
            print(f"  - {entity['name']} ({entity['country']}) - {entity['confidence']:.3f}")
            print(f"    {entity['evidence']}")

    return results_by_level

if __name__ == "__main__":
    # Test the hybrid detector
    test_hybrid_detector()

    print("\n" + "="*70)
    print("ANALYZING TED DATABASE WITH HYBRID DETECTION")
    print("="*70)

    # Analyze TED database
    results = analyze_ted_with_hybrid()

    print(f"\nSUMMARY:")
    total_positive = sum(v for k, v in results.items() if k != 'NONE')
    print(f"Total entities with Chinese indicators: {total_positive}")
    print(f"High confidence entities (CRITICAL + HIGH): {results['CRITICAL'] + results['HIGH']}")
    print(f"Worth investigating (MEDIUM + LOW): {results['MEDIUM'] + results['LOW']}")
    print(f"False positives eliminated: {results['NONE']}")
