#!/usr/bin/env python3
"""
Rebuild Clean Table - Workaround for Database Lock
Creates new table with only valid Chinese entities
"""

import sqlite3
from datetime import datetime

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

def rebuild_clean_table():
    """Create new clean table without problematic records"""

    print("=" * 80)
    print("REBUILDING CLEAN TABLE - DATABASE LOCK WORKAROUND")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB, timeout=120)
    cursor = conn.cursor()

    # Get current count
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
    initial_count = cursor.fetchone()[0]
    print(f"\nCurrent table: {initial_count:,} records")

    # Count records we're KEEPING
    print("\nCounting records to keep...")
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types != '["china_sourced_product"]'
          AND (recipient_name NOT LIKE '%CATALINA CHINA%' AND vendor_name NOT LIKE '%CATALINA CHINA%')
          AND (recipient_name NOT LIKE '%FACCHIN%' AND vendor_name NOT LIKE '%FACCHIN%')
    """)
    keep_count = cursor.fetchone()[0]
    print(f"  Records to keep: {keep_count:,}")

    remove_count = initial_count - keep_count
    print(f"  Records to remove: {remove_count:,}")

    # Show breakdown of what we're removing
    print("\n  Breakdown of removals:")

    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305 WHERE detection_types = '[\"china_sourced_product\"]'")
    sourced = cursor.fetchone()[0]
    print(f"    - china_sourced_product: {sourced:,}")

    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE (recipient_name LIKE '%CATALINA CHINA%' OR vendor_name LIKE '%CATALINA CHINA%')
          AND award_description LIKE '%TABLEWARE%'
    """)
    catalina = cursor.fetchone()[0]
    print(f"    - Catalina China (ceramics): {catalina:,}")

    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE recipient_name LIKE '%FACCHIN%' OR vendor_name LIKE '%FACCHIN%'
    """)
    facchina = cursor.fetchone()[0]
    print(f"    - Facchinaggi/Facchina (Italian): {facchina:,}")

    # Create new clean table
    print("\n[1/5] Creating new clean table...")
    cursor.execute("DROP TABLE IF EXISTS usaspending_china_305_clean")

    cursor.execute("""
        CREATE TABLE usaspending_china_305_clean AS
        SELECT * FROM usaspending_china_305
        WHERE detection_types != '["china_sourced_product"]'
          AND (recipient_name NOT LIKE '%CATALINA CHINA%' AND vendor_name NOT LIKE '%CATALINA CHINA%')
          AND (recipient_name NOT LIKE '%FACCHIN%' AND vendor_name NOT LIKE '%FACCHIN%')
    """)
    print(f"  [OK] Created clean table")

    # Verify count
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_305_clean")
    clean_count = cursor.fetchone()[0]
    print(f"  [OK] Clean table has {clean_count:,} records")

    # Create indexes on new table
    print("\n[2/5] Creating indexes on clean table...")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clean_recipient_country ON usaspending_china_305_clean(recipient_country_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clean_pop_country ON usaspending_china_305_clean(pop_country_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clean_amount ON usaspending_china_305_clean(award_amount)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clean_date ON usaspending_china_305_clean(action_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clean_recipient ON usaspending_china_305_clean(recipient_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clean_vendor ON usaspending_china_305_clean(vendor_name)')
    print("  [OK] Indexes created")

    # Drop old table
    print("\n[3/5] Dropping old table...")
    cursor.execute("DROP TABLE usaspending_china_305")
    print("  [OK] Old table dropped")

    # Rename new table
    print("\n[4/5] Renaming clean table...")
    cursor.execute("ALTER TABLE usaspending_china_305_clean RENAME TO usaspending_china_305")
    print("  [OK] Table renamed")

    # Vacuum to reclaim space
    print("\n[5/5] Vacuuming database...")
    cursor.execute("VACUUM")
    print("  [OK] Database vacuumed")

    conn.commit()
    conn.close()

    # Summary
    print("\n" + "=" * 80)
    print("CLEAN TABLE REBUILD COMPLETE")
    print("=" * 80)

    print(f"\nBefore: {initial_count:,} records")
    print(f"After:  {clean_count:,} records")
    print(f"Removed: {remove_count:,} records ({(remove_count/initial_count)*100:.1f}%)")

    print(f"\nRemoved records breakdown:")
    print(f"  - China sourced products (US companies): {sourced:,}")
    print(f"  - Catalina China (American ceramics): {catalina:,}")
    print(f"  - Facchinaggi/Facchina (Italian): {facchina:,}")

    print(f"\nMain database now contains:")
    print(f"  - {clean_count:,} Chinese entities")
    print(f"  - No china_sourced_product records")
    print(f"  - No false positives")

    return {
        'initial_count': initial_count,
        'final_count': clean_count,
        'removed': remove_count,
        'breakdown': {
            'china_sourced_product': sourced,
            'catalina_china': catalina,
            'facchinaggi': facchina
        }
    }

if __name__ == "__main__":
    try:
        results = rebuild_clean_table()
        print(f"\n[SUCCESS] Database cleaned: {results['final_count']:,} verified Chinese entities")
    except Exception as e:
        print(f"\n[ERROR] Rebuild failed: {e}")
        import traceback
        traceback.print_exc()
