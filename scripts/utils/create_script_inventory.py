#!/usr/bin/env python3
"""
Script Inventory Generator - Comprehensive Project Script Analysis

Purpose:
    Scans all Python scripts in the project and generates comprehensive inventory:
    - Script metadata (name, location, size, last modified)
    - Documentation status (has docstring, purpose extracted)
    - Dependencies (imports, database tables)
    - Categorization and duplication detection
    - Recommendations for consolidation

Output:
    - analysis/SCRIPT_INVENTORY_REPORT.md (human-readable)
    - analysis/script_inventory.json (machine-readable)

Usage:
    python scripts/utils/create_script_inventory.py
    python scripts/utils/create_script_inventory.py --output-dir custom/path

Last Updated: 2025-10-18
"""

import os
import re
import ast
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import argparse


class ScriptInventory:
    """Analyze and catalog all Python scripts in the project"""

    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.scripts = []
        self.categories = defaultdict(list)
        self.duplicates = defaultdict(list)
        self.issues = []

    def scan_scripts(self):
        """Scan ALL Python files in the project (entire tree)"""
        print("Scanning entire project for Python scripts...")

        # Scan entire project recursively
        for script in self.project_root.rglob("*.py"):
            # Skip __pycache__, virtual environments, and .git
            script_str = str(script)
            if any(skip in script_str for skip in ['__pycache__', '.venv', 'venv', '.git']):
                continue

            # Determine location relative to project root
            try:
                rel_path = script.relative_to(self.project_root)
                if rel_path.parent == Path('.'):
                    location = "root"
                else:
                    # Use first directory as location category
                    parts = rel_path.parts
                    location = str(parts[0]) if len(parts) > 1 else "root"
            except ValueError:
                location = "external"

            self.analyze_script(script, location=location)

        print(f"Found {len(self.scripts)} scripts")

    def analyze_script(self, script_path, location):
        """Analyze a single script file"""
        try:
            stat = script_path.stat()
            content = script_path.read_text(encoding='utf-8', errors='ignore')

            # Extract metadata
            metadata = {
                'name': script_path.name,
                'path': str(script_path.relative_to(self.project_root)),
                'location': location,
                'size_bytes': stat.st_size,
                'size_kb': round(stat.st_size / 1024, 2),
                'lines': len(content.splitlines()),
                'last_modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'days_since_modified': (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days,
            }

            # Extract docstring
            docstring = self.extract_docstring(content)
            metadata['has_docstring'] = bool(docstring)
            metadata['docstring'] = docstring[:200] if docstring else None
            metadata['purpose'] = self.extract_purpose(docstring) if docstring else None

            # Extract imports
            metadata['imports'] = self.extract_imports(content)
            metadata['import_count'] = len(metadata['imports'])

            # Extract database tables
            metadata['database_tables'] = self.extract_database_tables(content)

            # Detect main function
            metadata['has_main'] = 'if __name__' in content

            # Detect TODO/FIXME markers
            metadata['todo_count'] = len(re.findall(r'#.*?(TODO|FIXME|BUG|HACK)', content, re.IGNORECASE))

            # Categorize
            metadata['category'] = self.categorize_script(script_path.name, content, location)

            # Check for issues
            issues = self.check_issues(metadata)
            if issues:
                metadata['issues'] = issues
                self.issues.extend([(metadata['name'], issue) for issue in issues])

            self.scripts.append(metadata)

            # Track by category
            self.categories[metadata['category']].append(metadata['name'])

            # Track duplicates
            self.duplicates[metadata['name']].append(metadata['path'])

        except Exception as e:
            print(f"Error analyzing {script_path}: {e}")

    def extract_docstring(self, content):
        """Extract module-level docstring"""
        try:
            tree = ast.parse(content)
            return ast.get_docstring(tree)
        except:
            # Fallback: regex extraction
            match = re.search(r'^"""(.*?)"""', content, re.DOTALL | re.MULTILINE)
            if match:
                return match.group(1).strip()
            match = re.search(r"^'''(.*?)'''", content, re.DOTALL | re.MULTILINE)
            if match:
                return match.group(1).strip()
        return None

    def extract_purpose(self, docstring):
        """Extract purpose from docstring"""
        if not docstring:
            return None

        # Look for "Purpose:" section
        match = re.search(r'Purpose:\s*\n\s*(.+?)(?:\n\n|\n[A-Z]|$)', docstring, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Otherwise return first line
        first_line = docstring.split('\n')[0].strip()
        return first_line if first_line else None

    def extract_imports(self, content):
        """Extract import statements"""
        imports = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                # Extract package name
                if line.startswith('import '):
                    pkg = line.replace('import ', '').split()[0].split('.')[0]
                else:
                    pkg = line.split()[1].split('.')[0]
                imports.append(pkg)
        return list(set(imports))  # Deduplicate

    def extract_database_tables(self, content):
        """Extract database table references"""
        tables = set()

        # Look for CREATE TABLE
        for match in re.finditer(r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?([a-z_]+)', content, re.IGNORECASE):
            tables.add(match.group(1))

        # Look for INSERT INTO
        for match in re.finditer(r'INSERT INTO\s+([a-z_]+)', content, re.IGNORECASE):
            tables.add(match.group(1))

        # Look for SELECT FROM
        for match in re.finditer(r'FROM\s+([a-z_]+)', content, re.IGNORECASE):
            table = match.group(1)
            if table.lower() not in ['select', 'where', 'order', 'group', 'having']:
                tables.add(table)

        return sorted(list(tables))

    def categorize_script(self, name, content, location):
        """Categorize script by name and content"""
        name_lower = name.lower()

        # By directory location
        if 'collectors' in location or 'collection' in location:
            return 'collectors'
        if 'analyzers' in location or 'analysis' in location:
            return 'analyzers'
        if 'processors' in location or 'processing' in location:
            return 'processors'
        if 'validators' in location or 'validation' in location:
            return 'validators'
        if 'tests' in location or 'test' in name_lower:
            return 'tests'
        if 'utils' in location or 'maintenance' in location:
            return 'utilities'
        if 'archive' in location or 'backup' in location:
            return 'archived'

        # By naming pattern
        if name_lower.startswith('collect_'):
            return 'collectors'
        if name_lower.startswith('process_'):
            return 'processors'
        if name_lower.startswith('analyze_'):
            return 'analyzers'
        if name_lower.startswith('integrate_'):
            return 'integrators'
        if name_lower.startswith('validate_') or name_lower.startswith('verify_') or name_lower.startswith('check_'):
            return 'validators'
        if name_lower.startswith('test_'):
            return 'tests'
        if name_lower.startswith('build_'):
            return 'reporting'
        if 'presentation' in name_lower or 'slides' in name_lower:
            return 'reporting'

        # Root directory scripts
        if location == 'root':
            return 'root_scripts'

        return 'uncategorized'

    def check_issues(self, metadata):
        """Check for potential issues"""
        issues = []

        # Large scripts
        if metadata['lines'] > 1000:
            issues.append(f"LARGE: {metadata['lines']} lines (consider refactoring)")

        # No docstring
        if not metadata['has_docstring']:
            issues.append("NO_DOCSTRING: Missing module documentation")

        # Old scripts
        if metadata['days_since_modified'] > 180:
            issues.append(f"OLD: Not modified in {metadata['days_since_modified']} days")

        # High TODO count
        if metadata['todo_count'] > 5:
            issues.append(f"HIGH_TODO: {metadata['todo_count']} TODO/FIXME markers")

        return issues

    def generate_report(self, output_dir=None):
        """Generate comprehensive markdown report"""
        output_dir = Path(output_dir) if output_dir else self.project_root / "analysis"
        output_dir.mkdir(exist_ok=True)

        report_path = output_dir / "SCRIPT_INVENTORY_REPORT.md"
        json_path = output_dir / "script_inventory.json"

        # Generate markdown report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_markdown_report())

        # Generate JSON data
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'generated': datetime.now().isoformat(),
                'total_scripts': len(self.scripts),
                'scripts': self.scripts,
                'categories': dict(self.categories),
                'duplicates': {k: v for k, v in self.duplicates.items() if len(v) > 1},
                'issues': self.issues,
                'summary': self.generate_summary()
            }, f, indent=2)

        print(f"\nReports generated:")
        print(f"  - {report_path}")
        print(f"  - {json_path}")

        return report_path, json_path

    def generate_markdown_report(self):
        """Generate markdown format report"""
        lines = [
            "# OSINT Foresight - Script Inventory Report",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Scripts**: {len(self.scripts)}",
            "",
            "---",
            "",
            "## Executive Summary",
            ""
        ]

        # Summary statistics
        summary = self.generate_summary()
        lines.extend([
            f"- **Total Scripts**: {summary['total_scripts']}",
            f"- **Total Lines of Code**: {summary['total_lines']:,}",
            f"- **Total Size**: {summary['total_size_mb']:.2f} MB",
            f"- **Scripts with Docstrings**: {summary['with_docstring']} ({summary['docstring_percent']:.1f}%)",
            f"- **Root Directory Scripts**: {summary['root_scripts']} (should be 0)",
            f"- **Duplicate Names**: {summary['duplicate_count']}",
            f"- **Scripts with Issues**: {summary['scripts_with_issues']}",
            "",
            "---",
            "",
            "## Categories Breakdown",
            ""
        ])

        # Category breakdown
        for category, scripts in sorted(self.categories.items(), key=lambda x: len(x[1]), reverse=True):
            lines.append(f"### {category.title()} ({len(scripts)} scripts)")
            lines.append("")
            for script in sorted(scripts)[:10]:  # Show first 10
                lines.append(f"- {script}")
            if len(scripts) > 10:
                lines.append(f"- ... and {len(scripts) - 10} more")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## Duplicates (Same Filename in Different Locations)",
            ""
        ])

        # Duplicates
        duplicates = {k: v for k, v in self.duplicates.items() if len(v) > 1}
        if duplicates:
            for name, paths in sorted(duplicates.items()):
                lines.append(f"### {name}")
                for path in paths:
                    lines.append(f"- {path}")
                lines.append("")
        else:
            lines.append("✅ No duplicate filenames found")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## Issues Detected",
            ""
        ])

        # Issues
        if self.issues:
            issue_by_type = defaultdict(list)
            for script, issue in self.issues:
                issue_type = issue.split(':')[0]
                issue_by_type[issue_type].append((script, issue))

            for issue_type, items in sorted(issue_by_type.items()):
                lines.append(f"### {issue_type} ({len(items)} scripts)")
                lines.append("")
                for script, issue in sorted(items)[:20]:  # Show first 20
                    lines.append(f"- **{script}**: {issue}")
                if len(items) > 20:
                    lines.append(f"- ... and {len(items) - 20} more")
                lines.append("")
        else:
            lines.append("✅ No issues detected")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## Largest Scripts (>1000 lines)",
            ""
        ])

        # Largest scripts
        large_scripts = [s for s in self.scripts if s['lines'] > 1000]
        if large_scripts:
            lines.append("| Script | Lines | Size | Category | Location |")
            lines.append("|--------|-------|------|----------|----------|")
            for s in sorted(large_scripts, key=lambda x: x['lines'], reverse=True):
                lines.append(f"| {s['name']} | {s['lines']:,} | {s['size_kb']:.1f} KB | {s['category']} | {s['location']} |")
            lines.append("")
        else:
            lines.append("✅ No scripts over 1000 lines")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## Root Directory Scripts (Should be Moved)",
            ""
        ])

        # Root scripts
        root_scripts = [s for s in self.scripts if s['location'] == 'root']
        if root_scripts:
            lines.append(f"**Found {len(root_scripts)} scripts in root directory**")
            lines.append("")
            lines.append("| Script | Lines | Suggested Category | Suggested Location |")
            lines.append("|--------|-------|-------------------|-------------------|")
            for s in sorted(root_scripts, key=lambda x: x['name']):
                suggested = self.suggest_location(s)
                lines.append(f"| {s['name']} | {s['lines']} | {s['category']} | {suggested} |")
            lines.append("")
        else:
            lines.append("✅ No scripts in root directory")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## Recommendations",
            "",
            "### High Priority",
            f"1. **Move {len(root_scripts)} root scripts** to appropriate subdirectories",
            f"2. **Refactor {len(large_scripts)} large scripts** (>1000 lines)",
            f"3. **Add docstrings** to {summary['total_scripts'] - summary['with_docstring']} undocumented scripts",
            f"4. **Archive old scripts** - {summary['old_scripts']} scripts not modified in 180+ days",
            "",
            "### Medium Priority",
            f"5. **Resolve {len(duplicates)} duplicate filenames**",
            f"6. **Address {len(self.issues)} total issues** across all scripts",
            "",
            "### Low Priority",
            f"7. **Review and update** scripts with high TODO counts",
            "",
            "---",
            "",
            f"**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Next Review**: {datetime.now().replace(day=datetime.now().day + 7).strftime('%Y-%m-%d')} (weekly)",
            ""
        ])

        return '\n'.join(lines)

    def suggest_location(self, script_metadata):
        """Suggest proper location for a script"""
        category = script_metadata['category']
        name = script_metadata['name']

        mapping = {
            'collectors': 'scripts/collectors/',
            'processors': 'scripts/processors/',
            'analyzers': 'scripts/analyzers/',
            'integrators': 'scripts/integrators/',
            'validators': 'scripts/validators/',
            'tests': 'tests/',
            'utilities': 'scripts/utils/',
            'reporting': 'scripts/reporting/',
        }

        return mapping.get(category, 'scripts/misc/') + name

    def generate_summary(self):
        """Generate summary statistics"""
        return {
            'total_scripts': len(self.scripts),
            'total_lines': sum(s['lines'] for s in self.scripts),
            'total_size_mb': sum(s['size_bytes'] for s in self.scripts) / (1024 * 1024),
            'with_docstring': sum(1 for s in self.scripts if s['has_docstring']),
            'docstring_percent': (sum(1 for s in self.scripts if s['has_docstring']) / len(self.scripts) * 100) if self.scripts else 0,
            'root_scripts': len([s for s in self.scripts if s['location'] == 'root']),
            'duplicate_count': len([k for k, v in self.duplicates.items() if len(v) > 1]),
            'scripts_with_issues': len(set(script for script, _ in self.issues)),
            'old_scripts': len([s for s in self.scripts if s['days_since_modified'] > 180]),
        }


def main():
    parser = argparse.ArgumentParser(description='Generate script inventory report')
    parser.add_argument('--output-dir', help='Output directory for reports', default=None)
    parser.add_argument('--project-root', help='Project root directory', default=None)
    args = parser.parse_args()

    print("=" * 70)
    print("OSINT Foresight - Script Inventory Generator")
    print("=" * 70)
    print()

    inventory = ScriptInventory(project_root=args.project_root)
    inventory.scan_scripts()

    print("\nGenerating reports...")
    report_path, json_path = inventory.generate_report(output_dir=args.output_dir)

    print("\n" + "=" * 70)
    print("Summary:")
    print("=" * 70)
    summary = inventory.generate_summary()
    for key, value in summary.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")

    print("\n✅ Inventory complete!")
    print(f"📄 View report: {report_path}")


if __name__ == '__main__':
    main()
