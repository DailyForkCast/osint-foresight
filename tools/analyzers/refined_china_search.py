#!/usr/bin/env python3
"""
Refined search for ACTUAL China (country) references
Excludes U.S. locations like China Lake, China Spring, etc.
"""

import re
from pathlib import Path
from datetime import datetime
import json

def refined_china_search():
    print("=" * 80)
    print("REFINED CHINA (COUNTRY) SEARCH - EXCLUDING U.S. LOCATIONS")
    print(f"Start: {datetime.now()}")
    print("=" * 80)

    # Target the main file with high hit rate
    data_file = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5848.dat")

    # Exclusion patterns for U.S. locations
    us_location_exclusions = [
        r'china\s+lake',  # China Lake, California
        r'china\s+spring', # China Spring, Texas
        r'china\s+grove',  # China Grove, North Carolina
        r'china\s+beach',  # Various U.S. locations
        r'china\s+creek',  # Various U.S. locations
        r'china\s+point',  # Maryland
        r'china\s+camp',   # California
        r'naws\s+china',   # Naval Air Weapons Station China Lake
        r'nawc\s+china'    # Naval Air Warfare Center China Lake
    ]

    # Positive patterns for actual China
    china_positive_patterns = [
        r'\bpeople\'?s republic of china\b',
        r'\bprc\b(?!\s+lake)',  # PRC but not followed by Lake
        r'\bbeijing\b',
        r'\bshanghai\b',
        r'\bshenzhen\b',
        r'\bguangzhou\b',
        r'\btianjin\b',
        r'\bwuhan\b',
        r'\bhong kong\b',
        r'\bmacau\b',
        r'\bxinjiang\b',
        r'\btibet\b',
        r'\bchinese government\b',
        r'\bchinese military\b',
        r'\bchinese communist\b',
        r'\bembassy beijing\b',
        r'\bconsulate shanghai\b',
        r'\bmade in china\b',
        r'\bexport.*china\b',
        r'\bimport.*china\b',
        r'\bchina\b(?!\s+(lake|spring|grove|beach|creek|point|camp))'  # China NOT followed by US location names
    ]

    # Known Chinese companies
    chinese_companies = [
        r'\bhuawei\b',
        r'\bzte\b',
        r'\bhikvision\b',
        r'\bdahua\b',
        r'\bdji\b',
        r'\blenovo\b',
        r'\balibaba\b',
        r'\btencent\b',
        r'\bbaidu\b',
        r'\bxiaomi\b',
        r'\bbyd\b',
        r'\bhaier\b',
        r'\btcl\b',
        r'\boppo\b',
        r'\bvivo\b',
        r'\bchinaunicom\b',
        r'\bchina telecom\b',
        r'\bchina mobile\b',
        r'\bsinopec\b',
        r'\bpetroChina\b',
        r'\bbank of china\b',
        r'\bicbc\b',  # Industrial and Commercial Bank of China
        r'\bsmic\b',  # Semiconductor Manufacturing International
        r'\bcomac\b',  # Commercial Aircraft Corporation of China
        r'\bcrrc\b'   # China Railway Rolling Stock
    ]

    # Compile patterns
    exclusion_compiled = [re.compile(p, re.IGNORECASE) for p in us_location_exclusions]
    positive_compiled = [re.compile(p, re.IGNORECASE) for p in china_positive_patterns]
    company_compiled = [re.compile(p, re.IGNORECASE) for p in chinese_companies]

    print(f"\nSearching {data_file.name} (222 GB)...")
    print("Excluding: China Lake, China Spring, and other U.S. locations")
    print("Including: Beijing, Shanghai, Chinese companies, etc.")
    print("-" * 80)

    # Results storage
    actual_china_records = []
    company_counts = {}
    location_counts = {}
    excluded_count = 0
    total_actual_china = 0

    lines_checked = 0
    max_lines = 2000000  # Check first 2M lines for speed

    with open(data_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            lines_checked += 1

            if lines_checked % 200000 == 0:
                print(f"  Checked {lines_checked:,} lines... Found {total_actual_china} actual China references")

            line_lower = line.lower()

            # First check for exclusions
            is_us_location = False
            for exclusion in exclusion_compiled:
                if exclusion.search(line_lower):
                    is_us_location = True
                    excluded_count += 1
                    break

            if is_us_location:
                continue  # Skip U.S. locations

            # Check for positive China patterns
            china_match = False
            matched_pattern = None

            # Check company names first (most specific)
            for company_pattern in company_compiled:
                if company_pattern.search(line_lower):
                    china_match = True
                    matched_pattern = company_pattern.pattern
                    company_name = matched_pattern.strip('\\b')
                    company_counts[company_name] = company_counts.get(company_name, 0) + 1
                    break

            # If no company match, check location patterns
            if not china_match:
                for positive_pattern in positive_compiled:
                    if positive_pattern.search(line_lower):
                        china_match = True
                        matched_pattern = positive_pattern.pattern
                        # Track location mentions
                        if 'beijing' in matched_pattern:
                            location_counts['beijing'] = location_counts.get('beijing', 0) + 1
                        elif 'shanghai' in matched_pattern:
                            location_counts['shanghai'] = location_counts.get('shanghai', 0) + 1
                        break

            if china_match:
                total_actual_china += 1

                # Save sample records
                if len(actual_china_records) < 100:
                    fields = line.split('\t')
                    actual_china_records.append({
                        'line_number': line_num,
                        'matched_pattern': matched_pattern,
                        'sample_text': line[:500],
                        'field_count': len(fields)
                    })

            if lines_checked >= max_lines:
                break

    # Results summary
    print("\n" + "=" * 80)
    print("REFINED SEARCH RESULTS")
    print("=" * 80)

    print(f"\nLines analyzed: {lines_checked:,}")
    print(f"U.S. locations excluded: {excluded_count:,}")
    print(f"Actual China references found: {total_actual_china:,}")

    if total_actual_china > 0:
        percentage = (total_actual_china / lines_checked) * 100
        print(f"Actual China percentage: {percentage:.4f}%")

        # Extrapolate to full file
        extrapolated = int(total_actual_china * (98463609 / lines_checked))
        print(f"\nESTIMATED actual China references in full file: {extrapolated:,}")

    # Company breakdown
    if company_counts:
        print("\nCHINESE COMPANIES FOUND:")
        for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {company}: {count:,}")

    # Location breakdown
    if location_counts:
        print("\nCHINESE LOCATIONS FOUND:")
        for location, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {location}: {count:,}")

    # Sample records
    if actual_china_records:
        print(f"\nSAMPLE ACTUAL CHINA RECORDS (first 5):")
        print("-" * 40)
        for i, record in enumerate(actual_china_records[:5], 1):
            print(f"\n[{i}] Line {record['line_number']}:")
            print(f"    Pattern: {record['matched_pattern']}")
            print(f"    Text: {record['sample_text'][:200]}...")

    # Save results
    output = {
        'summary': {
            'lines_checked': lines_checked,
            'excluded_us_locations': excluded_count,
            'actual_china_found': total_actual_china,
            'percentage': (total_actual_china / lines_checked * 100) if lines_checked > 0 else 0,
            'extrapolated_total': int(total_actual_china * (98463609 / lines_checked)) if lines_checked > 0 else 0
        },
        'companies': company_counts,
        'locations': location_counts,
        'samples': actual_china_records[:20]  # Save first 20 samples
    }

    output_file = Path("refined_china_search_results.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    print(f"\nEnd: {datetime.now()}")

if __name__ == "__main__":
    refined_china_search()
