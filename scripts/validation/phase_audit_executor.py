#!/usr/bin/env python3
"""
Phase-by-Phase Audit Executor
Automated validation of Germany and Italy research against new protocols
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from glob import glob
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhaseAuditExecutor:
    """
    Executes comprehensive phase-by-phase audit of country research
    """

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.artifacts_path = self.base_path / "artifacts"

        # Define critical tests per phase
        self.phase_tests = {
            0: self.audit_phase0_setup,
            1: self.audit_phase1_2_indicators,
            2: self.audit_phase1_2_indicators,
            3: self.audit_phase3_technology,
            4: self.audit_phase4_supply_chain,
            5: self.audit_phase5_7_institutions,
            6: self.audit_phase5_7_institutions,
            7: self.audit_phase5_7_institutions,
            8: self.audit_phase8_risk,  # CRITICAL
            9: self.audit_phase9_13_strategic,
            10: self.audit_phase9_13_strategic,
            11: self.audit_phase9_13_strategic,
            12: self.audit_phase9_13_strategic,
            13: self.audit_phase9_13_strategic
        }

        # Track audit results
        self.audit_log = []

    def run_country_audit(self, country: str) -> Dict[str, Any]:
        """
        Run complete audit for a country
        """
        logger.info(f"Starting audit for {country}")

        audit_results = {
            "country": country,
            "timestamp": datetime.now().isoformat(),
            "phase_results": {},
            "critical_failures": [],
            "re_analysis_required": [],
            "compliance_score": 0.0,
            "priority_score": 0
        }

        # Check each phase
        for phase_num in range(14):
            phase_key = f"phase{phase_num:02d}"
            phase_results = self.audit_phase(country, phase_num)

            audit_results["phase_results"][phase_key] = phase_results

            # Track failures
            if phase_results["status"] == "FAIL":
                audit_results["re_analysis_required"].append(phase_num)

                if phase_num == 8:  # Risk assessment is critical
                    audit_results["critical_failures"].append({
                        "phase": 8,
                        "failures": phase_results["failed_tests"],
                        "severity": "CRITICAL"
                    })

        # Calculate scores
        audit_results["compliance_score"] = self.calculate_compliance_score(audit_results)
        audit_results["priority_score"] = self.calculate_priority_score(audit_results)

        # Generate recommendations
        audit_results["recommendations"] = self.generate_recommendations(audit_results)

        return audit_results

    def audit_phase(self, country: str, phase_num: int) -> Dict[str, Any]:
        """
        Audit a specific phase for a country
        """
        phase_key = f"phase{phase_num:02d}"

        # Find artifacts
        country_path = self.artifacts_path / country / "_national"
        phase_files = list(country_path.glob(f"{phase_key}*.json"))

        result = {
            "phase": phase_num,
            "status": "PASS",
            "artifacts_found": len(phase_files),
            "tests_run": [],
            "passed_tests": [],
            "failed_tests": [],
            "warnings": []
        }

        # Check if phase exists
        if not phase_files:
            result["status"] = "MISSING"
            result["failed_tests"].append("No artifacts found")
            return result

        # Run phase-specific tests
        if phase_num in self.phase_tests:
            test_results = self.phase_tests[phase_num](country, phase_files)
            result["tests_run"] = test_results["tests_run"]
            result["passed_tests"] = test_results["passed"]
            result["failed_tests"] = test_results["failed"]
            result["warnings"] = test_results.get("warnings", [])

            # Determine overall status
            if test_results["failed"]:
                result["status"] = "FAIL"
            elif test_results.get("warnings"):
                result["status"] = "PARTIAL"

        return result

    def audit_phase0_setup(self, country: str, files: List[Path]) -> Dict:
        """Audit Phase 0: Setup and Scoping"""
        results = {
            "tests_run": [],
            "passed": [],
            "failed": [],
            "warnings": []
        }

        tests = {
            "threat_specificity": False,
            "mcf_sources_initialized": False,
            "conference_baseline": False,
            "ror_configured": False
        }

        # Check each file
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Test: Threat specificity
            if "threat" in str(data).lower() or "china" in str(data).lower():
                # Check if threats are specific
                threat_text = str(data).lower()
                if any(specific in threat_text for specific in
                       ["pla", "mss", "unit", "apt", "specific"]):
                    tests["threat_specificity"] = True
                else:
                    results["warnings"].append("Generic threat descriptions found")

            # Test: MCF sources
            if any(mcf in str(data).lower() for mcf in ["ror", "orcid", "openaire"]):
                tests["mcf_sources_initialized"] = True

            # Test: Conference baseline
            if "conference" in str(data).lower() or "event" in str(data).lower():
                tests["conference_baseline"] = True

        # Compile results
        for test_name, passed in tests.items():
            results["tests_run"].append(test_name)
            if passed:
                results["passed"].append(test_name)
            else:
                results["failed"].append(test_name)

        return results

    def audit_phase1_2_indicators(self, country: str, files: List[Path]) -> Dict:
        """Audit Phase 1-2: Indicators and Metrics"""
        results = {
            "tests_run": [],
            "passed": [],
            "failed": [],
            "warnings": []
        }

        tests = {
            "confidence_scale_0_1": False,
            "uncertainty_present": False,
            "multiple_sources": False,
            "statistical_baseline": False,
            "counterfactual_baseline": False
        }

        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Test: Confidence scale
            confidence_values = self.extract_confidence_values(data)
            if confidence_values:
                if all(0 <= v <= 1.0 for v in confidence_values):
                    tests["confidence_scale_0_1"] = True
                elif any(v > 1.0 for v in confidence_values):
                    results["warnings"].append(f"Found confidence values >1: {max(confidence_values)}")

            # Test: Uncertainty bands
            if self.check_uncertainty_present(data):
                tests["uncertainty_present"] = True

            # Test: Multiple sources
            if "sources" in str(data) and isinstance(data.get("sources"), list):
                if len(data.get("sources", [])) >= 2:
                    tests["multiple_sources"] = True

            # Test: Statistical baseline
            if any(term in str(data).lower() for term in
                   ["baseline", "average", "normal", "typical"]):
                tests["statistical_baseline"] = True

        # Compile results
        for test_name, passed in tests.items():
            results["tests_run"].append(test_name)
            if passed:
                results["passed"].append(test_name)
            else:
                results["failed"].append(test_name)

        return results

    def audit_phase3_technology(self, country: str, files: List[Path]) -> Dict:
        """Audit Phase 3: Technology Landscape"""
        results = {
            "tests_run": [],
            "passed": [],
            "failed": [],
            "warnings": []
        }

        tests = {
            "technology_specificity": False,
            "ror_normalization": False,
            "counterfactual_analysis": False,
            "china_overlap_specific": False,
            "leonardo_standard": False
        }

        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Test: Technology specificity (Leonardo standard)
            tech_text = str(data).lower()
            if any(specific in tech_text for specific in
                   ["model", "version", "specification", "trl", "aw139", "mh-139"]):
                tests["technology_specificity"] = True
                tests["leonardo_standard"] = True

            # Test: ROR normalization
            if "ror" in tech_text or "org_ror" in str(data):
                tests["ror_normalization"] = True

            # Test: Counterfactual analysis
            if any(term in tech_text for term in
                   ["counterfactual", "opposite", "contradictory", "alternative"]):
                tests["counterfactual_analysis"] = True

            # Test: China overlap specificity
            if "china" in tech_text and any(term in tech_text for term in
                                           ["exact", "same", "identical", "overlap"]):
                tests["china_overlap_specific"] = True

        # Compile results
        for test_name, passed in tests.items():
            results["tests_run"].append(test_name)
            if passed:
                results["passed"].append(test_name)
            else:
                results["failed"].append(test_name)

        return results

    def audit_phase4_supply_chain(self, country: str, files: List[Path]) -> Dict:
        """Audit Phase 4: Supply Chain Dependencies"""
        results = {
            "tests_run": [],
            "passed": [],
            "failed": [],
            "warnings": []
        }

        tests = {
            "component_specificity": False,
            "china_dependency_quantified": False,
            "code_dependencies": False,
            "baseline_comparison": False,
            "alternatives_assessed": False
        }

        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            supply_text = str(data).lower()

            # Test: Component specificity
            if any(term in supply_text for term in
                   ["part number", "specification", "grade", "model"]):
                tests["component_specificity"] = True

            # Test: China dependency quantification
            if "china" in supply_text and any(char in str(data) for char in ["%", "percent"]):
                tests["china_dependency_quantified"] = True

            # Test: Code dependencies
            if any(term in supply_text for term in
                   ["github", "pypi", "npm", "libraries.io", "package"]):
                tests["code_dependencies"] = True

            # Test: Baseline comparison
            if any(term in supply_text for term in
                   ["global average", "industry standard", "baseline", "typical"]):
                tests["baseline_comparison"] = True

            # Test: Alternatives
            if "alternative" in supply_text or "substitute" in supply_text:
                tests["alternatives_assessed"] = True

        # Compile results
        for test_name, passed in tests.items():
            results["tests_run"].append(test_name)
            if passed:
                results["passed"].append(test_name)
            else:
                results["failed"].append(test_name)

        return results

    def audit_phase5_7_institutions(self, country: str, files: List[Path]) -> Dict:
        """Audit Phase 5-7: Institutions, Funding, and Links"""
        results = {
            "tests_run": [],
            "passed": [],
            "failed": [],
            "warnings": []
        }

        tests = {
            "institution_normalization": False,
            "funding_transparency": False,
            "conference_connections": False,
            "standards_participation": False,
            "counterfactual_partnerships": False
        }

        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            content = str(data).lower()

            # Test: Institution normalization
            if "ror" in content or "org_ror" in str(data):
                tests["institution_normalization"] = True

            # Test: Funding transparency
            if any(term in content for term in
                   ["lei", "beneficial owner", "ultimate parent", "opensanctions"]):
                tests["funding_transparency"] = True

            # Test: Conference connections
            if "conference" in content and any(term in content for term in
                                              ["partnership", "met", "formed"]):
                tests["conference_connections"] = True

            # Test: Standards participation
            if any(term in content for term in
                   ["ietf", "w3c", "3gpp", "etsi", "standards"]):
                tests["standards_participation"] = True

            # Test: Counterfactual partnerships
            if "partnership" in content and any(term in content for term in
                                               ["non-china", "comparison", "baseline"]):
                tests["counterfactual_partnerships"] = True

        # Compile results
        for test_name, passed in tests.items():
            results["tests_run"].append(test_name)
            if passed:
                results["passed"].append(test_name)
            else:
                results["failed"].append(test_name)

        return results

    def audit_phase8_risk(self, country: str, files: List[Path]) -> Dict:
        """Audit Phase 8: Risk Assessment - CRITICAL"""
        results = {
            "tests_run": [],
            "passed": [],
            "failed": [],
            "warnings": []
        }

        tests = {
            "risk_specificity": False,
            "counterfactual_validation": False,
            "confidence_calibration": False,
            "alternative_hypotheses": False,
            "bombshell_validation": False,
            "oversight_gaps": False
        }

        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            risk_text = str(data).lower()

            # Test: Risk specificity
            if any(term in risk_text for term in
                   ["specific", "exact", "yolo", "aw139", "detailed"]):
                tests["risk_specificity"] = True
            elif "risk" in risk_text and len(risk_text) < 100:
                results["warnings"].append("Risk descriptions too generic")

            # Test: Counterfactual validation
            if any(term in risk_text for term in
                   ["counterfactual", "contradictory", "opposite", "disconfirming"]):
                tests["counterfactual_validation"] = True

            # Test: Confidence calibration
            confidence_values = self.extract_confidence_values(data)
            if confidence_values and all(0 <= v <= 1.0 for v in confidence_values):
                if self.check_uncertainty_present(data):
                    tests["confidence_calibration"] = True

            # Test: Alternative hypotheses
            if any(term in risk_text for term in
                   ["alternative", "benign", "commercial", "hypothesis"]):
                tests["alternative_hypotheses"] = True

            # Test: Bombshell validation
            if "bombshell" in risk_text or "extraordinary" in risk_text:
                tests["bombshell_validation"] = True

            # Test: Oversight gaps
            if any(term in risk_text for term in
                   ["oversight", "gap", "vulnerability", "silo"]):
                tests["oversight_gaps"] = True

        # Compile results
        for test_name, passed in tests.items():
            results["tests_run"].append(test_name)
            if passed:
                results["passed"].append(test_name)
            else:
                results["failed"].append(test_name)

        # Phase 8 failures are critical
        if results["failed"]:
            results["warnings"].append("CRITICAL: Phase 8 validation failures require immediate attention")

        return results

    def audit_phase9_13_strategic(self, country: str, files: List[Path]) -> Dict:
        """Audit Phase 9-13: Strategic Analysis"""
        results = {
            "tests_run": [],
            "passed": [],
            "failed": [],
            "warnings": []
        }

        tests = {
            "negative_evidence": False,
            "forecast_uncertainty": False,
            "deception_indicators": False,
            "policy_validation": False
        }

        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            content = str(data).lower()

            # Test: Negative evidence
            if any(term in content for term in
                   ["not found", "negative", "absent", "missing", "contradiction"]):
                tests["negative_evidence"] = True

            # Test: Forecast uncertainty
            if "forecast" in content and any(term in content for term in
                                            ["uncertainty", "confidence", "probability", "scenario"]):
                tests["forecast_uncertainty"] = True

            # Test: Deception indicators
            if "deception" in str(file_path).lower() or "deception" in content:
                tests["deception_indicators"] = True

            # Test: Policy validation
            if "policy" in content and any(term in content for term in
                                          ["evidence", "confidence", "validation"]):
                tests["policy_validation"] = True

        # Compile results
        for test_name, passed in tests.items():
            results["tests_run"].append(test_name)
            if passed:
                results["passed"].append(test_name)
            else:
                results["failed"].append(test_name)

        return results

    def extract_confidence_values(self, data: Any) -> List[float]:
        """Extract all confidence values from nested data"""
        values = []

        if isinstance(data, dict):
            for key, value in data.items():
                if "confidence" in key.lower() and isinstance(value, (int, float)):
                    values.append(float(value))
                elif isinstance(value, (dict, list)):
                    values.extend(self.extract_confidence_values(value))
        elif isinstance(data, list):
            for item in data:
                values.extend(self.extract_confidence_values(item))

        return values

    def check_uncertainty_present(self, data: Any) -> bool:
        """Check if uncertainty bands are present"""
        data_str = str(data).lower()
        return any(term in data_str for term in
                  ["uncertainty", "range", "±", "plus_minus", "error", "band"])

    def calculate_compliance_score(self, audit_results: Dict) -> float:
        """Calculate overall compliance score (0-100)"""
        total_tests = 0
        passed_tests = 0

        for phase_results in audit_results["phase_results"].values():
            if phase_results["status"] != "MISSING":
                total_tests += len(phase_results["tests_run"])
                passed_tests += len(phase_results["passed_tests"])

        if total_tests == 0:
            return 0.0

        return round((passed_tests / total_tests) * 100, 1)

    def calculate_priority_score(self, audit_results: Dict) -> int:
        """
        Calculate re-analysis priority score
        Higher score = more urgent
        """
        score = 0

        # Critical phase failures
        if 8 in audit_results["re_analysis_required"]:
            score += 100  # Phase 8 is most critical

        # Missing phases
        for phase_results in audit_results["phase_results"].values():
            if phase_results["status"] == "MISSING":
                score += 20

        # Failed validations
        for phase_results in audit_results["phase_results"].values():
            if phase_results["status"] == "FAIL":
                score += 10 * len(phase_results["failed_tests"])

        # Partial passes
        for phase_results in audit_results["phase_results"].values():
            if phase_results["status"] == "PARTIAL":
                score += 5

        return score

    def generate_recommendations(self, audit_results: Dict) -> List[Dict]:
        """Generate prioritized recommendations"""
        recommendations = []

        # Check Phase 8 first (critical)
        phase8_results = audit_results["phase_results"].get("phase08", {})
        if phase8_results.get("status") in ["FAIL", "MISSING"]:
            recommendations.append({
                "priority": "CRITICAL",
                "phase": 8,
                "action": "Complete Phase 8 risk assessment with counterfactual validation",
                "reason": "Risk assessment is critical for decision-making"
            })

        # Check for missing phases
        for phase_key, results in audit_results["phase_results"].items():
            if results["status"] == "MISSING":
                phase_num = int(phase_key.replace("phase", ""))
                if phase_num != 8:  # Already handled above
                    recommendations.append({
                        "priority": "HIGH" if phase_num in [2, 3, 4] else "MEDIUM",
                        "phase": phase_num,
                        "action": f"Complete Phase {phase_num}",
                        "reason": "Missing phase data"
                    })

        # Check for specific test failures
        critical_tests = [
            "counterfactual_validation",
            "confidence_calibration",
            "ror_normalization"
        ]

        for phase_key, results in audit_results["phase_results"].items():
            for test in results.get("failed_tests", []):
                if test in critical_tests:
                    phase_num = int(phase_key.replace("phase", ""))
                    recommendations.append({
                        "priority": "HIGH",
                        "phase": phase_num,
                        "action": f"Fix {test} in Phase {phase_num}",
                        "reason": "Critical validation requirement"
                    })

        # Sort by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 4))

        return recommendations

    def generate_audit_report(self, audit_results: Dict) -> str:
        """Generate human-readable audit report"""
        report = []
        report.append(f"\n{'='*70}")
        report.append(f"AUDIT REPORT: {audit_results['country']}")
        report.append(f"Timestamp: {audit_results['timestamp']}")
        report.append(f"{'='*70}\n")

        # Summary
        report.append(f"COMPLIANCE SCORE: {audit_results['compliance_score']}%")
        report.append(f"PRIORITY SCORE: {audit_results['priority_score']} (higher = more urgent)")
        report.append(f"PHASES REQUIRING RE-ANALYSIS: {len(audit_results['re_analysis_required'])}")

        if audit_results['critical_failures']:
            report.append(f"\n!!! CRITICAL FAILURES:")
            for failure in audit_results['critical_failures']:
                report.append(f"  - Phase {failure['phase']}: {', '.join(failure['failures'])}")

        # Phase-by-phase results
        report.append(f"\nPHASE-BY-PHASE RESULTS:")
        for phase_key, results in audit_results['phase_results'].items():
            status_text = {
                "PASS": "[PASS]",
                "PARTIAL": "[PARTIAL]",
                "FAIL": "[FAIL]",
                "MISSING": "[MISSING]"
            }
            status = status_text.get(results['status'], "[UNKNOWN]")

            report.append(f"\n{status} {phase_key.upper()}:")
            report.append(f"  Status: {results['status']}")
            report.append(f"  Artifacts: {results['artifacts_found']}")

            if results['passed_tests']:
                report.append(f"  + Passed: {', '.join(results['passed_tests'])}")

            if results['failed_tests']:
                report.append(f"  - Failed: {', '.join(results['failed_tests'])}")

            if results['warnings']:
                report.append(f"  ! Warnings: {', '.join(results['warnings'])}")

        # Recommendations
        if audit_results['recommendations']:
            report.append(f"\n{'='*70}")
            report.append("PRIORITIZED RECOMMENDATIONS:")
            for i, rec in enumerate(audit_results['recommendations'][:10], 1):
                report.append(f"\n{i}. [{rec['priority']}] Phase {rec['phase']}")
                report.append(f"   Action: {rec['action']}")
                report.append(f"   Reason: {rec['reason']}")

        report.append(f"\n{'='*70}\n")

        return '\n'.join(report)

def run_comprehensive_audit():
    """Main execution function"""
    print("="*70)
    print("PHASE-BY-PHASE AUDIT EXECUTOR")
    print("Validating Germany and Italy Research")
    print("="*70)

    auditor = PhaseAuditExecutor()

    # Audit both countries
    countries = ["Italy", "Germany", "Germany_consolidated"]

    all_results = {}

    for country in countries:
        country_path = Path("artifacts") / country
        if country_path.exists():
            print(f"\nAuditing {country}...")
            results = auditor.run_country_audit(country)
            all_results[country] = results

            # Generate and print report
            report = auditor.generate_audit_report(results)
            print(report)

            # Save detailed results
            output_file = Path(f"audit_results_{country}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Detailed results saved to: {output_file}")

    # Compare countries
    print("\n" + "="*70)
    print("COMPARATIVE ANALYSIS")
    print("="*70)

    for country, results in all_results.items():
        print(f"\n{country}:")
        print(f"  Compliance: {results['compliance_score']}%")
        print(f"  Priority: {results['priority_score']}")
        print(f"  Re-analysis needed: {len(results['re_analysis_required'])} phases")

    return all_results

if __name__ == "__main__":
    run_comprehensive_audit()
