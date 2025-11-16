#!/usr/bin/env python3
"""
language_detection_helper.py - European Language False Positive Detection

Hybrid approach combining:
1. Language detection (langdetect) - with high confidence threshold
2. Keyword-based patterns (German, Finnish, Portuguese, etc.)
3. Domain knowledge (technical terms, company suffixes)

Purpose: Identify non-Chinese European language entities that may be false positives
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

try:
    from langdetect import detect_langs, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("Warning: langdetect not available, using pattern-based detection only")


@dataclass
class LanguageDetectionResult:
    """Result of language detection analysis"""
    text: str
    detected_language: Optional[str]
    confidence: float
    matching_patterns: List[str]
    is_likely_false_positive: bool
    reasoning: str


class EuropeanLanguageDetector:
    """Detect European language false positives in Chinese entity detection"""

    # German technical/business suffixes and words
    GERMAN_PATTERNS = {
        'technical_suffixes': [
            r'\btechnik\b',
            r'\btechnische\b',
            r'\btechnischen\b',
            r'\bheiztechnik\b',
            r'\bkonferenztechnik\b',
            r'\bmedizintechnik\b',
            r'\belektrotechnik\b',
            r'\binformationstechnik\b',
        ],
        'business_suffixes': [
            r'\bgmbh\b',
            r'\bg\.m\.b\.h\b',
            r'\bag\b',
            r'\bkg\b',
            r'\be\.v\b',
            r'\bgesellschaft\b',
        ],
        'common_words': [
            r'\bund\b',
            r'\bdeutsche\b',
            r'\bdeutschen\b',
            r'\bdienstleistungen\b',
            r'\bkasino\b',
            r'\bfuer\b',
            r'\bvon\b',
        ],
    }

    # Finnish patterns
    FINNISH_PATTERNS = {
        'company_suffixes': [
            r'\boy\b',
            r'\boyj\b',
            r'\bab\b',
        ],
        'technical_words': [
            r'insinooritoimisto',  # Engineering firm
            r'toimisto',  # Office
            r'palvelu',  # Service
        ],
    }

    # Portuguese patterns
    PORTUGUESE_PATTERNS = {
        'common_words': [
            r'\bensino\b',  # Teaching
            r'\bpesquisa\b',  # Research
            r'\bservicos\b',  # Services
            r'\bconstrucoes\b',  # Construction
            r'\blimitada\b',  # Limited
        ],
        'business_suffixes': [
            r'\bltda\b',
            r'\bs\.a\b',
        ],
    }

    # Italian patterns
    ITALIAN_PATTERNS = {
        'company_suffixes': [
            r'\bs\.p\.a\b',
            r'\bs\.r\.l\b',
            r'\bs\.n\.c\b',
        ],
        'common_words': [
            r'\bsoc\b',
            r'\bcoop\b',
            r'\blivornese\b',
            r'\bfacchinaggi\b',
            r'\bfacchina\b',
        ],
    }

    # Russian/Slavic patterns
    RUSSIAN_PATTERNS = {
        'company_suffixes': [
            r'\bzao\b',
            r'\boao\b',
            r'\bpao\b',
        ],
        'common_words': [
            r'golitsino',
            r'russinov',
        ],
        'company_names': [
            r'russinov\s+communications',  # Specific company
        ],
    }

    # Greek patterns
    GREEK_PATTERNS = {
        'common_words': [
            r'prasino',
            r'astiko',
        ],
    }

    # Hungarian patterns
    HUNGARIAN_PATTERNS = {
        'common_words': [
            r'lakasztextil',
            r'pand\s+k\.',
        ],
    }

    # Geographic/regional names (not related to China)
    GEOGRAPHIC_PATTERNS = {
        'indochina': [
            r'\bindochina\b',  # Vietnam/Cambodia/Laos region
        ],
        'us_locations': [
            r'\bchina\s+grove\b',
            r'\bchina\s+lake\b',
            r'\bchina\s+spring\b',
        ],
    }

    # Common English words that contain Chinese patterns
    ENGLISH_COMMON_WORDS = {
        'containing_he': [
            r'\bthe\b',
            r'\bwhen\b',
            r'\bwhere\b',
            r'\bwhether\b',
            r'\bother\b',
        ],
        'containing_li': [
            r'\blimited\b',
            r'\bliability\b',
            r'\blicense\b',
        ],
        'containing_chin': [
            r'\bmachine\b',
            r'\bmachinery\b',
            r'\bmachining\b',
            r'\bteaching\b',
            r'\bcoaching\b',
            r'\bmachinary\b',  # Common misspelling
        ],
    }

    # Additional European patterns
    ADDITIONAL_EUROPEAN = {
        'tech_company_suffixes': [
            r'tech\b',  # Generic tech companies
            r'construcoes',  # Portuguese construction
        ],
    }

    # Known false positive company patterns
    KNOWN_FALSE_POSITIVES = [
        r'comac\s+pump',  # Not COMAC aircraft
        r'aztec\s+environmental',  # Not ZTE
        r'cosco\s+fire\s+protection',  # Not COSCO shipping
        r'cosco\s+fire',  # Not COSCO shipping
        r'american\s+cosco',  # American COSCO (not China COSCO Shipping)
        r'sino[-\s]?european',  # European joint ventures
        r'sino[-\s]?german',
        r'euro[-\s]?china',
        r'sino[-\s]?french',
        r'sino[-\s]?italian',
        r'homer\s+laughlin\s+china',  # Porcelain company
        r'casino',
        r'kasino',  # German spelling of casino
        r'resort',
        r'hotel',
        r'insurance\s+company',
        r'in\s+indochina',  # Geographic qualifier
        r'traffic\s+international',  # NGO working in Indochina
    ]

    def __init__(self, confidence_threshold: float = 0.8):
        """
        Initialize detector

        Args:
            confidence_threshold: Minimum confidence for langdetect (0.0-1.0)
        """
        self.confidence_threshold = confidence_threshold
        self.langdetect_available = LANGDETECT_AVAILABLE

    def detect_language(self, text: str) -> Tuple[Optional[str], float]:
        """
        Detect language using langdetect (if available)

        Returns:
            (language_code, confidence) or (None, 0.0) if unavailable/uncertain
        """
        if not self.langdetect_available or not text:
            return None, 0.0

        try:
            results = detect_langs(text.lower())
            if results:
                top_result = results[0]
                return top_result.lang, top_result.prob
            return None, 0.0
        except LangDetectException:
            return None, 0.0

    def check_patterns(self, text: str, pattern_dict: Dict[str, List[str]]) -> List[str]:
        """Check if text matches any patterns in dictionary"""
        matches = []
        text_lower = text.lower()

        for category, patterns in pattern_dict.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matches.append(f"{category}:{pattern}")

        return matches

    def analyze_text(self, text: str) -> LanguageDetectionResult:
        """
        Comprehensive language analysis

        Returns:
            LanguageDetectionResult with detection and reasoning
        """
        text_lower = text.lower()

        # Language detection
        lang, lang_confidence = self.detect_language(text)

        # Pattern matching
        all_matches = []

        # Check known false positives first
        known_fp_matches = []
        for pattern in self.KNOWN_FALSE_POSITIVES:
            if re.search(pattern, text_lower, re.IGNORECASE):
                known_fp_matches.append(f"known_fp:{pattern}")

        if known_fp_matches:
            return LanguageDetectionResult(
                text=text,
                detected_language=lang,
                confidence=1.0,  # High confidence for known patterns
                matching_patterns=known_fp_matches,
                is_likely_false_positive=True,
                reasoning=f"Matches known false positive pattern: {', '.join(known_fp_matches)}"
            )

        # Check European language patterns
        german_matches = self.check_patterns(text, self.GERMAN_PATTERNS)
        finnish_matches = self.check_patterns(text, self.FINNISH_PATTERNS)
        portuguese_matches = self.check_patterns(text, self.PORTUGUESE_PATTERNS)
        italian_matches = self.check_patterns(text, self.ITALIAN_PATTERNS)
        russian_matches = self.check_patterns(text, self.RUSSIAN_PATTERNS)
        greek_matches = self.check_patterns(text, self.GREEK_PATTERNS)
        hungarian_matches = self.check_patterns(text, self.HUNGARIAN_PATTERNS)
        geographic_matches = self.check_patterns(text, self.GEOGRAPHIC_PATTERNS)
        english_matches = self.check_patterns(text, self.ENGLISH_COMMON_WORDS)
        additional_matches = self.check_patterns(text, self.ADDITIONAL_EUROPEAN)

        all_matches = (german_matches + finnish_matches + portuguese_matches +
                      italian_matches + russian_matches + greek_matches +
                      hungarian_matches + geographic_matches + english_matches +
                      additional_matches)

        # Decision logic
        is_false_positive = False
        reasoning_parts = []

        # Strong pattern evidence
        if len(all_matches) >= 2:
            is_false_positive = True
            reasoning_parts.append(f"Multiple European language patterns: {', '.join(all_matches)}")

        elif len(all_matches) == 1:
            # Single pattern match
            match = all_matches[0]

            # German technical suffixes are strong indicators
            if 'german:technical_suffixes' in match or 'german:business_suffixes' in match:
                is_false_positive = True
                reasoning_parts.append(f"German company/technical term: {match}")

            # Portuguese/Italian business suffixes
            elif any(x in match for x in ['portuguese:', 'italian:', 'finnish:']):
                is_false_positive = True
                reasoning_parts.append(f"European company suffix: {match}")

            # Geographic names
            elif 'geographic:' in match:
                is_false_positive = True
                reasoning_parts.append(f"Geographic region (not China): {match}")

            # Russian/Portuguese/Greek/Hungarian words
            elif any(x in match for x in ['russian:', 'portuguese:', 'greek:', 'hungarian:']):
                is_false_positive = True
                reasoning_parts.append(f"European language word: {match}")

            # English misspellings that create Chinese patterns
            elif 'containing_chin:' in match and 'machinary' in text_lower:
                is_false_positive = True
                reasoning_parts.append(f"Common misspelling creating false Chinese pattern: {match}")

            else:
                # Weaker evidence, use language detection with lower threshold
                if lang and lang_confidence >= 0.60:  # Lower threshold for single pattern
                    if lang in ['de', 'fi', 'pt', 'it', 'ru', 'el', 'hu', 'es', 'fr', 'ro']:
                        is_false_positive = True
                        reasoning_parts.append(f"Language detection: {lang} ({lang_confidence:.2%}), pattern: {match}")

        # Language detection only (no pattern matches)
        elif lang and lang_confidence >= 0.95:  # Very high threshold without patterns
            if lang in ['de', 'fi', 'pt', 'it', 'ru', 'el', 'hu', 'es', 'fr']:
                is_false_positive = True
                reasoning_parts.append(f"High-confidence language detection: {lang} ({lang_confidence:.2%})")

        # Build final reasoning
        if not reasoning_parts:
            if lang:
                reasoning_parts.append(f"Language detected as {lang} ({lang_confidence:.2%}), but below threshold or not European")
            else:
                reasoning_parts.append("No European language patterns detected")

        reasoning = "; ".join(reasoning_parts)

        return LanguageDetectionResult(
            text=text,
            detected_language=lang,
            confidence=lang_confidence if all_matches else max(lang_confidence, len(all_matches) * 0.3),
            matching_patterns=all_matches,
            is_likely_false_positive=is_false_positive,
            reasoning=reasoning
        )

    def batch_analyze(self, texts: List[str]) -> List[LanguageDetectionResult]:
        """Analyze multiple texts"""
        return [self.analyze_text(text) for text in texts]


def main():
    """Test the detector on known false positive samples"""

    detector = EuropeanLanguageDetector(confidence_threshold=0.8)

    # Test cases from our manual review
    test_cases = [
        # German technical words
        "HDS HEIZTECHNISCHE DIENSTLEISTUNGEN",
        "BRAEHLER ICS KONFERENZTECHNI",
        "EICKEMEYER MEDIZINTECHNIK FUER TIERAERZTE KG",
        "R & W ROHR- UND HEIZTECHNIK GMBH",
        "TTV-BILD-+ KONFERENZTECHNIK GMBH",

        # German casino
        "UHG KASINO",

        # Finnish
        "INSINOORITOIMISTO MIKKO GRANLUND OY",

        # Portuguese
        "ENSINO E PESQUISA LTDA",
        "MOZTECH CONSTRUCOES",

        # Italian
        "SOC COOP LIVORNESE",
        "FACCHINAGGI SRL",

        # Russian
        'ZAO "GOLITSINO"',
        "RUSSINOV COMMUNICATIONS",

        # Greek
        "ASTIKO PRASINO",

        # Geographic
        "INDOCHINA RESEARCH LIMITED",
        "TRAFFIC INTERNATIONAL IN INDOCHINA",

        # Known false positives
        "COMAC PUMP & WELL LLC",
        "AZTEC ENVIRONMENTAL",
        "COSCO FIRE PROTECTION INC",
        "HOMER LAUGHLIN CHINA COMPANY",

        # English machinery misspelling
        "TRADING AND DEVELOPMENT COMPANY FOR MACHINARY AND EQUIPMENT",

        # Should NOT be flagged (legitimate Chinese entities)
        "CHINA SHIPPING DEVELOPMENT CO., LTD.",
        "BEIJING TECHNOLOGY CORPORATION",
        "HUAWEI TECHNOLOGIES CO., LTD.",
        "LENOVO GROUP LIMITED",
    ]

    print("="*100)
    print("EUROPEAN LANGUAGE FALSE POSITIVE DETECTION TEST")
    print("="*100)
    print()

    false_positives_identified = 0
    legitimate_entities_protected = 0

    for text in test_cases:
        result = detector.analyze_text(text)

        # Determine if this is expected to be a false positive
        is_expected_fp = not any(x in text.upper() for x in ['CHINA SHIPPING', 'BEIJING', 'HUAWEI', 'LENOVO'])

        status = "[OK]" if result.is_likely_false_positive == is_expected_fp else "[X]"

        if result.is_likely_false_positive:
            false_positives_identified += 1
        else:
            if any(x in text.upper() for x in ['CHINA SHIPPING', 'BEIJING', 'HUAWEI', 'LENOVO']):
                legitimate_entities_protected += 1

        print(f"{status} {text}")
        print(f"   False Positive: {result.is_likely_false_positive}")
        print(f"   Reasoning: {result.reasoning}")
        if result.matching_patterns:
            print(f"   Patterns: {', '.join(result.matching_patterns)}")
        print()

    print("="*100)
    print(f"Summary:")
    print(f"  False positives identified: {false_positives_identified}")
    print(f"  Legitimate entities protected: {legitimate_entities_protected}")
    print(f"  Total tested: {len(test_cases)}")
    print("="*100)


if __name__ == "__main__":
    main()
