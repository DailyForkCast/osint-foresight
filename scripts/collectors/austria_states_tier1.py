#!/usr/bin/env python3
"""Austria Federal States - Tier 1 Verified Subnational Collection
9 Bundesländer (federal states)
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_austria_states():
    print("=" * 70)
    print("AUSTRIA FEDERAL STATES - TIER 1 VERIFIED SUBNATIONAL")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Vienna (capital, city-state)
        {'name': 'Government of Vienna', 'name_native': 'Wiener Landesregierung', 'type': 'executive', 'state': 'Vienna', 'website': 'https://www.wien.gv.at'},
        {'name': 'Vienna City Council', 'name_native': 'Wiener Gemeinderat', 'type': 'parliament', 'state': 'Vienna', 'website': 'https://www.wien.gv.at/mdb'},
        {'name': 'Vienna Business Agency', 'name_native': 'Wirtschaftsagentur Wien', 'type': 'agency', 'state': 'Vienna', 'website': 'https://wirtschaftsagentur.at'},

        # Lower Austria
        {'name': 'Government of Lower Austria', 'name_native': 'NÖ Landesregierung', 'type': 'executive', 'state': 'Lower Austria', 'website': 'https://www.noe.gv.at'},
        {'name': 'Lower Austria Landtag', 'name_native': 'NÖ Landtag', 'type': 'parliament', 'state': 'Lower Austria', 'website': 'https://www.noe-landtag.gv.at'},

        # Upper Austria
        {'name': 'Government of Upper Austria', 'name_native': 'OÖ Landesregierung', 'type': 'executive', 'state': 'Upper Austria', 'website': 'https://www.land-oberoesterreich.gv.at'},
        {'name': 'Upper Austria Landtag', 'name_native': 'OÖ Landtag', 'type': 'parliament', 'state': 'Upper Austria', 'website': 'https://www.land-oberoesterreich.gv.at/landtag'},
        {'name': 'Business Upper Austria', 'name_native': 'Business Upper Austria', 'type': 'agency', 'state': 'Upper Austria', 'website': 'https://www.biz-up.at'},

        # Styria (Graz)
        {'name': 'Government of Styria', 'name_native': 'Steiermärkische Landesregierung', 'type': 'executive', 'state': 'Styria', 'website': 'https://www.verwaltung.steiermark.at'},
        {'name': 'Styrian Landtag', 'name_native': 'Steiermärkischer Landtag', 'type': 'parliament', 'state': 'Styria', 'website': 'https://www.landtag-steiermark.at'},

        # Tyrol (Innsbruck)
        {'name': 'Government of Tyrol', 'name_native': 'Tiroler Landesregierung', 'type': 'executive', 'state': 'Tyrol', 'website': 'https://www.tirol.gv.at'},
        {'name': 'Tyrolean Landtag', 'name_native': 'Tiroler Landtag', 'type': 'parliament', 'state': 'Tyrol', 'website': 'https://www.tirol.gv.at/landtag'},

        # Salzburg
        {'name': 'Government of Salzburg', 'name_native': 'Salzburger Landesregierung', 'type': 'executive', 'state': 'Salzburg', 'website': 'https://www.salzburg.gv.at'},
        {'name': 'Salzburg Landtag', 'name_native': 'Salzburger Landtag', 'type': 'parliament', 'state': 'Salzburg', 'website': 'https://www.salzburg.gv.at/landtag'},

        # Carinthia
        {'name': 'Government of Carinthia', 'name_native': 'Kärntner Landesregierung', 'type': 'executive', 'state': 'Carinthia', 'website': 'https://www.ktn.gv.at'},
        {'name': 'Carinthian Landtag', 'name_native': 'Kärntner Landtag', 'type': 'parliament', 'state': 'Carinthia', 'website': 'https://www.ktn.gv.at/landtag'},

        # Vorarlberg
        {'name': 'Government of Vorarlberg', 'name_native': 'Vorarlberger Landesregierung', 'type': 'executive', 'state': 'Vorarlberg', 'website': 'https://www.vorarlberg.at'},
        {'name': 'Vorarlberg Landtag', 'name_native': 'Vorarlberger Landtag', 'type': 'parliament', 'state': 'Vorarlberg', 'website': 'https://www.vorarlberg.at/landtag'},

        # Burgenland
        {'name': 'Government of Burgenland', 'name_native': 'Burgenländische Landesregierung', 'type': 'executive', 'state': 'Burgenland', 'website': 'https://www.burgenland.at'},
        {'name': 'Burgenland Landtag', 'name_native': 'Burgenländischer Landtag', 'type': 'parliament', 'state': 'Burgenland', 'website': 'https://www.burgenland.at/landtag'}
    ]

    for inst in institutions:
        inst_id = generate_id(f"at_{inst['state'].lower().replace(' ', '_')}_subnational", inst['name'])
        notes = json.dumps({
            'collection_tier': 'tier_1_verified_only',
            'collection_date': '2025-10-26',
            'bundesland': inst['state'],
            'not_collected': {'china_relevance': '[NOT COLLECTED]'}
        })

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, subnational_jurisdiction, official_website,
             china_relevance, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inst_id, inst['name'], inst['name_native'], inst['type'], 'subnational_state',
              'AT', inst['state'], inst['website'], None, 'active', notes,
              datetime.now().isoformat(), datetime.now().isoformat()))
        print(f"  [AT-{inst['state']}] {inst['name']}")

    conn.commit()
    print(f"\nTotal states (Bundesländer): {len(set([i['state'] for i in institutions]))}")
    print(f"Total institutions: {len(institutions)}")

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]
    print(f"Total subnational (all countries): {total_subnational}")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_austria_states()
