#!/usr/bin/env python3
"""
Deep schema analysis for 305-column USAspending format.

Target: 5848.dat.gz (15.4 GB, 305 columns)
Goal: Map detection fields (names, countries, award amounts)
"""

import gzip
from pathlib import Path


def analyze_305_schema():
    """Analyze 305-column format to identify detection fields."""

    data_file = Path("F:/OSINT_DATA/USAspending/extracted_data/5848.dat.gz")

    if not data_file.exists():
        print(f"ERROR: File not found: {data_file}")
        return

    print("="*80)
    print("305-Column Schema Analysis")
    print("="*80)
    print(f"File: {data_file.name}")
    print(f"Size: 15.4 GB")
    print("="*80)

    # Sample records
    sample_size = 100
    records = []

    print(f"\nReading first {sample_size} records...")
    with gzip.open(data_file, 'rt', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            if i >= sample_size:
                break
            fields = line.strip().split('\t')
            records.append(fields)

            if i == 0:
                print(f"Columns detected: {len(fields)}")

    # Analyze field patterns
    print("\n" + "="*80)
    print("FIELD PATTERN ANALYSIS")
    print("="*80)

    # Key field candidates
    name_candidates = []
    country_candidates = []
    amount_candidates = []
    date_candidates = []

    for idx in range(len(records[0])):
        # Collect samples for this field
        samples = [r[idx] if idx < len(r) else '' for r in records[:20]]
        non_empty = [s for s in samples if s.strip()]

        if not non_empty:
            continue

        sample_str = non_empty[0] if non_empty else ''

        # Check for country indicators
        if any(country in sample_str.upper() for country in ['USA', 'UNITED STATES', 'CHINA', 'CHN']):
            country_candidates.append((idx, sample_str[:50]))

        # Check for country codes (2-3 letter codes)
        if len(sample_str) == 3 and sample_str.isalpha() and sample_str.isupper():
            country_candidates.append((idx, f"{sample_str} (code)"))

        # Check for amounts (numeric with decimals)
        if sample_str.replace('.', '').replace('-', '').replace(',', '').isdigit():
            try:
                val = float(sample_str.replace(',', ''))
                if abs(val) > 100:  # Likely currency
                    amount_candidates.append((idx, f"${val:,.2f}"))
            except:
                pass

        # Check for dates
        if '-' in sample_str and any(c.isdigit() for c in sample_str):
            if len(sample_str) > 8 and sample_str.count('-') >= 2:
                date_candidates.append((idx, sample_str[:20]))

    print("\nCOUNTRY FIELD CANDIDATES:")
    for idx, sample in country_candidates[:30]:
        print(f"  [{idx}]: {sample}")

    print("\nAMOUNT FIELD CANDIDATES:")
    for idx, sample in amount_candidates[:15]:
        print(f"  [{idx}]: {sample}")

    print("\nDATE FIELD CANDIDATES:")
    for idx, sample in date_candidates[:10]:
        print(f"  [{idx}]: {sample}")

    # Print detailed sample records
    print("\n" + "="*80)
    print("SAMPLE RECORDS (First 5)")
    print("="*80)

    for rec_num, record in enumerate(records[:5]):
        print(f"\n--- Record {rec_num + 1} (Fields: {len(record)}) ---")
        for idx, field in enumerate(record):
            if field.strip():  # Only show non-empty
                display = field[:80] if len(field) > 80 else field
                print(f"  [{idx}]: {display}")

    # Search for China-related samples
    print("\n" + "="*80)
    print("SEARCHING FOR CHINA-RELATED SAMPLES")
    print("="*80)

    china_keywords = ['china', 'chinese', 'beijing', 'shanghai', 'chn']
    found_count = 0
    max_samples = 10

    print(f"\nScanning up to 10,000 records for China keywords...")
    with gzip.open(data_file, 'rt', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            if i >= 10000 or found_count >= max_samples:
                break

            line_lower = line.lower()
            if any(kw in line_lower for kw in china_keywords):
                fields = line.strip().split('\t')
                print(f"\n--- China-related Record #{i + 1} (Fields: {len(fields)}) ---")

                # Show fields that might contain China references
                for idx, field in enumerate(fields):
                    field_lower = field.lower()
                    if any(kw in field_lower for kw in china_keywords) or (
                        any(c in field.upper() for c in ['USA', 'CHN', 'TWN']) and len(field) <= 50
                    ):
                        display = field[:100] if len(field) > 100 else field
                        print(f"  [{idx}]: {display}")

                found_count += 1

    print(f"\nFound {found_count} China-related samples")

    # Summary
    print("\n" + "="*80)
    print("CRITICAL FIELDS FOR CHINA DETECTION")
    print("="*80)

    print("\nBased on analysis, key fields appear to be:")
    print("(Verify these by examining sample records above)")
    print("\nCountry fields:")
    for idx, sample in country_candidates[:10]:
        print(f"  - [{idx}]: {sample}")

    print("\nAmount fields:")
    for idx, sample in amount_candidates[:5]:
        print(f"  - [{idx}]: {sample}")


if __name__ == '__main__':
    analyze_305_schema()
