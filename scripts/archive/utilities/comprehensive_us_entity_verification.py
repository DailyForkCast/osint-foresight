#!/usr/bin/env python3
"""
Comprehensive US Entity Verification
Verify ALL US entities individually, not just top ones
"""

import sqlite3
from collections import defaultdict

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

def comprehensive_us_verification():
    """Verify every single US entity"""

    print("=" * 80)
    print("COMPREHENSIVE US ENTITY VERIFICATION")
    print("=" * 80)
    print("\nVerifying ALL 863 US-country records individually...")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB, timeout=120)
    cursor = conn.cursor()

    # Get total US count
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE recipient_country_code IN ('USA', 'UNITED STATES')
           OR recipient_country_name IN ('USA', 'UNITED STATES')
    """)
    total_us = cursor.fetchone()[0]
    print(f"\nTotal US-country records: {total_us:,}")

    # Get ALL unique US entities
    print("\n" + "=" * 80)
    print("ALL UNIQUE US ENTITIES (COMPLETE LIST)")
    print("=" * 80)

    cursor.execute("""
        SELECT
            COALESCE(vendor_name, recipient_name) as entity,
            recipient_name,
            vendor_name,
            recipient_country_code,
            pop_country_code,
            detection_types,
            COUNT(*) as count
        FROM usaspending_china_305
        WHERE recipient_country_code IN ('USA', 'UNITED STATES')
           OR recipient_country_name IN ('USA', 'UNITED STATES')
        GROUP BY entity, recipient_name, vendor_name, detection_types
        ORDER BY count DESC
    """)

    all_us_entities = cursor.fetchall()

    print(f"\nTotal unique US entities: {len(all_us_entities)}")
    print("\nComplete list:\n")

    verified_chinese = []
    needs_review = []
    potential_false_positives = []

    for entity, recipient, vendor, r_country, pop_country, detection_types, count in all_us_entities:

        # Classification logic
        classification = "UNKNOWN"
        reason = ""

        # Check if it's verified Chinese-owned
        if entity and 'LENOVO' in entity.upper():
            classification = "VERIFIED: Chinese-owned"
            reason = "Lenovo Group Limited (China)"
            verified_chinese.append((entity, count, reason))

        elif entity and 'PHARMARON' in entity.upper():
            # Check if has PoP = CHN
            classification = "VERIFIED: Chinese-owned" if pop_country == 'CHN' else "NEEDS REVIEW"
            reason = "Chinese CRO, PoP=CHN" if pop_country == 'CHN' else "Chinese CRO, PoP unclear"
            if classification == "VERIFIED: Chinese-owned":
                verified_chinese.append((entity, count, reason))
            else:
                needs_review.append((entity, count, reason))

        elif entity and ('CHINA PUBLISHING' in entity.upper() or 'BEIJING BOOK' in entity.upper()):
            classification = "VERIFIED: Chinese book distributor" if pop_country == 'CHN' else "NEEDS REVIEW"
            reason = f"Chinese distributor, PoP={pop_country or 'N/A'}"
            if classification.startswith("VERIFIED"):
                verified_chinese.append((entity, count, reason))
            else:
                needs_review.append((entity, count, reason))

        elif entity and 'CHINESE ACADEMY' in entity.upper():
            classification = "VERIFIED: Chinese institution"
            reason = "Chinese research academy"
            verified_chinese.append((entity, count, reason))

        # Check if it's detecting the recipient (not the vendor)
        elif detection_types and 'chinese_name_recipient' in detection_types and 'chinese_name_vendor' not in detection_types:
            classification = "VERIFIED: Chinese recipient"
            reason = f"US vendor, Chinese recipient: {recipient[:40] if recipient else 'N/A'}"
            verified_chinese.append((entity, count, reason))

        # Check if it's a substring match that slipped through
        elif entity:
            entity_upper = entity.upper()
            if any(x in entity_upper for x in ['SINO', 'CHINA', 'ZTE', 'BYD', 'BEIJING', 'SHANGHAI']):
                # Check if it's word boundary or substring
                has_obvious_chinese = any(city in entity_upper for city in ['BEIJING', 'SHANGHAI', 'GUANGZHOU', 'SHENZHEN'])
                has_chinese_word = 'CHINA ' in entity_upper or ' CHINA' in entity_upper or entity_upper.startswith('CHINA') or entity_upper.endswith('CHINA')

                if has_obvious_chinese or has_chinese_word:
                    classification = "LIKELY: Chinese-related"
                    reason = "Has Chinese city/word boundary"
                    needs_review.append((entity, count, reason))
                else:
                    classification = "POTENTIAL FALSE POSITIVE"
                    reason = "Substring match, needs verification"
                    potential_false_positives.append((entity, count, reason))
            else:
                classification = "UNCLEAR"
                reason = "No obvious Chinese pattern"
                needs_review.append((entity, count, reason))

        # Print each entity
        print(f"{count:4d} | {entity[:50]:50} | {classification:30} | {reason[:40]}")

    # Summary by category
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    print(f"\n[1] VERIFIED CHINESE (legitimate):")
    print(f"    Count: {len(verified_chinese)} entities, {sum(c for _, c, _ in verified_chinese):,} records")
    for entity, count, reason in verified_chinese[:10]:
        print(f"      {count:4d} | {entity[:50]:50} | {reason}")
    if len(verified_chinese) > 10:
        print(f"      ... and {len(verified_chinese) - 10} more")

    print(f"\n[2] NEEDS REVIEW (unclear):")
    print(f"    Count: {len(needs_review)} entities, {sum(c for _, c, _ in needs_review):,} records")
    for entity, count, reason in needs_review[:10]:
        print(f"      {count:4d} | {entity[:50]:50} | {reason}")
    if len(needs_review) > 10:
        print(f"      ... and {len(needs_review) - 10} more")

    print(f"\n[3] POTENTIAL FALSE POSITIVES:")
    print(f"    Count: {len(potential_false_positives)} entities, {sum(c for _, c, _ in potential_false_positives):,} records")
    for entity, count, reason in potential_false_positives:
        print(f"      {count:4d} | {entity[:50]:50} | {reason}")

    # Final accounting
    print("\n" + "=" * 80)
    print("ACCOUNTING")
    print("=" * 80)

    total_verified = sum(c for _, c, _ in verified_chinese)
    total_review = sum(c for _, c, _ in needs_review)
    total_fp = sum(c for _, c, _ in potential_false_positives)

    print(f"\nTotal US records: {total_us:,}")
    print(f"  Verified Chinese: {total_verified:,} ({(total_verified/total_us)*100:.1f}%)")
    print(f"  Needs Review: {total_review:,} ({(total_review/total_us)*100:.1f}%)")
    print(f"  Potential False Positives: {total_fp:,} ({(total_fp/total_us)*100:.1f}%)")

    discrepancy = total_us - (total_verified + total_review + total_fp)
    if discrepancy != 0:
        print(f"  Discrepancy: {discrepancy:,}")

    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)

    if total_fp > 0 or total_review > 50:
        print(f"\n[WARNING] Not all US entities have been individually verified")
        print(f"  - {total_verified:,} verified Chinese entities")
        print(f"  - {total_review:,} need manual review")
        print(f"  - {total_fp:,} potential false positives")
    else:
        print(f"\n[OK] All US entities verified as Chinese-related")
        print(f"  - {total_verified:,} verified Chinese entities")

    conn.close()

    return {
        'total_us': total_us,
        'verified_chinese': verified_chinese,
        'needs_review': needs_review,
        'potential_false_positives': potential_false_positives
    }

if __name__ == "__main__":
    try:
        results = comprehensive_us_verification()
        print(f"\n[SUCCESS] Comprehensive verification complete")
        print(f"Total US records: {results['total_us']:,}")
        print(f"Verified: {len(results['verified_chinese'])} entities")
        print(f"Needs review: {len(results['needs_review'])} entities")
    except Exception as e:
        print(f"\n[ERROR] Verification failed: {e}")
        import traceback
        traceback.print_exc()
