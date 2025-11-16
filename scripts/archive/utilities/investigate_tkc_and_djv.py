#!/usr/bin/env python3
"""
Investigate PRI/DJI construction JV and all T K C ENTERPRISES records.
"""

import sqlite3
from pathlib import Path
import json

def investigate_records():
    """Investigate specific records for relevance."""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    print("="*100)
    print("INVESTIGATING PRI/DJI CONSTRUCTION JV AND T K C ENTERPRISES")
    print("="*100)

    # 1. Check PRI/DJI transaction
    print("\n" + "="*100)
    print("1. PRI/DJI, A CONSTRUCTION JV - Transaction 1273215")
    print("="*100)

    tables = [
        ('usaspending_china_101', '101-column'),
        ('usaspending_china_305', '305-column'),
        ('usaspending_china_comprehensive', '206-column')
    ]

    found = False
    for table, format_name in tables:
        try:
            cursor = conn.execute(f"""
                SELECT * FROM {table}
                WHERE transaction_id = '1273215'
            """)

            row = cursor.fetchone()
            if row:
                found = True
                row_dict = dict(row)
                print(f"\nFOUND IN: {format_name}")
                print(f"Recipient: {row_dict.get('recipient_name', 'N/A')}")
                print(f"Vendor: {row_dict.get('vendor_name', 'N/A')}")
                print(f"Sub-awardee: {row_dict.get('sub_awardee_name', 'N/A')}")
                print(f"Description: {(row_dict.get('award_description', '') or 'N/A')[:500]}...")
                print(f"Detection Types: {row_dict.get('detection_types', 'N/A')}")
                print(f"Confidence: {row_dict.get('highest_confidence', 'N/A')}")
                print(f"POP Country: {row_dict.get('pop_country_name', '') or row_dict.get('pop_country', 'N/A')}")
                print(f"Recipient Country: {row_dict.get('recipient_country_name', '') or row_dict.get('recipient_country', 'N/A')}")

                # Check why it was flagged
                print("\nWHY FLAGGED:")
                if 'dji' in row_dict.get('recipient_name', '').lower():
                    print("  - 'DJI' in recipient name (matches DJI drone company)")
        except Exception as e:
            pass

    if not found:
        print("NOT FOUND in database")

    # 2. Get ALL T K C ENTERPRISES records
    print("\n\n" + "="*100)
    print("2. ALL T K C ENTERPRISES INC RECORDS (41 total)")
    print("="*100)

    for table, format_name in tables:
        try:
            cursor = conn.execute(f"""
                SELECT transaction_id, recipient_name, vendor_name, award_description,
                       detection_types, highest_confidence,
                       pop_country_name, recipient_country_name
                FROM {table}
                WHERE recipient_name LIKE '%T K C ENTERPRISES%'
                   OR vendor_name LIKE '%T K C ENTERPRISES%'
                ORDER BY transaction_id
            """)

            rows = cursor.fetchall()
            if rows:
                print(f"\n{format_name}: {len(rows)} records")
                print(f"{'-'*100}")

                # Analyze patterns
                detection_reasons = {}
                descriptions_sample = []

                for row in rows:
                    row_dict = dict(row)
                    det_types = row_dict.get('detection_types', '')

                    # Count detection types
                    if det_types:
                        if det_types not in detection_reasons:
                            detection_reasons[det_types] = 0
                        detection_reasons[det_types] += 1

                    # Collect sample descriptions
                    if len(descriptions_sample) < 5:
                        descriptions_sample.append({
                            'transaction_id': row_dict['transaction_id'],
                            'description': (row_dict.get('award_description', '') or 'N/A')[:300],
                            'pop_country': row_dict.get('pop_country_name', 'N/A'),
                            'detection': det_types
                        })

                print(f"\nDetection Type Breakdown:")
                for det_type, count in sorted(detection_reasons.items()):
                    print(f"  {det_type}: {count} records")

                print(f"\nSample Records:")
                for i, sample in enumerate(descriptions_sample, 1):
                    print(f"\n  {i}. Transaction {sample['transaction_id']}")
                    print(f"     POP Country: {sample['pop_country']}")
                    print(f"     Detection: {sample['detection']}")
                    print(f"     Description: {sample['description']}...")

                # Check for actual China connections
                print(f"\n\nChecking for ACTUAL China connections:")
                cursor = conn.execute(f"""
                    SELECT transaction_id, recipient_name, pop_country_name,
                           recipient_country_name, award_description
                    FROM {table}
                    WHERE (recipient_name LIKE '%T K C ENTERPRISES%'
                       OR vendor_name LIKE '%T K C ENTERPRISES%')
                      AND (pop_country_name LIKE '%CHINA%'
                       OR recipient_country_name LIKE '%CHINA%')
                """)

                china_records = cursor.fetchall()
                if china_records:
                    print(f"  Found {len(china_records)} with China in country fields:")
                    for rec in china_records[:3]:
                        print(f"    {rec['transaction_id']}: POP={rec['pop_country_name']}, Recipient Country={rec['recipient_country_name']}")
                else:
                    print(f"  NO records with China in country fields")
                    print(f"  → All T K C ENTERPRISES detections appear to be FALSE POSITIVES")

        except Exception as e:
            print(f"Error checking {format_name}: {e}")

    # 3. Check what's triggering T K C detection
    print("\n\n" + "="*100)
    print("3. ANALYZING T K C ENTERPRISES DETECTION TRIGGER")
    print("="*100)

    # Check if description contains "china"
    cursor = conn.execute("""
        SELECT award_description
        FROM usaspending_china_305
        WHERE recipient_name LIKE '%T K C ENTERPRISES%'
        LIMIT 5
    """)

    print("\nChecking descriptions for 'china' mentions:")
    for row in cursor:
        desc = (row['award_description'] or '').lower()
        if 'china' in desc or 'chinese' in desc:
            # Find context around "china"
            idx = desc.find('china')
            if idx == -1:
                idx = desc.find('chinese')

            start = max(0, idx - 50)
            end = min(len(desc), idx + 50)
            context = desc[start:end]
            print(f"  Found: ...{context}...")
        else:
            print(f"  No 'china' in description: {desc[:100]}...")

    conn.close()

    # Summary
    print("\n\n" + "="*100)
    print("SUMMARY AND RECOMMENDATIONS")
    print("="*100)
    print("""
FINDINGS:

1. PRI/DJI, A CONSTRUCTION JV:
   - Likely flagged because 'DJI' matches DJI (drone manufacturer)
   - Need to check if this is actually DJI or just abbreviation
   - Recommend: Add to false positive filter if confirmed US company

2. T K C ENTERPRISES INC (41 records):
   - ALL appear to be false positives
   - No records have China in country fields
   - Likely triggered by description mentions of "china" (product origin)
   - Recommend: Add 't k c enterprises' to false positive filter

3. Other entities to add to false positive filters:
   - 'comac pump' / 'comac well'
   - 'aztec environmental'
   - 'ezteq'
   - 'mavich'
   - 'vista gorgonio'
   - 'pri/djv' (if confirmed not DJI)

4. Description-based exclusions needed:
   - 'made in china'
   - 'manufactured in china'
   - 'produced in china'
   - 'ethnic tibet'
""")


if __name__ == '__main__':
    investigate_records()
