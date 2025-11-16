#!/usr/bin/env python3
"""Spain Remaining Autonomous Communities - Tier 1 Verified Subnational Collection
Final 4 autonomous communities: Navarre, Extremadura, Cantabria, La Rioja
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_spain_remaining():
    print("=" * 70)
    print("SPAIN REMAINING AUTONOMOUS COMMUNITIES - TIER 1 VERIFIED")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Navarre
        {'name': 'Government of Navarre', 'name_native': 'Gobierno de Navarra', 'type': 'executive', 'region': 'Navarre', 'website': 'https://www.navarra.es'},
        {'name': 'Parliament of Navarre', 'name_native': 'Parlamento de Navarra', 'type': 'parliament', 'region': 'Navarre', 'website': 'https://www.parlamentodenavarra.es'},

        # Extremadura
        {'name': 'Junta de Extremadura', 'name_native': 'Junta de Extremadura', 'type': 'executive', 'region': 'Extremadura', 'website': 'https://www.juntaex.es'},
        {'name': 'Assembly of Extremadura', 'name_native': 'Asamblea de Extremadura', 'type': 'parliament', 'region': 'Extremadura', 'website': 'https://www.asambleaex.es'},

        # Cantabria
        {'name': 'Government of Cantabria', 'name_native': 'Gobierno de Cantabria', 'type': 'executive', 'region': 'Cantabria', 'website': 'https://www.cantabria.es'},
        {'name': 'Parliament of Cantabria', 'name_native': 'Parlamento de Cantabria', 'type': 'parliament', 'region': 'Cantabria', 'website': 'https://www.parlamento-cantabria.es'},

        # La Rioja
        {'name': 'Government of La Rioja', 'name_native': 'Gobierno de La Rioja', 'type': 'executive', 'region': 'La Rioja', 'website': 'https://www.larioja.org'},
        {'name': 'Parliament of La Rioja', 'name_native': 'Parlamento de La Rioja', 'type': 'parliament', 'region': 'La Rioja', 'website': 'https://www.parlamento-larioja.org'}
    ]

    for inst in institutions:
        region_cleaned = inst['region'].lower().replace(' ', '_')
        inst_id = generate_id(f"es_{region_cleaned}_subnational", inst['name'])
        notes = json.dumps({
            'collection_tier': 'tier_1_verified_only',
            'collection_date': '2025-10-26',
            'autonomous_community': inst['region'],
            'not_collected': {'china_relevance': '[NOT COLLECTED]'}
        })

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, subnational_jurisdiction, official_website,
             china_relevance, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inst_id, inst['name'], inst['name_native'], inst['type'], 'subnational_region',
              'ES', inst['region'], inst['website'], None, 'active', notes,
              datetime.now().isoformat(), datetime.now().isoformat()))
        print(f"  [ES-{inst['region']}] {inst['name']}")

    conn.commit()
    print(f"\nNew regions added: {len(set([i['region'] for i in institutions]))}")
    print(f"New institutions: {len(institutions)}")

    cursor.execute('SELECT COUNT(DISTINCT subnational_jurisdiction) FROM european_institutions WHERE country_code = "ES" AND jurisdiction_level LIKE "subnational%"')
    total_es_regions = cursor.fetchone()[0]
    print(f"Total Spanish autonomous communities: {total_es_regions}/17")

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]
    print(f"Total subnational (all countries): {total_subnational}")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_spain_remaining()
