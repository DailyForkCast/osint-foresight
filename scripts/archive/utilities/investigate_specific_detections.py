#!/usr/bin/env python3
"""
Investigate why specific transactions were flagged as China-related.
"""

import sqlite3
from pathlib import Path
import json

def investigate_transactions():
    """Look up specific transaction IDs and show detection rationale."""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # Transaction IDs to investigate
    transaction_ids = [
        '121654629',  # COMAC PUMP & WELL LLC
        '48212082',   # MBA OFFICE SUPPLY INC.
        '60565125',   # AZTEC ENVIRONMENTAL, INC.
        '179199549',  # EZTEQ LLC
    ]

    # Additional entities mentioned
    entity_names = [
        "Avic's Travel, LLC",
        "VISTA GORGONIO INC",
        "T K C ENTERPRISES INC",
    ]

    print("="*100)
    print("INVESTIGATING SPECIFIC DETECTIONS")
    print("="*100)
    print()

    # Check all three tables
    tables = [
        ('usaspending_china_101', '101-column'),
        ('usaspending_china_305', '305-column'),
        ('usaspending_china_comprehensive', '206-column')
    ]

    for transaction_id in transaction_ids:
        print(f"\n{'='*100}")
        print(f"TRANSACTION ID: {transaction_id}")
        print(f"{'='*100}")

        found = False
        for table, format_name in tables:
            try:
                cursor = conn.execute(f"""
                    SELECT * FROM {table}
                    WHERE transaction_id = ?
                """, (transaction_id,))

                row = cursor.fetchone()
                if row:
                    found = True
                    row_dict = dict(row)

                    print(f"\nFOUND IN: {format_name}")
                    print(f"Recipient: {row_dict.get('recipient_name', 'N/A')}")
                    print(f"Vendor: {row_dict.get('vendor_name', 'N/A')}")
                    print(f"Sub-awardee: {row_dict.get('sub_awardee_name', 'N/A')}")
                    print(f"Sub-awardee Parent: {row_dict.get('sub_awardee_parent_name', 'N/A')}")
                    print(f"Sub-awardee Country: {row_dict.get('sub_awardee_country', 'N/A')}")
                    print(f"Description: {(row_dict.get('award_description', 'N/A') or 'N/A')[:300]}...")
                    print(f"Detection Types: {row_dict.get('detection_types', 'N/A')}")
                    print(f"Rationale: {row_dict.get('detection_rationale', 'N/A')}")
                    print(f"Confidence: {row_dict.get('highest_confidence', 'N/A')}")

            except Exception as e:
                pass

        if not found:
            print(f"NOT FOUND in any table")

    # Search by entity name
    print(f"\n\n{'='*100}")
    print("SEARCHING BY ENTITY NAME")
    print(f"{'='*100}")

    for entity_name in entity_names:
        print(f"\n{'-'*100}")
        print(f"ENTITY: {entity_name}")
        print(f"{'-'*100}")

        found_any = False
        for table, format_name in tables:
            try:
                # Search in recipient_name, vendor_name, sub_awardee_name
                cursor = conn.execute(f"""
                    SELECT transaction_id, recipient_name, vendor_name, sub_awardee_name,
                           detection_types, detection_rationale, highest_confidence,
                           award_description
                    FROM {table}
                    WHERE recipient_name LIKE ?
                       OR vendor_name LIKE ?
                       OR sub_awardee_name LIKE ?
                    LIMIT 5
                """, (f'%{entity_name}%', f'%{entity_name}%', f'%{entity_name}%'))

                rows = cursor.fetchall()
                if rows:
                    found_any = True
                    print(f"\nFOUND {len(rows)} in {format_name}:")
                    for row in rows:
                        row_dict = dict(row)
                        print(f"  Transaction: {row_dict['transaction_id']}")
                        print(f"  Recipient: {row_dict.get('recipient_name', 'N/A')}")
                        print(f"  Vendor: {row_dict.get('vendor_name', 'N/A')}")
                        print(f"  Sub-awardee: {row_dict.get('sub_awardee_name', 'N/A')}")
                        print(f"  Detection: {row_dict['detection_types']}")
                        print(f"  Rationale: {row_dict['detection_rationale']}")
                        print(f"  Description: {(row_dict.get('award_description', 'N/A') or 'N/A')[:200]}...")
                        print()
            except Exception as e:
                pass

        if not found_any:
            print(f"  NOT FOUND in any table")

    # Search for "made in China" descriptions
    print(f"\n\n{'='*100}")
    print("SEARCHING FOR 'MADE IN CHINA' DESCRIPTIONS")
    print(f"{'='*100}")

    for table, format_name in tables:
        try:
            cursor = conn.execute(f"""
                SELECT COUNT(*) as count
                FROM {table}
                WHERE LOWER(award_description) LIKE '%made in china%'
            """)

            count = cursor.fetchone()['count']
            print(f"\n{format_name}: {count:,} records with 'made in China' in description")

            if count > 0:
                # Get a sample
                cursor = conn.execute(f"""
                    SELECT transaction_id, recipient_name, award_description,
                           detection_types, detection_rationale
                    FROM {table}
                    WHERE LOWER(award_description) LIKE '%made in china%'
                    LIMIT 5
                """)

                rows = cursor.fetchall()
                print(f"Sample of {len(rows)} records:")
                for row in rows:
                    row_dict = dict(row)
                    print(f"\n  Transaction: {row_dict['transaction_id']}")
                    print(f"  Recipient: {row_dict.get('recipient_name', 'N/A')}")
                    print(f"  Description: {(row_dict.get('award_description', 'N/A') or 'N/A')[:300]}...")
                    print(f"  Detection: {row_dict['detection_types']}")
                    print(f"  Rationale: {row_dict['detection_rationale']}")
        except Exception as e:
            print(f"Error searching {format_name}: {e}")

    # Search for "SUPPORT TO ETHNIC TIBETS IN CHINA"
    print(f"\n\n{'='*100}")
    print("SEARCHING FOR 'SUPPORT TO ETHNIC TIBETS IN CHINA' DESCRIPTIONS")
    print(f"{'='*100}")

    for table, format_name in tables:
        try:
            cursor = conn.execute(f"""
                SELECT COUNT(*) as count
                FROM {table}
                WHERE LOWER(award_description) LIKE '%ethnic tibet%'
            """)

            count = cursor.fetchone()['count']
            if count > 0:
                print(f"\n{format_name}: {count:,} records with 'ethnic tibet' in description")

                # Get sample
                cursor = conn.execute(f"""
                    SELECT transaction_id, recipient_name, award_description,
                           detection_types, detection_rationale
                    FROM {table}
                    WHERE LOWER(award_description) LIKE '%ethnic tibet%'
                    LIMIT 3
                """)

                rows = cursor.fetchall()
                for row in rows:
                    row_dict = dict(row)
                    print(f"\n  Transaction: {row_dict['transaction_id']}")
                    print(f"  Recipient: {row_dict.get('recipient_name', 'N/A')}")
                    print(f"  Description: {row_dict.get('award_description', 'N/A')}")
                    print(f"  Detection: {row_dict['detection_types']}")
        except Exception as e:
            pass

    conn.close()


if __name__ == '__main__':
    investigate_transactions()
