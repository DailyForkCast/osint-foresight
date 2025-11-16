#!/usr/bin/env python3
"""
Generate New 300-Record Sample with Tier Categories
Generates a fresh sample from the database with Confidence_Tier included
"""

import sqlite3
import csv
import json
from pathlib import Path
from datetime import datetime

# Database configuration
DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("data/processed/usaspending_manual_review")

def determine_tier(confidence):
    """Determine confidence tier from confidence score"""
    try:
        conf = float(confidence)
        if conf >= 0.9:
            return "HIGH"
        elif conf >= 0.6:
            return "MEDIUM"
        elif conf >= 0.3:
            return "LOW"
        else:
            return "VERY_LOW"
    except (ValueError, TypeError):
        return "UNKNOWN"

def generate_tiered_sample():
    """Generate new sample with tier categories"""

    print("=" * 70)
    print("GENERATING NEW 300-RECORD SAMPLE WITH TIER CATEGORIES")
    print("=" * 70)

    # Connect to database
    print(f"\n[1/5] Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Output file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = OUTPUT_DIR / f"tiered_sample_{timestamp}.csv"
    output_json = OUTPUT_DIR / f"tiered_sample_{timestamp}.json"

    print(f"[2/5] Querying database for stratified sample...")

    # Sample distribution: 200 HIGH, 50 MEDIUM, 50 LOW
    samples = []

    # HIGH confidence (>= 0.9) - 200 records
    print("  - Sampling 200 HIGH confidence records (>= 0.9)...")
    cursor.execute("""
        SELECT
            transaction_id,
            recipient_name,
            vendor_name,
            pop_country_code,
            pop_country_name,
            SUBSTR(award_description, 1, 150),
            award_amount,
            highest_confidence,
            detection_types
        FROM usaspending_china_305
        WHERE CAST(highest_confidence AS REAL) >= 0.9
        ORDER BY RANDOM()
        LIMIT 200
    """)
    high_records = cursor.fetchall()
    print(f"    Found: {len(high_records)} HIGH confidence records")
    samples.extend(high_records)

    # MEDIUM confidence (0.6 - 0.89) - 50 records
    print("  - Sampling 50 MEDIUM confidence records (0.6 - 0.89)...")
    cursor.execute("""
        SELECT
            transaction_id,
            recipient_name,
            vendor_name,
            pop_country_code,
            pop_country_name,
            SUBSTR(award_description, 1, 150),
            award_amount,
            highest_confidence,
            detection_types
        FROM usaspending_china_305
        WHERE CAST(highest_confidence AS REAL) >= 0.6
          AND CAST(highest_confidence AS REAL) < 0.9
        ORDER BY RANDOM()
        LIMIT 50
    """)
    medium_records = cursor.fetchall()
    print(f"    Found: {len(medium_records)} MEDIUM confidence records")
    samples.extend(medium_records)

    # LOW confidence (0.3 - 0.59) - 50 records
    print("  - Sampling 50 LOW confidence records (0.3 - 0.59)...")
    cursor.execute("""
        SELECT
            transaction_id,
            recipient_name,
            vendor_name,
            pop_country_code,
            pop_country_name,
            SUBSTR(award_description, 1, 150),
            award_amount,
            highest_confidence,
            detection_types
        FROM usaspending_china_305
        WHERE CAST(highest_confidence AS REAL) >= 0.3
          AND CAST(highest_confidence AS REAL) < 0.6
        ORDER BY RANDOM()
        LIMIT 50
    """)
    low_records = cursor.fetchall()
    print(f"    Found: {len(low_records)} LOW confidence records")
    samples.extend(low_records)

    conn.close()

    print(f"\n[3/5] Total records sampled: {len(samples)}")

    # Add tier categories
    print("[4/5] Adding tier categories...")
    tiered_samples = []
    tier_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "VERY_LOW": 0, "UNKNOWN": 0}

    for record in samples:
        (transaction_id, recipient_name, vendor_name, country_code,
         country_name, award_description, award_amount, confidence, detection_types) = record

        tier = determine_tier(confidence)
        tier_counts[tier] += 1

        tiered_samples.append({
            "Transaction_ID": transaction_id or "",
            "Recipient_Name": recipient_name or "",
            "Vendor_Name": vendor_name or "",
            "Country_Code": country_code or "",
            "Country_Name": country_name or "",
            "Award_Description": award_description or "",
            "Award_Amount": award_amount or "",
            "Confidence": confidence or "",
            "Confidence_Tier": tier,
            "Detection_Types": detection_types or "",
            "Review_Notes": ""
        })

    # Write CSV
    print(f"[5/5] Writing outputs...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "Transaction_ID", "Recipient_Name", "Vendor_Name",
        "Country_Code", "Country_Name", "Award_Description",
        "Award_Amount", "Confidence", "Confidence_Tier",
        "Detection_Types", "Review_Notes"
    ]

    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tiered_samples)

    # Write JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(tiered_samples, f, indent=2, ensure_ascii=False)

    # Summary
    print("\n" + "=" * 70)
    print("SAMPLE GENERATION COMPLETE")
    print("=" * 70)
    print(f"\nCSV Output: {output_csv}")
    print(f"JSON Output: {output_json}")
    print(f"\nTotal Records: {len(tiered_samples)}")
    print("\nTier Distribution:")
    for tier in ["HIGH", "MEDIUM", "LOW", "VERY_LOW", "UNKNOWN"]:
        count = tier_counts[tier]
        if count > 0:
            print(f"  {tier:12s}: {count:3d} records")

    print("\n[SUCCESS] New sample with tier categories ready for manual review")
    print("=" * 70)

    return output_csv, output_json

if __name__ == "__main__":
    try:
        csv_file, json_file = generate_tiered_sample()
        print(f"\nNext Steps:")
        print(f"1. Open: {csv_file}")
        print(f"2. Review each record and mark as TP/FP in 'Review_Notes' column")
        print(f"3. Calculate precision: TP / (TP + FP)")
    except Exception as e:
        print(f"\n[ERROR] Failed to generate sample: {e}")
        import traceback
        traceback.print_exc()
