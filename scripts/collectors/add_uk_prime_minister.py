#!/usr/bin/env python3
"""Add UK Prime Minister's Office"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def add_pm():
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institution = {
        'name': 'Prime Minister of the United Kingdom',
        'name_native': 'Prime Minister of the United Kingdom',
        'type': 'executive',
        'website': 'https://www.gov.uk/government/organisations/prime-ministers-office-10-downing-street'
    }

    inst_id = generate_id("gb_national", institution['name'])
    notes = json.dumps({
        'collection_tier': 'tier_1_verified_only',
        'collection_date': '2025-10-26',
        'added_reason': 'Missing institution needed for PM personnel link',
        'not_collected': {'china_relevance': '[NOT COLLECTED]'}
    })

    cursor.execute('''
        INSERT OR REPLACE INTO european_institutions
        (institution_id, institution_name, institution_name_native, institution_type,
         jurisdiction_level, country_code, official_website, china_relevance,
         status, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (inst_id, institution['name'], institution['name_native'], institution['type'],
          'national', 'GB', institution['website'], None, 'active', notes,
          datetime.now().isoformat(), datetime.now().isoformat()))

    conn.commit()
    print(f"Added: {institution['name']}")
    conn.close()

if __name__ == '__main__':
    add_pm()
