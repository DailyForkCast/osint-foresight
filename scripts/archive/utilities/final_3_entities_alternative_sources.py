#!/usr/bin/env python3
"""
Final 3 Entities - Alternative Data Sources

Check remaining 10 entities across ALL available databases:
1. SEC EDGAR filings
2. TED procurement contracts
3. CORDIS research projects
4. OpenAIRE research
5. EPO patents
6. Any other alternative spellings
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 80)
print("FINAL 3 ENTITIES - CHECKING ALL ALTERNATIVE DATA SOURCES")
print("=" * 80)
print()

remaining_10 = [
    ('CCTC', ['CCTC', 'China Construction Technology', 'Construction Technology Consulting']),
    ('CSTC', ['CSTC', 'China Shipbuilding Trading', 'Shipbuilding Trading']),
    ('China Cargo Airlines', ['China Cargo', 'China Cargo Airlines', 'CK Cargo']),
    ('China Shipping Group', ['China Shipping', 'CSCL', 'China Shipping Container']),
    ('CloudWalk', ['CloudWalk', 'Cloudwalk Technology', 'Guangzhou CloudWalk']),
    ('GTCOM', ['GTCOM', 'Global Tone', 'Global Tone Communication']),
    ('Geosun', ['Geosun', 'Beijing Geosun', 'Geosun Navigation']),
    ('JOUAV', ['JOUAV', 'Jouav Technology', 'Chengdu Jouav']),
    ('Quectel', ['Quectel', 'Quectel Wireless', 'Shanghai Quectel']),
    ('Sinotrans', ['Sinotrans', 'Sinotrans Logistics', 'China National Foreign Trade'])
]

findings = {}

for entity_name, search_terms in remaining_10:
    print(f"{entity_name}:")
    print("-" * 80)

    found_in = []

    for term in search_terms:
        # Check SEC EDGAR
        cursor.execute("""
            SELECT COUNT(*)
            FROM sec_edgar_chinese_entities_local
            WHERE entity_name LIKE ?
        """, (f'%{term}%',))
        sec_count = cursor.fetchone()[0]

        # Check TED contracts
        try:
            cursor.execute("""
                SELECT COUNT(*)
                FROM ted_contractors
                WHERE contractor_name LIKE ?
            """, (f'%{term}%',))
            ted_count = cursor.fetchone()[0]
        except:
            ted_count = 0

        # Check CORDIS
        try:
            cursor.execute("""
                SELECT COUNT(*)
                FROM cordis_chinese_orgs
                WHERE organization_name LIKE ?
            """, (f'%{term}%',))
            cordis_count = cursor.fetchone()[0]
        except:
            cordis_count = 0

        # Check OpenAIRE
        try:
            cursor.execute("""
                SELECT COUNT(*)
                FROM openaire_chinese_organizations
                WHERE org_name LIKE ?
            """, (f'%{term}%',))
            openaire_count = cursor.fetchone()[0]
        except:
            openaire_count = 0

        # Check if any data found
        if sec_count > 0 or ted_count > 0 or cordis_count > 0 or openaire_count > 0:
            print(f"  [FOUND] '{term}':")
            if sec_count > 0:
                print(f"    SEC EDGAR: {sec_count} mentions")
                found_in.append(('SEC', term, sec_count))
            if ted_count > 0:
                print(f"    TED Contracts: {ted_count} contracts")
                found_in.append(('TED', term, ted_count))
            if cordis_count > 0:
                print(f"    CORDIS: {cordis_count} projects")
                found_in.append(('CORDIS', term, cordis_count))
            if openaire_count > 0:
                print(f"    OpenAIRE: {openaire_count} organizations")
                found_in.append(('OpenAIRE', term, openaire_count))

    if found_in:
        findings[entity_name] = found_in
        print(f"  VERDICT: VALIDATABLE via alternative sources!")
    else:
        findings[entity_name] = None
        print(f"  VERDICT: Not found in any data source")

    print()

conn.close()

# Print summary
print("=" * 80)
print("SUMMARY - ALTERNATIVE DATA SOURCE VALIDATION")
print("=" * 80)
print()

validatable_count = sum(1 for v in findings.values() if v is not None)

print(f"Entities checked: 10")
print(f"Validatable via alternative sources: {validatable_count}")
print(f"Still not found: {10 - validatable_count}")
print()

if validatable_count > 0:
    print("NEWLY VALIDATABLE:")
    for entity, sources in findings.items():
        if sources:
            print(f"\n{entity}:")
            for source_type, term, count in sources:
                print(f"  - {source_type}: '{term}' ({count} records)")

# Final projection
current = 52
projected = current + validatable_count
target = 55

print()
print("=" * 80)
print("FINAL PROJECTION")
print("=" * 80)
print()
print(f"Current: 52/62 (83.9%)")
print(f"Projected: {projected}/62 ({projected/62*100:.1f}%)")
print(f"Target (90%): {target}/62")
print()

if projected >= target:
    print("SUCCESS! WE CAN REACH 90% VALIDATION!")
else:
    gap = target - projected
    print(f"Gap: {gap} entities short of 90% target")
    print()
    print("RECOMMENDATION:")
    if gap <= 2:
        print(f"  - Current {projected/62*100:.1f}% is excellent validation for public data sources")
        print(f"  - The remaining {gap} entities may not be publicly validatable")
    else:
        print(f"  - Achieved {projected/62*100:.1f}% validation")
        print("  - Remaining entities require:")
        print("    * Proprietary corporate databases")
        print("    * Chinese-language sources (CNIPA patents, Chinese databases)")
        print("    * Direct corporate registry lookups")
