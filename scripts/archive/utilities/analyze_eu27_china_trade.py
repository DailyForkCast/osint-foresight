"""
EU-27 China Trade Pattern Analysis (2020-2023)
Identify countries with Lithuania-like export decreases
"""

import sqlite3
import sys
import json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

db = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = db.cursor()

print('='*100)
print('EU-27 CHINA TRADE PATTERN ANALYSIS (2020-2023)')
print('Purpose: Identify countries with export decreases similar to Lithuania')
print('='*100)
print()

# EU country codes (27 member states)
eu_countries = {
    'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria', 'HR': 'Croatia',
    'CY': 'Cyprus', 'CZ': 'Czechia', 'DK': 'Denmark', 'EE': 'Estonia',
    'FI': 'Finland', 'FR': 'France', 'DE': 'Germany', 'GR': 'Greece',
    'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy', 'LV': 'Latvia',
    'LT': 'Lithuania', 'LU': 'Luxembourg', 'MT': 'Malta', 'NL': 'Netherlands',
    'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania', 'SK': 'Slovakia',
    'SI': 'Slovenia', 'ES': 'Spain', 'SE': 'Sweden'
}

print('STEP 1: EXTRACTING TRADE DATA FOR ALL EU COUNTRIES')
print('-'*100)

results = {}

for code, name in sorted(eu_countries.items()):
    # Get annual exports and imports
    cursor.execute("""
        SELECT
            CAST(SUBSTR(period, 1, 4) AS INTEGER) as year,
            flow,
            SUM(CASE WHEN value_eur IS NOT NULL THEN value_eur ELSE 0 END) as total_value
        FROM eurostat_comext
        WHERE reporter = ?
          AND partner = 'CN'
          AND CAST(SUBSTR(period, 1, 4) AS INTEGER) BETWEEN 2020 AND 2023
        GROUP BY year, flow
        ORDER BY year, flow
    """, (code,))

    trade_data = {}
    for year, flow, value in cursor.fetchall():
        if year not in trade_data:
            trade_data[year] = {'imports': 0, 'exports': 0}

        if flow == '1':  # Import
            trade_data[year]['imports'] = value
        elif flow == '2':  # Export
            trade_data[year]['exports'] = value

    if trade_data:
        results[code] = {
            'name': name,
            'trade_data': trade_data
        }

        # Calculate export changes
        if 2020 in trade_data and 2021 in trade_data:
            exp_2020 = trade_data[2020]['exports']
            exp_2021 = trade_data[2021]['exports']
            if exp_2020 > 0:
                change_2021 = ((exp_2021 - exp_2020) / exp_2020 * 100)
                results[code]['export_change_2020_2021'] = change_2021
            else:
                results[code]['export_change_2020_2021'] = None

        if 2020 in trade_data and 2023 in trade_data:
            exp_2020 = trade_data[2020]['exports']
            exp_2023 = trade_data[2023]['exports']
            if exp_2020 > 1_000_000:  # Only if baseline > 1M EUR
                change_total = ((exp_2023 - exp_2020) / exp_2020 * 100)
                results[code]['export_change_2020_2023'] = change_total
            else:
                results[code]['export_change_2020_2023'] = None

print(f'Collected trade data for {len(results)}/27 EU countries')
print()

print('='*100)
print('STEP 2: EXPORT CHANGE ANALYSIS (2020-2021)')
print('Context: Lithuania Taiwan events occurred in 2021')
print('='*100)
print()

# Sort by export change 2020-2021
countries_with_changes = [
    (code, data) for code, data in results.items()
    if data.get('export_change_2020_2021') is not None
]
countries_with_changes.sort(key=lambda x: x[1]['export_change_2020_2021'])

print(f"{'Rank':<6} {'Country':<20} {'2020 Exports':<18} {'2021 Exports':<18} {'Change':<15} {'Pattern':<15}")
print('-'*100)

for rank, (code, data) in enumerate(countries_with_changes, 1):
    name = data['name']
    exp_2020 = data['trade_data'][2020]['exports'] / 1_000_000
    exp_2021 = data['trade_data'][2021]['exports'] / 1_000_000
    change = data['export_change_2020_2021']

    # Classify pattern
    if change < -50:
        pattern = 'MAJOR DECREASE'
    elif change < -20:
        pattern = 'Decrease'
    elif change < -5:
        pattern = 'Minor decrease'
    elif change > 50:
        pattern = 'MAJOR INCREASE'
    elif change > 20:
        pattern = 'Increase'
    elif change > 5:
        pattern = 'Minor increase'
    else:
        pattern = 'Stable'

    marker = ' <- Lithuania (validated)' if code == 'LT' else ''
    print(f"{rank:<6} {name:<20} €{exp_2020:>14.1f}M  €{exp_2021:>14.1f}M  {change:>12.1f}%  {pattern:<15}{marker}")

print()
print('='*100)
print('STEP 3: CUMULATIVE EXPORT CHANGE (2020-2023)')
print('='*100)
print()

countries_with_total_changes = [
    (code, data) for code, data in results.items()
    if data.get('export_change_2020_2023') is not None
]
countries_with_total_changes.sort(key=lambda x: x[1]['export_change_2020_2023'])

print(f"{'Rank':<6} {'Country':<20} {'2020 Exports':<18} {'2023 Exports':<18} {'Change':<15} {'Pattern':<15}")
print('-'*100)

flagged_countries = []

for rank, (code, data) in enumerate(countries_with_total_changes, 1):
    name = data['name']
    exp_2020 = data['trade_data'][2020]['exports'] / 1_000_000
    exp_2023 = data['trade_data'].get(2023, {}).get('exports', 0) / 1_000_000
    change = data['export_change_2020_2023']

    # Classify pattern
    if change < -50:
        pattern = 'MAJOR DECREASE'
        flagged_countries.append((code, name, change))
    elif change < -20:
        pattern = 'Decrease'
        flagged_countries.append((code, name, change))
    elif change < -5:
        pattern = 'Minor decrease'
    elif change > 50:
        pattern = 'MAJOR INCREASE'
    elif change > 20:
        pattern = 'Increase'
    elif change > 5:
        pattern = 'Minor increase'
    else:
        pattern = 'Stable'

    marker = ' <- Lithuania (validated)' if code == 'LT' else ''
    print(f"{rank:<6} {name:<20} €{exp_2020:>14.1f}M  €{exp_2023:>14.1f}M  {change:>12.1f}%  {pattern:<15}{marker}")

print()
print('='*100)
print('STEP 4: FLAGGED COUNTRIES FOR FURTHER INVESTIGATION')
print('='*100)
print()

if flagged_countries:
    print(f'Countries with >20% export decrease (2020-2023):')
    print(f'{len(flagged_countries)} countries flagged')
    print()
    for code, name, change in flagged_countries:
        validated = ' [VALIDATED via TED + Trade]' if code == 'LT' else ''
        print(f'  - {name} ({code}): {change:.1f}% decrease{validated}')
    print()
    print('Recommended actions:')
    print('  1. Run TED procurement analysis for these countries')
    print('  2. Collect GDELT data for these countries (2020-2023)')
    print('  3. Check for political events in 2021-2022')
    print('  4. Validate if decreases are China-specific or global')
else:
    print('No countries (besides Lithuania) show >20% export decreases')

print()
print('='*100)
print('STEP 5: CONTROL GROUP ANALYSIS')
print('Countries with STABLE or INCREASING exports (potential control group)')
print('='*100)
print()

stable_countries = [
    (code, data) for code, data in results.items()
    if data.get('export_change_2020_2023') is not None
    and -10 < data['export_change_2020_2023'] < 10
]

growing_countries = [
    (code, data) for code, data in results.items()
    if data.get('export_change_2020_2023') is not None
    and data['export_change_2020_2023'] > 20
]

print(f'Stable exports (-10% to +10%): {len(stable_countries)} countries')
for code, data in stable_countries[:5]:
    change = data['export_change_2020_2023']
    print(f'  - {data["name"]} ({code}): {change:+.1f}%')

print()
print(f'Growing exports (>+20%): {len(growing_countries)} countries')
for code, data in growing_countries[:5]:
    change = data['export_change_2020_2023']
    print(f'  - {data["name"]} ({code}): {change:+.1f}%')

print()
print('='*100)
print('ANALYSIS COMPLETE')
print('='*100)
print()
print('Next steps:')
print('  1. Save results to JSON for detailed review')
print('  2. Run TED analysis for flagged countries')
print('  3. Create comparative visualization')
print()

# Save results to JSON
output_file = f'analysis/EU27_CHINA_TRADE_ANALYSIS_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)
print(f'Results saved to: {output_file}')

db.close()
