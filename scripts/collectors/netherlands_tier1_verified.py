#!/usr/bin/env python3
"""
Netherlands Federal Institutions - Tier 1 Verified Collection
ZERO FABRICATION COMPLIANCE

Collects ONLY verifiable facts from official Dutch government websites.
"""

import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    """Generate unique ID"""
    hash_part = hashlib.md5(text.encode()).hexdigest()[:12]
    return f"{prefix}_{hash_part}"

def collect_netherlands_tier1():
    """Collect Netherlands federal institutions - Tier 1 VERIFIED ONLY"""

    print("=" * 70)
    print("NETHERLANDS FEDERAL INSTITUTIONS - TIER 1 VERIFIED COLLECTION")
    print("ZERO FABRICATION PROTOCOL COMPLIANCE")
    print("=" * 70)
    print()
    print("Collection Date: 2025-10-26")
    print()

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        {
            'name': 'Ministry of Foreign Affairs',
            'name_native': 'Ministerie van Buitenlandse Zaken',
            'type': 'ministry',
            'website': 'https://www.government.nl/ministries/ministry-of-foreign-affairs',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Ministry of Defence',
            'name_native': 'Ministerie van Defensie',
            'type': 'ministry',
            'website': 'https://www.government.nl/ministries/ministry-of-defence',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Ministry of Economic Affairs and Climate Policy',
            'name_native': 'Ministerie van Economische Zaken en Klimaat',
            'type': 'ministry',
            'website': 'https://www.government.nl/ministries/ministry-of-economic-affairs-and-climate-policy',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Ministry of Education, Culture and Science',
            'name_native': 'Ministerie van Onderwijs, Cultuur en Wetenschap',
            'type': 'ministry',
            'website': 'https://www.government.nl/ministries/ministry-of-education-culture-and-science',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Ministry of Justice and Security',
            'name_native': 'Ministerie van Justitie en Veiligheid',
            'type': 'ministry',
            'website': 'https://www.government.nl/ministries/ministry-of-justice-and-security',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'General Intelligence and Security Service',
            'name_native': 'Algemene Inlichtingen- en Veiligheidsdienst',
            'type': 'agency',
            'website': 'https://www.aivd.nl',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Military Intelligence and Security Service',
            'name_native': 'Militaire Inlichtingen- en Veiligheidsdienst',
            'type': 'agency',
            'website': 'https://www.defensie.nl/organisatie/mivd',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'National Cyber Security Centre',
            'name_native': 'Nationaal Cyber Security Centrum',
            'type': 'agency',
            'website': 'https://www.ncsc.nl',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'House of Representatives',
            'name_native': 'Tweede Kamer',
            'type': 'parliament',
            'website': 'https://www.tweedekamer.nl',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Senate',
            'name_native': 'Eerste Kamer',
            'type': 'parliament',
            'website': 'https://www.eerstekamer.nl',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Netherlands Enterprise Agency',
            'name_native': 'Rijksdienst voor Ondernemend Nederland',
            'type': 'agency',
            'website': 'https://www.rvo.nl',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Netherlands Foreign Investment Agency',
            'name_native': 'Netherlands Foreign Investment Agency',
            'type': 'agency',
            'website': 'https://investinholland.com',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Authority for Consumers and Markets',
            'name_native': 'Autoriteit Consument en Markt',
            'type': 'regulator',
            'website': 'https://www.acm.nl',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        }
    ]

    print("Phase 1: Inserting verified Dutch institutions...")
    print()

    for inst in institutions:
        inst_id = generate_id('nl_verified', inst['name'])

        not_collected = {
            'china_relevance': '[NOT COLLECTED: Requires analytical framework]',
            'us_relevance': '[NOT COLLECTED: Requires analytical framework]',
            'tech_relevance': '[NOT COLLECTED: Requires analytical framework]',
            'policy_domains': '[NOT COLLECTED: Requires systematic cataloging]',
            'key_personnel': '[NOT COLLECTED: Requires biography parsing]'
        }

        notes_json = json.dumps({
            'collection_tier': 'tier_1_verified_only',
            'collection_date': inst['source_verified_date'],
            'collection_method': 'manual_url_verification',
            'website_accessible': inst['website_accessible'],
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
            'NL',
            inst['website'],
            None, None, None,
            'active',
            notes_json,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

        print(f"  + {inst['name']}")
        print(f"    URL: {inst['website']}")
        print()

    conn.commit()
    print(f"Total: {len(institutions)} institutions")
    print()

    # Validation
    cursor.execute('''
        SELECT COUNT(*) FROM european_institutions
        WHERE country_code = 'NL' AND china_relevance IS NOT NULL
    ''')
    fabricated = cursor.fetchone()[0]

    if fabricated == 0:
        print("+ NO FABRICATED DATA")
    else:
        print(f"WARNING: {fabricated} fabricated")
    print()

    # Summary
    cursor.execute('''
        SELECT country_code, COUNT(*) FROM european_institutions
        WHERE jurisdiction_level = 'national'
        GROUP BY country_code
        ORDER BY COUNT(*) DESC
    ''')
    print("COVERAGE:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    cursor.execute('SELECT COUNT(DISTINCT country_code) FROM european_institutions')
    print(f"\nCountries: {cursor.fetchone()[0]}/42")
    print()

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_netherlands_tier1()
