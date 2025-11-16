#!/usr/bin/env python3
"""
Output Validation - Leonardo Standard Compliance Checker
Validates that all phase outputs meet Leonardo Standard requirements
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.phases.phase_01_data_validation import execute_phase_1
from src.phases.phase_02_technology_landscape import execute_phase_2
from src.phases.phase_03_supply_chain_v3_final import execute_phase_3
from src.phases.phase_04_institutions import execute_phase_4
from src.phases.phase_05_funding import execute_phase_5
from src.phases.phase_06_international_links import execute_phase_6


class LeonardoOutputValidator:
    """
    Validates phase outputs against Leonardo Standard requirements

    Leonardo Standard Requirements:
    1. Probability bands (CERTAIN, HIGHLY LIKELY, LIKELY, POSSIBLE, UNLIKELY)
    2. Quality scores (1-5 scale)
    3. Confidence assessments (with rationale)
    4. Source validation (with URLs/references)
    5. Proper metadata (timestamps, version, as_of dates)
    6. Null data handling (documented when data unavailable)
    7. Country-specific improvements (actionable recommendations)
    """

    PROBABILITY_BANDS = [
        'CERTAIN', 'HIGHLY_LIKELY', 'LIKELY', 'POSSIBLE',
        'UNLIKELY', 'HIGHLY_UNLIKELY', 'IMPOSSIBLE'
    ]

    REQUIRED_METADATA_FIELDS = [
        'analysis_type', 'country', 'as_of'
    ]

    OPTIONAL_METADATA_FIELDS = [
        'version', 'leonardo_standard_compliant', 'has_improvements',
        'data_sources', 'analysis_types', 'phase'
    ]

    def __init__(self):
        self.results = []
        self.summary = {
            'total_entries': 0,
            'compliant_entries': 0,
            'non_compliant_entries': 0,
            'issues': [],
            'warnings': []
        }

    def validate_entry(self, entry: Dict[str, Any], phase: int, country: str) -> Dict[str, Any]:
        """Validate a single entry against Leonardo Standard"""
        validation = {
            'phase': phase,
            'country': country,
            'analysis_type': entry.get('analysis_type', 'UNKNOWN'),
            'compliant': True,
            'issues': [],
            'warnings': [],
            'scores': {}
        }

        # 1. Check required metadata
        for field in self.REQUIRED_METADATA_FIELDS:
            if field not in entry:
                validation['issues'].append(f"Missing required metadata field: {field}")
                validation['compliant'] = False

        # 2. Check 'as_of' timestamp format
        if 'as_of' in entry:
            if not self._validate_timestamp(entry['as_of']):
                validation['issues'].append(f"Invalid timestamp format: {entry['as_of']}")
                validation['compliant'] = False

        # 3. Check for probability bands (if applicable)
        if 'probability' in entry or 'likelihood' in entry:
            prob_value = entry.get('probability') or entry.get('likelihood')
            if prob_value not in self.PROBABILITY_BANDS:
                validation['warnings'].append(
                    f"Probability band '{prob_value}' not in standard set"
                )

        # 4. Check quality scores (if present)
        if 'quality_score' in entry:
            score = entry.get('quality_score')
            if not isinstance(score, (int, float)) or score < 1 or score > 5:
                validation['issues'].append(
                    f"Quality score {score} not in valid range (1-5)"
                )
                validation['compliant'] = False
            else:
                validation['scores']['quality'] = score

        # 5. Check confidence assessments
        if 'confidence' in entry:
            confidence = entry.get('confidence')
            if isinstance(confidence, dict):
                if 'score' not in confidence:
                    validation['warnings'].append("Confidence object missing score")
                if 'rationale' not in confidence:
                    validation['warnings'].append("Confidence object missing rationale")
            elif isinstance(confidence, str):
                # String confidence (e.g., "HIGH", "MEDIUM", "LOW")
                if confidence.upper() not in ['HIGH', 'MEDIUM', 'LOW']:
                    validation['warnings'].append(
                        f"String confidence '{confidence}' not in standard set"
                    )

        # 6. Check source validation
        if 'sources' in entry or 'data_source' in entry:
            sources = entry.get('sources') or [entry.get('data_source')]
            if not sources:
                validation['warnings'].append("Empty sources list")
            else:
                validation['scores']['source_count'] = len(sources)
        else:
            validation['warnings'].append("No source validation present")

        # 7. Check for null data handling
        if 'null_data' in entry or 'data_gaps' in entry:
            validation['scores']['null_handling'] = True

        # 8. Check for improvement recommendations (if phase 1-6)
        if entry.get('analysis_type') == 'improvement_recommendations':
            validation['scores']['has_improvements'] = True
            if 'priority_actions' not in entry:
                validation['warnings'].append(
                    "Improvement recommendations missing priority_actions"
                )

        return validation

    def validate_phase_output(self, phase_result: Dict[str, Any], phase_num: int, country: str) -> Dict[str, Any]:
        """Validate complete phase output"""
        phase_validation = {
            'phase': phase_num,
            'country': country,
            'total_entries': len(phase_result.get('entries', [])),
            'compliant_entries': 0,
            'non_compliant_entries': 0,
            'entry_validations': [],
            'metadata_validation': {},
            'overall_compliant': True
        }

        # Validate metadata
        metadata = phase_result.get('metadata', {})
        if not metadata:
            phase_validation['metadata_validation']['missing'] = True
            phase_validation['overall_compliant'] = False
        else:
            # Check leonardo_standard_compliant flag
            if 'leonardo_standard_compliant' in metadata:
                phase_validation['metadata_validation']['claims_compliant'] = metadata['leonardo_standard_compliant']

            # Check has_improvements flag
            if 'has_improvements' in metadata:
                phase_validation['metadata_validation']['has_improvements'] = metadata['has_improvements']

            # Check as_of timestamp
            if 'as_of' not in metadata:
                phase_validation['metadata_validation']['missing_timestamp'] = True

        # Validate each entry
        for entry in phase_result.get('entries', []):
            entry_val = self.validate_entry(entry, phase_num, country)
            phase_validation['entry_validations'].append(entry_val)

            if entry_val['compliant']:
                phase_validation['compliant_entries'] += 1
            else:
                phase_validation['non_compliant_entries'] += 1
                phase_validation['overall_compliant'] = False

        return phase_validation

    def validate_country(self, country_code: str) -> Dict[str, Any]:
        """Validate all phases for a country"""
        print(f"\n{'='*80}")
        print(f"VALIDATING COUNTRY: {country_code}")
        print(f"{'='*80}")

        country_validation = {
            'country': country_code,
            'phases': [],
            'summary': {
                'total_phases': 6,
                'compliant_phases': 0,
                'non_compliant_phases': 0,
                'total_entries': 0,
                'compliant_entries': 0
            }
        }

        phases = [
            (execute_phase_1, 1, "Data Validation"),
            (execute_phase_2, 2, "Technology Landscape"),
            (execute_phase_3, 3, "Supply Chain"),
            (execute_phase_4, 4, "Institutions"),
            (execute_phase_5, 5, "Funding Flows"),
            (execute_phase_6, 6, "International Links")
        ]

        for phase_func, phase_num, phase_name in phases:
            print(f"\nPhase {phase_num}: {phase_name}...", end=" ")
            try:
                result = phase_func(country_code, {})
                validation = self.validate_phase_output(result, phase_num, country_code)
                country_validation['phases'].append(validation)

                # Update summary
                country_validation['summary']['total_entries'] += validation['total_entries']
                country_validation['summary']['compliant_entries'] += validation['compliant_entries']

                if validation['overall_compliant']:
                    country_validation['summary']['compliant_phases'] += 1
                    print("[PASS] COMPLIANT")
                else:
                    country_validation['summary']['non_compliant_phases'] += 1
                    print("[FAIL] NON-COMPLIANT")
                    print(f"  Issues: {validation['non_compliant_entries']} entries failed")

            except Exception as e:
                print(f"[ERROR] {e}")
                country_validation['phases'].append({
                    'phase': phase_num,
                    'error': str(e),
                    'overall_compliant': False
                })
                country_validation['summary']['non_compliant_phases'] += 1

        return country_validation

    def _validate_timestamp(self, timestamp: str) -> bool:
        """Validate ISO 8601 timestamp format"""
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return True
        except:
            return False

    def generate_report(self, validations: List[Dict[str, Any]]) -> str:
        """Generate comprehensive validation report"""
        total_countries = len(validations)
        total_phases = sum(v['summary']['total_phases'] for v in validations)
        compliant_phases = sum(v['summary']['compliant_phases'] for v in validations)
        total_entries = sum(v['summary']['total_entries'] for v in validations)
        compliant_entries = sum(v['summary']['compliant_entries'] for v in validations)

        report = f"""
{'='*80}
LEONARDO STANDARD OUTPUT VALIDATION REPORT
{'='*80}
Generated: {datetime.now().isoformat()}

EXECUTIVE SUMMARY
=================
Countries Tested: {total_countries}
Total Phases: {total_phases}
Compliant Phases: {compliant_phases} ({compliant_phases/total_phases*100:.1f}%)
Non-Compliant Phases: {total_phases - compliant_phases} ({(total_phases-compliant_phases)/total_phases*100:.1f}%)

Total Entries: {total_entries}
Compliant Entries: {compliant_entries} ({compliant_entries/total_entries*100:.1f}%)
Non-Compliant Entries: {total_entries - compliant_entries} ({(total_entries-compliant_entries)/total_entries*100:.1f}%)

DETAILED RESULTS
================
"""

        for validation in validations:
            country = validation['country']
            summary = validation['summary']

            report += f"\n{country}: {summary['compliant_phases']}/{summary['total_phases']} phases compliant"
            report += f" ({summary['compliant_entries']}/{summary['total_entries']} entries)\n"

            # Show non-compliant phases
            for phase_val in validation['phases']:
                if not phase_val.get('overall_compliant', True):
                    phase_num = phase_val.get('phase', '?')
                    if 'error' in phase_val:
                        report += f"  Phase {phase_num}: ERROR - {phase_val['error']}\n"
                    else:
                        non_compliant = phase_val.get('non_compliant_entries', 0)
                        report += f"  Phase {phase_num}: {non_compliant} non-compliant entries\n"

                        # Show sample issues
                        for entry_val in phase_val.get('entry_validations', [])[:3]:
                            if not entry_val['compliant']:
                                issues = '; '.join(entry_val['issues'][:2])
                                report += f"    - {entry_val['analysis_type']}: {issues}\n"

        report += f"\n{'='*80}\n"

        # Overall assessment
        compliance_rate = compliant_phases / total_phases * 100 if total_phases > 0 else 0

        if compliance_rate >= 95:
            report += "ASSESSMENT: [EXCELLENT] System meets Leonardo Standard\n"
        elif compliance_rate >= 80:
            report += "ASSESSMENT: [GOOD] Minor improvements needed\n"
        elif compliance_rate >= 60:
            report += "ASSESSMENT: [MODERATE] Significant improvements needed\n"
        else:
            report += "ASSESSMENT: [POOR] Major compliance issues\n"

        report += f"{'='*80}\n"

        return report


def main():
    print("="*80)
    print("LEONARDO STANDARD OUTPUT VALIDATION")
    print("="*80)

    # Test countries from different tiers
    test_countries = [
        'IT',  # Original (full data)
        'GR',  # Tier 1 (template)
        'US'   # Tier 5 (template)
    ]

    print(f"\nTesting {len(test_countries)} countries:")
    for code in test_countries:
        print(f"  - {code}")

    validator = LeonardoOutputValidator()
    validations = []

    for country in test_countries:
        validation = validator.validate_country(country)
        validations.append(validation)

    # Generate report
    print("\n" + "="*80)
    print("GENERATING VALIDATION REPORT")
    print("="*80)

    report = validator.generate_report(validations)
    print(report)

    # Save results
    output_dir = Path("C:/Projects/OSINT - Foresight/analysis")

    with open(output_dir / "leonardo_validation_results.json", 'w', encoding='utf-8') as f:
        json.dump(validations, f, indent=2)

    with open(output_dir / "leonardo_validation_report.txt", 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nResults saved to: {output_dir}")
    print(f"  - leonardo_validation_results.json (detailed data)")
    print(f"  - leonardo_validation_report.txt (summary report)")
    print("\n" + "="*80)
    print("Validation complete!")
    print("="*80)


if __name__ == "__main__":
    main()
