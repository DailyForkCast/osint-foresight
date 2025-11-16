#!/usr/bin/env python3
"""
Comprehensive Netherlands data query using actual database schema.
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

def query_netherlands():
    """Query all Netherlands data from verified tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    results = {
        'query_date': datetime.now().isoformat(),
        'country': 'Netherlands (NL)',
        'data_sources': {}
    }

    print("="*80)
    print("NETHERLANDS COMPREHENSIVE INTELLIGENCE ASSESSMENT")
    print("Data Query Results")
    print("="*80)

    # 1. CORDIS EU Research Projects
    print("\n1. CORDIS EU RESEARCH PROJECTS")
    print("-" * 40)
    cursor.execute('''
        SELECT COUNT(*) as total,
               SUM(CASE WHEN chinese_org IS NOT NULL THEN 1 ELSE 0 END) as with_china,
               SUM(funding_total) as total_funding,
               SUM(ec_contribution) as ec_funding
        FROM cordis_projects
        WHERE country_code = 'NL'
    ''')
    row = cursor.fetchone()
    results['data_sources']['cordis'] = {
        'total_projects': row[0],
        'projects_with_china': row[1],
        'total_funding_eur': float(row[2]) if row[2] else 0,
        'ec_contribution_eur': float(row[3]) if row[3] else 0
    }
    print(f"Total Netherlands projects: {row[0]:,}")
    print(f"Projects with Chinese orgs: {row[1]:,} ({row[1]/row[0]*100:.1f}%)")
    print(f"Total funding: €{row[2]:,.0f}" if row[2] else "Total funding: N/A")
    print(f"EC contribution: €{row[3]:,.0f}" if row[3] else "EC contribution: N/A")

    # Top Chinese organizations
    cursor.execute('''
        SELECT chinese_org, COUNT(*) as cnt, SUM(ec_contribution) as funding
        FROM cordis_projects
        WHERE country_code = 'NL' AND chinese_org IS NOT NULL
        GROUP BY chinese_org
        ORDER BY cnt DESC
        LIMIT 15
    ''')
    chinese_orgs = cursor.fetchall()
    results['data_sources']['cordis']['top_chinese_partners'] = [
        {'org': org, 'projects': cnt, 'funding': float(funding) if funding else 0}
        for org, cnt, funding in chinese_orgs
    ]
    print("\nTop 15 Chinese Organizations:")
    for org, cnt, funding in chinese_orgs:
        print(f"  {org}: {cnt} projects, €{funding:,.0f}" if funding else f"  {org}: {cnt} projects")

    # 2. GLEIF Legal Entities
    print("\n\n2. GLEIF LEGAL ENTITIES (Netherlands)")
    print("-" * 40)
    cursor.execute('''
        SELECT COUNT(*) FROM gleif_entities
        WHERE headquarters_country = 'NL' OR legal_jurisdiction = 'NL'
    ''')
    nl_entities = cursor.fetchone()[0]
    print(f"Netherlands legal entities: {nl_entities:,}")

    # Check for Chinese ownership
    cursor.execute('''
        SELECT COUNT(DISTINCT e.lei)
        FROM gleif_entities e
        JOIN gleif_relationships r ON e.lei = r.child_lei
        WHERE (e.headquarters_country = 'NL' OR e.legal_jurisdiction = 'NL')
          AND r.parent_country = 'CN'
    ''')
    chinese_owned = cursor.fetchone()[0]
    results['data_sources']['gleif'] = {
        'total_nl_entities': nl_entities,
        'chinese_owned_count': chinese_owned
    }
    print(f"With Chinese ownership: {chinese_owned:,}")

    # 3. ASPI China Tech Infrastructure
    print("\n\n3. ASPI CHINA TECH INFRASTRUCTURE (Netherlands)")
    print("-" * 40)
    cursor.execute('''
        SELECT company_name, infrastructure_type, COUNT(*) as cnt
        FROM aspi_infrastructure
        WHERE country = 'Netherlands' OR country_code = 'NL'
        GROUP BY company_name, infrastructure_type
        ORDER BY cnt DESC
    ''')
    aspi_data = cursor.fetchall()
    results['data_sources']['aspi'] = {
        'total_infrastructure': len(aspi_data),
        'details': [{'company': row[0], 'type': row[1], 'count': row[2]} for row in aspi_data]
    }
    print(f"Chinese infrastructure records: {len(aspi_data)}")
    if aspi_data:
        print("Infrastructure breakdown:")
        for company, infra_type, cnt in aspi_data:
            print(f"  {company} - {infra_type}: {cnt}")
    else:
        print("  No Chinese infrastructure detected in Netherlands")

    # 4. OpenAIRE Research Collaborations
    print("\n\n4. OPENAIRE RESEARCH COLLABORATIONS")
    print("-" * 40)
    cursor.execute('''
        PRAGMA table_info(openaire_collaborations)
    ''')
    cols = [c[1] for c in cursor.fetchall()]
    print(f"OpenAIRE columns: {', '.join(cols)}")

    # Try to query Netherlands
    cursor.execute('''
        SELECT COUNT(*) FROM openaire_collaborations
        WHERE country_a = 'NL' OR country_b = 'NL'
    ''')
    collab_count = cursor.fetchone()[0]
    print(f"Netherlands collaborations: {collab_count:,}")

    # Netherlands-China
    cursor.execute('''
        SELECT COUNT(*) FROM openaire_collaborations
        WHERE (country_a = 'NL' AND country_b = 'CN')
           OR (country_a = 'CN' AND country_b = 'NL')
    ''')
    nl_china_collab = cursor.fetchone()[0]
    results['data_sources']['openaire'] = {
        'total_collaborations': collab_count,
        'with_china': nl_china_collab
    }
    print(f"Netherlands-China collaborations: {nl_china_collab:,}")

    # 5. Bilateral Events
    print("\n\n5. BILATERAL EVENTS (Netherlands-China)")
    print("-" * 40)
    cursor.execute('''
        SELECT event_type, event_date, description
        FROM bilateral_events
        WHERE country_code = 'NL'
        ORDER BY event_date DESC
    ''')
    events = cursor.fetchall()
    results['data_sources']['bilateral_events'] = {
        'total': len(events),
        'events': [{'type': e[0], 'date': e[1], 'description': e[2]} for e in events]
    }
    print(f"Total events: {len(events)}")
    for event_type, date, desc in events:
        print(f"  {date}: {event_type} - {desc[:80]}...")

    # 6. Semiconductor Equipment Suppliers
    print("\n\n6. SEMICONDUCTOR EQUIPMENT (Netherlands)")
    print("-" * 40)
    cursor.execute('''
        SELECT company_name, equipment_type, market_share_pct, strategic_importance
        FROM semiconductor_equipment_suppliers
        WHERE company_name LIKE '%ASML%' OR country LIKE '%Nether%'
    ''')
    semi_data = cursor.fetchall()
    results['data_sources']['semiconductor'] = {
        'suppliers': [{'company': row[0], 'equipment': row[1], 'market_share': row[2], 'importance': row[3]}
                     for row in semi_data]
    }
    if semi_data:
        print(f"Found {len(semi_data)} semiconductor equipment suppliers:")
        for company, equip, share, importance in semi_data:
            print(f"  {company}: {equip} (Market share: {share}%, Importance: {importance})")
    else:
        print("No semiconductor data found (checking for ASML)")

    # 7. Patents
    print("\n\n7. PATENTS (Netherlands assignees)")
    print("-" * 40)
    cursor.execute('''
        PRAGMA table_info(patents)
    ''')
    patent_cols = [c[1] for c in cursor.fetchall()]
    print(f"Patent table columns: {', '.join(patent_cols[:10])}...")

    # Try to find Netherlands patents
    cursor.execute('''
        SELECT COUNT(*) FROM patents
        WHERE assignee_country = 'NL'
    ''')
    nl_patents = cursor.fetchone()[0]
    results['data_sources']['patents'] = {
        'total_nl_patents': nl_patents
    }
    print(f"Netherlands patents: {nl_patents:,}")

    # 8. BIS Entity List
    print("\n\n8. BIS ENTITY LIST (Export Controls)")
    print("-" * 40)
    cursor.execute('''
        SELECT name, country FROM bis_entity_list
        WHERE country LIKE '%Nether%' OR name LIKE '%ASML%' OR name LIKE '%Nether%'
    ''')
    bis_entities = cursor.fetchall()
    results['data_sources']['bis'] = {
        'netherlands_entities': len(bis_entities),
        'entities': [{'name': row[0], 'country': row[1]} for row in bis_entities]
    }
    if bis_entities:
        print(f"Netherlands entities on BIS list: {len(bis_entities)}")
        for name, country in bis_entities:
            print(f"  {name} ({country})")
    else:
        print("No Netherlands entities on BIS list")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY: Netherlands Data Coverage Assessment")
    print("="*80)

    summary_stats = []
    for source, data in results['data_sources'].items():
        if isinstance(data, dict):
            key_metric = None
            if 'total_projects' in data:
                key_metric = f"{data['total_projects']:,} projects"
            elif 'total_nl_entities' in data:
                key_metric = f"{data['total_nl_entities']:,} entities"
            elif 'total_infrastructure' in data:
                key_metric = f"{data['total_infrastructure']} infrastructure"
            elif 'total_collaborations' in data:
                key_metric = f"{data['total_collaborations']:,} collaborations"
            elif 'total' in data:
                key_metric = f"{data['total']} events"

            if key_metric:
                summary_stats.append(f"{source.upper()}: {key_metric}")

    for stat in summary_stats:
        print(f"✓ {stat}")

    # Key Finding
    print("\n" + "="*80)
    print("KEY FINDINGS")
    print("="*80)
    print(f"✓ {results['data_sources']['cordis']['projects_with_china']:,} EU-funded research projects involve Chinese organizations")
    print(f"✓ {results['data_sources']['openaire']['with_china']:,} Netherlands-China research collaborations detected")
    print(f"✓ {results['data_sources']['gleif']['total_nl_entities']:,} Netherlands legal entities in global database")
    print(f"✓ ASML semiconductor equipment data {'AVAILABLE' if semi_data else 'NEEDS VERIFICATION'}")

    # Save results
    output_file = "analysis/netherlands_comprehensive_data.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nComplete results saved to: {output_file}")

    conn.close()
    return results

if __name__ == "__main__":
    query_netherlands()
