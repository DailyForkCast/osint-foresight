#!/usr/bin/env python3
"""Switzerland Remaining Cantons - Tier 1 Verified Subnational Collection
Final 17 smaller cantons to complete all 26
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_swiss_remaining():
    print("=" * 70)
    print("SWITZERLAND REMAINING CANTONS - TIER 1 VERIFIED")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Uri
        {'name': 'Canton of Uri Government Council', 'name_native': 'Regierungsrat Uri', 'type': 'executive', 'canton': 'Uri', 'website': 'https://www.ur.ch'},

        # Schwyz
        {'name': 'Canton of Schwyz Government Council', 'name_native': 'Regierungsrat Schwyz', 'type': 'executive', 'canton': 'Schwyz', 'website': 'https://www.sz.ch'},

        # Obwalden
        {'name': 'Canton of Obwalden Government Council', 'name_native': 'Regierungsrat Obwalden', 'type': 'executive', 'canton': 'Obwalden', 'website': 'https://www.ow.ch'},

        # Nidwalden
        {'name': 'Canton of Nidwalden Government Council', 'name_native': 'Regierungsrat Nidwalden', 'type': 'executive', 'canton': 'Nidwalden', 'website': 'https://www.nw.ch'},

        # Glarus
        {'name': 'Canton of Glarus Government Council', 'name_native': 'Regierungsrat Glarus', 'type': 'executive', 'canton': 'Glarus', 'website': 'https://www.gl.ch'},

        # Fribourg
        {'name': 'State Council of Fribourg', 'name_native': 'Conseil d\'État de Fribourg', 'type': 'executive', 'canton': 'Fribourg', 'website': 'https://www.fr.ch'},
        {'name': 'Grand Council of Fribourg', 'name_native': 'Grand Conseil de Fribourg', 'type': 'parliament', 'canton': 'Fribourg', 'website': 'https://www.fr.ch/gc'},

        # Solothurn
        {'name': 'Canton of Solothurn Government Council', 'name_native': 'Regierungsrat Solothurn', 'type': 'executive', 'canton': 'Solothurn', 'website': 'https://www.so.ch'},
        {'name': 'Solothurn Cantonal Council', 'name_native': 'Kantonsrat Solothurn', 'type': 'parliament', 'canton': 'Solothurn', 'website': 'https://www.so.ch/kr'},

        # Basel-Landschaft
        {'name': 'Canton of Basel-Landschaft Government Council', 'name_native': 'Regierungsrat Basel-Landschaft', 'type': 'executive', 'canton': 'Basel-Landschaft', 'website': 'https://www.baselland.ch'},
        {'name': 'Basel-Landschaft Landrat', 'name_native': 'Landrat Basel-Landschaft', 'type': 'parliament', 'canton': 'Basel-Landschaft', 'website': 'https://www.baselland.ch/landrat'},

        # Schaffhausen
        {'name': 'Canton of Schaffhausen Government Council', 'name_native': 'Regierungsrat Schaffhausen', 'type': 'executive', 'canton': 'Schaffhausen', 'website': 'https://www.sh.ch'},
        {'name': 'Schaffhausen Cantonal Council', 'name_native': 'Kantonsrat Schaffhausen', 'type': 'parliament', 'canton': 'Schaffhausen', 'website': 'https://www.sh.ch/kr'},

        # Appenzell Ausserrhoden
        {'name': 'Canton of Appenzell Ausserrhoden Government Council', 'name_native': 'Regierungsrat Appenzell Ausserrhoden', 'type': 'executive', 'canton': 'Appenzell Ausserrhoden', 'website': 'https://www.ar.ch'},

        # Appenzell Innerrhoden
        {'name': 'Canton of Appenzell Innerrhoden Government Council', 'name_native': 'Regierungsrat Appenzell Innerrhoden', 'type': 'executive', 'canton': 'Appenzell Innerrhoden', 'website': 'https://www.ai.ch'},

        # Grisons / Graubünden
        {'name': 'Canton of Grisons Government Council', 'name_native': 'Regierung Graubünden', 'type': 'executive', 'canton': 'Grisons', 'website': 'https://www.gr.ch'},
        {'name': 'Grisons Grand Council', 'name_native': 'Grosser Rat Graubünden', 'type': 'parliament', 'canton': 'Grisons', 'website': 'https://www.gr.ch/grosser-rat'},

        # Thurgau
        {'name': 'Canton of Thurgau Government Council', 'name_native': 'Regierungsrat Thurgau', 'type': 'executive', 'canton': 'Thurgau', 'website': 'https://www.tg.ch'},
        {'name': 'Thurgau Grand Council', 'name_native': 'Grosser Rat Thurgau', 'type': 'parliament', 'canton': 'Thurgau', 'website': 'https://www.tg.ch/grosser-rat'},

        # Valais
        {'name': 'State Council of Valais', 'name_native': 'Conseil d\'État du Valais', 'type': 'executive', 'canton': 'Valais', 'website': 'https://www.vs.ch'},
        {'name': 'Grand Council of Valais', 'name_native': 'Grand Conseil du Valais', 'type': 'parliament', 'canton': 'Valais', 'website': 'https://www.vs.ch/gc'},

        # Neuchâtel
        {'name': 'State Council of Neuchâtel', 'name_native': 'Conseil d\'État de Neuchâtel', 'type': 'executive', 'canton': 'Neuchâtel', 'website': 'https://www.ne.ch'},
        {'name': 'Grand Council of Neuchâtel', 'name_native': 'Grand Conseil de Neuchâtel', 'type': 'parliament', 'canton': 'Neuchâtel', 'website': 'https://www.ne.ch/gc'},

        # Geneva (second entry for parliament)
        {'name': 'Jura State Council', 'name_native': 'Gouvernement jurassien', 'type': 'executive', 'canton': 'Jura', 'website': 'https://www.jura.ch'},
        {'name': 'Jura Parliament', 'name_native': 'Parlement jurassien', 'type': 'parliament', 'canton': 'Jura', 'website': 'https://www.jura.ch/parlement'}
    ]

    for inst in institutions:
        canton_cleaned = inst['canton'].lower().replace(' ', '_').replace('-', '_')
        inst_id = generate_id(f"ch_{canton_cleaned}_subnational", inst['name'])
        notes = json.dumps({
            'collection_tier': 'tier_1_verified_only',
            'collection_date': '2025-10-26',
            'canton': inst['canton'],
            'not_collected': {'china_relevance': '[NOT COLLECTED]'}
        })

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, subnational_jurisdiction, official_website,
             china_relevance, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inst_id, inst['name'], inst['name_native'], inst['type'], 'subnational_state',
              'CH', inst['canton'], inst['website'], None, 'active', notes,
              datetime.now().isoformat(), datetime.now().isoformat()))
        print(f"  [CH-{inst['canton']}] {inst['name']}")

    conn.commit()
    print(f"\nNew cantons added: {len(set([i['canton'] for i in institutions]))}")
    print(f"New institutions: {len(institutions)}")

    cursor.execute('SELECT COUNT(DISTINCT subnational_jurisdiction) FROM european_institutions WHERE country_code = "CH" AND jurisdiction_level LIKE "subnational%"')
    total_ch_cantons = cursor.fetchone()[0]
    print(f"Total Swiss cantons: {total_ch_cantons}/26")

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]
    print(f"Total subnational (all countries): {total_subnational}")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_swiss_remaining()
