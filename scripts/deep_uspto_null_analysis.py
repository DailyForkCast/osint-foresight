#!/usr/bin/env python3
"""
Deep Analysis of USPTO NULL Country Records
Systematic search for Chinese entities hidden in the 1.58M NULL records
"""

import sqlite3
from collections import defaultdict, Counter
import re

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from dynamic SQL construction.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    # Check for valid characters only (alphanumeric + underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    # Check length (SQLite limit is 1024, we use 100 for safety)
    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    # Blacklist dangerous SQL keywords
    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

print("=" * 80)
print("DEEP USPTO NULL COUNTRY ANALYSIS")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Get total NULL records
cur.execute("SELECT COUNT(*) FROM uspto_assignee WHERE ee_country IS NULL OR ee_country = ''")
total_null = cur.fetchone()[0]
print(f"\nTotal NULL/empty country records: {total_null:,}")

# ============================================================================
# PHASE 1: Known Chinese Companies in NULL Records (Expanded List)
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 1: KNOWN CHINESE COMPANIES IN NULL RECORDS")
print("=" * 80)

# Massively expanded list - including subsidiaries, variants, joint ventures
chinese_companies = [
    # Major Tech Companies
    'HUAWEI', 'ZTE', 'XIAOMI', 'OPPO', 'VIVO', 'ONEPLUS', 'REALME', 'MEIZU',
    'LENOVO', 'TCL', 'HAIER', 'HISENSE', 'MIDEA', 'GREE',

    # Internet Giants
    'ALIBABA', 'TENCENT', 'BAIDU', 'BYTEDANCE', 'TIKTOK', 'JD.COM', 'MEITUAN',
    'DIDI', 'PINDUODUO', 'NETEASE', 'SINA', 'SOHU', 'WEIBO',

    # EV & Automotive
    'BYD', 'NIO', 'XPENG', 'LI AUTO', 'GEELY', 'GREAT WALL', 'CHERY', 'SAIC',
    'DONGFENG', 'FAW', 'BAIC', 'GAC', 'NIO NEXTEV', 'LEAPMOTOR',

    # Telecom & Network
    'CHINA MOBILE', 'CHINA TELECOM', 'CHINA UNICOM', 'CHINA TOWER',
    'FIBERHOME', 'DATANG', 'POTEVIO', 'ERICSSON PANDA',

    # Surveillance & AI
    'HIKVISION', 'DAHUA', 'SENSETIME', 'MEGVII', 'CLOUDWALK', 'YITU',
    'UNIVIEW', 'TIANDY', 'WATRIX', 'IFLYTEK',

    # Semiconductors & Electronics
    'SMIC', 'SEMICONDUCTOR MANUFACTURING', 'YANGTZE MEMORY', 'YMTC',
    'UNISOC', 'SPREADTRUM', 'ROCKCHIP', 'AMLOGIC', 'ALLWINNER',
    'BOE', 'CSOT', 'TIANMA', 'TRULY', 'GOODIX',

    # Defense & Aerospace (SOEs)
    'AVIC', 'AVIATION INDUSTRY', 'COMAC', 'NORINCO', 'CASIC', 'CASC',
    'CETC', 'CHINA ELECTRONICS', 'CHINA AEROSPACE', 'CNGC', 'NUCTECH',

    # Energy & Resources
    'CATL', 'BYD BATTERY', 'GOTION', 'EVE ENERGY', 'CALB',
    'SINOPEC', 'PETROCHINA', 'CNOOC', 'STATE GRID', 'CHINA COAL',

    # Pharma & Biotech
    'WUXI', 'JIANGSU HENGRUI', 'SINO BIOPHARMACEUTICAL', 'CHINA RESOURCES',
    'BGI', 'GENOMICS', 'SINOVAC', 'SINOPHARM',

    # Finance & Banking
    'ICBC', 'CHINA CONSTRUCTION BANK', 'AGRICULTURAL BANK', 'BANK OF CHINA',
    'ANT GROUP', 'ALIPAY', 'WECHAT PAY', 'UNIONPAY',

    # Infrastructure & Construction
    'CHINA RAILWAY', 'CHINA COMMUNICATIONS', 'CHINA STATE CONSTRUCTION',
    'POWERCHINA', 'SINOHYDRO', 'CRRC', 'ZOOMLION',

    # Universities & Research Institutes
    'TSINGHUA', 'PEKING UNIVERSITY', 'CHINESE ACADEMY', 'CAS',
    'FUDAN', 'ZHEJIANG UNIVERSITY', 'SHANGHAI JIAO TONG',

    # Emerging Tech
    'CAMBRICON', 'HORIZON ROBOTICS', 'DEEPGLINT', 'CLOUDMINDS',
    'UBTECH', 'DJI', 'AUTEL', 'YUNEEC',
]

company_results = []
total_company_matches = set()

for company in chinese_companies:
    # Use word boundaries to avoid false positives
    # SECURITY: Use parameterized query to prevent SQL injection
    cur.execute("""
        SELECT rf_id, ee_name, ee_city, ee_address_1
        FROM uspto_assignee
        WHERE (ee_country IS NULL OR ee_country = '')
        AND (
            ee_name LIKE ?
            OR ee_name LIKE ?
            OR ee_name LIKE ?
            OR ee_name = ?
        )
    """, (f'% {company}%', f'{company} %', f'% {company}', company))

    matches = cur.fetchall()
    if matches:
        total_company_matches.update([m[0] for m in matches])
        company_results.append((company, len(matches), matches[:3]))  # Store first 3 examples

# Sort by count
company_results.sort(key=lambda x: x[1], reverse=True)

print(f"\nFound {len(total_company_matches):,} NULL records matching {len(company_results)} known Chinese companies")
print("\nTop 30 Companies Found:")
for i, (company, count, examples) in enumerate(company_results[:30], 1):
    print(f"\n{i}. {company}: {count:,} records")
    for rf_id, name, city, addr in examples[:2]:
        city_str = city if city else "N/A"
        print(f"   - {name[:60]} | {city_str}")

# ============================================================================
# PHASE 2: Chinese City Patterns in NULL Records (Massively Expanded)
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 2: CHINESE CITIES IN NULL RECORDS")
print("=" * 80)

chinese_cities = [
    # Tier 1 Cities
    'BEIJING', 'SHANGHAI', 'GUANGZHOU', 'SHENZHEN',

    # Provincial Capitals (33 total)
    'NANJING', 'HANGZHOU', 'WUHAN', 'CHENGDU', 'CHONGQING', 'TIANJIN',
    'XIAN', 'SHENYANG', 'HARBIN', 'CHANGCHUN', 'JINAN', 'ZHENGZHOU',
    'SHIJIAZHUANG', 'TAIYUAN', 'HOHHOT', 'YINCHUAN', 'URUMQI', 'LANZHOU',
    'XINING', 'LHASA', 'KUNMING', 'GUIYANG', 'NANNING', 'HAIKOU',
    'CHANGSHA', 'NANCHANG', 'FUZHOU', 'HEFEI', 'TAIPEI', 'HONG KONG',

    # Major Tech Hubs (20+)
    'SUZHOU', 'DONGGUAN', 'FOSHAN', 'NINGBO', 'WUXI', 'QINGDAO',
    'DALIAN', 'XIAMEN', 'ZHUHAI', 'HUIZHOU', 'ZHONGSHAN', 'JIANGMEN',
    'SHAOXING', 'WENZHOU', 'YANTAI', 'WEIFANG', 'ZIBO', 'LUOYANG',

    # Manufacturing Centers
    'DONGGUAN', 'FOSHAN', 'JIAXING', 'HUZHOU', 'TAIZHOU', 'JINHUA',
    'QUZHOU', 'LISHUI', 'ANQING', 'WUHU', 'BENGBU',

    # Special Economic Zones & New Areas
    'PUDONG', 'BINHAI', 'LIANGJIANG', 'NANSHA', 'QIANHAI',
]

city_matches = set()
city_breakdown = []

for city in chinese_cities:
    # SECURITY: Use parameterized query to prevent SQL injection
    cur.execute("""
        SELECT rf_id, ee_name, ee_city, ee_address_1
        FROM uspto_assignee
        WHERE (ee_country IS NULL OR ee_country = '')
        AND UPPER(ee_city) LIKE ?
    """, (f'%{city}%',))

    matches = cur.fetchall()
    if matches:
        city_matches.update([m[0] for m in matches])
        city_breakdown.append((city, len(matches)))

city_breakdown.sort(key=lambda x: x[1], reverse=True)

print(f"\nFound {len(city_matches):,} NULL records with Chinese cities")
print("\nTop 20 Cities:")
for i, (city, count) in enumerate(city_breakdown[:20], 1):
    print(f"{i:2d}. {city:20s}: {count:,}")

# ============================================================================
# PHASE 3: Address Pattern Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 3: ADDRESS PATTERN ANALYSIS")
print("=" * 80)

# Chinese address patterns
patterns = [
    ("Contains 'CHINA'", "ee_address_1 LIKE '%CHINA%' OR ee_address_2 LIKE '%CHINA%'"),
    ("Contains 'CHINESE'", "ee_address_1 LIKE '%CHINESE%' OR ee_address_2 LIKE '%CHINESE%'"),
    ("Contains 'P.R.C'", "ee_address_1 LIKE '%P.R.C%' OR ee_address_2 LIKE '%P.R.C%'"),
    ("Contains 'PEOPLE''S REPUBLIC'", "ee_address_1 LIKE '%PEOPLE%REPUBLIC%' OR ee_address_2 LIKE '%PEOPLE%REPUBLIC%'"),
    ("District/Road patterns", "ee_address_1 LIKE '% DISTRICT%' OR ee_address_1 LIKE '% ROAD%'"),
]

address_matches = set()

for label, condition in patterns:
    # SECURITY: Use string concatenation for hardcoded conditions from safe list
    cur.execute("""
        SELECT rf_id, ee_name, ee_address_1
        FROM uspto_assignee
        WHERE (ee_country IS NULL OR ee_country = '')
        AND (""" + condition + ")")

    matches = cur.fetchall()
    if matches:
        address_matches.update([m[0] for m in matches])
        print(f"\n{label}: {len(matches):,} records")
        # Show examples
        for rf_id, name, addr in matches[:3]:
            print(f"  - {name[:50]} | {addr[:60]}")

# ============================================================================
# PHASE 4: Postal Code Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 4: POSTAL CODE ANALYSIS")
print("=" * 80)

# Chinese postal codes: 6 digits, first digit 1-9
cur.execute("""
    SELECT rf_id, ee_name, ee_city, ee_postcode
    FROM uspto_assignee
    WHERE (ee_country IS NULL OR ee_country = '')
    AND LENGTH(ee_postcode) = 6
    AND ee_postcode GLOB '[1-9][0-9][0-9][0-9][0-9][0-9]'
""")

postal_matches = cur.fetchall()
postal_ids = {m[0] for m in postal_matches}

print(f"\nFound {len(postal_ids):,} NULL records with Chinese postal code patterns")

# Analyze postal code prefixes
postal_prefixes = Counter([m[3][:3] for m in postal_matches if m[3]])
print("\nTop 10 Postal Code Prefixes:")
for prefix, count in postal_prefixes.most_common(10):
    # Map to regions
    region_map = {
        '100': 'Beijing', '200': 'Shanghai', '510': 'Guangzhou',
        '518': 'Shenzhen', '310': 'Hangzhou', '210': 'Nanjing',
        '430': 'Wuhan', '610': 'Chengdu', '300': 'Tianjin',
    }
    region = region_map.get(prefix, 'Unknown')
    print(f"  {prefix}xxx ({region}): {count:,}")

# ============================================================================
# PHASE 5: Combined Analysis - Overlap and Unique
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 5: COMBINED ANALYSIS")
print("=" * 80)

all_chinese_null = total_company_matches | city_matches | address_matches | postal_ids

print(f"\nTotal unique Chinese entities in NULL records: {len(all_chinese_null):,}")
print(f"\nBreakdown:")
print(f"  Company name matches:    {len(total_company_matches):,}")
print(f"  City matches:            {len(city_matches):,}")
print(f"  Address pattern matches: {len(address_matches):,}")
print(f"  Postal code matches:     {len(postal_ids):,}")

# Calculate overlaps
company_only = total_company_matches - city_matches - address_matches - postal_ids
city_only = city_matches - total_company_matches - address_matches - postal_ids
multiple_signals = [rf_id for rf_id in all_chinese_null
                    if sum([
                        rf_id in total_company_matches,
                        rf_id in city_matches,
                        rf_id in address_matches,
                        rf_id in postal_ids
                    ]) >= 2]

print(f"\n  Company name only:       {len(company_only):,}")
print(f"  City only:               {len(city_only):,}")
print(f"  Multiple signals (2+):   {len(multiple_signals):,}")

# ============================================================================
# FINAL TALLY
# ============================================================================
print("\n" + "=" * 80)
print("FINAL USPTO CHINESE ENTITY COUNT")
print("=" * 80)

# Previous findings (from comprehensive_uspto_chinese_detection.py)
previous_count = 4824  # Non-NULL Chinese entities

print(f"\nPrevious count (non-NULL country):  {previous_count:,}")
print(f"New NULL record findings:            {len(all_chinese_null):,}")
print(f"{'=' * 50}")
print(f"TOTAL CHINESE USPTO ASSIGNEES:       {previous_count + len(all_chinese_null):,}")

print(f"\n{'=' * 80}")
print("Analysis complete!")
print("=" * 80)

conn.close()
