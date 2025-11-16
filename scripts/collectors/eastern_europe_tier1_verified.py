#!/usr/bin/env python3
"""Eastern Europe - Tier 1 Verified Collection
Romania, Bulgaria, Slovakia
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_eastern_europe():
    print("=" * 70)
    print("EASTERN EUROPE - TIER 1 VERIFIED")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Romania
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Ministerul Afacerilor Externe', 'type': 'ministry', 'country': 'RO', 'website': 'https://www.mae.ro'},
        {'name': 'Ministry of National Defence', 'name_native': 'Ministerul Apărării Naționale', 'type': 'ministry', 'country': 'RO', 'website': 'https://www.mapn.ro'},
        {'name': 'Ministry of Economy, Entrepreneurship and Tourism', 'name_native': 'Ministerul Economiei', 'type': 'ministry', 'country': 'RO', 'website': 'https://www.economie.gov.ro'},
        {'name': 'Ministry of Research, Innovation and Digitalization', 'name_native': 'Ministerul Cercetării, Inovării și Digitalizării', 'type': 'ministry', 'country': 'RO', 'website': 'https://www.research.gov.ro'},
        {'name': 'Romanian Intelligence Service', 'name_native': 'Serviciul Român de Informații', 'type': 'agency', 'country': 'RO', 'website': 'https://www.sri.ro'},
        {'name': 'Foreign Intelligence Service', 'name_native': 'Serviciul de Informații Externe', 'type': 'agency', 'country': 'RO', 'website': 'https://www.sie.ro'},
        {'name': 'Chamber of Deputies', 'name_native': 'Camera Deputaților', 'type': 'parliament', 'country': 'RO', 'website': 'https://www.cdep.ro'},
        {'name': 'Senate', 'name_native': 'Senatul', 'type': 'parliament', 'country': 'RO', 'website': 'https://www.senat.ro'},
        {'name': 'Competition Council', 'name_native': 'Consiliul Concurenței', 'type': 'regulator', 'country': 'RO', 'website': 'https://www.consiliulconcurentei.ro'},
        {'name': 'Invest Romania', 'name_native': 'Invest Romania', 'type': 'agency', 'country': 'RO', 'website': 'https://www.investromania.gov.ro'},

        # Bulgaria
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Министерство на външните работи', 'type': 'ministry', 'country': 'BG', 'website': 'https://www.mfa.bg'},
        {'name': 'Ministry of Defence', 'name_native': 'Министерство на отбраната', 'type': 'ministry', 'country': 'BG', 'website': 'https://www.mod.bg'},
        {'name': 'Ministry of Economy and Industry', 'name_native': 'Министерство на икономиката и индустрията', 'type': 'ministry', 'country': 'BG', 'website': 'https://www.mi.government.bg'},
        {'name': 'Ministry of Education and Science', 'name_native': 'Министерство на образованието и науката', 'type': 'ministry', 'country': 'BG', 'website': 'https://www.mon.bg'},
        {'name': 'State Agency for National Security', 'name_native': 'Държавна агенция "Национална сигурност"', 'type': 'agency', 'country': 'BG', 'website': 'https://www.dans.bg'},
        {'name': 'National Assembly', 'name_native': 'Народно събрание', 'type': 'parliament', 'country': 'BG', 'website': 'https://www.parliament.bg'},
        {'name': 'Commission on Protection of Competition', 'name_native': 'Комисия за защита на конкуренцията', 'type': 'regulator', 'country': 'BG', 'website': 'https://www.cpc.bg'},
        {'name': 'InvestBulgaria Agency', 'name_native': 'Агенция за инвестиции', 'type': 'agency', 'country': 'BG', 'website': 'https://www.investbg.government.bg'},

        # Slovakia
        {'name': 'Ministry of Foreign and European Affairs', 'name_native': 'Ministerstvo zahraničných vecí a európskych záležitostí', 'type': 'ministry', 'country': 'SK', 'website': 'https://www.mzv.sk'},
        {'name': 'Ministry of Defence', 'name_native': 'Ministerstvo obrany', 'type': 'ministry', 'country': 'SK', 'website': 'https://www.mosr.sk'},
        {'name': 'Ministry of Economy', 'name_native': 'Ministerstvo hospodárstva', 'type': 'ministry', 'country': 'SK', 'website': 'https://www.mhsr.sk'},
        {'name': 'Ministry of Education, Science, Research and Sport', 'name_native': 'Ministerstvo školstva, vedy, výskumu a športu', 'type': 'ministry', 'country': 'SK', 'website': 'https://www.minedu.sk'},
        {'name': 'Slovak Intelligence Service', 'name_native': 'Slovenská informačná služba', 'type': 'agency', 'country': 'SK', 'website': 'https://www.sis.gov.sk'},
        {'name': 'National Council', 'name_native': 'Národná rada', 'type': 'parliament', 'country': 'SK', 'website': 'https://www.nrsr.sk'},
        {'name': 'Antimonopoly Office', 'name_native': 'Protimonopolný úrad', 'type': 'regulator', 'country': 'SK', 'website': 'https://www.antimon.gov.sk'},
        {'name': 'Slovak Investment and Trade Development Agency', 'name_native': 'Slovenská agentúra pre investície a obchod', 'type': 'agency', 'country': 'SK', 'website': 'https://www.sario.sk'}
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
    collect_eastern_europe()
