#!/usr/bin/env python3
"""
Enhanced Pattern Matcher with False Positive Prevention
Addresses the NIO substring matching incident and similar issues
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from collections import Counter

try:
    from .entity_validator import EntityValidator
except ImportError:
    from entity_validator import EntityValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MatchResult:
    """Structured result for pattern matches"""
    entity: str
    text_snippet: str
    start_pos: int
    end_pos: int
    confidence: float
    validation_status: str
    context: Dict[str, Any]
    issues: List[str] = None

    def __post_init__(self):
        if self.issues is None:
            self.issues = []

class EnhancedPatternMatcher:
    """
    Enhanced pattern matcher with multiple validation layers
    Designed to prevent false positive incidents like NIO
    """

    def __init__(self):
        self.entity_validator = EntityValidator()

        # Matching strategies by entity type
        self.matching_strategies = {
            'default': self._word_boundary_match,
            'short_names': self._enhanced_short_name_match,  # For 2-3 letter entities
            'common_words': self._strict_context_match       # For entities that might be common words
        }

        # Classification of entities by risk level
        self.entity_classifications = {
            'nio': 'high_risk',      # Known to cause false positives
            'boe': 'high_risk',      # Short name, common letters
            'tcl': 'high_risk',      # Common in tech contexts
            'byd': 'medium_risk',    # Possible false positives
            'huawei': 'low_risk',    # Distinctive name
            'xiaomi': 'low_risk',    # Distinctive name
            'hikvision': 'low_risk'  # Long, distinctive name
        }

        # Statistics tracking
        self.match_statistics = {
            'total_attempted': 0,
            'raw_matches': 0,
            'validated_matches': 0,
            'false_positives_caught': 0,
            'statistical_anomalies': 0
        }

    def find_chinese_companies(self, text: str, context: Dict[str, Any] = None) -> List[MatchResult]:
        """
        Find Chinese companies in text with comprehensive validation

        Args:
            text: Text to search
            context: Additional context (date, country, etc.)

        Returns:
            List of validated matches
        """
        if context is None:
            context = {}

        matches = []
        self.match_statistics['total_attempted'] += 1

        # Get list of entities to search for
        entities = list(self.entity_validator.chinese_companies.keys())

        for entity in entities:
            entity_matches = self._find_entity_matches(entity, text, context)
            matches.extend(entity_matches)

        # Statistical validation
        match_counts = Counter(match.entity for match in matches)
        anomalies = self.entity_validator.detect_statistical_anomalies(match_counts)

        if anomalies:
            self.match_statistics['statistical_anomalies'] += 1
            logger.warning(f"Statistical anomalies detected: {len(anomalies)} issues")

            # Filter out matches from anomalous entities
            anomalous_entities = {a['entity'] for a in anomalies if a['severity'] == 'critical'}

            original_count = len(matches)
            matches = [m for m in matches if m.entity not in anomalous_entities]

            if original_count > len(matches):
                logger.warning(f"Filtered {original_count - len(matches)} matches from anomalous entities")

        self.match_statistics['validated_matches'] = len(matches)
        return matches

    def _find_entity_matches(self, entity: str, text: str, context: Dict[str, Any]) -> List[MatchResult]:
        """Find all matches for a specific entity"""

        matches = []

        # Choose matching strategy based on entity classification
        risk_level = self.entity_classifications.get(entity, 'medium_risk')

        if risk_level == 'high_risk':
            strategy = self.matching_strategies['common_words']
        elif len(entity) <= 3:
            strategy = self.matching_strategies['short_names']
        else:
            strategy = self.matching_strategies['default']

        # Find raw matches
        raw_matches = strategy(entity, text)
        self.match_statistics['raw_matches'] += len(raw_matches)

        for match_info in raw_matches:
            start, end, snippet = match_info

            # Create context for this specific match
            match_context = context.copy()
            match_context.update({
                'match_position': (start, end),
                'surrounding_text': self._extract_surrounding_text(text, start, end)
            })

            # Validate the match
            validation = self.entity_validator.validate_entity_match(
                entity, snippet, match_context
            )

            # Create match result
            match_result = MatchResult(
                entity=entity,
                text_snippet=snippet,
                start_pos=start,
                end_pos=end,
                confidence=validation['confidence'],
                validation_status='valid' if validation['valid'] else 'invalid',
                context=match_context,
                issues=validation.get('issues', [])
            )

            if validation['valid']:
                matches.append(match_result)
            else:
                self.match_statistics['false_positives_caught'] += 1
                logger.debug(f"False positive caught: {entity} in '{snippet}' - {validation['issues']}")

        return matches

    def _word_boundary_match(self, entity: str, text: str) -> List[Tuple[int, int, str]]:
        """Standard word boundary matching"""

        pattern = r'\b' + re.escape(entity) + r'\b'
        matches = []

        for match in re.finditer(pattern, text, re.IGNORECASE):
            start, end = match.span()
            snippet = text[max(0, start-20):min(len(text), end+20)]
            matches.append((start, end, snippet))

        return matches

    def _enhanced_short_name_match(self, entity: str, text: str) -> List[Tuple[int, int, str]]:
        """Enhanced matching for short entity names (2-3 characters)"""

        matches = []

        # More restrictive pattern for short names
        # Must be surrounded by non-alphanumeric characters or specific contexts
        pattern = r'(?:^|\s|[^\w])(' + re.escape(entity) + r')(?=\s|[^\w]|$)'

        for match in re.finditer(pattern, text, re.IGNORECASE):
            # Get the actual entity match (group 1)
            entity_start = match.start(1)
            entity_end = match.end(1)

            # Check additional context requirements for short names
            context_valid = self._validate_short_name_context(entity, text, entity_start, entity_end)

            if context_valid:
                snippet = text[max(0, entity_start-30):min(len(text), entity_end+30)]
                matches.append((entity_start, entity_end, snippet))

        return matches

    def _strict_context_match(self, entity: str, text: str) -> List[Tuple[int, int, str]]:
        """Strict matching for entities prone to false positives"""

        matches = []

        # Start with word boundary matches
        word_matches = self._word_boundary_match(entity, text)

        for start, end, snippet in word_matches:
            # Additional validation for high-risk entities
            if self._validate_high_risk_context(entity, snippet):
                matches.append((start, end, snippet))

        return matches

    def _validate_short_name_context(self, entity: str, text: str, start: int, end: int) -> bool:
        """Additional validation for short entity names"""

        # Extract broader context
        context_start = max(0, start - 50)
        context_end = min(len(text), end + 50)
        context = text[context_start:context_end].lower()

        # Check for business context indicators
        business_indicators = [
            'company', 'corporation', 'ltd', 'inc', 'gmbh', 'spa',
            'contract', 'supplier', 'vendor', 'manufacturer',
            'technology', 'systems', 'solutions', 'services'
        ]

        for indicator in business_indicators:
            if indicator in context:
                return True

        # Check if it's likely a proper noun (capitalized in original text)
        original_match = text[start:end]
        if original_match.isupper() or original_match[0].isupper():
            return True

        return False

    def _validate_high_risk_context(self, entity: str, snippet: str) -> bool:
        """Validate context for high-risk entities (like NIO)"""

        snippet_lower = snippet.lower()

        # Known false positive patterns for specific entities
        false_positive_patterns = {
            'nio': ['antonio', 'matrimonio', 'patrimonio', 'convenio', 'millennio', 'dominio'],
            'boe': ['facebook', 'somebody', 'anybody'],
            'tcl': ['tcl_script', 'tcl/tk']
        }

        if entity in false_positive_patterns:
            for pattern in false_positive_patterns[entity]:
                if pattern in snippet_lower:
                    return False

        # Require business context for high-risk entities
        business_context = [
            'electric vehicle', 'car', 'automotive', 'ev', 'battery',
            'company', 'corporation', 'technology', 'systems',
            'contract', 'procurement', 'supplier', 'manufacturer'
        ]

        for context_term in business_context:
            if context_term in snippet_lower:
                return True

        # If no business context found for high-risk entity, likely false positive
        return False

    def _extract_surrounding_text(self, text: str, start: int, end: int,
                                window: int = 100) -> str:
        """Extract surrounding text for context analysis"""

        context_start = max(0, start - window)
        context_end = min(len(text), end + window)

        return text[context_start:context_end]

    def validate_batch_results(self, results: List[MatchResult],
                             sample_rate: float = 0.1) -> Dict[str, Any]:
        """Validate batch results with statistical analysis"""

        validation_result = {
            'total_matches': len(results),
            'entities_found': len(set(r.entity for r in results)),
            'confidence_stats': {},
            'anomalies': [],
            'recommendations': [],
            'quality_score': 0.0
        }

        if not results:
            return validation_result

        # Entity distribution analysis
        entity_counts = Counter(r.entity for r in results)

        # Statistical anomaly detection
        anomalies = self.entity_validator.detect_statistical_anomalies(entity_counts)
        validation_result['anomalies'] = anomalies

        # Confidence distribution
        confidences = [r.confidence for r in results]
        validation_result['confidence_stats'] = {
            'mean': sum(confidences) / len(confidences),
            'min': min(confidences),
            'max': max(confidences),
            'low_confidence_count': len([c for c in confidences if c < 0.7])
        }

        # Quality scoring
        quality_factors = {
            'no_critical_anomalies': 0.4 if not any(a['severity'] == 'critical' for a in anomalies) else 0.0,
            'entity_diversity': min(0.3, len(set(r.entity for r in results)) / 10),
            'high_confidence': min(0.3, len([c for c in confidences if c >= 0.8]) / len(confidences))
        }

        validation_result['quality_score'] = sum(quality_factors.values())

        # Generate recommendations
        if anomalies:
            validation_result['recommendations'].append(
                "Statistical anomalies detected - review pattern matching logic"
            )

        if validation_result['confidence_stats']['mean'] < 0.6:
            validation_result['recommendations'].append(
                "Low average confidence - consider stricter validation"
            )

        high_volume_entity = max(entity_counts, key=entity_counts.get)
        if entity_counts[high_volume_entity] / len(results) > 0.5:
            validation_result['recommendations'].append(
                f"High concentration in {high_volume_entity} - possible false positive pattern"
            )

        return validation_result

    def generate_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality report"""

        report = {
            'generated': datetime.now().isoformat(),
            'statistics': self.match_statistics.copy(),
            'false_positive_rate': 0.0,
            'validation_effectiveness': 0.0,
            'recommendations': []
        }

        # Calculate rates
        if self.match_statistics['raw_matches'] > 0:
            fp_rate = self.match_statistics['false_positives_caught'] / self.match_statistics['raw_matches']
            report['false_positive_rate'] = fp_rate

            validation_effectiveness = 1.0 - (self.match_statistics['false_positives_caught'] /
                                            max(1, self.match_statistics['raw_matches']))
            report['validation_effectiveness'] = validation_effectiveness

        # Generate recommendations based on statistics
        if report['false_positive_rate'] > 0.1:
            report['recommendations'].append(
                "High false positive rate - review entity classification and patterns"
            )

        if self.match_statistics['statistical_anomalies'] > 0:
            report['recommendations'].append(
                "Statistical anomalies detected in processing - investigate data quality"
            )

        # Entity validator report
        ev_report = self.entity_validator.generate_qa_report()
        report['entity_validation'] = ev_report

        return report


def test_enhanced_pattern_matcher():
    """Test the enhanced pattern matcher with false positive cases"""

    matcher = EnhancedPatternMatcher()

    print("Testing Enhanced Pattern Matcher")
    print("=" * 70)

    # Test Case 1: NIO false positive prevention
    print("\nTest 1: NIO False Positive Prevention")
    false_positive_text = """
    Il patrimonio culturale dell'unione europea include numerosi siti.
    Antonio Merloni ha firmato un convenio per il millennio.
    La cerimonia matrimoniale ha avuto luogo nel dominio pubblico.
    """

    matches = matcher.find_chinese_companies(false_positive_text)
    print(f"  Text contains multiple 'nio' substrings")
    print(f"  Matches found: {len(matches)}")
    for match in matches:
        print(f"    {match.entity}: {match.validation_status} (confidence: {match.confidence:.2f})")

    # Test Case 2: Legitimate company matches
    print("\nTest 2: Legitimate Company Matches")
    legitimate_text = """
    Huawei Technologies provided telecommunications equipment.
    ZTE Corporation delivered network infrastructure.
    Xiaomi smartphone procurement contract signed.
    """

    matches = matcher.find_chinese_companies(legitimate_text, {
        'contract_date': '2020-01-01',
        'contract_country': 'DE'
    })
    print(f"  Matches found: {len(matches)}")
    for match in matches:
        print(f"    {match.entity}: {match.validation_status} (confidence: {match.confidence:.2f})")

    # Test Case 3: Statistical anomaly detection
    print("\nTest 3: Statistical Anomaly Detection")

    # Simulate the NIO false positive incident
    fake_results = []
    for i in range(182008):
        fake_results.append(MatchResult(
            entity='nio', text_snippet=f'antonio_{i}', start_pos=0, end_pos=3,
            confidence=0.3, validation_status='suspicious', context={}
        ))

    for i in range(3701):
        fake_results.append(MatchResult(
            entity='zte', text_snippet=f'zte_{i}', start_pos=0, end_pos=3,
            confidence=0.8, validation_status='valid', context={}
        ))

    validation = matcher.validate_batch_results(fake_results)
    print(f"  Total matches: {validation['total_matches']}")
    print(f"  Quality score: {validation['quality_score']:.2f}")
    print(f"  Anomalies: {len(validation['anomalies'])}")
    for anomaly in validation['anomalies']:
        print(f"    {anomaly['type']}: {anomaly['message']}")

    # Test Case 4: Quality report generation
    print("\nTest 4: Quality Report")
    report = matcher.generate_quality_report()
    print(f"  False positive rate: {report['false_positive_rate']:.1%}")
    print(f"  Recommendations: {len(report['recommendations'])}")
    for rec in report['recommendations']:
        print(f"    - {rec}")

    return matcher

if __name__ == "__main__":
    test_enhanced_pattern_matcher()
