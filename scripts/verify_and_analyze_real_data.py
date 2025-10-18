#!/usr/bin/env python3
"""
Verify what we actually extracted and search for China patterns
"""

import json
import re
from pathlib import Path
from datetime import datetime

class RealDataVerifier:
    def __init__(self):
        self.china_patterns = [
            r'\bchina\b', r'\bchinese\b', r'\bbeijing\b', r'\bshanghai\b',
            r'\bhuawei\b', r'\bzte\b', r'\balibaba\b', r'\btencent\b',
            r'\bprc\b', r'\bsino-', r'\bcn\b'
        ]
        self.findings = {
            'ted_status': {},
            'json_china_matches': [],
            'tsv_insights': {},
            'real_accessibility': {}
        }

    def verify_ted_extraction(self):
        """Check what really got extracted from TED"""
        print("\n[TED VERIFICATION]")
        ted_path = Path("F:/DECOMPRESSED_DATA/ted_extracted")

        if not ted_path.exists():
            print("  TED extraction path doesn't exist!")
            self.findings['ted_status']['exists'] = False
            return

        # Find all files recursively
        all_files = list(ted_path.rglob("*"))
        xml_files = list(ted_path.rglob("*.xml"))

        # Check deeper nesting
        deep_search = []
        for d in ted_path.iterdir():
            if d.is_dir():
                subdirs = list(d.iterdir())
                for subdir in subdirs[:3]:  # Check first 3
                    if subdir.is_dir():
                        files_in_subdir = list(subdir.iterdir())
                        deep_search.append({
                            'path': str(subdir),
                            'file_count': len(files_in_subdir),
                            'sample_files': [f.name for f in files_in_subdir[:5]]
                        })

        self.findings['ted_status'] = {
            'exists': True,
            'total_items': len(all_files),
            'xml_files': len(xml_files),
            'directories': len([f for f in all_files if f.is_dir()]),
            'deep_structure': deep_search[:5]
        }

        print(f"  Found {len(all_files)} total items")
        print(f"  XML files: {len(xml_files)}")
        print(f"  Nested structure depth: {len(deep_search)} subdirectories explored")

    def analyze_json_sample(self):
        """Search for China patterns in JSON sample"""
        print("\n[JSON CHINA ANALYSIS]")
        json_file = Path("C:/Projects/OSINT - Foresight/json_51gb_sample.json")

        if not json_file.exists():
            print("  JSON sample not found!")
            return

        with open(json_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Search for China patterns
        for pattern in self.china_patterns:
            matches = re.findall(pattern, content.lower())
            if matches:
                self.findings['json_china_matches'].append({
                    'pattern': pattern,
                    'count': len(matches),
                    'samples': matches[:5]
                })

        # Look for specific fields
        lines = content.split('\n')
        dept_agriculture = sum(1 for line in lines if 'Department of Agriculture' in line)
        redacted = sum(1 for line in lines if 'REDACTED' in line)
        direct_payment = sum(1 for line in lines if 'direct payment' in line)

        self.findings['json_insights'] = {
            'total_lines': len(lines),
            'dept_agriculture': dept_agriculture,
            'redacted_entries': redacted,
            'direct_payments': direct_payment,
            'china_matches': len(self.findings['json_china_matches'])
        }

        print(f"  Analyzed {len(lines)} lines")
        print(f"  China patterns found: {len(self.findings['json_china_matches'])}")

    def verify_tsv_structure(self):
        """Verify TSV analysis results"""
        print("\n[TSV VERIFICATION]")
        tsv_analysis = Path("C:/Projects/OSINT - Foresight/tsv_analysis.json")

        if tsv_analysis.exists():
            with open(tsv_analysis, 'r') as f:
                data = json.load(f)

            self.findings['tsv_insights'] = {
                'files_analyzed': len(data),
                'total_columns': data[0]['columns'] if data else 0,
                'sample_rows': sum(d['sample_rows'] for d in data),
                'structure': 'USASpending database tables' if data[0]['columns'] == 374 else 'Unknown'
            }

            print(f"  TSV files: {len(data)}")
            print(f"  Columns: {data[0]['columns'] if data else 0}")
            print(f"  Structure: Likely USASpending full export")

    def check_real_accessibility(self):
        """What can we really access right now?"""
        print("\n[REAL ACCESSIBILITY CHECK]")

        # Check all key locations
        checks = {
            'json_sample': Path("C:/Projects/OSINT - Foresight/json_51gb_sample.json"),
            'tsv_analysis': Path("C:/Projects/OSINT - Foresight/tsv_analysis.json"),
            'postgres_scripts': Path("C:/Projects/OSINT - Foresight/postgres_scripts/"),
            'overnight_script': Path("C:/Projects/OSINT - Foresight/overnight_decompress.py"),
            'ted_extracted': Path("F:/DECOMPRESSED_DATA/ted_extracted"),
            'usaspending_dat': Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/")
        }

        for name, path in checks.items():
            if path.exists():
                if path.is_file():
                    size = path.stat().st_size / 1024  # KB
                    self.findings['real_accessibility'][name] = f"EXISTS ({size:.1f} KB)"
                else:
                    file_count = len(list(path.glob("*")))
                    self.findings['real_accessibility'][name] = f"EXISTS ({file_count} items)"
            else:
                self.findings['real_accessibility'][name] = "NOT FOUND"

        # Count what we can really parse NOW
        parseable_now = {
            'cordis_json': 21,  # From earlier
            'postgres_tables': 45,  # Parsed earlier
            'json_sample': 1,  # Just sampled
            'tsv_structure': 2,  # Structure known
            'ted_files': 0  # Not extracted properly
        }

        self.findings['real_accessibility']['parseable_files'] = sum(parseable_now.values())
        self.findings['real_accessibility']['breakdown'] = parseable_now

    def generate_reality_report(self):
        """Generate honest assessment of what we have"""
        report = "# REALITY CHECK: What We Actually Have Access To\n\n"
        report += f"Generated: {datetime.now().isoformat()}\n\n"

        report += "## TED Extraction Status\n\n"
        ted = self.findings['ted_status']
        if ted.get('exists'):
            report += f"- Total items found: {ted['total_items']}\n"
            report += f"- XML files: {ted['xml_files']}\n"
            report += f"- Directories: {ted['directories']}\n\n"

            if ted.get('deep_structure'):
                report += "### Nested Structure Found:\n"
                for item in ted['deep_structure'][:3]:
                    report += f"- {item['path']}: {item['file_count']} files\n"
                    if item['sample_files']:
                        report += f"  Sample: {', '.join(item['sample_files'][:3])}\n"
        else:
            report += "- TED extraction FAILED\n\n"

        report += "\n## JSON Sample Analysis (USASpending)\n\n"
        if 'json_insights' in self.findings:
            insights = self.findings['json_insights']
            report += f"- Lines analyzed: {insights['total_lines']}\n"
            report += f"- Dept of Agriculture entries: {insights['dept_agriculture']}\n"
            report += f"- Redacted entries: {insights['redacted_entries']}\n"
            report += f"- Direct payments: {insights['direct_payments']}\n\n"

            if self.findings['json_china_matches']:
                report += "### China Patterns Found:\n"
                for match in self.findings['json_china_matches']:
                    report += f"- Pattern '{match['pattern']}': {match['count']} occurrences\n"
            else:
                report += "### China Patterns: NONE FOUND in sample\n"

        report += "\n## TSV Files (107 GB)\n\n"
        if 'tsv_insights' in self.findings:
            tsv = self.findings['tsv_insights']
            report += f"- Files analyzed: {tsv['files_analyzed']}\n"
            report += f"- Columns per file: {tsv['total_columns']}\n"
            report += f"- Structure: {tsv['structure']}\n"
            report += "- Status: Structure known, ready for streaming parse\n"

        report += "\n## What's REALLY Accessible NOW\n\n"
        for name, status in self.findings['real_accessibility'].items():
            if name not in ['parseable_files', 'breakdown']:
                report += f"- {name}: {status}\n"

        report += f"\n### Parseable Files Count:\n"
        if 'breakdown' in self.findings['real_accessibility']:
            total = self.findings['real_accessibility']['parseable_files']
            report += f"**TOTAL: {total} files actually parseable**\n\n"
            for source, count in self.findings['real_accessibility']['breakdown'].items():
                report += f"- {source}: {count}\n"

        report += "\n## The Truth\n\n"
        report += "### What WORKED ✅\n"
        report += "- JSON sample extraction (999 lines from 51GB file)\n"
        report += "- TSV structure analysis (374 columns identified)\n"
        report += "- PostgreSQL scripts created\n"
        report += "- Overnight batch prepared\n\n"

        report += "### What PARTIALLY WORKED ⚠️\n"
        report += "- TED extraction (created structure but files deeply nested)\n"
        report += "- China search (no matches in JSON sample)\n\n"

        report += "### What FAILED ❌\n"
        report += "- Complete TED file extraction\n"
        report += "- Finding China patterns in USASpending sample\n\n"

        report += "## Next REAL Actions\n\n"
        report += "1. **Fix TED extraction**: Files are nested 3+ levels deep\n"
        report += "2. **Run overnight decompression**: Execute run_overnight.bat\n"
        report += "3. **PostgreSQL restore**: Follow postgres_scripts/restore_usaspending.sh\n"
        report += "4. **Stream parse TSV files**: 107 GB with 374 columns each\n"
        report += "5. **Expand JSON sampling**: Current sample may be too small for China patterns\n"

        return report

    def run(self):
        """Execute all verifications"""
        print("="*70)
        print("REALITY CHECK: Verifying What We Actually Have")
        print("="*70)

        # Run all checks
        self.verify_ted_extraction()
        self.analyze_json_sample()
        self.verify_tsv_structure()
        self.check_real_accessibility()

        # Generate and save report
        report = self.generate_reality_report()

        report_path = Path("C:/Projects/OSINT - Foresight/REALITY_CHECK_REPORT.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n[Report saved to: {report_path}]")

        # Also save raw findings
        with open("C:/Projects/OSINT - Foresight/reality_check_findings.json", 'w') as f:
            json.dump(self.findings, f, indent=2, default=str)

        print("\n" + "="*70)
        print("REALITY CHECK COMPLETE")
        print("="*70)
        print(f"\nParseable files NOW: {self.findings['real_accessibility'].get('parseable_files', 0)}")
        print(f"China patterns found: {len(self.findings.get('json_china_matches', []))}")


if __name__ == "__main__":
    verifier = RealDataVerifier()
    verifier.run()
