#!/usr/bin/env python3
"""
Upgrade China Shipping Development Entities to TIER_1

Based on COSCO investigation findings:
- China Shipping Development was involved in 2016 COSCO merger
- 12 US government contracts (2003-2011)
- 3 DPRK HFO transport contracts (strategic/sensitive)
- Maritime logistics SOE - clearly strategic

Should be upgraded from TIER_2 to TIER_1
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

def upgrade_china_shipping_to_tier1():
    """Upgrade China Shipping Development entities to TIER_1"""

    print("=" * 80)
    print("UPGRADING CHINA SHIPPING DEVELOPMENT TO TIER_1")
    print("=" * 80)
    print()

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Find all China Shipping Development records
    print("Step 1: Finding China Shipping Development records...")
    print()

    # Check usaspending_china_305
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM usaspending_china_305
        WHERE (recipient_name LIKE '%CHINA SHIPPING DEVELOPMENT%'
           OR vendor_name LIKE '%CHINA SHIPPING DEVELOPMENT%')
          AND importance_tier != 'TIER_1'
    """)
    count_305 = cursor.fetchone()['count']
    print(f"  usaspending_china_305: {count_305} records need upgrade")

    # Get sample records before upgrade
    cursor.execute("""
        SELECT transaction_id, recipient_name, vendor_name, importance_tier, action_date, award_amount
        FROM usaspending_china_305
        WHERE (recipient_name LIKE '%CHINA SHIPPING DEVELOPMENT%'
           OR vendor_name LIKE '%CHINA SHIPPING DEVELOPMENT%')
          AND importance_tier != 'TIER_1'
        LIMIT 5
    """)

    samples = cursor.fetchall()
    if samples:
        print("\n  Sample records BEFORE upgrade:")
        for row in samples:
            entity_name = row['recipient_name'] or row['vendor_name']
            print(f"    - {entity_name[:60]}")
            print(f"      Date: {row['action_date']}, Amount: ${row['award_amount']:,.2f}")
            print(f"      Current tier: {row['importance_tier']}")

    # Check other tables (101, comprehensive)
    tables_to_check = ['usaspending_china_101', 'usaspending_china_comprehensive']
    total_count = count_305

    for table in tables_to_check:
        try:
            cursor.execute(f"""
                SELECT COUNT(*) as count
                FROM {table}
                WHERE recipient_name LIKE '%CHINA SHIPPING DEVELOPMENT%'
                  AND importance_tier != 'TIER_1'
            """)
            count = cursor.fetchone()['count']
            print(f"  {table}: {count} records need upgrade")
            total_count += count
        except sqlite3.OperationalError:
            print(f"  {table}: Table not found or no vendor_name column")

    print()
    print(f"Total records to upgrade: {total_count}")
    print()

    if total_count == 0:
        print("[INFO] No records need upgrading (already TIER_1 or don't exist)")
        conn.close()
        return

    # Confirm upgrade
    print("=" * 80)
    print("RATIONALE FOR TIER_1 UPGRADE")
    print("=" * 80)
    print()
    print("1. Strategic Sector: Maritime logistics (state-controlled)")
    print("2. PRC SOE Merger: Part of 2016 COSCO Shipping consolidation")
    print("3. Strategic Operations: 3x DPRK HFO transport contracts (Six-Party Talks)")
    print("4. US Contracting: 12 total contracts, $2.27M value (2003-2011)")
    print("5. Current Parent: China COSCO Shipping Corporation (4th largest globally)")
    print()
    print("Conclusion: Clearly strategic entity, should be TIER_1")
    print()

    # Perform upgrade
    print("Step 2: Performing TIER_1 upgrade...")
    print()

    # Update usaspending_china_305
    cursor.execute("""
        UPDATE usaspending_china_305
        SET importance_tier = 'TIER_1',
            detection_types = detection_types || ',strategic_soe_merger'
        WHERE (recipient_name LIKE '%CHINA SHIPPING DEVELOPMENT%'
           OR vendor_name LIKE '%CHINA SHIPPING DEVELOPMENT%')
          AND importance_tier != 'TIER_1'
    """)
    updated_305 = cursor.rowcount
    print(f"  [OK] Updated {updated_305} records in usaspending_china_305")

    # Update other tables
    for table in tables_to_check:
        try:
            cursor.execute(f"""
                UPDATE {table}
                SET importance_tier = 'TIER_1',
                    detection_types = detection_types || ',strategic_soe_merger'
                WHERE recipient_name LIKE '%CHINA SHIPPING DEVELOPMENT%'
                  AND importance_tier != 'TIER_1'
            """)
            updated = cursor.rowcount
            if updated > 0:
                print(f"  [OK] Updated {updated} records in {table}")
        except sqlite3.OperationalError as e:
            print(f"  [SKIP] {table}: {e}")

    # Commit changes
    conn.commit()
    print()
    print("[OK] All updates committed to database")
    print()

    # Verify upgrade
    print("Step 3: Verifying upgrade...")
    print()

    cursor.execute("""
        SELECT transaction_id, recipient_name, vendor_name, importance_tier, action_date, award_amount
        FROM usaspending_china_305
        WHERE (recipient_name LIKE '%CHINA SHIPPING DEVELOPMENT%'
           OR vendor_name LIKE '%CHINA SHIPPING DEVELOPMENT%')
        LIMIT 5
    """)

    samples_after = cursor.fetchall()
    if samples_after:
        print("  Sample records AFTER upgrade:")
        for row in samples_after:
            entity_name = row['recipient_name'] or row['vendor_name']
            print(f"    - {entity_name[:60]}")
            print(f"      Date: {row['action_date']}, Amount: ${row['award_amount']:,.2f}")
            print(f"      Current tier: {row['importance_tier']}")

    # Count remaining TIER_2/TIER_3 records (should be 0)
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM usaspending_china_305
        WHERE (recipient_name LIKE '%CHINA SHIPPING DEVELOPMENT%'
           OR vendor_name LIKE '%CHINA SHIPPING DEVELOPMENT%')
          AND importance_tier != 'TIER_1'
    """)
    remaining = cursor.fetchone()['count']

    print()
    if remaining == 0:
        print("[SUCCESS] All China Shipping Development records upgraded to TIER_1")
    else:
        print(f"[WARNING] {remaining} records still not TIER_1 (check vendor_name column)")

    conn.close()

    print()
    print("=" * 80)
    print("UPGRADE COMPLETE")
    print("=" * 80)
    print()
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Records upgraded: {updated_305}")
    print(f"New tier: TIER_1")
    print(f"Detection type added: strategic_soe_merger")
    print()
    print("Next steps:")
    print("  1. Cross-reference with entity_mergers table")
    print("  2. Update entity_aliases with name variations")
    print("  3. Flag related Dalian Ocean Shipping contracts (same merger)")
    print()


if __name__ == "__main__":
    upgrade_china_shipping_to_tier1()
