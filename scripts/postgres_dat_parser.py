#!/usr/bin/env python3
"""
PostgreSQL .dat File Parser
Parses PostgreSQL COPY format data from USASpending database dumps
"""

import re
import json
import csv
from pathlib import Path
from datetime import datetime
import sys
from collections import defaultdict

class PostgresDatParser:
    def __init__(self):
        self.data_root = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906")
        self.parsed_data = defaultdict(list)
        self.table_schemas = {}
        self.statistics = {
            'files_found': 0,
            'files_parsed': 0,
            'tables_extracted': 0,
            'total_rows': 0,
            'parse_errors': 0
        }

    def parse_toc_file(self):
        """Parse the table of contents file to understand database structure"""
        toc_file = self.data_root / "toc.dat"

        if not toc_file.exists():
            print("ERROR: toc.dat not found")
            return False

        print("\nParsing table of contents...")

        try:
            with open(toc_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract table definitions
            table_pattern = r'CREATE TABLE\s+(?:"?(\w+)"?\.)?"?(\w+)"?\s*\((.*?)\);'
            tables = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)

            for schema, table, columns in tables:
                full_name = f"{schema}.{table}" if schema else table

                # Parse column definitions
                col_pattern = r'"?(\w+)"?\s+(\w+(?:\s*\([^)]+\))?)'
                columns_found = re.findall(col_pattern, columns)

                self.table_schemas[full_name] = {
                    'schema': schema,
                    'table': table,
                    'columns': [{'name': col[0], 'type': col[1]} for col in columns_found]
                }

            print(f"Found {len(self.table_schemas)} table definitions")

            # Also look for COPY statements that map data files to tables
            copy_pattern = r'COPY\s+(?:"?(\w+)"?\.)?"?(\w+)"?\s*(?:\((.*?)\))?\s+FROM stdin;'
            copy_statements = re.findall(copy_pattern, content, re.IGNORECASE)

            self.copy_mappings = []
            for schema, table, columns in copy_statements:
                self.copy_mappings.append({
                    'schema': schema,
                    'table': table,
                    'columns': columns.split(',') if columns else []
                })

            print(f"Found {len(self.copy_mappings)} COPY statements")

            return True

        except Exception as e:
            print(f"Error parsing toc.dat: {e}")
            return False

    def parse_data_file(self, filepath):
        """Parse a single .dat data file"""
        try:
            rows = []
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # Skip empty lines and PostgreSQL end marker
                    if not line.strip() or line.strip() == '\\.' or line.startswith('PGDMP'):
                        continue

                    # Split by tab (PostgreSQL COPY default delimiter)
                    fields = line.strip().split('\t')

                    # Clean fields
                    cleaned_fields = []
                    for field in fields:
                        # Handle NULL values
                        if field == '\\N':
                            cleaned_fields.append(None)
                        else:
                            cleaned_fields.append(field)

                    rows.append(cleaned_fields)

            return rows

        except Exception as e:
            print(f"Error parsing {filepath.name}: {e}")
            self.statistics['parse_errors'] += 1
            return []

    def infer_table_from_data(self, data_rows, filename):
        """Infer table structure from data patterns"""
        if not data_rows:
            return None

        # Analyze first few rows to infer structure
        sample = data_rows[:10]

        column_count = len(sample[0]) if sample else 0

        # Try to detect data types
        column_types = []
        for col_idx in range(column_count):
            types_found = set()

            for row in sample:
                if col_idx < len(row):
                    value = row[col_idx]
                    if value is None:
                        continue
                    elif re.match(r'^\d+$', value):
                        types_found.add('integer')
                    elif re.match(r'^\d+\.\d+$', value):
                        types_found.add('decimal')
                    elif re.match(r'^\d{4}-\d{2}-\d{2}', value):
                        types_found.add('timestamp')
                    elif value.lower() in ['true', 'false', 't', 'f']:
                        types_found.add('boolean')
                    else:
                        types_found.add('text')

            # Choose most likely type
            if 'timestamp' in types_found:
                column_types.append('timestamp')
            elif 'decimal' in types_found:
                column_types.append('decimal')
            elif 'integer' in types_found:
                column_types.append('integer')
            elif 'boolean' in types_found:
                column_types.append('boolean')
            else:
                column_types.append('text')

        return {
            'filename': filename,
            'row_count': len(data_rows),
            'column_count': column_count,
            'inferred_types': column_types,
            'sample_data': data_rows[:5]
        }

    def process_all_dat_files(self):
        """Process all .dat files in the directory"""
        print(f"\nScanning for .dat files in {self.data_root}...")

        dat_files = list(self.data_root.glob("*.dat"))

        # Exclude toc.dat
        dat_files = [f for f in dat_files if f.name != "toc.dat"]

        self.statistics['files_found'] = len(dat_files)
        print(f"Found {len(dat_files)} data files")

        # Process files
        for i, filepath in enumerate(dat_files, 1):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(dat_files)} files...")

            # Skip very large files for now
            file_size = filepath.stat().st_size
            if file_size > 100 * 1024 * 1024:  # Skip files > 100MB
                print(f"Skipping large file {filepath.name} ({file_size / 1e6:.1f} MB)")
                continue

            print(f"[{i}/{len(dat_files)}] Parsing {filepath.name} ({file_size / 1e6:.2f} MB)...")

            # Parse the data
            rows = self.parse_data_file(filepath)

            if rows:
                # Infer table structure
                table_info = self.infer_table_from_data(rows, filepath.name)

                if table_info:
                    self.parsed_data[filepath.name] = table_info
                    self.statistics['files_parsed'] += 1
                    self.statistics['total_rows'] += len(rows)

                    # Save a sample for analysis
                    if i <= 5:  # Save first 5 files as samples
                        sample_file = Path(f"C:/Projects/OSINT - Foresight/dat_samples/{filepath.stem}_sample.json")
                        sample_file.parent.mkdir(exist_ok=True)

                        with open(sample_file, 'w') as f:
                            json.dump(table_info, f, indent=2, default=str)

    def extract_usaspending_insights(self):
        """Extract key insights from parsed USASpending data"""
        print("\nExtracting USASpending insights...")

        insights = {
            'total_tables': len(self.parsed_data),
            'total_rows': self.statistics['total_rows'],
            'table_summary': [],
            'data_patterns': {}
        }

        # Analyze each parsed table
        for filename, table_info in self.parsed_data.items():
            insights['table_summary'].append({
                'file': filename,
                'rows': table_info['row_count'],
                'columns': table_info['column_count'],
                'types': table_info['inferred_types']
            })

            # Look for interesting patterns
            for row in table_info.get('sample_data', [])[:10]:
                # Look for dollar amounts
                for field in row:
                    if field and isinstance(field, str):
                        if '$' in field or re.match(r'^\d+\.?\d*$', field):
                            if 'financial_values' not in insights['data_patterns']:
                                insights['data_patterns']['financial_values'] = []
                            insights['data_patterns']['financial_values'].append(field)

                        # Look for dates
                        if re.match(r'\d{4}-\d{2}-\d{2}', field):
                            if 'dates' not in insights['data_patterns']:
                                insights['data_patterns']['dates'] = []
                            insights['data_patterns']['dates'].append(field)

                        # Look for organization names
                        if len(field) > 10 and field[0].isupper():
                            if 'possible_orgs' not in insights['data_patterns']:
                                insights['data_patterns']['possible_orgs'] = []
                            insights['data_patterns']['possible_orgs'].append(field[:100])

        return insights

    def save_results(self):
        """Save parsing results"""
        print("\nSaving results...")

        # Save parsed data summary
        summary = {
            'generated': datetime.now().isoformat(),
            'statistics': self.statistics,
            'tables_found': len(self.table_schemas),
            'files_parsed': len(self.parsed_data),
            'table_schemas': self.table_schemas,
            'parsed_files': list(self.parsed_data.keys())
        }

        with open("C:/Projects/OSINT - Foresight/postgres_dat_parse_summary.json", 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        # Save insights
        insights = self.extract_usaspending_insights()

        with open("C:/Projects/OSINT - Foresight/usaspending_insights.json", 'w') as f:
            json.dump(insights, f, indent=2, default=str)

        # Generate report
        self.generate_report(insights)

        print("Results saved")

    def generate_report(self, insights):
        """Generate parsing report"""
        report = "# PostgreSQL .dat Files Parsing Report\n\n"
        report += f"Generated: {datetime.now().isoformat()}\n\n"

        report += "## Summary\n\n"
        report += f"- Files found: {self.statistics['files_found']}\n"
        report += f"- Files parsed: {self.statistics['files_parsed']}\n"
        report += f"- Total rows extracted: {self.statistics['total_rows']:,}\n"
        report += f"- Parse errors: {self.statistics['parse_errors']}\n\n"

        report += "## Table Structures Found\n\n"
        if self.table_schemas:
            for table_name, schema in list(self.table_schemas.items())[:10]:
                report += f"### {table_name}\n"
                report += f"- Columns: {len(schema['columns'])}\n"
                for col in schema['columns'][:5]:
                    report += f"  - {col['name']}: {col['type']}\n"
                report += "\n"
        else:
            report += "No table schemas extracted from toc.dat\n\n"

        report += "## Data Insights\n\n"
        report += f"- Total tables processed: {insights['total_tables']}\n"
        report += f"- Total data rows: {insights['total_rows']:,}\n\n"

        if insights['data_patterns']:
            report += "### Data Patterns Found\n\n"
            for pattern_type, examples in insights['data_patterns'].items():
                report += f"- **{pattern_type}**: {len(examples)} instances\n"
                for example in examples[:3]:
                    report += f"  - {example}\n"

        report += "\n## Next Steps\n\n"
        report += "1. Consider restoring to PostgreSQL for full access\n"
        report += "2. Focus on specific tables of interest\n"
        report += "3. Build targeted extractors for key data types\n"

        with open("C:/Projects/OSINT - Foresight/postgres_dat_parsing_report.md", 'w', encoding='utf-8') as f:
            f.write(report)

        print("Report saved: postgres_dat_parsing_report.md")

    def run(self):
        """Execute the parser"""
        print("\n" + "="*70)
        print("POSTGRESQL .DAT FILES PARSER")
        print("="*70)

        # Parse table of contents
        self.parse_toc_file()

        # Process all data files
        self.process_all_dat_files()

        # Save results
        self.save_results()

        print("\n" + "="*70)
        print("PARSING COMPLETE")
        print("="*70)
        print(f"\nParsed {self.statistics['files_parsed']} files")
        print(f"Extracted {self.statistics['total_rows']:,} total rows")

        return 0


if __name__ == "__main__":
    parser = PostgresDatParser()
    sys.exit(parser.run())
