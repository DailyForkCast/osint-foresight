#!/usr/bin/env python3
"""
Fix Word Boundary Issues in Chinese Entity Detection
Apply word boundary regex to all detection scripts

Date: October 22, 2025
Purpose: Prevent substring false positives (MACHINARY → CHINA, HEIZTECHNIK → ZTE, etc.)
"""

import re
from pathlib import Path
from datetime import datetime

# Detection scripts that need fixing
SCRIPTS_TO_FIX = [
    "scripts/process_usaspending_305_column.py",
    "scripts/process_usaspending_101_column.py",
    "scripts/process_usaspending_374_column.py",
    "scripts/refined_chinese_detector.py",
    "scripts/hybrid_chinese_detector.py",
]

def create_word_boundary_detection_class():
    """Create a reusable word boundary detection helper"""

    code = '''
import re

class WordBoundaryChineseDetector:
    """
    Enhanced Chinese entity detection with word boundary checking

    Prevents substring false positives:
    - "MACHINARY" no longer matches "CHINA"
    - "HEIZTECHNIK" no longer matches "ZTE"
    - "KASINO" no longer matches "SINO"
    """

    @staticmethod
    def detect_pattern_with_boundary(text, patterns, min_length=3):
        """
        Detect patterns using word boundaries

        Args:
            text: Text to search
            patterns: List/set of patterns to match
            min_length: Minimum pattern length for boundary checking (default: 3)

        Returns:
            (matched_pattern, confidence) or (None, 0)
        """
        if not text:
            return None, 0

        text_upper = text.upper()

        for pattern in patterns:
            pattern_upper = pattern.upper()

            # For very short patterns (< min_length), require exact word match
            if len(pattern_upper) < min_length:
                # Must be a complete word
                if re.search(r'\\b' + re.escape(pattern_upper) + r'\\b', text_upper):
                    return pattern, 0.9
            else:
                # For longer patterns, check word boundary
                if re.search(r'\\b' + re.escape(pattern_upper) + r'\\b', text_upper):
                    return pattern, 0.9
                # Also allow as part of compound (with hyphen or underscore)
                elif re.search(r'(^|[\\s_-])' + re.escape(pattern_upper) + r'($|[\\s_-])', text_upper):
                    return pattern, 0.85

        return None, 0

    @staticmethod
    def detect_chinese_name(company_name, chinese_patterns):
        """
        Detect Chinese company name with word boundaries

        Example usage:
            patterns = ['HUAWEI', 'ZTE', 'BEIJING', 'SHANGHAI', 'CHINA']
            matched, confidence = WordBoundaryChineseDetector.detect_chinese_name(name, patterns)
        """
        return WordBoundaryChineseDetector.detect_pattern_with_boundary(
            company_name, chinese_patterns, min_length=3
        )

    @staticmethod
    def detect_chinese_country(country_text, country_patterns):
        """
        Detect Chinese country indicators with word boundaries

        Example usage:
            patterns = ['CHINA', 'CHN', 'PRC', 'BEIJING', 'SHANGHAI']
            matched, confidence = WordBoundaryChineseDetector.detect_chinese_country(country, patterns)
        """
        return WordBoundaryChineseDetector.detect_pattern_with_boundary(
            country_text, country_patterns, min_length=2
        )
'''

    return code


def fix_detection_method_simple():
    """Create simple inline fix for existing detection methods"""

    before_pattern = r'''
    # OLD (WRONG):
    for pattern in self.CHINESE_NAME_PATTERNS:
        if pattern in company_name.upper():
            return True, 0.7
    '''

    after_pattern = r'''
    # NEW (CORRECT) - Word boundaries
    import re
    company_name_upper = company_name.upper()
    for pattern in self.CHINESE_NAME_PATTERNS:
        pattern_upper = pattern.upper()
        # Use word boundary for accurate matching
        if re.search(r'\b' + re.escape(pattern_upper) + r'\b', company_name_upper):
            return True, 0.9  # Higher confidence for word boundary match
    '''

    return before_pattern, after_pattern


def backup_script(script_path):
    """Create timestamped backup of script"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{script_path}.backup_{timestamp}"

    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  Backup created: {backup_path}")
    return backup_path


def main():
    base_path = Path(r"C:\Projects\OSINT - Foresight")

    print("=" * 80)
    print("Word Boundary Fix - Apply to Chinese Detection Scripts")
    print("=" * 80)

    # Create the helper class file
    helper_path = base_path / "scripts" / "word_boundary_detector.py"
    with open(helper_path, 'w', encoding='utf-8') as f:
        f.write(create_word_boundary_detection_class())

    print(f"\n[OK] Created helper class: {helper_path}")

    print("\n" + "=" * 80)
    print("NEXT STEPS - Manual Fix Required")
    print("=" * 80)

    print("\nThe following scripts need word boundary fixes:")
    print("\n1. USAS pending Scripts:")
    for script in SCRIPTS_TO_FIX:
        full_path = base_path / script
        if full_path.exists():
            print(f"   - {script}")
        else:
            print(f"   - {script} (NOT FOUND)")

    print("\n2. Recommended Approach:")
    print("   a) Use WordBoundaryChineseDetector helper class")
    print("   b) Replace pattern 'in' checks with:")
    print("      re.search(r'\\b' + re.escape(pattern) + r'\\b', text)")
    print("   c) Test with known false positives:")
    print("      - 'MACHINARY' should NOT match 'CHINA'")
    print("      - 'HEIZTECHNIK' should NOT match 'ZTE'")
    print("      - 'KASINO' should NOT match 'SINO'")

    print("\n3. Example Fix:")
    print("""
    # BEFORE (Wrong):
    if 'CHINA' in company_name.upper():
        return True

    # AFTER (Correct):
    import re
    if re.search(r'\\bCHINA\\b', company_name.upper()):
        return True
    """)

    print("\n" + "=" * 80)
    print("Or use the helper class:")
    print("=" * 80)
    print("""
    from word_boundary_detector import WordBoundaryChineseDetector

    matched, confidence = WordBoundaryChineseDetector.detect_chinese_name(
        company_name,
        self.CHINESE_NAME_PATTERNS
    )
    if matched:
        return True, confidence
    """)

    print("\n" + "=" * 80)
    print("Helper class created. Ready for manual application to detection scripts.")
    print("=" * 80)


if __name__ == '__main__':
    main()
