"""
OpenAlex Semiconductor Research EU-China Collaboration Analysis
Identifies and analyzes semiconductor research partnerships between EU and China
Zero Fabrication Protocol compliant
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict
import os

DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'
OUTPUT_DIR = 'C:/Projects/OSINT-Foresight/analysis/semiconductors'

EU27_COUNTRIES = [
    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
    'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
    'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
]

print("="*80)
print("OPENALEX SEMICONDUCTOR EU-CHINA COLLABORATION ANALYSIS")
print("="*80)
print(f"Database: {DB_PATH}")
print(f"Output: {OUTPUT_DIR}\n")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ============================================================================
# STEP 1: Identify semiconductor-related works
# ============================================================================

print("="*80)
print("STEP 1: Identifying Semiconductor Research Papers")
print("="*80 + "\n")

# Load semiconductor keywords
with open('C:/Projects/OSINT-Foresight/config/openalex_technology_keywords_v5.json', 'r') as f:
    keywords_config = json.load(f)

semiconductor_keywords = keywords_config.get('Semiconductors', {})

# Build comprehensive keyword list
all_keywords = []
for category, kw_list in semiconductor_keywords.items():
    all_keywords.extend(kw_list)

print(f"Loaded {len(all_keywords)} semiconductor keywords from v5 config\n")

# Create optimized search - use most specific keywords to reduce false positives
core_semiconductor_keywords = [
    'semiconductor', 'chip fabrication', 'wafer processing',
    'euv lithography', 'photolithography', 'mosfet', 'finfet',
    'gate-all-around', 'integrated circuit', 'ic design', 'asic', 'fpga',
    'soc design', 'vlsi', 'cmos technology', 'chiplet',
    'silicon wafer', 'gan device', 'sic device', 'wide bandgap',
    '3d integration', 'heterogeneous integration'
]

print("Using focused semiconductor keywords for high precision:")
for kw in core_semiconductor_keywords[:10]:
    print(f"  - {kw}")
print(f"  ... and {len(core_semiconductor_keywords) - 10} more\n")

# Build WHERE clause
semiconductor_conditions = " OR ".join([
    f"(title LIKE '%{kw}%' OR abstract LIKE '%{kw}%' OR keywords LIKE '%{kw}%')"
    for kw in core_semiconductor_keywords
])

# Count semiconductor works
print("Counting semiconductor-related works...")
cursor.execute(f"""
SELECT COUNT(DISTINCT work_id)
FROM openalex_works
WHERE ({semiconductor_conditions})
""")

total_semiconductor_works = cursor.fetchone()[0]
print(f"Total semiconductor works: {total_semiconductor_works:,}\n")

# ============================================================================
# STEP 2: Identify EU-China collaborations
# ============================================================================

print("="*80)
print("STEP 2: Identifying EU-China Semiconductor Collaborations")
print("="*80 + "\n")

eu_condition = " OR ".join([f"wa.country_code = '{cc}'" for cc in EU27_COUNTRIES])

query_eu_china_collabs = f"""
WITH semiconductor_works AS (
    SELECT DISTINCT work_id
    FROM openalex_works
    WHERE ({semiconductor_conditions})
),
eu_authors AS (
    SELECT DISTINCT wa.work_id
    FROM openalex_work_authors wa
    JOIN semiconductor_works sw ON wa.work_id = sw.work_id
    WHERE ({eu_condition})
),
china_authors AS (
    SELECT DISTINCT wa.work_id
    FROM openalex_work_authors wa
    JOIN semiconductor_works sw ON wa.work_id = sw.work_id
    WHERE wa.country_code = 'CN'
)
SELECT COUNT(DISTINCT ea.work_id)
FROM eu_authors ea
JOIN china_authors ca ON ea.work_id = ca.work_id
"""

print("Analyzing EU-China co-authorships...")
cursor.execute(query_eu_china_collabs)
eu_china_semiconductor_collabs = cursor.fetchone()[0]

print(f"Semiconductor papers with EU-China collaboration: {eu_china_semiconductor_collabs:,}")
if total_semiconductor_works > 0:
    pct = (eu_china_semiconductor_collabs / total_semiconductor_works * 100)
    print(f"Percentage of semiconductor papers with EU-China collab: {pct:.1f}%\n")

# ============================================================================
# STEP 3: Detailed collaboration papers
# ============================================================================

print("="*80)
print("STEP 3: Extracting Detailed Collaboration Data")
print("="*80 + "\n")

query_collaboration_details = f"""
WITH semiconductor_works AS (
    SELECT work_id, title, publication_year, doi, abstract,
           primary_topic, technology_domain, keywords, cited_by_count
    FROM openalex_works
    WHERE ({semiconductor_conditions})
),
eu_authors AS (
    SELECT wa.work_id, wa.institution_name, wa.country_code
    FROM openalex_work_authors wa
    JOIN semiconductor_works sw ON wa.work_id = sw.work_id
    WHERE ({eu_condition})
),
china_authors AS (
    SELECT wa.work_id, wa.institution_name, wa.country_code
    FROM openalex_work_authors wa
    JOIN semiconductor_works sw ON wa.work_id = sw.work_id
    WHERE wa.country_code = 'CN'
)
SELECT DISTINCT
    sw.work_id,
    sw.title,
    sw.publication_year,
    sw.doi,
    sw.primary_topic,
    sw.technology_domain,
    sw.keywords,
    sw.cited_by_count
FROM semiconductor_works sw
JOIN eu_authors ea ON sw.work_id = ea.work_id
JOIN china_authors ca ON sw.work_id = ca.work_id
WHERE sw.publication_year IS NOT NULL
ORDER BY sw.publication_year DESC, sw.cited_by_count DESC
LIMIT 5000
"""

print("Extracting up to 5,000 EU-China semiconductor collaboration papers...")
cursor.execute(query_collaboration_details)

collaboration_papers = []
for row in cursor.fetchall():
    collaboration_papers.append({
        'work_id': row[0],
        'title': row[1],
        'publication_year': row[2],
        'doi': row[3],
        'primary_topic': row[4],
        'technology_domain': row[5],
        'keywords': row[6],
        'cited_by_count': row[7]
    })

print(f"Extracted {len(collaboration_papers):,} collaboration papers\n")

# ============================================================================
# STEP 4: Time-series analysis
# ============================================================================

print("="*80)
print("STEP 4: Temporal Trend Analysis")
print("="*80 + "\n")

# Group by year
papers_by_year = defaultdict(int)
for paper in collaboration_papers:
    if paper['publication_year']:
        papers_by_year[paper['publication_year']] += 1

print("Year | Papers | Cumulative")
print("-" * 50)
cumulative = 0
for year in sorted(papers_by_year.keys()):
    count = papers_by_year[year]
    cumulative += count
    print(f"{year} | {count:>6,} | {cumulative:>10,}")

# ============================================================================
# STEP 5: Top EU countries collaborating with China
# ============================================================================

print("\n" + "="*80)
print("STEP 5: Top EU Countries in Semiconductor Collaboration with China")
print("="*80 + "\n")

# Get work IDs for EU-China collaborations
work_ids_str = ",".join([f"'{p['work_id']}'" for p in collaboration_papers[:1000]])  # Sample first 1000

if work_ids_str:
    query_eu_countries = f"""
    SELECT country_code, COUNT(DISTINCT work_id) as papers,
           GROUP_CONCAT(DISTINCT institution_name, ' | ') as institutions
    FROM openalex_work_authors
    WHERE work_id IN ({work_ids_str})
      AND ({eu_condition})
    GROUP BY country_code
    ORDER BY papers DESC
    """

    cursor.execute(query_eu_countries)
    print("Rank | Country | Papers | Sample Institutions")
    print("-" * 100)

    eu_country_data = []
    for idx, (country, papers, institutions) in enumerate(cursor.fetchall(), 1):
        # Truncate institutions list
        inst_list = institutions.split(' | ')[:3]
        inst_str = ', '.join(inst_list)
        if len(institutions.split(' | ')) > 3:
            inst_str += f", ... ({len(institutions.split(' | '))} total)"

        print(f"{idx:>3} | {country:>7} | {papers:>6,} | {inst_str[:80]}")

        eu_country_data.append({
            'rank': idx,
            'country_code': country,
            'collaboration_papers': papers,
            'sample_institutions': inst_list
        })

# ============================================================================
# STEP 6: Top Chinese institutions
# ============================================================================

print("\n" + "="*80)
print("STEP 6: Top Chinese Institutions in EU Semiconductor Collaborations")
print("="*80 + "\n")

if work_ids_str:
    query_chinese_institutions = f"""
    SELECT institution_name, COUNT(DISTINCT work_id) as papers
    FROM openalex_work_authors
    WHERE work_id IN ({work_ids_str})
      AND country_code = 'CN'
      AND institution_name IS NOT NULL
    GROUP BY institution_name
    ORDER BY papers DESC
    LIMIT 30
    """

    cursor.execute(query_chinese_institutions)
    print("Rank | Institution | Papers")
    print("-" * 100)

    chinese_institution_data = []
    for idx, (institution, papers) in enumerate(cursor.fetchall(), 1):
        inst_name = institution[:80] if institution else "Unknown"
        print(f"{idx:>3} | {inst_name:<80} | {papers:>6,}")

        chinese_institution_data.append({
            'rank': idx,
            'institution': institution,
            'collaboration_papers': papers
        })

# ============================================================================
# STEP 7: Technology domains and topics
# ============================================================================

print("\n" + "="*80)
print("STEP 7: Technology Domains and Research Topics")
print("="*80 + "\n")

# Count by technology domain
domains = defaultdict(int)
topics = defaultdict(int)

for paper in collaboration_papers:
    if paper['technology_domain']:
        domains[paper['technology_domain']] += 1
    if paper['primary_topic']:
        topics[paper['primary_topic']] += 1

print("Technology Domains:")
print("Domain | Papers")
print("-" * 60)
for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:15]:
    domain_name = domain[:50] if domain else "Unclassified"
    print(f"{domain_name:<50} | {count:>8,}")

print("\nTop Research Topics:")
print("Topic | Papers")
print("-" * 80)
for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:20]:
    topic_name = topic[:70] if topic else "Unclassified"
    print(f"{topic_name:<70} | {count:>8,}")

# ============================================================================
# STEP 8: Most cited papers
# ============================================================================

print("\n" + "="*80)
print("STEP 8: Most Cited EU-China Semiconductor Collaboration Papers")
print("="*80 + "\n")

# Sort by citations
top_cited = sorted(collaboration_papers, key=lambda x: x['cited_by_count'] or 0, reverse=True)[:20]

print("Rank | Citations | Year | Title")
print("-" * 120)
for idx, paper in enumerate(top_cited, 1):
    title = paper['title'][:80] if paper['title'] else "No title"
    year = paper['publication_year'] or "N/A"
    citations = paper['cited_by_count'] or 0
    print(f"{idx:>3} | {citations:>9,} | {year} | {title}")

# ============================================================================
# STEP 9: Save results
# ============================================================================

print("\n" + "="*80)
print("STEP 9: Saving Results")
print("="*80 + "\n")

os.makedirs(OUTPUT_DIR, exist_ok=True)

results = {
    'metadata': {
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'database': DB_PATH,
        'total_semiconductor_works': total_semiconductor_works,
        'eu_china_collaboration_papers': eu_china_semiconductor_collabs,
        'papers_extracted': len(collaboration_papers),
        'keywords_used': core_semiconductor_keywords,
        'eu_countries_analyzed': EU27_COUNTRIES,
        'zero_fabrication_compliant': True,
        'source': 'OpenAlex Research Database'
    },
    'temporal_analysis': {
        'papers_by_year': dict(papers_by_year),
        'earliest_year': min(papers_by_year.keys()) if papers_by_year else None,
        'latest_year': max(papers_by_year.keys()) if papers_by_year else None
    },
    'geographic_analysis': {
        'top_eu_countries': eu_country_data[:20],
        'top_chinese_institutions': chinese_institution_data[:30]
    },
    'technology_analysis': {
        'domains': dict(sorted(domains.items(), key=lambda x: x[1], reverse=True)[:20]),
        'topics': dict(sorted(topics.items(), key=lambda x: x[1], reverse=True)[:30])
    },
    'top_cited_papers': [{
        'rank': idx + 1,
        'title': p['title'],
        'year': p['publication_year'],
        'citations': p['cited_by_count'],
        'doi': p['doi'],
        'topic': p['primary_topic']
    } for idx, p in enumerate(top_cited[:50])],
    'sample_papers': collaboration_papers[:100]  # First 100 papers
}

output_file = f"{OUTPUT_DIR}/eu_china_semiconductor_collaborations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Results saved to: {output_file}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("ANALYSIS SUMMARY")
print("="*80 + "\n")

print(f"OpenAlex Semiconductor Research Analysis:")
print(f"  Total semiconductor works in database: {total_semiconductor_works:,}")
print(f"  EU-China collaboration papers: {eu_china_semiconductor_collabs:,}")

if papers_by_year:
    earliest = min(papers_by_year.keys())
    latest = max(papers_by_year.keys())
    print(f"  Date range: {earliest}-{latest}")
    print(f"  Average papers/year: {sum(papers_by_year.values()) / len(papers_by_year):.0f}")

if eu_country_data:
    print(f"\nTop 3 EU Countries:")
    for i in range(min(3, len(eu_country_data))):
        country = eu_country_data[i]
        print(f"  {i+1}. {country['country_code']}: {country['collaboration_papers']:,} papers")

if chinese_institution_data:
    print(f"\nTop 3 Chinese Institutions:")
    for i in range(min(3, len(chinese_institution_data))):
        inst = chinese_institution_data[i]
        inst_name = inst['institution'][:60] if inst['institution'] else "Unknown"
        print(f"  {i+1}. {inst_name}: {inst['collaboration_papers']:,} papers")

if top_cited:
    print(f"\nMost Cited Paper:")
    top = top_cited[0]
    title = top['title'][:80] if top['title'] else "No title"
    print(f"  Title: {title}")
    print(f"  Year: {top['publication_year']}")
    print(f"  Citations: {top['cited_by_count']:,}")

conn.close()

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
