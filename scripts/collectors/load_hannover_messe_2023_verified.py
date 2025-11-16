#!/usr/bin/env python3
"""
Hannover Messe 2023 - VERIFIED DATA ONLY
==============================================
Loads verified data from Hannover Messe 2023 (April 17-21, 2023)
World's leading industrial technology trade fair.

DATA VERIFICATION PROTOCOL:
- ALL data has source citations
- NO fabricated details
- confidence_level field indicates verification status

Sources:
- ExamineChina (examinechina.com) - Chinese participation statistics
- Automation.com (automation.com) - Event coverage
- Robotics & Automation News (roboticsandautomationnews.com) - AI/robotics focus
- JAKA Robotics (jaka.com) - Company participation
- Promwad (promwad.com) - Event overview

Created: 2025-10-27
Last verified: 2025-10-27
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('F:/OSINT_WAREHOUSE/osint_master.db')

# Event metadata (VERIFIED from Western sources)
EVENT_DATA = {
    'event_id': 'HANNOVER_MESSE_2023',
    'event_name': 'Hannover Messe 2023',
    'event_series': 'Hannover Messe',
    'edition': '2023',
    'event_type': 'Trade Show',
    'technology_domain': 'Industrial Technology & Automation',
    'start_date': '2023-04-17',  # Source: Multiple sources
    'end_date': '2023-04-21',
    'location_city': 'Hannover',
    'location_country': 'Germany',
    'location_country_code': 'DE',
    'venue': 'Hannover Fairground',
    'organizer_name': 'Deutsche Messe AG',
    'organizer_type': 'Exhibition Company',
    'website_url': 'https://www.hannovermesse.de',
    'expected_attendance': None,  # NOT FOUND in verified sources
    'exhibitor_count': 4000,  # Source: Automation.com, Promwad
    'event_scope': 'International',
    'dual_use_indicator': True,  # Industrial automation has dual-use applications
    'verification_sources': 'Automation.com 2023-03; Promwad 2023; ExamineChina',
    'notes': '800 Chinese companies (20% of exhibitors, per Deutsche Messe chairman). AI in manufacturing focus. Hall 17 = robotics hotspot.'
}

# Exhibitors (VERIFIED ONLY - LIMITED Western media coverage for Chinese companies)
EXHIBITORS = [
    {
        'entity_name': 'Huawei',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'entity_list_status': 'US Entity List (2019)',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Industrial automation, enterprise solutions',
        'products_displayed': 'CSO Manufacturing participated in Industrial Transformation Stage (specific products not detailed in Western sources)',
        'verification_source': 'Deutsche Messe event program (Industrial Transformation Stage)',
        'confidence_level': 'confirmed_presence',
        'notes': 'Huawei CSO Manufacturing from European Industry Development Department participated in Industrial Transformation Stage.'
    },
    {
        'entity_name': 'Aubo Robotics',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Collaborative robots, therapy robots',
        'products_displayed': 'Collaborative robot with therapy demonstration capabilities',
        'verification_source': 'ExamineChina (examinechina.com/hannover-messe-2023)',
        'confidence_level': 'confirmed',
        'notes': 'Beijing-based collaborative robotics company. Showcased therapy robot demonstrations.'
    },
    {
        'entity_name': 'JAKA Robotics',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Collaborative robots, industrial automation',
        'products_displayed': 'Robotics products (specific models not detailed in public sources)',
        'verification_source': 'JAKA Robotics official site (jaka.com/home/)',
        'confidence_level': 'confirmed_presence',
        'notes': 'Chinese collaborative robot manufacturer. Specific products not detailed in accessible Western sources.'
    },
]

# Intelligence Summary
INTELLIGENCE_SUMMARY = """
Hannover Messe 2023 - Chinese Participation Analysis
=====================================================

VERIFIED CHINESE PRESENCE:
- 800 Chinese companies (20% of 4,000 total exhibitors)
- Quote from Deutsche Messe AG chairman: "Chinese companies are competitive in the global markets and are always ready to learn and improve"
- 3 companies documented with Western source verification
- Chinese visitors returned in force post-COVID

DATA LIMITATIONS - CRITICAL NOTE:
- Western media coverage of specific Chinese exhibitors was LIMITED
- Only 3 companies verified from accessible Western sources
- Complete list of 800 Chinese exhibitors not publicly available
- Product specifications mostly not detailed in Western press coverage
- This represents <1% documentation rate (3 of 800 companies)

MAJOR THEMES AT HANNOVER MESSE 2023:
- AI in manufacturing (main focus)
- Carbon-neutral production
- Industry 4.0
- Hydrogen and fuel cells
- Robotics (Hall 17 = robotics hotspot)

VERIFIED CHINESE EXHIBITORS:

1. Huawei - Industrial automation, enterprise solutions
   - Entity List company present at European industrial show
   - CSO Manufacturing participated in Industrial Transformation Stage

2. Aubo Robotics - Collaborative robots with therapy applications
   - Beijing-based company
   - Showcased therapy robot demonstrations

3. JAKA Robotics - Collaborative robots
   - Chinese robot manufacturer
   - Specific products not detailed in Western sources

KEY OBSERVATIONS:
1. 800 Chinese companies = 20% of total (significant industrial automation presence)
2. Entity List company (Huawei) present at European industrial trade show
3. Chinese robotics companies (Aubo, JAKA) in collaborative robot sector
4. Post-COVID: Chinese visitors and exhibitors returned in force
5. Limited Western media coverage of Chinese exhibitors (documentation challenge)

STRATEGIC SIGNIFICANCE:
- Chinese industrial automation sector well-represented in Europe
- Collaborative robotics focus (Aubo, JAKA) aligns with Industry 4.0 trends
- Huawei maintaining European industrial market presence despite US Entity List
- 20% Chinese participation shows deep integration in global industrial supply chains

ENTITY LIST PARADOX CONTINUES:
- Huawei: ABSENT from CES 2023 (US show)
- Huawei: PRESENT at Hannover Messe 2023 (EU industrial show)
- Huawei: DOMINANT at MWC 2023 (EU mobile show)
- Finding: US Entity List enforced at US shows, NOT at European events

DOCUMENTATION CHALLENGES:
- Hannover Messe 2023 had limited English-language Western media coverage
- Most Chinese exhibitor details only available in Chinese-language sources
- Western robotics/automation press focused on European/US companies
- Future improvement: May need archived versions of Chinese sources (with caution)

DEDUPLICATION NOTE:
- Exhibitor counts represent PARTICIPATIONS, not unique companies
- Huawei appears at multiple conferences (MWC, Hannover Messe)
- Aggregate statistics (800) represent participation slots at THIS conference
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
    print(f"     Exhibitors: {EVENT_DATA['exhibitor_count']:,}")
    print(f"     Chinese Exhibitors: 800 (20% - per Deutsche Messe chairman)")
    print(f"     WARNING: Limited Western media coverage of Chinese exhibitors")
    return EVENT_DATA['event_id']


def insert_exhibitors(conn, cursor, event_id):
    """Insert exhibitors with verification metadata"""
    print(f"\n[OK] Inserting {len(EXHIBITORS)} verified exhibitors...")
    print(f"     Note: Only {len(EXHIBITORS)} of 800 Chinese companies verified from Western sources")

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

        print(f"  {chinese_flag} {exhibitor['entity_name']:30} | {booth_info:25} | {conf_level} {entity_list}")

    verified_booths = sum(1 for e in EXHIBITORS if e.get('booth_number'))
    entity_list_companies = sum(1 for e in EXHIBITORS if e.get('entity_list_status'))
    documentation_rate = (len(EXHIBITORS) / 800) * 100
    print(f"\n  Exhibitors with verified booth numbers: {verified_booths}/{len(EXHIBITORS)}")
    print(f"  Entity List companies present: {entity_list_companies}/{len(EXHIBITORS)} (Huawei)")
    print(f"  Documentation rate: {documentation_rate:.1f}% ({len(EXHIBITORS)} of 800 Chinese companies)")


def load_data():
    """Load Hannover Messe 2023 verified data to database."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("="*70)
    print("LOADING HANNOVER MESSE 2023 VERIFIED DATA")
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
    print(f"  Total Exhibitors: {EVENT_DATA['exhibitor_count']:,}")
    print(f"\n  Verified Chinese Exhibitors Loaded: {len(EXHIBITORS)} of 800 total")
    print(f"  - With booth numbers: {sum(1 for e in EXHIBITORS if e.get('booth_number'))}")
    print(f"  - Confirmed presence only: {sum(1 for e in EXHIBITORS if not e.get('booth_number'))}")
    print(f"\n  Data Quality Notes:")
    print(f"  - 800 Chinese companies per Deutsche Messe chairman")
    print(f"  - Only {len(EXHIBITORS)} documented from Western sources ({(len(EXHIBITORS)/800*100):.1f}%)")
    print(f"  - Limited English-language coverage of Chinese industrial exhibitors")
    print(f"  - Huawei (Entity List) present at EU industrial show")
    print("="*70)
    print("[OK] HANNOVER MESSE 2023 DATA LOAD COMPLETE")
    print("="*70)

if __name__ == '__main__':
    load_data()
