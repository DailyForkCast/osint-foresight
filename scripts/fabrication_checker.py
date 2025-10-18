#!/usr/bin/env python3
"""
Automated Fabrication Checker for OSINT Foresight Project
Scans documentation for fabrication risks and unmarked hypothetical data

Runs regular checks for:
1. Actively prohibited patterns (from our known issues)
2. Unexpected fabrication risks (new patterns that could emerge)
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set
import hashlib

class FabricationDetector:
    """Detects potential fabrication in documentation"""

    def __init__(self):
        # Known fabricated numbers to watch for
        self.known_fabrications = {
            "12B", "€12B", "12 billion",
            "4,500", "4500", "forty-five hundred",
            "100,000", "100000", "500,000", "500000",
            "100,000-500,000", "100K-500K"
            # NOTE: 168 and 222 are REAL verified numbers from italy_china_project_ids.json
        }

        # Patterns that indicate potential fabrication
        self.danger_patterns = [
            # Numbers without proper markers
            (r'\b\d{1,3}(?:,\d{3})+\b(?![^\[]*\])', "Large number without verification marker"),
            (r'€\d+[BMK]\b(?![^\[]*\])', "Currency amount without verification marker"),
            (r'\$\d+[BMK]\b(?![^\[]*\])', "Currency amount without verification marker"),

            # Projection language without markers
            (r'\b(?:expected|anticipated|projected|estimated)\s+\d+', "Projection term with number - needs [PROJECTION] marker"),
            (r'\b(?:could|would|might|should)\s+(?:reach|total|amount to)\s+\d+', "Hypothetical language with number"),

            # Percentage claims without source
            (r'\b\d+(?:\.\d+)?%(?![^\[]*\])', "Percentage without verification marker"),

            # Time-based projections
            (r'\b(?:by|in)\s+20\d{2}\s+.*\d+', "Future projection needs [PROJECTION] marker"),

            # Comparative claims
            (r'\b\d+x\s+(?:more|less|greater|higher)', "Multiplier claim without source"),

            # Range estimates
            (r'\b\d+\s*-\s*\d+\s+(?!years|months|days)', "Range estimate without verification"),
        ]

        # Required markers for different data types
        self.required_markers = {
            "verified": "[VERIFIED DATA]",
            "hypothetical": "[HYPOTHETICAL EXAMPLE]",
            "illustrative": "[ILLUSTRATIVE ONLY]",
            "projection": "[PROJECTION - NOT VERIFIED]",
            "example": "[EXAMPLE ONLY]",
            "gap": "[EVIDENCE GAP:",
        }

        # Files to check
        self.check_paths = [
            "README.md",
            "docs/*.md",
            "docs/**/*.md",
            "analysis/*.md",
            "analysis/**/*.md",
            "artifacts/**/*.md",
            "countries/**/*.md",
        ]

        # Files to exclude from checks
        self.exclude_patterns = [
            "**/archive/**",
            "**/ARCHIVED_*",
            "**/*_ARCHIVE_*",
            "**/test_*",
            "scripts/*.py",  # Code files have different rules
        ]

    def check_file(self, filepath: Path) -> List[Dict]:
        """Check a single file for fabrication risks"""
        issues = []

        try:
            content = filepath.read_text(encoding='utf-8')
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                # Skip code blocks and comments
                if line.strip().startswith('```') or line.strip().startswith('#'):
                    continue

                # Check for known fabricated numbers
                for fab_num in self.known_fabrications:
                    if fab_num in line and not any(marker in line for marker in self.required_markers.values()):
                        issues.append({
                            'file': str(filepath),
                            'line': line_num,
                            'type': 'KNOWN_FABRICATION',
                            'severity': 'HIGH',
                            'text': line.strip()[:100],
                            'issue': f"Contains known fabricated number: {fab_num}",
                            'fix': f"Remove or mark with {self.required_markers['hypothetical']}"
                        })

                # Check danger patterns
                for pattern, description in self.danger_patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        # Check if properly marked
                        if not any(marker in line for marker in self.required_markers.values()):
                            issues.append({
                                'file': str(filepath),
                                'line': line_num,
                                'type': 'PATTERN_RISK',
                                'severity': 'MEDIUM',
                                'text': line.strip()[:100],
                                'issue': description,
                                'match': match.group(),
                                'fix': "Add appropriate marker or verify data source"
                            })

                # Check for mixed real and hypothetical in same paragraph
                if any(marker in line for marker in ["[VERIFIED DATA]", "[HYPOTHETICAL"]):
                    if "[VERIFIED DATA]" in line and "[HYPOTHETICAL" in line:
                        issues.append({
                            'file': str(filepath),
                            'line': line_num,
                            'type': 'MIXED_DATA',
                            'severity': 'HIGH',
                            'text': line.strip()[:100],
                            'issue': "Mixed verified and hypothetical data in same line",
                            'fix': "Separate into different paragraphs"
                        })

                # Check for numbers that look too specific to be estimates
                specific_pattern = r'\b\d{3,4}\.\d{1,2}\b'
                if re.search(specific_pattern, line) and "[VERIFIED DATA]" not in line:
                    issues.append({
                        'file': str(filepath),
                        'line': line_num,
                        'type': 'SUSPICIOUS_PRECISION',
                        'severity': 'MEDIUM',
                        'text': line.strip()[:100],
                        'issue': "Suspiciously precise number without verification",
                        'fix': "Verify source or mark as estimate"
                    })

        except Exception as e:
            issues.append({
                'file': str(filepath),
                'line': 0,
                'type': 'READ_ERROR',
                'severity': 'LOW',
                'issue': f"Could not read file: {e}"
            })

        return issues

    def scan_project(self) -> Dict:
        """Scan entire project for fabrication risks"""
        all_issues = []
        files_checked = 0

        project_root = Path("C:/Projects/OSINT - Foresight")

        for pattern in self.check_paths:
            for filepath in project_root.glob(pattern):
                # Skip excluded patterns
                if any(filepath.match(exc) for exc in self.exclude_patterns):
                    continue

                if filepath.is_file():
                    issues = self.check_file(filepath)
                    all_issues.extend(issues)
                    files_checked += 1

        # Categorize issues
        high_severity = [i for i in all_issues if i['severity'] == 'HIGH']
        medium_severity = [i for i in all_issues if i['severity'] == 'MEDIUM']
        low_severity = [i for i in all_issues if i['severity'] == 'LOW']

        # Check for emerging patterns
        emerging_patterns = self.detect_emerging_patterns(all_issues)

        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'files_checked': files_checked,
            'total_issues': len(all_issues),
            'high_severity': len(high_severity),
            'medium_severity': len(medium_severity),
            'low_severity': len(low_severity),
            'emerging_patterns': emerging_patterns,
            'issues': {
                'high': high_severity[:10],  # Top 10 high severity
                'medium': medium_severity[:5],  # Top 5 medium
                'low': low_severity[:3]  # Top 3 low
            }
        }

        return report

    def detect_emerging_patterns(self, issues: List[Dict]) -> List[Dict]:
        """Detect new patterns of potential fabrication"""
        patterns = {}

        for issue in issues:
            if issue['type'] not in patterns:
                patterns[issue['type']] = {
                    'count': 0,
                    'files': set(),
                    'examples': []
                }

            patterns[issue['type']]['count'] += 1
            patterns[issue['type']]['files'].add(issue['file'])

            if len(patterns[issue['type']]['examples']) < 3:
                patterns[issue['type']]['examples'].append(issue.get('text', '')[:50])

        # Convert sets to lists for JSON serialization
        emerging = []
        for pattern_type, data in patterns.items():
            if data['count'] > 3:  # Pattern appears multiple times
                emerging.append({
                    'pattern': pattern_type,
                    'frequency': data['count'],
                    'spread': len(data['files']),
                    'examples': data['examples']
                })

        return sorted(emerging, key=lambda x: x['frequency'], reverse=True)

    def generate_report(self, output_path: str = None) -> str:
        """Generate and save fabrication check report"""
        report = self.scan_project()

        # Create markdown report
        md_report = f"""# Fabrication Check Report
Generated: {report['timestamp']}

## Summary
- **Files Checked:** {report['files_checked']}
- **Total Issues:** {report['total_issues']}
- **High Severity:** {report['high_severity']} [WARNING]
- **Medium Severity:** {report['medium_severity']} [CAUTION]
- **Low Severity:** {report['low_severity']} [NOTE]

## Critical Issues (High Severity)
"""

        for issue in report['issues']['high']:
            md_report += f"""
### {issue['file']}:{issue['line']}
- **Type:** {issue['type']}
- **Issue:** {issue['issue']}
- **Text:** `{issue.get('text', '')}`
- **Fix:** {issue.get('fix', 'Review and verify')}
"""

        if report['emerging_patterns']:
            md_report += "\n## Emerging Patterns\n"
            for pattern in report['emerging_patterns']:
                md_report += f"""
### {pattern['pattern']}
- **Frequency:** {pattern['frequency']} occurrences
- **Spread:** {pattern['spread']} files
- **Examples:** {', '.join(pattern['examples'])}
"""

        md_report += """
## Recommendations
1. Review all HIGH severity issues immediately
2. Add proper markers to unverified numbers
3. Separate verified and hypothetical data
4. Run this check before any major commits
5. Consider adding to CI/CD pipeline

## Marker Reference
- `[VERIFIED DATA]` - For confirmed numbers from sources
- `[HYPOTHETICAL EXAMPLE]` - For illustrative scenarios
- `[ILLUSTRATIVE ONLY]` - For teaching examples
- `[PROJECTION - NOT VERIFIED]` - For future estimates
- `[EVIDENCE GAP: detail]` - For missing data

---
*Run `python scripts/fabrication_checker.py` for updated report*
"""

        # Save report
        if output_path:
            output_file = Path(output_path)
        else:
            output_file = Path("C:/Projects/OSINT - Foresight/docs/reports/FABRICATION_CHECK_REPORT.md")

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(md_report, encoding='utf-8')

        # Also save JSON for programmatic access
        json_file = output_file.with_suffix('.json')
        json_file.write_text(json.dumps(report, indent=2, default=str), encoding='utf-8')

        return str(output_file)


def main():
    """Run fabrication check and generate report"""
    print("Starting Fabrication Check...")

    detector = FabricationDetector()
    report_path = detector.generate_report()

    # Load and display summary
    report = json.loads(Path(report_path).with_suffix('.json').read_text())

    print(f"\nCheck Complete!")
    print(f"Files Checked: {report['files_checked']}")
    print(f"High Severity Issues: {report['high_severity']}")
    print(f"Medium Severity Issues: {report['medium_severity']}")
    print(f"Low Severity Issues: {report['low_severity']}")

    if report['high_severity'] > 0:
        print(f"\nCRITICAL: {report['high_severity']} high severity issues found!")
        print(f"   Review report at: {report_path}")

    print(f"\nFull report saved to: {report_path}")

    return 0 if report['high_severity'] == 0 else 1


if __name__ == "__main__":
    exit(main())
