#!/usr/bin/env python3
"""
Fix TIER 1 Strategic Entity Matching - Add Word Boundaries

The current implementation uses substring matching which causes false positives:
- "ZTE" matches "ZTERS", "AZTEC", "EZTEQ"
- "AVIC" matches "MAVICH"

This script updates all three processors to use word boundary matching for TIER 1.
"""

import re
from pathlib import Path

def fix_processor(file_path: Path):
    """Fix word boundary matching in a processor."""

    print(f"\nFixing {file_path.name}...")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the TIER 1 entity check
    old_pattern = r"        # TIER 1: Strategic Entities \(name match\)\n        for entity in self\.TIER_1_STRATEGIC_ENTITIES:\n            if entity in recipient or entity in vendor:\n                return \('TIER_1', 1\.0, 'strategic_entity'\)"

    # New pattern with word boundaries
    new_pattern = r"""        # TIER 1: Strategic Entities (name match with word boundaries)
        for entity in self.TIER_1_STRATEGIC_ENTITIES:
            # Use word boundaries to avoid substring matches (ZTE vs ZTERS, AZTEC, etc.)
            pattern = r'\b' + re.escape(entity) + r'\b'
            if re.search(pattern, recipient, re.IGNORECASE) or re.search(pattern, vendor, re.IGNORECASE):
                return ('TIER_1', 1.0, 'strategic_entity')"""

    if old_pattern not in content:
        # Try alternate match
        if "for entity in self.TIER_1_STRATEGIC_ENTITIES:" in content:
            # Find and replace the specific section
            content = re.sub(
                r"(        # TIER 1: Strategic Entities \(name match\)\n"
                r"        for entity in self\.TIER_1_STRATEGIC_ENTITIES:\n"
                r"            if entity in recipient or entity in vendor:\n"
                r"                return \('TIER_1', 1\.0, 'strategic_entity'\))",
                new_pattern,
                content
            )
            print(f"  [OK] Updated with word boundary matching")
        else:
            print(f"  [WARNING] Could not find TIER 1 entity check pattern")
            return False
    else:
        content = content.replace(old_pattern, new_pattern)
        print(f"  [OK] Updated with word boundary matching")

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

def main():
    """Fix all three processors."""

    print("="*80)
    print("FIXING TIER 1 WORD BOUNDARY MATCHING")
    print("="*80)

    processors = [
        Path('scripts/process_usaspending_305_column.py'),
        Path('scripts/process_usaspending_101_column.py'),
        Path('scripts/process_usaspending_comprehensive.py'),
    ]

    for processor in processors:
        if processor.exists():
            fix_processor(processor)
        else:
            print(f"\n[WARNING] File not found: {processor}")

    print("\n" + "="*80)
    print("FIX COMPLETE")
    print("="*80)

    print("\nWord boundary matching added for TIER 1 entities.")
    print("This prevents false positives like:")
    print("  - 'ZTE' matching 'ZTERS', 'AZTEC', 'EZTEQ'")
    print("  - 'AVIC' matching 'MAVICH'")
    print("\nRe-run the tier-stratified sample to verify fix.")

if __name__ == '__main__':
    main()
