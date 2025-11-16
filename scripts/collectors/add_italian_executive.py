#!/usr/bin/env python3
"""Add Italian Presidency and Prime Minister's Office"""
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

    institutions = [
        {
            'name': 'Presidency of the Italian Republic',
            'name_native': 'Presidenza della Repubblica Italiana',
            'type': 'executive',
            'website': 'https://www.quirinale.it'
        },
        {
            'name': 'Presidency of the Council of Ministers',
            'name_native': 'Presidenza del Consiglio dei Ministri',
            'type': 'executive',
            'website': 'https://www.governo.it'
        }
    ]

    for institution in institutions:
        inst_id = generate_id("it_national", institution['name'])
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
              'national', 'IT', institution['website'], None, 'active', notes,
              datetime.now().isoformat(), datetime.now().isoformat()))

        print(f"Added: {institution['name']} ({institution['name_native']})")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_executive()
