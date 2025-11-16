#!/usr/bin/env python3
"""
Analyze Missing 24 Entities - Root Cause Analysis

Investigates why 24/62 entities aren't validating and finds where they SHOULD appear.
"""

import sqlite3
import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent
CORRECTED_RESULTS = PROJECT_ROOT / "analysis" / "industry_specific_validation_CORRECTED_20251024_204731.json"
DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

print("="*80)
print("ROOT CAUSE ANALYSIS: 24 NON-VALIDATED ENTITIES")
print("="*80)
print()

# Load corrected results
with open(CORRECTED_RESULTS, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find non-validated
non_validated = [e for e in data['detailed_findings'] if len(e['validation_sources']) == 0]

print(f"Analyzing {len(non_validated)} entities...")
print()

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Analysis results
analysis = {
    'total_missing': len(non_validated),
    'by_category': defaultdict(list),
    'actionable_fixes': []
}

print("="*80)
print("CATEGORY 1: SERVICE COMPANIES (expected to have no patents/research)")
print("="*80)
print()

service_companies = [
    'CSCEC', 'CCCG', 'CCTC', 'CNCEC', 'Sinotrans', 'China Cargo Airlines', 'CSTC'
]

for entity in non_validated:
    if entity['entity_name'] in service_companies:
        print(f"{entity['entity_name']:30} {entity['sector']}")
        analysis['by_category']['service_companies'].append(entity['entity_name'])

print()
print("ACTION: These may be legitimately unvalidatable via patents/research.")
print("        Need alternative validation: SEC filings, corporate registries, news.")
print()

print("="*80)
print("CATEGORY 2: WRONG/MISSING SEARCH TERMS")
print("="*80)
print()

# Test specific cases
test_cases = [
    ('Norinco', ['China North', 'Norinco', 'China North Industries']),
    ('China Unicom', ['China Unicom', 'Unicom', 'China United Network']),
    ('COSCO Shipping', ['COSCO', 'COSCO Shipping', 'COSCO SHIPPING']),
    ('Sinochem Holdings', ['Sinochem', 'ChemChina', 'Sinochem Holdings']),
    ('CATL', ['CATL', 'Contemporary Amperex', 'Ningde Amperex']),
    ('Quectel', ['Quectel', 'Quectel Wireless']),
    ('CloudWalk', ['CloudWalk', 'Cloud Walk', 'Cloudwalk Technology']),
    ('CNOOC', ['CNOOC', 'China National Offshore Oil']),
    ('JOUAV', ['JOUAV', 'Joyance']),
    ('NetPosa', ['NetPosa', 'Dahua', 'Dahua Technology'])
]

for entity_name, test_terms in test_cases:
    print(f"{entity_name}:")
    for term in test_terms:
        # Test patents
        cursor.execute("""
            SELECT COUNT(DISTINCT patent_number)
            FROM uspto_patents_chinese
            WHERE assignee_name LIKE ?
        """, (f'%{term}%',))
        patent_count = cursor.fetchone()[0]

        # Test research
        cursor.execute("""
            SELECT SUM(works_count)
            FROM openalex_entities
            WHERE name LIKE ? OR normalized_name LIKE ?
        """, (f'%{term}%', f'%{term}%'))
        row = cursor.fetchone()
        research_count = row[0] if row and row[0] else 0

        if patent_count > 0 or research_count > 0:
            print(f"  [+] '{term}': {patent_count} patents, {research_count} papers")
            analysis['actionable_fixes'].append({
                'entity': entity_name,
                'action': 'add_search_term',
                'term': term,
                'expected_patents': patent_count,
                'expected_research': research_count
            })
        else:
            print(f"  [-] '{term}': 0 patents, 0 papers")
    print()

print("="*80)
print("CATEGORY 3: RECENT COMPANIES (may be too new)")
print("="*80)
print()

recent_companies = {
    'CATL': 2011,
    'CloudWalk': 2015,
    'JOUAV': 2010,
    'Quectel': 2010,
    'NetPosa': 2002
}

for entity_name, founded in recent_companies.items():
    entity_obj = next((e for e in non_validated if e['entity_name'] == entity_name), None)
    if entity_obj:
        print(f"{entity_name:30} Founded: {founded}")

        # Check if ANY patents exist with expanded search
        search_terms = entity_obj.get('search_terms_used', [])
        if search_terms:
            cursor.execute("""
                SELECT COUNT(DISTINCT patent_number), MIN(year), MAX(year)
                FROM uspto_patents_chinese
                WHERE assignee_name LIKE ?
            """, (f'%{search_terms[0]}%',))
            row = cursor.fetchone()
            if row and row[0] > 0:
                print(f"  Found {row[0]} patents ({row[1]}-{row[2]})")
            else:
                print(f"  0 patents found")

        analysis['by_category']['recent_companies'].append(entity_name)

print()

print("="*80)
print("CATEGORY 4: ALTERNATIVE DATA SOURCES NEEDED")
print("="*80)
print()

print("These entities likely need specialized databases:")
print()

specialized_entities = [
    ('GTCOM', 'AI Translation', 'GitHub activity, AI conference papers'),
    ('NetPosa', 'Video Surveillance', 'Product databases, Chinese patents (CNIPA)'),
    ('Knownsec', 'Cybersecurity', 'CVE databases, security conferences'),
    ('Geosun', 'Navigation', 'GPS/GNSS databases, navigation conferences'),
    ('M&S Electronics', 'Components', 'Component databases, supply chain data'),
    ('CH UAV', 'Military Drones', 'Defense procurement (China), export records'),
    ('China SpaceSat', 'Satellites', 'Satellite launch databases, space conferences'),
    ('CSGC', 'Weapons', 'Defense procurement (China), arms export data')
]

for entity_name, sector, suggested_sources in specialized_entities:
    print(f"{entity_name:30} {sector}")
    print(f"  >> {suggested_sources}")
    analysis['by_category']['needs_alternative_sources'].append({
        'entity': entity_name,
        'sector': sector,
        'suggested_sources': suggested_sources
    })

conn.close()

print()
print("="*80)
print("SUMMARY")
print("="*80)
print()

print(f"Total missing: {analysis['total_missing']}")
print()
print("By category:")
print(f"  Service companies (legitimately no patents): {len(analysis['by_category']['service_companies'])}")
print(f"  Wrong/missing search terms (actionable): {len(analysis['actionable_fixes'])}")
print(f"  Recent companies (may lack data): {len(analysis['by_category']['recent_companies'])}")
print(f"  Need alternative sources: {len(analysis['by_category']['needs_alternative_sources'])}")
print()

if analysis['actionable_fixes']:
    print("ACTIONABLE FIXES:")
    for fix in analysis['actionable_fixes']:
        print(f"  {fix['entity']}: Add '{fix['term']}' => +{fix['expected_patents']} patents, +{fix['expected_research']} papers")

# Save analysis
output_path = PROJECT_ROOT / "analysis" / "missing_entities_root_cause_analysis.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(analysis, f, indent=2, ensure_ascii=False)

print()
print(f"Analysis saved to: {output_path}")
