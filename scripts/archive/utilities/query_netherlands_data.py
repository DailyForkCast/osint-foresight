#!/usr/bin/env python3
"""
Query Netherlands data across all available sources in OSINT master database.
"""

import sqlite3
import json
from collections import defaultdict

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

def query_netherlands_data():
    """Query all Netherlands-related data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    results = {}

    print("="*80)
    print("NETHERLANDS INTELLIGENCE DATA QUERY")
    print("="*80)

    # 1. CORDIS EU Research Projects
    print("\n1. CORDIS EU Research Projects (Netherlands involvement)")
    try:
        cursor.execute("""
            SELECT COUNT(DISTINCT p.project_id) as project_count,
                   COUNT(CASE WHEN cc.has_china = 1 THEN 1 END) as china_collab_count
            FROM cordis_projects p
            JOIN cordis_project_countries pc ON p.project_id = pc.project_id
            LEFT JOIN cordis_china_collaborations cc ON p.project_id = cc.project_id
            WHERE pc.country_code = 'NL'
        """)
        row = cursor.fetchone()
        results['cordis'] = {
            'total_projects': row[0] if row else 0,
            'china_collaborations': row[1] if row else 0
        }
        print(f"   Total Netherlands projects: {row[0] if row else 0}")
        print(f"   With China collaboration: {row[1] if row else 0}")
    except Exception as e:
        print(f"   Error: {e}")
        results['cordis'] = {'error': str(e)}

    # 2. TED EU Procurement
    print("\n2. TED EU Procurement Contracts (Netherlands)")
    try:
        cursor.execute("""
            SELECT COUNT(*) as total_contracts,
                   SUM(CASE WHEN chinese_entity_detected = 1 THEN 1 ELSE 0 END) as chinese_contracts
            FROM ted_contracts
            WHERE buyer_country = 'NL' OR buyer_country_code = 'NL'
        """)
        row = cursor.fetchone()
        results['ted'] = {
            'total_contracts': row[0] if row else 0,
            'chinese_contracts': row[1] if row else 0
        }
        print(f"   Total contracts: {row[0] if row else 0}")
        print(f"   Chinese contractor involvement: {row[1] if row else 0}")
    except Exception as e:
        print(f"   Error: {e}")
        results['ted'] = {'error': str(e)}

    # 3. USPTO Patents (Netherlands assignees)
    print("\n3. USPTO Patents (Netherlands assignees)")
    try:
        cursor.execute("""
            SELECT COUNT(DISTINCT patent_id) as total_patents,
                   COUNT(CASE WHEN has_chinese_involvement = 1 THEN 1 END) as chinese_collab
            FROM uspto_patents
            WHERE assignee_country = 'NL' OR assignee_country_code = 'NL'
        """)
        row = cursor.fetchone()
        results['uspto'] = {
            'total_patents': row[0] if row else 0,
            'chinese_involvement': row[1] if row else 0
        }
        print(f"   Total NL patents: {row[0] if row else 0}")
        print(f"   With Chinese involvement: {row[1] if row else 0}")
    except Exception as e:
        print(f"   Error: {e}")
        results['uspto'] = {'error': str(e)}

    # 4. OpenAIRE Research (if exists)
    print("\n4. OpenAIRE Research Collaborations")
    try:
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN is_china_collaboration = 1 THEN 1 ELSE 0 END) as china_collab
            FROM openaire_research_products
            WHERE country_code = 'NL'
        """)
        row = cursor.fetchone()
        results['openaire'] = {
            'total_products': row[0] if row else 0,
            'china_collaborations': row[1] if row else 0
        }
        print(f"   Total research products: {row[0] if row else 0}")
        print(f"   China collaborations: {row[1] if row else 0}")
    except Exception as e:
        print(f"   Error: {e}")
        results['openaire'] = {'error': str(e)}

    # 5. GLEIF Legal Entities (Netherlands)
    print("\n5. GLEIF Legal Entities (Netherlands-China connections)")
    try:
        cursor.execute("""
            SELECT COUNT(*) as total_entities,
                   COUNT(CASE WHEN parent_country = 'CN' THEN 1 END) as chinese_owned
            FROM gleif_lei_entities
            WHERE country = 'NL'
        """)
        row = cursor.fetchone()
        results['gleif'] = {
            'total_entities': row[0] if row else 0,
            'chinese_owned': row[1] if row else 0
        }
        print(f"   Total NL entities: {row[0] if row else 0}")
        print(f"   Chinese-owned: {row[1] if row else 0}")
    except Exception as e:
        print(f"   Error: {e}")
        results['gleif'] = {'error': str(e)}

    # 6. Bilateral Events (Netherlands-China)
    print("\n6. Bilateral Events (Netherlands-China)")
    try:
        cursor.execute("""
            SELECT COUNT(*) as total_events,
                   event_type,
                   COUNT(*) as count
            FROM bilateral_events
            WHERE country_code = 'NL' OR country_name LIKE '%Netherlands%'
            GROUP BY event_type
        """)
        rows = cursor.fetchall()
        results['bilateral_events'] = {
            'total': sum(r[2] for r in rows) if rows else 0,
            'by_type': {r[1]: r[2] for r in rows} if rows else {}
        }
        print(f"   Total events: {sum(r[2] for r in rows) if rows else 0}")
        for row in rows:
            print(f"      {row[1]}: {row[2]}")
    except Exception as e:
        print(f"   Error: {e}")
        results['bilateral_events'] = {'error': str(e)}

    # 7. Academic Partnerships
    print("\n7. Academic Partnerships (Netherlands-China)")
    try:
        cursor.execute("""
            SELECT COUNT(*) as partnerships
            FROM academic_partnerships
            WHERE (country_a = 'NL' AND country_b = 'CN')
               OR (country_a = 'CN' AND country_b = 'NL')
        """)
        row = cursor.fetchone()
        results['academic_partnerships'] = {
            'total': row[0] if row else 0
        }
        print(f"   Total NL-China partnerships: {row[0] if row else 0}")
    except Exception as e:
        print(f"   Error: {e}")
        results['academic_partnerships'] = {'error': str(e)}

    # 8. ASPI Infrastructure (Chinese companies in Netherlands)
    print("\n8. ASPI China Tech Infrastructure (Netherlands)")
    try:
        cursor.execute("""
            SELECT COUNT(*) as total,
                   company_name,
                   infrastructure_type,
                   COUNT(*) as count
            FROM aspi_infrastructure
            WHERE country_code = 'NL' OR country_name LIKE '%Netherlands%'
            GROUP BY company_name, infrastructure_type
        """)
        rows = cursor.fetchall()
        results['aspi'] = {
            'total': len(rows),
            'details': [{'company': r[1], 'type': r[2], 'count': r[3]} for r in rows]
        }
        print(f"   Total infrastructure records: {len(rows)}")
        for row in rows:
            print(f"      {row[1]} - {row[2]}: {row[3]}")
    except Exception as e:
        print(f"   Error: {e}")
        results['aspi'] = {'error': str(e)}

    # 9. Semiconductor-specific data
    print("\n9. Semiconductor Market Data (Netherlands context)")
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM semiconductor_equipment_suppliers
            WHERE country = 'Netherlands' OR company_name LIKE '%ASML%'
        """)
        row = cursor.fetchone()
        results['semiconductor'] = {
            'equipment_suppliers': row[0] if row else 0
        }
        print(f"   Semiconductor equipment suppliers: {row[0] if row else 0}")
    except Exception as e:
        print(f"   Error: {e}")
        results['semiconductor'] = {'error': str(e)}

    # 10. Check for any Netherlands entities in monitoring lists
    print("\n10. Export Control & Sanctions (Netherlands entities)")
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM bis_entity_list
            WHERE country LIKE '%Netherlands%' OR address LIKE '%Netherlands%'
        """)
        row = cursor.fetchone()
        results['bis_entity_list'] = {
            'netherlands_entities': row[0] if row else 0
        }
        print(f"   Netherlands entities on BIS list: {row[0] if row else 0}")
    except Exception as e:
        print(f"   Error: {e}")
        results['bis_entity_list'] = {'error': str(e)}

    conn.close()

    # Summary
    print("\n" + "="*80)
    print("SUMMARY: Netherlands Data Coverage")
    print("="*80)
    total_records = 0
    for source, data in results.items():
        if isinstance(data, dict) and 'error' not in data:
            count = data.get('total', data.get('total_projects', data.get('total_entities', 0)))
            if count:
                print(f"{source}: {count:,} records")
                total_records += count

    print(f"\nTotal records across all sources: {total_records:,}")

    # Save to JSON
    output_file = "analysis/netherlands_data_coverage.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {output_file}")

    return results

if __name__ == "__main__":
    query_netherlands_data()
