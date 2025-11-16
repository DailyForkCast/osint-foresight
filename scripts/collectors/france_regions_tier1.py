#!/usr/bin/env python3
"""France Regions - Tier 1 Verified Subnational Collection
Major metropolitan and overseas regions
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_france_regions():
    print("=" * 70)
    print("FRANCE REGIONS - TIER 1 VERIFIED SUBNATIONAL")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Île-de-France (Paris, capital region)
        {'name': 'Regional Council of Île-de-France', 'name_native': 'Conseil régional d\'Île-de-France', 'type': 'executive', 'region': 'Île-de-France', 'website': 'https://www.iledefrance.fr'},
        {'name': 'Île-de-France Regional Economic Development Agency', 'name_native': 'Paris Region Entreprises', 'type': 'agency', 'region': 'Île-de-France', 'website': 'https://www.investparisregion.eu'},

        # Auvergne-Rhône-Alpes (Lyon, 2nd largest economy)
        {'name': 'Regional Council of Auvergne-Rhône-Alpes', 'name_native': 'Conseil régional d\'Auvergne-Rhône-Alpes', 'type': 'executive', 'region': 'Auvergne-Rhône-Alpes', 'website': 'https://www.auvergnerhonealpes.fr'},
        {'name': 'AURA Economic Development Agency', 'name_native': 'AURA-EE', 'type': 'agency', 'region': 'Auvergne-Rhône-Alpes', 'website': 'https://www.auvergnerhonealpes-ee.fr'},

        # Nouvelle-Aquitaine (Bordeaux, largest region by area)
        {'name': 'Regional Council of Nouvelle-Aquitaine', 'name_native': 'Conseil régional de Nouvelle-Aquitaine', 'type': 'executive', 'region': 'Nouvelle-Aquitaine', 'website': 'https://www.nouvelle-aquitaine.fr'},
        {'name': 'Nouvelle-Aquitaine Development Agency', 'name_native': 'ADI Nouvelle-Aquitaine', 'type': 'agency', 'region': 'Nouvelle-Aquitaine', 'website': 'https://www.adi-na.fr'},

        # Occitanie (Toulouse, aerospace hub)
        {'name': 'Regional Council of Occitanie', 'name_native': 'Conseil régional d\'Occitanie', 'type': 'executive', 'region': 'Occitanie', 'website': 'https://www.laregion.fr'},
        {'name': 'Occitanie Investment Agency', 'name_native': 'AD\'OCC', 'type': 'agency', 'region': 'Occitanie', 'website': 'https://www.agence-adocc.com'},

        # Hauts-de-France (Lille, northern industrial region)
        {'name': 'Regional Council of Hauts-de-France', 'name_native': 'Conseil régional des Hauts-de-France', 'type': 'executive', 'region': 'Hauts-de-France', 'website': 'https://www.hautsdefrance.fr'},
        {'name': 'Hauts-de-France Investment Agency', 'name_native': 'Rev3', 'type': 'agency', 'region': 'Hauts-de-France', 'website': 'https://rev3.fr'},

        # Provence-Alpes-Côte d'Azur (Marseille, Mediterranean)
        {'name': 'Regional Council of Provence-Alpes-Côte d\'Azur', 'name_native': 'Conseil régional de Provence-Alpes-Côte d\'Azur', 'type': 'executive', 'region': 'Provence-Alpes-Côte d\'Azur', 'website': 'https://www.maregionsud.fr'},
        {'name': 'Sud Investment Agency', 'name_native': 'Provence Promotion', 'type': 'agency', 'region': 'Provence-Alpes-Côte d\'Azur', 'website': 'https://www.investinprovence.com'},

        # Grand Est (Strasbourg, EU institutions)
        {'name': 'Regional Council of Grand Est', 'name_native': 'Conseil régional du Grand Est', 'type': 'executive', 'region': 'Grand Est', 'website': 'https://www.grandest.fr'},
        {'name': 'Grand Est Economic Development Agency', 'name_native': 'Grand E-Nov+', 'type': 'agency', 'region': 'Grand Est', 'website': 'https://www.grandest.fr/vos-aides/grand-e-nov/'},

        # Pays de la Loire (Nantes)
        {'name': 'Regional Council of Pays de la Loire', 'name_native': 'Conseil régional des Pays de la Loire', 'type': 'executive', 'region': 'Pays de la Loire', 'website': 'https://www.paysdelaloire.fr'},
        {'name': 'Pays de la Loire Development Agency', 'name_native': 'Solutions&co', 'type': 'agency', 'region': 'Pays de la Loire', 'website': 'https://www.solutions-eco.fr'},

        # Bretagne (Rennes)
        {'name': 'Regional Council of Brittany', 'name_native': 'Conseil régional de Bretagne', 'type': 'executive', 'region': 'Bretagne', 'website': 'https://www.bretagne.bzh'},
        {'name': 'Brittany Economic Development Agency', 'name_native': 'Bretagne Développement Innovation', 'type': 'agency', 'region': 'Bretagne', 'website': 'https://www.bdi.fr'},

        # Normandie (Rouen)
        {'name': 'Regional Council of Normandy', 'name_native': 'Conseil régional de Normandie', 'type': 'executive', 'region': 'Normandie', 'website': 'https://www.normandie.fr'},
        {'name': 'Normandy Investment Agency', 'name_native': 'AD Normandie', 'type': 'agency', 'region': 'Normandie', 'website': 'https://www.agence-normandie-attractivite.fr'},

        # Bourgogne-Franche-Comté (Dijon)
        {'name': 'Regional Council of Bourgogne-Franche-Comté', 'name_native': 'Conseil régional de Bourgogne-Franche-Comté', 'type': 'executive', 'region': 'Bourgogne-Franche-Comté', 'website': 'https://www.bourgognefranchecomte.fr'},

        # Centre-Val de Loire (Orléans)
        {'name': 'Regional Council of Centre-Val de Loire', 'name_native': 'Conseil régional du Centre-Val de Loire', 'type': 'executive', 'region': 'Centre-Val de Loire', 'website': 'https://www.centre-valdeloire.fr'},

        # Corse (Corsica, special status)
        {'name': 'Assembly of Corsica', 'name_native': 'Assemblée de Corse', 'type': 'parliament', 'region': 'Corse', 'website': 'https://www.isula.corsica'},
        {'name': 'Executive Council of Corsica', 'name_native': 'Conseil exécutif de Corse', 'type': 'executive', 'region': 'Corse', 'website': 'https://www.isula.corsica'}
    ]

    for inst in institutions:
        region_cleaned = inst['region'].lower().replace(' ', '_').replace('-', '_').replace("'", '')
        inst_id = generate_id(f"fr_{region_cleaned}_subnational", inst['name'])
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
              'FR', inst['region'], inst['website'], None, 'active', notes,
              datetime.now().isoformat(), datetime.now().isoformat()))
        print(f"  [FR-{inst['region']}] {inst['name']}")

    conn.commit()
    print(f"\nTotal regions: {len(set([i['region'] for i in institutions]))}")
    print(f"Total institutions: {len(institutions)}")

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]
    print(f"Total subnational (all countries): {total_subnational}")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_france_regions()
