#!/usr/bin/env python3
"""
International Collaboration Network Analysis
OpenAlex Chinese Technology Research
"""

import sqlite3
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
from collections import Counter
import re

db_path = Path("F:/OSINT_Data/openalex_analytics/openalex_chinese_research.db")

print("="*80)
print("INTERNATIONAL COLLABORATION NETWORK ANALYSIS")
print("="*80)
print()

if not db_path.exists():
    print(f"[ERROR] Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)

# ============================================================================
# 1. INTERNATIONAL COLLABORATION OVERVIEW
# ============================================================================

print("[1] INTERNATIONAL COLLABORATION OVERVIEW")
print("-"*80)

query = """
SELECT
    COUNT(*) as total_papers,
    SUM(CASE WHEN collaboration_type = 'International' THEN 1 ELSE 0 END) as intl_papers,
    ROUND(SUM(CASE WHEN collaboration_type = 'International' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as intl_pct,
    SUM(CASE WHEN collaboration_type = 'Domestic' THEN 1 ELSE 0 END) as domestic_papers
FROM research_papers_expanded
"""

df_overview = pd.read_sql_query(query, conn)

print()
print(f"Total papers: {int(df_overview['total_papers'].values[0]):,}")
print(f"International collaborations: {int(df_overview['intl_papers'].values[0]):,} ({df_overview['intl_pct'].values[0]:.1f}%)")
print(f"Domestic only: {int(df_overview['domestic_papers'].values[0]):,} ({100-df_overview['intl_pct'].values[0]:.1f}%)")
print()

# ============================================================================
# 2. TOP INTERNATIONAL PARTNER INSTITUTIONS
# ============================================================================

print("[2] TOP INTERNATIONAL PARTNER INSTITUTIONS")
print("-"*80)

# Get all international papers
query = """
SELECT
    international_institutions,
    technology_category,
    publication_year
FROM research_papers_expanded
WHERE collaboration_type = 'International'
    AND international_institutions IS NOT NULL
    AND international_institutions != ''
"""

df_intl = pd.read_sql_query(query, conn)

# Parse institution names
all_institutions = []
for institutions_str in df_intl['international_institutions'].values:
    if pd.notna(institutions_str) and institutions_str:
        # Split by semicolon
        institutions = [inst.strip() for inst in institutions_str.split(';') if inst.strip()]
        all_institutions.extend(institutions)

# Count occurrences
inst_counter = Counter(all_institutions)
top_institutions = inst_counter.most_common(50)

print()
print(f"Top 30 International Partner Institutions:")
print(f"{'Rank':<6} {'Institution':<55} {'Papers':>8}")
print("-"*75)

for i, (inst, count) in enumerate(top_institutions[:30], 1):
    print(f"{i:<6} {inst[:54]:<55} {count:>8,}")

print()

# ============================================================================
# 3. COLLABORATION BY TOPIC
# ============================================================================

print("[3] INTERNATIONAL COLLABORATION BY TECHNOLOGY TOPIC")
print("-"*80)

query = """
SELECT
    technology_category,
    COUNT(*) as total_papers,
    SUM(CASE WHEN collaboration_type = 'International' THEN 1 ELSE 0 END) as intl_papers,
    ROUND(SUM(CASE WHEN collaboration_type = 'International' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as intl_pct,
    AVG(CASE WHEN collaboration_type = 'International' THEN cited_by_count ELSE NULL END) as avg_intl_citations,
    AVG(CASE WHEN collaboration_type = 'Domestic' THEN cited_by_count ELSE NULL END) as avg_domestic_citations
FROM research_papers_expanded
GROUP BY technology_category
ORDER BY intl_pct DESC
"""

df_topic_collab = pd.read_sql_query(query, conn)

print()
print(f"{'Topic':<30} {'Intl %':>10} {'Intl Cites':>12} {'Dom. Cites':>12} {'Citation Boost':>15}")
print("-"*85)

for _, row in df_topic_collab.iterrows():
    topic = row['technology_category']
    intl_pct = row['intl_pct']
    intl_cites = row['avg_intl_citations'] if pd.notna(row['avg_intl_citations']) else 0
    dom_cites = row['avg_domestic_citations'] if pd.notna(row['avg_domestic_citations']) else 0

    if dom_cites > 0:
        citation_boost = ((intl_cites - dom_cites) / dom_cites * 100)
        boost_str = f"+{citation_boost:.1f}%"
    else:
        boost_str = "N/A"

    print(f"{topic:<30} {intl_pct:>9.1f}% {intl_cites:>12.1f} {dom_cites:>12.1f} {boost_str:>15}")

print()

# ============================================================================
# 4. TOP CHINESE INSTITUTIONS IN INTERNATIONAL COLLABORATION
# ============================================================================

print("[4] TOP CHINESE INSTITUTIONS IN INTERNATIONAL COLLABORATION")
print("-"*80)

query = """
SELECT
    chinese_institutions,
    COUNT(*) as papers,
    SUM(CASE WHEN collaboration_type = 'International' THEN 1 ELSE 0 END) as intl_papers,
    ROUND(SUM(CASE WHEN collaboration_type = 'International' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as intl_pct
FROM research_papers_expanded
WHERE chinese_institutions IS NOT NULL
    AND chinese_institutions != ''
GROUP BY chinese_institutions
HAVING COUNT(*) >= 100
ORDER BY intl_papers DESC
LIMIT 50
"""

df_chinese_inst = pd.read_sql_query(query, conn)

# Parse first institution from each record
chinese_inst_data = []

for _, row in df_chinese_inst.iterrows():
    inst_str = row['chinese_institutions']
    if pd.notna(inst_str) and inst_str:
        # Get first institution
        first_inst = inst_str.split(';')[0].strip()
        chinese_inst_data.append({
            'institution': first_inst,
            'papers': int(row['papers']),
            'intl_papers': int(row['intl_papers']),
            'intl_pct': row['intl_pct']
        })

# Aggregate by institution name
inst_aggregated = {}
for item in chinese_inst_data:
    inst = item['institution']
    if inst not in inst_aggregated:
        inst_aggregated[inst] = {
            'papers': 0,
            'intl_papers': 0
        }
    inst_aggregated[inst]['papers'] += item['papers']
    inst_aggregated[inst]['intl_papers'] += item['intl_papers']

# Calculate percentage and sort
for inst in inst_aggregated:
    total = inst_aggregated[inst]['papers']
    intl = inst_aggregated[inst]['intl_papers']
    inst_aggregated[inst]['intl_pct'] = (intl / total * 100) if total > 0 else 0

sorted_chinese_inst = sorted(
    inst_aggregated.items(),
    key=lambda x: x[1]['intl_papers'],
    reverse=True
)[:30]

print()
print(f"{'Rank':<6} {'Institution':<45} {'Total':>8} {'Intl':>8} {'Intl %':>8}")
print("-"*80)

for i, (inst, data) in enumerate(sorted_chinese_inst, 1):
    print(f"{i:<6} {inst[:44]:<45} {data['papers']:>8,} {data['intl_papers']:>8,} {data['intl_pct']:>7.1f}%")

print()

# ============================================================================
# 5. COLLABORATION PATTERNS OVER TIME
# ============================================================================

print("[5] COLLABORATION PATTERNS OVER TIME")
print("-"*80)

query = """
SELECT
    publication_year,
    COUNT(*) as total_papers,
    SUM(CASE WHEN collaboration_type = 'International' THEN 1 ELSE 0 END) as intl_papers,
    ROUND(SUM(CASE WHEN collaboration_type = 'International' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as intl_pct
FROM research_papers_expanded
GROUP BY publication_year
ORDER BY publication_year
"""

df_yearly_collab = pd.read_sql_query(query, conn)

# Show select years
print()
print("International Collaboration Rate by Year:")
for year in [2011, 2014, 2017, 2020, 2022, 2024]:
    year_data = df_yearly_collab[df_yearly_collab['publication_year'] == year]
    if len(year_data) > 0:
        intl_pct = year_data['intl_pct'].values[0]
        intl_papers = int(year_data['intl_papers'].values[0])
        total_papers = int(year_data['total_papers'].values[0])
        print(f"  {year}: {intl_pct:.1f}% ({intl_papers:,} / {total_papers:,})")

print()

# Identify trend
early_avg = df_yearly_collab[df_yearly_collab['publication_year'].between(2011, 2015)]['intl_pct'].mean()
mid_avg = df_yearly_collab[df_yearly_collab['publication_year'].between(2016, 2020)]['intl_pct'].mean()
recent_avg = df_yearly_collab[df_yearly_collab['publication_year'].between(2021, 2024)]['intl_pct'].mean()

print(f"Average collaboration rates by period:")
print(f"  2011-2015: {early_avg:.1f}%")
print(f"  2016-2020: {mid_avg:.1f}%")
print(f"  2021-2024: {recent_avg:.1f}%")
print()

if recent_avg < mid_avg:
    print(f"[FINDING] International collaboration has declined {mid_avg-recent_avg:.1f} percentage points")
    print(f"           from the MIC2025 era (possibly due to geopolitical tensions)")
else:
    print(f"[FINDING] International collaboration has increased {recent_avg-mid_avg:.1f} percentage points")

print()

# ============================================================================
# 6. STRATEGIC TOPICS - LOW INTERNATIONAL COLLABORATION
# ============================================================================

print("[6] STRATEGIC TOPICS (Low International Collaboration)")
print("-"*80)

strategic_topics = df_topic_collab[df_topic_collab['intl_pct'] < 25.0].copy()
strategic_topics = strategic_topics.sort_values('intl_pct')

print()
print("Topics with below-average international collaboration (<25%):")
print(f"{'Topic':<30} {'Intl %':>10} {'Total Papers':>15}")
print("-"*60)

for _, row in strategic_topics.iterrows():
    topic = row['technology_category']
    intl_pct = row['intl_pct']
    total = int(row['total_papers'])
    print(f"{topic:<30} {intl_pct:>9.1f}% {total:>15,}")

print()
print("[INTERPRETATION] Lower international collaboration may indicate:")
print("  - Strategic/sensitive research areas")
print("  - Domestic focus and self-reliance efforts")
print("  - Areas of competitive advantage")
print()

# ============================================================================
# 7. SAVE RESULTS
# ============================================================================

print("[7] SAVING RESULTS")
print("-"*80)

results = {
    'analysis_date': datetime.now().isoformat(),
    'overview': {
        'total_papers': int(df_overview['total_papers'].values[0]),
        'international_papers': int(df_overview['intl_papers'].values[0]),
        'international_pct': float(df_overview['intl_pct'].values[0])
    },
    'top_partner_institutions': [
        {'institution': inst, 'papers': count}
        for inst, count in top_institutions[:50]
    ],
    'collaboration_by_topic': df_topic_collab.to_dict('records'),
    'top_chinese_institutions': [
        {'institution': inst, **data}
        for inst, data in sorted_chinese_inst
    ],
    'temporal_trends': {
        'early_period_2011_2015': float(early_avg),
        'mic2025_era_2016_2020': float(mid_avg),
        'recent_2021_2024': float(recent_avg),
        'yearly_data': df_yearly_collab.to_dict('records')
    },
    'strategic_topics': strategic_topics.to_dict('records')
}

output_file = Path("analysis/openalex_collaboration_networks.json")
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n[OK] Results saved to: {output_file}")

print()
print("="*80)
print("COLLABORATION NETWORK ANALYSIS COMPLETE")
print("="*80)
print()
print("Key Findings:")
print(f"  - Overall international collaboration: {df_overview['intl_pct'].values[0]:.1f}%")
print(f"  - Highest collab topic: {df_topic_collab.iloc[0]['technology_category']} ({df_topic_collab.iloc[0]['intl_pct']:.1f}%)")
print(f"  - Strategic topics (low collab): {len(strategic_topics)}")
print(f"  - Collaboration trend: {'Declining' if recent_avg < mid_avg else 'Increasing'}")
print()

conn.close()
