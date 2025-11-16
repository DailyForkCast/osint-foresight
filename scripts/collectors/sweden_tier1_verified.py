#!/usr/bin/env python3
"""
Sweden Federal Institutions - Tier 1 Verified Collection
ZERO FABRICATION COMPLIANCE
"""

import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    hash_part = hashlib.md5(text.encode()).hexdigest()[:12]
    return f"{prefix}_{hash_part}"

def collect_sweden_tier1():
    print("=" * 70)
    print("SWEDEN FEDERAL INSTITUTIONS - TIER 1 VERIFIED")
    print("=" * 70)
    print()

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        {
            'name': 'Ministry for Foreign Affairs',
            'name_native': 'Utrikesdepartementet',
            'type': 'ministry',
            'website': 'https://www.government.se/government-of-sweden/ministry-for-foreign-affairs/',
            'source_verified_date': '2025-10-26'
        },
        {
            'name': 'Ministry of Defence',
            'name_native': 'Försvarsdepartementet',
            'type': 'ministry',
            'website': 'https://www.government.se/government-of-sweden/ministry-of-defence/',
            'source_verified_date': '2025-10-26'
        },
        {
            'name': 'Ministry of Enterprise and Innovation',
            'name_native': 'Näringsdepartementet',
            'type': 'ministry',
            'website': 'https://www.government.se/government-of-sweden/ministry-of-enterprise-and-innovation/',
            'source_verified_date': '2025-10-26'
        },
        {
            'name': 'Ministry of Education and Research',
            'name_native': 'Utbildningsdepartementet',
            'type': 'ministry',
            'website': 'https://www.government.se/government-of-sweden/ministry-of-education-and-research/',
            'source_verified_date': '2025-10-26'
        },
        {
            'name': 'Ministry of Justice',
            'name_native': 'Justitiedepartementet',
            'type': 'ministry',
            'website': 'https://www.government.se/government-of-sweden/ministry-of-justice/',
            'source_verified_date': '2025-10-26'
        },
        {
            'name': 'Security Service',
            'name_native': 'Säkerhetspolisen',
            'type': 'agency',
            'website': 'https://www.sakerhetspolisen.se',
            'source_verified_date': '2025-10-26'
        },
        {
            'name': 'Swedish Defence Intelligence and Security Service',
            'name_native': 'Försvarets radioanstalt',
            'type': 'agency',
            'website': 'https://www.fra.se',
            'source_verified_date': '2025-10-26'
        },
        {
            'name': 'Swedish Civil Contingencies Agency',
            'name_native': 'Myndigheten för samhällsskydd och beredskap',
            'type': 'agency',
            'website': 'https://www.msb.se',
            'source_verified_date': '2025-10-26'
        },
        {
            'name': 'Riksdag',
            'name_native': 'Sveriges riksdag',
            'type': 'parliament',
            'website': 'https://www.riksdagen.se',
            'source_verified_date': '2025-10-26'
        },
        {
            'name': 'Swedish Competition Authority',
            'name_native': 'Konkurrensverket',
            'type': 'regulator',
            'website': 'https://www.konkurrensverket.se',
            'source_verified_date': '2025-10-26'
        },
        {
            'name': 'Business Sweden',
            'name_native': 'Business Sweden',
            'type': 'agency',
            'website': 'https://www.business-sweden.com',
            'source_verified_date': '2025-10-26'
        }
    ]

    for inst in institutions:
        inst_id = generate_id('se_verified', inst['name'])
        notes = json.dumps({
            'collection_tier': 'tier_1_verified_only',
            'collection_date': inst['source_verified_date'],
            'not_collected': {
                'china_relevance': '[NOT COLLECTED]',
                'personnel': '[NOT COLLECTED]'
            }
        })

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, official_website,
             china_relevance, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inst_id, inst['name'], inst['name_native'], inst['type'], 'national', 'SE',
              inst['website'], None, 'active', notes,
              datetime.now().isoformat(), datetime.now().isoformat()))

        print(f"  + {inst['name']}")

    conn.commit()
    print(f"\nTotal: {len(institutions)} institutions")

    cursor.execute('SELECT COUNT(DISTINCT country_code) FROM european_institutions')
    print(f"Countries: {cursor.fetchone()[0]}/42")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_sweden_tier1()
