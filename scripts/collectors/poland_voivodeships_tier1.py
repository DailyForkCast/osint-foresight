#!/usr/bin/env python3
"""Poland Voivodeships - Tier 1 Verified Subnational Collection
All 16 Polish voivodeships (województwa)
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_poland_voivodeships():
    print("=" * 70)
    print("POLAND VOIVODESHIPS - TIER 1 VERIFIED SUBNATIONAL")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Masovian (Warsaw, capital)
        {'name': 'Marshal Office of Masovian Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Mazowieckiego', 'type': 'executive', 'voivodeship': 'Masovian', 'website': 'https://www.mazovia.pl'},
        {'name': 'Masovian Voivodeship Assembly', 'name_native': 'Sejmik Województwa Mazowieckiego', 'type': 'parliament', 'voivodeship': 'Masovian', 'website': 'https://sejmik.mazovia.pl'},

        # Silesian (Katowice, industrial)
        {'name': 'Marshal Office of Silesian Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Śląskiego', 'type': 'executive', 'voivodeship': 'Silesian', 'website': 'https://www.slaskie.pl'},
        {'name': 'Silesian Voivodeship Assembly', 'name_native': 'Sejmik Województwa Śląskiego', 'type': 'parliament', 'voivodeship': 'Silesian', 'website': 'https://sejmik.slaskie.pl'},

        # Greater Poland (Poznań)
        {'name': 'Marshal Office of Greater Poland Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Wielkopolskiego', 'type': 'executive', 'voivodeship': 'Greater Poland', 'website': 'https://www.umww.pl'},
        {'name': 'Greater Poland Voivodeship Assembly', 'name_native': 'Sejmik Województwa Wielkopolskiego', 'type': 'parliament', 'voivodeship': 'Greater Poland', 'website': 'https://sejmik.wielkopolska.pl'},

        # Lesser Poland (Kraków)
        {'name': 'Marshal Office of Lesser Poland Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Małopolskiego', 'type': 'executive', 'voivodeship': 'Lesser Poland', 'website': 'https://www.malopolska.pl'},
        {'name': 'Lesser Poland Voivodeship Assembly', 'name_native': 'Sejmik Województwa Małopolskiego', 'type': 'parliament', 'voivodeship': 'Lesser Poland', 'website': 'https://bip.malopolska.pl/umwm'},

        # Lower Silesian (Wrocław)
        {'name': 'Marshal Office of Lower Silesian Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Dolnośląskiego', 'type': 'executive', 'voivodeship': 'Lower Silesian', 'website': 'https://www.umwd.dolnyslask.pl'},
        {'name': 'Lower Silesian Voivodeship Assembly', 'name_native': 'Sejmik Województwa Dolnośląskiego', 'type': 'parliament', 'voivodeship': 'Lower Silesian', 'website': 'https://sejmik.dolnyslask.pl'},

        # Łódź
        {'name': 'Marshal Office of Łódź Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Łódzkiego', 'type': 'executive', 'voivodeship': 'Łódź', 'website': 'https://www.lodzkie.pl'},
        {'name': 'Łódź Voivodeship Assembly', 'name_native': 'Sejmik Województwa Łódzkiego', 'type': 'parliament', 'voivodeship': 'Łódź', 'website': 'https://sejmik.lodzkie.pl'},

        # Pomeranian (Gdańsk)
        {'name': 'Marshal Office of Pomeranian Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Pomorskiego', 'type': 'executive', 'voivodeship': 'Pomeranian', 'website': 'https://www.pomorskie.eu'},
        {'name': 'Pomeranian Voivodeship Assembly', 'name_native': 'Sejmik Województwa Pomorskiego', 'type': 'parliament', 'voivodeship': 'Pomeranian', 'website': 'https://sejmik.pomorskie.eu'},

        # Kuyavian-Pomeranian (Bydgoszcz/Toruń)
        {'name': 'Marshal Office of Kuyavian-Pomeranian Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Kujawsko-Pomorskiego', 'type': 'executive', 'voivodeship': 'Kuyavian-Pomeranian', 'website': 'https://www.kujawsko-pomorskie.pl'},
        {'name': 'Kuyavian-Pomeranian Voivodeship Assembly', 'name_native': 'Sejmik Województwa Kujawsko-Pomorskiego', 'type': 'parliament', 'voivodeship': 'Kuyavian-Pomeranian', 'website': 'https://sejmik.kujawsko-pomorskie.pl'},

        # West Pomeranian (Szczecin)
        {'name': 'Marshal Office of West Pomeranian Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Zachodniopomorskiego', 'type': 'executive', 'voivodeship': 'West Pomeranian', 'website': 'https://www.wzp.pl'},
        {'name': 'West Pomeranian Voivodeship Assembly', 'name_native': 'Sejmik Województwa Zachodniopomorskiego', 'type': 'parliament', 'voivodeship': 'West Pomeranian', 'website': 'https://sejmik.wzp.pl'},

        # Lublin
        {'name': 'Marshal Office of Lublin Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Lubelskiego', 'type': 'executive', 'voivodeship': 'Lublin', 'website': 'https://www.lubelskie.pl'},
        {'name': 'Lublin Voivodeship Assembly', 'name_native': 'Sejmik Województwa Lubelskiego', 'type': 'parliament', 'voivodeship': 'Lublin', 'website': 'https://sejmik.lubelskie.pl'},

        # Podlaskie (Białystok)
        {'name': 'Marshal Office of Podlaskie Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Podlaskiego', 'type': 'executive', 'voivodeship': 'Podlaskie', 'website': 'https://www.wrotapodlasia.pl'},
        {'name': 'Podlaskie Voivodeship Assembly', 'name_native': 'Sejmik Województwa Podlaskiego', 'type': 'parliament', 'voivodeship': 'Podlaskie', 'website': 'https://sejmik.wrotapodlasia.pl'},

        # Subcarpathian (Rzeszów)
        {'name': 'Marshal Office of Subcarpathian Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Podkarpackiego', 'type': 'executive', 'voivodeship': 'Subcarpathian', 'website': 'https://www.podkarpackie.pl'},
        {'name': 'Subcarpathian Voivodeship Assembly', 'name_native': 'Sejmik Województwa Podkarpackiego', 'type': 'parliament', 'voivodeship': 'Subcarpathian', 'website': 'https://sejmik.podkarpackie.pl'},

        # Warmian-Masurian (Olsztyn)
        {'name': 'Marshal Office of Warmian-Masurian Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Warmińsko-Mazurskiego', 'type': 'executive', 'voivodeship': 'Warmian-Masurian', 'website': 'https://www.warmia.mazury.pl'},
        {'name': 'Warmian-Masurian Voivodeship Assembly', 'name_native': 'Sejmik Województwa Warmińsko-Mazurskiego', 'type': 'parliament', 'voivodeship': 'Warmian-Masurian', 'website': 'https://sejmik.warmia.mazury.pl'},

        # Lubusz (Gorzów Wielkopolski/Zielona Góra)
        {'name': 'Marshal Office of Lubusz Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Lubuskiego', 'type': 'executive', 'voivodeship': 'Lubusz', 'website': 'https://lubuskie.pl'},
        {'name': 'Lubusz Voivodeship Assembly', 'name_native': 'Sejmik Województwa Lubuskiego', 'type': 'parliament', 'voivodeship': 'Lubusz', 'website': 'https://sejmik.lubuskie.pl'},

        # Świętokrzyskie (Kielce)
        {'name': 'Marshal Office of Świętokrzyskie Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Świętokrzyskiego', 'type': 'executive', 'voivodeship': 'Świętokrzyskie', 'website': 'https://www.swietokrzyskie.pro'},
        {'name': 'Świętokrzyskie Voivodeship Assembly', 'name_native': 'Sejmik Województwa Świętokrzyskiego', 'type': 'parliament', 'voivodeship': 'Świętokrzyskie', 'website': 'https://sejmik.kielce.pl'},

        # Opole
        {'name': 'Marshal Office of Opole Voivodeship', 'name_native': 'Urząd Marszałkowski Województwa Opolskiego', 'type': 'executive', 'voivodeship': 'Opole', 'website': 'https://www.umwo.opole.pl'},
        {'name': 'Opole Voivodeship Assembly', 'name_native': 'Sejmik Województwa Opolskiego', 'type': 'parliament', 'voivodeship': 'Opole', 'website': 'https://sejmik.opole.pl'}
    ]

    for inst in institutions:
        voivodeship_cleaned = inst['voivodeship'].lower().replace(' ', '_').replace('-', '_')
        inst_id = generate_id(f"pl_{voivodeship_cleaned}_subnational", inst['name'])
        notes = json.dumps({
            'collection_tier': 'tier_1_verified_only',
            'collection_date': '2025-10-26',
            'voivodeship': inst['voivodeship'],
            'not_collected': {'china_relevance': '[NOT COLLECTED]'}
        })

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, subnational_jurisdiction, official_website,
             china_relevance, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inst_id, inst['name'], inst['name_native'], inst['type'], 'subnational_region',
              'PL', inst['voivodeship'], inst['website'], None, 'active', notes,
              datetime.now().isoformat(), datetime.now().isoformat()))
        print(f"  [PL-{inst['voivodeship']}] {inst['name']}".encode('ascii', errors='replace').decode('ascii'))

    conn.commit()
    print(f"\nTotal voivodeships: {len(set([i['voivodeship'] for i in institutions]))}")
    print(f"Total institutions: {len(institutions)}")

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]
    print(f"Total subnational (all countries): {total_subnational}")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_poland_voivodeships()
