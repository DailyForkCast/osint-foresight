#!/usr/bin/env python3
"""
Investigate 6 Non-German BRI Contracts
Check if these are actual Belt & Road Initiative references
"""

import sqlite3
import re
from pathlib import Path

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

print("\n" + "="*80)
print("INVESTIGATING 6 NON-GERMAN BRI CONTRACTS")
print("="*80)
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get non-German BRI contracts
non_german = cursor.execute("""
    SELECT
        id, notice_number, publication_date,
        ca_name, ca_country,
        contractor_name,
        contract_title,
        contract_description,
        value_total, currency
    FROM ted_contracts_production
    WHERE influence_category = 'BRI_RELATED'
    AND ca_country != 'DEU'
    ORDER BY ca_country, publication_date DESC
""").fetchall()

print(f"Found {len(non_german)} non-German BRI contracts")
print()

for i, contract in enumerate(non_german, 1):
    contract_id, notice, pub_date, ca_name, ca_country, contractor, title, description, value, currency = contract

    combined_text = f"{title} {description or ''}".lower()

    print(f"="*80)
    print(f"CONTRACT {i}: {ca_country}")
    print(f"="*80)
    print(f"ID: {contract_id}")
    print(f"Notice: {notice}")
    print(f"Date: {pub_date}")
    print(f"CA: {ca_name}")
    print(f"Contractor: {contractor or 'N/A'}")
    print(f"Title: {title[:100]}")
    print(f"Value: {value} {currency or 'N/A'}")
    print()
    print("DESCRIPTION (first 500 chars):")
    print((description or 'N/A')[:500])
    print()

    # Find what triggered BRI detection
    print("BRI PATTERN MATCHES:")

    # Check for 'BRI' standalone
    bri_matches = list(re.finditer(r'.{0,30}\bbri\b.{0,30}', combined_text, re.IGNORECASE))
    if bri_matches:
        print(f"  'BRI' found ({len(bri_matches)} times):")
        for match in bri_matches[:3]:
            print(f"    ...{match.group()}...")

    # Check for Belt and Road
    if re.search(r'belt\s+and\s+road', combined_text, re.IGNORECASE):
        print("  ✓ 'Belt and Road' found")
        matches = list(re.finditer(r'.{0,40}belt\s+and\s+road.{0,40}', combined_text, re.IGNORECASE))
        for match in matches[:2]:
            print(f"    ...{match.group()}...")

    # Check for Silk Road
    if re.search(r'silk\s+road', combined_text, re.IGNORECASE):
        print("  ✓ 'Silk Road' found")
        matches = list(re.finditer(r'.{0,40}silk\s+road.{0,40}', combined_text, re.IGNORECASE))
        for match in matches[:2]:
            print(f"    ...{match.group()}...")

    print()

    # Assessment
    print("ASSESSMENT:")

    # Check for German-style BRI (building measurement)
    if re.search(r'bruttorauminhalt|m[²³]|cbm|volume', combined_text, re.IGNORECASE):
        print("  ⚠️  LIKELY FALSE POSITIVE - Contains building measurement terms")
    elif re.search(r'belt\s+and\s+road\s+initiative', combined_text, re.IGNORECASE):
        print("  ✓ LIKELY TRUE BRI - Contains 'Belt and Road Initiative'")
    elif re.search(r'(china|chinese).*\bbri\b|\bbri\b.*(china|chinese)', combined_text, re.IGNORECASE):
        print("  ? POSSIBLE BRI - Contains 'BRI' + China reference")
    else:
        print("  ? UNCERTAIN - Manual review needed")

    print()

conn.close()

print("="*80)
print("INVESTIGATION COMPLETE")
print("="*80)
