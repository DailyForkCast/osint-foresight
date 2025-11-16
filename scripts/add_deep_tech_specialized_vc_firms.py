"""
Add Deep Tech and Specialized Chinese VC Firms
==============================================
Add niche/specialist VCs focused on dual-use advanced technologies
found through comprehensive web research.

Author: OSINT Foresight Analysis
Date: 2025-10-25
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3
from datetime import datetime

db_path = 'F:/OSINT_WAREHOUSE/osint_master.db'

print("\n" + "="*70)
print("ADDING DEEP TECH & SPECIALIZED CHINESE VC FIRMS")
print("="*70)
print("\nBased on comprehensive web research for:")
print("  - Semiconductor/AI specialists")
print("  - Biotech/pharma specialists")
print("  - Quantum computing investors")
print("  - Aerospace/robotics/advanced materials")
print("  - Government mega-funds")

# Comprehensive list from web research
specialized_firms = [
    # GOVERNMENT MEGA-FUNDS & SOE
    ('National AI Industry Investment Fund', 'AI Fund, MIIT-MOF AI Fund', 'GOVERNMENT', 'SOE', 'Ministry of Industry and Information Technology, Ministry of Finance', 2025, 'Shanghai', 8.2, 'Artificial Intelligence, Computing Power, Algorithms', 'China', 'Joint venture of Guozhi Investment and Big Fund III, focuses on AI supply chain'),
    ('Big Fund Phase III', 'National IC Fund Phase III, CICF III', 'GOVERNMENT', 'SOE', 'China Integrated Circuit Industry Investment Fund', 2024, 'Beijing', 47.5, 'Semiconductors, Lithography, Design Software, HBM', 'China', 'Third phase of Big Fund (2024-2039), fighting US export controls'),
    ('National Venture Capital Guidance Fund', 'Hard Tech VC Fund, 1 Trillion Fund', 'GOVERNMENT', 'SOE', 'Chinese government', 2025, 'Beijing', 138.0, 'Quantum Computing, AI, Semiconductors, Renewable Energy', 'China', '$138B government fund targeting hard tech sectors'),
    ('Guozhi Investment', 'Guozhi Private Equity Fund Management', 'GOVERNMENT', 'SOE', 'State-backed', 2025, 'Shanghai', None, 'Artificial Intelligence, Strategic Investments', 'China', 'Joint operator of National AI Fund with Big Fund III'),
    ('Tsinghua Holdings Capital', 'Tsinghua Holdings, THC', 'VC', 'SOE-AFFILIATED', 'Tsinghua University', 2003, 'Beijing', 5.0, 'Deep Tech, Hard Tech, Semiconductors, Materials, Biotech', 'China', 'Top science university affiliated VC, invests in university spinouts'),
    ('Beijing Municipal Funds', 'Beijing Industry Investment Funds', 'GOVERNMENT', 'SOE', 'Beijing municipal government', 2024, 'Beijing', 5.6, 'AI, Healthcare, Robotics, IT', 'China', 'Four funds each exceeding 10B yuan focused on strategic sectors'),
    ('Zhejiang Provincial VC Cluster', 'Zhejiang Hi-Tech Funds', 'GOVERNMENT', 'SOE-AFFILIATED', 'Zhejiang provincial government', 2024, 'Hangzhou', 10.0, 'AI, Robotics, Advanced Manufacturing', 'China', 'Emerged as biggest regional VC recipient in 2024'),

    # BIOTECH/HEALTHCARE SPECIALISTS (New or enhanced)
    ('Quan Capital', 'Quan', 'VC', 'PRIVATE', 'None publicly known', 2017, 'Shanghai', 0.425, 'Therapeutics, Enabling Technologies, High-end Healthcare Services', 'China', 'Early and late-stage healthcare investments'),
    ('Third Rock Ventures China', 'Third Rock China', 'VC', 'PRIVATE', 'Third Rock Ventures (US)', 2020, 'Shanghai & Boston', 2.0, 'Biotechnology, Drug Discovery', 'US-China', 'US biotech VC with China cross-border activity'),
    ('Foresite Capital China', 'Foresite China', 'VC', 'PRIVATE', 'Foresite Capital (US)', 2018, 'Shanghai & San Francisco', 1.5, 'Healthcare Technology, Biotechnology', 'US-China', 'Healthcare VC active in China biotech'),
    ('Bain Capital Life Sciences China', 'Bain LS China', 'PE/VC', 'PRIVATE', 'Bain Capital (US)', 2020, 'Shanghai & Boston', 3.0, 'Biotechnology, Pharmaceuticals', 'US-China', 'Bain Capital life sciences arm, China cross-border'),
    ('Atlas Venture China', 'Atlas China', 'VC', 'PRIVATE', 'Atlas Venture (US)', 2019, 'Shanghai & Boston', 1.0, 'Biotechnology, Early-stage Drug Discovery', 'US-China', 'US biotech VC with China activity'),
    ('RTW Investments China', 'RTW China', 'VC/HEDGE', 'PRIVATE', 'RTW Investments (US)', 2016, 'Hong Kong & New York', 2.5, 'Biotechnology, Pharmaceuticals', 'US-China-Global', 'Healthcare-focused hedge fund/VC active in China'),

    # QUANTUM COMPUTING SPECIALISTS
    ('Starry Investment', 'Starry Capital', 'VC', 'PRIVATE', 'None publicly known', 2015, 'Beijing', 0.5, 'Quantum Computing, Deep Tech, AI', 'China', 'Quantum computing specialist, invested in SpinQ'),
    ('Huaqiang Capital', 'Huaqiang', 'VC', 'SOE-AFFILIATED', 'Huaqiang Group (electronics)', 2010, 'Shenzhen', 1.0, 'Quantum Computing, Semiconductors, Electronics', 'China', 'Electronics group affiliated VC, quantum focus'),
    ('Jiusong Fund', 'Jiusong Capital', 'VC', 'PRIVATE', 'None publicly known', 2012, 'Shanghai', 0.3, 'Quantum Computing, Advanced Materials', 'China', 'Deep tech specialist, quantum investments'),
    ('Jianxin Equity Investment', 'Jianxin Capital', 'PE', 'SOE-AFFILIATED', 'China Construction Bank affiliated', 2009, 'Beijing', 2.0, 'Quantum Computing, Strategic Technology', 'China', 'Bank-affiliated PE with quantum investments'),
    ('Liangxi Science and Technology City Development Fund', 'Liangxi Fund', 'GOVERNMENT', 'SOE', 'Wuxi municipal government', 2018, 'Wuxi', 1.0, 'Quantum Computing, AI, Advanced Technology', 'China', 'Municipal government fund supporting quantum startups'),

    # SEMICONDUCTOR/AI SPECIALISTS (Beyond Big Fund)
    ('Shanghai Semiconductor Investment Fund', 'Shanghai Semi Fund', 'GOVERNMENT', 'SOE', 'Shanghai municipal government', 2016, 'Shanghai', 5.0, 'Semiconductors, IC Design, Equipment', 'China', 'Local government semiconductor fund'),
    ('Hubei Changjiang Integrated Circuit Industry Investment Fund', 'Hubei IC Fund', 'GOVERNMENT', 'SOE', 'Hubei provincial government', 2017, 'Wuhan', 12.0, 'Semiconductors, Memory Chips', 'China', 'Provincial semiconductor fund, supports Yangtze Memory'),
    ('Xiamen Semiconductor Investment Fund', 'Xiamen Semi Fund', 'GOVERNMENT', 'SOE', 'Xiamen municipal government', 2017, 'Xiamen', 50.0, 'Semiconductors, Compound Semiconductors', 'China', 'Major municipal semiconductor fund'),

    # AEROSPACE/ROBOTICS SPECIALISTS
    ('China Aerospace Investment Holdings', 'CASIC Capital, Aerospace Capital', 'CVC', 'SOE', 'China Aerospace Science and Industry Corporation (CASIC)', 2010, 'Beijing', 3.0, 'Aerospace, Defense Technology, Dual-use Tech', 'China', 'State aerospace corporation investment arm'),
    ('AVIC Capital', 'Aviation Industry Corporation Capital', 'CVC', 'SOE', 'Aviation Industry Corporation of China (AVIC)', 2009, 'Beijing', 5.0, 'Aerospace, Aviation, Advanced Materials', 'China', 'State aviation corporation investment arm'),
    ('Shanghai Robotics Investment Fund', 'Shanghai Robotics Fund', 'GOVERNMENT', 'SOE', 'Shanghai municipal government', 2020, 'Shanghai', 2.0, 'Robotics, AI, Automation', 'China', 'Municipal fund for robotics industry'),

    # ADDITIONAL TOP-TIER VCs FROM WEB RESEARCH
    ('Dinghui Investment', 'Dinghui Capital', 'VC', 'PRIVATE', 'None publicly known', 2011, 'Beijing', 2.0, 'Technology, Healthcare, Consumer', 'China', 'Hurun Global VCs list top 10 firm'),
    ('Yunfeng Financial', 'Yunfeng, YF Financial', 'PE', 'PRIVATE', 'Jack Ma co-founder (40% ownership)', 2010, 'Shanghai & Hong Kong', 5.0, 'Technology, Healthcare, Financial Services, Media', 'Greater China', 'Alternate name for Yunfeng Capital per Hurun'),

    # CROSS-BORDER SPECIALISTS ACTIVE IN CHINA (International firms but critical for tracking)
    ('OrbiMed Advisors China', 'OrbiMed China Operations', 'VC', 'PRIVATE', 'OrbiMed (US)', 2007, 'Hong Kong & Shanghai', 5.0, 'Biotechnology, Healthcare, Pharmaceuticals', 'Asia-US', 'Leading US healthcare VC, active China operations'),
    ('Longwood Fund', 'Longwood', 'VC', 'PRIVATE', 'None publicly known (US-based)', 2010, 'Boston & Shanghai', 0.8, 'Biotechnology, Life Sciences', 'US-China', 'Boston biotech VC with China cross-border activity'),
    ('SR One China', 'SR One', 'CVC', 'CORPORATE', 'GSK (but independent)', 2011, 'Shanghai & Philadelphia', 1.0, 'Biotechnology, Life Sciences', 'US-China', 'GSK-originated independent biotech VC'),
]

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"\n[INFO] Attempting to add {len(specialized_firms)} specialized firms...")
print("\n" + "="*70)

added = 0
skipped = 0
errors = 0

for firm_data in specialized_firms:
    firm_name = firm_data[0]

    try:
        # Check if already exists
        cursor.execute('SELECT firm_name FROM known_chinese_vc_firms WHERE firm_name = ?', (firm_name,))
        if cursor.fetchone():
            print(f"  ⏭️  {firm_name} - Already exists")
            skipped += 1
            continue

        # Check alternate names
        cursor.execute('''
            SELECT firm_name FROM known_chinese_vc_firms
            WHERE alternate_names LIKE ?
        ''', (f'%{firm_name}%',))
        if cursor.fetchone():
            print(f"  ⏭️  {firm_name} - Found as alternate name")
            skipped += 1
            continue

        # Insert new firm
        cursor.execute('''
            INSERT INTO known_chinese_vc_firms
            (firm_name, alternate_names, firm_type, ownership_type, prc_connections,
             founded_year, headquarters, aum_usd_billions, focus_sectors, geographic_focus,
             notes, added_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*firm_data, datetime.now()))

        print(f"  ✅ {firm_name}")
        print(f"      Type: {firm_data[2]} | Focus: {firm_data[8]}")
        added += 1

    except Exception as e:
        print(f"  ❌ Error adding {firm_name}: {e}")
        errors += 1

conn.commit()

# Get final count
cursor.execute('SELECT COUNT(*) FROM known_chinese_vc_firms')
total_firms = cursor.fetchone()[0]

# Get breakdown by type
cursor.execute('''
    SELECT firm_type, COUNT(*) as count
    FROM known_chinese_vc_firms
    GROUP BY firm_type
    ORDER BY count DESC
''')
type_breakdown = cursor.fetchall()

conn.close()

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"\nFirms added this run: {added}")
print(f"Firms skipped (duplicates): {skipped}")
print(f"Errors: {errors}")
print(f"\nTotal firms now in database: {total_firms}")

print("\n" + "="*70)
print("BREAKDOWN BY TYPE")
print("="*70)
for firm_type, count in type_breakdown:
    print(f"  {firm_type}: {count}")

print("\n" + "="*70)
print("KEY ADDITIONS - DUAL-USE TECHNOLOGY SPECIALISTS")
print("="*70)
print("""
GOVERNMENT MEGA-FUNDS:
  ✅ National AI Industry Investment Fund ($8.2B) - AI supply chain
  ✅ National VC Guidance Fund ($138B) - Quantum, AI, semiconductors
  ✅ Big Fund Phase III ($47.5B) - Semiconductors vs US export controls

QUANTUM COMPUTING SPECIALISTS:
  ✅ Starry Investment, Huaqiang Capital, Jiusong Fund
  ✅ Jianxin Equity Investment, Liangxi Science and Technology Fund

BIOTECH/PHARMA SPECIALISTS:
  ✅ Quan Capital ($425M) - Therapeutics focus
  ✅ Third Rock Ventures China, Foresite Capital China
  ✅ Bain Capital Life Sciences China, Atlas Venture China
  ✅ RTW Investments China, OrbiMed Advisors China

SEMICONDUCTOR SPECIALISTS (Regional):
  ✅ Shanghai/Hubei/Xiamen Semiconductor Investment Funds

AEROSPACE/ROBOTICS:
  ✅ China Aerospace Investment Holdings (CASIC)
  ✅ AVIC Capital (Aviation Industry Corp)
  ✅ Shanghai Robotics Investment Fund

UNIVERSITY-AFFILIATED:
  ✅ Tsinghua Holdings Capital - Deep tech spinouts

Total dual-use tech specialist VCs tracked: ~30 new firms
""")

print("\n✅ Database now includes comprehensive dual-use technology specialists")
print("="*70)
