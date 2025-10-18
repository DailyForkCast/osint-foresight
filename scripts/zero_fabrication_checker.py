#!/usr/bin/env python3
"""
Zero Fabrication Compliance Checker
Automatically scans scripts and documents for potential fabrication violations

USAGE: python scripts/zero_fabrication_checker.py [directory]

This script enforces the zero fabrication protocol established after
the Web of Science incident where we claimed data we didn't have.
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class ZeroFabricationChecker:
    """Check files for compliance with zero fabrication protocol"""

    def __init__(self):
        # Forbidden terms that suggest fabrication
        self.forbidden_terms = [
            r'\btypically\b', r'\busually\b', r'\bgenerally\b', r'\bnormally\b',
            r'\blikely\b', r'\bprobably\b', r'\bpresumably\b',
            r'\bestimated?\b', r'\bexpected?\b', r'\banticipated?\b',
            r'\bprojected?\b', r'\bassumed?\b', r'\binferred?\b',
            r'reasonable to assume', r'industry standard', r'comparable systems',
            r'based on typical', r'it is estimated', r'approximately \d+%',
            r'roughly \d+', r'about \d+%', r'~\d+%'
        ]

        # Required protocol markers
        self.required_markers = [
            'ZERO FABRICATION',
            'no data available',
            'cannot determine',
            'detected', 'found', 'measured', 'analyzed'
        ]

        # Allowed exceptions (in comments or specific contexts)
        self.allowed_contexts = [
            'HYPOTHETICAL EXAMPLE',
            'ILLUSTRATIVE ONLY',
            'PROJECTION - NOT VERIFIED',
            'TODO:', 'FIXME:', 'NOTE:'
        ]

        self.violations = []
        self.warnings = []
        self.compliant_files = []

    def check_file(self, filepath: Path) -> Dict:
        """Check a single file for compliance"""

        if not filepath.exists():
            return {"error": f"File not found: {filepath}"}

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            return {"error": f"Could not read {filepath}: {e}"}

        violations = []
        warnings = []
        has_protocol = False

        # Check for zero fabrication protocol header
        if 'ZERO FABRICATION' in content.upper():
            has_protocol = True

        # Check each line for violations
        for i, line in enumerate(lines, 1):
            # Skip comment lines in code
            if line.strip().startswith('#') or line.strip().startswith('//'):
                # Still check comments for protocol compliance
                if not any(marker in line for marker in self.allowed_contexts):
                    for pattern in self.forbidden_terms[:5]:  # Check key terms only
                        if re.search(pattern, line, re.IGNORECASE):
                            warnings.append({
                                'line': i,
                                'text': line.strip(),
                                'issue': f'Forbidden term in comment: {pattern}'
                            })
                continue

            # Check for forbidden terms
            for pattern in self.forbidden_terms:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check if it's in an allowed context
                    if not any(ctx in line for ctx in self.allowed_contexts):
                        violations.append({
                            'line': i,
                            'text': line.strip(),
                            'pattern': pattern,
                            'severity': 'HIGH'
                        })

        # Check for missing protocol in Python/script files
        if filepath.suffix in ['.py', '.sh'] and not has_protocol:
            warnings.append({
                'line': 0,
                'text': 'File header',
                'issue': 'Missing ZERO FABRICATION protocol declaration'
            })

        return {
            'file': str(filepath),
            'has_protocol': has_protocol,
            'violations': violations,
            'warnings': warnings,
            'compliant': len(violations) == 0 and has_protocol
        }

    def check_directory(self, directory: Path) -> Dict:
        """Recursively check all Python files in directory"""

        results = {
            'checked': [],
            'violations': [],
            'warnings': [],
            'compliant': [],
            'summary': {}
        }

        # Find all Python files
        py_files = list(directory.rglob('*.py'))

        print(f"Checking {len(py_files)} Python files in {directory}...")

        for filepath in py_files:
            # Skip virtual environments and cache
            if any(skip in str(filepath) for skip in ['venv', '__pycache__', '.git']):
                continue

            result = self.check_file(filepath)

            if 'error' in result:
                print(f"Error: {result['error']}")
                continue

            results['checked'].append(str(filepath))

            if result['violations']:
                results['violations'].append(result)
                print(f"[X] {filepath.name}: {len(result['violations'])} violations")
            elif result['warnings']:
                results['warnings'].append(result)
                print(f"[!] {filepath.name}: {len(result['warnings'])} warnings")
            elif result['compliant']:
                results['compliant'].append(str(filepath))
                print(f"[OK] {filepath.name}: Compliant")
            else:
                print(f"[?] {filepath.name}: Needs review")

        # Generate summary
        results['summary'] = {
            'total_files': len(results['checked']),
            'compliant': len(results['compliant']),
            'with_violations': len(results['violations']),
            'with_warnings': len(results['warnings']),
            'compliance_rate': round(len(results['compliant']) / max(len(results['checked']), 1) * 100, 1)
        }

        return results

    def generate_report(self, results: Dict) -> str:
        """Generate compliance report"""

        report = f"""
# Zero Fabrication Compliance Report
Generated: {datetime.now().isoformat()}

## Summary
- **Files Checked:** {results['summary']['total_files']}
- **Fully Compliant:** {results['summary']['compliant']} ({results['summary']['compliance_rate']}%)
- **With Violations:** {results['summary']['with_violations']}
- **With Warnings:** {results['summary']['with_warnings']}

"""

        if results['violations']:
            report += "## Critical Violations\n\n"
            for file_result in results['violations']:
                report += f"### {Path(file_result['file']).name}\n"
                for v in file_result['violations'][:5]:  # Show first 5
                    report += f"- Line {v['line']}: `{v['pattern']}` found\n"
                    report += f"  ```{v['text'][:100]}...```\n"
                report += "\n"

        if results['warnings']:
            report += "## Warnings\n\n"
            for file_result in results['warnings'][:10]:  # Show first 10
                report += f"- {Path(file_result['file']).name}: {file_result['warnings'][0]['issue']}\n"

        report += """
## Required Actions

1. **For Violations:** Add zero fabrication protocol header and remove forbidden terms
2. **For Warnings:** Add protocol declaration to file headers
3. **For All Files:** Replace estimation language with factual reporting

## Forbidden Terms to Remove
- typically, usually, generally, normally
- likely, probably, presumably
- estimated, expected, anticipated, projected
- "reasonable to assume", "industry standard"

## Required Replacements
- Use: detected, found, measured, analyzed
- Use: "no data available" for missing data
- Use: "cannot determine" for unknowns

## Remember
Every fabrication undermines all analysis. When in doubt, report "no data available".
"""

        return report

def main():
    """Main entry point"""

    # Determine directory to check
    if len(sys.argv) > 1:
        check_dir = Path(sys.argv[1])
    else:
        check_dir = Path('scripts')

    if not check_dir.exists():
        print(f"Error: Directory {check_dir} not found")
        sys.exit(1)

    print(f"\n{'='*60}")
    print("Zero Fabrication Compliance Checker")
    print(f"{'='*60}\n")

    checker = ZeroFabricationChecker()
    results = checker.check_directory(check_dir)

    # Generate and save report
    report = checker.generate_report(results)

    report_path = Path('docs/reports/zero_fabrication_compliance.md')
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReport saved to: {report_path}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Compliance Rate: {results['summary']['compliance_rate']}%")
    print(f"Action Required: {results['summary']['with_violations']} files need immediate fixes")
    print(f"{'='*60}\n")

    # Exit with error if violations found
    if results['summary']['with_violations'] > 0:
        sys.exit(1)
    else:
        print("[SUCCESS] All checked files are compliant!")

if __name__ == '__main__':
    main()
