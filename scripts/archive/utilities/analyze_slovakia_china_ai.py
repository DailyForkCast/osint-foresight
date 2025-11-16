import sqlite3
import json
import sys
import io
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Connect to database
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

print("SLOVAKIA-CHINA AI COLLABORATIONS - DEEP DIVE ANALYSIS")
print("=" * 90)

# Query using only columns that exist
query = """
SELECT DISTINCT
    w.work_id,
    w.title,
    w.publication_year,
    w.publication_date,
    w.cited_by_count,
    w.type
FROM openalex_works w
WHERE w.work_id IN (
    -- Works with both Slovak and Chinese authors
    SELECT DISTINCT wa1.work_id
    FROM openalex_work_authors wa1
    JOIN openalex_work_authors wa2 ON wa1.work_id = wa2.work_id
    WHERE wa1.country_code = 'SK'
    AND wa2.country_code = 'CN'
)
AND (
    -- AI-related keywords in title
    LOWER(w.title) LIKE '%artificial intelligence%'
    OR LOWER(w.title) LIKE '%machine learning%'
    OR LOWER(w.title) LIKE '%deep learning%'
    OR LOWER(w.title) LIKE '%neural network%'
    OR LOWER(w.title) LIKE '%computer vision%'
    OR LOWER(w.title) LIKE '%natural language%'
    OR LOWER(w.title) LIKE '%data mining%'
    OR LOWER(w.title) LIKE '%pattern recognition%'
    OR LOWER(w.title) LIKE '%robotics%'
    OR LOWER(w.title) LIKE '%classification%'
    OR LOWER(w.title) LIKE '%algorithm%'
    OR LOWER(w.title) LIKE '%optimization%'
    OR LOWER(w.title) LIKE '%prediction%'
    OR LOWER(w.title) LIKE '%clustering%'
    OR LOWER(w.title) LIKE '%regression%'
)
ORDER BY w.publication_year DESC, w.cited_by_count DESC
"""

cursor.execute(query)
results = cursor.fetchall()

print(f"\nFound {len(results)} Slovakia-China AI-related collaborative works\n")

# Collect data for analysis
works_by_year = defaultdict(list)
all_works = []

for row in results:
    work_id, title, year, date, citations, work_type = row

    work_data = {
        'work_id': work_id,
        'title': title,
        'year': year,
        'date': date,
        'citations': citations or 0,
        'type': work_type or ''
    }
    all_works.append(work_data)

    if year:
        works_by_year[year].append(work_data)

print("\n" + "=" * 90)
print("TEMPORAL TREND ANALYSIS")
print("=" * 90)

years_sorted = sorted(works_by_year.keys())
if years_sorted:
    print(f"\nYear Range: {years_sorted[0]} - {years_sorted[-1]}")
    print("\nCollaborations by Year:")
    print("-" * 90)

    for year in years_sorted:
        count = len(works_by_year[year])
        total_citations = sum(w['citations'] for w in works_by_year[year])
        avg_citations = total_citations / count if count > 0 else 0
        bar = "█" * min(int(count / 2), 40)
        print(f"  {year}: {count:3d} works | {total_citations:4d} citations | {avg_citations:5.1f} avg | {bar}")

    # Recent trend
    if len(years_sorted) >= 5:
        recent_5_years = years_sorted[-5:]
        recent_count = sum(len(works_by_year[y]) for y in recent_5_years)
        older_count = len(results) - recent_count
        print(f"\nRecent 5 years ({recent_5_years[0]}-{recent_5_years[-1]}): {recent_count} works ({recent_count/len(results)*100:.1f}%)")
        print(f"Older works: {older_count} ({older_count/len(results)*100:.1f}%)")
else:
    print("\nNo temporal data available")

print("\n" + "=" * 90)
print("AI SUB-AREA ANALYSIS (from titles)")
print("=" * 90)

# Analyze AI sub-areas from titles
ai_keywords = {
    'Machine Learning': ['machine learning', 'supervised learning', 'unsupervised learning'],
    'Deep Learning': ['deep learning', 'neural network', 'cnn', 'convolutional'],
    'Computer Vision': ['computer vision', 'image', 'visual', 'object detection'],
    'Natural Language Processing': ['natural language', 'nlp', 'text mining', 'sentiment'],
    'Robotics': ['robot', 'robotic', 'autonomous'],
    'Optimization': ['optimization', 'genetic algorithm'],
    'Classification': ['classification', 'classifier'],
    'Clustering': ['clustering', 'cluster analysis'],
    'Data Mining': ['data mining', 'knowledge discovery'],
    'Pattern Recognition': ['pattern recognition'],
    'Prediction/Forecasting': ['prediction', 'forecasting', 'prognosis'],
    'Recommendation Systems': ['recommendation', 'recommender']
}

area_counts = defaultdict(list)
for work in all_works:
    title_lower = work['title'].lower() if work['title'] else ''
    for area, keywords in ai_keywords.items():
        if any(kw in title_lower for kw in keywords):
            area_counts[area].append(work)

print("\nAI Sub-Areas (inferred from titles):")
print("-" * 90)
area_list = [(area, len(works)) for area, works in area_counts.items()]
area_list.sort(key=lambda x: x[1], reverse=True)

for i, (area, count) in enumerate(area_list, 1):
    pct = count / len(results) * 100
    print(f"{i:2d}. {area:35s}: {count:3d} works ({pct:4.1f}%)")

# Sample high-impact titles
print("\n" + "=" * 90)
print("SAMPLE HIGH-IMPACT WORKS (>10 citations)")
print("=" * 90)

high_impact = sorted([w for w in all_works if w['citations'] > 10],
                     key=lambda x: x['citations'], reverse=True)

for i, work in enumerate(high_impact[:10], 1):
    print(f"\n{i}. {work['title'][:80]}")
    print(f"   Year: {work['year']} | Citations: {work['citations']} | ID: {work['work_id']}")

print("\n" + "=" * 90)
print("INSTITUTIONAL COLLABORATION ANALYSIS")
print("=" * 90)

if all_works:
    work_ids_str = ','.join([f"'{w['work_id']}'" for w in all_works])

    institution_query = f"""
    SELECT
        wa.institution_name,
        wa.country_code,
        COUNT(DISTINCT wa.work_id) as work_count,
        COUNT(DISTINCT CASE WHEN w.cited_by_count > 10 THEN wa.work_id END) as high_impact_works
    FROM openalex_work_authors wa
    JOIN openalex_works w ON wa.work_id = w.work_id
    WHERE wa.work_id IN ({work_ids_str})
    AND wa.country_code IN ('SK', 'CN')
    AND wa.institution_name IS NOT NULL
    GROUP BY wa.institution_name, wa.country_code
    ORDER BY work_count DESC
    LIMIT 40
    """

    cursor.execute(institution_query)
    institutions = cursor.fetchall()

    print("\nSlovak Institutions (AI Collaborations with China):")
    print("-" * 90)
    slovak_insts = [(name, count, high_impact) for name, cc, count, high_impact in institutions if cc == 'SK']
    for i, (name, count, high_impact) in enumerate(slovak_insts[:15], 1):
        pct = count / len(results) * 100
        print(f"{i:2d}. {name[:50]:50s}: {count:3d} ({pct:4.1f}%) | {high_impact:2d} high-impact")

    print("\nChinese Partner Institutions:")
    print("-" * 90)
    chinese_insts = [(name, count, high_impact) for name, cc, count, high_impact in institutions if cc == 'CN']
    for i, (name, count, high_impact) in enumerate(chinese_insts[:20], 1):
        pct = count / len(results) * 100
        print(f"{i:2d}. {name[:50]:50s}: {count:3d} ({pct:4.1f}%) | {high_impact:2d} high-impact")

conn.close()

# Save detailed data
output_data = {
    "metadata": {
        "query_date": "2025-11-10",
        "total_works": len(results),
        "year_range": f"{years_sorted[0]}-{years_sorted[-1]}" if years_sorted else "N/A",
        "data_source": "F:/OSINT_WAREHOUSE/osint_master.db (OpenAlex)"
    },
    "temporal_analysis": {
        "by_year": {str(year): len(works_by_year[year]) for year in years_sorted}
    },
    "ai_subareas": [{"area": area, "count": count} for area, count in area_list],
    "slovak_institutions": [{"name": name, "works": count, "high_impact": hi} for name, count, hi in slovak_insts],
    "chinese_institutions": [{"name": name, "works": count, "high_impact": hi} for name, count, hi in chinese_insts],
    "sample_works": all_works[:100]
}

with open('C:/Projects/OSINT-Foresight/analysis/SLOVAKIA_CHINA_AI_DEEP_DIVE_20251110.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 90)
print(f"\nDetailed data saved to: analysis/SLOVAKIA_CHINA_AI_DEEP_DIVE_20251110.json")
print(f"Total Slovakia-China AI collaborations identified: {len(results)}")
print("\nNote: CSET reports 32 Slovakia-China AI articles (2022)")
print(f"OpenAlex query found: {len(results)} AI-related collaborations")
