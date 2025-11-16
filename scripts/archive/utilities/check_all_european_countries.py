#!/usr/bin/env python3
"""Check ALL European countries in GDELT database"""
import sqlite3

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# All European country codes (EU + EEA + Balkans + Eastern Europe)
EUROPEAN_COUNTRIES = {
    # EU-27
    'AUT': 'Austria', 'BEL': 'Belgium', 'BGR': 'Bulgaria', 'HRV': 'Croatia',
    'CYP': 'Cyprus', 'CZE': 'Czech Republic', 'DNK': 'Denmark', 'EST': 'Estonia',
    'FIN': 'Finland', 'FRA': 'France', 'DEU': 'Germany', 'GRC': 'Greece',
    'HUN': 'Hungary', 'IRL': 'Ireland', 'ITA': 'Italy', 'LVA': 'Latvia',
    'LTU': 'Lithuania', 'LUX': 'Luxembourg', 'MLT': 'Malta', 'NLD': 'Netherlands',
    'POL': 'Poland', 'PRT': 'Portugal', 'ROU': 'Romania', 'SVK': 'Slovakia',
    'SVN': 'Slovenia', 'ESP': 'Spain', 'SWE': 'Sweden',

    # EEA non-EU
    'NOR': 'Norway', 'ISL': 'Iceland', 'LIE': 'Liechtenstein',

    # UK (Brexit)
    'GBR': 'United Kingdom',

    # EU Candidates
    'MKD': 'North Macedonia', 'MNE': 'Montenegro', 'SRB': 'Serbia',
    'TUR': 'Turkey', 'ALB': 'Albania', 'BIH': 'Bosnia and Herzegovina',
    'UKR': 'Ukraine', 'MDA': 'Moldova', 'GEO': 'Georgia',

    # Other European
    'CHE': 'Switzerland', 'BLR': 'Belarus', 'RUS': 'Russia',
    'ARM': 'Armenia', 'AZE': 'Azerbaijan', 'KOS': 'Kosovo'
}

print("\n" + "=" * 90)
print("ALL EUROPEAN COUNTRIES - CHINA BILATERAL EVENTS")
print("=" * 90)

# Query all at once
all_codes = list(EUROPEAN_COUNTRIES.keys())
placeholders = ','.join(['?' for _ in all_codes])

query = f'''
    SELECT
        CASE
            WHEN actor1_country_code = 'CHN' THEN actor2_country_code
            WHEN actor2_country_code = 'CHN' THEN actor1_country_code
        END as eu_country,
        COUNT(*) as events
    FROM gdelt_events
    WHERE (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
      AND (actor1_country_code IN ({placeholders}) OR actor2_country_code IN ({placeholders}))
    GROUP BY eu_country
    ORDER BY events DESC
'''

cursor.execute(query, all_codes + all_codes)
results = cursor.fetchall()

# Print results
print("\nRANKED BY EVENT COUNT:")
print("-" * 90)

total_bilateral = 0
eu27_total = 0
candidate_total = 0
other_total = 0

EU27 = ['AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA',
        'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD',
        'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE']

CANDIDATES = ['MKD', 'MNE', 'SRB', 'TUR', 'ALB', 'BIH', 'UKR', 'MDA', 'GEO']

for code, count in results:
    if code and code in EUROPEAN_COUNTRIES:
        name = EUROPEAN_COUNTRIES[code]
        total_bilateral += count

        # Categorize
        if code in EU27:
            category = "EU-27"
            eu27_total += count
        elif code in CANDIDATES:
            category = "CANDIDATE"
            candidate_total += count
        elif code == 'GBR':
            category = "UK (post-Brexit)"
        elif code == 'RUS':
            category = "RUSSIA"
        elif code in ['NOR', 'ISL', 'CHE']:
            category = "EEA/EFTA"
        else:
            category = "OTHER"
            other_total += count

        print(f"{name:25} ({code}) | {count:8,} events | {category}")

print("=" * 90)
print(f"\nTOTAL EUROPEAN BILATERAL EVENTS: {total_bilateral:,}")
print(f"  EU-27 Total: {eu27_total:,}")
print(f"  Candidate Countries: {candidate_total:,}")
print(f"  Other European: {other_total:,}")

# Get China total for percentage
cursor.execute("SELECT COUNT(*) FROM gdelt_events WHERE actor1_country_code = 'CHN' OR actor2_country_code = 'CHN'")
china_total = cursor.fetchone()[0]

print(f"\nTotal China events: {china_total:,}")
print(f"European percentage: {100*total_bilateral/china_total:.2f}%")

# Find countries with NO data
missing = []
for code, name in EUROPEAN_COUNTRIES.items():
    found = False
    for result_code, _ in results:
        if result_code == code:
            found = True
            break
    if not found:
        missing.append(f"{name} ({code})")

if missing:
    print(f"\n\nCOUNTRIES WITH NO BILATERAL DATA ({len(missing)}):")
    print("-" * 90)
    for country in sorted(missing):
        print(f"  {country}")
else:
    print("\n\nALL EUROPEAN COUNTRIES HAVE DATA!")

print("=" * 90)
