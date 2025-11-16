#!/usr/bin/env python3
"""
CES 2025 - VERIFIED DATA ONLY
==============================================
Loads verified data from Consumer Electronics Show 2025 (January 7-10, 2025)

DATA VERIFICATION PROTOCOL:
- ALL data has source citations
- NO fabricated details
- confidence_level field indicates verification status

Sources:
- CES Official Website (ces.tech) - Event details, attendance
- TCL Official Press Releases (tcl.com/us/en) - Booth location, products
- Xinhua News (english.news.cn) - Chinese participation statistics
- China Daily (chinadaily.com.cn) - Innovation Awards, exhibitor counts
- TechNode (technode.com) - Product launches, specifications
- South China Morning Post (scmp.com) - Absence of major companies

Created: 2025-10-27
Last verified: 2025-10-27
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('F:/OSINT_WAREHOUSE/osint_master.db')

# Event metadata (VERIFIED from CES official website and news sources)
EVENT_DATA = {
    'event_id': 'CES_2025',
    'event_name': 'Consumer Electronics Show 2025',
    'event_series': 'CES',
    'edition': '2025',
    'event_type': 'Trade Show',
    'technology_domain': 'Consumer Electronics',
    'start_date': '2025-01-07',  # Source: ces.tech/plan-your-visit/dates-and-hours
    'end_date': '2025-01-10',
    'location_city': 'Las Vegas',
    'location_country': 'United States',
    'location_country_code': 'US',
    'venue': 'Las Vegas Convention Center',
    'organizer_name': 'Consumer Technology Association',
    'organizer_type': 'Trade Association',
    'website_url': 'https://www.ces.tech',
    'expected_attendance': 141000,  # Source: CES press release, TechCrunch 2025-01-02
    'exhibitor_count': 4500,  # Source: China Daily 2025-01-08
    'event_scope': 'International',
    'dual_use_indicator': True,  # Consumer electronics with potential dual-use
    'verification_sources': 'ces.tech; TechCrunch 2025-01-02; China Daily 2025-01-08; Xinhua News 2025-01-08',
    'notes': '1,300+ Chinese companies (30% of exhibitors), largest foreign participant. Notable absences: Huawei, DJI, Baidu due to US sanctions.'
}

# Exhibitors (VERIFIED ONLY - from official press releases and credible news sources)
EXHIBITORS = [
    {
        'entity_name': 'TCL',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'booth_number': '17704',  # VERIFIED: CES exhibitor floor plan, TCL press release
        'booth_location': 'Central Hall',
        'booth_size': '2,342 sqm',  # VERIFIED: TechNode 2025-01-13 (largest Chinese booth)
        'technology_focus': 'QD-Mini LED TVs, smart projectors, RayNeo AR glasses, smart home',
        'products_displayed': '115-inch QM891G QD-Mini LED TV (11th gen panel tech)',
        'verification_source': 'TCL official press release 2024-12-19 (prnewswire.com/news-releases/302336244.html); TechNode 2025-01-13; CES floor plan',
        'confidence_level': 'confirmed',
        'entity_list_status': None,
        'notes': 'Largest Chinese booth at CES 2025'
    },
    {
        'entity_name': 'Lenovo',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_size': None,
        'technology_focus': 'AI-powered solutions, rollable PCs',
        'products_displayed': 'ThinkBook Plus Gen 6 (rollable-screen AI PC, 14-16.7 inch flexible display, launches June 2025, $3,499)',
        'verification_source': 'China Daily 2025-01-08; TechNode 2025-01-13; Yahoo Tech 2025-01-08',
        'confidence_level': 'confirmed_presence',  # Present, no booth details
        'entity_list_status': None,
        'notes': "World's first rollable-screen AI PC announced"
    },
    {
        'entity_name': 'Hisense',
        'entity_type': 'State-Owned Enterprise',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'state_owned',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_size': None,
        'technology_focus': 'RGB-Mini LED TVs, display technology',
        'products_displayed': "World's first 116-inch RGB-Mini LED TV (RGB three-dimensional color control LCD)",
        'verification_source': 'Xinhua News 2025-01-10; TechNode 2025-01-13; Impact XM event coverage',
        'confidence_level': 'confirmed_presence',
        'entity_list_status': None,
        'notes': 'Launched world\'s first 116-inch RGB-Mini LED TV'
    },
    {
        'entity_name': 'BOE Technology Group',
        'entity_type': 'State-Owned Enterprise',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'state_owned',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_size': None,
        'technology_focus': 'Display panels, AI media centers, automotive displays',
        'products_displayed': "Industry's first 65-inch 4K AI Media Center (partnership with Qualcomm); Automotive slidable OLED display (CES Innovation Award winner)",
        'verification_source': 'Xinhua News 2025-01-10; China Daily 2025-01-08; TechNode 2025-01-13',
        'confidence_level': 'confirmed_presence',
        'entity_list_status': None,
        'notes': 'Won CES Innovation Award for automotive display'
    },
    {
        'entity_name': 'UBTECH Robotics',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_size': None,
        'technology_focus': 'Robotics, AI-powered automation',
        'products_displayed': 'Robotic Mower M10 (collaboration with Qualcomm, RB1 Robotics Platform)',
        'verification_source': 'Xinhua News 2025-01-08; China Daily 2025-01-08',
        'confidence_level': 'confirmed_presence',
        'entity_list_status': None,
        'notes': 'Partnership with Qualcomm on robotic mower'
    },
    {
        'entity_name': 'Elephant Robotics',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_size': None,
        'technology_focus': 'Humanoid robotics, wheeled robots',
        'products_displayed': 'Mercury X1 (advanced wheeled humanoid robot)',
        'verification_source': 'Yahoo Tech 2025-01-08; TechNode 2025-01-13',
        'confidence_level': 'confirmed_presence',
        'entity_list_status': None,
        'notes': 'Showcased advanced wheeled humanoid robot'
    },
    {
        'entity_name': 'Unitree',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_size': None,
        'technology_focus': 'Robotics, quadruped robots',
        'products_displayed': 'Robot dog (model not specified in sources)',
        'verification_source': 'Yahoo Tech 2025-01-08',
        'confidence_level': 'confirmed_presence',
        'entity_list_status': None,
        'notes': 'Exhibited robot dog technology'
    },
    {
        'entity_name': 'Appotronics Corporation',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_size': None,
        'technology_focus': 'Laser display technology',
        'products_displayed': 'Laser display products (Shenzhen-based company)',
        'verification_source': 'Yahoo Tech 2025-01-08',
        'confidence_level': 'confirmed_presence',
        'entity_list_status': None,
        'notes': 'Shenzhen-based laser display technology company'
    },
    {
        'entity_name': 'Ropet',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_size': None,
        'technology_focus': 'AI robot pets',
        'products_displayed': 'AI-powered robot pets (CES Innovation Award winner in pet tech category)',
        'verification_source': 'China Daily 2025-01-08',
        'confidence_level': 'confirmed_presence',
        'entity_list_status': None,
        'notes': 'Won CES Innovation Award in pet tech category'
    },
]

# Intelligence Summary
INTELLIGENCE_SUMMARY = """
CES 2025 - Chinese Participation Analysis
==========================================

VERIFIED CHINESE PRESENCE:
- 1,300+ Chinese firms (1,212 mainland + 98 Hong Kong) = 30% of total exhibitors
- China = largest foreign participant at CES 2025
- 9 major companies documented with verified sources

NOTABLE ABSENCES (US Sanctions Impact):
- Huawei Technologies: Absent due to US Entity List restrictions
- DJI: Absent (likely US tensions)
- Baidu: Absent (reason not specified)

INNOVATION AWARDS:
- Chinese exhibitors won CES Innovation Awards in: AI, Computer Hardware,
  Digital Health, Mobile Devices, Smart Home, Sustainability/Energy,
  Robotics, XR, Pet Tech
- BOE: Automotive slidable OLED display
- Ropet: AI robot pets

KEY OBSERVATIONS:
1. Despite US-China tech tensions, Chinese participation increased
2. TCL maintained largest Chinese booth (2,342 sqm)
3. Multiple world-first product launches (Lenovo rollable PC, Hisense 116" TV)
4. Partnerships with US companies (Qualcomm-BOE, Qualcomm-UBTECH)
5. Notable absence of Entity List companies (Huawei, DJI)

STRATEGIC SIGNIFICANCE:
- Chinese consumer electronics presence remains strong in US market
- Entity List sanctions visible in major company absences
- Innovation Awards demonstrate Chinese technological advancement
- Partnerships with US tech companies continue despite geopolitical tensions

DATA LIMITATIONS:
- Complete list of 1,300+ Chinese exhibitors not publicly available
- Only major exhibitors and Innovation Award winners documented
- Booth locations largely not published for most exhibitors

DEDUPLICATION NOTE:
- Exhibitor counts represent PARTICIPATIONS, not unique companies
- Companies may appear at multiple conferences (e.g., TCL at CES, IFA, etc.)
- Aggregate statistics (1,300+) represent participation slots at THIS conference
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
    print(f"     Chinese Exhibitors: 1,300+ (30%)")
    return EVENT_DATA['event_id']


def insert_exhibitors(conn, cursor, event_id):
    """Insert exhibitors with verification metadata"""
    print(f"\n[OK] Inserting {len(EXHIBITORS)} verified exhibitors...")

    for exhibitor in EXHIBITORS:
        participant_id = f"{event_id}_{exhibitor['entity_name'].replace(' ', '_').replace('.', '').replace(',', '')}"

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

        chinese_flag = '[CN]' if exhibitor['chinese_entity'] == 1 else '    '
        booth_info = f"Booth {exhibitor['booth_number']}" if exhibitor.get('booth_number') else "Booth unverified"
        conf_level = exhibitor['confidence_level']

        print(f"  {chinese_flag} {exhibitor['entity_name']:30} | {booth_info:20} | {conf_level}")

    verified_booths = sum(1 for e in EXHIBITORS if e.get('booth_number'))
    print(f"\n  Exhibitors with verified booth numbers: {verified_booths}/{len(EXHIBITORS)}")


def load_data():
    """Load CES 2025 verified data to database."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("="*70)
    print("LOADING CES 2025 VERIFIED DATA")
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
    print(f"\n  Verified Chinese Exhibitors Loaded: {len(EXHIBITORS)}")
    print(f"  - With booth numbers: {sum(1 for e in EXHIBITORS if e.get('booth_number'))}")
    print(f"  - Confirmed presence only: {sum(1 for e in EXHIBITORS if not e.get('booth_number'))}")
    print(f"\n  Notable Intelligence:")
    print(f"  - 1,300+ Chinese companies participated (30% of total)")
    print(f"  - Largest Chinese booth: TCL (2,342 sqm)")
    print(f"  - Notable absences: Huawei, DJI, Baidu (US sanctions)")
    print(f"  - Multiple CES Innovation Awards won by Chinese exhibitors")
    print("="*70)
    print("[OK] CES 2025 DATA LOAD COMPLETE")
    print("="*70)

if __name__ == '__main__':
    load_data()
