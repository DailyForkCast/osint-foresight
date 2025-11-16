#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collect data for Slide 8 (Case Studies) enrichment - SIMPLIFIED
Focus on: BIS Entity List, OpenAlex, Cross-System Correlations
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
    'slide_8_case_studies': {},
    'enrichment_summary': {
        'purpose': 'Case studies showing civil-to-defense tech integration',
        'entities': ['SenseTime', 'Megvii', 'BGI', 'USTC', 'CASIC'],
        'data_sources': ['BIS Entity List', 'OpenAlex', 'Cross-System Correlations']
    }
}

print("\n" + "="*80)
print("SLIDE 8 DATA COLLECTION - CASE STUDIES")
print("="*80)

# ============================================================================
# Entity 1: SenseTime - AI/Surveillance
# ============================================================================
print("\n[1/5] SenseTime - AI/Surveillance")
sensetime = {'entity_name': 'SenseTime', 'category': 'AI/Surveillance', 'transition': 'Civil AI to PLA surveillance systems'}

cursor.execute("SELECT entity_name, technology_focus, reason_for_inclusion, risk_score, effective_date, address FROM bis_entity_list_fixed WHERE entity_name LIKE '%SenseTime%'")
bis_data = cursor.fetchone()
if bis_data:
    sensetime['bis'] = {'name': bis_data[0], 'tech': bis_data[1], 'reason': bis_data[2], 'risk': bis_data[3], 'date': bis_data[4], 'location': bis_data[5]}
    print(f"  [BIS] Risk: {bis_data[3]}, Reason: {bis_data[2]}")

results['slide_8_case_studies']['SenseTime'] = sensetime

# ============================================================================
# Entity 2: Megvii (Face++) - Facial Recognition/AI
# ============================================================================
print("\n[2/5] Megvii (Face++) - Facial Recognition/AI")
megvii = {'entity_name': 'Megvii', 'category': 'Facial Recognition/AI', 'transition': 'Facial recognition to security/surveillance applications'}

cursor.execute("SELECT entity_name, technology_focus, reason_for_inclusion, risk_score, effective_date, address FROM bis_entity_list_fixed WHERE entity_name LIKE '%Megvii%'")
bis_data = cursor.fetchone()
if bis_data:
    megvii['bis'] = {'name': bis_data[0], 'tech': bis_data[1], 'reason': bis_data[2], 'risk': bis_data[3], 'date': bis_data[4], 'location': bis_data[5]}
    print(f"  [BIS] Risk: {bis_data[3]}, Reason: {bis_data[2]}")

results['slide_8_case_studies']['Megvii'] = megvii

# ============================================================================
# Entity 3: BGI - Biotechnology
# ============================================================================
print("\n[3/5] BGI (Beijing Genomics Institute) - Biotechnology")
bgi = {'entity_name': 'BGI', 'category': 'Biotechnology', 'transition': 'Genomics research to PLA biodata collection'}

cursor.execute("SELECT entity_name, technology_focus, reason_for_inclusion, risk_score, effective_date, address FROM bis_entity_list_fixed WHERE entity_name LIKE '%BGI%'")
bis_data = cursor.fetchone()
if bis_data:
    bgi['bis'] = {'name': bis_data[0], 'tech': bis_data[1], 'reason': bis_data[2], 'risk': bis_data[3], 'date': bis_data[4], 'location': bis_data[5]}
    print(f"  [BIS] Risk: {bis_data[3]}, Reason: {bis_data[2]}")

results['slide_8_case_studies']['BGI'] = bgi

# ============================================================================
# Entity 4: USTC - Quantum/AI Research
# ============================================================================
print("\n[4/5] USTC (University of Science and Technology of China) - Quantum/AI")
ustc = {'entity_name': 'USTC', 'category': 'Academic/Research', 'transition': 'Quantum/AI research to PLA applications'}

cursor.execute("SELECT display_name, country_code, works_count, cited_by_count FROM import_openalex_institutions WHERE display_name LIKE '%University of Science and Technology of China%'")
openalex_data = cursor.fetchone()
if openalex_data:
    ustc['openalex'] = {'name': openalex_data[0], 'country': openalex_data[1], 'works': openalex_data[2], 'citations': openalex_data[3]}
    print(f"  [OpenAlex] Works: {openalex_data[2]}, Citations: {openalex_data[3]}")

# Check if USTC-related entities appear in cross-system
cursor.execute("SELECT normalized_entity_name, total_systems, max_risk_score FROM cross_system_entity_correlation WHERE normalized_entity_name LIKE '%USTC%' OR normalized_entity_name LIKE '%中国科学技术大学%' LIMIT 5")
cross = cursor.fetchall()
if cross:
    ustc['cross_system'] = [{'name': c[0], 'systems': c[1], 'risk': c[2]} for c in cross]
    print(f"  [Cross-System] Found in {cross[0][1]} systems")

results['slide_8_case_studies']['USTC'] = ustc

# ============================================================================
# Entity 5: CASIC - Defense/Space
# ============================================================================
print("\n[5/5] CASIC (China Aerospace Science and Industry Corp) - Defense/Space")
casic = {'entity_name': 'CASIC', 'category': 'State-Owned Defense', 'transition': 'Civilian space tech to military space systems'}

cursor.execute("SELECT entity_name, technology_focus, reason_for_inclusion, risk_score, effective_date, address FROM bis_entity_list_fixed WHERE entity_name LIKE '%CASIC%' OR entity_name LIKE '%China Aerospace Science and Industry%'")
bis_data = cursor.fetchone()
if bis_data:
    casic['bis'] = {'name': bis_data[0], 'tech': bis_data[1], 'reason': bis_data[2], 'risk': bis_data[3], 'date': bis_data[4], 'location': bis_data[5]}
    print(f"  [BIS] Risk: {bis_data[3]}, Reason: {bis_data[2]}")

results['slide_8_case_studies']['CASIC'] = casic

# ============================================================================
# Export
# ============================================================================
output_file = 'slide8_data_collected.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n" + "="*80)
print("DATA COLLECTION COMPLETE")
print("="*80)
print(f"\nExported to: {output_file}")
print("\nData Summary:")
for entity, data in results['slide_8_case_studies'].items():
    print(f"\n{entity} ({data['category']}):")
    print(f"  Transition: {data['transition']}")
    if 'bis' in data:
        print(f"  BIS Risk Score: {data['bis']['risk']}")
    if 'openalex' in data:
        print(f"  Research Output: {data['openalex']['works']} works")
    if 'cross_system' in data:
        print(f"  Multi-System Presence: {len(data['cross_system'])} records")

conn.close()
print("\n[READY] Data collected for Slide 8 enrichment script")
