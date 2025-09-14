#!/usr/bin/env python3
"""
Validate phase outputs for temporal awareness and citation compliance.
Run this on any phase output before submission.
"""

import json
import re
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.temporal_validator import TemporalValidator
from src.utils.citation_validator import CitationValidator


class PhaseOutputValidator:
    """Comprehensive validator for phase outputs."""

    def __init__(self, current_date: date = None):
        """Initialize with current or specified date."""
        if current_date is None:
            current_date = date(2025, 9, 13)  # Fixed analysis date

        self.current_date = current_date
        self.temporal_validator = TemporalValidator(current_date)
        self.citation_validator = CitationValidator()
        self.errors = []
        self.warnings = []

    def validate_file(self, file_path: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate a phase output file."""
        file_path = Path(file_path)

        if not file_path.exists():
            return False, {"error": f"File not found: {file_path}"}

        # Detect file type
        if file_path.suffix == '.json':
            return self.validate_json(file_path)
        elif file_path.suffix in ['.md', '.txt']:
            return self.validate_text(file_path)
        else:
            return False, {"error": f"Unsupported file type: {file_path.suffix}"}

    def validate_json(self, file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """Validate JSON phase output."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return False, {"error": f"Invalid JSON: {e}"}

        results = {
            "file": str(file_path),
            "type": "json",
            "temporal_issues": [],
            "citation_issues": [],
            "warnings": []
        }

        # Check for analysis_date
        if 'analysis_date' not in data:
            results['warnings'].append("Missing 'analysis_date' field")
        else:
            # Validate the analysis date
            analysis_date_str = data['analysis_date']
            if analysis_date_str != "2025-09-13":
                results['warnings'].append(
                    f"Analysis date {analysis_date_str} doesn't match current date 2025-09-13"
                )

        # Validate temporal aspects in recommendations
        if 'recommendations' in data:
            for i, rec in enumerate(data['recommendations']):
                valid, errors = self.temporal_validator.validate_recommendation(rec)
                if not valid:
                    results['temporal_issues'].extend([
                        f"Recommendation {i+1}: {error}" for error in errors
                    ])

        # Validate citations/sources
        sources = data.get('sources', data.get('citations', []))
        for i, source in enumerate(sources):
            if isinstance(source, dict):
                valid, errors = self.citation_validator.validate(source)
                if not valid:
                    results['citation_issues'].extend([
                        f"Source {i+1}: {error}" for error in errors
                    ])

        # Check for past dates in any date fields
        past_dates = self._find_past_dates_in_dict(data)
        if past_dates:
            results['temporal_issues'].extend(past_dates)

        # Determine overall validity
        is_valid = (
            len(results['temporal_issues']) == 0 and
            len(results['citation_issues']) == 0
        )

        return is_valid, results

    def validate_text(self, file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """Validate text/markdown phase output."""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        results = {
            "file": str(file_path),
            "type": "text",
            "temporal_issues": [],
            "citation_issues": [],
            "warnings": []
        }

        # Check for temporal issues
        temporal_issues = self.temporal_validator.check_document_dates(text)

        if temporal_issues['past_dates']:
            for issue in temporal_issues['past_dates']:
                results['temporal_issues'].append(issue['error'])

        if temporal_issues['unrealistic_timelines']:
            for issue in temporal_issues['unrealistic_timelines']:
                results['warnings'].append(issue['warning'])

        # Check for citation issues
        urls = re.findall(r'https?://[^\s\)]+', text)
        homepage_urls = []

        for url in urls:
            # Check if it's a homepage URL
            if re.match(r'^https?://[^/]+/?$', url):
                homepage_urls.append(url)
            elif url.endswith(('.com/', '.org/', '.gov/', '.edu/')):
                homepage_urls.append(url)

        if homepage_urls:
            results['citation_issues'].append(
                f"Found {len(homepage_urls)} homepage-only URLs that need specific document links"
            )
            for url in homepage_urls[:5]:  # Show first 5
                results['citation_issues'].append(f"  - {url}")

        # Check for missing accessed_date mentions
        if 'accessed' not in text.lower() and 'retrieved' not in text.lower():
            results['warnings'].append(
                "No 'accessed' or 'retrieved' dates found - ensure all sources have access dates"
            )

        # Check for analysis date
        if '2025-09-13' not in text and 'September 13, 2025' not in text:
            results['warnings'].append("Analysis date (September 13, 2025) not found in document")

        # Determine overall validity
        is_valid = (
            len(results['temporal_issues']) == 0 and
            len(results['citation_issues']) == 0
        )

        return is_valid, results

    def _find_past_dates_in_dict(self, data: Any, path: str = "") -> List[str]:
        """Recursively find past dates in dictionary."""
        issues = []

        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key

                # Check if this looks like a date field
                if any(date_word in key.lower() for date_word in
                       ['date', 'deadline', 'target', 'completion', 'start', 'end']):
                    if isinstance(value, str):
                        # Try to parse as date
                        extracted = self.temporal_validator._extract_date(value)
                        if extracted and extracted < self.current_date:
                            # Check if it's used in forward-looking context
                            if any(word in key.lower() for word in
                                   ['target', 'deadline', 'completion', 'implementation']):
                                issues.append(
                                    f"Field '{new_path}' has past date {value} "
                                    f"(current: {self.current_date})"
                                )

                # Recurse
                issues.extend(self._find_past_dates_in_dict(value, new_path))

        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_path = f"{path}[{i}]"
                issues.extend(self._find_past_dates_in_dict(item, new_path))

        return issues

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable validation report."""
        lines = []
        lines.append("=" * 60)
        lines.append("PHASE OUTPUT VALIDATION REPORT")
        lines.append(f"File: {results['file']}")
        lines.append(f"Type: {results['type']}")
        lines.append(f"Validated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)

        # Temporal Issues
        if results['temporal_issues']:
            lines.append("\n[X] TEMPORAL ISSUES (MUST FIX):")
            for issue in results['temporal_issues']:
                lines.append(f"  - {issue}")
        else:
            lines.append("\n[OK] TEMPORAL VALIDATION: Passed")

        # Citation Issues
        if results['citation_issues']:
            lines.append("\n[X] CITATION ISSUES (MUST FIX):")
            for issue in results['citation_issues']:
                lines.append(f"  - {issue}")
        else:
            lines.append("\n[OK] CITATION VALIDATION: Passed")

        # Warnings
        if results['warnings']:
            lines.append("\n[!] WARNINGS (REVIEW):")
            for warning in results['warnings']:
                lines.append(f"  - {warning}")

        # Summary
        lines.append("\n" + "=" * 60)
        if not results['temporal_issues'] and not results['citation_issues']:
            lines.append("STATUS: PASSED - Ready for submission")
        else:
            total_issues = len(results['temporal_issues']) + len(results['citation_issues'])
            lines.append(f"STATUS: FAILED - {total_issues} issues must be fixed")
        lines.append("=" * 60)

        return "\n".join(lines)


def main():
    """Main validation function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate phase outputs for temporal and citation compliance"
    )
    parser.add_argument(
        "file",
        help="Path to phase output file (JSON or Markdown)"
    )
    parser.add_argument(
        "--date",
        default="2025-09-13",
        help="Current date for validation (default: 2025-09-13)"
    )
    parser.add_argument(
        "--output",
        help="Save validation report to file"
    )

    args = parser.parse_args()

    # Parse date
    try:
        current_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    except ValueError:
        print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD")
        sys.exit(1)

    # Create validator
    validator = PhaseOutputValidator(current_date)

    # Validate file
    is_valid, results = validator.validate_file(args.file)

    # Generate report
    report = validator.generate_report(results)

    # Output report
    print(report)

    # Save to file if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to: {args.output}")

    # Exit with appropriate code
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
