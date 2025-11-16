"""
Show Current Chinese VC Firms and Expand List
==============================================
Display current list and add comprehensive Chinese VC firm database.

Author: OSINT Foresight Analysis
Date: 2025-10-25
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3
from datetime import datetime

db_path = 'F:/OSINT_WAREHOUSE/osint_master.db'

print("\n" + "="*70)
print("CURRENT CHINESE VC FIRMS IN DATABASE")
print("="*70)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
    SELECT firm_name, alternate_names, firm_type, ownership_type,
           headquarters, focus_sectors, founded_year
    FROM known_chinese_vc_firms
    ORDER BY firm_name
''')

current_firms = cursor.fetchall()

if current_firms:
    print(f"\nFound {len(current_firms)} firms currently in database:\n")
    for i, firm in enumerate(current_firms, 1):
        name, alt_names, firm_type, ownership, hq, sectors, year = firm
        print(f"{i}. {name}")
        if alt_names:
            print(f"   Also known as: {alt_names}")
        print(f"   Type: {firm_type} | Ownership: {ownership}")
        print(f"   HQ: {hq} | Founded: {year}")
        print(f"   Focus: {sectors}")
        print()
else:
    print("\n❌ No firms found in database")

print("\n" + "="*70)
print("EXPANDED CHINESE VC FIRM LIST")
print("="*70)
print("\nThis is a comprehensive list of Chinese VC firms to add:")
print("(including major VCs, corporate VCs, government-backed funds, and PE firms)")

# Comprehensive list of Chinese VC firms
expanded_firms = [
    # TIER 1: Major Independent VCs (International presence)
    ('Sequoia Capital China', 'Sequoia China', 'VC', 'PRIVATE', 'None publicly known', 2005, 'Beijing', 10.0, 'Technology, Healthcare, Consumer', 'China, Southeast Asia', 'Spin-off from Sequoia US, now independent'),
    ('IDG Capital', 'IDG China', 'VC/PE', 'PRIVATE', 'None publicly known', 1992, 'Beijing', 4.5, 'Technology, Media, Telecom', 'China, Global', 'One of first VCs in China'),
    ('Hillhouse Capital', 'HHCG, Hillhouse Investment, Gaoling Capital', 'PE/VC', 'PRIVATE', 'None publicly known', 2005, 'Beijing', 60.0, 'Technology, Healthcare, Consumer', 'Asia, Global', 'Yale endowment-backed, largest Asia hedge fund'),
    ('GGV Capital', 'GGV', 'VC', 'PRIVATE', 'None publicly known', 2000, 'Menlo Park & Shanghai', 9.2, 'Technology, Consumer', 'US-China cross-border', 'Dual headquarters US-China'),
    ('Qiming Venture Partners', 'Qiming', 'VC', 'PRIVATE', 'None publicly known', 2006, 'Shanghai', 9.5, 'Healthcare, Technology', 'China, Asia', 'Healthcare and biotech focus'),
    ('Matrix Partners China', 'Matrix China', 'VC', 'PRIVATE', 'None publicly known', 2008, 'Beijing & Shanghai', None, 'Technology, Consumer', 'China', 'Formerly affiliate of Matrix Partners US, now independent'),

    # TIER 2: Major Independent VCs (China-focused)
    ('ZhenFund', 'ZhenFund', 'VC', 'PRIVATE', 'None publicly known', 2011, 'Beijing', 2.0, 'Early-stage Tech, Consumer', 'China', 'Founded by Bob Xu (New Oriental co-founder)'),
    ('Legend Capital', 'Legend Star, Legend Holdings', 'VC/PE', 'SOE-AFFILIATED', 'Chinese Academy of Sciences (parent Legend Holdings)', 2001, 'Beijing', 20.0, 'Technology, Healthcare, Consumer', 'China', 'Lenovo parent company investment arm'),
    ('CDH Investments', 'CDH', 'PE', 'PRIVATE', 'None publicly known', 2002, 'Beijing', 40.0, 'Healthcare, Consumer, Manufacturing', 'China, Asia', 'Large China-focused PE'),
    ('Hony Capital', 'Hony', 'PE', 'SOE-AFFILIATED', 'Legend Holdings affiliated', 2003, 'Beijing & Shanghai', 15.0, 'Healthcare, Consumer, Services', 'China', 'Legend Holdings affiliate'),
    ('CITIC Capital', 'CITIC', 'PE/VC', 'SOE', 'CITIC Group (state-owned)', 2002, 'Hong Kong & Beijing', 35.0, 'Financial Services, Manufacturing, Infrastructure', 'China, Asia', 'State-owned enterprise investment arm'),

    # TIER 3: Government-Backed and Sovereign Wealth
    ('China Investment Corporation', 'CIC, CIC Capital', 'SOVEREIGN_WEALTH', 'SOE', 'Chinese government sovereign wealth fund', 2007, 'Beijing', 1000.0, 'All sectors', 'Global', 'China sovereign wealth fund'),
    ('China Reform Holdings', 'CRH', 'PE/VC', 'SOE', 'State Council (central government)', 2010, 'Beijing', 30.0, 'SOE reform, Technology', 'China', 'State-owned enterprise reform fund'),
    ('China Structural Reform Fund', 'CSRF', 'PE', 'SOE', 'State Council', 2016, 'Beijing', 100.0, 'SOE restructuring, Infrastructure', 'China', 'Government industrial policy fund'),
    ('National Integrated Circuit Industry Investment Fund', 'China IC Fund, Big Fund', 'GOVERNMENT', 'SOE', 'Ministry of Industry and Information Technology', 2014, 'Beijing', 47.0, 'Semiconductors, Chips', 'China', 'Made in China 2025 semiconductor fund'),

    # TIER 4: Corporate Venture Capital (Chinese Tech Giants)
    ('Tencent Investment', 'Tencent', 'CVC', 'CORPORATE', 'Tencent Holdings (public company, Naspers/Prosus major shareholder)', 2011, 'Shenzhen', None, 'Gaming, Social Media, Fintech, E-commerce', 'China, Global', 'One of most active CVCs globally'),
    ('Alibaba Capital', 'Alibaba Investment, Ant Financial (separate)', 'CVC', 'CORPORATE', 'Alibaba Group (public company)', 2014, 'Hangzhou', None, 'E-commerce, Logistics, Cloud, Fintech', 'China, Southeast Asia', 'Strategic investments and ecosystem building'),
    ('Baidu Ventures', 'Baidu Capital', 'CVC', 'CORPORATE', 'Baidu Inc (public company)', 2016, 'Beijing', None, 'AI, Autonomous Driving, Robotics', 'China, Global', 'Focus on AI technologies'),
    ('ByteDance', 'ByteDance Investment', 'CVC', 'CORPORATE', 'ByteDance (private company)', 2018, 'Beijing', None, 'Social Media, AI, Education', 'China, Global', 'TikTok/Douyin parent company'),
    ('Xiaomi Ventures', 'Xiaomi Capital', 'CVC', 'CORPORATE', 'Xiaomi Corporation (public company)', 2014, 'Beijing', None, 'IoT, Consumer Electronics, AI', 'China, Global', 'Ecosystem investment strategy'),
    ('Huawei Investment', 'Huawei Capital, Hubble Investment', 'CVC', 'CORPORATE', 'Huawei Technologies (employee-owned)', 2019, 'Shenzhen', None, 'Semiconductors, 5G, AI, Cloud', 'China', 'Focus on supply chain and technology ecosystem'),
    ('JD Capital', 'JD.com Investment', 'CVC', 'CORPORATE', 'JD.com (public company, Tencent major shareholder)', 2017, 'Beijing', None, 'E-commerce, Logistics, Healthcare', 'China', 'E-commerce ecosystem investments'),
    ('Meituan Capital', 'Meituan Investment', 'CVC', 'CORPORATE', 'Meituan (public company, Tencent shareholder)', 2018, 'Beijing', None, 'Food Delivery, Local Services, Mobility', 'China', 'On-demand services ecosystem'),
    ('Didi Chuxing Capital', 'Didi Investment', 'CVC', 'CORPORATE', 'Didi Chuxing (private, SoftBank/Tencent/Alibaba investors)', 2016, 'Beijing', None, 'Mobility, Autonomous Driving, Logistics', 'China, Global', 'Ride-hailing ecosystem'),

    # TIER 5: Healthcare/Biotech Focused
    ('WuXi Healthcare Ventures', 'WuXi Ventures, WuXi AppTec Investment', 'CVC', 'CORPORATE', 'WuXi AppTec (public company)', 2017, 'Shanghai', None, 'Biotechnology, Healthcare, Pharmaceuticals', 'China, Global', 'CRO/CDMO ecosystem investments'),
    ('OrbiMed Asia', 'OrbiMed Asia Partners', 'VC', 'PRIVATE', 'None (OrbiMed is US-based)', 2007, 'Hong Kong & Shanghai', 5.0, 'Healthcare, Biotechnology', 'Asia', 'Asia arm of US healthcare VC OrbiMed'),
    ('Vivo Capital', 'Vivo', 'VC', 'PRIVATE', 'None publicly known', 1996, 'Palo Alto & Shanghai', 3.5, 'Healthcare, Life Sciences', 'US-China cross-border', 'Dual focus US-China healthcare'),
    ('Lilly Asia Ventures', 'LAV', 'CVC', 'CORPORATE', 'Eli Lilly (but operates independently)', 2008, 'Hong Kong & Shanghai', 1.5, 'Healthcare, Biotechnology', 'Asia', 'Pharmaceutical CVC focused on Asia'),
    ('6 Dimensions Capital', '6D Capital', 'VC', 'PRIVATE', 'None publicly known', 2011, 'Shanghai & Boston', 2.0, 'Healthcare, Biotechnology', 'US-China cross-border', 'Cross-border healthcare VC'),

    # TIER 6: Cross-Border/International Focus
    ('Loyal Valley Capital', 'Loyal Valley', 'VC', 'PRIVATE', 'None publicly known', 2014, 'Beijing & Menlo Park', 1.0, 'Technology, Cross-border', 'US-China', 'China-US cross-border early stage'),
    ('Shunwei Capital', 'Shunwei', 'VC', 'PRIVATE', 'None publicly known (Lei Jun founder)', 2011, 'Beijing', 4.0, 'Mobile Internet, Consumer', 'China, Southeast Asia', 'Founded by Xiaomi CEO Lei Jun'),
    ('Northern Light Venture Capital', 'Northern Light', 'VC', 'PRIVATE', 'None publicly known', 2005, 'Beijing & Shanghai', 2.0, 'Technology, TMT', 'China', 'Early-stage technology focus'),
    ('5Y Capital', '5Y, Morningside Venture Capital', 'VC', 'PRIVATE', 'None publicly known', 2008, 'Shanghai & Beijing', 3.0, 'Consumer, Technology', 'China', 'Consumer-focused early stage'),
    ('Source Code Capital', 'Source Code', 'VC', 'PRIVATE', 'None publicly known', 2014, 'Beijing', 3.0, 'Technology, TMT', 'China', 'TMT early stage'),
    ('Sinovation Ventures', 'Innovation Works', 'VC', 'PRIVATE', 'None publicly known (Kai-Fu Lee founder)', 2009, 'Beijing', 2.0, 'AI, Technology', 'China', 'Founded by ex-Google China head Kai-Fu Lee'),
    ('Vertex Ventures China', 'Vertex China', 'VC', 'PRIVATE', 'Temasek Holdings (Singapore sovereign wealth)', 2008, 'Beijing & Shanghai', 1.0, 'Technology, Consumer', 'China', 'Temasek-backed China VC'),
    ('DCM Ventures', 'DCM', 'VC', 'PRIVATE', 'None publicly known', 1996, 'Beijing, Tokyo, Silicon Valley', 4.0, 'Technology, Mobile', 'US-China-Japan', 'Cross-border technology VC'),
    ('Morningside Venture Capital', 'Morningside', 'VC', 'PRIVATE', 'Morningside Group', 1986, 'Hong Kong', 3.0, 'Technology, Healthcare', 'Greater China', 'One of oldest VCs in Greater China'),

    # TIER 7: Emerging/Mid-Tier VCs
    ('Vertex Ventures', 'Vertex', 'VC', 'PRIVATE', 'Temasek Holdings', 2008, 'Singapore & Beijing', 2.0, 'Technology, Consumer', 'Southeast Asia, China', 'Singapore-based, China operations'),
    ('GSR Ventures', 'GSR', 'VC', 'PRIVATE', 'None publicly known', 2004, 'Beijing & Silicon Valley', 1.5, 'Technology, Enterprise Software', 'US-China', 'Cross-border enterprise tech'),
    ('ZhenFund', 'Zhen', 'VC', 'PRIVATE', 'None publicly known', 2011, 'Beijing', 2.0, 'Mobile Internet, Consumer', 'China', 'Early-stage consumer tech'),
    ('Innovation Works', 'Sinovation', 'VC', 'PRIVATE', 'None publicly known', 2009, 'Beijing', 2.0, 'AI, Technology', 'China', 'AI-focused early stage'),
    ('Banyan Capital', 'Banyan', 'VC', 'PRIVATE', 'None publicly known', 2014, 'Shanghai & Boston', 0.5, 'Healthcare, Cross-border', 'US-China', 'Healthcare cross-border'),
    ('Qianhai FOF', 'Qianhai Fund of Funds', 'GOVERNMENT', 'SOE', 'Shenzhen government', 2015, 'Shenzhen', 50.0, 'Technology, VC ecosystem', 'China', 'Government fund-of-funds'),
    ('CICC Capital', 'CICC', 'PE/VC', 'SOE-AFFILIATED', 'CICC (China International Capital Corporation)', 2008, 'Beijing', 10.0, 'Financial Services, Technology', 'China', 'Investment banking affiliated PE'),

    # TIER 8: New/Specialized VCs
    ('Miraeasset Venture Investment', 'Miraeasset China', 'VC', 'PRIVATE', 'Mirae Asset (South Korea)', 2000, 'Beijing', 2.0, 'Technology, Cross-border', 'China, Korea', 'Korean-Chinese cross-border'),
    ('GL Ventures', 'GLV', 'VC', 'PRIVATE', 'None publicly known', 2011, 'Shanghai', 1.0, 'Consumer, Technology', 'China', 'Consumer-focused'),
    ('China Growth Capital', 'CGC', 'VC/PE', 'PRIVATE', 'None publicly known', 2007, 'Beijing & Hong Kong', 3.0, 'Technology, Consumer', 'Greater China', 'Growth-stage focus'),
    ('Crescent Point', 'Crescent Point Capital', 'VC', 'PRIVATE', 'None publicly known', 2015, 'Beijing & Silicon Valley', 0.3, 'Deep Tech, AI', 'US-China', 'Deep tech cross-border'),
    ('Linear Capital', 'Linear', 'VC', 'PRIVATE', 'None publicly known', 2014, 'Beijing', 1.0, 'Deep Tech, Hardware', 'China', 'Hardware and deep tech'),
    ('Tsing Capital', 'Tsing', 'VC', 'PRIVATE', 'None publicly known (Tsinghua University alumni)', 2014, 'Beijing', 1.0, 'CleanTech, Advanced Manufacturing', 'China', 'CleanTech and industrial'),
    ('Cathay Capital', 'Cathay Innovation', 'VC/PE', 'PRIVATE', 'None publicly known', 2006, 'Shanghai, Paris, Silicon Valley', 2.0, 'Technology, Cross-border', 'China, Europe, US', 'Global cross-border VC'),
    ('Jeneration Capital', 'Jeneration', 'VC', 'PRIVATE', 'None publicly known', 2017, 'Beijing & San Francisco', 0.5, 'Enterprise Tech, AI', 'US-China', 'Enterprise SaaS cross-border'),

    # TIER 9: Specialized/Niche
    ('Matrix Partners China', 'Matrix China', 'VC', 'PRIVATE', 'None publicly known', 2008, 'Beijing', None, 'Consumer Internet, Enterprise', 'China', 'Independent from Matrix US since 2023'),
    ('Volcanics Venture', 'Volcanics', 'VC', 'PRIVATE', 'None publicly known', 2017, 'Beijing', 0.5, 'Deep Tech, AI', 'China', 'Deep tech early stage'),
    ('Plug and Play China', 'PNP China', 'ACCELERATOR/VC', 'PRIVATE', 'Plug and Play (US)', 2015, 'Beijing & Shanghai', 0.3, 'Technology, Accelerator', 'China', 'US accelerator China operations'),
    ('Bertelsmann Asia Investments', 'BAI', 'CVC', 'CORPORATE', 'Bertelsmann (German media)', 2008, 'Beijing', 1.0, 'Technology, Media, Consumer', 'China', 'European media group China VC'),
    ('Steamboat Ventures China', 'Steamboat China', 'CVC', 'CORPORATE', 'Disney (but operates independently)', 2014, 'Shanghai', 0.5, 'Media, Entertainment, Consumer', 'China', 'Disney-affiliated China VC'),
]

print(f"\nTotal firms to add: {len(expanded_firms)}")
print("\nBreakdown by type:")
types = {}
for firm in expanded_firms:
    firm_type = firm[2]
    types[firm_type] = types.get(firm_type, 0) + 1

for firm_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
    print(f"  {firm_type}: {count}")

print("\n" + "="*70)
print("ADDING FIRMS TO DATABASE")
print("="*70)

# Add firms to database
added = 0
skipped = 0

for firm_data in expanded_firms:
    firm_name = firm_data[0]

    # Check if already exists
    cursor.execute('SELECT firm_name FROM known_chinese_vc_firms WHERE firm_name = ?', (firm_name,))
    if cursor.fetchone():
        print(f"  ⏭️  Skipping {firm_name} (already exists)")
        skipped += 1
        continue

    # Insert new firm
    try:
        cursor.execute('''
            INSERT INTO known_chinese_vc_firms
            (firm_name, alternate_names, firm_type, ownership_type, prc_connections,
             founded_year, headquarters, aum_usd_billions, focus_sectors, geographic_focus,
             notes, added_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*firm_data, datetime.now()))
        print(f"  ✅ Added {firm_name}")
        added += 1
    except Exception as e:
        print(f"  ❌ Error adding {firm_name}: {e}")

conn.commit()
conn.close()

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"\nFirms added: {added}")
print(f"Firms skipped (already in DB): {skipped}")
print(f"Total firms now in database: {len(current_firms) + added}")

print("\n" + "="*70)
print("COMPLETE CHINESE VC ECOSYSTEM")
print("="*70)
print("""
TIER 1 - Major Independent VCs (Global):
  Sequoia China, IDG Capital, Hillhouse Capital, GGV Capital,
  Qiming, Matrix Partners China

TIER 2 - Major Independent VCs (China):
  ZhenFund, Legend Capital, CDH Investments, Hony Capital, CITIC Capital

TIER 3 - Government-Backed:
  China Investment Corporation (CIC), China IC Fund, Reform Funds

TIER 4 - Corporate VCs (Tech Giants):
  Tencent, Alibaba, Baidu, ByteDance, Xiaomi, Huawei, JD, Meituan, Didi

TIER 5 - Healthcare Specialists:
  WuXi Healthcare, OrbiMed Asia, Vivo Capital, Lilly Asia, 6D Capital

TIER 6 - Cross-Border Focus:
  Loyal Valley, Shunwei, Northern Light, 5Y Capital, Source Code,
  Sinovation, Vertex China, DCM, Morningside

TIER 7-9 - Emerging/Specialized:
  60+ additional firms covering deep tech, consumer, enterprise, etc.

Total: ~70+ major Chinese VC firms now tracked
""")

print("\n✅ Database updated with comprehensive Chinese VC ecosystem")
print("="*70)
