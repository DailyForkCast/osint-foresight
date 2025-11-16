#!/usr/bin/env python3
"""
Analyze specific false positive patterns to understand detection logic.
"""

import sqlite3
from pathlib import Path

def analyze_patterns():
    """Analyze why specific entities were flagged."""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    print("="*100)
    print("FALSE POSITIVE PATTERN ANALYSIS")
    print("="*100)

    # Check the Chinese name patterns used in detection
    print("\n\nLet me analyze each false positive:\n")

    # 1. COMAC PUMP & WELL LLC
    print("="*100)
    print("1. COMAC PUMP & WELL LLC")
    print("="*100)
    print("Issue: 'COMAC' matches Chinese aircraft manufacturer (Commercial Aircraft Corp of China)")
    print("Reality: This is a US pump and well company (COVID relief)")
    print("Pattern matched: 'comac' (entity list)")
    print("Fix needed: Need to distinguish COMAC (aircraft) from local pump companies")
    print()

    # 2. MBA OFFICE SUPPLY - "made in China"
    print("="*100)
    print("2. MBA OFFICE SUPPLY INC. (and 346 similar records)")
    print("="*100)
    print("Issue: Description contains 'MADE IN CHINA' for product labeling")
    print("Reality: US company purchasing items manufactured in China")
    print("Pattern matched: pop_country_china (description mentions China)")
    print("Fix needed: Exclude descriptions with 'made in china' / 'manufactured in china'")

    cursor = conn.execute("""
        SELECT recipient_name, award_description
        FROM usaspending_china_305
        WHERE LOWER(award_description) LIKE '%made in china%'
        LIMIT 10
    """)

    print("\nSample 'made in China' descriptions:")
    for i, row in enumerate(cursor.fetchall(), 1):
        desc = row['award_description'] or ''
        print(f"{i}. {row['recipient_name']}: {desc[:150]}...")
    print()

    # 3. AZTEC ENVIRONMENTAL, INC.
    print("="*100)
    print("3. AZTEC ENVIRONMENTAL, INC.")
    print("="*100)
    name = "AZTEC ENVIRONMENTAL, INC."
    name_lower = name.lower()
    print(f"Name: {name}")
    print(f"Checking Chinese name patterns...")

    # Load Chinese name patterns from the processor config
    chinese_patterns = [
        'china', 'chinese', 'beijing', 'shanghai', 'hong kong', 'hongkong',
        'shenzhen', 'guangzhou', 'chengdu', 'wuhan', 'tianjin',
        'sino', 'sinotech', 'zhonghua', 'huawei', 'xiaomi', 'alibaba',
        'tencent', 'baidu', 'lenovo', 'zte', 'haier', 'tsinghua'
    ]

    matches = [p for p in chinese_patterns if p in name_lower]
    if matches:
        print(f"MATCHED: {matches}")
    else:
        print("Hmm, not matching obvious patterns. Let me check for substring issues...")
        # Check for partial matches
        for pattern in chinese_patterns:
            if any(pattern in word.lower() for word in name.split()):
                print(f"  Partial match: '{pattern}' in name")
    print()

    # 4. EZTEQ LLC
    print("="*100)
    print("4. EZTEQ LLC")
    print("="*100)
    name = "EZTEQ LLC"
    print(f"Name: {name}")
    print("Issue: Probably matching 'teq' or 'eq' pattern")
    print("Reality: US company (likely 'EZ Tech' or 'Easy Tech Equipment')")
    print()

    # 5. Check for more entity name patterns
    print("="*100)
    print("5. Checking other mentioned entities")
    print("="*100)

    entities_to_check = [
        "AVIC",  # Could match Aviation Industry Corporation of China
        "VISTA GORGONIO",
        "T K C ENTERPRISES",
        "TKC",  # Checking if 'TKC' matches something
    ]

    for entity in entities_to_check:
        cursor = conn.execute("""
            SELECT COUNT(*) as count
            FROM usaspending_china_305
            WHERE recipient_name LIKE ?
            LIMIT 1
        """, (f'%{entity}%',))

        count = cursor.fetchone()['count']
        if count > 0:
            print(f"\n'{entity}': Found {count} records")

            cursor = conn.execute("""
                SELECT transaction_id, recipient_name, detection_types
                FROM usaspending_china_305
                WHERE recipient_name LIKE ?
                LIMIT 3
            """, (f'%{entity}%',))

            for row in cursor:
                print(f"  {row['transaction_id']}: {row['recipient_name']}")
                print(f"    Detection: {row['detection_types']}")

    # 6. Ethnic Tibet pattern
    print("\n" + "="*100)
    print("6. 'SUPPORT TO ETHNIC TIBETS IN CHINA' Pattern")
    print("="*100)
    print("Issue: Descriptions about humanitarian aid to Tibetan people IN China")
    print("Reality: These are US aid programs, not Chinese entities")
    print("Fix needed: Exclude descriptions with 'ethnic tibet' / 'support to ethnic'")

    cursor = conn.execute("""
        SELECT recipient_name, award_description
        FROM usaspending_china_101
        WHERE LOWER(award_description) LIKE '%ethnic tibet%'
        LIMIT 5
    """)

    print("\nSample 'ethnic tibet' records:")
    for row in cursor:
        print(f"  {row['recipient_name']}")
        print(f"    Description: {row['award_description'][:200]}...")
        print()

    conn.close()

    # Summary of fixes needed
    print("\n" + "="*100)
    print("SUMMARY OF FIXES NEEDED")
    print("="*100)
    print("""
1. Add to false positive filters:
   - 'comac pump' / 'comac well' (to exclude pump companies from COMAC aircraft)
   - 'aztec' (Aztec Environmental)
   - 'ezteq' (EZ Tech company)
   - 'avic travel' (if matching Aviation Industry Corp of China)
   - 'vista gorgonio'
   - 't k c enterprises' / 'tkc enterprises'

2. Add description-based exclusions:
   - 'made in china' (product origin labeling)
   - 'manufactured in china' (product origin)
   - 'produced in china' (product origin)
   - 'ethnic tibet' (humanitarian aid to Tibetan people)
   - 'support to ethnic' (general humanitarian aid)

3. Consider: Should "made in China" products be flagged at all?
   - These are US entities buying China-manufactured goods
   - Not the same as Chinese entities winning contracts
   - Recommend: EXCLUDE these from China entity detection
   - Alternative: Flag separately as "China-sourced products" (different category)
""")


if __name__ == '__main__':
    analyze_patterns()
