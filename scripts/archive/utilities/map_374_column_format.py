#!/usr/bin/env python3
"""
Map 374-column USAspending format to known detection fields.

Analyzes the 374-column file format and identifies which columns
correspond to the critical China detection fields.
"""

import gzip
from pathlib import Path

# Critical detection fields from 206-column schema (0-indexed)
KNOWN_SCHEMA_206 = {
    23: 'recipient_name',
    27: 'recipient_parent_name',
    29: 'recipient_location_country_name',
    39: 'pop_country_name',
    59: 'sub_awardee_name',
    63: 'sub_awardee_parent_name',
    65: 'sub_awardee_country_name',
    46: 'award_description',
    82: 'subaward_description',
}

def analyze_format(file_path: Path, num_records: int = 10):
    """Analyze file format and try to identify key columns."""

    print(f"Analyzing: {file_path.name}")
    print(f"=" * 80)

    records = []
    with gzip.open(file_path, 'rt', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            if i >= num_records:
                break
            fields = line.strip().split('\t')
            records.append(fields)

    if not records:
        print("No records found!")
        return

    num_cols = len(records[0])
    print(f"\nTotal columns: {num_cols}")
    print(f"Records analyzed: {len(records)}")

    # Look for columns containing country names
    print(f"\n{'='*80}")
    print("SEARCHING FOR COUNTRY FIELDS")
    print(f"{'='*80}")

    for col_idx in range(num_cols):
        # Get sample values from this column
        values = set()
        for record in records:
            if col_idx < len(record):
                val = record[col_idx].strip()
                if val and val != '\\N':
                    values.add(val)

        # Check if this looks like a country field
        country_keywords = ['UNITED STATES', 'USA', 'CHINA', 'HONG KONG']
        if any(kw in str(values).upper() for kw in country_keywords):
            sample_vals = list(values)[:5]
            print(f"\n[{col_idx}] Possible country field:")
            print(f"    Sample values: {sample_vals}")

    # Look for columns containing organization names
    print(f"\n{'='*80}")
    print("SEARCHING FOR NAME FIELDS")
    print(f"{'='*80}")

    for col_idx in range(num_cols):
        values = set()
        for record in records:
            if col_idx < len(record):
                val = record[col_idx].strip()
                if val and val != '\\N' and len(val) > 5:
                    values.add(val)

        # Check if contains organization name patterns
        org_keywords = ['INC', 'LLC', 'CORP', 'UNIVERSITY', 'COMPANY', 'LTD']
        sample_text = ' '.join(list(values)[:3]).upper()

        if any(kw in sample_text for kw in org_keywords):
            sample_vals = list(values)[:3]
            print(f"\n[{col_idx}] Possible name field:")
            print(f"    Sample values: {sample_vals}")

    # Print sample record structure
    print(f"\n{'='*80}")
    print("SAMPLE RECORD (First 50 fields)")
    print(f"{'='*80}")

    if records:
        first_record = records[0]
        for i in range(min(50, len(first_record))):
            val = first_record[i]
            if len(val) > 60:
                val = val[:57] + "..."
            print(f"[{i:3d}] {val}")


def compare_formats():
    """Compare 374-column and 206-column formats."""

    file_374 = Path("F:/OSINT_DATA/USAspending/extracted_data/5877.dat.gz")
    file_206 = Path("F:/OSINT_DATA/USAspending/extracted_data/5876.dat.gz")

    print("\n" + "="*80)
    print("374-COLUMN FORMAT ANALYSIS")
    print("="*80)
    analyze_format(file_374, num_records=20)

    print("\n\n" + "="*80)
    print("206-COLUMN FORMAT ANALYSIS (FOR REFERENCE)")
    print("="*80)
    analyze_format(file_206, num_records=20)

    print("\n\n" + "="*80)
    print("DETECTION FIELD MAPPING - 206-COLUMN FORMAT")
    print("="*80)

    # Load 206-column samples to verify schema
    with gzip.open(file_206, 'rt', encoding='utf-8', errors='replace') as f:
        sample_206 = f.readline().strip().split('\t')

    print("\nKnown detection fields (206-column format):")
    for idx, field_name in KNOWN_SCHEMA_206.items():
        val = sample_206[idx] if idx < len(sample_206) else "N/A"
        if len(val) > 60:
            val = val[:57] + "..."
        print(f"  [{idx:3d}] {field_name:40s} = {val}")


if __name__ == '__main__':
    compare_formats()
