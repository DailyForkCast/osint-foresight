#!/usr/bin/env python3
"""
generate_tier2_clean_sample.py - Generate New TIER_2 Sample

Generates stratified sample from cleaned TIER_2 data (post-reprocessing)
for manual validation of precision improvements.

Usage:
    python generate_tier2_clean_sample.py
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

def generate_tier2_sample():
    """Generate stratified sample from cleaned TIER_2 data"""

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)

    print("=" * 60)
    print("TIER_2 CLEAN SAMPLE GENERATION")
    print("=" * 60)
    print(f"\nDatabase: {db_path}")
    print("Post-reprocessing sample for precision validation")

    # Get TIER_2 counts by table and confidence
    # Using 305 table only (has vendor_name column)
    tables_info = [
        ('usaspending_china_305', 'recipient_name', 'vendor_name', 'award_description',
         'recipient_country_code', 'importance_tier', 'highest_confidence'),
    ]

    all_samples = []

    for table_name, recip_col, vendor_col, desc_col, country_col, imp_col, conf_col in tables_info:
        print(f"\n[{table_name}]")

        # Get TIER_2 count
        count_query = f"""
            SELECT COUNT(*) as count,
                   {conf_col} as confidence
            FROM {table_name}
            WHERE {imp_col} = 'TIER_2'
            GROUP BY {conf_col}
        """

        count_df = pd.read_sql(count_query, conn)
        print(f"  Total TIER_2 records: {count_df['count'].sum()}")

        for _, row in count_df.iterrows():
            conf = row['confidence']
            count = row['count']
            print(f"    {conf}: {count}")

        # Sample proportionally
        # Target: 300 total sample
        tier2_total = count_df['count'].sum()

        # Simple random sample from all TIER_2
        sample_size = min(300, tier2_total)  # Take up to 300 records

        print(f"  Sampling: {sample_size} records")

        # Query sample
        sample_query = f"""
            SELECT
                '{table_name}' as source_table,
                {recip_col} as Recipient_Name,
                {vendor_col} as Vendor_Name,
                {desc_col} as Award_Description,
                {country_col} as Country_Code,
                {imp_col} as Importance_Tier,
                {conf_col} as Confidence_Tier
            FROM {table_name}
            WHERE {imp_col} = 'TIER_2'
            ORDER BY RANDOM()
            LIMIT {sample_size}
        """

        sample_df = pd.read_sql(sample_query, conn)
        all_samples.append(sample_df)
        print(f"    Sampled {len(sample_df)} TIER_2 records")

    # Combine all samples
    combined_sample = pd.concat(all_samples, ignore_index=True)

    # Add validation columns
    combined_sample['Manual_Review'] = ''
    combined_sample['Is_True_Positive'] = ''
    combined_sample['Suggested_Tier'] = ''
    combined_sample['Notes'] = ''

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("data/processed/usaspending_manual_review")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"tier2_clean_sample_{timestamp}.csv"
    combined_sample.to_csv(output_path, index=False)

    print("\n" + "=" * 60)
    print("SAMPLE GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nTotal records sampled: {len(combined_sample)}")
    print(f"\nBreakdown by confidence:")
    print(combined_sample['Confidence_Tier'].value_counts())
    print(f"\nBreakdown by source:")
    print(combined_sample['source_table'].value_counts())

    print(f"\nOutput: {output_path}")
    print("\nNext step: Manual review of sample to validate precision improvement")
    print("Target precision: >=95% (up from 70-75% pre-reprocessing)")

    conn.close()
    return output_path

if __name__ == "__main__":
    generate_tier2_sample()
