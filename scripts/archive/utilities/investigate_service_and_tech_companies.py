#!/usr/bin/env python3
"""
Investigate Service Companies and Recent Tech via Alternative Data Sources

Service companies: CSCEC, CCCG, CCTC, CNCEC, Sinotrans, China Cargo Airlines, CSTC
Recent tech: CloudWalk, JOUAV, Quectel, GTCOM, Knownsec

Check:
1. SEC EDGAR filings (for companies with US operations)
2. Alternative search terms
3. Known subsidiaries or brands
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 80)
print("INVESTIGATING SERVICE COMPANIES VIA ALTERNATIVE SOURCES")
print("=" * 80)
print()

# Service companies with alternative terms
service_test_cases = {
    'CSCEC': ['China State Construction Engineering', 'CSCEC', 'State Construction'],
    'CCCG': ['China Communications Construction', 'CCCG', 'China Comm Construction'],
    'CCTC': ['China Construction Technology Consulting', 'CCTC'],
    'CNCEC': ['China National Chemical Engineering', 'CNCEC'],
    'Sinotrans': ['Sinotrans', 'China National Foreign Trade Transportation'],
    'China Cargo Airlines': ['China Cargo', 'China Cargo Airlines'],
    'CSTC': ['China Shipbuilding Trading', 'CSTC']
}

# Recent tech companies with alternative terms
tech_test_cases = {
    'CloudWalk': ['CloudWalk', 'Cloud Walk Technology', 'Cloudwalk Tech'],
    'JOUAV': ['JOUAV', 'Joyance', 'Chengdu Jouav'],
    'Quectel': ['Quectel', 'Quectel Wireless', 'Shanghai Quectel'],
    'GTCOM': ['GTCOM', 'Global Tone Communication', 'Beijing GTCOM'],
    'Knownsec': ['Knownsec', 'Knownsec Technology', 'Beijing Knownsec']
}

print("SERVICE COMPANIES:")
print("-" * 80)
print()

service_findings = {}

for entity_name, search_terms in service_test_cases.items():
    print(f"{entity_name}:")
    found = False

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

        # Test SEC EDGAR
        cursor.execute("""
            SELECT COUNT(*)
            FROM sec_edgar_chinese_entities_local
            WHERE entity_name LIKE ?
        """, (f'%{term}%',))
        sec_count = cursor.fetchone()[0]

        if patent_count > 0 or research_count > 0 or sec_count > 0:
            print(f"  [+] '{term}': Patents: {patent_count}, Research: {research_count}, SEC: {sec_count}")
            found = True
            service_findings[entity_name] = {
                'term': term,
                'patents': patent_count,
                'research': research_count,
                'sec': sec_count
            }

    if not found:
        print(f"  [-] Not found in any data source")
        service_findings[entity_name] = None

    print()

print()
print("=" * 80)
print("RECENT TECH COMPANIES:")
print("-" * 80)
print()

tech_findings = {}

for entity_name, search_terms in tech_test_cases.items():
    print(f"{entity_name}:")
    found = False

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
            print(f"  [+] '{term}': Patents: {patent_count}, Research: {research_count}")
            found = True
            tech_findings[entity_name] = {
                'term': term,
                'patents': patent_count,
                'research': research_count
            }

            # Show sample patents
            if patent_count > 0:
                cursor.execute("""
                    SELECT assignee_name, title, year
                    FROM uspto_patents_chinese
                    WHERE assignee_name LIKE ?
                    ORDER BY year DESC
                    LIMIT 2
                """, (f'%{term}%',))
                print(f"      Sample patents:")
                for row in cursor.fetchall():
                    print(f"        - ({row[2]}) {row[1][:70]}")

    if not found:
        print(f"  [-] Not found in any data source")
        tech_findings[entity_name] = None

    print()

conn.close()

# Print summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()

service_validated = sum(1 for v in service_findings.values() if v is not None)
tech_validated = sum(1 for v in tech_findings.values() if v is not None)

print(f"Service companies validated: {service_validated}/7")
print(f"Recent tech companies validated: {tech_validated}/5")
print(f"Total newly validatable: {service_validated + tech_validated}")
print()

if service_validated > 0:
    print("Service companies found:")
    for entity, data in service_findings.items():
        if data:
            print(f"  - {entity}: {data['term']}")

if tech_validated > 0:
    print()
    print("Tech companies found:")
    for entity, data in tech_findings.items():
        if data:
            print(f"  - {entity}: {data['term']}")
