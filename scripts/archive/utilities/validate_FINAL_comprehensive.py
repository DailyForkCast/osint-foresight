#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE VALIDATION

Incorporates ALL search term enhancements discovered through investigation:
- 4 initial fixes (CATL, Norinco, China Unicom, NetPosa, CNOOC)
- 3 from "needs research" (CASIC, COSCO Shipping, Sinochem)
- 3 service companies (CSCEC, CCCG, CNCEC)

Expected: 41 + 8 new = 49/62 (79%) validation rate
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

# COMPREHENSIVE Enhanced search terms mapping
SEARCH_TERM_ENHANCEMENTS = {
    # Initial 6 enhancements
    'CATL': ['Contemporary Amperex', 'Ningde Amperex'],
    'Norinco': ['China North', 'China North Industries'],
    'China Unicom': ['China United Network', 'China United Network Communications'],
    'Sinochem Holdings': ['Sinochem', 'China National Chemical'],
    'CNOOC': ['CNOOC', 'China National Offshore Oil'],
    'NetPosa': ['Dahua', 'Dahua Technology'],

    # Additional promising entities
    'CASIC': ['China Aerospace Science and Industry', 'Aerospace Science and Industry Corporation'],
    'COSCO Shipping': ['China Ocean Shipping', 'COSCO Shipping'],
    'Sinochem Holdings (ChemChina-Sinochem Combined)': ['Sinochem', 'China National Chemical', 'Sinochem Group'],

    # Service companies
    'CSCEC': ['China State Construction Engineering', 'State Construction'],
    'CCCG': ['China Communications Construction', 'CCCG'],
    'CNCEC': ['China National Chemical Engineering', 'CNCEC'],

    # Other known entities to verify
    'Hikvision': ['Hikvision', 'Hangzhou Hikvision'],
    'ZTE': ['ZTE', 'Zhongxing Telecommunication'],
    'BOE Technology': ['BOE', 'Beijing BOE Optoelectronics']
}

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 80)
print("FINAL COMPREHENSIVE VALIDATION WITH ALL ENHANCED SEARCH TERMS")
print("=" * 80)
print()
print(f"Enhancements applied to: {len(SEARCH_TERM_ENHANCEMENTS)} entities")
print()

results = {
    'timestamp': datetime.now().isoformat(),
    'validation_summary': {
        'total_entities': len(entities),
        'validated_count': 0,
        'validation_rate': 0.0,
        'improvements_applied': len(SEARCH_TERM_ENHANCEMENTS)
    },
    'detailed_findings': [],
    'by_source': {
        'patents_only': 0,
        'research_only': 0,
        'patents_and_research': 0,
        'not_validated': 0
    }
}

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

    # Add enhancements if available
    if name in SEARCH_TERM_ENHANCEMENTS:
        enhanced_terms = SEARCH_TERM_ENHANCEMENTS[name]
        search_terms.extend(enhanced_terms)

    # Clean and deduplicate
    cleaned_terms = []
    for term in search_terms:
        # Skip Chinese characters
        if any('\u4e00' <= char <= '\u9fff' for char in term):
            continue
        # Skip empty
        if not term or not term.strip():
            continue
        # Deduplicate
        if term not in cleaned_terms:
            cleaned_terms.append(term)

    if not cleaned_terms:
        results['detailed_findings'].append({
            'entity_name': name,
            'validated': False,
            'reason': 'No valid English search terms'
        })
        results['by_source']['not_validated'] += 1
        continue

    # Query patents with DISTINCT counts
    where_clauses = ' OR '.join(['assignee_name LIKE ?' for _ in cleaned_terms])
    like_patterns = [f'%{term}%' for term in cleaned_terms]

    cursor.execute(f"""
        SELECT COUNT(DISTINCT patent_number)
        FROM uspto_patents_chinese
        WHERE {where_clauses}
    """, like_patterns)

    patent_count = cursor.fetchone()[0]

    # Query research with DISTINCT counts
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

        # Categorize by source
        if patent_count > 0 and research_count > 0:
            results['by_source']['patents_and_research'] += 1
        elif patent_count > 0:
            results['by_source']['patents_only'] += 1
        else:
            results['by_source']['research_only'] += 1
    else:
        results['by_source']['not_validated'] += 1

    finding = {
        'entity_name': name,
        'validated': validated,
        'patent_count': patent_count,
        'research_count': research_count,
        'search_terms_used': cleaned_terms,
        'enhanced': name in SEARCH_TERM_ENHANCEMENTS
    }

    results['detailed_findings'].append(finding)

conn.close()

# Calculate final rate
results['validation_summary']['validation_rate'] = (
    results['validation_summary']['validated_count'] /
    results['validation_summary']['total_entities'] * 100
)

# Print summary
print("=" * 80)
print("FINAL VALIDATION SUMMARY")
print("=" * 80)
print()
print(f"Total entities: {results['validation_summary']['total_entities']}")
print(f"Validated: {results['validation_summary']['validated_count']}")
print(f"Validation rate: {results['validation_summary']['validation_rate']:.1f}%")
print()
print("By source:")
print(f"  Patents AND Research: {results['by_source']['patents_and_research']}")
print(f"  Patents only: {results['by_source']['patents_only']}")
print(f"  Research only: {results['by_source']['research_only']}")
print(f"  Not validated: {results['by_source']['not_validated']}")
print()

# Show enhanced entities
print("=" * 80)
print(f"ENTITIES WITH ENHANCED SEARCH TERMS ({sum(1 for f in results['detailed_findings'] if f.get('enhanced', False))} total)")
print("=" * 80)
print()

enhanced_entities = [f for f in results['detailed_findings'] if f.get('enhanced', False)]
enhanced_entities.sort(key=lambda x: x['validated'], reverse=True)

for finding in enhanced_entities:
    status = "[VALIDATED]" if finding['validated'] else "[NOT FOUND]"
    print(f"{status:15} {finding['entity_name']:40} Patents: {finding['patent_count']:5}  Research: {finding['research_count']:8}")

# Show non-validated entities
print()
print("=" * 80)
print(f"NON-VALIDATED ENTITIES ({results['by_source']['not_validated']} total)")
print("=" * 80)
print()

non_validated = [f for f in results['detailed_findings'] if not f['validated']]
for finding in non_validated:
    print(f"  - {finding['entity_name']}")

# Calculate path to 90%
print()
print("=" * 80)
print("PATH TO 90% VALIDATION")
print("=" * 80)
print()

current_rate = results['validation_summary']['validation_rate']
target_entities = int(62 * 0.9)  # 56 entities
needed = target_entities - results['validation_summary']['validated_count']

print(f"Current: {results['validation_summary']['validated_count']}/62 = {current_rate:.1f}%")
print(f"Target (90%): {target_entities}/62 entities")
print(f"Still need: {needed} more entities")

if needed > 0:
    print()
    print("Remaining entities require:")
    print("  - Alternative data sources (financial databases, corporate registries)")
    print("  - Chinese patent databases (CNIPA)")
    print("  - News/media validation")
    print("  - Accept some entities may not be publicly validatable")

# Save results
output_path = PROJECT_ROOT / "analysis" / f"validation_FINAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print()
print(f"Results saved to: {output_path}")
