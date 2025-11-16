#!/usr/bin/env python3
"""
Validate Filtered Eurostat COMEXT Data
Inspect CSV files before database loading
Date: November 1, 2025
"""

import csv
import os
from pathlib import Path
from collections import Counter
import json

# Directories
FILTERED_DIR = Path("F:/OSINT_Data/Trade_Facilities/eurostat_comext_v3")
OUTPUT_FILE = Path("analysis/eurostat_filtered_validation_20251101.json")

def validate_filtered_data():
    """Validate all filtered CSV files"""

    print("="*80)
    print("EUROSTAT FILTERED DATA VALIDATION")
    print("="*80)
    print(f"Directory: {FILTERED_DIR}")
    print()

    # Find all filtered CSV files
    csv_files = list(FILTERED_DIR.glob("*_china_all_products.csv"))

    if not csv_files:
        print(f"[ERROR] No filtered CSV files found in {FILTERED_DIR}")
        return

    print(f"Found {len(csv_files)} filtered CSV files")
    print()

    validation_results = {
        'total_files': len(csv_files),
        'files': [],
        'column_analysis': {},
        'data_quality': {},
        'sample_records': []
    }

    # Validate each file
    for csv_file in sorted(csv_files):
        print("="*80)
        print(f"Validating: {csv_file.name}")
        print("="*80)

        file_stats = {
            'filename': csv_file.name,
            'size_mb': csv_file.stat().st_size / (1024 * 1024),
            'record_count': 0,
            'columns': [],
            'sample_partners': [],
            'sample_reporters': [],
            'sample_products': [],
            'has_value_column': False,
            'has_quantity_column': False
        }

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                # Get column names
                file_stats['columns'] = reader.fieldnames if reader.fieldnames else []

                print(f"Size: {file_stats['size_mb']:.2f} MB")
                print(f"Columns ({len(file_stats['columns'])}): {', '.join(file_stats['columns'][:10])}")
                if len(file_stats['columns']) > 10:
                    print(f"         ... and {len(file_stats['columns']) - 10} more")
                print()

                # Check for key columns
                columns_lower = [col.lower() for col in file_stats['columns']]
                file_stats['has_value_column'] = any('value' in col for col in columns_lower)
                file_stats['has_quantity_column'] = any('quantity' in col or 'qty' in col for col in columns_lower)

                # Analyze first 1000 rows
                partners = Counter()
                reporters = Counter()
                products = Counter()
                trade_types = Counter()

                for i, row in enumerate(reader):
                    file_stats['record_count'] += 1

                    if i < 1000:
                        # Sample first 1000 rows
                        partner = row.get('PARTNER', row.get('partner', ''))
                        reporter = row.get('REPORTER', row.get('reporter', ''))
                        product = row.get('PRODUCT_NC', row.get('product_nc', row.get('PRODUCT', '')))
                        trade_type = row.get('TRADE_TYPE', row.get('trade_type', row.get('FLOW', '')))

                        if partner:
                            partners[partner] += 1
                        if reporter:
                            reporters[reporter] += 1
                        if product:
                            products[product] += 1
                        if trade_type:
                            trade_types[trade_type] += 1

                    # Save first 3 records as samples
                    if i < 3:
                        validation_results['sample_records'].append({
                            'file': csv_file.name,
                            'record': dict(row)
                        })

                    # Progress indicator
                    if file_stats['record_count'] % 50000 == 0:
                        print(f"  Validated {file_stats['record_count']:,} records...", end='\r')

                print(f"  Validated {file_stats['record_count']:,} records     ")

                # Store top values
                file_stats['sample_partners'] = [{'code': k, 'count': v} for k, v in partners.most_common(10)]
                file_stats['sample_reporters'] = [{'code': k, 'count': v} for k, v in reporters.most_common(10)]
                file_stats['sample_products'] = [{'code': k, 'count': v} for k, v in products.most_common(10)]
                file_stats['trade_types'] = [{'type': k, 'count': v} for k, v in trade_types.most_common(10)]

                # Display summary
                print()
                print(f"Record Count: {file_stats['record_count']:,}")
                print(f"Has Value Column: {file_stats['has_value_column']}")
                print(f"Has Quantity Column: {file_stats['has_quantity_column']}")
                print()

                if partners:
                    print("Top Partners (sample from first 1000 rows):")
                    for code, count in partners.most_common(5):
                        print(f"  {code}: {count:,}")
                    print()

                if reporters:
                    print("Top Reporters (sample from first 1000 rows):")
                    for code, count in reporters.most_common(5):
                        print(f"  {code}: {count:,}")
                    print()

                if products:
                    print("Top Products (sample from first 1000 rows):")
                    for code, count in products.most_common(5):
                        product_code = code[:30] + '...' if len(code) > 30 else code
                        print(f"  {product_code}: {count:,}")
                    print()

                if trade_types:
                    print("Trade Types (sample from first 1000 rows):")
                    for tt, count in trade_types.most_common(5):
                        print(f"  {tt}: {count:,}")
                    print()

        except Exception as e:
            print(f"[ERROR] Failed to validate {csv_file.name}: {e}")
            file_stats['error'] = str(e)

        validation_results['files'].append(file_stats)

    # Overall statistics
    print("="*80)
    print("VALIDATION SUMMARY")
    print("="*80)

    total_records = sum(f['record_count'] for f in validation_results['files'])
    total_size_mb = sum(f['size_mb'] for f in validation_results['files'])

    print(f"Total Files: {validation_results['total_files']}")
    print(f"Total Records: {total_records:,}")
    print(f"Total Size: {total_size_mb:.2f} MB ({total_size_mb/1024:.2f} GB)")
    print()

    # Check column consistency
    if validation_results['files']:
        first_columns = set(validation_results['files'][0]['columns'])
        all_same = all(set(f['columns']) == first_columns for f in validation_results['files'])

        print(f"Column Consistency: {'✓ All files have same columns' if all_same else '✗ Column mismatch detected'}")

        if not all_same:
            print("\nColumn Variations:")
            for f in validation_results['files']:
                if set(f['columns']) != first_columns:
                    print(f"  {f['filename']}: {len(f['columns'])} columns")
        print()

    # Data quality checks
    print("DATA QUALITY CHECKS:")

    # Check for China partners
    china_partners_found = set()
    for f in validation_results['files']:
        for partner_info in f['sample_partners']:
            if partner_info['code'] in ['CN', 'HK', 'MO']:
                china_partners_found.add(partner_info['code'])

    print(f"  China partners found: {', '.join(sorted(china_partners_found)) if china_partners_found else 'NONE'}")
    if china_partners_found:
        print("  ✓ China/HK/Macau partners confirmed")
    else:
        print("  ✗ WARNING: No China/HK/Macau partners in sample data!")
    print()

    # Check for strategic product columns
    if validation_results['files']:
        sample_columns = validation_results['files'][0]['columns']
        product_columns = [col for col in sample_columns if 'product' in col.lower() or 'nc' in col.lower() or 'cn8' in col.lower()]

        print(f"  Product-related columns found: {', '.join(product_columns) if product_columns else 'NONE'}")
        if product_columns:
            print("  ✓ Product classification columns available")
        else:
            print("  ✗ WARNING: No obvious product columns detected")
        print()

    # Save validation results
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2, ensure_ascii=False)

    print(f"✓ Validation results saved to: {OUTPUT_FILE}")
    print()

    # Display sample record
    if validation_results['sample_records']:
        print("="*80)
        print("SAMPLE RECORD (from first file)")
        print("="*80)
        sample = validation_results['sample_records'][0]['record']
        for key, value in sample.items():
            print(f"  {key:25} = {value}")
        print()

    print("="*80)
    print("VALIDATION COMPLETE")
    print("="*80)
    print()
    print("Next Steps:")
    print("1. Review validation results to understand data structure")
    print("2. Verify China/HK/Macau partner codes are present")
    print("3. Identify correct product code column for strategic filtering")
    print("4. Proceed with database loading if validation passes")
    print()

if __name__ == '__main__':
    validate_filtered_data()
