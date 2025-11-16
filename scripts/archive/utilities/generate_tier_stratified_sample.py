#!/usr/bin/env python3
"""
Generate Tier-Stratified Sample for Manual Review

Creates a 300-record sample showing examples from all three importance tiers
BEFORE full re-processing. This allows validation of categorization logic.

Sample distribution:
- 50 TIER 1 (Strategic entities/technologies)
- 100 TIER 2 (Technology/services)
- 150 TIER 3 (Commodity purchases)
"""

import sqlite3
import json
import csv
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add scripts to path
sys.path.insert(0, 'scripts')
from process_usaspending_305_column import USAspending305Processor

# Configuration
DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
OUTPUT_DIR = Path("data/processed/usaspending_manual_review")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def categorize_existing_sample():
    """Apply importance tier logic to existing 300-record sample."""

    print("="*80)
    print("GENERATING TIER-STRATIFIED SAMPLE")
    print("="*80)
    print("\nLoading existing sample and applying importance tier logic...")

    # Load existing sample
    sample_file = Path("data/processed/usaspending_manual_review/fresh_sample_20251016_200923.json")
    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    samples = data['samples']
    print(f"Original sample: {len(samples)} records")

    # Initialize processor to use categorization method
    processor = USAspending305Processor()

    # Categorize all records
    categorized = defaultdict(list)

    for record in samples:
        tier, score, commodity_type = processor._categorize_importance(
            recipient_name=record.get('recipient_name', ''),
            vendor_name=record.get('vendor_name', ''),
            description=record.get('award_description', '')
        )

        record['importance_tier'] = tier
        record['importance_score'] = score
        record['commodity_type'] = commodity_type

        categorized[tier].append(record)

    # Show distribution
    print("\n--- Categorization Results ---")
    for tier in ['TIER_1', 'TIER_2', 'TIER_3', 'UNCATEGORIZED']:
        count = len(categorized[tier])
        pct = count / len(samples) * 100
        print(f"{tier}: {count} records ({pct:.1f}%)")

    return categorized

def create_stratified_sample(categorized):
    """Create stratified sample with examples from all tiers."""

    print("\n--- Creating Stratified Sample ---")
    print("Target distribution:")
    print("  TIER 1 (Strategic): 50 records")
    print("  TIER 2 (Technology): 100 records")
    print("  TIER 3 (Commodity): 150 records")
    print()

    # Get samples from each tier
    tier1_sample = categorized['TIER_1'][:50] if len(categorized['TIER_1']) >= 50 else categorized['TIER_1']
    tier2_sample = categorized['TIER_2'][:100] if len(categorized['TIER_2']) >= 100 else categorized['TIER_2']
    tier3_sample = categorized['TIER_3'][:150] if len(categorized['TIER_3']) >= 150 else categorized['TIER_3']

    # Combine
    stratified_sample = tier1_sample + tier2_sample + tier3_sample

    print(f"Actual sample collected:")
    print(f"  TIER 1: {len(tier1_sample)} records")
    print(f"  TIER 2: {len(tier2_sample)} records")
    print(f"  TIER 3: {len(tier3_sample)} records")
    print(f"  TOTAL: {len(stratified_sample)} records")

    return stratified_sample

def save_sample(stratified_sample):
    """Save stratified sample to CSV and JSON."""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = OUTPUT_DIR / f"tier_stratified_sample_{timestamp}.csv"
    json_file = OUTPUT_DIR / f"tier_stratified_sample_{timestamp}.json"

    # Save CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Importance Tier',
            'Score',
            'Commodity Type',
            'Transaction ID',
            'Recipient Name',
            'Vendor Name',
            'Country Code',
            'Award Description (first 150 chars)',
            'Award Amount',
            'Confidence',
            'Detection Types',
            'Review Notes (correct tier? Y/N, comments)'
        ])

        for record in stratified_sample:
            writer.writerow([
                record['importance_tier'],
                record['importance_score'],
                record['commodity_type'],
                record['transaction_id'],
                record['recipient_name'],
                record.get('vendor_name', ''),
                record.get('pop_country_code', ''),
                (record.get('award_description', '') or '')[:150],
                f"${record['award_amount']:,.2f}" if record.get('award_amount') else '',
                record.get('highest_confidence', ''),
                record.get('detection_types', ''),
                ''  # Empty for review notes
            ])

    print(f"\n[SUCCESS] CSV saved to: {csv_file}")

    # Save JSON with metadata
    tier_counts = defaultdict(int)
    commodity_counts = defaultdict(int)

    for record in stratified_sample:
        tier_counts[record['importance_tier']] += 1
        if record['commodity_type']:
            commodity_counts[record['commodity_type']] += 1

    output_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_records': len(stratified_sample),
            'sample_type': 'tier_stratified',
            'distribution_by_tier': dict(tier_counts),
            'distribution_by_commodity_type': dict(commodity_counts),
            'purpose': 'Pre-reprocessing validation - verify categorization logic',
            'instructions': [
                'Review each tier for accuracy',
                'TIER 1 should be strategic entities/technologies only',
                'TIER 2 should be technology/services',
                'TIER 3 should be commodity purchases (office supplies, hardware, etc.)',
                'Mark any misclassifications in Review Notes column'
            ]
        },
        'samples': stratified_sample
    }

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] JSON saved to: {json_file}")

    return csv_file, json_file

def print_tier_examples(stratified_sample):
    """Print examples from each tier."""

    print("\n" + "="*80)
    print("TIER EXAMPLES FOR REVIEW")
    print("="*80)

    # Group by tier
    by_tier = defaultdict(list)
    for record in stratified_sample:
        by_tier[record['importance_tier']].append(record)

    # Show examples from each tier
    for tier in ['TIER_1', 'TIER_2', 'TIER_3']:
        if tier not in by_tier:
            continue

        print(f"\n--- {tier} Examples (showing first 10) ---")

        if tier == 'TIER_1':
            print("Expected: Strategic entities, Chinese Academy, Huawei, quantum, AI, etc.")
        elif tier == 'TIER_2':
            print("Expected: Computers, machinery, engineering services, etc.")
        else:  # TIER_3
            print("Expected: Commodity purchases - surge protectors, ink cartridges, hardware, etc.")

        print()

        for i, record in enumerate(by_tier[tier][:10]):
            recipient = record['recipient_name'][:45]
            desc = (record.get('award_description', '') or '')[:80]
            commodity_type = record['commodity_type']

            print(f"{i+1}. [{commodity_type}]")
            print(f"   {recipient}")
            print(f"   {desc}...")
            print()

    # Show commodity type distribution for TIER 3
    print("\n--- TIER 3 Commodity Type Distribution ---")
    tier3_commodities = defaultdict(int)
    for record in by_tier['TIER_3']:
        tier3_commodities[record['commodity_type']] += 1

    for commodity_type in sorted(tier3_commodities.keys()):
        count = tier3_commodities[commodity_type]
        print(f"  {commodity_type}: {count}")

def print_instructions(csv_file):
    """Print manual review instructions."""

    print("\n" + "="*80)
    print("MANUAL REVIEW INSTRUCTIONS")
    print("="*80)
    print(f"\n1. Open CSV file: {csv_file}")
    print("\n2. For each record, verify the tier assignment is correct:")
    print("   - TIER 1: Strategic entities (Chinese Academy, Huawei) or technologies (quantum, AI)")
    print("   - TIER 2: General technology (computers, machinery) or services (engineering, consulting)")
    print("   - TIER 3: Commodity purchases (surge protectors, ink, screws, aprons, etc.)")
    print("\n3. In 'Review Notes' column, mark:")
    print("   - 'Y' if tier is correct")
    print("   - 'N - should be TIER_X' if misclassified")
    print("   - Add comments for any patterns we missed")
    print("\n4. Look for patterns we should add:")
    print("   - New commodity types not yet categorized")
    print("   - Strategic entities we missed")
    print("   - Technology keywords we should add")
    print("\n5. Goal: Verify categorization logic before 17-hour re-processing")
    print("="*80)

def main():
    """Generate tier-stratified sample."""

    # Categorize existing sample
    categorized = categorize_existing_sample()

    # Create stratified sample
    stratified_sample = create_stratified_sample(categorized)

    # Save to files
    csv_file, json_file = save_sample(stratified_sample)

    # Print examples
    print_tier_examples(stratified_sample)

    # Print instructions
    print_instructions(csv_file)

    print("\n[SUCCESS] Tier-stratified sample ready for review!")

if __name__ == '__main__':
    main()
