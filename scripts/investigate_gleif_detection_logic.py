"""
Investigate GLEIF Detection Logic
=================================
Check why certain entities were classified as "Chinese"
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3
import json

db_path = 'F:/OSINT_WAREHOUSE/osint_master.db'

# Sample LEI codes that look like false positives
test_leis = [
    '0G2RK908D4IGON5CRG48',  # SCHUKRA BERNDORF GMBH (Austria)
    '3912005BP066MMELTJ57',  # Europäische Akademie Otzenhausen (Germany)
    '15DYKVGPQCMYBH2DZ583',  # VTB BANK (AUSTRIA) AG (Russian bank)
    '213800DWTSI7ACSGHN32',  # ALIBABA PICTURES (should be Chinese)
    '2549001ACVFAZRNMKL32',  # Xiaomi (should be Chinese)
]

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n" + "="*70)
print("INVESTIGATING GLEIF DETECTION LOGIC")
print("="*70)

for lei in test_leis:
    cursor.execute('''
        SELECT
            lei,
            legal_name,
            legal_address_country,
            legal_jurisdiction,
            hq_address_country,
            entity_category
        FROM gleif_entities
        WHERE lei = ?
    ''', (lei,))

    row = cursor.fetchone()
    if row:
        print(f"\nLEI: {row[0]}")
        print(f"  Legal Name: {row[1]}")
        print(f"  Legal Address Country: {row[2]}")
        print(f"  Legal Jurisdiction: {row[3]}")
        print(f"  HQ Country: {row[4]}")
        print(f"  Entity Category: {row[5]}")
    else:
        print(f"\nLEI: {lei} - NOT FOUND")

# Now check: how did we detect "Chinese entities in Europe"?
print("\n" + "="*70)
print("DETECTION QUERY ANALYSIS")
print("="*70)

# Query 1: Chinese entities (CN country)
print("\n[1] Entities with legal_address_country = 'CN':")
cursor.execute("SELECT COUNT(*) FROM gleif_entities WHERE legal_address_country = 'CN'")
print(f"    Count: {cursor.fetchone()[0]:,}")

# Query 2: Chinese entities (HK)
print("\n[2] Entities with legal_address_country = 'HK':")
cursor.execute("SELECT COUNT(*) FROM gleif_entities WHERE legal_address_country = 'HK'")
print(f"    Count: {cursor.fetchone()[0]:,}")

# Query 3: How are European countries being detected?
print("\n[3] Sample of entities with legal_address_country = 'AT':")
cursor.execute("""
    SELECT lei, legal_name, legal_address_country
    FROM gleif_entities
    WHERE legal_address_country = 'AT'
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"    {row[0]}: {row[1]} ({row[2]})")

# Query 4: Check if there's a cross-reference issue
print("\n[4] Checking gleif_cross_references table:")
cursor.execute("SELECT COUNT(*) FROM gleif_cross_references")
cross_ref_count = cursor.fetchone()[0]
print(f"    Total cross-references: {cross_ref_count:,}")

if cross_ref_count > 0:
    print("\n    Sample cross-references:")
    cursor.execute("SELECT * FROM gleif_cross_references LIMIT 5")
    for row in cursor.fetchall():
        print(f"    {row}")

# Query 5: Check if detection query was wrong
print("\n" + "="*70)
print("HYPOTHESIS: Script queried AT entities instead of CN entities")
print("="*70)

# What the script SHOULD have done
print("\n[CORRECT] Chinese entities in European countries:")
european_countries = ['GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'SE', 'DK']

for country in european_countries:
    cursor.execute("""
        SELECT COUNT(*)
        FROM gleif_entities
        WHERE legal_jurisdiction = 'CN'
        AND legal_address_country = ?
    """, (country,))
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"  {country}: {count:,} Chinese entities")

# Alternative: HQ in China, registered in Europe
print("\n[ALTERNATIVE] Entities with HQ in China, registered in Europe:")
for country in european_countries:
    cursor.execute("""
        SELECT COUNT(*)
        FROM gleif_entities
        WHERE hq_address_country IN ('CN', 'HK')
        AND legal_address_country = ?
    """, (country,))
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"  {country}: {count:,} entities")

conn.close()

print("\n" + "="*70)
print("INVESTIGATION COMPLETE")
print("="*70)
