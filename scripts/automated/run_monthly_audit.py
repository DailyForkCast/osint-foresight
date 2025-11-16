#!/usr/bin/env python3
"""
Automated Monthly Audit - Chinese Entity Detection System

Runs comprehensive audit suite and generates reports.
Designed to be run monthly via Task Scheduler.

Usage:
    python scripts/automated/run_monthly_audit.py

Output:
    - audit_results/YYYY-MM-DD_audit_report.md
    - audit_results/YYYY-MM-DD_audit_results.json
    - Alerts if pass rate < 90%

Last Updated: 2025-11-03
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "tests"))

from test_comprehensive_audit import ComprehensiveAudit, TestResult


def save_audit_results(results: List[TestResult], output_dir: Path) -> Tuple[str, str]:
    """Save audit results to markdown and JSON"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Calculate statistics
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    pass_rate = 100 * passed / total if total > 0 else 0

    critical = sum(1 for r in results if not r.passed and r.severity == "CRITICAL")
    high = sum(1 for r in results if not r.passed and r.severity == "HIGH")
    medium = sum(1 for r in results if not r.passed and r.severity == "MEDIUM")

    # Save JSON
    json_path = output_dir / f"{timestamp}_audit_results.json"
    json_data = {
        "timestamp": timestamp,
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "critical_failures": critical,
        "high_failures": high,
        "medium_failures": medium,
        "results": [
            {
                "name": r.name,
                "category": r.category,
                "passed": r.passed,
                "severity": r.severity,
                "expected": r.expected,
                "actual": r.actual,
                "evidence": r.evidence
            }
            for r in results
        ]
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)

    # Save Markdown
    md_path = output_dir / f"{timestamp}_audit_report.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Monthly Audit Report\n")
        f.write(f"**Date:** {timestamp}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Total Tests:** {total}\n")
        f.write(f"- **Passed:** {passed}\n")
        f.write(f"- **Failed:** {failed}\n")
        f.write(f"- **Pass Rate:** {pass_rate:.1f}%\n\n")
        f.write(f"## Failures by Severity\n\n")
        f.write(f"- **Critical:** {critical}\n")
        f.write(f"- **High:** {high}\n")
        f.write(f"- **Medium:** {medium}\n\n")

        if critical > 0:
            f.write(f"## CRITICAL FAILURES ⚠️\n\n")
            for r in results:
                if not r.passed and r.severity == "CRITICAL":
                    f.write(f"### {r.name}\n")
                    f.write(f"- **Category:** {r.category}\n")
                    f.write(f"- **Expected:** {r.expected}\n")
                    f.write(f"- **Actual:** {r.actual}\n")
                    f.write(f"- **Evidence:** {r.evidence}\n\n")

        # Pass/Fail status
        if pass_rate >= 90 and critical == 0:
            f.write(f"\n## Status: ✅ PASS\n")
        elif pass_rate >= 80:
            f.write(f"\n## Status: ⚠️ WARNING\n")
        else:
            f.write(f"\n## Status: ❌ FAIL\n")

    return str(md_path), str(json_path)


def send_alert_if_needed(pass_rate: float, critical_failures: int):
    """Send alert if audit fails"""
    if pass_rate < 90 or critical_failures > 0:
        print("\n" + "!"*80)
        print("ALERT: Audit failed minimum standards")
        print(f"Pass Rate: {pass_rate:.1f}% (target: ≥90%)")
        print(f"Critical Failures: {critical_failures} (target: 0)")
        print("!"*80 + "\n")

        # In production, this would send email/Slack notification
        # For now, just print to stdout which Task Scheduler will capture


def main():
    """Run monthly audit"""
    print("="*80)
    print("MONTHLY AUTOMATED AUDIT")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # Create audit instance
    audit = ComprehensiveAudit()

    # Run all phases
    print("Running audit phases...")
    audit.phase1_unicode_attacks()
    audit.phase1_typographic_evasion()
    audit.phase1_abbreviation_attacks()
    audit.phase2_product_vs_entity()
    audit.phase2_geographic_ambiguity()
    audit.phase3_bis_entity_list()
    audit.phase3_taiwan_companies()
    audit.phase3_known_non_chinese()
    audit.phase4_false_positives()
    audit.phase5_opensanctions_sample()

    # Calculate results
    total = len(audit.results)
    passed = sum(1 for r in audit.results if r.passed)
    pass_rate = 100 * passed / total if total > 0 else 0
    critical = sum(1 for r in audit.results if not r.passed and r.severity == "CRITICAL")

    # Save results
    output_dir = project_root / "audit_results"
    md_path, json_path = save_audit_results(audit.results, output_dir)

    print("\n" + "="*80)
    print(f"Audit Complete: {pass_rate:.1f}% pass rate")
    print(f"Reports saved:")
    print(f"  - {md_path}")
    print(f"  - {json_path}")
    print("="*80 + "\n")

    # Send alert if needed
    send_alert_if_needed(pass_rate, critical)

    # Exit code
    if pass_rate >= 90 and critical == 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()
