#!/usr/bin/env python3
"""
Enhanced Validation with Improved Search Terms

Applies the discoveries from root cause analysis:
- CATL: Add "Contemporary Amperex", "Ningde Amperex"
- Norinco: Add "China North"
- China Unicom: Add "China United Network"
- Sinochem Holdings: Add "Sinochem"
- CNOOC: Add "CNOOC", "China National Offshore Oil"
- NetPosa: Add "Dahua", "Dahua Technology"
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
    entities = data.get('entities', data)  # Handle both structures

# Enhanced search terms mapping
SEARCH_TERM_ENHANCEMENTS = {
    'CATL': ['Contemporary Amperex', 'Ningde Amperex'],
    'Norinco': ['China North', 'China North Industries'],
    'China Unicom': ['China United Network', 'China United Network Communications'],
    'Sinochem Holdings': ['Sinochem', 'Sinochem Group'],
    'CNOOC': ['CNOOC', 'China National Offshore Oil'],
    'NetPosa': ['Dahua', 'Dahua Technology'],
    'Hikvision': ['Hikvision', 'Hangzhou Hikvision'],
    'ZTE': ['ZTE', 'Zhongxing Telecommunication'],
    'BOE Technology': ['BOE', 'Beijing BOE Optoelectronics']
}

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 80)
print("ENHANCED VALIDATION WITH IMPROVED SEARCH TERMS")
print("=" * 80)
print()

results = {
    'timestamp': datetime.now().isoformat(),
    'validation_summary': {
        'total_entities': len(entities),
        'validated_count': 0,
        'validation_rate': 0.0,
        'improvements_applied': len(SEARCH_TERM_ENHANCEMENTS)
    },
    'detailed_findings': []
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
        print(f"{name}: Added enhanced terms: {enhanced_terms}")

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

    # Check procurement (TED contracts)
    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM ted_procurement_chinese_entities_found
            WHERE entity_name = ?
        """, (name,))
        procurement_count = cursor.fetchone()[0]
    except:
        procurement_count = 0

    # Determine validation
    validated = patent_count > 0 or research_count > 0 or procurement_count > 0

    if validated:
        results['validation_summary']['validated_count'] += 1

    finding = {
        'entity_name': name,
        'validated': validated,
        'patent_count': patent_count,
        'research_count': research_count,
        'procurement_count': procurement_count,
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
print()
print("=" * 80)
print("VALIDATION SUMMARY")
print("=" * 80)
print()
print(f"Total entities: {results['validation_summary']['total_entities']}")
print(f"Validated: {results['validation_summary']['validated_count']}")
print(f"Validation rate: {results['validation_summary']['validation_rate']:.1f}%")
print(f"Enhanced search terms applied: {results['validation_summary']['improvements_applied']} entities")
print()

# Show newly validated entities
print("=" * 80)
print("NEWLY VALIDATED ENTITIES (with enhanced search terms)")
print("=" * 80)
print()

newly_validated = [f for f in results['detailed_findings']
                   if f['validated'] and f.get('enhanced', False)]

for finding in newly_validated:
    print(f"{finding['entity_name']:30} Patents: {finding['patent_count']:5}  Research: {finding['research_count']:8}  Procurement: {finding['procurement_count']:3}")

# Save results
output_path = PROJECT_ROOT / "analysis" / f"enhanced_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print()
print(f"Results saved to: {output_path}")
