#!/usr/bin/env python3
"""
investigate_flagged_entities.py - Investigate Flagged TIER_2 Entities

Checks detection reasons and details for entities flagged in manual review.
"""

import sqlite3
import pandas as pd
import json

def investigate_entity(conn, entity_name):
    """Look up entity and show detection details"""

    # Search across all tables
    tables = ['usaspending_china_305', 'usaspending_china_101', 'usaspending_china_comprehensive']

    results = []

    for table in tables:
        try:
            query = f"""
                SELECT
                    recipient_name,
                    award_description,
                    detection_types,
                    detection_details,
                    highest_confidence,
                    importance_tier
                FROM {table}
                WHERE recipient_name LIKE '%{entity_name}%'
                LIMIT 5
            """

            df = pd.read_sql(query, conn)
            if len(df) > 0:
                results.append({
                    'table': table,
                    'records': df.to_dict('records')
                })
        except:
            pass

    return results

def check_bis_entity_list(conn, entity_name):
    """Check if entity is on BIS Entity List"""

    try:
        query = """
            SELECT entity_name, federal_register_notice, country
            FROM bis_entity_list
            WHERE entity_name LIKE ?
        """

        df = pd.read_sql(query, conn, params=(f'%{entity_name}%',))
        return df.to_dict('records')
    except:
        return []

def main():
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)

    # Entities to investigate
    entities = {
        'SINOVA': 'SINOVA SICHERHEIT & TECHNIK',
        'PERISSINOTTO': 'FP PERISSINOTTO',
        'FIAT': 'FIAT SPA',
        'IVECO': 'IVECO MAGIRUS',
        'GUANGZHOU HENGDA': 'GUANGZHOU HENGDA SHIYOU',
        'CHINA SOUTH LOCOMOTIVE': 'CHINA SOUTH LOCOMOTIVE',
        'BEIJING INSTITUTE OF GENOMICS': 'BEIJING INSTITUTE OF GENOMICS',
        'SINOASIA': 'SINOASIA B&R'
    }

    print("="*80)
    print("FLAGGED ENTITY INVESTIGATION")
    print("="*80)

    for key, entity in entities.items():
        print(f"\n{'='*80}")
        print(f"ENTITY: {entity}")
        print("="*80)

        # Check database
        results = investigate_entity(conn, entity)

        if not results:
            print(f"  [!] NOT FOUND in database")
            continue

        for result in results:
            print(f"\n  Table: {result['table']}")
            print(f"  Records found: {len(result['records'])}")

            for i, record in enumerate(result['records'][:2], 1):  # Show first 2
                print(f"\n  Record {i}:")
                print(f"    Name: {record['recipient_name']}")
                print(f"    Tier: {record['importance_tier']}")
                print(f"    Confidence: {record['highest_confidence']}")
                print(f"    Detection Types: {record['detection_types']}")

                # Parse detection details
                try:
                    details = json.loads(record['detection_details']) if record['detection_details'] else {}
                    if details:
                        print(f"    Detection Details:")
                        for det_type, det_info in details.items():
                            print(f"      - {det_type}: {det_info}")
                except:
                    pass

                # Show snippet of description
                desc = str(record['award_description'])[:200]
                print(f"    Description: {desc}...")

        # Check BIS
        print(f"\n  BIS Entity List Check:")
        bis_results = check_bis_entity_list(conn, entity)
        if bis_results:
            print(f"    [!] FOUND ON BIS ENTITY LIST!")
            for bis_record in bis_results:
                print(f"      - {bis_record['entity_name']} ({bis_record['country']})")
                print(f"        Federal Register: {bis_record['federal_register_notice']}")
        else:
            print(f"    [ ] Not on BIS Entity List")

    print("\n" + "="*80)
    print("INVESTIGATION COMPLETE")
    print("="*80)

    conn.close()

if __name__ == "__main__":
    main()
