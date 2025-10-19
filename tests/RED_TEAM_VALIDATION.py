#!/usr/bin/env python3
"""
Red Team Validation - Try to break our detection logic

This script attempts to find edge cases and bypass patterns that our unit tests don't catch.
We want to identify gaps in test coverage BEFORE production use.

Last Updated: 2025-10-18
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "scripts"))

from process_usaspending_305_column import USAspending305Processor


class RedTeamValidator:
    """Red team testing - try to break detection logic"""

    def __init__(self):
        self.processor = USAspending305Processor()
        self.findings = []

    def test_bypass_attempts(self):
        """Try to bypass Chinese entity detection"""
        print("=" * 80)
        print("RED TEAM VALIDATION - Bypass Attempts")
        print("=" * 80)
        print()

        bypass_attempts = [
            # Obfuscation techniques
            ("H u a w e i", "Spaced company name"),
            ("Hua-wei", "Hyphenated name"),
            ("Hua wei", "Split name"),

            # Mixed scripts (skipping Chinese chars due to console encoding)
            # ("华为 Huawei", "Chinese characters + English"),

            # Misspellings
            ("Hwawei", "Common misspelling"),
            ("Huawai", "Common misspelling"),

            # Similar sounding
            ("Wahway Technologies", "Phonetic similar"),

            # Abbreviations
            ("HW Technologies", "Abbreviated"),
            ("ZT Corporation", "Abbreviated ZTE"),

            # Country variations
            ("PEOPLES REPUBLIC OF CHINA", "Alternate spelling"),
            ("P.R.C.", "Abbreviated"),
            ("Mainland China", "Informal name"),

            # Hong Kong tricks
            ("HONG-KONG", "Hyphenated"),
            ("HK SAR", "Special administrative region"),

            # Taiwan edge cases
            ("Taipei", "Capital city - should NOT detect as China"),
            ("ROC", "Republic of China - should NOT detect"),
            ("Formosa", "Old name for Taiwan - should NOT detect"),

            # False positives we might miss
            ("Chinati Foundation", "Contains 'china'"),
            ("Chino Hills California", "City name"),
            ("Machinist Union", "Contains 'chin'"),
            ("China Beach", "Location name"),

            # Legitimate US companies
            ("China King Restaurant", "Restaurant chain"),
            ("Great Wall Chinese Restaurant", "Restaurant"),
            ("Panda Express", "Chinese-American chain - NOT Chinese entity"),
        ]

        print("Testing bypass attempts:\n")
        bypasses_found = 0
        false_positives_found = 0

        for test_input, description in bypass_attempts:
            # Test name detection
            detected_name = self.processor._has_chinese_name(test_input)
            # Test country detection
            detected_country = self.processor._is_china_country(test_input)

            detected = detected_name or detected_country

            # Categorize findings
            should_detect = any(keyword in description.lower() for keyword in
                               ['company', 'corporation', 'technologies', 'misspelling',
                                'phonetic', 'china', 'prc', 'hong-kong', 'hong kong'])
            should_not_detect = any(keyword in description.lower() for keyword in
                                   ['should not', 'taiwan', 'roc', 'formosa', 'false positive',
                                    'restaurant', 'panda express', 'location', 'city'])

            status = "DETECTED" if detected else "NOT DETECTED"

            if should_not_detect and detected:
                symbol = "PROBLEM"
                false_positives_found += 1
            elif should_detect and not detected:
                symbol = "BYPASS"
                bypasses_found += 1
            else:
                symbol = "OK"

            print(f"[{symbol:^10}] {test_input:40} -> {status:15} ({description})")

        print()
        print("=" * 80)
        print(f"Bypass attempts found: {bypasses_found}")
        print(f"False positives found: {false_positives_found}")
        print("=" * 80)
        print()

        return bypasses_found, false_positives_found

    def test_confidence_scoring(self):
        """Validate confidence scores are reasonable"""
        print("=" * 80)
        print("CONFIDENCE SCORING VALIDATION")
        print("=" * 80)
        print()

        # These should have DIFFERENT confidence levels
        test_cases = [
            ("CHN", "Country code - should be HIGH"),
            ("Huawei Technologies", "Known entity - should be HIGH"),
            ("Beijing Company", "City name - should be MEDIUM/HIGH"),
            ("China acceptable", "Product sourcing - should be LOW"),
            ("Generic Inc", "No indicators - should be NONE"),
        ]

        # Note: We don't have direct confidence scoring in the individual functions
        # They return boolean. Confidence is calculated in _detect_china_connection
        # This is a limitation we should note.

        print("Note: Individual detection functions return boolean, not confidence.")
        print("Confidence scoring happens in full _detect_china_connection method.")
        print("This means we CAN'T test confidence at the unit level.")
        print()
        print("RECOMMENDATION: Add confidence scoring to individual methods OR")
        print("                add integration tests for full detection pipeline.")
        print()

    def test_edge_cases(self):
        """Test edge cases that might not be covered"""
        print("=" * 80)
        print("EDGE CASE TESTING")
        print("=" * 80)
        print()

        edge_cases = [
            # Encoding issues
            ("CHINA", "All caps"),
            ("china", "All lowercase"),
            ("ChInA", "Mixed case"),
            ("  CHINA  ", "Extra whitespace"),
            ("CHINA\n", "Newline"),
            ("CHINA\t", "Tab"),

            # Unicode (skipping due to console encoding)
            # ("中国", "Chinese characters for China"),

            # Empty/None
            ("", "Empty string"),
            (None, "None value"),

            # Very long strings
            ("A" * 1000 + "CHINA", "Very long string with China"),

            # Special characters
            ("CHINA!", "With punctuation"),
            ("CHINA?", "With question mark"),
            ("(CHINA)", "In parentheses"),

            # Numbers
            ("CHINA 123", "With numbers"),
            ("123 CHINA", "Numbers first"),
        ]

        print("Testing edge cases:\n")
        errors_found = 0

        for test_input, description in edge_cases:
            try:
                result = self.processor._is_china_country(test_input) or \
                        self.processor._has_chinese_name(test_input)
                print(f"[OK] {str(test_input)[:40]:40} -> {result} ({description})")
            except Exception as e:
                print(f"[ERROR] {str(test_input)[:40]:40} -> EXCEPTION: {e}")
                errors_found += 1

        print()
        print(f"Errors found: {errors_found}")
        print()

    def run_all_tests(self):
        """Run all red team validation tests"""
        print("\n")
        print("*" * 80)
        print("RED TEAM VALIDATION SUITE")
        print("Testing OSINT Foresight Chinese Entity Detection Logic")
        print("*" * 80)
        print("\n")

        bypasses, false_positives = self.test_bypass_attempts()
        self.test_confidence_scoring()
        self.test_edge_cases()

        print()
        print("=" * 80)
        print("RED TEAM VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Bypass techniques that work: {bypasses}")
        print(f"False positives detected: {false_positives}")
        print()

        if bypasses > 0:
            print("WARNING: Some bypass techniques work - detection can be evaded!")
        if false_positives > 0:
            print("WARNING: Some false positives detected - may flag non-Chinese entities!")

        if bypasses == 0 and false_positives == 0:
            print("PASS: No critical issues found in red team testing")
        else:
            print("REVIEW NEEDED: Issues found that may require attention")

        print("=" * 80)
        print()


if __name__ == "__main__":
    validator = RedTeamValidator()
    validator.run_all_tests()
