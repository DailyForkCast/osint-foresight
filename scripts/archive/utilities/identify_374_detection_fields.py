#!/usr/bin/env python3
"""
Identify China detection fields in 374-column USAspending format.

Maps the 374-column schema to the known detection strategy fields.
"""

import gzip
from pathlib import Path

def analyze_file_for_detection_fields():
    """Identify key detection fields in 374-column format."""

    file_path = Path("F:/OSINT_DATA/USAspending/extracted_data/5877.dat.gz")

    print("="*80)
    print("374-COLUMN FORMAT - DETECTION FIELD IDENTIFICATION")
    print("="*80)
    print(f"\nAnalyzing: {file_path.name}")
    print(f"Reading first 100 records...\n")

    records = []
    with gzip.open(file_path, 'rt', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            if i >= 100:
                break
            fields = line.strip().split('\t')
            records.append(fields)

    print(f"Records loaded: {len(records)}")
    print(f"Columns in format: {len(records[0]) if records else 0}")

    # Confirmed prime recipient fields
    print("\n" + "="*80)
    print("CONFIRMED: PRIME RECIPIENT FIELDS")
    print("="*80)

    prime_fields = {
        69: 'recipient_name',
        72: 'recipient_parent_name',
        41: 'recipient_location_country_name',
        42: 'recipient_location_country_code',
        54: 'pop_country (place of performance)',
    }

    for col_idx, field_name in sorted(prime_fields.items()):
        print(f"\n[{col_idx}] {field_name}")
        # Show 5 sample values
        samples = []
        for record in records[:10]:
            if col_idx < len(record):
                val = record[col_idx]
                if val and val != '\\N':
                    samples.append(val)
        print(f"    Samples: {samples[:5]}")

    # Search for sub-awardee fields
    print("\n" + "="*80)
    print("SEARCHING: SUB-AWARDEE FIELDS")
    print("="*80)

    # Known company patterns
    company_keywords = ['INC', 'LLC', 'CORP', 'LTD', 'COMPANY', 'CORPORATION',
                        'INTERNATIONAL', 'TECHNOLOGIES', 'SYSTEMS']

    # Check columns that might contain sub-awardee data
    # These are typically in a separate section of the record
    candidate_ranges = [
        (200, 300, "Mid-range section"),
        (300, 374, "High-range section"),
    ]

    potential_subawardee_fields = {}

    for start, end, section_name in candidate_ranges:
        print(f"\n{section_name} (columns {start}-{end}):")

        for col_idx in range(start, min(end, len(records[0]))):
            # Count how many records have company-like values
            company_count = 0
            samples = []

            for record in records:
                if col_idx < len(record):
                    val = record[col_idx].upper()
                    if val and val != '\\N' and len(val) > 5:
                        if any(kw in val for kw in company_keywords):
                            company_count += 1
                            if len(samples) < 5:
                                samples.append(record[col_idx])

            if company_count >= 3:  # At least 3 records match
                print(f"  [{col_idx}] {company_count} company-like values")
                print(f"        Samples: {samples[:3]}")
                potential_subawardee_fields[col_idx] = samples

    # Look for country fields in sub-awardee sections
    print("\n" + "="*80)
    print("SEARCHING: SUB-AWARDEE COUNTRY FIELDS")
    print("="*80)

    country_keywords = ['UNITED STATES', 'USA', 'CHINA', 'HONG KONG', 'JAPAN', 'JPN']

    for col_idx in range(200, min(374, len(records[0]))):
        country_count = 0
        samples = set()

        for record in records:
            if col_idx < len(record):
                val = record[col_idx].upper()
                if val and val != '\\N':
                    if any(kw in val for kw in country_keywords):
                        country_count += 1
                        samples.add(record[col_idx])

        if country_count >= 5:  # At least 5 records match
            print(f"  [{col_idx}] Country field - {country_count} matches")
            print(f"        Values: {list(samples)[:5]}")

    # Look for description fields
    print("\n" + "="*80)
    print("SEARCHING: DESCRIPTION FIELDS")
    print("="*80)

    for col_idx in range(len(records[0])):
        long_text_count = 0
        for record in records:
            if col_idx < len(record):
                val = record[col_idx]
                if val and val != '\\N' and len(val) > 50:
                    long_text_count += 1

        if long_text_count >= 10:  # At least 10 records have long text
            sample = records[0][col_idx] if col_idx < len(records[0]) else "N/A"
            if len(sample) > 100:
                sample = sample[:97] + "..."
            print(f"  [{col_idx}] Long text field ({long_text_count}/100 records)")
            print(f"        Sample: {sample}")

    # Final summary
    print("\n" + "="*80)
    print("DETECTION FIELD MAPPING SUMMARY (374-COLUMN FORMAT)")
    print("="*80)
    print("""
Based on analysis, the critical fields are:

PRIMARY RECIPIENT DETECTION:
  [69]  recipient_name
  [72]  recipient_parent_name
  [41]  recipient_location_country_name
  [42]  recipient_location_country_code
  [54]  pop_country (place of performance)

SUB-AWARDEE DETECTION:
  [TBD] - Further analysis needed
  - Check columns 200-374 for sub-awardee data
  - Sub-awardee section may not exist in all records
  - May need to process only prime contractor records

NEXT STEPS:
1. Create processor for 374-column format using confirmed fields
2. Test detection logic on known Chinese entities
3. Process 100GB of data (files 5877, 5878)
4. Analyze detection rates and validate results
""")


if __name__ == '__main__':
    analyze_file_for_detection_fields()
