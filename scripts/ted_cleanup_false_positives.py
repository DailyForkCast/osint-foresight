#!/usr/bin/env python3
"""
Clean up TED database false positives
Remove old regex-based detections and fix company name matching issues
"""

import sqlite3
import json

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

# Strict Chinese company list (excluding false positives like "gree")
CHINESE_COMPANIES = [
    'huawei', 'zte', 'alibaba', 'tencent', 'baidu', 'xiaomi', 'oppo', 'vivo',
    'lenovo', 'dahua', 'hikvision', 'tiktok', 'bytedance', 'dji',
    'longi', 'ja solar', 'trina', 'jinko', 'canadian solar', 'risen energy',
    'byd', 'geely', 'great wall motor', 'xpeng', 'li auto', 'chery',
    'crrc', 'china railway', 'cosco', 'china shipping',
    'china state construction', 'cscec',
    'sany', 'zoomlion', 'xcmg', 'weichai', 'midea',
    'sinopec', 'petrochina', 'cnooc', 'chalco',
    'comac', 'avic'
]

def cleanup_database():
    """Remove false positives and apply strict company matching"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("="*80)
    print("TED DATABASE CLEANUP - REMOVING FALSE POSITIVES")
    print("="*80)

    # Get current stats
    cur.execute("SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1")
    before_count = cur.fetchone()[0]
    print(f"\nBefore cleanup: {before_count:,} China-related contracts")

    # Reset all China flags
    print("\nResetting all China-related flags...")
    cur.execute('''
        UPDATE ted_contracts_production
        SET is_chinese_related = 0,
            chinese_confidence = 0.0,
            chinese_indicators = NULL
    ''')
    conn.commit()

    # Re-scan with strict company matching
    print("Re-scanning with strict company matching...")
    cur.execute("SELECT id, contract_title FROM ted_contracts_production WHERE contract_title IS NOT NULL")

    matched = 0
    processed = 0

    for contract_id, title in cur.fetchall():
        processed += 1

        if not title:
            continue

        title_lower = title.lower()

        # Check for exact company matches
        matched_companies = []
        for company in CHINESE_COMPANIES:
            # Use word boundary matching to avoid "green" matching "gree"
            if f' {company} ' in f' {title_lower} ' or title_lower.startswith(f'{company} ') or title_lower.endswith(f' {company}'):
                matched_companies.append(company)

        if matched_companies:
            cur.execute('''
                UPDATE ted_contracts_production
                SET is_chinese_related = 1,
                    chinese_confidence = 0.9,
                    chinese_indicators = ?
                WHERE id = ?
            ''', (json.dumps({'companies': matched_companies}), contract_id))
            matched += 1

        if processed % 50000 == 0:
            conn.commit()
            print(f"  Processed {processed:,} contracts, {matched} matches...")

    conn.commit()

    # Get final stats
    cur.execute("SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1")
    after_count = cur.fetchone()[0]

    print(f"\n{'='*80}")
    print("CLEANUP COMPLETE")
    print(f"{'='*80}")
    print(f"Before: {before_count:,} China-related")
    print(f"After: {after_count:,} China-related")
    print(f"Removed: {before_count - after_count:,} false positives")
    print(f"False positive rate: {(before_count - after_count) / before_count * 100:.1f}%")

    # Show breakdown by company
    print("\nVerified Chinese company mentions:")
    cur.execute("""
        SELECT chinese_indicators
        FROM ted_contracts_production
        WHERE is_chinese_related = 1 AND chinese_indicators IS NOT NULL
    """)

    company_counts = {}
    for row in cur.fetchall():
        indicators = json.loads(row[0])
        if 'companies' in indicators:
            for company in indicators['companies']:
                company_counts[company] = company_counts.get(company, 0) + 1

    for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {company.title()}: {count}")

    conn.close()

if __name__ == '__main__':
    cleanup_database()
