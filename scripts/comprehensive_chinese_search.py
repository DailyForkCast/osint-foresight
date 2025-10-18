#!/usr/bin/env python3
"""
Comprehensive Chinese Entity Search
Thorough search using extensive Chinese geographic and organizational indicators
"""

import sys
import sqlite3
import json
sys.path.append('C:/Projects/OSINT - Foresight/scripts')
from hybrid_chinese_detector import HybridChineseDetector

# COMPREHENSIVE CHINESE INDICATORS

# Major cities (Tier 1 and Tier 2)
chinese_cities = [
    # Tier 1 cities
    'Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen',

    # New Tier 1 cities
    'Chengdu', 'Chongqing', 'Hangzhou', 'Wuhan', 'Xian', "Xi'an",
    'Nanjing', 'Tianjin', 'Suzhou', 'Zhengzhou', 'Changsha',
    'Dongguan', 'Qingdao', 'Shenyang', 'Ningbo', 'Kunming',

    # Tier 2 cities
    'Dalian', 'Xiamen', 'Hefei', 'Foshan', 'Fuzhou',
    'Wuxi', 'Harbin', 'Nanchang', 'Nanning', 'Changchun',
    'Shijiazhuang', 'Guiyang', 'Taiyuan', 'Jinan', 'Lanzhou',
    'Wenzhou', 'Nantong', 'Changzhou', 'Xuzhou', 'Yangzhou',
    'Zhuhai', 'Huizhou', 'Yantai', 'Quanzhou', 'Tangshan'
]

# Chinese provinces and autonomous regions
chinese_provinces = [
    # Provinces
    'Anhui', 'Fujian', 'Gansu', 'Guangdong', 'Guizhou',
    'Hainan', 'Hebei', 'Heilongjiang', 'Henan', 'Hubei',
    'Hunan', 'Jiangsu', 'Jiangxi', 'Jilin', 'Liaoning',
    'Qinghai', 'Shaanxi', 'Shandong', 'Shanxi', 'Sichuan',
    'Yunnan', 'Zhejiang',

    # Autonomous regions
    'Guangxi', 'Inner Mongolia', 'Nei Mongol', 'Ningxia',
    'Tibet', 'Xizang', 'Xinjiang',

    # Special Administrative Regions
    'Hong Kong', 'Macau', 'Macao',

    # Abbreviations and variations
    'HK', 'MO', 'SAR'
]

# Major Chinese companies and organizations
chinese_organizations = [
    # Technology giants
    'Huawei', 'ZTE', 'Xiaomi', 'Lenovo', 'Oppo', 'Vivo', 'OnePlus',
    'DJI', 'Hikvision', 'Dahua', 'TP-Link', 'TCL', 'Hisense',

    # Internet and software
    'Alibaba', 'Tencent', 'Baidu', 'ByteDance', 'JD.com', 'NetEase',
    'Weibo', 'Meituan', 'Didi', 'Bilibili', 'Kuaishou',

    # Semiconductors and electronics
    'SMIC', 'HiSilicon', 'YMTC', 'Cambricon', 'Horizon Robotics',
    'Unisoc', 'Allwinner', 'Rockchip', 'MediaTek', 'Foxconn',

    # Automotive
    'BYD', 'Geely', 'Great Wall', 'NIO', 'Xpeng', 'Li Auto',
    'SAIC', 'FAW', 'Dongfeng', 'Changan', 'GAC', 'BAIC',

    # State enterprises
    'Sinopec', 'PetroChina', 'State Grid', 'China Mobile',
    'China Telecom', 'China Unicom', 'CNOOC', 'CNPC',
    'China Railway', 'CRRC', 'COSCO', 'AVIC', 'COMAC',
    'CSSC', 'NORINCO', 'CETC', 'CNNC', 'CASC', 'CASIC',

    # Banks and financial
    'ICBC', 'Bank of China', 'China Construction Bank',
    'Agricultural Bank', 'Bank of Communications',
    'China Merchants Bank', 'UnionPay', 'Ping An',

    # Airlines and logistics
    'Air China', 'China Eastern', 'China Southern', 'Hainan Airlines',
    'SF Express', 'ZTO Express', 'YTO Express', 'STO Express',

    # Energy and resources
    'China National', 'China State', 'Sinosteel', 'Chinalco',
    'China Coal', 'China Resources', 'China Poly', 'COFCO'
]

# Chinese universities and research institutions
chinese_institutions = [
    # C9 League (China's Ivy League)
    'Tsinghua', 'Peking University', 'Fudan', 'Shanghai Jiao Tong',
    'Nanjing University', 'Zhejiang University', 'USTC',
    'Harbin Institute', 'Xian Jiaotong', "Xi'an Jiaotong",

    # Other major universities
    'Beihang', 'Beijing Institute of Technology', 'Tongji',
    'Renmin University', 'Nankai', 'Tianjin University',
    'Wuhan University', 'Huazhong', 'Sun Yat-sen',
    'Sichuan University', 'Xiamen University', 'Dalian University',

    # Research institutions
    'Chinese Academy of Sciences', 'CAS', 'Chinese Academy of Engineering',
    'China Academy', 'Beijing Academy', 'Shanghai Academy'
]

# Additional Chinese terms and indicators
chinese_terms = [
    'China', 'Chinese', 'PRC', "People's Republic", 'Mainland',
    'Zhongguo', 'Zhonghua', 'Sino', 'CN', 'CHN',
    '.cn', '.com.cn', '.org.cn', '.gov.cn',
    'RMB', 'CNY', 'Yuan', 'Renminbi'
]

def comprehensive_chinese_search():
    """Perform comprehensive search for Chinese entities in TED database"""

    detector = HybridChineseDetector()
    conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
    cur = conn.cursor()

    print('=== COMPREHENSIVE CHINESE ENTITY SEARCH ===\n')

    # Combine all indicators
    all_indicators = (
        chinese_cities + chinese_provinces +
        chinese_organizations + chinese_institutions +
        chinese_terms
    )

    # Remove duplicates
    all_indicators = list(set(all_indicators))

    print(f'Searching with {len(all_indicators)} Chinese indicators...\n')

    found_entities = {}

    # Search for each indicator
    for i, indicator in enumerate(all_indicators):
        if i % 20 == 0:
            print(f'Progress: {i}/{len(all_indicators)} indicators searched...')

        # Search in contractor names and authorities
        cur.execute('''
            SELECT DISTINCT contractor_name, contractor_country, contracting_authority
            FROM ted_china_contracts
            WHERE (contractor_name LIKE ? OR contracting_authority LIKE ?)
            AND contractor_name IS NOT NULL
            LIMIT 10
        ''', (f'%{indicator}%', f'%{indicator}%'))

        for row in cur.fetchall():
            contractor, country, authority = row

            # Skip if already processed
            entity_key = (contractor, country)
            if entity_key in found_entities:
                continue

            # Analyze with hybrid detector
            result = detector.detect_chinese_entity(contractor, country, authority)

            if result.confidence_score > 0.2:  # Any Chinese indicators
                try:
                    name_clean = contractor.encode('ascii', 'ignore').decode('ascii')[:80]
                    found_entities[entity_key] = {
                        'name': name_clean,
                        'country': country or 'N/A',
                        'confidence': result.confidence_score,
                        'level': result.confidence_level.value,
                        'recommendation': result.recommendation,
                        'matched_indicator': indicator,
                        'evidence': result.certainty_factors[0] if result.certainty_factors else
                                  result.risk_factors[0] if result.risk_factors else 'Pattern match'
                    }
                except:
                    pass

    print(f'\nSearch complete. Found {len(found_entities)} unique entities with Chinese indicators.\n')

    # Group by confidence level
    by_level = {
        'CRITICAL': [],
        'HIGH': [],
        'MEDIUM': [],
        'LOW': [],
        'MINIMAL': []
    }

    for entity in found_entities.values():
        if entity['level'] in by_level:
            by_level[entity['level']].append(entity)

    # Sort each level by confidence
    for level in by_level:
        by_level[level].sort(key=lambda x: x['confidence'], reverse=True)

    # Display results
    print('=== RESULTS BY CONFIDENCE LEVEL ===\n')

    for level, entities in by_level.items():
        if entities:
            print(f'{level} CONFIDENCE ({len(entities)} entities):')
            print('-' * 80)

            # Show top 5 for each level
            for entity in entities[:5]:
                print(f"Name: {entity['name']}")
                print(f"Country: {entity['country']} | Confidence: {entity['confidence']:.3f}")
                print(f"Matched: '{entity['matched_indicator']}' | Evidence: {entity['evidence']}")
                print(f"Recommendation: {entity['recommendation']}")
                print()

            if len(entities) > 5:
                print(f"... and {len(entities) - 5} more {level} confidence entities\n")

    # Summary statistics
    print('=== SUMMARY STATISTICS ===')
    total = len(found_entities)
    critical_high = len(by_level['CRITICAL']) + len(by_level['HIGH'])
    medium = len(by_level['MEDIUM'])
    low_minimal = len(by_level['LOW']) + len(by_level['MINIMAL'])

    print(f'Total entities with Chinese indicators: {total}')
    print(f'Critical/High confidence (definitive): {critical_high}')
    print(f'Medium confidence (probable): {medium}')
    print(f'Low/Minimal confidence (possible): {low_minimal}')

    # Check the original false positives
    print('\n=== VALIDATION CHECK ===')
    cur.execute('''
        SELECT COUNT(*) FROM ted_china_contracts WHERE china_linked = 1
    ''')
    original_count = cur.fetchone()[0]

    print(f'Original system flagged: {original_count:,} entities')
    print(f'Comprehensive search found: {total} entities')
    print(f'Reduction: {(original_count - total) / original_count:.1%}')
    print(f'False positive elimination: {original_count - total:,} entities')

    conn.close()

    return found_entities, by_level

if __name__ == "__main__":
    found_entities, by_level = comprehensive_chinese_search()

    # Save results
    results = {
        'total_found': len(found_entities),
        'by_level': {level: len(entities) for level, entities in by_level.items()},
        'sample_entities': {}
    }

    # Save sample entities for each level
    for level, entities in by_level.items():
        results['sample_entities'][level] = entities[:3]  # Top 3 for each level

    with open('C:/Projects/OSINT - Foresight/analysis/comprehensive_chinese_search_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print('\nResults saved to comprehensive_chinese_search_results.json')
