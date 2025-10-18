#!/usr/bin/env python3
"""
Direct analysis of USASpending data for China-related patterns
Processes the large .dat files directly without PostgreSQL import
More efficient for one-time analysis
"""

import re
from pathlib import Path
from datetime import datetime
import json

def analyze_china_patterns():
    base_path = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/")

    # China-related patterns to search for
    china_patterns = [
        r'\bchina\b', r'\bchinese\b', r'\bprc\b', r'\bbeijing\b',
        r'\bshanghai\b', r'\bshenzhen\b', r'\bhuawei\b', r'\bzte\b',
        r'\blenovo\b', r'\balibaba\b', r'\btencent\b', r'\bbaidu\b',
        r'\bdji\b', r'\bxiaomi\b', r'\bbyd\b', r'\bhaier\b',
        # Add patterns for Chinese universities and research institutes
        r'\btsinghua\b', r'\bpeking university\b', r'\bcas\b',
        r'\bchinese academy\b', r'\bfudan\b', r'\bzhejiang\b'
    ]

    # Compile patterns for efficiency
    compiled_patterns = [re.compile(p, re.IGNORECASE) for p in china_patterns]

    print("=" * 70)
    print("CHINA PATTERN ANALYSIS IN USASPENDING DATA")
    print(f"Start time: {datetime.now()}")
    print("=" * 70)

    # Check which files are ready
    large_files = ['5801', '5836', '5847', '5848', '5862']
    ready_files = []

    for name in large_files:
        dat_file = base_path / f"{name}.dat"
        if dat_file.exists():
            size_gb = dat_file.stat().st_size / 1e9

            # Check for PostgreSQL end marker to ensure complete
            with open(dat_file, 'rb') as f:
                f.seek(max(0, dat_file.stat().st_size - 1000))
                last_bytes = f.read(1000)
                is_complete = b'\\.' in last_bytes

            if is_complete or name == '5801':  # 5801 might still be processing
                ready_files.append((name, dat_file, size_gb))
                status = "COMPLETE" if is_complete else "PROCESSING"
                print(f"  {name}.dat: {size_gb:.2f} GB [{status}]")

    if not ready_files:
        print("No files ready for analysis!")
        return

    print("\n" + "-" * 70)
    print("Searching for China-related patterns...")
    print("-" * 70)

    results = {}

    for name, dat_file, size_gb in ready_files:
        print(f"\nAnalyzing {name}.dat ({size_gb:.2f} GB)...")

        matches = []
        line_count = 0
        china_count = 0
        sample_size = 100 * 1024 * 1024  # Analyze first 100MB of each file

        try:
            with open(dat_file, 'r', encoding='utf-8', errors='ignore') as f:
                bytes_read = 0

                for line_num, line in enumerate(f, 1):
                    line_count += 1
                    bytes_read += len(line.encode('utf-8', errors='ignore'))

                    # Search for China patterns
                    line_lower = line.lower()
                    for pattern in compiled_patterns:
                        if pattern.search(line_lower):
                            china_count += 1
                            if len(matches) < 10:  # Keep first 10 matches as examples
                                matches.append({
                                    'line_num': line_num,
                                    'pattern': pattern.pattern,
                                    'context': line[:200]
                                })
                            break

                    # Stop after sample size
                    if bytes_read >= sample_size:
                        break

                # Extrapolate to full file
                if bytes_read > 0:
                    total_estimated_lines = int(line_count * (size_gb * 1e9 / bytes_read))
                    total_estimated_china = int(china_count * (size_gb * 1e9 / bytes_read))
                else:
                    total_estimated_lines = 0
                    total_estimated_china = 0

                results[name] = {
                    'file_size_gb': size_gb,
                    'lines_analyzed': line_count,
                    'china_mentions_found': china_count,
                    'estimated_total_lines': total_estimated_lines,
                    'estimated_total_china_mentions': total_estimated_china,
                    'china_percentage': (china_count / line_count * 100) if line_count > 0 else 0,
                    'sample_matches': matches[:5]  # Keep only 5 examples
                }

                print(f"  Lines analyzed: {line_count:,}")
                print(f"  China mentions found: {china_count:,}")
                print(f"  Estimated total China mentions: {total_estimated_china:,}")
                print(f"  China percentage: {results[name]['china_percentage']:.4f}%")

        except Exception as e:
            print(f"  Error analyzing {name}: {e}")
            results[name] = {'error': str(e)}

    # Save results
    output_file = Path("china_pattern_analysis_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)

    total_china_mentions = sum(r.get('estimated_total_china_mentions', 0)
                               for r in results.values() if 'error' not in r)

    print(f"Total estimated China-related records: {total_china_mentions:,}")
    print(f"Results saved to: {output_file}")

    # Print top patterns found
    print("\nSample China-related records found:")
    for name, result in results.items():
        if 'sample_matches' in result and result['sample_matches']:
            print(f"\nFrom {name}.dat:")
            for match in result['sample_matches'][:2]:
                print(f"  Line {match['line_num']}: {match['context'][:100]}...")

    print("\n" + "=" * 70)
    print(f"End time: {datetime.now()}")

if __name__ == "__main__":
    analyze_china_patterns()
