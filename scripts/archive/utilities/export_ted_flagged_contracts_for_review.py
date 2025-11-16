"""
Export TED Flagged Contracts for Manual Review
Creates Excel file with all 295 flagged contracts and detection reason analysis
"""

import sqlite3
import pandas as pd
import re
from datetime import datetime

# Database path
DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'
OUTPUT_FILE = 'analysis/TED_295_FLAGGED_CONTRACTS_MANUAL_REVIEW.xlsx'

def analyze_flag_reason(row):
    """
    Analyze why a contract might have been flagged as Chinese-related.
    Returns a detailed reason string.
    """
    reasons = []

    # Check contractor name
    name = str(row['contractor_name']) if row['contractor_name'] else ''

    # Chinese characters
    if re.search(r'[\u4e00-\u9fff]', name):
        reasons.append("CHINESE_CHARACTERS_IN_NAME")

    # Chinese keywords (case insensitive)
    chinese_keywords = [
        'china', 'chinese', 'beijing', 'shanghai', 'huawei', 'zte',
        'alibaba', 'tencent', 'shenzhen', 'guangzhou', 'hong kong',
        'macau', 'hk', 'prc', 'peoples republic', 'cnooc', 'sinopec',
        'petrochina', 'byd', 'lenovo', 'xiaomi', 'oppo', 'vivo',
        'haier', 'midea', 'gree', 'sany', 'zoomlion', 'sinotruk'
    ]

    name_lower = name.lower()
    matched_keywords = [kw for kw in chinese_keywords if kw in name_lower]
    if matched_keywords:
        reasons.append(f"KEYWORDS: {', '.join(matched_keywords)}")

    # Check country codes
    country = str(row['contractor_country']) if row['contractor_country'] else ''
    iso_country = str(row['iso_country']) if row['iso_country'] else ''

    if country.upper() in ['CN', 'CHN', 'HK', 'HKG', 'MO', 'MAC']:
        reasons.append(f"COUNTRY_CODE: {country}")
    elif iso_country.upper() in ['CN', 'CHN', 'HK', 'HKG', 'MO', 'MAC']:
        reasons.append(f"ISO_COUNTRY: {iso_country}")

    # Check address
    address = str(row['contractor_address']) if row['contractor_address'] else ''
    if re.search(r'[\u4e00-\u9fff]', address):
        reasons.append("CHINESE_CHARACTERS_IN_ADDRESS")

    address_lower = address.lower()
    if any(city in address_lower for city in ['beijing', 'shanghai', 'shenzhen', 'guangzhou', 'hong kong']):
        reasons.append("CHINESE_CITY_IN_ADDRESS")

    # Check for Chinese company suffixes
    chinese_suffixes = ['有限公司', '股份有限公司', 'co., ltd', 'limited', 'group co']
    if any(suffix in name_lower for suffix in chinese_suffixes):
        # Only flag if combined with other indicators
        if any('CHINESE' in r or 'KEYWORD' in r or 'COUNTRY' in r for r in reasons):
            reasons.append("CHINESE_COMPANY_SUFFIX")

    if not reasons:
        return "UNKNOWN - Manual flagging or historical data"

    return " | ".join(reasons)

def main():
    """Export flagged contracts to Excel with analysis."""

    print("="*80)
    print("TED FLAGGED CONTRACTS EXPORT FOR MANUAL REVIEW")
    print("="*80)
    print()

    # Connect to database
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH, timeout=60)

    # Query flagged contracts
    print("Querying 295 flagged contracts...")
    query = """
        SELECT
            id,
            notice_number,
            publication_date,
            form_type,
            contract_title,
            contractor_name,
            contractor_country,
            contractor_address,
            contractor_city,
            contractor_postal_code,
            iso_country,
            nuts_code,
            place_of_performance,
            value_total as contract_value,
            currency as contract_currency,
            cpv_code,
            cpv_main as cpv_description,
            ca_name as buyer_name,
            ca_country as buyer_country,
            is_chinese_related,
            chinese_indicators,
            chinese_confidence,
            detection_rationale
        FROM ted_contracts_production
        WHERE is_chinese_related = 1
        ORDER BY publication_date DESC, id
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"  Found {len(df):,} flagged contracts")
    print()

    # Analyze flag reasons
    print("Analyzing flag reasons...")
    df['flag_reason'] = df.apply(analyze_flag_reason, axis=1)

    # Add confidence assessment
    def assess_confidence(reason):
        """Assess confidence that this is truly Chinese-related."""
        if 'CHINESE_CHARACTERS' in reason:
            return 'HIGH'
        elif 'COUNTRY_CODE: CN' in reason or 'COUNTRY_CODE: HK' in reason:
            return 'HIGH'
        elif 'huawei' in reason.lower() or 'zte' in reason.lower():
            return 'HIGH'
        elif 'KEYWORDS' in reason and len(reason.split('|')) > 1:
            return 'MEDIUM'
        elif 'KEYWORDS' in reason:
            return 'LOW-MEDIUM'
        else:
            return 'UNKNOWN'

    df['confidence'] = df['flag_reason'].apply(assess_confidence)

    # Reorder columns for better readability
    columns_order = [
        'id',
        'confidence',
        'flag_reason',
        'contractor_name',
        'contractor_country',
        'iso_country',
        'contractor_city',
        'contractor_address',
        'contract_title',
        'contract_value',
        'contract_currency',
        'publication_date',
        'notice_number',
        'form_type',
        'buyer_name',
        'buyer_country',
        'cpv_code',
        'cpv_description',
        'nuts_code',
        'place_of_performance',
        'contractor_postal_code',
        'is_chinese_related',
        'chinese_indicators',
        'chinese_confidence',
        'detection_rationale'
    ]

    df = df[columns_order]

    # Count by confidence level
    print()
    print("Confidence Level Distribution:")
    confidence_counts = df['confidence'].value_counts()
    for level, count in confidence_counts.items():
        print(f"  {level:15} {count:4,} ({count/len(df)*100:5.1f}%)")
    print()

    # Count by flag reason patterns
    print("Top Flag Reason Patterns:")
    reason_counts = df['flag_reason'].value_counts().head(10)
    for reason, count in reason_counts.items():
        print(f"  {count:3,} contracts: {reason[:80]}")
    print()

    # Export to Excel
    print(f"Exporting to Excel: {OUTPUT_FILE}")

    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        # Main sheet with all contracts
        df.to_excel(writer, sheet_name='All Contracts', index=False)

        # Summary sheet
        summary_data = {
            'Metric': [
                'Total Flagged Contracts',
                'High Confidence',
                'Medium Confidence',
                'Low-Medium Confidence',
                'Unknown Confidence',
                '',
                'Export Date',
                'Database'
            ],
            'Value': [
                len(df),
                len(df[df['confidence'] == 'HIGH']),
                len(df[df['confidence'] == 'MEDIUM']),
                len(df[df['confidence'] == 'LOW-MEDIUM']),
                len(df[df['confidence'] == 'UNKNOWN']),
                '',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                DB_PATH
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # High confidence only
        high_conf = df[df['confidence'] == 'HIGH']
        if len(high_conf) > 0:
            high_conf.to_excel(writer, sheet_name='High Confidence', index=False)

        # Medium confidence only
        med_conf = df[df['confidence'].isin(['MEDIUM', 'LOW-MEDIUM'])]
        if len(med_conf) > 0:
            med_conf.to_excel(writer, sheet_name='Medium Confidence', index=False)

        # Unknown/Manual only
        unknown_conf = df[df['confidence'] == 'UNKNOWN']
        if len(unknown_conf) > 0:
            unknown_conf.to_excel(writer, sheet_name='Unknown-Manual', index=False)

        # Get workbook to auto-size columns
        workbook = writer.book
        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

    print()
    print("="*80)
    print("EXPORT COMPLETE")
    print("="*80)
    print()
    print(f"Excel file created: {OUTPUT_FILE}")
    print()
    print("Sheets created:")
    print("  1. All Contracts - All 295 flagged contracts")
    print("  2. Summary - Statistics and metadata")
    print("  3. High Confidence - Contracts with strong Chinese indicators")
    print("  4. Medium Confidence - Contracts with moderate indicators")
    print("  5. Unknown-Manual - Contracts flagged by unknown/manual methods")
    print()
    print("Columns included:")
    print("  - confidence: Assessment of how likely this is Chinese-related")
    print("  - flag_reason: Detailed explanation of detection indicators")
    print("  - contractor_name: Company name")
    print("  - contractor_country: Country code")
    print("  - contract_title: What the contract is for")
    print("  - contract_value: Contract amount")
    print("  - Plus 15 additional data fields")
    print()
    print("Next step: Manual review to validate true positives")
    print()

if __name__ == "__main__":
    main()
