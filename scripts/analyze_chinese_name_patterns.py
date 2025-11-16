#!/usr/bin/env python3
"""
Analyze "chinese_name_pattern" findings from comprehensive test.

The test found 447 records with Chinese name transliteration patterns.
Need to check if these are real Chinese entities or false positives.
"""

import gzip
import json
import re
from pathlib import Path
from process_usaspending_comprehensive import USAspendingComprehensiveProcessor

# Chinese name patterns from comprehensive test
CHINESE_NAME_PATTERNS = [
    (r'\b[a-z]*zh[a-z]*\b', 'zh sound'),
    (r'\b[a-z]*xi[a-z]*\b', 'xi sound'),
    (r'\b[a-z]*ch[a-z]*\b', 'ch sound'),
]

COMMON_ENGLISH_WORDS = {
    # Common "ch" words
    'ch': ['church', 'school', 'teach', 'technology', 'tech', 'channel', 'chapter', 'chief',
           'choice', 'choose', 'chosen', 'christmas', 'chronicle', 'merchant', 'purchase',
           'research', 'search', 'such', 'much', 'which', 'each', 'reach', 'beach',
           'rich', 'inch', 'lunch', 'bunch', 'ranch', 'branch'],
    # Common "sh" words
    'sh': ['show', 'shop', 'should', 'shape', 'share', 'sharp', 'shift', 'ship', 'shore'],
    # Common "zh" words
    'zh': [],  # Very few English words with 'zh'
}

def analyze_name_patterns(file_path: Path, max_records: int = 500000):
    """
    Check all records for Chinese name patterns and validate.
    """

    processor = USAspendingComprehensiveProcessor()

    print(f"\n{'='*80}")
    print("CHINESE NAME PATTERN ANALYSIS")
    print(f"{'='*80}\n")

    pattern_matches = []
    likely_false_positives = []
    potential_chinese = []

    record_count = 0

    with gzip.open(file_path, 'rt', encoding='utf-8', errors='replace') as f:
        for line_num, line in enumerate(f, 1):
            if record_count >= max_records:
                break

            fields = line.strip().split('\t')
            if len(fields) < 206:
                continue

            record_count += 1

            try:
                transaction = processor._extract_transaction(fields)

                # Check if already detected
                detection_results = processor._detect_china_entity(transaction, fields)
                if detection_results:
                    continue  # Already detected

                # Check for name patterns
                all_names = f"{transaction.recipient_name} {transaction.recipient_parent_name} {transaction.sub_awardee_name} {transaction.sub_awardee_parent_name}".lower()

                found_patterns = []
                matched_words = []

                for pattern, pattern_name in CHINESE_NAME_PATTERNS:
                    matches = re.findall(pattern, all_names)
                    if matches:
                        # Filter out common English words
                        if pattern_name == 'ch sound':
                            matches = [m for m in matches if m not in COMMON_ENGLISH_WORDS['ch']]
                        elif pattern_name == 'sh sound':
                            matches = [m for m in matches if m not in COMMON_ENGLISH_WORDS['sh']]

                        if matches:
                            found_patterns.append(pattern_name)
                            matched_words.extend(matches[:3])  # First 3 matches

                if found_patterns:
                    record = {
                        'line_number': line_num,
                        'recipient_name': transaction.recipient_name[:100],
                        'recipient_parent': transaction.recipient_parent_name[:100],
                        'recipient_country': transaction.recipient_country,
                        'sub_awardee_name': transaction.sub_awardee_name[:100],
                        'sub_awardee_country': transaction.sub_awardee_country,
                        'patterns': found_patterns,
                        'matched_words': matched_words[:5],
                        'amount': transaction.federal_action_obligation,
                    }

                    pattern_matches.append(record)

                    # Check if likely Chinese (has other Chinese indicators)
                    if any(keyword in all_names for keyword in ['china', 'chinese', 'beijing', 'shanghai', 'hong kong']):
                        potential_chinese.append(record)
                    # Check if likely false positive (common English words)
                    elif any(word in all_names for word in ['church', 'school', 'technology', 'research']):
                        if len(likely_false_positives) < 100:
                            likely_false_positives.append(record)

            except Exception as e:
                continue

            if record_count % 100000 == 0:
                print(f"  Processed {record_count:,} records")
                print(f"    Pattern matches: {len(pattern_matches)}")
                print(f"    Potential Chinese: {len(potential_chinese)}")

    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}")
    print(f"Total records: {record_count:,}")
    print(f"Name pattern matches: {len(pattern_matches)}")
    print(f"Potential Chinese entities: {len(potential_chinese)}")
    print(f"Likely false positives: {len(likely_false_positives)}")
    print(f"{'='*80}\n")

    return pattern_matches, potential_chinese, likely_false_positives


def save_analysis(pattern_matches, potential_chinese, likely_false_positives):
    """Save analysis results."""

    output_dir = Path("data/processed/usaspending_comprehensive_test")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save potential Chinese entities (PRIORITY)
    if potential_chinese:
        chinese_file = output_dir / "chinese_name_patterns_potential.json"
        with open(chinese_file, 'w', encoding='utf-8') as f:
            json.dump({
                'count': len(potential_chinese),
                'records': potential_chinese
            }, f, indent=2)
        print(f"Saved potential Chinese entities: {chinese_file}")
        print(f"  ⚠️  FOUND {len(potential_chinese)} POTENTIAL MISSES")

    # Save likely false positives
    fp_file = output_dir / "chinese_name_patterns_false_positives.json"
    with open(fp_file, 'w', encoding='utf-8') as f:
        json.dump({
            'count': len(likely_false_positives),
            'records': likely_false_positives
        }, f, indent=2)
    print(f"Saved likely false positives: {fp_file}")

    # Create summary
    summary_file = output_dir / "CHINESE_NAME_PATTERNS_ANALYSIS.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("CHINESE NAME PATTERN ANALYSIS\n")
        f.write("="*80 + "\n\n")

        f.write(f"Total pattern matches: {len(pattern_matches)}\n")
        f.write(f"Potential Chinese entities: {len(potential_chinese)}\n")
        f.write(f"Likely false positives: {len(likely_false_positives)}\n\n")

        if not potential_chinese:
            f.write("✅ NO CHINESE ENTITIES FOUND\n\n")
            f.write("All name pattern matches appear to be false positives.\n")
        else:
            f.write(f"⚠️  FOUND {len(potential_chinese)} POTENTIAL CHINESE ENTITIES\n\n")

            f.write("="*80 + "\n")
            f.write("POTENTIAL CHINESE ENTITIES (Manual Review Required)\n")
            f.write("="*80 + "\n\n")

            for i, record in enumerate(potential_chinese[:20], 1):
                f.write(f"{i}. LINE {record['line_number']}\n")
                f.write(f"   Recipient: {record['recipient_name']}\n")
                if record['recipient_parent']:
                    f.write(f"   Parent: {record['recipient_parent']}\n")
                f.write(f"   Country: {record['recipient_country']}\n")
                if record['sub_awardee_name']:
                    f.write(f"   Sub-awardee: {record['sub_awardee_name']}\n")
                f.write(f"   Patterns: {', '.join(record['patterns'])}\n")
                f.write(f"   Matched words: {', '.join(record['matched_words'])}\n")
                f.write(f"   Amount: ${record['amount']:,.2f}\n")
                f.write("\n" + "-"*80 + "\n\n")

        f.write("="*80 + "\n")
        f.write("SAMPLE FALSE POSITIVES\n")
        f.write("="*80 + "\n\n")

        for i, record in enumerate(likely_false_positives[:10], 1):
            f.write(f"{i}. {record['recipient_name'][:70]}\n")
            f.write(f"   Matched: {', '.join(record['matched_words'][:3])}\n\n")

    print(f"Created summary: {summary_file}")


def main():
    """Run name pattern analysis."""

    test_file = Path("F:/OSINT_DATA/USAspending/extracted_data/5876.dat.gz")

    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return

    pattern_matches, potential_chinese, likely_false_positives = analyze_name_patterns(
        test_file, max_records=500000
    )

    save_analysis(pattern_matches, potential_chinese, likely_false_positives)

    print("\n" + "="*80)
    if potential_chinese:
        print(f"WARNING: Found {len(potential_chinese)} potential Chinese entities")
        print("Review CHINESE_NAME_PATTERNS_ANALYSIS.txt")
    else:
        print("SUCCESS: No Chinese entities found via name patterns")
        print("Patterns create only false positives - should NOT be used")
    print("="*80)


if __name__ == '__main__':
    main()
