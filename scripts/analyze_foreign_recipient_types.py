#!/usr/bin/env python3
"""
Analyze "foreign_recipient_type" findings from comprehensive test.

The comprehensive test found 7,755 records (1.5%) with "foreign_recipient_type"
indicators. We need to manually review a sample to see if these are actually
Chinese entities we're missing or just generic "foreign" classifications.
"""

import gzip
import json
from pathlib import Path
from collections import Counter
from process_usaspending_comprehensive import USAspendingComprehensiveProcessor

def analyze_foreign_types(file_path: Path, max_records: int = 500000):
    """
    Extract and analyze all records with "foreign" in recipient_type field.
    """

    processor = USAspendingComprehensiveProcessor()

    print(f"\n{'='*80}")
    print("FOREIGN RECIPIENT TYPE ANALYSIS")
    print(f"{'='*80}\n")

    foreign_types_found = Counter()
    chinese_in_foreign = []
    all_foreign_sample = []

    record_count = 0

    with gzip.open(file_path, 'rt', encoding='utf-8', errors='replace') as f:
        for line_num, line in enumerate(f, 1):
            if record_count >= max_records:
                break

            fields = line.strip().split('\t')
            if len(fields) < 206:
                continue

            record_count += 1

            # Get recipient type
            recipient_type = fields[37] if len(fields) > 37 else ''
            recipient_country = fields[29] if len(fields) > 29 else ''

            # Check if "foreign" in type AND not already detected as China
            if recipient_type and 'foreign' in recipient_type.lower():
                foreign_types_found[recipient_type] += 1

                # Check if already detected by standard logic
                try:
                    transaction = processor._extract_transaction(fields)
                    detection_results = processor._detect_china_entity(transaction, fields)

                    if not detection_results:
                        # NOT already detected - could be a miss!
                        record = {
                            'line_number': line_num,
                            'recipient_name': transaction.recipient_name[:100],
                            'recipient_parent': transaction.recipient_parent_name[:100],
                            'recipient_type': recipient_type,
                            'recipient_country': recipient_country,
                            'sub_awardee_name': transaction.sub_awardee_name[:100],
                            'sub_awardee_country': transaction.sub_awardee_country,
                            'amount': transaction.federal_action_obligation,
                            'description': transaction.award_description[:200],
                        }

                        # Check if this looks Chinese
                        all_text = f"{transaction.recipient_name} {transaction.recipient_parent_name} {transaction.sub_awardee_name}".lower()
                        if any(keyword in all_text for keyword in ['china', 'chinese', 'beijing', 'shanghai']):
                            chinese_in_foreign.append(record)

                        if len(all_foreign_sample) < 200:
                            all_foreign_sample.append(record)

                except Exception as e:
                    continue

            if record_count % 100000 == 0:
                print(f"  Processed {record_count:,} records")
                print(f"    Foreign types found: {len(foreign_types_found)}")
                print(f"    Chinese in foreign: {len(chinese_in_foreign)}")

    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}")
    print(f"Total records: {record_count:,}")
    print(f"Unique foreign recipient types: {len(foreign_types_found)}")
    print(f"Total 'foreign' type records: {sum(foreign_types_found.values()):,}")
    print(f"Chinese entities with 'foreign' type: {len(chinese_in_foreign)}")
    print(f"{'='*80}\n")

    # Print breakdown of foreign types
    print("Foreign Recipient Types:")
    for type_desc, count in foreign_types_found.most_common(20):
        print(f"  {count:6,} | {type_desc[:70]}")

    return foreign_types_found, chinese_in_foreign, all_foreign_sample


def save_analysis(foreign_types, chinese_in_foreign, all_foreign_sample):
    """Save analysis results."""

    output_dir = Path("data/processed/usaspending_comprehensive_test")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save foreign types breakdown
    types_file = output_dir / "foreign_recipient_types_breakdown.json"
    with open(types_file, 'w', encoding='utf-8') as f:
        json.dump({
            'unique_types': len(foreign_types),
            'total_records': sum(foreign_types.values()),
            'types': [{'type': k, 'count': v} for k, v in foreign_types.most_common()],
        }, f, indent=2)

    print(f"\nSaved types breakdown: {types_file}")

    # Save Chinese entities with foreign type (potential misses)
    if chinese_in_foreign:
        chinese_file = output_dir / "chinese_with_foreign_type.json"
        with open(chinese_file, 'w', encoding='utf-8') as f:
            json.dump({
                'count': len(chinese_in_foreign),
                'records': chinese_in_foreign
            }, f, indent=2)
        print(f"Saved Chinese entities with foreign type: {chinese_file}")
        print(f"  ⚠️  FOUND {len(chinese_in_foreign)} POTENTIAL MISSES")

    # Save diverse sample
    sample_file = output_dir / "foreign_type_sample.json"
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump({
            'sample_size': len(all_foreign_sample),
            'records': all_foreign_sample[:100]
        }, f, indent=2)
    print(f"Saved sample: {sample_file}")

    # Create human-readable summary
    summary_file = output_dir / "FOREIGN_TYPE_ANALYSIS.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("FOREIGN RECIPIENT TYPE ANALYSIS\n")
        f.write("="*80 + "\n\n")

        f.write(f"Total 'foreign' recipient type records: {sum(foreign_types.values()):,}\n")
        f.write(f"Unique type descriptions: {len(foreign_types)}\n")
        f.write(f"Chinese entities found: {len(chinese_in_foreign)}\n\n")

        if not chinese_in_foreign:
            f.write("✅ NO CHINESE ENTITIES WITH FOREIGN TYPE\n\n")
            f.write("All 'foreign' classifications appear to be non-Chinese.\n")
        else:
            f.write(f"⚠️  FOUND {len(chinese_in_foreign)} CHINESE ENTITIES WITH FOREIGN TYPE\n\n")
            f.write("These may have been missed by standard detection logic.\n\n")

            f.write("="*80 + "\n")
            f.write("CHINESE ENTITIES WITH FOREIGN TYPE (Potential Misses)\n")
            f.write("="*80 + "\n\n")

            for i, record in enumerate(chinese_in_foreign[:20], 1):
                f.write(f"{i}. LINE {record['line_number']}\n")
                f.write(f"   Recipient: {record['recipient_name']}\n")
                if record['recipient_parent']:
                    f.write(f"   Parent: {record['recipient_parent']}\n")
                f.write(f"   Type: {record['recipient_type']}\n")
                f.write(f"   Country: {record['recipient_country']}\n")
                if record['sub_awardee_name']:
                    f.write(f"   Sub-awardee: {record['sub_awardee_name']}\n")
                f.write(f"   Amount: ${record['amount']:,.2f}\n")
                if record['description']:
                    f.write(f"   Description: {record['description']}\n")
                f.write("\n" + "-"*80 + "\n\n")

        f.write("="*80 + "\n")
        f.write("TOP 20 FOREIGN RECIPIENT TYPES\n")
        f.write("="*80 + "\n\n")

        for type_desc, count in foreign_types.most_common(20):
            f.write(f"{count:6,} | {type_desc}\n")

    print(f"Created summary: {summary_file}")


def main():
    """Run foreign type analysis."""

    test_file = Path("F:/OSINT_DATA/USAspending/extracted_data/5876.dat.gz")

    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return

    foreign_types, chinese_in_foreign, all_foreign_sample = analyze_foreign_types(
        test_file, max_records=500000
    )

    save_analysis(foreign_types, chinese_in_foreign, all_foreign_sample)

    print("\n" + "="*80)
    if chinese_in_foreign:
        print(f"WARNING: Found {len(chinese_in_foreign)} Chinese entities with 'foreign' type")
        print("These may be missed by current detection logic.")
        print("Review FOREIGN_TYPE_ANALYSIS.txt for details")
    else:
        print("SUCCESS: No Chinese entities found in 'foreign' type classifications")
        print("Current detection logic appears comprehensive")
    print("="*80)


if __name__ == '__main__':
    main()
