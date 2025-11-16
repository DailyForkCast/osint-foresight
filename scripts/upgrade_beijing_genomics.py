#!/usr/bin/env python3
"""
upgrade_beijing_genomics.py - Upgrade Beijing Institute of Genomics to TIER_1

Updates all Beijing Institute of Genomics records from TIER_2 to TIER_1
due to dual-use genomics research concerns.
"""

import sqlite3
from datetime import datetime

def upgrade_beijing_genomics():
    """Upgrade Beijing Institute of Genomics to TIER_1"""

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("="*60)
    print("BEIJING INSTITUTE OF GENOMICS - TIER_1 UPGRADE")
    print("="*60)
    print(f"\nDatabase: {db_path}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    entity_pattern = "%BEIJING INSTITUTE OF GENOMICS%"

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
    print("\nReason: Chinese Academy of Sciences (CAS) genomics institute")
    print("Concerns:")
    print("  - Dual-use genomics technology (CRISPR, gene editing)")
    print("  - PCR/resequencing capabilities")
    print("  - CAS has known PLA connections")
    print("  - Military-Civil Fusion target area")
    print("  - Bioweapons potential")

    print("\nContracts found:")
    print("  - HICKSTEIN-PRIMER DESIGN, PCR TO RESEQUENCING")
    print("  - SCREENING ZEBRAFISH MUTANTS BY RESEQUENCING")

    print("\n" + "="*60)

    conn.close()

if __name__ == "__main__":
    upgrade_beijing_genomics()
