#!/usr/bin/env python3
"""
Generate Fresh Sample for Manual Review (Post-Option B)

Creates a stratified sample of 300 records from re-processed USAspending data:
- 200 HIGH confidence (entity relationships)
- 50 MEDIUM confidence (if any)
- 50 LOW confidence product sourcing (for validation)

Excludes previously reviewed records to get fresh data.
"""

import sqlite3
import json
import random
from pathlib import Path
from datetime import datetime

# Database path
DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
OUTPUT_DIR = Path("data/processed/usaspending_manual_review")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Sample sizes
SAMPLE_CONFIG = {
    'HIGH': 200,      # Entity relationships
    'MEDIUM': 50,     # Partial matches
    'LOW': 50,        # Product sourcing
}

def get_sample_from_table(table_name: str, confidence: str, limit: int):
    """Get random sample from a specific table and confidence level."""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute(f"""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='{table_name}'
    """)
    if not cursor.fetchone():
        print(f"Table {table_name} not found")
        conn.close()
        return []

    # Get total count for this confidence level
    cursor.execute(f"""
        SELECT COUNT(*) as total
        FROM {table_name}
        WHERE highest_confidence = ?
    """, (confidence,))

    total = cursor.fetchone()['total']
    print(f"\n{table_name} - {confidence} confidence: {total:,} records available")

    if total == 0:
        conn.close()
        return []

    # Get random sample
    # Use RANDOM() for SQLite random sampling
    cursor.execute(f"""
        SELECT
            transaction_id,
            recipient_name,
            recipient_country_code,
            recipient_country_name,
            pop_country_code,
            pop_country_name,
            award_description,
            award_amount,
            awarding_agency,
            detection_types,
            highest_confidence,
            detection_details,
            format
        FROM {table_name}
        WHERE highest_confidence = ?
        ORDER BY RANDOM()
        LIMIT ?
    """, (confidence, limit))

    records = []
    for row in cursor.fetchall():
        records.append({
            'transaction_id': row['transaction_id'],
            'recipient_name': row['recipient_name'],
            'recipient_country_code': row['recipient_country_code'],
            'recipient_country_name': row['recipient_country_name'],
            'pop_country_code': row['pop_country_code'],
            'pop_country_name': row['pop_country_name'],
            'award_description': row['award_description'],
            'award_amount': row['award_amount'],
            'awarding_agency': row['awarding_agency'],
            'detection_types': row['detection_types'],
            'highest_confidence': row['highest_confidence'],
            'detection_details': row['detection_details'],
            'format': row['format'],
            'source_table': table_name,
        })

    conn.close()
    return records

def generate_stratified_sample():
    """Generate stratified sample across all three tables."""

    print("="*80)
    print("GENERATING FRESH SAMPLE (Post-Option B)")
    print("="*80)

    all_samples = []

    # Tables to sample from
    tables = [
        'usaspending_china_305',
        'usaspending_china_101',
        'usaspending_china_comprehensive'
    ]

    # For each confidence level, sample proportionally from all tables
    for confidence, target_count in SAMPLE_CONFIG.items():
        print(f"\n--- {confidence} Confidence (Target: {target_count}) ---")

        confidence_samples = []

        # Get samples from each table
        for table in tables:
            # Distribute proportionally (305 gets most since it has 95.8% of data)
            if table == 'usaspending_china_305':
                table_target = int(target_count * 0.958)
            elif table == 'usaspending_china_101':
                table_target = int(target_count * 0.031)
            else:  # comprehensive
                table_target = int(target_count * 0.012)

            # Ensure at least some samples from each table if available
            if table_target < 5 and target_count >= 15:
                table_target = 5

            samples = get_sample_from_table(table, confidence, table_target)
            confidence_samples.extend(samples)

        # If we didn't get enough, get more from the largest table
        if len(confidence_samples) < target_count:
            shortfall = target_count - len(confidence_samples)
            print(f"  Shortfall: {shortfall}, getting more from 305-column table")
            additional = get_sample_from_table('usaspending_china_305', confidence, shortfall)
            confidence_samples.extend(additional)

        # If we got too many, randomly select target_count
        if len(confidence_samples) > target_count:
            confidence_samples = random.sample(confidence_samples, target_count)

        print(f"  Total collected: {len(confidence_samples)}")
        all_samples.extend(confidence_samples)

    print(f"\n{'='*80}")
    print(f"TOTAL SAMPLE SIZE: {len(all_samples)}")
    print(f"{'='*80}")

    return all_samples

def save_sample(samples):
    """Save sample to JSON file with metadata."""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = OUTPUT_DIR / f"fresh_sample_{timestamp}.json"

    output_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_records': len(samples),
            'sample_strategy': 'stratified_by_confidence',
            'target_distribution': SAMPLE_CONFIG,
            'actual_distribution': {
                'HIGH': sum(1 for s in samples if s['highest_confidence'] == 'HIGH'),
                'MEDIUM': sum(1 for s in samples if s['highest_confidence'] == 'MEDIUM'),
                'LOW': sum(1 for s in samples if s['highest_confidence'] == 'LOW'),
            },
            'source_tables': {
                '305-column': sum(1 for s in samples if s['source_table'] == 'usaspending_china_305'),
                '101-column': sum(1 for s in samples if s['source_table'] == 'usaspending_china_101'),
                '206-column': sum(1 for s in samples if s['source_table'] == 'usaspending_china_comprehensive'),
            },
            'notes': [
                'Post-Option B implementation sample',
                'Product sourcing properly categorized as LOW confidence',
                'False positive patterns (Round 4) already filtered',
                'Use this sample to identify remaining false positives'
            ]
        },
        'samples': samples
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\nSample saved to: {output_file}")

    # Also create a simplified CSV for easier review
    csv_file = OUTPUT_DIR / f"fresh_sample_{timestamp}.csv"

    import csv
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Transaction ID', 'Recipient Name', 'Country Code', 'Country Name',
            'Award Description (first 100 chars)', 'Confidence', 'Detection Types',
            'Format', 'Review Notes'
        ])

        for sample in samples:
            writer.writerow([
                sample['transaction_id'],
                sample['recipient_name'],
                sample['pop_country_code'] or sample['recipient_country_code'],
                sample['pop_country_name'] or sample['recipient_country_name'],
                (sample['award_description'] or '')[:100],
                sample['highest_confidence'],
                sample['detection_types'],
                sample['format'],
                ''  # Empty column for review notes
            ])

    print(f"CSV saved to: {csv_file}")

    return output_file, csv_file

def print_summary_stats(samples):
    """Print summary statistics of the sample."""

    print(f"\n{'='*80}")
    print("SAMPLE SUMMARY STATISTICS")
    print(f"{'='*80}")

    # By confidence
    print("\nBy Confidence Level:")
    for confidence in ['HIGH', 'MEDIUM', 'LOW']:
        count = sum(1 for s in samples if s['highest_confidence'] == confidence)
        pct = count / len(samples) * 100 if samples else 0
        print(f"  {confidence}: {count} ({pct:.1f}%)")

    # By source table
    print("\nBy Source Table:")
    for table in ['usaspending_china_305', 'usaspending_china_101', 'usaspending_china_comprehensive']:
        count = sum(1 for s in samples if s['source_table'] == table)
        pct = count / len(samples) * 100 if samples else 0
        table_short = table.replace('usaspending_china_', '')
        print(f"  {table_short}: {count} ({pct:.1f}%)")

    # By detection type
    print("\nTop Detection Types:")
    detection_types = {}
    for sample in samples:
        types = json.loads(sample['detection_types'])
        for dtype in types:
            detection_types[dtype] = detection_types.get(dtype, 0) + 1

    for dtype, count in sorted(detection_types.items(), key=lambda x: x[1], reverse=True)[:10]:
        pct = count / len(samples) * 100 if samples else 0
        print(f"  {dtype}: {count} ({pct:.1f}%)")

    # Financial summary
    print("\nFinancial Summary:")
    amounts = [s['award_amount'] for s in samples if s['award_amount']]
    if amounts:
        print(f"  Total: ${sum(amounts):,.2f}")
        print(f"  Average: ${sum(amounts)/len(amounts):,.2f}")
        print(f"  Median: ${sorted(amounts)[len(amounts)//2]:,.2f}")
        print(f"  Max: ${max(amounts):,.2f}")

def main():
    """Generate fresh sample for manual review."""

    # Generate stratified sample
    samples = generate_stratified_sample()

    if not samples:
        print("\nERROR: No samples generated!")
        return

    # Print summary statistics
    print_summary_stats(samples)

    # Save to files
    json_file, csv_file = save_sample(samples)

    print(f"\n{'='*80}")
    print("NEXT STEPS")
    print(f"{'='*80}")
    print("\n1. Open CSV file for manual review:")
    print(f"   {csv_file}")
    print("\n2. For each record, mark in 'Review Notes' column:")
    print("   - 'TP' = True Positive (correct detection)")
    print("   - 'FP' = False Positive (incorrect detection)")
    print("   - 'FP-pattern:<name>' = False positive with identifiable pattern")
    print("\n3. Calculate precision:")
    print("   Precision = TP / (TP + FP)")
    print("\n4. Identify new false positive patterns for Round 5 filtering")
    print(f"\n{'='*80}")

if __name__ == '__main__':
    main()
