#!/usr/bin/env python3
"""UK Devolved Governments - Tier 1 Verified Subnational Collection
Scotland, Wales, Northern Ireland
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_uk_devolved():
    print("=" * 70)
    print("UK DEVOLVED GOVERNMENTS - TIER 1 VERIFIED SUBNATIONAL")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Scotland
        {'name': 'Scottish Government', 'name_native': 'Riaghaltas na h-Alba', 'type': 'executive', 'nation': 'Scotland', 'website': 'https://www.gov.scot'},
        {'name': 'Scottish Parliament', 'name_native': 'Pàrlamaid na h-Alba', 'type': 'parliament', 'nation': 'Scotland', 'website': 'https://www.parliament.scot'},
        {'name': 'Scottish Government International Development', 'name_native': 'Scottish Government International Development', 'type': 'agency', 'nation': 'Scotland', 'website': 'https://www.gov.scot/policies/international-development/'},
        {'name': 'Scottish Enterprise', 'name_native': 'Scottish Enterprise', 'type': 'agency', 'nation': 'Scotland', 'website': 'https://www.scottish-enterprise.com'},
        {'name': 'Scotland Office', 'name_native': 'Scotland Office', 'type': 'ministry', 'nation': 'Scotland', 'website': 'https://www.gov.uk/government/organisations/office-of-the-secretary-of-state-for-scotland'},

        # Wales
        {'name': 'Welsh Government', 'name_native': 'Llywodraeth Cymru', 'type': 'executive', 'nation': 'Wales', 'website': 'https://www.gov.wales'},
        {'name': 'Senedd', 'name_native': 'Senedd Cymru', 'type': 'parliament', 'nation': 'Wales', 'website': 'https://senedd.wales'},
        {'name': 'Welsh Government International Relations', 'name_native': 'Cysylltiadau Rhyngwladol', 'type': 'agency', 'nation': 'Wales', 'website': 'https://www.gov.wales/international'},
        {'name': 'Business Wales', 'name_native': 'Busnes Cymru', 'type': 'agency', 'nation': 'Wales', 'website': 'https://businesswales.gov.wales'},

        # Northern Ireland
        {'name': 'Northern Ireland Executive', 'name_native': 'Northern Ireland Executive', 'type': 'executive', 'nation': 'Northern Ireland', 'website': 'https://www.northernireland.gov.uk'},
        {'name': 'Northern Ireland Assembly', 'name_native': 'Northern Ireland Assembly', 'type': 'parliament', 'nation': 'Northern Ireland', 'website': 'https://www.niassembly.gov.uk'},
        {'name': 'Department for the Economy Northern Ireland', 'name_native': 'Department for the Economy', 'type': 'ministry', 'nation': 'Northern Ireland', 'website': 'https://www.economy-ni.gov.uk'},
        {'name': 'Invest Northern Ireland', 'name_native': 'Invest Northern Ireland', 'type': 'agency', 'nation': 'Northern Ireland', 'website': 'https://www.investni.com'},
        {'name': 'Northern Ireland Office', 'name_native': 'Northern Ireland Office', 'type': 'ministry', 'nation': 'Northern Ireland', 'website': 'https://www.gov.uk/government/organisations/northern-ireland-office'}
    ]

    for inst in institutions:
        inst_id = generate_id(f"gb_{inst['nation'].lower().replace(' ', '_')}_subnational", inst['name'])
        notes = json.dumps({
            'collection_tier': 'tier_1_verified_only',
            'collection_date': '2025-10-26',
            'devolved_nation': inst['nation'],
            'not_collected': {'china_relevance': '[NOT COLLECTED]'}
        })

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, subnational_jurisdiction, official_website,
             china_relevance, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inst_id, inst['name'], inst['name_native'], inst['type'], 'subnational_nation',
              'GB', inst['nation'], inst['website'], None, 'active', notes,
              datetime.now().isoformat(), datetime.now().isoformat()))
        print(f"  [GB-{inst['nation']}] {inst['name']}")

    conn.commit()
    print(f"\nTotal devolved nations: {len(set([i['nation'] for i in institutions]))}")
    print(f"Total institutions: {len(institutions)}")

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]
    print(f"Total subnational (all countries): {total_subnational}")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_uk_devolved()
