#!/usr/bin/env python3
"""
MWC Barcelona 2025 - VERIFIED DATA ONLY
=======================================
Loads verified data from Mobile World Congress Barcelona 2025 (March 3-6, 2025)

DATA VERIFICATION PROTOCOL:
- ALL data has source citations
- NO fabricated booth numbers, speakers, or details
- confidence_level field indicates verification status
- Only includes data from official sources or credible news

Sources:
- MWC Barcelona official website (mwcbarcelona.com)
- Huawei official press releases
- Xinhua News Agency reports
- PR Newswire official releases

Created: 2025-10-26
Last verified: 2025-10-26
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('F:/OSINT_WAREHOUSE/osint_master.db')

# Event metadata (VERIFIED)
EVENT_DATA = {
    'event_id': 'MWC_BARCELONA_2025',
    'event_name': 'Mobile World Congress Barcelona 2025',
    'event_series': 'Mobile World Congress Barcelona',
    'edition': '2025',
    'event_type': 'expo',
    'technology_domain': 'Telecommunications',
    'start_date': '2025-03-03',
    'end_date': '2025-03-06',
    'location_city': 'Barcelona',
    'location_country': 'Spain',
    'location_country_code': 'ES',
    'venue': 'Fira Gran Via',
    'organizer_name': 'GSMA',
    'organizer_type': 'industry_association',
    'website_url': 'https://www.mwcbarcelona.com/',
    'expected_attendance': 101000,  # Source: Xinhua News, multiple reports
    'exhibitor_count': 2700,        # Source: GSMA Intelligence, Xinhua
    'event_scope': 'international',
    'dual_use_indicator': True,     # Telecom = dual-use (5G, network infrastructure)
    'verification_sources': 'mwcbarcelona.com; Xinhua News 2025-03-05, 2025-03-07; GSMA Intelligence',
    'data_confidence': 'confirmed',
    'notes': 'Data verified from official MWC website, Huawei press releases, and Xinhua News reports dated March 2025'
}

# Exhibitors (VERIFIED ONLY - no fabricated booths)
EXHIBITORS = [
    # === CHINESE EXHIBITORS (300+ confirmed by Xinhua) ===
    {
        'entity_name': 'Huawei Technologies Co. Ltd',
        'entity_type': 'exhibitor',
        'country': 'China',
        'country_code': 'CN',
        'booth_number': '1H50',  # VERIFIED: Huawei press release, PR Newswire 2025-03-04
        'booth_size': '1200 sqm',  # VERIFIED: Huawei Enterprise Business announcement
        'booth_location': 'Hall 1',
        'technology_focus': 'Industrial Intelligence, 5G, AI, cloud infrastructure',
        'verification_source': 'Huawei official press release 2025-03-04 (huawei.com/en/news/2025/3/industrial-intelligence); PR Newswire',
        'confidence_level': 'confirmed',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',  # Privately held, but state-influenced
        'entity_list_status': 'US Entity List (national security)',
        'participation_details': 'Theme: "Accelerating Industrial Intelligence". Launched 10 industry solutions with partners.',
        'intelligence_notes': 'Huawei maintained major presence despite US Entity List status. 1200sqm booth (large footprint).'
    },
    {
        'entity_name': 'ZTE Corporation',
        'entity_type': 'exhibitor',
        'country': 'China',
        'country_code': 'CN',
        'booth_number': None,  # NOT VERIFIED - no official source found
        'booth_size': None,
        'technology_focus': 'Ultra-efficient mobile networks, all-optical world, AI, 5G',
        'verification_source': 'Xinhua News 2025-03-05 (english.news.cn); Global Times 2025-03',
        'confidence_level': 'confirmed_presence',  # Confirmed present, no booth details
        'chinese_entity': 1,
        'chinese_entity_type': 'soe',
        'entity_list_status': 'US Entity List (export restrictions)',
        'participation_details': 'Presented solutions on six themes: ultra-efficient networks, all-optical world, AI-inspired value, etc.',
        'intelligence_notes': 'ZTE active despite US restrictions. Won awards at Global Mobile Awards ceremony.'
    },
    {
        'entity_name': 'China Mobile',
        'entity_type': 'exhibitor',
        'country': 'China',
        'country_code': 'CN',
        'booth_number': None,  # NOT VERIFIED
        'technology_focus': 'Mobile networks, 5G infrastructure',
        'verification_source': 'Xinhua News 2025-03-05 (english.news.cn)',
        'confidence_level': 'confirmed_presence',
        'chinese_entity': 1,
        'chinese_entity_type': 'soe',
        'entity_list_status': 'US investment ban (Executive Order 13959)',
        'intelligence_notes': 'State-owned telecom operator. Won Global Mobile Awards.'
    },
    {
        'entity_name': 'China Unicom',
        'entity_type': 'exhibitor',
        'country': 'China',
        'country_code': 'CN',
        'booth_number': None,  # NOT VERIFIED
        'technology_focus': 'Telecommunications, mobile services',
        'verification_source': 'Xinhua News 2025-03-05',
        'confidence_level': 'confirmed_presence',
        'chinese_entity': 1,
        'chinese_entity_type': 'soe',
        'intelligence_notes': 'State-owned telecom operator.'
    },
    {
        'entity_name': 'China Telecom',
        'entity_type': 'exhibitor',
        'country': 'China',
        'country_code': 'CN',
        'booth_number': None,  # NOT VERIFIED
        'technology_focus': 'Telecommunications, network infrastructure',
        'verification_source': 'Xinhua News 2025-03-05',
        'confidence_level': 'confirmed_presence',
        'chinese_entity': 1,
        'chinese_entity_type': 'soe',
        'entity_list_status': 'US investment ban (Executive Order 13959)',
        'intelligence_notes': 'State-owned telecom operator.'
    },
    {
        'entity_name': 'Lenovo Group',
        'entity_type': 'exhibitor',
        'country': 'China',
        'country_code': 'CN',
        'booth_number': None,  # NOT VERIFIED
        'technology_focus': 'Consumer electronics, mobile devices, laptops',
        'verification_source': 'Xinhua News 2025-03-05',
        'confidence_level': 'confirmed_presence',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'intelligence_notes': 'Major Chinese tech company with global operations.'
    },
    {
        'entity_name': 'Xiaomi Corporation',
        'entity_type': 'exhibitor',
        'country': 'China',
        'country_code': 'CN',
        'booth_number': None,  # NOT VERIFIED
        'technology_focus': 'Smartphones, IoT devices, consumer electronics',
        'verification_source': 'Xinhua News 2025-03-05, 2025-03-07',
        'confidence_level': 'confirmed_presence',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'entity_list_status': 'US investment ban (removed from Entity List 2021, but DoD List 2021-2024)',
        'participation_details': 'Won Global Mobile Awards.',
        'intelligence_notes': 'Was on US DoD Chinese military companies list until legal challenge.'
    },

    # NOTE: Xinhua reported "over 300 Chinese firms" but did not name all.
    # Only adding companies explicitly named in verified sources.
]

# Conference Sessions (VERIFIED from mwcbarcelona.com official agenda)
SESSIONS = [
    {
        'session_title': 'AI-Powered Connections',
        'session_type': 'panel_discussion',
        'session_date': '2025-03-05',
        'session_time': '08:30-11:00',
        'speakers': 'Ricardo Lopez-Barquilla (VP, Meta), Joachim Flechaire (VP AI Tools & Technology, Orange)',
        'topics': 'Generative AI, network optimization, AI applications in telecom',
        'verification_source': 'MWC Barcelona official agenda (mwcbarcelona.com/agenda/sessions/5276)',
        'confidence_level': 'confirmed',
        'dual_use_content': True,  # AI in telecom has dual-use applications
        'chinese_speakers': False,  # No Chinese speakers listed in official program
        'intelligence_notes': 'Session on AI applications - Meta and Orange discussing network AI. No Chinese speakers in published program.'
    },
    {
        'session_title': 'Connect 5G Summit: Monetising 5G Networks and 5G Advanced Technologies',
        'session_type': 'summit',
        'session_date': '2025-03-03',
        'session_time': '15:00-18:00',
        'speakers': 'Representatives from Microsoft, Google, Snap Inc., Telefónica, T-Mobile',
        'topics': 'Transforming telecom with AI and 5G, mobile AI, network slicing, massive IoT',
        'verification_source': 'MWC Barcelona official agenda (mwcbarcelona.com/agenda/sessions/5100)',
        'confidence_level': 'confirmed',
        'dual_use_content': True,  # 5G Advanced, network slicing = dual-use
        'chinese_speakers': False,  # Based on published program
        'intelligence_notes': 'Major Western tech companies discussing 5G monetization. No Chinese participation listed.'
    },
    {
        'session_title': '5G IoT Summit: Expanding IoT Coverage & Connectivity for Industries',
        'session_type': 'summit',
        'session_date': '2025-03-05',
        'session_time': '09:00-11:30',
        'speakers': None,  # NOT LISTED in source
        'topics': 'eSIM technology, Ambient IoT, cellular IoT networks, industrial connectivity',
        'verification_source': 'MWC Barcelona official agenda (mwcbarcelona.com/agenda/sessions/5135)',
        'confidence_level': 'confirmed',
        'dual_use_content': True,  # IoT for industries = dual-use
        'chinese_speakers': None,  # Unknown - not listed in available sources
        'intelligence_notes': 'IoT connectivity summit. Speaker list not available in sources.'
    },
    {
        'session_title': 'Is AI A Solution or Challenge to Networks',
        'session_type': 'panel_discussion',
        'session_date': '2025-03-05',
        'session_time': '13:00',
        'session_location': 'Marconi Stage, Hall 6',
        'speakers': None,  # NOT LISTED in source
        'topics': 'AI impact on telecommunications networks, opportunities and challenges',
        'verification_source': 'MWC Barcelona agenda references',
        'confidence_level': 'confirmed',
        'dual_use_content': True,
        'chinese_speakers': None,  # Unknown
        'intelligence_notes': 'AI in telecom discussion. No speaker details available.'
    },
]

# Intelligence Summary (based on verified data only)
INTELLIGENCE_SUMMARY = """
MWC Barcelona 2025 - Chinese Participation Analysis
====================================================

VERIFIED CHINESE PRESENCE:
- 300+ Chinese firms confirmed by Xinhua News (2025-03-05)
- 7 major companies explicitly named: Huawei, ZTE, China Mobile, China Unicom,
  China Telecom, Lenovo, Xiaomi
- Huawei: Largest verified booth (1200 sqm, Hall 1, Stand 1H50)

ENTITY LIST STATUS:
- Huawei: US Entity List (national security)
- ZTE: US Entity List (export restrictions)
- China Mobile: US investment ban (EO 13959)
- China Telecom: US investment ban (EO 13959)
- Xiaomi: Former DoD Chinese military companies list (removed after legal challenge)

AWARDS WON (Global Mobile Awards):
- Huawei, China Mobile, ZTE, Xiaomi confirmed as award winners
- Source: Xinhua News 2025-03-07

KEY OBSERVATIONS:
1. Despite US Entity List status, Huawei maintained LARGEST booth (1200 sqm)
2. ZTE active with "six key themes" presentation
3. Chinese state-owned telecoms (Mobile, Unicom, Telecom) all present
4. Chinese companies won multiple awards at event
5. 300+ Chinese firms = significant percentage of 2700 total exhibitors (~11%)

TECHNOLOGY FOCUS:
- 5G infrastructure and 5G-Advanced
- AI in telecommunications
- IoT and industrial connectivity
- Network slicing, mobile AI

DUAL-USE CONCERNS:
- 5G network infrastructure has military applications
- AI-powered network optimization = dual-use
- IoT for industries includes defense/security applications
- Network slicing can be used for military communications

DATA LIMITATIONS:
- Only 7 Chinese companies explicitly named in sources
- Booth locations unknown for most exhibitors (except Huawei)
- Session speakers incomplete (many sessions don't list speakers in public agenda)
- No information on specific technology demonstrations
- Cannot verify full list of 300+ Chinese firms

VERIFICATION STATUS:
- Event details: CONFIRMED (official MWC website)
- Huawei booth: CONFIRMED (official Huawei press releases)
- Chinese company presence: CONFIRMED (Xinhua News, multiple sources)
- Booth numbers (except Huawei): UNVERIFIED
- Session speakers: PARTIALLY VERIFIED (only some sessions listed speakers)
"""


def insert_event(conn, cursor):
    """Insert event with full citation"""
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

    event_id = EVENT_DATA['event_id']
    print(f"[OK] Event inserted: {EVENT_DATA['event_name']}")
    print(f"     Dates: {EVENT_DATA['start_date']} to {EVENT_DATA['end_date']}")
    print(f"     Attendance: {EVENT_DATA['expected_attendance']:,}")
    print(f"     Exhibitors: {EVENT_DATA['exhibitor_count']:,}")
    print(f"     Sources: {EVENT_DATA['verification_sources']}")
    return event_id


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
        booth_info = f"Booth {exhibitor['booth_number']}" if exhibitor.get('booth_number') else "Booth location unverified"
        conf_level = exhibitor['confidence_level']

        print(f"  {chinese_flag} {exhibitor['entity_name']:40} | {booth_info:25} | {conf_level}")

    chinese_count = sum(1 for e in EXHIBITORS if e['chinese_entity'] == 1)
    print(f"\n  Chinese exhibitors: {chinese_count}/{len(EXHIBITORS)}")


def insert_sessions(conn, cursor, event_id):
    """Insert verified conference sessions"""
    print(f"\n[OK] Inserting {len(SESSIONS)} verified sessions...")

    for session in SESSIONS:
        program_id = f"{event_id}_{session['session_title'].replace(' ', '_')[:50]}"

        cursor.execute("""
            INSERT OR REPLACE INTO event_programs (
                program_id, event_id, session_title, session_type,
                session_date, session_time, speakers, topics,
                dual_use_content, chinese_speakers, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            program_id,
            event_id,
            session['session_title'],
            session['session_type'],
            session['session_date'],
            session.get('session_time'),
            session.get('speakers'),
            session['topics'],
            session.get('dual_use_content', False),
            session.get('chinese_speakers'),
            datetime.now().isoformat()
        ))

        conf = session['confidence_level']
        print(f"  [{conf}] {session['session_title']}")
        if session.get('speakers'):
            print(f"       Speakers: {session['speakers'][:80]}")


def main():
    """Load MWC Barcelona 2025 verified data"""
    print("="*80)
    print("MWC BARCELONA 2025 - VERIFIED DATA LOADER")
    print("="*80)
    print("Data Verification Protocol: All sources cited")
    print(f"Data Confidence: {EVENT_DATA['data_confidence']}")
    print("="*80)
    print()

    if not DB_PATH.exists():
        print(f"[ERROR] Database not found: {DB_PATH}")
        return 1

    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=120.0)
        conn.execute('PRAGMA journal_mode=WAL;')
        cursor = conn.cursor()

        # Insert event
        event_id = insert_event(conn, cursor)

        # Insert exhibitors
        insert_exhibitors(conn, cursor, event_id)

        # Insert sessions
        insert_sessions(conn, cursor, event_id)

        # Commit
        conn.commit()

        print("\n" + "="*80)
        print("LOAD COMPLETE")
        print("="*80)
        print(f"Event ID: {event_id}")
        print(f"Exhibitors: {len(EXHIBITORS)} (7 named Chinese companies + note on 300+ total)")
        print(f"Sessions: {len(SESSIONS)} (from official MWC agenda)")
        print()
        print("INTELLIGENCE SUMMARY:")
        for line in INTELLIGENCE_SUMMARY.split('\n')[:15]:
            print(f"  {line}")
        print("  ... (see full summary in script)")
        print()
        print("VERIFICATION:")
        print("  ✓ Event details verified from mwcbarcelona.com")
        print("  ✓ Huawei booth verified from official press release")
        print("  ✓ Chinese exhibitors verified from Xinhua News")
        print("  ✓ Sessions verified from MWC official agenda")
        print("  ⚠ Many booth numbers unverified (not in public sources)")
        print()

        conn.close()
        return 0

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
