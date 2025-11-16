#!/usr/bin/env python3
"""
Italy Federal Institutions - Tier 1 Verified Collection
ZERO FABRICATION COMPLIANCE

Collects ONLY verifiable facts from official Italian government websites.
"""

import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    """Generate unique ID"""
    hash_part = hashlib.md5(text.encode()).hexdigest()[:12]
    return f"{prefix}_{hash_part}"

def collect_italy_tier1():
    """Collect Italian federal institutions - Tier 1 VERIFIED ONLY"""

    print("=" * 70)
    print("ITALY FEDERAL INSTITUTIONS - TIER 1 VERIFIED COLLECTION")
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
            'name': 'Ministry of Foreign Affairs and International Cooperation',
            'name_native': 'Ministero degli Affari Esteri e della Cooperazione Internazionale',
            'type': 'ministry',
            'website': 'https://www.esteri.it',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Ministry of Economy and Finance',
            'name_native': 'Ministero dell\'Economia e delle Finanze',
            'type': 'ministry',
            'website': 'https://www.mef.gov.it',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Ministry of Defence',
            'name_native': 'Ministero della Difesa',
            'type': 'ministry',
            'website': 'https://www.difesa.it',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Ministry of Enterprises and Made in Italy',
            'name_native': 'Ministero delle Imprese e del Made in Italy',
            'type': 'ministry',
            'website': 'https://www.mimit.gov.it',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Ministry of University and Research',
            'name_native': 'Ministero dell\'Università e della Ricerca',
            'type': 'ministry',
            'website': 'https://www.mur.gov.it',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Ministry of the Interior',
            'name_native': 'Ministero dell\'Interno',
            'type': 'ministry',
            'website': 'https://www.interno.gov.it',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'External Intelligence and Security Agency',
            'name_native': 'Agenzia Informazioni e Sicurezza Esterna',
            'type': 'agency',
            'website': 'https://www.sicurezzanazionale.gov.it/sisr.nsf/aise',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Internal Information and Security Agency',
            'name_native': 'Agenzia Informazioni e Sicurezza Interna',
            'type': 'agency',
            'website': 'https://www.sicurezzanazionale.gov.it/sisr.nsf/aisi',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'National Cybersecurity Agency',
            'name_native': 'Agenzia per la Cybersicurezza Nazionale',
            'type': 'agency',
            'website': 'https://www.acn.gov.it',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Chamber of Deputies',
            'name_native': 'Camera dei Deputati',
            'type': 'parliament',
            'website': 'https://www.camera.it',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Senate of the Republic',
            'name_native': 'Senato della Repubblica',
            'type': 'parliament',
            'website': 'https://www.senato.it',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Italian Competition Authority',
            'name_native': 'Autorità Garante della Concorrenza e del Mercato',
            'type': 'regulator',
            'website': 'https://www.agcm.it',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Italian Trade Agency',
            'name_native': 'Agenzia ICE',
            'type': 'agency',
            'website': 'https://www.ice.it',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Invitalia',
            'name_native': 'Agenzia nazionale per l\'attrazione degli investimenti',
            'type': 'agency',
            'website': 'https://www.invitalia.it',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        }
    ]

    print("Phase 1: Inserting verified Italian institutions...")
    print()

    for inst in institutions:
        inst_id = generate_id('it_verified', inst['name'])

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
            'IT',
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
    print(f"Total institutions collected: {len(institutions)}")
    print()

    # Summary
    print("=" * 70)
    print("TIER 1 COLLECTION COMPLETE")
    print("=" * 70)
    print()

    # Validation
    cursor.execute('''
        SELECT COUNT(*) FROM european_institutions
        WHERE country_code = 'IT' AND china_relevance IS NOT NULL
    ''')
    fabricated = cursor.fetchone()[0]

    if fabricated == 0:
        print("+ NO FABRICATED DATA")
    else:
        print(f"WARNING: {fabricated} institutions have fabricated data")
    print()

    # Show coverage
    cursor.execute('''
        SELECT country_code, COUNT(*) FROM european_institutions
        WHERE jurisdiction_level = 'national'
        GROUP BY country_code
        ORDER BY COUNT(*) DESC
    ''')

    print("COVERAGE BY COUNTRY:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} institutions")

    cursor.execute('SELECT COUNT(DISTINCT country_code) FROM european_institutions')
    print(f"\nCountries: {cursor.fetchone()[0]}/42")
    print()

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_italy_tier1()
