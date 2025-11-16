#!/usr/bin/env python3
"""Switzerland Cantons - Tier 1 Verified Subnational Collection
Priority: Major cantons with international/economic significance
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_swiss_cantons():
    print("=" * 70)
    print("SWITZERLAND CANTONS - TIER 1 VERIFIED SUBNATIONAL")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Zurich (economic/financial center)
        {'name': 'Canton of Zurich Executive Council', 'name_native': 'Regierungsrat des Kantons Zürich', 'type': 'executive', 'canton': 'Zurich', 'website': 'https://www.zh.ch/de/regierungsrat.html'},
        {'name': 'Canton of Zurich Cantonal Council', 'name_native': 'Kantonsrat Zürich', 'type': 'parliament', 'canton': 'Zurich', 'website': 'https://www.kantonsrat.zh.ch'},
        {'name': 'Greater Zurich Area AG', 'name_native': 'Greater Zurich Area AG', 'type': 'agency', 'canton': 'Zurich', 'website': 'https://www.greaterzuricharea.com'},

        # Geneva (international organizations, diplomacy)
        {'name': 'Canton of Geneva State Council', 'name_native': 'Conseil d\'État de Genève', 'type': 'executive', 'canton': 'Geneva', 'website': 'https://www.ge.ch/conseil-etat'},
        {'name': 'Geneva Grand Council', 'name_native': 'Grand Conseil de Genève', 'type': 'parliament', 'canton': 'Geneva', 'website': 'https://www.ge.ch/grand-conseil'},
        {'name': 'Geneva Economic Promotion', 'name_native': 'Office de promotion économique', 'type': 'agency', 'canton': 'Geneva', 'website': 'https://www.ge.ch/office-promotion-economique'},

        # Bern (capital)
        {'name': 'Canton of Bern Executive Council', 'name_native': 'Regierungsrat des Kantons Bern', 'type': 'executive', 'canton': 'Bern', 'website': 'https://www.be.ch/regierungsrat'},
        {'name': 'Bern Grand Council', 'name_native': 'Grosser Rat des Kantons Bern', 'type': 'parliament', 'canton': 'Bern', 'website': 'https://www.gr.be.ch'},
        {'name': 'Bern Economic Development Agency', 'name_native': 'Wirtschaftsförderung Kanton Bern', 'type': 'agency', 'canton': 'Bern', 'website': 'https://www.vol.be.ch/vol/de/index/wirtschaft.html'},

        # Basel-Stadt (pharma/chemicals)
        {'name': 'Canton of Basel-Stadt Government Council', 'name_native': 'Regierungsrat Basel-Stadt', 'type': 'executive', 'canton': 'Basel-Stadt', 'website': 'https://www.bs.ch/regierungsrat'},
        {'name': 'Basel Grand Council', 'name_native': 'Grosser Rat Basel-Stadt', 'type': 'parliament', 'canton': 'Basel-Stadt', 'website': 'https://www.grosserrat.bs.ch'},
        {'name': 'Basel Area Business & Innovation', 'name_native': 'BaselArea', 'type': 'agency', 'canton': 'Basel-Stadt', 'website': 'https://www.baselarea.swiss'},

        # Vaud (Lausanne, international sports)
        {'name': 'Canton of Vaud State Council', 'name_native': 'Conseil d\'État vaudois', 'type': 'executive', 'canton': 'Vaud', 'website': 'https://www.vd.ch/conseil-etat'},
        {'name': 'Vaud Grand Council', 'name_native': 'Grand Conseil vaudois', 'type': 'parliament', 'canton': 'Vaud', 'website': 'https://www.vd.ch/grand-conseil'},
        {'name': 'Vaud Economic Promotion', 'name_native': 'Promotion économique vaudoise', 'type': 'agency', 'canton': 'Vaud', 'website': 'https://www.vaud.ch/economie'},

        # Ticino (Italian-speaking, bordering Italy)
        {'name': 'Canton of Ticino State Council', 'name_native': 'Consiglio di Stato del Canton Ticino', 'type': 'executive', 'canton': 'Ticino', 'website': 'https://www4.ti.ch/index.php?id=82'},
        {'name': 'Ticino Grand Council', 'name_native': 'Gran Consiglio della Repubblica e Cantone Ticino', 'type': 'parliament', 'canton': 'Ticino', 'website': 'https://www3.ti.ch/CAN/GranConsiglio/'},
        {'name': 'Ticino Economic Development', 'name_native': 'Organizzazione per lo sviluppo economico del Cantone Ticino', 'type': 'agency', 'canton': 'Ticino', 'website': 'https://www.ti.ch/economia'},

        # Zug (low-tax corporate haven)
        {'name': 'Canton of Zug Government Council', 'name_native': 'Regierungsrat des Kantons Zug', 'type': 'executive', 'canton': 'Zug', 'website': 'https://www.zg.ch/regierungsrat'},
        {'name': 'Zug Cantonal Council', 'name_native': 'Kantonsrat Zug', 'type': 'parliament', 'canton': 'Zug', 'website': 'https://www.zg.ch/kantonsrat'},
        {'name': 'Zug Economic Development', 'name_native': 'Standortförderung Zug', 'type': 'agency', 'canton': 'Zug', 'website': 'https://www.zg.ch/wirtschaft'},

        # Aargau (industrial canton)
        {'name': 'Canton of Aargau Government Council', 'name_native': 'Regierungsrat Aargau', 'type': 'executive', 'canton': 'Aargau', 'website': 'https://www.ag.ch/regierungsrat'},
        {'name': 'Aargau Grand Council', 'name_native': 'Grosser Rat des Kantons Aargau', 'type': 'parliament', 'canton': 'Aargau', 'website': 'https://www.ag.ch/grossrat'},

        # St. Gallen (eastern Switzerland)
        {'name': 'Canton of St. Gallen Government Council', 'name_native': 'Regierungsrat des Kantons St.Gallen', 'type': 'executive', 'canton': 'St. Gallen', 'website': 'https://www.sg.ch/regierung.html'},
        {'name': 'St. Gallen Cantonal Council', 'name_native': 'Kantonsrat St.Gallen', 'type': 'parliament', 'canton': 'St. Gallen', 'website': 'https://www.ratsinfo.sg.ch'}
    ]

    for inst in institutions:
        inst_id = generate_id(f"ch_{inst['canton'].lower()}_subnational", inst['name'])
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
    print(f"\nTotal Swiss cantons: {len(set([i['canton'] for i in institutions]))}")
    print(f"Total institutions: {len(institutions)}")

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]
    print(f"Total subnational (all countries): {total_subnational}")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_swiss_cantons()
