#!/usr/bin/env python3
"""
Test Different-Name Subsidiaries Validation

Tests whether subsidiaries with DIFFERENT names (not containing parent company)
improve validation rate beyond the 14.5% baseline.

Expected: High improvement because these subsidiaries operate under own brands.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent
HISTORICAL_DB_PATH = PROJECT_ROOT / "data" / "prc_soe_historical_database.json"
DIFFERENT_SUBS_PATH = PROJECT_ROOT / "data" / "different_name_subsidiaries.json"
MASTER_DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
ANALYSIS_DIR = PROJECT_ROOT / "analysis"
ANALYSIS_DIR.mkdir(exist_ok=True)

print("="*80)
print("VALIDATION WITH DIFFERENT-NAME SUBSIDIARIES")
print("="*80)
print()
print("Testing subsidiaries that DON'T contain parent company names:")
print("  - OOCL (COSCO subsidiary)")
print("  - Syngenta, Pirelli (ChemChina subsidiaries)")
print("  - CRRC Tangshan, Qingdao Sifang, etc. (CRRC subsidiaries)")
print()

# Load historical database
print("Loading historical database...")
with open(HISTORICAL_DB_PATH, 'r', encoding='utf-8') as f:
    historical_data = json.load(f)
print(f"  Loaded {len(historical_data['entities'])} entities")

# Load different-name subsidiary database
print("Loading different-name subsidiary database...")
with open(DIFFERENT_SUBS_PATH, 'r', encoding='utf-8') as f:
    subs_data = json.load(f)
print(f"  Loaded {subs_data['metadata']['total_subsidiaries']} subsidiaries")
print(f"  For {subs_data['metadata']['total_parent_entities']} parent entities")
print()

# Connect to master database
print("Connecting to master database...")
conn = sqlite3.connect(MASTER_DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
print("  Connected")
print()

# Build search terms mapping
print("Building search terms...")
print()

# Map entity names to their different-name subsidiaries
entity_subsidiary_map = {}

# Map common names to entity IDs for matching
for entity_name, entity_data in subs_data['entities'].items():
    entity_subsidiary_map[entity_name] = []
    for sub in entity_data['subsidiaries']:
        # Add all name variants
        names_to_add = [sub['name']]
        if 'short_name' in sub:
            names_to_add.append(sub['short_name'])
        if 'full_name' in sub:
            names_to_add.append(sub['full_name'])

        entity_subsidiary_map[entity_name].extend(names_to_add)

print("Subsidiary mapping:")
for parent, subs in entity_subsidiary_map.items():
    print(f"  {parent}: {len(subs)} search terms")
print()

results = {
    'timestamp': datetime.now().isoformat(),
    'total_entities': len(historical_data['entities']),
    'entities_with_different_name_subs': len(entity_subsidiary_map),
    'comparison': {
        'baseline': {'entities': 0, 'usaspending': 0, 'ted': 0},
        'with_different_subs': {'entities': 0, 'usaspending': 0, 'ted': 0}
    },
    'new_entities_found': [],
    'detailed_findings': []
}

print("="*80)
print("SEARCHING DATABASES")
print("="*80)
print()

for entity in historical_data['entities']:
    entity_name = entity.get('common_name', '')
    entity_id = entity.get('entity_id', '')

    finding = {
        'entity_id': entity_id,
        'entity_name': entity_name,
        'has_different_name_subs': entity_name in entity_subsidiary_map,
        'parent_search': {'usaspending': [], 'ted': []},
        'subsidiary_search': {'usaspending': [], 'ted': []}
    }

    print(f"Searching: {entity_name}")

    # Get parent search terms
    parent_terms = []
    if entity_name:
        parent_terms.append(entity_name)
    if 'official_name_en' in entity:
        parent_terms.append(entity['official_name_en'])
    if 'aliases' in entity:
        parent_terms.extend(entity['aliases'])

    # Search USAspending with parent names
    for term in parent_terms:
        if any('\u4e00' <= char <= '\u9fff' for char in term):
            continue

        try:
            cursor.execute("""
                SELECT recipient_name, COUNT(*) as count
                FROM usaspending_china_comprehensive
                WHERE recipient_name LIKE ?
                GROUP BY recipient_name
                LIMIT 10
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

    # Search TED with parent names
    for term in parent_terms:
        if any('\u4e00' <= char <= '\u9fff' for char in term):
            continue

        try:
            cursor.execute("""
                SELECT supplier_name, COUNT(*) as count
                FROM ted_china_contracts_fixed
                WHERE (supplier_name LIKE ? OR buyer_name LIKE ?)
                  AND supplier_name IS NOT NULL
                GROUP BY supplier_name
                LIMIT 10
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

    # Search with different-name subsidiaries if available
    if entity_name in entity_subsidiary_map:
        sub_terms = entity_subsidiary_map[entity_name]

        # Search USAspending with subsidiary names
        for term in sub_terms:
            if any('\u4e00' <= char <= '\u9fff' for char in term):
                continue

            try:
                cursor.execute("""
                    SELECT recipient_name, COUNT(*) as count
                    FROM usaspending_china_comprehensive
                    WHERE recipient_name LIKE ?
                    GROUP BY recipient_name
                    LIMIT 10
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

        # Search TED with subsidiary names
        for term in sub_terms:
            if any('\u4e00' <= char <= '\u9fff' for char in term):
                continue

            try:
                cursor.execute("""
                    SELECT supplier_name, COUNT(*) as count
                    FROM ted_china_contracts_fixed
                    WHERE (supplier_name LIKE ? OR buyer_name LIKE ?)
                      AND supplier_name IS NOT NULL
                    GROUP BY supplier_name
                    LIMIT 10
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

    # Calculate results
    parent_usa = len(finding['parent_search']['usaspending'])
    parent_ted = len(finding['parent_search']['ted'])
    sub_usa = len(finding['subsidiary_search']['usaspending'])
    sub_ted = len(finding['subsidiary_search']['ted'])

    # Track baseline (parent only)
    if parent_usa > 0 or parent_ted > 0:
        results['comparison']['baseline']['entities'] += 1
        if parent_usa > 0:
            results['comparison']['baseline']['usaspending'] += 1
        if parent_ted > 0:
            results['comparison']['baseline']['ted'] += 1

    # Track with subsidiaries
    if parent_usa > 0 or parent_ted > 0 or sub_usa > 0 or sub_ted > 0:
        results['comparison']['with_different_subs']['entities'] += 1
        if parent_usa > 0 or sub_usa > 0:
            results['comparison']['with_different_subs']['usaspending'] += 1
        if parent_ted > 0 or sub_ted > 0:
            results['comparison']['with_different_subs']['ted'] += 1

        # Check if this is a NEW entity found via subsidiaries
        if (parent_usa == 0 and parent_ted == 0) and (sub_usa > 0 or sub_ted > 0):
            results['new_entities_found'].append({
                'entity_name': entity_name,
                'usaspending_hits': sub_usa,
                'ted_hits': sub_ted,
                'matched_subsidiaries': list(set([
                    r['matched_on'] for r in finding['subsidiary_search']['usaspending']
                ] + [
                    r['matched_on'] for r in finding['subsidiary_search']['ted']
                ]))
            })
            print(f"  NEW! Found via subsidiaries: {sub_usa} USA, {sub_ted} TED")

    if parent_usa + parent_ted + sub_usa + sub_ted > 0:
        if sub_usa > 0 or sub_ted > 0:
            print(f"  FOUND: Parent ({parent_usa} USA, {parent_ted} TED) + Subsidiary ({sub_usa} USA, {sub_ted} TED)")
        else:
            print(f"  Found: Parent only ({parent_usa} USA, {parent_ted} TED)")
    else:
        print(f"  Not found")

    results['detailed_findings'].append(finding)

conn.close()

print()
print("="*80)
print("COMPARISON RESULTS")
print("="*80)
print()

baseline = results['comparison']['baseline']
with_subs = results['comparison']['with_different_subs']

print("BASELINE (parent names only):")
print(f"  Entities found: {baseline['entities']}/{results['total_entities']} ({baseline['entities']/results['total_entities']*100:.1f}%)")
print(f"  USAspending: {baseline['usaspending']} entities")
print(f"  TED: {baseline['ted']} entities")
print()

print("WITH DIFFERENT-NAME SUBSIDIARIES:")
print(f"  Entities found: {with_subs['entities']}/{results['total_entities']} ({with_subs['entities']/results['total_entities']*100:.1f}%)")
print(f"  USAspending: {with_subs['usaspending']} entities")
print(f"  TED: {with_subs['ted']} entities")
print()

improvement = with_subs['entities'] - baseline['entities']
improvement_pct = (improvement / results['total_entities'] * 100) if results['total_entities'] > 0 else 0

print(f"IMPROVEMENT: +{improvement} entities ({improvement_pct:.1f} percentage points)")
print()

if results['new_entities_found']:
    print("="*80)
    print("NEW ENTITIES FOUND VIA DIFFERENT-NAME SUBSIDIARIES")
    print("="*80)
    print()
    for new_entity in results['new_entities_found']:
        print(f"{new_entity['entity_name']}:")
        print(f"  USAspending: {new_entity['usaspending_hits']} hits")
        print(f"  TED: {new_entity['ted_hits']} hits")
        print(f"  Matched subsidiaries: {', '.join(new_entity['matched_subsidiaries'])}")
        print()

# Save results
output_path = ANALYSIS_DIR / f"different_name_subsidiary_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("="*80)
print(f"Detailed results saved to: {output_path}")
print("="*80)
