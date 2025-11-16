#!/usr/bin/env python3
"""
Investigate Remaining False Positives
Analyze single-detection US companies and other patterns
"""

import sqlite3
import re
from collections import defaultdict

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

CHINESE_NAME_PATTERNS = {
    'beijing', 'shanghai', 'guangzhou', 'shenzhen',
    'china', 'chinese', 'sino', 'huawei', 'zte',
    'alibaba', 'tencent', 'baidu', 'lenovo',
    'haier', 'xiaomi', 'byd', 'geely'
}

def find_matching_pattern(name):
    """Find which pattern matches and how"""
    if not name:
        return []

    name_lower = name.lower()
    matches = []

    for pattern in CHINESE_NAME_PATTERNS:
        if pattern in name_lower:
            # Check if it's a word boundary match or substring
            word_pattern = r'\b' + re.escape(pattern) + r'\b'
            if re.search(word_pattern, name_lower):
                matches.append((pattern, 'word_boundary'))
            else:
                matches.append((pattern, 'substring'))

    return matches

def investigate_remaining_false_positives():
    """Investigate all remaining US companies and questionable entities"""

    print("=" * 80)
    print("INVESTIGATING REMAINING FALSE POSITIVES")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB, timeout=120)
    cursor = conn.cursor()

    # Total count
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    total = cursor.fetchone()[0]
    print(f"\nCurrent total: {total:,}")

    # [1] Single-detection US companies
    print("\n" + "=" * 80)
    print("[1] SINGLE-DETECTION US COMPANIES")
    print("=" * 80)

    cursor.execute("""
        SELECT
            recipient_name,
            vendor_name,
            recipient_country_code,
            recipient_country_name,
            detection_types,
            COUNT(*) as count
        FROM usaspending_china_305
        WHERE (recipient_country_code IN ('USA', 'UNITED STATES')
               OR recipient_country_name IN ('USA', 'UNITED STATES'))
          AND (detection_types = '["chinese_name_vendor"]'
               OR detection_types = '["chinese_name_recipient"]')
          AND recipient_name NOT LIKE '%LENOVO%'
          AND vendor_name NOT LIKE '%LENOVO%'
        GROUP BY recipient_name, vendor_name, detection_types
        ORDER BY count DESC
        LIMIT 30
    """)

    single_detection_us = cursor.fetchall()
    total_single_us = sum(c for _, _, _, _, _, c in single_detection_us)

    print(f"\nTotal single-detection US companies: {total_single_us:,} records")
    print(f"\nTop 30 entities:")

    substring_matches = []
    word_boundary_matches = []

    for recipient, vendor, r_country_code, r_country_name, detection_type, count in single_detection_us:
        entity_name = vendor if vendor else recipient

        matches = find_matching_pattern(entity_name)

        has_substring = any(match_type == 'substring' for _, match_type in matches)
        has_word_boundary = any(match_type == 'word_boundary' for _, match_type in matches)

        match_info = ""
        for pattern, match_type in matches:
            if match_type == 'substring':
                match_info += f" '{pattern}' (SUBSTRING)"
            else:
                match_info += f" '{pattern}' (WORD)"

        classification = "REMOVE" if has_substring else "REVIEW"

        print(f"  {count:4d} | {entity_name[:50]:50} | {classification} |{match_info}")

        if has_substring:
            substring_matches.append({
                'entity': entity_name,
                'recipient': recipient,
                'vendor': vendor,
                'count': count,
                'matches': matches
            })
        elif has_word_boundary:
            word_boundary_matches.append({
                'entity': entity_name,
                'recipient': recipient,
                'vendor': vendor,
                'count': count,
                'matches': matches
            })

    # [2] Casino/Hotel false positives
    print("\n" + "=" * 80)
    print("[2] CASINO/HOTEL FALSE POSITIVES (CASINO -> SINO)")
    print("=" * 80)

    cursor.execute("""
        SELECT
            recipient_name,
            vendor_name,
            recipient_country_code,
            detection_types,
            COUNT(*) as count
        FROM usaspending_china_305
        WHERE (recipient_name LIKE '%CASINO%' OR vendor_name LIKE '%CASINO%')
          AND recipient_name NOT LIKE '%LENOVO%'
          AND vendor_name NOT LIKE '%LENOVO%'
        GROUP BY recipient_name, vendor_name
        ORDER BY count DESC
    """)

    casino_records = cursor.fetchall()
    total_casino = sum(c for _, _, _, _, c in casino_records)

    print(f"\nTotal casino/hotel records: {total_casino:,}")
    print(f"\nAll casino entities:")

    casino_to_remove = []
    for recipient, vendor, r_country, detection_type, count in casino_records:
        entity_name = vendor if vendor else recipient

        # Check if it's a real Chinese casino or false positive
        is_china = r_country in ['CHN', 'CHINA']

        classification = "KEEP (China)" if is_china else "REMOVE (False positive)"

        print(f"  {count:4d} | {entity_name[:50]:50} | {r_country:15} | {classification}")

        if not is_china:
            casino_to_remove.append({
                'entity': entity_name,
                'recipient': recipient,
                'vendor': vendor,
                'count': count
            })

    # [3] Other questionable non-US entities
    print("\n" + "=" * 80)
    print("[3] NON-US QUESTIONABLE ENTITIES")
    print("=" * 80)

    # Check for Italian, German companies with single detection
    cursor.execute("""
        SELECT
            recipient_name,
            vendor_name,
            recipient_country_code,
            detection_types,
            COUNT(*) as count
        FROM usaspending_china_305
        WHERE recipient_country_code NOT IN ('CHN', 'CHINA', 'USA', 'UNITED STATES')
          AND (detection_types = '["chinese_name_vendor"]'
               OR detection_types = '["chinese_name_recipient"]'
               OR detection_types = '["chinese_name_recipient", "chinese_name_vendor"]')
          AND recipient_name NOT LIKE '%BEIJING%'
          AND recipient_name NOT LIKE '%SHANGHAI%'
          AND recipient_name NOT LIKE '%GUANGZHOU%'
          AND vendor_name NOT LIKE '%BEIJING%'
          AND vendor_name NOT LIKE '%SHANGHAI%'
          AND vendor_name NOT LIKE '%GUANGZHOU%'
        GROUP BY recipient_name, vendor_name, recipient_country_code
        ORDER BY count DESC
        LIMIT 20
    """)

    non_us_questionable = cursor.fetchall()

    print(f"\nTop 20 non-US entities with name-only detection:")

    non_us_to_review = []
    for recipient, vendor, r_country, detection_type, count in non_us_questionable:
        entity_name = vendor if vendor else recipient

        matches = find_matching_pattern(entity_name)
        has_substring = any(match_type == 'substring' for _, match_type in matches)

        match_info = ""
        for pattern, match_type in matches:
            match_info += f" '{pattern}' ({match_type})"

        classification = "REMOVE?" if has_substring else "REVIEW"

        print(f"  {count:4d} | {entity_name[:40]:40} | {r_country:10} | {classification} |{match_info}")

        non_us_to_review.append({
            'entity': entity_name,
            'recipient': recipient,
            'vendor': vendor,
            'country': r_country,
            'count': count,
            'matches': matches,
            'has_substring': has_substring
        })

    # [4] Check PHARMARON specifically
    print("\n" + "=" * 80)
    print("[4] PHARMARON INVESTIGATION")
    print("=" * 80)

    cursor.execute("""
        SELECT
            transaction_id,
            recipient_name,
            vendor_name,
            recipient_country_code,
            pop_country_code,
            award_description,
            detection_types
        FROM usaspending_china_305
        WHERE recipient_name LIKE '%PHARMARON%' OR vendor_name LIKE '%PHARMARON%'
        LIMIT 5
    """)

    pharmaron_records = cursor.fetchall()

    print(f"\nPharmaron sample records ({len(pharmaron_records)}):")
    for tid, recipient, vendor, r_country, pop_country, description, detection_type in pharmaron_records:
        print(f"\n  Transaction: {tid}")
        print(f"  Recipient: {recipient}")
        print(f"  Vendor: {vendor}")
        print(f"  Recipient Country: {r_country}")
        print(f"  PoP Country: {pop_country}")
        print(f"  Detection: {detection_type}")
        print(f"  Description: {description[:100] if description else 'N/A'}...")

    # PHARMARON is a Chinese CRO (Contract Research Organization) with US subsidiary
    # They are Chinese-owned, so should be KEPT

    # Summary
    print("\n" + "=" * 80)
    print("REMOVAL RECOMMENDATIONS")
    print("=" * 80)

    print(f"\n[1] Single-detection US substring matches:")
    print(f"    Records to remove: {sum(r['count'] for r in substring_matches):,}")
    print(f"    Examples: SINON'S FARM, BIOSPACE, SINONYM CONSULTING, SPIRIT LAKE CASINO")

    print(f"\n[2] Casino false positives (non-China):")
    print(f"    Records to remove: {sum(r['count'] for r in casino_to_remove):,}")
    print(f"    Examples: SPIRIT LAKE CASINO, GRAND PALM HOTEL CASINO")

    print(f"\n[3] Non-US questionable entities:")
    print(f"    Needs review: {len(non_us_to_review)} entities")
    print(f"    Potentially remove: {sum(r['count'] for r in non_us_to_review if r['has_substring']):,} records")

    print(f"\n[4] PHARMARON:")
    print(f"    Classification: KEEP (Chinese-owned CRO with US operations)")

    total_to_remove = (
        sum(r['count'] for r in substring_matches) +
        sum(r['count'] for r in casino_to_remove)
    )

    print(f"\n" + "=" * 80)
    print(f"CONSERVATIVE REMOVAL ESTIMATE: {total_to_remove:,} records")
    print(f"Remaining after removal: {total - total_to_remove:,} records")
    print(f"=" * 80)

    conn.close()

    return {
        'substring_us_matches': substring_matches,
        'casino_false_positives': casino_to_remove,
        'non_us_questionable': non_us_to_review,
        'total_to_remove': total_to_remove
    }

if __name__ == "__main__":
    try:
        results = investigate_remaining_false_positives()
        print(f"\n[SUCCESS] Investigation complete")
        print(f"Conservative removal: {results['total_to_remove']:,} records")
    except Exception as e:
        print(f"\n[ERROR] Investigation failed: {e}")
        import traceback
        traceback.print_exc()
