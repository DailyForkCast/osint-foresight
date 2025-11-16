#!/usr/bin/env python3
"""
Generate final TED Chinese contractor report
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_FILE = Path("C:/Projects/OSINT - Foresight/analysis/TED_CHINESE_CONTRACTORS_FINAL_REPORT.json")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=" * 80)
print("TED CHINESE CONTRACTOR EXTRACTION - FINAL REPORT")
print("=" * 80)

# Total statistics
cur.execute("SELECT COUNT(*) FROM ted_contractors")
total = cur.fetchone()[0]
print(f"\nTotal contractors extracted: {total:,}")

cur.execute("SELECT COUNT(*) FROM ted_contractors WHERE is_chinese = 1")
chinese_total = cur.fetchone()[0]
print(f"Chinese contractors detected (includes false positives): {chinese_total}")

# High confidence - Country code = CN
cur.execute("SELECT COUNT(*) FROM ted_contractors WHERE contractor_country = 'CN'")
cn_country = cur.fetchone()[0]
print(f"\n** HIGH CONFIDENCE (Country Code = CN): {cn_country}")

# Get all CN contractors
print("\n" + "=" * 80)
print("VERIFIED CHINESE CONTRACTORS (Country Code = CN)")
print("=" * 80)

cur.execute("""
    SELECT contractor_name, contractor_address, contract_title, publication_date, source_archive
    FROM ted_contractors
    WHERE contractor_country = 'CN'
    ORDER BY publication_date
""")

cn_contractors = []
for row in cur.fetchall():
    name, address, title, date, archive = row
    print(f"\n{date} - {archive}")
    print(f"  Contractor: {name}")
    if address:
        print(f"  Address: {address}")
    print(f"  Contract: {title[:100] if title else 'N/A'}...")

    cn_contractors.append({
        'contractor_name': name,
        'contractor_address': address,
        'contract_title': title,
        'publication_date': date,
        'source_archive': archive,
        'confidence': 'HIGH',
        'indicator': 'country_code_CN'
    })

# Medium confidence - Chinese cities/provinces in name
print("\n" + "=" * 80)
print("MEDIUM CONFIDENCE - Chinese Geographic Indicators")
print("=" * 80)

cur.execute("""
    SELECT contractor_name, contractor_country, chinese_indicators, contract_title, publication_date
    FROM ted_contractors
    WHERE is_chinese = 1
    AND contractor_country != 'CN'
    AND (
        chinese_indicators LIKE '%beijing%' OR
        chinese_indicators LIKE '%shanghai%' OR
        chinese_indicators LIKE '%shenzhen%' OR
        chinese_indicators LIKE '%guangzhou%' OR
        chinese_indicators LIKE '%hong kong%' OR
        chinese_indicators LIKE '%wuxi%' OR
        chinese_indicators LIKE '%ningbo%'
    )
    ORDER BY publication_date
""")

medium_confidence = []
for row in cur.fetchall():
    name, country, indicators, title, date = row
    # Filter out false positives
    if any(fp in name.lower() for fp in ['glaxosmithkline', 'ghk consulting', 'mieschke']):
        continue

    print(f"\n{date}")
    print(f"  {name} ({country})")
    print(f"  Indicators: {indicators}")
    print(f"  {title[:80] if title else 'N/A'}...")

    medium_confidence.append({
        'contractor_name': name,
        'contractor_country': country,
        'chinese_indicators': indicators,
        'contract_title': title,
        'publication_date': date,
        'confidence': 'MEDIUM'
    })

# Save to JSON
report = {
    'generated': datetime.now().isoformat(),
    'total_contractors_extracted': total,
    'chinese_detections_raw': chinese_total,
    'high_confidence_cn_country': len(cn_contractors),
    'medium_confidence_geographic': len(medium_confidence),
    'high_confidence_contractors': cn_contractors,
    'medium_confidence_contractors': medium_confidence
}

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total contractors: {total:,}")
print(f"HIGH confidence (CN country code): {len(cn_contractors)}")
print(f"MEDIUM confidence (geographic indicators): {len(medium_confidence)}")
print(f"\nReport saved to: {OUTPUT_FILE}")

conn.close()
