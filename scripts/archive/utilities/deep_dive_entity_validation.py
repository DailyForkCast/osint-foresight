#!/usr/bin/env python3
"""
Deep Dive Entity Validation
Carefully analyze all remaining entities - why they're in, do they belong, are any unclear
"""

import sqlite3
import json
from pathlib import Path
from collections import defaultdict

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("analysis")

def deep_dive_validation():
    """Perform deep dive validation of all remaining entities"""

    print("=" * 80)
    print("DEEP DIVE ENTITY VALIDATION")
    print("=" * 80)
    print("\nAnalyzing why each record is in the database...")
    print("Checking if they belong...")
    print("Identifying unclear cases...")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB)
    cursor = conn.cursor()

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    total = cursor.fetchone()[0]
    print(f"\nTotal records to validate: {total:,}")

    # Get all detection type combinations
    cursor.execute("""
        SELECT detection_types, COUNT(*) as count
        FROM usaspending_china_305
        GROUP BY detection_types
        ORDER BY count DESC
    """)

    detection_types = cursor.fetchall()
    print(f"Detection type combinations: {len(detection_types)}")

    validation_results = {
        'total_records': total,
        'detection_types': [],
        'unclear_cases': [],
        'summary': {}
    }

    # Analyze each detection type
    for detection_type_str, count in detection_types:
        print("\n" + "=" * 80)
        detection_types_parsed = json.loads(detection_type_str)
        print(f"DETECTION TYPE: {detection_type_str}")
        print(f"Count: {count:,} records ({(count/total)*100:.1f}%)")
        print("=" * 80)

        # Get sample records
        cursor.execute("""
            SELECT
                transaction_id,
                recipient_name,
                vendor_name,
                recipient_country_code,
                pop_country_code,
                award_description
            FROM usaspending_china_305
            WHERE detection_types = ?
            LIMIT 10
        """, (detection_type_str,))

        samples = cursor.fetchall()

        # Analyze why these are detected
        print("\nWHY DETECTED:")
        detection_reasons = []

        if "chinese_name_recipient" in detection_types_parsed:
            detection_reasons.append("  - Recipient name contains Chinese patterns")
        if "chinese_name_vendor" in detection_types_parsed:
            detection_reasons.append("  - Vendor name contains Chinese patterns")
        if "recipient_country_china" in detection_types_parsed:
            detection_reasons.append("  - Recipient country is China")
        if "pop_country_china" in detection_types_parsed:
            detection_reasons.append("  - Place of performance is China")

        for reason in detection_reasons:
            print(reason)

        # Show samples
        print("\nSAMPLE RECORDS (first 5):")
        unclear_samples = []

        for i, sample in enumerate(samples[:5], 1):
            (tid, recipient, vendor, recipient_country, pop_country, description) = sample

            print(f"\n  Sample {i}:")
            print(f"    Transaction: {tid}")
            print(f"    Recipient: {recipient[:60] if recipient else 'N/A'}")
            print(f"    Vendor: {vendor[:60] if vendor else 'N/A'}")
            if recipient_country:
                print(f"    Recipient Country: {recipient_country}")
            if pop_country:
                print(f"    PoP Country: {pop_country}")
            print(f"    Description: {description[:80] if description else 'N/A'}...")

            # Determine if this is CLEAR or UNCLEAR
            is_clear = check_if_clear(recipient, vendor, recipient_country, pop_country, detection_types_parsed)
            clarity = "CLEAR" if is_clear else "UNCLEAR"
            print(f"    Clarity: {clarity}")

            if not is_clear:
                unclear_samples.append({
                    'transaction_id': tid,
                    'recipient': recipient,
                    'vendor': vendor,
                    'reason': f"Detection type: {detection_type_str}",
                    'needs_review': True
                })

        # Validation assessment
        print("\nVALIDATION ASSESSMENT:")
        validation = assess_detection_type(detection_types_parsed, samples)
        print(f"  Confidence: {validation['confidence']}")
        print(f"  Belongs: {validation['belongs']}")
        print(f"  Notes: {validation['notes']}")

        validation_results['detection_types'].append({
            'detection_type': detection_type_str,
            'count': count,
            'percentage': round((count/total)*100, 1),
            'validation': validation,
            'unclear_count': len(unclear_samples)
        })

        validation_results['unclear_cases'].extend(unclear_samples)

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    total_unclear = len(validation_results['unclear_cases'])
    print(f"\nTotal records: {total:,}")
    print(f"Unclear cases: {total_unclear:,} ({(total_unclear/total)*100:.1f}%)")

    # Count by confidence level
    high_confidence = sum(1 for dt in validation_results['detection_types'] if dt['validation']['confidence'] == 'HIGH')
    medium_confidence = sum(1 for dt in validation_results['detection_types'] if dt['validation']['confidence'] == 'MEDIUM')
    low_confidence = sum(1 for dt in validation_results['detection_types'] if dt['validation']['confidence'] == 'LOW')

    print(f"\nDetection type confidence:")
    print(f"  HIGH confidence: {high_confidence} types")
    print(f"  MEDIUM confidence: {medium_confidence} types")
    print(f"  LOW confidence: {low_confidence} types")

    # Top unclear patterns
    if validation_results['unclear_cases']:
        print(f"\nTop unclear patterns:")
        unclear_vendors = defaultdict(int)
        unclear_recipients = defaultdict(int)

        for case in validation_results['unclear_cases'][:50]:
            if case['vendor']:
                unclear_vendors[case['vendor'][:60]] += 1
            if case['recipient']:
                unclear_recipients[case['recipient'][:60]] += 1

        print("\n  Unclear vendors (top 5):")
        for vendor, count in sorted(unclear_vendors.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {count:3d} | {vendor}")

        print("\n  Unclear recipients (top 5):")
        for recipient, count in sorted(unclear_recipients.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {count:3d} | {recipient}")

    # Save results
    results_file = OUTPUT_DIR / f"deep_dive_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2, ensure_ascii=False)

    print(f"\nDetailed results saved to: {results_file}")

    conn.close()

    return validation_results

def check_if_clear(recipient, vendor, recipient_country, pop_country, detection_types):
    """Check if a record is clearly a Chinese entity"""

    # If recipient country is China, it's clear
    if recipient_country and recipient_country.upper() in ['CHN', 'CHINA']:
        return True

    # If both recipient and vendor have Chinese names, it's clear
    if "chinese_name_recipient" in detection_types and "chinese_name_vendor" in detection_types:
        # Check if names have obvious Chinese indicators
        if recipient and vendor:
            obvious_indicators = ['BEIJING', 'SHANGHAI', 'GUANGZHOU', 'SHENZHEN', 'CHINA', 'CHINESE', 'LENOVO', 'HUAWEI', 'ZTE']
            recipient_upper = recipient.upper()
            vendor_upper = vendor.upper()

            if any(indicator in recipient_upper or indicator in vendor_upper for indicator in obvious_indicators):
                return True

    # If only name detection and no country confirmation, might be unclear
    if detection_types == ["chinese_name_recipient"] or detection_types == ["chinese_name_vendor"]:
        return False

    # Default: if has country confirmation or both name detections, consider clear
    if "recipient_country_china" in detection_types:
        return True

    if len(detection_types) >= 2:
        return True

    return False

def assess_detection_type(detection_types, samples):
    """Assess the validity of a detection type combination"""

    # HIGH confidence: Has country code confirmation
    if "recipient_country_china" in detection_types:
        return {
            'confidence': 'HIGH',
            'belongs': 'YES',
            'notes': 'Recipient country code confirms Chinese entity'
        }

    # HIGH confidence: Both name detections (recipient AND vendor)
    if "chinese_name_recipient" in detection_types and "chinese_name_vendor" in detection_types:
        return {
            'confidence': 'HIGH',
            'belongs': 'YES',
            'notes': 'Both recipient and vendor have Chinese name patterns'
        }

    # MEDIUM confidence: Place of performance + name
    if "pop_country_china" in detection_types and ("chinese_name_recipient" in detection_types or "chinese_name_vendor" in detection_types):
        return {
            'confidence': 'MEDIUM',
            'belongs': 'LIKELY',
            'notes': 'Chinese name pattern + China place of performance'
        }

    # LOW confidence: Name only (single detection)
    if detection_types == ["chinese_name_recipient"] or detection_types == ["chinese_name_vendor"]:
        return {
            'confidence': 'LOW',
            'belongs': 'NEEDS REVIEW',
            'notes': 'Name pattern only - may include false positives'
        }

    # MEDIUM confidence: Other combinations
    return {
        'confidence': 'MEDIUM',
        'belongs': 'LIKELY',
        'notes': 'Multiple detection signals'
    }

if __name__ == "__main__":
    try:
        from datetime import datetime
        results = deep_dive_validation()
        print(f"\n[SUCCESS] Deep dive validation complete")
        print(f"Total records: {results['total_records']:,}")
        print(f"Unclear cases: {len(results['unclear_cases']):,}")
    except Exception as e:
        print(f"\n[ERROR] Validation failed: {e}")
        import traceback
        traceback.print_exc()
