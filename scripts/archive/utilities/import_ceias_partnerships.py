#!/usr/bin/env python3
"""
Import CEIAS Partnerships - Romania, Czech Republic, Poland
High-priority PLA-affiliated and corporate partnerships
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(DB_PATH), timeout=60.0)

print("IMPORTING CEIAS PARTNERSHIPS...")

# Partnership data (partnership_id, country_code, foreign_institution, foreign_institution_type,
#                   chinese_institution, chinese_institution_type, partnership_type, status,
#                   military_involvement, strategic_concerns, technology_transfer_concerns,
#                   cooperation_areas, controversy_notes, source_url)

partnerships = [
    # ROMANIA - PLA-AFFILIATED
    ('RO_BIT_1', 'RO', 'Romanian University (unspecified)', 'university', 'Beijing Institute of Technology', 'university', 'research_cooperation', 'active', True, True, True, 'Engineering, defense technology', 'Seven Sons of National Defense - Very high risk classification by CEIAS', 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'),
    ('RO_BIT_2', 'RO', 'Romanian University (unspecified)', 'university', 'Beijing Institute of Technology', 'university', 'research_cooperation', 'active', True, True, True, 'Engineering, defense technology', 'Seven Sons of National Defense - Very high risk classification by CEIAS (second partnership)', 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'),
    ('RO_CRAIOVA_HEU', 'RO', 'University of Craiova', 'university', 'Harbin Engineering University', 'university', 'research_cooperation', 'active', True, True, True, 'Applied Mathematics, engineering, naval technology', 'Seven Sons of National Defense - Very high risk. China-Romania Research Center (2021)', 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'),
    ('RO_BALCESCU_PLA_AEU', 'RO', 'Nicolae Balcescu Land Forces Academy', 'military_academy', 'PLA Army Engineering University', 'military_university', 'military_cooperation', 'active', True, True, True, 'Military engineering, defense cooperation', 'Direct PLA institution cooperation - Extremely high risk', 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'),

    # ROMANIA - CORPORATE
    ('RO_CORP_HUAWEI_BUCHAREST', 'RO', 'Polytechnic University of Bucharest', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Seeds For Future program, HarmonyOS development, 5G research', '8th edition of Seeds For Future in 2021, HarmonyOS Developer Contest', 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'),

    # CZECH REPUBLIC - PLA-AFFILIATED
    ('CZ_BRNO_SEVEN_SONS', 'CZ', 'Brno University of Technology', 'university', 'Seven Sons Defense University (unspecified)', 'university', 'research_cooperation', 'active', True, True, True, 'Engineering, defense technology', 'Seven Sons of National Defense partnership - Very high risk per CEIAS', 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'),
    ('CZ_PARDUBICE_SEVEN_SONS', 'CZ', 'University of Pardubice', 'university', 'Seven Sons Defense University (unspecified)', 'university', 'research_cooperation', 'active', True, True, True, 'Engineering, chemical engineering, explosives', 'Seven Sons of National Defense partnership - Very high risk per CEIAS', 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'),
    ('CZ_CTU_SEVEN_SONS', 'CZ', 'Czech Technical University in Prague', 'university', 'Seven Sons Defense University (unspecified)', 'university', 'research_cooperation', 'active', True, True, True, 'Engineering, aerospace, defense applications', 'Seven Sons of National Defense partnership - Very high risk per CEIAS', 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'),
    ('CZ_UCT_TSINGHUA_NUCLEAR', 'CZ', 'University of Chemistry and Technology Prague', 'university', 'Tsinghua University - Institute of Nuclear and New Energy Technology', 'university', 'research_cooperation', 'active', True, True, True, 'Nuclear energy, nuclear weapons technology research', 'Military nuclear research involvement - Very high risk per CEIAS experts', 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'),

    # CZECH REPUBLIC - CORPORATE
    ('CZ_CORP_HUAWEI_MASARYK', 'CZ', 'Masaryk University', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Exchange and internship programs', 'Student exchange/internship program with Huawei', 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'),
    ('CZ_CORP_TELLHOW_MASARYK', 'CZ', 'Masaryk University', 'university', 'Tellhow', 'corporation', 'corporate_cooperation', 'active', True, True, True, 'Exchange and internship programs', 'Tellhow is military technology producer - High security concern', 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'),

    # POLAND - PLA-AFFILIATED
    ('PL_GDANSK_BIT', 'PL', 'University of Gdansk', 'university', 'Beijing Institute of Technology', 'university', 'research_cooperation', 'active', True, True, True, 'Engineering, materials science', 'Seven Sons of National Defense - Multiple Polish partnerships', 'https://ceias.eu/poland-extensive-ties-little-results/'),
    ('PL_POZNAN_BIT', 'PL', 'Adam Mickiewicz University (Poznan)', 'university', 'Beijing Institute of Technology', 'university', 'research_cooperation', 'active', True, True, True, 'Engineering, technology cooperation', 'Seven Sons of National Defense partnership', 'https://ceias.eu/poland-extensive-ties-little-results/'),
    ('PL_WUT_BIT', 'PL', 'Warsaw University of Technology', 'university', 'Beijing Institute of Technology', 'university', 'research_cooperation', 'active', True, True, True, 'Engineering, aerospace, defense applications', 'Seven Sons of National Defense partnership', 'https://ceias.eu/poland-extensive-ties-little-results/'),
    ('PL_IFTR_HIT', 'PL', 'Institute of Fundamental Technological Research (Polish Academy)', 'research_institute', 'Harbin Institute of Technology', 'university', 'research_cooperation', 'active', True, True, True, 'Aerospace, materials science, engineering', 'Seven Sons of National Defense - US Entity List institution', 'https://ceias.eu/poland-extensive-ties-little-results/'),
    ('PL_INP_BEIHANG', 'PL', 'Institute of Nuclear Physics (Polish Academy)', 'research_institute', 'Beihang University', 'university', 'research_cooperation', 'active', True, True, True, 'Nuclear physics, aerospace engineering', 'Seven Sons of National Defense (formerly Beijing University of Aeronautics and Astronautics)', 'https://ceias.eu/poland-extensive-ties-little-results/'),
    ('PL_WROCLAW_BEIHANG', 'PL', 'University of Wroclaw', 'university', 'Beihang University', 'university', 'research_cooperation', 'active', True, True, True, 'Aerospace engineering, materials science', 'Seven Sons of National Defense partnership', 'https://ceias.eu/poland-extensive-ties-little-results/'),
    ('PL_WUT_NUAA', 'PL', 'Warsaw University of Technology', 'university', 'Nanjing University of Aeronautics and Astronautics', 'university', 'research_cooperation', 'active', True, True, True, 'Aerospace engineering, aeronautics', 'Seven Sons of National Defense - Aerospace focus', 'https://ceias.eu/poland-extensive-ties-little-results/'),
    ('PL_WUT_NPU', 'PL', 'Warsaw University of Technology', 'university', 'Northwestern Polytechnical University', 'university', 'research_cooperation', 'active', True, True, True, 'Aerospace, materials science, defense applications', 'Seven Sons of National Defense - PLA Air Force affiliation', 'https://ceias.eu/poland-extensive-ties-little-results/'),

    # POLAND - CORPORATE
    ('PL_CORP_HUAWEI_WUT', 'PL', 'Warsaw University of Technology', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, '5G research, telecommunications, ICT training', 'Only Polish university acknowledging Huawei cooperation (per CEIAS), details not disclosed', 'https://ceias.eu/poland-extensive-ties-little-results/'),
]

print(f"Importing {len(partnerships)} partnerships...")
count = 0

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
        count += 1
        print(f"  OK: {p[2]} <-> {p[4]}")
    except Exception as e:
        print(f"  ERROR: {p[0]} - {e}")

conn.commit()
print(f"\nImported {count} partnerships, committed to database")

# Verification
cur = conn.cursor()

print("\n" + "="*80)
print("VERIFICATION")
print("="*80)

for country, name in [('RO', 'Romania'), ('CZ', 'Czech Republic'), ('PL', 'Poland')]:
    cur.execute(f"SELECT COUNT(*) FROM academic_partnerships WHERE country_code = '{country}'")
    total = cur.fetchone()[0]

    cur.execute(f"SELECT COUNT(*) FROM academic_partnerships WHERE country_code = '{country}' AND military_involvement = 1")
    pla = cur.fetchone()[0]

    cur.execute(f"SELECT COUNT(*) FROM academic_partnerships WHERE country_code = '{country}' AND chinese_institution_type = 'corporation'")
    corp = cur.fetchone()[0]

    print(f"\n{name}:")
    print(f"  Total partnerships: {total}")
    print(f"  PLA-affiliated: {pla}")
    print(f"  Corporate: {corp}")

# Overall totals
cur.execute("SELECT COUNT(*) FROM academic_partnerships")
total_partnerships = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM academic_partnerships WHERE military_involvement = 1")
total_pla = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM cultural_institutions")
total_ci = cur.fetchone()[0]

print(f"\n" + "="*80)
print("OVERALL CEIAS DATA IN DATABASE")
print("="*80)
print(f"Confucius Institutes: {total_ci}")
print(f"Academic Partnerships: {total_partnerships}")
print(f"  - PLA-affiliated: {total_pla}")
print(f"  - Corporate: {total_partnerships - total_pla}")

print("\n[SUCCESS] CEIAS partnership integration complete!")
conn.close()
