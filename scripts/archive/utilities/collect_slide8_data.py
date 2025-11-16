#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collect comprehensive data for Slide 8 (Case Studies) enrichment
Entities: SenseTime, Megvii, BGI, USTC, CASIC
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
    'slide_8_case_studies': {}
}

print("\n" + "="*80)
print("SLIDE 8 DATA COLLECTION - CASE STUDIES")
print("="*80)

# ============================================================================
# Entity 1: SenseTime (商汤科技)
# ============================================================================
print("\n[1/5] SenseTime - AI/Surveillance")
sensetime_data = {}

# BIS Entity List
cursor.execute("""
SELECT entity_name, technology_focus, reason_for_inclusion, risk_score, effective_date, address
FROM bis_entity_list_fixed
WHERE entity_name LIKE '%SenseTime%'
""")
bis_data = cursor.fetchone()
if bis_data:
    sensetime_data['bis_entity_list'] = {
        'name': bis_data[0],
        'tech_focus': bis_data[1],
        'reason': bis_data[2],
        'risk_score': bis_data[3],
        'listing_date': bis_data[4],
        'address': bis_data[5]
    }
    print(f"  [BIS] Risk Score: {bis_data[3]}, Reason: {bis_data[2]}")

# Entity linkages
cursor.execute("""
SELECT entity_type, connection_type, risk_score, notes
FROM entity_linkages
WHERE entity_name LIKE '%SenseTime%' OR entity_name LIKE '%商汤%'
LIMIT 10
""")
linkages = cursor.fetchall()
if linkages:
    sensetime_data['entity_linkages'] = [
        {'type': l[0], 'connection': l[1], 'risk': l[2], 'notes': l[3]}
        for l in linkages
    ]
    print(f"  [Linkages] Found {len(linkages)} entity connections")

results['slide_8_case_studies']['SenseTime'] = sensetime_data

# ============================================================================
# Entity 2: Megvii (Face++) (旷视科技)
# ============================================================================
print("\n[2/5] Megvii (Face++) - Facial Recognition/AI")
megvii_data = {}

# BIS Entity List
cursor.execute("""
SELECT entity_name, technology_focus, reason_for_inclusion, risk_score, effective_date, address
FROM bis_entity_list_fixed
WHERE entity_name LIKE '%Megvii%' OR entity_name LIKE '%Face++%'
""")
bis_data = cursor.fetchone()
if bis_data:
    megvii_data['bis_entity_list'] = {
        'name': bis_data[0],
        'tech_focus': bis_data[1],
        'reason': bis_data[2],
        'risk_score': bis_data[3],
        'listing_date': bis_data[4],
        'address': bis_data[5]
    }
    print(f"  [BIS] Risk Score: {bis_data[3]}, Reason: {bis_data[2]}")

# Entity linkages
cursor.execute("""
SELECT entity_type, connection_type, risk_score, notes
FROM entity_linkages
WHERE entity_name LIKE '%Megvii%' OR entity_name LIKE '%旷视%'
LIMIT 10
""")
linkages = cursor.fetchall()
if linkages:
    megvii_data['entity_linkages'] = [
        {'type': l[0], 'connection': l[1], 'risk': l[2], 'notes': l[3]}
        for l in linkages
    ]
    print(f"  [Linkages] Found {len(linkages)} entity connections")

results['slide_8_case_studies']['Megvii'] = megvii_data

# ============================================================================
# Entity 3: BGI (华大基因)
# ============================================================================
print("\n[3/5] BGI (Beijing Genomics Institute) - Biotechnology")
bgi_data = {}

# BIS Entity List
cursor.execute("""
SELECT entity_name, technology_focus, reason_for_inclusion, risk_score, effective_date, address
FROM bis_entity_list_fixed
WHERE entity_name LIKE '%BGI%' OR entity_name LIKE '%Beijing Genomics%'
""")
bis_data = cursor.fetchone()
if bis_data:
    bgi_data['bis_entity_list'] = {
        'name': bis_data[0],
        'tech_focus': bis_data[1],
        'reason': bis_data[2],
        'risk_score': bis_data[3],
        'listing_date': bis_data[4],
        'address': bis_data[5]
    }
    print(f"  [BIS] Risk Score: {bis_data[3]}, Reason: {bis_data[2]}")

# Entity linkages
cursor.execute("""
SELECT entity_type, connection_type, risk_score, notes
FROM entity_linkages
WHERE entity_name LIKE '%BGI%' OR entity_name LIKE '%华大基因%'
LIMIT 10
""")
linkages = cursor.fetchall()
if linkages:
    bgi_data['entity_linkages'] = [
        {'type': l[0], 'connection': l[1], 'risk': l[2], 'notes': l[3]}
        for l in linkages
    ]
    print(f"  [Linkages] Found {len(linkages)} entity connections")

results['slide_8_case_studies']['BGI'] = bgi_data

# ============================================================================
# Entity 4: USTC (中国科学技术大学)
# ============================================================================
print("\n[4/5] USTC (University of Science and Technology of China) - Quantum/AI Research")
ustc_data = {}

# OpenAlex institution data
cursor.execute("""
SELECT display_name, country_code, works_count, cited_by_count
FROM import_openalex_institutions
WHERE display_name LIKE '%University of Science and Technology of China%'
""")
openalex_data = cursor.fetchone()
if openalex_data:
    ustc_data['openalex_institution'] = {
        'name': openalex_data[0],
        'country': openalex_data[1],
        'total_works': openalex_data[2],
        'total_citations': openalex_data[3]
    }
    print(f"  [OpenAlex] Works: {openalex_data[2]}, Citations: {openalex_data[3]}")

# Check for high-risk collaborations
cursor.execute("""
SELECT author_name, institution_name, technology_sector, risk_score
FROM openalex_china_high_risk
WHERE institution_name LIKE '%USTC%' OR institution_name LIKE '%中国科学技术大学%'
LIMIT 10
""")
high_risk = cursor.fetchall()
if high_risk:
    ustc_data['high_risk_collaborations'] = [
        {'author': hr[0], 'institution': hr[1], 'sector': hr[2], 'risk': hr[3]}
        for hr in high_risk
    ]
    print(f"  [High-Risk] Found {len(high_risk)} flagged collaborations")

# Entity linkages
cursor.execute("""
SELECT entity_type, connection_type, risk_score, notes
FROM entity_linkages
WHERE entity_name LIKE '%USTC%' OR entity_name LIKE '%中国科学技术大学%'
LIMIT 10
""")
linkages = cursor.fetchall()
if linkages:
    ustc_data['entity_linkages'] = [
        {'type': l[0], 'connection': l[1], 'risk': l[2], 'notes': l[3]}
        for l in linkages
    ]
    print(f"  [Linkages] Found {len(linkages)} entity connections")

results['slide_8_case_studies']['USTC'] = ustc_data

# ============================================================================
# Entity 5: CASIC (中国航天科工集团)
# ============================================================================
print("\n[5/5] CASIC (China Aerospace Science and Industry Corp) - Defense/Space")
casic_data = {}

# BIS Entity List
cursor.execute("""
SELECT entity_name, technology_focus, reason_for_inclusion, risk_score, effective_date, address
FROM bis_entity_list_fixed
WHERE entity_name LIKE '%CASIC%' OR entity_name LIKE '%China Aerospace Science and Industry%'
""")
bis_data = cursor.fetchone()
if bis_data:
    casic_data['bis_entity_list'] = {
        'name': bis_data[0],
        'tech_focus': bis_data[1],
        'reason': bis_data[2],
        'risk_score': bis_data[3],
        'listing_date': bis_data[4],
        'address': bis_data[5]
    }
    print(f"  [BIS] Risk Score: {bis_data[3]}, Reason: {bis_data[2]}")

# Entity linkages
cursor.execute("""
SELECT entity_type, connection_type, risk_score, notes
FROM entity_linkages
WHERE entity_name LIKE '%CASIC%' OR entity_name LIKE '%航天科工%'
LIMIT 10
""")
linkages = cursor.fetchall()
if linkages:
    casic_data['entity_linkages'] = [
        {'type': l[0], 'connection': l[1], 'risk': l[2], 'notes': l[3]}
        for l in linkages
    ]
    print(f"  [Linkages] Found {len(linkages)} entity connections")

results['slide_8_case_studies']['CASIC'] = casic_data

# ============================================================================
# Additional context: Cross-system analysis
# ============================================================================
print("\n[ADDITIONAL] Checking cross-system entity correlations...")
cursor.execute("""
SELECT entity_name, total_appearances, system_count, risk_indicators
FROM cross_system_entity_correlation
WHERE entity_name LIKE '%SenseTime%'
   OR entity_name LIKE '%Megvii%'
   OR entity_name LIKE '%BGI%'
   OR entity_name LIKE '%USTC%'
   OR entity_name LIKE '%CASIC%'
LIMIT 10
""")
cross_system = cursor.fetchall()
if cross_system:
    results['cross_system_analysis'] = [
        {
            'entity': cs[0],
            'appearances': cs[1],
            'systems': cs[2],
            'risk_indicators': cs[3]
        }
        for cs in cross_system
    ]
    print(f"  [Cross-System] Found {len(cross_system)} entities with multi-system presence")

# ============================================================================
# Export results
# ============================================================================
output_file = 'slide8_data_collected.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n" + "="*80)
print("DATA COLLECTION COMPLETE")
print("="*80)
print(f"\nResults exported to: {output_file}")
print(f"Entities with data: {len([v for v in results['slide_8_case_studies'].values() if v])}/5")

# Summary statistics
for entity, data in results['slide_8_case_studies'].items():
    print(f"\n{entity}:")
    print(f"  Data sources: {len(data)}")
    if 'bis_entity_list' in data:
        print(f"  BIS Risk Score: {data['bis_entity_list']['risk_score']}")
    if 'openalex_institution' in data:
        print(f"  OpenAlex Works: {data['openalex_institution']['total_works']}")

conn.close()
