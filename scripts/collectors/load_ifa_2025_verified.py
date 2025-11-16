#!/usr/bin/env python3
"""
IFA 2025 - VERIFIED DATA ONLY
==============================================
Loads verified data from IFA 2025 (September 5-9, 2025)
International Consumer Electronics Trade Show in Berlin.

DATA VERIFICATION PROTOCOL:
- ALL data has source citations
- NO fabricated details
- confidence_level field indicates verification status

Sources:
- China Daily (chinadaily.com.cn) - Chinese exhibitor statistics, product launches
- Xinhua News (english.news.cn) - Chinese participation analysis
- Global Times (globaltimes.cn) - Exhibition coverage
- IFA Official Website (ifa-berlin.com) - Event details
- DJI Official (dji.com) - Product announcements
- Hisense Official (hisense.com) - Product specifications

Created: 2025-10-27
Last verified: 2025-10-27
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('F:/OSINT_WAREHOUSE/osint_master.db')

# Event metadata (VERIFIED from official sources)
EVENT_DATA = {
    'event_id': 'IFA_2025',
    'event_name': 'IFA 2025',
    'event_series': 'IFA',
    'edition': '2025',
    'event_type': 'Trade Show',
    'technology_domain': 'Consumer Electronics',
    'start_date': '2025-09-05',  # Source: ifa-berlin.com official
    'end_date': '2025-09-09',
    'location_city': 'Berlin',
    'location_country': 'Germany',
    'location_country_code': 'DE',
    'venue': 'Messe Berlin Exhibition Grounds',
    'organizer_name': 'Messe Berlin GmbH',
    'organizer_type': 'Exhibition Company',
    'website_url': 'https://www.ifa-berlin.com',
    'expected_attendance': 182000,  # Source: China Daily 2025-09-10
    'exhibitor_count': 1795,  # Source: China Daily 2025-09-10
    'event_scope': 'International',
    'dual_use_indicator': False,  # Consumer electronics focus
    'verification_sources': 'ifa-berlin.com; China Daily 2025-09-10; Xinhua News 2025-09-06; Global Times 2025-09-09',
    'notes': '700+ Chinese companies (38% of exhibitors) - largest foreign participant group. Focus: consumer electronics, home appliances, AI-powered devices.'
}

# Exhibitors (VERIFIED ONLY - from official press releases and credible news sources)
EXHIBITORS = [
    {
        'entity_name': 'Hisense',
        'entity_type': 'State-Owned Enterprise',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'state_owned',
        'entity_list_status': None,
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Display technology, smart TVs, home appliances',
        'products_displayed': '116-inch Mini LED TV (world record), Mini LED Pro technology, laser projectors',
        'verification_source': 'China Daily 2025-09-10; Xinhua News 2025-09-06; Hisense official press release 2025-09-04',
        'confidence_level': 'confirmed',
        'notes': 'Unveiled 116-inch Mini LED TV, largest at IFA 2025. Major presence in European consumer electronics market.'
    },
    {
        'entity_name': 'DJI',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'entity_list_status': 'US Investment Ban (2021)',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Consumer drones, imaging technology, microphones',
        'products_displayed': 'DJI Mic 3 (wireless microphone system), DJI Osmo 360 (360-degree camera)',
        'verification_source': 'DJI official announcement 2025-09-05 (dji.com); China Daily 2025-09-10; Global Times 2025-09-09',
        'confidence_level': 'confirmed',
        'notes': 'Launched two new products at IFA 2025. Present in European market despite US investment restrictions.'
    },
    {
        'entity_name': 'Haier',
        'entity_type': 'State-Owned Enterprise',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'state_owned',
        'entity_list_status': None,
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Smart home appliances, IoT ecosystem',
        'products_displayed': 'Smart home appliances, connected kitchen ecosystem (specific models not detailed in sources)',
        'verification_source': 'Xinhua News 2025-09-06; China Daily 2025-09-10',
        'confidence_level': 'confirmed_presence',
        'notes': 'One of major Chinese home appliance exhibitors. Focus on European smart home market.'
    },
    {
        'entity_name': 'TCL',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'entity_list_status': None,
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Display technology, smart TVs, consumer electronics',
        'products_displayed': 'QD-Mini LED TVs, smart home products (specific models not detailed in sources)',
        'verification_source': 'China Daily 2025-09-10; Xinhua News 2025-09-06',
        'confidence_level': 'confirmed_presence',
        'notes': 'Regular IFA exhibitor, major display technology presence in European market.'
    },
    {
        'entity_name': 'Midea',
        'entity_type': 'State-Owned Enterprise',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'state_owned',
        'entity_list_status': None,
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Home appliances, HVAC systems, robotics',
        'products_displayed': 'Smart appliances, connected home systems (specific models not detailed in sources)',
        'verification_source': 'Xinhua News 2025-09-06; China Daily 2025-09-10',
        'confidence_level': 'confirmed_presence',
        'notes': 'One of largest Chinese home appliance manufacturers. Strong European market presence.'
    },
    {
        'entity_name': 'Xiaomi',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'entity_list_status': None,
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Consumer electronics, smartphones, IoT devices',
        'products_displayed': 'Smart home ecosystem products (specific models not detailed in sources)',
        'verification_source': 'China Daily 2025-09-10; Xinhua News 2025-09-06',
        'confidence_level': 'confirmed_presence',
        'notes': 'Major presence in European consumer electronics market. Focus on IoT ecosystem.'
    },
]

# Intelligence Summary
INTELLIGENCE_SUMMARY = """
IFA 2025 - Chinese Participation Analysis
==========================================

VERIFIED CHINESE PRESENCE:
- 700+ Chinese companies participated
- 38% of 1,795 total exhibitors
- Largest foreign participant group
- 6 major companies documented with verified sources

KEY PRODUCT LAUNCHES:
- Hisense: 116-inch Mini LED TV (world record size)
- DJI: Mic 3, Osmo 360 (new product launches)
- Multiple smart home and IoT ecosystem products

STRATEGIC OBSERVATIONS:
1. Chinese consumer electronics dominance in European market
2. DJI present despite US investment ban - European market access unrestricted
3. Heavy focus on display technology (Mini LED, OLED)
4. Smart home and IoT ecosystem integration
5. AI-powered consumer devices

MARKET INTELLIGENCE:
- 38% Chinese exhibitor ratio indicates market dominance
- Major SOEs (Hisense, Haier, Midea) and private companies (DJI, TCL, Xiaomi) both present
- European consumer electronics market heavily reliant on Chinese manufacturing
- Product launches timed with European market entry

ENTITY LIST IMPLICATIONS:
- DJI present despite US investment restrictions
- No impact on European trade show participation
- Demonstrates bifurcation of US/EU tech policy

COMPETITIVE ANALYSIS:
- Chinese companies focus on premium consumer segment (large displays, advanced features)
- World-first product launches (Hisense 116-inch TV)
- Strong brand presence in European retail market

DATA LIMITATIONS:
- Complete list of 700+ Chinese exhibitors not publicly available
- Only 6 major exhibitors documented with verification
- Most booth locations not published
- Product details limited to major launches covered in media
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
    print(f"     Chinese Exhibitors: 700+ (38%)")
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
        entity_list = '[RESTRICTED]' if exhibitor.get('entity_list_status') else ''

        print(f"  {chinese_flag} {exhibitor['entity_name']:30} | {booth_info:20} | {conf_level} {entity_list}")

    verified_booths = sum(1 for e in EXHIBITORS if e.get('booth_number'))
    restricted_companies = sum(1 for e in EXHIBITORS if e.get('entity_list_status'))
    print(f"\n  Exhibitors with verified booth numbers: {verified_booths}/{len(EXHIBITORS)}")
    print(f"  US-restricted companies present: {restricted_companies}/{len(EXHIBITORS)}")


def load_data():
    """Load IFA 2025 verified data to database."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("="*70)
    print("LOADING IFA 2025 VERIFIED DATA")
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
    print(f"  - 700+ Chinese companies participated (38% of total)")
    print(f"  - Largest foreign participant group")
    print(f"  - DJI present despite US investment restrictions")
    print(f"  - Hisense launched world-record 116-inch Mini LED TV")
    print("="*70)
    print("[OK] IFA 2025 DATA LOAD COMPLETE")
    print("="*70)

if __name__ == '__main__':
    load_data()
