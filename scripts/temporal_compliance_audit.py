#!/usr/bin/env python3
"""
Temporal Compliance Audit Script
Scans all documents for temporal awareness issues based on current date Sept 13, 2025
"""

import re
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Tuple, Any
import json

# Current analysis date
CURRENT_DATE = date(2025, 9, 13)
CURRENT_YEAR = 2025


class TemporalComplianceAuditor:
    """Audit documents for temporal compliance issues."""

    def __init__(self):
        self.current_date = CURRENT_DATE
        self.issues = {}
        self.patterns = {
            'past_targets': [
                r'by (?:end of )?2024',
                r'in 2024',
                r'for 2024',
                r'2024 targets?',
                r'achieve.*2024',
                r'implement.*2024',
                r'by early 2025',
                r'by Q[12] 2025',
                r'by (?:January|February|March|April|May|June|July|August) 2025',
            ],
            'unrealistic_immediate': [
                r'immediate(?:ly)?\s+(?:achieve|implement|deploy|result)',
                r'by end of (?:this year|2025)',
                r'within (?:weeks|days)',
                r'quick wins? by 2025',
                r'before (?:October|November|December) 2025',
            ],
            'budget_issues': [
                r'FY\s?2025 budget',
                r'FY\s?2026 budget (?:increase|allocation|adjustment)',
                r'2025 fiscal year funding',
                r'adjust.*2025 budget',
            ],
            'timeline_issues': [
                r'(?:complete|finish|achieve).*(?:by|in) (?:Q3|Q4) 2025',
                r'2024-2025 (?:period|timeline|goals)',
                r'immediate deployment',
                r'rapid implementation by 2025',
            ]
        }

    def scan_file(self, file_path: Path) -> Dict[str, Any]:
        """Scan a single file for temporal compliance issues."""
        issues = {
            'file': str(file_path),
            'past_targets': [],
            'unrealistic_immediate': [],
            'budget_issues': [],
            'timeline_issues': [],
            'severity': 'low',  # low, medium, high, critical
            'recommendation': 'keep'  # keep, fix, archive
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Skip if file is empty
            if not content.strip():
                return issues

            # Check each pattern category
            for category, patterns in self.patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        context = self._get_context(content, match.start(), match.end())
                        issues[category].append({
                            'match': match.group(),
                            'context': context,
                            'line': content[:match.start()].count('\n') + 1
                        })

            # Calculate severity
            total_issues = sum(len(issues[cat]) for cat in self.patterns.keys())
            if total_issues == 0:
                issues['severity'] = 'compliant'
                issues['recommendation'] = 'keep'
            elif total_issues <= 2:
                issues['severity'] = 'low'
                issues['recommendation'] = 'fix'
            elif total_issues <= 5:
                issues['severity'] = 'medium'
                issues['recommendation'] = 'fix'
            elif total_issues <= 10:
                issues['severity'] = 'high'
                issues['recommendation'] = 'fix' if 'phase' in str(file_path) else 'archive'
            else:
                issues['severity'] = 'critical'
                issues['recommendation'] = 'archive'

            # Special handling for certain file types
            if 'archive' in str(file_path):
                issues['recommendation'] = 'already_archived'
            elif 'executive' in str(file_path).lower() or 'policy' in str(file_path).lower():
                if total_issues > 0:
                    issues['recommendation'] = 'fix'  # Always fix executive/policy briefs

        except Exception as e:
            issues['error'] = str(e)
            issues['recommendation'] = 'review'

        return issues

    def _get_context(self, text: str, start: int, end: int, window: int = 100) -> str:
        """Get context around a match."""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        context = text[context_start:context_end]
        # Clean up whitespace
        context = ' '.join(context.split())
        return f"...{context}..."

    def scan_directory(self, directory: Path, pattern: str = "*.md") -> Dict[str, List[Dict]]:
        """Scan all files in a directory."""
        results = {
            'compliant': [],
            'low': [],
            'medium': [],
            'high': [],
            'critical': [],
            'errors': []
        }

        files = list(directory.rglob(pattern))
        print(f"Scanning {len(files)} files in {directory}")

        for file_path in files:
            issues = self.scan_file(file_path)
            severity = issues.get('severity', 'error')

            if 'error' in issues:
                results['errors'].append(issues)
            else:
                results[severity].append(issues)

        return results

    def generate_report(self, results: Dict[str, List[Dict]]) -> str:
        """Generate compliance report."""
        report = []
        report.append("# TEMPORAL COMPLIANCE AUDIT REPORT")
        report.append(f"\n*Audit Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        report.append(f"*Current Reference Date: {CURRENT_DATE}*")
        report.append("\n## EXECUTIVE SUMMARY\n")

        # Count totals
        total_files = sum(len(results[cat]) for cat in results.keys())
        compliant_files = len(results['compliant'])
        non_compliant = total_files - compliant_files - len(results['errors'])

        report.append(f"- **Total Files Scanned**: {total_files}")
        report.append(f"- **Fully Compliant**: {compliant_files} ({compliant_files/total_files*100:.1f}%)")
        report.append(f"- **Non-Compliant**: {non_compliant} ({non_compliant/total_files*100:.1f}%)")
        report.append(f"- **Errors**: {len(results['errors'])}")

        # Breakdown by severity
        report.append("\n### Severity Breakdown:")
        report.append(f"- 🔴 **Critical**: {len(results['critical'])} files")
        report.append(f"- 🟠 **High**: {len(results['high'])} files")
        report.append(f"- 🟡 **Medium**: {len(results['medium'])} files")
        report.append(f"- 🟢 **Low**: {len(results['low'])} files")
        report.append(f"- ✅ **Compliant**: {len(results['compliant'])} files")

        # Critical issues that need immediate attention
        report.append("\n## 🔴 CRITICAL ISSUES (Immediate Action Required)\n")
        if results['critical']:
            for issue in results['critical']:
                file_name = Path(issue['file']).name
                parent = Path(issue['file']).parent.name
                report.append(f"\n### {parent}/{file_name}")
                report.append(f"**Recommendation**: {issue['recommendation'].upper()}")

                total_issues = sum(len(issue[cat]) for cat in ['past_targets', 'unrealistic_immediate', 'budget_issues', 'timeline_issues'])
                report.append(f"**Total Issues**: {total_issues}")

                # Show first few examples
                for category in ['past_targets', 'unrealistic_immediate', 'budget_issues', 'timeline_issues']:
                    if issue[category]:
                        report.append(f"\n**{category.replace('_', ' ').title()}**:")
                        for item in issue[category][:2]:  # Show first 2 examples
                            report.append(f"- Line {item['line']}: \"{item['match']}\"")
        else:
            report.append("*No critical issues found*")

        # High priority fixes
        report.append("\n## 🟠 HIGH PRIORITY FIXES\n")
        if results['high']:
            for issue in results['high']:
                file_name = Path(issue['file']).name
                parent = Path(issue['file']).parent.name
                report.append(f"- {parent}/{file_name}: {issue['recommendation']} ({sum(len(issue[cat]) for cat in self.patterns.keys())} issues)")
        else:
            report.append("*No high priority issues*")

        # Recommendations by country
        report.append("\n## RECOMMENDATIONS BY COUNTRY\n")

        countries = {}
        for severity in results:
            for issue in results[severity]:
                if 'country=' in issue['file']:
                    country = issue['file'].split('country=')[1].split('/')[0]
                    if country not in countries:
                        countries[country] = {'fix': [], 'archive': [], 'keep': []}

                    rec = issue['recommendation']
                    if rec in ['fix', 'archive', 'keep']:
                        countries[country][rec].append(Path(issue['file']).name)

        for country in sorted(countries.keys()):
            report.append(f"\n### {country}")
            if countries[country]['fix']:
                report.append(f"**Fix ({len(countries[country]['fix'])} files):**")
                for file in countries[country]['fix'][:5]:  # Show first 5
                    report.append(f"- {file}")
            if countries[country]['archive']:
                report.append(f"**Archive ({len(countries[country]['archive'])} files):**")
                for file in countries[country]['archive'][:5]:
                    report.append(f"- {file}")
            if countries[country]['keep']:
                report.append(f"**Keep ({len(countries[country]['keep'])} files):** {len(countries[country]['keep'])} compliant files")

        # Specific document categories
        report.append("\n## DOCUMENT CATEGORY ANALYSIS\n")

        categories = {
            'Executive Briefs': [],
            'Policy Briefs': [],
            'Phase Reports': [],
            'Other': []
        }

        for severity in results:
            for issue in results[severity]:
                file_path = issue['file'].lower()
                if 'executive' in file_path:
                    categories['Executive Briefs'].append(issue)
                elif 'policy' in file_path:
                    categories['Policy Briefs'].append(issue)
                elif 'phase' in file_path:
                    categories['Phase Reports'].append(issue)
                else:
                    categories['Other'].append(issue)

        for category, issues in categories.items():
            if issues:
                non_compliant = [i for i in issues if i['severity'] != 'compliant']
                if non_compliant:
                    report.append(f"\n### {category}")
                    report.append(f"- Total: {len(issues)} files")
                    report.append(f"- Non-compliant: {len(non_compliant)} files")
                    report.append(f"- Recommended to fix: {len([i for i in non_compliant if i['recommendation'] == 'fix'])}")
                    report.append(f"- Recommended to archive: {len([i for i in non_compliant if i['recommendation'] == 'archive'])}")

        # Common patterns found
        report.append("\n## COMMON TEMPORAL ISSUES FOUND\n")

        all_issues = {
            'past_targets': 0,
            'unrealistic_immediate': 0,
            'budget_issues': 0,
            'timeline_issues': 0
        }

        for severity in results:
            for issue in results[severity]:
                for category in all_issues:
                    all_issues[category] += len(issue.get(category, []))

        for category, count in sorted(all_issues.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                report.append(f"- **{category.replace('_', ' ').title()}**: {count} occurrences")

        # Action plan
        report.append("\n## RECOMMENDED ACTION PLAN\n")
        report.append("### Immediate Actions (Today):")
        report.append("1. Archive all documents with 'critical' severity from AT, PT, NO folders")
        report.append("2. Fix Italy Executive Brief - update all 2024-2025 targets to 2026-2027")
        report.append("3. Review and fix all executive/policy briefs")

        report.append("\n### Short-term Actions (This Week):")
        report.append("1. Update Ireland phase reports with temporal corrections")
        report.append("2. Fix Slovakia phase reports for temporal compliance")
        report.append("3. Apply temporal validator to all new documents")

        report.append("\n### Process Improvements:")
        report.append("1. Use temporal injection template for all new documents")
        report.append("2. Run validation script before finalizing any report")
        report.append("3. Add pre-commit hook to check temporal compliance")

        return "\n".join(report)


def main():
    """Run temporal compliance audit."""
    auditor = TemporalComplianceAuditor()

    # Define directories to scan
    directories = [
        Path("C:/Projects/OSINT - Foresight/reports"),
        Path("C:/Projects/OSINT - Foresight/artifacts"),
        Path("C:/Projects/OSINT - Foresight/out")
    ]

    all_results = {
        'compliant': [],
        'low': [],
        'medium': [],
        'high': [],
        'critical': [],
        'errors': []
    }

    print("\nTEMPORAL COMPLIANCE AUDIT")
    print("=" * 60)
    print(f"Current Date: {CURRENT_DATE}")
    print(f"Scanning for temporal issues...")
    print("=" * 60)

    for directory in directories:
        if directory.exists():
            print(f"\nScanning {directory}...")
            results = auditor.scan_directory(directory)

            # Merge results
            for severity in all_results:
                all_results[severity].extend(results[severity])

    # Generate report
    report = auditor.generate_report(all_results)

    # Save report
    report_path = Path("C:/Projects/OSINT - Foresight/docs/reports/TEMPORAL_COMPLIANCE_AUDIT.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n[OK] Audit complete! Report saved to:")
    print(f"   {report_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total = sum(len(all_results[cat]) for cat in all_results)
    print(f"Total files scanned: {total}")
    print(f"Compliant: {len(all_results['compliant'])}")
    print(f"Critical issues: {len(all_results['critical'])}")
    print(f"High priority: {len(all_results['high'])}")
    print(f"Medium priority: {len(all_results['medium'])}")
    print(f"Low priority: {len(all_results['low'])}")

    # Save detailed results as JSON
    json_path = Path("C:/Projects/OSINT - Foresight/docs/reports/temporal_audit_details.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)

    print(f"\nDetailed results saved to: {json_path}")


if __name__ == "__main__":
    main()
