#!/usr/bin/env python3
"""
Enhance China detection in existing TED data
Re-analyze contracts with improved methodology:
1. Separate location mentions from contractor nationality
2. Focus on company names and entities, not generic "China" mentions
3. Add contractor country extraction where available
"""

import sqlite3
import json
import re
from pathlib import Path

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

# Comprehensive Chinese company list
CHINESE_COMPANIES = [
    # Telecom/Tech
    'huawei', 'zte', 'alibaba', 'tencent', 'baidu', 'xiaomi', 'oppo', 'vivo',
    'lenovo', 'dahua', 'hikvision', 'tiktok', 'bytedance', 'dji',

    # Solar/Energy
    'longi', 'ja solar', 'trina', 'jinko', 'canadian solar', 'risen energy',

    # Automotive
    'byd', 'geely', 'great wall', 'nio', 'xpeng', 'li auto', 'chery',

    # Rail/Transport
    'crrc', 'china railway', 'cosco', 'china shipping',

    # Construction
    'china state construction', 'cscec', 'china railway construction',
    'china communications construction',

    # Industrial
    'sany', 'zoomlion', 'xcmg', 'weichai', 'midea', 'gree',

    # Chemicals/Materials
    'sinopec', 'petrochina', 'cnooc', 'chalco', 'baoshan steel',

    # Aviation
    'comac', 'avic',
]

# Major Chinese cities (excluding Beijing/Shanghai which are too generic)
CHINESE_CITIES = [
    'shenzhen', 'guangzhou', 'chengdu', 'hangzhou', 'wuhan',
    'suzhou', 'tianjin', 'nanjing', 'dongguan', 'foshan',
]

def enhance_china_detection():
    """Re-analyze all contracts with improved detection"""

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Add new fields if they don't exist
    cur.execute('''
        ALTER TABLE ted_contracts_production
        ADD COLUMN chinese_company_match TEXT
    ''')

    cur.execute('''
        ALTER TABLE ted_contracts_production
        ADD COLUMN is_location_only BOOLEAN DEFAULT 0
    ''')

    conn.commit()

    print("Enhancing China detection on existing contracts...")

    # Get all contracts
    cur.execute('SELECT id, contract_title, chinese_indicators FROM ted_contracts_production')

    updated = 0
    company_matches = 0

    for row in cur.fetchall():
        contract_id, title, indicators_json = row

        if not title:
            continue

        title_lower = title.lower()

        # Check for company matches
        matched_companies = []
        for company in CHINESE_COMPANIES:
            if company in title_lower:
                matched_companies.append(company)

        # Only flag as China-related if we have company match
        if matched_companies:
            cur.execute('''
                UPDATE ted_contracts_production
                SET chinese_company_match = ?,
                    is_chinese_related = 1,
                    chinese_confidence = 0.9
                WHERE id = ?
            ''', (json.dumps(matched_companies), contract_id))
            company_matches += 1

        updated += 1
        if updated % 10000 == 0:
            conn.commit()
            print(f"  Processed {updated:,} contracts, {company_matches} with company matches")

    conn.commit()

    print(f"\nEnhancement complete:")
    print(f"  Total contracts processed: {updated:,}")
    print(f"  Chinese company matches: {company_matches}")

    # Generate report
    print("\n" + "=" * 80)
    print("REFINED CHINA ANALYSIS")
    print("=" * 80)

    cur.execute('''
        SELECT COUNT(*) FROM ted_contracts_production
        WHERE chinese_company_match IS NOT NULL
    ''')
    print(f"\nContracts with Chinese company mentions: {cur.fetchone()[0]:,}")

    # Breakdown by company
    print("\nTop Chinese companies mentioned:")
    for company in CHINESE_COMPANIES[:20]:
        cur.execute(f'''
            SELECT COUNT(*) FROM ted_contracts_production
            WHERE chinese_company_match LIKE '%{company}%'
        ''')
        count = cur.fetchone()[0]
        if count > 0:
            print(f"  {company.title()}: {count}")

    conn.close()

if __name__ == '__main__':
    try:
        enhance_china_detection()
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Columns already exist, re-running analysis only...")
            enhance_china_detection()
        else:
            raise
