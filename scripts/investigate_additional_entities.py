#!/usr/bin/env python3
"""
investigate_additional_entities.py - Investigate Additional Flagged Entities

Investigates entities from continued manual review.
"""

import sqlite3
import pandas as pd
import json

def investigate_entity(conn, entity_pattern, label):
    """Look up entity and show detection details"""

    print(f"\n{'='*80}")
    print(f"ENTITY: {label}")
    print("="*80)

    tables = ['usaspending_china_305', 'usaspending_china_101', 'usaspending_china_comprehensive']

    for table in tables:
        try:
            query = f"""
                SELECT
                    recipient_name,
                    award_description,
                    importance_tier,
                    highest_confidence,
                    detection_types,
                    detection_details,
                    COUNT(*) OVER() as total_count
                FROM {table}
                WHERE recipient_name LIKE ?
                LIMIT 3
            """

            df = pd.read_sql(query, conn, params=(entity_pattern,))

            if len(df) > 0:
                print(f"\n  Table: {table}")
                print(f"  Total records: {df['total_count'].iloc[0]}")

                for i, row in df.iterrows():
                    print(f"\n  Record {i+1}:")
                    print(f"    Name: {row['recipient_name']}")
                    print(f"    Tier: {row['importance_tier']}")
                    print(f"    Confidence: {row['highest_confidence']}")
                    print(f"    Detection Types: {row['detection_types']}")

                    # Parse detection details
                    try:
                        details = json.loads(row['detection_details']) if row['detection_details'] else {}
                        if details:
                            print(f"    Detection Details:")
                            for key, val in details.items():
                                print(f"      {key}: {val}")
                    except:
                        pass

                    # Show description snippet
                    desc = str(row['award_description'])[:150]
                    print(f"    Description: {desc}...")

        except Exception as e:
            pass

def main():
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)

    print("="*80)
    print("ADDITIONAL ENTITY INVESTIGATION")
    print("="*80)

    entities = [
        ("%CENTRAL PEOPLE'S GOVERNMENT%", "Central People's Government of PRC"),
        ("%FUDAN UNIVERSITY%", "Fudan University"),
        ("%REPUBLIC OF CHINA (TAIWAN)%", "Taiwan Government"),
        ("%NATIONAL TAIWAN UNIVERSITY%", "National Taiwan University"),
        ("%HONVEDELMI%", "Hungarian Ministry of Defense"),
        ("%GEORGE INSTITUTE%CHINA%", "The George Institute, China"),
    ]

    for pattern, label in entities:
        investigate_entity(conn, pattern, label)

    conn.close()

if __name__ == "__main__":
    main()
