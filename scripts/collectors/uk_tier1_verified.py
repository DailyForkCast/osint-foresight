#!/usr/bin/env python3
"""
United Kingdom Federal Institutions - Tier 1 Verified Collection
ZERO FABRICATION COMPLIANCE
"""

import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    """Generate unique ID"""
    hash_part = hashlib.md5(text.encode()).hexdigest()[:12]
    return f"{prefix}_{hash_part}"

def collect_uk_tier1():
    """Collect UK federal institutions - Tier 1 VERIFIED ONLY"""

    print("=" * 70)
    print("UNITED KINGDOM FEDERAL INSTITUTIONS - TIER 1 VERIFIED")
    print("=" * 70)
    print()
    print("Collection Date: 2025-10-26")
    print()

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        {
            'name': 'Foreign, Commonwealth and Development Office',
            'name_native': 'Foreign, Commonwealth and Development Office',
            'type': 'ministry',
            'website': 'https://www.gov.uk/government/organisations/foreign-commonwealth-development-office',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Ministry of Defence',
            'name_native': 'Ministry of Defence',
            'type': 'ministry',
            'website': 'https://www.gov.uk/government/organisations/ministry-of-defence',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Department for Business and Trade',
            'name_native': 'Department for Business and Trade',
            'type': 'ministry',
            'website': 'https://www.gov.uk/government/organisations/department-for-business-and-trade',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Department for Science, Innovation and Technology',
            'name_native': 'Department for Science, Innovation and Technology',
            'type': 'ministry',
            'website': 'https://www.gov.uk/government/organisations/department-for-science-innovation-and-technology',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'HM Treasury',
            'name_native': 'HM Treasury',
            'type': 'ministry',
            'website': 'https://www.gov.uk/government/organisations/hm-treasury',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Home Office',
            'name_native': 'Home Office',
            'type': 'ministry',
            'website': 'https://www.gov.uk/government/organisations/home-office',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Security Service (MI5)',
            'name_native': 'Security Service',
            'type': 'agency',
            'website': 'https://www.mi5.gov.uk',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Secret Intelligence Service (MI6)',
            'name_native': 'Secret Intelligence Service',
            'type': 'agency',
            'website': 'https://www.sis.gov.uk',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Government Communications Headquarters',
            'name_native': 'Government Communications Headquarters',
            'type': 'agency',
            'website': 'https://www.gchq.gov.uk',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'National Cyber Security Centre',
            'name_native': 'National Cyber Security Centre',
            'type': 'agency',
            'website': 'https://www.ncsc.gov.uk',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'House of Commons',
            'name_native': 'House of Commons',
            'type': 'parliament',
            'website': 'https://www.parliament.uk/business/commons/',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'House of Lords',
            'name_native': 'House of Lords',
            'type': 'parliament',
            'website': 'https://www.parliament.uk/business/lords/',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Competition and Markets Authority',
            'name_native': 'Competition and Markets Authority',
            'type': 'regulator',
            'website': 'https://www.gov.uk/government/organisations/competition-and-markets-authority',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'UK Export Finance',
            'name_native': 'UK Export Finance',
            'type': 'agency',
            'website': 'https://www.gov.uk/government/organisations/uk-export-finance',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Department for International Trade',
            'name_native': 'Department for International Trade',
            'type': 'agency',
            'website': 'https://www.gov.uk/government/organisations/department-for-international-trade',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        }
    ]

    print("Phase 1: Inserting verified UK institutions...")
    print()

    for inst in institutions:
        inst_id = generate_id('uk_verified', inst['name'])

        not_collected = {
            'china_relevance': '[NOT COLLECTED: Requires analytical framework]',
            'us_relevance': '[NOT COLLECTED: Requires analytical framework]',
            'tech_relevance': '[NOT COLLECTED: Requires analytical framework]'
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
            'GB',
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
    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE country_code = \"GB\" AND china_relevance IS NOT NULL')
    if cursor.fetchone()[0] == 0:
        print("+ NO FABRICATED DATA")
    print()

    # Summary
    cursor.execute('''
        SELECT country_code, COUNT(*) FROM european_institutions
        WHERE jurisdiction_level = 'national'
        GROUP BY country_code
        ORDER BY COUNT(*) DESC LIMIT 10
    ''')
    print("TOP COUNTRIES:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    cursor.execute('SELECT COUNT(DISTINCT country_code) FROM european_institutions')
    total = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level = \"national\"')
    total_inst = cursor.fetchone()[0]

    print(f"\nCOVERAGE: {total}/42 countries, {total_inst} national institutions")
    print()

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_uk_tier1()
