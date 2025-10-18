#!/usr/bin/env python3
"""
validate_documentation.py - Documentation Validation System

Validates project documentation to prevent outdated statistics and maintain quality:
- Checks for old database statistics (3.6 GB, 132 tables, 16.8M records)
- Verifies Tier 1+2 files contain current statistics
- Ensures archive structure is maintained
- Validates ARCHIVE_INDEX.md files exist
- Can be used as git pre-commit hook

Usage:
    python validate_documentation.py              # Validate all documentation
    python validate_documentation.py --fix        # Auto-fix issues where possible
    python validate_documentation.py --hook       # Run as git pre-commit hook (exit 1 on failure)
    python validate_documentation.py --tier 1     # Validate only Tier 1 files
"""

import os
import re
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import argparse

# Configuration
PROJECT_ROOT = Path("C:/Projects/OSINT - Foresight")

# Current correct values (as of October 2025)
CURRENT_VALUES = {
    'database_size': '23 GB',
    'table_count': '218',
    'active_tables': '159',
    'empty_tables': '59',
    'record_count': '101.3M',
    'patent_count': '577,197'
}

# Old values that should NOT appear in Tier 1+2 documentation
OLD_VALUES = {
    'database_size': ['3.6 GB', '3.6GB', '34 GB', '34GB'],
    'table_count': ['132 tables', '137 tables', '122 tables'],
    'record_count': ['16.8M', '16.8 M', '16.8M+'],
    'patent_count': ['568,324']
}

# Tier 1: Critical Documentation (must be perfect)
TIER1_FILES = [
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "docs/prompts/active/master/CLAUDE_CODE_MASTER_V9.8_COMPLETE.md",
    PROJECT_ROOT / "docs/UNIFIED_DATA_INFRASTRUCTURE_INVENTORY_MULTICOUNTRY.md",
    PROJECT_ROOT / "docs/SCRIPTS_INVENTORY.md"
]

# Tier 2: Architecture Documentation (must be accurate)
TIER2_FILES = [
    PROJECT_ROOT / "KNOWLEDGE_BASE/04_PROJECT_ARCHITECTURE/DATABASE_CONSOLIDATION_REPORT.md",
    PROJECT_ROOT / "KNOWLEDGE_BASE/04_PROJECT_ARCHITECTURE/CONSOLIDATION_COMPLETE_SUMMARY.md",
    PROJECT_ROOT / "KNOWLEDGE_BASE/04_PROJECT_ARCHITECTURE/FINAL_CONSOLIDATION_REPORT.md",
    PROJECT_ROOT / "KNOWLEDGE_BASE/SESSION_SUMMARY_20250929.md"
]

# Archive directories that should have README.md and proper structure
ARCHIVE_DIRS = [
    PROJECT_ROOT / "KNOWLEDGE_BASE/archive",
    PROJECT_ROOT / "analysis/archive"
]


class ValidationResult:
    """Track validation results"""
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []
        self.total_files = 0
        self.files_with_issues = 0

    def add_error(self, file_path, message):
        self.errors.append({'file': str(file_path), 'message': message})
        self.files_with_issues += 1

    def add_warning(self, file_path, message):
        self.warnings.append({'file': str(file_path), 'message': message})

    def add_pass(self, file_path, message):
        self.passed.append({'file': str(file_path), 'message': message})

    def has_errors(self):
        return len(self.errors) > 0

    def summary(self):
        return {
            'total_files': self.total_files,
            'passed': len(self.passed),
            'warnings': len(self.warnings),
            'errors': len(self.errors),
            'files_with_issues': self.files_with_issues
        }


def check_old_values(file_path: Path, content: str, tier: int) -> list:
    """
    Check if file contains old, outdated values.
    Returns list of issues found.
    """
    issues = []

    for category, old_vals in OLD_VALUES.items():
        for old_val in old_vals:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + re.escape(old_val) + r'\b'
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'type': 'old_value',
                    'category': category,
                    'value': old_val,
                    'line': line_num,
                    'severity': 'error' if tier <= 2 else 'warning'
                })

    return issues


def check_current_values(file_path: Path, content: str, tier: int) -> list:
    """
    Check if Tier 1+2 files contain current correct values.
    Returns list of issues found.
    """
    issues = []

    if tier > 2:
        return issues  # Only check Tier 1+2 files

    # Check for current database size
    if '23 GB' not in content and '23GB' not in content:
        issues.append({
            'type': 'missing_current_value',
            'category': 'database_size',
            'expected': '23 GB',
            'severity': 'error'
        })

    # Check for current table count (allow some flexibility in how it's expressed)
    if '218' not in content or '159' not in content:
        issues.append({
            'type': 'missing_current_value',
            'category': 'table_count',
            'expected': '218 tables (159 active, 59 empty)',
            'severity': 'error'
        })

    # Check for current record count
    if '101' not in content or 'M' not in content:
        issues.append({
            'type': 'missing_current_value',
            'category': 'record_count',
            'expected': '101.3M',
            'severity': 'warning'  # Warning because format may vary
        })

    return issues


def validate_file(file_path: Path, tier: int) -> dict:
    """
    Validate a single documentation file.
    Returns dict with validation results.
    """
    if not file_path.exists():
        return {
            'status': 'missing',
            'issues': [{'type': 'missing_file', 'severity': 'error'}]
        }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {
            'status': 'error',
            'issues': [{'type': 'read_error', 'message': str(e), 'severity': 'error'}]
        }

    issues = []

    # Check for old values
    issues.extend(check_old_values(file_path, content, tier))

    # Check for current values (Tier 1+2 only)
    if tier <= 2:
        issues.extend(check_current_values(file_path, content, tier))

    if not issues:
        return {'status': 'pass', 'issues': []}
    else:
        return {'status': 'fail', 'issues': issues}


def validate_archive_structure() -> dict:
    """
    Validate that archive directories have proper structure.
    Returns dict with validation results.
    """
    issues = []

    for archive_dir in ARCHIVE_DIRS:
        if not archive_dir.exists():
            issues.append({
                'type': 'missing_archive_dir',
                'path': str(archive_dir),
                'severity': 'warning'
            })
            continue

        # Check for README.md
        readme = archive_dir / "README.md"
        if not readme.exists():
            issues.append({
                'type': 'missing_archive_readme',
                'path': str(readme),
                'severity': 'error'
            })

        # Check for month directories and their ARCHIVE_INDEX.md
        for month_dir in archive_dir.glob("????-??"):
            if month_dir.is_dir():
                index_file = month_dir / "ARCHIVE_INDEX.md"
                if not index_file.exists():
                    issues.append({
                        'type': 'missing_archive_index',
                        'path': str(index_file),
                        'severity': 'error'
                    })

    return {'issues': issues}


def validate_tier(tier: int, result: ValidationResult):
    """Validate all files in a specific tier"""
    files = []
    tier_name = ""

    if tier == 1:
        files = TIER1_FILES
        tier_name = "Tier 1 (Critical)"
    elif tier == 2:
        files = TIER2_FILES
        tier_name = "Tier 2 (Architecture)"
    else:
        return

    print(f"\n{'='*60}")
    print(f"Validating {tier_name} Documentation")
    print(f"{'='*60}")

    for file_path in files:
        result.total_files += 1
        validation = validate_file(file_path, tier)

        if validation['status'] == 'missing':
            result.add_error(file_path, "File not found")
            print(f"  [ERROR] MISSING: {file_path.name}")

        elif validation['status'] == 'error':
            result.add_error(file_path, validation['issues'][0].get('message', 'Read error'))
            print(f"  [ERROR] ERROR: {file_path.name}")

        elif validation['status'] == 'fail':
            errors = [i for i in validation['issues'] if i['severity'] == 'error']
            warnings = [i for i in validation['issues'] if i['severity'] == 'warning']

            if errors:
                for issue in errors:
                    if issue['type'] == 'old_value':
                        msg = f"Contains old value '{issue['value']}' at line {issue['line']}"
                    else:
                        msg = f"Missing current value: {issue['expected']}"
                    result.add_error(file_path, msg)
                print(f"  [ERROR] FAILED: {file_path.name} ({len(errors)} errors)")

            if warnings:
                for issue in warnings:
                    if issue['type'] == 'old_value':
                        msg = f"Contains old value '{issue['value']}' at line {issue['line']}"
                    else:
                        msg = f"Missing current value: {issue['expected']}"
                    result.add_warning(file_path, msg)
                print(f"  [WARNING]  WARNING: {file_path.name} ({len(warnings)} warnings)")

        else:  # pass
            result.add_pass(file_path, "All checks passed")
            print(f"  [OK] PASSED: {file_path.name}")


def run_validation(args):
    """Main validation logic"""
    result = ValidationResult()

    print(f"\n{'#'*60}")
    print("# OSINT Foresight - Documentation Validation")
    print(f"# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}")

    # Validate specified tiers
    if args.tier is None or args.tier == 1:
        validate_tier(1, result)

    if args.tier is None or args.tier == 2:
        validate_tier(2, result)

    # Validate archive structure
    if args.tier is None:
        print(f"\n{'='*60}")
        print("Validating Archive Structure")
        print(f"{'='*60}")

        archive_validation = validate_archive_structure()
        for issue in archive_validation['issues']:
            if issue['severity'] == 'error':
                result.add_error(Path(issue['path']), f"Archive issue: {issue['type']}")
                print(f"  [ERROR] {issue['type']}: {issue['path']}")
            else:
                result.add_warning(Path(issue['path']), f"Archive issue: {issue['type']}")
                print(f"  [WARNING]  {issue['type']}: {issue['path']}")

        if not archive_validation['issues']:
            print("  [OK] Archive structure valid")

    # Print summary
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}")
    summary = result.summary()
    print(f"Total Files: {summary['total_files']}")
    print(f"Passed:      {summary['passed']}")
    print(f"Warnings:    {summary['warnings']}")
    print(f"Errors:      {summary['errors']}")
    print(f"{'='*60}")

    # Print details
    if result.errors:
        print(f"\n[ERROR] ERRORS ({len(result.errors)}):")
        for error in result.errors:
            print(f"  - {Path(error['file']).name}: {error['message']}")

    if result.warnings:
        print(f"\n[WARNING]  WARNINGS ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"  - {Path(warning['file']).name}: {warning['message']}")

    # Save report
    if not args.hook:
        report_path = PROJECT_ROOT / "analysis" / f"VALIDATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'errors': result.errors,
            'warnings': result.warnings,
            'passed': result.passed
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n[FILE] Report saved: {report_path}")

    # Return appropriate exit code
    if args.hook:
        if result.has_errors():
            print("\n[BLOCKED] VALIDATION FAILED - Commit blocked")
            print("   Fix errors above before committing.")
            return 1
        else:
            print("\n[OK] VALIDATION PASSED - OK to commit")
            return 0
    else:
        return 1 if result.has_errors() else 0


def main():
    parser = argparse.ArgumentParser(
        description="Validate OSINT Foresight documentation"
    )
    parser.add_argument(
        "--hook",
        action="store_true",
        help="Run as git pre-commit hook (exit 1 on failure)"
    )
    parser.add_argument(
        "--tier",
        type=int,
        choices=[1, 2],
        help="Validate only specific tier (1 or 2)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix issues where possible (future feature)"
    )

    args = parser.parse_args()

    if args.fix:
        print("[WARNING]  Auto-fix feature not yet implemented")
        return 1

    exit_code = run_validation(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
