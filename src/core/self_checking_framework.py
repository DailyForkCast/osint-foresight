#!/usr/bin/env python3
"""
Self-Checking Framework
Comprehensive validation and cross-checking system
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime
from pathlib import Path
import hashlib
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Levels of validation stringency"""
    BASIC = "basic"        # Simple range and null checks
    STANDARD = "standard"  # Cross-field validation
    RIGOROUS = "rigorous"  # Multi-source verification
    FORENSIC = "forensic"  # Full audit trail required


class CheckType(Enum):
    """Types of checks to perform"""
    RANGE = "range"              # Value within expected range
    CONSISTENCY = "consistency"  # Internal consistency
    CROSS_SOURCE = "cross_source" # Cross-source agreement
    TEMPORAL = "temporal"        # Temporal consistency
    COMPLETENESS = "completeness" # Data completeness
    EVIDENCE = "evidence"        # Evidence sufficiency


class SelfCheckingFramework:
    """Comprehensive self-checking and validation system"""

    def __init__(self):
        self.validation_rules = self._initialize_rules()
        self.check_results = []
        self.failed_checks = []
        self.audit_trail = []

        # Evidence requirements
        self.evidence_requirements = {
            'minor_claim': 1,     # Single source acceptable
            'standard_claim': 2,  # Two independent sources
            'major_claim': 3,     # Three sources required
            'bombshell': 4        # Four sources or official registry
        }

        # Confidence scoring weights
        self.confidence_weights = {
            'source_agreement': 0.3,
            'evidence_quality': 0.3,
            'temporal_consistency': 0.2,
            'logical_consistency': 0.2
        }

    def _initialize_rules(self) -> Dict:
        """Initialize validation rules"""

        return {
            'value_ranges': {
                'percentage': (0.0, 100.0),
                'rate': (0.0, 1.0),
                'count': (0, float('inf')),
                'year': (1900, 2030),
                'hhi': (0.0, 1.0),
                'confidence': (0.0, 1.0)
            },
            'required_fields': {
                'claim': ['statement', 'evidence', 'confidence', 'source'],
                'entity': ['name', 'id', 'type', 'country'],
                'metric': ['value', 'unit', 'timestamp', 'source']
            },
            'cross_checks': {
                'company_country': ['GLEIF', 'TED', 'CORDIS'],
                'research_output': ['OpenAlex', 'Semantic_Scholar', 'CrossRef'],
                'trade_value': ['Eurostat', 'World_Bank', 'OECD']
            }
        }

    def validate_data(self, data: Dict, data_type: str,
                     level: ValidationLevel = ValidationLevel.STANDARD) -> Dict:
        """Validate data according to specified level"""

        validation_result = {
            'timestamp': datetime.now().isoformat(),
            'data_type': data_type,
            'level': level.value,
            'checks_performed': [],
            'passed': True,
            'issues': [],
            'confidence': 1.0
        }

        # Basic checks (always performed)
        basic_checks = self._perform_basic_checks(data, data_type)
        validation_result['checks_performed'].extend(basic_checks['checks'])
        if not basic_checks['passed']:
            validation_result['passed'] = False
            validation_result['issues'].extend(basic_checks['issues'])
            validation_result['confidence'] *= 0.7

        # Standard checks
        if level.value in ['standard', 'rigorous', 'forensic']:
            standard_checks = self._perform_standard_checks(data, data_type)
            validation_result['checks_performed'].extend(standard_checks['checks'])
            if not standard_checks['passed']:
                validation_result['passed'] = False
                validation_result['issues'].extend(standard_checks['issues'])
                validation_result['confidence'] *= 0.8

        # Rigorous checks
        if level.value in ['rigorous', 'forensic']:
            rigorous_checks = self._perform_rigorous_checks(data, data_type)
            validation_result['checks_performed'].extend(rigorous_checks['checks'])
            if not rigorous_checks['passed']:
                validation_result['passed'] = False
                validation_result['issues'].extend(rigorous_checks['issues'])
                validation_result['confidence'] *= 0.9

        # Forensic checks
        if level == ValidationLevel.FORENSIC:
            forensic_checks = self._perform_forensic_checks(data, data_type)
            validation_result['checks_performed'].extend(forensic_checks['checks'])
            if not forensic_checks['passed']:
                validation_result['passed'] = False
                validation_result['issues'].extend(forensic_checks['issues'])
                validation_result['confidence'] *= 0.95

        # Log result
        self.check_results.append(validation_result)
        if not validation_result['passed']:
            self.failed_checks.append(validation_result)
            logger.warning(f"Validation failed for {data_type}: {validation_result['issues']}")

        return validation_result

    def _perform_basic_checks(self, data: Dict, data_type: str) -> Dict:
        """Perform basic validation checks"""

        result = {
            'checks': [],
            'passed': True,
            'issues': []
        }

        # Null checks
        check_name = 'null_check'
        if self._check_nulls(data):
            result['checks'].append(f"{check_name}: passed")
        else:
            result['passed'] = False
            result['issues'].append('Contains unexpected null values')
            result['checks'].append(f"{check_name}: failed")

        # Range checks
        check_name = 'range_check'
        range_issues = self._check_ranges(data)
        if not range_issues:
            result['checks'].append(f"{check_name}: passed")
        else:
            result['passed'] = False
            result['issues'].extend(range_issues)
            result['checks'].append(f"{check_name}: failed")

        # Required fields
        if data_type in self.validation_rules['required_fields']:
            check_name = 'required_fields'
            missing = self._check_required_fields(data, data_type)
            if not missing:
                result['checks'].append(f"{check_name}: passed")
            else:
                result['passed'] = False
                result['issues'].append(f"Missing required fields: {missing}")
                result['checks'].append(f"{check_name}: failed")

        return result

    def _perform_standard_checks(self, data: Dict, data_type: str) -> Dict:
        """Perform standard validation checks"""

        result = {
            'checks': [],
            'passed': True,
            'issues': []
        }

        # Consistency checks
        check_name = 'consistency'
        consistency_issues = self._check_consistency(data)
        if not consistency_issues:
            result['checks'].append(f"{check_name}: passed")
        else:
            result['passed'] = False
            result['issues'].extend(consistency_issues)
            result['checks'].append(f"{check_name}: failed")

        # Temporal checks
        check_name = 'temporal'
        temporal_issues = self._check_temporal(data)
        if not temporal_issues:
            result['checks'].append(f"{check_name}: passed")
        else:
            result['passed'] = False
            result['issues'].extend(temporal_issues)
            result['checks'].append(f"{check_name}: failed")

        return result

    def _perform_rigorous_checks(self, data: Dict, data_type: str) -> Dict:
        """Perform rigorous validation checks"""

        result = {
            'checks': [],
            'passed': True,
            'issues': []
        }

        # Cross-source validation
        if 'sources' in data and len(data['sources']) > 1:
            check_name = 'cross_source'
            cross_issues = self._check_cross_source(data)
            if not cross_issues:
                result['checks'].append(f"{check_name}: passed")
            else:
                result['passed'] = False
                result['issues'].extend(cross_issues)
                result['checks'].append(f"{check_name}: failed")

        # Evidence sufficiency
        if 'claim_type' in data:
            check_name = 'evidence_sufficiency'
            if self._check_evidence_sufficiency(data):
                result['checks'].append(f"{check_name}: passed")
            else:
                result['passed'] = False
                result['issues'].append('Insufficient evidence for claim type')
                result['checks'].append(f"{check_name}: failed")

        return result

    def _perform_forensic_checks(self, data: Dict, data_type: str) -> Dict:
        """Perform forensic-level validation checks"""

        result = {
            'checks': [],
            'passed': True,
            'issues': []
        }

        # Full audit trail
        check_name = 'audit_trail'
        if self._check_audit_trail(data):
            result['checks'].append(f"{check_name}: passed")
        else:
            result['passed'] = False
            result['issues'].append('Incomplete audit trail')
            result['checks'].append(f"{check_name}: failed")

        # Provenance verification
        check_name = 'provenance'
        if self._check_provenance(data):
            result['checks'].append(f"{check_name}: passed")
        else:
            result['passed'] = False
            result['issues'].append('Cannot verify provenance')
            result['checks'].append(f"{check_name}: failed")

        return result

    def _check_nulls(self, data: Dict) -> bool:
        """Check for unexpected null values"""

        def check_nested(obj, path=""):
            if obj is None:
                return False
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if value is None and key not in ['optional', 'notes', 'metadata']:
                        logger.debug(f"Null found at {path}.{key}")
                        return False
                    if isinstance(value, dict):
                        if not check_nested(value, f"{path}.{key}"):
                            return False
            return True

        return check_nested(data)

    def _check_ranges(self, data: Dict) -> List[str]:
        """Check if values are within expected ranges"""

        issues = []

        def check_nested(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, (int, float)):
                        # Check known range types
                        if 'percentage' in key.lower() or 'percent' in key.lower() or '_pct' in key.lower():
                            if not (0 <= value <= 100):
                                issues.append(f"{path}.{key}={value} outside percentage range [0,100]")
                        elif 'rate' in key.lower() or 'ratio' in key.lower():
                            if not (0 <= value <= 1):
                                issues.append(f"{path}.{key}={value} outside rate range [0,1]")
                        elif 'hhi' in key.lower():
                            if not (0 <= value <= 1):
                                issues.append(f"{path}.{key}={value} outside HHI range [0,1]")
                        elif 'year' in key.lower():
                            if not (1900 <= value <= 2030):
                                issues.append(f"{path}.{key}={value} outside year range [1900,2030]")
                        elif 'confidence' in key.lower() or 'score' in key.lower():
                            if not (0 <= value <= 1):
                                issues.append(f"{path}.{key}={value} outside confidence range [0,1]")
                    elif isinstance(value, dict):
                        check_nested(value, f"{path}.{key}")

        check_nested(data)
        return issues

    def _check_required_fields(self, data: Dict, data_type: str) -> List[str]:
        """Check for required fields"""

        if data_type not in self.validation_rules['required_fields']:
            return []

        required = self.validation_rules['required_fields'][data_type]
        missing = [field for field in required if field not in data or data[field] is None]

        return missing

    def _check_consistency(self, data: Dict) -> List[str]:
        """Check internal consistency"""

        issues = []

        # Check: Total = Sum of components
        if 'total' in data and 'components' in data:
            if isinstance(data['components'], dict):
                calculated = sum(data['components'].values())
                if abs(data['total'] - calculated) > 0.01:
                    issues.append(f"Total {data['total']} != sum of components {calculated}")

        # Check: Percentages sum to 100
        for key in data:
            if 'percentages' in key and isinstance(data[key], dict):
                total = sum(data[key].values())
                if abs(total - 100) > 1:
                    issues.append(f"{key} sum to {total}%, not 100%")

        # Check: Start date < End date
        if 'start_date' in data and 'end_date' in data:
            if data['end_date'] < data['start_date']:
                issues.append("End date before start date")

        # Check: Parent >= Child
        if 'parent_count' in data and 'child_count' in data:
            if data['child_count'] > data['parent_count']:
                issues.append(f"Child count {data['child_count']} > parent count {data['parent_count']}")

        return issues

    def _check_temporal(self, data: Dict) -> List[str]:
        """Check temporal consistency"""

        issues = []

        # Check for anachronistic data
        current_year = datetime.now().year

        if 'year' in data and data['year'] > current_year:
            issues.append(f"Future year {data['year']} > current year {current_year}")

        # Check for suspicious temporal patterns
        if 'time_series' in data:
            ts = data['time_series']
            if isinstance(ts, list) and len(ts) > 1:
                # Check if all values identical
                values = [item.get('value') for item in ts if 'value' in item]
                if len(set(values)) == 1 and len(values) > 5:
                    issues.append("Suspicious: all time series values identical")

        return issues

    def _check_cross_source(self, data: Dict) -> List[str]:
        """Check cross-source agreement"""

        issues = []

        if 'sources' not in data:
            return issues

        sources = data['sources']

        # Check for conflicting values
        if isinstance(sources, dict):
            values = {}
            for source, source_data in sources.items():
                if 'value' in source_data:
                    val = source_data['value']
                    if val not in values:
                        values[val] = []
                    values[val].append(source)

            # If multiple different values
            if len(values) > 1:
                # Calculate variation
                numeric_values = [v for v in values.keys() if isinstance(v, (int, float))]
                if numeric_values:
                    mean_val = sum(numeric_values) / len(numeric_values)
                    max_deviation = max(abs(v - mean_val) / mean_val for v in numeric_values if mean_val != 0)

                    if max_deviation > 0.2:  # >20% deviation
                        issues.append(f"High cross-source disagreement: {max_deviation:.1%} deviation")

        return issues

    def _check_evidence_sufficiency(self, data: Dict) -> bool:
        """Check if evidence is sufficient for claim type"""

        claim_type = data.get('claim_type', 'standard_claim')
        evidence_count = len(data.get('evidence', []))

        required = self.evidence_requirements.get(claim_type, 2)

        return evidence_count >= required

    def _check_audit_trail(self, data: Dict) -> bool:
        """Check for complete audit trail"""

        required_audit_fields = ['timestamp', 'source', 'method', 'version', 'hash']

        if 'audit' not in data:
            return False

        audit = data['audit']

        return all(field in audit for field in required_audit_fields)

    def _check_provenance(self, data: Dict) -> bool:
        """Check data provenance"""

        if 'provenance' not in data:
            return False

        prov = data['provenance']

        required = ['source_url', 'capture_time', 'capture_method', 'integrity_hash']

        return all(field in prov for field in required)

    def calculate_confidence(self, data: Dict) -> float:
        """Calculate confidence score for data"""

        confidence_factors = {
            'source_agreement': 0.0,
            'evidence_quality': 0.0,
            'temporal_consistency': 0.0,
            'logical_consistency': 0.0
        }

        # Source agreement
        if 'sources' in data:
            source_count = len(data['sources'])
            if source_count >= 3:
                confidence_factors['source_agreement'] = 1.0
            elif source_count == 2:
                confidence_factors['source_agreement'] = 0.7
            elif source_count == 1:
                confidence_factors['source_agreement'] = 0.4

        # Evidence quality
        if 'evidence' in data:
            evidence = data['evidence']
            if isinstance(evidence, list):
                official_sources = sum(1 for e in evidence if e.get('type') == 'official')
                if official_sources >= 2:
                    confidence_factors['evidence_quality'] = 1.0
                elif official_sources == 1:
                    confidence_factors['evidence_quality'] = 0.8
                elif len(evidence) >= 2:
                    confidence_factors['evidence_quality'] = 0.6
                else:
                    confidence_factors['evidence_quality'] = 0.3

        # Temporal consistency
        temporal_issues = self._check_temporal(data)
        if not temporal_issues:
            confidence_factors['temporal_consistency'] = 1.0
        elif len(temporal_issues) == 1:
            confidence_factors['temporal_consistency'] = 0.7
        else:
            confidence_factors['temporal_consistency'] = 0.4

        # Logical consistency
        consistency_issues = self._check_consistency(data)
        if not consistency_issues:
            confidence_factors['logical_consistency'] = 1.0
        elif len(consistency_issues) == 1:
            confidence_factors['logical_consistency'] = 0.7
        else:
            confidence_factors['logical_consistency'] = 0.4

        # Calculate weighted confidence
        total_confidence = sum(
            confidence_factors[factor] * weight
            for factor, weight in self.confidence_weights.items()
        )

        return round(total_confidence, 3)

    def generate_validation_report(self) -> Dict:
        """Generate comprehensive validation report"""

        report = {
            'generated': datetime.now().isoformat(),
            'total_checks': len(self.check_results),
            'passed': len([r for r in self.check_results if r['passed']]),
            'failed': len(self.failed_checks),
            'pass_rate': 0.0,
            'common_issues': {},
            'recommendations': []
        }

        if self.check_results:
            report['pass_rate'] = report['passed'] / report['total_checks']

        # Analyze common issues
        all_issues = []
        for check in self.failed_checks:
            all_issues.extend(check['issues'])

        # Count issue frequency
        from collections import Counter
        issue_counts = Counter(all_issues)
        report['common_issues'] = dict(issue_counts.most_common(5))

        # Generate recommendations
        if 'null' in str(report['common_issues']).lower():
            report['recommendations'].append('Improve null value handling')

        if 'range' in str(report['common_issues']).lower():
            report['recommendations'].append('Review and update range validation rules')

        if 'consistency' in str(report['common_issues']).lower():
            report['recommendations'].append('Implement stricter consistency checks')

        if report['pass_rate'] < 0.8:
            report['recommendations'].append('Urgent: Address systematic validation failures')

        return report


    def validate(self, data: Dict, validation_level: ValidationLevel = ValidationLevel.STANDARD) -> Dict:
        """Main validation method - validates data at specified level"""

        validation_result = {
            'timestamp': datetime.now().isoformat(),
            'validation_level': validation_level.value,
            'valid': True,
            'issues': [],
            'warnings': [],
            'checks_performed': [],
            'confidence_score': 1.0
        }

        # Perform checks based on validation level
        if validation_level == ValidationLevel.BASIC:
            # Basic validation: null checks, range validation
            basic_result = self._basic_validation(data)
            validation_result['checks_performed'].append('basic_validation')

            if not basic_result['valid']:
                validation_result['valid'] = False
                validation_result['issues'].extend(basic_result.get('issues', []))

        elif validation_level == ValidationLevel.STANDARD:
            # Standard: Basic + consistency checks
            basic_result = self._basic_validation(data)
            consistency_result = self._consistency_validation(data)

            validation_result['checks_performed'].extend(['basic_validation', 'consistency_validation'])

            if not basic_result['valid'] or not consistency_result['valid']:
                validation_result['valid'] = False
                validation_result['issues'].extend(basic_result.get('issues', []))
                validation_result['issues'].extend(consistency_result.get('issues', []))

        elif validation_level == ValidationLevel.RIGOROUS:
            # Rigorous: Standard + cross-source validation
            basic_result = self._basic_validation(data)
            consistency_result = self._consistency_validation(data)
            cross_source_result = self._cross_source_validation(data)

            validation_result['checks_performed'].extend(['basic_validation', 'consistency_validation', 'cross_source_validation'])

            if not basic_result['valid'] or not consistency_result['valid'] or not cross_source_result['valid']:
                validation_result['valid'] = False
                validation_result['issues'].extend(basic_result.get('issues', []))
                validation_result['issues'].extend(consistency_result.get('issues', []))
                validation_result['issues'].extend(cross_source_result.get('issues', []))

        elif validation_level == ValidationLevel.FORENSIC:
            # Forensic: All checks + audit trail validation
            basic_result = self._basic_validation(data)
            consistency_result = self._consistency_validation(data)
            cross_source_result = self._cross_source_validation(data)
            audit_result = self._audit_trail_validation(data)

            validation_result['checks_performed'].extend(['basic_validation', 'consistency_validation', 'cross_source_validation', 'audit_trail_validation'])

            if not all([basic_result['valid'], consistency_result['valid'], cross_source_result['valid'], audit_result['valid']]):
                validation_result['valid'] = False
                validation_result['issues'].extend(basic_result.get('issues', []))
                validation_result['issues'].extend(consistency_result.get('issues', []))
                validation_result['issues'].extend(cross_source_result.get('issues', []))
                validation_result['issues'].extend(audit_result.get('issues', []))

        # Calculate confidence score
        validation_result['confidence_score'] = self.calculate_confidence(data)

        # Log result
        self.check_results.append(validation_result)
        if not validation_result['valid']:
            self.failed_checks.append(validation_result)

        return validation_result

    def _basic_validation(self, data: Dict) -> Dict:
        """Basic validation: null checks, required fields, ranges"""

        result = {'valid': True, 'issues': []}

        # Check for null values in critical fields
        if data.get('value') is None:
            result['valid'] = False
            result['issues'].append("Null value in critical field")

        # Check ranges for percentages
        if 'percentage' in data:
            percentage = data['percentage']
            if percentage < 0 or percentage > 100:
                result['valid'] = False
                result['issues'].append(f"Percentage out of range: {percentage}")

        # Check for negative counts
        for key, value in data.items():
            if 'count' in key.lower() and isinstance(value, (int, float)) and value < 0:
                result['valid'] = False
                result['issues'].append(f"Negative count: {key}={value}")

        return result

    def _consistency_validation(self, data: Dict) -> Dict:
        """Consistency validation: internal logical consistency"""

        result = {'valid': True, 'issues': []}

        # Check sum consistency
        if all(key in data for key in ['total', 'part_a', 'part_b']):
            if data['part_a'] + data['part_b'] > data['total']:
                result['valid'] = False
                result['issues'].append(f"Parts exceed total: {data['part_a']} + {data['part_b']} > {data['total']}")

        # Check logical consistency
        if 'success_rate' in data and 'failure_rate' in data:
            if abs(data['success_rate'] + data['failure_rate'] - 1.0) > 0.01:
                result['valid'] = False
                result['issues'].append("Success and failure rates don't sum to 1.0")

        return result

    def _cross_source_validation(self, data: Dict) -> Dict:
        """Cross-source validation: check agreement between sources"""

        result = {'valid': True, 'issues': []}

        if 'sources' in data:
            sources = data['sources']
            if len(sources) >= 2:
                values = [s.get('value') for s in sources if s.get('value') is not None]
                if len(values) >= 2:
                    max_val = max(values)
                    min_val = min(values)

                    if max_val > 0:
                        variation = (max_val - min_val) / max_val
                        if variation > 0.5:  # More than 50% variation
                            result['valid'] = False
                            result['issues'].append(f"High source disagreement: {variation*100:.1f}% variation")

        return result

    def _audit_trail_validation(self, data: Dict) -> Dict:
        """Audit trail validation: check for complete provenance"""

        result = {'valid': True, 'issues': []}

        required_fields = ['audit_trail', 'sources', 'confidence']

        for field in required_fields:
            if field not in data:
                result['valid'] = False
                result['issues'].append(f"Missing required field for forensic validation: {field}")

        # Check audit trail completeness
        if 'audit_trail' in data:
            audit_trail = data['audit_trail']
            required_steps = ['fetched', 'validated', 'cross-checked']

            for step in required_steps:
                if step not in audit_trail:
                    result['valid'] = False
                    result['issues'].append(f"Missing audit step: {step}")

        return result

    def check_cross_source_agreement(self, sources: List[Dict]) -> Dict:
        """Check agreement between multiple sources"""

        result = {
            'check': 'cross_source_agreement',
            'agreement': True,
            'confidence': 1.0,
            'conflicts': [],
            'timestamp': datetime.now().isoformat()
        }

        if len(sources) < 2:
            return result

        # Extract values
        values = []
        for source in sources:
            if 'value' in source:
                values.append(source['value'])

        if not values:
            result['agreement'] = False
            result['confidence'] = 0.0
            result['conflicts'].append("No values found in sources")
            return result

        # Calculate statistics
        mean_value = sum(values) / len(values)
        max_value = max(values)
        min_value = min(values)

        # Check for significant disagreement
        if max_value > 0:
            variation = (max_value - min_value) / max_value

            if variation > 0.5:  # More than 50% variation
                result['agreement'] = False
                result['confidence'] = max(0.0, 1.0 - variation)
                result['conflicts'].append(f"High variation: {variation*100:.1f}%")
                result['conflicts'].append(f"Values range from {min_value} to {max_value}")
            elif variation > 0.2:  # 20-50% variation
                result['confidence'] = 0.7
                result['conflicts'].append(f"Moderate variation: {variation*100:.1f}%")
            else:
                result['confidence'] = 0.95

        return result


def test_self_checking():
    """Test the self-checking framework"""

    framework = SelfCheckingFramework()

    print("Testing Self-Checking Framework")
    print("="*60)

    # Test 1: Valid data
    print("\nTest 1: Valid data")
    valid_data = {
        'total': 100,
        'components': {'A': 40, 'B': 35, 'C': 25},
        'percentage': 45.5,
        'rate': 0.75,
        'year': 2023
    }
    result = framework.validate_data(valid_data, 'metric', ValidationLevel.STANDARD)
    print(f"  Passed: {result['passed']}")
    print(f"  Confidence: {result['confidence']}")

    # Test 2: Invalid data
    print("\nTest 2: Invalid data")
    invalid_data = {
        'total': 100,
        'components': {'A': 40, 'B': 35, 'C': 30},  # Sum = 105
        'percentage': 150,  # Invalid percentage
        'rate': 1.5,  # Invalid rate
        'year': 2050  # Future year
    }
    result = framework.validate_data(invalid_data, 'metric', ValidationLevel.RIGOROUS)
    print(f"  Passed: {result['passed']}")
    print(f"  Issues: {result['issues'][:2]}")

    # Test 3: Evidence sufficiency
    print("\nTest 3: Evidence sufficiency")
    claim_data = {
        'claim_type': 'bombshell',
        'statement': 'Major finding',
        'evidence': [
            {'source': 'A', 'type': 'official'},
            {'source': 'B', 'type': 'unofficial'}
        ]  # Only 2 sources for bombshell (needs 4)
    }
    result = framework.validate_data(claim_data, 'claim', ValidationLevel.RIGOROUS)
    print(f"  Passed: {result['passed']}")
    print(f"  Evidence sufficient: {'evidence_sufficiency' not in str(result['issues'])}")

    # Test 4: Calculate confidence
    print("\nTest 4: Confidence calculation")
    multi_source_data = {
        'sources': {'A': {'value': 100}, 'B': {'value': 102}, 'C': {'value': 98}},
        'evidence': [{'type': 'official'}, {'type': 'official'}],
    }
    confidence = framework.calculate_confidence(multi_source_data)
    print(f"  Confidence score: {confidence}")

    # Generate report
    print("\n" + "="*60)
    report = framework.generate_validation_report()
    print(f"Validation Summary:")
    print(f"  Total checks: {report['total_checks']}")
    print(f"  Pass rate: {report['pass_rate']:.1%}")
    print(f"  Common issues: {list(report['common_issues'].keys())}")
    print(f"  Recommendations: {report['recommendations']}")

    return framework

if __name__ == "__main__":
    test_self_checking()
