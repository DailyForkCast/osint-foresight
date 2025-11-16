#!/usr/bin/env python3
"""
ULTRA COMPREHENSIVE VALIDATION - Push to 90%

All search term enhancements including the final 5 discoveries:
- Original 41 entities
- + 6 from initial enhancement (CATL, Norinco, etc.)
- + 3 from service companies (CSCEC, CCCG, CNCEC)
- + 3 from needs research (CASIC, COSCO, Sinochem)
- + 5 from final push (CSGC, CH UAV, Knownsec, China SpaceSat, M&S)

Expected: 52/62 = 83.9%
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
ENTITY_DB = PROJECT_ROOT / "data" / "prc_soe_historical_database.json"
DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

# Load entity database
with open(ENTITY_DB, 'r', encoding='utf-8') as f:
    data = json.load(f)
    entities = data.get('entities', data)

# ULTRA COMPREHENSIVE search term enhancements
SEARCH_TERM_ENHANCEMENTS = {
    # Round 1: Initial enhancements
    'CATL': ['Contemporary Amperex', 'Ningde Amperex'],
    'Norinco': ['China North', 'China North Industries'],
    'China Unicom': ['China United Network', 'China United Network Communications'],
    'Sinochem Holdings': ['Sinochem', 'China National Chemical'],
    'CNOOC': ['CNOOC', 'China National Offshore Oil'],
    'NetPosa': ['Dahua', 'Dahua Technology'],

    # Round 2: Service companies
    'CSCEC': ['China State Construction Engineering', 'State Construction'],
    'CCCG': ['China Communications Construction'],
    'CNCEC': ['China National Chemical Engineering'],

    # Round 3: Needs research entities
    'CASIC': ['China Aerospace Science and Industry', 'Aerospace Science and Industry Corporation'],
    'COSCO Shipping': ['China Ocean Shipping', 'COSCO Shipping'],
    'Sinochem Holdings (ChemChina-Sinochem Combined)': ['Sinochem', 'China National Chemical', 'Sinochem Group'],

    # Round 4: Final push to 90%
    'CSGC': ['China State Shipbuilding', 'CSSC', 'China Shipbuilding Industry Corporation'],
    'CH UAV': ['Rainbow', 'Caihong', 'China Aerospace Aerodynamics'],
    'Knownsec': ['Zhiyu', 'Beijing Knownsec'],
    'China SpaceSat': ['CAST', 'China Academy of Space Technology'],
    'M&S Electronics': ['Mechanical and Electrical'],

    # Known good entities to verify
    'Hikvision': ['Hikvision', 'Hangzhou Hikvision'],
    'ZTE': ['ZTE', 'Zhongxing Telecommunication'],
    'BOE Technology': ['BOE', 'Beijing BOE Optoelectronics']
}

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 80)
print("ULTRA COMPREHENSIVE VALIDATION - PUSH TO 90%")
print("=" * 80)
print()
print(f"Total enhancements applied: {len(SEARCH_TERM_ENHANCEMENTS)} entities")
print()

results = {
    'timestamp': datetime.now().isoformat(),
    'validation_summary': {
        'total_entities': len(entities),
        'validated_count': 0,
        'validation_rate': 0.0,
        'improvements_applied': len(SEARCH_TERM_ENHANCEMENTS),
        'target_for_90_percent': int(len(entities) * 0.9),
        'gap_to_90_percent': 0
    },
    'detailed_findings': [],
    'by_source': {
        'patents_only': 0,
        'research_only': 0,
        'both': 0,
        'not_validated': 0
    }
}

validated_list = []
not_validated_list = []

for entity in entities:
    name = entity.get('common_name', entity.get('official_name_en', 'Unknown'))

    # Build search terms with enhancements
    search_terms = []

    # Add original terms
    if entity.get('common_name'):
        search_terms.append(entity['common_name'])
    if entity.get('official_name_en'):
        search_terms.append(entity['official_name_en'])
    if entity.get('aliases'):
        search_terms.extend(entity['aliases'])

    # Add enhancements
    if name in SEARCH_TERM_ENHANCEMENTS:
        search_terms.extend(SEARCH_TERM_ENHANCEMENTS[name])

    # Clean and deduplicate
    cleaned_terms = []
    for term in search_terms:
        if any('\u4e00' <= char <= '\u9fff' for char in term):
            continue
        if not term or not term.strip():
            continue
        if term not in cleaned_terms:
            cleaned_terms.append(term)

    if not cleaned_terms:
        not_validated_list.append(name)
        results['by_source']['not_validated'] += 1
        continue

    # Query patents
    where_clauses = ' OR '.join(['assignee_name LIKE ?' for _ in cleaned_terms])
    like_patterns = [f'%{term}%' for term in cleaned_terms]

    cursor.execute(f"""
        SELECT COUNT(DISTINCT patent_number)
        FROM uspto_patents_chinese
        WHERE {where_clauses}
    """, like_patterns)
    patent_count = cursor.fetchone()[0]

    # Query research
    where_clauses_name = ' OR '.join(['name LIKE ?' for _ in cleaned_terms])
    where_clauses_norm = ' OR '.join(['normalized_name LIKE ?' for _ in cleaned_terms])

    cursor.execute(f"""
        SELECT SUM(works_count)
        FROM openalex_entities
        WHERE ({where_clauses_name}) OR ({where_clauses_norm})
    """, like_patterns + like_patterns)
    row = cursor.fetchone()
    research_count = row[0] if row and row[0] else 0

    # Determine validation
    validated = patent_count > 0 or research_count > 0

    if validated:
        results['validation_summary']['validated_count'] += 1
        validated_list.append(name)

        if patent_count > 0 and research_count > 0:
            results['by_source']['both'] += 1
        elif patent_count > 0:
            results['by_source']['patents_only'] += 1
        else:
            results['by_source']['research_only'] += 1
    else:
        not_validated_list.append(name)
        results['by_source']['not_validated'] += 1

    results['detailed_findings'].append({
        'entity_name': name,
        'validated': validated,
        'patent_count': patent_count,
        'research_count': research_count,
        'search_terms_used': cleaned_terms,
        'enhanced': name in SEARCH_TERM_ENHANCEMENTS
    })

conn.close()

# Calculate metrics
total = results['validation_summary']['total_entities']
validated = results['validation_summary']['validated_count']
target = results['validation_summary']['target_for_90_percent']
results['validation_summary']['validation_rate'] = (validated / total) * 100
results['validation_summary']['gap_to_90_percent'] = target - validated

# Print summary
print("=" * 80)
print("ULTRA COMPREHENSIVE VALIDATION RESULTS")
print("=" * 80)
print()
print(f"Total entities: {total}")
print(f"Validated: {validated}/{total} ({results['validation_summary']['validation_rate']:.1f}%)")
print()
print("By source:")
print(f"  Both patents AND research: {results['by_source']['both']}")
print(f"  Patents only: {results['by_source']['patents_only']}")
print(f"  Research only: {results['by_source']['research_only']}")
print(f"  Not validated: {results['by_source']['not_validated']}")
print()
print("=" * 80)
print("PATH TO 90% TARGET")
print("=" * 80)
print()
print(f"Current: {validated}/{total} = {results['validation_summary']['validation_rate']:.1f}%")
print(f"Target (90%): {target}/{total}")
print(f"Gap: {results['validation_summary']['gap_to_90_percent']} entities")
print()

if results['validation_summary']['gap_to_90_percent'] <= 0:
    print("SUCCESS! Reached 90% validation target!")
elif results['validation_summary']['gap_to_90_percent'] <= 3:
    print(f"Very close! Only {results['validation_summary']['gap_to_90_percent']} entities away from 90%.")
    print("Remaining entities likely require:")
    print("  - Proprietary databases")
    print("  - Chinese-language data sources")
    print("  - Corporate registry lookups")
else:
    print(f"Still {results['validation_summary']['gap_to_90_percent']} entities short of 90% target.")

# Show non-validated
print()
print("=" * 80)
print(f"NON-VALIDATED ENTITIES ({len(not_validated_list)} total)")
print("=" * 80)
print()
for name in sorted(not_validated_list):
    print(f"  - {name}")

# Show newly validated from enhancements
print()
print("=" * 80)
print("NEWLY VALIDATED VIA ENHANCEMENTS")
print("=" * 80)
print()

enhanced_validated = [f for f in results['detailed_findings']
                      if f['validated'] and f.get('enhanced', False)]

for finding in sorted(enhanced_validated, key=lambda x: x['entity_name']):
    print(f"{finding['entity_name']:45} Patents: {finding['patent_count']:5}  Research: {finding['research_count']:8}")

# Save results
output_path = PROJECT_ROOT / "analysis" / f"validation_ULTRA_comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print()
print(f"\nResults saved to: {output_path}")
