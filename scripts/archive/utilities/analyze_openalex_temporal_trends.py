#!/usr/bin/env python3
"""
Comprehensive Temporal Trends Analysis
OpenAlex Chinese Technology Research 2011-2025
"""

import sqlite3
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

db_path = Path("F:/OSINT_Data/openalex_analytics/openalex_chinese_research.db")

print("="*80)
print("TEMPORAL TRENDS ANALYSIS")
print("Chinese Technology Research Publications 2011-2025")
print("="*80)
print()

if not db_path.exists():
    print(f"[ERROR] Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)

# ============================================================================
# 1. OVERALL PUBLICATION TRENDS
# ============================================================================

print("[1] OVERALL PUBLICATION TRENDS")
print("-"*80)

query = """
SELECT
    publication_year,
    COUNT(*) as total_papers,
    SUM(CASE WHEN collaboration_type = 'International' THEN 1 ELSE 0 END) as international_papers,
    ROUND(SUM(CASE WHEN collaboration_type = 'International' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as intl_pct,
    AVG(cited_by_count) as avg_citations
FROM research_papers_expanded
GROUP BY publication_year
ORDER BY publication_year
"""

df_yearly = pd.read_sql_query(query, conn)

print(f"\n{'Year':<6} {'Papers':>8} {'YoY Growth':>12} {'Intl %':>10} {'Avg Cites':>12}")
print("-"*60)

for i, row in df_yearly.iterrows():
    year = int(row['publication_year'])
    papers = int(row['total_papers'])
    intl_pct = row['intl_pct']
    avg_cites = row['avg_citations']

    # Calculate YoY growth
    if i > 0:
        prev_papers = int(df_yearly.iloc[i-1]['total_papers'])
        yoy_growth = ((papers - prev_papers) / prev_papers * 100)
        growth_str = f"+{yoy_growth:.1f}%" if yoy_growth > 0 else f"{yoy_growth:.1f}%"
    else:
        growth_str = "baseline"

    print(f"{year:<6} {papers:>8,} {growth_str:>12} {intl_pct:>9.1f}% {avg_cites:>12.1f}")

# Overall growth statistics
first_year_papers = int(df_yearly.iloc[0]['total_papers'])
last_year_papers = int(df_yearly.iloc[-2]['total_papers'])  # Exclude 2025 (partial)
total_growth = ((last_year_papers - first_year_papers) / first_year_papers * 100)
years_span = 2024 - 2011
cagr = ((last_year_papers / first_year_papers) ** (1/years_span) - 1) * 100

print()
print(f"Overall Growth (2011-2024): +{total_growth:.1f}%")
print(f"CAGR: {cagr:.1f}%")
print()

# ============================================================================
# 2. PRE/POST MIC2025 COMPARISON
# ============================================================================

print("[2] PRE/POST MIC2025 COMPARISON")
print("-"*80)

query = """
SELECT
    CASE
        WHEN publication_year <= 2015 THEN 'Pre-MIC2025 (2011-2015)'
        WHEN publication_year BETWEEN 2016 AND 2020 THEN 'MIC2025 Era (2016-2020)'
        ELSE 'Post-Acceleration (2021-2025)'
    END as period,
    COUNT(*) as total_papers,
    AVG(cited_by_count) as avg_citations,
    SUM(CASE WHEN collaboration_type = 'International' THEN 1 ELSE 0 END) as international_papers,
    ROUND(SUM(CASE WHEN collaboration_type = 'International' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as intl_pct
FROM research_papers_expanded
GROUP BY period
ORDER BY
    CASE
        WHEN period = 'Pre-MIC2025 (2011-2015)' THEN 1
        WHEN period = 'MIC2025 Era (2016-2020)' THEN 2
        ELSE 3
    END
"""

df_periods = pd.read_sql_query(query, conn)

print()
for _, row in df_periods.iterrows():
    period = row['period']
    papers = int(row['total_papers'])
    avg_cites = row['avg_citations']
    intl_pct = row['intl_pct']

    print(f"{period}:")
    print(f"  Total papers: {papers:,}")
    print(f"  Average citations: {avg_cites:.1f}")
    print(f"  International collaboration: {intl_pct:.1f}%")
    print()

# Calculate growth between periods
pre_mic = int(df_periods.iloc[0]['total_papers'])
mic_era = int(df_periods.iloc[1]['total_papers'])
post_accel = int(df_periods.iloc[2]['total_papers'])

growth_pre_to_mic = ((mic_era - pre_mic) / pre_mic * 100)
growth_mic_to_post = ((post_accel - mic_era) / mic_era * 100)

print(f"Growth Pre-MIC2025 to MIC2025 Era: +{growth_pre_to_mic:.1f}%")
print(f"Growth MIC2025 Era to Post-Acceleration: +{growth_mic_to_post:.1f}%")
print()

# ============================================================================
# 3. TOPIC-SPECIFIC TRENDS
# ============================================================================

print("[3] TOPIC-SPECIFIC GROWTH TRENDS")
print("-"*80)

query = """
SELECT
    technology_category,
    publication_year,
    COUNT(*) as papers,
    AVG(cited_by_count) as avg_citations
FROM research_papers_expanded
GROUP BY technology_category, publication_year
ORDER BY technology_category, publication_year
"""

df_topic_yearly = pd.read_sql_query(query, conn)

# Calculate growth for each topic (2011 baseline to 2024)
topic_growth = {}

for topic in df_topic_yearly['technology_category'].unique():
    topic_data = df_topic_yearly[df_topic_yearly['technology_category'] == topic]

    # Get 2011 and 2024 papers
    papers_2011 = topic_data[topic_data['publication_year'] == 2011]['papers'].values
    papers_2024 = topic_data[topic_data['publication_year'] == 2024]['papers'].values

    if len(papers_2011) > 0 and len(papers_2024) > 0:
        growth = ((papers_2024[0] - papers_2011[0]) / papers_2011[0] * 100)
        topic_growth[topic] = {
            'papers_2011': int(papers_2011[0]),
            'papers_2024': int(papers_2024[0]),
            'growth_pct': growth
        }

# Sort by growth rate
sorted_topics = sorted(topic_growth.items(), key=lambda x: x[1]['growth_pct'], reverse=True)

print()
print(f"{'Topic':<30} {'2011':>8} {'2024':>8} {'Growth':>12}")
print("-"*65)

for topic, data in sorted_topics:
    print(f"{topic:<30} {data['papers_2011']:>8,} {data['papers_2024']:>8,} {data['growth_pct']:>11.1f}%")

print()

# ============================================================================
# 4. RECENT ACCELERATION (2020-2024)
# ============================================================================

print("[4] RECENT ACCELERATION (2020-2024)")
print("-"*80)

query = """
SELECT
    technology_category,
    SUM(CASE WHEN publication_year = 2020 THEN 1 ELSE 0 END) as papers_2020,
    SUM(CASE WHEN publication_year = 2024 THEN 1 ELSE 0 END) as papers_2024
FROM research_papers_expanded
WHERE publication_year IN (2020, 2024)
GROUP BY technology_category
"""

df_recent = pd.read_sql_query(query, conn)
df_recent['growth_pct'] = ((df_recent['papers_2024'] - df_recent['papers_2020']) / df_recent['papers_2020'] * 100)
df_recent = df_recent.sort_values('growth_pct', ascending=False)

print()
print(f"{'Topic':<30} {'2020':>8} {'2024':>8} {'4-Yr Growth':>14}")
print("-"*70)

for _, row in df_recent.iterrows():
    topic = row['technology_category']
    papers_2020 = int(row['papers_2020'])
    papers_2024 = int(row['papers_2024'])
    growth = row['growth_pct']

    print(f"{topic:<30} {papers_2020:>8,} {papers_2024:>8,} {growth:>13.1f}%")

print()

# ============================================================================
# 5. INTERNATIONAL COLLABORATION EVOLUTION
# ============================================================================

print("[5] INTERNATIONAL COLLABORATION TRENDS")
print("-"*80)

query = """
SELECT
    publication_year,
    technology_category,
    COUNT(*) as total_papers,
    SUM(CASE WHEN collaboration_type = 'International' THEN 1 ELSE 0 END) as intl_papers,
    ROUND(SUM(CASE WHEN collaboration_type = 'International' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as intl_pct
FROM research_papers_expanded
GROUP BY publication_year, technology_category
ORDER BY publication_year, technology_category
"""

df_collab = pd.read_sql_query(query, conn)

# Calculate average international collaboration by period
collab_by_period = {}

for year in [2012, 2017, 2022, 2024]:
    year_data = df_collab[df_collab['publication_year'] == year]
    avg_intl_pct = year_data['intl_pct'].mean()
    collab_by_period[year] = avg_intl_pct

print()
print("Average International Collaboration Rate:")
print(f"  2012: {collab_by_period[2012]:.1f}%")
print(f"  2017: {collab_by_period[2017]:.1f}%")
print(f"  2022: {collab_by_period[2022]:.1f}%")
print(f"  2024: {collab_by_period[2024]:.1f}%")
print()

# Topic-specific collaboration rates
query = """
SELECT
    technology_category,
    ROUND(SUM(CASE WHEN collaboration_type = 'International' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as intl_pct
FROM research_papers_expanded
GROUP BY technology_category
ORDER BY intl_pct DESC
"""

df_topic_collab = pd.read_sql_query(query, conn)

print("International Collaboration by Topic (Overall):")
for _, row in df_topic_collab.iterrows():
    topic = row['technology_category']
    intl_pct = row['intl_pct']
    print(f"  {topic:<30} {intl_pct:>6.1f}%")

print()

# ============================================================================
# 6. SAVE RESULTS
# ============================================================================

print("[6] SAVING RESULTS")
print("-"*80)

results = {
    'analysis_date': datetime.now().isoformat(),
    'overall_trends': {
        'total_growth_2011_2024': float(total_growth),
        'cagr': float(cagr),
        'yearly_data': df_yearly.to_dict('records')
    },
    'period_comparison': {
        'pre_mic2025': {
            'papers': int(pre_mic),
            'period': '2011-2015'
        },
        'mic2025_era': {
            'papers': int(mic_era),
            'period': '2016-2020',
            'growth_from_pre': float(growth_pre_to_mic)
        },
        'post_acceleration': {
            'papers': int(post_accel),
            'period': '2021-2025',
            'growth_from_mic_era': float(growth_mic_to_post)
        }
    },
    'topic_growth': {topic: data for topic, data in sorted_topics},
    'recent_acceleration': df_recent.to_dict('records'),
    'collaboration_trends': {
        'by_period': collab_by_period,
        'by_topic': df_topic_collab.to_dict('records')
    }
}

output_file = Path("analysis/openalex_temporal_trends.json")
output_file.parent.mkdir(exist_ok=True)

with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n[OK] Results saved to: {output_file}")

# Save detailed yearly data to CSV
df_yearly.to_csv('analysis/openalex_yearly_trends.csv', index=False)
print(f"[OK] Yearly data saved to: analysis/openalex_yearly_trends.csv")

# Save topic-specific trends
df_topic_yearly.to_csv('analysis/openalex_topic_yearly_trends.csv', index=False)
print(f"[OK] Topic trends saved to: analysis/openalex_topic_yearly_trends.csv")

print()
print("="*80)
print("TEMPORAL TRENDS ANALYSIS COMPLETE")
print("="*80)
print()
print("Key Findings:")
print(f"  - Total growth 2011-2024: +{total_growth:.1f}%")
print(f"  - Compound annual growth rate: {cagr:.1f}%")
print(f"  - Fastest growing topic: {sorted_topics[0][0]} (+{sorted_topics[0][1]['growth_pct']:.1f}%)")
print(f"  - International collaboration trending: {collab_by_period[2024]:.1f}% (2024)")
print()

conn.close()
