"""
Identify EU Countries with Significant GDELT China Events
Focus: 2020-2023 period to identify validation candidates
"""

import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

db = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = db.cursor()

print('='*100)
print('EU COUNTRIES WITH CHINA GDELT EVENTS (2020-2023)')
print('Purpose: Identify countries for multi-country validation expansion')
print('='*100)
print()

# EU country codes (27 member states)
eu_countries = [
    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
    'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
    'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
]

eu_country_names = {
    'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria', 'HR': 'Croatia',
    'CY': 'Cyprus', 'CZ': 'Czechia', 'DK': 'Denmark', 'EE': 'Estonia',
    'FI': 'Finland', 'FR': 'France', 'DE': 'Germany', 'GR': 'Greece',
    'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy', 'LV': 'Latvia',
    'LT': 'Lithuania', 'LU': 'Luxembourg', 'MT': 'Malta', 'NL': 'Netherlands',
    'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania', 'SK': 'Slovakia',
    'SI': 'Slovenia', 'ES': 'Spain', 'SE': 'Sweden'
}

print('STEP 1: OVERALL EU-CHINA GDELT EVENTS')
print('-'*100)

# Check GDELT table structure first
cursor.execute("PRAGMA table_info(gdelt_events)")
columns = [col[1] for col in cursor.fetchall()]
print(f"Available columns in gdelt_events: {', '.join(columns[:15])}...")
print()

# Check if we have country codes
if 'actor1_country_code' in columns and 'actor2_country_code' in columns:
    # Count events by EU country
    country_events = []

    for country_code in eu_countries:
        cursor.execute("""
            SELECT COUNT(*)
            FROM gdelt_events
            WHERE (actor1_country_code = ? OR actor2_country_code = ?)
              AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
              AND CAST(SUBSTR(sqldate, 1, 4) AS INTEGER) BETWEEN 2020 AND 2023
        """, (country_code, country_code))
        count = cursor.fetchone()[0]

        if count > 0:
            country_events.append((country_code, eu_country_names[country_code], count))

    # Sort by event count
    country_events.sort(key=lambda x: x[2], reverse=True)

    print(f"EU countries with China GDELT events (2020-2023):")
    print(f"{'Rank':<6} {'Code':<6} {'Country':<20} {'Events':<15} {'Priority':<15}")
    print('-'*70)

    for rank, (code, name, count) in enumerate(country_events, 1):
        priority = 'HIGH' if count > 1000 else 'MEDIUM' if count > 100 else 'LOW'
        marker = ' <- Lithuania (validated)' if code == 'LT' else ''
        print(f"{rank:<6} {code:<6} {name:<20} {count:>13,}  {priority:<15}{marker}")

    print()
    print(f"Total EU countries with China events: {len(country_events)}/27")
    print()

    # Identify top 5 for detailed analysis
    top_5 = country_events[:5]
    print('='*100)
    print('RECOMMENDED FOR MULTI-COUNTRY VALIDATION')
    print('='*100)
    print()
    print('Top 5 EU countries by GDELT event volume (plus Lithuania for comparison):')
    print()

    for rank, (code, name, count) in enumerate(top_5, 1):
        print(f"{rank}. {name} ({code}): {count:,} events")

    # Add Lithuania if not in top 5
    lt_in_top5 = any(code == 'LT' for code, _, _ in top_5)
    if not lt_in_top5:
        lt_data = next((d for d in country_events if d[0] == 'LT'), None)
        if lt_data:
            print(f"\n+ Lithuania (LT): {lt_data[2]:,} events (validated baseline)")

    print()
    print('Strategy:')
    print('  1. Run trade validation for top 5 countries (same methodology as Lithuania)')
    print('  2. Compare patterns - which countries show 2021-2022 decreases?')
    print('  3. Run procurement validation for countries with trade decreases')
    print('  4. Identify if Lithuania pattern is unique or shared')
    print()

else:
    print("GDELT table does not have expected country code columns")
    print("Available columns:", columns)

print('='*100)
print('NEXT: Trade data extraction for top countries')
print('='*100)

db.close()
