"""
TED Procurement Analysis for Flagged EU Countries
Check if export decreases correlate with procurement changes
"""

import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

db = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = db.cursor()

# Flagged countries from trade analysis
flagged_countries = {
    'LT': 'Lithuania',
    'SK': 'Slovakia',
    'GR': 'Greece',
    'FI': 'Finland',
    'SE': 'Sweden',
    'DK': 'Denmark',
    'NL': 'Netherlands',
    'IE': 'Ireland',
    'LV': 'Latvia',
    'SI': 'Slovenia',
    'ES': 'Spain',
    'BG': 'Bulgaria',
    'CY': 'Cyprus'
}

print('='*100)
print('TED PROCUREMENT ANALYSIS: FLAGGED EU COUNTRIES')
print('Countries with >20% export decrease to China (2020-2023)')
print('='*100)
print()

results = {}

for code, name in flagged_countries.items():
    cursor.execute("""
        SELECT
            year,
            COUNT(*) as contracts,
            SUM(CASE WHEN contract_value IS NOT NULL THEN contract_value ELSE 0 END) as total_value
        FROM ted_china_contracts_fixed
        WHERE (buyer_country LIKE ? OR buyer_country = ?)
          AND year BETWEEN 2020 AND 2023
        GROUP BY year
        ORDER BY year
    """, (f'%{name}%', code))

    data = cursor.fetchall()

    if data:
        results[code] = {
            'name': name,
            'years': {year: {'contracts': contracts, 'value': value} for year, contracts, value in data}
        }

print(f"{'Country':<20} {'2020':<20} {'2021':<20} {'2022':<20} {'2023':<20} {'Pattern':<20}")
print(f"{'':20} {'Contracts (Value)':<20} {'Contracts (Value)':<20} {'Contracts (Value)':<20} {'Contracts (Value)':<20}")
print('-'*120)

for code, name in sorted(flagged_countries.items(), key=lambda x: x[1]):
    row = f"{name:<20}"

    if code in results:
        data = results[code]['years']

        for year in [2020, 2021, 2022, 2023]:
            if year in data:
                contracts = data[year]['contracts']
                value = data[year]['value'] / 1_000_000 if data[year]['value'] else 0
                row += f" {contracts:>2} (€{value:>6.2f}M)"
                row += " " * (20 - len(f" {contracts:>2} (€{value:>6.2f}M)"))
            else:
                row += f" 0 (€  0.00M)      "

        # Determine pattern
        y2020 = data.get(2020, {}).get('contracts', 0)
        y2021 = data.get(2021, {}).get('contracts', 0)
        y2022 = data.get(2022, {}).get('contracts', 0)

        if y2020 > 0 and y2021 == 0:
            pattern = 'CEASED 2021'
        elif y2020 > 0 and y2021 < y2020 * 0.5:
            pattern = 'MAJOR DECREASE'
        elif y2020 > 0 and y2021 < y2020:
            pattern = 'Decrease'
        else:
            pattern = 'No baseline'

        if code == 'LT':
            pattern += ' [VALIDATED]'

        row += pattern
    else:
        row += " No contracts found" + " " * 60

    print(row)

print()
print('='*100)
print('KEY OBSERVATIONS')
print('='*100)
print()

# Count how many show Lithuania-like pattern
ceased_2021 = [code for code, data in results.items() if
                data['years'].get(2020, {}).get('contracts', 0) > 0 and
                data['years'].get(2021, {}).get('contracts', 0) == 0]

major_decrease = [code for code, data in results.items() if
                   data['years'].get(2020, {}).get('contracts', 0) > 0 and
                   data['years'].get(2021, {}).get('contracts', 0) < data['years'].get(2020, {}).get('contracts', 0) * 0.5 and
                   code not in ceased_2021]

print(f"Countries with procurement CEASED in 2021 (Lithuania pattern): {len(ceased_2021)}")
if ceased_2021:
    for code in ceased_2021:
        name = results[code]['name']
        val_2020 = results[code]['years'].get(2020, {}).get('contracts', 0)
        print(f"  - {name} ({code}): {val_2020} contracts in 2020, 0 in 2021")

print()
print(f"Countries with MAJOR procurement decrease in 2021: {len(major_decrease)}")
if major_decrease:
    for code in major_decrease:
        name = results[code]['name']
        val_2020 = results[code]['years'].get(2020, {}).get('contracts', 0)
        val_2021 = results[code]['years'].get(2021, {}).get('contracts', 0)
        pct_change = ((val_2021 - val_2020) / val_2020 * 100) if val_2020 > 0 else 0
        print(f"  - {name} ({code}): {val_2020} -> {val_2021} contracts ({pct_change:.1f}%)")

print()
no_contracts = [code for code in flagged_countries.keys() if code not in results]
print(f"Countries with NO Chinese contractor data in TED: {len(no_contracts)}")
if no_contracts:
    for code in no_contracts:
        name = flagged_countries[code]
        print(f"  - {name} ({code})")

print()
print('='*100)
print('INTERPRETATION')
print('='*100)
print()

if len(ceased_2021) > 1:
    print(f"FINDING: {len(ceased_2021)} countries show Lithuania-like procurement cessation in 2021")
    print("This suggests coordinated EU policy or widespread Chinese restriction, NOT isolated Lithuania-Taiwan event")
elif len(ceased_2021) == 1 and 'LT' in ceased_2021:
    print("FINDING: Only Lithuania shows procurement cessation pattern")
    print("This supports hypothesis that Lithuania-Taiwan events were country-specific")
else:
    print("FINDING: Mixed patterns across flagged countries")

print()
print("Note: Low/zero TED contracts may indicate:")
print("  1. Actual procurement cessation (policy change)")
print("  2. Below TED reporting thresholds")
print("  3. Chinese contractor detection limitations")
print("  4. Countries never had significant China procurement (no baseline)")

db.close()
