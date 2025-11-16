#!/usr/bin/env python3
"""
Example: Comprehensive Validation Using Unified Manager
Demonstrates how to use all validators for claims, findings, and negative evidence
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from core.unified_validation_manager import UnifiedValidationManager


def validate_research_claim():
    """Example: Validate a research collaboration claim"""

    print("=" * 70)
    print("Example 1: Research Collaboration Claim Validation")
    print("=" * 70)

    manager = UnifiedValidationManager()

    # Claim: Italy has 222 China research collaborations
    claim = {
        'type': 'claim',
        'statement': 'Italy has 222 collaborative research projects with Chinese institutions',
        'claim_type': 'significant',  # Requires 3+ sources and primary evidence
        'data': {
            'collaboration_count': 222,
            'sources': {
                'CORDIS': {'value': 222, 'type': 'primary'},
                'OpenAlex': {'value': 218, 'type': 'secondary'}
            }
        },
        'evidence': [
            {
                'source': 'CORDIS database query',
                'type': 'primary',
                'official': True,
                'query': "SELECT COUNT(*) FROM projects WHERE country='IT' AND partner_country='CN'",
                'result': 222,
                'timestamp': datetime.now().isoformat()
            },
            {
                'source': 'OpenAlex affiliation analysis',
                'type': 'secondary',
                'verified': True,
                'result': 218,
                'timestamp': datetime.now().isoformat()
            },
            {
                'source': 'Manual verification sample (n=50)',
                'type': 'corroborating',
                'confidence': 0.94,
                'timestamp': datetime.now().isoformat()
            }
        ],
        'text': 'La collaborazione tra università italiane e istituti di ricerca cinesi nel contesto dei progetti CORDIS',
        'country': 'IT',
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'data_version': 'CORDIS_2025Q3'
        }
    }

    # Comprehensive validation
    result = manager.validate_finding(claim, validation_level='rigorous')

    print(f"\nValidation Result:")
    print(f"  Overall Passed: {result['overall_passed']}")
    print(f"  Confidence: {result['overall_confidence']:.2f}")
    print(f"  Validators Used: {', '.join(result['validators_used'])}")
    print(f"\nValidation Details:")

    for validator_name, validation in result['validations'].items():
        print(f"\n  {validator_name}:")
        print(f"    Passed: {validation['passed']}")
        if 'sufficiency_score' in validation:
            print(f"    Sufficiency Score: {validation['sufficiency_score']:.2f}")
        if 'confidence' in validation:
            print(f"    Confidence: {validation.get('confidence', 'N/A')}")
        if validation.get('issues'):
            print(f"    Issues: {validation['issues'][:2]}")
        if validation.get('recommendations'):
            print(f"    Recommendations: {validation['recommendations'][:1]}")

    return result


def validate_negative_evidence():
    """Example: Validate negative evidence (no results found)"""

    print("\n" + "=" * 70)
    print("Example 2: Negative Evidence Validation")
    print("=" * 70)

    manager = UnifiedValidationManager()

    # Search that found zero results
    search = {
        'query': 'Chinese telecommunications contracts in Finland',
        'data_source': 'TED database',
        'data_size_gb': 30.5,
        'time_period': '2015-2025',
        'attempts': 3,  # Multiple search attempts
        'zero_result_actions': [
            'logged_to_registry',
            'expanded_search',  # Tried broader terms
            'checked_completeness',  # Verified data completeness
            'verified_syntax',  # Checked query syntax
            'documented_absence',  # Documented the null finding
            'calculated_confidence'  # Calculated confidence in absence
        ]
    }

    result = manager.validate_negative_evidence(search)

    print(f"\nNegative Evidence Validation:")
    print(f"  Properly Handled: {result['passed']}")
    print(f"  Confidence in Absence: {result['confidence_in_absence']:.2f}")
    print(f"  Actions Taken: {len(result['actions_taken'])}/{len(result['actions_taken']) + len(result.get('actions_missing', []))}")

    if result.get('actions_missing'):
        print(f"  Missing Actions: {result['actions_missing']}")

    return result


def validate_cross_source_agreement():
    """Example: Validate agreement between multiple sources"""

    print("\n" + "=" * 70)
    print("Example 3: Cross-Source Agreement Validation")
    print("=" * 70)

    manager = UnifiedValidationManager()

    # Same metric from multiple sources
    sources = [
        {
            'source': 'Eurostat Trade Database',
            'value': 45.2,  # 45.2% import dependency
            'type': 'official',
            'timestamp': '2024-Q4'
        },
        {
            'source': 'OECD Economic Data',
            'value': 43.8,  # 43.8% import dependency
            'type': 'official',
            'timestamp': '2024-Q4'
        },
        {
            'source': 'World Bank Data',
            'value': 46.1,  # 46.1% import dependency
            'type': 'official',
            'timestamp': '2024-Q3'
        },
        {
            'source': 'Internal Analysis',
            'value': 44.5,  # 44.5% import dependency
            'type': 'derived',
            'timestamp': '2025-Q1'
        }
    ]

    result = manager.check_cross_source_agreement(sources)

    print(f"\nCross-Source Agreement:")
    print(f"  Agreement: {result['agreement']}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Sources: {len(sources)}")

    if result.get('conflicts'):
        print(f"  Conflicts Detected:")
        for conflict in result['conflicts']:
            print(f"    - {conflict}")

    return result


def validate_multilingual_finding():
    """Example: Validate multilingual detection"""

    print("\n" + "=" * 70)
    print("Example 4: Multilingual Detection Validation")
    print("=" * 70)

    manager = UnifiedValidationManager()

    # French procurement text
    text = """
    La société chinoise Huawei Technologies a remporté un contrat majeur
    pour la fourniture d'équipements de télécommunications 5G dans le cadre
    du marché public européen. Le contrat, d'une valeur de 15 millions d'euros,
    a été attribué après une procédure d'appel d'offres conforme aux directives
    de l'Union européenne.
    """

    result = manager.validate_multilingual_detection(text, 'FR')

    print(f"\nMultilingual Validation:")
    print(f"  China Detected: {result['passed']}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Languages Detected: {', '.join(result['language_names'])}")
    print(f"  Matches Found: {len(result['matches'])}")
    print(f"  False Positive Risk: {result['false_positive_risk']}")

    if result['matches']:
        print(f"\n  Sample Matches:")
        for match in result['matches'][:3]:
            print(f"    - {match.get('text', 'N/A')} ({match.get('type', 'pattern')})")

    return result


def main():
    """Run all validation examples"""

    print("\n")
    print("=" * 70)
    print("COMPREHENSIVE VALIDATION EXAMPLES")
    print("Using Unified Validation Manager")
    print("=" * 70)

    # Run all examples
    claim_result = validate_research_claim()
    neg_result = validate_negative_evidence()
    cross_result = validate_cross_source_agreement()
    multilingual_result = validate_multilingual_finding()

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    print(f"\n1. Research Claim: {'PASSED' if claim_result['overall_passed'] else 'FAILED'}")
    print(f"   Confidence: {claim_result['overall_confidence']:.2f}")

    print(f"\n2. Negative Evidence: {'PROPERLY HANDLED' if neg_result['passed'] else 'IMPROPERLY HANDLED'}")
    print(f"   Confidence in Absence: {neg_result['confidence_in_absence']:.2f}")

    print(f"\n3. Cross-Source Agreement: {'AGREEMENT' if cross_result['agreement'] else 'DISAGREEMENT'}")
    print(f"   Confidence: {cross_result['confidence']:.2f}")

    print(f"\n4. Multilingual Detection: {'DETECTED' if multilingual_result['passed'] else 'NOT DETECTED'}")
    print(f"   Confidence: {multilingual_result['confidence']:.2f}")

    print("\n" + "=" * 70)
    print("All validators are now ACTIVE in production!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
