#!/usr/bin/env python3
"""
Compare Original vs Enhanced Validation Results

Shows which entities were newly validated and which remain missing.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Load original corrected results
ORIGINAL = PROJECT_ROOT / "analysis" / "industry_specific_validation_CORRECTED_20251024_204731.json"
with open(ORIGINAL, 'r', encoding='utf-8') as f:
    original_data = json.load(f)

# Load enhanced results
ENHANCED = PROJECT_ROOT / "analysis" / "enhanced_validation_20251024_211239.json"
with open(ENHANCED, 'r', encoding='utf-8') as f:
    enhanced_data = json.load(f)

print("=" * 80)
print("VALIDATION IMPROVEMENT COMPARISON")
print("=" * 80)
print()

# Get entity names (handle different data structures)
original_validated = {e['entity_name'] for e in original_data['detailed_findings']
                      if len(e.get('validation_sources', [])) > 0}
enhanced_validated = {e['entity_name'] for e in enhanced_data['detailed_findings']
                      if e.get('validated', False)}

original_non_validated = {e['entity_name'] for e in original_data['detailed_findings']
                          if len(e.get('validation_sources', [])) == 0}
enhanced_non_validated = {e['entity_name'] for e in enhanced_data['detailed_findings']
                          if not e.get('validated', False)}

# Calculate improvements
newly_validated = enhanced_validated - original_validated
still_missing = enhanced_non_validated

print(f"ORIGINAL VALIDATION RATE: {len(original_validated)}/62 = {len(original_validated)/62*100:.1f}%")
print(f"ENHANCED VALIDATION RATE: {len(enhanced_validated)}/62 = {len(enhanced_validated)/62*100:.1f}%")
print(f"IMPROVEMENT: +{len(newly_validated)} entities (+{(len(enhanced_validated)-len(original_validated))/62*100:.1f} percentage points)")
print()

print("=" * 80)
print(f"NEWLY VALIDATED ENTITIES ({len(newly_validated)} total)")
print("=" * 80)
print()

# Get details for newly validated
for entity_name in sorted(newly_validated):
    entity_data = next(e for e in enhanced_data['detailed_findings'] if e['entity_name'] == entity_name)
    print(f"{entity_data['entity_name']:30} Patents: {entity_data['patent_count']:5}  Research: {entity_data['research_count']:8}  Procurement: {entity_data['procurement_count']:3}")

print()
print("=" * 80)
print(f"STILL NON-VALIDATED ENTITIES ({len(still_missing)} total)")
print("=" * 80)
print()

# Get details and categorize
for entity_name in sorted(still_missing):
    entity_data = next(e for e in enhanced_data['detailed_findings'] if e['entity_name'] == entity_name)
    print(f"{entity_data['entity_name']:30} Search terms: {len(entity_data['search_terms_used'])}")

# Categorize remaining entities
print()
print("=" * 80)
print("CATEGORIZATION OF REMAINING 21 ENTITIES")
print("=" * 80)
print()

service_companies = [
    'CSCEC', 'CCCG', 'CCTC', 'CNCEC', 'Sinotrans', 'China Cargo Airlines', 'CSTC'
]

recent_tech = [
    'CloudWalk', 'JOUAV', 'Quectel', 'GTCOM', 'Knownsec'
]

defense_specialized = [
    'CH UAV', 'China SpaceSat', 'CSGC', 'Geosun', 'M&S Electronics'
]

needs_research = []
for entity_name in sorted(still_missing):
    if entity_name not in service_companies and entity_name not in recent_tech and entity_name not in defense_specialized:
        needs_research.append(entity_name)

print(f"Service companies (may not have patents): {len(service_companies)}")
for name in service_companies:
    if name in still_missing:
        print(f"  - {name}")

print()
print(f"Recent tech companies (may lack US data): {len(recent_tech)}")
for name in recent_tech:
    if name in still_missing:
        print(f"  - {name}")

print()
print(f"Defense/specialized (need alternative sources): {len(defense_specialized)}")
for name in defense_specialized:
    if name in still_missing:
        print(f"  - {name}")

print()
print(f"Need additional research: {len(needs_research)}")
for name in needs_research:
    print(f"  - {name}")

# Calculate path to 90%
print()
print("=" * 80)
print("PATH TO 90% VALIDATION")
print("=" * 80)
print()

current_rate = len(enhanced_validated) / 62 * 100
target_rate = 90.0
needed_entities = int(62 * 0.9) - len(enhanced_validated)

print(f"Current: {len(enhanced_validated)}/62 = {current_rate:.1f}%")
print(f"Target: 90% = 56/62 entities")
print(f"Need to validate: {needed_entities} more entities")
print()
print("Recommended approach:")
print("1. Find alternative search terms for 'needs research' entities")
print("2. Add alternative data sources (SEC filings, news, corporate registries)")
print("3. Validate service companies through financial/corporate data")
print("4. Accept that some specialized defense entities may not be publicly validatable")
