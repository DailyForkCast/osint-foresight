#!/usr/bin/env python3
"""
Precision USPTO Chinese Entity Detector
Focus on HIGH-CONFIDENCE signals with false-positive filtering
"""

import sqlite3
import re

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

print("=" * 80)
print("PRECISION USPTO CHINESE ENTITY DETECTOR")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ============================================================================
# HIGH CONFIDENCE: Actual Chinese Tech Companies (with false positive filtering)
# ============================================================================
print("\n" + "=" * 80)
print("HIGH CONFIDENCE CHINESE COMPANIES")
print("=" * 80)

# Companies where we need exact/careful matching to avoid false positives
high_confidence_companies = {
    # Unambiguous company names
    'HUAWEI': ['HUAWEI TECHOLOG', 'HUAWEI DEVICE', 'HUAWEI DIGITAL'],
    'XIAOMI': ['XIAOMI INC', 'XIAOMI CORP', 'XIAOMI TECH', 'XIAOMI COMM'],
    'OPPO': ['OPPO MOBILE', 'OPPO GUANGDONG', 'GUANGDONG OPPO'],
    'VIVO': ['VIVO MOBILE', 'VIVO COMMUNICATION', 'BBK VIVO'],
    'ZTE': ['ZTE CORP', 'ZTE COMM', 'ZTE USA', 'ZTE SAN DIEGO'],
    'ALIBABA': ['ALIBABA GROUP', 'ALIBABA CHINA', 'ALIBABA.COM'],
    'TENCENT': ['TENCENT TECH', 'TENCENT HOLDINGS', 'TENCENT CORP'],
    'BAIDU': ['BAIDU USA', 'BAIDU ONLINE', 'BAIDU INC'],
    'BYTEDANCE': ['BYTEDANCE INC', 'BYTEDANCE LTD', 'BEIJING BYTEDANCE'],
    'DJI': ['DJI INNOVATIONS', 'SZ DJI'],
    'BYD': ['BYD COMPANY', 'BYD AUTO', 'BYD BATTERY'],
    'LENOVO': ['LENOVO GROUP', 'LENOVO BEIJING', 'LENOVO SINGAPORE'],
    'HIKVISION': ['HIKVISION DIGITAL', 'HANGZHOU HIKVISION'],
    'DAHUA': ['DAHUA TECHOLOG', 'ZHEJIANG DAHUA'],
    'SENSETIME': ['SENSETIME GROUP', 'SENSETIME HONG KONG'],
    'MEGVII': ['MEGVII TECHOLOG', 'BEIJING MEGVII'],
    'NIO': ['NIO INC', 'NIO USA', 'NEXTEV'],  # Exclude "UNION", "SENIOR"
    'XPENG': ['XPENG INC', 'XPENG MOTORS'],
    'GEELY': ['GEELY AUTO', 'ZHEJIANG GEELY'],
    'SMIC': ['SEMICONDUCTOR MANUFACTURING INTERNATIONAL'],
    'BOE': ['BOE TECHOLOG', 'BEIJING BOE'],  # Exclude "BOEINGER", "BOEING"
    'TCL': ['TCL CORP', 'TCL COMM', 'TCL KING'],  # Exclude "SPTCL", "ETCL"
    'HAIER': ['HAIER GROUP', 'QINGDAO HAIER'],
    'MIDEA': ['MIDEA GROUP', 'GUANGDONG MIDEA'],
    'GREE': ['GREE ELECTRIC', 'ZHUHAI GREE'],  # Exclude "AGREE", "DEGREE"
    'HISENSE': ['HISENSE ELECTRIC', 'QINGDAO HISENSE'],
    'WUXI': ['WUXI APPTEC', 'WUXI BIOLOGICS'],
    'CATL': ['CONTEMPORARY AMPEREX', 'NINGDE CATL'],
    'IFLYTEK': ['IFLYTEK CO', 'ANHUI IFLYTEK'],
    'CAMBRICON': ['CAMBRICON TECH'],
    'HORIZON ROBOTICS': ['HORIZON ROBOTICS'],
    'UNISOC': ['UNISOC COMM', 'UNISOC SHANGHAI'],
    'ROCKCHIP': ['FUZHOU ROCKCHIP', 'ROCKCHIP ELECTRON'],
}

chinese_entities = set()
company_breakdown = {}

for company, patterns in high_confidence_companies.items():
    company_ids = set()

    for pattern in patterns:
        # Search across ALL records (NULL and non-NULL)
        # SECURITY: Use parameterized query instead of f-string
        search_pattern = f'%{pattern}%'
        cur.execute("""
            SELECT rf_id, ee_name, ee_city, ee_country
            FROM uspto_assignee
            WHERE UPPER(ee_name) LIKE ?
        """, (search_pattern,))

        matches = cur.fetchall()
        for rf_id, name, city, country in matches:
            company_ids.add(rf_id)

    if company_ids:
        chinese_entities.update(company_ids)
        company_breakdown[company] = len(company_ids)

# Sort and display
sorted_companies = sorted(company_breakdown.items(), key=lambda x: x[1], reverse=True)

print(f"\nFound {len(chinese_entities):,} records from {len(sorted_companies)} high-confidence Chinese companies")
print("\nTop 20 Companies:")
for i, (company, count) in enumerate(sorted_companies[:20], 1):
    print(f"{i:2d}. {company:25s}: {count:,}")

# ============================================================================
# TIER 1 CHINESE CITIES (Major Tech Hubs Only)
# ============================================================================
print("\n" + "=" * 80)
print("TIER 1 CHINESE CITIES (Tech Hubs)")
print("=" * 80)

tier1_cities = {
    'BEIJING': ['BEIJING', 'PEKING'],
    'SHANGHAI': ['SHANGHAI'],
    'SHENZHEN': ['SHENZHEN', 'SHENZEN'],  # Common misspelling
    'GUANGZHOU': ['GUANGZHOU', 'CANTON'],
    'HANGZHOU': ['HANGZHOU'],
    'NANJING': ['NANJING', 'NANKING'],
    'SUZHOU': ['SUZHOU'],
    'WUHAN': ['WUHAN'],
    'CHENGDU': ['CHENGDU'],
    'XIAN': ['XIAN', 'XI AN'],
    'DONGGUAN': ['DONGGUAN'],
    'FOSHAN': ['FOSHAN'],
    'NINGBO': ['NINGBO'],
    'WUXI': ['WUXI'],
    'QINGDAO': ['QINGDAO', 'TSINGTAO'],
    'DALIAN': ['DALIAN'],
    'XIAMEN': ['XIAMEN'],
}

city_entities = set()
city_breakdown = {}

for city_name, patterns in tier1_cities.items():
    city_ids = set()

    for pattern in patterns:
        # SECURITY: Use parameterized query instead of f-string
        cur.execute("""
            SELECT rf_id, ee_name, ee_city, ee_country
            FROM uspto_assignee
            WHERE UPPER(ee_city) = ?
            AND (ee_country IS NULL OR ee_country = '' OR ee_country LIKE '%CHINA%')
        """, (pattern,))

        matches = cur.fetchall()
        for rf_id, name, city, country in matches:
            city_ids.add(rf_id)

    if city_ids:
        city_entities.update(city_ids)
        city_breakdown[city_name] = len(city_ids)

sorted_cities = sorted(city_breakdown.items(), key=lambda x: x[1], reverse=True)

print(f"\nFound {len(city_entities):,} records from {len(sorted_cities)} Tier 1 Chinese cities")
print("\nTop Cities:")
for i, (city, count) in enumerate(sorted_cities, 1):
    print(f"{i:2d}. {city:15s}: {count:,}")

# ============================================================================
# EXPLICIT CHINA COUNTRY CODES
# ============================================================================
print("\n" + "=" * 80)
print("EXPLICIT CHINA COUNTRY CODES")
print("=" * 80)

country_entities = set()

country_patterns = [
    "ee_country = 'CN'",
    "ee_country = 'CHN'",
    "ee_country = 'CHINA'",
    "ee_country LIKE 'P.R. CHINA%'",
    "ee_country LIKE 'PEOPLE%REPUBLIC%CHINA%'",
    "ee_country LIKE '%CHINA (MAINLAND)%'",
    "ee_country = 'PRC'",
]

for pattern in country_patterns:
    # SECURITY: Avoid f-string in execute() - pattern is a hardcoded WHERE clause
    cur.execute("SELECT rf_id FROM uspto_assignee WHERE " + pattern)
    ids = {row[0] for row in cur.fetchall()}
    country_entities.update(ids)

print(f"\nFound {len(country_entities):,} records with explicit China country codes")

# ============================================================================
# CHINESE POSTAL CODES (High Confidence Regions)
# ============================================================================
print("\n" + "=" * 80)
print("CHINESE POSTAL CODES (Major Tech Regions)")
print("=" * 80)

# Focus on known tech hub postal code prefixes
tech_hub_postcodes = [
    ('100', 'Beijing'),
    ('200', 'Shanghai'),
    ('518', 'Shenzhen'),
    ('510', 'Guangzhou'),
    ('310', 'Hangzhou'),
    ('210', 'Nanjing'),
    ('215', 'Suzhou'),
    ('430', 'Wuhan'),
    ('610', 'Chengdu'),
    ('710', "Xi'an"),
]

postal_entities = set()
postal_breakdown = {}

for prefix, region in tech_hub_postcodes:
    # SECURITY: Use parameterized query instead of f-string
    postcode_pattern = f'{prefix}%'
    cur.execute("""
        SELECT rf_id FROM uspto_assignee
        WHERE ee_postcode LIKE ?
        AND LENGTH(ee_postcode) = 6
        AND ee_postcode GLOB '[1-9][0-9][0-9][0-9][0-9][0-9]'
        AND (ee_country IS NULL OR ee_country = '' OR ee_country LIKE '%CHINA%')
    """, (postcode_pattern,))

    ids = {row[0] for row in cur.fetchall()}
    postal_entities.update(ids)
    if ids:
        postal_breakdown[region] = len(ids)

sorted_postal = sorted(postal_breakdown.items(), key=lambda x: x[1], reverse=True)

print(f"\nFound {len(postal_entities):,} records with Chinese tech hub postal codes")
print("\nTop Regions:")
for i, (region, count) in enumerate(sorted_postal, 1):
    print(f"{i:2d}. {region:15s}: {count:,}")

# ============================================================================
# ADDRESS CONTAINS "CHINA" (Filtered)
# ============================================================================
print("\n" + "=" * 80)
print("ADDRESS CONTAINS 'CHINA' (Filtered)")
print("=" * 80)

cur.execute("""
    SELECT rf_id, ee_name, ee_address_1, ee_country
    FROM uspto_assignee
    WHERE (ee_address_1 LIKE '% CHINA' OR ee_address_1 LIKE '%, CHINA%')
    OR (ee_address_2 LIKE '% CHINA' OR ee_address_2 LIKE '%, CHINA%')
""")

address_matches = cur.fetchall()
address_entities = set()

# Filter out false positives (e.g., "CHINA GARDEN ROAD")
false_positive_patterns = [
    'CHINA GARDEN', 'CHINA LAKE', 'CHINA SPRING', 'CHINA GROVE',
    'CHINA HILL', 'CHINA BASIN', 'CHINATOWN',
]

for rf_id, name, addr, country in address_matches:
    addr_upper = addr.upper() if addr else ""
    is_false_positive = any(fp in addr_upper for fp in false_positive_patterns)

    if not is_false_positive:
        address_entities.add(rf_id)

print(f"\nFound {len(address_entities):,} records with 'CHINA' in address (after filtering)")

# ============================================================================
# COMBINED RESULTS WITH CONFIDENCE SCORING
# ============================================================================
print("\n" + "=" * 80)
print("COMBINED RESULTS WITH CONFIDENCE SCORING")
print("=" * 80)

# Union all sets
all_chinese = (chinese_entities | city_entities | country_entities |
               postal_entities | address_entities)

# Calculate confidence tiers
very_high_confidence = country_entities | chinese_entities
high_confidence = very_high_confidence | city_entities
medium_confidence = high_confidence | postal_entities | address_entities

print(f"\nTotal Chinese USPTO Assignees: {len(all_chinese):,}")
print(f"\nConfidence Breakdown:")
print(f"  VERY HIGH (Country code OR known company): {len(very_high_confidence):,}")
print(f"  HIGH (+ Tier 1 cities):                    {len(high_confidence):,}")
print(f"  MEDIUM (+ Postal codes + Addresses):       {len(medium_confidence):,}")

# Signal overlap analysis
print(f"\nSignal Breakdown:")
print(f"  Explicit country codes:    {len(country_entities):,}")
print(f"  Known Chinese companies:   {len(chinese_entities):,}")
print(f"  Tier 1 cities:             {len(city_entities):,}")
print(f"  Tech hub postal codes:     {len(postal_entities):,}")
print(f"  Address contains 'CHINA':  {len(address_entities):,}")

# Multiple signal validation
multiple_signals = set()
for rf_id in all_chinese:
    signal_count = sum([
        rf_id in country_entities,
        rf_id in chinese_entities,
        rf_id in city_entities,
        rf_id in postal_entities,
        rf_id in address_entities,
    ])
    if signal_count >= 2:
        multiple_signals.add(rf_id)

print(f"\n  Multiple signals (2+):     {len(multiple_signals):,} ({len(multiple_signals)*100/len(all_chinese):.1f}%)")

# ============================================================================
# COMPARISON WITH OTHER COUNTRIES
# ============================================================================
print("\n" + "=" * 80)
print("COMPARISON WITH OTHER COUNTRIES")
print("=" * 80)

countries = [
    ('JAPAN', 'JAPAN'),
    ('GERMANY', 'GERMANY'),
    ('KOREA', "KOREA%"),
    ('FRANCE', 'FRANCE'),
    ('UNITED KINGDOM', 'UNITED KINGDOM'),
    ('CANADA', 'CANADA'),
]

print("\nCountry Rankings:")
for i, (country_name, pattern) in enumerate(countries, 1):
    # SECURITY: Use parameterized query instead of f-string
    cur.execute("SELECT COUNT(DISTINCT rf_id) FROM uspto_assignee WHERE ee_country LIKE ?", (pattern,))
    count = cur.fetchone()[0]
    print(f"{i}. {country_name:20s}: {count:,}")

print(f"\n7. CHINA (multi-signal):    {len(all_chinese):,}")

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80)

conn.close()
