#!/usr/bin/env python3
"""
Targeted queries for MCF/NQPF high-priority slide enrichment
Database: F:/OSINT_WAREHOUSE/osint_master.db (22GB)
"""

import sqlite3
import json
from pathlib import Path

print("="*80)
print("TARGETED ENRICHMENT QUERIES - HIGH PRIORITY SLIDES")
print("="*80)

db_path = 'F:/OSINT_WAREHOUSE/osint_master.db'

if not Path(db_path).exists():
    print(f"[ERROR] Database not found at {db_path}")
    exit(1)

print(f"\n[OK] Connecting to {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ========== SLIDE 10: HIT/NPU COLLABORATION CASES ==========
print("\n" + "="*80)
print("[SLIDE 10] HIT/NPU COLLABORATION CASES")
print("="*80)

# Search for Harbin Institute of Technology (HIT) and Northwestern Polytechnical University (NPU)
hit_keywords = ['Harbin Institute of Technology', 'HIT', 'Harbin']
npu_keywords = ['Northwestern Polytechnical University', 'NPU', 'Northwestern Poly']

print("\n--- Searching OpenAlex works for HIT collaborations ---")
try:
    # Get HIT institution data
    cursor.execute("""
    SELECT display_name, country_code, COUNT(*) as works_count
    FROM openalex_institutions
    WHERE display_name LIKE '%Harbin%'
    GROUP BY display_name, country_code
    ORDER BY works_count DESC
    LIMIT 10
    """)
    hit_institutions = cursor.fetchall()

    if hit_institutions:
        print("\nHarbin institutions found:")
        for inst in hit_institutions:
            print(f"  {inst[0]} ({inst[1]}): {inst[2]} works")
    else:
        print("  No Harbin institutions found")

    # Get NPU institution data
    cursor.execute("""
    SELECT display_name, country_code, COUNT(*) as works_count
    FROM openalex_institutions
    WHERE display_name LIKE '%Northwestern Polytechnical%'
       OR display_name LIKE '%Northwestern Poly%'
    GROUP BY display_name, country_code
    ORDER BY works_count DESC
    LIMIT 10
    """)
    npu_institutions = cursor.fetchall()

    if npu_institutions:
        print("\nNorthwestern Polytechnical institutions found:")
        for inst in npu_institutions:
            print(f"  {inst[0]} ({inst[1]}): {inst[2]} works")
    else:
        print("  No NPU institutions found")

    # Check CORDIS collaborations
    print("\n--- Searching CORDIS for HIT/NPU EU collaborations ---")
    cursor.execute("""
    SELECT DISTINCT project_title, chinese_org, eu_partner_count, start_year
    FROM cordis_china_collaborations
    WHERE chinese_org LIKE '%Harbin%'
       OR chinese_org LIKE '%Northwestern Poly%'
    LIMIT 10
    """)
    cordis_collabs = cursor.fetchall()

    if cordis_collabs:
        print(f"\nFound {len(cordis_collabs)} CORDIS projects:")
        for collab in cordis_collabs[:5]:
            print(f"  {collab[2]} | {collab[3]} | {collab[0][:60]}...")
            print(f"    Chinese org: {collab[1]}")
    else:
        print("  No CORDIS collaborations found")

except Exception as e:
    print(f"  [ERROR] {e}")

# ========== SLIDE 11: GLOBAL EXAMPLES - TED PROCUREMENT ==========
print("\n" + "="*80)
print("[SLIDE 11] GLOBAL EXAMPLES - TED PROCUREMENT")
print("="*80)

print("\n--- Checking TED procurement tables ---")
try:
    # Check ted_contractors table
    cursor.execute("SELECT COUNT(*) FROM ted_contractors")
    contractor_count = cursor.fetchone()[0]
    print(f"\nted_contractors: {contractor_count:,} records")

    # Check for Chinese contractors
    cursor.execute("""
    SELECT contractor_name, contractor_country, COUNT(*) as contract_count
    FROM ted_contractors
    WHERE contractor_country = 'CN'
       OR contractor_name LIKE '%China%'
       OR contractor_name LIKE '%Huawei%'
       OR contractor_name LIKE '%ZTE%'
    GROUP BY contractor_name, contractor_country
    ORDER BY contract_count DESC
    LIMIT 20
    """)
    chinese_contractors = cursor.fetchall()

    if chinese_contractors:
        print(f"\nChinese contractors found: {len(chinese_contractors)}")
        for contractor in chinese_contractors[:10]:
            print(f"  {contractor[0]} ({contractor[1]}): {contractor[2]} contracts")
    else:
        print("\n[CRITICAL FINDING] No Chinese contractors found in TED data")

    # Check ted_china_contracts_fixed
    cursor.execute("SELECT COUNT(*) FROM ted_china_contracts_fixed")
    china_contracts = cursor.fetchone()[0]
    print(f"\nted_china_contracts_fixed: {china_contracts:,} records")

    if china_contracts > 0:
        cursor.execute("""
        SELECT contractor_name, contractor_country, contract_value, publication_date
        FROM ted_china_contracts_fixed
        ORDER BY contract_value DESC
        LIMIT 10
        """)
        top_contracts = cursor.fetchall()

        print("\nTop contracts:")
        for contract in top_contracts:
            print(f"  {contract[0]} ({contract[1]}): {contract[2]} | {contract[3]}")

except Exception as e:
    print(f"  [ERROR] {e}")

# ========== SLIDE 14: ILLICIT ACQUISITION CASES ==========
print("\n" + "="*80)
print("[SLIDE 14] ILLICIT ACQUISITION CASES")
print("="*80)

print("\n--- Checking BIS Entity List ---")
try:
    # Get BIS Entity List statistics
    cursor.execute("""
    SELECT country, COUNT(*) as entity_count
    FROM bis_entity_list
    WHERE country = 'China'
       OR country = 'CN'
       OR country LIKE '%China%'
    GROUP BY country
    """)
    bis_china = cursor.fetchall()

    if bis_china:
        print("\nBIS Entity List - China entries:")
        total = sum([row[1] for row in bis_china])
        print(f"  Total Chinese entities: {total}")

        # Get sample entities
        cursor.execute("""
        SELECT name, addresses, federal_register_citation, date_added
        FROM bis_entity_list
        WHERE country = 'China' OR country = 'CN'
        ORDER BY date_added DESC
        LIMIT 10
        """)
        sample_entities = cursor.fetchall()

        print("\nRecent additions:")
        for entity in sample_entities[:5]:
            print(f"  {entity[0]}")
            print(f"    Added: {entity[3]} | FR: {entity[2]}")
    else:
        print("  No Chinese entities found")

    # Check for specific high-profile entities
    print("\n--- Checking for specific companies (Huawei, ZTE, etc.) ---")
    companies = ['Huawei', 'ZTE', 'SMIC', 'YMTC', 'Hikvision', 'Dahua']

    for company in companies:
        cursor.execute("""
        SELECT name, federal_register_citation, date_added
        FROM bis_entity_list
        WHERE name LIKE ?
        """, (f'%{company}%',))
        results = cursor.fetchall()

        if results:
            print(f"\n{company}: {len(results)} entries")
            for result in results[:3]:
                print(f"  {result[0]} | Added {result[2]}")

    # Check opensanctions
    print("\n--- Checking OpenSanctions data ---")
    cursor.execute("""
    SELECT COUNT(*) FROM opensanctions_entities
    WHERE country LIKE '%China%' OR country = 'CN'
    """)
    opensanctions_count = cursor.fetchone()[0]
    print(f"\nOpenSanctions Chinese entities: {opensanctions_count:,}")

except Exception as e:
    print(f"  [ERROR] {e}")

# ========== SUMMARY & EXPORT ==========
print("\n" + "="*80)
print("QUERY COMPLETE - EXPORTING RESULTS")
print("="*80)

# Export key findings for enrichment scripts
findings = {
    "slide_10_hit_npu": {
        "hit_institutions": hit_institutions if 'hit_institutions' in locals() else [],
        "npu_institutions": npu_institutions if 'npu_institutions' in locals() else [],
        "cordis_collaborations": cordis_collabs if 'cordis_collabs' in locals() else []
    },
    "slide_11_ted": {
        "contractor_count": contractor_count if 'contractor_count' in locals() else 0,
        "chinese_contractors": chinese_contractors if 'chinese_contractors' in locals() else [],
        "china_contracts_count": china_contracts if 'china_contracts' in locals() else 0
    },
    "slide_14_illicit": {
        "bis_entity_count": total if 'total' in locals() else 0,
        "opensanctions_count": opensanctions_count if 'opensanctions_count' in locals() else 0
    }
}

with open('enrichment_query_results.json', 'w') as f:
    json.dump(findings, f, indent=2)

print("\n[OK] Results exported to enrichment_query_results.json")

conn.close()
print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
