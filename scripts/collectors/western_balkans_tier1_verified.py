#!/usr/bin/env python3
"""Western Balkans - Tier 1 Verified Collection
Serbia, Albania, North Macedonia, Bosnia and Herzegovina, Montenegro, Kosovo
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_western_balkans():
    print("=" * 70)
    print("WESTERN BALKANS - TIER 1 VERIFIED")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Serbia
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Министарство спољних послова', 'type': 'ministry', 'country': 'RS', 'website': 'https://www.mfa.gov.rs'},
        {'name': 'Ministry of Defence', 'name_native': 'Министарство одбране', 'type': 'ministry', 'country': 'RS', 'website': 'https://www.mod.gov.rs'},
        {'name': 'Ministry of Economy', 'name_native': 'Министарство привреде', 'type': 'ministry', 'country': 'RS', 'website': 'https://privreda.gov.rs'},
        {'name': 'Ministry of Education, Science and Technological Development', 'name_native': 'Министарство просвете, науке и технолошког развоја', 'type': 'ministry', 'country': 'RS', 'website': 'https://www.mpn.gov.rs'},
        {'name': 'Security Intelligence Agency', 'name_native': 'Безбедносно-информативна агенција', 'type': 'agency', 'country': 'RS', 'website': 'https://www.bia.gov.rs'},
        {'name': 'National Assembly', 'name_native': 'Народна скупштина', 'type': 'parliament', 'country': 'RS', 'website': 'https://www.parlament.gov.rs'},
        {'name': 'Commission for Protection of Competition', 'name_native': 'Комисија за заштиту конкуренције', 'type': 'regulator', 'country': 'RS', 'website': 'https://www.kzk.gov.rs'},
        {'name': 'Development Agency of Serbia', 'name_native': 'Развојна агенција Србије', 'type': 'agency', 'country': 'RS', 'website': 'https://ras.gov.rs'},

        # Albania
        {'name': 'Ministry for Europe and Foreign Affairs', 'name_native': 'Ministria për Europën dhe Punët e Jashtme', 'type': 'ministry', 'country': 'AL', 'website': 'https://punetejashtme.gov.al'},
        {'name': 'Ministry of Defence', 'name_native': 'Ministria e Mbrojtjes', 'type': 'ministry', 'country': 'AL', 'website': 'https://mod.gov.al'},
        {'name': 'Ministry of Finance and Economy', 'name_native': 'Ministria e Financave dhe Ekonomisë', 'type': 'ministry', 'country': 'AL', 'website': 'https://financa.gov.al'},
        {'name': 'Ministry of Education, Sport and Youth', 'name_native': 'Ministria e Arsimit, Sportit dhe Rinisë', 'type': 'ministry', 'country': 'AL', 'website': 'https://arsimi.gov.al'},
        {'name': 'State Intelligence Service', 'name_native': 'Shërbimi Informativ i Shtetit', 'type': 'agency', 'country': 'AL', 'website': 'https://www.shish.gov.al'},
        {'name': 'Parliament of Albania', 'name_native': 'Kuvendi i Shqipërisë', 'type': 'parliament', 'country': 'AL', 'website': 'https://www.parlament.al'},
        {'name': 'Albanian Competition Authority', 'name_native': 'Autoriteti i Konkurrencës', 'type': 'regulator', 'country': 'AL', 'website': 'https://caa.gov.al'},
        {'name': 'Albanian Investment Development Agency', 'name_native': 'Agjencia Shqiptare e Zhvillimit të Investimeve', 'type': 'agency', 'country': 'AL', 'website': 'https://aida.gov.al'},

        # North Macedonia
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Министерство за надворешни работи', 'type': 'ministry', 'country': 'MK', 'website': 'https://www.mfa.gov.mk'},
        {'name': 'Ministry of Defence', 'name_native': 'Министерство за одбрана', 'type': 'ministry', 'country': 'MK', 'website': 'https://www.mod.gov.mk'},
        {'name': 'Ministry of Economy', 'name_native': 'Министерство за економија', 'type': 'ministry', 'country': 'MK', 'website': 'https://www.economy.gov.mk'},
        {'name': 'Ministry of Education and Science', 'name_native': 'Министерство за образование и наука', 'type': 'ministry', 'country': 'MK', 'website': 'https://mon.gov.mk'},
        {'name': 'Intelligence Agency', 'name_native': 'Агенција за разузнавање', 'type': 'agency', 'country': 'MK', 'website': 'https://www.arm.gov.mk'},
        {'name': 'Assembly', 'name_native': 'Собрание', 'type': 'parliament', 'country': 'MK', 'website': 'https://www.sobranie.mk'},
        {'name': 'Commission for Protection of Competition', 'name_native': 'Комисија за заштита на конкуренцијата', 'type': 'regulator', 'country': 'MK', 'website': 'https://kzk.gov.mk'},
        {'name': 'Invest North Macedonia', 'name_native': 'Инвестирај во Северна Македонија', 'type': 'agency', 'country': 'MK', 'website': 'https://investnorthmacedonia.gov.mk'},

        # Bosnia and Herzegovina
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Ministarstvo vanjskih poslova', 'type': 'ministry', 'country': 'BA', 'website': 'https://www.mvp.gov.ba'},
        {'name': 'Ministry of Defence', 'name_native': 'Ministarstvo odbrane', 'type': 'ministry', 'country': 'BA', 'website': 'https://www.mod.gov.ba'},
        {'name': 'Ministry of Foreign Trade and Economic Relations', 'name_native': 'Ministarstvo vanjske trgovine i ekonomskih odnosa', 'type': 'ministry', 'country': 'BA', 'website': 'https://www.mvteo.gov.ba'},
        {'name': 'Intelligence-Security Agency', 'name_native': 'Obavještajno-sigurnosna agencija', 'type': 'agency', 'country': 'BA', 'website': 'https://www.osa.gov.ba'},
        {'name': 'Parliamentary Assembly', 'name_native': 'Parlamentarna skupština', 'type': 'parliament', 'country': 'BA', 'website': 'https://www.parlament.ba'},
        {'name': 'Competition Council', 'name_native': 'Vijeće konkurencije', 'type': 'regulator', 'country': 'BA', 'website': 'https://bihkonk.gov.ba'},
        {'name': 'Foreign Investment Promotion Agency', 'name_native': 'Agencija za promociju stranih investicija', 'type': 'agency', 'country': 'BA', 'website': 'https://www.fipa.gov.ba'},

        # Montenegro
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Ministarstvo vanjskih poslova', 'type': 'ministry', 'country': 'ME', 'website': 'https://www.mvp.gov.me'},
        {'name': 'Ministry of Defence', 'name_native': 'Ministarstvo odbrane', 'type': 'ministry', 'country': 'ME', 'website': 'https://www.mod.gov.me'},
        {'name': 'Ministry of Economic Development', 'name_native': 'Ministarstvo ekonomskog razvoja', 'type': 'ministry', 'country': 'ME', 'website': 'https://www.mek.gov.me'},
        {'name': 'Ministry of Education, Science, Culture and Sports', 'name_native': 'Ministarstvo prosvjete, nauke, kulture i sporta', 'type': 'ministry', 'country': 'ME', 'website': 'https://www.gov.me/mpin'},
        {'name': 'National Security Agency', 'name_native': 'Agencija za nacionalnu bezbjednost', 'type': 'agency', 'country': 'ME', 'website': 'https://www.anb.me'},
        {'name': 'Parliament of Montenegro', 'name_native': 'Skupština Crne Gore', 'type': 'parliament', 'country': 'ME', 'website': 'https://www.skupstina.me'},
        {'name': 'Agency for Protection of Competition', 'name_native': 'Agencija za zaštitu konkurencije', 'type': 'regulator', 'country': 'ME', 'website': 'https://www.azzk.me'},
        {'name': 'Investment and Development Fund', 'name_native': 'Investiciono-razvojni fond', 'type': 'agency', 'country': 'ME', 'website': 'https://www.irfcg.me'},

        # Kosovo
        {'name': 'Ministry of Foreign Affairs and Diaspora', 'name_native': 'Ministria e Punëve të Jashtme dhe Diasporës', 'type': 'ministry', 'country': 'XK', 'website': 'https://www.mfa-ks.net'},
        {'name': 'Ministry of Defence', 'name_native': 'Ministria e Mbrojtjes', 'type': 'ministry', 'country': 'XK', 'website': 'https://mod.rks-gov.net'},
        {'name': 'Ministry of Industry, Entrepreneurship and Trade', 'name_native': 'Ministria e Industrisë, Ndërmarrësisë dhe Tregtisë', 'type': 'ministry', 'country': 'XK', 'website': 'https://mti.rks-gov.net'},
        {'name': 'Ministry of Education, Science, Technology and Innovation', 'name_native': 'Ministria e Arsimit, Shkencës, Teknologjisë dhe Inovacionit', 'type': 'ministry', 'country': 'XK', 'website': 'https://masht.rks-gov.net'},
        {'name': 'Kosovo Intelligence Agency', 'name_native': 'Agjencia Kosovare e Inteligjencës', 'type': 'agency', 'country': 'XK', 'website': 'https://aki.rks-gov.net'},
        {'name': 'Assembly of Kosovo', 'name_native': 'Kuvendi i Kosovës', 'type': 'parliament', 'country': 'XK', 'website': 'https://www.kuvendikosoves.org'},
        {'name': 'Kosovo Competition Authority', 'name_native': 'Autoriteti i Konkurrencës së Kosovës', 'type': 'regulator', 'country': 'XK', 'website': 'https://ak.rks-gov.net'},
        {'name': 'Kosovo Investment and Enterprise Support Agency', 'name_native': 'Agjencia e Kosovës për Investime dhe Mbështetje të Ndërmarrjeve', 'type': 'agency', 'country': 'XK', 'website': 'https://kiesa.rks-gov.net'}
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
    collect_western_balkans()
