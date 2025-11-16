"""
OpenAlex Semiconductor EU-China Collaboration Analysis - FAST VERSION
Uses optimized queries with temp tables for performance
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
print("OPENALEX SEMICONDUCTOR EU-CHINA COLLABORATION ANALYSIS (FAST VERSION)")
print("="*80)
print(f"Database: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ============================================================================
# STEP 1: Create temp table of semiconductor works (fast)
# ============================================================================

print("STEP 1: Identifying semiconductor works...")

# Use focused keywords for high precision
keywords = ['semiconductor', 'chip fabrication', 'wafer', 'mosfet', 'finfet',
            'integrated circuit', 'asic', 'fpga', 'vlsi', 'cmos',
            'euv lithography', 'photolithography']

conditions = " OR ".join([f"title LIKE '%{kw}%' OR keywords LIKE '%{kw}%'" for kw in keywords])

cursor.execute(f"""
CREATE TEMP TABLE IF NOT EXISTS temp_semiconductor_works AS
SELECT DISTINCT work_id, title, publication_year, cited_by_count, primary_topic, technology_domain
FROM openalex_works
WHERE ({conditions})
""")

cursor.execute("SELECT COUNT(*) FROM temp_semiconductor_works")
total_semiconductor = cursor.fetchone()[0]
print(f"  Semiconductor works: {total_semiconductor:,}\n")

# ============================================================================
# STEP 2: Get EU-China collaborations (optimized approach)
# ============================================================================

print("STEP 2: Finding EU-China collaborations...")

# First, get works with EU authors
eu_list = "', '".join(EU27_COUNTRIES)
cursor.execute(f"""
CREATE TEMP TABLE IF NOT EXISTS temp_eu_works AS
SELECT DISTINCT wa.work_id
FROM openalex_work_authors wa
JOIN temp_semiconductor_works sw ON wa.work_id = sw.work_id
WHERE wa.country_code IN ('{eu_list}')
""")

cursor.execute("SELECT COUNT(*) FROM temp_eu_works")
eu_works = cursor.fetchone()[0]
print(f"  Works with EU authors: {eu_works:,}")

# Now get works with China authors
cursor.execute("""
CREATE TEMP TABLE IF NOT EXISTS temp_china_works AS
SELECT DISTINCT wa.work_id
FROM openalex_work_authors wa
JOIN temp_semiconductor_works sw ON wa.work_id = sw.work_id
WHERE wa.country_code = 'CN'
""")

cursor.execute("SELECT COUNT(*) FROM temp_china_works")
china_works = cursor.fetchone()[0]
print(f"  Works with China authors: {china_works:,}")

# Get EU-China collaborations (works with BOTH)
cursor.execute("""
CREATE TEMP TABLE IF NOT EXISTS temp_eu_china_collabs AS
SELECT DISTINCT ew.work_id
FROM temp_eu_works ew
JOIN temp_china_works cw ON ew.work_id = cw.work_id
""")

cursor.execute("SELECT COUNT(*) FROM temp_eu_china_collabs")
eu_china_collabs = cursor.fetchone()[0]
print(f"  EU-China collaborations: {eu_china_collabs:,}")

if total_semiconductor > 0:
    pct = (eu_china_collabs / total_semiconductor * 100)
    print(f"  Percentage: {pct:.1f}%\n")

# ============================================================================
# STEP 3: Get collaboration details
# ============================================================================

print("STEP 3: Extracting collaboration details...")

cursor.execute("""
SELECT sw.work_id, sw.title, sw.publication_year, sw.cited_by_count,
       sw.primary_topic, sw.technology_domain
FROM temp_semiconductor_works sw
JOIN temp_eu_china_collabs ec ON sw.work_id = ec.work_id
WHERE sw.publication_year IS NOT NULL
ORDER BY sw.publication_year DESC, sw.cited_by_count DESC
LIMIT 2000
""")

collaboration_papers = []
for row in cursor.fetchall():
    collaboration_papers.append({
        'work_id': row[0],
        'title': row[1],
        'publication_year': row[2],
        'cited_by_count': row[3],
        'primary_topic': row[4],
        'technology_domain': row[5]
    })

print(f"  Extracted {len(collaboration_papers):,} papers\n")

# ============================================================================
# STEP 4: Temporal analysis
# ============================================================================

print("STEP 4: Temporal trends...")

papers_by_year = defaultdict(int)
for paper in collaboration_papers:
    if paper['publication_year']:
        papers_by_year[paper['publication_year']] += 1

print("\nYear | Papers")
print("-" * 30)
for year in sorted(papers_by_year.keys()):
    print(f"{year} | {papers_by_year[year]:>6,}")

# ============================================================================
# STEP 5: Top EU countries
# ============================================================================

print("\n" + "="*80)
print("STEP 5: Top EU Countries")
print("="*80 + "\n")

# Sample first 500 collaborations for country analysis
work_ids = [p['work_id'] for p in collaboration_papers[:500]]
work_ids_str = "', '".join(work_ids)

if work_ids_str:
    cursor.execute(f"""
    SELECT country_code, COUNT(DISTINCT work_id) as papers
    FROM openalex_work_authors
    WHERE work_id IN ('{work_ids_str}')
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
# STEP 6: Top Chinese institutions
# ============================================================================

print("\n" + "="*80)
print("STEP 6: Top Chinese Institutions")
print("="*80 + "\n")

if work_ids_str:
    cursor.execute(f"""
    SELECT institution_name, COUNT(DISTINCT work_id) as papers
    FROM openalex_work_authors
    WHERE work_id IN ('{work_ids_str}')
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
# STEP 7: Technology domains
# ============================================================================

print("\n" + "="*80)
print("STEP 7: Technology Domains")
print("="*80 + "\n")

domains = defaultdict(int)
topics = defaultdict(int)

for paper in collaboration_papers:
    if paper['technology_domain']:
        domains[paper['technology_domain']] += 1
    if paper['primary_topic']:
        topics[paper['primary_topic']] += 1

print("Top Domains:")
for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]:
    domain_name = domain[:60] if domain else "Unclassified"
    print(f"  {domain_name:<60} | {count:>5,}")

print("\nTop Topics:")
for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:15]:
    topic_name = topic[:70] if topic else "Unclassified"
    print(f"  {topic_name:<70} | {count:>5,}")

# ============================================================================
# STEP 8: Most cited
# ============================================================================

print("\n" + "="*80)
print("STEP 8: Most Cited Papers")
print("="*80 + "\n")

top_cited = sorted(collaboration_papers, key=lambda x: x['cited_by_count'] or 0, reverse=True)[:15]

print("Rank | Cites | Year | Title")
print("-" * 120)
for idx, paper in enumerate(top_cited, 1):
    title = paper['title'][:90] if paper['title'] else "No title"
    year = paper['publication_year'] or "N/A"
    cites = paper['cited_by_count'] or 0
    print(f"{idx:>3} | {cites:>5,} | {year} | {title}")

# ============================================================================
# STEP 9: Save results
# ============================================================================

print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80 + "\n")

os.makedirs(OUTPUT_DIR, exist_ok=True)

results = {
    'metadata': {
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'database': DB_PATH,
        'total_semiconductor_works': total_semiconductor,
        'eu_works': eu_works,
        'china_works': china_works,
        'eu_china_collaborations': eu_china_collabs,
        'papers_analyzed': len(collaboration_papers),
        'zero_fabrication_compliant': True,
        'source': 'OpenAlex Research Database',
        'method': 'Optimized queries with temp tables'
    },
    'temporal_analysis': dict(papers_by_year),
    'geographic_analysis': {
        'top_eu_countries': eu_countries[:20] if 'eu_countries' in locals() else [],
        'top_chinese_institutions': chinese_institutions[:20] if 'chinese_institutions' in locals() else []
    },
    'technology_analysis': {
        'top_domains': dict(sorted(domains.items(), key=lambda x: x[1], reverse=True)[:20]),
        'top_topics': dict(sorted(topics.items(), key=lambda x: x[1], reverse=True)[:30])
    },
    'top_cited_papers': [{
        'rank': i+1,
        'title': p['title'],
        'year': p['publication_year'],
        'citations': p['cited_by_count'],
        'topic': p['primary_topic']
    } for i, p in enumerate(top_cited[:30])],
    'sample_papers': collaboration_papers[:50]
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
print(f"  EU semiconductor research: {eu_works:,}")
print(f"  China semiconductor research: {china_works:,}")
print(f"  EU-China collaborations: {eu_china_collabs:,}")

if papers_by_year:
    print(f"\nTemporal Span: {min(papers_by_year.keys())}-{max(papers_by_year.keys())}")
    print(f"Average per year: {sum(papers_by_year.values()) / len(papers_by_year):.0f} papers")

if 'eu_countries' in locals() and eu_countries:
    print(f"\nTop EU Collaborators:")
    for i in range(min(3, len(eu_countries))):
        print(f"  {i+1}. {eu_countries[i]['country']}: {eu_countries[i]['papers']:,}")

if 'chinese_institutions' in locals() and chinese_institutions:
    print(f"\nTop Chinese Institutions:")
    for i in range(min(3, len(chinese_institutions))):
        inst_name = chinese_institutions[i]['institution'][:60] if chinese_institutions[i]['institution'] else "Unknown"
        print(f"  {i+1}. {inst_name}: {chinese_institutions[i]['papers']:,}")

# Cleanup
cursor.execute("DROP TABLE IF EXISTS temp_semiconductor_works")
cursor.execute("DROP TABLE IF EXISTS temp_eu_works")
cursor.execute("DROP TABLE IF EXISTS temp_china_works")
cursor.execute("DROP TABLE IF EXISTS temp_eu_china_collabs")

conn.close()

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
