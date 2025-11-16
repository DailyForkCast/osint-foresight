#!/usr/bin/env python3
"""
Identify False Positives in USAspending Chinese Entity Detection Database
Based on patterns identified in manual review
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("analysis")

def identify_false_positives():
    """
    Scan database for false positive patterns identified in manual review
    """

    print("=" * 80)
    print("FALSE POSITIVE IDENTIFICATION - USASPENDING CHINESE ENTITY DETECTION")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get total record count
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    total_records = cursor.fetchone()[0]
    print(f"\nTotal records in database: {total_records:,}")

    false_positive_categories = defaultdict(list)
    false_positive_counts = defaultdict(int)

    # Category 1: Homer Laughlin China Company (American ceramics manufacturer)
    print("\n[1/5] Scanning for Homer Laughlin China Company (American ceramics)...")
    cursor.execute("""
        SELECT
            transaction_id,
            recipient_name,
            vendor_name,
            award_description,
            award_amount,
            detection_types
        FROM usaspending_china_305
        WHERE recipient_name LIKE '%HOMER LAUGHLIN%'
           OR vendor_name LIKE '%HOMER LAUGHLIN%'
    """)

    homer_laughlin_records = cursor.fetchall()
    false_positive_counts['homer_laughlin'] = len(homer_laughlin_records)
    print(f"  Found: {len(homer_laughlin_records)} records")

    if homer_laughlin_records:
        false_positive_categories['homer_laughlin'] = [
            {
                'transaction_id': r[0],
                'recipient_name': r[1],
                'vendor_name': r[2],
                'award_description': r[3][:100] if r[3] else "",
                'award_amount': r[4],
                'detection_types': r[5],
                'reason': 'American ceramics manufacturer - "China" refers to porcelain, not country'
            }
            for r in homer_laughlin_records[:10]  # Sample first 10
        ]

    # Category 2: Aztec companies (substring match with ZTE)
    print("\n[2/5] Scanning for Aztec companies (substring false positive)...")
    cursor.execute("""
        SELECT
            transaction_id,
            recipient_name,
            vendor_name,
            award_description,
            award_amount,
            detection_types
        FROM usaspending_china_305
        WHERE (recipient_name LIKE '%AZTEC%' OR vendor_name LIKE '%AZTEC%')
          AND recipient_name NOT LIKE '%ZTE %'
          AND vendor_name NOT LIKE '%ZTE %'
    """)

    aztec_records = cursor.fetchall()
    false_positive_counts['aztec'] = len(aztec_records)
    print(f"  Found: {len(aztec_records)} records")

    if aztec_records:
        false_positive_categories['aztec'] = [
            {
                'transaction_id': r[0],
                'recipient_name': r[1],
                'vendor_name': r[2],
                'award_description': r[3][:100] if r[3] else "",
                'award_amount': r[4],
                'detection_types': r[5],
                'reason': 'American company - AZTEC substring matches ZTE pattern'
            }
            for r in aztec_records[:10]
        ]

    # Category 3: Generic "China Company" ceramics/porcelain manufacturers
    print("\n[3/5] Scanning for 'China Company' ceramics manufacturers...")
    cursor.execute("""
        SELECT
            transaction_id,
            recipient_name,
            vendor_name,
            award_description,
            award_amount,
            detection_types,
            pop_country_code
        FROM usaspending_china_305
        WHERE (recipient_name LIKE '%CHINA COMPANY%' OR vendor_name LIKE '%CHINA COMPANY%')
          AND pop_country_code = 'USA'
          AND (award_description LIKE '%PLATE%'
               OR award_description LIKE '%BOWL%'
               OR award_description LIKE '%CUP%'
               OR award_description LIKE '%DINNER%'
               OR award_description LIKE '%TABLEWARE%'
               OR award_description LIKE '%CERAMIC%'
               OR award_description LIKE '%PORCELAIN%')
    """)

    china_company_records = cursor.fetchall()
    false_positive_counts['china_company_ceramics'] = len(china_company_records)
    print(f"  Found: {len(china_company_records)} records")

    if china_company_records:
        false_positive_categories['china_company_ceramics'] = [
            {
                'transaction_id': r[0],
                'recipient_name': r[1],
                'vendor_name': r[2],
                'award_description': r[3][:100] if r[3] else "",
                'award_amount': r[4],
                'detection_types': r[5],
                'pop_country_code': r[6],
                'reason': 'US ceramics/porcelain company - "China" refers to material, not country'
            }
            for r in china_company_records[:10]
        ]

    # Category 4: Other substring matches (contains ZTE, DJI, etc. as substring)
    print("\n[4/5] Scanning for other substring false positives...")

    # Check for words containing "ZTE" but not actually ZTE
    cursor.execute("""
        SELECT
            transaction_id,
            recipient_name,
            vendor_name,
            award_description,
            award_amount,
            detection_types
        FROM usaspending_china_305
        WHERE (recipient_name LIKE '%ZTE%' OR vendor_name LIKE '%ZTE%')
          AND recipient_name NOT LIKE '% ZTE %'
          AND recipient_name NOT LIKE 'ZTE %'
          AND recipient_name NOT LIKE '% ZTE'
          AND vendor_name NOT LIKE '% ZTE %'
          AND vendor_name NOT LIKE 'ZTE %'
          AND vendor_name NOT LIKE '% ZTE'
        LIMIT 100
    """)

    zte_substring_records = cursor.fetchall()
    false_positive_counts['zte_substring'] = len(zte_substring_records)
    print(f"  Found: {len(zte_substring_records)} potential records (checking first 100)")

    if zte_substring_records:
        # Filter out records where ZTE appears as part of another word
        filtered_zte = []
        for r in zte_substring_records[:20]:
            recipient = r[1] or ""
            vendor = r[2] or ""
            # Check if ZTE appears in suspicious contexts
            if any(pattern in recipient.upper() or pattern in vendor.upper()
                   for pattern in ['AZTEC', 'GAZETTE', 'QUARTZER', 'PRIVATEER']):
                filtered_zte.append({
                    'transaction_id': r[0],
                    'recipient_name': r[1],
                    'vendor_name': r[2],
                    'award_description': r[3][:100] if r[3] else "",
                    'award_amount': r[4],
                    'detection_types': r[5],
                    'reason': 'ZTE appears as substring in unrelated company name'
                })

        false_positive_categories['zte_substring'] = filtered_zte
        false_positive_counts['zte_substring'] = len(filtered_zte)

    # Category 5: Place of performance detection only (US/European companies working in China)
    print("\n[5/5] Scanning for place-of-performance-only detections...")
    cursor.execute("""
        SELECT
            transaction_id,
            recipient_name,
            vendor_name,
            award_description,
            award_amount,
            detection_types,
            pop_country_code
        FROM usaspending_china_305
        WHERE detection_types LIKE '%pop_country_china%'
          AND detection_types NOT LIKE '%chinese_name%'
          AND detection_types NOT LIKE '%recipient_country%'
          AND (vendor_name LIKE '%AVAYA%'
               OR vendor_name LIKE '%CISCO%'
               OR vendor_name LIKE '%DELL%'
               OR vendor_name LIKE '%HP%'
               OR vendor_name LIKE '%IBM%')
        LIMIT 50
    """)

    pop_only_records = cursor.fetchall()
    false_positive_counts['pop_only_western_vendors'] = len(pop_only_records)
    print(f"  Found: {len(pop_only_records)} records (US/EU tech companies)")

    if pop_only_records:
        false_positive_categories['pop_only_western_vendors'] = [
            {
                'transaction_id': r[0],
                'recipient_name': r[1],
                'vendor_name': r[2],
                'award_description': r[3][:100] if r[3] else "",
                'award_amount': r[4],
                'detection_types': r[5],
                'pop_country_code': r[6],
                'reason': 'US/European company working in China - vendor is not Chinese'
            }
            for r in pop_only_records[:10]
        ]

    conn.close()

    # Calculate totals
    total_definite_fps = (
        false_positive_counts['homer_laughlin'] +
        false_positive_counts['aztec'] +
        false_positive_counts['china_company_ceramics'] +
        false_positive_counts['zte_substring']
    )

    total_policy_question = false_positive_counts['pop_only_western_vendors']

    # Generate report
    print("\n" + "=" * 80)
    print("FALSE POSITIVE SUMMARY")
    print("=" * 80)

    print(f"\nTotal Records in Database: {total_records:,}")
    print(f"\nDEFINITE False Positives: {total_definite_fps:,}")
    print(f"  - Homer Laughlin (ceramics): {false_positive_counts['homer_laughlin']:,}")
    print(f"  - Aztec companies (substring): {false_positive_counts['aztec']:,}")
    print(f"  - China Company ceramics: {false_positive_counts['china_company_ceramics']:,}")
    print(f"  - ZTE substring matches: {false_positive_counts['zte_substring']:,}")

    print(f"\nPOLICY QUESTION Records: {total_policy_question:,}")
    print(f"  - US/EU vendors, place of performance China: {false_positive_counts['pop_only_western_vendors']:,}")

    fp_percentage = (total_definite_fps / total_records) * 100
    print(f"\nEstimated False Positive Rate: {fp_percentage:.2f}%")

    # Write detailed report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"false_positive_identification_{timestamp}.json"

    report = {
        'timestamp': datetime.now().isoformat(),
        'database_path': DB_PATH,
        'total_records': total_records,
        'summary': {
            'total_definite_false_positives': total_definite_fps,
            'total_policy_question_records': total_policy_question,
            'false_positive_percentage': round(fp_percentage, 2)
        },
        'counts_by_category': dict(false_positive_counts),
        'sample_records_by_category': dict(false_positive_categories)
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nDetailed report written to: {output_file}")

    # Show examples
    print("\n" + "=" * 80)
    print("EXAMPLE FALSE POSITIVES")
    print("=" * 80)

    for category, records in false_positive_categories.items():
        if records:
            print(f"\n{category.upper().replace('_', ' ')}:")
            for i, record in enumerate(records[:3], 1):
                print(f"\n  {i}. Transaction: {record['transaction_id']}")
                print(f"     Vendor: {record['vendor_name']}")
                print(f"     Description: {record['award_description']}")
                print(f"     Amount: ${record['award_amount']}")
                print(f"     Reason: {record['reason']}")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("\n1. IMMEDIATE CLEANUP ACTIONS:")
    print(f"   - Remove {false_positive_counts['homer_laughlin']:,} Homer Laughlin records (American ceramics)")
    print(f"   - Remove {false_positive_counts['aztec']:,} Aztec company records (substring match)")
    print(f"   - Review {false_positive_counts['china_company_ceramics']:,} 'China Company' ceramics records")

    print("\n2. DETECTION PATTERN IMPROVEMENTS:")
    print("   - Add word boundary matching for ZTE, DJI, etc.")
    print("   - Exclude 'CHINA COMPANY' when context is ceramics/porcelain/tableware")
    print("   - Add false positive exclusion list")

    print("\n3. POLICY DECISIONS NEEDED:")
    print(f"   - Should place-of-performance-only trigger detection?")
    print(f"     (Currently {total_policy_question:,} records from US/EU vendors working in China)")

    print("\n4. ESTIMATED DATABASE CLEANUP:")
    print(f"   - Before: {total_records:,} records")
    print(f"   - After:  {total_records - total_definite_fps:,} records")
    print(f"   - Removed: {total_definite_fps:,} false positives ({fp_percentage:.2f}%)")

    return report

if __name__ == "__main__":
    try:
        report = identify_false_positives()
        print("\n" + "=" * 80)
        print("[SUCCESS] False positive identification complete")
        print("=" * 80)
    except Exception as e:
        print(f"\n[ERROR] Failed to identify false positives: {e}")
        import traceback
        traceback.print_exc()
