#!/usr/bin/env python3
"""
Deep Investigation of 4 Promising Entities

These entities should have patents/research but aren't being found:
- CASIC (China Aerospace Science and Industry Corporation)
- COSCO Shipping
- China Shipping Group
- Sinochem Holdings (ChemChina-Sinochem Combined)
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 80)
print("DEEP INVESTIGATION OF 4 PROMISING ENTITIES")
print("=" * 80)
print()

# Define alternative search terms to test
test_cases = {
    'CASIC': [
        'CASIC',
        'China Aerospace Science and Industry',
        'China Aerospace Science & Industry',
        'Aerospace Science and Industry Corporation',
        'Aerospace Science & Industry Corp'
    ],
    'COSCO Shipping': [
        'COSCO',
        'COSCO Shipping',
        'China Ocean Shipping',
        'China COSCO',
        'COSCO Group',
        'COSCO Container',
        'COSCO Holdings'
    ],
    'China Shipping Group': [
        'China Shipping',
        'China Shipping Group',
        'China Shipping Development',
        'CSCL',
        'China Shipping Container Lines'
    ],
    'Sinochem Holdings': [
        'Sinochem',
        'ChemChina',
        'China National Chemical',
        'Sinochem Group',
        'ChemChina Group',
        'China National Chemical Corporation'
    ]
}

findings = {}

for entity_name, search_terms in test_cases.items():
    print(f"{entity_name}:")
    print("-" * 80)

    entity_findings = {
        'best_patent_term': None,
        'best_patent_count': 0,
        'best_research_term': None,
        'best_research_count': 0,
        'all_results': []
    }

    for term in search_terms:
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

        result = {
            'term': term,
            'patents': patent_count,
            'research': research_count
        }
        entity_findings['all_results'].append(result)

        if patent_count > 0 or research_count > 0:
            print(f"  [+] '{term}':")
            print(f"      Patents: {patent_count}, Research: {research_count}")

            if patent_count > entity_findings['best_patent_count']:
                entity_findings['best_patent_term'] = term
                entity_findings['best_patent_count'] = patent_count

            if research_count > entity_findings['best_research_count']:
                entity_findings['best_research_term'] = term
                entity_findings['best_research_count'] = research_count

            # Show sample patents if found
            if patent_count > 0:
                cursor.execute("""
                    SELECT assignee_name, patent_number, title, year
                    FROM uspto_patents_chinese
                    WHERE assignee_name LIKE ?
                    ORDER BY year DESC
                    LIMIT 3
                """, (f'%{term}%',))

                print(f"      Sample patents:")
                for row in cursor.fetchall():
                    print(f"        - {row[0][:50]:50} ({row[3]}) {row[2][:60]}")

        else:
            print(f"  [-] '{term}': No data found")

    findings[entity_name] = entity_findings
    print()

# Print summary
print("=" * 80)
print("SUMMARY - RECOMMENDED SEARCH TERMS")
print("=" * 80)
print()

for entity_name, entity_data in findings.items():
    print(f"{entity_name}:")
    if entity_data['best_patent_count'] > 0:
        print(f"  PATENTS: '{entity_data['best_patent_term']}' => {entity_data['best_patent_count']} patents")
    if entity_data['best_research_count'] > 0:
        print(f"  RESEARCH: '{entity_data['best_research_term']}' => {entity_data['best_research_count']} papers")
    if entity_data['best_patent_count'] == 0 and entity_data['best_research_count'] == 0:
        print(f"  NOT FOUND - Need alternative data sources")
    print()

conn.close()

print("=" * 80)
print("NEXT STEPS")
print("=" * 80)
print()
print("1. Add recommended search terms to entity database")
print("2. Re-run enhanced validation")
print("3. Investigate entities still not found with alternative data sources")
