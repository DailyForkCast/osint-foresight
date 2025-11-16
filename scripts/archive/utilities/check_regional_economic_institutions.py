#!/usr/bin/env python3
"""Query database to find correct institution names for regional economy ministers"""
import sqlite3

db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check what economic institutions exist for these regions
regions = [
    ('DE', 'Bavaria'),
    ('DE', 'North Rhine-Westphalia'),
    ('DE', 'Baden-Württemberg'),
    ('IT', 'Lombardy'),
    ('IT', 'Lazio'),
    ('ES', 'Catalonia'),
    ('ES', 'Madrid'),
    ('FR', 'Île-de-France')
]

print("=" * 70)
print("REGIONAL INSTITUTION SEARCH")
print("=" * 70)
print()

for country, region in regions:
    print(f"\n{country} - {region}:")

    # Try to find any institution for this region
    cursor.execute('''
        SELECT institution_name, institution_type, subnational_jurisdiction
        FROM european_institutions
        WHERE country_code = ?
        AND (institution_name LIKE ? OR subnational_jurisdiction LIKE ?)
        ORDER BY institution_type
    ''', (country, f'%{region}%', f'%{region}%'))

    results = cursor.fetchall()
    if results:
        for name, inst_type, jurisdiction in results:
            print(f"  - {name} ({inst_type}, {jurisdiction})")
    else:
        print(f"  [NOT FOUND]")

# Also check if there are any economic/economy ministries at subnational level
print("\n" + "=" * 70)
print("ALL SUBNATIONAL ECONOMIC MINISTRIES")
print("=" * 70)
cursor.execute('''
    SELECT country_code, institution_name, subnational_jurisdiction
    FROM european_institutions
    WHERE jurisdiction_level != 'national'
    AND institution_type = 'ministry'
    AND (institution_name LIKE '%Economy%' OR institution_name LIKE '%Economic%')
    ORDER BY country_code, subnational_jurisdiction
''')

results = cursor.fetchall()
if results:
    for country, name, jurisdiction in results:
        print(f"{country} - {name} ({jurisdiction})")
else:
    print("[NO SUBNATIONAL ECONOMIC MINISTRIES FOUND]")

conn.close()
