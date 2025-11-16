#!/usr/bin/env python3
"""Verify 374-column schema field mappings."""

import gzip

print("="*80)
print("VERIFYING 374-COLUMN SCHEMA")
print("="*80)

with gzip.open('F:/OSINT_DATA/USAspending/extracted_data/5877.dat.gz', 'rt', encoding='utf-8', errors='replace') as f:
    # Read first record
    first = f.readline().strip().split('\t')

    print(f'\nTotal columns in file: {len(first)}')
    print()

    # Check our claimed field positions
    print("CLAIMED FIELD POSITIONS:")
    print("-" * 80)
    claimed_fields = {
        41: 'recipient_location_country_name',
        42: 'recipient_location_country_code',
        54: 'pop_country',
        69: 'recipient_name',
        72: 'recipient_parent_name',
    }

    for idx, field_name in sorted(claimed_fields.items()):
        val = first[idx] if idx < len(first) else "OUT OF RANGE"
        print(f"[{idx:3d}] {field_name:40s} = {val}")

    # Search for country-related fields
    print("\n" + "="*80)
    print("ACTUAL COUNTRY FIELDS FOUND:")
    print("-" * 80)
    country_keywords = ['UNITED STATES', 'USA', 'CHINA', 'HONG KONG', 'CHN']
    for i, val in enumerate(first):
        if val.upper() in country_keywords:
            print(f"[{i:3d}] {val}")

    # Search for company name fields
    print("\n" + "="*80)
    print("COMPANY NAME FIELDS (with INC, LLC, CORP, JR):")
    print("-" * 80)
    name_keywords = ['INC', 'LLC', 'CORP', 'JR', 'CO ']
    for i, val in enumerate(first):
        if len(val) > 5 and val != r'\N':
            if any(kw in val.upper() for kw in name_keywords):
                display = val[:60] + "..." if len(val) > 60 else val
                print(f"[{i:3d}] {display}")

    print("\n" + "="*80)
    print("TESTING WITH SECOND RECORD (for confirmation):")
    print("-" * 80)

    # Read second record
    second = f.readline().strip().split('\t')
    print(f'Second record columns: {len(second)}')
    print()

    for idx, field_name in sorted(claimed_fields.items()):
        val = second[idx] if idx < len(second) else "OUT OF RANGE"
        print(f"[{idx:3d}] {field_name:40s} = {val}")

    print("\n" + "="*80)
