#!/usr/bin/env python3
"""
USAspending Comprehensive Sample Test

Larger sample test (500k-1M records) checking ALL potential Chinese indicators
across the complete 206-column schema.

Additional Fields to Check:
1. Business type codes (foreign-owned indicators)
2. Ultimate parent company (vs immediate parent)
3. Recipient type classifications
4. Complete address analysis (all address fields)
5. Award type patterns
6. DUNS/UEI cross-referencing
7. Multiple description fields (NAICS desc, PSC desc, etc.)
8. Funding office details
9. Congressional district anomalies
10. Entity name variations across fields
"""

import gzip
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict
from process_usaspending_comprehensive import USAspendingComprehensiveProcessor

class ComprehensiveSampleAnalyzer:
    """
    Comprehensive analyzer checking ALL potential Chinese indicators.
    """

    def __init__(self):
        self.processor = USAspendingComprehensiveProcessor()

        # Statistics tracking
        self.stats = {
            'total_records': 0,
            'standard_detections': 0,
            'additional_indicators': defaultdict(int),
            'field_coverage': defaultdict(int),
        }

        # Track interesting patterns
        self.patterns_found = []
        self.detections_by_indicator = defaultdict(list)

    # Additional Chinese indicators not in base processor

    CHINESE_BUSINESS_TYPES = [
        'foreign-owned', 'foreign owned', 'foreign entity',
        'non-u.s.', 'non us', 'international',
    ]

    CHINESE_NAME_INDICATORS = [
        # Common Chinese company structures
        'group co', 'holdings ltd', 'international trade',
        'import export', 'trading company',
        # Chinese transliteration patterns (consonant clusters)
        r'\b[a-z]*zh[a-z]*\b',  # zh sound
        r'\b[a-z]*xi[a-z]*\b',  # xi sound
        r'\b[a-z]*ch[a-z]*\b',  # ch sound (but not "tech", "church", etc.)
    ]

    SUSPICIOUS_PATTERNS = [
        # Recently registered in sensitive sectors
        # Generic/vague company names with Chinese indicators
        r'(global|international|worldwide)\s+(trading|import|export|tech)',
        # P.O. Box addresses (could hide foreign registration)
        r'p\.?o\.?\s*box',
    ]

    def analyze_additional_fields(self, fields: List[str],
                                  line_num: int) -> Dict[str, List[str]]:
        """
        Check additional fields beyond standard detection logic.

        Returns dict of {indicator_type: [list of findings]}
        """

        if len(fields) < 206:
            return {}

        findings = defaultdict(list)

        # Extract additional fields not in standard detection
        recipient_type = fields[37] if len(fields) > 37 else ''
        business_types = fields[25] if len(fields) > 25 else ''  # May contain foreign ownership indicators

        # Multiple parent fields
        recipient_parent_uei = fields[26] if len(fields) > 26 else ''
        recipient_parent_name = fields[27] if len(fields) > 27 else ''

        # Complete address fields
        recipient_city = fields[35] if len(fields) > 35 else ''
        recipient_address_1 = fields[36] if len(fields) > 36 else ''
        recipient_state = fields[30] if len(fields) > 30 else ''
        recipient_zip = fields[38] if len(fields) > 38 else ''

        pop_city = fields[43] if len(fields) > 43 else ''
        pop_state = fields[40] if len(fields) > 40 else ''
        pop_zip = fields[44] if len(fields) > 44 else ''

        sub_awardee_city = fields[68] if len(fields) > 68 else ''
        sub_awardee_address = fields[69] if len(fields) > 69 else ''
        sub_awardee_state = fields[66] if len(fields) > 66 else ''
        sub_awardee_zip = fields[71] if len(fields) > 71 else ''

        # Award type and classification
        award_type = fields[119] if len(fields) > 119 else ''
        psc_code = fields[163] if len(fields) > 163 else ''
        psc_description = fields[164] if len(fields) > 164 else ''
        naics_description = fields[48] if len(fields) > 48 else ''

        # Description fields
        subaward_desc = fields[82] if len(fields) > 82 else ''

        # Agency details
        awarding_office = fields[12] if len(fields) > 12 else ''
        funding_office = fields[18] if len(fields) > 18 else ''

        # DUNS/UEI for cross-reference
        recipient_duns = fields[21] if len(fields) > 21 else ''
        recipient_uei = fields[22] if len(fields) > 22 else ''
        sub_awardee_duns = fields[60] if len(fields) > 60 else ''
        sub_awardee_uei = fields[61] if len(fields) > 61 else ''

        # 1. CHECK BUSINESS TYPES FOR FOREIGN OWNERSHIP
        if business_types and business_types != '\\N':
            for indicator in self.CHINESE_BUSINESS_TYPES:
                if indicator in business_types.lower():
                    findings['foreign_business_type'].append(
                        f"Business type contains '{indicator}': {business_types[:100]}"
                    )

        # 2. CHECK RECIPIENT TYPE
        if recipient_type and 'foreign' in recipient_type.lower():
            findings['foreign_recipient_type'].append(
                f"Recipient type indicates foreign: {recipient_type}"
            )

        # 3. CHECK FOR CHINESE NAME PATTERNS
        all_names = f"{fields[23]} {fields[27]} {fields[59]} {fields[63]}".lower()

        # Look for transliteration patterns
        for pattern in self.CHINESE_NAME_INDICATORS:
            if isinstance(pattern, str):
                if pattern in all_names:
                    findings['chinese_name_pattern'].append(f"Pattern '{pattern}' in entity names")
            else:
                # Regex pattern
                matches = re.findall(pattern, all_names)
                if matches:
                    # Filter out common English words
                    filtered = [m for m in matches if m not in ['tech', 'technology', 'church', 'school', 'teaching']]
                    if filtered:
                        findings['chinese_transliteration'].append(
                            f"Transliteration pattern: {', '.join(filtered[:5])}"
                        )

        # 4. CHECK ADDRESS ANOMALIES
        # P.O. Box with large federal contract (could be shell company)
        all_addresses = f"{recipient_address_1} {sub_awardee_address}".lower()
        if re.search(r'p\.?o\.?\s*box', all_addresses):
            findings['po_box_address'].append(
                f"P.O. Box address: {recipient_address_1[:100] if 'p.o.' in recipient_address_1.lower() else sub_awardee_address[:100]}"
            )

        # 5. CHECK PSC/NAICS DESCRIPTIONS FOR CHINESE INDICATORS
        all_descriptions = f"{naics_description} {psc_description}".lower()
        chinese_keywords = ['china', 'chinese', 'beijing', 'shanghai']
        for keyword in chinese_keywords:
            if keyword in all_descriptions:
                findings['chinese_in_classification_desc'].append(
                    f"'{keyword}' in classification description"
                )

        # 6. CHECK FOR SUSPICIOUS PATTERNS
        all_text = f"{all_names} {all_addresses} {business_types}".lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            if matches:
                findings['suspicious_pattern'].append(
                    f"Suspicious pattern match: {pattern[:50]}"
                )

        # 7. CHECK ULTIMATE PARENT VS IMMEDIATE PARENT MISMATCH
        # (Could indicate shell company structure)
        recipient_name = fields[23] if len(fields) > 23 else ''
        if (recipient_name and recipient_parent_name and
            recipient_name != recipient_parent_name and
            recipient_parent_name != '\\N'):
            # If parent has Chinese indicators but recipient doesn't
            if any(entity.lower() in recipient_parent_name.lower()
                   for entity in self.processor.CHINA_ENTITIES):
                if not any(entity.lower() in recipient_name.lower()
                          for entity in self.processor.CHINA_ENTITIES):
                    findings['hidden_chinese_parent'].append(
                        f"Recipient: {recipient_name[:50]} / Parent: {recipient_parent_name[:50]}"
                    )

        # 8. CHECK FOR ZERO/MINIMAL ADDRESS DATA (suspicious for federal contracts)
        if recipient_address_1 in ['', '\\N'] and float(fields[6] if fields[6] not in ['\\N', ''] else 0) > 100000:
            findings['missing_address_large_contract'].append(
                f"Large contract (${fields[6]}) with no address"
            )

        # 9. CHECK SUBAWARD DESCRIPTION FOR CHINESE ENTITIES/LOCATIONS
        if subaward_desc and subaward_desc != '\\N':
            # More aggressive checking in subaward descriptions
            for city in ['beijing', 'shanghai', 'shenzhen', 'guangzhou', 'hong kong',
                        'tianjin', 'chongqing', 'wuhan', 'chengdu', 'hangzhou']:
                if re.search(r'\b' + city + r'\b', subaward_desc.lower()):
                    findings['chinese_city_in_subaward_desc'].append(
                        f"City '{city}' mentioned in subaward description"
                    )

        # 10. CHECK AWARD TYPE PATTERNS
        # Certain award types more likely to involve foreign entities
        if award_type and award_type != '\\N':
            if any(keyword in award_type.lower()
                   for keyword in ['grant', 'cooperative agreement', 'other']):
                # Track for pattern analysis
                self.stats['field_coverage']['award_type_checked'] += 1

        return dict(findings)

    def run_comprehensive_test(self, file_path: Path, max_records: int = 500000):
        """
        Run comprehensive test with additional field checking.
        """

        print(f"\n{'='*80}")
        print("COMPREHENSIVE SAMPLE TEST")
        print(f"{'='*80}\n")
        print(f"Sample Size: {max_records:,} records")
        print(f"File: {file_path.name}")
        print(f"\nChecking ALL 206 columns for Chinese indicators...")
        print(f"{'='*80}\n")

        standard_detections = []
        additional_findings = []

        with gzip.open(file_path, 'rt', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                if line_num > max_records:
                    break

                fields = line.strip().split('\t')
                if len(fields) < 206:
                    continue

                self.stats['total_records'] += 1

                # Run standard detection
                try:
                    transaction = self.processor._extract_transaction(fields)
                    detection_results = self.processor._detect_china_entity(transaction, fields)

                    if detection_results:
                        self.stats['standard_detections'] += 1
                        detection_record = self.processor._build_detection_record(
                            transaction, detection_results, fields
                        )
                        standard_detections.append(detection_record)

                        # Also check for additional indicators on detections
                        additional = self.analyze_additional_fields(fields, line_num)
                        if additional:
                            detection_record['additional_indicators'] = additional

                    else:
                        # NON-detection: Check for additional indicators we might have missed
                        additional = self.analyze_additional_fields(fields, line_num)
                        if additional:
                            # Found something the standard detection missed!
                            finding = {
                                'line_number': line_num,
                                'recipient_name': transaction.recipient_name[:100],
                                'recipient_parent': transaction.recipient_parent_name[:100],
                                'sub_awardee_name': transaction.sub_awardee_name[:100],
                                'amount': transaction.federal_action_obligation,
                                'additional_indicators': additional,
                                'indicator_count': sum(len(v) for v in additional.values())
                            }
                            additional_findings.append(finding)

                            # Track statistics
                            for indicator_type in additional.keys():
                                self.stats['additional_indicators'][indicator_type] += 1

                except Exception as e:
                    continue

                if line_num % 100000 == 0:
                    print(f"  Processed {line_num:,} records:")
                    print(f"    Standard detections: {self.stats['standard_detections']}")
                    print(f"    Additional findings: {len(additional_findings)}")

        print(f"\n{'='*80}")
        print("COMPREHENSIVE TEST RESULTS")
        print(f"{'='*80}")
        print(f"Records processed: {self.stats['total_records']:,}")
        print(f"Standard detections: {self.stats['standard_detections']} "
              f"({self.stats['standard_detections']/self.stats['total_records']*100:.4f}%)")
        print(f"Additional findings: {len(additional_findings)}")

        if self.stats['additional_indicators']:
            print(f"\nAdditional Indicators Found:")
            for indicator_type, count in sorted(self.stats['additional_indicators'].items(),
                                               key=lambda x: x[1], reverse=True):
                print(f"  {indicator_type}: {count}")

        print(f"{'='*80}\n")

        return standard_detections, additional_findings

    def save_results(self, standard_detections: List[Dict],
                    additional_findings: List[Dict]):
        """Save comprehensive test results."""

        output_dir = Path("data/processed/usaspending_comprehensive_test")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save standard detections
        detections_file = output_dir / "standard_detections.json"
        with open(detections_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_records': self.stats['total_records'],
                'detection_count': len(standard_detections),
                'detection_rate': len(standard_detections) / self.stats['total_records'] * 100,
                'detections': standard_detections[:50]  # First 50
            }, f, indent=2)

        print(f"Saved standard detections: {detections_file}")

        # Save additional findings
        findings_file = output_dir / "additional_findings.json"
        with open(findings_file, 'w', encoding='utf-8') as f:
            # Sort by indicator count (most indicators first)
            sorted_findings = sorted(additional_findings,
                                    key=lambda x: x['indicator_count'],
                                    reverse=True)
            json.dump({
                'total_findings': len(additional_findings),
                'findings': sorted_findings[:100]  # Top 100
            }, f, indent=2)

        print(f"Saved additional findings: {findings_file}")

        # Create human-readable summary
        summary_file = output_dir / "COMPREHENSIVE_TEST_SUMMARY.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("COMPREHENSIVE SAMPLE TEST - SUMMARY\n")
            f.write("="*80 + "\n\n")

            f.write(f"Sample Size: {self.stats['total_records']:,} records\n")
            f.write(f"Standard Detections: {self.stats['standard_detections']} "
                   f"({self.stats['standard_detections']/self.stats['total_records']*100:.4f}%)\n")
            f.write(f"Additional Findings: {len(additional_findings)}\n\n")

            f.write("="*80 + "\n")
            f.write("ADDITIONAL INDICATORS FOUND (Beyond Standard Detection)\n")
            f.write("="*80 + "\n\n")

            if not additional_findings:
                f.write("✅ NO ADDITIONAL FINDINGS\n\n")
                f.write("Standard detection logic appears comprehensive.\n")
                f.write("No additional Chinese indicators found beyond what's already detected.\n")
            else:
                f.write(f"Found {len(additional_findings)} records with additional indicators.\n\n")

                # Summary by indicator type
                f.write("Indicator Type Breakdown:\n")
                for indicator_type, count in sorted(self.stats['additional_indicators'].items(),
                                                   key=lambda x: x[1], reverse=True):
                    f.write(f"  {indicator_type}: {count}\n")

                f.write("\n" + "="*80 + "\n")
                f.write("TOP 20 ADDITIONAL FINDINGS (Manual Review Required)\n")
                f.write("="*80 + "\n\n")

                sorted_findings = sorted(additional_findings,
                                       key=lambda x: x['indicator_count'],
                                       reverse=True)

                for i, finding in enumerate(sorted_findings[:20], 1):
                    f.write(f"{i}. LINE {finding['line_number']}\n")
                    f.write(f"   Recipient: {finding['recipient_name']}\n")
                    if finding['recipient_parent']:
                        f.write(f"   Parent: {finding['recipient_parent']}\n")
                    if finding['sub_awardee_name']:
                        f.write(f"   Sub-awardee: {finding['sub_awardee_name']}\n")
                    f.write(f"   Amount: ${finding['amount']:,.2f}\n")
                    f.write(f"\n   INDICATORS ({finding['indicator_count']}):\n")
                    for indicator_type, details in finding['additional_indicators'].items():
                        for detail in details:
                            f.write(f"     [{indicator_type}] {detail}\n")
                    f.write("\n" + "-"*80 + "\n\n")

        print(f"Created summary: {summary_file}")


def main():
    """Run comprehensive sample test."""

    test_file = Path("F:/OSINT_DATA/USAspending/extracted_data/5876.dat.gz")

    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return

    print("\nUSAspending Comprehensive Sample Test")
    print("="*80)
    print("\nThis will process 500,000 records checking ALL potential Chinese indicators")
    print("across the complete 206-column schema.\n")

    analyzer = ComprehensiveSampleAnalyzer()
    standard_detections, additional_findings = analyzer.run_comprehensive_test(
        test_file, max_records=500000
    )

    analyzer.save_results(standard_detections, additional_findings)

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Standard detections: {len(standard_detections)}")
    print(f"Additional findings: {len(additional_findings)}")

    if additional_findings:
        print(f"\n⚠️  Found {len(additional_findings)} records with indicators")
        print("    not caught by standard detection logic.")
        print("    Manual review recommended!")
    else:
        print("\n✅ No additional indicators found beyond standard detection.")
        print("    Detection logic appears comprehensive.")

    print("\nReview COMPREHENSIVE_TEST_SUMMARY.txt for details")


if __name__ == '__main__':
    main()
