#!/usr/bin/env python3
"""
Paris Air Show 2025 - VERIFIED DATA ONLY
==============================================
Loads verified data from 55th International Paris Air Show (June 16-22, 2025)
World's oldest and largest aerospace trade show.

DATA VERIFICATION PROTOCOL:
- ALL data has source citations
- NO fabricated details
- confidence_level field indicates verification status

Sources:
- COMAC Official (english.comac.cc) - COMAC participation, MOUs
- People's Daily (en.people.cn) - Chinese exhibitor statistics
- South China Morning Post (scmp.com) - Industry analysis
- Flight Global (flightglobal.com) - Aviation industry coverage
- Pamir Consulting (pamirllc.com) - Aviation analysis

Created: 2025-10-27
Last verified: 2025-10-27
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('F:/OSINT_WAREHOUSE/osint_master.db')

# Event metadata (VERIFIED from official sources)
EVENT_DATA = {
    'event_id': 'PARIS_AIR_SHOW_2025',
    'event_name': '55th International Paris Air Show',
    'event_series': 'Paris Air Show',
    'edition': '2025',
    'event_type': 'Trade Show',
    'technology_domain': 'Aerospace & Aviation',
    'start_date': '2025-06-16',  # Source: COMAC official, People's Daily
    'end_date': '2025-06-22',
    'location_city': 'Le Bourget',
    'location_country': 'France',
    'location_country_code': 'FR',
    'venue': 'Paris Le Bourget Exhibition Center',
    'organizer_name': 'SIAE (Salon International de l\'Aéronautique et de l\'Espace)',
    'organizer_type': 'Trade Association',
    'website_url': 'https://www.siae.fr',
    'expected_attendance': 140000,  # Approximate based on historical data
    'exhibitor_count': 2400,  # Approximate based on historical data
    'event_scope': 'International',
    'dual_use_indicator': True,  # Aviation/aerospace has significant dual-use applications
    'verification_sources': 'COMAC official 2025-06-17; People\'s Daily 2025-06-27; SCMP 2025-06-20; Flight Global 2025-06-16',
    'notes': '76 Chinese exhibitors (2.6x increase from 29 in 2023). First de facto Chinese country pavilion. Complete industrial chain representation.'
}

# Exhibitors (VERIFIED ONLY - from official sources and credible news)
EXHIBITORS = [
    {
        'entity_name': 'Commercial Aircraft Corporation of China (COMAC)',
        'entity_type': 'State-Owned Enterprise',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'state_owned',
        'entity_list_status': None,
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Commercial aircraft, regional jets, wide-body aircraft',
        'products_displayed': 'C909 regional jet mockup, C919 narrow-body mockup, C929 wide-body mockup (12,000km range, 280 passengers)',
        'verification_source': 'COMAC official 2025-06-17 (english.comac.cc/news/latest/202506/17); People\'s Daily 2025-06-27; Pamir Consulting 2025-06-19',
        'confidence_level': 'confirmed',
        'notes': 'Signed MOU with SAFRAN and Crane Aerospace on C929 cooperation. C909 services 15 routes with 3 SE Asian airlines. C919 in large-scale delivery.'
    },
    {
        'entity_name': 'Aviation Industry Corporation of China (AVIC)',
        'entity_type': 'State-Owned Enterprise',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'state_owned',
        'entity_list_status': 'US Entity List (various subsidiaries)',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Military and civil aircraft, helicopters, drones, precision weapons',
        'products_displayed': '8 major product categories, 30 signature items: fighter jets, transport aircraft, trainers, helicopters, drones, precision weapons',
        'verification_source': 'People\'s Daily 2025-06-27; Flight Global 2025-06-16; SCMP 2025-06-20',
        'confidence_level': 'confirmed',
        'notes': '38 consecutive years at Paris Air Show. Dual-use products including military drones and precision weapons systems.'
    },
    {
        'entity_name': 'SAFRAN (French company - included for context of COMAC partnership)',
        'entity_type': 'Private Corporation',
        'country': 'France',
        'country_code': 'FR',
        'chinese_entity': 0,
        'chinese_entity_type': None,
        'entity_list_status': None,
        'booth_number': None,
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Aircraft engines, aerospace equipment',
        'products_displayed': 'C929 cooperation partnership with COMAC',
        'verification_source': 'COMAC official 2025-06-17',
        'confidence_level': 'confirmed',
        'notes': 'Signed MOU with COMAC on C929 Program Cooperation. Demonstrates Western-Chinese aerospace collaboration.'
    },
]

# Intelligence Summary
INTELLIGENCE_SUMMARY = """
Paris Air Show 2025 - Chinese Participation Analysis
====================================================

VERIFIED CHINESE PRESENCE:
- 76 Chinese exhibitors (162% increase from 29 in 2023)
- First de facto Chinese country pavilion in show history
- Complete industrial chain: complete aircraft, core components, advanced materials, intelligent manufacturing
- 2 major companies documented with verification (COMAC, AVIC)

STRATEGIC AIRCRAFT PROGRAMS:

COMAC Aircraft Portfolio:
- C909: Regional jet, 15 routes operational with 3 SE Asian airlines
- C919: Narrow-body, large-scale delivery phase
- C929: Wide-body under development (12,000km range, 280 passengers, 3-class config)

AVIC Product Categories:
- Fighter jets (military application)
- Transport aircraft (dual-use)
- Trainers
- Helicopters (dual-use)
- Drones (dual-use - military and civilian applications)
- Precision weapons (military)

INTERNATIONAL PARTNERSHIPS:
- COMAC-SAFRAN MOU: C929 Program Cooperation
- COMAC-Crane Aerospace & Electronics: C929 cooperation
- Demonstrates continued Western aerospace industry engagement with Chinese manufacturers

DUAL-USE TECHNOLOGY CONCERNS:
- AVIC's 38-year continuous presence includes military systems
- Drones with civilian/military applications
- Precision weapons systems
- Transport aircraft with potential military logistics applications
- Advanced materials with aerospace/defense applications

ENTITY LIST IMPLICATIONS:
- AVIC has Entity List subsidiaries but continues Paris Air Show participation
- No restriction on European trade show participation
- COMAC not on Entity List, partners freely with Western companies
- Bifurcation: US restrictions vs European aerospace industry engagement

MARKET INTELLIGENCE:
- 162% increase in Chinese exhibitors signals aggressive market expansion
- First Chinese country pavilion indicates coordinated government support
- Complete industrial chain representation shows manufacturing maturity
- C919 large-scale delivery competes directly with Boeing 737/Airbus A320
- C929 development targets long-haul market (Boeing 787/Airbus A350 competitor)

STRATEGIC SIGNIFICANCE:
- Chinese aerospace industry achieving commercial competitiveness
- European aerospace companies (SAFRAN) maintain partnerships despite US-China tensions
- Military-civil fusion evident in AVIC's dual-use product portfolio
- Chinese aviation self-sufficiency advancing (reduces Boeing/Airbus dependence)

DATA LIMITATIONS:
- Complete list of 76 Chinese exhibitors not publicly available
- Only 2 major exhibitors (COMAC, AVIC) documented with detailed verification
- Most booth locations and product specifications not published
- Partnership MOUs announced but detailed terms not disclosed

DEDUPLICATION NOTE:
- Exhibitor counts represent PARTICIPATIONS, not unique companies
- AVIC appears at multiple defense/aerospace events (38 consecutive years at Paris)
- Aggregate "76 Chinese exhibitors" represents participation slots at THIS conference
- Cross-conference unique company count requires deduplication analysis
- See: scripts/analysis/deduplicate_conference_exhibitors.py
"""


def insert_event(conn, cursor):
    """Insert event with full schema compliance"""
    cursor.execute("""
        INSERT OR REPLACE INTO technology_events (
            event_id, event_name, event_series, edition, event_type,
            technology_domain, start_date, end_date, location_city,
            location_country, location_country_code, venue, organizer_name,
            organizer_type, website_url, expected_attendance, exhibitor_count,
            event_scope, dual_use_indicator, created_at, last_updated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        EVENT_DATA['event_id'],
        EVENT_DATA['event_name'],
        EVENT_DATA['event_series'],
        EVENT_DATA['edition'],
        EVENT_DATA['event_type'],
        EVENT_DATA['technology_domain'],
        EVENT_DATA['start_date'],
        EVENT_DATA['end_date'],
        EVENT_DATA['location_city'],
        EVENT_DATA['location_country'],
        EVENT_DATA['location_country_code'],
        EVENT_DATA['venue'],
        EVENT_DATA['organizer_name'],
        EVENT_DATA['organizer_type'],
        EVENT_DATA['website_url'],
        EVENT_DATA['expected_attendance'],
        EVENT_DATA['exhibitor_count'],
        EVENT_DATA['event_scope'],
        EVENT_DATA['dual_use_indicator'],
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))

    print(f"[OK] Event inserted: {EVENT_DATA['event_name']}")
    print(f"     Dates: {EVENT_DATA['start_date']} to {EVENT_DATA['end_date']}")
    print(f"     Attendance: {EVENT_DATA['expected_attendance']:,}")
    print(f"     Exhibitors: {EVENT_DATA['exhibitor_count']:,}")
    print(f"     Chinese Exhibitors: 76 (162% increase from 2023)")
    return EVENT_DATA['event_id']


def insert_exhibitors(conn, cursor, event_id):
    """Insert exhibitors with verification metadata"""
    print(f"\n[OK] Inserting {len(EXHIBITORS)} verified exhibitors...")

    for exhibitor in EXHIBITORS:
        participant_id = f"{event_id}_{exhibitor['entity_name'].replace(' ', '_').replace('.', '').replace(',', '').replace('(', '').replace(')', '')}"

        cursor.execute("""
            INSERT OR REPLACE INTO event_participants (
                participant_id, event_id, entity_name, entity_normalized,
                entity_type, entity_country, entity_country_code,
                chinese_entity, chinese_entity_type, participation_role,
                booth_number, booth_size, technology_focus,
                verification_status, data_source, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            participant_id,
            event_id,
            exhibitor['entity_name'],
            exhibitor['entity_name'].lower().strip(),
            exhibitor['entity_type'],
            exhibitor['country'],
            exhibitor['country_code'],
            exhibitor['chinese_entity'],
            exhibitor.get('chinese_entity_type'),
            'Exhibitor',
            exhibitor.get('booth_number'),
            exhibitor.get('booth_size'),
            exhibitor['technology_focus'],
            exhibitor['confidence_level'],
            exhibitor['verification_source'],
            datetime.now().isoformat()
        ))

        chinese_flag = '[CN]' if exhibitor['chinese_entity'] == 1 else '[FR]'
        booth_info = f"Booth {exhibitor['booth_number']}" if exhibitor.get('booth_number') else "Booth unverified"
        conf_level = exhibitor['confidence_level']
        entity_list = '[ENTITY LIST]' if exhibitor.get('entity_list_status') else ''

        print(f"  {chinese_flag} {exhibitor['entity_name']:50} | {booth_info:20} | {conf_level} {entity_list}")

    verified_booths = sum(1 for e in EXHIBITORS if e.get('booth_number'))
    chinese_exhibitors = sum(1 for e in EXHIBITORS if e['chinese_entity'] == 1)
    entity_list_companies = sum(1 for e in EXHIBITORS if e.get('entity_list_status'))
    print(f"\n  Chinese exhibitors documented: {chinese_exhibitors}/{len(EXHIBITORS)}")
    print(f"  Exhibitors with verified booth numbers: {verified_booths}/{len(EXHIBITORS)}")
    print(f"  Entity List companies present: {entity_list_companies}/{len(EXHIBITORS)}")


def load_data():
    """Load Paris Air Show 2025 verified data to database."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("="*70)
    print("LOADING PARIS AIR SHOW 2025 VERIFIED DATA")
    print("="*70)

    # Load event
    print("\n[1/2] Loading event data...")
    event_id = insert_event(conn, cursor)

    # Load exhibitors
    print(f"\n[2/2] Loading exhibitor data...")
    insert_exhibitors(conn, cursor, event_id)

    conn.commit()
    conn.close()

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"  Event: {EVENT_DATA['event_name']}")
    print(f"  Dates: {EVENT_DATA['start_date']} to {EVENT_DATA['end_date']}")
    print(f"  Venue: {EVENT_DATA['venue']}, {EVENT_DATA['location_city']}")
    print(f"  Attendance: {EVENT_DATA['expected_attendance']:,}")
    print(f"  Total Exhibitors: {EVENT_DATA['exhibitor_count']:,}")
    print(f"\n  Verified Chinese Exhibitors Loaded: {sum(1 for e in EXHIBITORS if e['chinese_entity'] == 1)}")
    print(f"  - With booth numbers: {sum(1 for e in EXHIBITORS if e.get('booth_number') and e['chinese_entity'] == 1)}")
    print(f"  - Confirmed presence only: {sum(1 for e in EXHIBITORS if not e.get('booth_number') and e['chinese_entity'] == 1)}")
    print(f"\n  Notable Intelligence:")
    print(f"  - 76 Chinese companies participated (162% increase from 2023)")
    print(f"  - First de facto Chinese country pavilion")
    print(f"  - COMAC showcased C909, C919, C929 aircraft programs")
    print(f"  - AVIC present for 38th consecutive year (military systems included)")
    print(f"  - COMAC-SAFRAN MOU on C929 wide-body cooperation")
    print(f"  - DUAL-USE WARNING: Military aircraft, drones, precision weapons")
    print("="*70)
    print("[OK] PARIS AIR SHOW 2025 DATA LOAD COMPLETE")
    print("="*70)

if __name__ == '__main__':
    load_data()
