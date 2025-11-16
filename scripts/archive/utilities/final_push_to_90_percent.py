#!/usr/bin/env python3
"""
Final Push to 90% Validation - Deep Investigation

Remaining 15 entities - try everything:
1. Alternative English names
2. Parent/subsidiary relationships
3. Romanization variations
4. Brand names
5. Stock ticker searches
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 80)
print("FINAL PUSH TO 90% - DEEP INVESTIGATION OF 15 REMAINING ENTITIES")
print("=" * 80)
print()

# Comprehensive alternative search terms for all 15
test_cases = {
    'China Shipping Group': [
        'China Shipping',
        'CSCL',
        'China Shipping Container',
        'China Shipping Development'
    ],
    'CSGC': [
        'China Shipbuilding Group',
        'CSGC',
        'China State Shipbuilding',
        'CSSC',  # Common abbreviation
        'China Shipbuilding Industry Corporation'
    ],
    'CCTC': [
        'China Construction Technology',
        'CCTC',
        'Construction Technology Consulting'
    ],
    'CloudWalk': [
        'CloudWalk',
        'Cloudwalk Technology',
        'Cloud Walk',
        'Guangzhou CloudWalk',
        'Yun Cong'  # Romanization
    ],
    'CH UAV': [
        'CH UAV',
        'Rainbow',  # CH = Cai Hong (Rainbow) in Chinese
        'Caihong',
        'China Aerospace Aerodynamics'
    ],
    'JOUAV': [
        'JOUAV',
        'Joyance',
        'Chengdu Jouav',
        'Vertical Technologies'
    ],
    'Knownsec': [
        'Knownsec',
        'Beijing Knownsec',
        'Zhiyu',
        'Knownsec Technology'
    ],
    'GTCOM': [
        'GTCOM',
        'Global Tone Communication',
        'Beijing GTCOM',
        'Yitu Technology'  # Sometimes confused
    ],
    'Quectel': [
        'Quectel',
        'Quectel Wireless',
        'Shanghai Quectel',
        'Quectel Technology'
    ],
    'Geosun': [
        'Geosun',
        'Geosun Navigation',
        'Beijing Geosun',
        'Hezhong Sida'
    ],
    'China SpaceSat': [
        'China SpaceSat',
        'DFH Satellite',
        'Dong Fang Hong',
        'China Academy of Space Technology',
        'CAST'
    ],
    'Sinotrans': [
        'Sinotrans',
        'China National Foreign Trade',
        'Sinotrans Logistics',
        'Sinotrans Limited'
    ],
    'China Cargo Airlines': [
        'China Cargo',
        'China Cargo Airlines',
        'CK Cargo',
        'China Freight'
    ],
    'CSTC': [
        'China Shipbuilding Trading',
        'CSTC',
        'Shipbuilding Trading Company'
    ],
    'M&S Electronics': [
        'M&S Electronics',
        'M&S Electron',
        'Tianjin M&S',
        'Mechanical and Electrical'
    ]
}

findings = {}
validatable_count = 0

for entity_name, search_terms in test_cases.items():
    print(f"{entity_name}:")
    print("-" * 80)

    best_patent_term = None
    best_patent_count = 0
    best_research_term = None
    best_research_count = 0

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

        if patent_count > 0 or research_count > 0:
            print(f"  [FOUND] '{term}': Patents: {patent_count}, Research: {research_count}")

            if patent_count > best_patent_count:
                best_patent_term = term
                best_patent_count = patent_count

            if research_count > best_research_count:
                best_research_term = term
                best_research_count = research_count

            # Show sample data
            if patent_count > 0 and patent_count <= 5:
                cursor.execute("""
                    SELECT assignee_name, title, year
                    FROM uspto_patents_chinese
                    WHERE assignee_name LIKE ?
                    ORDER BY year DESC
                    LIMIT 3
                """, (f'%{term}%',))
                for row in cursor.fetchall():
                    print(f"          Patent: {row[0][:60]} ({row[2]})")

    if best_patent_count > 0 or best_research_count > 0:
        print(f"  VERDICT: VALIDATABLE")
        findings[entity_name] = {
            'validatable': True,
            'best_patent_term': best_patent_term,
            'best_patent_count': best_patent_count,
            'best_research_term': best_research_term,
            'best_research_count': best_research_count
        }
        validatable_count += 1
    else:
        print(f"  VERDICT: NOT FOUND IN ANY DATA SOURCE")
        findings[entity_name] = {
            'validatable': False
        }

    print()

conn.close()

# Print summary
print("=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print()

print(f"Entities investigated: 15")
print(f"Newly validatable: {validatable_count}")
print(f"Still not found: {15 - validatable_count}")
print()

if validatable_count > 0:
    print("=" * 80)
    print("NEWLY VALIDATABLE ENTITIES")
    print("=" * 80)
    print()

    for entity, data in findings.items():
        if data['validatable']:
            print(f"{entity}:")
            if data['best_patent_count'] > 0:
                print(f"  Add '{data['best_patent_term']}' for {data['best_patent_count']} patents")
            if data['best_research_count'] > 0:
                print(f"  Add '{data['best_research_term']}' for {data['best_research_count']} papers")
            print()

# Calculate final projection
current = 47
projected = current + validatable_count
target = 55

print("=" * 80)
print("PROJECTION TO 90%")
print("=" * 80)
print()
print(f"Current validated: {current}/62 (75.8%)")
print(f"If all new terms added: {projected}/62 ({projected/62*100:.1f}%)")
print(f"Target for 90%: {target}/62")
print(f"Gap remaining: {target - projected} entities")
print()

if projected >= target:
    print("SUCCESS: We can reach 90% validation!")
else:
    print(f"Still {target - projected} entities short of 90% target.")
    print()
    print("Recommendation:")
    print("  - Accept 75-80% validation as realistic for public data sources")
    print("  - Remaining entities require proprietary databases or are not publicly validatable")
