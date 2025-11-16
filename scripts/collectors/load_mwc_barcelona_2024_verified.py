#!/usr/bin/env python3
"""
MWC Barcelona 2024 - VERIFIED DATA ONLY
==============================================
Loads verified data from Mobile World Congress Barcelona 2024 (February 26-29, 2024)

DATA VERIFICATION PROTOCOL:
- ALL data has source citations
- NO fabricated details
- confidence_level field indicates verification status

Sources:
- Xinhua News (english.news.cn) - Chinese participation statistics
- China Daily (chinadaily.com.cn) - Exhibition coverage
- People's Daily (en.people.cn) - Chinese company coverage
- Digitimes (digitimes.com) - Industry analysis
- Huawei Official (carrier.huawei.com) - Company participation

Created: 2025-10-27
Last verified: 2025-10-27
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('F:/OSINT_WAREHOUSE/osint_master.db')

# Event metadata (VERIFIED from official sources)
EVENT_DATA = {
    'event_id': 'MWC_BARCELONA_2024',
    'event_name': 'Mobile World Congress Barcelona 2024',
    'event_series': 'MWC Barcelona',
    'edition': '2024',
    'event_type': 'Trade Show',
    'technology_domain': 'Mobile & Telecommunications',
    'start_date': '2024-02-26',  # Source: Xinhua News, China Daily
    'end_date': '2024-02-29',
    'location_city': 'Barcelona',
    'location_country': 'Spain',
    'location_country_code': 'ES',
    'venue': 'Fira de Barcelona Gran Via',
    'organizer_name': 'GSMA',
    'organizer_type': 'Industry Association',
    'website_url': 'https://www.mwcbarcelona.com',
    'expected_attendance': 95000,  # Source: Digitimes 2024-02-22
    'exhibitor_count': 2400,  # Source: Xinhua News 2024-02-26
    'event_scope': 'International',
    'dual_use_indicator': True,  # Telecom infrastructure has dual-use applications
    'verification_sources': 'Xinhua News 2024-02-26; China Daily 2024-02-27; People\'s Daily 2024-02-28; Digitimes 2024-02-22',
    'notes': '300 Chinese companies (12.5% of exhibitors). Huawei was largest exhibitor. Focus: 5G/5G-A, AI integration, network infrastructure.'
}

# Exhibitors (VERIFIED ONLY)
EXHIBITORS = [
    {
        'entity_name': 'Huawei Technologies',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'entity_list_status': 'US Entity List (2019)',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': '5G, ICT products, network infrastructure',
        'products_displayed': 'Comprehensive 5G technology suite, ICT products and solutions',
        'verification_source': 'Digitimes 2024-02-22; Xinhua News 2024-02-26; Huawei official carrier.huawei.com/en/events/mwc2024',
        'confidence_level': 'confirmed',
        'notes': 'Largest exhibitor at MWC 2024 per GSMA. Despite geopolitical tensions, maintained dominant presence.'
    },
    {
        'entity_name': 'ZTE Corporation',
        'entity_type': 'State-Owned Enterprise',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'state_owned',
        'entity_list_status': None,
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': '5G-A, AON, computing power, energy solutions',
        'products_displayed': 'Groundbreaking 5G-A achievements, AON technology, computing power solutions, energy systems, cutting-edge terminals',
        'verification_source': 'Digitimes 2024-02-22; China Daily 2024-02-27; People\'s Daily 2024-02-28',
        'confidence_level': 'confirmed',
        'notes': 'Strategic focus on 5G-A (5G Advanced) technology, next-generation network infrastructure.'
    },
    {
        'entity_name': 'China Mobile',
        'entity_type': 'State-Owned Enterprise',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'state_owned',
        'entity_list_status': 'US Investment Ban (2021)',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Mobile network operations, 5G services',
        'products_displayed': '5G network services and infrastructure (specific products not detailed in sources)',
        'verification_source': 'Xinhua News 2024-02-26; China Daily 2024-02-27',
        'confidence_level': 'confirmed_presence',
        'notes': 'World\'s largest mobile operator by subscribers. US investment ban but European presence unrestricted.'
    },
    {
        'entity_name': 'China Telecom',
        'entity_type': 'State-Owned Enterprise',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'state_owned',
        'entity_list_status': 'US Investment Ban (2021)',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Telecommunications services, network infrastructure',
        'products_displayed': 'Telecom services and infrastructure (specific products not detailed in sources)',
        'verification_source': 'Xinhua News 2024-02-26; China Daily 2024-02-27',
        'confidence_level': 'confirmed_presence',
        'notes': 'Major Chinese telecom operator. US investment restrictions don\'t prevent European trade show participation.'
    },
    {
        'entity_name': 'Lenovo',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'entity_list_status': None,
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Mobile devices, PCs, enterprise technology',
        'products_displayed': 'Mobile and enterprise technology portfolio (specific products not detailed in sources)',
        'verification_source': 'Xinhua News 2024-02-26',
        'confidence_level': 'confirmed_presence',
        'notes': 'Leading Chinese PC and mobile device manufacturer.'
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
        'technology_focus': 'Smartphones, IoT devices, consumer electronics',
        'products_displayed': 'Smartphone and IoT device portfolio (specific products not detailed in sources)',
        'verification_source': 'Xinhua News 2024-02-26; China Daily 2024-02-27',
        'confidence_level': 'confirmed_presence',
        'notes': 'Major smartphone manufacturer and IoT ecosystem provider.'
    },
    {
        'entity_name': 'iFlytek',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'entity_list_status': 'US Entity List (2019)',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'AI voice recognition, natural language processing',
        'products_displayed': 'AI voice and language technology (specific products not detailed in sources)',
        'verification_source': 'Xinhua News 2024-02-26',
        'confidence_level': 'confirmed_presence',
        'notes': 'AI company on US Entity List. Demonstrates European market access despite US restrictions.'
    },
    {
        'entity_name': 'Honor',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'entity_list_status': None,
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Smartphones, consumer electronics',
        'products_displayed': 'Smartphone lineup (specific models not detailed in sources)',
        'verification_source': 'Digitimes 2024-02-22; People\'s Daily 2024-02-28',
        'confidence_level': 'confirmed_presence',
        'notes': 'Former Huawei brand, now independent. Captured significant attention at MWC 2024.'
    },
]

# Intelligence Summary
INTELLIGENCE_SUMMARY = """
MWC Barcelona 2024 - Chinese Participation Analysis
===================================================

VERIFIED CHINESE PRESENCE:
- 300 Chinese companies out of 2,400 total exhibitors (12.5%)
- 8 major companies documented with verified sources

HUAWEI DOMINANCE:
- Huawei = LARGEST EXHIBITOR at MWC 2024 (per GSMA)
- Despite US Entity List status since 2019
- Comprehensive 5G technology suite displayed
- Demonstrates: US restrictions ≠ European market exclusion

ENTITY LIST PARADOX:
| Company | US Status | MWC 2024 Presence |
|---------|-----------|------------------|
| Huawei | Entity List (2019) | ✅ LARGEST exhibitor |
| iFlytek | Entity List (2019) | ✅ Present |
| China Mobile | Investment Ban (2021) | ✅ Present |
| China Telecom | Investment Ban (2021) | ✅ Present |

**Finding:** US Entity List/Investment bans DO NOT prevent European trade show participation.

TECHNOLOGY FOCUS:
- 5G and 5G-A (5G Advanced) infrastructure
- AI integration in telecommunications
- Network computing power
- Energy-efficient solutions
- Terminal devices (smartphones, IoT)

STRATEGIC OBSERVATIONS:
1. Chinese telecom dominance in Europe continues
2. Huawei maintains market leadership despite US sanctions
3. State-owned telecom operators (China Mobile, China Telecom) unrestricted in EU
4. 5G-A technology (ZTE) positioning for next-generation networks
5. AI voice technology (iFlytek) present despite Entity List

DUAL-USE CONCERNS:
- 5G infrastructure with potential surveillance applications
- Network computing power = data collection capability
- State-owned telecom operators = potential government access
- AI voice recognition technology

GEOPOLITICAL IMPLICATIONS:
- US-EU policy divergence on Chinese telecom
- European operators depend on Huawei/ZTE infrastructure
- Chinese state-owned telecom operators have European market access
- US sanctions ineffective in European context

DATA LIMITATIONS:
- Complete list of 300 Chinese exhibitors not publicly available
- Only 8 major exhibitors documented with verification
- Booth locations and sizes not published
- Product specifications limited to general technology categories
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
    print(f"     Chinese Exhibitors: 300 (12.5%)")
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
        booth_info = exhibitor.get('booth_size') or 'Booth unverified'
        conf_level = exhibitor['confidence_level']
        entity_list = '[ENTITY LIST]' if exhibitor.get('entity_list_status') else ''

        print(f"  {chinese_flag} {exhibitor['entity_name']:30} | {booth_info:20} | {conf_level} {entity_list}")

    entity_list_count = sum(1 for e in EXHIBITORS if e.get('entity_list_status'))
    print(f"\n  Entity List/US-restricted companies: {entity_list_count}/{len(EXHIBITORS)}")


def load_data():
    """Load MWC Barcelona 2024 verified data to database."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("="*70)
    print("LOADING MWC BARCELONA 2024 VERIFIED DATA")
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
    print(f"  - Entity List/US-restricted: {sum(1 for e in EXHIBITORS if e.get('entity_list_status'))}")
    print(f"\n  Notable Intelligence:")
    print(f"  - 300 Chinese companies participated (12.5% of total)")
    print(f"  - Huawei: LARGEST exhibitor at MWC 2024 (per GSMA)")
    print(f"  - 4 companies with US restrictions/bans (unrestricted in EU)")
    print(f"  - Focus: 5G/5G-A, AI integration, network infrastructure")
    print(f"  - DUAL-USE WARNING: Telecom infrastructure, state-owned operators")
    print("="*70)
    print("[OK] MWC BARCELONA 2024 DATA LOAD COMPLETE")
    print("="*70)

if __name__ == '__main__':
    load_data()
