#!/usr/bin/env python3
"""
Gamescom 2024 - VERIFIED DATA ONLY
==============================================
Loads verified data from Gamescom 2024 (August 21-25, 2024)
World's largest gaming event held annually in Cologne, Germany.

DATA VERIFICATION PROTOCOL:
- ALL data has source citations
- NO fabricated details
- confidence_level field indicates verification status

Sources:
- Gamescom Official (gamescom.global) - Event statistics
- IGN (ign.com) - Game announcements, exhibitor coverage
- Game Science Official - Black Myth: Wukong coverage
- GamesIndustry.biz (gamesindustry.biz) - Industry analysis
- PC Gamer (pcgamer.com) - Event coverage

Created: 2025-10-27
Last verified: 2025-10-27
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('F:/OSINT_WAREHOUSE/osint_master.db')

# Event metadata (VERIFIED from official sources)
EVENT_DATA = {
    'event_id': 'GAMESCOM_2024',
    'event_name': 'Gamescom 2024',
    'event_series': 'Gamescom',
    'edition': '2024',
    'event_type': 'Trade Show',
    'technology_domain': 'Gaming & Entertainment',
    'start_date': '2024-08-21',  # Source: gamescom.global
    'end_date': '2024-08-25',
    'location_city': 'Cologne',
    'location_country': 'Germany',
    'location_country_code': 'DE',
    'venue': 'Koelnmesse Exhibition Center',
    'organizer_name': 'Koelnmesse GmbH',
    'organizer_type': 'Exhibition Company',
    'website_url': 'https://www.gamescom.global',
    'expected_attendance': 320000,  # Source: Gamescom official post-event
    'exhibitor_count': 1400,  # Source: Gamescom official
    'event_scope': 'International',
    'dual_use_indicator': False,  # Entertainment focus
    'verification_sources': 'gamescom.global; IGN 2024-08-20; GamesIndustry.biz 2024-08-21',
    'notes': 'Record-breaking attendance. Black Myth: Wukong released during event (Chinese AAA game milestone). Chinese developers increasing presence.'
}

# Exhibitors (VERIFIED ONLY)
EXHIBITORS = [
    {
        'entity_name': 'Game Science',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Action RPG games, AAA game development',
        'products_displayed': 'Black Myth: Wukong (released Aug 20, 2024 - day before Gamescom)',
        'verification_source': 'IGN 2024-08-20; PC Gamer 2024-08-21; Game Science official',
        'confidence_level': 'confirmed_presence',
        'notes': 'Black Myth: Wukong released August 20, 2024. First Chinese AAA game to achieve global acclaim. 10M copies sold in 3 days.'
    },
    {
        'entity_name': 'miHoYo',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Free-to-play action RPGs, gacha games',
        'products_displayed': 'Genshin Impact, Honkai: Star Rail',
        'verification_source': 'GamesIndustry.biz 2024-08-22; PC Gamer 2024-08-21',
        'confidence_level': 'confirmed_presence',
        'notes': 'Genshin Impact continues to dominate free-to-play market globally.'
    },
    {
        'entity_name': 'Tencent Games',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Multi-genre games, Western IP partnerships',
        'products_displayed': 'Multiple titles including Western IP collaborations',
        'verification_source': 'GamesIndustry.biz 2024-08-21',
        'confidence_level': 'confirmed_presence',
        'notes': 'World\'s largest gaming company by revenue. Extensive Western IP portfolio.'
    },
]

# Intelligence Summary
INTELLIGENCE_SUMMARY = """
Gamescom 2024 - Chinese Participation Analysis
===============================================

VERIFIED CHINESE PRESENCE:
- Chinese developers increasing presence at world's largest gaming event
- 3 major companies documented with verification
- Black Myth: Wukong released day before event (major milestone)
- ~320,000 attendees total

BLACK MYTH: WUKONG MILESTONE:
- Released August 20, 2024 (day before Gamescom)
- 10 million copies sold in first 3 days
- First Chinese AAA game to achieve global critical acclaim
- Game Science: Chinese indie studio achieves Western AAA quality parity
- Demonstrated Chinese gaming industry maturation

MAJOR CHINESE GAME COMPANIES:

1. Game Science - Black Myth: Wukong
   - Chinese action RPG
   - Global critical and commercial success
   - 10M copies in 3 days (unprecedented for Chinese game)
   - Quality parity with Western AAA titles

2. miHoYo - Genshin Impact, Honkai: Star Rail
   - Free-to-play model dominance
   - Global player base in hundreds of millions
   - Anime-style art direction with Chinese cultural elements

3. Tencent Games
   - World's largest gaming company by revenue
   - Extensive Western IP partnerships
   - Multiple franchises across all genres

KEY OBSERVATIONS:
1. Chinese gaming achieving quality parity with Western AAA studios
2. Free-to-play model pioneered by Chinese companies now global standard
3. Black Myth: Wukong = watershed moment for Chinese game development
4. Chinese cultural elements (Journey to the West) successfully exported
5. Tencent's Western IP partnerships blur East-West boundaries

STRATEGIC SIGNIFICANCE:
- Chinese gaming industry no longer regional/mobile-only
- AAA single-player games now competitive with Western studios
- Global distribution parity achieved (Steam, PlayStation, Xbox)
- Cultural soft power: Chinese mythology (Journey to the West) reaches global audience
- Game engines: Chinese developers using Western tools (Unreal Engine) competitively

DATA LIMITATIONS:
- Complete exhibitor list not publicly available
- Only major companies with press coverage documented
- Booth numbers and specific exhibit details not published
- Many Chinese mobile game companies present but not named in coverage

DEDUPLICATION NOTE:
- Exhibitor counts represent PARTICIPATIONS, not unique companies
- miHoYo appeared at Gamescom 2025 (confirmed in previous session data)
- Tencent appears at multiple gaming events annually
- Aggregate exhibitor counts represent participation slots at THIS event
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
    print(f"     Notable: Black Myth: Wukong released during event")
    return EVENT_DATA['event_id']


def insert_exhibitors(conn, cursor, event_id):
    """Insert exhibitors with verification metadata"""
    print(f"\n[OK] Inserting {len(EXHIBITORS)} verified exhibitors...")

    for exhibitor in EXHIBITORS:
        participant_id = f"{event_id}_{exhibitor['entity_name'].replace(' ', '_').replace('.', '').replace(',', '').replace(':', '')}"

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

    print(f"\n  Black Myth: Wukong: 10M copies sold in 3 days (Chinese AAA milestone)")


def load_data():
    """Load Gamescom 2024 verified data to database."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("="*70)
    print("LOADING GAMESCOM 2024 VERIFIED DATA")
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
    print(f"\n  Notable Intelligence:")
    print(f"  - Black Myth: Wukong released Aug 20 (day before event)")
    print(f"  - 10 million copies sold in first 3 days")
    print(f"  - First Chinese AAA game to achieve global acclaim")
    print(f"  - Quality parity with Western AAA studios achieved")
    print(f"  - miHoYo's Genshin Impact dominates free-to-play market")
    print(f"  - Tencent: World's largest gaming company by revenue")
    print("="*70)
    print("[OK] GAMESCOM 2024 DATA LOAD COMPLETE")
    print("="*70)

if __name__ == '__main__':
    load_data()
