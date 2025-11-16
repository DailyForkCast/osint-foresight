#!/usr/bin/env python3
"""Italy Regions - Tier 1 Verified Subnational Collection
Priority: Major regions with economic/political significance
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_italy_regions():
    print("=" * 70)
    print("ITALY REGIONS - TIER 1 VERIFIED SUBNATIONAL")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Lombardy (economic powerhouse, Milan)
        {'name': 'Region of Lombardy', 'name_native': 'Regione Lombardia', 'type': 'executive', 'region': 'Lombardy', 'website': 'https://www.regione.lombardia.it'},
        {'name': 'Regional Council of Lombardy', 'name_native': 'Consiglio regionale della Lombardia', 'type': 'parliament', 'region': 'Lombardy', 'website': 'https://www.consiglio.regione.lombardia.it'},
        {'name': 'Lombardy Development Agency', 'name_native': 'Agenzia per lo sviluppo', 'type': 'agency', 'region': 'Lombardy', 'website': 'https://www.regione.lombardia.it'},

        # Lazio (capital region, Rome)
        {'name': 'Region of Lazio', 'name_native': 'Regione Lazio', 'type': 'executive', 'region': 'Lazio', 'website': 'https://www.regione.lazio.it'},
        {'name': 'Regional Council of Lazio', 'name_native': 'Consiglio regionale del Lazio', 'type': 'parliament', 'region': 'Lazio', 'website': 'https://www.consiglio.regione.lazio.it'},
        {'name': 'Lazio Innovation Hub', 'name_native': 'Lazio Innova', 'type': 'agency', 'region': 'Lazio', 'website': 'https://www.lazioinnova.it'},

        # Veneto (Venice, strong economy)
        {'name': 'Region of Veneto', 'name_native': 'Regione del Veneto', 'type': 'executive', 'region': 'Veneto', 'website': 'https://www.regione.veneto.it'},
        {'name': 'Regional Council of Veneto', 'name_native': 'Consiglio regionale del Veneto', 'type': 'parliament', 'region': 'Veneto', 'website': 'https://www.consiglioveneto.it'},

        # Piedmont (Turin, automotive/industry)
        {'name': 'Region of Piedmont', 'name_native': 'Regione Piemonte', 'type': 'executive', 'region': 'Piedmont', 'website': 'https://www.regione.piemonte.it'},
        {'name': 'Regional Council of Piedmont', 'name_native': 'Consiglio regionale del Piemonte', 'type': 'parliament', 'region': 'Piedmont', 'website': 'https://www.cr.piemonte.it'},

        # Emilia-Romagna (Bologna, manufacturing)
        {'name': 'Region of Emilia-Romagna', 'name_native': 'Regione Emilia-Romagna', 'type': 'executive', 'region': 'Emilia-Romagna', 'website': 'https://www.regione.emilia-romagna.it'},
        {'name': 'Regional Assembly of Emilia-Romagna', 'name_native': 'Assemblea legislativa dell\'Emilia-Romagna', 'type': 'parliament', 'region': 'Emilia-Romagna', 'website': 'https://www.assemblea.emr.it'},

        # Tuscany (Florence, culture/tourism)
        {'name': 'Region of Tuscany', 'name_native': 'Regione Toscana', 'type': 'executive', 'region': 'Tuscany', 'website': 'https://www.regione.toscana.it'},
        {'name': 'Regional Council of Tuscany', 'name_native': 'Consiglio regionale della Toscana', 'type': 'parliament', 'region': 'Tuscany', 'website': 'https://www.consiglio.regione.toscana.it'},

        # Sicily (largest island)
        {'name': 'Sicilian Region', 'name_native': 'Regione Siciliana', 'type': 'executive', 'region': 'Sicily', 'website': 'https://www.regione.sicilia.it'},
        {'name': 'Sicilian Regional Assembly', 'name_native': 'Assemblea Regionale Siciliana', 'type': 'parliament', 'region': 'Sicily', 'website': 'https://www.ars.sicilia.it'},

        # Campania (Naples)
        {'name': 'Region of Campania', 'name_native': 'Regione Campania', 'type': 'executive', 'region': 'Campania', 'website': 'https://www.regione.campania.it'},
        {'name': 'Regional Council of Campania', 'name_native': 'Consiglio regionale della Campania', 'type': 'parliament', 'region': 'Campania', 'website': 'https://www.consiglio.regione.campania.it'},

        # Apulia (Puglia, southern Italy)
        {'name': 'Region of Apulia', 'name_native': 'Regione Puglia', 'type': 'executive', 'region': 'Apulia', 'website': 'https://www.regione.puglia.it'},
        {'name': 'Regional Council of Apulia', 'name_native': 'Consiglio regionale della Puglia', 'type': 'parliament', 'region': 'Apulia', 'website': 'https://www.consiglio.puglia.it'},

        # Liguria (Genoa, port city)
        {'name': 'Region of Liguria', 'name_native': 'Regione Liguria', 'type': 'executive', 'region': 'Liguria', 'website': 'https://www.regione.liguria.it'},
        {'name': 'Regional Council of Liguria', 'name_native': 'Consiglio regionale della Liguria', 'type': 'parliament', 'region': 'Liguria', 'website': 'https://www.consiglio.regione.liguria.it'}
    ]

    for inst in institutions:
        inst_id = generate_id(f"it_{inst['region'].lower().replace(' ', '_').replace('-', '_')}_subnational", inst['name'])
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
    print(f"\nTotal regions: {len(set([i['region'] for i in institutions]))}")
    print(f"Total institutions: {len(institutions)}")

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]
    print(f"Total subnational (all countries): {total_subnational}")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_italy_regions()
