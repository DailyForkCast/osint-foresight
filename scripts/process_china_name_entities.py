#!/usr/bin/env python3
"""
process_china_name_entities.py - Process China Name Entity Recommendations

Executes recommendations from China name entity investigation:

UPGRADES TO TIER_1 (3 entities):
1. CHINA SHIPPING DEVELOPMENT CO., LTD. - COSCO (PRC SOE)
2. CHINA SOUTH LOCOMOTIVE & ROLLING STOCK - CRRC (PRC SOE)
3. CHINA RAILWAY JIANCHANG ENGINE - PRC construction/railway SOE

REMOVALS (2 entities):
4. OVERSEA-CHINESE BANKING CORPORATION - Singapore bank (false positive)
5. SOUTH CHINA CAFE - Restaurant (false positive)

NO ACTION:
6. THE CHINA NAVIGATION COMPANY - Keep in TIER_2 (Swire Group)
7. LENOVO GROUP LIMITED - Already in supply chain tracking
"""

import sqlite3
from datetime import datetime
import json

class ChinaNameEntityProcessor:
    """Process China name entity recommendations"""

    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.stats = {
            'upgraded_to_tier1': 0,
            'removed_false_positives': 0
        }

    def upgrade_to_tier1(self, pattern, label, reasoning):
        """Upgrade entity to TIER_1"""

        print(f"\n{'='*80}")
        print(f"UPGRADING TO TIER_1: {label}")
        print("="*80)
        print(f"Reasoning: {reasoning}")

        tables = ['usaspending_china_305', 'usaspending_china_101', 'usaspending_china_comprehensive']
        total_upgraded = 0

        for table in tables:
            try:
                # Count records
                count_query = f"""
                    SELECT COUNT(*) as count
                    FROM {table}
                    WHERE recipient_name LIKE ?
                      AND importance_tier != 'TIER_1'
                """

                self.cursor.execute(count_query, (pattern,))
                count = self.cursor.fetchone()[0]

                if count == 0:
                    continue

                print(f"\n  Table: {table}")
                print(f"  Records to upgrade: {count}")

                # Upgrade to TIER_1
                update_query = f"""
                    UPDATE {table}
                    SET importance_tier = 'TIER_1',
                        importance_score = 0.95
                    WHERE recipient_name LIKE ?
                      AND importance_tier != 'TIER_1'
                """

                self.cursor.execute(update_query, (pattern,))
                upgraded = self.cursor.rowcount
                total_upgraded += upgraded

                print(f"  [OK] Upgraded {upgraded} records to TIER_1")

            except Exception as e:
                print(f"  [ERROR] {table}: {e}")

        self.stats['upgraded_to_tier1'] += total_upgraded
        return total_upgraded

    def remove_entity(self, pattern, label, reasoning):
        """Remove false positive entity"""

        print(f"\n{'='*80}")
        print(f"REMOVING FALSE POSITIVE: {label}")
        print("="*80)
        print(f"Reasoning: {reasoning}")

        tables = ['usaspending_china_305', 'usaspending_china_101', 'usaspending_china_comprehensive']
        total_removed = 0

        for table in tables:
            try:
                # Count records
                count_query = f"""
                    SELECT COUNT(*) as count
                    FROM {table}
                    WHERE recipient_name LIKE ?
                       OR vendor_name LIKE ?
                """

                self.cursor.execute(count_query, (pattern, pattern))
                count = self.cursor.fetchone()[0]

                if count == 0:
                    continue

                print(f"\n  Table: {table}")
                print(f"  Records to remove: {count}")

                # Delete records
                delete_query = f"""
                    DELETE FROM {table}
                    WHERE recipient_name LIKE ?
                       OR vendor_name LIKE ?
                """

                self.cursor.execute(delete_query, (pattern, pattern))
                removed = self.cursor.rowcount
                total_removed += removed

                print(f"  [OK] Removed {removed} records")

            except Exception as e:
                print(f"  [ERROR] {table}: {e}")

        self.stats['removed_false_positives'] += total_removed
        return total_removed

    def process_all(self):
        """Process all recommendations"""

        print("="*80)
        print("CHINA NAME ENTITY PROCESSING")
        print("="*80)
        print(f"\nDatabase: {self.db_path}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print("\n" + "="*80)
        print("TIER_1 UPGRADES (PRC STATE-OWNED ENTITIES)")
        print("="*80)

        # 1. China Shipping Development - COSCO
        self.upgrade_to_tier1(
            "%CHINA SHIPPING DEVELOPMENT%",
            "CHINA SHIPPING DEVELOPMENT CO., LTD.",
            "Confirmed PRC SOE - Part of COSCO Shipping, critical infrastructure"
        )

        # 2. China South Locomotive - CRRC
        self.upgrade_to_tier1(
            "%CHINA SOUTH LOCOMOTIVE%",
            "CHINA SOUTH LOCOMOTIVE & ROLLING STOCK INDUSTRY (GROUP) CORP",
            "Confirmed PRC SOE - Now CRRC Corporation, world's largest rolling stock manufacturer"
        )

        # 3. China Railway Jianchang Engine
        self.upgrade_to_tier1(
            "%CHINA RAILWAY JIANCHANG ENGINE%",
            "CHINA RAILWAY JIANCHANG ENGINE",
            "PRC construction/railway firm - Operating in Africa, state-controlled sector"
        )

        print("\n" + "="*80)
        print("FALSE POSITIVE REMOVALS")
        print("="*80)

        # 4. Oversea-Chinese Banking Corporation
        self.remove_entity(
            "%OVERSEA-CHINESE BANKING%",
            "OVERSEA-CHINESE BANKING CORPORATION LIMITED",
            "Singapore bank (OCBC), not PRC-owned, serves Chinese diaspora"
        )

        # 5. South China Cafe
        self.remove_entity(
            "%SOUTH CHINA CAFE%",
            "SOUTH CHINA CAFE",
            "Restaurant/food service, no strategic concern"
        )

        # Commit all changes
        self.conn.commit()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print detailed summary"""

        print("\n" + "="*80)
        print("PROCESSING COMPLETE")
        print("="*80)

        print(f"\nRECORDS MODIFIED:")
        print(f"  Upgraded to TIER_1: {self.stats['upgraded_to_tier1']}")
        print(f"  False positives removed: {self.stats['removed_false_positives']}")
        print(f"  Total changes: {self.stats['upgraded_to_tier1'] + self.stats['removed_false_positives']}")

        print("\n" + "="*80)
        print("ENTITIES UPGRADED TO TIER_1")
        print("="*80)

        print("\n1. CHINA SHIPPING DEVELOPMENT CO., LTD.")
        print("   - Status: PRC state-owned enterprise")
        print("   - Parent: COSCO Shipping (formed 2016 merger)")
        print("   - Sector: Critical infrastructure - shipping/logistics")
        print("   - Contracts: $2.27M in shipping charters")
        print("   - Strategic Concern: Global shipping capability, dual-use logistics")

        print("\n2. CHINA SOUTH LOCOMOTIVE & ROLLING STOCK INDUSTRY (GROUP) CORP")
        print("   - Status: PRC state-owned enterprise")
        print("   - Parent: CRRC Corporation (formed 2015 merger)")
        print("   - Sector: Railway equipment manufacturing")
        print("   - Position: World's largest rolling stock manufacturer")
        print("   - Strategic Concern: Defense/transportation infrastructure")

        print("\n3. CHINA RAILWAY JIANCHANG ENGINE")
        print("   - Status: PRC state-controlled construction/railway firm")
        print("   - Operations: Africa (Tanzania) infrastructure projects")
        print("   - Sector: Railway/construction (state-controlled in PRC)")
        print("   - Strategic Concern: Belt & Road infrastructure expansion")

        print("\n" + "="*80)
        print("FALSE POSITIVES REMOVED")
        print("="*80)

        print("\n4. OVERSEA-CHINESE BANKING CORPORATION LIMITED")
        print("   - Status: Singapore bank (NOT PRC-owned)")
        print("   - Founded: 1932, publicly traded (Singapore Exchange)")
        print("   - Serves: Chinese diaspora communities")
        print("   - Contracts: $199K in ATM services (Singapore)")
        print("   - Reason for Removal: No PRC control, false positive")

        print("\n5. SOUTH CHINA CAFE")
        print("   - Status: Restaurant/food service")
        print("   - Contracts: Single contract, $0 value")
        print("   - Reason for Removal: No strategic concern, cuisine name only")

        print("\n" + "="*80)
        print("NO ACTION TAKEN (AS APPROPRIATE)")
        print("="*80)

        print("\n6. THE CHINA NAVIGATION COMPANY PTE. LTD.")
        print("   - Status: KEPT IN TIER_2")
        print("   - Owner: Swire Group (UK/Hong Kong conglomerate)")
        print("   - Location: Singapore (PTE. LTD.)")
        print("   - Contracts: $55.5M in shipping services")
        print("   - Reasoning: International company, not PRC-controlled")
        print("   - Action: Continue monitoring in TIER_2")

        print("\n7. LENOVO GROUP LIMITED")
        print("   - Status: NO ACTION NEEDED")
        print("   - Contracts: 533 records, $60.9M")
        print("   - Current Status: Already in dedicated supply chain tracking")
        print("   - Reasoning: Properly classified and tracked")

        print("\n" + "="*80)
        print("STRATEGIC ANALYSIS")
        print("="*80)

        print("\nPRC STATE-OWNED ENTERPRISE EXPANSION:")
        print("  - All 3 upgraded entities are confirmed or likely PRC SOEs")
        print("  - Sectors: Shipping (COSCO), Railway (CRRC), Construction (CREC)")
        print("  - Geographic reach: Global shipping, Africa infrastructure")
        print("  - Strategic concerns: Critical infrastructure, dual-use capabilities")

        print("\nFALSE POSITIVE PATTERN:")
        print("  - 'OVERSEA-CHINESE' refers to diaspora, not PRC entities")
        print("  - Geographic/cultural names ('South China') trigger detection")
        print("  - Need to distinguish ethnic Chinese vs. PRC-controlled entities")

        print("\nKEY FINDING:")
        print("  - China Shipping Development contracts include:")
        print("    * 'TRANSPORT OF HFO TO THE DPRK' (North Korea)")
        print("    * Multiple shipping charters for US military logistics")
        print("  - Raises questions about PRC SOE involvement in sensitive shipments")

        print("\n" + "="*80)

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"analysis/china_name_entity_processing_{timestamp}.json"

        with open(report_path, 'w') as f:
            json.dump({
                'processing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'statistics': self.stats,
                'upgrades': [
                    'CHINA SHIPPING DEVELOPMENT CO., LTD.',
                    'CHINA SOUTH LOCOMOTIVE & ROLLING STOCK',
                    'CHINA RAILWAY JIANCHANG ENGINE'
                ],
                'removals': [
                    'OVERSEA-CHINESE BANKING CORPORATION LIMITED',
                    'SOUTH CHINA CAFE'
                ],
                'no_action': [
                    'THE CHINA NAVIGATION COMPANY PTE. LTD. (kept in TIER_2)',
                    'LENOVO GROUP LIMITED (already tracked)'
                ]
            }, f, indent=2)

        print(f"\nReport saved: {report_path}")
        print("="*80)

    def close(self):
        self.conn.close()

def main():
    print("\n" + "="*80)
    print("IMPORTANT: Processing China Name Entity Recommendations")
    print("="*80)
    print("\nThis will:")
    print("  1. UPGRADE 3 entities to TIER_1 (PRC SOEs)")
    print("     - China Shipping Development (COSCO)")
    print("     - China South Locomotive (CRRC)")
    print("     - China Railway Jianchang Engine")
    print("\n  2. REMOVE 2 false positives")
    print("     - Oversea-Chinese Banking Corporation (Singapore)")
    print("     - South China Cafe (Restaurant)")
    print("\n  3. NO ACTION on:")
    print("     - China Navigation Company (keep TIER_2)")
    print("     - Lenovo (already tracked)")

    response = input("\nProceed with processing? (yes/no): ")

    if response.lower() != 'yes':
        print("\n[CANCELLED] No changes made to database")
        return

    processor = ChinaNameEntityProcessor()
    processor.process_all()
    processor.close()

if __name__ == "__main__":
    main()
