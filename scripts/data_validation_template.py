#!/usr/bin/env python3
"""
Data Validation Template
Use this before any data analysis to avoid Terminal E-type errors
"""

import json
import pandas as pd
from pathlib import Path

def validate_data_structure(filepath):
    """
    Always run this first to understand your data
    """
    print(f"\n{'='*60}")
    print(f"DATA STRUCTURE VALIDATION")
    print(f"File: {filepath}")
    print(f"{'='*60}")

    # Load data
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Basic info
    print(f"\nBasic Information:")
    print(f"  Total records: {len(data)}")
    print(f"  Data type: {type(data)}")

    if isinstance(data, list) and len(data) > 0:
        print(f"  Record type: {type(data[0])}")

        if isinstance(data[0], dict):
            print(f"  Fields: {list(data[0].keys())[:10]}")
            print(f"\nSample record:")
            print(json.dumps(data[0], indent=2)[:500])

            # Check for country fields
            print(f"\nCountry-related fields:")
            country_fields = [k for k in data[0].keys()
                            if 'country' in k.lower() or 'nation' in k.lower()]
            if country_fields:
                print(f"  Found: {country_fields}")

                # Sample country values
                for field in country_fields[:3]:
                    values = [r.get(field) for r in data[:100] if r.get(field)]
                    unique = list(set(values))[:10]
                    print(f"  {field} samples: {unique}")
            else:
                print("  No dedicated country fields found")

    return data

def test_search_patterns(data, patterns, field=None):
    """
    Test search patterns for false positives
    """
    print(f"\n{'='*60}")
    print(f"SEARCH PATTERN TESTING")
    print(f"{'='*60}")

    sample = data[:1000]  # Test on first 1000 records

    for pattern in patterns:
        print(f"\nPattern: '{pattern}'")

        if field:
            # Search in specific field
            matches = [r for r in sample if pattern in str(r.get(field, ''))]
            print(f"  Matches in {field}: {len(matches)}/{len(sample)}")
        else:
            # Search in full record (DANGEROUS - shows why it's bad)
            matches_full = [r for r in sample if pattern in str(r)]
            matches_lower = [r for r in sample if pattern.lower() in str(r).lower()]

            print(f"  Matches (exact) in full text: {len(matches_full)}/{len(sample)}")
            print(f"  Matches (case-insensitive): {len(matches_lower)}/{len(sample)}")

            if len(matches_full) > len(sample) * 0.1:  # >10% matches
                print(f"  WARNING: High match rate suggests false positives!")

                # Show why matches occurred
                if matches_full:
                    sample_match = str(matches_full[0])[:200]
                    import re
                    contexts = re.findall(f'.{{0,10}}{pattern}.{{0,10}}', sample_match)
                    print(f"  Match contexts: {contexts[:5]}")

def validate_results(data, results, check_field=None):
    """
    Validate analysis results for reasonableness
    """
    print(f"\n{'='*60}")
    print(f"RESULTS VALIDATION")
    print(f"{'='*60}")

    total = len(data)

    for country, count in results.items():
        percentage = (count / total) * 100 if total > 0 else 0

        print(f"\n{country}: {count} ({percentage:.2f}%)")

        # Warnings
        if percentage > 10:
            print(f"  WARNING: >10% seems high for country-specific data")
        if percentage > 25:
            print(f"  CRITICAL: >25% likely indicates false positives")

        # Manual verification
        if check_field and count > 0:
            samples = [r for r in data[:1000]
                      if r.get(check_field) == country][:3]
            print(f"  Samples for verification:")
            for s in samples:
                print(f"    - {s.get('name', s.get('title', 'Unknown'))[:60]}")

def main():
    """
    Example usage - adapt to your data
    """
    # Example: Analyzing CORDIS organizations
    filepath = "C:/Projects/OSINT - Foresight/data/raw/source=cordis/h2020/projects/organization.json"

    # Step 1: Understand structure
    data = validate_data_structure(filepath)

    # Step 2: Test search patterns
    # Bad patterns (too short, common in text)
    bad_patterns = ['AT', 'IE', 'PT', 'China']
    print("\nTesting BAD patterns (prone to false positives):")
    test_search_patterns(data, bad_patterns)

    # Good patterns (specific fields)
    if isinstance(data, list) and len(data) > 0:
        if 'country' in data[0]:
            print("\nTesting GOOD pattern (using country field):")
            countries = ['CN', 'IE', 'PT', 'AT', 'BG', 'GR', 'EL']
            results = {}
            for country in countries:
                count = len([r for r in data if r.get('country') == country])
                results[country] = count

            # Step 3: Validate results
            validate_results(data, results, 'country')

    print(f"\n{'='*60}")
    print("VALIDATION COMPLETE")
    print("Remember: Always prefer structured fields over text search!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
