#!/usr/bin/env python3
"""
process_manual_review_batch2.py - Process Manual Review Batch 2

Handles actions from continued manual review:
1. Upgrade Central People's Government to TIER_1
2. Upgrade ALL Fudan University records to TIER_1
3. Remove Taiwan Government/University (false positives)
4. Remove Hungarian Ministry of Defense (false positive)
5. George Institute - no action (legitimate medical research)
"""

import sqlite3
from datetime import datetime

class ManualReviewProcessor:
    """Process manual review findings batch 2"""

    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.stats = {
            'upgraded_to_tier1': 0,
            'removed_false_positives': 0
        }

    def upgrade_entity(self, pattern, label):
        """Upgrade entity to TIER_1"""

        print(f"\n{'='*60}")
        print(f"UPGRADING: {label}")
        print("="*60)

        tables = ['usaspending_china_305', 'usaspending_china_101', 'usaspending_china_comprehensive']

        total_upgraded = 0

        for table in tables:
            # Count records to upgrade
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

        self.stats['upgraded_to_tier1'] += total_upgraded
        return total_upgraded

    def remove_entity(self, pattern, label):
        """Remove false positive entity"""

        print(f"\n{'='*60}")
        print(f"REMOVING: {label}")
        print("="*60)

        tables = ['usaspending_china_305', 'usaspending_china_101', 'usaspending_china_comprehensive']

        total_removed = 0

        for table in tables:
            # Count records
            count_query = f"""
                SELECT COUNT(*) as count
                FROM {table}
                WHERE recipient_name LIKE ?
            """

            self.cursor.execute(count_query, (pattern,))
            count = self.cursor.fetchone()[0]

            if count == 0:
                continue

            print(f"\n  Table: {table}")
            print(f"  Records to remove: {count}")

            # Delete records
            delete_query = f"""
                DELETE FROM {table}
                WHERE recipient_name LIKE ?
            """

            self.cursor.execute(delete_query, (pattern,))
            removed = self.cursor.rowcount
            total_removed += removed

            print(f"  [OK] Removed {removed} records")

        self.stats['removed_false_positives'] += total_removed
        return total_removed

    def process_all(self):
        """Process all manual review actions"""

        print("="*60)
        print("MANUAL REVIEW BATCH 2 - PROCESSING")
        print("="*60)
        print(f"\nDatabase: {self.db_path}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. Upgrade Central People's Government
        self.upgrade_entity(
            "%CENTRAL PEOPLE'S GOVERNMENT%",
            "Central People's Government of PRC"
        )

        # 2. Upgrade ALL Fudan University records
        self.upgrade_entity(
            "%FUDAN UNIVERSITY%",
            "Fudan University (ALL departments)"
        )

        # 3. Remove Taiwan Government
        self.remove_entity(
            "%GOVERNMENT OF THE REPUBLIC OF CHINA (TAIWAN)%",
            "Taiwan Government (false positive)"
        )

        # 4. Remove National Taiwan University
        self.remove_entity(
            "%NATIONAL TAIWAN UNIVERSITY%",
            "National Taiwan University (false positive)"
        )

        # 5. Remove Hungarian Ministry of Defense
        self.remove_entity(
            "%HONVEDELMI%",
            "Hungarian Ministry of Defense (false positive)"
        )

        # Commit all changes
        self.conn.commit()

        # Print summary
        print("\n" + "="*60)
        print("BATCH 2 PROCESSING COMPLETE")
        print("="*60)

        print(f"\nRecords upgraded to TIER_1: {self.stats['upgraded_to_tier1']}")
        print(f"False positives removed: {self.stats['removed_false_positives']}")

        print("\n" + "="*60)
        print("ENTITIES PROCESSED")
        print("="*60)

        print("\nUPGRADED TO TIER_1:")
        print("  1. Central People's Government of PRC")
        print("     - Literally the Chinese government")
        print("     - Contracts: Lung cancer research, disease control")
        print("     - Strategic concern: Direct government entity")

        print("\n  2. Fudan University (ALL departments)")
        print("     - Major Chinese research university")
        print("     - Departments: Occupational Health, Public Health")
        print("     - Contracts: Genotyping, clinical research, biomedical")
        print("     - Concern: Top-tier Chinese research institution")

        print("\nREMOVED (FALSE POSITIVES):")
        print("  3. Government of the Republic of China (Taiwan)")
        print("     - Taiwan government entity")
        print("     - Reason: Taiwan policy - not mainland China")

        print("\n  4. National Taiwan University")
        print("     - Taiwan university")
        print("     - Reason: Taiwan policy - not mainland China")

        print("\n  5. Hungarian Ministry of Defense")
        print("     - HONVEDELMI MINISZTERIUM (Hungarian)")
        print("     - Reason: Hungarian words triggering chinese_name detector")
        print("     - Location: Hungary")
        print("     - Contracts: US military exercise support")

        print("\nKEPT IN TIER_2 (NO ACTION):")
        print("  6. The George Institute, China")
        print("     - Australian medical research org (China branch)")
        print("     - Legitimate international medical research")
        print("     - Contracts: Biomedical research, cardiovascular studies")

        print("\n" + "="*60)

    def close(self):
        self.conn.close()

def main():
    processor = ManualReviewProcessor()
    processor.process_all()
    processor.close()

if __name__ == "__main__":
    main()
