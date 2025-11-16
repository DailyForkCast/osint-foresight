#!/usr/bin/env python3
"""
analyze_substring_false_positives.py - Identify Substring False Positives

Analyzes TIER_2 non-China/non-US export to find records where chinese_name
detector matched SUBSTRINGS within larger words (word boundary issue).

Examples:
- "KASINO" contains "SINO"
- "TECHNIK" contains "CHIN"
- "MACHINARY" contains "CHIN"
"""

import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime

# Common Chinese name patterns that trigger detection
CHINESE_PATTERNS = [
    'CHIN', 'CHINA', 'CHINESE',
    'SINO', 'SINOASIA',
    'BEIJING', 'SHANGHAI', 'GUANGZHOU', 'SHENZHEN',
    'HUA', 'HUAWEI',
    'ZTE', 'HAIER', 'LENOVO',
    'TSINGHUA', 'PEKING',
    'HONG', 'KONG',
    # Common Chinese surnames/names
    'WANG', 'LI', 'ZHANG', 'LIU', 'CHEN', 'YANG', 'HUANG', 'ZHAO', 'WU', 'ZHOU',
    'XU', 'SUN', 'MA', 'ZHU', 'HU', 'GUO', 'HE', 'GAO', 'LIN', 'LUO',
    # Pinyin patterns
    'XING', 'MING', 'DONG', 'FENG', 'WEI', 'JIAN', 'PING', 'QING',
]

# German/European words that contain Chinese patterns
KNOWN_EUROPEAN_WORDS = {
    'TECHNIK': 'CHIN',      # German for "technology"
    'TECHNISCHE': 'CHIN',   # German for "technical"
    'KASINO': 'SINO',       # German for "casino"
    'MASCHINEN': 'CHIN',    # German for "machines"
    'MACHINERY': 'CHIN',    # English, often misspelled
    'MACHINARY': 'CHIN',    # Common misspelling
    'MACHINE': 'CHIN',
    'MECHANICS': 'CHIN',
    'MECHANICAL': 'CHIN',
    'SCHINENVERKEHR': 'CHIN',  # German rail-related
}

def analyze_substring_patterns(csv_path):
    """Analyze CSV for substring false positive patterns"""

    print("="*80)
    print("SUBSTRING FALSE POSITIVE ANALYSIS")
    print("="*80)
    print(f"\nInput: {csv_path}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load data
    df = pd.read_csv(csv_path)
    print(f"\nTotal records: {len(df)}")

    # Track results
    substring_matches = []

    # Analyze each record
    for idx, row in df.iterrows():
        recipient = str(row.get('Recipient_Name', '')).upper()
        vendor = str(row.get('Vendor_Name', '')).upper()

        # Check for substring matches
        for text, field_name in [(recipient, 'Recipient_Name'), (vendor, 'Vendor_Name')]:
            if text == 'NAN' or not text:
                continue

            # Check each Chinese pattern
            for pattern in CHINESE_PATTERNS:
                if pattern in text:
                    # Check if it's a substring match (not whole word)
                    # Use word boundaries
                    whole_word_pattern = r'\b' + re.escape(pattern) + r'\b'

                    if pattern in text and not re.search(whole_word_pattern, text):
                        # This is a substring match!

                        # Find the word containing the pattern
                        words = text.split()
                        containing_words = [w for w in words if pattern in w and w != pattern]

                        if containing_words:
                            substring_matches.append({
                                'recipient_name': row.get('Recipient_Name', ''),
                                'vendor_name': row.get('Vendor_Name', ''),
                                'field': field_name,
                                'full_text': text,
                                'chinese_pattern': pattern,
                                'containing_words': containing_words,
                                'recipient_country': row.get('Recipient_Country', ''),
                                'pop_country': row.get('POP_Country', ''),
                                'detection_types': row.get('Detection_Types', ''),
                                'confidence': row.get('Confidence_Tier', '')
                            })

    print(f"\n[OK] Found {len(substring_matches)} substring false positive matches")

    # Convert to DataFrame
    matches_df = pd.DataFrame(substring_matches)

    if len(matches_df) == 0:
        print("\n[!] No substring matches found")
        return

    # Analyze patterns
    print("\n" + "="*80)
    print("SUBSTRING PATTERN ANALYSIS")
    print("="*80)

    # Group by containing word
    all_containing_words = []
    for words_list in matches_df['containing_words']:
        all_containing_words.extend(words_list)

    word_counts = pd.Series(all_containing_words).value_counts()

    print("\nTop 30 Words Containing Chinese Patterns:")
    print(f"{'Word':<40} {'Count':<10} {'Likely Pattern'}")
    print("-"*80)

    for word, count in word_counts.head(30).items():
        # Find which pattern(s) triggered this word
        pattern_matches = matches_df[matches_df['containing_words'].apply(lambda x: word in x)]
        patterns = pattern_matches['chinese_pattern'].unique()
        pattern_str = ', '.join(patterns[:3])  # Show up to 3 patterns

        print(f"{word:<40} {count:<10} {pattern_str}")

    # Group by Chinese pattern
    print("\n" + "="*80)
    print("GROUPED BY CHINESE PATTERN")
    print("="*80)

    pattern_counts = matches_df['chinese_pattern'].value_counts()
    for pattern, count in pattern_counts.head(10).items():
        print(f"\nPattern: '{pattern}' -> {count} substring matches")

        # Show example words
        pattern_matches = matches_df[matches_df['chinese_pattern'] == pattern]
        example_words = []
        for words_list in pattern_matches['containing_words'].head(5):
            example_words.extend(words_list)
        example_words = list(set(example_words))[:5]

        print(f"  Example words: {', '.join(example_words)}")

    # Identify clear false positives
    print("\n" + "="*80)
    print("CLEAR FALSE POSITIVE CATEGORIES")
    print("="*80)

    german_tech_words = matches_df[matches_df['containing_words'].apply(
        lambda words: any('TECHNIK' in w or 'TECHNISCHE' in w for w in words)
    )]
    print(f"\nGerman Technical Words (TECHNIK, TECHNISCHE): {len(german_tech_words)} records")
    if len(german_tech_words) > 0:
        print("  Examples:")
        for i, row in german_tech_words.head(5).iterrows():
            print(f"    - {row['recipient_name']}")

    kasino_words = matches_df[matches_df['containing_words'].apply(
        lambda words: any('KASINO' in w for w in words)
    )]
    print(f"\nGerman Casino Words (KASINO): {len(kasino_words)} records")
    if len(kasino_words) > 0:
        print("  Examples:")
        for i, row in kasino_words.head(5).iterrows():
            print(f"    - {row['recipient_name']}")

    machine_words = matches_df[matches_df['containing_words'].apply(
        lambda words: any('MACHINE' in w or 'MACHINERY' in w or 'MACHINARY' in w for w in words)
    )]
    print(f"\nMachine/Machinery Words: {len(machine_words)} records")
    if len(machine_words) > 0:
        print("  Examples:")
        for i, row in machine_words.head(5).iterrows():
            print(f"    - {row['recipient_name']}")

    mechanic_words = matches_df[matches_df['containing_words'].apply(
        lambda words: any('MECHANIC' in w for w in words)
    )]
    print(f"\nMechanical Words: {len(mechanic_words)} records")
    if len(mechanic_words) > 0:
        print("  Examples:")
        for i, row in mechanic_words.head(5).iterrows():
            print(f"    - {row['recipient_name']}")

    # Export detailed results
    output_dir = Path("analysis")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Excel export
    excel_path = output_dir / f"substring_false_positives_{timestamp}.xlsx"

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = {
            'Category': [
                'Total Records Analyzed',
                'Substring Matches Found',
                'German Technical Words',
                'German Casino Words',
                'Machine/Machinery Words',
                'Mechanical Words',
                'Unique Patterns Detected',
                'Analysis Date'
            ],
            'Count': [
                len(df),
                len(matches_df),
                len(german_tech_words),
                len(kasino_words),
                len(machine_words),
                len(mechanic_words),
                len(pattern_counts),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

        # All substring matches
        matches_df.to_excel(writer, sheet_name='All Substring Matches', index=False)

        # Top words
        word_freq = pd.DataFrame({
            'Word': word_counts.index,
            'Count': word_counts.values
        })
        word_freq.to_excel(writer, sheet_name='Top Words', index=False)

        # By pattern
        pattern_freq = pd.DataFrame({
            'Pattern': pattern_counts.index,
            'Count': pattern_counts.values
        })
        pattern_freq.to_excel(writer, sheet_name='By Pattern', index=False)

        # Category sheets
        if len(german_tech_words) > 0:
            german_tech_words.to_excel(writer, sheet_name='German Technical', index=False)
        if len(kasino_words) > 0:
            kasino_words.to_excel(writer, sheet_name='German Casino', index=False)
        if len(machine_words) > 0:
            machine_words.to_excel(writer, sheet_name='Machine Words', index=False)
        if len(mechanic_words) > 0:
            mechanic_words.to_excel(writer, sheet_name='Mechanical Words', index=False)

    print(f"\n[OK] Excel report: {excel_path}")

    # Generate list of unique entities for removal
    unique_recipients = matches_df['recipient_name'].unique()
    # Filter out NaN values
    unique_recipients = [str(x) for x in unique_recipients if pd.notna(x) and str(x) != 'nan']
    print(f"\n[OK] Found {len(unique_recipients)} unique entities with substring false positives")

    # Save entity list
    entity_list_path = output_dir / f"substring_false_positive_entities_{timestamp}.txt"
    with open(entity_list_path, 'w') as f:
        f.write("# Entities with Substring False Positive Patterns\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Total: {len(unique_recipients)} entities\n\n")
        for entity in sorted(unique_recipients):
            f.write(f"{entity}\n")

    print(f"[OK] Entity list: {entity_list_path}")

    # Print summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)

    print(f"\nTotal records analyzed: {len(df)}")
    print(f"Substring false positives found: {len(matches_df)}")
    print(f"Unique entities affected: {len(unique_recipients)}")
    print(f"Percentage of file: {len(matches_df)/len(df)*100:.1f}%")

    print("\nTop 5 Problematic Patterns:")
    for i, (pattern, count) in enumerate(pattern_counts.head(5).items(), 1):
        print(f"  {i}. '{pattern}': {count} matches")

    print("\nRecommended Actions:")
    print("  1. Add word boundary checking to chinese_name detector")
    print("  2. Exclude common European words (TECHNIK, KASINO, MACHINERY)")
    print("  3. Remove these entities from TIER_2")
    print("  4. Re-run detection with improved word boundaries")

    print("\n" + "="*80)

    return excel_path, entity_list_path, matches_df

def main():
    # Find most recent export
    csv_path = "data/processed/usaspending_manual_review/tier2_non_china_COMPLETE_20251019_110542.csv"

    analyze_substring_patterns(csv_path)

if __name__ == "__main__":
    main()
