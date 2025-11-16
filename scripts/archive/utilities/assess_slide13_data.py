#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assess data availability for Slide 13 (Gray-Zone Tech Acquisition)
Focus: University/company collaborations, legitimate activities vs MCF-leveraged outcomes
"""

import sqlite3
import json

db_path = 'F:/OSINT_WAREHOUSE/osint_master.db'
print(f"Connecting to: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

results = {
    'slide_13_assessment': {
        'purpose': 'Gray-zone tech acquisition - legitimate activities leveraged for MCF',
        'data_needs': [
            'EU-China research collaborations (CORDIS)',
            'University partnership patterns (OpenAlex)',
            'Zhongguancun (ZGC) entity activities',
            'Joint ventures and technology transfers'
        ]
    },
    'data_sources_found': [],
    'sample_data': {},
    'recommendations': []
}

print("\n" + "="*80)
print("SLIDE 13 DATA ASSESSMENT - GRAY-ZONE TECH ACQUISITION")
print("="*80)

# ============================================================================
# Check 1: CORDIS EU-China Projects
# ============================================================================
print("\n[1/5] Checking CORDIS EU-China research collaborations...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%cordis%'")
cordis_tables = cursor.fetchall()

if cordis_tables:
    print(f"  [OK] Found {len(cordis_tables)} CORDIS tables:")
    for table in cordis_tables:
        table_name = table[0]
        print(f"      - {table_name}")
        results['data_sources_found'].append(f"CORDIS: {table_name}")

        # Sample Chinese collaborations
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]
        print(f"        Total records: {total}")

        # Try to find China-related records
        cursor.execute(f"PRAGMA table_info({table_name})")
        cols = [c[1] for c in cursor.fetchall()]

        if 'country' in cols or 'country_code' in cols:
            country_col = 'country' if 'country' in cols else 'country_code'
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {country_col} LIKE '%CN%' OR {country_col} LIKE '%China%'")
            china_count = cursor.fetchone()[0]
            print(f"        China-related: {china_count}")
            results['sample_data']['cordis_china_count'] = china_count
else:
    print("  [X] No CORDIS tables found")

# ============================================================================
# Check 2: OpenAlex Collaborations
# ============================================================================
print("\n[2/5] Checking OpenAlex collaboration patterns...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%openalex%'")
openalex_tables = cursor.fetchall()

if openalex_tables:
    print(f"  [OK] Found {len(openalex_tables)} OpenAlex tables")

    # Check for collaboration/co-authorship data
    collab_tables = [t[0] for t in openalex_tables if 'collab' in t[0].lower() or 'china' in t[0].lower()]
    if collab_tables:
        print(f"  [OK] Found {len(collab_tables)} collaboration-specific tables:")
        for table in collab_tables:
            print(f"      - {table}")
            results['data_sources_found'].append(f"OpenAlex: {table}")

            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"        Records: {count}")

    # Check openalex_china_deep for collaboration patterns
    if 'openalex_china_deep' in [t[0] for t in openalex_tables]:
        cursor.execute("SELECT COUNT(*) FROM openalex_china_deep")
        deep_count = cursor.fetchone()[0]
        print(f"  [OK] openalex_china_deep: {deep_count} records")
        results['sample_data']['openalex_china_deep'] = deep_count

        # Sample some collaborations
        cursor.execute("""
        SELECT title, institutions, publication_year
        FROM openalex_china_deep
        WHERE institutions LIKE '%University%'
        LIMIT 5
        """)
        samples = cursor.fetchall()
        if samples:
            print(f"  [Sample] Found {len(samples)} university collaboration examples")
            results['sample_data']['collaboration_examples'] = len(samples)
else:
    print("  [X] No OpenAlex tables found")

# ============================================================================
# Check 3: Zhongguancun (ZGC) Activities
# ============================================================================
print("\n[3/5] Checking Zhongguancun (ZGC) entity data...")

# Search for ZGC/Zhongguancun in various tables
zgc_keywords = ['%Zhongguancun%', '%ZGC%', '%中关村%']
zgc_found = False

# Check BIS Entity List for ZGC entities
cursor.execute("""
SELECT entity_name, address, technology_focus
FROM bis_entity_list_fixed
WHERE entity_name LIKE '%Zhongguancun%' OR address LIKE '%Zhongguancun%'
LIMIT 10
""")
zgc_bis = cursor.fetchall()
if zgc_bis:
    print(f"  [OK] Found {len(zgc_bis)} ZGC entities in BIS Entity List")
    for entity in zgc_bis[:3]:
        print(f"      - {entity[0]}")
    results['sample_data']['zgc_bis_entities'] = len(zgc_bis)
    zgc_found = True

# Check SEC Edgar for ZGC
cursor.execute("""
SELECT name FROM sqlite_master
WHERE type='table' AND (name LIKE '%sec%' OR name LIKE '%edgar%')
""")
sec_tables = cursor.fetchall()
if sec_tables:
    # Try to find ZGC in SEC data
    cursor.execute("""
    SELECT company_name, country
    FROM sec_edgar_companies
    WHERE company_name LIKE '%Zhongguancun%' OR address LIKE '%Zhongguancun%'
    LIMIT 10
    """)
    zgc_sec = cursor.fetchall()
    if zgc_sec:
        print(f"  [OK] Found {len(zgc_sec)} ZGC entities in SEC Edgar")
        results['sample_data']['zgc_sec_entities'] = len(zgc_sec)
        zgc_found = True

if not zgc_found:
    print("  [X] No specific ZGC entity data found")

# ============================================================================
# Check 4: Joint Ventures / Technology Transfer
# ============================================================================
print("\n[4/5] Checking joint venture / technology transfer data...")

# Check if there are tables with JV or tech transfer data
cursor.execute("""
SELECT name FROM sqlite_master
WHERE type='table' AND (
    name LIKE '%venture%' OR
    name LIKE '%transfer%' OR
    name LIKE '%partnership%' OR
    name LIKE '%joint%'
)
""")
jv_tables = cursor.fetchall()

if jv_tables:
    print(f"  [OK] Found {len(jv_tables)} tables with joint venture/transfer data:")
    for table in jv_tables:
        print(f"      - {table[0]}")
        results['data_sources_found'].append(f"JV/Transfer: {table[0]}")
else:
    print("  [X] No specific JV/tech transfer tables found")

# Check entity linkages for cross-border partnerships
cursor.execute("""
SELECT COUNT(*) FROM entity_linkages
WHERE (source1_type = 'sec_edgar' AND source2_type LIKE '%china%')
   OR (source2_type = 'sec_edgar' AND source1_type LIKE '%china%')
""")
cross_border_count = cursor.fetchone()[0]
if cross_border_count > 0:
    print(f"  [OK] Found {cross_border_count} cross-border entity linkages")
    results['sample_data']['cross_border_linkages'] = cross_border_count

# ============================================================================
# Check 5: Patent Collaborations
# ============================================================================
print("\n[5/5] Checking patent collaboration data...")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%patent%'")
patent_tables = cursor.fetchall()

if patent_tables:
    print(f"  [OK] Found {len(patent_tables)} patent tables")

    # Check for Chinese inventor collaborations with Western institutions
    cursor.execute("""
    SELECT COUNT(*) FROM intelligence_patents
    WHERE inventor_names LIKE '%China%' OR assignee_names LIKE '%China%'
    """)
    china_patents = cursor.fetchone()[0]
    if china_patents > 0:
        print(f"  [OK] Found {china_patents} patents with Chinese involvement")
        results['sample_data']['china_patents'] = china_patents

# ============================================================================
# Assessment Summary
# ============================================================================
print("\n" + "="*80)
print("ASSESSMENT SUMMARY")
print("="*80)

data_sources_count = len(results['data_sources_found'])
sample_data_count = len(results['sample_data'])

print(f"\nData sources available: {data_sources_count}")
print(f"Sample data points found: {sample_data_count}")

# Determine enrichment potential
if data_sources_count >= 3 and sample_data_count >= 3:
    potential = "HIGH"
    results['recommendations'].append("HIGH POTENTIAL: Multiple data sources with substantial records")
    print("\n[RECOMMENDATION] HIGH POTENTIAL for Slide 13 enrichment")
elif data_sources_count >= 2 or sample_data_count >= 2:
    potential = "MEDIUM"
    results['recommendations'].append("MEDIUM POTENTIAL: Some data available, may need supplementation")
    print("\n[RECOMMENDATION] MEDIUM POTENTIAL for Slide 13 enrichment")
else:
    potential = "LOW"
    results['recommendations'].append("LOW POTENTIAL: Limited data available")
    print("\n[RECOMMENDATION] LOW POTENTIAL for Slide 13 enrichment")

results['enrichment_potential'] = potential

# Specific recommendations
print("\nSpecific Recommendations:")
if 'cordis_china_count' in results['sample_data'] and results['sample_data']['cordis_china_count'] > 0:
    print(f"  - Use CORDIS data: {results['sample_data']['cordis_china_count']} China-related projects")
if 'openalex_china_deep' in results['sample_data']:
    print(f"  - Use OpenAlex collaborations: {results['sample_data']['openalex_china_deep']} deep analysis records")
if 'zgc_bis_entities' in results['sample_data']:
    print(f"  - Include ZGC examples: {results['sample_data']['zgc_bis_entities']} entities identified")
if 'china_patents' in results['sample_data']:
    print(f"  - Add patent collaboration examples: {results['sample_data']['china_patents']} patents available")

# Export
output_file = 'slide13_assessment.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nResults exported to: {output_file}")

conn.close()
