#!/usr/bin/env python3
"""
generate_tier2_non_china_sample.py - Generate TIER_2 Non-China Sample

Generates sample of TIER_2 records where the country is NOT China or US.
This helps identify false positives detected by name/description rather than location.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

def generate_non_china_sample():
    """Generate TIER_2 sample excluding China and US"""

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)

    print("="*60)
    print("TIER_2 NON-CHINA/NON-US COMPLETE EXPORT")
    print("="*60)
    print(f"\nDatabase: {db_path}")
    print("Exporting ALL TIER_2 records where country is NOT China/US")
    print("Purpose: Identify false positives from name/description detection")

    # Query TIER_2 records excluding China and US
    query = """
        SELECT
            'usaspending_china_305' as source_table,
            recipient_name as Recipient_Name,
            vendor_name as Vendor_Name,
            award_description as Award_Description,
            recipient_country_code as Recipient_Country,
            recipient_country_name as Recipient_Country_Name,
            pop_country_code as POP_Country,
            pop_country_name as POP_Country_Name,
            importance_tier as Importance_Tier,
            highest_confidence as Confidence_Tier,
            detection_types as Detection_Types,
            detection_details as Detection_Details
        FROM usaspending_china_305
        WHERE importance_tier = 'TIER_2'
          AND (
            -- Exclude China
            (recipient_country_code NOT IN ('CHN', 'CHINA', 'CN') OR recipient_country_code IS NULL)
            AND (recipient_country_name NOT LIKE '%CHINA%' OR recipient_country_name IS NULL)
            AND (pop_country_code NOT IN ('CHN', 'CHINA', 'CN') OR pop_country_code IS NULL)
            AND (pop_country_name NOT LIKE '%CHINA%' OR pop_country_name IS NULL)
            -- Exclude US
            AND (recipient_country_code NOT IN ('USA', 'US', 'USA') OR recipient_country_code IS NULL)
            AND (recipient_country_name NOT LIKE '%UNITED STATES%' OR recipient_country_name IS NULL)
            AND (pop_country_code NOT IN ('USA', 'US', 'USA') OR pop_country_code IS NULL)
            AND (pop_country_name NOT LIKE '%UNITED STATES%' OR pop_country_name IS NULL)
          )
        ORDER BY recipient_country_code, recipient_name
    """

    df = pd.read_sql(query, conn)

    print(f"\n[OK] Found {len(df)} TIER_2 records from non-China/non-US countries")

    if len(df) == 0:
        print("\n[!] No records found - all TIER_2 are China or US")
        conn.close()
        return

    # Add review columns
    df['Manual_Review'] = ''
    df['Is_False_Positive'] = ''
    df['Correct_Action'] = ''
    df['Notes'] = ''

    # Analyze what we found
    print("\nCountry Breakdown:")

    # Recipient countries
    recip_countries = df['Recipient_Country'].value_counts()
    if len(recip_countries) > 0:
        print("\n  Recipient Countries:")
        for country, count in recip_countries.head(10).items():
            if pd.notna(country):
                print(f"    {country}: {count}")

    # POP countries
    pop_countries = df['POP_Country'].value_counts()
    if len(pop_countries) > 0:
        print("\n  Place of Performance Countries:")
        for country, count in pop_countries.head(10).items():
            if pd.notna(country):
                print(f"    {country}: {count}")

    # Detection types
    print("\n  Detection Types:")
    detection_counts = {}
    for types in df['Detection_Types'].dropna():
        try:
            import json
            type_list = json.loads(types)
            for det_type in type_list:
                detection_counts[det_type] = detection_counts.get(det_type, 0) + 1
        except:
            pass

    for det_type, count in sorted(detection_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {det_type}: {count}")

    # Save sample
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("data/processed/usaspending_manual_review")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"tier2_non_china_COMPLETE_{timestamp}.csv"
    df.to_csv(output_path, index=False)

    print("\n" + "="*60)
    print("COMPLETE EXPORT FINISHED")
    print("="*60)

    print(f"\nTotal records exported: {len(df)}")
    print("(This is ALL non-China/non-US TIER_2 records)")
    print(f"\nBreakdown by confidence:")
    print(df['Confidence_Tier'].value_counts())

    print(f"\nOutput: {output_path}")

    print("\n" + "="*60)
    print("ANALYSIS NOTES")
    print("="*60)
    print("\nThese records were detected as China-related but are NOT in China/US.")
    print("\nLikely detection reasons:")
    print("  - Name contains 'China' or Chinese-sounding words")
    print("  - Description mentions China")
    print("  - Vendor name contains Chinese elements")
    print("  - False positive patterns (like Hungarian Ministry of Defense)")
    print("\nManual review should identify:")
    print("  - False positives to remove")
    print("  - Legitimate third-country entities with China connections")
    print("  - New false positive patterns to add to filters")

    print("\n" + "="*60)

    conn.close()

    return output_path

if __name__ == "__main__":
    generate_non_china_sample()
