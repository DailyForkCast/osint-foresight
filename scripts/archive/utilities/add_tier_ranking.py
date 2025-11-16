#!/usr/bin/env python3
"""
Add Confidence Tier Ranking to Fresh Sample CSV
Adds a tier column based on confidence scores:
- HIGH: confidence >= 0.9
- MEDIUM: 0.6 <= confidence < 0.9
- LOW: 0.3 <= confidence < 0.6
"""

import csv
import sys
from pathlib import Path

def determine_tier(confidence_str):
    """Determine confidence tier from confidence score string"""
    try:
        confidence = float(confidence_str)
        if confidence >= 0.9:
            return "HIGH"
        elif confidence >= 0.6:
            return "MEDIUM"
        elif confidence >= 0.3:
            return "LOW"
        else:
            return "VERY_LOW"
    except (ValueError, TypeError):
        return "UNKNOWN"

def add_tier_ranking(input_file, output_file):
    """Add tier ranking column to the CSV"""

    print(f"Reading: {input_file}")

    # Read the CSV
    rows = []
    with open(input_file, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        # Add Confidence_Tier column after Confidence column
        new_fieldnames = []
        for field in fieldnames:
            new_fieldnames.append(field)
            if field == "Confidence":
                new_fieldnames.append("Confidence_Tier")

        # Process rows
        for row in reader:
            confidence_tier = determine_tier(row.get('Confidence', ''))
            row['Confidence_Tier'] = confidence_tier
            rows.append(row)

    print(f"Processed {len(rows)} records")

    # Count by tier
    tier_counts = {}
    for row in rows:
        tier = row.get('Confidence_Tier', 'UNKNOWN')
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    print("\nTier Distribution:")
    for tier in ['HIGH', 'MEDIUM', 'LOW', 'VERY_LOW', 'UNKNOWN']:
        count = tier_counts.get(tier, 0)
        if count > 0:
            print(f"  {tier}: {count} records")

    # Write the updated CSV
    print(f"\nWriting: {output_file}")
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[SUCCESS] Added Confidence_Tier column to {len(rows)} records")
    return True

if __name__ == "__main__":
    input_file = Path("data/processed/usaspending_manual_review/fresh_sample_20251016_200923.csv")
    output_file = input_file  # Overwrite the original file

    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)

    success = add_tier_ranking(input_file, output_file)

    if success:
        print("\n[COMPLETE] Tier ranking column added successfully")
        sys.exit(0)
    else:
        print("\nERROR: Failed to add tier ranking")
        sys.exit(1)
