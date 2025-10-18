#!/usr/bin/env python3
"""
Schedule regular fabrication checks for the OSINT Foresight project
Can be run as a scheduled task or cron job
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json

def run_fabrication_check():
    """Run the fabrication checker and return results"""
    script_path = Path("C:/Projects/OSINT - Foresight/scripts/fabrication_checker.py")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Read the JSON report for analysis
        report_path = Path("C:/Projects/OSINT - Foresight/docs/reports/FABRICATION_CHECK_REPORT.json")
        if report_path.exists():
            with open(report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)

            return {
                'success': True,
                'exit_code': result.returncode,
                'high_severity': report['high_severity'],
                'medium_severity': report['medium_severity'],
                'total_issues': report['total_issues'],
                'timestamp': report['timestamp']
            }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Check timed out after 60 seconds'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def check_threshold_violations(results):
    """Check if issues exceed acceptable thresholds"""
    violations = []

    # Define thresholds
    THRESHOLDS = {
        'high_severity': 0,  # Zero tolerance for high severity
        'medium_severity': 50,  # Allow some medium issues
        'total_issues': 100  # Overall limit
    }

    if results.get('high_severity', 0) > THRESHOLDS['high_severity']:
        violations.append(f"HIGH SEVERITY: {results['high_severity']} issues (threshold: {THRESHOLDS['high_severity']})")

    if results.get('medium_severity', 0) > THRESHOLDS['medium_severity']:
        violations.append(f"MEDIUM SEVERITY: {results['medium_severity']} issues (threshold: {THRESHOLDS['medium_severity']})")

    if results.get('total_issues', 0) > THRESHOLDS['total_issues']:
        violations.append(f"TOTAL ISSUES: {results['total_issues']} (threshold: {THRESHOLDS['total_issues']})")

    return violations

def log_results(results, violations):
    """Log check results to a history file"""
    log_path = Path("C:/Projects/OSINT - Foresight/docs/reports/fabrication_check_history.jsonl")

    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'results': results,
        'violations': violations,
        'action_required': len(violations) > 0
    }

    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')

def main():
    """Main scheduled check routine"""
    print(f"Starting scheduled fabrication check at {datetime.utcnow().isoformat()}")

    # Run the check
    results = run_fabrication_check()

    if not results['success']:
        print(f"ERROR: Check failed - {results.get('error', 'Unknown error')}")
        return 1

    # Check for threshold violations
    violations = check_threshold_violations(results)

    # Log results
    log_results(results, violations)

    # Report status
    if violations:
        print("\nTHRESHOLD VIOLATIONS DETECTED:")
        for violation in violations:
            print(f"  - {violation}")
        print(f"\nAction required! Review report at: docs/reports/FABRICATION_CHECK_REPORT.md")
        return 1
    else:
        print(f"\nCheck passed. Issues within acceptable limits.")
        print(f"  High: {results['high_severity']} | Medium: {results['medium_severity']} | Total: {results['total_issues']}")
        return 0

if __name__ == "__main__":
    exit(main())
