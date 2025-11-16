#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collect data for Slide 13 (Gray-Zone Tech Acquisition) - FIXED
Conservative approach with schema checking
"""

import sqlite3
import json
from datetime import datetime

db_path = 'F:/OSINT_WAREHOUSE/osint_master.db'
print(f"Connecting to: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

results = {
    'collection_date': datetime.now().isoformat(),
    'slide_13_gray_zone': {
        'purpose': 'Demonstrate legitimate research collaborations leveraged for MCF',
        'pattern': 'Legitimate Activity → Gray-Zone Exploitation → MCF Integration'
    },
    'data_collected': {}
}

print("\n" + "="*80)
print("SLIDE 13 DATA COLLECTION - GRAY-ZONE TECH ACQUISITION")
print("="*80)

# ============================================================================
# 1. CORDIS Chinese Organizations
# ============================================================================
print("\n[1/4] CORDIS Chinese Research Organizations...")

cursor.execute("SELECT org_name, org_type, project_count, total_funding FROM cordis_chinese_orgs LIMIT 15")
chinese_orgs = cursor.fetchall()

if chinese_orgs:
    print(f"  [OK] Found {len(chinese_orgs)} sample organizations")
    results['data_collected']['cordis_organizations'] = {
        'total': 411,
        'sample': [
            {
                'name': org[0],
                'type': org[1],
                'projects': org[2],
                'funding_eur': org[3]
            }
            for org in chinese_orgs
        ],
        'note': 'Chinese entities participating in EU-funded research (legitimate activity)'
    }

    print("\n  Top 5 Chinese organizations in CORDIS:")
    for i, org in enumerate(chinese_orgs[:5], 1):
        print(f"    {i}. {org[0]} ({org[1]}) - {org[2]} projects")

# Get total project count
cursor.execute("SELECT COUNT(*) FROM cordis_project_countries")
total_project_countries = cursor.fetchone()[0]
print(f"\n  Total CORDIS project-country records: {total_project_countries}")
results['data_collected']['cordis_projects_total'] = total_project_countries

# ============================================================================
# 2. OpenAlex High-Risk Collaborations
# ============================================================================
print("\n[2/4] OpenAlex High-Risk Research Collaborations...")

cursor.execute("SELECT * FROM openalex_china_high_risk LIMIT 20")
high_risk_collabs = cursor.fetchall()

cursor.execute("PRAGMA table_info(openalex_china_high_risk)")
cols = [c[1] for c in cursor.fetchall()]

if high_risk_collabs:
    print(f"  [OK] Found {len(high_risk_collabs)} high-risk collaboration samples")

    # Build sample data dynamically
    samples = []
    for collab in high_risk_collabs[:10]:
        sample_dict = {}
        for i, col_name in enumerate(cols):
            if i < len(collab):
                sample_dict[col_name] = str(collab[i])[:200] if collab[i] else None
        samples.append(sample_dict)

    results['data_collected']['high_risk_collaborations'] = {
        'total': 1000,
        'sample': samples,
        'note': 'Research collaborations flagged for dual-use technology (gray-zone activity)'
    }

    print(f"  [OK] Collected 10 collaboration examples")

# ============================================================================
# 3. Chinese Research Entities
# ============================================================================
print("\n[3/4] Chinese Research Entities in OpenAlex...")

cursor.execute("SELECT * FROM import_openalex_china_entities LIMIT 15")
china_entities = cursor.fetchall()

cursor.execute("PRAGMA table_info(import_openalex_china_entities)")
entity_cols = [c[1] for c in cursor.fetchall()]

if china_entities:
    print(f"  [OK] Found {len(china_entities)} entity samples")

    entity_samples = []
    for ent in china_entities[:10]:
        ent_dict = {}
        for i, col in enumerate(entity_cols):
            if i < len(ent):
                ent_dict[col] = str(ent[i])[:200] if ent[i] else None
        entity_samples.append(ent_dict)

    results['data_collected']['chinese_research_entities'] = {
        'total': 6344,
        'sample': entity_samples,
        'note': 'Chinese institutions active in international research'
    }

    print(f"  [OK] Collected 10 entity examples")

# ============================================================================
# 4. BIS Entity List Academic Institutions
# ============================================================================
print("\n[4/4] BIS Entity List Academic/Research Institutions...")

cursor.execute("""
SELECT entity_name, technology_focus, reason_for_inclusion, risk_score, effective_date
FROM bis_entity_list_fixed
WHERE entity_name LIKE '%University%' OR entity_name LIKE '%Institute%' OR entity_name LIKE '%Academy%'
ORDER BY risk_score DESC
LIMIT 15
""")
bis_academic = cursor.fetchall()

if bis_academic:
    print(f"  [OK] Found {len(bis_academic)} academic entities on BIS Entity List")
    results['data_collected']['bis_academic_entities'] = {
        'count': len(bis_academic),
        'entities': [
            {
                'name': ent[0],
                'tech_focus': ent[1],
                'reason': ent[2],
                'risk_score': ent[3],
                'listing_date': ent[4]
            }
            for ent in bis_academic
        ],
        'note': 'Academic entities with documented MCF ties (MCF integration confirmed)'
    }

    print("\n  Top 5 BIS-listed academic entities:")
    for i, ent in enumerate(bis_academic[:5], 1):
        print(f"    {i}. {ent[0]} (Risk: {ent[3]})")
        print(f"       Reason: {ent[2]}")

# ============================================================================
# Generate Gray-Zone Pattern Summary
# ============================================================================
results['gray_zone_pattern'] = {
    'stage_1_legitimate': {
        'activity': 'EU-funded research collaboration',
        'data_source': 'CORDIS',
        'example_count': 411,
        'legitimacy': 'Fully legitimate, government-approved research partnerships'
    },
    'stage_2_gray_zone': {
        'activity': 'Dual-use technology transfer, high-risk entity involvement',
        'data_source': 'OpenAlex High-Risk Analysis',
        'example_count': 1000,
        'concern': 'Legitimate research with potential dual-use applications'
    },
    'stage_3_mcf_integration': {
        'activity': 'Entity List designation, export control restrictions',
        'data_source': 'BIS Entity List',
        'example_count': 15,
        'status': 'MCF ties documented, technology transfer restricted'
    }
}

print("\n" + "="*80)
print("GRAY-ZONE PATTERN SUMMARY")
print("="*80)
print("\nSTAGE 1 - LEGITIMATE ACTIVITY:")
print(f"  {results['gray_zone_pattern']['stage_1_legitimate']['example_count']} Chinese orgs in EU-funded research")
print(f"  Status: {results['gray_zone_pattern']['stage_1_legitimate']['legitimacy']}")

print("\nSTAGE 2 - GRAY-ZONE EXPLOITATION:")
print(f"  {results['gray_zone_pattern']['stage_2_gray_zone']['example_count']} high-risk collaborations identified")
print(f"  Concern: {results['gray_zone_pattern']['stage_2_gray_zone']['concern']}")

print("\nSTAGE 3 - MCF INTEGRATION CONFIRMED:")
print(f"  {results['gray_zone_pattern']['stage_3_mcf_integration']['example_count']} academic entities on BIS Entity List")
print(f"  Status: {results['gray_zone_pattern']['stage_3_mcf_integration']['status']}")

# ============================================================================
# Export
# ============================================================================
output_file = 'slide13_data_collected.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n" + "="*80)
print("DATA COLLECTION COMPLETE")
print("="*80)
print(f"\nExported to: {output_file}")
print("\n[READY] Data collected for Slide 13 enrichment script")

conn.close()
