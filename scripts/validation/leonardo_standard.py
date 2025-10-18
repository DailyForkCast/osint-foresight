"""
Leonardo Standard Technology Validation
v9.8 Compliant Implementation

This module implements the 8-point Leonardo Standard for technology specificity
and validation. The Leonardo threshold (85) must be met for all technology claims.
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TechnologySpecificity(Enum):
    """Levels of technology specificity"""
    GENERIC = 1  # "helicopters", "drones" - FORBIDDEN
    CATEGORY = 2  # "military helicopters" - INSUFFICIENT
    MODEL = 3    # "AW139 helicopter" - ACCEPTABLE
    VARIANT = 4  # "MH-139A Grey Wolf variant" - PREFERRED
    SERIAL = 5   # "Serial #15235, delivered 2024" - OPTIMAL


@dataclass
class LeonardoValidation:
    """Validation result for Leonardo Standard compliance"""
    technology: str
    specificity_level: TechnologySpecificity = TechnologySpecificity.GENERIC
    variant_overlap: Optional[str] = None
    china_access: Optional[str] = None
    exploitation_path: Optional[str] = None
    timeline: Optional[str] = None
    alternatives_tested: List[str] = field(default_factory=list)
    oversight_gaps: List[str] = field(default_factory=list)
    confidence_score: int = 0
    confidence_rationale: str = ""
    passed: bool = False
    violations: List[str] = field(default_factory=list)


class LeonardoStandard:
    """
    Leonardo Standard validation system
    Enforces 8-point specificity requirements
    """

    LEONARDO_THRESHOLD = 85  # Minimum score required

    REQUIRED_SPECIFICS = [
        "exact_technology",     # "AW139 helicopter" not "helicopters"
        "variant_overlap",      # "MH-139 is military variant"
        "china_access",         # "40+ operating in China"
        "exploitation_path",    # "Reverse engineering via maintenance"
        "timeline",             # "Simulator delivery 2026"
        "alternatives",         # "Test 5+ explanations"
        "oversight_gaps",       # "Civilian sales unrestricted"
        "confidence_score"      # "15/20 with rationale"
    ]

    # Generic terms that must be avoided
    FORBIDDEN_GENERIC_TERMS = [
        "advanced technology",
        "military equipment",
        "defense systems",
        "dual-use technology",
        "high-tech",
        "cutting-edge",
        "state-of-the-art",
        "next-generation",
        "sophisticated",
        "modern systems"
    ]

    def __init__(self):
        self.validations = []
        self.violations_log = []

    def validate_technology(self, claim: Dict[str, Any]) -> LeonardoValidation:
        """
        Validate a technology claim against Leonardo Standard

        Args:
            claim: Dictionary containing technology claim details

        Returns:
            LeonardoValidation result
        """
        validation = LeonardoValidation(
            technology=claim.get('technology', 'UNSPECIFIED')
        )

        # 1. Check technology specificity
        validation.specificity_level = self._assess_specificity(claim.get('technology', ''))
        if validation.specificity_level.value < 3:
            validation.violations.append(
                f"Technology '{validation.technology}' is too generic (level {validation.specificity_level.value}/5)"
            )

        # 2. Check variant overlap
        if 'variant_overlap' in claim:
            validation.variant_overlap = claim['variant_overlap']
            validation.confidence_score += 15
        else:
            validation.violations.append("Missing variant overlap analysis")

        # 3. Check China access documentation
        if 'china_access' in claim:
            validation.china_access = claim['china_access']
            validation.confidence_score += 15
        else:
            validation.violations.append("Missing China access documentation")

        # 4. Check exploitation path
        if 'exploitation_path' in claim:
            validation.exploitation_path = claim['exploitation_path']
            validation.confidence_score += 15
        else:
            validation.violations.append("Missing exploitation path analysis")

        # 5. Check timeline
        if 'timeline' in claim:
            validation.timeline = claim['timeline']
            validation.confidence_score += 10
        else:
            validation.violations.append("Missing timeline information")

        # 6. Check alternatives testing
        if 'alternatives' in claim:
            validation.alternatives_tested = claim['alternatives']
            if len(validation.alternatives_tested) >= 5:
                validation.confidence_score += 15
            else:
                validation.violations.append(
                    f"Insufficient alternatives tested ({len(validation.alternatives_tested)}/5)"
                )
        else:
            validation.violations.append("No alternative explanations tested")

        # 7. Check oversight gaps
        if 'oversight_gaps' in claim:
            validation.oversight_gaps = claim['oversight_gaps']
            validation.confidence_score += 10
        else:
            validation.violations.append("Missing oversight gap analysis")

        # 8. Apply specificity bonus
        validation.confidence_score += validation.specificity_level.value * 4

        # Calculate confidence rationale
        validation.confidence_rationale = self._generate_rationale(validation)

        # Determine if passed
        validation.passed = validation.confidence_score >= self.LEONARDO_THRESHOLD

        # Log validation
        self.validations.append(validation)
        if not validation.passed:
            self.violations_log.append({
                'technology': validation.technology,
                'score': validation.confidence_score,
                'violations': validation.violations,
                'timestamp': datetime.now().isoformat()
            })

        return validation

    def _assess_specificity(self, technology: str) -> TechnologySpecificity:
        """
        Assess the specificity level of a technology description
        """
        tech_lower = technology.lower()

        # Check for forbidden generic terms
        for term in self.FORBIDDEN_GENERIC_TERMS:
            if term in tech_lower:
                return TechnologySpecificity.GENERIC

        # Check for model/serial numbers
        import re
        if re.search(r'serial\s*#?\s*\d+', tech_lower):
            return TechnologySpecificity.SERIAL
        if re.search(r'[A-Z]{2,}\d{2,}', technology):  # Model numbers like AW139
            if 'variant' in tech_lower or 'version' in tech_lower:
                return TechnologySpecificity.VARIANT
            return TechnologySpecificity.MODEL

        # Check for category-level descriptions
        if any(word in tech_lower for word in ['military', 'civilian', 'commercial']):
            return TechnologySpecificity.CATEGORY

        return TechnologySpecificity.GENERIC

    def _generate_rationale(self, validation: LeonardoValidation) -> str:
        """
        Generate confidence score rationale
        """
        components = []

        if validation.specificity_level.value >= 3:
            components.append(f"Specific technology identified ({validation.specificity_level.name})")
        if validation.variant_overlap:
            components.append("Variant overlap documented")
        if validation.china_access:
            components.append("China access verified")
        if validation.exploitation_path:
            components.append("Exploitation path analyzed")
        if len(validation.alternatives_tested) >= 5:
            components.append(f"{len(validation.alternatives_tested)} alternatives tested")

        return f"Score {validation.confidence_score}/100: " + "; ".join(components)

    def validate_batch(self, claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate multiple technology claims

        Args:
            claims: List of technology claims to validate

        Returns:
            Summary of validation results
        """
        results = []
        for claim in claims:
            results.append(self.validate_technology(claim))

        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed

        return {
            'total_claims': len(results),
            'passed': passed,
            'failed': failed,
            'pass_rate': passed / len(results) if results else 0,
            'average_score': sum(r.confidence_score for r in results) / len(results) if results else 0,
            'common_violations': self._analyze_violations(results),
            'results': [self._serialize_validation(r) for r in results]
        }

    def _analyze_violations(self, results: List[LeonardoValidation]) -> Dict[str, int]:
        """
        Analyze common violation patterns
        """
        violation_counts = {}
        for result in results:
            for violation in result.violations:
                key = violation.split(':')[0] if ':' in violation else violation
                violation_counts[key] = violation_counts.get(key, 0) + 1
        return violation_counts

    def _serialize_validation(self, validation: LeonardoValidation) -> Dict[str, Any]:
        """
        Serialize validation result for storage/transmission
        """
        return {
            'technology': validation.technology,
            'specificity_level': validation.specificity_level.name,
            'confidence_score': validation.confidence_score,
            'passed': validation.passed,
            'violations': validation.violations,
            'rationale': validation.confidence_rationale,
            'details': {
                'variant_overlap': validation.variant_overlap,
                'china_access': validation.china_access,
                'exploitation_path': validation.exploitation_path,
                'timeline': validation.timeline,
                'alternatives_tested': validation.alternatives_tested,
                'oversight_gaps': validation.oversight_gaps
            }
        }

    def generate_report(self) -> str:
        """
        Generate Leonardo Standard compliance report
        """
        if not self.validations:
            return "No validations performed"

        passed = sum(1 for v in self.validations if v.passed)
        failed = len(self.validations) - passed

        report = f"""
Leonardo Standard Validation Report
====================================
Generated: {datetime.now().isoformat()}

Summary Statistics
------------------
Total Validations: {len(self.validations)}
Passed: {passed} ({passed/len(self.validations)*100:.1f}%)
Failed: {failed} ({failed/len(self.validations)*100:.1f}%)
Leonardo Threshold: {self.LEONARDO_THRESHOLD}

Average Confidence Score: {sum(v.confidence_score for v in self.validations)/len(self.validations):.1f}

Most Common Violations:
"""
        violation_counts = {}
        for v in self.validations:
            for violation in v.violations:
                violation_counts[violation] = violation_counts.get(violation, 0) + 1

        for violation, count in sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            report += f"  - {violation}: {count} occurrences\n"

        report += "\nFailed Technologies:\n"
        for v in self.validations:
            if not v.passed:
                report += f"  - {v.technology}: Score {v.confidence_score} (Need {self.LEONARDO_THRESHOLD})\n"

        return report


# Example usage
if __name__ == "__main__":
    validator = LeonardoStandard()

    # Good example - passes Leonardo Standard
    good_claim = {
        'technology': 'AW139 helicopter serial #15235',
        'variant_overlap': 'MH-139A Grey Wolf is military variant of civilian AW139',
        'china_access': '42 AW139s operating in China through civilian channels',
        'exploitation_path': 'Reverse engineering possible through maintenance contracts',
        'timeline': 'Simulator systems delivered to China 2026',
        'alternatives': [
            'Independent development',
            'Russian technology transfer',
            'European partnership',
            'Cyber espionage',
            'Open source intelligence'
        ],
        'oversight_gaps': [
            'No restrictions on civilian variant sales',
            'Maintenance training not monitored',
            'Spare parts freely available'
        ]
    }

    # Bad example - fails Leonardo Standard
    bad_claim = {
        'technology': 'advanced military helicopters',
        'china_access': 'China interested in helicopters'
    }

    print("Testing good claim:")
    result1 = validator.validate_technology(good_claim)
    print(f"  Score: {result1.confidence_score} - {'PASSED' if result1.passed else 'FAILED'}")
    print(f"  Rationale: {result1.confidence_rationale}")

    print("\nTesting bad claim:")
    result2 = validator.validate_technology(bad_claim)
    print(f"  Score: {result2.confidence_score} - {'PASSED' if result2.passed else 'FAILED'}")
    print(f"  Violations: {result2.violations}")

    print("\n" + validator.generate_report())