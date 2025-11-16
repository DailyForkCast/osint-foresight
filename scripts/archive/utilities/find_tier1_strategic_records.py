#!/usr/bin/env python3
"""
Find TIER_1 Strategic Records in Database
Searches the full database for actual strategic entities and technologies
"""

import sqlite3
import csv
from pathlib import Path
from datetime import datetime

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("data/processed/usaspending_manual_review")

def find_tier1_records():
    """Find all TIER_1 strategic records in the database"""

    print("=" * 80)
    print("SEARCHING FOR TIER_1 STRATEGIC RECORDS")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Strategic entities to search for
    strategic_entities = [
        'CHINESE ACADEMY', 'HUAWEI', 'ZTE', 'LENOVO',
        'TSINGHUA', 'PEKING UNIVERSITY',
        'AVIC', 'COMAC', 'DJI', 'HIKVISION', 'DAHUA',
        'NORINCO', 'CSSC'
    ]

    # Strategic technologies to search for
    strategic_tech = [
        'QUANTUM', 'ARTIFICIAL INTELLIGENCE', 'SEMICONDUCTOR',
        'BIOTECHNOLOGY', 'SATELLITE', 'HYPERSONIC', 'NUCLEAR',
        'ADVANCED MATERIAL', 'SPACE SYSTEM', 'SPACE TECHNOLOGY',
        'SPACECRAFT', 'MICROCHIP', 'PHARMACEUTICAL'
    ]

    tier1_records = []

    print("\n[1/3] Searching for strategic entities...")
    for entity in strategic_entities:
        # Search in recipient_name, vendor_name
        cursor.execute("""
            SELECT
                transaction_id,
                recipient_name,
                vendor_name,
                pop_country_code,
                pop_country_name,
                award_description,
                award_amount,
                highest_confidence,
                detection_types
            FROM usaspending_china_305
            WHERE recipient_name LIKE ?
               OR vendor_name LIKE ?
            LIMIT 10
        """, (f'%{entity}%', f'%{entity}%'))

        results = cursor.fetchall()
        if results:
            print(f"  Found {len(results)} records for: {entity}")
            for r in results:
                tier1_records.append({
                    'entity_or_tech': entity,
                    'category': 'strategic_entity',
                    'transaction_id': r[0],
                    'recipient_name': r[1],
                    'vendor_name': r[2],
                    'country_code': r[3],
                    'country_name': r[4],
                    'award_description': r[5],
                    'award_amount': r[6],
                    'confidence': r[7],
                    'detection_types': r[8]
                })

    print(f"\n[2/3] Searching for strategic technologies...")
    for tech in strategic_tech:
        # Search in award_description
        cursor.execute("""
            SELECT
                transaction_id,
                recipient_name,
                vendor_name,
                pop_country_code,
                pop_country_name,
                award_description,
                award_amount,
                highest_confidence,
                detection_types
            FROM usaspending_china_305
            WHERE award_description LIKE ?
            LIMIT 10
        """, (f'%{tech}%',))

        results = cursor.fetchall()
        if results:
            print(f"  Found {len(results)} records for: {tech}")
            for r in results:
                tier1_records.append({
                    'entity_or_tech': tech,
                    'category': 'strategic_technology',
                    'transaction_id': r[0],
                    'recipient_name': r[1],
                    'vendor_name': r[2],
                    'country_code': r[3],
                    'country_name': r[4],
                    'award_description': r[5],
                    'award_amount': r[6],
                    'confidence': r[7],
                    'detection_types': r[8]
                })

    conn.close()

    print(f"\n[3/3] Total TIER_1 strategic records found: {len(tier1_records)}")

    if tier1_records:
        # Write to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_csv = OUTPUT_DIR / f"tier1_strategic_records_{timestamp}.csv"

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "Entity_or_Tech", "Category", "Transaction_ID", "Recipient_Name",
            "Vendor_Name", "Country_Code", "Country_Name", "Award_Description",
            "Award_Amount", "Confidence", "Detection_Types"
        ]

        with open(output_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in tier1_records:
                writer.writerow({
                    "Entity_or_Tech": record['entity_or_tech'],
                    "Category": record['category'],
                    "Transaction_ID": record['transaction_id'],
                    "Recipient_Name": record['recipient_name'] or "",
                    "Vendor_Name": record['vendor_name'] or "",
                    "Country_Code": record['country_code'] or "",
                    "Country_Name": record['country_name'] or "",
                    "Award_Description": record['award_description'] or "",
                    "Award_Amount": record['award_amount'] or "",
                    "Confidence": record['confidence'] or "",
                    "Detection_Types": record['detection_types'] or ""
                })

        print("\n" + "=" * 80)
        print("TIER_1 STRATEGIC RECORDS FOUND")
        print("=" * 80)
        print(f"\nOutput: {output_csv}")
        print(f"Total Records: {len(tier1_records)}")

        # Show breakdown by category
        entity_count = sum(1 for r in tier1_records if r['category'] == 'strategic_entity')
        tech_count = sum(1 for r in tier1_records if r['category'] == 'strategic_technology')

        print(f"\nBreakdown:")
        print(f"  Strategic Entities: {entity_count} records")
        print(f"  Strategic Technologies: {tech_count} records")

        # Show top examples
        print(f"\nTop 5 Examples:")
        for i, record in enumerate(tier1_records[:5], 1):
            print(f"\n{i}. {record['entity_or_tech']} ({record['category']})")
            print(f"   Vendor: {record['vendor_name']}")
            desc = record['award_description'] or ""
            print(f"   Description: {desc[:100]}...")
            print(f"   Amount: ${record['award_amount']}")

        return output_csv
    else:
        print("\n" + "=" * 80)
        print("NO TIER_1 STRATEGIC RECORDS FOUND")
        print("=" * 80)
        print("\nThis means:")
        print("  - No Huawei, ZTE, Lenovo, DJI, Hikvision purchases detected")
        print("  - No Chinese Academy or university partnerships detected")
        print("  - No quantum, semiconductor, AI strategic technology purchases")
        print("\nPossible reasons:")
        print("  - Detection patterns are too restrictive")
        print("  - These entities use subsidiaries/alternate names")
        print("  - Strategic purchases go through different procurement channels")
        return None

if __name__ == "__main__":
    try:
        find_tier1_records()
    except Exception as e:
        print(f"\n[ERROR] Failed to search: {e}")
        import traceback
        traceback.print_exc()
