#!/usr/bin/env python3
"""
Entity Validation Framework
Prevents false positives like the NIO substring matching incident
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, date
from pathlib import Path
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CompanyInfo:
    """Company information for validation"""
    name: str
    founded_date: date
    operating_countries: List[str]
    business_type: str
    verified: bool = False
    aliases: List[str] = None

    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []

class EntityValidator:
    """
    Validates entity matches to prevent false positives like the NIO incident

    The NIO incident: 182,008 false matches because "nio" substring matched
    Italian/Latin words like unio→u[nio], senio→se[nio], Antonio→Anto[nio]
    """

    def __init__(self):
        # Known Chinese companies with validation data
        self.chinese_companies = self._load_chinese_companies()

        # Linguistic patterns that cause false positives
        self.false_positive_patterns = self._load_false_positive_patterns()

        # Statistical thresholds for anomaly detection
        self.anomaly_thresholds = {
            'max_concentration': 0.50,  # >50% concentration triggers review
            'min_entities': 3,          # Need at least 3 different entities
            'max_growth_rate': 5.0      # >500% year-over-year growth
        }

        # Validation results tracking
        self.validation_log = []
        self.false_positives_caught = []

    def _load_chinese_companies(self) -> Dict[str, CompanyInfo]:
        """Load verified Chinese company database"""

        companies = {
            'huawei': CompanyInfo(
                name='Huawei Technologies Co., Ltd.',
                founded_date=date(1987, 1, 1),
                operating_countries=['CN', 'DE', 'UK', 'FR', 'IT', 'ES'],
                business_type='telecommunications'
            ),
            'zte': CompanyInfo(
                name='ZTE Corporation',
                founded_date=date(1985, 1, 1),
                operating_countries=['CN', 'DE', 'UK', 'FR', 'IT'],
                business_type='telecommunications'
            ),
            'nio': CompanyInfo(
                name='NIO Inc.',
                founded_date=date(2014, 11, 25),  # Founded 2014
                operating_countries=['CN', 'NO'],  # Minimal EU presence
                business_type='automotive',
                aliases=['蔚来', 'NextEV']
            ),
            'byd': CompanyInfo(
                name='BYD Company Limited',
                founded_date=date(1995, 2, 10),
                operating_countries=['CN', 'DE', 'UK', 'FR', 'NL'],
                business_type='automotive'
            ),
            'oppo': CompanyInfo(
                name='OPPO Digital Inc.',
                founded_date=date(2004, 1, 1),
                operating_countries=['CN', 'DE', 'UK', 'FR', 'IT', 'ES'],
                business_type='electronics'
            ),
            'vivo': CompanyInfo(
                name='Vivo Communication Technology Co. Ltd.',
                founded_date=date(2009, 1, 1),
                operating_countries=['CN', 'DE', 'UK', 'FR', 'IT'],
                business_type='electronics'
            ),
            'xiaomi': CompanyInfo(
                name='Xiaomi Corporation',
                founded_date=date(2010, 4, 6),
                operating_countries=['CN', 'DE', 'UK', 'FR', 'IT', 'ES'],
                business_type='electronics'
            ),
            'tcl': CompanyInfo(
                name='TCL Technology Group Corporation',
                founded_date=date(1981, 1, 1),
                operating_countries=['CN', 'DE', 'UK', 'FR', 'IT'],
                business_type='electronics'
            ),
            'boe': CompanyInfo(
                name='BOE Technology Group Co., Ltd.',
                founded_date=date(1993, 4, 9),
                operating_countries=['CN', 'DE', 'UK'],
                business_type='displays'
            ),
            'lenovo': CompanyInfo(
                name='Lenovo Group Limited',
                founded_date=date(1984, 11, 1),
                operating_countries=['CN', 'DE', 'UK', 'FR', 'IT', 'ES'],
                business_type='computers'
            ),
            'hikvision': CompanyInfo(
                name='Hangzhou Hikvision Digital Technology Co., Ltd.',
                founded_date=date(2001, 11, 30),
                operating_countries=['CN', 'DE', 'UK', 'IT'],
                business_type='security'
            ),
            'dahua': CompanyInfo(
                name='Dahua Technology Co., Ltd.',
                founded_date=date(2001, 1, 1),
                operating_countries=['CN', 'DE', 'UK', 'IT'],
                business_type='security'
            )
        }

        return companies

    def _load_false_positive_patterns(self) -> Dict[str, List[str]]:
        """Patterns that commonly cause false positives"""

        return {
            'nio': [
                # Italian/Latin words containing "nio"
                'unio', 'senio', 'opinio', 'millennio', 'antonio', 'convenio',
                'patrimonio', 'cerimoniale', 'testimonial', 'matrimonio',
                'demonio', 'dominio', 'genio', 'ionico', 'pioniere'
            ],
            'zte': [
                # Words ending in "zte"
                'katze', 'hetze', 'setze', 'platze', 'glotze'
            ],
            'boe': [
                # Common three-letter combinations
                'facebook', 'somebody', 'anybody', 'emboe'
            ],
            'tcl': [
                # Programming/technical terms
                'tcl_script', 'tcl/tk', 'tcl_proc'
            ]
        }

    def validate_entity_match(self, entity_name: str, text: str,
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate an entity match to prevent false positives

        Args:
            entity_name: The entity being searched for (e.g., 'nio')
            text: The text where the match was found
            context: Additional context (contract_date, country, etc.)

        Returns:
            Validation result with confidence score and reasons
        """

        result = {
            'entity': entity_name,
            'valid': False,
            'confidence': 0.0,
            'match_type': 'unknown',
            'issues': [],
            'warnings': [],
            'context_analysis': {}
        }

        # Step 1: Word boundary validation
        word_boundary_valid = self._check_word_boundaries(entity_name, text)
        if not word_boundary_valid:
            result['issues'].append("Failed word boundary check - likely substring match")
            result['match_type'] = 'substring_false_positive'
            return result

        # Step 2: Company existence validation
        if entity_name not in self.chinese_companies:
            result['issues'].append(f"Unknown entity: {entity_name}")
            return result

        company_info = self.chinese_companies[entity_name]

        # Step 3: Temporal validation
        temporal_valid = self._check_temporal_consistency(company_info, context)
        if not temporal_valid['valid']:
            result['issues'].extend(temporal_valid['issues'])
            result['warnings'].extend(temporal_valid['warnings'])

        # Step 4: Geographic validation
        geographic_valid = self._check_geographic_consistency(company_info, context)
        if not geographic_valid['valid']:
            result['warnings'].extend(geographic_valid['warnings'])

        # Step 5: Context validation
        context_valid = self._check_context_relevance(entity_name, text, company_info)
        result['context_analysis'] = context_valid

        # Step 6: False positive pattern check
        fp_check = self._check_false_positive_patterns(entity_name, text)
        if fp_check['likely_false_positive']:
            result['issues'].append(f"Matches false positive pattern: {fp_check['pattern']}")
            result['match_type'] = 'linguistic_false_positive'
            return result

        # Calculate confidence score
        confidence_factors = {
            'word_boundary': 0.3 if word_boundary_valid else 0.0,
            'temporal': temporal_valid.get('confidence', 0.0) * 0.2,
            'geographic': geographic_valid.get('confidence', 0.5) * 0.1,
            'context': context_valid.get('confidence', 0.5) * 0.3,
            'no_false_positive': 0.1 if not fp_check['likely_false_positive'] else 0.0
        }

        result['confidence'] = sum(confidence_factors.values())
        result['valid'] = result['confidence'] >= 0.7 and len(result['issues']) == 0
        result['match_type'] = 'validated_entity' if result['valid'] else 'uncertain'

        # Log validation
        self.validation_log.append(result)

        if not result['valid']:
            self.false_positives_caught.append(result)
            logger.warning(f"Potential false positive: {entity_name} in context")

        return result

    def _check_word_boundaries(self, entity_name: str, text: str) -> bool:
        """Check if match respects word boundaries (fixes NIO substring issue)"""

        # Create pattern with word boundaries
        pattern = r'\b' + re.escape(entity_name.lower()) + r'\b'

        # Check if the match is a complete word
        matches = re.finditer(pattern, text.lower())

        for match in matches:
            # Additional validation: check surrounding characters
            start, end = match.span()

            # Get surrounding context
            context_start = max(0, start - 10)
            context_end = min(len(text), end + 10)
            surrounding = text[context_start:context_end].lower()

            # Check if it's part of a larger word (additional safety)
            if start > 0 and text[start-1].isalpha():
                continue
            if end < len(text) and text[end].isalpha():
                continue

            return True

        return False

    def _check_temporal_consistency(self, company_info: CompanyInfo,
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if the match is temporally consistent"""

        result = {'valid': True, 'confidence': 1.0, 'issues': [], 'warnings': []}

        if 'contract_date' in context:
            contract_date = context['contract_date']
            if isinstance(contract_date, str):
                contract_date = datetime.strptime(contract_date[:10], '%Y-%m-%d').date()

            # Check if contract predates company founding
            if contract_date < company_info.founded_date:
                result['valid'] = False
                result['confidence'] = 0.0
                result['issues'].append(
                    f"Contract date {contract_date} predates company founding {company_info.founded_date}"
                )

            # Check if it's very early in company lifecycle
            elif (contract_date - company_info.founded_date).days < 365:
                result['warnings'].append(
                    f"Contract within first year of company existence"
                )
                result['confidence'] = 0.6

        return result

    def _check_geographic_consistency(self, company_info: CompanyInfo,
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if the company operates in the contract country"""

        result = {'valid': True, 'confidence': 1.0, 'warnings': []}

        if 'contract_country' in context:
            country = context['contract_country']

            if country not in company_info.operating_countries:
                result['valid'] = False
                result['confidence'] = 0.3
                result['warnings'].append(
                    f"Company not known to operate in {country}"
                )

        return result

    def _check_context_relevance(self, entity_name: str, text: str,
                               company_info: CompanyInfo) -> Dict[str, Any]:
        """Check if the context is relevant to the company's business"""

        result = {'confidence': 0.5, 'relevant_terms': [], 'business_match': False}

        # Business type keywords
        business_keywords = {
            'telecommunications': ['telecom', 'network', 'infrastructure', 'antenna', '5g', '4g', 'cellular'],
            'automotive': ['vehicle', 'car', 'electric', 'battery', 'charging', 'automotive'],
            'electronics': ['smartphone', 'device', 'consumer', 'electronic', 'mobile'],
            'security': ['surveillance', 'camera', 'security', 'monitoring', 'cctv'],
            'displays': ['display', 'screen', 'monitor', 'panel', 'lcd', 'oled'],
            'computers': ['computer', 'laptop', 'server', 'hardware', 'pc']
        }

        relevant_keywords = business_keywords.get(company_info.business_type, [])

        for keyword in relevant_keywords:
            if keyword in text.lower():
                result['relevant_terms'].append(keyword)

        if result['relevant_terms']:
            result['business_match'] = True
            result['confidence'] = min(1.0, 0.5 + len(result['relevant_terms']) * 0.1)

        return result

    def _check_false_positive_patterns(self, entity_name: str, text: str) -> Dict[str, Any]:
        """Check against known false positive patterns"""

        result = {'likely_false_positive': False, 'pattern': None, 'confidence': 1.0}

        if entity_name in self.false_positive_patterns:
            patterns = self.false_positive_patterns[entity_name]

            # Extract words containing the entity name
            entity_pattern = r'\b\w*' + re.escape(entity_name) + r'\w*\b'
            matches = re.findall(entity_pattern, text.lower())

            for match in matches:
                if match != entity_name and match in patterns:
                    result['likely_false_positive'] = True
                    result['pattern'] = match
                    result['confidence'] = 0.1
                    break

        return result

    def detect_statistical_anomalies(self, results: Dict[str, int]) -> List[Dict[str, Any]]:
        """Detect statistical anomalies that suggest data quality issues"""

        anomalies = []
        total = sum(results.values())

        if total == 0:
            return anomalies

        # Check concentration (catches NIO-type issues)
        for entity, count in results.items():
            concentration = count / total
            if concentration > self.anomaly_thresholds['max_concentration']:
                anomalies.append({
                    'type': 'extreme_concentration',
                    'entity': entity,
                    'concentration': concentration,
                    'count': count,
                    'message': f"{entity}: {concentration:.1%} concentration - highly suspicious",
                    'severity': 'critical',
                    'likely_cause': 'false_positive_pattern'
                })

        # Check entity diversity
        if len(results) < self.anomaly_thresholds['min_entities'] and total > 1000:
            anomalies.append({
                'type': 'low_diversity',
                'entity_count': len(results),
                'total_matches': total,
                'message': f"Only {len(results)} entities in {total} matches - low diversity",
                'severity': 'high',
                'likely_cause': 'pattern_matching_error'
            })

        # Check for impossible distributions
        sorted_counts = sorted(results.values(), reverse=True)
        if len(sorted_counts) >= 2:
            ratio = sorted_counts[0] / sorted_counts[1] if sorted_counts[1] > 0 else float('inf')
            if ratio > 50:  # Top entity 50x more than second
                anomalies.append({
                    'type': 'extreme_ratio',
                    'top_entity': max(results, key=results.get),
                    'ratio': ratio,
                    'message': f"Top entity {ratio:.0f}x more than second - likely error",
                    'severity': 'critical',
                    'likely_cause': 'substring_matching'
                })

        return anomalies

    def batch_validate(self, matches: List[Dict[str, Any]],
                      sample_rate: float = 0.1) -> Dict[str, Any]:
        """Validate a batch of matches with sampling for large datasets"""

        results = {
            'total_matches': len(matches),
            'validated_sample': 0,
            'valid_matches': 0,
            'false_positives': 0,
            'confidence_distribution': {},
            'anomalies': [],
            'recommendations': []
        }

        # Determine sample size
        sample_size = max(100, int(len(matches) * sample_rate))
        sample_size = min(sample_size, len(matches))

        # Stratified sampling - include high-volume entities
        entity_counts = {}
        for match in matches:
            entity = match.get('entity', 'unknown')
            entity_counts[entity] = entity_counts.get(entity, 0) + 1

        # Check for statistical anomalies first
        anomalies = self.detect_statistical_anomalies(entity_counts)
        results['anomalies'] = anomalies

        # If critical anomalies found, increase sample rate
        if any(a['severity'] == 'critical' for a in anomalies):
            sample_size = min(1000, len(matches))
            results['recommendations'].append("Critical anomalies detected - increased validation sample")

        # Sample validation
        import random
        sample_matches = random.sample(matches, sample_size)

        for match in sample_matches:
            validation = self.validate_entity_match(
                match.get('entity', ''),
                match.get('text', ''),
                match.get('context', {})
            )

            results['validated_sample'] += 1
            if validation['valid']:
                results['valid_matches'] += 1
            else:
                results['false_positives'] += 1

        # Calculate estimates
        if results['validated_sample'] > 0:
            false_positive_rate = results['false_positives'] / results['validated_sample']
            estimated_fp = int(len(matches) * false_positive_rate)

            results['estimated_false_positives'] = estimated_fp
            results['estimated_accuracy'] = 1 - false_positive_rate

            if false_positive_rate > 0.1:  # >10% false positive rate
                results['recommendations'].append(
                    f"High false positive rate ({false_positive_rate:.1%}) - review pattern matching"
                )

        return results

    def generate_qa_report(self) -> Dict[str, Any]:
        """Generate comprehensive QA report"""

        report = {
            'generated': datetime.now().isoformat(),
            'validations_performed': len(self.validation_log),
            'false_positives_caught': len(self.false_positives_caught),
            'false_positive_rate': 0.0,
            'common_fp_patterns': {},
            'recommendations': []
        }

        if self.validation_log:
            fp_rate = len(self.false_positives_caught) / len(self.validation_log)
            report['false_positive_rate'] = fp_rate

            # Analyze common patterns
            fp_patterns = {}
            for fp in self.false_positives_caught:
                entity = fp['entity']
                fp_patterns[entity] = fp_patterns.get(entity, 0) + 1

            report['common_fp_patterns'] = fp_patterns

            # Generate recommendations
            if fp_rate > 0.05:  # >5% false positive rate
                report['recommendations'].append("High false positive rate - review entity matching logic")

            if 'nio' in fp_patterns and fp_patterns['nio'] > 10:
                report['recommendations'].append("NIO showing high false positives - likely substring issue")

        return report


def test_entity_validator():
    """Test the entity validator with known false positive cases"""

    validator = EntityValidator()

    print("Testing Entity Validator")
    print("=" * 60)

    # Test Case 1: NIO false positive (the actual incident)
    print("\nTest 1: NIO False Positive Detection")
    test_text = "Antonio Merloni patrimonio unione europea convenio"
    result = validator.validate_entity_match('nio', test_text, {})
    print(f"  Text: {test_text}")
    print(f"  Valid: {result['valid']}")
    print(f"  Issues: {result['issues']}")

    # Test Case 2: Legitimate NIO match
    print("\nTest 2: Legitimate NIO Match")
    test_text = "NIO electric vehicle procurement for charging infrastructure"
    result = validator.validate_entity_match('nio', test_text, {
        'contract_date': '2020-01-01',
        'contract_country': 'CN'
    })
    print(f"  Text: {test_text}")
    print(f"  Valid: {result['valid']}")
    print(f"  Confidence: {result['confidence']:.2f}")

    # Test Case 3: Temporal inconsistency
    print("\nTest 3: Temporal Inconsistency")
    test_text = "NIO electric vehicle contract"
    result = validator.validate_entity_match('nio', test_text, {
        'contract_date': '2010-01-01'  # Before NIO founded
    })
    print(f"  Date: 2010 (NIO founded 2014)")
    print(f"  Valid: {result['valid']}")
    print(f"  Issues: {result['issues']}")

    # Test Case 4: Statistical anomaly detection
    print("\nTest 4: Statistical Anomaly Detection")
    fake_results = {'nio': 182008, 'huawei': 11, 'zte': 3701}
    anomalies = validator.detect_statistical_anomalies(fake_results)
    print(f"  Results: {fake_results}")
    print(f"  Anomalies detected: {len(anomalies)}")
    for anomaly in anomalies:
        print(f"    {anomaly['type']}: {anomaly['message']}")

    return validator

if __name__ == "__main__":
    test_entity_validator()
