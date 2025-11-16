#!/usr/bin/env python3
"""
Germany Federal Institutions - Tier 1 Expansion
ZERO FABRICATION COMPLIANCE

Adds additional German federal institutions:
- Additional ministries (Finance, Justice, Development, Transport)
- Competition/regulatory agencies
- Research organizations

All from official government websites with verified URLs.
"""

import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    """Generate unique ID"""
    hash_part = hashlib.md5(text.encode()).hexdigest()[:12]
    return f"{prefix}_{hash_part}"

def expand_germany_federal():
    """Expand German federal institutions - Tier 1 VERIFIED ONLY"""

    print("=" * 70)
    print("GERMANY FEDERAL INSTITUTIONS - TIER 1 EXPANSION")
    print("ZERO FABRICATION PROTOCOL COMPLIANCE")
    print("=" * 70)
    print()
    print("Collection Date: 2025-10-26")
    print("Collection Method: Manual verification of official government websites")
    print("Data Collected: ONLY verifiable facts (names, URLs, types)")
    print()

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Additional German federal institutions
    # All URLs verified 2025-10-26

    institutions = [
        {
            'name': 'Federal Ministry of Finance',
            'name_native': 'Bundesministerium der Finanzen',
            'type': 'ministry',
            'website': 'https://www.bundesfinanzministerium.de',
            'source_verified_date': '2025-10-26',
            'website_accessible': True,
            'rationale': 'Financial regulation, sanctions policy, international finance'
        },
        {
            'name': 'Federal Ministry of Justice',
            'name_native': 'Bundesministerium der Justiz',
            'type': 'ministry',
            'website': 'https://www.bmj.de',
            'source_verified_date': '2025-10-26',
            'website_accessible': True,
            'rationale': 'Legal framework, data protection, competition law'
        },
        {
            'name': 'Federal Ministry for Digital and Transport',
            'name_native': 'Bundesministerium für Digitales und Verkehr',
            'type': 'ministry',
            'website': 'https://bmdv.bund.de',
            'source_verified_date': '2025-10-26',
            'website_accessible': True,
            'rationale': 'Digital infrastructure, telecommunications, transport policy'
        },
        {
            'name': 'Federal Ministry for Economic Cooperation and Development',
            'name_native': 'Bundesministerium für wirtschaftliche Zusammenarbeit und Entwicklung',
            'type': 'ministry',
            'website': 'https://www.bmz.de',
            'source_verified_date': '2025-10-26',
            'website_accessible': True,
            'rationale': 'Development cooperation, international partnerships'
        },
        {
            'name': 'Federal Cartel Office',
            'name_native': 'Bundeskartellamt',
            'type': 'agency',
            'website': 'https://www.bundeskartellamt.de',
            'source_verified_date': '2025-10-26',
            'website_accessible': True,
            'rationale': 'Competition policy, merger control, market regulation'
        },
        {
            'name': 'Federal Office for Economic Affairs and Export Control',
            'name_native': 'Bundesamt für Wirtschaft und Ausfuhrkontrolle',
            'type': 'agency',
            'website': 'https://www.bafa.de',
            'source_verified_date': '2025-10-26',
            'website_accessible': True,
            'rationale': 'Export controls, dual-use goods, trade licensing'
        },
        {
            'name': 'German Federal Foreign Trade and Investment Agency',
            'name_native': 'Germany Trade and Invest',
            'type': 'agency',
            'website': 'https://www.gtai.de',
            'source_verified_date': '2025-10-26',
            'website_accessible': True,
            'rationale': 'Foreign trade promotion, investment attraction'
        },
        {
            'name': 'Federal Agency for Disruptive Innovation',
            'name_native': 'Bundesagentur für Sprunginnovationen',
            'type': 'agency',
            'website': 'https://www.sprind.org',
            'source_verified_date': '2025-10-26',
            'website_accessible': True,
            'rationale': 'Innovation funding, technology development, R&D'
        }
    ]

    print("Phase 1: Adding verified institutions...")
    print()

    added_count = 0
    for inst in institutions:
        inst_id = generate_id('de_verified', inst['name'])

        # Check if already exists
        cursor.execute('''
            SELECT institution_id FROM european_institutions
            WHERE institution_id = ?
        ''', (inst_id,))

        if cursor.fetchone():
            print(f"  SKIP: {inst['name']} (already in database)")
            continue

        # Prepare notes documenting what we DON'T have
        not_collected = {
            'china_relevance': '[NOT COLLECTED: Requires analytical framework]',
            'us_relevance': '[NOT COLLECTED: Requires analytical framework]',
            'tech_relevance': '[NOT COLLECTED: Requires analytical framework]',
            'policy_domains': '[NOT COLLECTED: Requires systematic cataloging]',
            'key_personnel': '[NOT COLLECTED: Requires biography parsing]',
            'recent_publications': '[NOT COLLECTED: Requires press release scraper]'
        }

        notes_json = json.dumps({
            'collection_tier': 'tier_1_verified_only',
            'collection_date': inst['source_verified_date'],
            'collection_method': 'manual_url_verification',
            'website_accessible': inst['website_accessible'],
            'collection_rationale': inst['rationale'],
            'not_collected': not_collected
        }, indent=2)

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, official_website,
             china_relevance, us_relevance, tech_relevance,
             status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            inst_id,
            inst['name'],
            inst['name_native'],
            inst['type'],
            'national',
            'DE',
            inst['website'],
            None,  # NULL - not fabricated
            None,  # NULL - not fabricated
            None,  # NULL - not fabricated
            'active',
            notes_json,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

        added_count += 1
        print(f"  + {inst['name']}")
        print(f"    URL: {inst['website']}")
        print(f"    Rationale: {inst['rationale']}")
        print()

    conn.commit()

    # Summary
    print("=" * 70)
    print("EXPANSION COMPLETE")
    print("=" * 70)
    print()
    print(f"Institutions Added: {added_count}")
    print()

    # Show total coverage
    cursor.execute('''
        SELECT COUNT(*) FROM european_institutions
        WHERE country_code = 'DE' AND jurisdiction_level = 'national'
    ''')
    total_federal = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(*) FROM european_institutions
        WHERE country_code = 'DE' AND jurisdiction_level = 'subnational_state'
    ''')
    total_state = cursor.fetchone()[0]

    print(f"Germany Total Coverage:")
    print(f"  Federal Institutions: {total_federal}")
    print(f"  State Institutions: {total_state}")
    print(f"  Total: {total_federal + total_state}")
    print()

    # Validation
    print("=" * 70)
    print("VALIDATION")
    print("=" * 70)
    print()

    cursor.execute('''
        SELECT COUNT(*) FROM european_institutions
        WHERE country_code = 'DE'
          AND (china_relevance IS NOT NULL
               OR us_relevance IS NOT NULL
               OR tech_relevance IS NOT NULL)
    ''')
    fabricated = cursor.fetchone()[0]

    if fabricated == 0:
        print("+ NO FABRICATED DATA")
        print("+ All analytical fields properly NULL")
    else:
        print(f"WARNING: {fabricated} institutions have fabricated scores")

    print()
    conn.close()

    print("=" * 70)
    print("SESSION COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    expand_germany_federal()
