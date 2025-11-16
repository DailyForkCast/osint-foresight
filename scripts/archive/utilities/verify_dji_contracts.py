#!/usr/bin/env python3
"""
Verify DJI Contracts in USAspending Database

Determines whether DJI contracts are:
1. Legitimate DJI drone company contracts (Section 1260H entity)
2. False positive (construction JV or other company with "DJI" in name)
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Database path
MASTER_DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

print("="*80)
print("DJI CONTRACT VERIFICATION")
print("="*80)
print()

# Connect to database
conn = sqlite3.connect(MASTER_DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Search for DJI contracts
print("Searching USAspending database for 'DJI' in recipient names...")
print()

cursor.execute("""
    SELECT
        recipient_name,
        recipient_parent_name,
        recipient_country,
        pop_country,
        action_date,
        naics_code,
        naics_description,
        award_description,
        federal_action_obligation,
        total_dollars_obligated,
        awarding_agency,
        funding_agency,
        fiscal_year
    FROM usaspending_china_comprehensive
    WHERE recipient_name LIKE '%DJI%'
    ORDER BY action_date DESC
""")

contracts = cursor.fetchall()

print(f"Found {len(contracts)} contracts with 'DJI' in recipient name")
print()

if not contracts:
    print("No contracts found.")
    conn.close()
    exit()

# Analyze contracts
print("="*80)
print("CONTRACT DETAILS")
print("="*80)
print()

results = {
    'total_contracts': len(contracts),
    'timestamp': datetime.now().isoformat(),
    'analysis': {
        'is_drone_company': False,
        'is_construction_jv': False,
        'confidence': 'unknown'
    },
    'contracts': []
}

unique_recipients = set()
for row in contracts:
    recipient = row['recipient_name']
    unique_recipients.add(recipient)

    contract_data = {
        'recipient_name': recipient,
        'recipient_parent': row['recipient_parent_name'],
        'recipient_country': row['recipient_country'],
        'pop_country': row['pop_country'],
        'date': row['action_date'],
        'fiscal_year': row['fiscal_year'],
        'naics_code': row['naics_code'],
        'naics_description': row['naics_description'],
        'description': row['award_description'],
        'federal_action_obligation': row['federal_action_obligation'],
        'total_dollars_obligated': row['total_dollars_obligated'],
        'awarding_agency': row['awarding_agency'],
        'funding_agency': row['funding_agency']
    }
    results['contracts'].append(contract_data)

    print(f"Recipient: {recipient}")
    print(f"Parent: {row['recipient_parent_name']}")
    print(f"Recipient Country: {row['recipient_country'] or 'Unknown'}")
    print(f"Place of Performance: {row['pop_country']}")
    print(f"Date: {row['action_date']} ({row['fiscal_year']})")
    print(f"NAICS: {row['naics_code']} - {row['naics_description']}")
    print(f"Description: {row['award_description']}")
    print(f"Obligation: ${row['federal_action_obligation']:,.2f}")
    print(f"Total Value: ${row['total_dollars_obligated']:,.2f}")
    print(f"Agency: {row['awarding_agency']}")
    print("-"*80)
    print()

print()
print("="*80)
print("ANALYSIS")
print("="*80)
print()

print(f"Unique Recipients: {len(unique_recipients)}")
for recipient in unique_recipients:
    print(f"  - {recipient}")
print()

# Determine if this is DJI drone company or false positive
print("DETERMINATION:")
print()

# Check for indicators
is_construction = any('CONSTRUCTION' in r or 'JV' in r for r in unique_recipients)
is_china = any(c['recipient_country'] and 'CHINA' in c['recipient_country'].upper()
              for c in results['contracts'] if c['recipient_country'])
is_china_pop = any(c['pop_country'] and 'CHINA' in c['pop_country'].upper()
                  for c in results['contracts'] if c['pop_country'])
is_drone_naics = any(c['naics_description'] and ('AIRCRAFT' in c['naics_description'].upper() or
                                                   'DRONE' in c['naics_description'].upper() or
                                                   'UAV' in c['naics_description'].upper() or
                                                   'UNMANNED' in c['naics_description'].upper())
                    for c in results['contracts'] if c['naics_description'])
is_construction_naics = any(c['naics_description'] and 'CONSTRUCTION' in c['naics_description'].upper()
                           for c in results['contracts'] if c['naics_description'])

print(f"Construction/JV in name: {is_construction}")
print(f"China recipient location: {is_china}")
print(f"China place of performance: {is_china_pop}")
print(f"Drone/Aircraft NAICS: {is_drone_naics}")
print(f"Construction NAICS: {is_construction_naics}")
print()

if is_construction and is_construction_naics and not is_china and not is_drone_naics:
    print("VERDICT: FALSE POSITIVE - Construction Joint Venture")
    print()
    print("Reasoning:")
    print("  - Contractor name contains 'CONSTRUCTION' and 'JV'")
    print("  - NAICS code indicates commercial/institutional building construction")
    print("  - Not located in China")
    print("  - Not drone or aircraft related")
    print()
    print("Conclusion: This is NOT Shenzhen DJI Innovation Technology Co., Ltd. (the drone company)")
    print("This is an unrelated construction joint venture with 'DJI' in its name.")
    print()
    print("WARNING: The DJI entity found is a FALSE POSITIVE.")
    print("Correct validation count: 0 USAspending contracts for DJI drone company")

    results['analysis']['is_drone_company'] = False
    results['analysis']['is_construction_jv'] = True
    results['analysis']['confidence'] = 'high'

elif (is_china or is_china_pop) and is_drone_naics:
    print("VERDICT: LIKELY LEGITIMATE - DJI Drone Company")
    print()
    print("Reasoning:")
    print(f"  - China location: {is_china or is_china_pop}")
    print(f"  - Drone/Aircraft NAICS: {is_drone_naics}")
    print()
    print("Conclusion: This appears to be the actual DJI drone company")
    print("CRITICAL: Section 1260H entity with US government contracts")

    results['analysis']['is_drone_company'] = True
    results['analysis']['is_construction_jv'] = False
    results['analysis']['confidence'] = 'high' if (is_china and is_drone_naics) else 'medium'

else:
    print("VERDICT: UNCERTAIN - Requires Manual Review")
    print()
    print("Reasoning:")
    print("  - Insufficient data to make definitive determination")
    print("  - May require additional investigation")

    results['analysis']['confidence'] = 'low'

print()
print("="*80)

# Save results
output_path = Path("analysis/dji_contract_verification.json")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Results saved to: {output_path}")

conn.close()
