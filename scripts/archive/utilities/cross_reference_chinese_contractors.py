#!/usr/bin/env python3
"""
Cross-Reference Chinese TED Contractors
Link 522 Chinese contractors with other datasets to build entity profiles
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import re

# Database paths
ted_db = Path("F:/OSINT_WAREHOUSE/osint_master.db")
warehouse_db = Path("F:/OSINT_WAREHOUSE/osint_master.db")  # Same database

print("\n" + "="*80)
print("CROSS-REFERENCE ANALYSIS: CHINESE TED CONTRACTORS")
print("="*80)
print()

# Connect to databases
ted_conn = sqlite3.connect(ted_db)
ted_cursor = ted_conn.cursor()

print("Step 1: Extracting Chinese contractors from TED...")
print()

# Get all Chinese contractors
chinese_contractors = ted_cursor.execute("""
    SELECT DISTINCT
        contractor_name,
        contractor_country,
        COUNT(*) as contract_count,
        SUM(CASE WHEN value_total > 0 THEN value_total ELSE 0 END) as total_value_eur,
        MIN(publication_date) as first_contract,
        MAX(publication_date) as last_contract
    FROM ted_contracts_production
    WHERE detection_rationale IS NOT NULL
    AND contractor_name IS NOT NULL
    AND contractor_name != ''
    GROUP BY contractor_name, contractor_country
    ORDER BY contract_count DESC
""").fetchall()

print(f"Found {len(chinese_contractors)} unique Chinese contractors")
print()

# Build contractor profiles
profiles = {}

for contractor_name, contractor_country, count, total_value, first_date, last_date in chinese_contractors:
    profiles[contractor_name] = {
        'name': contractor_name,
        'country': contractor_country,
        'ted': {
            'contract_count': count,
            'total_value_eur': total_value if total_value else 0,
            'first_contract': first_date,
            'last_contract': last_date,
            'contracts': []
        },
        'openalex': [],
        'uspto': [],
        'usaspending': [],
        'cordis': []
    }

print("Step 2: Getting TED contract details...")
print()

# Get contract details for each contractor
for contractor_name in profiles.keys():
    contracts = ted_cursor.execute("""
        SELECT
            id, notice_number, publication_date,
            ca_name, ca_country,
            contract_title, value_total, currency
        FROM ted_contracts_production
        WHERE contractor_name = ?
        ORDER BY publication_date DESC
        LIMIT 10
    """, (contractor_name,)).fetchall()

    for row in contracts:
        contract_id, notice, pub_date, ca_name, ca_country, title, value, currency = row
        profiles[contractor_name]['ted']['contracts'].append({
            'id': contract_id,
            'notice': notice,
            'date': pub_date,
            'ca_name': ca_name,
            'ca_country': ca_country,
            'title': title[:100],
            'value': value,
            'currency': currency
        })

print("Step 3: Cross-referencing with OpenAlex...")
print()

# Check if OpenAlex data exists
try:
    openalex_results = ted_cursor.execute("""
        SELECT COUNT(*) FROM openalex_collaborations
        WHERE chinese_institution LIKE '%Huawei%'
        OR chinese_institution LIKE '%ZTE%'
        OR chinese_institution LIKE '%Alibaba%'
        LIMIT 1
    """).fetchone()

    if openalex_results and openalex_results[0] > 0:
        print("  OpenAlex table found - searching for contractor matches...")

        # Search for top contractors in OpenAlex
        top_contractors = sorted(profiles.items(), key=lambda x: x[1]['ted']['contract_count'], reverse=True)[:50]

        for contractor_name, profile in top_contractors:
            # Normalize name for matching
            search_name = contractor_name.lower().split()[0] if contractor_name else ''

            if len(search_name) < 3:
                continue

            # Search OpenAlex for this entity
            matches = ted_cursor.execute("""
                SELECT
                    work_id, work_title, publication_date,
                    european_institution, chinese_institution
                FROM openalex_collaborations
                WHERE LOWER(chinese_institution) LIKE ?
                LIMIT 5
            """, (f'%{search_name}%',)).fetchall()

            for match in matches:
                work_id, title, pub_date, eu_inst, cn_inst = match
                profile['openalex'].append({
                    'work_id': work_id,
                    'title': title[:100] if title else '',
                    'date': pub_date,
                    'european_partner': eu_inst,
                    'chinese_institution': cn_inst
                })

        print(f"  Checked top 50 contractors against OpenAlex")
    else:
        print("  OpenAlex data not found or table empty")

except Exception as e:
    print(f"  OpenAlex search skipped: {str(e)[:60]}")

print()
print("Step 4: Cross-referencing with USPTO...")
print()

# Check if USPTO data exists
try:
    uspto_count = ted_cursor.execute("""
        SELECT COUNT(*) FROM uspto_patents WHERE 1=1 LIMIT 1
    """).fetchone()

    if uspto_count:
        print("  USPTO table found - searching for contractor matches...")

        top_contractors = sorted(profiles.items(), key=lambda x: x[1]['ted']['contract_count'], reverse=True)[:50]

        for contractor_name, profile in top_contractors:
            search_name = contractor_name.lower().split()[0] if contractor_name else ''

            if len(search_name) < 3:
                continue

            # Search USPTO for this entity
            matches = ted_cursor.execute("""
                SELECT
                    patent_id, patent_title, grant_date, assignee_name
                FROM uspto_patents
                WHERE LOWER(assignee_name) LIKE ?
                LIMIT 5
            """, (f'%{search_name}%',)).fetchall()

            for match in matches:
                patent_id, title, grant_date, assignee = match
                profile['uspto'].append({
                    'patent_id': patent_id,
                    'title': title[:100] if title else '',
                    'grant_date': grant_date,
                    'assignee': assignee
                })

        print(f"  Checked top 50 contractors against USPTO")
    else:
        print("  USPTO data not found")

except Exception as e:
    print(f"  USPTO search skipped: {str(e)[:60]}")

print()
print("Step 5: Generating profiles...")
print()

# Find contractors with multi-dataset presence
multi_dataset_contractors = []

for name, profile in profiles.items():
    datasets_found = []
    if profile['ted']['contract_count'] > 0:
        datasets_found.append('TED')
    if profile['openalex']:
        datasets_found.append('OpenAlex')
    if profile['uspto']:
        datasets_found.append('USPTO')

    if len(datasets_found) >= 2:
        multi_dataset_contractors.append({
            'name': name,
            'datasets': datasets_found,
            'ted_contracts': profile['ted']['contract_count'],
            'openalex_papers': len(profile['openalex']),
            'uspto_patents': len(profile['uspto'])
        })

# Sort by dataset coverage
multi_dataset_contractors.sort(key=lambda x: (len(x['datasets']), x['ted_contracts']), reverse=True)

print(f"Contractors found in multiple datasets: {len(multi_dataset_contractors)}")
print()

if multi_dataset_contractors:
    print("Top Multi-Dataset Entities:")
    print("-" * 80)
    for i, entity in enumerate(multi_dataset_contractors[:20], 1):
        print(f"{i:2d}. {entity['name'][:50]}")
        print(f"    Datasets: {', '.join(entity['datasets'])}")
        print(f"    TED: {entity['ted_contracts']} contracts | "
              f"OpenAlex: {entity['openalex_papers']} papers | "
              f"USPTO: {entity['uspto_patents']} patents")
        print()

# Statistics
print("="*80)
print("SUMMARY STATISTICS")
print("="*80)
print()

total_contractors = len(profiles)
total_contracts = sum(p['ted']['contract_count'] for p in profiles.values())
with_openalex = sum(1 for p in profiles.values() if p['openalex'])
with_uspto = sum(1 for p in profiles.values() if p['uspto'])

print(f"Total Chinese Contractors: {total_contractors}")
print(f"Total TED Contracts: {total_contracts}")
print(f"Contractors also in OpenAlex: {with_openalex} ({with_openalex/total_contractors*100:.1f}%)")
print(f"Contractors also in USPTO: {with_uspto} ({with_uspto/total_contractors*100:.1f}%)")
print(f"Multi-dataset entities: {len(multi_dataset_contractors)} ({len(multi_dataset_contractors)/total_contractors*100:.1f}%)")
print()

# Save full profiles
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = Path(f"analysis/chinese_contractor_profiles_{timestamp}.json")

# Prepare for JSON export (limit size)
export_profiles = {}
for name, profile in list(profiles.items())[:100]:  # Top 100 by contract count
    export_profiles[name] = profile

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'timestamp': timestamp,
        'summary': {
            'total_contractors': total_contractors,
            'total_contracts': total_contracts,
            'with_openalex': with_openalex,
            'with_uspto': with_uspto,
            'multi_dataset': len(multi_dataset_contractors)
        },
        'multi_dataset_entities': multi_dataset_contractors[:50],
        'profiles': export_profiles
    }, f, indent=2, default=str)

print(f"Detailed profiles saved to: {output_file}")
print()

ted_conn.close()

print("="*80)
print("CROSS-REFERENCE ANALYSIS COMPLETE")
print("="*80)
