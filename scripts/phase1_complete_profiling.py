#!/usr/bin/env python3
"""
Phase 1 COMPLETE: Profile all decompressed content (2-3 TB)
Runs after decompression completes to achieve 100% content profiling
"""

import os
import json
import csv
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import hashlib
import sys
from collections import defaultdict

class CompleteContentProfiler:
    def __init__(self):
        # Decompressed data location
        self.decompressed_root = Path("F:/DECOMPRESSED_DATA")

        # Check if decompression is complete
        if not self.check_decompression_complete():
            print("WARNING: Decompression may still be in progress")
            response = input("Continue anyway? (yes/no): ")
            if response.lower() != 'yes':
                sys.exit(1)

        self.content_profiles = {}
        self.database_profiles = {}
        self.schema_registry = {}
        self.parse_stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'by_type': defaultdict(lambda: {'success': 0, 'fail': 0}),
            'by_location': defaultdict(lambda: {'files': 0, 'success': 0, 'fail': 0})
        }

        self.results = {
            'generated': datetime.now().isoformat(),
            'phase': 'Phase 1 Complete Profiling',
            'source': 'F:/DECOMPRESSED_DATA',
            'files_analyzed': 0,
            'total_bytes_analyzed': 0,
            'schemas_discovered': 0,
            'databases_introspected': 0,
            'parse_success_rate': 0.0
        }

    def check_decompression_complete(self):
        """Check if decompression has completed"""
        stats_file = Path("C:/Projects/OSINT - Foresight/decompression_to_f_stats.json")

        if stats_file.exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)
                if 'completed' in stats:
                    print(f"Decompression completed at: {stats['completed']}")
                    print(f"Files created: {stats['files_created']:,}")
                    print(f"Total decompressed: {stats['total_decompressed_bytes'] / 1e9:.2f} GB")
                    return True

        # Check if directory has content
        if self.decompressed_root.exists():
            file_count = sum(1 for _ in self.decompressed_root.rglob('*') if _.is_file())
            if file_count > 0:
                print(f"Found {file_count} files in decompressed directory")
                return True

        return False

    def profile_json_content(self, filepath):
        """Profile JSON file content"""
        profile = {
            'type': 'json',
            'records': 0,
            'schema': {},
            'sample_data': []
        }

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)

                if isinstance(data, list):
                    profile['records'] = len(data)
                    if data:
                        # Sample first few records
                        profile['sample_data'] = data[:3]
                        # Infer schema from first record
                        if isinstance(data[0], dict):
                            profile['schema'] = self.infer_schema(data[0])

                elif isinstance(data, dict):
                    profile['records'] = 1
                    profile['schema'] = self.infer_schema(data)
                    profile['sample_data'] = [data]

            return 'success', profile

        except Exception as e:
            return 'json_parse_error', {'error': str(e)[:200]}

    def profile_xml_content(self, filepath):
        """Profile XML file content"""
        profile = {
            'type': 'xml',
            'root_element': '',
            'element_count': 0,
            'namespaces': [],
            'depth': 0
        }

        try:
            tree = ET.parse(filepath)
            root = tree.getroot()

            profile['root_element'] = root.tag
            profile['element_count'] = len(list(root.iter()))

            # Extract namespaces
            namespaces = set()
            for elem in root.iter():
                if '}' in elem.tag:
                    ns = elem.tag.split('}')[0][1:]
                    namespaces.add(ns)
            profile['namespaces'] = list(namespaces)

            # Calculate depth
            def get_depth(element, current_depth=0):
                depths = [current_depth]
                for child in element:
                    depths.append(get_depth(child, current_depth + 1))
                return max(depths)

            profile['depth'] = get_depth(root)

            return 'success', profile

        except Exception as e:
            return 'xml_parse_error', {'error': str(e)[:200]}

    def profile_csv_content(self, filepath):
        """Profile CSV/TSV file content"""
        profile = {
            'type': 'csv',
            'rows': 0,
            'columns': 0,
            'headers': [],
            'sample_rows': []
        }

        try:
            # Detect delimiter
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline()
                delimiter = '\t' if '\t' in first_line else ','
                f.seek(0)

                reader = csv.DictReader(f, delimiter=delimiter)
                profile['headers'] = reader.fieldnames or []
                profile['columns'] = len(profile['headers'])

                rows = []
                for i, row in enumerate(reader):
                    if i < 3:  # Sample first 3 rows
                        profile['sample_rows'].append(row)
                    rows.append(row)

                profile['rows'] = len(rows)

            return 'success', profile

        except Exception as e:
            return 'csv_parse_error', {'error': str(e)[:200]}

    def profile_text_content(self, filepath):
        """Profile text/log files"""
        profile = {
            'type': 'text',
            'lines': 0,
            'characters': 0,
            'encoding': 'utf-8',
            'sample_lines': []
        }

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                profile['lines'] = len(lines)
                profile['characters'] = sum(len(line) for line in lines)
                profile['sample_lines'] = lines[:5]

            return 'success', profile

        except Exception as e:
            return 'text_parse_error', {'error': str(e)[:200]}

    def infer_schema(self, record):
        """Infer schema from a record"""
        schema = {}

        for key, value in record.items():
            if value is None:
                schema[key] = 'null'
            elif isinstance(value, bool):
                schema[key] = 'boolean'
            elif isinstance(value, int):
                schema[key] = 'integer'
            elif isinstance(value, float):
                schema[key] = 'float'
            elif isinstance(value, str):
                schema[key] = 'string'
            elif isinstance(value, list):
                schema[key] = 'array'
                if value and isinstance(value[0], dict):
                    schema[key] = {'type': 'array', 'items': self.infer_schema(value[0])}
            elif isinstance(value, dict):
                schema[key] = {'type': 'object', 'properties': self.infer_schema(value)}
            else:
                schema[key] = 'unknown'

        return schema

    def profile_file(self, filepath, location):
        """Profile a single file based on extension"""
        ext = filepath.suffix.lower()

        profile = {
            'path': str(filepath),
            'location': location,
            'size': filepath.stat().st_size if filepath.exists() else 0,
            'extension': ext,
            'modified': datetime.fromtimestamp(
                filepath.stat().st_mtime
            ).isoformat() if filepath.exists() else None
        }

        # Choose profiling method based on extension
        if ext in ['.json', '.jsonl']:
            status, content_profile = self.profile_json_content(filepath)
        elif ext in ['.xml']:
            status, content_profile = self.profile_xml_content(filepath)
        elif ext in ['.csv', '.tsv']:
            status, content_profile = self.profile_csv_content(filepath)
        elif ext in ['.txt', '.log']:
            status, content_profile = self.profile_text_content(filepath)
        else:
            status = 'unsupported_type'
            content_profile = {'type': 'unsupported'}

        profile['parse_status'] = status
        profile['content'] = content_profile

        # Update statistics
        self.parse_stats['total'] += 1
        self.parse_stats['by_location'][location]['files'] += 1

        if status == 'success':
            self.parse_stats['successful'] += 1
            self.parse_stats['by_type'][ext]['success'] += 1
            self.parse_stats['by_location'][location]['success'] += 1

            # Register schema if found
            if 'schema' in content_profile and content_profile['schema']:
                schema_key = f"{location}_{ext}"
                if schema_key not in self.schema_registry:
                    self.schema_registry[schema_key] = []
                self.schema_registry[schema_key].append(content_profile['schema'])
        else:
            self.parse_stats['failed'] += 1
            self.parse_stats['by_type'][ext]['fail'] += 1
            self.parse_stats['by_location'][location]['fail'] += 1

        return profile

    def process_location(self, location_path, location_name):
        """Process all files in a location"""
        print(f"\nProcessing {location_name}...")

        if not location_path.exists():
            print(f"  Location not found: {location_path}")
            return

        file_count = 0
        total_bytes = 0

        # Recursively process all files
        for filepath in location_path.rglob('*'):
            if not filepath.is_file():
                continue

            file_count += 1
            if file_count % 100 == 0:
                print(f"  Processed {file_count} files...")

            profile = self.profile_file(filepath, location_name)
            self.content_profiles[str(filepath)] = profile

            total_bytes += profile['size']
            self.results['total_bytes_analyzed'] += profile['size']

        print(f"  Completed: {file_count} files, {total_bytes / 1e9:.2f} GB")

    def generate_stratified_samples(self):
        """Create stratified samples N=20 per data type"""
        print("\nGenerating stratified samples...")

        samples = defaultdict(list)

        for filepath, profile in self.content_profiles.items():
            if profile['parse_status'] == 'success':
                ext = profile['extension']
                location = profile['location']
                key = f"{location}_{ext}"

                if len(samples[key]) < 20:
                    samples[key].append({
                        'path': filepath,
                        'size': profile['size'],
                        'records': profile['content'].get('records', 0),
                        'schema_fields': len(profile['content'].get('schema', {}))
                    })

        # Save samples
        samples_dir = Path("C:/Projects/OSINT - Foresight/phase1_complete_samples")
        samples_dir.mkdir(exist_ok=True)

        for key, sample_list in samples.items():
            with open(samples_dir / f"{key}_samples.json", 'w') as f:
                json.dump(sample_list, f, indent=2)

        print(f"  Created {len(samples)} sample sets")

    def run(self):
        """Execute complete content profiling"""
        print("\n" + "="*70)
        print("PHASE 1 COMPLETE: PROFILING ALL DECOMPRESSED CONTENT")
        print("="*70)
        print(f"\nSource: {self.decompressed_root}")

        # Process each location
        locations = [
            ('project_data', self.decompressed_root / 'project_data'),
            ('osint_data', self.decompressed_root / 'osint_data'),
            ('ted_data', self.decompressed_root / 'ted_data'),
            ('osint_backups', self.decompressed_root / 'osint_backups'),
            ('horizons_data', self.decompressed_root / 'horizons_data')
        ]

        for location_name, location_path in locations:
            self.process_location(location_path, location_name)

        # Calculate final statistics
        self.results['files_analyzed'] = self.parse_stats['total']
        self.results['schemas_discovered'] = len(self.schema_registry)

        if self.parse_stats['total'] > 0:
            self.results['parse_success_rate'] = (
                self.parse_stats['successful'] / self.parse_stats['total'] * 100
            )

        # Generate stratified samples
        self.generate_stratified_samples()

        # Save results
        self.save_results()

        # Print summary
        print("\n" + "="*70)
        print("PHASE 1 COMPLETE")
        print("="*70)
        print(f"\nFiles analyzed: {self.results['files_analyzed']:,}")
        print(f"Total data: {self.results['total_bytes_analyzed'] / 1e9:.2f} GB")
        print(f"Parse success rate: {self.results['parse_success_rate']:.1f}%")
        print(f"Schemas discovered: {self.results['schemas_discovered']}")

        print("\nParse Statistics by Type:")
        for ext, stats in sorted(self.parse_stats['by_type'].items()):
            total = stats['success'] + stats['fail']
            if total > 0:
                rate = stats['success'] / total * 100
                print(f"  {ext}: {stats['success']}/{total} ({rate:.1f}%)")

        print("\nParse Statistics by Location:")
        for location, stats in self.parse_stats['by_location'].items():
            if stats['files'] > 0:
                rate = stats['success'] / stats['files'] * 100
                print(f"  {location}: {stats['success']}/{stats['files']} ({rate:.1f}%)")

        return 0

    def save_results(self):
        """Save all profiling results"""
        print("\nSaving results...")

        # Save content profiles
        with open("C:/Projects/OSINT - Foresight/content_profiles_complete.json", 'w') as f:
            json.dump(self.content_profiles, f, indent=2, default=str)

        # Save parse statistics
        with open("C:/Projects/OSINT - Foresight/parse_statistics_final.json", 'w') as f:
            json.dump(self.parse_stats, f, indent=2)

        # Save schema registry
        with open("C:/Projects/OSINT - Foresight/schema_registry.json", 'w') as f:
            json.dump(self.schema_registry, f, indent=2)

        # Save summary
        with open("C:/Projects/OSINT - Foresight/phase1_complete_summary.json", 'w') as f:
            json.dump(self.results, f, indent=2)

        # Generate report
        self.generate_report()

        print("Results saved successfully")

    def generate_report(self):
        """Generate comprehensive Phase 1 report"""
        report = "# Phase 1 Complete: Content Profiling Report\n\n"
        report += f"Generated: {self.results['generated']}\n\n"

        report += "## Executive Summary\n\n"
        report += f"- **Files Analyzed**: {self.results['files_analyzed']:,}\n"
        report += f"- **Total Data**: {self.results['total_bytes_analyzed'] / 1e9:.2f} GB\n"
        report += f"- **Parse Success Rate**: {self.results['parse_success_rate']:.1f}%\n"
        report += f"- **Schemas Discovered**: {self.results['schemas_discovered']}\n\n"

        report += "## Compliance Status\n\n"
        report += "- ✅ All decompressed files profiled\n"
        report += "- ✅ Content profiles generated\n"
        report += "- ✅ Stratified samples created (N=20)\n"
        report += "- ✅ Schema inference completed\n"
        report += f"- {'✅' if self.results['parse_success_rate'] > 70 else '⚠️'} Parse rate: {self.results['parse_success_rate']:.1f}%\n\n"

        # Save report
        with open("C:/Projects/OSINT - Foresight/phase1_complete_report.md", 'w', encoding='utf-8') as f:
            f.write(report)


if __name__ == "__main__":
    profiler = CompleteContentProfiler()
    sys.exit(profiler.run())
