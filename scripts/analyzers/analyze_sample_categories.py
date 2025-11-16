#!/usr/bin/env python3
"""
Analyze Fresh Sample by Product Category

Categorizes the 300-record sample by commercial activity type to identify
commodity purchases that should be demoted in importance vs strategic entities.
"""

import json
import csv
from collections import defaultdict, Counter
from pathlib import Path

# Load sample
SAMPLE_FILE = Path("data/processed/usaspending_manual_review/fresh_sample_20251016_200923.json")
OUTPUT_DIR = Path("analysis")

def categorize_record(record):
    """Categorize a record by commercial activity type."""

    desc = (record.get('award_description') or '').upper()
    recipient = (record.get('recipient_name') or '').upper()
    vendor = (record.get('vendor_name') or '').upper()

    # TIER 1: Strategic Entities (HIGH IMPORTANCE)
    strategic_entities = [
        'CHINESE ACADEMY', 'HUAWEI', 'ZTE', 'LENOVO', 'XIAOMI',
        'TENCENT', 'ALIBABA', 'BAIDU', 'DJI', 'HIKVISION',
        'DAHUA', 'HYTERA', 'AVIC', 'COMAC', 'CSSC',
        'CHINESE UNIVERSITY', 'TSINGHUA', 'PEKING UNIVERSITY',
        'CAS ', 'RESEARCH CENTER', 'RESEARCH INSTITUTE'
    ]

    for entity in strategic_entities:
        if entity in recipient or entity in vendor:
            return 'TIER_1_STRATEGIC_ENTITY'

    # TIER 2: Technology/Services (MEDIUM IMPORTANCE)
    tech_keywords = [
        'SOFTWARE', 'COMPUTER', 'SERVER', 'NETWORK', 'DATABASE',
        'TELECOMMUNICATIONS', 'SATELLITE', 'SEMICONDUCTOR', 'CHIP',
        'PROCESSOR', 'CIRCUIT', 'SENSOR', 'DRONE', 'ROBOT',
        'ARTIFICIAL INTELLIGENCE', 'MACHINE LEARNING', 'QUANTUM',
        'BIOTECHNOLOGY', 'PHARMACEUTICAL'
    ]

    for keyword in tech_keywords:
        if keyword in desc:
            return 'TIER_2_TECHNOLOGY'

    # TIER 3: Commodity Office Supplies (LOW IMPORTANCE)
    office_supplies = [
        'CARTRIDGE', 'TONER', 'INK', 'PAPER', 'STAPLE', 'FOLDER',
        'PEN', 'PENCIL', 'MARKER', 'ENVELOPE', 'CLIP', 'BINDER',
        'NOTEPAD', 'POST-IT'
    ]

    for keyword in office_supplies:
        if keyword in desc:
            return 'TIER_3_OFFICE_SUPPLIES'

    # TIER 3: Commodity Electronics (LOW IMPORTANCE)
    commodity_electronics = [
        'SURGE PROTECTOR', 'POWER STRIP', 'EXTENSION CORD', 'CABLE',
        'ADAPTER', 'USB', 'CHARGER', 'BATTERY', 'FLASHLIGHT',
        'LIGHT BULB', 'LED'
    ]

    for keyword in commodity_electronics:
        if keyword in desc:
            return 'TIER_3_COMMODITY_ELECTRONICS'

    # TIER 3: Hardware/Tools (LOW IMPORTANCE)
    hardware = [
        'SCREW', 'BOLT', 'NUT', 'WASHER', 'WEDGE', 'HOOK', 'HINGE',
        'LOCK', 'KEY', 'NAIL', 'HAMMER', 'WRENCH', 'PLIERS',
        'SCREWDRIVER', 'DRILL BIT'
    ]

    for keyword in hardware:
        if keyword in desc:
            return 'TIER_3_HARDWARE'

    # TIER 3: Apparel/PPE (LOW IMPORTANCE)
    apparel = [
        'APRON', 'GLOVE', 'SHOE', 'BOOT', 'HAT', 'UNIFORM',
        'VEST', 'JACKET', 'PANTS', 'SHIRT', 'SOCKS'
    ]

    for keyword in apparel:
        if keyword in desc:
            return 'TIER_3_APPAREL'

    # TIER 3: Kitchen/Janitorial (LOW IMPORTANCE)
    kitchen_janitorial = [
        'FUNNEL', 'WHISK', 'SPATULA', 'LADLE', 'SPOON', 'FORK',
        'KNIFE', 'PLATE', 'CUP', 'MOP', 'BROOM', 'BUCKET',
        'CLEANER', 'DETERGENT', 'SOAP'
    ]

    for keyword in kitchen_janitorial:
        if keyword in desc:
            return 'TIER_3_KITCHEN_JANITORIAL'

    # TIER 2: General Equipment/Machinery (MEDIUM IMPORTANCE)
    equipment = [
        'EQUIPMENT', 'MACHINERY', 'ENGINE', 'MOTOR', 'PUMP',
        'VALVE', 'COMPRESSOR', 'GENERATOR', 'TURBINE',
        'VEHICLE', 'AIRCRAFT', 'SHIP', 'VESSEL'
    ]

    for keyword in equipment:
        if keyword in desc:
            return 'TIER_2_EQUIPMENT'

    # Default: Uncategorized (review needed)
    return 'UNCATEGORIZED'

def analyze_sample():
    """Analyze sample by category."""

    with open(SAMPLE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    samples = data['samples']

    # Categorize all records
    categories = defaultdict(list)

    for record in samples:
        category = categorize_record(record)
        categories[category].append(record)

    # Analysis
    print("="*80)
    print("SAMPLE CATEGORIZATION ANALYSIS")
    print("="*80)
    print(f"\nTotal Records: {len(samples)}")
    print(f"Categories Found: {len(categories)}")

    # Count by tier
    tier1_count = sum(len(records) for cat, records in categories.items() if cat.startswith('TIER_1'))
    tier2_count = sum(len(records) for cat, records in categories.items() if cat.startswith('TIER_2'))
    tier3_count = sum(len(records) for cat, records in categories.items() if cat.startswith('TIER_3'))
    uncategorized = len(categories.get('UNCATEGORIZED', []))

    print(f"\n--- BY IMPORTANCE TIER ---")
    print(f"TIER 1 (Strategic Entities): {tier1_count} ({tier1_count/len(samples)*100:.1f}%)")
    print(f"TIER 2 (Technology/Equipment): {tier2_count} ({tier2_count/len(samples)*100:.1f}%)")
    print(f"TIER 3 (Commodity Purchases): {tier3_count} ({tier3_count/len(samples)*100:.1f}%)")
    print(f"UNCATEGORIZED (Review Needed): {uncategorized} ({uncategorized/len(samples)*100:.1f}%)")

    # Detailed breakdown
    print(f"\n--- DETAILED BREAKDOWN ---")
    for category in sorted(categories.keys()):
        records = categories[category]
        print(f"\n{category}: {len(records)} records")

        # Show confidence distribution
        confidences = [float(r['highest_confidence']) for r in records]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0
        print(f"  Average Confidence: {avg_conf:.2f}")

        # Show 3 examples
        for i, record in enumerate(records[:3]):
            recipient = record['recipient_name'][:40]
            desc = (record.get('award_description') or '')[:60]
            conf = record['highest_confidence']
            print(f"  {i+1}. [{conf}] {recipient}: {desc}...")

        if len(records) > 3:
            print(f"  ... and {len(records)-3} more")

    # Save categorization to CSV
    output_file = OUTPUT_DIR / "sample_categorization_analysis.csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Category', 'Tier', 'Transaction ID', 'Recipient Name',
            'Award Description (first 100 chars)', 'Confidence',
            'Detection Types', 'Suggested Importance'
        ])

        for category in sorted(categories.keys()):
            tier = category.split('_')[1] if '_' in category else 'N/A'
            importance = {
                '1': 'HIGH',
                '2': 'MEDIUM',
                '3': 'VERY_LOW',
                'N/A': 'REVIEW_NEEDED'
            }.get(tier, 'REVIEW_NEEDED')

            for record in categories[category]:
                writer.writerow([
                    category,
                    tier,
                    record['transaction_id'],
                    record['recipient_name'],
                    (record.get('award_description') or '')[:100],
                    record['highest_confidence'],
                    record['detection_types'],
                    importance
                ])

    print(f"\n{'='*80}")
    print(f"Full categorization saved to: {output_file}")
    print(f"{'='*80}")

    # Save summary JSON
    summary = {
        'total_records': len(samples),
        'by_tier': {
            'TIER_1_STRATEGIC': tier1_count,
            'TIER_2_TECHNOLOGY_EQUIPMENT': tier2_count,
            'TIER_3_COMMODITY': tier3_count,
            'UNCATEGORIZED': uncategorized
        },
        'by_category': {
            cat: {
                'count': len(records),
                'avg_confidence': sum(float(r['highest_confidence']) for r in records) / len(records)
            }
            for cat, records in categories.items()
        },
        'recommendations': {
            'tier_1_action': 'Keep HIGH importance - strategic intelligence value',
            'tier_2_action': 'Keep MEDIUM importance - technology transfer monitoring',
            'tier_3_action': 'Demote to VERY_LOW importance - commodity purchases only',
            'tier_3_rationale': 'Low strategic value, bulk procurement of manufactured goods'
        }
    }

    summary_file = OUTPUT_DIR / "sample_categorization_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"\nSummary saved to: {summary_file}")

    return categories, summary

if __name__ == '__main__':
    categories, summary = analyze_sample()
