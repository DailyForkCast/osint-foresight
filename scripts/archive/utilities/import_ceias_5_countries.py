#!/usr/bin/env python3
"""
Import CEIAS Data for 5 Additional Countries
Slovenia, Bulgaria, Croatia, Greece, Austria
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(DB_PATH), timeout=60.0)

print("IMPORTING CEIAS DATA FOR 5 COUNTRIES")
print("="*80)

# Step 1: Add countries to bilateral_countries table
print("\nStep 1: Adding countries...")
countries = [
    ('SI', 'Slovenia', '斯洛文尼亚', True, True, 'active'),
    ('BG', 'Bulgaria', '保加利亚', True, True, 'active'),
    ('HR', 'Croatia', '克罗地亚', True, True, 'active'),
    ('GR', 'Greece', '希腊', True, True, 'active'),
    ('AT', 'Austria', '奥地利', True, False, 'observer'),
]

for c in countries:
    conn.execute("""
        INSERT OR REPLACE INTO bilateral_countries
        (country_code, country_name, country_name_chinese, eu_member,
         nato_member, bri_participation_status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, c)
    print(f"  OK: {c[1]} ({c[0]})")

conn.commit()

# Step 2: Import Confucius Institutes
print("\nStep 2: Importing Confucius Institutes...")

confucius_institutes = [
    # SLOVENIA
    ('CI_SI_LJUBLJANA', 'SI', 'confucius_institute', 'Confucius Institute at University of Ljubljana', 'University of Ljubljana Faculty of Economics', 'university', 'Ljubljana', 'Ljubljana', None, 'active', 'Mandarin courses, cultural programs', True, False, 'https://ceias.eu/slovenia-leaning-towards-a-gradual-and-selective-academic-cooperation-with-china/'),

    # BULGARIA
    ('CI_BG_SOFIA', 'BG', 'confucius_institute', 'Confucius Institute at Sofia University', 'Sofia University St. Kliment Ohridski', 'university', 'Sofia', 'Sofia', None, 'active', 'Mandarin courses, cultural programs', True, False, 'https://ceias.eu/bulgaria-a-steady-embrace-of-chinese-academia/'),
    ('CI_BG_TARNOVO', 'BG', 'confucius_institute', 'Confucius Institute at Veliko Tarnovo', 'St. Cyril and St. Methodius University of Veliko Tarnovo', 'university', 'Veliko Tarnovo', 'Veliko Tarnovo', None, 'active', 'Mandarin courses, cultural programs', True, False, 'https://ceias.eu/bulgaria-a-steady-embrace-of-chinese-academia/'),

    # CROATIA
    ('CI_HR_ZAGREB', 'HR', 'confucius_institute', 'Confucius Institute at University of Zagreb', 'University of Zagreb Faculty of Philosophy', 'university', 'Zagreb', 'Zagreb', 2012, 'active', 'Mandarin courses, cultural programs, Sinology department', True, True, 'https://ceias.eu/croatia-chinas-growing-role-in-croatia-through-academic-ties/'),
    ('CI_HR_RIJEKA', 'HR', 'confucius_institute', 'Confucius Institute at University of Rijeka', 'University of Rijeka', 'university', 'Rijeka', 'Primorje-Gorski Kotar', None, 'active', 'Mandarin courses, cultural programs', True, False, 'https://ceias.eu/croatia-chinas-growing-role-in-croatia-through-academic-ties/'),

    # GREECE
    ('CI_GR_ATHENS_1', 'GR', 'confucius_institute', 'Confucius Institute in Athens (First)', 'Unspecified university', 'university', 'Athens', 'Attica', 2009, 'active', 'Mandarin courses, cultural programs', True, False, 'https://ceias.eu/greece-the-overlooked-risks-of-academic-cooperation-with-china/'),
    ('CI_GR_ATHENS_2', 'GR', 'confucius_institute', 'Confucius Institute in Athens (Second)', 'Unspecified university', 'university', 'Athens', 'Attica', None, 'active', 'Mandarin courses, cultural programs', True, False, 'https://ceias.eu/greece-the-overlooked-risks-of-academic-cooperation-with-china/'),
    ('CI_GR_THESSALONIKI', 'GR', 'confucius_institute', 'Confucius Institute in Thessaloniki', 'Unspecified university', 'university', 'Thessaloniki', 'Central Macedonia', None, 'active', 'Mandarin courses, cultural programs', True, False, 'https://ceias.eu/greece-the-overlooked-risks-of-academic-cooperation-with-china/'),
    ('CI_GR_PATRAS', 'GR', 'confucius_institute', 'Confucius Institute in Patras', 'Unspecified university', 'university', 'Patras', 'Western Greece', None, 'active', 'Mandarin courses, cultural programs', True, False, 'https://ceias.eu/greece-the-overlooked-risks-of-academic-cooperation-with-china/'),
    ('CI_GR_VOLOS', 'GR', 'confucius_institute', 'Confucius Institute in Volos', 'Unspecified university', 'university', 'Volos', 'Thessaly', None, 'suspended', 'Suspended due to flood damage in 2023', True, False, 'https://ceias.eu/greece-the-overlooked-risks-of-academic-cooperation-with-china/'),

    # AUSTRIA
    ('CI_AT_VIENNA', 'AT', 'confucius_institute', 'Confucius Institute at University of Vienna', 'University of Vienna', 'university', 'Vienna', 'Vienna', 2006, 'active', 'Mandarin courses, cultural events', False, False, 'https://ceias.eu/austria-china-just-one-partner-among-many/'),
    ('CI_AT_GRAZ', 'AT', 'confucius_institute', 'Confucius Institute at University of Graz', 'University of Graz', 'university', 'Graz', 'Styria', 2010, 'active', 'Mandarin courses, cultural programming, 1 CI Classroom in Weiz', False, False, 'https://ceias.eu/austria-china-just-one-partner-among-many/'),
]

count_ci = 0
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
        count_ci += 1
        print(f"  OK: {ci[3]}")
    except Exception as e:
        print(f"  ERROR: {ci[0]} - {e}")

conn.commit()

# Step 3: Import Academic Partnerships
print("\nStep 3: Importing Academic Partnerships...")

partnerships = [
    # SLOVENIA - PLA-AFFILIATED
    ('SI_LJUBLJANA_HIT', 'SI', 'University of Ljubljana', 'university', 'Harbin Institute of Technology', 'university', 'research_cooperation', 'active', True, True, True, 'Engineering, aerospace, materials science', 'Seven Sons of National Defense - US Entity List institution', 'https://ceias.eu/slovenia-leaning-towards-a-gradual-and-selective-academic-cooperation-with-china/'),
    ('SI_LJUBLJANA_NUAA', 'SI', 'University of Ljubljana', 'university', 'Nanjing University of Aeronautics and Astronautics', 'university', 'research_cooperation', 'active', True, True, True, 'Aerospace engineering, aeronautics', 'Seven Sons of National Defense - Aerospace focus', 'https://ceias.eu/slovenia-leaning-towards-a-gradual-and-selective-academic-cooperation-with-china/'),
    ('SI_LJUBLJANA_NJUST', 'SI', 'University of Ljubljana', 'university', 'Nanjing University of Science and Technology', 'university', 'research_cooperation', 'active', True, True, True, 'Defense technology, weapons research', 'Seven Sons of National Defense - Weapons systems focus', 'https://ceias.eu/slovenia-leaning-towards-a-gradual-and-selective-academic-cooperation-with-china/'),

    # SLOVENIA - CORPORATE
    ('SI_CORP_HUAWEI_LJUBLJANA', 'SI', 'University of Ljubljana', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, '5G research equipment donation', 'Huawei 5G research equipment partnership', 'https://ceias.eu/slovenia-leaning-towards-a-gradual-and-selective-academic-cooperation-with-china/'),

    # BULGARIA - CORPORATE
    ('BG_CORP_HUAWEI_GABROVO', 'BG', 'Technical University of Gabrovo', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'ICT Academy, telecommunications training', 'Huawei ICT Academy partnership', 'https://ceias.eu/bulgaria-a-steady-embrace-of-chinese-academia/'),
    ('BG_CORP_HUAWEI_VARNA', 'BG', 'University of Economics Varna', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'ICT Academy, telecommunications training', 'Huawei ICT Academy partnership', 'https://ceias.eu/bulgaria-a-steady-embrace-of-chinese-academia/'),
    ('BG_CORP_HUAWEI_PLOVDIV', 'BG', 'University of Plovdiv', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'ICT Academy, telecommunications training', 'Huawei ICT Academy partnership', 'https://ceias.eu/bulgaria-a-steady-embrace-of-chinese-academia/'),
    ('BG_CORP_HUAWEI_TU_SOFIA', 'BG', 'Technical University of Sofia', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'ICT Academy, telecommunications training', 'Huawei ICT Academy partnership', 'https://ceias.eu/bulgaria-a-steady-embrace-of-chinese-academia/'),

    # CROATIA - PLA-AFFILIATED
    ('HR_ZAGREB_XJTU', 'HR', 'University of Zagreb', 'university', "Xi'an Jiaotong University", 'university', 'research_cooperation', 'active', True, True, True, 'Green ammonia research, sustainable energy', 'High-risk per ASPI - Project ended 2021, student exchanges continue', 'https://ceias.eu/croatia-chinas-growing-role-in-croatia-through-academic-ties/'),
    ('HR_ZAGREB_NPU', 'HR', 'University of Zagreb', 'university', 'Northwestern Polytechnic University', 'university', 'research_cooperation', 'active', True, True, True, 'Graph theory, mathematics research', 'High-risk PLA-affiliated institution', 'https://ceias.eu/croatia-chinas-growing-role-in-croatia-through-academic-ties/'),
    ('HR_BOSKOVIC_UESTC', 'HR', 'Ruder Boskovic Institute', 'research_institute', 'University of Electronic Science and Technology of China', 'university', 'research_cooperation', 'active', True, True, True, 'Enzyme development, bioactive compounds', 'PLA-affiliated institution cooperation', 'https://ceias.eu/croatia-chinas-growing-role-in-croatia-through-academic-ties/'),
    ('HR_PHYSICS_BIT', 'HR', 'Institute of Physics Zagreb', 'research_institute', 'Beijing Institute of Technology', 'university', 'research_cooperation', 'ended', True, True, True, 'Low-dimensional materials, information applications', 'Seven Sons of National Defense - Ended 2021', 'https://ceias.eu/croatia-chinas-growing-role-in-croatia-through-academic-ties/'),

    # AUSTRIA - CORPORATE
    ('AT_GRAZ_CETC', 'AT', 'Graz University of Technology', 'university', 'China Electronics Technology Group Corporation', 'corporation', 'corporate_cooperation', 'active', True, True, True, 'Sino-Austrian Electronic Technology Innovation Center (SAETIC), smart water management', 'Military-linked state-owned enterprise - Established 2015', 'https://ceias.eu/austria-china-just-one-partner-among-many/'),
    ('AT_TU_WIEN_HUAWEI', 'AT', 'Vienna University of Technology', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, '44 digitalization stipends for students', 'Huawei stipend program started Feb 2022', 'https://ceias.eu/austria-china-just-one-partner-among-many/'),
    ('AT_TU_WIEN_ZTE', 'AT', 'Vienna University of Technology', 'university', 'ZTE Corporation', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Telecommunications research and cooperation', 'ZTE partnership for telecom research', 'https://ceias.eu/austria-china-just-one-partner-among-many/'),
]

count_p = 0
for p in partnerships:
    try:
        conn.execute("""
            INSERT OR REPLACE INTO academic_partnerships
            (partnership_id, country_code, foreign_institution, foreign_institution_type,
             chinese_institution, chinese_institution_type, partnership_type, status,
             military_involvement, strategic_concerns, technology_transfer_concerns,
             cooperation_areas, controversy_notes, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, p)
        count_p += 1
        print(f"  OK: {p[2]} <-> {p[4]}")
    except Exception as e:
        print(f"  ERROR: {p[0]} - {e}")

conn.commit()

# Step 4: Verification
print("\n" + "="*80)
print("IMPORT VERIFICATION")
print("="*80)

cur = conn.cursor()

for code, name in [('SI', 'Slovenia'), ('BG', 'Bulgaria'), ('HR', 'Croatia'),
                    ('GR', 'Greece'), ('AT', 'Austria')]:
    cur.execute(f"SELECT COUNT(*) FROM cultural_institutions WHERE country_code = '{code}'")
    ci_count = cur.fetchone()[0]

    cur.execute(f"SELECT COUNT(*) FROM academic_partnerships WHERE country_code = '{code}'")
    p_count = cur.fetchone()[0]

    cur.execute(f"SELECT COUNT(*) FROM academic_partnerships WHERE country_code = '{code}' AND military_involvement = 1")
    pla_count = cur.fetchone()[0]

    print(f"\n{name} ({code}):")
    print(f"  Confucius Institutes: {ci_count}")
    print(f"  Total Partnerships: {p_count}")
    print(f"  PLA-affiliated: {pla_count}")

# Overall totals
cur.execute("SELECT COUNT(*) FROM cultural_institutions")
total_ci = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM academic_partnerships")
total_p = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM academic_partnerships WHERE military_involvement = 1")
total_pla = cur.fetchone()[0]

print("\n" + "="*80)
print("OVERALL DATABASE TOTALS")
print("="*80)
print(f"Total Confucius Institutes: {total_ci}")
print(f"Total Academic Partnerships: {total_p}")
print(f"  - PLA-affiliated: {total_pla}")
print(f"  - Corporate: {total_p - total_pla}")

print(f"\n[SUCCESS] Imported {count_ci} CIs and {count_p} partnerships for 5 countries!")
conn.close()
