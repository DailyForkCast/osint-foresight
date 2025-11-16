#!/usr/bin/env python3
"""
Generate Comprehensive USPTO Chinese Patent Analysis Report (Simplified - No CPC JOIN)
Based on 425,074 Chinese patents detected from 2011-2020
"""

import sqlite3
import json
from datetime import datetime
from collections import Counter

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = "C:/Projects/OSINT - Foresight/analysis"

def query_database(query):
    """Execute query and return results"""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def generate_report():
    """Generate comprehensive analysis report"""

    print("="*80)
    print("USPTO CHINESE PATENT COMPREHENSIVE ANALYSIS REPORT")
    print("="*80)

    report = {
        "generated_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "data_source": "USPTO Patent Filewrapper 2011-2020",
        "methodology": "Multi-signal Chinese entity detection with 10-tier scoring",
        "detection_threshold": "50 points minimum",
        "summary": {},
        "temporal_analysis": {},
        "geographic_analysis": {},
        "entity_analysis": {},
        "signal_analysis": {},
        "strategic_findings": {}
    }

    # 1. SUMMARY STATISTICS
    print("\n1. Calculating summary statistics...")

    total_patents = query_database("SELECT COUNT(*) FROM uspto_patents_chinese")[0][0]

    confidence_dist = query_database("""
        SELECT confidence, COUNT(*) as count
        FROM uspto_patents_chinese
        GROUP BY confidence
        ORDER BY
            CASE confidence
                WHEN 'VERY_HIGH' THEN 1
                WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3
                ELSE 4
            END
    """)

    report['summary'] = {
        'total_chinese_patents': total_patents,
        'data_period': '2011-2020',
        'confidence_distribution': {conf: count for conf, count in confidence_dist}
    }

    print(f"   Total Chinese patents: {total_patents:,}")
    print(f"   Confidence breakdown:")
    for conf, count in confidence_dist:
        pct = (count / total_patents) * 100
        print(f"     {conf:12s}: {count:,} ({pct:.1f}%)")

    # 2. TEMPORAL ANALYSIS
    print("\n2. Analyzing temporal trends...")

    yearly_counts = query_database("""
        SELECT year, COUNT(*) as count
        FROM uspto_patents_chinese
        WHERE year IS NOT NULL
        GROUP BY year
        ORDER BY year
    """)

    yearly_confidence = {}
    for year in range(2011, 2021):
        year_conf = query_database(f"""
            SELECT confidence, COUNT(*) as count
            FROM uspto_patents_chinese
            WHERE year = {year}
            GROUP BY confidence
        """)
        yearly_confidence[year] = {conf: count for conf, count in year_conf}

    report['temporal_analysis'] = {
        'patents_by_year': {year: count for year, count in yearly_counts},
        'confidence_by_year': yearly_confidence
    }

    # Calculate growth rate
    first_year_count = yearly_counts[0][1] if yearly_counts else 0
    last_year_count = yearly_counts[-1][1] if yearly_counts else 0

    if first_year_count > 0:
        growth_rate = ((last_year_count - first_year_count) / first_year_count) * 100
        report['temporal_analysis']['growth_rate_2011_2020'] = f"{growth_rate:.1f}%"

    print(f"   Growth 2011-2020: {growth_rate:.1f}%")
    print(f"   Peak year: {max(yearly_counts, key=lambda x: x[1])[0]} ({max(yearly_counts, key=lambda x: x[1])[1]:,} patents)")

    # 3. GEOGRAPHIC ANALYSIS
    print("\n3. Analyzing geographic distribution...")

    top_cities = query_database("""
        SELECT assignee_city, COUNT(*) as count
        FROM uspto_patents_chinese
        WHERE assignee_city IS NOT NULL AND assignee_city != ''
        GROUP BY assignee_city
        ORDER BY count DESC
        LIMIT 20
    """)

    top_countries = query_database("""
        SELECT assignee_country, COUNT(*) as count
        FROM uspto_patents_chinese
        WHERE assignee_country IS NOT NULL AND assignee_country != ''
        GROUP BY assignee_country
        ORDER BY count DESC
    """)

    report['geographic_analysis'] = {
        'top_cities': {city: count for city, count in top_cities},
        'countries': {country: count for country, count in top_countries}
    }

    print(f"   Top 5 cities:")
    for city, count in top_cities[:5]:
        print(f"     {city:20s}: {count:,}")

    # 4. ENTITY ANALYSIS
    print("\n4. Analyzing top Chinese entities...")

    top_assignees = query_database("""
        SELECT assignee_name, COUNT(*) as patent_count
        FROM uspto_patents_chinese
        WHERE assignee_name IS NOT NULL AND assignee_name != ''
        GROUP BY assignee_name
        ORDER BY patent_count DESC
        LIMIT 50
    """)

    report['entity_analysis'] = {
        'top_50_assignees': [
            {'name': name, 'patent_count': count}
            for name, count in top_assignees
        ]
    }

    print(f"   Top 10 assignees:")
    for name, count in top_assignees[:10]:
        print(f"     {name[:40]:40s}: {count:,}")

    # 5. DETECTION SIGNAL ANALYSIS
    print("\n5. Analyzing detection signals...")

    all_signals = query_database("""
        SELECT detection_signals
        FROM uspto_patents_chinese
        WHERE detection_signals IS NOT NULL
    """)

    signal_counter = Counter()
    for (signals_str,) in all_signals:
        for signal in signals_str.split(','):
            signal_type = signal.split('_')[0] if '_' in signal else signal
            signal_counter[signal_type] += 1

    report['signal_analysis'] = {
        'signal_frequency': dict(signal_counter.most_common(15)),
        'total_unique_signals': len(signal_counter)
    }

    print(f"   Top detection signals:")
    for signal, count in signal_counter.most_common(10):
        print(f"     {signal:15s}: {count:,}")

    # 6. STRATEGIC FINDINGS (skip CPC for now)
    print("\n6. Generating strategic findings...")

    high_conf_assignees = query_database("""
        SELECT assignee_name, COUNT(*) as count
        FROM uspto_patents_chinese
        WHERE confidence = 'VERY_HIGH'
            AND assignee_name IS NOT NULL
            AND assignee_name != ''
        GROUP BY assignee_name
        ORDER BY count DESC
        LIMIT 30
    """)

    report['strategic_findings']['high_confidence_entities'] = [
        {'name': name, 'patent_count': count}
        for name, count in high_conf_assignees
    ]

    print(f"   Identified {len(high_conf_assignees)} high-confidence entities for priority review")

    # 7. KEY INSIGHTS
    print("\n7. Generating key insights...")

    report['key_insights'] = [
        f"Identified {total_patents:,} Chinese patents in USPTO (2011-2020)",
        f"{confidence_dist[0][1]:,} patents ({(confidence_dist[0][1]/total_patents)*100:.1f}%) classified as VERY_HIGH confidence",
        f"Growth rate of {growth_rate:.1f}% from 2011 to 2020",
        f"Top assignee: {top_assignees[0][0]} with {top_assignees[0][1]:,} patents",
        f"Geographic concentration: {top_cities[0][0]} leads with {top_cities[0][1]:,} patents ({(top_cities[0][1]/total_patents)*100:.1f}% of total)"
    ]

    # Save report
    output_file = f"{OUTPUT_DIR}/USPTO_CHINESE_PATENT_ANALYSIS_REPORT.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"REPORT GENERATED: {output_file}")
    print(f"{'='*80}")

    return report

if __name__ == '__main__':
    generate_report()
    print("\nReport generation complete!")
