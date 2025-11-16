#!/usr/bin/env python3
"""
Investigate Company Ownership
Distinguish US subsidiaries of Chinese companies from false positives
"""

import sqlite3

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

def investigate_company(company_name, limit=5):
    """Investigate a specific company"""

    conn = sqlite3.connect(MAIN_DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            transaction_id,
            recipient_name,
            vendor_name,
            recipient_country_code,
            recipient_country_name,
            pop_country_code,
            pop_country_name,
            award_description,
            detection_types
        FROM usaspending_china_305
        WHERE vendor_name LIKE ? OR recipient_name LIKE ?
        LIMIT ?
    """, (f"%{company_name}%", f"%{company_name}%", limit))

    records = cursor.fetchall()
    conn.close()

    return records

# Companies to investigate
companies = [
    "LENOVO",
    "MSD BIZTECH",
    "SKYDIVE ELSINORE",
    "OZTECH",
    "KACHINA",
    "LBYD",
    "JUSINO",
    "CHINAULT",
    "EZTEQ",
    "AZTEK COMPUTERS",
    "CASINO CREEK",
    "UNITED GLASSWARE"
]

print("=" * 80)
print("COMPANY OWNERSHIP INVESTIGATION")
print("=" * 80)
print("\nChecking if these are Chinese-owned or just substring matches...")
print("=" * 80)

for company in companies:
    print(f"\n{'=' * 80}")
    print(f"COMPANY: {company}")
    print(f"{'=' * 80}")

    records = investigate_company(company, limit=3)

    if not records:
        print(f"  No records found")
        continue

    # Analyze first record in detail
    (tid, recipient, vendor, recipient_country_code, recipient_country_name,
     pop_country_code, pop_country_name, description, detection_types) = records[0]

    print(f"\nRecord count: {len(records)} (showing first 3)")
    print(f"\nSample transaction: {tid}")
    print(f"  Recipient: {recipient}")
    print(f"  Vendor: {vendor}")
    print(f"  Recipient Country: {recipient_country_name or recipient_country_code or 'N/A'}")
    print(f"  PoP Country: {pop_country_name or pop_country_code or 'N/A'}")
    print(f"  Description: {description[:100] if description else 'N/A'}...")

    # Determine ownership
    print(f"\nOWNERSHIP ANALYSIS:")

    # Check for obvious Chinese ownership
    if "LENOVO" in company.upper():
        print(f"  Type: CHINESE-OWNED US SUBSIDIARY")
        print(f"  Owner: Lenovo Group Limited (China)")
        print(f"  Classification: INCLUDE - This IS a Chinese company")

    elif recipient_country_code == "CHN" or recipient_country_name == "CHINA":
        print(f"  Type: CHINESE ENTITY")
        print(f"  Recipient in China")
        print(f"  Classification: INCLUDE")

    elif pop_country_code == "CHN" or pop_country_name == "CHINA":
        print(f"  Type: WORK PERFORMED IN CHINA")
        print(f"  But recipient country: {recipient_country_name or recipient_country_code}")
        print(f"  Classification: UNCLEAR - needs review")

    elif recipient_country_code == "USA" or recipient_country_code == "UNITED STATES":
        # Check description for clues
        desc_upper = (description or '').upper()

        # Look for Chinese ownership indicators
        chinese_indicators = [
            'BEIJING', 'SHANGHAI', 'SHENZHEN', 'GUANGZHOU',
            'CHINA OPERATIONS', 'CHINESE SUBSIDIARY',
            'LENOVO GROUP', 'HUAWEI', 'ZTE CORP'
        ]

        has_chinese_indicator = any(ind in desc_upper for ind in chinese_indicators)

        if has_chinese_indicator:
            print(f"  Type: POSSIBLY CHINESE-OWNED")
            print(f"  Description mentions Chinese operations")
            print(f"  Classification: NEEDS VERIFICATION")
        else:
            # Check if it's a name match issue
            if any(x in company.upper() for x in ['SINO', 'CHINA', 'ZTE', 'BYD']):
                print(f"  Type: LIKELY FALSE POSITIVE (substring match)")
                print(f"  US company with name containing Chinese pattern")
                print(f"  Classification: EXCLUDE")
            else:
                print(f"  Type: UNCLEAR")
                print(f"  Classification: NEEDS MANUAL REVIEW")
    else:
        print(f"  Type: FOREIGN (non-US, non-China)")
        print(f"  Country: {recipient_country_name or recipient_country_code}")
        print(f"  Classification: UNCLEAR")

print("\n" + "=" * 80)
print("SUMMARY RECOMMENDATIONS")
print("=" * 80)

print("\nINCLUDE (Chinese-owned companies):")
print("  - Lenovo (United States) Inc. - US subsidiary of Lenovo Group (China)")

print("\nEXCLUDE (American companies, substring matches):")
print("  - SKYDIVE ELSINORE - California skydiving company (SINO)")
print("  - KACHINA - Native American word (CHINA)")
print("  - JUSINO-BERRIOS - Spanish surname (SINO)")
print("  - CHINAULT - Person's name (CHINA)")
print("  - CASINO CREEK - US company (SINO)")
print("  - OZTECH - US company (ZTE)")
print("  - EZTEQ - US company (ZTE)")
print("  - AZTEK COMPUTERS - US company (ZTE)")
print("  - LBYD FEDERAL - US company (BYD)")
print("  - MSD BIZTECH - US company (ZTE)")
print("  - UNITED GLASSWARE & CHINA CO. - US tableware (CHINA)")

print("\nRECOMMENDATION:")
print("  Remove all US-country records EXCEPT those with verified Chinese ownership")
print("  Keep: Lenovo (US subsidiaries of Chinese companies)")
print("  Remove: All others with USA country code")
