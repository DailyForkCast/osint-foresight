"""
Validate Historical SOE Database v2.0 Expansion
Confirms all Section 1260H entities are present and generates final statistics.
"""

import json
from collections import defaultdict
from datetime import datetime

# Read the expanded database
print("=" * 80)
print("HISTORICAL SOE DATABASE v2.0 - EXPANSION VALIDATION")
print("=" * 80)
print()

with open('data/prc_soe_historical_database.json', 'r', encoding='utf-8') as f:
    database = json.load(f)

# Read the definition file
with open('section_1260h_entity_definitions.json', 'r', encoding='utf-8') as f:
    definitions = json.load(f)

# Count entities by category
print("ENTITY COUNTS BY CATEGORY")
print("-" * 80)

definition_counts = {}
for category, entities in definitions.items():
    count = len(entities)
    definition_counts[category] = count
    print(f"{category:40} {count:3} entities")

total_definitions = sum(definition_counts.values())
print(f"{'TOTAL NEW ENTITIES TO ADD':40} {total_definitions:3} entities")
print()

# Analyze current database
print("CURRENT DATABASE ANALYSIS")
print("-" * 80)

total_entities = len(database['entities'])
print(f"Total entities in database: {total_entities}")
print()

# Count Section 1260H entities
section_1260h_count = 0
entity_list_count = 0
seven_sons_count = 0
sector_distribution = defaultdict(int)
entity_list_by_date = []

for entity in database['entities']:
    # Get sector
    sector = 'Unknown'
    if 'strategic_classification' in entity:
        strat_class = entity['strategic_classification']
        if isinstance(strat_class, dict):
            sector = strat_class.get('sector', 'Unknown')
        elif isinstance(strat_class, str):
            sector = strat_class

    if sector == 'Unknown' and 'sector' in entity:
        sector = entity.get('sector', 'Unknown')

    sector_distribution[sector] += 1

    # Check MCF classification
    if 'mcf_classification' in entity:
        mcf = entity['mcf_classification']

        if mcf.get('section_1260h_listed'):
            section_1260h_count += 1

        if mcf.get('entity_list'):
            entity_list_count += 1
            entity_list_by_date.append({
                'name': entity.get('common_name', entity.get('official_name_en', 'Unknown')),
                'date': mcf.get('entity_list_date', 'Unknown'),
                'technology': mcf.get('dual_use_technology', [])
            })

        if mcf.get('seven_sons_national_defense'):
            seven_sons_count += 1

print(f"Section 1260H entities: {section_1260h_count}")
print(f"BIS Entity List: {entity_list_count}")
print(f"Seven Sons of National Defense: {seven_sons_count}")
print()

# Sector distribution
print("SECTOR DISTRIBUTION")
print("-" * 80)
for sector, count in sorted(sector_distribution.items(), key=lambda x: x[1], reverse=True):
    print(f"{sector:60} {count:3}")
print()

# Expected vs Actual
print("EXPANSION PROGRESS")
print("-" * 80)
original_count = 10
expected_new = 52
expected_total = original_count + expected_new

print(f"Original database (v1.0): {original_count} entities")
print(f"Expected new entities: {expected_new}")
print(f"Expected total (v2.0): {expected_total}")
print(f"Current total: {total_entities}")
print()

if total_entities >= expected_total:
    print(f"STATUS: COMPLETE")
    print(f"All {expected_new} Section 1260H entities have been added!")
    completion_pct = 100
else:
    remaining = expected_total - total_entities
    completion_pct = (total_entities / expected_total) * 100
    print(f"STATUS: IN PROGRESS ({completion_pct:.1f}% complete)")
    print(f"Remaining entities to add: {remaining}")

print()

# Entity List Timeline
print("BIS ENTITY LIST - TIMELINE")
print("-" * 80)
# Sort by date, treating None/Unknown as earliest
entity_list_by_date.sort(key=lambda x: x['date'] if x['date'] and x['date'] != 'Unknown' else '0000-00-00')
for entry in entity_list_by_date:
    tech_str = ', '.join(entry['technology'][:3]) if entry['technology'] else 'Various'
    date_str = entry['date'] if entry['date'] and entry['date'] != 'Unknown' else 'Unknown'
    print(f"{date_str:12} {entry['name']:30} {tech_str}")
print()

# Cross-reference with definitions to find missing entities
print("VALIDATION - CHECKING FOR MISSING ENTITIES")
print("-" * 80)

# Build set of entity IDs from database
db_entity_ids = {entity.get('entity_id') for entity in database['entities']}

# Check each category
missing_entities = []
for category, entities_list in definitions.items():
    for entity_def in entities_list:
        entity_id = entity_def.get('entity_id')
        if entity_id not in db_entity_ids:
            missing_entities.append({
                'id': entity_id,
                'name': entity_def.get('common_name', 'Unknown'),
                'category': category
            })

if missing_entities:
    print(f"Found {len(missing_entities)} missing entities:")
    print()
    for missing in missing_entities:
        print(f"  {missing['id']:20} {missing['name']:30} ({missing['category']})")
else:
    print("All entities from definition file are present in database!")

print()
print("=" * 80)

# Version comparison
print("DATABASE VERSION COMPARISON")
print("=" * 80)
print()

print("v1.0 (Original - Western Contracting Focus)")
print("  Total entities: 10")
print("  Section 1260H coverage: ~3 (30%)")
print("  Focus: SOE mergers and Western contracts")
print("  Technology companies: 0")
print()

print(f"v2.0 (Current - MCF Expanded)")
print(f"  Total entities: {total_entities}")
print(f"  Section 1260H coverage: {section_1260h_count} ({section_1260h_count/58*100:.0f}% of ~58 designated)")
print(f"  Focus: Military-Civil Fusion and dual-use technology")
print(f"  Technology companies: {len([e for e in database['entities'] if 'MCF-PRIVATE' in e.get('entity_id', '') or 'MCF-' in e.get('entity_id', '')])}")
print(f"  BIS Entity List tracked: {entity_list_count}")
print()

# Calculate stats for report
stats = {
    'validation_date': datetime.now().isoformat(),
    'database_version': database.get('metadata', {}).get('version', '2.0'),
    'total_entities': total_entities,
    'original_entities': original_count,
    'new_entities': total_entities - original_count,
    'section_1260h_entities': section_1260h_count,
    'section_1260h_coverage_pct': round(section_1260h_count / 58 * 100, 1),
    'entity_list_count': entity_list_count,
    'seven_sons_count': seven_sons_count,
    'expansion_complete': total_entities >= expected_total,
    'completion_percentage': round(completion_pct, 1),
    'missing_entities_count': len(missing_entities),
    'sector_count': len(sector_distribution)
}

# Save validation results
with open('analysis/database_expansion_validation_results.json', 'w', encoding='utf-8') as f:
    json.dump({
        'validation_stats': stats,
        'sector_distribution': dict(sector_distribution),
        'entity_list_timeline': entity_list_by_date,
        'missing_entities': missing_entities
    }, f, indent=2, ensure_ascii=False)

print("Validation results saved to: analysis/database_expansion_validation_results.json")
print()

if stats['expansion_complete']:
    print("=" * 80)
    print("EXPANSION COMPLETE - READY FOR VALIDATION SUITE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Run cross-reference validation against USPTO, OpenAlex, USAspending, TED")
    print("  2. Generate comprehensive intelligence reports")
    print("  3. Add subsidiary lists for top 20 entities")
    print("  4. Integrate with entity_aliases and entity_mergers tables")
else:
    print("=" * 80)
    print(f"EXPANSION IN PROGRESS - {remaining} entities remaining")
    print("=" * 80)
