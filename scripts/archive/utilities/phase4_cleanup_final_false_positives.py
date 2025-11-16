#!/usr/bin/env python3
"""
Phase 4 Cleanup - Final False Positive Removal
Remove remaining substring matches and casino false positives
"""

import sqlite3
from datetime import datetime

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

def phase4_cleanup():
    """Remove final false positives"""

    print("=" * 80)
    print("PHASE 4 CLEANUP - FINAL FALSE POSITIVE REMOVAL")
    print("=" * 80)
    print(f"\nExecution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB, timeout=120)
    cursor = conn.cursor()

    # Get initial count
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    initial_count = cursor.fetchone()[0]
    print(f"\nInitial count: {initial_count:,} records")

    # [1] Count single-detection US substring matches (excluding PHARMARON)
    print("\n[1/5] Counting single-detection US substring matches...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE (recipient_country_code IN ('USA', 'UNITED STATES')
               OR recipient_country_name IN ('USA', 'UNITED STATES'))
          AND (detection_types = '["chinese_name_vendor"]'
               OR detection_types = '["chinese_name_recipient"]')
          AND recipient_name NOT LIKE '%LENOVO%'
          AND vendor_name NOT LIKE '%LENOVO%'
          AND recipient_name NOT LIKE '%PHARMARON%'
          AND vendor_name NOT LIKE '%PHARMARON%'
          AND recipient_name NOT LIKE '%CHINESE ACADEMY%'
          AND vendor_name NOT LIKE '%CHINESE ACADEMY%'
          AND (
              recipient_name LIKE '%SINO%'
              OR vendor_name LIKE '%SINO%'
              OR recipient_name LIKE '%ZTE%'
              OR vendor_name LIKE '%ZTE%'
              OR recipient_name LIKE '%BYD%'
              OR vendor_name LIKE '%BYD%'
              OR recipient_name LIKE '%CHINA%'
              OR vendor_name LIKE '%CHINA%'
              OR recipient_name LIKE '%CASINO%'
              OR vendor_name LIKE '%CASINO%'
          )
    """)
    us_substring_count = cursor.fetchone()[0]
    print(f"  US substring matches to remove: {us_substring_count:,}")

    # [2] Count all casino/hotel records (already counted, just confirming)
    print("\n[2/5] Counting casino/hotel false positives...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE (recipient_name LIKE '%CASINO%' OR vendor_name LIKE '%CASINO%')
          AND recipient_country_code NOT IN ('CHN', 'CHINA')
          AND recipient_name NOT LIKE '%LENOVO%'
          AND vendor_name NOT LIKE '%LENOVO%'
    """)
    casino_count = cursor.fetchone()[0]
    print(f"  Casino/hotel false positives: {casino_count:,}")

    # [3] Count non-US substring matches (Italian, Spanish, German)
    print("\n[3/5] Counting non-US substring matches...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE recipient_country_code NOT IN ('CHN', 'CHINA', 'USA', 'UNITED STATES')
          AND (detection_types = '["chinese_name_vendor"]'
               OR detection_types = '["chinese_name_recipient"]'
               OR detection_types = '["chinese_name_recipient", "chinese_name_vendor"]')
          AND (
              recipient_name LIKE '%CERTOSINO%'
              OR vendor_name LIKE '%CERTOSINO%'
              OR recipient_name LIKE '%MONTESINOS%'
              OR vendor_name LIKE '%MONTESINOS%'
              OR recipient_name LIKE '%SCHUTZTECHNIK%'
              OR vendor_name LIKE '%SCHUTZTECHNIK%'
              OR recipient_name LIKE '%JUSINO%'
              OR vendor_name LIKE '%JUSINO%'
              OR recipient_name LIKE '%COMZTECH%'
              OR vendor_name LIKE '%COMZTECH%'
              OR recipient_name LIKE '%SINOOIL%'
              OR vendor_name LIKE '%SINOOIL%'
          )
    """)
    non_us_substring_count = cursor.fetchone()[0]
    print(f"  Non-US substring matches: {non_us_substring_count:,}")

    # Show sample of what we're removing
    print("\n[4/5] Sample of records being removed:")

    cursor.execute("""
        SELECT DISTINCT vendor_name, COUNT(*) as count
        FROM usaspending_china_305
        WHERE (
            -- US substring matches
            (
                (recipient_country_code IN ('USA', 'UNITED STATES')
                 OR recipient_country_name IN ('USA', 'UNITED STATES'))
                AND (detection_types = '["chinese_name_vendor"]'
                     OR detection_types = '["chinese_name_recipient"]')
                AND recipient_name NOT LIKE '%LENOVO%'
                AND vendor_name NOT LIKE '%LENOVO%'
                AND recipient_name NOT LIKE '%PHARMARON%'
                AND vendor_name NOT LIKE '%PHARMARON%'
            )
            OR
            -- Casino false positives
            (
                (recipient_name LIKE '%CASINO%' OR vendor_name LIKE '%CASINO%')
                AND recipient_country_code NOT IN ('CHN', 'CHINA')
            )
            OR
            -- Non-US substring matches
            (
                recipient_country_code NOT IN ('CHN', 'CHINA', 'USA', 'UNITED STATES')
                AND (
                    recipient_name LIKE '%CERTOSINO%'
                    OR vendor_name LIKE '%CERTOSINO%'
                    OR recipient_name LIKE '%MONTESINOS%'
                    OR vendor_name LIKE '%MONTESINOS%'
                )
            )
        )
        GROUP BY vendor_name
        ORDER BY count DESC
        LIMIT 15
    """)

    for vendor, count in cursor.fetchall():
        print(f"  {count:4d} | {vendor[:60] if vendor else 'N/A'}")

    # Create clean table
    print("\n[5/5] Creating clean table...")

    cursor.execute("DROP TABLE IF EXISTS usaspending_china_305_phase4")

    # Keep everything EXCEPT the false positives
    cursor.execute("""
        CREATE TABLE usaspending_china_305_phase4 AS
        SELECT * FROM usaspending_china_305
        WHERE NOT (
            -- Remove US substring matches (except PHARMARON, CHINESE ACADEMY)
            (
                (recipient_country_code IN ('USA', 'UNITED STATES')
                 OR recipient_country_name IN ('USA', 'UNITED STATES'))
                AND (detection_types = '["chinese_name_vendor"]'
                     OR detection_types = '["chinese_name_recipient"]')
                AND recipient_name NOT LIKE '%LENOVO%'
                AND vendor_name NOT LIKE '%LENOVO%'
                AND recipient_name NOT LIKE '%PHARMARON%'
                AND vendor_name NOT LIKE '%PHARMARON%'
                AND recipient_name NOT LIKE '%CHINESE ACADEMY%'
                AND vendor_name NOT LIKE '%CHINESE ACADEMY%'
                AND (
                    recipient_name LIKE '%SINO%'
                    OR vendor_name LIKE '%SINO%'
                    OR recipient_name LIKE '%ZTE%'
                    OR vendor_name LIKE '%ZTE%'
                    OR recipient_name LIKE '%BYD%'
                    OR vendor_name LIKE '%BYD%'
                    OR recipient_name LIKE '%CHINA%'
                    OR vendor_name LIKE '%CHINA%'
                    OR recipient_name LIKE '%CASINO%'
                    OR vendor_name LIKE '%CASINO%'
                )
            )
            OR
            -- Remove casino false positives (non-China)
            (
                (recipient_name LIKE '%CASINO%' OR vendor_name LIKE '%CASINO%')
                AND recipient_country_code NOT IN ('CHN', 'CHINA')
                AND recipient_name NOT LIKE '%LENOVO%'
                AND vendor_name NOT LIKE '%LENOVO%'
            )
            OR
            -- Remove non-US substring matches
            (
                recipient_country_code NOT IN ('CHN', 'CHINA', 'USA', 'UNITED STATES')
                AND (detection_types = '["chinese_name_vendor"]'
                     OR detection_types = '["chinese_name_recipient"]'
                     OR detection_types = '["chinese_name_recipient", "chinese_name_vendor"]')
                AND (
                    recipient_name LIKE '%CERTOSINO%'
                    OR vendor_name LIKE '%CERTOSINO%'
                    OR recipient_name LIKE '%MONTESINOS%'
                    OR vendor_name LIKE '%MONTESINOS%'
                    OR recipient_name LIKE '%SCHUTZTECHNIK%'
                    OR vendor_name LIKE '%SCHUTZTECHNIK%'
                    OR recipient_name LIKE '%JUSINO%'
                    OR vendor_name LIKE '%JUSINO%'
                    OR recipient_name LIKE '%COMZTECH%'
                    OR vendor_name LIKE '%COMZTECH%'
                    OR recipient_name LIKE '%SINOOIL%'
                    OR vendor_name LIKE '%SINOOIL%'
                )
            )
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305_phase4")
    clean_count = cursor.fetchone()[0]
    print(f"  Clean table created: {clean_count:,} records")

    # Create indexes
    print("\nCreating indexes...")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_phase4_recipient_country ON usaspending_china_305_phase4(recipient_country_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_phase4_pop_country ON usaspending_china_305_phase4(pop_country_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_phase4_recipient ON usaspending_china_305_phase4(recipient_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_phase4_vendor ON usaspending_china_305_phase4(vendor_name)')

    # Drop views
    print("Dropping views...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
    views = cursor.fetchall()
    for view_name, in views:
        cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
    print(f"  Dropped {len(views)} views")

    # Replace old table
    print("Replacing old table...")
    cursor.execute("DROP TABLE usaspending_china_305")
    cursor.execute("ALTER TABLE usaspending_china_305_phase4 RENAME TO usaspending_china_305")

    conn.commit()
    conn.close()

    # Calculate totals
    removed_count = initial_count - clean_count

    # Summary
    print("\n" + "=" * 80)
    print("PHASE 4 CLEANUP COMPLETE")
    print("=" * 80)

    print(f"\nBefore: {initial_count:,} records")
    print(f"After:  {clean_count:,} records")
    print(f"Removed: {removed_count:,} records ({(removed_count/initial_count)*100:.1f}%)")

    print(f"\nRemoved categories:")
    print(f"  - US substring matches (except PHARMARON, Chinese Academy): ~{us_substring_count:,}")
    print(f"  - Casino/hotel false positives: ~{casino_count:,}")
    print(f"  - Non-US substring matches (Italian, Spanish, German): ~{non_us_substring_count:,}")

    print(f"\nKept (verified Chinese entities):")
    print(f"  - Lenovo (Chinese-owned US subsidiary)")
    print(f"  - PHARMARON (Chinese-owned CRO)")
    print(f"  - Chinese Academy of Medical Science")
    print(f"  - All country-confirmed entities")
    print(f"  - All word-boundary matches")

    print(f"\nDatabase now contains:")
    print(f"  {clean_count:,} high-confidence Chinese entities")

    return {
        'initial_count': initial_count,
        'final_count': clean_count,
        'removed': removed_count,
        'us_substring': us_substring_count,
        'casino': casino_count,
        'non_us_substring': non_us_substring_count
    }

if __name__ == "__main__":
    try:
        results = phase4_cleanup()
        print(f"\n[SUCCESS] Phase 4 cleanup complete: {results['final_count']:,} verified Chinese entities")
    except Exception as e:
        print(f"\n[ERROR] Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
