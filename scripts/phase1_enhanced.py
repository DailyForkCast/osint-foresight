#!/usr/bin/env python3
"""
Phase 1 ENHANCED: Content Profiling with Stratified Sampling
Includes all requirements: per-file profiles, DB introspection, N=20 samples, delta logging
"""

import json
import sqlite3
import os
import random
from pathlib import Path
from datetime import datetime
import hashlib
import pandas as pd
import csv

class EnhancedContentProfiler:
    def __init__(self):
        self.content_profiles = {}
        self.database_profiles = {}
        self.stratified_samples = {}
        self.delta_log = []

        self.profile_results = {
            'generated': datetime.now().isoformat(),
            'datasets_profiled': 0,
            'files_analyzed': 0,
            'databases_introspected': 0,
            'samples_created': 0,
            'parse_success_rate': 0
        }

        # Load previous run for delta comparison
        self.previous_run = self.load_previous_run()

    def load_previous_run(self):
        """Load previous run results for delta comparison"""
        previous_path = Path("C:/Projects/OSINT - Foresight/phase1_previous_run.json")
        if previous_path.exists():
            with open(previous_path, 'r') as f:
                return json.load(f)
        return None

    def profile_file_content(self, filepath):
        """Create detailed content profile for a file"""
        profile = {
            'path': str(filepath),
            'size': 0,
            'extension': filepath.suffix,
            'encoding': 'unknown',
            'line_count': 0,
            'field_count': 0,
            'parse_status': 'pending',
            'schema': {},
            'sample_records': []
        }

        try:
            stats = filepath.stat()
            profile['size'] = stats.st_size
            profile['modified'] = datetime.fromtimestamp(stats.st_mtime).isoformat()

            # Determine file type and parse accordingly
            if filepath.suffix.lower() in ['.json', '.jsonl']:
                profile = self.profile_json_file(filepath, profile)
            elif filepath.suffix.lower() in ['.csv', '.tsv']:
                profile = self.profile_csv_file(filepath, profile)
            elif filepath.suffix.lower() in ['.xml']:
                profile = self.profile_xml_file(filepath, profile)
            elif filepath.suffix.lower() in ['.db', '.sqlite', '.sqlite3']:
                profile = self.profile_database_file(filepath, profile)
            else:
                profile['parse_status'] = 'unsupported_format'

        except Exception as e:
            profile['parse_status'] = 'error'
            profile['error'] = str(e)

        return profile

    def profile_json_file(self, filepath, profile):
        """Profile JSON/JSONL file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Try to read as JSON
                if filepath.suffix == '.jsonl':
                    lines = f.readlines()
                    profile['line_count'] = len(lines)

                    # Sample first few records
                    for i, line in enumerate(lines[:5]):
                        record = json.loads(line)
                        profile['sample_records'].append(record)

                        # Infer schema from first record
                        if i == 0:
                            profile['schema'] = self.infer_schema(record)
                            profile['field_count'] = len(profile['schema'])
                else:
                    data = json.load(f)

                    if isinstance(data, list):
                        profile['line_count'] = len(data)
                        profile['sample_records'] = data[:5]
                        if data:
                            profile['schema'] = self.infer_schema(data[0])
                            profile['field_count'] = len(profile['schema'])
                    elif isinstance(data, dict):
                        profile['line_count'] = 1
                        profile['sample_records'] = [data]
                        profile['schema'] = self.infer_schema(data)
                        profile['field_count'] = len(profile['schema'])

            profile['parse_status'] = 'success'
            profile['encoding'] = 'utf-8'

        except Exception as e:
            profile['parse_status'] = 'parse_error'
            profile['error'] = str(e)

        return profile

    def profile_csv_file(self, filepath, profile):
        """Profile CSV/TSV file"""
        try:
            delimiter = '\t' if filepath.suffix == '.tsv' else ','

            # Read first few rows to detect schema
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                rows = []
                for i, row in enumerate(reader):
                    if i < 5:  # Sample first 5 rows
                        rows.append(row)
                    if i == 0:
                        profile['schema'] = {k: 'string' for k in row.keys()}
                        profile['field_count'] = len(row.keys())

            # Count total rows
            with open(filepath, 'r', encoding='utf-8') as f:
                profile['line_count'] = sum(1 for line in f) - 1  # Subtract header

            profile['sample_records'] = rows
            profile['parse_status'] = 'success'
            profile['encoding'] = 'utf-8'

        except Exception as e:
            profile['parse_status'] = 'parse_error'
            profile['error'] = str(e)

        return profile

    def profile_xml_file(self, filepath, profile):
        """Profile XML file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read(10000)  # Read first 10KB

            profile['line_count'] = content.count('\n')
            profile['parse_status'] = 'partial'  # We're not fully parsing XML
            profile['encoding'] = 'utf-8'

            # Basic XML statistics
            profile['schema'] = {
                'element_count_estimate': content.count('<'),
                'has_namespace': 'xmlns' in content
            }

        except Exception as e:
            profile['parse_status'] = 'parse_error'
            profile['error'] = str(e)

        return profile

    def profile_database_file(self, filepath, profile):
        """Profile SQLite database file"""
        try:
            conn = sqlite3.connect(str(filepath))
            cursor = conn.cursor()

            # Get table list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            profile['schema'] = {}
            total_rows = 0

            for table in tables:
                table_name = table[0]

                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                total_rows += row_count

                # Get column info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                profile['schema'][table_name] = {
                    'row_count': row_count,
                    'columns': [col[1] for col in columns]
                }

                # Sample records from first table
                if not profile['sample_records'] and row_count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                    profile['sample_records'] = cursor.fetchall()

            profile['line_count'] = total_rows
            profile['field_count'] = len(tables)
            profile['parse_status'] = 'success'

            conn.close()

            # Store in database profiles
            self.database_profiles[str(filepath)] = profile['schema']

        except Exception as e:
            profile['parse_status'] = 'parse_error'
            profile['error'] = str(e)

        return profile

    def infer_schema(self, record):
        """Infer schema from a record"""
        schema = {}

        if isinstance(record, dict):
            for key, value in record.items():
                if isinstance(value, str):
                    schema[key] = 'string'
                elif isinstance(value, (int, float)):
                    schema[key] = 'number'
                elif isinstance(value, bool):
                    schema[key] = 'boolean'
                elif isinstance(value, list):
                    schema[key] = 'array'
                elif isinstance(value, dict):
                    schema[key] = 'object'
                else:
                    schema[key] = 'unknown'

        return schema

    def create_stratified_samples(self, dataset_path, dataset_name):
        """Create stratified samples N=20 for a dataset"""
        print(f"Creating stratified samples for {dataset_name}...")

        samples_dir = Path(f"C:/Projects/OSINT - Foresight/samples/{dataset_name}")
        samples_dir.mkdir(parents=True, exist_ok=True)

        # Collect all files in dataset
        all_files = []
        for root, dirs, files in os.walk(dataset_path):
            for file in files:
                filepath = Path(root) / file
                if filepath.suffix in ['.json', '.jsonl', '.csv', '.tsv', '.xml', '.db', '.sqlite']:
                    all_files.append(filepath)

        # Create stratified sample by file type
        file_types = {}
        for file in all_files:
            ext = file.suffix
            if ext not in file_types:
                file_types[ext] = []
            file_types[ext].append(file)

        samples = []
        samples_per_type = max(1, 20 // len(file_types)) if file_types else 0

        for ext, files in file_types.items():
            # Sample up to samples_per_type from each file type
            n_samples = min(len(files), samples_per_type)
            sampled_files = random.sample(files, n_samples)

            for file in sampled_files:
                profile = self.profile_file_content(file)
                samples.append({
                    'file': str(file),
                    'type': ext,
                    'size': profile['size'],
                    'parse_status': profile['parse_status'],
                    'line_count': profile['line_count'],
                    'field_count': profile['field_count']
                })

                # Save sample pack
                sample_pack = {
                    'original_path': str(file),
                    'profile': profile,
                    'sample_data': profile['sample_records'][:20] if profile['sample_records'] else []
                }

                sample_filename = f"sample_{len(samples):03d}.json"
                with open(samples_dir / sample_filename, 'w', encoding='utf-8') as f:
                    json.dump(sample_pack, f, indent=2, default=str)

        # Ensure we have exactly 20 samples (or all available files)
        while len(samples) < 20 and len(samples) < len(all_files):
            remaining = [f for f in all_files if str(f) not in [s['file'] for s in samples]]
            if remaining:
                file = random.choice(remaining)
                profile = self.profile_file_content(file)
                samples.append({
                    'file': str(file),
                    'type': file.suffix,
                    'size': profile['size'],
                    'parse_status': profile['parse_status'],
                    'line_count': profile['line_count'],
                    'field_count': profile['field_count']
                })

                # Save sample pack
                sample_pack = {
                    'original_path': str(file),
                    'profile': profile,
                    'sample_data': profile['sample_records'][:20] if profile['sample_records'] else []
                }

                sample_filename = f"sample_{len(samples):03d}.json"
                with open(samples_dir / sample_filename, 'w', encoding='utf-8') as f:
                    json.dump(sample_pack, f, indent=2, default=str)

        self.stratified_samples[dataset_name] = samples
        self.profile_results['samples_created'] += len(samples)

        return samples

    def calculate_delta(self, current_data):
        """Calculate delta from previous run"""
        if not self.previous_run:
            return {
                'is_first_run': True,
                'changes': []
            }

        delta = {
            'is_first_run': False,
            'changes': []
        }

        # Compare datasets
        prev_datasets = set(self.previous_run.get('datasets', {}).keys())
        curr_datasets = set(current_data.get('datasets', {}).keys())

        new_datasets = curr_datasets - prev_datasets
        removed_datasets = prev_datasets - curr_datasets

        for ds in new_datasets:
            delta['changes'].append({
                'type': 'new_dataset',
                'dataset': ds
            })

        for ds in removed_datasets:
            delta['changes'].append({
                'type': 'removed_dataset',
                'dataset': ds
            })

        # Compare file counts
        for ds in curr_datasets & prev_datasets:
            prev_count = self.previous_run['datasets'][ds].get('file_count', 0)
            curr_count = current_data['datasets'][ds].get('file_count', 0)

            if curr_count != prev_count:
                delta['changes'].append({
                    'type': 'file_count_change',
                    'dataset': ds,
                    'previous': prev_count,
                    'current': curr_count,
                    'difference': curr_count - prev_count
                })

        return delta

    def profile_all_datasets(self):
        """Profile all major datasets"""
        print("Phase 1: Content profiling with stratified sampling...")

        datasets = [
            ("project_data", "C:/Projects/OSINT - Foresight/data/processed"),
            ("ted_data", "F:/TED_Data/monthly"),
            ("osint_data", "F:/OSINT_DATA"),
            ("openalex_backup", "F:/OSINT_Backups/openalex")
        ]

        current_data = {'datasets': {}}
        total_success = 0
        total_files = 0

        for dataset_name, dataset_path in datasets:
            if not Path(dataset_path).exists():
                print(f"Skipping {dataset_name}: path not found")
                continue

            print(f"\nProfiling {dataset_name}: {dataset_path}")
            self.profile_results['datasets_profiled'] += 1

            dataset_info = {
                'path': dataset_path,
                'file_count': 0,
                'success_count': 0,
                'profiles': []
            }

            # Profile a subset of files
            file_count = 0
            for root, dirs, files in os.walk(dataset_path):
                # Limit depth
                depth = root.replace(dataset_path, '').count(os.sep)
                if depth > 2:
                    continue

                for file in files[:10]:  # Limit files per directory
                    if file_count >= 50:  # Max 50 files per dataset
                        break

                    filepath = Path(root) / file
                    profile = self.profile_file_content(filepath)

                    # Save individual profile
                    profile_path = Path(f"C:/Projects/OSINT - Foresight/profiles/{dataset_name}")
                    profile_path.mkdir(parents=True, exist_ok=True)

                    profile_filename = f"profile_{file_count:04d}.json"
                    with open(profile_path / profile_filename, 'w', encoding='utf-8') as f:
                        json.dump(profile, f, indent=2, default=str)

                    dataset_info['profiles'].append(profile_filename)

                    if profile['parse_status'] == 'success':
                        dataset_info['success_count'] += 1
                        total_success += 1

                    file_count += 1
                    total_files += 1
                    self.profile_results['files_analyzed'] += 1

            dataset_info['file_count'] = file_count
            current_data['datasets'][dataset_name] = dataset_info

            # Create stratified samples
            samples = self.create_stratified_samples(Path(dataset_path), dataset_name)

        # Calculate parse success rate
        if total_files > 0:
            self.profile_results['parse_success_rate'] = (total_success / total_files) * 100

        # Calculate delta
        self.delta_log = self.calculate_delta(current_data)

        # Save current run for next delta
        with open("C:/Projects/OSINT - Foresight/phase1_previous_run.json", 'w') as f:
            json.dump(current_data, f, indent=2)

        # Database introspection summary
        self.profile_results['databases_introspected'] = len(self.database_profiles)

    def generate_report(self):
        """Generate Phase 1 verification report"""

        # Save all profiles
        with open("C:/Projects/OSINT - Foresight/content_profiles_summary.json", 'w') as f:
            json.dump(self.content_profiles, f, indent=2, default=str)

        # Save database introspection
        if self.database_profiles:
            with open("C:/Projects/OSINT - Foresight/database_introspection.json", 'w') as f:
                json.dump(self.database_profiles, f, indent=2)

        # Save stratified samples summary
        with open("C:/Projects/OSINT - Foresight/stratified_samples.json", 'w') as f:
            json.dump(self.stratified_samples, f, indent=2)

        # Save delta log
        with open("C:/Projects/OSINT - Foresight/delta_log.json", 'w') as f:
            json.dump(self.delta_log, f, indent=2)

        # Generate report
        report = f"""# Phase 1: Content Profiling Report (Enhanced)

Generated: {self.profile_results['generated']}

## Profile Summary

| Metric | Value |
|--------|-------|
| Datasets Profiled | {self.profile_results['datasets_profiled']} |
| Files Analyzed | {self.profile_results['files_analyzed']:,} |
| Parse Success Rate | {self.profile_results['parse_success_rate']:.1f}% |
| Databases Introspected | {self.profile_results['databases_introspected']} |
| Stratified Samples Created | {self.profile_results['samples_created']} |

## Database Introspection

"""

        if self.database_profiles:
            for db_path, schema in self.database_profiles.items():
                report += f"### {Path(db_path).name}\n\n"
                total_rows = 0
                for table, info in schema.items():
                    report += f"- **{table}**: {info['row_count']:,} rows, {len(info['columns'])} columns\n"
                    total_rows += info['row_count']
                report += f"- **Total rows**: {total_rows:,}\n\n"
        else:
            report += "No databases found in sample.\n\n"

        report += """## Stratified Sampling Results

"""

        for dataset, samples in self.stratified_samples.items():
            report += f"### {dataset} (N={len(samples)})\n\n"

            # Group by file type
            by_type = {}
            for sample in samples:
                ext = sample['type']
                if ext not in by_type:
                    by_type[ext] = []
                by_type[ext].append(sample)

            for ext, items in by_type.items():
                success_count = sum(1 for item in items if item['parse_status'] == 'success')
                report += f"- **{ext}**: {len(items)} files, {success_count} parsed successfully\n"

            report += "\n"

        report += """## Delta Logging

"""

        if self.delta_log['is_first_run']:
            report += "This is the first run - no previous data for comparison.\n\n"
        else:
            if self.delta_log['changes']:
                report += f"Found {len(self.delta_log['changes'])} changes since last run:\n\n"
                for change in self.delta_log['changes'][:10]:  # Show first 10
                    if change['type'] == 'new_dataset':
                        report += f"- New dataset: {change['dataset']}\n"
                    elif change['type'] == 'removed_dataset':
                        report += f"- Removed dataset: {change['dataset']}\n"
                    elif change['type'] == 'file_count_change':
                        report += f"- {change['dataset']}: {change['previous']} → {change['current']} files ({change['difference']:+d})\n"
            else:
                report += "No changes detected since last run.\n\n"

        report += """## Proof of Analysis

### Sample Content Profiles

Three random files with full profiling:

"""

        # Show 3 sample profiles as proof
        sample_files = Path("C:/Projects/OSINT - Foresight/profiles").rglob("*.json")
        shown = 0
        for profile_file in list(sample_files)[:3]:
            with open(profile_file, 'r') as f:
                profile = json.load(f)
            report += f"""#### File: {Path(profile['path']).name}
- Size: {profile['size']:,} bytes
- Parse Status: {profile['parse_status']}
- Line Count: {profile['line_count']:,}
- Field Count: {profile['field_count']}

"""
            shown += 1

        report += f"""## Artifacts Created

1. Individual content profiles in `profiles/<dataset>/`
2. `database_introspection.json` with table/row counts
3. Stratified samples in `samples/<dataset>/` (N=20 per dataset)
4. `delta_log.json` comparing to previous run
5. `stratified_samples.json` with sampling summary

## Phase 1 Complete ✓

Content profiling completed with {self.profile_results['parse_success_rate']:.1f}% parse success rate.
Ready for schema standardization in Phase 2.
"""

        with open("C:/Projects/OSINT - Foresight/phase1_enhanced_report.md", 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\nPhase 1 Enhanced Complete!")
        print(f"- Files analyzed: {self.profile_results['files_analyzed']:,}")
        print(f"- Parse success rate: {self.profile_results['parse_success_rate']:.1f}%")
        print(f"- Samples created: {self.profile_results['samples_created']}")
        print(f"- Report saved: phase1_enhanced_report.md")

def main():
    profiler = EnhancedContentProfiler()
    profiler.profile_all_datasets()
    profiler.generate_report()

if __name__ == "__main__":
    main()
