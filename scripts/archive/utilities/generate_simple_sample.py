#!/usr/bin/env python3
"""
Generate Simple Sample for Manual Review (Post-Option B)

Samples 300 records from 305-column table (95.8% of all data):
- 200 HIGH confidence (0.9+) - for precision testing
- 50 MEDIUM confidence (0.6-0.89) - if available
- 50 LOW confidence (0.3) - product sourcing validation
"""

import sqlite3
import json
import csv
from pathlib import Path
from datetime import datetime

# Configuration
DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
OUTPUT_DIR = Path("data/processed/usaspending_manual_review")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_samples():
    """Get stratified sample from 305-column table."""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("="*80)
    print("GENERATING FRESH SAMPLE (Post-Option B)")
    print("="*80)
    print("\nSampling from: usaspending_china_305")
    print("Table size: 159,513 records")
    print()

    samples = []

    # 1. HIGH confidence (0.9+) - 200 samples
    print("1. HIGH confidence (>=0.9): Target 200")
    cursor.execute("""
        SELECT
            transaction_id,
            recipient_name,
            pop_country_code,
            pop_country_name,
            award_description,
            award_amount,
            vendor_name,
            detection_types,
            highest_confidence,
            detection_details
        FROM usaspending_china_305
        WHERE CAST(highest_confidence AS REAL) >= 0.9
        ORDER BY RANDOM()
        LIMIT 200
    """)

    high_samples = cursor.fetchall()
    print(f"   Collected: {len(high_samples)}")
    samples.extend(high_samples)

    # 2. MEDIUM confidence (0.6-0.89) - 50 samples
    print("2. MEDIUM confidence (0.6-0.89): Target 50")
    cursor.execute("""
        SELECT
            transaction_id,
            recipient_name,
            pop_country_code,
            pop_country_name,
            award_description,
            award_amount,
            vendor_name,
            detection_types,
            highest_confidence,
            detection_details
        FROM usaspending_china_305
        WHERE CAST(highest_confidence AS REAL) >= 0.6
          AND CAST(highest_confidence AS REAL) < 0.9
        ORDER BY RANDOM()
        LIMIT 50
    """)

    medium_samples = cursor.fetchall()
    print(f"   Collected: {len(medium_samples)}")
    samples.extend(medium_samples)

    # 3. LOW confidence (0.3) - 50 samples (product sourcing)
    print("3. LOW confidence (0.3): Target 50")
    cursor.execute("""
        SELECT
            transaction_id,
            recipient_name,
            pop_country_code,
            pop_country_name,
            award_description,
            award_amount,
            vendor_name,
            detection_types,
            highest_confidence,
            detection_details
        FROM usaspending_china_305
        WHERE CAST(highest_confidence AS REAL) = 0.3
        ORDER BY RANDOM()
        LIMIT 50
    """)

    low_samples = cursor.fetchall()
    print(f"   Collected: {len(low_samples)}")
    samples.extend(low_samples)

    conn.close()

    print(f"\nTOTAL SAMPLE SIZE: {len(samples)}")
    print("="*80)

    return samples

def save_samples(samples):
    """Save samples to CSV for manual review."""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = OUTPUT_DIR / f"fresh_sample_{timestamp}.csv"

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Transaction ID',
            'Recipient Name',
            'Vendor Name',
            'Country Code',
            'Country Name',
            'Award Description (first 150 chars)',
            'Award Amount',
            'Confidence',
            'Detection Types',
            'Review Notes (TP/FP/FP-pattern:<name>)'
        ])

        for sample in samples:
            writer.writerow([
                sample['transaction_id'],
                sample['recipient_name'],
                sample['vendor_name'] or '',
                sample['pop_country_code'],
                sample['pop_country_name'],
                (sample['award_description'] or '')[:150],
                f"${sample['award_amount']:,.2f}" if sample['award_amount'] else '',
                sample['highest_confidence'],
                sample['detection_types'],
                ''  # Empty for manual review notes
            ])

    print(f"\n[SUCCESS] CSV saved to: {csv_file}")

    # Also save detailed JSON
    json_file = OUTPUT_DIR / f"fresh_sample_{timestamp}.json"

    json_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_records': len(samples),
            'source_table': 'usaspending_china_305',
            'distribution': {
                'HIGH (>=0.9)': sum(1 for s in samples if float(s['highest_confidence']) >= 0.9),
                'MEDIUM (0.6-0.89)': sum(1 for s in samples if 0.6 <= float(s['highest_confidence']) < 0.9),
                'LOW (0.3)': sum(1 for s in samples if float(s['highest_confidence']) == 0.3),
            },
            'post_option_b': True,
            'notes': [
                'Product sourcing properly categorized as LOW (0.3)',
                'False positive Round 4 patterns already filtered',
                'Use for identifying remaining false positives'
            ]
        },
        'samples': [dict(s) for s in samples]
    }

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] JSON saved to: {json_file}")

    return csv_file, json_file

def print_instructions(csv_file):
    """Print manual review instructions."""

    print(f"\n{'='*80}")
    print("MANUAL REVIEW INSTRUCTIONS")
    print(f"{'='*80}")
    print(f"\n1. Open CSV file: {csv_file}")
    print("\n2. For each record, mark in 'Review Notes' column:")
    print("   - 'TP' = True Positive (correct detection)")
    print("   - 'FP' = False Positive (incorrect detection)")
    print("   - 'FP-pattern:<name>' = False positive with pattern")
    print("       Example: 'FP-pattern:US company name substring'")
    print("\n3. Calculate precision after review:")
    print("   Precision = TP / (TP + FP)")
    print("\n4. Identify patterns in false positives for Round 5 filtering")
    print("\n5. Goal: Achieve >=95% precision")
    print(f"\n{'='*80}\n")

def main():
    """Generate sample and save to CSV."""

    # Generate samples
    samples = get_samples()

    if not samples:
        print("\nERROR: No samples generated!")
        return

    # Save to files
    csv_file, json_file = save_samples(samples)

    # Print instructions
    print_instructions(csv_file)

if __name__ == '__main__':
    main()
