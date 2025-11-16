#!/usr/bin/env python3
"""
Fix BRI Detection and Re-run
1. Clear all 872 false positive BRI detections
2. Re-run influence detection with corrected BRI pattern (requires Belt & Road Initiative or China context)
"""

import sqlite3
from pathlib import Path
import re
import json
from datetime import datetime

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

print("\n" + "="*80)
print("FIX BRI DETECTION AND RE-RUN")
print("="*80)
print()

# Step 1: Clear false positives
print("STEP 1: Clearing 872 BRI false positives...")
conn = sqlite3.connect(db_path, timeout=60.0)
cursor = conn.cursor()

cursor.execute("""
    UPDATE ted_contracts_production
    SET influence_category = NULL,
        influence_priority = NULL,
        influence_patterns = NULL
    WHERE influence_category = 'BRI_RELATED'
""")

cleared = cursor.rowcount
conn.commit()
print(f"Cleared {cleared} false positive BRI contracts")
print()

# Step 2: Re-run BRI detection with CORRECTED pattern
print("STEP 2: Re-running BRI detection with corrected pattern...")
print()

# CORRECTED BRI patterns - NO standalone 'BRI', requires full context
bri_patterns = [
    r'\bbelt\s+and\s+road\s+(initiative|project|program|programme)?\b',
    r'\bone\s+belt\s+one\s+road\b',
    r'\bsilk\s+road\s+(initiative|project|program|programme)\b',
    r'\b(china|chinese).{0,50}\bbri\b',  # BRI with China context
    r'\bbri\b.{0,50}\b(china|chinese)\b'  # BRI with China context
]

# Get all contracts to check
print("Fetching contracts to check...")
all_contracts = cursor.execute("""
    SELECT
        id,
        contract_title,
        contract_description,
        ca_name
    FROM ted_contracts_production
""").fetchall()

print(f"Checking {len(all_contracts):,} contracts...")
print()

bri_found = []
processed = 0

for contract_id, title, description, ca_name in all_contracts:
    processed += 1

    if processed % 100000 == 0:
        print(f"Progress: {processed:,}/{len(all_contracts):,} ({processed/len(all_contracts)*100:.1f}%)")

    # Combine text
    combined_text = ' '.join([
        str(title or ''),
        str(description or ''),
        str(ca_name or '')
    ]).lower()

    # Check BRI patterns
    found = False
    matched_pattern = None

    for pattern in bri_patterns:
        if re.search(pattern, combined_text, re.IGNORECASE):
            found = True
            matched_pattern = pattern
            break

    if found:
        bri_found.append({
            'id': contract_id,
            'pattern': matched_pattern,
            'title': (title or '')[:100]
        })

print(f"Progress: {processed:,}/{len(all_contracts):,} (100.0%)")
print()

# Step 3: Update database with TRUE BRI contracts
print(f"STEP 3: Found {len(bri_found)} TRUE BRI contracts")
print()

if bri_found:
    print("Sample of detected BRI contracts:")
    for i, contract in enumerate(bri_found[:5], 1):
        print(f"  {i}. {contract['title']}")
        print(f"     Pattern: {contract['pattern'][:60]}")

    print()
    print(f"Updating database...")

    for contract in bri_found:
        cursor.execute("""
            UPDATE ted_contracts_production
            SET influence_category = 'BRI_RELATED',
                influence_priority = 'HIGH',
                influence_patterns = ?
            WHERE id = ?
        """, (json.dumps({'belt_road_initiative': [contract['pattern']]}), contract['id']))

    conn.commit()
    print(f"Updated {len(bri_found)} contracts")
else:
    print("No TRUE Belt & Road Initiative contracts found in TED database")

print()

# Step 4: Final verification
print("STEP 4: Final verification...")
final_count = cursor.execute("""
    SELECT COUNT(*) FROM ted_contracts_production
    WHERE influence_category = 'BRI_RELATED'
""").fetchone()[0]

print(f"BRI contracts after correction: {final_count}")
print()

conn.close()

# Save report
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
report = {
    'timestamp': timestamp,
    'false_positives_cleared': cleared,
    'true_bri_found': len(bri_found),
    'contracts': [{'id': c['id'], 'title': c['title'], 'pattern': c['pattern']} for c in bri_found]
}

report_file = Path(f"analysis/bri_correction_report_{timestamp}.json")
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)

print(f"Report saved to: {report_file}")
print()

print("="*80)
print("BRI DETECTION FIX COMPLETE")
print("="*80)
print()
print(f"SUMMARY:")
print(f"  False Positives Cleared: {cleared}")
print(f"  True BRI Found: {len(bri_found)}")
print(f"  Reduction: {cleared - len(bri_found)} contracts ({(cleared - len(bri_found))/cleared*100:.1f}%)")
print()
