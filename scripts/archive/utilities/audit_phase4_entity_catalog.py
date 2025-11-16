#!/usr/bin/env python3
"""
OSINT Foresight Data Audit - Phase 4: Entity & Relationship Cataloging
Extracts entities by dataset, identifies Chinese entities, catalogs variations
"""

import sqlite3
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

output_dir = Path("C:/Projects/OSINT - Foresight/audit_outputs")
output_dir.mkdir(exist_ok=True)

print("="*80)
print("PHASE 4: ENTITY & RELATIONSHIP CATALOGING")
print("="*80)
print()

# Primary database
db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
conn = sqlite3.connect(db_path, timeout=30)
cursor = conn.cursor()

# ============================================================================
# Task 1: Extract Entities by Dataset
# ============================================================================

print("TASK 1: EXTRACT ENTITIES BY DATASET")
print("-" * 40)

entity_catalog = {}

# 1.1 USAspending Entities
print("\n1. USAspending entities:")
try:
    cursor.execute("""
        SELECT DISTINCT
            recipient_name,
            COUNT(*) as occurrences,
            SUM(federal_action_obligation) as total_value
        FROM usaspending_china_374
        WHERE recipient_name IS NOT NULL
        AND recipient_name != ''
        GROUP BY recipient_name
        ORDER BY occurrences DESC
        LIMIT 100
    """)

    usaspending_entities = [
        {'name': row[0], 'occurrences': row[1], 'total_value': row[2]}
        for row in cursor.fetchall()
    ]

    entity_catalog['usaspending'] = {
        'unique_entities': len(usaspending_entities),
        'top_50': usaspending_entities[:50]
    }

    print(f"  Unique entities: {len(usaspending_entities)}")
    print(f"  Top 5 by occurrences:")
    for ent in usaspending_entities[:5]:
        print(f"    {ent['name']}: {ent['occurrences']} contracts")

except Exception as e:
    print(f"  Error: {str(e)}")

# 1.2 TED Contractors
print("\n2. TED contractors:")
try:
    cursor.execute("""
        SELECT DISTINCT
            contractor_name,
            COUNT(*) as occurrences
        FROM ted_contractors
        WHERE contractor_name IS NOT NULL
        AND contractor_name != ''
        GROUP BY contractor_name
        ORDER BY occurrences DESC
        LIMIT 100
    """)

    ted_entities = [
        {'name': row[0], 'occurrences': row[1]}
        for row in cursor.fetchall()
    ]

    entity_catalog['ted'] = {
        'unique_entities': len(ted_entities),
        'top_50': ted_entities[:50]
    }

    print(f"  Unique entities: {len(ted_entities)}")
    print(f"  Top 5 by occurrences:")
    for ent in ted_entities[:5]:
        print(f"    {ent['name']}: {ent['occurrences']} contracts")

except Exception as e:
    print(f"  Error: {str(e)}")

# 1.3 USPTO Patent Assignees
print("\n3. USPTO patent assignees (Chinese):")
try:
    cursor.execute("""
        SELECT DISTINCT
            assignee_name,
            COUNT(*) as occurrences
        FROM uspto_patents_chinese
        WHERE assignee_name IS NOT NULL
        AND assignee_name != ''
        AND assignee_name != '\\N'
        GROUP BY assignee_name
        ORDER BY occurrences DESC
        LIMIT 100
    """)

    uspto_entities = [
        {'name': row[0], 'occurrences': row[1]}
        for row in cursor.fetchall()
    ]

    entity_catalog['uspto'] = {
        'unique_entities': len(uspto_entities),
        'top_50': uspto_entities[:50]
    }

    print(f"  Unique entities: {len(uspto_entities)}")
    print(f"  Top 5 by occurrences:")
    for ent in uspto_entities[:5]:
        print(f"    {ent['name']}: {ent['occurrences']} patents")

except Exception as e:
    print(f"  Error: {str(e)}")

# 1.4 OpenAlex Institutions
print("\n4. OpenAlex institutions:")
try:
    cursor.execute("""
        SELECT DISTINCT
            institution_name,
            country_code,
            COUNT(*) as occurrences
        FROM openalex_work_authors
        WHERE institution_name IS NOT NULL
        AND institution_name != ''
        GROUP BY institution_name, country_code
        ORDER BY occurrences DESC
        LIMIT 100
    """)

    openalex_entities = [
        {'name': row[0], 'country': row[1], 'occurrences': row[2]}
        for row in cursor.fetchall()
    ]

    entity_catalog['openalex'] = {
        'unique_entities': len(openalex_entities),
        'top_50': openalex_entities[:50]
    }

    print(f"  Unique entities: {len(openalex_entities)}")
    print(f"  Top 5 by occurrences:")
    for ent in openalex_entities[:5]:
        print(f"    {ent['name']} ({ent['country']}): {ent['occurrences']} papers")

except Exception as e:
    print(f"  Error: {str(e)}")

# 1.5 GLEIF Legal Entities
print("\n5. GLEIF legal entities (sample):")
try:
    cursor.execute("""
        SELECT
            lei,
            legal_name,
            entity_status,
            registration_authority
        FROM gleif_entities
        WHERE legal_name IS NOT NULL
        AND legal_name != ''
        LIMIT 100
    """)

    gleif_entities = [
        {'lei': row[0], 'name': row[1], 'status': row[2], 'authority': row[3]}
        for row in cursor.fetchall()
    ]

    entity_catalog['gleif'] = {
        'sample_size': len(gleif_entities),
        'sample': gleif_entities[:50]
    }

    print(f"  Sample size: {len(gleif_entities)}")
    print(f"  First 3:")
    for ent in gleif_entities[:3]:
        print(f"    {ent['name']} ({ent['lei']})")

except Exception as e:
    print(f"  Error: {str(e)}")

# Save entity catalog
with open(output_dir / "entity_catalog_by_dataset.json", "w", encoding='utf-8') as f:
    json.dump(entity_catalog, f, indent=2, ensure_ascii=False)

print(f"\n[SAVED] entity_catalog_by_dataset.json")

# ============================================================================
# Task 2: Chinese Entity Identification
# ============================================================================

print("\n" + "="*80)
print("TASK 2: CHINESE ENTITY IDENTIFICATION")
print("-" * 40)

chinese_entities = {}

# Chinese entity patterns (from Phase 2 analysis)
chinese_patterns = [
    'huawei', 'zte', 'lenovo', 'xiaomi', 'dji', 'hikvision', 'dahua',
    'tencent', 'alibaba', 'baidu', 'bytedance', 'cosco', 'byd', 'catl',
    'smic', 'comac', 'avic', 'china', 'chinese', 'beijing', 'shanghai',
    'shenzhen', 'guangdong', 'zhejiang'
]

# 2.1 Cross-dataset Chinese entity extraction
print("\nSearching for Chinese entities across datasets...")

for dataset_name, dataset_info in entity_catalog.items():
    if dataset_name == 'gleif':
        continue  # Skip GLEIF sample

    chinese_matches = []
    entities = dataset_info.get('top_50', [])

    for entity in entities:
        entity_name = entity['name'].lower()

        # Check if any Chinese pattern matches
        for pattern in chinese_patterns:
            if pattern in entity_name:
                chinese_matches.append({
                    'name': entity['name'],
                    'occurrences': entity.get('occurrences', 0),
                    'matched_pattern': pattern,
                    'dataset': dataset_name
                })
                break  # Only count first match

    chinese_entities[dataset_name] = chinese_matches
    print(f"  {dataset_name}: {len(chinese_matches)} Chinese entities found")

# Save Chinese entity identification
with open(output_dir / "chinese_entities_identified.json", "w", encoding='utf-8') as f:
    json.dump(chinese_entities, f, indent=2, ensure_ascii=False)

print(f"\n[SAVED] chinese_entities_identified.json")

# ============================================================================
# Task 3: Entity Name Variations Catalog
# ============================================================================

print("\n" + "="*80)
print("TASK 3: ENTITY NAME VARIATIONS CATALOG")
print("-" * 40)

# Focus on key entities with known variations
key_entities = {
    'Huawei': ['huawei', 'hua wei', 'huawei technologies'],
    'ZTE': ['zte', 'zte corporation'],
    'Lenovo': ['lenovo', 'lenovo group'],
    'China': ['china', 'prc', "people's republic of china"],
    'Chinese Academy of Sciences': ['chinese academy of sciences', 'cas', 'academia sinica']
}

entity_variations = {}

for entity_base, patterns in key_entities.items():
    print(f"\n{entity_base} variations:")

    variations_found = defaultdict(list)

    # Search USAspending
    if 'usaspending' in entity_catalog:
        for ent in entity_catalog['usaspending']['top_50']:
            for pattern in patterns:
                if pattern in ent['name'].lower():
                    variations_found['usaspending'].append(ent['name'])
                    break

    # Search TED
    if 'ted' in entity_catalog:
        for ent in entity_catalog['ted']['top_50']:
            for pattern in patterns:
                if pattern in ent['name'].lower():
                    variations_found['ted'].append(ent['name'])
                    break

    # Search USPTO
    if 'uspto' in entity_catalog:
        for ent in entity_catalog['uspto']['top_50']:
            for pattern in patterns:
                if pattern in ent['name'].lower():
                    variations_found['uspto'].append(ent['name'])
                    break

    entity_variations[entity_base] = dict(variations_found)

    # Print summary
    total_vars = sum(len(v) for v in variations_found.values())
    print(f"  Found {total_vars} variations across datasets")
    for dataset, names in variations_found.items():
        if names:
            print(f"    {dataset}: {names[0]}")  # Show first example

# Save entity variations
with open(output_dir / "entity_name_variations.json", "w", encoding='utf-8') as f:
    json.dump(entity_variations, f, indent=2, ensure_ascii=False)

print(f"\n[SAVED] entity_name_variations.json")

# ============================================================================
# Task 4: Entity Relationship Mapping
# ============================================================================

print("\n" + "="*80)
print("TASK 4: ENTITY RELATIONSHIP MAPPING")
print("-" * 40)

entity_relationships = {}

# 4.1 Cross-dataset entity appearances
print("\nMapping cross-dataset appearances...")

cross_dataset_entities = defaultdict(lambda: defaultdict(int))

# Get simplified entity names for matching
def normalize_name(name):
    """Normalize entity name for matching"""
    if not name:
        return ""
    name = name.lower()
    # Remove common suffixes
    name = re.sub(r'\s+(inc|llc|ltd|corp|corporation|company|co)\.?$', '', name)
    # Remove punctuation
    name = re.sub(r'[^\w\s]', ' ', name)
    # Collapse whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    return name

# Collect all entities
all_entities = []

for dataset_name, dataset_info in entity_catalog.items():
    if dataset_name == 'gleif':
        continue

    entities = dataset_info.get('top_50', [])
    for ent in entities:
        normalized = normalize_name(ent['name'])
        if normalized:
            all_entities.append({
                'original_name': ent['name'],
                'normalized_name': normalized,
                'dataset': dataset_name,
                'occurrences': ent.get('occurrences', 0)
            })

# Find cross-dataset matches
print("\nFinding entities appearing in multiple datasets...")

from collections import Counter

normalized_to_datasets = defaultdict(list)
for ent in all_entities:
    normalized_to_datasets[ent['normalized_name']].append(ent)

# Find entities in 2+ datasets
cross_dataset = {}
for normalized_name, appearances in normalized_to_datasets.items():
    datasets = {app['dataset'] for app in appearances}
    if len(datasets) >= 2:
        cross_dataset[normalized_name] = {
            'datasets': list(datasets),
            'appearances': appearances
        }

print(f"  Entities appearing in 2+ datasets: {len(cross_dataset)}")

# Show top examples
cross_dataset_sorted = sorted(
    cross_dataset.items(),
    key=lambda x: len(x[1]['datasets']),
    reverse=True
)

print("\n  Top cross-dataset entities:")
for i, (name, info) in enumerate(cross_dataset_sorted[:10], 1):
    print(f"    {i}. {name}: {len(info['datasets'])} datasets ({', '.join(info['datasets'])})")

entity_relationships['cross_dataset_appearances'] = {
    name: {'datasets': info['datasets'], 'count': len(info['datasets'])}
    for name, info in list(cross_dataset.items())[:100]
}

# 4.2 Entity co-occurrences (simplified - within dataset)
print("\n4.2 Entity co-occurrence analysis:")
print("  (Analyzing collaboration patterns within datasets...)")

# OpenAlex institution collaborations
try:
    cursor.execute("""
        SELECT DISTINCT
            a1.institution_name as inst1,
            a2.institution_name as inst2,
            COUNT(DISTINCT a1.work_id) as joint_papers
        FROM openalex_work_authors a1
        JOIN openalex_work_authors a2 ON a1.work_id = a2.work_id
        WHERE a1.institution_name < a2.institution_name
        AND a1.institution_name IS NOT NULL
        AND a2.institution_name IS NOT NULL
        GROUP BY a1.institution_name, a2.institution_name
        HAVING joint_papers >= 2
        ORDER BY joint_papers DESC
        LIMIT 50
    """)

    collaborations = [
        {'inst1': row[0], 'inst2': row[1], 'joint_papers': row[2]}
        for row in cursor.fetchall()
    ]

    entity_relationships['openalex_collaborations'] = collaborations

    print(f"  Found {len(collaborations)} institution collaborations (2+ papers)")
    if collaborations:
        print(f"  Top collaboration: {collaborations[0]['inst1']} <-> {collaborations[0]['inst2']}: {collaborations[0]['joint_papers']} papers")

except Exception as e:
    print(f"  Error: {str(e)}")

# Save entity relationships
with open(output_dir / "entity_relationships.json", "w", encoding='utf-8') as f:
    json.dump(entity_relationships, f, indent=2, ensure_ascii=False)

print(f"\n[SAVED] entity_relationships.json")

# ============================================================================
# Summary Statistics
# ============================================================================

print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

summary = {
    'audit_date': datetime.now().isoformat(),
    'entities_by_dataset': {
        name: info.get('unique_entities', info.get('sample_size', 0))
        for name, info in entity_catalog.items()
    },
    'chinese_entities_by_dataset': {
        name: len(entities)
        for name, entities in chinese_entities.items()
    },
    'entity_variations_tracked': len(entity_variations),
    'cross_dataset_entities': len(entity_relationships.get('cross_dataset_appearances', {})),
    'collaboration_pairs': len(entity_relationships.get('openalex_collaborations', []))
}

print(f"\nEntities cataloged by dataset:")
for dataset, count in summary['entities_by_dataset'].items():
    print(f"  {dataset}: {count}")

print(f"\nChinese entities identified:")
for dataset, count in summary['chinese_entities_by_dataset'].items():
    print(f"  {dataset}: {count}")

print(f"\nEntity variations tracked: {summary['entity_variations_tracked']} base entities")
print(f"Cross-dataset entities: {summary['cross_dataset_entities']}")
print(f"Collaboration pairs: {summary['collaboration_pairs']}")

# Save summary
with open(output_dir / "phase4_entity_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"\n[SAVED] phase4_entity_summary.json")

conn.close()

print("\n" + "="*80)
print("PHASE 4 COMPLETE")
print("="*80)
print(f"\nOutput files saved to: {output_dir}")
print()
