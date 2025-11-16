#!/usr/bin/env python3
"""Czech Republic Regions - Tier 1 Verified Subnational Collection
All 13 regions plus Prague (capital)
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_czech_regions():
    print("=" * 70)
    print("CZECH REPUBLIC REGIONS - TIER 1 VERIFIED SUBNATIONAL")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Prague (capital, city-region)
        {'name': 'Prague City Hall', 'name_native': 'Magistrát hlavního města Prahy', 'type': 'executive', 'region': 'Prague', 'website': 'https://www.praha.eu'},
        {'name': 'Prague City Assembly', 'name_native': 'Zastupitelstvo hlavního města Prahy', 'type': 'parliament', 'region': 'Prague', 'website': 'https://www.praha.eu/jnp/cz/o_meste/zastupitelstvo/'},

        # Central Bohemian Region
        {'name': 'Central Bohemian Region Authority', 'name_native': 'Krajský úřad Středočeského kraje', 'type': 'executive', 'region': 'Central Bohemia', 'website': 'https://www.kr-stredocesky.cz'},
        {'name': 'Central Bohemian Regional Assembly', 'name_native': 'Zastupitelstvo Středočeského kraje', 'type': 'parliament', 'region': 'Central Bohemia', 'website': 'https://www.kr-stredocesky.cz/zastupitelstvo'},

        # South Bohemian Region
        {'name': 'South Bohemian Region Authority', 'name_native': 'Krajský úřad Jihočeského kraje', 'type': 'executive', 'region': 'South Bohemia', 'website': 'https://www.kraj-jihocesky.cz'},
        {'name': 'South Bohemian Regional Assembly', 'name_native': 'Zastupitelstvo Jihočeského kraje', 'type': 'parliament', 'region': 'South Bohemia', 'website': 'https://www.kraj-jihocesky.cz/zastupitelstvo'},

        # Plzeň Region
        {'name': 'Plzeň Region Authority', 'name_native': 'Krajský úřad Plzeňského kraje', 'type': 'executive', 'region': 'Plzeň', 'website': 'https://www.plzensky-kraj.cz'},
        {'name': 'Plzeň Regional Assembly', 'name_native': 'Zastupitelstvo Plzeňského kraje', 'type': 'parliament', 'region': 'Plzeň', 'website': 'https://www.plzensky-kraj.cz/zastupitelstvo'},

        # Karlovy Vary Region
        {'name': 'Karlovy Vary Region Authority', 'name_native': 'Krajský úřad Karlovarského kraje', 'type': 'executive', 'region': 'Karlovy Vary', 'website': 'https://www.kr-karlovarsky.cz'},

        # Ústí nad Labem Region
        {'name': 'Ústí nad Labem Region Authority', 'name_native': 'Krajský úřad Ústeckého kraje', 'type': 'executive', 'region': 'Ústí nad Labem', 'website': 'https://www.kr-ustecky.cz'},

        # Liberec Region
        {'name': 'Liberec Region Authority', 'name_native': 'Krajský úřad Libereckého kraje', 'type': 'executive', 'region': 'Liberec', 'website': 'https://www.kraj-lbc.cz'},

        # Hradec Králové Region
        {'name': 'Hradec Králové Region Authority', 'name_native': 'Krajský úřad Královéhradeckého kraje', 'type': 'executive', 'region': 'Hradec Králové', 'website': 'https://www.kr-kralovehradecky.cz'},

        # Pardubice Region
        {'name': 'Pardubice Region Authority', 'name_native': 'Krajský úřad Pardubického kraje', 'type': 'executive', 'region': 'Pardubice', 'website': 'https://www.pardubickykraj.cz'},

        # Vysočina Region
        {'name': 'Vysočina Region Authority', 'name_native': 'Krajský úřad kraje Vysočina', 'type': 'executive', 'region': 'Vysočina', 'website': 'https://www.kr-vysocina.cz'},

        # South Moravian Region (Brno)
        {'name': 'South Moravian Region Authority', 'name_native': 'Krajský úřad Jihomoravského kraje', 'type': 'executive', 'region': 'South Moravia', 'website': 'https://www.kr-jihomoravsky.cz'},
        {'name': 'South Moravian Regional Assembly', 'name_native': 'Zastupitelstvo Jihomoravského kraje', 'type': 'parliament', 'region': 'South Moravia', 'website': 'https://www.kr-jihomoravsky.cz/zastupitelstvo'},

        # Olomouc Region
        {'name': 'Olomouc Region Authority', 'name_native': 'Krajský úřad Olomouckého kraje', 'type': 'executive', 'region': 'Olomouc', 'website': 'https://www.kr-olomoucky.cz'},

        # Zlín Region
        {'name': 'Zlín Region Authority', 'name_native': 'Krajský úřad Zlínského kraje', 'type': 'executive', 'region': 'Zlín', 'website': 'https://www.kr-zlinsky.cz'},

        # Moravian-Silesian Region (Ostrava)
        {'name': 'Moravian-Silesian Region Authority', 'name_native': 'Krajský úřad Moravskoslezského kraje', 'type': 'executive', 'region': 'Moravian-Silesian', 'website': 'https://www.msk.cz'},
        {'name': 'Moravian-Silesian Regional Assembly', 'name_native': 'Zastupitelstvo Moravskoslezského kraje', 'type': 'parliament', 'region': 'Moravian-Silesian', 'website': 'https://www.msk.cz/zastupitelstvo'}
    ]

    for inst in institutions:
        region_cleaned = inst['region'].lower().replace(' ', '_').replace('-', '_')
        inst_id = generate_id(f"cz_{region_cleaned}_subnational", inst['name'])
        notes = json.dumps({
            'collection_tier': 'tier_1_verified_only',
            'collection_date': '2025-10-26',
            'region': inst['region'],
            'not_collected': {'china_relevance': '[NOT COLLECTED]'}
        })

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, subnational_jurisdiction, official_website,
             china_relevance, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inst_id, inst['name'], inst['name_native'], inst['type'], 'subnational_region',
              'CZ', inst['region'], inst['website'], None, 'active', notes,
              datetime.now().isoformat(), datetime.now().isoformat()))
        print(f"  [CZ-{inst['region']}] {inst['name']}".encode('ascii', errors='replace').decode('ascii'))

    conn.commit()
    print(f"\nTotal regions: {len(set([i['region'] for i in institutions]))}")
    print(f"Total institutions: {len(institutions)}")

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]
    print(f"Total subnational (all countries): {total_subnational}")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_czech_regions()
