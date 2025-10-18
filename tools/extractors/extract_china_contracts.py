#!/usr/bin/env python3
"""
Extract and categorize all 42.4 million China-related records from file 5848
This is the critical deep-dive analysis
"""

import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

def extract_china_contracts():
    print("=" * 80)
    print("EXTRACTING 42.4 MILLION CHINA-RELATED FEDERAL CONTRACTS")
    print(f"Start time: {datetime.now()}")
    print("=" * 80)

    # File 5848 - the goldmine with 43% China references
    data_file = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5848.dat")

    if not data_file.exists():
        print(f"ERROR: {data_file} not found!")
        return

    file_size_gb = data_file.stat().st_size / 1e9
    print(f"File size: {file_size_gb:.2f} GB")
    print(f"Expected China records: ~42.4 million")
    print("-" * 80)

    # Enhanced China patterns for deeper analysis
    china_company_patterns = [
        r'\bhuawei\b', r'\bzte\b', r'\blenovo\b', r'\balibaba\b', r'\btencent\b',
        r'\bbaidu\b', r'\bdji\b', r'\bxiaomi\b', r'\bbyd\b', r'\bhaier\b',
        r'\bhikvision\b', r'\bdahua\b', r'\bsmic\b', r'\bcrrc\b', r'\bcomac\b',
        r'\bcosco\b', r'\bsinopec\b', r'\bcnooc\b', r'\bpetroChina\b',
        r'\bbank of china\b', r'\bicbc\b', r'\bccb\b', r'\bagricultural bank of china\b'
    ]

    china_location_patterns = [
        r'\bchina\b', r'\bchinese\b', r'\bprc\b', r'\bpeople\'?s republic\b',
        r'\bbeijing\b', r'\bshanghai\b', r'\bshenzhen\b', r'\bguangzhou\b',
        r'\bhong kong\b', r'\btianjin\b', r'\bwuhan\b', r'\bchengdu\b',
        r'\bxian\b', r'\bhangzhou\b', r'\bnanjing\b', r'\bdalian\b'
    ]

    china_institution_patterns = [
        r'\bcas\b', r'\bchinese academy\b', r'\btsinghua\b', r'\bpeking university\b',
        r'\bfudan\b', r'\bzhejiang\b', r'\bharbin\b', r'\bbeihang\b',
        r'\bbuaa\b', r'\bnudt\b', r'\bnorinco\b', r'\bavic\b', r'\bcasic\b',
        r'\bcasc\b', r'\bcetc\b', r'\bcssc\b', r'\bcsic\b'
    ]

    # Compile all patterns
    all_patterns = china_company_patterns + china_location_patterns + china_institution_patterns
    compiled_patterns = [re.compile(p, re.IGNORECASE) for p in all_patterns]

    # Categories for analysis
    categories = {
        'defense_related': re.compile(r'\b(defense|military|army|navy|air force|missile|weapon|radar|satellite)\b', re.IGNORECASE),
        'technology': re.compile(r'\b(software|hardware|computer|network|cyber|data|ai|artificial intelligence|5g|semiconductor)\b', re.IGNORECASE),
        'infrastructure': re.compile(r'\b(construction|bridge|port|railway|highway|airport|power|energy|grid)\b', re.IGNORECASE),
        'telecommunications': re.compile(r'\b(telecom|communications|wireless|cellular|broadband|fiber)\b', re.IGNORECASE),
        'research': re.compile(r'\b(research|study|analysis|laboratory|university|institute|academic)\b', re.IGNORECASE),
        'supply_chain': re.compile(r'\b(supply|procurement|vendor|supplier|manufacturer|import|export)\b', re.IGNORECASE)
    }

    # Storage for results
    china_contracts = []
    entity_counts = Counter()
    category_counts = Counter()
    timeline = defaultdict(int)
    high_risk_contracts = []

    # Value thresholds for risk assessment
    HIGH_VALUE_THRESHOLD = 1000000  # $1M

    print("\nProcessing file (this will take 10-15 minutes for 222 GB)...")
    print("Extracting: Companies, Locations, Values, Dates, Risk Indicators")
    print("-" * 80)

    lines_processed = 0
    china_found = 0
    high_value_count = 0
    defense_count = 0
    sample_limit = 1000000  # Extract first 1M China records for detailed analysis

    try:
        with open(data_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                lines_processed += 1

                # Progress indicator
                if lines_processed % 100000 == 0:
                    pct = (lines_processed * 100 / 98463609)  # Total lines from previous analysis
                    print(f"  Progress: {lines_processed:,} lines ({pct:.1f}%) - Found {china_found:,} China records")

                line_lower = line.lower()

                # Check for China patterns
                china_match = False
                matched_patterns = []

                for pattern in compiled_patterns:
                    if pattern.search(line_lower):
                        china_match = True
                        matched_patterns.append(pattern.pattern)
                        entity_counts[pattern.pattern] += 1

                if china_match:
                    china_found += 1

                    # Extract contract details (if within sample limit)
                    if china_found <= sample_limit:
                        fields = line.split('\t')

                        # Extract key fields (positions may vary)
                        contract_data = {
                            'line_number': line_num,
                            'matched_patterns': matched_patterns,
                            'full_text': line[:500],  # First 500 chars
                            'fields': fields[:10] if len(fields) > 10 else fields  # First 10 fields
                        }

                        # Try to extract value (look for numeric fields)
                        for field in fields:
                            try:
                                value = float(field.replace(',', '').replace('$', ''))
                                if value > 1000:  # Likely a contract value
                                    contract_data['value'] = value
                                    if value >= HIGH_VALUE_THRESHOLD:
                                        high_value_count += 1
                                    break
                            except:
                                continue

                        # Extract date (look for date patterns)
                        date_pattern = re.search(r'20\d{2}-\d{2}-\d{2}|20\d{6}', line)
                        if date_pattern:
                            date_str = date_pattern.group()
                            contract_data['date'] = date_str
                            year = date_str[:4]
                            timeline[year] += 1

                        # Categorize
                        for cat_name, cat_pattern in categories.items():
                            if cat_pattern.search(line_lower):
                                contract_data['category'] = cat_name
                                category_counts[cat_name] += 1

                                # Flag high-risk
                                if cat_name in ['defense_related', 'telecommunications']:
                                    high_risk_contracts.append(contract_data)
                                    defense_count += 1
                                break

                        china_contracts.append(contract_data)

                # Stop after processing enough data for analysis
                if lines_processed >= 10000000:  # Process first 10M lines for speed
                    print(f"\nStopping after {lines_processed:,} lines for initial analysis")
                    break

    except Exception as e:
        print(f"Error during processing: {e}")

    # Analysis results
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)

    print(f"\nRecords Processed: {lines_processed:,}")
    print(f"China Records Found: {china_found:,}")
    print(f"China Percentage: {(china_found/lines_processed*100):.2f}%")

    print(f"\nHigh-Value Contracts (>$1M): {high_value_count:,}")
    print(f"Defense/Telecom Related: {defense_count:,}")

    # Top entities
    print("\nTOP CHINA ENTITIES MENTIONED:")
    print("-" * 40)
    for entity, count in entity_counts.most_common(20):
        print(f"  {entity}: {count:,} mentions")

    # Category breakdown
    print("\nCONTRACT CATEGORIES:")
    print("-" * 40)
    total_categorized = sum(category_counts.values())
    for category, count in category_counts.most_common():
        pct = (count / total_categorized * 100) if total_categorized > 0 else 0
        print(f"  {category}: {count:,} ({pct:.1f}%)")

    # Timeline
    print("\nTIMELINE OF CHINA CONTRACTS:")
    print("-" * 40)
    for year in sorted(timeline.keys()):
        print(f"  {year}: {timeline[year]:,} contracts")

    # High-risk contracts
    print(f"\nHIGH-RISK CONTRACTS IDENTIFIED: {len(high_risk_contracts):,}")
    if high_risk_contracts:
        print("\nSample High-Risk Contracts:")
        for contract in high_risk_contracts[:5]:
            print(f"  Line {contract['line_number']}: {contract.get('category', 'uncategorized')}")
            if 'value' in contract:
                print(f"    Value: ${contract['value']:,.2f}")
            print(f"    Patterns: {', '.join(contract['matched_patterns'][:3])}")

    # Save detailed results
    output_file = Path("china_contracts_detailed.json")
    results_summary = {
        'processing_stats': {
            'lines_processed': lines_processed,
            'china_records_found': china_found,
            'china_percentage': china_found/lines_processed*100 if lines_processed > 0 else 0,
            'high_value_count': high_value_count,
            'defense_related': defense_count
        },
        'top_entities': dict(entity_counts.most_common(50)),
        'categories': dict(category_counts),
        'timeline': dict(timeline),
        'high_risk_sample': high_risk_contracts[:100],  # Save first 100 high-risk
        'sample_contracts': china_contracts[:1000]  # Save first 1000 for analysis
    }

    with open(output_file, 'w') as f:
        json.dump(results_summary, f, indent=2, default=str)

    print(f"\nDetailed results saved to: {output_file}")

    # Extrapolation to full dataset
    if lines_processed > 0:
        extrapolated_total = int(china_found * (98463609 / lines_processed))
        print(f"\nEXTRAPOLATED TOTAL China contracts in full file: {extrapolated_total:,}")

    print("\n" + "=" * 80)
    print(f"End time: {datetime.now()}")

    return results_summary

if __name__ == "__main__":
    extract_china_contracts()
