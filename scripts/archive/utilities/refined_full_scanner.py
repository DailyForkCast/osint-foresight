#!/usr/bin/env python3
"""
Refined scanner that excludes U.S. location names but INCLUDES Chinese activity in the U.S.
"""

import re
from pathlib import Path
from datetime import datetime
import json
import time

def scan_with_smart_filtering(file_path, file_name):
    """
    Process EVERY line but smartly filter:
    - EXCLUDE: U.S. locations named "China Lake", "China Spring", etc.
    - INCLUDE: Chinese companies operating in U.S.
    - INCLUDE: Chinese government activities in U.S.
    - INCLUDE: Chinese investments/ownership in U.S.
    """

    print(f"\n{'='*80}")
    print(f"SMART CHINA SCAN: {file_name}")
    print(f"File size: {file_path.stat().st_size / 1e9:.2f} GB")
    print(f"Start: {datetime.now()}")
    print(f"{'='*80}")

    # FALSE POSITIVES - U.S. geographic locations to exclude
    us_false_positives = [
        r'china\s+lake',           # China Lake, California
        r'china\s+spring',          # China Spring, Texas
        r'china\s+grove',           # China Grove, North Carolina
        r'china\s+beach',           # Various U.S. locations
        r'china\s+creek',           # Various U.S. locations
        r'china\s+point',           # Maryland
        r'china\s+camp',            # California
        r'naws\s+china\s+lake',     # Naval Air Weapons Station China Lake
        r'nawc\s+china\s+lake',     # Naval Air Warfare Center China Lake
        r'naval.{0,20}china\s+lake' # Naval [anything] China Lake
    ]

    # TRUE POSITIVES - Chinese entities/activities to INCLUDE
    chinese_entities_in_us = [
        # Chinese companies with U.S. operations
        r'\bhuawei.{0,20}(usa|united states|america)',
        r'\bzte.{0,20}(usa|united states|america)',
        r'\blenovo.{0,20}(usa|united states|america)',
        r'\btiktok',  # Chinese company operating in U.S.
        r'\bbytedance',  # TikTok parent
        r'\bwechat',  # Chinese app used in U.S.

        # Chinese government presence in U.S.
        r'chinese\s+embassy',
        r'chinese\s+consulate',
        r'embassy.{0,20}china',
        r'consulate.{0,20}china',
        r'chinese\s+government.{0,30}(usa|united states|america)',

        # Chinese ownership/investment patterns
        r'owned.{0,20}china',
        r'owned.{0,20}chinese',
        r'chinese.{0,20}owned',
        r'china.{0,20}owned',
        r'chinese.{0,20}investor',
        r'china.{0,20}investment',
        r'subsidiary.{0,20}china',
        r'china.{0,20}subsidiary',

        # Trade/Import/Export with China
        r'import.{0,20}china',
        r'export.{0,20}china',
        r'china.{0,20}trade',
        r'made\s+in\s+china',
        r'manufactured.{0,20}china',
        r'china.{0,20}supplier',

        # Research/Collaboration
        r'china.{0,20}research',
        r'chinese.{0,20}researcher',
        r'collaboration.{0,20}china',
        r'china.{0,20}collaboration',
        r'chinese.{0,20}university',
        r'china.{0,20}university'
    ]

    # Specific Chinese companies (regardless of location)
    chinese_companies = [
        r'\bhuawei\b', r'\bzte\b', r'\bhikvision\b', r'\bdahua\b',
        r'\bdji\b', r'\blenovo\b', r'\balibaba\b', r'\btencent\b',
        r'\bbaidu\b', r'\bxiaomi\b', r'\bbyd\b', r'\bhaier\b',
        r'\btcl\b', r'\boppo\b', r'\bvivo\b', r'\boneplus\b',
        r'\bchinaunicom\b', r'\bchina\s+telecom\b', r'\bchina\s+mobile\b',
        r'\bsinopec\b', r'\bpetroChina\b', r'\bcnooc\b',
        r'\bbank\s+of\s+china\b', r'\bicbc\b', r'\bccb\b',
        r'\bsmic\b', r'\bcomac\b', r'\bcrrc\b', r'\bcosco\b'
    ]

    # MCF/Defense entities
    mcf_entities = [
        r'\bnorinco\b', r'\bavic\b', r'\bcasic\b', r'\bcasc\b',
        r'\bcetc\b', r'\bcssc\b', r'\bcsic\b', r'\bnuctech\b',
        r'\bhytera\b', r'\binspur\b', r'\bsugon\b', r'\biflytek\b',
        r'\bsensetime\b', r'\bmegvii\b', r'\byitu\b', r'\bcloudwalk\b'
    ]

    # Chinese locations/references
    china_locations = [
        r'\bbeijing\b', r'\bshanghai\b', r'\bshenzhen\b', r'\bguangzhou\b',
        r'\btianjin\b', r'\bwuhan\b', r'\bhong\s+kong\b', r'\bmacau\b',
        r'\bchengdu\b', r'\bhangzhou\b', r'\bnanjing\b', r'\bxian\b',
        r'\bpeople\'?s\s+republic\s+of\s+china\b',
        r'\bprc\b(?!\s+lake)',  # PRC but not PRC Lake
        r'\bchinese\s+government\b',
        r'\bchinese\s+military\b',
        r'\bchinese\s+communist\s+party\b',
        r'\bccp\b'  # Chinese Communist Party
    ]

    # General China pattern (excluding false positives)
    general_china = r'\bchina\b(?!\s+(lake|spring|grove|beach|creek|point|camp))'

    # Compile patterns
    false_positive_compiled = [re.compile(p, re.IGNORECASE) for p in us_false_positives]
    chinese_in_us_compiled = [re.compile(p, re.IGNORECASE) for p in chinese_entities_in_us]
    company_compiled = [re.compile(p, re.IGNORECASE) for p in chinese_companies]
    mcf_compiled = [re.compile(p, re.IGNORECASE) for p in mcf_entities]
    location_compiled = [re.compile(p, re.IGNORECASE) for p in china_locations]
    general_compiled = re.compile(general_china, re.IGNORECASE)

    # Counters
    total_lines = 0
    china_references = 0
    false_positives_excluded = 0

    # Detailed tracking
    chinese_activity_in_us = 0
    company_mentions = {}
    mcf_mentions = {}
    location_mentions = {}
    activity_types = {
        'embassy_consulate': 0,
        'trade_import_export': 0,
        'ownership_investment': 0,
        'research_collaboration': 0,
        'chinese_companies': 0,
        'mcf_entities': 0,
        'general_china': 0
    }

    sample_records = []

    # Progress tracking
    start_time = time.time()
    last_report = time.time()

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            total_lines += 1

            # Progress report
            if total_lines % 1000000 == 0 or (time.time() - last_report) > 30:
                elapsed = time.time() - start_time
                rate = total_lines / elapsed if elapsed > 0 else 0
                print(f"Progress: {total_lines:,} lines | "
                      f"China: {china_references:,} | "
                      f"China in US: {chinese_activity_in_us:,} | "
                      f"Excluded: {false_positives_excluded:,} | "
                      f"Rate: {rate:.0f} lines/sec")
                last_report = time.time()

            line_lower = line.lower()

            # FIRST: Check for false positives
            is_false_positive = False
            for pattern in false_positive_compiled:
                if pattern.search(line_lower):
                    is_false_positive = True
                    false_positives_excluded += 1
                    break

            if is_false_positive:
                continue  # Skip U.S. geographic locations

            # Check for Chinese activities IN the U.S.
            china_in_us_found = False
            for pattern in chinese_in_us_compiled:
                if pattern.search(line_lower):
                    china_in_us_found = True
                    chinese_activity_in_us += 1
                    china_references += 1

                    # Categorize the activity
                    if 'embassy' in line_lower or 'consulate' in line_lower:
                        activity_types['embassy_consulate'] += 1
                    elif 'import' in line_lower or 'export' in line_lower or 'trade' in line_lower:
                        activity_types['trade_import_export'] += 1
                    elif 'owned' in line_lower or 'investment' in line_lower or 'investor' in line_lower:
                        activity_types['ownership_investment'] += 1
                    elif 'research' in line_lower or 'collaboration' in line_lower:
                        activity_types['research_collaboration'] += 1

                    if len(sample_records) < 10000:
                        sample_records.append({
                            'line': line_num,
                            'type': 'China_in_US',
                            'pattern': pattern.pattern[:50],
                            'text': line[:300]
                        })
                    break

            # Check for MCF entities (high priority)
            mcf_found = False
            for pattern in mcf_compiled:
                if pattern.search(line_lower):
                    mcf_found = True
                    entity = pattern.pattern.strip('\\b')
                    mcf_mentions[entity] = mcf_mentions.get(entity, 0) + 1
                    china_references += 1
                    activity_types['mcf_entities'] += 1

                    if len(sample_records) < 10000:
                        sample_records.append({
                            'line': line_num,
                            'type': 'MCF_Entity',
                            'entity': entity,
                            'text': line[:300]
                        })
                    break

            # Check for Chinese companies
            company_found = False
            for pattern in company_compiled:
                if pattern.search(line_lower):
                    company_found = True
                    company = pattern.pattern.strip('\\b').replace('\\s+', ' ')
                    company_mentions[company] = company_mentions.get(company, 0) + 1
                    china_references += 1
                    activity_types['chinese_companies'] += 1

                    if len(sample_records) < 10000:
                        sample_records.append({
                            'line': line_num,
                            'type': 'Chinese_Company',
                            'entity': company,
                            'text': line[:300]
                        })
                    break

            # Check for Chinese locations
            location_found = False
            for pattern in location_compiled:
                if pattern.search(line_lower):
                    location_found = True
                    china_references += 1

                    # Track specific locations
                    for loc in ['beijing', 'shanghai', 'shenzhen', 'guangzhou', 'hong kong']:
                        if loc in line_lower:
                            location_mentions[loc] = location_mentions.get(loc, 0) + 1
                            break

                    if len(sample_records) < 10000:
                        sample_records.append({
                            'line': line_num,
                            'type': 'China_Location',
                            'pattern': pattern.pattern[:30],
                            'text': line[:300]
                        })
                    break

            # General China reference (if nothing else matched)
            if not any([china_in_us_found, mcf_found, company_found, location_found]):
                if general_compiled.search(line_lower):
                    china_references += 1
                    activity_types['general_china'] += 1

                    if len(sample_records) < 10000:
                        sample_records.append({
                            'line': line_num,
                            'type': 'General_China',
                            'text': line[:300]
                        })

    # Final statistics
    elapsed_total = time.time() - start_time

    results = {
        'file': file_name,
        'total_lines': total_lines,
        'china_references': china_references,
        'false_positives_excluded': false_positives_excluded,
        'chinese_activity_in_us': chinese_activity_in_us,
        'percentage': (china_references / total_lines * 100) if total_lines > 0 else 0,
        'activity_types': activity_types,
        'mcf_entities': dict(sorted(mcf_mentions.items(), key=lambda x: x[1], reverse=True)),
        'companies': dict(sorted(company_mentions.items(), key=lambda x: x[1], reverse=True)),
        'locations': dict(sorted(location_mentions.items(), key=lambda x: x[1], reverse=True)),
        'processing_time_seconds': elapsed_total,
        'sample_records': sample_records[:100]
    }

    print(f"\n{'='*80}")
    print(f"COMPLETED: {file_name}")
    print(f"Total lines: {total_lines:,}")
    print(f"China references: {china_references:,} ({results['percentage']:.4f}%)")
    print(f"Chinese activity IN U.S.: {chinese_activity_in_us:,}")
    print(f"False positives excluded: {false_positives_excluded:,}")
    print(f"Time: {elapsed_total/60:.1f} minutes")
    print(f"{'='*80}")

    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        base = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/")
        file_path = base / file_name

        if file_path.exists():
            results = scan_with_smart_filtering(file_path, file_name)
            output_name = f'smart_scan_{file_name.replace(".dat", "")}.json'
            with open(output_name, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Results saved to: {output_name}")
        else:
            print(f"File not found: {file_name}")
    else:
        print("Usage: python refined_full_scanner.py <filename>")
