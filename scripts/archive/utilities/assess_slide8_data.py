#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assess data availability for Slide 8 (Case Studies) enrichment
Target entities: SenseTime, Megvii, BGI, USTC, CASIC
"""

import sqlite3
import json

db_path = 'F:/OSINT_WAREHOUSE/osint_master.db'
print(f"Connecting to: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Target entities for Slide 8
target_entities = ['SenseTime', 'Megvii', 'BGI', 'USTC', 'CASIC']

results = {
    'slide_8_case_studies': {},
    'data_sources_found': [],
    'recommendations': []
}

print("\n" + "="*80)
print("SLIDE 8 DATA ASSESSMENT - CASE STUDIES")
print("="*80)

# Check BIS Entity List for these entities
print("\n[1/5] Checking BIS Entity List...")
for entity in target_entities:
    cursor.execute("""
    SELECT entity_name, technology_focus, reason_for_inclusion, risk_score, effective_date
    FROM bis_entity_list_fixed
    WHERE entity_name LIKE ?
    LIMIT 5
    """, (f'%{entity}%',))

    matches = cursor.fetchall()
    if matches:
        print(f"  [OK] Found {len(matches)} matches for {entity}")
        results['slide_8_case_studies'][entity] = {
            'bis_entity_list': [
                {
                    'name': m[0],
                    'tech_focus': m[1],
                    'reason': m[2],
                    'risk_score': m[3],
                    'date': m[4]
                } for m in matches
            ]
        }
    else:
        print(f"  [X] No matches for {entity}")
        results['slide_8_case_studies'][entity] = {}

# Check for SEC Edgar data
print("\n[2/5] Checking SEC Edgar data...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%sec%' OR name LIKE '%edgar%'")
sec_tables = cursor.fetchall()
if sec_tables:
    print(f"  [OK] Found {len(sec_tables)} SEC-related tables:")
    for table in sec_tables:
        print(f"      - {table[0]}")
        results['data_sources_found'].append(f"SEC table: {table[0]}")
else:
    print("  [X] No SEC Edgar tables found")

# Check for USPTO patent data
print("\n[3/5] Checking USPTO patent data...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%patent%' OR name LIKE '%uspto%'")
patent_tables = cursor.fetchall()
if patent_tables:
    print(f"  [OK] Found {len(patent_tables)} patent-related tables:")
    for table in patent_tables[:5]:  # Show first 5
        print(f"      - {table[0]}")
    results['data_sources_found'].append(f"USPTO tables: {len(patent_tables)} found")
else:
    print("  [X] No USPTO patent tables found")

# Check for OpenAlex data
print("\n[4/5] Checking OpenAlex data...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%openalex%'")
openalex_tables = cursor.fetchall()
if openalex_tables:
    print(f"  [OK] Found {len(openalex_tables)} OpenAlex-related tables:")
    for table in openalex_tables[:5]:
        print(f"      - {table[0]}")
    results['data_sources_found'].append(f"OpenAlex tables: {len(openalex_tables)} found")

    # Check USTC specifically in OpenAlex
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%openalex%institution%'")
    inst_tables = cursor.fetchall()
    if inst_tables:
        table_name = inst_tables[0][0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE display_name LIKE '%University of Science and Technology of China%'")
        ustc_count = cursor.fetchone()[0]
        print(f"      USTC in {table_name}: {ustc_count} records")
else:
    print("  [X] No OpenAlex tables found")

# Check for entity cross-reference tables
print("\n[5/5] Checking entity cross-reference tables...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%entity%' OR name LIKE '%cross%ref%'")
entity_tables = cursor.fetchall()
if entity_tables:
    print(f"  [OK] Found {len(entity_tables)} entity-related tables:")
    for table in entity_tables[:10]:
        print(f"      - {table[0]}")
    results['data_sources_found'].append(f"Entity tables: {len(entity_tables)} found")
else:
    print("  [X] No entity cross-reference tables found")

# Summary and recommendations
print("\n" + "="*80)
print("ASSESSMENT SUMMARY")
print("="*80)

entities_with_data = sum(1 for e in results['slide_8_case_studies'].values() if e)
print(f"\nEntities with available data: {entities_with_data}/{len(target_entities)}")
print(f"Total data sources found: {len(results['data_sources_found'])}")

if entities_with_data >= 3:
    results['recommendations'].append("HIGH POTENTIAL: Sufficient data for meaningful enrichment")
    print("\n[RECOMMENDATION] HIGH POTENTIAL for Slide 8 enrichment")
elif entities_with_data >= 1:
    results['recommendations'].append("MEDIUM POTENTIAL: Partial data available")
    print("\n[RECOMMENDATION] MEDIUM POTENTIAL for Slide 8 enrichment")
else:
    results['recommendations'].append("LOW POTENTIAL: Limited data available")
    print("\n[RECOMMENDATION] LOW POTENTIAL for Slide 8 enrichment")

# Export results
output_file = 'slide8_assessment.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nResults exported to: {output_file}")

conn.close()
