#!/usr/bin/env python3
"""
Analyze USPTO CPC Strategic Technologies for Chinese Patents
Optimized separate query to avoid slow JOINs
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict, Counter

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = "C:/Projects/OSINT - Foresight/analysis"

def main():
    print("="*80)
    print("USPTO CPC STRATEGIC TECHNOLOGIES ANALYSIS - CHINESE PATENTS")
    print("="*80)

    conn = sqlite3.connect(DB_PATH, timeout=300)
    cursor = conn.cursor()

    # Step 1: Get all Chinese patent application numbers
    print("\n1. Loading Chinese patent application numbers...")
    cursor.execute("""
        SELECT DISTINCT application_number
        FROM uspto_patents_chinese
        WHERE application_number IS NOT NULL
    """)
    chinese_app_numbers = set(row[0] for row in cursor.fetchall())
    print(f"   Found {len(chinese_app_numbers):,} unique Chinese patent application numbers")

    # Step 2: Get strategic CPC classifications and check if they match Chinese patents
    print("\n2. Analyzing strategic CPC classifications...")
    cursor.execute("""
        SELECT
            application_number,
            technology_area,
            cpc_full
        FROM uspto_cpc_classifications
        WHERE is_strategic = 1
            AND application_number IS NOT NULL
    """)

    strategic_tech_counts = Counter()
    strategic_tech_patents = defaultdict(set)
    chinese_strategic_count = 0

    processed = 0
    for app_num, tech_area, cpc_full in cursor:
        processed += 1
        if processed % 100000 == 0:
            print(f"   Processed {processed:,} strategic classifications | Chinese matches: {chinese_strategic_count:,}")

        if app_num in chinese_app_numbers:
            strategic_tech_counts[tech_area] += 1
            strategic_tech_patents[tech_area].add(app_num)
            chinese_strategic_count += 1

    print(f"\n   Total strategic classifications processed: {processed:,}")
    print(f"   Chinese patent strategic matches: {chinese_strategic_count:,}")

    # Step 3: Generate report
    print("\n3. Generating strategic technology report...")

    report = {
        'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_chinese_patents': len(chinese_app_numbers),
        'strategic_classifications_found': chinese_strategic_count,
        'technologies': {}
    }

    # Sort by patent count
    sorted_techs = sorted(strategic_tech_counts.items(), key=lambda x: x[1], reverse=True)

    print("\n" + "="*80)
    print("STRATEGIC TECHNOLOGY AREAS - CHINESE PATENTS")
    print("="*80)
    print(f"\n{'Technology Area':<40} {'Patents':<10} {'% of Chinese':<12}")
    print("-"*80)

    for tech_area, count in sorted_techs[:20]:
        unique_patents = len(strategic_tech_patents[tech_area])
        pct = (unique_patents / len(chinese_app_numbers)) * 100
        print(f"{tech_area:<40} {unique_patents:<10,} {pct:<12.2f}%")

        report['technologies'][tech_area] = {
            'patent_count': unique_patents,
            'percentage': round(pct, 2)
        }

    # Save report
    output_file = f"{OUTPUT_DIR}/USPTO_CPC_STRATEGIC_TECHNOLOGIES_CHINESE.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "="*80)
    print(f"REPORT SAVED: {output_file}")
    print("="*80)

    # Step 4: Generate summary statistics
    print("\n4. Summary Statistics:")
    print(f"   Total Chinese patents: {len(chinese_app_numbers):,}")
    print(f"   Patents with strategic tech: {len(set.union(*strategic_tech_patents.values())):,}")
    pct_strategic = (len(set.union(*strategic_tech_patents.values())) / len(chinese_app_numbers)) * 100
    print(f"   Percentage with strategic tech: {pct_strategic:.1f}%")

    print("\n   Top 10 Strategic Technology Areas:")
    for i, (tech_area, count) in enumerate(sorted_techs[:10], 1):
        unique_patents = len(strategic_tech_patents[tech_area])
        print(f"   {i:2d}. {tech_area:<35s}: {unique_patents:>6,} patents")

    conn.close()
    print("\nAnalysis complete!")

if __name__ == '__main__':
    main()
