#!/usr/bin/env python3
"""Baltic States - Tier 1 Verified Collection
Estonia, Latvia, Lithuania
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_baltics():
    print("=" * 70)
    print("BALTIC STATES - TIER 1 VERIFIED")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Estonia
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Välisministeerium', 'type': 'ministry', 'country': 'EE', 'website': 'https://vm.ee'},
        {'name': 'Ministry of Defence', 'name_native': 'Kaitseministeerium', 'type': 'ministry', 'country': 'EE', 'website': 'https://www.kaitseministeerium.ee'},
        {'name': 'Ministry of Economic Affairs and Communications', 'name_native': 'Majandus- ja kommunikatsiooniministeerium', 'type': 'ministry', 'country': 'EE', 'website': 'https://www.mkm.ee'},
        {'name': 'Ministry of Education and Research', 'name_native': 'Haridus- ja teadusministeerium', 'type': 'ministry', 'country': 'EE', 'website': 'https://www.hm.ee'},
        {'name': 'Estonian Foreign Intelligence Service', 'name_native': 'Välisluureamet', 'type': 'agency', 'country': 'EE', 'website': 'https://www.valisluureamet.ee'},
        {'name': 'Estonian Internal Security Service', 'name_native': 'Kaitsepolitseiamet', 'type': 'agency', 'country': 'EE', 'website': 'https://www.kapo.ee'},
        {'name': 'Riigikogu', 'name_native': 'Riigikogu', 'type': 'parliament', 'country': 'EE', 'website': 'https://www.riigikogu.ee'},
        {'name': 'Competition Authority', 'name_native': 'Konkurentsiamet', 'type': 'regulator', 'country': 'EE', 'website': 'https://www.konkurentsiamet.ee'},
        {'name': 'Enterprise Estonia', 'name_native': 'Ettevõtluse Arendamise Sihtasutus', 'type': 'agency', 'country': 'EE', 'website': 'https://www.eas.ee'},

        # Latvia
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Ārlietu ministrija', 'type': 'ministry', 'country': 'LV', 'website': 'https://www.mfa.gov.lv'},
        {'name': 'Ministry of Defence', 'name_native': 'Aizsardzības ministrija', 'type': 'ministry', 'country': 'LV', 'website': 'https://www.mod.gov.lv'},
        {'name': 'Ministry of Economics', 'name_native': 'Ekonomikas ministrija', 'type': 'ministry', 'country': 'LV', 'website': 'https://www.em.gov.lv'},
        {'name': 'Ministry of Education and Science', 'name_native': 'Izglītības un zinātnes ministrija', 'type': 'ministry', 'country': 'LV', 'website': 'https://www.izm.gov.lv'},
        {'name': 'Constitution Protection Bureau', 'name_native': 'Satversmes aizsardzības birojs', 'type': 'agency', 'country': 'LV', 'website': 'https://www.sab.gov.lv'},
        {'name': 'Saeima', 'name_native': 'Saeima', 'type': 'parliament', 'country': 'LV', 'website': 'https://www.saeima.lv'},
        {'name': 'Competition Council', 'name_native': 'Konkurences padome', 'type': 'regulator', 'country': 'LV', 'website': 'https://www.kp.gov.lv'},
        {'name': 'Investment and Development Agency of Latvia', 'name_native': 'Latvijas Investīciju un attīstības aģentūra', 'type': 'agency', 'country': 'LV', 'website': 'https://www.liaa.gov.lv'},

        # Lithuania
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Užsienio reikalų ministerija', 'type': 'ministry', 'country': 'LT', 'website': 'https://www.urm.lt'},
        {'name': 'Ministry of National Defence', 'name_native': 'Krašto apsaugos ministerija', 'type': 'ministry', 'country': 'LT', 'website': 'https://kam.lt'},
        {'name': 'Ministry of Economy and Innovation', 'name_native': 'Ekonomikos ir inovacijų ministerija', 'type': 'ministry', 'country': 'LT', 'website': 'https://eimin.lrv.lt'},
        {'name': 'Ministry of Education, Science and Sport', 'name_native': 'Švietimo, mokslo ir sporto ministerija', 'type': 'ministry', 'country': 'LT', 'website': 'https://www.smm.lt'},
        {'name': 'State Security Department', 'name_native': 'Valstybės saugumo departamentas', 'type': 'agency', 'country': 'LT', 'website': 'https://www.vsd.lt'},
        {'name': 'Second Investigation Department', 'name_native': 'Antrasis operatyvinių tarnybų departamentas', 'type': 'agency', 'country': 'LT', 'website': 'https://www.aotd.lt'},
        {'name': 'Seimas', 'name_native': 'Seimas', 'type': 'parliament', 'country': 'LT', 'website': 'https://www.lrs.lt'},
        {'name': 'Competition Council', 'name_native': 'Konkurencijos taryba', 'type': 'regulator', 'country': 'LT', 'website': 'https://kt.gov.lt'},
        {'name': 'Invest Lithuania', 'name_native': 'Investuok Lietuvoje', 'type': 'agency', 'country': 'LT', 'website': 'https://investlithuania.com'}
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
    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_baltics()
