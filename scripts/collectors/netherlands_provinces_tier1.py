#!/usr/bin/env python3
"""Netherlands Provinces - Tier 1 Verified Subnational Collection
All 12 Dutch provinces
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_netherlands_provinces():
    print("=" * 70)
    print("NETHERLANDS PROVINCES - TIER 1 VERIFIED SUBNATIONAL")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # North Holland (Amsterdam)
        {'name': 'Province of North Holland', 'name_native': 'Provincie Noord-Holland', 'type': 'executive', 'province': 'North Holland', 'website': 'https://www.noord-holland.nl'},
        {'name': 'Provincial Council of North Holland', 'name_native': 'Provinciale Staten Noord-Holland', 'type': 'parliament', 'province': 'North Holland', 'website': 'https://www.noord-holland.nl/Provinciale_Staten'},

        # South Holland (The Hague, Rotterdam)
        {'name': 'Province of South Holland', 'name_native': 'Provincie Zuid-Holland', 'type': 'executive', 'province': 'South Holland', 'website': 'https://www.zuid-holland.nl'},
        {'name': 'Provincial Council of South Holland', 'name_native': 'Provinciale Staten Zuid-Holland', 'type': 'parliament', 'province': 'South Holland', 'website': 'https://www.zuid-holland.nl/onderwerpen/bestuur/provinciale-staten/'},

        # Utrecht
        {'name': 'Province of Utrecht', 'name_native': 'Provincie Utrecht', 'type': 'executive', 'province': 'Utrecht', 'website': 'https://www.provincie-utrecht.nl'},
        {'name': 'Provincial Council of Utrecht', 'name_native': 'Provinciale Staten Utrecht', 'type': 'parliament', 'province': 'Utrecht', 'website': 'https://www.provincie-utrecht.nl/ps'},

        # North Brabant (Eindhoven)
        {'name': 'Province of North Brabant', 'name_native': 'Provincie Noord-Brabant', 'type': 'executive', 'province': 'North Brabant', 'website': 'https://www.brabant.nl'},
        {'name': 'Provincial Council of North Brabant', 'name_native': 'Provinciale Staten Noord-Brabant', 'type': 'parliament', 'province': 'North Brabant', 'website': 'https://www.brabant.nl/subsites/provinciale-staten'},

        # Gelderland (Arnhem)
        {'name': 'Province of Gelderland', 'name_native': 'Provincie Gelderland', 'type': 'executive', 'province': 'Gelderland', 'website': 'https://www.gelderland.nl'},
        {'name': 'Provincial Council of Gelderland', 'name_native': 'Provinciale Staten Gelderland', 'type': 'parliament', 'province': 'Gelderland', 'website': 'https://www.gelderland.nl/Provinciale-Staten'},

        # Overijssel (Zwolle)
        {'name': 'Province of Overijssel', 'name_native': 'Provincie Overijssel', 'type': 'executive', 'province': 'Overijssel', 'website': 'https://www.overijssel.nl'},
        {'name': 'Provincial Council of Overijssel', 'name_native': 'Provinciale Staten Overijssel', 'type': 'parliament', 'province': 'Overijssel', 'website': 'https://www.overijssel.nl/ps'},

        # Limburg (Maastricht)
        {'name': 'Province of Limburg', 'name_native': 'Provincie Limburg', 'type': 'executive', 'province': 'Limburg', 'website': 'https://www.limburg.nl'},
        {'name': 'Provincial Council of Limburg', 'name_native': 'Provinciale Staten Limburg', 'type': 'parliament', 'province': 'Limburg', 'website': 'https://www.limburg.nl/ps'},

        # Groningen
        {'name': 'Province of Groningen', 'name_native': 'Provincie Groningen', 'type': 'executive', 'province': 'Groningen', 'website': 'https://www.provinciegroningen.nl'},
        {'name': 'Provincial Council of Groningen', 'name_native': 'Provinciale Staten Groningen', 'type': 'parliament', 'province': 'Groningen', 'website': 'https://www.provinciegroningen.nl/ps'},

        # Friesland
        {'name': 'Province of Friesland', 'name_native': 'Provincie Fryslân', 'type': 'executive', 'province': 'Friesland', 'website': 'https://www.fryslan.frl'},
        {'name': 'Provincial Council of Friesland', 'name_native': 'Provinciale Staten Fryslân', 'type': 'parliament', 'province': 'Friesland', 'website': 'https://www.fryslan.frl/ps'},

        # Drenthe
        {'name': 'Province of Drenthe', 'name_native': 'Provincie Drenthe', 'type': 'executive', 'province': 'Drenthe', 'website': 'https://www.provincie.drenthe.nl'},
        {'name': 'Provincial Council of Drenthe', 'name_native': 'Provinciale Staten Drenthe', 'type': 'parliament', 'province': 'Drenthe', 'website': 'https://www.provincie.drenthe.nl/ps'},

        # Zeeland
        {'name': 'Province of Zeeland', 'name_native': 'Provincie Zeeland', 'type': 'executive', 'province': 'Zeeland', 'website': 'https://www.zeeland.nl'},
        {'name': 'Provincial Council of Zeeland', 'name_native': 'Provinciale Staten Zeeland', 'type': 'parliament', 'province': 'Zeeland', 'website': 'https://www.zeeland.nl/ps'},

        # Flevoland
        {'name': 'Province of Flevoland', 'name_native': 'Provincie Flevoland', 'type': 'executive', 'province': 'Flevoland', 'website': 'https://www.flevoland.nl'},
        {'name': 'Provincial Council of Flevoland', 'name_native': 'Provinciale Staten Flevoland', 'type': 'parliament', 'province': 'Flevoland', 'website': 'https://www.flevoland.nl/ps'}
    ]

    for inst in institutions:
        province_cleaned = inst['province'].lower().replace(' ', '_')
        inst_id = generate_id(f"nl_{province_cleaned}_subnational", inst['name'])
        notes = json.dumps({
            'collection_tier': 'tier_1_verified_only',
            'collection_date': '2025-10-26',
            'province': inst['province'],
            'not_collected': {'china_relevance': '[NOT COLLECTED]'}
        })

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, subnational_jurisdiction, official_website,
             china_relevance, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inst_id, inst['name'], inst['name_native'], inst['type'], 'subnational_state',
              'NL', inst['province'], inst['website'], None, 'active', notes,
              datetime.now().isoformat(), datetime.now().isoformat()))
        print(f"  [NL-{inst['province']}] {inst['name']}")

    conn.commit()
    print(f"\nTotal provinces: {len(set([i['province'] for i in institutions]))}")
    print(f"Total institutions: {len(institutions)}")

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]
    print(f"Total subnational (all countries): {total_subnational}")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_netherlands_provinces()
