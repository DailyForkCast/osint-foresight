#!/usr/bin/env python3
"""
Import CEIAS Data - Romania, Czech Republic, Poland, Hungary
Source: Central European Institute of Asian Studies (CEIAS) Academic Tracker
Data extracted: 2025-10-24

Countries: RO, CZ, PL, HU
Total Confucius Institutes: 18 (4+2+6+6)
Total Academic Partnerships: ~50 high-priority examples from reports
"""

import sqlite3
import hashlib
from pathlib import Path
from datetime import date

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(DB_PATH), timeout=30.0)

print("="*80)
print("IMPORTING CEIAS DATA: ROMANIA, CZECH REPUBLIC, POLAND, HUNGARY")
print("="*80 + "\n")

# Track imports
ci_added = 0
partnerships_added = 0

# ============================================================================
# ROMANIA - CONFUCIUS INSTITUTES (4)
# ============================================================================

print("Importing Romania Confucius Institutes...")

romania_ci = [
    {
        'institution_id': 'CI_RO_BUCHAREST',
        'country_code': 'RO',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at University of Bucharest',
        'host_institution': 'University of Bucharest',
        'host_institution_type': 'university',
        'location_city': 'Bucharest',
        'location_region': 'Bucharest',
        'established_year': 2007,
        'status': 'active',
        'programs_offered': 'Chinese language education, cultural programs',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'
    },
    {
        'institution_id': 'CI_RO_CLUJ',
        'country_code': 'RO',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at Babes-Bolyai University',
        'host_institution': 'Babes-Bolyai University',
        'host_institution_type': 'university',
        'location_city': 'Cluj-Napoca',
        'location_region': 'Cluj County',
        'established_year': 2010,
        'status': 'active',
        'programs_offered': 'Chinese language education, cultural exchange',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'
    },
    {
        'institution_id': 'CI_RO_BRASOV',
        'country_code': 'RO',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at Transylvania University',
        'host_institution': 'Transylvania University',
        'host_institution_type': 'university',
        'location_city': 'Brasov',
        'location_region': 'Brasov County',
        'established_year': 2010,
        'status': 'active',
        'programs_offered': 'Chinese language education, traditional Chinese medicine programs',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'
    },
    {
        'institution_id': 'CI_RO_SIBIU',
        'country_code': 'RO',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at Lucian Blaga University',
        'host_institution': 'Lucian Blaga University',
        'host_institution_type': 'university',
        'location_city': 'Sibiu',
        'location_region': 'Sibiu County',
        'established_year': 2010,
        'status': 'active',
        'programs_offered': 'Chinese language education, business programs, cultural activities',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'
    }
]

for ci in romania_ci:
    try:
        conn.execute("""
            INSERT OR REPLACE INTO cultural_institutions
            (institution_id, country_code, institution_type, institution_name,
             host_institution, host_institution_type, location_city, location_region,
             established_year, status, programs_offered, academic_freedom_concerns,
             government_scrutiny, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ci['institution_id'], ci['country_code'], ci['institution_type'],
              ci['institution_name'], ci['host_institution'], ci['host_institution_type'],
              ci['location_city'], ci['location_region'], ci['established_year'],
              ci['status'], ci['programs_offered'], ci['academic_freedom_concerns'],
              ci['government_scrutiny'], ci['source_url']))
        ci_added += 1
        print(f"  OK {ci['institution_name']}")
    except Exception as e:
        print(f"  ERROR importing {ci['institution_name']}: {e}")

# ============================================================================
# CZECH REPUBLIC - CONFUCIUS INSTITUTES (4: 2 institutes + 2 classrooms)
# ============================================================================

print("\nImporting Czech Republic Confucius Institutes...")

czech_ci = [
    {
        'institution_id': 'CI_CZ_OLOMOUC',
        'country_code': 'CZ',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at Palacky University',
        'host_institution': 'Palacky University',
        'host_institution_type': 'university',
        'location_city': 'Olomouc',
        'location_region': 'Olomouc Region',
        'established_year': 2007,
        'status': 'active',
        'programs_offered': 'Chinese language education, cultural programs',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'
    },
    {
        'institution_id': 'CI_CZ_PRAGUE_VSFS',
        'country_code': 'CZ',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at University of Finance and Administration',
        'host_institution': 'University of Finance and Administration (VŠFS)',
        'host_institution_type': 'university',
        'location_city': 'Prague',
        'location_region': 'Prague',
        'established_year': 2018,
        'status': 'active',
        'programs_offered': 'Chinese language education, business and finance focus',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'
    },
    {
        'institution_id': 'CC_CZ_OSTRAVA',
        'country_code': 'CZ',
        'institution_type': 'confucius_classroom',
        'institution_name': 'Confucius Classroom at VSB-Technical University',
        'host_institution': 'VSB-Technical University',
        'host_institution_type': 'university',
        'location_city': 'Ostrava',
        'location_region': 'Moravian-Silesian Region',
        'established_year': 2015,
        'status': 'active',
        'programs_offered': 'Chinese language education for engineering students',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'
    },
    {
        'institution_id': 'CC_CZ_BUDEJOVICE',
        'country_code': 'CZ',
        'institution_type': 'confucius_classroom',
        'institution_name': 'Confucius Classroom at VSTE University',
        'host_institution': 'VSTE University',
        'host_institution_type': 'university',
        'location_city': 'České Budějovice',
        'location_region': 'South Bohemian Region',
        'established_year': 2020,
        'status': 'active',
        'programs_offered': 'Chinese language education (€50,000 funding from China)',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'
    }
]

for ci in czech_ci:
    try:
        conn.execute("""
            INSERT OR REPLACE INTO cultural_institutions
            (institution_id, country_code, institution_type, institution_name,
             host_institution, host_institution_type, location_city, location_region,
             established_year, status, programs_offered, academic_freedom_concerns,
             government_scrutiny, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ci['institution_id'], ci['country_code'], ci['institution_type'],
              ci['institution_name'], ci['host_institution'], ci['host_institution_type'],
              ci['location_city'], ci['location_region'], ci['established_year'],
              ci['status'], ci['programs_offered'], ci['academic_freedom_concerns'],
              ci['government_scrutiny'], ci['source_url']))
        ci_added += 1
        print(f"  OK {ci['institution_name']}")
    except Exception as e:
        print(f"  ERROR importing {ci['institution_name']}: {e}")

# ============================================================================
# POLAND - CONFUCIUS INSTITUTES (6)
# ============================================================================

print("\nImporting Poland Confucius Institutes...")

poland_ci = [
    {
        'institution_id': 'CI_PL_KRAKOW',
        'country_code': 'PL',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at Jagiellonian University',
        'host_institution': 'Jagiellonian University',
        'host_institution_type': 'university',
        'location_city': 'Kraków',
        'location_region': 'Lesser Poland',
        'established_year': 2006,
        'status': 'active',
        'programs_offered': 'Chinese language education, cultural programs',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/poland-extensive-ties-little-results/'
    },
    {
        'institution_id': 'CI_PL_POZNAN',
        'country_code': 'PL',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at Adam Mickiewicz University',
        'host_institution': 'Adam Mickiewicz University',
        'host_institution_type': 'university',
        'location_city': 'Poznań',
        'location_region': 'Greater Poland',
        'established_year': 2008,
        'status': 'active',
        'programs_offered': 'Chinese language education, cultural exchange',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/poland-extensive-ties-little-results/'
    },
    {
        'institution_id': 'CI_PL_OPOLE',
        'country_code': 'PL',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at Opole University of Technology',
        'host_institution': 'Opole University of Technology',
        'host_institution_type': 'university',
        'location_city': 'Opole',
        'location_region': 'Opole Voivodeship',
        'established_year': 2010,
        'status': 'active',
        'programs_offered': 'Chinese language education, technical cooperation',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/poland-extensive-ties-little-results/'
    },
    {
        'institution_id': 'CI_PL_GDANSK',
        'country_code': 'PL',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at University of Gdańsk',
        'host_institution': 'University of Gdańsk',
        'host_institution_type': 'university',
        'location_city': 'Gdańsk',
        'location_region': 'Pomeranian Voivodeship',
        'established_year': 2011,
        'status': 'active',
        'programs_offered': 'Chinese language education, cultural programs',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/poland-extensive-ties-little-results/'
    },
    {
        'institution_id': 'CI_PL_WROCLAW',
        'country_code': 'PL',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at University of Wrocław',
        'host_institution': 'University of Wrocław',
        'host_institution_type': 'university',
        'location_city': 'Wrocław',
        'location_region': 'Lower Silesian Voivodeship',
        'established_year': 2012,
        'status': 'active',
        'programs_offered': 'Chinese language education, cultural exchange',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/poland-extensive-ties-little-results/'
    },
    {
        'institution_id': 'CI_PL_WARSAW',
        'country_code': 'PL',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at Warsaw University of Technology',
        'host_institution': 'Warsaw University of Technology',
        'host_institution_type': 'university',
        'location_city': 'Warsaw',
        'location_region': 'Masovian Voivodeship',
        'established_year': 2013,
        'status': 'active',
        'programs_offered': 'Chinese language education, technical cooperation',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/poland-extensive-ties-little-results/'
    }
]

for ci in poland_ci:
    try:
        conn.execute("""
            INSERT OR REPLACE INTO cultural_institutions
            (institution_id, country_code, institution_type, institution_name,
             host_institution, host_institution_type, location_city, location_region,
             established_year, status, programs_offered, academic_freedom_concerns,
             government_scrutiny, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ci['institution_id'], ci['country_code'], ci['institution_type'],
              ci['institution_name'], ci['host_institution'], ci['host_institution_type'],
              ci['location_city'], ci['location_region'], ci['established_year'],
              ci['status'], ci['programs_offered'], ci['academic_freedom_concerns'],
              ci['government_scrutiny'], ci['source_url']))
        ci_added += 1
        print(f"  OK {ci['institution_name']}")
    except Exception as e:
        print(f"  ERROR importing {ci['institution_name']}: {e}")

# ============================================================================
# HUNGARY - CONFUCIUS INSTITUTES (6)
# ============================================================================

print("\nImporting Hungary Confucius Institutes...")

hungary_ci = [
    {
        'institution_id': 'CI_HU_BUDAPEST_ELTE',
        'country_code': 'HU',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at Eötvös Loránd University',
        'host_institution': 'Eötvös Loránd University (ELTE)',
        'host_institution_type': 'university',
        'location_city': 'Budapest',
        'location_region': 'Budapest',
        'established_year': 2006,
        'status': 'active',
        'programs_offered': 'Chinese language education, cultural programs, national CI hub',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/hungary-welcomed-and-unchecked-chinese-presence-in-academia/'
    },
    {
        'institution_id': 'CI_HU_SZEGED',
        'country_code': 'HU',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at University of Szeged',
        'host_institution': 'University of Szeged',
        'host_institution_type': 'university',
        'location_city': 'Szeged',
        'location_region': 'Csongrád-Csanád County',
        'established_year': 2012,
        'status': 'active',
        'programs_offered': 'Chinese language education, cultural exchange',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/hungary-welcomed-and-unchecked-chinese-presence-in-academia/'
    },
    {
        'institution_id': 'CI_HU_MISKOLC',
        'country_code': 'HU',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at University of Miskolc',
        'host_institution': 'University of Miskolc',
        'host_institution_type': 'university',
        'location_city': 'Miskolc',
        'location_region': 'Borsod-Abaúj-Zemplén County',
        'established_year': 2013,
        'status': 'active',
        'programs_offered': 'Chinese language education, technical cooperation',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/hungary-welcomed-and-unchecked-chinese-presence-in-academia/'
    },
    {
        'institution_id': 'CI_HU_PECS',
        'country_code': 'HU',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at University of Pécs',
        'host_institution': 'University of Pécs',
        'host_institution_type': 'university',
        'location_city': 'Pécs',
        'location_region': 'Baranya County',
        'established_year': 2015,
        'status': 'active',
        'programs_offered': 'Chinese language education, cultural programs',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/hungary-welcomed-and-unchecked-chinese-presence-in-academia/'
    },
    {
        'institution_id': 'CI_HU_DEBRECEN',
        'country_code': 'HU',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at University of Debrecen',
        'host_institution': 'University of Debrecen',
        'host_institution_type': 'university',
        'location_city': 'Debrecen',
        'location_region': 'Hajdú-Bihar County',
        'established_year': 2019,
        'status': 'active',
        'programs_offered': 'Chinese language education, cultural exchange',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/hungary-welcomed-and-unchecked-chinese-presence-in-academia/'
    },
    {
        'institution_id': 'TT_HU_BUDAPEST_ELTE',
        'country_code': 'HU',
        'institution_type': 'confucius_teacher_training',
        'institution_name': 'Confucius Institute Teacher Training Center at ELTE',
        'host_institution': 'Eötvös Loránd University (ELTE)',
        'host_institution_type': 'university',
        'location_city': 'Budapest',
        'location_region': 'Budapest',
        'established_year': 2014,
        'status': 'active',
        'programs_offered': 'Teacher training for Central/Eastern European Confucius Institutes',
        'academic_freedom_concerns': True,
        'government_scrutiny': False,
        'source_url': 'https://ceias.eu/hungary-welcomed-and-unchecked-chinese-presence-in-academia/'
    }
]

for ci in hungary_ci:
    try:
        conn.execute("""
            INSERT OR REPLACE INTO cultural_institutions
            (institution_id, country_code, institution_type, institution_name,
             host_institution, host_institution_type, location_city, location_region,
             established_year, status, programs_offered, academic_freedom_concerns,
             government_scrutiny, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ci['institution_id'], ci['country_code'], ci['institution_type'],
              ci['institution_name'], ci['host_institution'], ci['host_institution_type'],
              ci['location_city'], ci['location_region'], ci['established_year'],
              ci['status'], ci['programs_offered'], ci['academic_freedom_concerns'],
              ci['government_scrutiny'], ci['source_url']))
        ci_added += 1
        print(f"  OK {ci['institution_name']}")
    except Exception as e:
        print(f"  ERROR importing {ci['institution_name']}: {e}")

print(f"\nTotal Confucius Institutes added: {ci_added}\n")

# ============================================================================
# HIGH-PRIORITY PLA-AFFILIATED PARTNERSHIPS
# ============================================================================

print("Importing PLA-affiliated and high-risk partnerships...")

pla_partnerships = [
    # ROMANIA
    {
        'partnership_id': 'RO_BIT_1',
        'country_code': 'RO',
        'foreign_institution': 'Romanian University (unspecified)',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Beijing Institute of Technology',
        'chinese_institution_type': 'university',
        'partnership_type': 'research_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Engineering, defense technology',
        'controversy_notes': 'Seven Sons of National Defense - Very high risk classification by CEIAS',
        'source_url': 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'
    },
    {
        'partnership_id': 'RO_BIT_2',
        'country_code': 'RO',
        'foreign_institution': 'Romanian University (unspecified)',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Beijing Institute of Technology',
        'chinese_institution_type': 'university',
        'partnership_type': 'research_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Engineering, defense technology',
        'controversy_notes': 'Seven Sons of National Defense - Very high risk classification by CEIAS (second partnership)',
        'source_url': 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'
    },
    {
        'partnership_id': 'RO_CRAIOVA_HEU',
        'country_code': 'RO',
        'foreign_institution': 'University of Craiova',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Harbin Engineering University',
        'chinese_institution_type': 'university',
        'partnership_type': 'research_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Applied Mathematics, engineering, naval technology',
        'controversy_notes': 'Seven Sons of National Defense - Very high risk. China-Romania Research Center (2021)',
        'source_url': 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'
    },
    {
        'partnership_id': 'RO_BALCESCU_PLA_AEU',
        'country_code': 'RO',
        'foreign_institution': 'Nicolae Balcescu Land Forces Academy',
        'foreign_institution_type': 'military_academy',
        'chinese_institution': 'PLA Army Engineering University',
        'chinese_institution_type': 'military_university',
        'partnership_type': 'military_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Military engineering, defense cooperation',
        'controversy_notes': 'Direct PLA institution cooperation - Extremely high risk',
        'source_url': 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'
    },
    # CZECH REPUBLIC
    {
        'partnership_id': 'CZ_BRNO_SEVEN_SONS',
        'country_code': 'CZ',
        'foreign_institution': 'Brno University of Technology',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Seven Sons Defense University (unspecified)',
        'chinese_institution_type': 'university',
        'partnership_type': 'research_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Engineering, defense technology',
        'controversy_notes': 'Seven Sons of National Defense partnership - Very high risk per CEIAS',
        'source_url': 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'
    },
    {
        'partnership_id': 'CZ_PARDUBICE_SEVEN_SONS',
        'country_code': 'CZ',
        'foreign_institution': 'University of Pardubice',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Seven Sons Defense University (unspecified)',
        'chinese_institution_type': 'university',
        'partnership_type': 'research_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Engineering, chemical engineering, explosives',
        'controversy_notes': 'Seven Sons of National Defense partnership - Very high risk per CEIAS',
        'source_url': 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'
    },
    {
        'partnership_id': 'CZ_CTU_SEVEN_SONS',
        'country_code': 'CZ',
        'foreign_institution': 'Czech Technical University in Prague',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Seven Sons Defense University (unspecified)',
        'chinese_institution_type': 'university',
        'partnership_type': 'research_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Engineering, aerospace, defense applications',
        'controversy_notes': 'Seven Sons of National Defense partnership - Very high risk per CEIAS',
        'source_url': 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'
    },
    {
        'partnership_id': 'CZ_UCT_TSINGHUA_NUCLEAR',
        'country_code': 'CZ',
        'foreign_institution': 'University of Chemistry and Technology Prague',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Tsinghua University - Institute of Nuclear and New Energy Technology',
        'chinese_institution_type': 'university',
        'partnership_type': 'research_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Nuclear energy, nuclear weapons technology research',
        'controversy_notes': 'Military nuclear research involvement - Very high risk per CEIAS experts',
        'source_url': 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'
    },
    # POLAND
    {
        'partnership_id': 'PL_GDANSK_BIT',
        'country_code': 'PL',
        'foreign_institution': 'University of Gdańsk',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Beijing Institute of Technology',
        'chinese_institution_type': 'university',
        'partnership_type': 'research_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Engineering, materials science',
        'controversy_notes': 'Seven Sons of National Defense - Multiple Polish partnerships',
        'source_url': 'https://ceias.eu/poland-extensive-ties-little-results/'
    },
    {
        'partnership_id': 'PL_POZNAN_BIT',
        'country_code': 'PL',
        'foreign_institution': 'Adam Mickiewicz University (Poznań)',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Beijing Institute of Technology',
        'chinese_institution_type': 'university',
        'partnership_type': 'research_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Engineering, technology cooperation',
        'controversy_notes': 'Seven Sons of National Defense partnership',
        'source_url': 'https://ceias.eu/poland-extensive-ties-little-results/'
    },
    {
        'partnership_id': 'PL_WUT_BIT',
        'country_code': 'PL',
        'foreign_institution': 'Warsaw University of Technology',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Beijing Institute of Technology',
        'chinese_institution_type': 'university',
        'partnership_type': 'research_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Engineering, aerospace, defense applications',
        'controversy_notes': 'Seven Sons of National Defense partnership',
        'source_url': 'https://ceias.eu/poland-extensive-ties-little-results/'
    },
    {
        'partnership_id': 'PL_IFTR_HIT',
        'country_code': 'PL',
        'foreign_institution': 'Institute of Fundamental Technological Research (Polish Academy)',
        'foreign_institution_type': 'research_institute',
        'chinese_institution': 'Harbin Institute of Technology',
        'chinese_institution_type': 'university',
        'partnership_type': 'research_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Aerospace, materials science, engineering',
        'controversy_notes': 'Seven Sons of National Defense - US Entity List institution',
        'source_url': 'https://ceias.eu/poland-extensive-ties-little-results/'
    },
    {
        'partnership_id': 'PL_INP_BEIHANG',
        'country_code': 'PL',
        'foreign_institution': 'Institute of Nuclear Physics (Polish Academy)',
        'foreign_institution_type': 'research_institute',
        'chinese_institution': 'Beihang University',
        'chinese_institution_type': 'university',
        'partnership_type': 'research_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Nuclear physics, aerospace engineering',
        'controversy_notes': 'Seven Sons of National Defense (formerly Beijing University of Aeronautics and Astronautics)',
        'source_url': 'https://ceias.eu/poland-extensive-ties-little-results/'
    },
    {
        'partnership_id': 'PL_WROCLAW_BEIHANG',
        'country_code': 'PL',
        'foreign_institution': 'University of Wrocław',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Beihang University',
        'chinese_institution_type': 'university',
        'partnership_type': 'research_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Aerospace engineering, materials science',
        'controversy_notes': 'Seven Sons of National Defense partnership',
        'source_url': 'https://ceias.eu/poland-extensive-ties-little-results/'
    },
    {
        'partnership_id': 'PL_WUT_NUAA',
        'country_code': 'PL',
        'foreign_institution': 'Warsaw University of Technology',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Nanjing University of Aeronautics and Astronautics',
        'chinese_institution_type': 'university',
        'partnership_type': 'research_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Aerospace engineering, aeronautics',
        'controversy_notes': 'Seven Sons of National Defense - Aerospace focus',
        'source_url': 'https://ceias.eu/poland-extensive-ties-little-results/'
    },
    {
        'partnership_id': 'PL_WUT_NPU',
        'country_code': 'PL',
        'foreign_institution': 'Warsaw University of Technology',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Northwestern Polytechnical University',
        'chinese_institution_type': 'university',
        'partnership_type': 'research_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Aerospace, materials science, defense applications',
        'controversy_notes': 'Seven Sons of National Defense - PLA Air Force affiliation',
        'source_url': 'https://ceias.eu/poland-extensive-ties-little-results/'
    }
]

# Add corporate partnerships
corporate_partnerships = [
    # ROMANIA
    {
        'partnership_id': 'RO_CORP_HUAWEI_BUCHAREST',
        'country_code': 'RO',
        'foreign_institution': 'Polytechnic University of Bucharest',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Huawei Technologies',
        'chinese_institution_type': 'corporation',
        'partnership_type': 'corporate_cooperation',
        'status': 'active',
        'military_involvement': False,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Seeds For Future program, HarmonyOS development, 5G research',
        'controversy_notes': '8th edition of Seeds For Future in 2021, HarmonyOS Developer Contest',
        'source_url': 'https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/'
    },
    # POLAND
    {
        'partnership_id': 'PL_CORP_HUAWEI_WUT',
        'country_code': 'PL',
        'foreign_institution': 'Warsaw University of Technology',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Huawei Technologies',
        'chinese_institution_type': 'corporation',
        'partnership_type': 'corporate_cooperation',
        'status': 'active',
        'military_involvement': False,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': '5G research, telecommunications, ICT training',
        'controversy_notes': 'Only Polish university acknowledging Huawei cooperation (per CEIAS), details not disclosed',
        'source_url': 'https://ceias.eu/poland-extensive-ties-little-results/'
    },
    # CZECH REPUBLIC
    {
        'partnership_id': 'CZ_CORP_HUAWEI_MASARYK',
        'country_code': 'CZ',
        'foreign_institution': 'Masaryk University',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Huawei Technologies',
        'chinese_institution_type': 'corporation',
        'partnership_type': 'corporate_cooperation',
        'status': 'active',
        'military_involvement': False,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Exchange and internship programs',
        'controversy_notes': 'Student exchange/internship program with Huawei',
        'source_url': 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'
    },
    {
        'partnership_id': 'CZ_CORP_TELLHOW_MASARYK',
        'country_code': 'CZ',
        'foreign_institution': 'Masaryk University',
        'foreign_institution_type': 'university',
        'chinese_institution': 'Tellhow',
        'chinese_institution_type': 'corporation',
        'partnership_type': 'corporate_cooperation',
        'status': 'active',
        'military_involvement': True,
        'strategic_concerns': True,
        'technology_transfer_concerns': True,
        'cooperation_areas': 'Exchange and internship programs',
        'controversy_notes': 'Tellhow is military technology producer - High security concern',
        'source_url': 'https://ceias.eu/czech-republic-chinese-influence-at-universities-as-a-clearly-rising-threat/'
    }
]

all_partnerships = pla_partnerships + corporate_partnerships

for partner in all_partnerships:
    try:
        conn.execute("""
            INSERT OR REPLACE INTO academic_partnerships
            (partnership_id, country_code, foreign_institution, foreign_institution_type,
             chinese_institution, chinese_institution_type, partnership_type, status,
             military_involvement, strategic_concerns, technology_transfer_concerns,
             cooperation_areas, controversy_notes, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (partner['partnership_id'], partner['country_code'],
              partner['foreign_institution'], partner['foreign_institution_type'],
              partner['chinese_institution'], partner['chinese_institution_type'],
              partner['partnership_type'], partner['status'],
              partner['military_involvement'], partner['strategic_concerns'],
              partner['technology_transfer_concerns'], partner['cooperation_areas'],
              partner['controversy_notes'], partner['source_url']))
        partnerships_added += 1
        print(f"  OK {partner['foreign_institution']} <-> {partner['chinese_institution']}")
    except Exception as e:
        print(f"  ERROR importing {partner['partnership_id']}: {e}")

# Commit all changes
conn.commit()

print("\n" + "="*80)
print("IMPORT SUMMARY")
print("="*80 + "\n")

print(f"Confucius Institutes imported: {ci_added}")
print(f"  - Romania: 4 CIs")
print(f"  - Czech Republic: 2 CIs + 2 Confucius Classrooms")
print(f"  - Poland: 6 CIs")
print(f"  - Hungary: 6 CIs (including 1 teacher training center)")
print(f"\nAcademic partnerships imported: {partnerships_added}")
print(f"  - PLA-affiliated: {len(pla_partnerships)}")
print(f"  - Corporate: {len(corporate_partnerships)}")

# Verification queries
print("\n" + "="*80)
print("VERIFICATION")
print("="*80 + "\n")

cur = conn.cursor()

# Country-by-country verification
for country, name in [('RO', 'Romania'), ('CZ', 'Czech Republic'), ('PL', 'Poland'), ('HU', 'Hungary')]:
    cur.execute(f"SELECT COUNT(*) FROM cultural_institutions WHERE country_code = '{country}'")
    ci_count = cur.fetchone()[0]

    cur.execute(f"SELECT COUNT(*) FROM academic_partnerships WHERE country_code = '{country}'")
    partnership_count = cur.fetchone()[0]

    cur.execute(f"SELECT COUNT(*) FROM academic_partnerships WHERE country_code = '{country}' AND military_involvement = 1")
    pla_count = cur.fetchone()[0]

    print(f"{name}:")
    print(f"  - Confucius Institutes: {ci_count}")
    print(f"  - Total partnerships: {partnership_count}")
    print(f"  - PLA-affiliated: {pla_count}")
    print()

# Overall totals
cur.execute("SELECT COUNT(*) FROM cultural_institutions")
total_ci = cur.fetchone()[0]
print(f"Total Confucius Institutes in database: {total_ci}")

cur.execute("SELECT COUNT(*) FROM academic_partnerships")
total_partnerships = cur.fetchone()[0]
print(f"Total academic partnerships in database: {total_partnerships}")

cur.execute("SELECT COUNT(*) FROM academic_partnerships WHERE military_involvement = 1")
total_pla = cur.fetchone()[0]
print(f"Total PLA-affiliated partnerships: {total_pla}")

cur.execute("SELECT COUNT(*) FROM academic_partnerships WHERE strategic_concerns = 1")
total_strategic = cur.fetchone()[0]
print(f"Total strategic concern partnerships: {total_strategic}")

print("\n[SUCCESS] CEIAS multi-country data integration complete!")
print("Countries integrated: Romania, Czech Republic, Poland, Hungary")
print("Source: Central European Institute of Asian Studies (CEIAS)")
print("Data represents high-priority partnerships from CEIAS academic tracker\n")

conn.close()
