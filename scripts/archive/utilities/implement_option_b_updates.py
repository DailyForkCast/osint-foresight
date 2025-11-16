#!/usr/bin/env python3
"""
Apply Option B Updates to All Three USAspending Processors

Adds `china_sourced_product` detection category to distinguish:
- Chinese entity relationships (HIGH/MEDIUM confidence)
- China-manufactured products (LOW confidence, supply chain tracking)

This script will:
1. Add `_is_product_sourcing_mention()` function to each processor
2. Modify description detection logic to categorize product sourcing separately
3. Update false positive filters to include Round 4 patterns
"""

from pathlib import Path

# New function to add to all processors
PRODUCT_SOURCING_FUNCTION = '''
    def _is_product_sourcing_mention(self, description: str) -> bool:
        """
        Check if description mentions China as product origin (not entity relationship).

        Returns True if description indicates China-manufactured product.
        This is used for Option B: Separate category for supply chain visibility.
        """
        if not description:
            return False

        desc_lower = description.lower()

        # Product origin phrases (indicates manufacturing location, not entity)
        product_origin_phrases = [
            'made in china',
            'manufactured in china',
            'produced in china',
            'fabricated in china',
            'assembled in china',
            'origin china',
            'origin: china',
            'country of origin china',
            'country of origin: china',
            'made in prc',
            'manufactured in prc',
            'china acceptable',  # "made in China acceptable"
            'produced in prc',
        ]

        return any(phrase in desc_lower for phrase in product_origin_phrases)
'''

# Round 4 false positive patterns to add
ROUND_4_FALSE_POSITIVES = [
    # Round 4: Entity name substring false positives
    "'comac pump',  # Comac Pump & Well LLC (not COMAC aircraft)",
    "'comac well',",
    "'aztec environmental',  # Aztec Environmental (not ZTE)",
    "'aztec',  # Broader match for Aztec companies",
    "'ezteq',  # EZ Tech company",
    "'t k c enterprises',  # T K C Enterprises (41 false positives)",
    "'tkc enterprises',",
    "'mavich',  # Mavich LLC (contains 'avic')",
    "'vista gorgonio',  # Vista Gorgonio Inc",
    "'pri/djv',  # PRI/DJI Construction JV (not DJI drones)",
    "\"avic's travel\",  # Avic's Travel LLC (not AVIC)",
]

def main():
    """Show what needs to be updated in each processor."""

    print("="*100)
    print("OPTION B IMPLEMENTATION UPDATES")
    print("="*100)
    print()
    print("This script shows the updates needed for each processor.")
    print("Manual implementation is required due to different processor structures.")
    print()

    print("="*100)
    print("1. NEW FUNCTION TO ADD (all three processors)")
    print("="*100)
    print(PRODUCT_SOURCING_FUNCTION)

    print("\n" + "="*100)
    print("2. ROUND 4 FALSE POSITIVE PATTERNS TO ADD")
    print("="*100)
    print("Add to FALSE_POSITIVES list in each processor:")
    for pattern in ROUND_4_FALSE_POSITIVES:
        print(f"    {pattern}")

    print("\n" + "="*100)
    print("3. PROCESSORS TO UPDATE")
    print("="*100)

    processors = [
        ("scripts/process_usaspending_101_column.py", "101-column processor"),
        ("scripts/process_usaspending_305_column.py", "305-column processor"),
        ("scripts/process_usaspending_comprehensive.py", "206-column processor"),
    ]

    for path, name in processors:
        file_path = Path("C:/Projects/OSINT - Foresight") / path
        print(f"\n{name}:")
        print(f"  Path: {file_path}")
        print(f"  Exists: {file_path.exists()}")
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  Size: {size:,} bytes")

    print("\n" + "="*100)
    print("4. TESTING PLAN")
    print("="*100)
    print("""
After implementing updates:

1. Test with T K C ENTERPRISES record:
   - Transaction ID: 20841746
   - Expected: detection_type='china_sourced_product', confidence='LOW'
   - Description: "BATTERY, RECHARGEABLE... MADE IN CHINA ACCEPTABLE"

2. Test with MBA OFFICE SUPPLY record:
   - Transaction ID: 48212082
   - Expected: detection_type='china_sourced_product', confidence='LOW'
   - Description: "BRIEFCASE PART #7200 BK MADE IN CHINA"

3. Test with actual Chinese entity (control):
   - Should still detect as HIGH confidence with entity_name detection
   - Should NOT be categorized as product sourcing

4. Test with COMAC PUMP & WELL:
   - Should be filtered out by false positive list
   - Should NOT appear in detections

5. Test with Ethnic Tibet description:
   - Should be filtered out by false positive list
   - Should NOT appear in detections
""")

    print("\n" + "="*100)
    print("NEXT STEPS")
    print("="*100)
    print("""
1. Update 101-column processor (currently NO description checking)
2. Update 305-column processor (currently NO description checking)
3. Update 206-column processor (needs verification)
4. Run test suite on sample records
5. Decide on re-processing strategy:
   - Option A: Re-process all 117M+ records (8-12 hours)
   - Option B: Update only affected records via SQL (faster but riskier)
""")


if __name__ == '__main__':
    main()
