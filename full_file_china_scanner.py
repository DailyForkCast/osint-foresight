#!/usr/bin/env python3
"""
COMPLETE China scan - processes EVERY line in EVERY file
No sampling - full analysis as requested
"""

import re
from pathlib import Path
from datetime import datetime
import json
import time

def scan_entire_file(file_path, file_name):
    """Process EVERY line in the file"""

    print(f"\n{'='*80}")
    print(f"SCANNING ENTIRE FILE: {file_name}")
    print(f"File size: {file_path.stat().st_size / 1e9:.2f} GB")
    print(f"Start: {datetime.now()}")
    print(f"{'='*80}")

    # Exclusion patterns for U.S. locations
    us_locations = [
        r'china\s+lake',
        r'china\s+spring',
        r'china\s+grove',
        r'china\s+beach',
        r'china\s+creek',
        r'china\s+point',
        r'china\s+camp',
        r'naws\s+china',
        r'nawc\s+china'
    ]

    # Real China patterns
    china_patterns = [
        r'\bpeople\'?s republic of china\b',
        r'\bprc\b(?!\s+lake)',
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
        r'\bchina\b(?!\s+(lake|spring|grove|beach|creek|point|camp))'
    ]

    # Chinese companies
    chinese_companies = [
        r'\bhuawei\b', r'\bzte\b', r'\bhikvision\b', r'\bdahua\b',
        r'\bdji\b', r'\blenovo\b', r'\balibaba\b', r'\btencent\b',
        r'\bbaidu\b', r'\bxiaomi\b', r'\bbyd\b', r'\bhaier\b',
        r'\btcl\b', r'\boppo\b', r'\bvivo\b', r'\bchinaunicom\b',
        r'\bchina telecom\b', r'\bchina mobile\b', r'\bsinopec\b',
        r'\bpetroChina\b', r'\bbank of china\b', r'\bicbc\b',
        r'\bsmic\b', r'\bcomac\b', r'\bcrrc\b'
    ]

    # MCF entities
    mcf_entities = [
        r'\bnorinco\b', r'\bavic\b', r'\bcasic\b', r'\bcasc\b',
        r'\bcetc\b', r'\bcssc\b', r'\bcsic\b', r'\bnuctech\b',
        r'\bhytera\b', r'\binspur\b', r'\bsugon\b', r'\biflytek\b',
        r'\bsensetime\b', r'\bmegvii\b', r'\byitu\b'
    ]

    # Compile all patterns
    us_exclusions = [re.compile(p, re.IGNORECASE) for p in us_locations]
    china_compiled = [re.compile(p, re.IGNORECASE) for p in china_patterns]
    company_compiled = [re.compile(p, re.IGNORECASE) for p in chinese_companies]
    mcf_compiled = [re.compile(p, re.IGNORECASE) for p in mcf_entities]

    # Counters
    total_lines = 0
    china_references = 0
    us_locations_found = 0
    company_mentions = {}
    mcf_mentions = {}
    location_mentions = {}
    china_records = []

    # Progress tracking
    start_time = time.time()
    last_report = time.time()

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            total_lines += 1

            # Progress report every 1M lines or 30 seconds
            if total_lines % 1000000 == 0 or (time.time() - last_report) > 30:
                elapsed = time.time() - start_time
                rate = total_lines / elapsed if elapsed > 0 else 0
                eta = ((98463609 - total_lines) / rate / 60) if rate > 0 else 0

                print(f"Progress: {total_lines:,} lines | "
                      f"China found: {china_references:,} | "
                      f"Rate: {rate:.0f} lines/sec | "
                      f"ETA: {eta:.1f} min")
                last_report = time.time()

            line_lower = line.lower()

            # Check for U.S. location exclusions
            is_us_location = False
            for pattern in us_exclusions:
                if pattern.search(line_lower):
                    is_us_location = True
                    us_locations_found += 1
                    break

            if is_us_location:
                continue

            # Check for MCF entities (highest priority)
            mcf_found = False
            for pattern in mcf_compiled:
                if pattern.search(line_lower):
                    mcf_found = True
                    entity = pattern.pattern.strip('\\b')
                    mcf_mentions[entity] = mcf_mentions.get(entity, 0) + 1
                    china_references += 1

                    if len(china_records) < 10000:  # Save first 10k for analysis
                        china_records.append({
                            'line': line_num,
                            'type': 'MCF',
                            'entity': entity,
                            'text': line[:300]
                        })
                    break

            if mcf_found:
                continue

            # Check for Chinese companies
            company_found = False
            for pattern in company_compiled:
                if pattern.search(line_lower):
                    company_found = True
                    company = pattern.pattern.strip('\\b')
                    company_mentions[company] = company_mentions.get(company, 0) + 1
                    china_references += 1

                    if len(china_records) < 10000:
                        china_records.append({
                            'line': line_num,
                            'type': 'Company',
                            'entity': company,
                            'text': line[:300]
                        })
                    break

            if company_found:
                continue

            # Check for China locations/references
            for pattern in china_compiled:
                if pattern.search(line_lower):
                    china_references += 1

                    # Track specific locations
                    if 'beijing' in line_lower:
                        location_mentions['beijing'] = location_mentions.get('beijing', 0) + 1
                    elif 'shanghai' in line_lower:
                        location_mentions['shanghai'] = location_mentions.get('shanghai', 0) + 1
                    elif 'shenzhen' in line_lower:
                        location_mentions['shenzhen'] = location_mentions.get('shenzhen', 0) + 1

                    if len(china_records) < 10000:
                        china_records.append({
                            'line': line_num,
                            'type': 'Location/Other',
                            'pattern': pattern.pattern[:30],
                            'text': line[:300]
                        })
                    break

    # Final statistics
    elapsed_total = time.time() - start_time

    results = {
        'file': file_name,
        'total_lines': total_lines,
        'china_references': china_references,
        'us_locations_excluded': us_locations_found,
        'percentage': (china_references / total_lines * 100) if total_lines > 0 else 0,
        'mcf_entities': dict(sorted(mcf_mentions.items(), key=lambda x: x[1], reverse=True)),
        'companies': dict(sorted(company_mentions.items(), key=lambda x: x[1], reverse=True)),
        'locations': dict(sorted(location_mentions.items(), key=lambda x: x[1], reverse=True)),
        'processing_time_seconds': elapsed_total,
        'sample_records': china_records[:100]  # First 100 for review
    }

    print(f"\n{'='*80}")
    print(f"COMPLETED: {file_name}")
    print(f"Total lines processed: {total_lines:,}")
    print(f"China references found: {china_references:,}")
    print(f"Percentage: {results['percentage']:.4f}%")
    print(f"Time: {elapsed_total/60:.1f} minutes")
    print(f"{'='*80}")

    return results

def main():
    print("="*80)
    print("COMPLETE CHINA ANALYSIS - FULL FILE PROCESSING")
    print(f"Started: {datetime.now()}")
    print("="*80)

    base_path = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/")

    # Process ALL files
    files_to_process = [
        ("5848.dat", 222.45),  # Highest priority - most China refs
        ("5801.dat", 134.85),
        ("5836.dat", 124.72),
        ("5847.dat", 126.50),
        ("5862.dat", 52.05)
    ]

    all_results = {}

    for file_name, size_gb in files_to_process:
        file_path = base_path / file_name

        if file_path.exists():
            results = scan_entire_file(file_path, file_name)
            all_results[file_name] = results

            # Save intermediate results
            with open(f'full_scan_{file_name}.json', 'w') as f:
                json.dump(results, f, indent=2, default=str)
        else:
            print(f"WARNING: {file_name} not found!")

    # Final summary
    total_china = sum(r['china_references'] for r in all_results.values())
    total_lines = sum(r['total_lines'] for r in all_results.values())

    print("\n" + "="*80)
    print("FINAL SUMMARY - ALL FILES")
    print("="*80)
    print(f"Total lines processed: {total_lines:,}")
    print(f"Total China references: {total_china:,}")
    print(f"Overall percentage: {(total_china/total_lines*100):.4f}%")

    # Save complete results
    with open('complete_china_analysis.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\nCompleted: {datetime.now()}")
    print("Results saved to: complete_china_analysis.json")

if __name__ == "__main__":
    main()
