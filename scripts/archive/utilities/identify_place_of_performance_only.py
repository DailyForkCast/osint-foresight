#!/usr/bin/env python3
"""
Identify Place-of-Performance-Only Detections
Find US/EU companies manufacturing in China vs actual Chinese companies
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("analysis")

def identify_pop_only_detections():
    """Identify records detected only by place of performance in China"""

    print("=" * 80)
    print("IDENTIFYING PLACE-OF-PERFORMANCE-ONLY DETECTIONS")
    print("=" * 80)
    print("\nThese are US/EU companies manufacturing in China")
    print("NOT actual Chinese-owned entities")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB)
    cursor = conn.cursor()

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    total_count = cursor.fetchone()[0]
    print(f"\nTotal records in database: {total_count:,}")

    # Count place-of-performance-only records
    # These have pop_country_china but NO chinese_name detection
    print("\n[1/5] Counting place-of-performance-only detections...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%pop_country_china%'
          AND detection_types NOT LIKE '%chinese_name_recipient%'
          AND detection_types NOT LIKE '%chinese_name_vendor%'
    """)
    pop_only_count = cursor.fetchone()[0]

    pop_only_pct = (pop_only_count / total_count) * 100 if total_count > 0 else 0
    print(f"  Place-of-performance-only: {pop_only_count:,} records ({pop_only_pct:.2f}%)")

    # Count actual Chinese entities (with chinese_name detection)
    print("\n[2/5] Counting actual Chinese entity detections...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%chinese_name_recipient%'
           OR detection_types LIKE '%chinese_name_vendor%'
    """)
    chinese_entity_count = cursor.fetchone()[0]

    chinese_entity_pct = (chinese_entity_count / total_count) * 100 if total_count > 0 else 0
    print(f"  Actual Chinese entities: {chinese_entity_count:,} records ({chinese_entity_pct:.2f}%)")

    # Get sample of place-of-performance-only records
    print("\n[3/5] Sampling place-of-performance-only records...")
    cursor.execute("""
        SELECT
            transaction_id,
            recipient_name,
            vendor_name,
            pop_country_code,
            pop_country_name,
            award_description,
            award_amount,
            highest_confidence,
            detection_types
        FROM usaspending_china_305
        WHERE detection_types LIKE '%pop_country_china%'
          AND detection_types NOT LIKE '%chinese_name_recipient%'
          AND detection_types NOT LIKE '%chinese_name_vendor%'
        ORDER BY CAST(award_amount AS REAL) DESC
        LIMIT 50
    """)

    sample_records = []
    vendor_countries = Counter()
    recipient_countries = Counter()
    top_vendors = Counter()
    top_recipients = Counter()

    for row in cursor.fetchall():
        (transaction_id, recipient_name, vendor_name, pop_country_code,
         pop_country_name, award_description, award_amount,
         highest_confidence, detection_types) = row

        sample_records.append({
            'transaction_id': transaction_id,
            'recipient_name': recipient_name or '',
            'vendor_name': vendor_name or '',
            'pop_country_code': pop_country_code or '',
            'pop_country_name': pop_country_name or '',
            'award_description': (award_description or '')[:150],
            'award_amount': award_amount or 0,
            'highest_confidence': highest_confidence or 0,
            'detection_types': detection_types or ''
        })

        # Track vendor/recipient origins
        if vendor_name:
            top_vendors[vendor_name] += 1
        if recipient_name:
            top_recipients[recipient_name] += 1

    # Get all place-of-performance-only records for analysis
    print("\n[4/5] Analyzing vendor/recipient patterns...")
    cursor.execute("""
        SELECT recipient_name, vendor_name
        FROM usaspending_china_305
        WHERE detection_types LIKE '%pop_country_china%'
          AND detection_types NOT LIKE '%chinese_name_recipient%'
          AND detection_types NOT LIKE '%chinese_name_vendor%'
    """)

    all_pop_records = cursor.fetchall()
    all_vendors = Counter()
    all_recipients = Counter()

    for recipient, vendor in all_pop_records:
        if vendor:
            all_vendors[vendor] += 1
        if recipient:
            all_recipients[recipient] += 1

    conn.close()

    # Results summary
    print("\n[5/5] Generating analysis...")

    results = {
        'timestamp': datetime.now().isoformat(),
        'database': MAIN_DB,
        'total_records': total_count,
        'pop_only_records': pop_only_count,
        'pop_only_percentage': round(pop_only_pct, 2),
        'chinese_entity_records': chinese_entity_count,
        'chinese_entity_percentage': round(chinese_entity_pct, 2),
        'top_vendors': dict(all_vendors.most_common(20)),
        'top_recipients': dict(all_recipients.most_common(20)),
        'sample_records': sample_records[:20]
    }

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = OUTPUT_DIR / f"pop_only_analysis_{timestamp}.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "=" * 80)
    print("PLACE-OF-PERFORMANCE-ONLY ANALYSIS")
    print("=" * 80)

    print(f"\nTotal Records: {total_count:,}")
    print(f"\nBreakdown:")
    print(f"  Place-of-Performance-Only: {pop_only_count:,} ({pop_only_pct:.2f}%)")
    print(f"    - US/EU companies manufacturing in China")
    print(f"    - NOT Chinese-owned entities")
    print(f"\n  Actual Chinese Entities:   {chinese_entity_count:,} ({chinese_entity_pct:.2f}%)")
    print(f"    - Chinese-named companies")
    print(f"    - Actual PRC entities")

    print(f"\n--- TOP 10 VENDORS (Place-of-Performance-Only) ---")
    for vendor, count in all_vendors.most_common(10):
        print(f"  {count:4d} | {vendor[:70]}")

    print(f"\n--- TOP 10 RECIPIENTS (Place-of-Performance-Only) ---")
    for recipient, count in all_recipients.most_common(10):
        print(f"  {count:4d} | {recipient[:70]}")

    print(f"\n--- SAMPLE HIGH-VALUE RECORDS (Top 10 by Amount) ---")
    for i, record in enumerate(sample_records[:10], 1):
        amt = float(record['award_amount']) if record['award_amount'] else 0
        print(f"\n{i}. Transaction: {record['transaction_id']}")
        print(f"   Amount: ${amt:,.2f}")
        print(f"   Vendor: {record['vendor_name'][:60]}")
        print(f"   Recipient: {record['recipient_name'][:60]}")
        print(f"   Description: {record['award_description'][:80]}...")

    print(f"\n--- KEY INSIGHT ---")
    print(f"Place-of-performance-only records represent US/EU companies")
    print(f"doing business in China (e.g., manufacturing there).")
    print(f"\nThese are NOT Chinese companies - they are American/European")
    print(f"contractors who happen to manufacture or source from China.")
    print(f"\nExamples:")
    print(f"  - A-LINE ACCESSORIES INC (US company)")
    print(f"  - TTI INC (US electronics distributor)")
    print(f"  - OSHKOSH DEFENSE (US defense contractor)")
    print(f"\nUser Decision Needed:")
    print(f"  1. Keep in main database (monitoring China supply chain exposure)")
    print(f"  2. Separate to new database (focus only on Chinese-owned companies)")

    print(f"\nResults saved to: {results_file}")
    print("=" * 80)

    return results

if __name__ == "__main__":
    try:
        results = identify_pop_only_detections()
        print(f"\n[SUCCESS] Analysis complete")
        print(f"{results['pop_only_records']:,} place-of-performance-only records identified")
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
