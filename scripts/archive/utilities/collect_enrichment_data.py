#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collect enrichment data for MCF/NQPF presentation high-priority slides
Handles encoding issues and exports JSON for enrichment scripts
"""

import sqlite3
import json
import sys

# Force UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

db_path = 'F:/OSINT_WAREHOUSE/osint_master.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

enrichment_data = {}

print("="*80)
print("COLLECTING ENRICHMENT DATA")
print("="*80)

# ========== SLIDE 10: HIT/NPU CASES ==========
print("\n[SLIDE 10] HIT/NPU Entity List Status...")

# Check BIS Entity List for HIT and NPU
cursor.execute("""
SELECT entity_name, address, reason_for_inclusion, technology_focus, effective_date
FROM bis_entity_list_fixed
WHERE entity_name LIKE '%Harbin%'
   OR entity_name LIKE '%Northwestern Polytechnical%'
   OR entity_name LIKE '%HIT%'
   OR entity_name LIKE '%NPU%'
""")
hit_npu_bis = cursor.fetchall()

enrichment_data['slide_10'] = {
    'hit_npu_entity_list': [
        {
            'name': row[0],
            'address': row[1],
            'reason': row[2],
            'tech_focus': row[3],
            'date': row[4]
        }
        for row in hit_npu_bis
    ]
}

print(f"  Found {len(hit_npu_bis)} HIT/NPU entities on BIS Entity List")
for entity in hit_npu_bis:
    print(f"    - {entity[0]}")

# Check openalex_works schema and search
cursor.execute("PRAGMA table_info(openalex_works)")
openalex_cols = cursor.fetchall()
col_names = [col[1] for col in openalex_cols]

if 'raw_author_affiliations' in col_names:
    # Search for HIT collaborations
    cursor.execute("""
    SELECT title, publication_year, primary_topic, sustainable_development_goals
    FROM openalex_works
    WHERE raw_author_affiliations LIKE '%Harbin Institute of Technology%'
       OR raw_author_affiliations LIKE '%Northwestern Polytechnical University%'
    ORDER BY publication_year DESC
    LIMIT 20
    """)
    hit_npu_papers = cursor.fetchall()

    enrichment_data['slide_10']['research_papers'] = [
        {
            'title': row[0],
            'year': row[1],
            'topic': row[2],
            'sdg': row[3]
        }
        for row in hit_npu_papers
    ]

    print(f"  Found {len(hit_npu_papers)} recent HIT/NPU research papers")
else:
    print("  [NOTE] openalex_works doesn't have affiliation data")

# ========== SLIDE 11: TED PROCUREMENT ==========
print("\n[SLIDE 11] TED Procurement Data...")

# Get TED statistics
cursor.execute("SELECT COUNT(*) FROM ted_china_contracts_fixed")
ted_total = cursor.fetchone()[0]

# Get detection method breakdown
cursor.execute("""
SELECT detection_method, COUNT(*) as count
FROM ted_china_contracts_fixed
GROUP BY detection_method
ORDER BY count DESC
""")
detection_methods = cursor.fetchall()

# Get top contracts (avoid encoding issues by limiting fields)
cursor.execute("""
SELECT
    supplier_name,
    supplier_country,
    buyer_country,
    contract_value,
    publication_date,
    detection_method
FROM ted_china_contracts_fixed
WHERE contract_value IS NOT NULL
ORDER BY contract_value DESC
LIMIT 20
""")
top_contracts = cursor.fetchall()

enrichment_data['slide_11'] = {
    'total_records': ted_total,
    'detection_methods': {method: count for method, count in detection_methods},
    'top_contracts': [
        {
            'supplier': row[0],
            'supplier_country': row[1],
            'buyer_country': row[2],
            'value': float(row[3]) if row[3] else None,
            'date': row[4],
            'detection': row[5]
        }
        for row in top_contracts
    ]
}

print(f"  Total TED records: {ted_total:,}")
print(f"  Detection methods:")
for method, count in detection_methods:
    print(f"    {method}: {count:,}")

# ========== SLIDE 14: BIS ENTITY LIST ==========
print("\n[SLIDE 14] BIS Entity List Data...")

# Get all Chinese entities
cursor.execute("""
SELECT entity_name, technology_focus, reason_for_inclusion, risk_score
FROM bis_entity_list_fixed
WHERE china_related = 1
ORDER BY risk_score DESC
""")
bis_entities = cursor.fetchall()

enrichment_data['slide_14'] = {
    'total_entities': len(bis_entities),
    'entities': [
        {
            'name': row[0],
            'tech_focus': row[1],
            'reason': row[2],
            'risk_score': row[3]
        }
        for row in bis_entities
    ]
}

print(f"  Total BIS Entity List entries: {len(bis_entities)}")
print(f"  Top 10 by risk score:")
for entity in bis_entities[:10]:
    print(f"    {entity[0]} (Risk: {entity[3]})")

# ========== EXPORT RESULTS ==========
print("\n" + "="*80)
print("EXPORTING RESULTS")
print("="*80)

output_file = 'enrichment_data_collected.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(enrichment_data, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Data exported to {output_file}")
print("\nSummary:")
print(f"  Slide 10 - HIT/NPU: {len(enrichment_data['slide_10']['hit_npu_entity_list'])} Entity List entries")
print(f"  Slide 11 - TED: {enrichment_data['slide_11']['total_records']:,} contracts")
print(f"  Slide 14 - BIS: {enrichment_data['slide_14']['total_entities']} entities")

conn.close()

print("\n" + "="*80)
print("COLLECTION COMPLETE")
print("="*80)
