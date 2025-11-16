#!/usr/bin/env python3
"""
Verify Final Database Composition
Ensure main database contains only Chinese entities
"""

import sqlite3
from collections import Counter

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
SUPPLY_CHAIN_DB = "F:/OSINT_WAREHOUSE/osint_china_supply_chain.db"

def verify_databases():
    """Verify composition of both databases"""

    print("=" * 80)
    print("FINAL DATABASE COMPOSITION VERIFICATION")
    print("=" * 80)

    # Main database
    print("\n[1/2] MAIN DATABASE (Chinese Entities)")
    print("-" * 80)
    main_conn = sqlite3.connect(MAIN_DB)
    main_cursor = main_conn.cursor()

    # Total count
    main_cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    main_total = main_cursor.fetchone()[0]
    print(f"Total Records: {main_total:,}")

    # Detection types breakdown
    print("\nDetection Types:")

    # Chinese name recipient
    main_cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%chinese_name_recipient%'
    """)
    chinese_recipient = main_cursor.fetchone()[0]
    print(f"  Chinese name recipient: {chinese_recipient:,}")

    # Chinese name vendor
    main_cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%chinese_name_vendor%'
    """)
    chinese_vendor = main_cursor.fetchone()[0]
    print(f"  Chinese name vendor: {chinese_vendor:,}")

    # Both
    main_cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%chinese_name_recipient%'
          AND detection_types LIKE '%chinese_name_vendor%'
    """)
    both_chinese = main_cursor.fetchone()[0]
    print(f"  Both Chinese names: {both_chinese:,}")

    # Pop country china (should also have chinese_name)
    main_cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%pop_country_china%'
    """)
    pop_china = main_cursor.fetchone()[0]
    print(f"  Also has pop_country_china: {pop_china:,}")

    # Verify NO place-of-performance-only records
    main_cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types LIKE '%pop_country_china%'
          AND detection_types NOT LIKE '%chinese_name_recipient%'
          AND detection_types NOT LIKE '%chinese_name_vendor%'
    """)
    pop_only = main_cursor.fetchone()[0]

    if pop_only == 0:
        print(f"\n  [OK] Zero place-of-performance-only records (verification passed)")
    else:
        print(f"\n  [WARNING] Found {pop_only:,} place-of-performance-only records!")

    # Sample of vendors
    print("\nTop 10 Vendors (should be Chinese companies):")
    main_cursor.execute("""
        SELECT vendor_name, COUNT(*) as count
        FROM usaspending_china_305
        WHERE vendor_name IS NOT NULL AND vendor_name != ''
        GROUP BY vendor_name
        ORDER BY count DESC
        LIMIT 10
    """)
    for vendor, count in main_cursor.fetchall():
        print(f"  {count:4d} | {vendor[:70]}")

    # Sample of recipients
    print("\nTop 10 Recipients:")
    main_cursor.execute("""
        SELECT recipient_name, COUNT(*) as count
        FROM usaspending_china_305
        WHERE recipient_name IS NOT NULL AND recipient_name != ''
        GROUP BY recipient_name
        ORDER BY count DESC
        LIMIT 10
    """)
    for recipient, count in main_cursor.fetchall():
        print(f"  {count:4d} | {recipient[:70]}")

    main_conn.close()

    # Supply chain database
    print("\n" + "=" * 80)
    print("[2/2] SUPPLY CHAIN DATABASE (US/EU Companies)")
    print("-" * 80)
    supply_conn = sqlite3.connect(SUPPLY_CHAIN_DB)
    supply_cursor = supply_conn.cursor()

    # Total count
    supply_cursor.execute("SELECT COUNT(*) FROM usaspending_china_supply_chain")
    supply_total = supply_cursor.fetchone()[0]
    print(f"Total Records: {supply_total:,}")

    # Verify all are place-of-performance-only
    supply_cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_supply_chain
        WHERE detection_types LIKE '%pop_country_china%'
    """)
    all_pop = supply_cursor.fetchone()[0]
    print(f"  All have pop_country_china: {all_pop:,}")

    supply_cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_supply_chain
        WHERE detection_types LIKE '%chinese_name_recipient%'
           OR detection_types LIKE '%chinese_name_vendor%'
    """)
    chinese_names = supply_cursor.fetchone()[0]

    if chinese_names == 0:
        print(f"  [OK] Zero Chinese name detections (verification passed)")
    else:
        print(f"  [WARNING] Found {chinese_names:,} Chinese name detections!")

    # Top vendors
    print("\nTop 10 Vendors (should be US/EU companies):")
    supply_cursor.execute("""
        SELECT vendor_name, COUNT(*) as count
        FROM usaspending_china_supply_chain
        WHERE vendor_name IS NOT NULL AND vendor_name != ''
        GROUP BY vendor_name
        ORDER BY count DESC
        LIMIT 10
    """)
    for vendor, count in supply_cursor.fetchall():
        print(f"  {count:4d} | {vendor[:70]}")

    supply_conn.close()

    # Final summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    total_records = main_total + supply_total
    print(f"\nTotal Original Records: {total_records:,}")
    print(f"\nFinal Distribution:")
    print(f"  Main DB (Chinese entities):     {main_total:,} ({(main_total/total_records)*100:.1f}%)")
    print(f"  Supply Chain DB (US/EU):        {supply_total:,} ({(supply_total/total_records)*100:.1f}%)")

    if pop_only == 0 and chinese_names == 0:
        print(f"\n[SUCCESS] Databases properly separated")
        print(f"  - Main DB: Chinese entities only")
        print(f"  - Supply Chain DB: US/EU companies only")
        verification_status = "PASSED"
    else:
        print(f"\n[WARNING] Verification issues detected")
        if pop_only > 0:
            print(f"  - Main DB has {pop_only:,} place-of-performance-only records")
        if chinese_names > 0:
            print(f"  - Supply Chain DB has {chinese_names:,} Chinese name records")
        verification_status = "FAILED"

    print("\n" + "=" * 80)
    print(f"Verification Status: {verification_status}")
    print("=" * 80)

    return {
        'main_total': main_total,
        'supply_total': supply_total,
        'pop_only_in_main': pop_only,
        'chinese_names_in_supply': chinese_names,
        'verification_status': verification_status
    }

if __name__ == "__main__":
    try:
        results = verify_databases()
        if results['verification_status'] == 'PASSED':
            print(f"\n[SUCCESS] Database separation verified")
        else:
            print(f"\n[WARNING] Verification found issues - review output above")
    except Exception as e:
        print(f"\n[ERROR] Verification failed: {e}")
        import traceback
        traceback.print_exc()
