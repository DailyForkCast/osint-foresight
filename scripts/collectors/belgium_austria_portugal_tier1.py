#!/usr/bin/env python3
"""Belgium, Austria, Portugal - Tier 1 Verified Collection"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_be_at_pt():
    print("=" * 70)
    print("BELGIUM, AUSTRIA, PORTUGAL - TIER 1 VERIFIED")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Belgium
        {'name': 'Federal Public Service Foreign Affairs', 'name_native': 'Service public fédéral Affaires étrangères', 'type': 'ministry', 'country': 'BE', 'website': 'https://diplomatie.belgium.be'},
        {'name': 'Federal Public Service Defence', 'name_native': 'Service public fédéral Défense', 'type': 'ministry', 'country': 'BE', 'website': 'https://www.defense.belgium.be'},
        {'name': 'Federal Public Service Economy', 'name_native': 'Service public fédéral Économie', 'type': 'ministry', 'country': 'BE', 'website': 'https://economie.fgov.be'},
        {'name': 'State Security Service', 'name_native': 'Sûreté de l\'État', 'type': 'agency', 'country': 'BE', 'website': 'https://www.vsse.be'},
        {'name': 'General Intelligence and Security Service', 'name_native': 'Service général du renseignement et de la sécurité', 'type': 'agency', 'country': 'BE', 'website': 'https://www.sgrs.be'},
        {'name': 'Centre for Cybersecurity Belgium', 'name_native': 'Centre pour la Cybersécurité Belgique', 'type': 'agency', 'country': 'BE', 'website': 'https://ccb.belgium.be'},
        {'name': 'Chamber of Representatives', 'name_native': 'Chambre des représentants', 'type': 'parliament', 'country': 'BE', 'website': 'https://www.lachambre.be'},
        {'name': 'Senate', 'name_native': 'Sénat', 'type': 'parliament', 'country': 'BE', 'website': 'https://www.senate.be'},
        {'name': 'Belgian Competition Authority', 'name_native': 'Autorité belge de la concurrence', 'type': 'regulator', 'country': 'BE', 'website': 'https://www.abc-bma.be'},
        {'name': 'Flanders Investment & Trade', 'name_native': 'Flanders Investment & Trade', 'type': 'agency', 'country': 'BE', 'website': 'https://www.flandersinvestmentandtrade.com'},

        # Austria
        {'name': 'Federal Ministry for European and International Affairs', 'name_native': 'Bundesministerium für europäische und internationale Angelegenheiten', 'type': 'ministry', 'country': 'AT', 'website': 'https://www.bmeia.gv.at'},
        {'name': 'Federal Ministry of Defence', 'name_native': 'Bundesministerium für Landesverteidigung', 'type': 'ministry', 'country': 'AT', 'website': 'https://www.bundesheer.at'},
        {'name': 'Federal Ministry for Digital and Economic Affairs', 'name_native': 'Bundesministerium für Digitalisierung und Wirtschaftsstandort', 'type': 'ministry', 'country': 'AT', 'website': 'https://www.bmdw.gv.at'},
        {'name': 'Federal Ministry of the Interior', 'name_native': 'Bundesministerium für Inneres', 'type': 'ministry', 'country': 'AT', 'website': 'https://www.bmi.gv.at'},
        {'name': 'Federal Office for the Protection of the Constitution', 'name_native': 'Bundesamt für Verfassungsschutz und Terrorismusbekämpfung', 'type': 'agency', 'country': 'AT', 'website': 'https://www.bvt.gv.at'},
        {'name': 'National Council', 'name_native': 'Nationalrat', 'type': 'parliament', 'country': 'AT', 'website': 'https://www.parlament.gv.at/PAKT/NR/'},
        {'name': 'Federal Council', 'name_native': 'Bundesrat', 'type': 'parliament', 'country': 'AT', 'website': 'https://www.parlament.gv.at/PAKT/BR/'},
        {'name': 'Austrian Business Agency', 'name_native': 'Austrian Business Agency', 'type': 'agency', 'country': 'AT', 'website': 'https://www.aba.gv.at'},

        # Portugal
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Ministério dos Negócios Estrangeiros', 'type': 'ministry', 'country': 'PT', 'website': 'https://www.portaldiplomatico.mne.gov.pt'},
        {'name': 'Ministry of National Defence', 'name_native': 'Ministério da Defesa Nacional', 'type': 'ministry', 'country': 'PT', 'website': 'https://www.defesa.gov.pt'},
        {'name': 'Ministry of Economy and the Sea', 'name_native': 'Ministério da Economia e do Mar', 'type': 'ministry', 'country': 'PT', 'website': 'https://www.portugal.gov.pt/pt/gc23/area-de-governo/economia-e-mar'},
        {'name': 'Ministry of Science, Technology and Higher Education', 'name_native': 'Ministério da Ciência, Tecnologia e Ensino Superior', 'type': 'ministry', 'country': 'PT', 'website': 'https://www.portugal.gov.pt/pt/gc23/ministerio/mctes'},
        {'name': 'Security Intelligence Service', 'name_native': 'Serviço de Informações de Segurança', 'type': 'agency', 'country': 'PT', 'website': 'https://www.sis.pt'},
        {'name': 'Strategic Defence Intelligence Service', 'name_native': 'Serviço de Informações Estratégicas de Defesa', 'type': 'agency', 'country': 'PT', 'website': 'https://www.emgfa.pt/pt/sied'},
        {'name': 'Assembly of the Republic', 'name_native': 'Assembleia da República', 'type': 'parliament', 'country': 'PT', 'website': 'https://www.parlamento.pt'},
        {'name': 'Portuguese Competition Authority', 'name_native': 'Autoridade da Concorrência', 'type': 'regulator', 'country': 'PT', 'website': 'https://www.concorrencia.pt'},
        {'name': 'AICEP Portugal Global', 'name_native': 'Agência para o Investimento e Comércio Externo de Portugal', 'type': 'agency', 'country': 'PT', 'website': 'https://www.portugalglobal.pt'}
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
    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level = \"national\"')
    total = cursor.fetchone()[0]
    print(f"Countries: {countries}/42 ({int(100*countries/42)}%)")
    print(f"National institutions: {total}")
    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_be_at_pt()
