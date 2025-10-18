#!/usr/bin/env python3
"""
Enhanced Validation Framework v2.0
Expanded geographic scope with multilingual support and pattern detection
Specifically handles UK, Norway, Switzerland, Balkans, Turkey, Armenia, Azerbaijan, Georgia, Iceland
"""

import json
import logging
import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MultilingualPattern:
    """Pattern for multilingual entity detection"""
    language: str
    pattern: str
    context_keywords: List[str]
    false_positive_indicators: List[str]
    confidence_modifier: float

@dataclass
class GeographicContext:
    """Geographic context for validation"""
    country_code: str
    country_name: str
    languages: List[str]
    currency: str
    eu_member: bool
    eea_member: bool
    special_status: Optional[str]

class ExpandedGeographicValidator:
    """
    Validation for expanded geographic scope
    Handles all European countries including non-EU states
    """

    def __init__(self):
        self.geographic_contexts = self._load_geographic_contexts()
        self.multilingual_patterns = self._load_multilingual_patterns()
        self.china_indicators = self._load_china_indicators()

    def _load_geographic_contexts(self) -> Dict[str, GeographicContext]:
        """Load geographic validation contexts"""

        contexts = {
            # Non-EU European States (Priority expansion)
            'GB': GeographicContext('GB', 'United Kingdom', ['en'], 'GBP', False, False, 'Post-Brexit'),
            'NO': GeographicContext('NO', 'Norway', ['no', 'nb', 'nn'], 'NOK', False, True, 'EEA/EFTA'),
            'CH': GeographicContext('CH', 'Switzerland', ['de', 'fr', 'it', 'rm'], 'CHF', False, False, 'EFTA'),
            'IS': GeographicContext('IS', 'Iceland', ['is'], 'ISK', False, True, 'EEA/EFTA'),

            # Balkans (Full coverage)
            'AL': GeographicContext('AL', 'Albania', ['sq'], 'ALL', False, False, 'EU Candidate'),
            'BA': GeographicContext('BA', 'Bosnia and Herzegovina', ['bs', 'hr', 'sr'], 'BAM', False, False, 'EU Potential Candidate'),
            'MK': GeographicContext('MK', 'North Macedonia', ['mk'], 'MKD', False, False, 'EU Candidate'),
            'ME': GeographicContext('ME', 'Montenegro', ['sr'], 'EUR', False, False, 'EU Candidate'),
            'RS': GeographicContext('RS', 'Serbia', ['sr'], 'RSD', False, False, 'EU Candidate'),
            'XK': GeographicContext('XK', 'Kosovo', ['sq', 'sr'], 'EUR', False, False, 'Disputed Status'),

            # Caucasus (Full coverage)
            'AM': GeographicContext('AM', 'Armenia', ['hy'], 'AMD', False, False, 'Eastern Partnership'),
            'AZ': GeographicContext('AZ', 'Azerbaijan', ['az'], 'AZN', False, False, 'Eastern Partnership'),
            'GE': GeographicContext('GE', 'Georgia', ['ka'], 'GEL', False, False, 'Eastern Partnership'),

            # Turkey
            'TR': GeographicContext('TR', 'Turkey', ['tr'], 'TRY', False, False, 'EU Candidate'),

            # EU Countries (for reference)
            'DE': GeographicContext('DE', 'Germany', ['de'], 'EUR', True, True, None),
            'FR': GeographicContext('FR', 'France', ['fr'], 'EUR', True, True, None),
            'IT': GeographicContext('IT', 'Italy', ['it'], 'EUR', True, True, None),
            'ES': GeographicContext('ES', 'Spain', ['es', 'ca', 'gl', 'eu'], 'EUR', True, True, None),
            'PL': GeographicContext('PL', 'Poland', ['pl'], 'PLN', True, True, None),
            'HU': GeographicContext('HU', 'Hungary', ['hu'], 'HUF', True, True, None),
            'GR': GeographicContext('GR', 'Greece', ['el'], 'EUR', True, True, None),
        }

        return contexts

    def _load_multilingual_patterns(self) -> Dict[str, List[MultilingualPattern]]:
        """Load multilingual pattern detection rules"""

        patterns = {
            # English patterns (UK)
            'en': [
                MultilingualPattern(
                    language='en',
                    pattern=r'\b(China|Chinese|PRC|Beijing|Shanghai)\s+(company|corporation|enterprise|firm|supplier|contractor|vendor)\b',
                    context_keywords=['contract', 'agreement', 'procurement', 'tender', 'supply'],
                    false_positive_indicators=['china shop', 'china plate', 'china clay'],
                    confidence_modifier=1.0
                ),
                MultilingualPattern(
                    language='en',
                    pattern=r'\b(Huawei|ZTE|SMIC|CNOOC|Sinopec|Xiaomi|BYD|CATL|Hikvision|Dahua)\b',
                    context_keywords=['technology', 'equipment', 'infrastructure', '5G', 'telecom'],
                    false_positive_indicators=[],
                    confidence_modifier=1.2
                ),
            ],

            # Norwegian patterns
            'no': [
                MultilingualPattern(
                    language='no',
                    pattern=r'\b(kinesisk|Kina)\s+(selskap|firma|leverandør|entreprenør)\b',
                    context_keywords=['kontrakt', 'avtale', 'anskaffelse', 'teknologi'],
                    false_positive_indicators=['porselen'],
                    confidence_modifier=1.0
                ),
            ],

            # German/Swiss German patterns
            'de': [
                MultilingualPattern(
                    language='de',
                    pattern=r'\b(chinesisch|China)\s+(Unternehmen|Firma|Lieferant|Auftragnehmer)\b',
                    context_keywords=['Vertrag', 'Vereinbarung', 'Beschaffung', 'Technologie'],
                    false_positive_indicators=['Porzellan'],
                    confidence_modifier=1.0
                ),
            ],

            # Balkan languages - Serbian/Croatian/Bosnian
            'sr': [
                MultilingualPattern(
                    language='sr',
                    pattern=r'\b(kinesk|Kina)\s+(kompanija|preduzeće|dobavljač|izvođač)\b',
                    context_keywords=['ugovor', 'sporazum', 'nabavka', 'tehnologija'],
                    false_positive_indicators=['porcelan'],
                    confidence_modifier=1.0
                ),
            ],

            # Albanian
            'sq': [
                MultilingualPattern(
                    language='sq',
                    pattern=r'\b(kinez|Kina)\s+(kompani|ndërmarrje|furnizues|kontraktor)\b',
                    context_keywords=['kontratë', 'marrëveshje', 'prokurim', 'teknologji'],
                    false_positive_indicators=[],
                    confidence_modifier=1.0
                ),
            ],

            # Macedonian
            'mk': [
                MultilingualPattern(
                    language='mk',
                    pattern=r'\b(кинеск|Кина)\s+(компанија|претпријатие|добавувач|изведувач)\b',
                    context_keywords=['договор', 'набавка', 'технологија'],
                    false_positive_indicators=[],
                    confidence_modifier=1.0
                ),
            ],

            # Armenian
            'hy': [
                MultilingualPattern(
                    language='hy',
                    pattern=r'\b(չինական|Չինաստան)\s+(ընկերություն|մատակարար|կապալառու)\b',
                    context_keywords=['պայմանագիր', 'համաձայնագիր', 'գնումներ', 'տեխնոլոգիա'],
                    false_positive_indicators=[],
                    confidence_modifier=1.0
                ),
            ],

            # Georgian
            'ka': [
                MultilingualPattern(
                    language='ka',
                    pattern=r'\b(ჩინური|ჩინეთი)\s+(კომპანია|მომწოდებელი|კონტრაქტორი)\b',
                    context_keywords=['კონტრაქტი', 'შეთანხმება', 'შესყიდვა', 'ტექნოლოგია'],
                    false_positive_indicators=[],
                    confidence_modifier=1.0
                ),
            ],

            # Azerbaijani
            'az': [
                MultilingualPattern(
                    language='az',
                    pattern=r'\b(Çin|Çinli)\s+(şirkət|təchizatçı|podratçı)\b',
                    context_keywords=['müqavilə', 'razılaşma', 'satınalma', 'texnologiya'],
                    false_positive_indicators=[],
                    confidence_modifier=1.0
                ),
            ],

            # Turkish
            'tr': [
                MultilingualPattern(
                    language='tr',
                    pattern=r'\b(Çin|Çinli)\s+(şirket|firma|tedarikçi|yüklenici)\b',
                    context_keywords=['sözleşme', 'anlaşma', 'alım', 'teknoloji'],
                    false_positive_indicators=[],
                    confidence_modifier=1.0
                ),
            ],

            # Icelandic
            'is': [
                MultilingualPattern(
                    language='is',
                    pattern=r'\b(kínverskur|Kína)\s+(fyrirtæki|birgi|verktaki)\b',
                    context_keywords=['samningur', 'innkaup', 'tækni'],
                    false_positive_indicators=[],
                    confidence_modifier=1.0
                ),
            ],
        }

        return patterns

    def _load_china_indicators(self) -> Dict[str, List[str]]:
        """Load Chinese entity indicators by country"""

        indicators = {
            'company_suffixes': [
                'Ltd', 'Limited', 'Co.', 'Corporation', 'Corp',
                'Group', 'Holdings', 'Enterprises',
                'GmbH', 'AG', 'AS', 'AB', 'Oy', 'SA', 'SPA',
                'DOO', 'AD', 'OOD', 'Sh.p.k', 'LLC', 'JSC'
            ],

            'chinese_locations': [
                'Beijing', 'Shanghai', 'Shenzhen', 'Guangzhou', 'Hong Kong',
                'Chongqing', 'Tianjin', 'Wuhan', 'Chengdu', 'Nanjing',
                'Hangzhou', 'Xiamen', 'Dalian', 'Qingdao', 'Suzhou'
            ],

            'technology_keywords': [
                '5G', 'telecommunications', 'telecom', 'network', 'infrastructure',
                'AI', 'artificial intelligence', 'machine learning',
                'quantum', 'semiconductor', 'chips',
                'surveillance', 'camera', 'CCTV',
                'solar', 'battery', 'EV', 'electric vehicle',
                'drone', 'UAV', 'robotics'
            ],

            'bri_keywords': [
                'Belt and Road', 'BRI', 'One Belt One Road',
                'Silk Road', 'infrastructure', 'port', 'railway',
                'investment', 'development', 'cooperation'
            ]
        }

        return indicators

    def validate_china_involvement(
        self,
        text: str,
        country_code: str,
        document_metadata: Dict
    ) -> Dict:
        """
        Validate Chinese involvement in expanded geographic scope

        Args:
            text: Document text to analyze
            country_code: ISO country code
            document_metadata: Additional context

        Returns:
            Validation result with confidence scoring
        """

        result = {
            'country_code': country_code,
            'china_detected': False,
            'confidence': 0.0,
            'matches': [],
            'languages_detected': [],
            'false_positive_risk': 'low',
            'validation_timestamp': datetime.now().isoformat()
        }

        # Get geographic context
        if country_code not in self.geographic_contexts:
            result['error'] = f"Unknown country code: {country_code}"
            return result

        geo_context = self.geographic_contexts[country_code]
        result['country_name'] = geo_context.country_name
        result['special_status'] = geo_context.special_status

        # Check patterns for each language in country
        for language in geo_context.languages:
            if language in self.multilingual_patterns:
                language_matches = self._check_language_patterns(
                    text, language, self.multilingual_patterns[language]
                )

                if language_matches:
                    result['matches'].extend(language_matches)
                    result['languages_detected'].append(language)

        # Check for specific Chinese company names (language-independent)
        company_matches = self._check_company_names(text)
        if company_matches:
            result['matches'].extend(company_matches)

        # Check for Chinese locations
        location_matches = self._check_chinese_locations(text)
        if location_matches:
            result['matches'].extend(location_matches)

        # Calculate confidence score
        if result['matches']:
            result['china_detected'] = True
            result['confidence'] = self._calculate_confidence(result['matches'])

            # Assess false positive risk
            result['false_positive_risk'] = self._assess_false_positive_risk(
                text, result['matches']
            )

        return result

    def _check_language_patterns(
        self,
        text: str,
        language: str,
        patterns: List[MultilingualPattern]
    ) -> List[Dict]:
        """Check text against language-specific patterns"""

        matches = []

        for pattern_obj in patterns:
            regex_matches = re.finditer(pattern_obj.pattern, text, re.IGNORECASE)

            for match in regex_matches:
                # Check for false positive indicators
                is_false_positive = any(
                    fp in text.lower()
                    for fp in pattern_obj.false_positive_indicators
                )

                if not is_false_positive:
                    # Check for context keywords
                    context_score = sum(
                        1 for keyword in pattern_obj.context_keywords
                        if keyword.lower() in text.lower()
                    ) / max(1, len(pattern_obj.context_keywords))

                    matches.append({
                        'text': match.group(),
                        'language': language,
                        'position': match.span(),
                        'pattern': pattern_obj.pattern,
                        'context_score': context_score,
                        'confidence_modifier': pattern_obj.confidence_modifier
                    })

        return matches

    def _check_company_names(self, text: str) -> List[Dict]:
        """Check for known Chinese company names"""

        known_companies = [
            'Huawei', 'ZTE', 'SMIC', 'CNOOC', 'Sinopec', 'CNPC', 'PetroChina',
            'Xiaomi', 'BYD', 'CATL', 'Hikvision', 'Dahua', 'Alibaba', 'Tencent',
            'Baidu', 'China Mobile', 'China Telecom', 'China Unicom',
            'CRRC', 'COMAC', 'AVIC', 'Norinco', 'CETC', 'CASC', 'CASIC'
        ]

        matches = []

        for company in known_companies:
            if re.search(rf'\b{company}\b', text, re.IGNORECASE):
                matches.append({
                    'text': company,
                    'type': 'known_company',
                    'confidence_modifier': 1.5
                })

        return matches

    def _check_chinese_locations(self, text: str) -> List[Dict]:
        """Check for Chinese city/location mentions"""

        matches = []

        for location in self.china_indicators['chinese_locations']:
            if re.search(rf'\b{location}\b', text, re.IGNORECASE):
                matches.append({
                    'text': location,
                    'type': 'chinese_location',
                    'confidence_modifier': 1.1
                })

        return matches

    def _calculate_confidence(self, matches: List[Dict]) -> float:
        """Calculate overall confidence score"""

        if not matches:
            return 0.0

        base_confidence = min(1.0, len(matches) * 0.2)

        # Apply modifiers
        modifiers = [m.get('confidence_modifier', 1.0) for m in matches]
        avg_modifier = sum(modifiers) / len(modifiers)

        # Apply context scores if available
        context_scores = [
            m.get('context_score', 0.5) for m in matches
            if 'context_score' in m
        ]
        avg_context = sum(context_scores) / len(context_scores) if context_scores else 0.5

        final_confidence = base_confidence * avg_modifier * (0.5 + 0.5 * avg_context)

        return min(1.0, final_confidence)

    def _assess_false_positive_risk(self, text: str, matches: List[Dict]) -> str:
        """Assess false positive risk"""

        # Low risk if multiple different types of matches
        match_types = set(m.get('type', 'pattern') for m in matches)
        if len(match_types) >= 2:
            return 'low'

        # High risk if only generic terms without context
        has_context = any(m.get('context_score', 0) > 0.3 for m in matches)
        if not has_context:
            return 'high'

        # Medium risk otherwise
        return 'medium'

def test_expanded_validator():
    """Test validation across expanded countries"""

    validator = ExpandedGeographicValidator()

    test_cases = [
        {
            'country': 'GB',
            'text': 'Huawei Technologies UK provided 5G telecommunications equipment under contract reference GB-2023-5678.'
        },
        {
            'country': 'NO',
            'text': 'Kinesisk selskap levert teknologi for infrastruktur prosjekt i Norge.'
        },
        {
            'country': 'CH',
            'text': 'Chinesisches Unternehmen ZTE lieferte Netzwerk-Infrastruktur für Schweizer Telekom.'
        },
        {
            'country': 'RS',
            'text': 'Kineska kompanija CRRC isporučila voz za Beograd metro projekat.'
        },
        {
            'country': 'AM',
            'text': 'Չինական ընկերություն Huawei մատակարարել տեխնոլոգիա հեռահաղորդակցության համար։'
        },
        {
            'country': 'TR',
            'text': 'Çinli şirket BYD elektrikli otobüs tedarik sözleşmesi imzaladı.'
        },
    ]

    print("Testing Expanded Geographic Validator")
    print("=" * 70)

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['country']}")
        result = validator.validate_china_involvement(
            test['text'],
            test['country'],
            {}
        )

        print(f"  Country: {result.get('country_name')} ({result['country_code']})")
        print(f"  Special Status: {result.get('special_status', 'None')}")
        print(f"  China Detected: {result['china_detected']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Languages: {result['languages_detected']}")
        print(f"  Matches: {len(result['matches'])}")
        print(f"  False Positive Risk: {result['false_positive_risk']}")

if __name__ == "__main__":
    test_expanded_validator()