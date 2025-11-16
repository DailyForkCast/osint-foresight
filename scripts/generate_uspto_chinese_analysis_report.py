#!/usr/bin/env python3
"""
Generate Comprehensive USPTO Chinese Patent Analysis Report
Based on 425,074 Chinese patents detected from 2011-2020
"""

import sqlite3
import json
from datetime import datetime
from collections import Counter, defaultdict

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = "C:/Projects/OSINT - Foresight/analysis"

def query_database(query):
    """Execute query and return results"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def generate_report():
    """Generate comprehensive analysis report"""

    print("="*80)
    print("GENERATING USPTO CHINESE PATENT COMPREHENSIVE ANALYSIS REPORT")
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
        "confidence_analysis": {},
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

    # 6. STRATEGIC FINDINGS
    print("\n6. Generating strategic findings...")

    # Check for CPC classifications if available
    cpc_available = query_database("""
        SELECT COUNT(*)
        FROM sqlite_master
        WHERE type='table' AND name='uspto_cpc_classifications'
    """)[0][0] > 0

    if cpc_available:
        # Use simple JOIN on application_number only (most patents have this)
        strategic_techs = query_database("""
            SELECT c.technology_area, COUNT(DISTINCT p.application_number) as patent_count
            FROM uspto_patents_chinese p
            JOIN uspto_cpc_classifications c ON p.application_number = c.application_number
            WHERE c.is_strategic = 1
            GROUP BY c.technology_area
            ORDER BY patent_count DESC
        """)

        report['strategic_findings']['dual_use_technologies'] = {
            tech: count for tech, count in strategic_techs
        }

        print(f"   Dual-use/Strategic technology areas:")
        for tech, count in strategic_techs[:10]:
            print(f"     {tech:30s}: {count:,} patents")
    else:
        print(f"   CPC classifications pending (background processing)")
        report['strategic_findings']['dual_use_technologies'] = "Processing in background"

    # High-confidence entities for priority review
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

    # Generate human-readable markdown version
    generate_markdown_report(report)

    return report

def generate_markdown_report(report):
    """Generate markdown version of report"""

    output_file = f"{OUTPUT_DIR}/USPTO_CHINESE_PATENT_ANALYSIS_REPORT.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# USPTO Chinese Patent Analysis Report (2011-2020)\n\n")
        f.write(f"**Generated**: {report['generated_date']}  \n")
        f.write(f"**Data Source**: {report['data_source']}  \n")
        f.write(f"**Methodology**: {report['methodology']}  \n\n")

        f.write("---\n\n")
        f.write("## Executive Summary\n\n")

        summary = report['summary']
        f.write(f"- **Total Chinese Patents Identified**: {summary['total_chinese_patents']:,}\n")
        f.write(f"- **Analysis Period**: {summary['data_period']}\n\n")

        f.write("### Confidence Distribution\n\n")
        f.write("| Confidence Level | Count | Percentage |\n")
        f.write("|-----------------|-------|------------|\n")
        for conf, count in summary['confidence_distribution'].items():
            pct = (count / summary['total_chinese_patents']) * 100
            f.write(f"| {conf} | {count:,} | {pct:.1f}% |\n")

        f.write("\n---\n\n")
        f.write("## Key Insights\n\n")
        for insight in report['key_insights']:
            f.write(f"- {insight}\n")

        f.write("\n---\n\n")
        f.write("## Temporal Analysis\n\n")
        f.write("### Patents by Year\n\n")
        f.write("| Year | Patent Count |\n")
        f.write("|------|-------------|\n")
        for year, count in sorted(report['temporal_analysis']['patents_by_year'].items()):
            f.write(f"| {year} | {count:,} |\n")

        growth = report['temporal_analysis'].get('growth_rate_2011_2020', 'N/A')
        f.write(f"\n**Growth Rate (2011-2020)**: {growth}\n")

        f.write("\n---\n\n")
        f.write("## Geographic Analysis\n\n")
        f.write("### Top 20 Cities\n\n")
        f.write("| Rank | City | Patent Count |\n")
        f.write("|------|------|-------------|\n")
        for rank, (city, count) in enumerate(report['geographic_analysis']['top_cities'].items(), 1):
            f.write(f"| {rank} | {city} | {count:,} |\n")

        f.write("\n---\n\n")
        f.write("## Entity Analysis\n\n")
        f.write("### Top 50 Chinese Assignees\n\n")
        f.write("| Rank | Assignee Name | Patent Count |\n")
        f.write("|------|---------------|-------------|\n")
        for rank, entity in enumerate(report['entity_analysis']['top_50_assignees'], 1):
            f.write(f"| {rank} | {entity['name'][:60]} | {entity['patent_count']:,} |\n")

        f.write("\n---\n\n")
        f.write("## Detection Signal Analysis\n\n")
        f.write("| Signal Type | Frequency |\n")
        f.write("|-------------|----------|\n")
        for signal, count in list(report['signal_analysis']['signal_frequency'].items())[:15]:
            f.write(f"| {signal} | {count:,} |\n")

        f.write("\n---\n\n")
        f.write("## Strategic Findings\n\n")

        if isinstance(report['strategic_findings']['dual_use_technologies'], dict):
            f.write("### Dual-Use/Strategic Technology Areas\n\n")
            f.write("| Technology Area | Chinese Patent Count |\n")
            f.write("|----------------|---------------------|\n")
            for tech, count in list(report['strategic_findings']['dual_use_technologies'].items())[:15]:
                f.write(f"| {tech} | {count:,} |\n")
        else:
            f.write(f"**Dual-Use Technologies**: {report['strategic_findings']['dual_use_technologies']}\n\n")

        f.write("\n### High-Confidence Entities (Priority Review)\n\n")
        f.write("| Rank | Entity | VERY_HIGH Confidence Patents |\n")
        f.write("|------|--------|-----------------------------|\n")
        for rank, entity in enumerate(report['strategic_findings']['high_confidence_entities'][:20], 1):
            f.write(f"| {rank} | {entity['name'][:50]} | {entity['patent_count']:,} |\n")

        f.write("\n---\n\n")
        f.write("## Methodology\n\n")
        f.write("### Multi-Signal Detection System\n\n")
        f.write("10-tier weighted scoring:\n\n")
        f.write("1. **Country codes** (100 pts): CN, CHN, HK, MO\n")
        f.write("2. **Known Chinese companies** (80 pts): Huawei, Tencent, Alibaba, etc.\n")
        f.write("3. **Postal codes** (60 pts): 6-digit Chinese format\n")
        f.write("4. **Cities** (50 pts): 43 major Chinese cities\n")
        f.write("5. **Provinces** (40 pts): 27 provinces/regions\n")
        f.write("6. **Districts** (25 pts): Major tech hub districts\n")
        f.write("7. **Street patterns** (15 pts): Chinese naming conventions\n")
        f.write("8. **Phone numbers** (50 pts): Chinese phone formats\n")
        f.write("9. **Inventors** (20 pts each): Chinese inventor names\n")
        f.write("10. **Address patterns**: Multi-field geographic matching\n\n")

        f.write("**Confidence Levels**:\n")
        f.write("- VERY_HIGH: ≥100 points\n")
        f.write("- HIGH: 70-99 points\n")
        f.write("- MEDIUM: 50-69 points\n")
        f.write("- LOW: <50 points (excluded)\n\n")

    print(f"MARKDOWN REPORT: {output_file}")

if __name__ == '__main__':
    report = generate_report()
