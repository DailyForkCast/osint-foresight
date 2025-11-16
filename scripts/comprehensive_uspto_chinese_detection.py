#!/usr/bin/env python3
"""
Comprehensive USPTO Chinese Assignee Detection
Multi-signal approach to identify ALL Chinese patent assignees
"""

import sqlite3
from collections import defaultdict

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

# ============================================================================
# SECURITY: Whitelist validation to prevent SQL injection
# ============================================================================

# Allowed SQL WHERE conditions for country detection
ALLOWED_CONDITIONS = {
    "ee_country = 'CHINA'",
    "ee_country LIKE '%P.R.%' AND ee_country LIKE '%CHINA%'",
    "ee_country LIKE '%PEOPLE%REPUBLIC%'",
    "ee_country = 'CHN'",
    "ee_country = 'CN'"
}

# Allowed Chinese city names
ALLOWED_CITIES = {
    'BEIJING', 'SHANGHAI', 'SHENZHEN', 'GUANGZHOU', 'HANGZHOU',
    'NANJING', 'WUHAN', 'CHENGDU', 'TIANJIN', 'CHONGQING',
    'SUZHOU', 'XIAN', 'DONGGUAN', 'QINGDAO', 'DALIAN',
    'SHENYANG', 'HARBIN', 'CHANGSHA', 'KUNMING', 'XIAMEN',
    'FOSHAN', 'NINGBO', 'ZHENGZHOU', 'JINAN', 'HEFEI'
}

# Allowed Chinese company names
ALLOWED_COMPANIES = {
    'HUAWEI', 'ZTE', 'ALIBABA', 'TENCENT', 'XIAOMI', 'BYD',
    'LENOVO', 'HAIER', 'TCL', 'OPPO', 'VIVO', 'ONEPLUS',
    'DJI', 'HIKVISION', 'DAHUA', 'NUCTECH', 'BAIDU',
    'MEGVII', 'SENSETIME', 'BYTEDANCE', 'MEITUAN',
    'CHINA NATIONAL', 'CHINA TELECOM', 'CHINA MOBILE',
    'CHINA UNICOM', 'SINOPEC', 'PETROCHINA', 'CNOOC'
}

def validate_sql_condition(condition):
    """
    SECURITY: Validate SQL WHERE condition against whitelist.
    Only allows hardcoded, safe SQL conditions.
    """
    if condition not in ALLOWED_CONDITIONS:
        raise ValueError(f"Invalid SQL condition: {condition}. Not in whitelist.")
    return condition

def validate_city_name(city):
    """
    SECURITY: Validate city name against whitelist.
    """
    if city not in ALLOWED_CITIES:
        raise ValueError(f"Invalid city name: {city}. Not in whitelist.")
    return city

def validate_company_name(company):
    """
    SECURITY: Validate company name against whitelist.
    """
    if company not in ALLOWED_COMPANIES:
        raise ValueError(f"Invalid company name: {company}. Not in whitelist.")
    return company

def validate_integer_list(id_list, max_count=1000):
    """
    SECURITY: Validate that all items are integers and limit list size.
    Prevents SQL injection through ID list construction.
    """
    if len(id_list) > max_count:
        raise ValueError(f"ID list too large: {len(id_list)} > {max_count}")

    safe_ids = []
    for item in id_list:
        if not isinstance(item, int):
            try:
                safe_ids.append(int(item))
            except (ValueError, TypeError):
                raise ValueError(f"Invalid ID (not an integer): {item}")
        else:
            safe_ids.append(item)

    return safe_ids

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print('='*80)
print('COMPREHENSIVE USPTO CHINESE ASSIGNEE DETECTION')
print('='*80)

# Track unique IDs to avoid double-counting
chinese_ids = set()
detection_methods = defaultdict(int)

# 1. Country field detection
print('\n1. COUNTRY FIELD DETECTION:')
country_queries = [
    ("CHINA", "ee_country = 'CHINA'"),
    ("P.R. CHINA", "ee_country LIKE '%P.R.%' AND ee_country LIKE '%CHINA%'"),
    ("PEOPLE'S REPUBLIC", "ee_country LIKE '%PEOPLE%REPUBLIC%'"),
    ("CHN", "ee_country = 'CHN'"),
    ("CN", "ee_country = 'CN'"),
]

for label, condition in country_queries:
    # SECURITY: Validate SQL condition before use
    safe_condition = validate_sql_condition(condition)
    cur.execute(f"SELECT rf_id FROM uspto_assignee WHERE {safe_condition}")
    ids = {row[0] for row in cur.fetchall()}
    count = len(ids)
    if count > 0:
        print(f"  {label:20}: {count:,}")
        chinese_ids.update(ids)
        detection_methods[label] = count

# 2. Chinese city detection
print('\n2. CHINESE CITY DETECTION:')
chinese_cities = [
    'BEIJING', 'SHANGHAI', 'SHENZHEN', 'GUANGZHOU', 'HANGZHOU',
    'NANJING', 'WUHAN', 'CHENGDU', 'TIANJIN', 'CHONGQING',
    'SUZHOU', 'XIAN', 'DONGGUAN', 'QINGDAO', 'DALIAN',
    'SHENYANG', 'HARBIN', 'CHANGSHA', 'KUNMING', 'XIAMEN',
    'FOSHAN', 'NINGBO', 'ZHENGZHOU', 'JINAN', 'HEFEI'
]

city_ids = set()
for city in chinese_cities:
    # SECURITY: Validate city name before use and use parameterized query
    safe_city = validate_city_name(city)
    cur.execute("SELECT rf_id FROM uspto_assignee WHERE UPPER(ee_city) LIKE ?", (f'%{safe_city}%',))
    ids = {row[0] for row in cur.fetchall()}
    if len(ids) > 0:
        print(f"  {safe_city:20}: {len(ids):,}")
        city_ids.update(ids)

chinese_ids.update(city_ids)
detection_methods['Chinese Cities'] = len(city_ids)

# 3. Address contains "CHINA"
print('\n3. ADDRESS FIELD DETECTION:')
cur.execute("""
    SELECT rf_id FROM uspto_assignee
    WHERE ee_address_1 LIKE '%CHINA%' OR ee_address_2 LIKE '%CHINA%'
""")
addr_ids = {row[0] for row in cur.fetchall()}
print(f"  Address contains CHINA: {len(addr_ids):,}")
chinese_ids.update(addr_ids)
detection_methods['Address CHINA'] = len(addr_ids)

# 4. Known Chinese companies (SOEs + major tech)
print('\n4. KNOWN CHINESE COMPANY NAMES:')
chinese_companies = [
    'HUAWEI', 'ZTE', 'ALIBABA', 'TENCENT', 'XIAOMI', 'BYD',
    'LENOVO', 'HAIER', 'TCL', 'OPPO', 'VIVO', 'ONEPLUS',
    'DJI', 'HIKVISION', 'DAHUA', 'NUCTECH', 'BAIDU',
    'MEGVII', 'SENSETIME', 'BYTEDANCE', 'MEITUAN',
    'CHINA NATIONAL', 'CHINA TELECOM', 'CHINA MOBILE',
    'CHINA UNICOM', 'SINOPEC', 'PETROCHINA', 'CNOOC'
]

company_ids = set()
for company in chinese_companies:
    # SECURITY: Validate company name before use and use parameterized query
    safe_company = validate_company_name(company)
    cur.execute("SELECT rf_id FROM uspto_assignee WHERE UPPER(ee_name) LIKE ?", (f'%{safe_company}%',))
    ids = {row[0] for row in cur.fetchall()}
    if len(ids) > 0:
        print(f"  {safe_company:20}: {len(ids):,}")
        company_ids.update(ids)

chinese_ids.update(company_ids)
detection_methods['Known Companies'] = len(company_ids)

# 5. Chinese postal codes (6 digits, starting 1-9, but exclude other Asian countries)
print('\n5. POSTAL CODE PATTERN (6-digit, excluding Japan/Korea/Taiwan):')
cur.execute("""
    SELECT rf_id FROM uspto_assignee
    WHERE LENGTH(ee_postcode) = 6
    AND ee_postcode GLOB '[1-9][0-9][0-9][0-9][0-9][0-9]'
    AND ee_country NOT IN ('JAPAN', 'KOREA, REPUBLIC OF', 'TAIWAN', 'KOREA', 'SINGAPORE')
    AND UPPER(ee_city) NOT LIKE '%TOKYO%'
    AND UPPER(ee_city) NOT LIKE '%OSAKA%'
    AND UPPER(ee_city) NOT LIKE '%SEOUL%'
    AND UPPER(ee_city) NOT LIKE '%TAIPEI%'
""")
postal_ids = {row[0] for row in cur.fetchall()}
print(f"  6-digit postal codes: {len(postal_ids):,}")
chinese_ids.update(postal_ids)
detection_methods['Postal Codes'] = len(postal_ids)

# Final count
print('\n' + '='*80)
print('FINAL RESULTS:')
print('='*80)
print(f'\nTotal unique Chinese assignees identified: {len(chinese_ids):,}')
print(f'\nDetection method breakdown:')
for method, count in sorted(detection_methods.items(), key=lambda x: x[1], reverse=True):
    print(f'  {method:25}: {count:,}')

# Sample records
print('\n' + '='*80)
print('SAMPLE CHINESE ASSIGNEES (first 20):')
print('='*80)
# SECURITY: Validate integer IDs before constructing IN clause
sample_ids = list(chinese_ids)[:20]
safe_ids = validate_integer_list(sample_ids, max_count=20)
# Use parameterized query with placeholders
placeholders = ','.join(['?' for _ in safe_ids])
cur.execute(f"""
    SELECT ee_name, ee_city, ee_country
    FROM uspto_assignee
    WHERE rf_id IN ({placeholders})
""", safe_ids)
for i, row in enumerate(cur.fetchall(), 1):
    print(f'{i:2}. {row[0][:50]:50} | {row[1][:20]:20} | {row[2]}')

# Compare to other countries
print('\n' + '='*80)
print('COMPARISON TO TOP COUNTRIES:')
print('='*80)
cur.execute("""
    SELECT ee_country, COUNT(*) as cnt
    FROM uspto_assignee
    WHERE ee_country IS NOT NULL
    GROUP BY ee_country
    ORDER BY cnt DESC
    LIMIT 15
""")
print(f'\n{"Country":30} | Count')
print('-'*50)
for country, count in cur.fetchall():
    marker = ' ← CHINA' if 'CHINA' in country.upper() else ''
    print(f'{country:30} | {count:,}{marker}')

print(f'\n{"TOTAL CHINESE (multi-signal)":30} | {len(chinese_ids):,} ← ACTUAL')

conn.close()

print('\n' + '='*80)
print('ANALYSIS COMPLETE')
print('='*80)
