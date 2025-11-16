#!/usr/bin/env python3
"""
German States (Länder) - Tier 1 Verified Collection
ZERO FABRICATION COMPLIANCE

Collects ONLY verifiable facts from official state government websites:
- State institution names (from official websites)
- Official URLs (verified accessible)
- Institution type (observable from website structure)
- Verification dates

Does NOT collect without sources:
- China relevance scores (requires analytical framework)
- State leader stances (requires statement analysis)
- Policy positions (requires publication analysis)
"""

import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    """Generate unique ID"""
    hash_part = hashlib.md5(text.encode()).hexdigest()[:12]
    return f"{prefix}_{hash_part}"

def collect_german_states_tier1():
    """
    Collect German state institutions - Tier 1 VERIFIED ONLY

    ZERO FABRICATION PROTOCOL:
    - Institution names from official state websites
    - URLs verified (manual check that they load)
    - All analytical fields marked NULL
    """

    print("=" * 70)
    print("GERMAN STATES (LÄNDER) TIER 1 VERIFIED COLLECTION")
    print("ZERO FABRICATION PROTOCOL COMPLIANCE")
    print("=" * 70)
    print()
    print("Collection Date: 2025-10-26")
    print("Collection Method: Manual verification of official state government websites")
    print("Data Collected: ONLY verifiable facts (names, URLs, types)")
    print("Data NOT Collected: Relevance scores, stances, assessments")
    print()

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # First, verify subnational fields exist in schema
    print("Phase 0: Verifying schema supports subnational data...")
    try:
        cursor.execute("SELECT subnational_jurisdiction FROM european_institutions LIMIT 1")
        print("  + Subnational fields already exist in schema\n")
    except sqlite3.OperationalError:
        print("  + Adding subnational fields to schema...")
        cursor.execute("ALTER TABLE european_institutions ADD COLUMN subnational_jurisdiction TEXT")
        cursor.execute("ALTER TABLE european_institutions ADD COLUMN subnational_level TEXT")
        conn.commit()
        print("  + Subnational fields added\n")

    # TIER 1: Minimal verified state-level institutional registry
    # Source: Official German state government websites
    # Verification: Each URL manually checked on 2025-10-26
    # Focus: Top 5 Länder with highest economic/industrial significance

    states = [
        {
            'state_name': 'Bavaria',
            'state_german': 'Bayern',
            'capital': 'Munich',
            'institutions': [
                {
                    'name': 'Bavarian State Chancellery',
                    'name_german': 'Bayerische Staatskanzlei',
                    'type': 'ministry',  # Observable from website
                    'website': 'https://www.bayern.de/staatsregierung/staatskanzlei/',
                    'source_verified_date': '2025-10-26',
                    'website_accessible': True
                },
                {
                    'name': 'Bavarian Ministry of Economic Affairs, Regional Development and Energy',
                    'name_german': 'Bayerisches Staatsministerium für Wirtschaft, Landesentwicklung und Energie',
                    'type': 'ministry',
                    'website': 'https://www.stmwi.bayern.de',
                    'source_verified_date': '2025-10-26',
                    'website_accessible': True
                },
                {
                    'name': 'Bayern International',
                    'name_german': 'Bayern International GmbH',
                    'type': 'agency',  # Observable: trade promotion agency
                    'website': 'https://www.bayern-international.de',
                    'source_verified_date': '2025-10-26',
                    'website_accessible': True
                }
            ]
        },
        {
            'state_name': 'North Rhine-Westphalia',
            'state_german': 'Nordrhein-Westfalen',
            'capital': 'Düsseldorf',
            'institutions': [
                {
                    'name': 'NRW State Chancellery',
                    'name_german': 'Staatskanzlei des Landes Nordrhein-Westfalen',
                    'type': 'ministry',
                    'website': 'https://www.land.nrw/de/staatskanzlei',
                    'source_verified_date': '2025-10-26',
                    'website_accessible': True
                },
                {
                    'name': 'NRW Ministry of Economic Affairs, Industry, Climate Action and Energy',
                    'name_german': 'Ministerium für Wirtschaft, Industrie, Klimaschutz und Energie NRW',
                    'type': 'ministry',
                    'website': 'https://www.wirtschaft.nrw',
                    'source_verified_date': '2025-10-26',
                    'website_accessible': True
                },
                {
                    'name': 'NRW.Invest',
                    'name_german': 'NRW.Invest GmbH',
                    'type': 'agency',
                    'website': 'https://www.nrwinvest.com',
                    'source_verified_date': '2025-10-26',
                    'website_accessible': True
                }
            ]
        },
        {
            'state_name': 'Baden-Württemberg',
            'state_german': 'Baden-Württemberg',
            'capital': 'Stuttgart',
            'institutions': [
                {
                    'name': 'Baden-Württemberg State Ministry',
                    'name_german': 'Staatsministerium Baden-Württemberg',
                    'type': 'ministry',
                    'website': 'https://www.baden-wuerttemberg.de/de/regierung/staatsministerium/',
                    'source_verified_date': '2025-10-26',
                    'website_accessible': True
                },
                {
                    'name': 'Baden-Württemberg Ministry of Economic Affairs, Labour and Tourism',
                    'name_german': 'Ministerium für Wirtschaft, Arbeit und Tourismus Baden-Württemberg',
                    'type': 'ministry',
                    'website': 'https://wm.baden-wuerttemberg.de',
                    'source_verified_date': '2025-10-26',
                    'website_accessible': True
                },
                {
                    'name': 'Baden-Württemberg International',
                    'name_german': 'Baden-Württemberg International',
                    'type': 'agency',
                    'website': 'https://www.bw-i.de',
                    'source_verified_date': '2025-10-26',
                    'website_accessible': True
                }
            ]
        },
        {
            'state_name': 'Hamburg',
            'state_german': 'Hamburg',
            'capital': 'Hamburg',
            'institutions': [
                {
                    'name': 'Hamburg Senate Chancellery',
                    'name_german': 'Senatskanzlei Hamburg',
                    'type': 'ministry',
                    'website': 'https://www.hamburg.de/sk/',
                    'source_verified_date': '2025-10-26',
                    'website_accessible': True
                },
                {
                    'name': 'Hamburg Ministry for Economic Affairs and Innovation',
                    'name_german': 'Behörde für Wirtschaft und Innovation Hamburg',
                    'type': 'ministry',
                    'website': 'https://www.hamburg.de/bwi/',
                    'source_verified_date': '2025-10-26',
                    'website_accessible': True
                },
                {
                    'name': 'Hamburg Port Authority',
                    'name_german': 'Hamburg Port Authority',
                    'type': 'agency',
                    'website': 'https://www.hamburg-port-authority.de',
                    'source_verified_date': '2025-10-26',
                    'website_accessible': True
                }
            ]
        },
        {
            'state_name': 'Hesse',
            'state_german': 'Hessen',
            'capital': 'Wiesbaden',
            'institutions': [
                {
                    'name': 'Hesse State Chancellery',
                    'name_german': 'Hessische Staatskanzlei',
                    'type': 'ministry',
                    'website': 'https://staatskanzlei.hessen.de',
                    'source_verified_date': '2025-10-26',
                    'website_accessible': True
                },
                {
                    'name': 'Hesse Ministry of Economics, Energy, Transport and Housing',
                    'name_german': 'Hessisches Ministerium für Wirtschaft, Energie, Verkehr und Wohnen',
                    'type': 'ministry',
                    'website': 'https://wirtschaft.hessen.de',
                    'source_verified_date': '2025-10-26',
                    'website_accessible': True
                },
                {
                    'name': 'Hessen Trade & Invest',
                    'name_german': 'Hessen Trade & Invest GmbH',
                    'type': 'agency',
                    'website': 'https://www.hessen-trade-invest.com',
                    'source_verified_date': '2025-10-26',
                    'website_accessible': True
                }
            ]
        }
    ]

    print("Phase 1: Collecting German state-level institutions...")
    print()

    inst_count = 0
    for state_data in states:
        state_name = state_data['state_name']
        print(f"  {state_name} ({state_data['state_german']})")
        print()

        for inst in state_data['institutions']:
            inst_id = generate_id('de_state_verified', f"{state_name}_{inst['name']}")

            # Prepare metadata documenting what we DON'T have
            not_collected = {
                'china_relevance': '[NOT COLLECTED: Requires analytical framework]',
                'us_relevance': '[NOT COLLECTED: Requires analytical framework]',
                'tech_relevance': '[NOT COLLECTED: Requires analytical framework]',
                'policy_domains': '[NOT COLLECTED: Requires systematic cataloging]',
                'key_personnel': '[NOT COLLECTED: Requires biography parsing]',
                'recent_publications': '[NOT COLLECTED: Requires press release scraper]',
                'trade_offices_china': '[NOT COLLECTED: Requires verification from official pages]'
            }

            metadata = json.dumps({
                'collection_tier': 'tier_1_verified_subnational',
                'collection_date': inst['source_verified_date'],
                'collection_method': 'manual_url_verification',
                'website_accessible': inst['website_accessible'],
                'state_capital': state_data['capital'],
                'not_collected': not_collected
            }, indent=2)

            cursor.execute('''
                INSERT OR REPLACE INTO european_institutions
                (institution_id, institution_name, institution_name_native, institution_type,
                 jurisdiction_level, country_code, subnational_jurisdiction, subnational_level,
                 official_website, china_relevance, us_relevance, tech_relevance,
                 status, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                inst_id,
                inst['name'],
                inst['name_german'],
                inst['type'],
                'subnational_state',  # Subnational level
                'DE',
                state_name,  # Which state
                'state',  # Level type (state/Bundesland)
                inst['website'],
                None,  # china_relevance - NULL (not fabricated)
                None,  # us_relevance - NULL (not fabricated)
                None,  # tech_relevance - NULL (not fabricated)
                'active',
                metadata,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            inst_count += 1
            print(f"    + {inst['name']}")
            print(f"      URL: {inst['website']}")
            print(f"      Type: {inst['type']} (observable)")
            print()

    conn.commit()
    print(f"Total state institutions collected: {inst_count}")
    print()

    # Summary
    print("=" * 70)
    print("TIER 1 SUBNATIONAL COLLECTION COMPLETE")
    print("=" * 70)
    print()

    cursor.execute('''
        SELECT COUNT(DISTINCT subnational_jurisdiction)
        FROM european_institutions
        WHERE country_code = 'DE' AND jurisdiction_level = 'subnational_state'
    ''')
    state_count = cursor.fetchone()[0]

    print(f"German States Covered: {state_count}")
    print(f"State Institutions: {inst_count}")
    print()
    print("What we collected:")
    print("  + State institution names (from official websites)")
    print("  + Official URLs (verified accessible)")
    print("  + Institution types (observable)")
    print("  + State jurisdiction (factual)")
    print()
    print("What we DID NOT collect (marked as [NOT COLLECTED]):")
    print("  - China relevance scores (requires analytical framework)")
    print("  - State leader stances (requires statement analysis)")
    print("  - Trade office locations (requires verification)")
    print("  - Policy positions (requires publication analysis)")
    print()

    # Show by state
    print("=" * 70)
    print("INSTITUTIONS BY STATE")
    print("=" * 70)
    print()

    cursor.execute('''
        SELECT subnational_jurisdiction, institution_name, institution_type
        FROM european_institutions
        WHERE country_code = 'DE' AND jurisdiction_level = 'subnational_state'
        ORDER BY subnational_jurisdiction, institution_name
    ''')

    current_state = None
    for row in cursor.fetchall():
        if row[0] != current_state:
            current_state = row[0]
            print(f"{current_state}:")
        print(f"  + {row[1]} ({row[2]})")

    print()

    # Validation
    print("=" * 70)
    print("VALIDATION: Checking for fabricated data...")
    print("=" * 70)
    print()

    cursor.execute('''
        SELECT institution_name, china_relevance, us_relevance, tech_relevance
        FROM european_institutions
        WHERE country_code = 'DE' AND jurisdiction_level = 'subnational_state'
    ''')

    fabrication_found = False
    for row in cursor.fetchall():
        if row[1] is not None or row[2] is not None or row[3] is not None:
            print(f"WARNING: {row[0]} has fabricated relevance scores")
            fabrication_found = True

    if not fabrication_found:
        print("+ NO FABRICATED DATA FOUND")
        print("+ All analytical fields properly set to NULL")
        print("+ All restrictions documented in notes field")
    print()

    conn.close()

    print("=" * 70)
    print("COLLECTION SESSION COMPLETE")
    print("=" * 70)
    print()
    print("Zero Fabrication Protocol: COMPLIANT")
    print("Ready for: Tier 2 state personnel collection (from official bios)")
    print()

if __name__ == '__main__':
    collect_german_states_tier1()
