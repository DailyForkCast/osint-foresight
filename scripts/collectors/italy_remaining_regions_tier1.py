#!/usr/bin/env python3
"""Italy Remaining Regions - Tier 1 Verified Subnational Collection
Final 10 regions: Sardinia, Trentino-Alto Adige, Friuli-Venezia Giulia, Marche,
Umbria, Abruzzo, Molise, Basilicata, Calabria, Valle d'Aosta
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_italy_remaining():
    print("=" * 70)
    print("ITALY REMAINING REGIONS - TIER 1 VERIFIED")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Sardinia (autonomous)
        {'name': 'Region of Sardinia', 'name_native': 'Regione Autonoma della Sardegna', 'type': 'executive', 'region': 'Sardinia', 'website': 'https://www.regione.sardegna.it'},
        {'name': 'Regional Council of Sardinia', 'name_native': 'Consiglio regionale della Sardegna', 'type': 'parliament', 'region': 'Sardinia', 'website': 'https://www.consregsardegna.it'},

        # Trentino-Alto Adige / South Tyrol (autonomous)
        {'name': 'Region of Trentino-Alto Adige', 'name_native': 'Regione Trentino-Alto Adige', 'type': 'executive', 'region': 'Trentino-Alto Adige', 'website': 'https://www.regione.taa.it'},
        {'name': 'Regional Council of Trentino-Alto Adige', 'name_native': 'Consiglio regionale del Trentino-Alto Adige', 'type': 'parliament', 'region': 'Trentino-Alto Adige', 'website': 'https://www.consiglio.provincia.tn.it'},

        # Friuli-Venezia Giulia (autonomous)
        {'name': 'Region of Friuli-Venezia Giulia', 'name_native': 'Regione Autonoma Friuli-Venezia Giulia', 'type': 'executive', 'region': 'Friuli-Venezia Giulia', 'website': 'https://www.regione.fvg.it'},
        {'name': 'Regional Council of Friuli-Venezia Giulia', 'name_native': 'Consiglio regionale del Friuli-Venezia Giulia', 'type': 'parliament', 'region': 'Friuli-Venezia Giulia', 'website': 'https://www.consiglio.regione.fvg.it'},

        # Valle d'Aosta (autonomous)
        {'name': 'Region of Valle d\'Aosta', 'name_native': 'Regione Autonoma Valle d\'Aosta', 'type': 'executive', 'region': 'Valle d\'Aosta', 'website': 'https://www.regione.vda.it'},
        {'name': 'Regional Council of Valle d\'Aosta', 'name_native': 'Consiglio regionale della Valle d\'Aosta', 'type': 'parliament', 'region': 'Valle d\'Aosta', 'website': 'https://www.consiglio.vda.it'},

        # Marche
        {'name': 'Region of Marche', 'name_native': 'Regione Marche', 'type': 'executive', 'region': 'Marche', 'website': 'https://www.regione.marche.it'},
        {'name': 'Regional Assembly of Marche', 'name_native': 'Assemblea legislativa delle Marche', 'type': 'parliament', 'region': 'Marche', 'website': 'https://www.consiglio.marche.it'},

        # Umbria
        {'name': 'Region of Umbria', 'name_native': 'Regione Umbria', 'type': 'executive', 'region': 'Umbria', 'website': 'https://www.regione.umbria.it'},
        {'name': 'Regional Assembly of Umbria', 'name_native': 'Assemblea legislativa dell\'Umbria', 'type': 'parliament', 'region': 'Umbria', 'website': 'https://www.alumbria.it'},

        # Abruzzo
        {'name': 'Region of Abruzzo', 'name_native': 'Regione Abruzzo', 'type': 'executive', 'region': 'Abruzzo', 'website': 'https://www.regione.abruzzo.it'},
        {'name': 'Regional Council of Abruzzo', 'name_native': 'Consiglio regionale dell\'Abruzzo', 'type': 'parliament', 'region': 'Abruzzo', 'website': 'https://www.consiglio.regione.abruzzo.it'},

        # Molise
        {'name': 'Region of Molise', 'name_native': 'Regione Molise', 'type': 'executive', 'region': 'Molise', 'website': 'https://www3.regione.molise.it'},
        {'name': 'Regional Council of Molise', 'name_native': 'Consiglio regionale del Molise', 'type': 'parliament', 'region': 'Molise', 'website': 'https://www.consiglio.molise.it'},

        # Basilicata
        {'name': 'Region of Basilicata', 'name_native': 'Regione Basilicata', 'type': 'executive', 'region': 'Basilicata', 'website': 'https://www.regione.basilicata.it'},
        {'name': 'Regional Council of Basilicata', 'name_native': 'Consiglio regionale della Basilicata', 'type': 'parliament', 'region': 'Basilicata', 'website': 'https://www.consiglio.basilicata.it'},

        # Calabria
        {'name': 'Region of Calabria', 'name_native': 'Regione Calabria', 'type': 'executive', 'region': 'Calabria', 'website': 'https://www.regione.calabria.it'},
        {'name': 'Regional Council of Calabria', 'name_native': 'Consiglio regionale della Calabria', 'type': 'parliament', 'region': 'Calabria', 'website': 'https://www.consiglioregionale.calabria.it'}
    ]

    for inst in institutions:
        region_cleaned = inst['region'].lower().replace(' ', '_').replace('-', '_').replace("'", '')
        inst_id = generate_id(f"it_{region_cleaned}_subnational", inst['name'])
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
              'IT', inst['region'], inst['website'], None, 'active', notes,
              datetime.now().isoformat(), datetime.now().isoformat()))
        print(f"  [IT-{inst['region']}] {inst['name']}")

    conn.commit()
    print(f"\nNew regions added: {len(set([i['region'] for i in institutions]))}")
    print(f"New institutions: {len(institutions)}")

    cursor.execute('SELECT COUNT(DISTINCT subnational_jurisdiction) FROM european_institutions WHERE country_code = "IT" AND jurisdiction_level LIKE "subnational%"')
    total_it_regions = cursor.fetchone()[0]
    print(f"Total Italian regions: {total_it_regions}/20")

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]
    print(f"Total subnational (all countries): {total_subnational}")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_italy_remaining()
