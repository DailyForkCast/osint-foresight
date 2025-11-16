#!/usr/bin/env python3
"""Portugal Autonomous Regions - Tier 1 Verified Subnational Collection
Azores and Madeira
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_portugal_autonomous():
    print("=" * 70)
    print("PORTUGAL AUTONOMOUS REGIONS - TIER 1 VERIFIED SUBNATIONAL")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Azores
        {'name': 'Government of the Azores', 'name_native': 'Governo dos Açores', 'type': 'executive', 'region': 'Azores', 'website': 'https://portal.azores.gov.pt'},
        {'name': 'Legislative Assembly of the Azores', 'name_native': 'Assembleia Legislativa da Região Autónoma dos Açores', 'type': 'parliament', 'region': 'Azores', 'website': 'https://www.azores.gov.pt/assembleia'},
        {'name': 'Regional Directorate for External Affairs', 'name_native': 'Direção Regional dos Assuntos Externos', 'type': 'agency', 'region': 'Azores', 'website': 'https://portal.azores.gov.pt'},

        # Madeira
        {'name': 'Government of Madeira', 'name_native': 'Governo Regional da Madeira', 'type': 'executive', 'region': 'Madeira', 'website': 'https://www.madeira.gov.pt'},
        {'name': 'Legislative Assembly of Madeira', 'name_native': 'Assembleia Legislativa da Região Autónoma da Madeira', 'type': 'parliament', 'region': 'Madeira', 'website': 'https://www.alram.pt'},
        {'name': 'Madeira Investment Agency', 'name_native': 'Invest Madeira', 'type': 'agency', 'region': 'Madeira', 'website': 'https://www.investmadeira.pt'}
    ]

    for inst in institutions:
        region_cleaned = inst['region'].lower().replace(' ', '_')
        inst_id = generate_id(f"pt_{region_cleaned}_subnational", inst['name'])
        notes = json.dumps({
            'collection_tier': 'tier_1_verified_only',
            'collection_date': '2025-10-26',
            'autonomous_region': inst['region'],
            'not_collected': {'china_relevance': '[NOT COLLECTED]'}
        })

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, subnational_jurisdiction, official_website,
             china_relevance, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inst_id, inst['name'], inst['name_native'], inst['type'], 'subnational_autonomous',
              'PT', inst['region'], inst['website'], None, 'active', notes,
              datetime.now().isoformat(), datetime.now().isoformat()))
        print(f"  [PT-{inst['region']}] {inst['name']}")

    conn.commit()
    print(f"\nTotal autonomous regions: {len(set([i['region'] for i in institutions]))}")
    print(f"Total institutions: {len(institutions)}")

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]
    print(f"Total subnational (all countries): {total_subnational}")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_portugal_autonomous()
