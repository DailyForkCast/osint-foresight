#!/usr/bin/env python3
"""
Temporal Analysis of EU-China Academic Collaborations
Analyzes publication trends to measure impact of diplomatic restrictions
"""

import sqlite3
import sys
import io
import json
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

conn = sqlite3.connect(str(DB_PATH))
cur = conn.cursor()

print("="*80)
print("TEMPORAL ANALYSIS: EU-CHINA ACADEMIC COLLABORATIONS")
print("="*80 + "\n")

# Key diplomatic events timeline (from bilateral framework)
diplomatic_events = {
    2015: "UK Golden Era begins",
    2016: "Czech Republic Taiwan visit preparation",
    2017: "BRI expansion peak",
    2018: "US-China trade war begins",
    2019: "Huawei 5G restrictions start",
    2020: "UK Huawei ban, Czech Taiwan visit, COVID-19",
    2021: "Lithuania Taiwan office crisis",
    2022: "Ukraine war, EU-China tensions peak",
    2023: "Technology export controls expand",
    2024: "Continued decoupling rhetoric"
}

# Overall trend analysis
print("="*80)
print("OVERALL COLLABORATION TREND BY YEAR")
print("="*80 + "\n")

cur.execute("""
    SELECT publication_year, COUNT(*) as works
    FROM openalex_works
    WHERE publication_year IS NOT NULL
      AND publication_year >= 2000
      AND publication_year <= 2024
    GROUP BY publication_year
    ORDER BY publication_year DESC
""")

yearly_trends = cur.fetchall()

if yearly_trends:
    print(f"{'Year':<8} {'Works':<10} {'Change':<12} {'Diplomatic Context'}")
    print("-" * 90)

    prev_count = None
    for i, (year, count) in enumerate(yearly_trends):
        if prev_count:
            change = count - prev_count
            pct = ((count - prev_count) / prev_count * 100)
            change_str = f"{change:+,} ({pct:+.1f}%)"
        else:
            change_str = "—"

        context = diplomatic_events.get(year, "")
        print(f"{year:<8} {count:<10,} {change_str:<12} {context}")
        prev_count = count

    print("\n✓ Total works analyzed:", sum(count for _, count in yearly_trends))
else:
    print("⚠ No publication year data available")

# Identify inflection points
print("\n" + "="*80)
print("INFLECTION POINT ANALYSIS")
print("="*80 + "\n")

if len(yearly_trends) > 1:
    # Find years with significant changes
    changes = []
    for i in range(len(yearly_trends)-1):
        year1, count1 = yearly_trends[i]
        year2, count2 = yearly_trends[i+1]
        if count2 > 0:
            pct_change = ((count1 - count2) / count2 * 100)
            changes.append((year1, pct_change, count1, count2))

    # Show largest changes
    changes_sorted = sorted(changes, key=lambda x: abs(x[1]), reverse=True)[:10]

    print("Top 10 Largest Year-to-Year Changes:\n")
    print(f"{'Year':<8} {'Change':<12} {'From':<10} {'To':<10} {'Possible Cause'}")
    print("-" * 90)

    for year, pct, from_count, to_count in changes_sorted:
        context = diplomatic_events.get(year, "")
        print(f"{year:<8} {pct:+.1f}%{'':<7} {to_count:<10,} {from_count:<10,} {context}")

# Country-level analysis using existing aggregated data
print("\n" + "="*80)
print("COUNTRY-LEVEL COLLABORATION (From OpenAlex Entities)")
print("="*80 + "\n")

focus_countries = {
    'LT': 'Lithuania (Taiwan office 2021)',
    'CZ': 'Czech Republic (Taiwan visit 2020)',
    'GB': 'United Kingdom (Huawei ban 2020)',
    'PL': 'Poland (5G restrictions 2019)',
    'SE': 'Sweden (5G restrictions 2020)',
    'EE': 'Estonia (China-critical 2022)',
    'LV': 'Latvia (China-critical 2022)'
}

print("Current collaboration levels for high-tension countries:\n")
print(f"{'Country':<35} {'Institutions':<12} {'Total Works':<15}")
print("-" * 65)

for cc, description in focus_countries.items():
    cur.execute("""
        SELECT COUNT(*) as institutions,
               SUM(works_count) as total_works
        FROM openalex_entities
        WHERE country_code = ? AND entity_type = 'institution'
    """, (cc,))

    stats = cur.fetchone()
    if stats and stats[1]:
        print(f"{description:<35} {stats[0]:<12,} {stats[1]:<15,}")
    else:
        print(f"{description:<35} {'N/A':<12} {'N/A':<15}")

print("\n⚠️  Note: Year-by-year country breakdowns would require institution-work")
print("    linking table. Current data shows aggregated totals only.")

# Technology domain trends
print("\n" + "="*80)
print("TECHNOLOGY DOMAIN TRENDS (Strategic Areas)")
print("="*80 + "\n")

strategic_domains = [
    'artificial_intelligence',
    'semiconductors',
    'quantum_computing',
    'advanced_materials',
    'biotechnology',
    'aerospace',
    'energy_storage',
    'telecommunications'
]

for domain in strategic_domains:
    cur.execute("""
        SELECT publication_year, COUNT(*) as works
        FROM openalex_works
        WHERE technology_domain = ?
          AND publication_year >= 2015
          AND publication_year <= 2024
        GROUP BY publication_year
        ORDER BY publication_year DESC
    """, (domain,))

    domain_trends = cur.fetchall()

    if domain_trends and len(domain_trends) > 2:
        print(f"\n{domain.replace('_', ' ').title()}:")

        total = sum(count for _, count in domain_trends)
        peak_year = max(domain_trends, key=lambda x: x[1])
        recent_year = domain_trends[0]

        print(f"  Total works (2015-2024): {total:,}")
        print(f"  Peak: {peak_year[0]} ({peak_year[1]:,} works)")
        print(f"  Most recent: {recent_year[0]} ({recent_year[1]:,} works)")

        # Check if declining from peak
        if peak_year[0] < recent_year[0]:
            decline = ((recent_year[1] - peak_year[1]) / peak_year[1] * 100)
            if decline < -10:
                print(f"  ⚠️ DECLINING: {decline:.1f}% from peak")
            elif decline > 10:
                print(f"  ✅ GROWING: {decline:+.1f}% from peak")

# Pre/Post 2020 comparison (COVID + restrictions inflection point)
print("\n" + "="*80)
print("PRE/POST 2020 COMPARISON (Major Inflection Point)")
print("="*80 + "\n")

cur.execute("""
    SELECT
        CASE
            WHEN publication_year < 2020 THEN 'Pre-2020'
            ELSE 'Post-2020'
        END as period,
        COUNT(*) as works
    FROM openalex_works
    WHERE publication_year >= 2015
      AND publication_year <= 2024
    GROUP BY period
""")

period_comparison = dict(cur.fetchall())

if 'Pre-2020' in period_comparison and 'Post-2020' in period_comparison:
    pre = period_comparison['Pre-2020']
    post = period_comparison['Post-2020']

    # Normalize by number of years
    pre_avg = pre / 5  # 2015-2019
    post_avg = post / 5  # 2020-2024

    change = ((post_avg - pre_avg) / pre_avg * 100)

    print(f"Pre-2020 (2015-2019):")
    print(f"  Total works: {pre:,}")
    print(f"  Average per year: {pre_avg:,.0f}")
    print()
    print(f"Post-2020 (2020-2024):")
    print(f"  Total works: {post:,}")
    print(f"  Average per year: {post_avg:,.0f}")
    print()
    print(f"Change: {change:+.1f}% average annual works")
    print()

    if change < -5:
        print("📊 FINDING: Significant decline in collaboration post-2020")
        print("   Suggests diplomatic restrictions + COVID having measurable impact")
    elif change > 5:
        print("📊 FINDING: Collaboration continues to grow despite restrictions")
        print("   Suggests diplomatic tensions not affecting research collaboration")
    else:
        print("📊 FINDING: Collaboration relatively stable")
        print("   Suggests restrictions having limited immediate impact")

# Baltic states collective analysis
print("\n" + "="*80)
print("BALTIC STATES COLLECTIVE ANALYSIS (LT, EE, LV)")
print("="*80 + "\n")

baltic_countries = ['LT', 'EE', 'LV']

for cc in baltic_countries:
    cur.execute("""
        SELECT COUNT(*) as institutions,
               SUM(works_count) as total_works
        FROM openalex_entities
        WHERE country_code = ? AND entity_type = 'institution'
    """, (cc,))

    stats = cur.fetchone()
    if stats and stats[1]:
        print(f"{cc}: {stats[0]:,} institutions, {stats[1]:,} works")

print("\nBaltic states are collectively most China-critical in EU:")
print("  - Lithuania: Taiwan representative office (2021)")
print("  - Estonia: Banned China telecom companies (2022)")
print("  - Latvia: Growing China skepticism (2022-2024)")
print("\nTemporal analysis needed to measure if rhetoric matches research behavior")

# Generate summary report
print("\n" + "="*80)
print("KEY FINDINGS - ACADEMIC COLLABORATION TIMELINE")
print("="*80 + "\n")

summary = {
    'analysis_date': '2025-10-23',
    'key_findings': [],
    'temporal_patterns': {},
    'country_impacts': {},
    'domain_impacts': {}
}

# Save this analysis
output_path = Path('analysis/academic_collaboration_timeline.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump({
        'yearly_trends': yearly_trends,
        'diplomatic_events': diplomatic_events,
        'period_comparison': period_comparison
    }, f, indent=2, ensure_ascii=False)

print("✓ Temporal analysis complete")
print(f"✓ Results saved to: {output_path}")
print("\nNext steps:")
print("  1. Integrate temporal trends with bilateral_events timeline")
print("  2. Create visualization of collaboration vs. diplomatic tension")
print("  3. Deep dive on Lithuania/Czech/Poland post-restriction patterns")
print("  4. Analyze specific institutions with defense/security concerns")

conn.close()
