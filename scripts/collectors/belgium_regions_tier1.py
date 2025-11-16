#!/usr/bin/env python3
"""Belgium Regions - Tier 1 Verified Subnational Collection
3 Regions + 3 Communities (Flemish, French, German-speaking)
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_belgium_regions():
    print("=" * 70)
    print("BELGIUM REGIONS & COMMUNITIES - TIER 1 VERIFIED SUBNATIONAL")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Flemish Region (Flanders)
        {'name': 'Flemish Government', 'name_native': 'Vlaamse Regering', 'type': 'executive', 'region': 'Flanders', 'website': 'https://www.vlaanderen.be/vlaamse-regering'},
        {'name': 'Flemish Parliament', 'name_native': 'Vlaams Parlement', 'type': 'parliament', 'region': 'Flanders', 'website': 'https://www.vlaamsparlement.be'},
        {'name': 'Flanders Investment & Trade', 'name_native': 'Flanders Investment & Trade', 'type': 'agency', 'region': 'Flanders', 'website': 'https://www.flandersinvestmentandtrade.com'},
        {'name': 'Flanders Innovation & Entrepreneurship', 'name_native': 'VLAIO', 'type': 'agency', 'region': 'Flanders', 'website': 'https://www.vlaio.be'},

        # Walloon Region (Wallonia)
        {'name': 'Walloon Government', 'name_native': 'Gouvernement wallon', 'type': 'executive', 'region': 'Wallonia', 'website': 'https://www.wallonie.be'},
        {'name': 'Parliament of Wallonia', 'name_native': 'Parlement de Wallonie', 'type': 'parliament', 'region': 'Wallonia', 'website': 'https://www.parlement-wallonie.be'},
        {'name': 'Wallonia Foreign Trade and Investment Agency', 'name_native': 'Agence wallonne à l\'Exportation', 'type': 'agency', 'region': 'Wallonia', 'website': 'https://www.awex.be'},

        # Brussels-Capital Region
        {'name': 'Government of the Brussels-Capital Region', 'name_native': 'Gouvernement de la Région de Bruxelles-Capitale', 'type': 'executive', 'region': 'Brussels-Capital', 'website': 'https://be.brussels'},
        {'name': 'Parliament of the Brussels-Capital Region', 'name_native': 'Parlement de la Région de Bruxelles-Capitale', 'type': 'parliament', 'region': 'Brussels-Capital', 'website': 'https://www.parlement.brussels'},
        {'name': 'Brussels Invest & Export', 'name_native': 'hub.brussels', 'type': 'agency', 'region': 'Brussels-Capital', 'website': 'https://hub.brussels'},

        # French Community
        {'name': 'Government of the French Community', 'name_native': 'Gouvernement de la Fédération Wallonie-Bruxelles', 'type': 'executive', 'region': 'French Community', 'website': 'https://www.federation-wallonie-bruxelles.be'},
        {'name': 'Parliament of the French Community', 'name_native': 'Parlement de la Fédération Wallonie-Bruxelles', 'type': 'parliament', 'region': 'French Community', 'website': 'https://www.pfwb.be'},

        # German-speaking Community
        {'name': 'Government of the German-speaking Community', 'name_native': 'Regierung der Deutschsprachigen Gemeinschaft', 'type': 'executive', 'region': 'German-speaking Community', 'website': 'https://www.dg.be'},
        {'name': 'Parliament of the German-speaking Community', 'name_native': 'Parlament der Deutschsprachigen Gemeinschaft', 'type': 'parliament', 'region': 'German-speaking Community', 'website': 'https://www.pdg.be'}
    ]

    for inst in institutions:
        inst_id = generate_id(f"be_{inst['region'].lower().replace(' ', '_').replace('-', '_')}_subnational", inst['name'])
        notes = json.dumps({
            'collection_tier': 'tier_1_verified_only',
            'collection_date': '2025-10-26',
            'region_community': inst['region'],
            'not_collected': {'china_relevance': '[NOT COLLECTED]'}
        })

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, subnational_jurisdiction, official_website,
             china_relevance, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inst_id, inst['name'], inst['name_native'], inst['type'], 'subnational_region',
              'BE', inst['region'], inst['website'], None, 'active', notes,
              datetime.now().isoformat(), datetime.now().isoformat()))
        print(f"  [BE-{inst['region']}] {inst['name']}")

    conn.commit()
    print(f"\nTotal regions/communities: {len(set([i['region'] for i in institutions]))}")
    print(f"Total institutions: {len(institutions)}")

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]
    print(f"Total subnational (all countries): {total_subnational}")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_belgium_regions()
