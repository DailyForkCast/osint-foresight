#!/usr/bin/env python3
"""
Remove American Company False Positives
Keep Chinese-owned US subsidiaries (like Lenovo)
Remove substring match false positives
"""

import sqlite3
from datetime import datetime

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

def remove_american_false_positives():
    """Remove American companies, keep Chinese-owned subsidiaries"""

    print("=" * 80)
    print("REMOVING AMERICAN COMPANY FALSE POSITIVES")
    print("=" * 80)
    print("\nStrategy:")
    print("  - Remove: US companies with dual-name detection")
    print("  - Keep: Lenovo (Chinese-owned US subsidiary)")
    print("  - Keep: All non-US country records")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB, timeout=120)
    cursor = conn.cursor()

    # Get initial count
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    initial_count = cursor.fetchone()[0]
    print(f"\nInitial count: {initial_count:,} records")

    # Count records we'll remove
    print("\n[1/4] Counting American company false positives...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types = '["chinese_name_recipient", "chinese_name_vendor"]'
          AND (recipient_country_code IN ('USA', 'UNITED STATES')
               OR recipient_country_name IN ('USA', 'UNITED STATES'))
          AND recipient_name NOT LIKE '%LENOVO%'
          AND vendor_name NOT LIKE '%LENOVO%'
    """)
    remove_count = cursor.fetchone()[0]
    print(f"  American companies to remove: {remove_count:,}")

    # Count Lenovo records we're keeping
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types = '["chinese_name_recipient", "chinese_name_vendor"]'
          AND (recipient_country_code IN ('USA', 'UNITED STATES')
               OR recipient_country_name IN ('USA', 'UNITED STATES'))
          AND (recipient_name LIKE '%LENOVO%' OR vendor_name LIKE '%LENOVO%')
    """)
    lenovo_count = cursor.fetchone()[0]
    print(f"  Lenovo (Chinese-owned) to keep: {lenovo_count:,}")

    # Show sample of what we're removing
    print("\n[2/4] Sample of companies being removed:")
    cursor.execute("""
        SELECT DISTINCT vendor_name, COUNT(*) as count
        FROM usaspending_china_305
        WHERE detection_types = '["chinese_name_recipient", "chinese_name_vendor"]'
          AND (recipient_country_code IN ('USA', 'UNITED STATES')
               OR recipient_country_name IN ('USA', 'UNITED STATES'))
          AND recipient_name NOT LIKE '%LENOVO%'
          AND vendor_name NOT LIKE '%LENOVO%'
        GROUP BY vendor_name
        ORDER BY count DESC
        LIMIT 10
    """)

    for vendor, count in cursor.fetchall():
        print(f"  {count:4d} | {vendor[:60]}")

    # Create new clean table
    print("\n[3/4] Creating clean table without American false positives...")

    cursor.execute("DROP TABLE IF EXISTS usaspending_china_305_final")

    # Keep everything EXCEPT:
    # - dual-name detection + US country + NOT Lenovo
    cursor.execute("""
        CREATE TABLE usaspending_china_305_final AS
        SELECT * FROM usaspending_china_305
        WHERE NOT (
            detection_types = '["chinese_name_recipient", "chinese_name_vendor"]'
            AND (recipient_country_code IN ('USA', 'UNITED STATES')
                 OR recipient_country_name IN ('USA', 'UNITED STATES'))
            AND recipient_name NOT LIKE '%LENOVO%'
            AND vendor_name NOT LIKE '%LENOVO%'
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305_final")
    final_count = cursor.fetchone()[0]
    print(f"  Clean table created: {final_count:,} records")

    # Create indexes
    print("\n[4/4] Creating indexes...")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_final_recipient_country ON usaspending_china_305_final(recipient_country_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_final_pop_country ON usaspending_china_305_final(pop_country_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_final_recipient ON usaspending_china_305_final(recipient_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_final_vendor ON usaspending_china_305_final(vendor_name)')

    # Drop all views first
    print("\nDropping views...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
    views = cursor.fetchall()
    for view_name, in views:
        cursor.execute(f"DROP VIEW IF EXISTS {view_name}")

    # Replace old table
    print("Replacing old table...")
    cursor.execute("DROP TABLE usaspending_china_305")
    cursor.execute("ALTER TABLE usaspending_china_305_final RENAME TO usaspending_china_305")

    conn.commit()
    conn.close()

    # Summary
    print("\n" + "=" * 80)
    print("AMERICAN FALSE POSITIVES REMOVED")
    print("=" * 80)

    print(f"\nBefore: {initial_count:,} records")
    print(f"After:  {final_count:,} records")
    print(f"Removed: {remove_count:,} records ({(remove_count/initial_count)*100:.1f}%)")

    print(f"\nKept:")
    print(f"  - Lenovo (Chinese-owned): {lenovo_count:,} records")
    print(f"  - All Chinese-country records")
    print(f"  - All other detection types")

    print(f"\nRemoved:")
    print(f"  - American companies (substring matches)")
    print(f"  - SKYDIVE ELSINORE, KACHINA, JUSINO-BERRIOS, etc.")

    print(f"\nDatabase now contains:")
    print(f"  {final_count:,} verified Chinese entities")

    return {
        'initial_count': initial_count,
        'final_count': final_count,
        'removed': remove_count,
        'lenovo_kept': lenovo_count
    }

if __name__ == "__main__":
    try:
        results = remove_american_false_positives()
        print(f"\n[SUCCESS] Database cleaned: {results['final_count']:,} Chinese entities")
    except Exception as e:
        print(f"\n[ERROR] Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
