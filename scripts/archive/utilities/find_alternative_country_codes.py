#!/usr/bin/env python3
"""
Find alternative country codes for missing European countries
Check what codes GDELT actually uses
"""
import sqlite3

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

print("\n" + "=" * 100)
print("FINDING ALTERNATIVE COUNTRY CODES")
print("=" * 100)

# Get ALL unique country codes in database
print("\nQuerying all unique country codes in database...")
cursor.execute('''
    SELECT DISTINCT actor1_country_code
    FROM gdelt_events
    WHERE actor1_country_code IS NOT NULL

    UNION

    SELECT DISTINCT actor2_country_code
    FROM gdelt_events
    WHERE actor2_country_code IS NOT NULL

    ORDER BY 1
''')

all_codes = [row[0] for row in cursor.fetchall()]

print(f"Found {len(all_codes)} unique country codes in database")

# Search for codes that might be our missing countries
print("\n" + "=" * 100)
print("SEARCHING FOR ALTERNATIVE CODES")
print("=" * 100)

missing_countries = {
    'Romania': ['ROU', 'ROM', 'RO'],
    'Slovenia': ['SVN', 'SLO', 'SVE', 'SI'],
    'Bosnia and Herzegovina': ['BIH', 'BOS', 'BA'],
    'Montenegro': ['MNE', 'MNG', 'MNT', 'ME'],
    'Kosovo': ['KOS', 'KSV', 'XK', 'XKX']
}

for country, possible_codes in missing_countries.items():
    print(f"\n{country}:")
    print("-" * 100)

    found = False
    for code in possible_codes:
        if code in all_codes:
            # Get count for this code
            cursor.execute('''
                SELECT COUNT(*)
                FROM gdelt_events
                WHERE actor1_country_code = ? OR actor2_country_code = ?
            ''', (code, code))
            count = cursor.fetchone()[0]

            # Get China bilateral count
            cursor.execute('''
                SELECT COUNT(*)
                FROM gdelt_events
                WHERE (actor1_country_code = ? AND actor2_country_code = 'CHN')
                   OR (actor1_country_code = 'CHN' AND actor2_country_code = ?)
            ''', (code, code))
            china_count = cursor.fetchone()[0]

            print(f"  FOUND: {code} | Total events: {count:,} | China bilateral: {china_count:,}")
            found = True

    if not found:
        print(f"  NOT FOUND: None of these codes exist: {', '.join(possible_codes)}")

# Also search for European codes that contain these patterns
print("\n" + "=" * 100)
print("ALL EUROPEAN-LOOKING CODES IN DATABASE")
print("=" * 100)

european_patterns = ['R', 'S', 'B', 'M', 'K', 'A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'L', 'N', 'P', 'T', 'U']
european_codes = [code for code in all_codes if len(code) == 3 and code[0] in european_patterns]

print(f"\nFound {len(european_codes)} codes starting with European letters:")
print("-" * 100)

# Group by first letter
from collections import defaultdict
by_letter = defaultdict(list)
for code in european_codes:
    by_letter[code[0]].append(code)

for letter in sorted(by_letter.keys()):
    codes = ', '.join(sorted(by_letter[letter]))
    print(f"{letter}: {codes}")

# Check for any 3-letter codes containing ROM, SVN, BOS, MNE, KOS
print("\n" + "=" * 100)
print("CODES CONTAINING KEY PATTERNS")
print("=" * 100)

patterns = ['ROM', 'ROM', 'SVN', 'SLO', 'BIH', 'BOS', 'MNE', 'MNT', 'KOS', 'KSV']
for pattern in patterns:
    matches = [code for code in all_codes if pattern in code]
    if matches:
        print(f"\nCodes containing '{pattern}': {', '.join(matches)}")
        for code in matches:
            cursor.execute('''
                SELECT COUNT(*)
                FROM gdelt_events
                WHERE actor1_country_code = ? OR actor2_country_code = ?
            ''', (code, code))
            count = cursor.fetchone()[0]
            print(f"  {code}: {count:,} events")

print("\n" + "=" * 100)
print("\nAll codes saved for manual review")

# Save all codes to file
with open('analysis/all_gdelt_country_codes.txt', 'w') as f:
    f.write("ALL GDELT COUNTRY CODES IN DATABASE\n")
    f.write("=" * 80 + "\n\n")
    for code in all_codes:
        cursor.execute('''
            SELECT COUNT(*)
            FROM gdelt_events
            WHERE actor1_country_code = ? OR actor2_country_code = ?
        ''', (code, code))
        count = cursor.fetchone()[0]
        f.write(f"{code}: {count:,} events\n")

print("Complete list saved to: analysis/all_gdelt_country_codes.txt")
print("=" * 100)

conn.close()
