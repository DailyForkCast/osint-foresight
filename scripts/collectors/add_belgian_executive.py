#!/usr/bin/env python3
"""Add Belgian Federal Government"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def add_executive():
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institution = {
        'name': 'Federal Government of Belgium',
        'name_native': 'Federale Regering van België / Gouvernement fédéral de Belgique',
        'type': 'executive',
        'website': 'https://www.belgium.be'
    }

    inst_id = generate_id("be_national", institution['name'])
    notes = json.dumps({
        'collection_tier': 'tier_1_verified_only',
        'collection_date': '2025-10-26',
        'added_reason': 'Missing institution needed for executive personnel link',
        'not_collected': {'china_relevance': '[NOT COLLECTED]'}
    }, ensure_ascii=False)

    cursor.execute('''
        INSERT OR REPLACE INTO european_institutions
        (institution_id, institution_name, institution_name_native, institution_type,
         jurisdiction_level, country_code, official_website, china_relevance,
         status, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (inst_id, institution['name'], institution['name_native'], institution['type'],
          'national', 'BE', institution['website'], None, 'active', notes,
          datetime.now().isoformat(), datetime.now().isoformat()))

    conn.commit()
    print(f"Added: {institution['name']}")
    conn.close()

if __name__ == '__main__':
    add_executive()
