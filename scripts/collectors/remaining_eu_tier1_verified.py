#!/usr/bin/env python3
"""Remaining EU Countries - Tier 1 Verified Collection
Ireland, Croatia, Slovenia, Cyprus, Malta, Luxembourg
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_remaining_eu():
    print("=" * 70)
    print("REMAINING EU COUNTRIES - TIER 1 VERIFIED")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Ireland
        {'name': 'Department of Foreign Affairs', 'name_native': 'An Roinn Gnóthaí Eachtracha', 'type': 'ministry', 'country': 'IE', 'website': 'https://www.dfa.ie'},
        {'name': 'Department of Defence', 'name_native': 'An Roinn Cosanta', 'type': 'ministry', 'country': 'IE', 'website': 'https://www.gov.ie/en/organisation/department-of-defence/'},
        {'name': 'Department of Enterprise, Trade and Employment', 'name_native': 'An Roinn Fiontar, Trádála agus Fostaíochta', 'type': 'ministry', 'country': 'IE', 'website': 'https://www.gov.ie/en/organisation/department-of-enterprise-trade-and-employment/'},
        {'name': 'Department of Further and Higher Education', 'name_native': 'An Roinn Breisoideachais agus Ardoideachais', 'type': 'ministry', 'country': 'IE', 'website': 'https://www.gov.ie/en/organisation/department-of-further-and-higher-education-research-innovation-and-science/'},
        {'name': 'Directorate of Military Intelligence', 'name_native': 'Stiúrthóireacht na bhFaisnéise Míleata', 'type': 'agency', 'country': 'IE', 'website': 'https://www.military.ie'},
        {'name': 'National Cyber Security Centre', 'name_native': 'Lárionad Náisiúnta um Chibearshlándáil', 'type': 'agency', 'country': 'IE', 'website': 'https://www.ncsc.gov.ie'},
        {'name': 'Dáil Éireann', 'name_native': 'Dáil Éireann', 'type': 'parliament', 'country': 'IE', 'website': 'https://www.oireachtas.ie/en/debates/dail/'},
        {'name': 'Competition and Consumer Protection Commission', 'name_native': 'An Coimisiún um Iomaíocht agus Cosaint Tomhaltóirí', 'type': 'regulator', 'country': 'IE', 'website': 'https://www.ccpc.ie'},
        {'name': 'IDA Ireland', 'name_native': 'IDA Ireland', 'type': 'agency', 'country': 'IE', 'website': 'https://www.idaireland.com'},

        # Croatia
        {'name': 'Ministry of Foreign and European Affairs', 'name_native': 'Ministarstvo vanjskih i europskih poslova', 'type': 'ministry', 'country': 'HR', 'website': 'https://mvep.gov.hr'},
        {'name': 'Ministry of Defence', 'name_native': 'Ministarstvo obrane', 'type': 'ministry', 'country': 'HR', 'website': 'https://morh.gov.hr'},
        {'name': 'Ministry of Economy and Sustainable Development', 'name_native': 'Ministarstvo gospodarstva i održivog razvoja', 'type': 'ministry', 'country': 'HR', 'website': 'https://mingor.gov.hr'},
        {'name': 'Ministry of Science and Education', 'name_native': 'Ministarstvo znanosti i obrazovanja', 'type': 'ministry', 'country': 'HR', 'website': 'https://mzo.gov.hr'},
        {'name': 'Security and Intelligence Agency', 'name_native': 'Sigurnosno-obavještajna agencija', 'type': 'agency', 'country': 'HR', 'website': 'https://www.soa.hr'},
        {'name': 'Croatian Parliament', 'name_native': 'Hrvatski sabor', 'type': 'parliament', 'country': 'HR', 'website': 'https://www.sabor.hr'},
        {'name': 'Croatian Competition Agency', 'name_native': 'Agencija za zaštitu tržišnog natjecanja', 'type': 'regulator', 'country': 'HR', 'website': 'https://www.aztn.hr'},
        {'name': 'Croatian Investment Agency', 'name_native': 'Hrvatska agencija za investicije i konkurentnost', 'type': 'agency', 'country': 'HR', 'website': 'https://www.hamagbicro.hr'},

        # Slovenia
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Ministrstvo za zunanje zadeve', 'type': 'ministry', 'country': 'SI', 'website': 'https://www.gov.si/drzavni-organi/ministrstva/ministrstvo-za-zunanje-zadeve/'},
        {'name': 'Ministry of Defence', 'name_native': 'Ministrstvo za obrambo', 'type': 'ministry', 'country': 'SI', 'website': 'https://www.gov.si/drzavni-organi/ministrstva/ministrstvo-za-obrambo/'},
        {'name': 'Ministry of Economic Development and Technology', 'name_native': 'Ministrstvo za gospodarski razvoj in tehnologijo', 'type': 'ministry', 'country': 'SI', 'website': 'https://www.gov.si/drzavni-organi/ministrstva/ministrstvo-za-gospodarski-razvoj-in-tehnologijo/'},
        {'name': 'Ministry of Education, Science and Sport', 'name_native': 'Ministrstvo za izobraževanje, znanost in šport', 'type': 'ministry', 'country': 'SI', 'website': 'https://www.gov.si/drzavni-organi/ministrstva/ministrstvo-za-izobrazevanje-znanost-in-sport/'},
        {'name': 'Slovenian Intelligence and Security Agency', 'name_native': 'Slovenska obveščevalno-varnostna agencija', 'type': 'agency', 'country': 'SI', 'website': 'https://www.sova.gov.si'},
        {'name': 'National Assembly', 'name_native': 'Državni zbor', 'type': 'parliament', 'country': 'SI', 'website': 'https://www.dz-rs.si'},
        {'name': 'Competition Protection Agency', 'name_native': 'Agencija za varstvo konkurence', 'type': 'regulator', 'country': 'SI', 'website': 'https://www.varstvo-konkurence.si'},
        {'name': 'SPIRIT Slovenia', 'name_native': 'SPIRIT Slovenija', 'type': 'agency', 'country': 'SI', 'website': 'https://www.spiritslovenia.si'},

        # Cyprus
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Υπουργείο Εξωτερικών', 'type': 'ministry', 'country': 'CY', 'website': 'https://mfa.gov.cy'},
        {'name': 'Ministry of Defence', 'name_native': 'Υπουργείο Άμυνας', 'type': 'ministry', 'country': 'CY', 'website': 'https://mod.gov.cy'},
        {'name': 'Ministry of Energy, Commerce and Industry', 'name_native': 'Υπουργείο Ενέργειας, Εμπορίου και Βιομηχανίας', 'type': 'ministry', 'country': 'CY', 'website': 'https://www.mcit.gov.cy'},
        {'name': 'Ministry of Education, Sport and Youth', 'name_native': 'Υπουργείο Παιδείας, Αθλητισμού και Νεολαίας', 'type': 'ministry', 'country': 'CY', 'website': 'https://www.moec.gov.cy'},
        {'name': 'Cyprus Intelligence Service', 'name_native': 'Κυπριακή Υπηρεσία Πληροφοριών', 'type': 'agency', 'country': 'CY', 'website': 'https://www.nis.gov.cy'},
        {'name': 'House of Representatives', 'name_native': 'Βουλή των Αντιπροσώπων', 'type': 'parliament', 'country': 'CY', 'website': 'https://www.parliament.cy'},
        {'name': 'Commission for the Protection of Competition', 'name_native': 'Επιτροπή Προστασίας Ανταγωνισμού', 'type': 'regulator', 'country': 'CY', 'website': 'https://www.competition.gov.cy'},
        {'name': 'Invest Cyprus', 'name_native': 'Invest Cyprus', 'type': 'agency', 'country': 'CY', 'website': 'https://www.investcyprus.org.cy'},

        # Malta
        {'name': 'Ministry for Foreign and European Affairs', 'name_native': 'Ministeru għall-Affarijiet Barranin u Ewropej', 'type': 'ministry', 'country': 'MT', 'website': 'https://foreignandeu.gov.mt'},
        {'name': 'Armed Forces of Malta', 'name_native': 'Forzi Armati ta\' Malta', 'type': 'ministry', 'country': 'MT', 'website': 'https://afm.gov.mt'},
        {'name': 'Ministry for the Economy', 'name_native': 'Ministeru għall-Ekonomija', 'type': 'ministry', 'country': 'MT', 'website': 'https://economy.gov.mt'},
        {'name': 'Ministry for Education, Sport, Youth, Research and Innovation', 'name_native': 'Ministeru għall-Edukazzjoni', 'type': 'ministry', 'country': 'MT', 'website': 'https://education.gov.mt'},
        {'name': 'Security Service', 'name_native': 'Servizz tas-Sigurtà', 'type': 'agency', 'country': 'MT', 'website': 'https://homeaffairs.gov.mt'},
        {'name': 'Parliament of Malta', 'name_native': 'Parlament ta\' Malta', 'type': 'parliament', 'country': 'MT', 'website': 'https://parlament.mt'},
        {'name': 'Malta Competition and Consumer Affairs Authority', 'name_native': 'Awtorita\' għall-Kompetizzjoni u l-Affarijiet tal-Konsumatur', 'type': 'regulator', 'country': 'MT', 'website': 'https://mccaa.org.mt'},
        {'name': 'Malta Enterprise', 'name_native': 'Malta Enterprise', 'type': 'agency', 'country': 'MT', 'website': 'https://www.maltaenterprise.com'},

        # Luxembourg
        {'name': 'Ministry of Foreign and European Affairs', 'name_native': 'Ministère des Affaires étrangères et européennes', 'type': 'ministry', 'country': 'LU', 'website': 'https://maee.gouvernement.lu'},
        {'name': 'Ministry of Defence', 'name_native': 'Ministère de la Défense', 'type': 'ministry', 'country': 'LU', 'website': 'https://defense.gouvernement.lu'},
        {'name': 'Ministry of the Economy', 'name_native': 'Ministère de l\'Économie', 'type': 'ministry', 'country': 'LU', 'website': 'https://meco.gouvernement.lu'},
        {'name': 'Ministry of Higher Education and Research', 'name_native': 'Ministère de l\'Enseignement supérieur et de la Recherche', 'type': 'ministry', 'country': 'LU', 'website': 'https://mesr.gouvernement.lu'},
        {'name': 'State Intelligence Service', 'name_native': 'Service de Renseignement de l\'État', 'type': 'agency', 'country': 'LU', 'website': 'https://srel.lu'},
        {'name': 'Chamber of Deputies', 'name_native': 'Chambre des Députés', 'type': 'parliament', 'country': 'LU', 'website': 'https://www.chd.lu'},
        {'name': 'Competition Council', 'name_native': 'Conseil de la concurrence', 'type': 'regulator', 'country': 'LU', 'website': 'https://concurrence.public.lu'},
        {'name': 'Luxembourg for Business', 'name_native': 'Luxembourg for Business', 'type': 'agency', 'country': 'LU', 'website': 'https://www.luxembourgforbusiness.lu'}
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
    collect_remaining_eu()
