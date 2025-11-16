#!/usr/bin/env python3
"""
Hannover Messe 2025 - VERIFIED DATA ONLY
==============================================
Loads verified data from Hannover Messe 2025 (March 31 - April 4, 2025)
World's leading industrial technology trade fair.

DATA VERIFICATION PROTOCOL:
- ALL data has source citations
- NO fabricated details
- confidence_level field indicates verification status

Sources:
- Xinhua News (english.news.cn) - Chinese exhibitor statistics, Huawei presence
- CCTV English (english.cctv.com) - Exhibition coverage, technology focus
- Huawei Official (huawei.com) - Booth location, product details
- Deutsche Messe AG (hannovermesse.de) - Official event organizer
- China Daily (chinadaily.com.cn) - Chinese participation analysis

Created: 2025-10-27
Last verified: 2025-10-27
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('F:/OSINT_WAREHOUSE/osint_master.db')

# Event metadata (VERIFIED from official sources)
EVENT_DATA = {
    'event_id': 'HANNOVER_MESSE_2025',
    'event_name': 'Hannover Messe 2025',
    'event_series': 'Hannover Messe',
    'edition': '2025',
    'event_type': 'Trade Show',
    'technology_domain': 'Industrial Technology',
    'start_date': '2025-03-31',  # Source: hannovermesse.de official
    'end_date': '2025-04-04',
    'location_city': 'Hannover',
    'location_country': 'Germany',
    'location_country_code': 'DE',
    'venue': 'Hannover Exhibition Grounds',
    'organizer_name': 'Deutsche Messe AG',
    'organizer_type': 'Exhibition Company',
    'website_url': 'https://www.hannovermesse.de',
    'expected_attendance': 130000,  # Source: Xinhua News 2025-04-02
    'exhibitor_count': 4000,  # Source: Xinhua News 2025-04-02 (approximate)
    'event_scope': 'International',
    'dual_use_indicator': True,  # Industrial automation has dual-use applications
    'verification_sources': 'hannovermesse.de; Xinhua News 2025-04-02; CCTV English 2025-04-05; China Daily 2025-04-01',
    'notes': '~1,000 Chinese companies participated (2nd largest exhibitor group after Germany). Focus: AI, digitalization, industrial automation, energy transition.'
}

# Exhibitors (VERIFIED ONLY - from official sources and credible news)
EXHIBITORS = [
    {
        'entity_name': 'Huawei Technologies',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'entity_list_status': 'US Entity List (2019)',
        'booth_number': 'Hall 14, K52',  # VERIFIED: Huawei official announcement
        'booth_location': 'Hall 14',
        'booth_size': None,  # NOT FOUND in public sources
        'technology_focus': 'Industrial Internet, digitalization, AI automation',
        'products_displayed': 'FusionPlant Industrial Internet Platform (digital twin technology, AI-powered production optimization)',
        'verification_source': 'Huawei official website 2025-03-28 (huawei.com/en/events/hannovermesse2025); Xinhua News 2025-04-02; CCTV English 2025-04-05',
        'confidence_level': 'confirmed',
        'notes': 'Showcased industrial IoT and digital manufacturing solutions. Featured FusionPlant platform for smart factory applications.'
    },
    {
        'entity_name': 'Sany Group',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'entity_list_status': None,
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Heavy machinery, construction equipment, renewable energy',
        'products_displayed': 'Electrified construction equipment, wind turbine components (participation mentioned, specific products not detailed)',
        'verification_source': 'China Daily 2025-04-01; Xinhua News 2025-04-02',
        'confidence_level': 'confirmed_presence',
        'entity_list_status': None,
        'notes': 'One of major Chinese heavy machinery exhibitors. Focus on electrification and renewable energy equipment.'
    },
    {
        'entity_name': 'Envision Energy',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'entity_list_status': None,
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Smart energy, wind turbines, battery technology',
        'products_displayed': 'Energy management systems, smart grid technology (participation mentioned, specific products not detailed)',
        'verification_source': 'Xinhua News 2025-04-02; China Daily 2025-04-01',
        'confidence_level': 'confirmed_presence',
        'entity_list_status': None,
        'notes': 'Shanghai-based renewable energy technology company. Major player in European wind energy market.'
    },
    {
        'entity_name': 'BYD',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'entity_list_status': None,
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Electric vehicles, battery technology, energy storage',
        'products_displayed': 'Industrial battery systems, electric commercial vehicles (participation mentioned, specific products not detailed)',
        'verification_source': 'CCTV English 2025-04-05; Xinhua News 2025-04-02',
        'confidence_level': 'confirmed_presence',
        'entity_list_status': None,
        'notes': 'Focus on industrial energy storage and commercial vehicle electrification solutions.'
    },
]

# Intelligence Summary
INTELLIGENCE_SUMMARY = """
Hannover Messe 2025 - Chinese Participation Analysis
====================================================

VERIFIED CHINESE PRESENCE:
- ~1,000 Chinese companies participated
- 2nd largest exhibitor group (after Germany)
- 25% of total exhibitors
- 4 major companies documented with verified sources

KEY TECHNOLOGIES SHOWCASED:
- Industrial Internet and digitalization (Huawei)
- Renewable energy equipment (Sany, Envision)
- Battery and energy storage (BYD)
- AI-powered automation
- Smart manufacturing

STRATEGIC OBSERVATIONS:
1. Huawei participation despite US Entity List status - European market access continues
2. Heavy focus on "Made in China 2025" priority sectors:
   - Industrial automation
   - Renewable energy
   - Smart manufacturing
3. Chinese companies positioning in European energy transition market

ENTITY LIST IMPLICATIONS:
- Huawei present (Hall 14, K52) - demonstrates European trade show access despite US restrictions
- No other Entity List companies identified among documented exhibitors
- EU does not follow US Entity List restrictions for trade shows

DUAL-USE TECHNOLOGY CONCERNS:
- Industrial IoT platforms (digital twin technology)
- AI-powered production optimization
- Smart grid and energy management systems
- Potential applications in military manufacturing

DATA LIMITATIONS:
- Complete list of 1,000 Chinese exhibitors not publicly available
- Only 4 major exhibitors documented with verification
- Most booth locations not published
- Product details limited for most exhibitors
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
    print(f"     Chinese Exhibitors: ~1,000 (25%)")
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
        entity_list = '[ENTITY LIST]' if exhibitor.get('entity_list_status') else ''

        print(f"  {chinese_flag} {exhibitor['entity_name']:30} | {booth_info:20} | {conf_level} {entity_list}")

    verified_booths = sum(1 for e in EXHIBITORS if e.get('booth_number'))
    entity_list_companies = sum(1 for e in EXHIBITORS if e.get('entity_list_status'))
    print(f"\n  Exhibitors with verified booth numbers: {verified_booths}/{len(EXHIBITORS)}")
    print(f"  Entity List companies present: {entity_list_companies}/{len(EXHIBITORS)}")


def load_data():
    """Load Hannover Messe 2025 verified data to database."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("="*70)
    print("LOADING HANNOVER MESSE 2025 VERIFIED DATA")
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
    print(f"  - ~1,000 Chinese companies participated (25% of total)")
    print(f"  - 2nd largest exhibitor group after Germany")
    print(f"  - Huawei present despite US Entity List status")
    print(f"  - Focus: Industrial IoT, renewable energy, AI automation")
    print("="*70)
    print("[OK] HANNOVER MESSE 2025 DATA LOAD COMPLETE")
    print("="*70)

if __name__ == '__main__':
    load_data()
