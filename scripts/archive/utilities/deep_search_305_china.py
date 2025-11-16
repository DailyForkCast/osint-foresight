#!/usr/bin/env python3
"""
Deep search for China-related records in 305-column format.
Search up to 100K records to find actual China examples.
"""

import gzip
from pathlib import Path


def deep_search():
    """Search deeper for China-related records."""

    data_file = Path("F:/OSINT_DATA/USAspending/extracted_data/5848.dat.gz")

    print("="*80)
    print("Deep China Search - 305-Column Format")
    print("="*80)
    print(f"File: {data_file.name}")
    print(f"Searching up to 100,000 records...")
    print("="*80)

    # Stricter China keywords (avoid false positives)
    china_keywords = [
        'china',
        'chinese',
        'beijing',
        'shanghai',
        'guangzhou',
        'shenzhen',
        'hong kong',
        'people\'s republic',
        'prc'
    ]

    found_count = 0
    max_samples = 20
    checked = 0

    with gzip.open(data_file, 'rt', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            if i >= 100000 or found_count >= max_samples:
                break

            checked += 1

            # Skip if only contains "information" or "machine" (false positives)
            line_lower = line.lower()
            if 'information' in line_lower and 'china' not in line_lower:
                continue
            if 'machine' in line_lower and 'china' not in line_lower:
                continue

            # Check for actual China keywords
            if any(kw in line_lower for kw in china_keywords):
                fields = line.strip().split('\t')

                # Get key fields
                recipient_name = fields[200] if len(fields) > 200 else ''
                vendor_name = fields[13] if len(fields) > 13 else ''
                country_code = fields[107] if len(fields) > 107 else ''
                country_name = fields[108] if len(fields) > 108 else ''
                alt_country = fields[50] if len(fields) > 50 else ''
                alt_country_name = fields[49] if len(fields) > 49 else ''
                award_amount = fields[160] if len(fields) > 160 else ''

                # Only show if it has China indicators in relevant fields
                relevant_text = ' '.join([
                    recipient_name, vendor_name, country_code,
                    country_name, alt_country, alt_country_name
                ]).lower()

                if any(kw in relevant_text for kw in china_keywords):
                    print(f"\n{'='*80}")
                    print(f"China Record #{found_count + 1} (Line {i + 1})")
                    print(f"{'='*80}")
                    print(f"Recipient Name [200]: {recipient_name[:80]}")
                    print(f"Vendor Name [13]: {vendor_name[:80]}")
                    print(f"Country Code [107]: {country_code}")
                    print(f"Country Name [108]: {country_name[:50]}")
                    print(f"Alt Country [50]: {alt_country}")
                    print(f"Alt Country Name [49]: {alt_country_name[:50]}")
                    print(f"Award Amount [160]: ${award_amount}")

                    # Show other potentially relevant fields
                    print("\nOther potentially relevant fields:")
                    for idx in [0, 8, 9, 21, 22, 69, 160, 192]:
                        if idx < len(fields) and fields[idx].strip():
                            print(f"  [{idx}]: {fields[idx][:80]}")

                    found_count += 1

    print(f"\n{'='*80}")
    print(f"Search complete: Checked {checked:,} records")
    print(f"Found {found_count} China-related records")
    print(f"{'='*80}")

    if found_count == 0:
        print("\nWARNING: No China records found in first 100K records.")
        print("This format may have very few China detections.")
        print("\nLet me check recipient country patterns in first 1000 records:")

        # Quick country analysis
        with gzip.open(data_file, 'rt', encoding='utf-8', errors='replace') as f:
            countries = {}
            for i, line in enumerate(f):
                if i >= 1000:
                    break
                fields = line.strip().split('\t')
                country = fields[108] if len(fields) > 108 else ''
                if country and country != '\\N':
                    countries[country] = countries.get(country, 0) + 1

        print("\nTop recipient countries (first 1000 records):")
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:20]:
            print(f"  {country}: {count}")


if __name__ == '__main__':
    deep_search()
