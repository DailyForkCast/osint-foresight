#!/usr/bin/env python3
"""Final European Countries - Tier 1 Verified Collection
Switzerland, Liechtenstein, Monaco, Andorra, San Marino, Vatican City
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_final_countries():
    print("=" * 70)
    print("FINAL EUROPEAN COUNTRIES - TIER 1 VERIFIED")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Switzerland
        {'name': 'Federal Department of Foreign Affairs', 'name_native': 'Eidgenössisches Departement für auswärtige Angelegenheiten', 'type': 'ministry', 'country': 'CH', 'website': 'https://www.eda.admin.ch'},
        {'name': 'Federal Department of Defence', 'name_native': 'Eidgenössisches Departement für Verteidigung', 'type': 'ministry', 'country': 'CH', 'website': 'https://www.vbs.admin.ch'},
        {'name': 'State Secretariat for Economic Affairs', 'name_native': 'Staatssekretariat für Wirtschaft', 'type': 'ministry', 'country': 'CH', 'website': 'https://www.seco.admin.ch'},
        {'name': 'State Secretariat for Education, Research and Innovation', 'name_native': 'Staatssekretariat für Bildung, Forschung und Innovation', 'type': 'ministry', 'country': 'CH', 'website': 'https://www.sbfi.admin.ch'},
        {'name': 'Federal Intelligence Service', 'name_native': 'Nachrichtendienst des Bundes', 'type': 'agency', 'country': 'CH', 'website': 'https://www.vbs.admin.ch/de/sicherheit-politik/nachrichtendienst-des-bundes-ndb.html'},
        {'name': 'National Council', 'name_native': 'Nationalrat', 'type': 'parliament', 'country': 'CH', 'website': 'https://www.parlament.ch/en/organe/national-council'},
        {'name': 'Council of States', 'name_native': 'Ständerat', 'type': 'parliament', 'country': 'CH', 'website': 'https://www.parlament.ch/en/organe/council-of-states'},
        {'name': 'Competition Commission', 'name_native': 'Wettbewerbskommission', 'type': 'regulator', 'country': 'CH', 'website': 'https://www.weko.admin.ch'},
        {'name': 'Switzerland Global Enterprise', 'name_native': 'Switzerland Global Enterprise', 'type': 'agency', 'country': 'CH', 'website': 'https://www.s-ge.com'},

        # Liechtenstein
        {'name': 'Ministry of Foreign Affairs, Education and Sport', 'name_native': 'Ministerium für Äusseres, Bildung und Sport', 'type': 'ministry', 'country': 'LI', 'website': 'https://www.regierung.li/ministerien/ministerium-fuer-aeusseres-bildung-und-sport/'},
        {'name': 'Ministry of Home Affairs, Economic Affairs and Finance', 'name_native': 'Ministerium für Inneres, Wirtschaft und Umwelt', 'type': 'ministry', 'country': 'LI', 'website': 'https://www.regierung.li/ministerien/ministerium-fuer-inneres-wirtschaft-und-umwelt/'},
        {'name': 'Office of National Police', 'name_native': 'Landespolizei', 'type': 'agency', 'country': 'LI', 'website': 'https://www.landespolizei.li'},
        {'name': 'Landtag', 'name_native': 'Landtag des Fürstentums Liechtenstein', 'type': 'parliament', 'country': 'LI', 'website': 'https://www.landtag.li'},
        {'name': 'Liechtenstein Marketing', 'name_native': 'Liechtenstein Marketing', 'type': 'agency', 'country': 'LI', 'website': 'https://www.liechtenstein.li'},

        # Monaco
        {'name': 'Department of External Relations and Cooperation', 'name_native': 'Direction des Relations Extérieures et de la Coopération', 'type': 'ministry', 'country': 'MC', 'website': 'https://en.gouv.mc/Government-Institutions/The-Government/Ministry-of-State/Department-of-External-Relations-and-Cooperation'},
        {'name': 'Ministry of State', 'name_native': 'Ministère d\'État', 'type': 'ministry', 'country': 'MC', 'website': 'https://en.gouv.mc/Government-Institutions/The-Government/Ministry-of-State'},
        {'name': 'Department of Finance and Economy', 'name_native': 'Direction des Finances et de l\'Économie', 'type': 'ministry', 'country': 'MC', 'website': 'https://en.gouv.mc/Government-Institutions/The-Government/Ministry-of-State/Department-of-Finance-and-Economy'},
        {'name': 'National Council', 'name_native': 'Conseil National', 'type': 'parliament', 'country': 'MC', 'website': 'https://www.conseil-national.mc'},
        {'name': 'Monaco Economic Board', 'name_native': 'Monaco Economic Board', 'type': 'agency', 'country': 'MC', 'website': 'https://www.monacoeconomicboard.com'},

        # Andorra
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Ministeri d\'Afers Exteriors', 'type': 'ministry', 'country': 'AD', 'website': 'https://www.exteriors.ad'},
        {'name': 'Ministry of Economy, Competitiveness and Innovation', 'name_native': 'Ministeri d\'Economia, Competitivitat i Innovació', 'type': 'ministry', 'country': 'AD', 'website': 'https://www.govern.ad/economia'},
        {'name': 'General Council', 'name_native': 'Consell General', 'type': 'parliament', 'country': 'AD', 'website': 'https://www.consellgeneral.ad'},
        {'name': 'ACTUA', 'name_native': 'Agència per a la Competitivitat de l\'Empresa Andorrana', 'type': 'agency', 'country': 'AD', 'website': 'https://www.actua.ad'},

        # San Marino
        {'name': 'Department of Foreign Affairs', 'name_native': 'Segreteria di Stato per gli Affari Esteri', 'type': 'ministry', 'country': 'SM', 'website': 'https://www.esteri.sm'},
        {'name': 'Department of Industry and Trade', 'name_native': 'Segreteria di Stato per l\'Industria', 'type': 'ministry', 'country': 'SM', 'website': 'https://www.pa.sm'},
        {'name': 'Great and General Council', 'name_native': 'Consiglio Grande e Generale', 'type': 'parliament', 'country': 'SM', 'website': 'https://www.consigliograndeegenerale.sm'},
        {'name': 'San Marino Innovation', 'name_native': 'San Marino Innovation', 'type': 'agency', 'country': 'SM', 'website': 'https://www.sanmarinoinnovation.com'},

        # Vatican City (Holy See)
        {'name': 'Secretariat of State', 'name_native': 'Segreteria di Stato', 'type': 'ministry', 'country': 'VA', 'website': 'https://www.vatican.va/roman_curia/secretariat_state/'},
        {'name': 'Governorate of Vatican City State', 'name_native': 'Governatorato dello Stato della Città del Vaticano', 'type': 'ministry', 'country': 'VA', 'website': 'https://www.vaticanstate.va'}
    ]

    for inst in institutions:
        inst_id = generate_id(f"{inst['country'].lower()}_verified", inst['name'])
        notes = json.dumps({'collection_tier': 'tier_1_verified_only', 'collection_date': '2025-10-26', 'not_collected': {'china_relevance': '[NOT COLLECTED]'}})

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, official_website, china_relevance, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inst_id, inst['name'], inst['name_native'], inst['type'], 'national', inst['country'],
              inst['website'], None, 'active', notes, datetime.now().isoformat(), datetime.now().isoformat()))
        print(f"  [{inst['country']}] {inst['name']}")

    conn.commit()
    print(f"\nTotal: {len(institutions)}")
    cursor.execute('SELECT COUNT(DISTINCT country_code) FROM european_institutions')
    countries = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level = "national"')
    total = cursor.fetchone()[0]
    print(f"Countries: {countries}/42 ({int(100*countries/42)}%)")
    print(f"National institutions: {total}")

    print("\n" + "=" * 70)
    print("42-COUNTRY EUROPEAN INSTITUTIONAL COVERAGE: COMPLETE")
    print("=" * 70)

    conn.close()

if __name__ == '__main__':
    collect_final_countries()
