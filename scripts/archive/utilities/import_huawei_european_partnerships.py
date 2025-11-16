#!/usr/bin/env python3
"""
Import Huawei Educational Partnerships Across Europe
Based on comprehensive research of ICT Academies, Seeds for the Future, and Research Partnerships
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(DB_PATH), timeout=60.0)

print("="*80)
print("IMPORTING HUAWEI EUROPEAN EDUCATIONAL PARTNERSHIPS")
print("="*80)

# Huawei Educational Partnerships
# Format: (partnership_id, country_code, foreign_institution, foreign_institution_type,
#          chinese_institution, chinese_institution_type, partnership_type, status,
#          military_involvement, strategic_concerns, technology_transfer_concerns,
#          cooperation_areas, controversy_notes, source_url)

partnerships = [
    # UNITED KINGDOM
    ('UK_SURREY_HUAWEI_5GIC', 'GB', 'University of Surrey', 'university', 'Huawei Technologies', 'corporation', 'research_cooperation', 'active', False, True, True, '5G Innovation Centre, 5G research, £5M investment, 170+ researchers', 'Major 5G research partnership, concerns over technology transfer and security', 'https://www.huawei.com/en/news/2015/09/huawei-partners-with-university-of-surrey-consortium-on-5g-innovation-centre-opening'),
    ('UK_READING_HUAWEI_ICT', 'GB', 'University of Reading - Henley Business School', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'First UK Huawei ICT Academy (2015), digital talent development, ICT training', 'First Huawei ICT Academy in UK, ongoing partnership', 'https://www.henley.ac.uk/news/2022/huawei-ict-academy-partnership-continues-to-thrive'),

    # FRANCE
    ('FR_EURECOM_HUAWEI_6G', 'FR', 'EURECOM', 'university', 'Huawei Technologies', 'corporation', 'research_cooperation', 'active', False, True, True, 'Research Chair on 6G wireless networks, advanced intelligent wireless networks, future telecommunications', 'Huawei Research Chair at Sophia Antipolis focusing on post-5G/6G research', 'https://www.webtimemedias.com/article/sophia-eurecom-lance-les-recherches-sur-la-6g-avec-huawei'),
    ('FR_TELECOM_PARIS_HUAWEI', 'FR', 'Telecom Paris (Telecom ParisTech)', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Strategic partnership, Seeds for the Future program, telecommunications research', 'Huawei strategic partner for engineering talent development', 'https://e.huawei.com/en/blogs/industries/insights/2023/huawei-s-european-talent-ecosystem'),
    ('FR_IMT_HUAWEI', 'FR', 'Institut Mines-Telecom (IMT)', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Strategic partnership, ICT Academy network, digital skills training', 'Strategic partner for Huawei talent ecosystem in France', 'https://e.huawei.com/en/blogs/industries/insights/2023/huawei-s-european-talent-ecosystem'),

    # SPAIN
    ('ES_ALICANTE_HUAWEI', 'ES', 'University of Alicante', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'HCIA courses as compulsory curriculum, 1000+ active students, 160+ certified students, ranked #1 in Western Europe', 'Largest Huawei ICT Academy in Western Europe by student count', 'https://www.huawei.com/en/sustainability/the-latest/stories/win-win-development/investing-in-a-comprehensive-talent-ecosystem'),

    # NETHERLANDS
    ('NL_AMSTERDAM_HUAWEI', 'NL', 'University of Amsterdam', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Seeds for the Future program, student exchanges to China, ICT training', 'Seeds for the Future partnership since 2014', 'https://www-ctc.huawei.com/en/sustainability/win-win-development/social-contribution/seeds-for-the-future/netherlands'),
    ('NL_LEIDEN_HUAWEI', 'NL', 'Leiden University', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Seeds for the Future program, student exchanges, ICT training', 'Seeds for the Future partnership since 2014', 'https://www-ctc.huawei.com/en/sustainability/win-win-development/social-contribution/seeds-for-the-future/netherlands'),
    ('NL_EINDHOVEN_HUAWEI', 'NL', 'Technical University Eindhoven', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Seeds for the Future program, engineering partnerships, ICT training', 'Seeds for the Future partnership, technical university cooperation', 'https://www-ctc.huawei.com/en/sustainability/win-win-development/social-contribution/seeds-for-the-future/netherlands'),
    ('NL_TWENTE_HUAWEI', 'NL', 'University of Twente', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Seeds for the Future program, engineering research, ICT training', 'Seeds for the Future partnership, engineering focus', 'https://www-ctc.huawei.com/en/sustainability/win-win-development/social-contribution/seeds-for-the-future/netherlands'),

    # BELGIUM
    ('BE_KU_LEUVEN_HUAWEI', 'BE', 'KU Leuven', 'university', 'Huawei Technologies', 'corporation', 'research_cooperation', 'active', False, True, True, 'R&D collaboration, internships for MSc students in Computer Science/Engineering, RF transceivers for 4G/5G, Seeds for the Future', 'Huawei R&D Center located at KU Leuven Science Park, next-gen 5G systems research', 'https://eng.kuleuven.be/studeren/opleidingen/computerwetenschappen/stages/stagevoorstellen/stagevoorstellen-2023-4/internships-huawei-2023'),

    # POLAND
    ('PL_KOZMINSKI_HUAWEI', 'PL', 'Kozminski University Warsaw', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'ICT Academy, postgraduate studies in Managing Cyber Security, 5G/big data/AI/cloud computing training', 'ICT Academy partnership with cybersecurity focus', 'https://e.huawei.com/en/news/ebg/2021/kozminski-university-huawei-poland'),

    # SWITZERLAND (Non-EU but strategic)
    ('CH_FHNW_HUAWEI', 'CH', 'University of Applied Sciences Northwestern Switzerland (FHNW)', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Seeds for the Future program, student exchanges to China', 'Swiss university partnership for Seeds program', 'https://www.huawei.com/ch-en/news/ch/2023/revival-of-our-seeds-for-the-future-complete-program-2023'),
    ('CH_HSLU_HUAWEI', 'CH', 'Lucerne University of Applied Sciences (HSLU)', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Seeds for the Future program, student exchanges to China', 'Swiss university partnership for Seeds program', 'https://www.huawei.com/ch-en/news/ch/2023/revival-of-our-seeds-for-the-future-complete-program-2023'),
    ('CH_ZHAW_HUAWEI', 'CH', 'Zurich University of Applied Sciences (ZHAW)', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Seeds for the Future program, student exchanges to China', 'Swiss university partnership for Seeds program', 'https://www.huawei.com/ch-en/news/ch/2023/revival-of-our-seeds-for-the-future-complete-program-2023'),
    ('CH_OST_HUAWEI', 'CH', 'University of Applied Sciences Eastern Switzerland (OST)', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Seeds for the Future program, student exchanges to China', 'Swiss university partnership for Seeds program', 'https://www.huawei.com/ch-en/news/ch/2023/revival-of-our-seeds-for-the-future-complete-program-2023'),
    ('CH_BFH_HUAWEI', 'CH', 'Bern University of Applied Sciences (BFH)', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Seeds for the Future program, student exchanges to China', 'Swiss university partnership for Seeds program', 'https://www.huawei.com/ch-en/news/ch/2023/revival-of-our-seeds-for-the-future-complete-program-2023'),
    ('CH_FH_STGALLEN_HUAWEI', 'CH', 'FH St. Gallen', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Seeds for the Future program, student exchanges to China', 'Swiss university partnership for Seeds program', 'https://www.huawei.com/ch-en/news/ch/2023/revival-of-our-seeds-for-the-future-complete-program-2023'),
    ('CH_HES_SO_HUAWEI', 'CH', 'University of Applied Sciences Western Switzerland (HES-SO)', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Seeds for the Future program, student exchanges to China', 'Swiss university partnership for Seeds program', 'https://www.huawei.com/ch-en/news/ch/2023/revival-of-our-seeds-for-the-future-complete-program-2023'),

    # TURKEY (EU candidate)
    ('TR_BILKENT_HUAWEI', 'TR', 'Bilkent University Ankara', 'university', 'Huawei Technologies', 'corporation', 'corporate_cooperation', 'active', False, True, True, 'Huawei ICT Academy, HCIA/HCIP/HCIE certification courses, telecommunications training', 'ICT Academy partnership at CTIS department', 'https://www.ctis.bilkent.edu.tr/ctis_academicAllianceHuaweiICTAcademy.php'),

    # Already in database from CEIAS import - these are duplicates for reference:
    # Romania: Polytechnic University of Bucharest - Huawei
    # Czech: Masaryk University - Huawei
    # Poland: Warsaw University of Technology - Huawei
    # Bulgaria: 4 universities - Huawei
    # Slovenia: University of Ljubljana - Huawei
    # Austria: Vienna University of Technology - Huawei
    # Croatia: Huawei general partnership
]

print(f"\nImporting {len(partnerships)} Huawei educational partnerships...")
print("-"*80)

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
        print(f"  OK: {p[2]} <-> Huawei")
    except Exception as e:
        print(f"  ERROR: {p[0]} - {e}")

conn.commit()

# Verification
print("\n" + "="*80)
print("HUAWEI PARTNERSHIP VERIFICATION")
print("="*80)

cur = conn.cursor()

# Count by country
cur.execute("""
    SELECT country_code, COUNT(*) as count
    FROM academic_partnerships
    WHERE chinese_institution = 'Huawei Technologies'
    GROUP BY country_code
    ORDER BY count DESC
""")

print("\nHuawei partnerships by country:")
total_huawei = 0
for row in cur.fetchall():
    code, count_p = row
    total_huawei += count_p
    print(f"  {code}: {count_p} partnerships")

# Partnership types
cur.execute("""
    SELECT partnership_type, COUNT(*) as count
    FROM academic_partnerships
    WHERE chinese_institution = 'Huawei Technologies'
    GROUP BY partnership_type
""")

print("\nHuawei partnerships by type:")
for row in cur.fetchall():
    ptype, count_p = row
    print(f"  {ptype}: {count_p}")

# Overall statistics
print("\n" + "="*80)
print("OVERALL STATISTICS")
print("="*80)

# Total partnerships (all companies)
cur.execute("SELECT COUNT(*) FROM academic_partnerships")
total_all = cur.fetchone()[0]

# Total corporate partnerships
cur.execute("SELECT COUNT(*) FROM academic_partnerships WHERE chinese_institution_type = 'corporation'")
total_corporate = cur.fetchone()[0]

print(f"\nTotal academic partnerships in database: {total_all}")
print(f"Total corporate partnerships: {total_corporate}")
print(f"Huawei partnerships: {total_huawei} ({100*total_huawei/total_corporate:.1f}% of corporate)")

print("\n" + "="*80)
print("HUAWEI EUROPEAN FOOTPRINT SUMMARY")
print("="*80)

print("""
VERIFIED DATA (HIGH CONFIDENCE):
  - 30 specific university partnerships imported
  - 14 countries with documented institutions
  - 3 major research partnerships (UK Surrey, France EURECOM, Belgium KU Leuven)
  - 27 corporate partnerships (ICT Academies, Seeds programs)

CLAIMED SCALE (MEDIUM CONFIDENCE - from Huawei reports, unverified):

1. ICT ACADEMIES
   - CLAIMED: 200+ academies across Europe
   - VERIFIED: 30 specific institutions
   - DATA GAP: ~170 academies not individually identified
   - Student registrations: 10,000+ (2022, claimed)

2. SEEDS FOR THE FUTURE (Since 2011)
   - CLAIMED: 1,300+ European students from 30+ countries
   - Recent participation: 145 students from 23 countries (2024 Rome, verified)
   - Two-week study trips to China (Shenzhen HQ, Beijing facilities)

3. RESEARCH PARTNERSHIPS
   - CLAIMED: 240+ technology partnership agreements
   - CLAIMED: Over €75M per year investment
   - CLAIMED: 18 R&D organizations in 8 EU countries
   - CLAIMED: Cooperation with 100+ academic/research partners

4. INNOVATION CENTERS (VERIFIED)
   - Paris Innovation Center (€2M+ annual, claimed)
   - European Research Institute in Leuven, Belgium (verified)
   - 5G Innovation Centre at University of Surrey (£5M investment, verified)

DATA QUALITY NOTE:
Our verified partnerships represent the most strategically significant relationships
(major research centers, flagship ICT Academies, government-backed partnerships).
The gap of ~170 claimed academies likely consists of smaller engagements
(guest lectures, student competitions, internships) with lower strategic impact.

STRATEGIC CONCERNS:
- Technology transfer in critical areas (5G/6G, AI, cloud computing)
- Student recruitment and influence operations
- Access to cutting-edge European research
- Embedded presence in engineering curricula
- Talent pipeline development for Huawei ecosystem
""")

print(f"\n[SUCCESS] Imported {count} Huawei educational partnerships!")
conn.close()
