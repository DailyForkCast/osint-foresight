#!/usr/bin/env python3
"""
USAspending Database Schema Analyzer

Comprehensive analysis of all 206 columns in USAspending transaction data.
Extracts column names, examines sample data, categorizes by purpose.

Input: F:/OSINT_DATA/USAspending/extracted_data/*.dat.gz
Output: analysis/USASPENDING_SCHEMA_COMPREHENSIVE.md
"""

import gzip
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

def analyze_large_file(file_path: Path, sample_size: int = 100) -> Dict:
    """Analyze a large USAspending .dat.gz file."""

    print(f"\n{'='*80}")
    print(f"Analyzing: {file_path.name}")
    print(f"Size: {file_path.stat().st_size / (1024**3):.1f} GB")
    print(f"{'='*80}\n")

    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
        # Get header
        header = f.readline().strip().split('\t')
        num_columns = len(header)

        print(f"Total columns: {num_columns}\n")

        # Sample records
        records = []
        for i, line in enumerate(f):
            if i >= sample_size:
                break
            records.append(line.strip().split('\t'))

        print(f"Sampled {len(records)} records\n")

        return {
            'file': file_path.name,
            'num_columns': num_columns,
            'header': header,
            'sample_records': records
        }

def categorize_columns(header: List[str]) -> Dict[str, List[Tuple[int, str]]]:
    """Categorize columns by logical groupings."""

    categories = defaultdict(list)

    for idx, col in enumerate(header):
        col_lower = col.lower()

        # Transaction metadata
        if any(x in col_lower for x in ['transaction', 'award_id', 'piid', 'fain', 'uri',
                                         'action_date', 'fiscal_year', 'period_of_performance',
                                         'generated', 'last_modified', 'certified_date']):
            categories['Transaction Metadata'].append((idx, col))

        # Financial amounts
        elif any(x in col_lower for x in ['amount', 'obligation', 'outlay', 'funding',
                                           'potential_total', 'base_and_all', 'cost',
                                           'dollars', 'subsidy']):
            categories['Financial'].append((idx, col))

        # Awarding/Funding Agency
        elif any(x in col_lower for x in ['awarding', 'funding']) and \
             any(x in col_lower for x in ['agency', 'office', 'department', 'toptier', 'subtier']):
            categories['Agency Information'].append((idx, col))

        # Recipient/Contractor
        elif any(x in col_lower for x in ['recipient', 'awardee', 'parent_recipient',
                                           'ultimate_parent']):
            categories['Recipient Information'].append((idx, col))

        # Business classifications
        elif any(x in col_lower for x in ['business_type', 'small_business', 'minority',
                                           'woman_owned', 'veteran', 'category_business',
                                           'organization_type', 'entity_structure']):
            categories['Business Classifications'].append((idx, col))

        # Locations (recipient and place of performance)
        elif any(x in col_lower for x in ['location', 'address', 'city', 'state', 'country',
                                           'zip', 'county', 'congressional', 'place_of_performance',
                                           'pop_']):
            categories['Geographic Location'].append((idx, col))

        # Product/Service codes
        elif any(x in col_lower for x in ['naics', 'psc', 'product_or_service',
                                           'contract_award_type']):
            categories['Product/Service Codes'].append((idx, col))

        # Description/narrative
        elif any(x in col_lower for x in ['description', 'title', 'narrative', 'text']):
            categories['Descriptions'].append((idx, col))

        # Contract type and procurement
        elif any(x in col_lower for x in ['type_of_contract', 'extent_competed',
                                           'number_of_offers', 'solicitation',
                                           'procurement', 'pricing', 'contract_bundling']):
            categories['Contract Details'].append((idx, col))

        # CFDA/Assistance
        elif any(x in col_lower for x in ['cfda', 'assistance', 'grant', 'loan']):
            categories['Assistance Programs'].append((idx, col))

        # Officer names
        elif any(x in col_lower for x in ['officer', 'contact', 'official']):
            categories['Personnel'].append((idx, col))

        # IDs and codes
        elif any(x in col_lower for x in ['uei', 'duns', 'ein', 'sam', 'cage', 'dod_claimant',
                                           'program_number']):
            categories['Identifiers'].append((idx, col))

        # Timestamps
        elif any(x in col_lower for x in ['create_date', 'update_date', 'date_signed',
                                           'timestamp']):
            categories['Timestamps'].append((idx, col))

        # Search vectors (PostgreSQL full-text search)
        elif 'to_tsvector' in col_lower or col_lower.endswith('_ts'):
            categories['Search Vectors'].append((idx, col))

        # Miscellaneous
        else:
            categories['Other'].append((idx, col))

    return dict(categories)

def get_sample_values(records: List[List[str]], col_idx: int, max_samples: int = 5) -> List[str]:
    """Get sample values for a column, excluding NULLs."""

    samples = []
    for record in records:
        if col_idx < len(record):
            value = record[col_idx]
            if value and value != '\\N' and value not in samples:
                samples.append(value)
                if len(samples) >= max_samples:
                    break

    return samples

def generate_markdown_report(analysis: Dict, categories: Dict, output_path: Path):
    """Generate comprehensive markdown report."""

    header = analysis['header']
    records = analysis['sample_records']

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# USAspending Database - Complete Schema Analysis\n\n")
        f.write(f"**Source File**: {analysis['file']}\n")
        f.write(f"**Total Columns**: {analysis['num_columns']}\n")
        f.write(f"**Sample Size**: {len(records)} records\n")
        f.write(f"**Analysis Date**: 2025-10-11\n\n")

        f.write("---\n\n")
        f.write("## Table of Contents\n\n")
        for category in sorted(categories.keys()):
            anchor = category.lower().replace(' ', '-').replace('/', '')
            f.write(f"- [{category}](#{anchor}) ({len(categories[category])} columns)\n")
        f.write("\n---\n\n")

        # Category sections
        for category in sorted(categories.keys()):
            columns = sorted(categories[category])

            f.write(f"## {category}\n\n")
            f.write(f"**Total**: {len(columns)} columns\n\n")

            for col_idx, col_name in columns:
                samples = get_sample_values(records, col_idx, max_samples=3)

                f.write(f"### [{col_idx}] `{col_name}`\n\n")

                if samples:
                    f.write("**Sample Values**:\n")
                    for sample in samples:
                        # Truncate long values
                        display = sample[:100] + '...' if len(sample) > 100 else sample
                        f.write(f"- `{display}`\n")
                    f.write("\n")
                else:
                    f.write("*No non-null values in sample*\n\n")

                # Check NULL rate
                null_count = sum(1 for r in records if col_idx < len(r) and
                                 (not r[col_idx] or r[col_idx] == '\\N'))
                null_rate = (null_count / len(records)) * 100 if records else 0

                if null_rate > 50:
                    f.write(f"**NULL Rate**: {null_rate:.0f}% (high)\n\n")
                elif null_rate > 0:
                    f.write(f"**NULL Rate**: {null_rate:.0f}%\n\n")

            f.write("---\n\n")

        # Summary statistics
        f.write("## Summary Statistics\n\n")
        f.write(f"| Category | Columns | Percentage |\n")
        f.write(f"|----------|---------|------------|\n")

        total = analysis['num_columns']
        for category in sorted(categories.keys(), key=lambda x: len(categories[x]), reverse=True):
            count = len(categories[category])
            pct = (count / total) * 100
            f.write(f"| {category} | {count} | {pct:.1f}% |\n")

        f.write("\n---\n\n")

        # Key columns for China detection
        f.write("## Key Columns for China-Related Detection\n\n")
        f.write("Based on schema analysis, these columns are most relevant for identifying China-related transactions:\n\n")

        f.write("### Primary Detection Fields\n")
        f.write("1. **Recipient Information**: Entity names, parent companies\n")
        f.write("2. **Geographic Location**: Country codes, addresses\n")
        f.write("3. **Descriptions**: Award descriptions, narratives\n")
        f.write("4. **Product/Service Codes**: NAICS and PSC classifications\n\n")

        f.write("### Secondary Detection Fields\n")
        f.write("5. **Business Classifications**: Entity types, ownership\n")
        f.write("6. **Identifiers**: DUNS, UEI, CAGE codes (for cross-referencing)\n")
        f.write("7. **Search Vectors**: Full-text search fields (if available)\n\n")

        f.write("---\n\n")
        f.write("## Next Steps\n\n")
        f.write("1. **Design Detection Logic**: Multi-field strategy for China entity detection\n")
        f.write("2. **Validation Strategy**: Test on known entities (TED cross-reference)\n")
        f.write("3. **Processing Pipeline**: Batch processing for 215 GB dataset\n")
        f.write("4. **Cross-Reference**: Link to CORDIS, OpenAlex, TED databases\n")

def main():
    # Find a large transaction file
    data_dir = Path("F:/OSINT_DATA/USAspending/extracted_data")

    if not data_dir.exists():
        print(f"ERROR: Data directory not found: {data_dir}")
        sys.exit(1)

    # Use 5876.dat.gz (4.9 GB) - large but not the largest
    target_file = data_dir / "5876.dat.gz"

    if not target_file.exists():
        print(f"ERROR: Target file not found: {target_file}")
        sys.exit(1)

    # Analyze
    print("Starting comprehensive schema analysis...")
    analysis = analyze_large_file(target_file, sample_size=100)

    # Categorize
    print("Categorizing columns...")
    categories = categorize_columns(analysis['header'])

    print("\nCategory Summary:")
    for category, columns in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {category}: {len(columns)} columns")

    # Generate report
    output_path = Path("analysis/USASPENDING_SCHEMA_COMPREHENSIVE.md")
    print(f"\nGenerating report: {output_path}")
    generate_markdown_report(analysis, categories, output_path)

    print("\n" + "="*80)
    print("✅ Schema analysis complete!")
    print(f"   Report: {output_path}")
    print("="*80)

if __name__ == '__main__':
    main()
