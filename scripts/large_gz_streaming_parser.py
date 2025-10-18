#!/usr/bin/env python3
"""
Large .gz File Streaming Parser
Handles very large compressed files using streaming to avoid memory issues
"""

import gzip
import json
from pathlib import Path
from datetime import datetime
import sys
from collections import defaultdict

class LargeGzStreamingParser:
    def __init__(self):
        self.source_root = Path("F:/DECOMPRESSED_DATA")
        self.large_gz_files = []
        self.parsing_results = {
            'generated': datetime.now().isoformat(),
            'files_analyzed': 0,
            'total_size_gb': 0,
            'samples_extracted': 0,
            'file_summaries': []
        }

    def find_large_gz_files(self):
        """Find remaining large .gz files"""
        print("\nSearching for large .gz files...")

        for gz_file in self.source_root.rglob('*.gz'):
            size_gb = gz_file.stat().st_size / 1e9

            if size_gb > 1.0:  # Files larger than 1GB
                self.large_gz_files.append({
                    'path': gz_file,
                    'name': gz_file.name,
                    'size_gb': round(size_gb, 2),
                    'location': gz_file.parent.name
                })
                self.parsing_results['total_size_gb'] += size_gb

        self.large_gz_files.sort(key=lambda x: x['size_gb'], reverse=True)

        print(f"Found {len(self.large_gz_files)} large .gz files")
        print(f"Total size: {self.parsing_results['total_size_gb']:.2f} GB compressed")

        # Show top files
        print("\nLargest files:")
        for file_info in self.large_gz_files[:5]:
            print(f"  {file_info['name']}: {file_info['size_gb']} GB")

        return self.large_gz_files

    def stream_parse_gz_file(self, file_info, max_lines=10000):
        """Stream parse a large .gz file without loading it all into memory"""
        filepath = file_info['path']
        print(f"\nStream parsing {file_info['name']} ({file_info['size_gb']} GB)...")

        summary = {
            'filename': file_info['name'],
            'size_gb': file_info['size_gb'],
            'lines_sampled': 0,
            'format': 'unknown',
            'sample_data': [],
            'statistics': defaultdict(int),
            'data_patterns': {}
        }

        try:
            with gzip.open(filepath, 'rt', encoding='utf-8', errors='ignore') as f:
                # Read first line to detect format
                first_line = f.readline()

                if not first_line:
                    summary['format'] = 'empty'
                    return summary

                # Detect format
                if first_line.startswith('PGDMP'):
                    summary['format'] = 'postgres_dump'
                elif first_line.startswith('{') or first_line.startswith('['):
                    summary['format'] = 'json'
                elif '\t' in first_line:
                    summary['format'] = 'tsv'
                elif ',' in first_line:
                    summary['format'] = 'csv'
                elif first_line.startswith('<'):
                    summary['format'] = 'xml'
                else:
                    summary['format'] = 'text'

                # Sample first N lines
                f.seek(0)  # Reset to beginning

                for i, line in enumerate(f):
                    if i >= max_lines:
                        break

                    summary['lines_sampled'] += 1

                    # Store samples
                    if i < 100:  # First 100 lines
                        summary['sample_data'].append(line[:500])  # Limit line length

                    # Analyze patterns
                    if i % 1000 == 0:  # Check every 1000th line
                        self.analyze_line_patterns(line, summary)

                print(f"  Sampled {summary['lines_sampled']} lines")
                print(f"  Format detected: {summary['format']}")

        except Exception as e:
            summary['error'] = str(e)[:200]
            print(f"  Error: {e}")

        return summary

    def analyze_line_patterns(self, line, summary):
        """Analyze patterns in a line"""
        # Count field separators
        summary['statistics']['tabs'] += line.count('\t')
        summary['statistics']['commas'] += line.count(',')
        summary['statistics']['pipes'] += line.count('|')

        # Check for timestamps
        if '2020' in line or '2021' in line or '2022' in line or '2023' in line or '2024' in line or '2025' in line:
            summary['statistics']['date_references'] += 1

        # Check for numeric patterns
        if any(c.isdigit() for c in line):
            summary['statistics']['numeric_lines'] += 1

        # Check for JSON-like structures
        if '{' in line or '[' in line:
            summary['statistics']['json_like'] += 1

        # Look for SQL patterns
        if any(sql in line.upper() for sql in ['CREATE', 'INSERT', 'SELECT', 'TABLE']):
            summary['statistics']['sql_patterns'] += 1

    def extract_insights(self):
        """Extract insights from all parsed files"""
        insights = {
            'total_files': len(self.parsing_results['file_summaries']),
            'format_distribution': defaultdict(int),
            'postgres_dumps': [],
            'json_files': [],
            'csv_tsv_files': [],
            'unknown_format': []
        }

        for summary in self.parsing_results['file_summaries']:
            fmt = summary.get('format', 'unknown')
            insights['format_distribution'][fmt] += 1

            if fmt == 'postgres_dump':
                insights['postgres_dumps'].append(summary['filename'])
            elif fmt == 'json':
                insights['json_files'].append(summary['filename'])
            elif fmt in ['csv', 'tsv']:
                insights['csv_tsv_files'].append(summary['filename'])
            else:
                insights['unknown_format'].append(summary['filename'])

        return insights

    def save_results(self):
        """Save parsing results"""
        print("\nSaving results...")

        # Save full results
        with open("C:/Projects/OSINT - Foresight/large_gz_parsing_results.json", 'w') as f:
            json.dump(self.parsing_results, f, indent=2, default=str)

        # Extract and save insights
        insights = self.extract_insights()
        with open("C:/Projects/OSINT - Foresight/large_gz_insights.json", 'w') as f:
            json.dump(insights, f, indent=2)

        # Generate report
        self.generate_report(insights)

        print("Results saved")

    def generate_report(self, insights):
        """Generate parsing report"""
        report = "# Large .gz Files Streaming Parse Report\n\n"
        report += f"Generated: {datetime.now().isoformat()}\n\n"

        report += "## Summary\n\n"
        report += f"- Files analyzed: {self.parsing_results['files_analyzed']}\n"
        report += f"- Total size: {self.parsing_results['total_size_gb']:.2f} GB (compressed)\n"
        report += f"- Samples extracted: {self.parsing_results['samples_extracted']}\n\n"

        report += "## Format Distribution\n\n"
        for fmt, count in insights['format_distribution'].items():
            report += f"- **{fmt}**: {count} files\n"

        report += "\n## File Categories\n\n"

        if insights['postgres_dumps']:
            report += "### PostgreSQL Dumps\n"
            for filename in insights['postgres_dumps'][:10]:
                report += f"- {filename}\n"
            report += "\n"

        if insights['json_files']:
            report += "### JSON Files\n"
            for filename in insights['json_files'][:10]:
                report += f"- {filename}\n"
            report += "\n"

        if insights['csv_tsv_files']:
            report += "### CSV/TSV Files\n"
            for filename in insights['csv_tsv_files'][:10]:
                report += f"- {filename}\n"
            report += "\n"

        report += "## Recommendations\n\n"
        report += "1. **PostgreSQL dumps**: Restore to database for full access\n"
        report += "2. **JSON files**: Can be directly parsed and analyzed\n"
        report += "3. **CSV/TSV files**: Import to pandas for analysis\n"
        report += "4. **Very large files**: Consider cloud-based processing\n"

        report += "\n## Next Steps\n\n"
        report += "- For immediate analysis: Focus on JSON and CSV files\n"
        report += "- For comprehensive data: Set up PostgreSQL and restore dumps\n"
        report += "- For big data processing: Consider Apache Spark or similar\n"

        with open("C:/Projects/OSINT - Foresight/large_gz_parsing_report.md", 'w', encoding='utf-8') as f:
            f.write(report)

        print("Report saved: large_gz_parsing_report.md")

    def run(self, sample_only=True):
        """Execute the streaming parser"""
        print("\n" + "="*70)
        print("LARGE .GZ FILES STREAMING PARSER")
        print("="*70)

        # Find large files
        self.find_large_gz_files()

        if not self.large_gz_files:
            print("No large .gz files found")
            return 0

        # Determine how many to process
        files_to_process = self.large_gz_files[:3] if sample_only else self.large_gz_files

        if sample_only:
            print(f"\nSampling mode: Processing top {len(files_to_process)} largest files")
        else:
            print(f"\nProcessing all {len(files_to_process)} files")

        # Process each file
        for i, file_info in enumerate(files_to_process, 1):
            print(f"\n[{i}/{len(files_to_process)}] Processing {file_info['name']}...")

            summary = self.stream_parse_gz_file(file_info)
            self.parsing_results['file_summaries'].append(summary)
            self.parsing_results['files_analyzed'] += 1
            self.parsing_results['samples_extracted'] += len(summary['sample_data'])

        # Save results
        self.save_results()

        print("\n" + "="*70)
        print("STREAMING PARSE COMPLETE")
        print("="*70)
        print(f"\nAnalyzed {self.parsing_results['files_analyzed']} large files")
        print(f"Extracted {self.parsing_results['samples_extracted']} sample lines")

        return 0


if __name__ == "__main__":
    # Run in sample mode to avoid long processing times
    parser = LargeGzStreamingParser()
    sys.exit(parser.run(sample_only=True))
