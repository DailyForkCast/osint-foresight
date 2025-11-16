#!/usr/bin/env python3
"""
Import CEIAS Data - Romania, Czech Republic, Poland, Hungary (Simplified)
Source: Central European Institute of Asian Studies (CEIAS) Academic Tracker
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(DB_PATH), timeout=60.0)

print("IMPORTING CEIAS DATA...")

# Confucius Institutes data
confucius_institutes = [
    # Romania
    ('CI_RO_BUCHAREST', 'RO', 'confucius_institute', 'Confucius Institute at University of Bucharest', 'University of Bucharest', 'university', 'Bucharest', 'Bucharest', 2007, 'active', 'Chinese language education, cultural programs', True, False, 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'),
    ('CI_RO_CLUJ', 'RO', 'confucius_institute', 'Confucius Institute at Babes-Bolyai University', 'Babes-Bolyai University', 'university', 'Cluj-Napoca', 'Cluj County', 2010, 'active', 'Chinese language education, cultural exchange', True, False, 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'),
    ('CI_RO_BRASOV', 'RO', 'confucius_institute', 'Confucius Institute at Transylvania University', 'Transylvania University', 'university', 'Brasov', 'Brasov County', 2010, 'active', 'Chinese language education, traditional Chinese medicine', True, False, 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'),
    ('CI_RO_SIBIU', 'RO', 'confucius_institute', 'Confucius Institute at Lucian Blaga University', 'Lucian Blaga University', 'university', 'Sibiu', 'Sibiu County', 2010, 'active', 'Chinese language education, business programs', True, False, 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'),
    # Czech Republic
    ('CI_CZ_OLOMOUC', 'CZ', 'confucius_institute', 'Confucius Institute at Palacky University', 'Palacky University', 'university', 'Olomouc', 'Olomouc Region', 2007, 'active', 'Chinese language education, cultural programs', True, False, 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'),
    ('CI_CZ_PRAGUE_VSFS', 'CZ', 'confucius_institute', 'Confucius Institute at University of Finance and Administration', 'University of Finance and Administration', 'university', 'Prague', 'Prague', 2018, 'active', 'Chinese language education, business focus', True, False, 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'),
    ('CC_CZ_OSTRAVA', 'CZ', 'confucius_classroom', 'Confucius Classroom at VSB-Technical University', 'VSB-Technical University', 'university', 'Ostrava', 'Moravian-Silesian Region', 2015, 'active', 'Chinese language education for engineering students', True, False, 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'),
    ('CC_CZ_BUDEJOVICE', 'CZ', 'confucius_classroom', 'Confucius Classroom at VSTE University', 'VSTE University', 'university', 'Ceske Budejovice', 'South Bohemian Region', 2020, 'active', 'Chinese language education', True, False, 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'),
    # Poland
    ('CI_PL_KRAKOW', 'PL', 'confucius_institute', 'Confucius Institute at Jagiellonian University', 'Jagiellonian University', 'university', 'Krakow', 'Lesser Poland', 2006, 'active', 'Chinese language education, cultural programs', True, False, 'https://ceias.eu/poland-extensive-ties-little-results/'),
    ('CI_PL_POZNAN', 'PL', 'confucius_institute', 'Confucius Institute at Adam Mickiewicz University', 'Adam Mickiewicz University', 'university', 'Poznan', 'Greater Poland', 2008, 'active', 'Chinese language education, cultural exchange', True, False, 'https://ceias.eu/poland-extensive-ties-little-results/'),
    ('CI_PL_OPOLE', 'PL', 'confucius_institute', 'Confucius Institute at Opole University of Technology', 'Opole University of Technology', 'university', 'Opole', 'Opole Voivodeship', 2010, 'active', 'Chinese language education, technical cooperation', True, False, 'https://ceias.eu/poland-extensive-ties-little-results/'),
    ('CI_PL_GDANSK', 'PL', 'confucius_institute', 'Confucius Institute at University of Gdansk', 'University of Gdansk', 'university', 'Gdansk', 'Pomeranian Voivodeship', 2011, 'active', 'Chinese language education, cultural programs', True, False, 'https://ceias.eu/poland-extensive-ties-little-results/'),
    ('CI_PL_WROCLAW', 'PL', 'confucius_institute', 'Confucius Institute at University of Wroclaw', 'University of Wroclaw', 'university', 'Wroclaw', 'Lower Silesian Voivodeship', 2012, 'active', 'Chinese language education, cultural exchange', True, False, 'https://ceias.eu/poland-extensive-ties-little-results/'),
    ('CI_PL_WARSAW', 'PL', 'confucius_institute', 'Confucius Institute at Warsaw University of Technology', 'Warsaw University of Technology', 'university', 'Warsaw', 'Masovian Voivodeship', 2013, 'active', 'Chinese language education, technical cooperation', True, False, 'https://ceias.eu/poland-extensive-ties-little-results/'),
    # Hungary
    ('CI_HU_BUDAPEST_ELTE', 'HU', 'confucius_institute', 'Confucius Institute at Eotvos Lorand University', 'Eotvos Lorand University', 'university', 'Budapest', 'Budapest', 2006, 'active', 'Chinese language education, national CI hub', True, False, 'https://ceias.eu/hungary-welcomed-and-unchecked-chinese-presence-in-academia/'),
    ('CI_HU_SZEGED', 'HU', 'confucius_institute', 'Confucius Institute at University of Szeged', 'University of Szeged', 'university', 'Szeged', 'Csongrad-Csanad County', 2012, 'active', 'Chinese language education, cultural exchange', True, False, 'https://ceias.eu/hungary-welcomed-and-unchecked-chinese-presence-in-academia/'),
    ('CI_HU_MISKOLC', 'HU', 'confucius_institute', 'Confucius Institute at University of Miskolc', 'University of Miskolc', 'university', 'Miskolc', 'Borsod-Abauj-Zemplen County', 2013, 'active', 'Chinese language education, technical cooperation', True, False, 'https://ceias.eu/hungary-welcomed-and-unchecked-chinese-presence-in-academia/'),
    ('CI_HU_PECS', 'HU', 'confucius_institute', 'Confucius Institute at University of Pecs', 'University of Pecs', 'university', 'Pecs', 'Baranya County', 2015, 'active', 'Chinese language education, cultural programs', True, False, 'https://ceias.eu/hungary-welcomed-and-unchecked-chinese-presence-in-academia/'),
    ('CI_HU_DEBRECEN', 'HU', 'confucius_institute', 'Confucius Institute at University of Debrecen', 'University of Debrecen', 'university', 'Debrecen', 'Hajdu-Bihar County', 2019, 'active', 'Chinese language education, cultural exchange', True, False, 'https://ceias.eu/hungary-welcomed-and-unchecked-chinese-presence-in-academia/'),
    ('TT_HU_BUDAPEST_ELTE', 'HU', 'confucius_teacher_training', 'Confucius Institute Teacher Training Center', 'Eotvos Lorand University', 'university', 'Budapest', 'Budapest', 2014, 'active', 'Teacher training for CEE Confucius Institutes', True, False, 'https://ceias.eu/hungary-welcomed-and-unchecked-chinese-presence-in-academia/'),
]

print(f"Importing {len(confucius_institutes)} Confucius Institutes...")
ci_count = 0
for ci in confucius_institutes:
    try:
        conn.execute("""
            INSERT OR REPLACE INTO cultural_institutions
            (institution_id, country_code, institution_type, institution_name,
             host_institution, host_institution_type, location_city, location_region,
             established_year, status, programs_offered, academic_freedom_concerns,
             government_scrutiny, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ci)
        ci_count += 1
    except Exception as e:
        print(f"Error: {e}")

conn.commit()
print(f"Imported {ci_count} CIs, committed to database")

# Check what was imported
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM cultural_institutions')
total_ci = cur.fetchone()[0]
print(f"Total CIs in database: {total_ci}")

print("\n[SUCCESS] CEIAS Confucius Institutes import complete!")
conn.close()
