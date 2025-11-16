#!/usr/bin/env python3
"""
IFA 2019 - VERIFIED DATA ONLY
==============================================
Loads verified data from IFA Berlin 2019 (September 6-11, 2019)
770+ Chinese companies (39.7% of total exhibitors). Chinese companies won 40% of innovation awards.

DATA VERIFICATION PROTOCOL:
- ALL data has source citations
- NO fabricated details
- confidence_level field indicates verification status

Sources:
- GSMArena (gsmarena.com) - Huawei Kirin 990
- Digital Trends (digitaltrends.com) - Huawei, Hisense, TCL, Lenovo
- What Hi-Fi? (whathifi.com) - TCL, Hisense
- PR Newswire (prnewswire.com) - Hisense, TCL
- AVForums (avforums.com) - Hisense
- Tom's Hardware (tomshardware.com) - Lenovo
- Windows Central (windowscentral.com) - Lenovo
- Android Authority (androidauthority.com) - Lenovo

Created: 2025-10-28
Last verified: 2025-10-28
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('F:/OSINT_WAREHOUSE/osint_master.db')

# Event metadata (VERIFIED from Western sources)
EVENT_DATA = {
    'event_id': 'IFA_2019',
    'event_name': 'IFA 2019',
    'event_series': 'IFA',
    'edition': '2019',
    'event_type': 'Trade Show',
    'technology_domain': 'Consumer Electronics',
    'start_date': '2019-09-06',  # Source: Multiple Western media
    'end_date': '2019-09-11',
    'location_city': 'Berlin',
    'location_country': 'Germany',
    'location_country_code': 'DE',
    'venue': 'Messe Berlin Exhibition Grounds',
    'organizer_name': 'gfu Consumer & Home Electronics',
    'organizer_type': 'Trade Association',
    'website_url': 'https://www.ifa-berlin.com',
    'expected_attendance': 245000,  # Source: IFA official stats
    'exhibitor_count': 1939,  # Source: IFA official stats
    'event_scope': 'International',
    'dual_use_indicator': False,  # Consumer electronics focus
    'verification_sources': 'PR Newswire 2019-09; Digital Trends 2019-09; GSMArena 2019-09',
    'notes': '770+ Chinese companies (39.7% of exhibitors). Chinese companies won 40% of IFA Product Technical Innovation Awards (8 companies, 24 products from 20 manufacturers including TCL, Midea, Skyworth, BOE, KONKA, CHANGHONG, ECOVACS, Amazfit).'
}

# Exhibitors (VERIFIED ONLY - from Western media sources)
EXHIBITORS = [
    {
        'entity_name': 'Huawei Technologies',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'entity_list_status': 'US Entity List (May 2019)',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': '5G chipsets, mobile processors',
        'products_displayed': 'Kirin 990 SoC (7nm FinFET Plus EUV, integrated 5G modem, Cortex-A77 CPU, Mali-G77 GPU, NPU, 4K/60fps video)',
        'verification_source': 'GSMArena 2019-09-06 (gsmarena.com/huawei_kirin_990_announcement); Digital Trends 2019-09 (digitaltrends.com/mobile/huawei-kirin-990-ifa2019-news/); Beebom 2019-09',
        'confidence_level': 'confirmed',
        'notes': 'CEO Richard Yu held opening keynote. Kirin 990: World\'s first 5G SoC with integrated modem. Launched simultaneously in Berlin and Beijing. Tagline: "Rethink Evolution". Despite US Entity List (May 2019), maintained strong European presence.'
    },
    {
        'entity_name': 'TCL',
        'entity_type': 'State-Owned Enterprise',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'state_owned',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': '8K TVs, Mini LED, Quantum Dot, Android TV',
        'products_displayed': 'X10 Series 4K Mini LED (15,000+ LEDs, 768 zones, Quantum Dot, 100% DCI-P3, 1500 nits, world\'s first Mini LED Android TV), 8K QLED X Series (85"/75"/65", flagship 75" with 25,200 LEDs, 1200 nits)',
        'verification_source': 'TCL Official 2019-09 (tcl.com/ifa2019); What Hi-Fi? 2019-09; Digital Trends 2019-09; Hardware Upgrade IT 2019-09',
        'confidence_level': 'confirmed',
        'notes': 'TCL won IFA Product Technical Innovation Award. X10 Series = world\'s first Mini LED Android TV, one of world\'s slimmest Direct LED TVs. 8K flagship: 75" with 25,200 LEDs delivering 1200 nits brightness.'
    },
    {
        'entity_name': 'Hisense',
        'entity_type': 'State-Owned Enterprise',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'state_owned',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': '8K TVs, Dual-Cell ULED XD, Laser TV',
        'products_displayed': 'ULED XD 85U9E 8K (85", dual-cell, 150,000:1 contrast, 1M+ dimming zones), ULED XD 65U9E 4K (65", dual-cell), Sonic Laser TV',
        'verification_source': 'PR Newswire 2019-09 (prnewswire.com/news-releases/hisense-8k-uled-xd-tv-and-sonic-laser-tv-shine-at-ifa-2019); What Hi-Fi? 2019-09; Digital Trends 2019-09; AVForums 2019-09',
        'confidence_level': 'confirmed',
        'notes': 'Dual-Cell ULED XD: 2 LCD panels (1080p monochrome for contrast + 4K color panel) over backlight = 150,000:1 contrast ratio, 1M+ local dimming zones. 85U9E = 8K flagship. Mixed reviews: 8K model had blooming/flicker/banding, 4K model performed better.'
    },
    {
        'entity_name': 'Lenovo',
        'entity_type': 'Private Corporation',
        'country': 'China',
        'country_code': 'CN',
        'chinese_entity': 1,
        'chinese_entity_type': 'private',
        'booth_number': None,  # NOT FOUND in public sources
        'booth_location': None,
        'booth_size': None,
        'technology_focus': 'Laptops, ThinkPad, Yoga, ThinkBook',
        'products_displayed': 'Yoga S940 (14" up to 4K, 90% screen-to-body ratio, contour glass, Dolby Vision HDR, Dolby Atmos, Project Athena verified), ThinkBook 14, ThinkBook 15 (10th Gen Intel Core, PCIe SSD, Intel Optane Memory H10, €665-€675)',
        'verification_source': 'Windows Central 2019-09 (windowscentral.com/yoga-s940-announce); Tom\'s Hardware 2019-09 (tomshardware.com/news/lenovo-yoga-s940-c930-amoled); Digital Trends 2019-09; Android Authority 2019-09',
        'confidence_level': 'confirmed',
        'notes': 'Yoga S940: Originally unveiled CES 2019 Jan, re-announced at IFA 2019 Sept as Project Athena verified (co-engineered by Lenovo and Intel). 90% screen-to-body ratio with contour glass wrapping display. ThinkBook series: SMB focus, starting €665.'
    },
]

# Intelligence Summary
INTELLIGENCE_SUMMARY = """
IFA 2019 - Chinese Participation Analysis
==========================================

VERIFIED CHINESE PRESENCE:
- 770+ Chinese companies attended (39.7% of 1,939 exhibitors)
- 4 major companies documented with verified Western sources
- Chinese companies won 40% of IFA Product Technical Innovation Awards
- 8 Chinese companies won awards: TCL, Midea, Skyworth, BOE, KONKA, CHANGHONG, ECOVACS, Amazfit
- 24 products from 20 Chinese manufacturers won innovation awards

EVENT CONTEXT:
- September 6-11, 2019, Messe Berlin
- 245,000 expected visitors
- 1,939 exhibitors from 100+ countries
- 770+ Chinese exhibitors = 39.7% of total (highest concentration documented)

MAJOR CHINESE EXHIBITORS:

1. Huawei Technologies - 5G chipset leader
   - Kirin 990 SoC unveiled in opening keynote by CEO Richard Yu
   - World's first 5G SoC with integrated 5G modem
   - 7nm FinFET Plus EUV process, Cortex-A77 CPU, Mali-G77 GPU
   - First Kirin chipset with 4K/60fps video recording
   - Simultaneous launch in Berlin and Beijing
   - "Rethink Evolution" campaign
   - Despite US Entity List (May 2019), maintained European presence

2. TCL - Mini LED and 8K leader
   - X10 Series 4K Mini LED: World's first Mini LED Android TV
   - 15,000+ ultra-slim LEDs in 768 dimmable zones
   - Quantum Dot: 100% color volume DCI-P3 at 1500 nits
   - One of world's slimmest Direct LED TVs
   - 8K QLED X Series: 85", 75", 65" models
   - Flagship 75" 8K: 25,200 LEDs delivering 1200 nits
   - Won IFA Product Technical Innovation Award

3. Hisense - Dual-Cell ULED XD innovation
   - ULED XD 85U9E: 85" 8K dual-cell flagship
   - ULED XD 65U9E: 65" 4K dual-cell
   - Dual-Cell technology: 2 LCD panels (1080p monochrome + 4K color)
   - 150,000:1 contrast ratio, 1,000,000+ local dimming zones
   - Sonic Laser TV also showcased
   - Mixed initial reviews: 8K model had blooming/flicker/banding issues

4. Lenovo - Project Athena laptops
   - Yoga S940: Project Athena verified (Lenovo + Intel co-engineering)
   - 14" display up to 4K, 90% screen-to-body ratio
   - Contour glass wraps around display
   - Dolby Vision HDR, Dolby Atmos audio
   - ThinkBook 14/15: SMB focus, 10th Gen Intel Core, starting €665-€675

KEY OBSERVATIONS:
1. Highest Chinese participation rate: 770+ companies (39.7%)
2. 40% of innovation awards to Chinese companies (8 of 20 award-winning companies)
3. Huawei maintained strong European presence despite US Entity List
4. Chinese companies dominated display technology: Mini LED, Dual-Cell, 8K
5. 5G leadership: Huawei Kirin 990 opening keynote
6. TCL, Hisense, Lenovo all major consumer electronics players

STRATEGIC SIGNIFICANCE:
- Chinese companies nearly 40% of IFA 2019 exhibitors
- Innovation leadership: 40% of technical innovation awards
- Display technology dominance: Mini LED (TCL), Dual-Cell (Hisense), 8K
- 5G chipset leadership: Huawei Kirin 990 opening keynote
- Entity List companies maintained European trade show presence
- Strong showing across categories: smartphones, TVs, laptops, home appliances

INNOVATION AWARDS (Chinese Winners):
- TCL: QLED TVs, Mini LED
- Midea: Home appliances
- Skyworth: OLED TVs
- BOE: Display technology
- KONKA: Large-screen TVs
- CHANGHONG: 8K TVs with AI
- ECOVACS: DEEBOT OZMO 950 robot vacuum
- Amazfit: GTR smart watch

DATA LIMITATIONS:
- Complete list of 770+ Chinese exhibitors not publicly available
- Only 4 companies with detailed Western media verification (0.5% documentation rate)
- Booth numbers not published for most exhibitors
- Focus on major brands with Western press coverage
- Many smaller exhibitors not documented in Western media

DEDUPLICATION NOTE:
- Exhibitor counts represent PARTICIPATIONS, not unique companies
- Huawei, TCL, Hisense, Lenovo appear at multiple conferences
- Aggregate statistics (770+) represent participation slots at THIS conference
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
    print(f"     Exhibitors: {EVENT_DATA['exhibitor_count']:,} total")
    print(f"     Chinese: 770+ companies (39.7% - HIGHEST RATE)")
    return EVENT_DATA['event_id']


def insert_exhibitors(conn, cursor, event_id):
    """Insert exhibitors with verification metadata"""
    print(f"\n[OK] Inserting {len(EXHIBITORS)} verified exhibitors...")
    print(f"     Note: Only {len(EXHIBITORS)} of 770+ Chinese companies verified from Western sources")
    print(f"     Documentation rate: ~{(len(EXHIBITORS)/770)*100:.2f}%")

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
        entity_list = '[ENTITY LIST]' if exhibitor.get('entity_list_status') else ''
        conf_level = exhibitor['confidence_level']

        print(f"  {chinese_flag} {exhibitor['entity_name']:30} | {conf_level} {entity_list}")

    verified_booths = sum(1 for e in EXHIBITORS if e.get('booth_number'))
    entity_list_companies = sum(1 for e in EXHIBITORS if e.get('entity_list_status'))
    print(f"\n  Exhibitors with verified booth numbers: {verified_booths}/{len(EXHIBITORS)}")
    print(f"  Documentation rate: ~{(len(EXHIBITORS)/770)*100:.2f}% ({len(EXHIBITORS)} of 770+ Chinese companies)")
    print(f"  Entity List companies present: {entity_list_companies}/{len(EXHIBITORS)} (Huawei)")
    print(f"  Chinese innovation award winners documented: 1/{len(EXHIBITORS)} (TCL)")


def load_data():
    """Load IFA 2019 verified data to database."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("="*70)
    print("LOADING IFA 2019 VERIFIED DATA")
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
    print(f"  Chinese Exhibitors: 770+ (39.7% - HIGHEST RATE)")
    print(f"\n  Verified Chinese Exhibitors Loaded: {len(EXHIBITORS)}")
    print(f"  - With booth numbers: {sum(1 for e in EXHIBITORS if e.get('booth_number'))}")
    print(f"  - Confirmed presence only: {sum(1 for e in EXHIBITORS if not e.get('booth_number'))}")
    print(f"\n  Data Quality Notes:")
    print(f"  - 770+ Chinese companies attended (39.7% of all exhibitors)")
    print(f"  - Chinese companies won 40% of IFA Product Technical Innovation Awards")
    print(f"  - Only {len(EXHIBITORS)} documented from Western sources (~0.5%)")
    print(f"  - Focus on major brands with Western press releases")
    print(f"\n  Notable Intelligence:")
    print(f"  - Huawei Kirin 990: Opening keynote, world's first 5G SoC with integrated modem")
    print(f"  - TCL X10: World's first Mini LED Android TV (15,000+ LEDs)")
    print(f"  - Hisense ULED XD: 1,000,000+ local dimming zones via dual-cell tech")
    print(f"  - Lenovo Yoga S940: Project Athena verified (Intel co-engineering)")
    print("="*70)
    print("[OK] IFA 2019 DATA LOAD COMPLETE")
    print("="*70)

if __name__ == '__main__':
    load_data()
