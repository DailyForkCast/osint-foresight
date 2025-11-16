#!/usr/bin/env python3
"""Nordic Countries - Tier 1 Verified Collection
Denmark, Finland, Norway, Iceland
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_nordic():
    print("=" * 70)
    print("NORDIC COUNTRIES - TIER 1 VERIFIED")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Denmark
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Udenrigsministeriet', 'type': 'ministry', 'country': 'DK', 'website': 'https://um.dk'},
        {'name': 'Ministry of Defence', 'name_native': 'Forsvarsministeriet', 'type': 'ministry', 'country': 'DK', 'website': 'https://www.fmn.dk'},
        {'name': 'Ministry of Industry, Business and Financial Affairs', 'name_native': 'Erhvervsministeriet', 'type': 'ministry', 'country': 'DK', 'website': 'https://em.dk'},
        {'name': 'Ministry of Higher Education and Science', 'name_native': 'Uddannelses- og Forskningsministeriet', 'type': 'ministry', 'country': 'DK', 'website': 'https://ufm.dk'},
        {'name': 'Danish Defence Intelligence Service', 'name_native': 'Forsvarets Efterretningstjeneste', 'type': 'agency', 'country': 'DK', 'website': 'https://www.fe-ddis.dk'},
        {'name': 'Danish Security and Intelligence Service', 'name_native': 'Politiets Efterretningstjeneste', 'type': 'agency', 'country': 'DK', 'website': 'https://www.pet.dk'},
        {'name': 'Folketing', 'name_native': 'Folketinget', 'type': 'parliament', 'country': 'DK', 'website': 'https://www.ft.dk'},
        {'name': 'Danish Competition and Consumer Authority', 'name_native': 'Konkurrence- og Forbrugerstyrelsen', 'type': 'regulator', 'country': 'DK', 'website': 'https://www.kfst.dk'},
        {'name': 'Invest in Denmark', 'name_native': 'Invest in Denmark', 'type': 'agency', 'country': 'DK', 'website': 'https://investindk.com'},

        # Finland
        {'name': 'Ministry for Foreign Affairs', 'name_native': 'Ulkoministeriö', 'type': 'ministry', 'country': 'FI', 'website': 'https://um.fi'},
        {'name': 'Ministry of Defence', 'name_native': 'Puolustusministeriö', 'type': 'ministry', 'country': 'FI', 'website': 'https://www.defmin.fi'},
        {'name': 'Ministry of Economic Affairs and Employment', 'name_native': 'Työ- ja elinkeinoministeriö', 'type': 'ministry', 'country': 'FI', 'website': 'https://tem.fi'},
        {'name': 'Ministry of Education and Culture', 'name_native': 'Opetus- ja kulttuuriministeriö', 'type': 'ministry', 'country': 'FI', 'website': 'https://okm.fi'},
        {'name': 'Finnish Security Intelligence Service', 'name_native': 'Suojelupoliisi', 'type': 'agency', 'country': 'FI', 'website': 'https://www.supo.fi'},
        {'name': 'Finnish Defence Intelligence Agency', 'name_native': 'Puolustusvoimien tiedustelulaitos', 'type': 'agency', 'country': 'FI', 'website': 'https://puolustusvoimat.fi/tiedustelulaitos'},
        {'name': 'Parliament of Finland', 'name_native': 'Suomen eduskunta', 'type': 'parliament', 'country': 'FI', 'website': 'https://www.eduskunta.fi'},
        {'name': 'Finnish Competition and Consumer Authority', 'name_native': 'Kilpailu- ja kuluttajavirasto', 'type': 'regulator', 'country': 'FI', 'website': 'https://www.kkv.fi'},
        {'name': 'Business Finland', 'name_native': 'Business Finland', 'type': 'agency', 'country': 'FI', 'website': 'https://www.businessfinland.fi'},

        # Norway
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Utenriksdepartementet', 'type': 'ministry', 'country': 'NO', 'website': 'https://www.regjeringen.no/en/dep/ud/'},
        {'name': 'Ministry of Defence', 'name_native': 'Forsvarsdepartementet', 'type': 'ministry', 'country': 'NO', 'website': 'https://www.regjeringen.no/en/dep/fd/'},
        {'name': 'Ministry of Trade, Industry and Fisheries', 'name_native': 'Nærings- og fiskeridepartementet', 'type': 'ministry', 'country': 'NO', 'website': 'https://www.regjeringen.no/en/dep/nfd/'},
        {'name': 'Ministry of Education and Research', 'name_native': 'Kunnskapsdepartementet', 'type': 'ministry', 'country': 'NO', 'website': 'https://www.regjeringen.no/en/dep/kd/'},
        {'name': 'Norwegian Intelligence Service', 'name_native': 'Etterretningstjenesten', 'type': 'agency', 'country': 'NO', 'website': 'https://www.etterretningstjenesten.no'},
        {'name': 'Norwegian Police Security Service', 'name_native': 'Politiets sikkerhetstjeneste', 'type': 'agency', 'country': 'NO', 'website': 'https://www.pst.no'},
        {'name': 'Storting', 'name_native': 'Stortinget', 'type': 'parliament', 'country': 'NO', 'website': 'https://www.stortinget.no'},
        {'name': 'Norwegian Competition Authority', 'name_native': 'Konkurransetilsynet', 'type': 'regulator', 'country': 'NO', 'website': 'https://www.konkurransetilsynet.no'},
        {'name': 'Innovation Norway', 'name_native': 'Innovasjon Norge', 'type': 'agency', 'country': 'NO', 'website': 'https://www.innovasjonnorge.no'},

        # Iceland
        {'name': 'Ministry for Foreign Affairs', 'name_native': 'Utanríkisráðuneytið', 'type': 'ministry', 'country': 'IS', 'website': 'https://www.government.is/ministries/ministry-for-foreign-affairs/'},
        {'name': 'Prime Minister\'s Office', 'name_native': 'Forsætisráðuneytið', 'type': 'ministry', 'country': 'IS', 'website': 'https://www.government.is/ministries/prime-ministers-office/'},
        {'name': 'Ministry of Industries and Innovation', 'name_native': 'Atvinnuvega- og nýsköpunarráðuneytið', 'type': 'ministry', 'country': 'IS', 'website': 'https://www.government.is/ministries/ministry-of-industries-and-innovation/'},
        {'name': 'Ministry of Higher Education, Science and Innovation', 'name_native': 'Mennta- og menningarmálaráðuneytið', 'type': 'ministry', 'country': 'IS', 'website': 'https://www.government.is/ministries/ministry-of-higher-education-science-and-innovation/'},
        {'name': 'National Security Unit', 'name_native': 'Öryggissvið ríkislögreglustjóra', 'type': 'agency', 'country': 'IS', 'website': 'https://www.logreglan.is'},
        {'name': 'Althing', 'name_native': 'Alþingi', 'type': 'parliament', 'country': 'IS', 'website': 'https://www.althingi.is'},
        {'name': 'Icelandic Competition Authority', 'name_native': 'Samkeppniseftirlitið', 'type': 'regulator', 'country': 'IS', 'website': 'https://www.samkeppni.is'},
        {'name': 'Promote Iceland', 'name_native': 'Íslandsstofa', 'type': 'agency', 'country': 'IS', 'website': 'https://www.islandsstofa.is'}
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
    collect_nordic()
