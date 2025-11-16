#!/usr/bin/env python3
"""
German States (Länder) Institutional Collector
Purpose: Capture subnational China engagement at state level
Focus: Top 5 Länder with highest China exposure
"""

import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    """Generate unique ID"""
    hash_part = hashlib.md5(text.encode()).hexdigest()[:12]
    return f"{prefix}_{hash_part}"

def collect_german_states():
    """Collect German state-level institutions"""

    print("=" * 70)
    print("GERMAN STATES (LÄNDER) INSTITUTIONAL INTELLIGENCE")
    print("=" * 70)
    print()

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # First, update schema to support subnational
    print("Phase 0: Checking schema for subnational support...")
    try:
        cursor.execute("ALTER TABLE european_institutions ADD COLUMN subnational_jurisdiction TEXT")
        cursor.execute("ALTER TABLE european_institutions ADD COLUMN subnational_level TEXT")
        print("  + Added subnational fields to schema\n")
    except sqlite3.OperationalError:
        print("  + Subnational fields already exist\n")

    conn.commit()

    # Define state-level institutions
    states = [
        {
            'state': 'Bavaria',
            'state_german': 'Bayern',
            'capital': 'Munich',
            'population': '13.1 million',
            'china_relevance': 95,
            'institutions': [
                {
                    'name': 'Bavarian State Chancellery',
                    'name_german': 'Bayerische Staatskanzlei',
                    'type': 'ministry',
                    'website': 'https://www.bayern.de/staatsregierung/staatskanzlei/',
                    'domains': ['government', 'coordination', 'foreign_relations'],
                    'china_relevance': 95
                },
                {
                    'name': 'Bavarian Ministry of Economic Affairs',
                    'name_german': 'Bayerisches Staatsministerium für Wirtschaft',
                    'type': 'ministry',
                    'website': 'https://www.stmwi.bayern.de',
                    'domains': ['economy', 'trade', 'investment'],
                    'china_relevance': 100
                },
                {
                    'name': 'Bayern International',
                    'name_german': 'Bayern International GmbH',
                    'type': 'agency',
                    'website': 'https://www.bayern-international.de',
                    'domains': ['trade_promotion', 'investment_attraction'],
                    'china_relevance': 100,
                    'notes': 'Active trade office network in China, organizes delegations'
                },
                {
                    'name': 'Bavarian State Parliament',
                    'name_german': 'Bayerischer Landtag',
                    'type': 'parliament',
                    'website': 'https://www.bayern.landtag.de',
                    'domains': ['legislation', 'oversight'],
                    'china_relevance': 80
                }
            ],
            'personnel': [
                {
                    'name': 'Markus Söder',
                    'title': 'Minister-President of Bavaria',
                    'title_german': 'Ministerpräsident',
                    'party': 'CSU',
                    'institution': 'Bavarian State Chancellery',
                    'start_date': '2018-03-16',
                    'stance': 'moderate',
                    'notes': 'Pro-business, maintains China engagement for automotive industry'
                },
                {
                    'name': 'Hubert Aiwanger',
                    'title': 'Minister of Economic Affairs',
                    'party': 'Freie Wähler',
                    'institution': 'Bavarian Ministry of Economic Affairs',
                    'start_date': '2018-11-16',
                    'stance': 'accommodating',
                    'notes': 'Active China trade promotion, automotive sector focus'
                }
            ]
        },
        {
            'state': 'North Rhine-Westphalia',
            'state_german': 'Nordrhein-Westfalen',
            'capital': 'Düsseldorf',
            'population': '18 million',
            'china_relevance': 90,
            'institutions': [
                {
                    'name': 'NRW State Chancellery',
                    'name_german': 'Staatskanzlei NRW',
                    'type': 'ministry',
                    'website': 'https://www.land.nrw',
                    'domains': ['government', 'coordination'],
                    'china_relevance': 90
                },
                {
                    'name': 'NRW Ministry of Economic Affairs',
                    'name_german': 'Ministerium für Wirtschaft NRW',
                    'type': 'ministry',
                    'website': 'https://www.wirtschaft.nrw',
                    'domains': ['economy', 'trade', 'innovation'],
                    'china_relevance': 95
                },
                {
                    'name': 'NRW.Invest',
                    'type': 'agency',
                    'website': 'https://www.nrwinvest.com',
                    'domains': ['investment_attraction', 'trade_promotion'],
                    'china_relevance': 100,
                    'notes': 'Representative office in Shanghai, active China engagement'
                }
            ],
            'personnel': [
                {
                    'name': 'Hendrik Wüst',
                    'title': 'Minister-President of NRW',
                    'party': 'CDU',
                    'institution': 'NRW State Chancellery',
                    'start_date': '2021-10-27',
                    'stance': 'moderate'
                }
            ]
        },
        {
            'state': 'Baden-Württemberg',
            'state_german': 'Baden-Württemberg',
            'capital': 'Stuttgart',
            'population': '11.1 million',
            'china_relevance': 95,
            'institutions': [
                {
                    'name': 'Baden-Württemberg State Chancellery',
                    'name_german': 'Staatsministerium Baden-Württemberg',
                    'type': 'ministry',
                    'website': 'https://www.baden-wuerttemberg.de',
                    'domains': ['government', 'coordination'],
                    'china_relevance': 95
                },
                {
                    'name': 'Baden-Württemberg Ministry of Economic Affairs',
                    'name_german': 'Wirtschaftsministerium Baden-Württemberg',
                    'type': 'ministry',
                    'website': 'https://wm.baden-wuerttemberg.de',
                    'domains': ['economy', 'trade', 'technology'],
                    'china_relevance': 100
                },
                {
                    'name': 'Baden-Württemberg International',
                    'type': 'agency',
                    'website': 'https://www.bw-i.de',
                    'domains': ['trade_promotion', 'investment'],
                    'china_relevance': 100,
                    'notes': 'China offices, automotive/engineering sector focus'
                }
            ],
            'personnel': [
                {
                    'name': 'Winfried Kretschmann',
                    'title': 'Minister-President of Baden-Württemberg',
                    'party': 'Bündnis 90/Die Grünen',
                    'institution': 'Baden-Württemberg State Chancellery',
                    'start_date': '2011-05-12',
                    'stance': 'moderate',
                    'notes': 'Balances Green values with automotive industry China ties'
                }
            ]
        },
        {
            'state': 'Hesse',
            'state_german': 'Hessen',
            'capital': 'Wiesbaden',
            'population': '6.3 million',
            'china_relevance': 85,
            'institutions': [
                {
                    'name': 'Hesse State Chancellery',
                    'name_german': 'Hessische Staatskanzlei',
                    'type': 'ministry',
                    'website': 'https://staatskanzlei.hessen.de',
                    'domains': ['government', 'coordination'],
                    'china_relevance': 85
                },
                {
                    'name': 'Hesse Ministry of Economics',
                    'name_german': 'Hessisches Ministerium für Wirtschaft',
                    'type': 'ministry',
                    'website': 'https://wirtschaft.hessen.de',
                    'domains': ['economy', 'trade', 'finance'],
                    'china_relevance': 90,
                    'notes': 'Frankfurt financial center, Chinese banks presence'
                },
                {
                    'name': 'Hesse Trade & Invest',
                    'type': 'agency',
                    'website': 'https://www.hessen-trade-invest.com',
                    'domains': ['investment_attraction', 'export_promotion'],
                    'china_relevance': 90
                }
            ],
            'personnel': [
                {
                    'name': 'Boris Rhein',
                    'title': 'Minister-President of Hesse',
                    'party': 'CDU',
                    'institution': 'Hesse State Chancellery',
                    'start_date': '2022-05-31',
                    'stance': 'moderate'
                }
            ]
        },
        {
            'state': 'Hamburg',
            'state_german': 'Hamburg',
            'capital': 'Hamburg',
            'population': '1.9 million',
            'china_relevance': 90,
            'institutions': [
                {
                    'name': 'Hamburg Senate',
                    'name_german': 'Senat der Freien und Hansestadt Hamburg',
                    'type': 'ministry',
                    'website': 'https://www.hamburg.de/senat',
                    'domains': ['government', 'city_state_administration'],
                    'china_relevance': 90
                },
                {
                    'name': 'Hamburg Ministry of Economics',
                    'name_german': 'Behörde für Wirtschaft und Innovation',
                    'type': 'ministry',
                    'website': 'https://www.hamburg.de/bwi',
                    'domains': ['economy', 'trade', 'port'],
                    'china_relevance': 95
                },
                {
                    'name': 'Hamburg Port Authority',
                    'name_german': 'Hamburg Port Authority',
                    'type': 'agency',
                    'website': 'https://www.hamburg-port-authority.de',
                    'domains': ['infrastructure', 'logistics'],
                    'china_relevance': 100,
                    'notes': 'COSCO investment controversy 2022, China gateway port'
                }
            ],
            'personnel': [
                {
                    'name': 'Peter Tschentscher',
                    'title': 'First Mayor of Hamburg',
                    'title_german': 'Erster Bürgermeister',
                    'party': 'SPD',
                    'institution': 'Hamburg Senate',
                    'start_date': '2018-03-28',
                    'stance': 'moderate',
                    'notes': 'Defended COSCO port investment despite federal concerns'
                }
            ]
        }
    ]

    # Insert state institutions
    print("Phase 1: Collecting German state-level institutions...")
    inst_count = 0

    for state_data in states:
        state_name = state_data['state']
        print(f"\n  → {state_name} ({state_data['state_german']})")

        for inst in state_data['institutions']:
            inst_id = generate_id('de_state', f"{state_name}_{inst['name']}")

            cursor.execute('''
                INSERT OR REPLACE INTO european_institutions
                (institution_id, institution_name, institution_name_native, institution_type,
                 jurisdiction_level, country_code, subnational_jurisdiction, subnational_level,
                 official_website, policy_domains, china_relevance, us_relevance, tech_relevance,
                 status, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                inst_id,
                inst['name'],
                inst.get('name_german'),
                inst['type'],
                'subnational_state',
                'DE',
                state_name,
                'state',
                inst['website'],
                json.dumps(inst['domains']),
                inst['china_relevance'],
                70,  # US relevance
                80,  # Tech relevance
                'active',
                inst.get('notes'),
                datetime.now().isoformat()
            ))
            inst_count += 1
            print(f"    + {inst['name']}")

    conn.commit()
    print(f"\n  → Total: {inst_count} state institutions\n")

    # Insert state personnel
    print("Phase 2: Collecting state-level decision-makers...")
    person_count = 0

    for state_data in states:
        for person in state_data['personnel']:
            # Get institution_id
            cursor.execute('''
                SELECT institution_id FROM european_institutions
                WHERE institution_name = ? AND subnational_jurisdiction = ?
            ''', (person['institution'], state_data['state']))

            result = cursor.fetchone()
            if result:
                person_id = generate_id('de_state_person', person['name'])

                cursor.execute('''
                    INSERT OR REPLACE INTO institutional_personnel
                    (person_id, institution_id, full_name, title, role_type,
                     position_start_date, is_current, political_party, china_stance,
                     expertise_areas, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    person_id,
                    result[0],
                    person['name'],
                    person['title'],
                    'political',
                    person['start_date'],
                    1,
                    person['party'],
                    person['stance'],
                    json.dumps(['state_government', 'china_policy']),
                    person.get('notes'),
                    datetime.now().isoformat()
                ))
                person_count += 1
                print(f"  + {person['name']} - {person['title']}")

    conn.commit()
    print(f"\n  → Total: {person_count} state leaders\n")

    # Summary
    print("=" * 70)
    print("COLLECTION SUMMARY")
    print("=" * 70)

    cursor.execute('''
        SELECT COUNT(DISTINCT subnational_jurisdiction)
        FROM european_institutions
        WHERE country_code = 'DE' AND jurisdiction_level = 'subnational_state'
    ''')
    state_count = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(*) FROM european_institutions
        WHERE country_code = 'DE' AND jurisdiction_level = 'subnational_state'
    ''')
    total_inst = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(*) FROM institutional_personnel p
        JOIN european_institutions i ON p.institution_id = i.institution_id
        WHERE i.subnational_jurisdiction IS NOT NULL
    ''')
    total_person = cursor.fetchone()[0]

    print(f"German States Covered:     {state_count}")
    print(f"State Institutions:        {total_inst}")
    print(f"State-level Personnel:     {total_person}")
    print()

    # Show by state
    print("=" * 70)
    print("INSTITUTIONS BY STATE (China Relevance >= 90)")
    print("=" * 70)

    cursor.execute('''
        SELECT subnational_jurisdiction, institution_name, institution_type, china_relevance
        FROM european_institutions
        WHERE country_code = 'DE'
          AND jurisdiction_level = 'subnational_state'
          AND china_relevance >= 90
        ORDER BY subnational_jurisdiction, china_relevance DESC
    ''')

    current_state = None
    for row in cursor.fetchall():
        if row[0] != current_state:
            current_state = row[0]
            print(f"\n{current_state}:")

        print(f"  + {row[1]} ({row[2]}): {row[3]}/100")

    # Show state leaders
    print("\n" + "=" * 70)
    print("STATE LEADERS ON CHINA POLICY")
    print("=" * 70)

    cursor.execute('''
        SELECT p.full_name, p.title, i.subnational_jurisdiction, p.china_stance, p.political_party
        FROM institutional_personnel p
        JOIN european_institutions i ON p.institution_id = i.institution_id
        WHERE i.subnational_jurisdiction IS NOT NULL
          AND p.is_current = 1
        ORDER BY i.subnational_jurisdiction
    ''')

    for row in cursor.fetchall():
        print(f"\n  {row[2]}:")
        print(f"    {row[0]} - {row[1]}")
        print(f"    Party: {row[4]} | China Stance: {row[3]}")

    conn.close()

    print("\n" + "=" * 70)
    print("GERMAN STATES COLLECTION COMPLETE")
    print("=" * 70)
    print("\nCritical Insight:")
    print("  State-level engagement often MORE ACTIVE than federal level")
    print("  Bavaria, NRW, Baden-Württemberg drive automotive/industrial China ties")
    print("  Hamburg port controversy shows federal-state tensions")
    print()

if __name__ == '__main__':
    collect_german_states()
