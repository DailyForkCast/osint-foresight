#!/usr/bin/env python3
"""Greece and Hungary - Tier 1 Verified Collection"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_greece_hungary():
    print("=" * 70)
    print("GREECE & HUNGARY - TIER 1 VERIFIED")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Greece
        {'name': 'Ministry of Foreign Affairs', 'name_native': 'Υπουργείο Εξωτερικών', 'type': 'ministry', 'country': 'GR', 'website': 'https://www.mfa.gr'},
        {'name': 'Ministry of National Defence', 'name_native': 'Υπουργείο Εθνικής Άμυνας', 'type': 'ministry', 'country': 'GR', 'website': 'https://www.mod.mil.gr'},
        {'name': 'Ministry of Development and Investments', 'name_native': 'Υπουργείο Ανάπτυξης', 'type': 'ministry', 'country': 'GR', 'website': 'https://www.mindev.gov.gr'},
        {'name': 'National Intelligence Service', 'name_native': 'Εθνική Υπηρεσία Πληροφοριών', 'type': 'agency', 'country': 'GR', 'website': 'https://www.nis.gr'},
        {'name': 'Hellenic Parliament', 'name_native': 'Βουλή των Ελλήνων', 'type': 'parliament', 'country': 'GR', 'website': 'https://www.parliament.gr'},
        {'name': 'Enterprise Greece', 'name_native': 'Enterprise Greece', 'type': 'agency', 'country': 'GR', 'website': 'https://www.enterprisegreece.gov.gr'},

        # Hungary
        {'name': 'Ministry of Foreign Affairs and Trade', 'name_native': 'Külgazdasági és Külügyminisztérium', 'type': 'ministry', 'country': 'HU', 'website': 'https://kormany.hu/kulgazdasagi-es-kulugyminiszterium'},
        {'name': 'Ministry of Defence', 'name_native': 'Honvédelmi Minisztérium', 'type': 'ministry', 'country': 'HU', 'website': 'https://honvedelem.hu'},
        {'name': 'Ministry of Innovation and Technology', 'name_native': 'Innovációs és Technológiai Minisztérium', 'type': 'ministry', 'country': 'HU', 'website': 'https://www.kormany.hu/hu/innovacios-es-technologiai-miniszterium'},
        {'name': 'Information Office', 'name_native': 'Információs Hivatal', 'type': 'agency', 'country': 'HU', 'website': 'https://www.ih.gov.hu'},
        {'name': 'National Assembly', 'name_native': 'Országgyűlés', 'type': 'parliament', 'country': 'HU', 'website': 'https://www.parlament.hu'},
        {'name': 'Hungarian Investment Promotion Agency', 'name_native': 'Magyar Befektetési Ügynökség', 'type': 'agency', 'country': 'HU', 'website': 'https://hipa.hu'}
    ]

    for inst in institutions:
        inst_id = generate_id(f"{inst['country'].lower()}_verified", inst['name'])
        notes = json.dumps({'collection_tier': 'tier_1_verified_only', 'collection_date': '2025-10-26'})

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
    total_inst = cursor.fetchone()[0]
    print(f"Countries: {countries}/42")
    print(f"National institutions: {total_inst}")
    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_greece_hungary()
