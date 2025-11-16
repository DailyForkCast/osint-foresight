#!/usr/bin/env python3
"""
Re-run Validation with Subsidiary Names

Searches USAspending and TED databases using both parent and subsidiary names.
Expected to significantly increase validation rate from 14.5% to 50%+.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent
HISTORICAL_DB_PATH = PROJECT_ROOT / "data" / "prc_soe_historical_database.json"
SUBSIDIARIES_PATH = PROJECT_ROOT / "data" / "section_1260h_subsidiaries.json"
MASTER_DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
ANALYSIS_DIR = PROJECT_ROOT / "analysis"
ANALYSIS_DIR.mkdir(exist_ok=True)

print("="*80)
print("VALIDATION WITH SUBSIDIARY NAMES")
print("="*80)
print()

# Load historical database
print("Loading historical database...")
with open(HISTORICAL_DB_PATH, 'r', encoding='utf-8') as f:
    historical_data = json.load(f)
print(f"  Loaded {len(historical_data['entities'])} entities")

# Load subsidiary database
print("Loading subsidiary database...")
with open(SUBSIDIARIES_PATH, 'r', encoding='utf-8') as f:
    subsidiaries_data = json.load(f)
print(f"  Loaded {subsidiaries_data['metadata']['total_subsidiaries']} subsidiaries")
print(f"  For {subsidiaries_data['metadata']['total_parent_entities']} parent entities")
print()

# Connect to master database
print("Connecting to master database...")
conn = sqlite3.connect(MASTER_DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
print("  Connected")
print()

# Build comprehensive search terms for each entity
print("Building search terms (parent + subsidiaries)...")
print()

entity_search_terms = {}

for entity in historical_data['entities']:
    entity_name = entity.get('common_name', '')
    entity_id = entity.get('entity_id', '')

    # Start with parent company names
    search_terms = {
        'parent_names': [],
        'subsidiary_names': []
    }

    # Add common name
    if entity_name:
        search_terms['parent_names'].append(entity_name)

    # Add official English name
    if 'official_name_en' in entity:
        search_terms['parent_names'].append(entity['official_name_en'])

    # Add any existing aliases
    if 'aliases' in entity:
        search_terms['parent_names'].extend(entity['aliases'])

    # Add subsidiaries if available
    if entity_name in subsidiaries_data['entities']:
        subs = subsidiaries_data['entities'][entity_name]['subsidiaries']
        for sub in subs:
            search_terms['subsidiary_names'].append(sub['name'])
            if 'short_name' in sub:
                search_terms['subsidiary_names'].append(sub['short_name'])

    entity_search_terms[entity_name] = search_terms

    total_terms = len(search_terms['parent_names']) + len(search_terms['subsidiary_names'])
    if total_terms > 1:
        print(f"{entity_name:30} {len(search_terms['parent_names'])} parent + {len(search_terms['subsidiary_names'])} subsidiary = {total_terms} total search terms")

print()
print("="*80)
print("SEARCHING DATABASES")
print("="*80)
print()

results = {
    'timestamp': datetime.now().isoformat(),
    'total_entities': len(historical_data['entities']),
    'entities_with_subsidiaries': sum(1 for terms in entity_search_terms.values() if terms['subsidiary_names']),
    'comparison': {
        'without_subsidiaries': {'usaspending': 0, 'ted': 0, 'total': 0},
        'with_subsidiaries': {'usaspending': 0, 'ted': 0, 'total': 0}
    },
    'detailed_findings': []
}

for entity in historical_data['entities']:
    entity_name = entity.get('common_name', '')
    entity_id = entity.get('entity_id', '')

    search_terms = entity_search_terms.get(entity_name, {'parent_names': [], 'subsidiary_names': []})

    finding = {
        'entity_id': entity_id,
        'entity_name': entity_name,
        'has_subsidiaries': len(search_terms['subsidiary_names']) > 0,
        'parent_search': {'usaspending': [], 'ted': []},
        'subsidiary_search': {'usaspending': [], 'ted': []}
    }

    print(f"Searching: {entity_name}")

    # Search USAspending with parent names
    for term in search_terms['parent_names']:
        if any('\u4e00' <= char <= '\u9fff' for char in term):
            continue

        try:
            cursor.execute("""
                SELECT recipient_name, COUNT(*) as count
                FROM usaspending_china_comprehensive
                WHERE recipient_name LIKE ?
                GROUP BY recipient_name
            """, (f'%{term}%',))

            rows = cursor.fetchall()
            for row in rows:
                finding['parent_search']['usaspending'].append({
                    'recipient': row['recipient_name'],
                    'count': row['count'],
                    'matched_on': term
                })
        except Exception as e:
            pass

    # Search USAspending with subsidiary names
    for term in search_terms['subsidiary_names']:
        if any('\u4e00' <= char <= '\u9fff' for char in term):
            continue

        try:
            cursor.execute("""
                SELECT recipient_name, COUNT(*) as count
                FROM usaspending_china_comprehensive
                WHERE recipient_name LIKE ?
                GROUP BY recipient_name
            """, (f'%{term}%',))

            rows = cursor.fetchall()
            for row in rows:
                finding['subsidiary_search']['usaspending'].append({
                    'recipient': row['recipient_name'],
                    'count': row['count'],
                    'matched_on': term
                })
        except Exception as e:
            pass

    # Search TED with parent names
    for term in search_terms['parent_names']:
        if any('\u4e00' <= char <= '\u9fff' for char in term):
            continue

        try:
            cursor.execute("""
                SELECT supplier_name, COUNT(*) as count
                FROM ted_china_contracts_fixed
                WHERE (supplier_name LIKE ? OR buyer_name LIKE ?)
                  AND supplier_name IS NOT NULL
                GROUP BY supplier_name
            """, (f'%{term}%', f'%{term}%'))

            rows = cursor.fetchall()
            for row in rows:
                finding['parent_search']['ted'].append({
                    'supplier': row['supplier_name'],
                    'count': row['count'],
                    'matched_on': term
                })
        except Exception as e:
            pass

    # Search TED with subsidiary names
    for term in search_terms['subsidiary_names']:
        if any('\u4e00' <= char <= '\u9fff' for char in term):
            continue

        try:
            cursor.execute("""
                SELECT supplier_name, COUNT(*) as count
                FROM ted_china_contracts_fixed
                WHERE (supplier_name LIKE ? OR buyer_name LIKE ?)
                  AND supplier_name IS NOT NULL
                GROUP BY supplier_name
            """, (f'%{term}%', f'%{term}%'))

            rows = cursor.fetchall()
            for row in rows:
                finding['subsidiary_search']['ted'].append({
                    'supplier': row['supplier_name'],
                    'count': row['count'],
                    'matched_on': term
                })
        except Exception as e:
            pass

    # Calculate totals
    parent_usaspending = len(finding['parent_search']['usaspending'])
    parent_ted = len(finding['parent_search']['ted'])
    sub_usaspending = len(finding['subsidiary_search']['usaspending'])
    sub_ted = len(finding['subsidiary_search']['ted'])

    if parent_usaspending > 0 or parent_ted > 0:
        results['comparison']['without_subsidiaries']['total'] += 1
        if parent_usaspending > 0:
            results['comparison']['without_subsidiaries']['usaspending'] += 1
        if parent_ted > 0:
            results['comparison']['without_subsidiaries']['ted'] += 1

    if parent_usaspending > 0 or parent_ted > 0 or sub_usaspending > 0 or sub_ted > 0:
        results['comparison']['with_subsidiaries']['total'] += 1
        if parent_usaspending > 0 or sub_usaspending > 0:
            results['comparison']['with_subsidiaries']['usaspending'] += 1
        if parent_ted > 0 or sub_ted > 0:
            results['comparison']['with_subsidiaries']['ted'] += 1

    if parent_usaspending + parent_ted + sub_usaspending + sub_ted > 0:
        print(f"  FOUND: Parent ({parent_usaspending} USA, {parent_ted} TED) + Subsidiary ({sub_usaspending} USA, {sub_ted} TED)")
    else:
        print(f"  Not found")

    results['detailed_findings'].append(finding)

conn.close()

print()
print("="*80)
print("COMPARISON RESULTS")
print("="*80)
print()

print("WITHOUT Subsidiaries (parent names only):")
print(f"  USAspending: {results['comparison']['without_subsidiaries']['usaspending']} entities")
print(f"  TED: {results['comparison']['without_subsidiaries']['ted']} entities")
print(f"  Total: {results['comparison']['without_subsidiaries']['total']} entities ({results['comparison']['without_subsidiaries']['total']/results['total_entities']*100:.1f}%)")
print()

print("WITH Subsidiaries (parent + subsidiary names):")
print(f"  USAspending: {results['comparison']['with_subsidiaries']['usaspending']} entities")
print(f"  TED: {results['comparison']['with_subsidiaries']['ted']} entities")
print(f"  Total: {results['comparison']['with_subsidiaries']['total']} entities ({results['comparison']['with_subsidiaries']['total']/results['total_entities']*100:.1f}%)")
print()

improvement = results['comparison']['with_subsidiaries']['total'] - results['comparison']['without_subsidiaries']['total']
improvement_pct = (improvement / results['total_entities'] * 100) if results['total_entities'] > 0 else 0

print(f"IMPROVEMENT: +{improvement} entities ({improvement_pct:.1f} percentage points)")
print()

# Save results
output_path = ANALYSIS_DIR / f"subsidiary_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("="*80)
print(f"Detailed results saved to: {output_path}")
print("="*80)
