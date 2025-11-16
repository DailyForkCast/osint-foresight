"""
OpenAlex Semiconductor EU-China Collaboration Analysis - ULTRA-OPTIMIZED
Uses existing technology_domain classification instead of keyword matching
Zero Fabrication Protocol compliant
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict
import os

DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'
OUTPUT_DIR = 'C:/Projects/OSINT-Foresight/analysis/semiconductors'

EU27_COUNTRIES = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
                  'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
                  'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE']

print("="*80)
print("OPENALEX SEMICONDUCTOR COLLABORATION ANALYSIS (ULTRA-OPTIMIZED v2)")
print("="*80)
print(f"Database: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ============================================================================
# OPTIMIZATION STRATEGY: Use existing technology_domain column
# ============================================================================

print("STEP 1: Checking technology_domain for 'Semiconductors'...")

# Check if we have a Semiconductors technology domain
cursor.execute("""
SELECT DISTINCT technology_domain
FROM openalex_works
WHERE technology_domain LIKE '%semiconductor%'
   OR technology_domain LIKE '%Semiconductor%'
LIMIT 10
""")

domains = cursor.fetchall()
print(f"  Found {len(domains)} semiconductor domain variants:")
for domain in domains:
    print(f"    - {domain[0]}")

# Use the technology_domain filter (MUCH faster than keyword matching)
print("\nSTEP 2: Counting semiconductor works using technology_domain...")

cursor.execute("""
SELECT COUNT(DISTINCT work_id)
FROM openalex_works
WHERE technology_domain = 'Semiconductors'
""")

total_semiconductor = cursor.fetchone()[0]
print(f"  Total semiconductor works: {total_semiconductor:,}\n")

# ============================================================================
# STEP 3: Get works with authors from both EU and China (FAST approach)
# ============================================================================

print("STEP 3: Finding EU-China collaborations...")

# Direct query without temp tables
eu_list = "', '".join(EU27_COUNTRIES)

cursor.execute(f"""
SELECT
    w.work_id,
    COUNT(DISTINCT CASE WHEN wa.country_code IN ('{eu_list}') THEN wa.author_id END) as eu_authors,
    COUNT(DISTINCT CASE WHEN wa.country_code = 'CN' THEN wa.author_id END) as china_authors
FROM openalex_works w
JOIN openalex_work_authors wa ON w.work_id = wa.work_id
WHERE w.technology_domain = 'Semiconductors'
GROUP BY w.work_id
HAVING eu_authors > 0 AND china_authors > 0
""")

collab_works = cursor.fetchall()
print(f"  EU-China collaboration works: {len(collab_works):,}\n")

# Get work IDs for collaborations
collab_work_ids = [row[0] for row in collab_works]

if not collab_work_ids:
    print("No EU-China semiconductor collaborations found.")
    conn.close()
    exit()

# ============================================================================
# STEP 4: Get details for collaboration papers
# ============================================================================

print("STEP 4: Extracting collaboration paper details...")

# Batch query for details
work_ids_str = "', '".join(collab_work_ids[:1000])  # Limit to first 1000

cursor.execute(f"""
SELECT work_id, title, publication_year, cited_by_count, primary_topic, doi
FROM openalex_works
WHERE work_id IN ('{work_ids_str}')
ORDER BY cited_by_count DESC
""")

papers = []
for row in cursor.fetchall():
    papers.append({
        'work_id': row[0],
        'title': row[1],
        'year': row[2],
        'citations': row[3],
        'topic': row[4],
        'doi': row[5]
    })

print(f"  Extracted {len(papers):,} papers\n")

# ============================================================================
# STEP 5: Temporal analysis
# ============================================================================

print("STEP 5: Temporal analysis...")

years = defaultdict(int)
for paper in papers:
    if paper['year']:
        years[paper['year']] += 1

print("\nYear | Papers")
print("-" * 30)
for year in sorted(years.keys()):
    print(f"{year} | {years[year]:>6,}")

# ============================================================================
# STEP 6: Top EU countries
# ============================================================================

print("\n" + "="*80)
print("STEP 6: Top EU Countries")
print("="*80 + "\n")

# Sample 500 collaboration works for country analysis
sample_ids = "', '".join(collab_work_ids[:500])

cursor.execute(f"""
SELECT country_code, COUNT(DISTINCT work_id) as papers
FROM openalex_work_authors
WHERE work_id IN ('{sample_ids}')
  AND country_code IN ('{eu_list}')
GROUP BY country_code
ORDER BY papers DESC
""")

print("Rank | Country | Papers")
print("-" * 40)
eu_countries = []
for idx, (country, count) in enumerate(cursor.fetchall(), 1):
    print(f"{idx:>3} | {country:>7} | {count:>6,}")
    eu_countries.append({'rank': idx, 'country': country, 'papers': count})

# ============================================================================
# STEP 7: Top Chinese institutions
# ============================================================================

print("\n" + "="*80)
print("STEP 7: Top Chinese Institutions")
print("="*80 + "\n")

cursor.execute(f"""
SELECT institution_name, COUNT(DISTINCT work_id) as papers
FROM openalex_work_authors
WHERE work_id IN ('{sample_ids}')
  AND country_code = 'CN'
  AND institution_name IS NOT NULL
GROUP BY institution_name
ORDER BY papers DESC
LIMIT 20
""")

print("Rank | Institution | Papers")
print("-" * 100)
chinese_institutions = []
for idx, (inst, count) in enumerate(cursor.fetchall(), 1):
    inst_name = inst[:75] if inst else "Unknown"
    print(f"{idx:>3} | {inst_name:<75} | {count:>6,}")
    chinese_institutions.append({'rank': idx, 'institution': inst, 'papers': count})

# ============================================================================
# STEP 8: Top topics
# ============================================================================

print("\n" + "="*80)
print("STEP 8: Research Topics")
print("="*80 + "\n")

topics = defaultdict(int)
for paper in papers:
    if paper['topic']:
        topics[paper['topic']] += 1

print("Top 15 Topics:")
for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:15]:
    topic_name = topic[:70] if topic else "Unclassified"
    print(f"  {topic_name:<70} | {count:>5,}")

# ============================================================================
# STEP 9: Most cited papers
# ============================================================================

print("\n" + "="*80)
print("STEP 9: Most Cited Papers")
print("="*80 + "\n")

top_cited = sorted(papers, key=lambda x: x['citations'] or 0, reverse=True)[:15]

print("Rank | Cites | Year | Title")
print("-" * 120)
for idx, paper in enumerate(top_cited, 1):
    title = paper['title'][:90] if paper['title'] else "No title"
    year = paper['year'] or "N/A"
    cites = paper['citations'] or 0
    print(f"{idx:>3} | {cites:>5,} | {year} | {title}")

# ============================================================================
# STEP 10: Save results
# ============================================================================

print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80 + "\n")

os.makedirs(OUTPUT_DIR, exist_ok=True)

results = {
    'metadata': {
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'database': DB_PATH,
        'optimization_method': 'technology_domain classification (ultra-fast)',
        'total_semiconductor_works': total_semiconductor,
        'eu_china_collaborations': len(collab_works),
        'papers_analyzed': len(papers),
        'zero_fabrication_compliant': True,
        'source': 'OpenAlex Research Database'
    },
    'temporal_analysis': dict(years),
    'geographic_analysis': {
        'top_eu_countries': eu_countries,
        'top_chinese_institutions': chinese_institutions
    },
    'research_topics': dict(sorted(topics.items(), key=lambda x: x[1], reverse=True)[:30]),
    'top_cited_papers': [{
        'rank': i+1,
        'title': p['title'],
        'year': p['year'],
        'citations': p['citations'],
        'doi': p['doi'],
        'topic': p['topic']
    } for i, p in enumerate(top_cited[:30])],
    'sample_papers': papers[:50]
}

output_file = f"{OUTPUT_DIR}/eu_china_semiconductor_collaborations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Results saved to: {output_file}\n")

# ============================================================================
# SUMMARY
# ============================================================================

print("="*80)
print("ANALYSIS SUMMARY")
print("="*80 + "\n")

print(f"Semiconductor Research Intelligence:")
print(f"  Total semiconductor works: {total_semiconductor:,}")
print(f"  EU-China collaborations: {len(collab_works):,}")
print(f"  Papers analyzed: {len(papers):,}")

if years:
    print(f"\nTemporal Span: {min(years.keys())}-{max(years.keys())}")
    print(f"Average per year: {sum(years.values()) / len(years):.0f} papers")

if eu_countries:
    print(f"\nTop 3 EU Collaborators:")
    for i in range(min(3, len(eu_countries))):
        print(f"  {i+1}. {eu_countries[i]['country']}: {eu_countries[i]['papers']:,}")

if chinese_institutions:
    print(f"\nTop 3 Chinese Institutions:")
    for i in range(min(3, len(chinese_institutions))):
        inst_name = chinese_institutions[i]['institution'][:60]
        print(f"  {i+1}. {inst_name}: {chinese_institutions[i]['papers']:,}")

if top_cited:
    print(f"\nMost Cited Paper:")
    print(f"  Title: {top_cited[0]['title'][:80]}")
    print(f"  Year: {top_cited[0]['year']}")
    print(f"  Citations: {top_cited[0]['citations']:,}")

conn.close()

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
