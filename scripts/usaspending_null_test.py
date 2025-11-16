#!/usr/bin/env python3
"""
USAspending Null Test - Check for Missed Detections

Processes sample and looks for potential Chinese entities that our
detection logic might have missed.

Checks for:
1. Chinese-sounding entity names
2. Beijing/Shanghai/Shenzhen addresses
3. Common Chinese company suffixes (Ltd, Co, Corp)
4. Pinyin patterns
5. Known Chinese entity variations
"""

import gzip
import json
import re
from pathlib import Path
from typing import Dict, List
from process_usaspending_comprehensive import USAspendingComprehensiveProcessor

class NullTestAnalyzer:
    """Analyze non-detections for missed Chinese entities."""

    # Additional Chinese name patterns to check
    CHINESE_NAME_PATTERNS = [
        # Common Chinese company suffixes
        r'(beijing|shanghai|shenzhen|guangzhou|chongqing|tianjin|wuhan|chengdu)\s+(.*?)\s+(ltd|limited|co|corp|inc|company)',
        # Chinese pinyin patterns (common syllables)
        r'\b(zhang|wang|li|zhao|chen|yang|huang|zhou|wu|xu|sun|ma|zhu|guo|he|gao|lin|luo|zheng|liang|song|tang|han|deng|cao|peng|yuan|dong|pan|feng)\s+(.*?)\s+(technology|technologies|tech|electronics|manufacturing|industrial|group)',
        # Common Chinese state-owned enterprise patterns
        r'(china|chinese)\s+(national|state|provincial|municipal)',
        # Specific Chinese locations in addresses (require word boundaries to avoid "macaulay" matching "macau")
        r'\b(beijing|shanghai|shenzhen|guangzhou|hong\s+kong|macau)\b',
    ]

    # Indirect indicators
    INDIRECT_INDICATORS = {
        # China country code for phone numbers
        'phone_china': r'\+86[\s\-]?\d',
        # .cn domain for websites/emails
        'domain_cn': r'[\w\-]+\.cn\b',
        # Chinese postal codes (6 digits, usually 100000-899999)
        'postal_code_china': r'\b[1-8]\d{5}\b',
    }

    # Known Chinese company name variations we might have missed
    ADDITIONAL_ENTITIES = [
        'tsinghua', 'peking university', 'fudan', 'zhejiang university',
        'sinopharm', 'sinovac', 'bgi genomics',
        'ant group', 'ant financial',
        'meituan', 'didi', 'pinduoduo',
        'xiaohongshu', 'bilibili',
        'mindray', 'hisilicon',
        'changxin memory', 'yangtze memory',
        'state grid', 'china construction bank', 'icbc',
    ]

    def __init__(self):
        self.processor = USAspendingComprehensiveProcessor()
        self.potential_misses = []

    def analyze_record(self, fields: List[str], line_num: int) -> Dict:
        """
        Deep analysis of a non-detection record.

        Returns potential miss if Chinese indicators found.
        """

        if len(fields) < 206:
            return None

        # Extract key fields (based on schema analysis)
        recipient_name = fields[23] if len(fields) > 23 else ''
        recipient_parent = fields[27] if len(fields) > 27 else ''
        recipient_country = fields[29] if len(fields) > 29 else ''
        recipient_address = fields[36] if len(fields) > 36 else ''
        recipient_zip = fields[38] if len(fields) > 38 else ''
        pop_country = fields[39] if len(fields) > 39 else ''
        pop_city = fields[43] if len(fields) > 43 else ''
        pop_zip = fields[44] if len(fields) > 44 else ''
        sub_awardee_name = fields[59] if len(fields) > 59 else ''
        sub_awardee_parent = fields[63] if len(fields) > 63 else ''
        sub_awardee_country = fields[65] if len(fields) > 65 else ''
        sub_awardee_address = fields[69] if len(fields) > 69 else ''
        sub_awardee_zip = fields[71] if len(fields) > 71 else ''
        award_desc = fields[46] if len(fields) > 46 else ''
        subaward_desc = fields[82] if len(fields) > 82 else ''

        # Skip if already flagged as China by country
        if any('china' in str(c).lower() or 'hong kong' in str(c).lower()
               for c in [recipient_country, pop_country, sub_awardee_country]):
            return None

        indicators = []

        # Check for Chinese name patterns (include all contact/address fields)
        all_text = (f"{recipient_name} {recipient_parent} {sub_awardee_name} "
                   f"{sub_awardee_parent} {recipient_address} {recipient_zip} "
                   f"{pop_city} {pop_zip} {sub_awardee_address} {sub_awardee_zip}").lower()

        # Separate check for descriptions (don't check postal codes in descriptions - too many false positives)
        desc_text = f"{award_desc} {subaward_desc}".lower()

        for pattern in self.CHINESE_NAME_PATTERNS:
            if re.search(pattern, all_text, re.IGNORECASE):
                indicators.append(f"Name pattern match: {pattern[:50]}")

        # Check for additional entities
        for entity in self.ADDITIONAL_ENTITIES:
            if entity in all_text:
                indicators.append(f"Known Chinese entity: {entity}")

        # Check for Chinese city names in addresses (with word boundaries)
        chinese_cities = ['beijing', 'shanghai', 'shenzhen', 'guangzhou',
                         'hong kong', 'tianjin', 'chongqing']
        for city in chinese_cities:
            pattern = r'\b' + city + r'\b'
            if re.search(pattern, all_text, re.IGNORECASE):
                indicators.append(f"Chinese city in address: {city}")

        # Special case for Macau (avoid matching "Macaulay")
        if re.search(r'\bmacau\b', all_text, re.IGNORECASE):
            indicators.append(f"Chinese city in address: macau")

        # Check for indirect indicators (phone, domain only in names/addresses, NOT descriptions)
        for indicator_name, pattern in self.INDIRECT_INDICATORS.items():
            if indicator_name == 'postal_code_china':
                # Only check actual ZIP code fields, not general text (too many false positives)
                zip_fields = f"{recipient_zip} {pop_zip} {sub_awardee_zip}"
                matches = re.findall(pattern, zip_fields, re.IGNORECASE)
                if matches and zip_fields.strip():  # Only if zip fields have data
                    indicators.append(f"Chinese postal code in ZIP field: {matches[0]}")
            else:
                # Check phone/domain in all text (names + addresses + descriptions)
                full_text = f"{all_text} {desc_text}"
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                if matches:
                    if indicator_name == 'phone_china':
                        indicators.append(f"+86 phone number found: {matches[0][:20]}")
                    elif indicator_name == 'domain_cn':
                        indicators.append(f".cn domain found: {matches[0]}")

        # Check descriptions for partnership/collaboration mentions (already defined above)
        collab_keywords = [
            'sino-', 'sino american', 'china partnership', 'chinese partner',
            'collaboration with china', 'joint venture china'
        ]
        for keyword in collab_keywords:
            if keyword in desc_text:
                indicators.append(f"Partnership keyword: {keyword}")

        if indicators:
            return {
                'line_number': line_num,
                'recipient_name': recipient_name[:100],
                'recipient_parent': recipient_parent[:100],
                'recipient_country': recipient_country,
                'recipient_address': recipient_address[:100],
                'pop_country': pop_country,
                'pop_city': pop_city[:50],
                'sub_awardee_name': sub_awardee_name[:100],
                'sub_awardee_parent': sub_awardee_parent[:100],
                'sub_awardee_country': sub_awardee_country,
                'award_description': award_desc[:200],
                'indicators': indicators,
                'indicator_count': len(indicators)
            }

        return None

    def run_null_test(self, file_path: Path, max_records: int = 50000):
        """
        Run null test on sample.

        Process records that were NOT detected as Chinese and check
        if we missed any.
        """

        print(f"\n{'='*80}")
        print("NULL TEST - Checking for Missed Detections")
        print(f"{'='*80}\n")
        print(f"Processing {max_records:,} records from {file_path.name}")
        print("Looking for Chinese entities missed by detection logic...\n")

        detections_count = 0
        non_detections_checked = 0
        potential_misses = []

        with gzip.open(file_path, 'rt', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                if line_num > max_records:
                    break

                fields = line.strip().split('\t')
                if len(fields) < 206:
                    continue

                # Run normal detection
                try:
                    transaction = self.processor._extract_transaction(fields)
                    detection_results = self.processor._detect_china_entity(transaction, fields)

                    if detection_results:
                        detections_count += 1
                    else:
                        # This is a NON-detection - analyze for potential miss
                        non_detections_checked += 1
                        potential_miss = self.analyze_record(fields, line_num)
                        if potential_miss:
                            potential_misses.append(potential_miss)

                except Exception as e:
                    continue

                if line_num % 10000 == 0:
                    print(f"  Processed {line_num:,} records: "
                          f"{detections_count} detected, "
                          f"{len(potential_misses)} potential misses found")

        print(f"\n{'='*80}")
        print("NULL TEST RESULTS")
        print(f"{'='*80}")
        print(f"Records processed: {max_records:,}")
        print(f"Detections found: {detections_count} ({detections_count/max_records*100:.2f}%)")
        print(f"Non-detections checked: {non_detections_checked:,}")
        print(f"Potential misses identified: {len(potential_misses)}")
        print(f"{'='*80}\n")

        return potential_misses

    def save_results(self, potential_misses: List[Dict]):
        """Save null test results."""

        output_dir = Path("data/processed/usaspending_manual_review")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON
        output_file = output_dir / "null_test_potential_misses.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_potential_misses': len(potential_misses),
                'potential_misses': potential_misses
            }, f, indent=2)

        print(f"Saved results: {output_file}")

        # Create human-readable summary
        summary_file = output_dir / "NULL_TEST_SUMMARY.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("NULL TEST - Potential Missed Detections\n")
            f.write("="*80 + "\n\n")
            f.write(f"Total potential misses: {len(potential_misses)}\n\n")

            if not potential_misses:
                f.write("✅ NO MISSED DETECTIONS FOUND\n\n")
                f.write("All Chinese entities appear to be properly detected.\n")
            else:
                f.write("⚠️ POTENTIAL MISSES REQUIRING MANUAL REVIEW:\n\n")

                # Sort by indicator count (most indicators first)
                sorted_misses = sorted(potential_misses,
                                     key=lambda x: x['indicator_count'],
                                     reverse=True)

                for i, miss in enumerate(sorted_misses[:20], 1):
                    f.write(f"{i}. LINE {miss['line_number']}\n")
                    f.write(f"   Recipient: {miss['recipient_name']}\n")
                    if miss['recipient_parent']:
                        f.write(f"   Parent: {miss['recipient_parent']}\n")
                    f.write(f"   Country: {miss['recipient_country']}\n")
                    if miss['sub_awardee_name']:
                        f.write(f"   Sub-awardee: {miss['sub_awardee_name']}\n")
                    if miss['pop_city']:
                        f.write(f"   Location: {miss['pop_city']}\n")
                    f.write(f"\n   INDICATORS ({miss['indicator_count']}):\n")
                    for indicator in miss['indicators']:
                        f.write(f"     - {indicator}\n")
                    if miss['award_description']:
                        f.write(f"\n   Description: {miss['award_description']}\n")
                    f.write("\n" + "-"*80 + "\n\n")

        print(f"Created summary: {summary_file}")

def main():
    """Run null test."""

    test_file = Path("F:/OSINT_DATA/USAspending/extracted_data/5876.dat.gz")

    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return

    analyzer = NullTestAnalyzer()
    potential_misses = analyzer.run_null_test(test_file, max_records=50000)
    analyzer.save_results(potential_misses)

    if potential_misses:
        print(f"\nWARNING: Found {len(potential_misses)} potential missed detections")
        print("Review NULL_TEST_SUMMARY.txt for details")
    else:
        print("\nSUCCESS: No missed detections found - detection logic appears complete")

if __name__ == '__main__':
    main()
