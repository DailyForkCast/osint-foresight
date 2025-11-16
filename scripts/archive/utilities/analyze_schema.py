#!/usr/bin/env python3
import json
from pathlib import Path

db_path = Path("data/prc_soe_historical_database.json")
with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

# Analyze CRRC
crrc = [e for e in db['entities'] if 'CRRC' in e['common_name'] and e['entity_id'] == 'SOE-2015-001'][0]
print("="*80)
print("CRRC (merged result entity) structure:")
print("="*80)
print(f"Has merger_details: {'merger_details' in crrc}")
print(f"Has formation_details: {'formation_details' in crrc}")
print(f"strategic_classification type: {type(crrc.get('strategic_classification'))}")
print(f"strategic_classification value: {crrc.get('strategic_classification')}")
print(f"sector type: {type(crrc.get('sector'))}")
print(f"sector value: {crrc.get('sector')}")

# Analyze CSR
print("\n" + "="*80)
print("CSR (legacy entity) structure:")
print("="*80)
csr = [e for e in db['entities'] if e['entity_id'] == 'SOE-1998-001'][0]
print(f"Lifecycle keys: {list(csr['lifecycle'].keys())}")
print(f"Has 'merged_into' in lifecycle: {'merged_into' in csr['lifecycle']}")
print(f"Has 'merger_details' section: {'merger_details' in csr}")
if 'merger_details' in csr:
    print(f"merger_details.merged_into: {csr['merger_details'].get('merged_into')}")

# Analyze all entities' structure
print("\n" + "="*80)
print("Schema consistency analysis:")
print("="*80)
for entity in db['entities']:
    eid = entity['entity_id']
    name = entity['common_name']
    status = entity['lifecycle']['status']

    has_merger_details = 'merger_details' in entity
    has_formation_details = 'formation_details' in entity
    has_merged_into_lifecycle = 'merged_into' in entity['lifecycle']
    strategic_class_type = type(entity.get('strategic_classification')).__name__
    sector_location = 'top-level' if 'sector' in entity else 'unknown'

    print(f"{eid:15} {name:30} {status:10} | merger_details:{has_merger_details} formation_details:{has_formation_details} | merged_into_in_lifecycle:{has_merged_into_lifecycle} | strat_class:{strategic_class_type} | sector:{sector_location}")
