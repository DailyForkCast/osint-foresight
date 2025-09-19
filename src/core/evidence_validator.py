#!/usr/bin/env python3
"""
Evidence Sufficiency Validator
Ensures all claims have adequate supporting evidence
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
from pathlib import Path
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaimType(Enum):
    """Types of claims by significance"""
    TRIVIAL = "trivial"          # Basic fact, minimal evidence needed
    STANDARD = "standard"        # Normal claim, standard evidence
    SIGNIFICANT = "significant"  # Important finding, strong evidence
    CRITICAL = "critical"        # Major discovery, comprehensive evidence
    BOMBSHELL = "bombshell"     # Game-changing, exhaustive evidence


class EvidenceType(Enum):
    """Types of evidence by quality"""
    PRIMARY = "primary"          # Original source, official registry
    SECONDARY = "secondary"      # Derived data, processed information
    TERTIARY = "tertiary"       # Aggregated, summary data
    CIRCUMSTANTIAL = "circumstantial"  # Indirect evidence
    CORROBORATING = "corroborating"    # Supporting evidence


class EvidenceQuality(Enum):
    """Quality levels of evidence"""
    AUTHORITATIVE = "authoritative"  # Official government/registry
    VERIFIED = "verified"            # Multiple independent confirmations
    RELIABLE = "reliable"            # Trusted source
    UNCERTAIN = "uncertain"          # Unverified or single source
    QUESTIONABLE = "questionable"    # Conflicting or dubious


class EvidenceSufficiencyValidator:
    """Validates that claims have sufficient evidence"""

    def __init__(self):
        # Evidence requirements by claim type
        self.requirements = {
            ClaimType.TRIVIAL: {
                'min_sources': 1,
                'min_quality': EvidenceQuality.UNCERTAIN,
                'needs_primary': False,
                'needs_cross_validation': False
            },
            ClaimType.STANDARD: {
                'min_sources': 2,
                'min_quality': EvidenceQuality.RELIABLE,
                'needs_primary': False,
                'needs_cross_validation': False
            },
            ClaimType.SIGNIFICANT: {
                'min_sources': 3,
                'min_quality': EvidenceQuality.VERIFIED,
                'needs_primary': True,
                'needs_cross_validation': True
            },
            ClaimType.CRITICAL: {
                'min_sources': 4,
                'min_quality': EvidenceQuality.VERIFIED,
                'needs_primary': True,
                'needs_cross_validation': True
            },
            ClaimType.BOMBSHELL: {
                'min_sources': 5,
                'min_quality': EvidenceQuality.AUTHORITATIVE,
                'needs_primary': True,
                'needs_cross_validation': True,
                'needs_official': True  # Requires official/registry confirmation
            }
        }

        # Quality scoring
        self.quality_scores = {
            EvidenceQuality.AUTHORITATIVE: 1.0,
            EvidenceQuality.VERIFIED: 0.8,
            EvidenceQuality.RELIABLE: 0.6,
            EvidenceQuality.UNCERTAIN: 0.3,
            EvidenceQuality.QUESTIONABLE: 0.1
        }

        # Track validation results
        self.validation_log = []
        self.insufficient_evidence = []

    def validate_claim(self, claim: Dict) -> Dict:
        """Validate that a claim has sufficient evidence"""

        validation_result = {
            'timestamp': datetime.now().isoformat(),
            'claim': claim.get('statement', ''),
            'claim_type': claim.get('type', ClaimType.STANDARD),
            'valid': False,
            'sufficiency_score': 0.0,
            'issues': [],
            'recommendations': [],
            'evidence_summary': {}
        }

        # Determine claim type
        if isinstance(claim.get('type'), str):
            try:
                claim_type = ClaimType(claim['type'])
            except ValueError:
                claim_type = ClaimType.STANDARD
        else:
            claim_type = claim.get('type', ClaimType.STANDARD)

        # Get requirements
        requirements = self.requirements[claim_type]

        # Validate evidence
        evidence = claim.get('evidence', [])

        # Check source count
        source_count = len(evidence)
        if source_count < requirements['min_sources']:
            validation_result['issues'].append(
                f"Insufficient sources: {source_count} < {requirements['min_sources']} required"
            )
            validation_result['recommendations'].append(
                f"Add {requirements['min_sources'] - source_count} more independent sources"
            )

        # Check evidence quality
        quality_scores = []
        has_primary = False
        has_official = False

        for e in evidence:
            # Determine quality
            quality = self._assess_evidence_quality(e)
            quality_scores.append(self.quality_scores[quality])

            # Check for primary evidence
            if e.get('type') == EvidenceType.PRIMARY.value:
                has_primary = True

            # Check for official source
            if e.get('official', False) or 'government' in str(e.get('source', '')).lower():
                has_official = True

        # Calculate average quality
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        min_quality_score = self.quality_scores[requirements['min_quality']]

        if avg_quality < min_quality_score:
            validation_result['issues'].append(
                f"Insufficient evidence quality: {avg_quality:.2f} < {min_quality_score:.2f}"
            )
            validation_result['recommendations'].append(
                "Obtain higher quality evidence from authoritative sources"
            )

        # Check primary evidence requirement
        if requirements['needs_primary'] and not has_primary:
            validation_result['issues'].append("Missing primary evidence")
            validation_result['recommendations'].append(
                "Include at least one primary source (original data, official registry)"
            )

        # Check official requirement for bombshells
        if requirements.get('needs_official', False) and not has_official:
            validation_result['issues'].append("Bombshell claim requires official confirmation")
            validation_result['recommendations'].append(
                "Obtain confirmation from official government or registry source"
            )

        # Check cross-validation
        if requirements['needs_cross_validation']:
            if not self._check_cross_validation(evidence):
                validation_result['issues'].append("Evidence not cross-validated")
                validation_result['recommendations'].append(
                    "Verify claim using independent methodologies or data sources"
            )

        # Calculate sufficiency score
        validation_result['sufficiency_score'] = self._calculate_sufficiency_score(
            source_count, requirements['min_sources'],
            avg_quality, min_quality_score,
            has_primary, requirements['needs_primary'],
            has_official, requirements.get('needs_official', False)
        )

        # Determine if valid
        validation_result['valid'] = (
            len(validation_result['issues']) == 0 and
            validation_result['sufficiency_score'] >= 0.7
        )

        # Generate evidence summary
        validation_result['evidence_summary'] = {
            'source_count': source_count,
            'average_quality': avg_quality,
            'has_primary': has_primary,
            'has_official': has_official,
            'quality_distribution': self._get_quality_distribution(evidence)
        }

        # Log result
        self.validation_log.append(validation_result)

        if not validation_result['valid']:
            self.insufficient_evidence.append(validation_result)
            logger.warning(f"Insufficient evidence for claim: {claim.get('statement', '')[:50]}...")

        return validation_result

    def _assess_evidence_quality(self, evidence: Dict) -> EvidenceQuality:
        """Assess the quality of a piece of evidence"""

        # Check for quality indicators
        if evidence.get('official', False):
            return EvidenceQuality.AUTHORITATIVE

        if evidence.get('verified', False) or evidence.get('confirmations', 0) >= 2:
            return EvidenceQuality.VERIFIED

        if evidence.get('trusted', False) or evidence.get('reputation', 0) > 0.7:
            return EvidenceQuality.RELIABLE

        if evidence.get('uncertain', False) or not evidence.get('source'):
            return EvidenceQuality.UNCERTAIN

        # Default to reliable if source provided
        if evidence.get('source'):
            return EvidenceQuality.RELIABLE

        return EvidenceQuality.UNCERTAIN

    def _check_cross_validation(self, evidence: List[Dict]) -> bool:
        """Check if evidence is cross-validated"""

        # Look for different types of evidence
        evidence_types = set()
        sources = set()

        for e in evidence:
            if 'type' in e:
                evidence_types.add(e['type'])
            if 'source' in e:
                sources.add(e['source'])

        # Cross-validated if we have multiple types or multiple independent sources
        return len(evidence_types) >= 2 or len(sources) >= 3

    def _calculate_sufficiency_score(self,
                                    source_count: int, min_sources: int,
                                    avg_quality: float, min_quality: float,
                                    has_primary: bool, needs_primary: bool,
                                    has_official: bool, needs_official: bool) -> float:
        """Calculate overall evidence sufficiency score"""

        score = 0.0
        weights = {
            'source_count': 0.3,
            'quality': 0.3,
            'primary': 0.2,
            'official': 0.2
        }

        # Source count score
        source_score = min(1.0, source_count / min_sources)
        score += source_score * weights['source_count']

        # Quality score
        quality_score = min(1.0, avg_quality / min_quality) if min_quality > 0 else avg_quality
        score += quality_score * weights['quality']

        # Primary evidence score
        if needs_primary:
            primary_score = 1.0 if has_primary else 0.0
            score += primary_score * weights['primary']
        else:
            score += weights['primary']  # Full score if not required

        # Official evidence score
        if needs_official:
            official_score = 1.0 if has_official else 0.0
            score += official_score * weights['official']
        else:
            score += weights['official']  # Full score if not required

        return round(score, 3)

    def _get_quality_distribution(self, evidence: List[Dict]) -> Dict:
        """Get distribution of evidence quality"""

        distribution = {
            'authoritative': 0,
            'verified': 0,
            'reliable': 0,
            'uncertain': 0,
            'questionable': 0
        }

        for e in evidence:
            quality = self._assess_evidence_quality(e)
            distribution[quality.value] += 1

        return distribution

    def validate_negative_evidence(self, search_params: Dict) -> Dict:
        """Validate handling of negative evidence (zero results)"""

        validation_result = {
            'timestamp': datetime.now().isoformat(),
            'search': search_params,
            'properly_handled': False,
            'actions_taken': [],
            'actions_missing': [],
            'confidence_in_absence': 0.0
        }

        required_actions = [
            'logged_to_registry',
            'expanded_search',
            'checked_completeness',
            'verified_syntax',
            'documented_absence',
            'calculated_confidence'
        ]

        # Check which actions were taken
        actions = search_params.get('zero_result_actions', [])

        for required in required_actions:
            if required in actions or any(required in str(a) for a in actions):
                validation_result['actions_taken'].append(required)
            else:
                validation_result['actions_missing'].append(required)

        # Calculate confidence in absence
        confidence_factors = {
            'data_size': search_params.get('data_size_gb', 0) / 100,  # Normalize to 100GB
            'search_comprehensiveness': len(validation_result['actions_taken']) / len(required_actions),
            'multiple_attempts': 1.0 if search_params.get('attempts', 1) > 1 else 0.5
        }

        validation_result['confidence_in_absence'] = min(1.0, sum(confidence_factors.values()) / len(confidence_factors))

        # Determine if properly handled
        validation_result['properly_handled'] = (
            len(validation_result['actions_taken']) >= 4 and
            validation_result['confidence_in_absence'] >= 0.7
        )

        if not validation_result['properly_handled']:
            logger.warning(f"Improper zero-result handling: {validation_result['actions_missing']}")

        return validation_result

    def generate_evidence_report(self) -> Dict:
        """Generate comprehensive evidence sufficiency report"""

        report = {
            'generated': datetime.now().isoformat(),
            'total_claims': len(self.validation_log),
            'valid_claims': len([v for v in self.validation_log if v['valid']]),
            'insufficient_evidence': len(self.insufficient_evidence),
            'validity_rate': 0.0,
            'common_issues': {},
            'by_claim_type': {},
            'recommendations': []
        }

        if self.validation_log:
            report['validity_rate'] = report['valid_claims'] / report['total_claims']

        # Analyze by claim type
        for claim_type in ClaimType:
            type_validations = [v for v in self.validation_log
                              if v['claim_type'] == claim_type]
            if type_validations:
                valid = len([v for v in type_validations if v['valid']])
                report['by_claim_type'][claim_type.value] = {
                    'total': len(type_validations),
                    'valid': valid,
                    'rate': valid / len(type_validations)
                }

        # Common issues
        all_issues = []
        for validation in self.insufficient_evidence:
            all_issues.extend(validation['issues'])

        from collections import Counter
        issue_counts = Counter(all_issues)
        report['common_issues'] = dict(issue_counts.most_common(5))

        # Generate recommendations
        if report['validity_rate'] < 0.8:
            report['recommendations'].append(
                "Strengthen evidence collection processes"
            )

        if 'Insufficient sources' in str(report['common_issues']):
            report['recommendations'].append(
                "Implement multi-source verification as standard practice"
            )

        if 'Missing primary evidence' in str(report['common_issues']):
            report['recommendations'].append(
                "Prioritize primary source collection"
            )

        return report


def test_evidence_validator():
    """Test the evidence sufficiency validator"""

    validator = EvidenceSufficiencyValidator()

    print("Testing Evidence Sufficiency Validator")
    print("="*60)

    # Test 1: Standard claim with sufficient evidence
    print("\nTest 1: Standard claim - sufficient evidence")
    claim1 = {
        'statement': 'Italy has 45% dependency on China for critical components',
        'type': 'standard',
        'evidence': [
            {'source': 'Eurostat', 'type': 'primary', 'official': True},
            {'source': 'OECD', 'type': 'secondary', 'verified': True}
        ]
    }
    result = validator.validate_claim(claim1)
    print(f"  Valid: {result['valid']}")
    print(f"  Sufficiency score: {result['sufficiency_score']}")

    # Test 2: Bombshell claim with insufficient evidence
    print("\nTest 2: Bombshell claim - insufficient evidence")
    claim2 = {
        'statement': '100% of Italian quantum research involves China',
        'type': 'bombshell',
        'evidence': [
            {'source': 'OpenAlex', 'type': 'secondary'},
            {'source': 'News article', 'type': 'tertiary'}
        ]
    }
    result = validator.validate_claim(claim2)
    print(f"  Valid: {result['valid']}")
    print(f"  Issues: {result['issues'][:2]}")
    print(f"  Recommendations: {result['recommendations'][0]}")

    # Test 3: Zero results handling
    print("\nTest 3: Zero results handling")
    search = {
        'query': 'Germany-China collaboration',
        'data_size_gb': 350,
        'attempts': 1,
        'zero_result_actions': [
            'logged_to_registry',
            'expanded_search',
            'checked_completeness'
        ]
    }
    result = validator.validate_negative_evidence(search)
    print(f"  Properly handled: {result['properly_handled']}")
    print(f"  Confidence in absence: {result['confidence_in_absence']:.2f}")
    print(f"  Missing actions: {result['actions_missing'][:2]}")

    # Generate report
    print("\n" + "="*60)
    report = validator.generate_evidence_report()
    print("Evidence Sufficiency Report:")
    print(f"  Total claims: {report['total_claims']}")
    print(f"  Validity rate: {report['validity_rate']:.1%}")
    print(f"  Common issues: {list(report['common_issues'].keys())}")

    return validator

if __name__ == "__main__":
    test_evidence_validator()
