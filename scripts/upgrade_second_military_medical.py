#!/usr/bin/env python3
"""
upgrade_second_military_medical.py - Upgrade Second Military Medical University

Upgrades Second Military Medical University from TIER_2 to TIER_1
due to direct PLA connection.
"""

import sqlite3
from datetime import datetime

def upgrade_second_military():
    """Upgrade Second Military Medical University to TIER_1"""

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("="*60)
    print("SECOND MILITARY MEDICAL UNIVERSITY - TIER_1 UPGRADE")
    print("="*60)
    print(f"\nDatabase: {db_path}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    entity_pattern = "%SECOND MILITARY MEDICAL%"

    # Check all tables
    tables = ['usaspending_china_305', 'usaspending_china_101', 'usaspending_china_comprehensive']

    total_upgraded = 0

    for table in tables:
        print(f"\n[{table}]")

        # Count current TIER_2 records
        count_query = f"""
            SELECT COUNT(*) as count
            FROM {table}
            WHERE recipient_name LIKE ?
              AND importance_tier = 'TIER_2'
        """

        cursor.execute(count_query, (entity_pattern,))
        count = cursor.fetchone()[0]

        print(f"  Found {count} TIER_2 records to upgrade")

        if count == 0:
            continue

        # Show sample records
        sample_query = f"""
            SELECT recipient_name, award_description, highest_confidence
            FROM {table}
            WHERE recipient_name LIKE ?
              AND importance_tier = 'TIER_2'
            LIMIT 3
        """

        cursor.execute(sample_query, (entity_pattern,))
        samples = cursor.fetchall()

        print(f"  Sample records:")
        for i, (name, desc, conf) in enumerate(samples, 1):
            desc_short = desc[:80] if desc else ""
            print(f"    {i}. {name}")
            print(f"       Confidence: {conf}")
            print(f"       Description: {desc_short}...")

        # Upgrade to TIER_1
        update_query = f"""
            UPDATE {table}
            SET importance_tier = 'TIER_1',
                importance_score = 0.95
            WHERE recipient_name LIKE ?
              AND importance_tier = 'TIER_2'
        """

        cursor.execute(update_query, (entity_pattern,))
        upgraded = cursor.rowcount
        total_upgraded += upgraded

        print(f"  [OK] Upgraded {upgraded} records to TIER_1")

    # Commit changes
    conn.commit()

    print("\n" + "="*60)
    print("UPGRADE COMPLETE")
    print("="*60)
    print(f"\nTotal records upgraded: {total_upgraded}")
    print("\nReason: Direct PLA medical institution")
    print("Concerns:")
    print("  - Second Military Medical University")
    print("  - PLA-affiliated medical research")
    print("  - Dual-use medical technology potential")
    print("  - Military medical training and research")

    print("\n" + "="*60)

    conn.close()

if __name__ == "__main__":
    upgrade_second_military()
