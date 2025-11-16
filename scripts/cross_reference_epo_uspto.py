#!/usr/bin/env python3
"""
Cross-Reference EPO and USPTO Databases
Find Chinese companies in EPO that should also be in USPTO
"""

import sqlite3
from collections import Counter

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

print("=" * 80)
print("EPO <-> USPTO CROSS-REFERENCE ANALYSIS")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ============================================================================
# Get Top Chinese Companies from EPO
# ============================================================================
print("\n" + "=" * 80)
print("TOP CHINESE COMPANIES IN EPO")
print("=" * 80)

cur.execute("""
    SELECT applicant_name, COUNT(*) as patent_count
    FROM epo_patents
    WHERE applicant_country = 'CN'
    GROUP BY applicant_name
    ORDER BY patent_count DESC
    LIMIT 50
""")

epo_companies = cur.fetchall()

print(f"\nTop 50 Chinese companies in EPO ({len(epo_companies)} total):")
for i, (company, count) in enumerate(epo_companies[:20], 1):
    print(f"{i:2d}. {company[:50]:50s}: {count:,}")

#============================================================================
# Search for these companies in USPTO
# ============================================================================
print("\n" + "=" * 80)
print("SEARCHING EPO COMPANIES IN USPTO")
print("=" * 80)

found_in_uspto = []
not_found_in_uspto = []

for company, epo_count in epo_companies:
    # Extract key search terms from company name
    search_terms = []

    if 'HUAWEI' in company.upper():
        search_terms = ['HUAWEI']
    elif 'ZTE' in company.upper():
        search_terms = ['ZTE']
    elif 'XIAOMI' in company.upper():
        search_terms = ['XIAOMI']
    elif 'OPPO' in company.upper():
        search_terms = ['OPPO']
    elif 'VIVO' in company.upper():
        search_terms = ['VIVO']
    elif 'TENCENT' in company.upper():
        search_terms = ['TENCENT']
    elif 'ALIBABA' in company.upper():
        search_terms = ['ALIBABA']
    elif 'BAIDU' in company.upper():
        search_terms = ['BAIDU']
    elif 'BYTEDANCE' in company.upper() or 'TIKTOK' in company.upper():
        search_terms = ['BYTEDANCE', 'TIKTOK']
    elif 'LENOVO' in company.upper():
        search_terms = ['LENOVO']
    elif 'DJI' in company.upper():
        search_terms = ['DJI']
    elif 'BYD' in company.upper():
        search_terms = ['BYD COMPANY', 'BYD AUTO', 'BYD BATTERY']
    elif 'HIKVISION' in company.upper():
        search_terms = ['HIKVISION']
    elif 'DAHUA' in company.upper():
        search_terms = ['DAHUA']
    elif 'SENSETIME' in company.upper():
        search_terms = ['SENSETIME']
    elif 'MEGVII' in company.upper():
        search_terms = ['MEGVII']
    elif 'XPENG' in company.upper():
        search_terms = ['XPENG']
    elif 'NIO' in company.upper():
        search_terms = ['NIO INC', 'NIO USA', 'NEXTEV']
    elif 'GEELY' in company.upper():
        search_terms = ['GEELY']
    elif 'BOE' in company.upper() and 'TECHNOLOGY' in company.upper():
        search_terms = ['BOE TECHOLOG', 'BEIJING BOE']
    elif 'TCL' in company.upper():
        search_terms = ['TCL CORP', 'TCL COMM']
    elif 'HAIER' in company.upper():
        search_terms = ['HAIER']
    elif 'MIDEA' in company.upper():
        search_terms = ['MIDEA']
    elif 'GREE' in company.upper() and ('ELECTRIC' in company.upper() or 'ZHUHAI' in company.upper()):
        search_terms = ['GREE ELECTRIC', 'ZHUHAI GREE']
    elif 'HISENSE' in company.upper():
        search_terms = ['HISENSE']
    elif 'CATL' in company.upper() or 'AMPEREX' in company.upper():
        search_terms = ['CONTEMPORARY AMPEREX', 'CATL', 'NINGDE']
    elif 'SMIC' in company.upper() or 'SEMICONDUCTOR MANUFACTURING INTERNATIONAL' in company.upper():
        search_terms = ['SEMICONDUCTOR MANUFACTURING INTERNATIONAL', 'SMIC']
    elif 'UNISOC' in company.upper() or 'SPREADTRUM' in company.upper():
        search_terms = ['UNISOC', 'SPREADTRUM']
    elif 'ROCKCHIP' in company.upper():
        search_terms = ['ROCKCHIP']
    else:
        # Try to extract a distinctive term (first word or key identifier)
        words = company.upper().replace(',', '').replace('.', '').split()
        if len(words) >= 2:
            search_terms = [words[0], ' '.join(words[:2])]
        elif len(words) == 1 and len(words[0]) > 3:
            search_terms = [words[0]]

    if not search_terms:
        continue

    # Search USPTO for these terms
    uspto_count = 0
    for term in search_terms[:1]:  # Use first (most specific) term
        # SECURITY: Use parameterized query to prevent SQL injection
        cur.execute("""
            SELECT COUNT(DISTINCT rf_id)
            FROM uspto_assignee
            WHERE UPPER(ee_name) LIKE ?
        """, (f'%{term}%',))
        count = cur.fetchone()[0]
        uspto_count = max(uspto_count, count)

    if uspto_count > 0:
        found_in_uspto.append((company, epo_count, uspto_count, search_terms[0]))
    else:
        not_found_in_uspto.append((company, epo_count, search_terms[0]))

print(f"\n✓ Found in both EPO and USPTO: {len(found_in_uspto)}")
print(f"✗ In EPO but NOT in USPTO:     {len(not_found_in_uspto)}")

# Show companies found in both
print("\n" + "=" * 80)
print("COMPANIES IN BOTH EPO AND USPTO")
print("=" * 80)

found_in_uspto.sort(key=lambda x: x[1], reverse=True)  # Sort by EPO count

print(f"\nTop 20 (sorted by EPO patent count):")
for i, (company, epo_cnt, uspto_cnt, search_term) in enumerate(found_in_uspto[:20], 1):
    print(f"{i:2d}. {company[:35]:35s} | EPO: {epo_cnt:5,} | USPTO: {uspto_cnt:5,} | ('{search_term}')")

# Show companies NOT found in USPTO
if not_found_in_uspto:
    print("\n" + "=" * 80)
    print("⚠️  COMPANIES IN EPO BUT NOT FOUND IN USPTO")
    print("=" * 80)

    not_found_in_uspto.sort(key=lambda x: x[1], reverse=True)  # Sort by EPO count

    print(f"\nTop 20 missing companies:")
    for i, (company, epo_cnt, search_term) in enumerate(not_found_in_uspto[:20], 1):
        print(f"{i:2d}. {company[:50]:50s} | EPO: {epo_cnt:5,} | Search: '{search_term}'")

# ============================================================================
# Deep search for specific high-value missing companies
# ============================================================================
print("\n" + "=" * 80)
print("DEEP SEARCH FOR MISSING HIGH-VALUE COMPANIES")
print("=" * 80)

# Take top 5 missing companies and try broader searches
for company, epo_cnt, search_term in not_found_in_uspto[:5]:
    print(f"\n--- {company} (EPO: {epo_cnt:,}) ---")

    # Try various search strategies
    words = company.upper().replace(',', '').replace('.', '').split()

    strategies = [
        ('Full name', company[:30]),
        ('First word', words[0] if words else ''),
        ('Last word', words[-1] if len(words) > 1 else ''),
        ('First 2 words', ' '.join(words[:2]) if len(words) >= 2 else ''),
    ]

    for strategy_name, term in strategies:
        if not term or len(term) < 3:
            continue

        # SECURITY: Use parameterized query to prevent SQL injection
        cur.execute("""
            SELECT ee_name, ee_country
            FROM uspto_assignee
            WHERE UPPER(ee_name) LIKE ?
            LIMIT 3
        """, (f'%{term}%',))

        matches = cur.fetchall()
        if matches:
            print(f"  {strategy_name} ('{term}'): {len(matches)} matches")
            for name, country in matches[:2]:
                country_str = country if country else 'NULL'
                print(f"    - {name[:45]} | {country_str}")

print("\n" + "=" * 80)
print("Cross-reference analysis complete!")
print("=" * 80)

conn.close()
