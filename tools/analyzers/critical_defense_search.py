#!/usr/bin/env python3
"""
Search for CRITICAL China-Defense connections in USASpending
Focus on military, weapons, critical infrastructure
"""

import re
from pathlib import Path
from datetime import datetime
import json

def search_critical_defense():
    print("=" * 80)
    print("CRITICAL CHINA-DEFENSE CONNECTION SEARCH")
    print(f"Start: {datetime.now()}")
    print("=" * 80)

    # Target file 5848 - where 43% are China-related
    data_file = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5848.dat")

    # Critical defense patterns
    defense_patterns = {
        'weapons': r'\b(weapon|missile|ammunition|ordnance|artillery|bomb)\b',
        'military_systems': r'\b(f-35|f-22|aegis|patriot|thaad|radar|sonar)\b',
        'naval': r'\b(submarine|destroyer|carrier|warship|naval)\b',
        'aerospace': r'\b(fighter|bomber|drone|uav|satellite|spacecraft)\b',
        'cyber': r'\b(cyber|classified|secret|confidential|encryption)\b',
        'nuclear': r'\b(nuclear|uranium|plutonium|enrichment)\b',
        'critical_infrastructure': r'\b(power grid|water system|pipeline|dam|airport)\b',
        'communications': r'\b(5g|telecommunications|satcom|secure communication)\b'
    }

    # China patterns
    china_pattern = re.compile(r'\b(china|chinese|prc|beijing|shanghai|huawei|zte|lenovo)\b', re.IGNORECASE)

    # Compile defense patterns
    compiled_defense = {k: re.compile(v, re.IGNORECASE) for k, v in defense_patterns.items()}

    print(f"\nSearching {data_file.name} for China + Defense combinations...")
    print("Looking for: weapons, military systems, classified, nuclear, etc.")
    print("-" * 80)

    critical_findings = []
    category_counts = {k: 0 for k in defense_patterns.keys()}
    total_critical = 0

    lines_checked = 0
    max_lines = 5000000  # Check first 5M lines

    with open(data_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            lines_checked += 1

            if lines_checked % 500000 == 0:
                print(f"  Checked {lines_checked:,} lines... Found {total_critical} critical items")

            line_lower = line.lower()

            # First check for China
            if china_pattern.search(line_lower):
                # Then check for defense patterns
                for category, pattern in compiled_defense.items():
                    if pattern.search(line_lower):
                        total_critical += 1
                        category_counts[category] += 1

                        if len(critical_findings) < 100:  # Save first 100
                            critical_findings.append({
                                'line': line_num,
                                'category': category,
                                'text': line[:500]
                            })

                        break  # Found critical match

            if lines_checked >= max_lines:
                break

    # Results
    print("\n" + "=" * 80)
    print("CRITICAL FINDINGS")
    print("=" * 80)

    print(f"\nTotal China-Defense connections found: {total_critical:,}")

    if total_critical > 0:
        print("\nBREAKDOWN BY CATEGORY:")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"  {category}: {count:,}")

        # Extrapolate to full file
        extrapolated = int(total_critical * (98463609 / lines_checked))
        print(f"\nESTIMATED TOTAL in full file: {extrapolated:,} critical China-Defense connections")

        # Show samples
        print("\nSAMPLE CRITICAL FINDINGS:")
        print("-" * 40)
        for i, finding in enumerate(critical_findings[:10], 1):
            print(f"\n[{i}] Category: {finding['category']}")
            print(f"    Line: {finding['line']}")
            print(f"    Text: {finding['text'][:200]}...")

        # Save results
        output = {
            'summary': {
                'total_critical': total_critical,
                'lines_checked': lines_checked,
                'extrapolated_total': extrapolated
            },
            'categories': category_counts,
            'samples': critical_findings
        }

        with open('critical_china_defense.json', 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\nResults saved to: critical_china_defense.json")

        if extrapolated > 100000:
            print("\n" + "!" * 80)
            print("!!! ALERT: OVER 100,000 CHINA-DEFENSE CONNECTIONS ESTIMATED !!!")
            print("!" * 80)

    print(f"\nEnd: {datetime.now()}")

if __name__ == "__main__":
    search_critical_defense()
