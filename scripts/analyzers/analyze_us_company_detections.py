#!/usr/bin/env python3
"""
Analyze US Company False Positives
"""

import sqlite3
import re

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

CHINESE_NAME_PATTERNS = {
    'beijing', 'shanghai', 'guangzhou', 'shenzhen',
    'china', 'chinese', 'sino', 'huawei', 'zte',
    'alibaba', 'tencent', 'baidu', 'lenovo',
    'haier', 'xiaomi', 'byd', 'geely'
}

def find_matching_pattern(name):
    """Find which pattern matches"""
    if not name:
        return []

    name_lower = name.lower()
    matches = []

    for pattern in CHINESE_NAME_PATTERNS:
        if pattern in name_lower:
            word_pattern = r'\b' + re.escape(pattern) + r'\b'
            if re.search(word_pattern, name_lower):
                matches.append((pattern, 'word_boundary'))
            else:
                matches.append((pattern, 'substring'))

    return matches

conn = sqlite3.connect(MAIN_DB)
cursor = conn.cursor()

# Get US companies with both name detections
cursor.execute("""
    SELECT
        recipient_name,
        vendor_name,
        recipient_country_code,
        COUNT(*) as count
    FROM usaspending_china_305
    WHERE detection_types = '["chinese_name_recipient", "chinese_name_vendor"]'
      AND (recipient_country_code = 'USA' OR recipient_country_code = 'UNITED STATES')
    GROUP BY recipient_name, vendor_name
    ORDER BY count DESC
    LIMIT 20
""")

records = cursor.fetchall()

print("=" * 80)
print("TOP 20 US COMPANIES DETECTED AS CHINESE")
print("=" * 80)

for recipient, vendor, country, count in records:
    print(f"\n{count:4d} | {vendor if vendor else recipient}")

    # Analyze what pattern matched
    if recipient:
        matches = find_matching_pattern(recipient)
        if matches:
            print(f"       Recipient: {recipient[:60]}")
            for pattern, match_type in matches:
                print(f"         - '{pattern}' ({match_type})")

    if vendor:
        matches = find_matching_pattern(vendor)
        if matches:
            print(f"       Vendor: {vendor[:60]}")
            for pattern, match_type in matches:
                print(f"         - '{pattern}' ({match_type})")

conn.close()
