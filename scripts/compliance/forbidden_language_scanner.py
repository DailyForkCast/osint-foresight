#!/usr/bin/env python3
"""
Forbidden Language Scanner - Zero Fabrication Protocol Enforcement

Scans documents for forbidden language patterns that indicate fabrication,
assumptions, or unsupported interpretations.

Usage:
    python forbidden_language_scanner.py <file_or_directory>
    python forbidden_language_scanner.py report.md
    python forbidden_language_scanner.py analysis/

ZERO FABRICATION PROTOCOL COMPLIANCE:
- Automated enforcement tool
- Detects forbidden phrases from protocol
- Reports violations with line numbers
- Exit code 1 if violations found (CI/CD integration)
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Forbidden language patterns from Zero Fabrication Protocol
FORBIDDEN_PATTERNS = {
    "Estimation & Inference": [
        r"\bit is estimated that\b",
        r"\bbased on typical patterns\b",
        r"\bindustry standards suggest\b",
        r"\bcomparable databases show\b",
        r"\bwe can infer that\b",
        r"\bit'?s reasonable to assume\b",
        r"\blikely reflects\b",
        r"\bprobably indicates\b",
        r"\bsuggests that\b",
        r"\bimplies that\b",
    ],
    "Operations & Campaigns": [
        r"\bcoordinated campaign\b",
        r"\binfluence operation\b",
        r"\bpropaganda campaign\b",
        r"\bdisinformation effort\b",
        r"\bstrategic messaging\b",
        r"\borchestrated response\b",
        r"\bcoordinated messaging\b",
        r"\bsynchronized narrative\b",
    ],
    "Intent & Motivation": [
        r"\bdesigned to\b",
        r"\bintended to\b",
        r"\baimed at\b",
        r"\bseeking to\b",
        r"\battempting to\b",
        r"\bhiding\b",
        r"\bcircumventing\b",
        r"\bavoiding\b",
        r"\bdeceptive\b",
    ],
    "Corporate Characterization": [
        r"\bshell company\b",
        r"\bshell companies\b",
        r"\bfront company\b",
        r"\bnetwork of shells\b",
        r"\bdeceptive structure\b",
        r"\bsuspicious entity\b",
        r"\bdormant entity\b",
        r"\bempty shell\b",
    ],
    "Risk & Assessment": [
        r"\bhigh risk due to\b",
        r"\bred flags detected\b",
        r"\bsuspicious activity\b",
        r"\banomalous behavior\b",
        r"\bconcerning patterns\b",
    ],
    "Patterns & Trends": [
        r"\bpattern detected\b",
        r"\bemerging trend\b",
        r"\bgrowing threat\b",
        r"\bincreasing activity\b",
    ]
}

# Exceptions - these are allowed contexts
EXCEPTION_PATTERNS = [
    r"forbidden:\s*[\"'].*[\"']",  # In quoted forbidden examples
    r"❌.*",  # In examples marked as forbidden
    r"NON-COMPLIANT:.*",  # In examples marked as non-compliant
    r"Example of fabrication:.*",  # In training examples
]

class ViolationFinder:
    def __init__(self):
        self.violations: List[Dict] = []

    def is_exception(self, line: str) -> bool:
        """Check if line is in an allowed exception context"""
        for pattern in EXCEPTION_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    def scan_file(self, filepath: Path) -> List[Dict]:
        """Scan a single file for forbidden language"""
        violations = []

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                # Skip exception contexts
                if self.is_exception(line):
                    continue

                # Check all forbidden patterns
                for category, patterns in FORBIDDEN_PATTERNS.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            violations.append({
                                'file': str(filepath),
                                'line_number': line_num,
                                'category': category,
                                'pattern': pattern,
                                'matched_text': match.group(),
                                'line_content': line.strip(),
                                'severity': 'CRITICAL'
                            })

        except Exception as e:
            print(f"Error scanning {filepath}: {e}", file=sys.stderr)

        return violations

    def scan_directory(self, directory: Path) -> List[Dict]:
        """Recursively scan directory for violations"""
        violations = []

        # File types to scan
        extensions = ['.md', '.py', '.txt', '.json']

        for filepath in directory.rglob('*'):
            if filepath.is_file() and filepath.suffix in extensions:
                # Skip archived files
                if 'archive' in str(filepath).lower():
                    continue
                if 'ARCHIVED' in str(filepath):
                    continue

                file_violations = self.scan_file(filepath)
                violations.extend(file_violations)

        return violations

    def print_violations(self, violations: List[Dict]) -> None:
        """Print violations in readable format"""
        if not violations:
            print("[PASS] ZERO FABRICATION PROTOCOL: No violations detected")
            print()
            return

        print("=" * 80)
        print("[VIOLATION] ZERO FABRICATION PROTOCOL VIOLATIONS DETECTED")
        print("=" * 80)
        print()

        # Group by file
        files = {}
        for v in violations:
            if v['file'] not in files:
                files[v['file']] = []
            files[v['file']].append(v)

        for filepath, file_violations in files.items():
            print(f"[FILE] {filepath}")
            print(f"   Violations: {len(file_violations)}")
            print()

            # Group by category
            categories = {}
            for v in file_violations:
                if v['category'] not in categories:
                    categories[v['category']] = []
                categories[v['category']].append(v)

            for category, cat_violations in categories.items():
                print(f"   Category: {category}")
                for v in cat_violations:
                    print(f"      Line {v['line_number']}: {v['matched_text']}")
                    print(f"      Context: {v['line_content'][:100]}")
                print()

        print("=" * 80)
        print(f"Total Violations: {len(violations)}")
        print("=" * 80)
        print()
        print("ACTION REQUIRED:")
        print("1. Review each violation")
        print("2. Replace with factual language (see ZERO_FABRICATION_PROTOCOL.md)")
        print("3. Re-run scanner until 0 violations")
        print("4. Document if false positive")
        print()

def main():
    if len(sys.argv) < 2:
        print("Usage: python forbidden_language_scanner.py <file_or_directory>")
        print()
        print("Examples:")
        print("  python forbidden_language_scanner.py report.md")
        print("  python forbidden_language_scanner.py analysis/")
        print("  python forbidden_language_scanner.py .")
        sys.exit(1)

    target = Path(sys.argv[1])

    if not target.exists():
        print(f"Error: {target} does not exist")
        sys.exit(1)

    scanner = ViolationFinder()

    if target.is_file():
        violations = scanner.scan_file(target)
    else:
        violations = scanner.scan_directory(target)

    scanner.print_violations(violations)

    # Exit with code 1 if violations found (for CI/CD)
    if violations:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
