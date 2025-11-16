#!/usr/bin/env python3
"""
Generate Sample with Importance Tier Categorization
Applies TIER_1/TIER_2/TIER_3 categorization logic to show strategic intelligence value
"""

import sqlite3
import csv
import json
from pathlib import Path
from datetime import datetime

# Database configuration
DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("data/processed/usaspending_manual_review")

def categorize_importance(recipient_name, vendor_name, award_description):
    """
    Categorize record by strategic intelligence value.

    Logic:
    - TIER_1: Strategic entities + strategic tech/sensitive context
    - TIER_2: Strategic entities + commodity purchases, OR general tech from any vendor
    - TIER_3: Generic commodity purchases

    Returns:
        tuple: (tier, importance_score, commodity_type)
    """
    desc = (award_description or '').upper()
    recipient = (recipient_name or '').upper()
    vendor = (vendor_name or '').upper()

    # Exclude false positives FIRST (before TIER_1 checks)
    false_positive_patterns = [
        'SPACE HEATER', 'HEATER,SPACE', 'HEATER, SPACE',
        'AZTEC', 'A-AZTEC'  # US companies, not Chinese
    ]

    has_false_positive = any(fp in desc or fp in recipient or fp in vendor
                             for fp in false_positive_patterns)

    # Check if this is a strategic entity
    strategic_entities = [
        'CHINESE ACADEMY', 'HUAWEI', ' ZTE ', 'LENOVO',
        'TSINGHUA', 'PEKING UNIVERSITY', 'CAS ',
        'AVIC', 'COMAC', ' DJI ', 'HIKVISION', 'DAHUA',
        'NORINCO', 'CSSC', 'STATE-OWNED'
    ]

    is_strategic_entity = False
    if not has_false_positive:
        for entity in strategic_entities:
            if entity in recipient or entity in vendor:
                is_strategic_entity = True
                break

    # Check for strategic technologies
    strategic_tech = [
        'QUANTUM', 'ARTIFICIAL INTELLIGENCE', 'SEMICONDUCTOR', 'MACHINE LEARNING',
        'BIOTECHNOLOGY', 'SATELLITE', 'HYPERSONIC', 'NUCLEAR',
        'ADVANCED MATERIAL', 'SPACE SYSTEM', 'SPACE TECHNOLOGY', 'SPACECRAFT',
        ' CHIP ', 'MICROCHIP', 'PHARMACEUTICAL', 'CLASSIFIED', 'SECRET',
        'SERVER', 'NETWORK EQUIPMENT', 'SURVEILLANCE', 'FACIAL RECOGNITION',
        'TELECOMMUNICATIONS EQUIPMENT', 'ROUTER', 'SWITCH', 'FIREWALL'
    ]

    has_strategic_tech = any(tech in desc for tech in strategic_tech)

    # Check for commodity computer equipment (laptops, desktops, monitors, keyboards)
    commodity_computers = [
        'LAPTOP', 'NOTEBOOK', 'THINKPAD', 'DESKTOP', 'MONITOR', 'DISPLAY',
        'KEYBOARD', 'MOUSE', 'TABLET', 'IPAD', 'CHROMEBOOK'
    ]

    is_commodity_computer = any(item in desc for item in commodity_computers)

    # TIER 3: Generic Commodity Purchases (from any vendor)
    commodity_patterns = {
        'office_supplies': ['CARTRIDGE', 'TONER', 'INK', 'PAPER', 'ENVELOPE', 'FOLDER',
                           'PEN', 'PENCIL', 'MARKER', 'STAPLER', 'CLIP', 'BINDER', 'LABEL MAKER'],

        'commodity_electronics': ['SURGE PROTECTOR', 'POWER STRIP', 'CABLE', 'USB',
                                 'PHONE CHARGER', 'BATTERY', 'LIGHT BULB', 'LED', 'ADAPTER'],

        'hardware': ['SCREW', 'BOLT', 'NUT', 'WASHER', 'WEDGE', 'HOOK', 'HINGE',
                    'LOCK', 'HAND TOOL'],

        'apparel': ['APRON', 'GLOVE', 'BOOT', 'VEST', 'UNIFORM', 'PROTECTIVE EQUIPMENT'],

        'kitchen': ['FUNNEL', 'WHISK', 'PLATE', 'CUP', 'MOP', 'BROOM', 'UTENSIL',
                   'KITCHEN', 'CLEANING', 'TRASH BAG', 'PAPER TOWEL'],

        'auto_parts': ['RELAY', 'PIPE', 'ELBOW', 'FILTER', 'FLUID', 'MAINTENANCE']
    }

    for commodity_type, keywords in commodity_patterns.items():
        if any(kw in desc for kw in keywords):
            return ('TIER_3', 0.1, commodity_type)

    # TIER 1: Strategic entity + strategic technology/context
    if is_strategic_entity and has_strategic_tech:
        return ('TIER_1', 1.0, 'strategic_entity_with_strategic_tech')

    # TIER 2: Strategic entity + commodity computer equipment
    # (Lenovo laptop = Chinese company but routine purchase)
    if is_strategic_entity and is_commodity_computer:
        return ('TIER_2', 0.6, 'strategic_entity_commodity_computer')

    # TIER 1: Strategic entity alone (without commodity context)
    # (e.g., Chinese Academy research partnership, Huawei contract without commodity keywords)
    if is_strategic_entity:
        return ('TIER_1', 1.0, 'strategic_entity')

    # TIER 1: Strategic technology alone (any vendor)
    if has_strategic_tech:
        return ('TIER_1', 1.0, 'strategic_technology')

    # TIER 2: Default (general technology/equipment from any vendor)
    return ('TIER_2', 0.5, 'general_technology')

def determine_confidence_tier(confidence):
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

def generate_importance_tier_sample():
    """Generate sample with both confidence and importance tiers"""

    print("=" * 80)
    print("GENERATING SAMPLE WITH IMPORTANCE TIER CATEGORIZATION")
    print("=" * 80)

    # Connect to database
    print(f"\n[1/6] Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Output file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = OUTPUT_DIR / f"importance_tier_sample_{timestamp}.csv"
    output_json = OUTPUT_DIR / f"importance_tier_sample_{timestamp}.json"

    print(f"[2/6] Querying database for stratified sample...")
    print("  Strategy: Sample across confidence levels to get diverse records")

    # Sample distribution: 200 HIGH, 50 MEDIUM, 50 LOW confidence
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
            award_description,
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
            award_description,
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
            award_description,
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

    print(f"\n[3/6] Total records sampled: {len(samples)}")

    # Apply importance tier categorization
    print("[4/6] Applying importance tier categorization logic...")
    categorized_samples = []

    confidence_tier_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "VERY_LOW": 0, "UNKNOWN": 0}
    importance_tier_counts = {"TIER_1": 0, "TIER_2": 0, "TIER_3": 0}

    for record in samples:
        (transaction_id, recipient_name, vendor_name, country_code,
         country_name, award_description, award_amount, confidence, detection_types) = record

        # Determine confidence tier
        conf_tier = determine_confidence_tier(confidence)
        confidence_tier_counts[conf_tier] += 1

        # Determine importance tier
        imp_tier, imp_score, commodity_type = categorize_importance(
            recipient_name, vendor_name, award_description
        )
        importance_tier_counts[imp_tier] += 1

        categorized_samples.append({
            "Transaction_ID": transaction_id or "",
            "Recipient_Name": recipient_name or "",
            "Vendor_Name": vendor_name or "",
            "Country_Code": country_code or "",
            "Country_Name": country_name or "",
            "Award_Description": award_description or "",
            "Award_Amount": award_amount or "",
            "Confidence": confidence or "",
            "Confidence_Tier": conf_tier,
            "Importance_Tier": imp_tier,
            "Importance_Score": imp_score,
            "Commodity_Type": commodity_type,
            "Detection_Types": detection_types or "",
            "Review_Notes": ""
        })

    # Write CSV
    print(f"[5/6] Writing outputs...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "Transaction_ID", "Recipient_Name", "Vendor_Name",
        "Country_Code", "Country_Name", "Award_Description",
        "Award_Amount", "Confidence", "Confidence_Tier",
        "Importance_Tier", "Importance_Score", "Commodity_Type",
        "Detection_Types", "Review_Notes"
    ]

    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(categorized_samples)

    # Write JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(categorized_samples, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"[6/6] Analysis complete")
    print("\n" + "=" * 80)
    print("SAMPLE GENERATION COMPLETE")
    print("=" * 80)
    print(f"\nCSV Output: {output_csv}")
    print(f"JSON Output: {output_json}")
    print(f"\nTotal Records: {len(categorized_samples)}")

    print("\n--- CONFIDENCE TIER DISTRIBUTION ---")
    for tier in ["HIGH", "MEDIUM", "LOW", "VERY_LOW", "UNKNOWN"]:
        count = confidence_tier_counts[tier]
        if count > 0:
            pct = (count / len(categorized_samples)) * 100
            print(f"  {tier:12s}: {count:3d} records ({pct:5.1f}%)")

    print("\n--- IMPORTANCE TIER DISTRIBUTION ---")
    for tier in ["TIER_1", "TIER_2", "TIER_3"]:
        count = importance_tier_counts[tier]
        pct = (count / len(categorized_samples)) * 100
        tier_desc = {
            "TIER_1": "Strategic (high intelligence value)",
            "TIER_2": "Technology/Equipment (medium value)",
            "TIER_3": "Commodity Purchases (low value)"
        }[tier]
        print(f"  {tier}: {count:3d} records ({pct:5.1f}%) - {tier_desc}")

    # Show sample records by tier
    print("\n--- SAMPLE RECORDS BY IMPORTANCE TIER ---")

    for tier in ["TIER_1", "TIER_2", "TIER_3"]:
        tier_records = [r for r in categorized_samples if r["Importance_Tier"] == tier]
        if tier_records:
            print(f"\n{tier} Examples:")
            for i, record in enumerate(tier_records[:3], 1):
                desc = record["Award_Description"][:80] + "..." if len(record["Award_Description"]) > 80 else record["Award_Description"]
                print(f"  {i}. {desc}")
                print(f"     Vendor: {record['Vendor_Name']}")
                print(f"     Commodity Type: {record['Commodity_Type']}")

    print("\n" + "=" * 80)
    print("[SUCCESS] Sample with importance tier categorization ready for review")
    print("=" * 80)
    print("\nKey Insights:")
    print("  - TIER_1: Focus on these for strategic intelligence analysis")
    print("  - TIER_2: Secondary analysis, dual-use monitoring")
    print("  - TIER_3: Archive only, minimal intelligence value")

    return output_csv, output_json, importance_tier_counts

if __name__ == "__main__":
    try:
        csv_file, json_file, tier_counts = generate_importance_tier_sample()
        print(f"\nNext Steps:")
        print(f"1. Open: {csv_file}")
        print(f"2. Review TIER_1 records for strategic intelligence")
        print(f"3. Validate categorization accuracy")
        print(f"4. Consider full re-processing if categorization looks accurate")
    except Exception as e:
        print(f"\n[ERROR] Failed to generate sample: {e}")
        import traceback
        traceback.print_exc()
