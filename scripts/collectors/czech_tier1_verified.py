#!/usr/bin/env python3
"""Czech Republic - Tier 1 Verified Collection"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_czech_tier1():
    print("=" * 70)
    print("CZECH REPUBLIC - TIER 1 VERIFIED")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Ministerstvo zahraničních věcí', 'type': 'ministry', 'website': 'https://www.mzv.cz'},
        {'name': 'Ministry of Defence', 'name_native': 'Ministerstvo obrany', 'type': 'ministry', 'website': 'https://www.army.cz'},
        {'name': 'Ministry of Industry and Trade', 'name_native': 'Ministerstvo průmyslu a obchodu', 'type': 'ministry', 'website': 'https://www.mpo.cz'},
        {'name': 'Ministry of Education, Youth and Sports', 'name_native': 'Ministerstvo školství, mládeže a tělovýchovy', 'type': 'ministry', 'website': 'https://www.msmt.cz'},
        {'name': 'Ministry of Interior', 'name_native': 'Ministerstvo vnitra', 'type': 'ministry', 'website': 'https://www.mvcr.cz'},
        {'name': 'Security Information Service', 'name_native': 'Bezpečnostní informační služba', 'type': 'agency', 'website': 'https://www.bis.cz'},
        {'name': 'Military Intelligence', 'name_native': 'Vojenské zpravodajství', 'type': 'agency', 'website': 'https://www.vzcr.cz'},
        {'name': 'National Cyber and Information Security Agency', 'name_native': 'Národní úřad pro kybernetickou a informační bezpečnost', 'type': 'agency', 'website': 'https://www.nukib.cz'},
        {'name': 'Chamber of Deputies', 'name_native': 'Poslanecká sněmovna', 'type': 'parliament', 'website': 'https://www.psp.cz'},
        {'name': 'Senate', 'name_native': 'Senát', 'type': 'parliament', 'website': 'https://www.senat.cz'},
        {'name': 'CzechInvest', 'name_native': 'CzechInvest', 'type': 'agency', 'website': 'https://www.czechinvest.org'},
        {'name': 'CzechTrade', 'name_native': 'CzechTrade', 'type': 'agency', 'website': 'https://www.czechtrade.cz'}
    ]

    for inst in institutions:
        inst_id = generate_id('cz_verified', inst['name'])
        notes = json.dumps({'collection_tier': 'tier_1_verified_only', 'collection_date': '2025-10-26'})

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, official_website, china_relevance, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inst_id, inst['name'], inst['name_native'], inst['type'], 'national', 'CZ',
              inst['website'], None, 'active', notes, datetime.now().isoformat(), datetime.now().isoformat()))
        print(f"  + {inst['name']}")

    conn.commit()
    print(f"\nTotal: {len(institutions)}")
    cursor.execute('SELECT COUNT(DISTINCT country_code) FROM european_institutions')
    print(f"Countries: {cursor.fetchone()[0]}/42")
    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_czech_tier1()
