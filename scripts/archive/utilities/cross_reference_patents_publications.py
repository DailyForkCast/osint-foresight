#!/usr/bin/env python3
"""
Cross-Reference USPTO Patents with OpenAlex Publications
Identify research-to-patent pathways
"""

import sqlite3
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

openalex_db = Path("F:/OSINT_Data/openalex_analytics/openalex_chinese_research.db")
patent_db = Path("F:/OSINT_Data/osint_master.db")

print("="*80)
print("PATENT-PUBLICATION CROSS-REFERENCE ANALYSIS")
print("="*80)
print()

# Connect to both databases
conn_openalex = sqlite3.connect(openalex_db)
conn_patents = sqlite3.connect(patent_db)

# ============================================================================
# 1. PATENT DATABASE OVERVIEW
# ============================================================================

print("[1] PATENT DATABASE OVERVIEW")
print("-"*80)

# Get patent schema
cursor_patents = conn_patents.cursor()
cursor_patents.execute("PRAGMA table_info(patents)")
patent_columns = [row[1] for row in cursor_patents.fetchall()]

print(f"\nPatent table columns: {', '.join(patent_columns)}")

# Get patent statistics
query_patents = "SELECT COUNT(*) as total_patents FROM patents"
df_patent_count = pd.read_sql_query(query_patents, conn_patents)

print(f"\nTotal patents in database: {int(df_patent_count['total_patents'].values[0]):,}")

# Sample patents to understand structure
query_sample = "SELECT * FROM patents LIMIT 5"
df_patent_sample = pd.read_sql_query(query_sample, conn_patents)

print(f"\nSample patent record structure:")
print(df_patent_sample.iloc[0].to_string())

print()

# ============================================================================
# 2. OPENALEX PUBLICATIONS OVERVIEW
# ============================================================================

print("[2] OPENALEX PUBLICATIONS OVERVIEW")
print("-"*80)

query_openalex = """
SELECT
    COUNT(*) as total_papers,
    COUNT(DISTINCT technology_category) as total_topics
FROM research_papers_expanded
"""
df_openalex_count = pd.read_sql_query(query_openalex, conn_openalex)

print(f"\nTotal papers: {int(df_openalex_count['total_papers'].values[0]):,}")
print(f"Total topics: {int(df_openalex_count['total_topics'].values[0])}")

print()

# ============================================================================
# 3. TEMPORAL COMPARISON - PATENTS VS PUBLICATIONS
# ============================================================================

print("[3] TEMPORAL COMPARISON: Patents vs Publications")
print("-"*80)

# Get year columns from patents
if 'grant_year' in patent_columns:
    year_col = 'grant_year'
elif 'filing_year' in patent_columns:
    year_col = 'filing_year'
elif 'year' in patent_columns:
    year_col = 'year'
else:
    # Try to extract from other fields
    year_col = None

if year_col:
    query_patent_yearly = f"""
    SELECT
        {year_col} as year,
        COUNT(*) as patent_count
    FROM patents
    WHERE {year_col} IS NOT NULL
        AND {year_col} >= 2011
        AND {year_col} <= 2025
    GROUP BY {year_col}
    ORDER BY {year_col}
    """

    df_patent_yearly = pd.read_sql_query(query_patent_yearly, conn_patents)
else:
    print("[WARNING] Could not identify year column in patents table")
    df_patent_yearly = pd.DataFrame({'year': [], 'patent_count': []})

# Get publication counts by year
query_pub_yearly = """
SELECT
    publication_year as year,
    COUNT(*) as pub_count
FROM research_papers_expanded
WHERE publication_year >= 2011
    AND publication_year <= 2025
GROUP BY publication_year
ORDER BY publication_year
"""

df_pub_yearly = pd.read_sql_query(query_pub_yearly, conn_openalex)

# Merge
if len(df_patent_yearly) > 0:
    df_comparison = pd.merge(
        df_pub_yearly,
        df_patent_yearly,
        on='year',
        how='outer'
    ).fillna(0)

    df_comparison['year'] = df_comparison['year'].astype(int)
    df_comparison = df_comparison.sort_values('year')

    print()
    print(f"{'Year':<6} {'Publications':>14} {'Patents':>12} {'Pub/Patent Ratio':>18}")
    print("-"*60)

    for _, row in df_comparison.iterrows():
        year = int(row['year'])
        pubs = int(row['pub_count'])
        patents = int(row['patent_count'])

        if patents > 0:
            ratio = pubs / patents
            ratio_str = f"{ratio:.1f}:1"
        else:
            ratio_str = "N/A"

        print(f"{year:<6} {pubs:>14,} {patents:>12,} {ratio_str:>18}")

    print()
else:
    print("[WARNING] Cannot perform temporal comparison - year data not available in patents")

# ============================================================================
# 4. TOPIC-BASED PATENT ANALYSIS
# ============================================================================

print("[4] TECHNOLOGY TOPIC ANALYSIS")
print("-"*80)

# Check if technology/cpc fields exist in patents
tech_fields = [col for col in patent_columns if 'tech' in col.lower() or 'cpc' in col.lower() or 'classification' in col.lower()]

print(f"\nTechnology-related fields in patents table: {', '.join(tech_fields) if tech_fields else 'None found'}")

# Get publication counts by topic
query_pub_by_topic = """
SELECT
    technology_category,
    COUNT(*) as pub_count,
    MIN(publication_year) as first_year,
    MAX(publication_year) as last_year
FROM research_papers_expanded
GROUP BY technology_category
ORDER BY pub_count DESC
"""

df_pub_by_topic = pd.read_sql_query(query_pub_by_topic, conn_openalex)

print()
print(f"{'Technology Topic':<30} {'Publications':>14} {'Years Active':>15}")
print("-"*65)

for _, row in df_pub_by_topic.iterrows():
    topic = row['technology_category']
    pub_count = int(row['pub_count'])
    first_year = int(row['first_year'])
    last_year = int(row['last_year'])

    print(f"{topic:<30} {pub_count:>14,} {first_year}-{last_year:>4}")

print()

# ============================================================================
# 5. INSTITUTION OVERLAP ANALYSIS
# ============================================================================

print("[5] INSTITUTION OVERLAP ANALYSIS")
print("-"*80)

# Check if assignee/applicant fields exist
inst_fields = [col for col in patent_columns if 'assignee' in col.lower() or 'applicant' in col.lower() or 'owner' in col.lower()]

print(f"\nInstitution-related fields in patents: {', '.join(inst_fields) if inst_fields else 'None found'}")

# Get top institutions from publications
query_pub_institutions = """
SELECT
    chinese_institutions,
    COUNT(*) as paper_count
FROM research_papers_expanded
WHERE chinese_institutions IS NOT NULL
GROUP BY chinese_institutions
ORDER BY paper_count DESC
LIMIT 30
"""

df_pub_institutions = pd.read_sql_query(query_pub_institutions, conn_openalex)

# Extract first institution name
top_pub_institutions = []
for inst_str in df_pub_institutions['chinese_institutions'].values:
    if pd.notna(inst_str) and inst_str:
        first_inst = inst_str.split(';')[0].strip()
        top_pub_institutions.append(first_inst)

print(f"\nTop 10 institutions in publications:")
for i, inst in enumerate(top_pub_institutions[:10], 1):
    print(f"  {i}. {inst}")

print()

# ============================================================================
# 6. RESEARCH-TO-PATENT PATHWAY INDICATORS
# ============================================================================

print("[6] RESEARCH-TO-PATENT PATHWAY INDICATORS")
print("-"*80)

# Calculate indicators
total_pubs = int(df_openalex_count['total_papers'].values[0])
total_patents = int(df_patent_count['total_patents'].values[0])

if len(df_comparison) > 0:
    recent_pubs = int(df_comparison[df_comparison['year'].between(2020, 2024)]['pub_count'].sum())
    recent_patents = int(df_comparison[df_comparison['year'].between(2020, 2024)]['patent_count'].sum())

    print()
    print(f"Overall Metrics:")
    print(f"  Total publications (2011-2025): {total_pubs:,}")
    print(f"  Total patents (2011-2025): {total_patents:,}")
    print(f"  Publication-to-Patent ratio: {total_pubs/total_patents if total_patents > 0 else 0:.1f}:1")
    print()
    print(f"Recent Metrics (2020-2024):")
    print(f"  Publications: {recent_pubs:,}")
    print(f"  Patents: {recent_patents:,}")
    print(f"  Ratio: {recent_pubs/recent_patents if recent_patents > 0 else 0:.1f}:1")
    print()

# ============================================================================
# 7. SAVE RESULTS
# ============================================================================

print("[7] SAVING RESULTS")
print("-"*80)

results = {
    'analysis_date': datetime.now().isoformat(),
    'overview': {
        'total_publications': total_pubs,
        'total_patents': total_patents,
        'publication_to_patent_ratio': round(total_pubs/total_patents if total_patents > 0 else 0, 2)
    },
    'temporal_comparison': df_comparison.to_dict('records') if len(df_comparison) > 0 else [],
    'topic_breakdown': df_pub_by_topic.to_dict('records'),
    'top_publication_institutions': top_pub_institutions[:20]
}

output_file = Path("analysis/patent_publication_cross_reference.json")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Results saved to: {output_file}")

print()
print("="*80)
print("CROSS-REFERENCE ANALYSIS COMPLETE")
print("="*80)
print()
print(f"Key Findings:")
print(f"  - Publications: {total_pubs:,}")
print(f"  - Patents: {total_patents:,}")
print(f"  - Publication-to-Patent ratio: {total_pubs/total_patents if total_patents > 0 else 0:.1f}:1")
print()

conn_openalex.close()
conn_patents.close()
