#!/usr/bin/env python3
"""Spain Autonomous Communities - Tier 1 Verified Subnational Collection
Priority: Major autonomous communities with economic/political significance
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_spain_autonomous():
    print("=" * 70)
    print("SPAIN AUTONOMOUS COMMUNITIES - TIER 1 VERIFIED SUBNATIONAL")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Catalonia (Catalunya) - Barcelona, economic powerhouse
        {'name': 'Government of Catalonia', 'name_native': 'Generalitat de Catalunya', 'type': 'executive', 'region': 'Catalonia', 'website': 'https://web.gencat.cat'},
        {'name': 'Parliament of Catalonia', 'name_native': 'Parlament de Catalunya', 'type': 'parliament', 'region': 'Catalonia', 'website': 'https://www.parlament.cat'},
        {'name': 'Catalonia Trade & Investment', 'name_native': 'ACCIÓ', 'type': 'agency', 'region': 'Catalonia', 'website': 'https://accio.gencat.cat'},

        # Madrid - capital region
        {'name': 'Government of Madrid', 'name_native': 'Comunidad de Madrid', 'type': 'executive', 'region': 'Madrid', 'website': 'https://www.comunidad.madrid'},
        {'name': 'Assembly of Madrid', 'name_native': 'Asamblea de Madrid', 'type': 'parliament', 'region': 'Madrid', 'website': 'https://www.asambleamadrid.es'},
        {'name': 'Madrid Regional Development Agency', 'name_native': 'Madrid Región', 'type': 'agency', 'region': 'Madrid', 'website': 'https://www.madridemprende.com'},

        # Basque Country (Euskadi) - strong autonomy
        {'name': 'Basque Government', 'name_native': 'Eusko Jaurlaritza', 'type': 'executive', 'region': 'Basque Country', 'website': 'https://www.euskadi.eus'},
        {'name': 'Basque Parliament', 'name_native': 'Eusko Legebiltzarra', 'type': 'parliament', 'region': 'Basque Country', 'website': 'https://www.legebiltzarra.eus'},
        {'name': 'Basque Business Development Agency', 'name_native': 'SPRI', 'type': 'agency', 'region': 'Basque Country', 'website': 'https://www.spri.eus'},

        # Andalusia - largest by area and population
        {'name': 'Junta de Andalucía', 'name_native': 'Junta de Andalucía', 'type': 'executive', 'region': 'Andalusia', 'website': 'https://www.juntadeandalucia.es'},
        {'name': 'Parliament of Andalusia', 'name_native': 'Parlamento de Andalucía', 'type': 'parliament', 'region': 'Andalusia', 'website': 'https://www.parlamentodeandalucia.es'},
        {'name': 'Andalusia Trade', 'name_native': 'Extenda', 'type': 'agency', 'region': 'Andalusia', 'website': 'https://www.extenda.es'},

        # Valencian Community
        {'name': 'Generalitat Valenciana', 'name_native': 'Generalitat Valenciana', 'type': 'executive', 'region': 'Valencia', 'website': 'https://www.gva.es'},
        {'name': 'Valencian Parliament', 'name_native': 'Corts Valencianes', 'type': 'parliament', 'region': 'Valencia', 'website': 'https://www.cortsvalencianes.es'},
        {'name': 'Valencia Investment Agency', 'name_native': 'IVACE', 'type': 'agency', 'region': 'Valencia', 'website': 'https://www.ivace.es'},

        # Galicia
        {'name': 'Xunta de Galicia', 'name_native': 'Xunta de Galicia', 'type': 'executive', 'region': 'Galicia', 'website': 'https://www.xunta.gal'},
        {'name': 'Parliament of Galicia', 'name_native': 'Parlamento de Galicia', 'type': 'parliament', 'region': 'Galicia', 'website': 'https://www.parlamentodegalicia.es'},
        {'name': 'Galicia Innovation Agency', 'name_native': 'GAIN', 'type': 'agency', 'region': 'Galicia', 'website': 'https://gain.xunta.gal'},

        # Castile and León
        {'name': 'Junta de Castilla y León', 'name_native': 'Junta de Castilla y León', 'type': 'executive', 'region': 'Castile and León', 'website': 'https://www.jcyl.es'},
        {'name': 'Cortes of Castile and León', 'name_native': 'Cortes de Castilla y León', 'type': 'parliament', 'region': 'Castile and León', 'website': 'https://www.ccyl.es'},

        # Aragon
        {'name': 'Government of Aragon', 'name_native': 'Gobierno de Aragón', 'type': 'executive', 'region': 'Aragon', 'website': 'https://www.aragon.es'},
        {'name': 'Cortes of Aragon', 'name_native': 'Cortes de Aragón', 'type': 'parliament', 'region': 'Aragon', 'website': 'https://www.cortesaragon.es'},

        # Canary Islands
        {'name': 'Government of the Canary Islands', 'name_native': 'Gobierno de Canarias', 'type': 'executive', 'region': 'Canary Islands', 'website': 'https://www.gobiernodecanarias.org'},
        {'name': 'Parliament of the Canary Islands', 'name_native': 'Parlamento de Canarias', 'type': 'parliament', 'region': 'Canary Islands', 'website': 'https://www.parcan.es'},

        # Castile-La Mancha
        {'name': 'Junta de Castilla-La Mancha', 'name_native': 'Junta de Castilla-La Mancha', 'type': 'executive', 'region': 'Castile-La Mancha', 'website': 'https://www.castillalamancha.es'},
        {'name': 'Cortes of Castile-La Mancha', 'name_native': 'Cortes de Castilla-La Mancha', 'type': 'parliament', 'region': 'Castile-La Mancha', 'website': 'https://www.cortes-clm.es'},

        # Murcia
        {'name': 'Government of Murcia', 'name_native': 'Gobierno de la Región de Murcia', 'type': 'executive', 'region': 'Murcia', 'website': 'https://www.carm.es'},
        {'name': 'Regional Assembly of Murcia', 'name_native': 'Asamblea Regional de Murcia', 'type': 'parliament', 'region': 'Murcia', 'website': 'https://www.asambleamurcia.es'},

        # Asturias
        {'name': 'Principality of Asturias', 'name_native': 'Principado de Asturias', 'type': 'executive', 'region': 'Asturias', 'website': 'https://www.asturias.es'},
        {'name': 'General Assembly of Asturias', 'name_native': 'Junta General del Principado de Asturias', 'type': 'parliament', 'region': 'Asturias', 'website': 'https://www.jgpa.es'},

        # Balearic Islands
        {'name': 'Government of the Balearic Islands', 'name_native': 'Govern de les Illes Balears', 'type': 'executive', 'region': 'Balearic Islands', 'website': 'https://www.caib.es'},
        {'name': 'Parliament of the Balearic Islands', 'name_native': 'Parlament de les Illes Balears', 'type': 'parliament', 'region': 'Balearic Islands', 'website': 'https://www.parlamentib.es'}
    ]

    for inst in institutions:
        inst_id = generate_id(f"es_{inst['region'].lower().replace(' ', '_')}_subnational", inst['name'])
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
    print(f"\nTotal autonomous communities: {len(set([i['region'] for i in institutions]))}")
    print(f"Total institutions: {len(institutions)}")

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]
    print(f"Total subnational (all countries): {total_subnational}")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_spain_autonomous()
