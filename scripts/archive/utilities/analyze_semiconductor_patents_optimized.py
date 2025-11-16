"""
USPTO Semiconductor Patent Analysis - OPTIMIZED VERSION
Analyzes Chinese semiconductor patents with optimized queries
Zero Fabrication Protocol: All data from USPTO database
"""

import sqlite3
import json
from datetime import datetime
import os

DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'
OUTPUT_DIR = 'C:/Projects/OSINT-Foresight/analysis/patents'

print("="*80)
print("USPTO SEMICONDUCTOR PATENT ANALYSIS (OPTIMIZED)")
print("="*80)
print(f"Database: {DB_PATH}")
print("")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ============================================================================
# STEP 1: Get semiconductor application numbers (filter CPC first)
# ============================================================================

print("Step 1: Filtering semiconductor patents from CPC classifications...")

# Create temporary table of semiconductor app numbers (much faster)
cursor.execute("""
CREATE TEMP TABLE IF NOT EXISTS temp_semiconductor_apps AS
SELECT DISTINCT application_number
FROM uspto_cpc_classifications
WHERE cpc_full LIKE 'H01L%' OR cpc_full LIKE 'G11C%' OR cpc_full LIKE 'H03K%'
""")

cursor.execute("SELECT COUNT(*) FROM temp_semiconductor_apps")
semiconductor_apps_count = cursor.fetchone()[0]
print(f"  Found {semiconductor_apps_count:,} unique semiconductor applications\n")

# ============================================================================
# STEP 2: Get Chinese semiconductor patents
# ============================================================================

print("Step 2: Identifying Chinese semiconductor patents...")

cursor.execute("""
SELECT COUNT(DISTINCT cp.application_number)
FROM uspto_patents_chinese cp
WHERE EXISTS (
    SELECT 1 FROM temp_semiconductor_apps sa
    WHERE sa.application_number = cp.application_number
)
""")

chinese_semiconductor = cursor.fetchone()[0]
print(f"  Chinese semiconductor patents: {chinese_semiconductor:,}\n")

# ============================================================================
# STEP 3: Time-series analysis (simplified)
# ============================================================================

print("="*80)
print("TIME-SERIES ANALYSIS: Chinese Semiconductor Patents by Year")
print("="*80)

cursor.execute("""
SELECT
    cp.year,
    COUNT(DISTINCT cp.application_number) as patent_count
FROM uspto_patents_chinese cp
WHERE EXISTS (
    SELECT 1 FROM temp_semiconductor_apps sa
    WHERE sa.application_number = cp.application_number
)
AND cp.year IS NOT NULL
AND cp.year BETWEEN 2000 AND 2025
GROUP BY cp.year
ORDER BY cp.year
""")

timeseries_data = []
print("\nYear | Patents | YoY Change")
print("-" * 50)

prev_count = None
for row in cursor.fetchall():
    year = row[0]
    count = row[1]

    if prev_count:
        yoy_change = count - prev_count
        yoy_pct = (yoy_change / prev_count * 100) if prev_count > 0 else 0
        change_str = f"{yoy_change:+,} ({yoy_pct:+.1f}%)"
    else:
        change_str = "baseline"

    print(f"{year} | {count:>6,} | {change_str}")

    timeseries_data.append({
        'year': year,
        'patent_count': count,
        'yoy_change': (count - prev_count) if prev_count else 0
    })

    prev_count = count

# ============================================================================
# STEP 4: Top assignees
# ============================================================================

print("\n" + "="*80)
print("TOP CHINESE ASSIGNEES IN SEMICONDUCTOR")
print("="*80)

cursor.execute("""
SELECT
    cp.assignee_name,
    COUNT(DISTINCT cp.application_number) as patent_count,
    MIN(cp.year) as first_year,
    MAX(cp.year) as last_year
FROM uspto_patents_chinese cp
WHERE EXISTS (
    SELECT 1 FROM temp_semiconductor_apps sa
    WHERE sa.application_number = cp.application_number
)
AND cp.assignee_name IS NOT NULL
AND cp.assignee_name != ''
GROUP BY cp.assignee_name
HAVING patent_count >= 50
ORDER BY patent_count DESC
LIMIT 30
""")

assignee_data = []
print("\nRank | Assignee | Patents | First-Last Year")
print("-" * 90)

for idx, row in enumerate(cursor.fetchall(), 1):
    assignee = row[0][:50]
    count = row[1]
    first_year = row[2]
    last_year = row[3]

    print(f"{idx:>3} | {assignee:<50} | {count:>6,} | {first_year}-{last_year}")

    assignee_data.append({
        'rank': idx,
        'assignee': row[0],
        'patent_count': count,
        'first_year': first_year,
        'last_year': last_year
    })

# ============================================================================
# STEP 5: Technology breakdown (by CPC main group)
# ============================================================================

print("\n" + "="*80)
print("TECHNOLOGY BREAKDOWN (by CPC Code)")
print("="*80)

cursor.execute("""
SELECT
    SUBSTR(cpc.cpc_full, 1, 7) as cpc_code,
    COUNT(DISTINCT cp.application_number) as patent_count
FROM uspto_cpc_classifications cpc
JOIN uspto_patents_chinese cp ON cpc.application_number = cp.application_number
WHERE (cpc.cpc_full LIKE 'H01L%' OR cpc.cpc_full LIKE 'G11C%' OR cpc.cpc_full LIKE 'H03K%')
GROUP BY cpc_code
HAVING patent_count >= 100
ORDER BY patent_count DESC
LIMIT 20
""")

tech_data = []
print("\nCPC Code | Description | Patents")
print("-" * 80)

# Simple descriptions for main codes
CPC_DESCRIPTIONS = {
    'H01L 21': 'Semiconductor Manufacturing',
    'H01L 23': 'Device Packaging',
    'H01L 27': 'Integrated Circuits',
    'H01L 29': 'Semiconductor Devices',
    'H01L 31': 'Photovoltaic Devices',
    'G11C 11': 'DRAM Memory',
    'G11C 16': 'Flash Memory',
    'H03K 19': 'Logic Circuits'
}

for row in cursor.fetchall():
    cpc_code = row[0]
    count = row[1]
    desc = CPC_DESCRIPTIONS.get(cpc_code, 'Other Semiconductor')

    print(f"{cpc_code:<8} | {desc:<30} | {count:>7,}")

    tech_data.append({
        'cpc_code': cpc_code,
        'description': desc,
        'patent_count': count
    })

# ============================================================================
# STEP 6: Recent trends (2020-2025)
# ============================================================================

print("\n" + "="*80)
print("RECENT TRENDS (2020-2025)")
print("="*80)

cursor.execute("""
SELECT
    cp.year,
    COUNT(DISTINCT cp.application_number) as total,
    COUNT(DISTINCT CASE WHEN cp.assignee_name LIKE '%SMIC%' THEN cp.application_number END) as smic,
    COUNT(DISTINCT CASE WHEN cp.assignee_name LIKE '%Huawei%' OR cp.assignee_name LIKE '%HiSilicon%' THEN cp.application_number END) as huawei,
    COUNT(DISTINCT CASE WHEN cp.assignee_name LIKE '%BOE%' THEN cp.application_number END) as boe
FROM uspto_patents_chinese cp
WHERE EXISTS (
    SELECT 1 FROM temp_semiconductor_apps sa
    WHERE sa.application_number = cp.application_number
)
AND cp.year >= 2020
GROUP BY cp.year
ORDER BY cp.year
""")

recent_data = []
print("\nYear | Total | SMIC | Huawei | BOE")
print("-" * 50)

for row in cursor.fetchall():
    year = row[0]
    total = row[1]
    smic = row[2]
    huawei = row[3]
    boe = row[4]

    print(f"{year} | {total:>5,} | {smic:>4,} | {huawei:>6,} | {boe:>3,}")

    recent_data.append({
        'year': year,
        'total': total,
        'smic': smic,
        'huawei': huawei,
        'boe': boe
    })

# ============================================================================
# STEP 7: Key technology keywords
# ============================================================================

print("\n" + "="*80)
print("ADVANCED TECHNOLOGY KEYWORDS IN TITLES")
print("="*80)

keywords = {
    'Lithography': '%lithograph%',
    'EUV': '%EUV%',
    'FinFET': '%FinFET%',
    'GAA': '%gate%around%',
    '3D Packaging': '%3D%packag%',
    'Chiplet': '%chiplet%',
    '3D NAND': '%3D%NAND%',
    'MRAM': '%MRAM%',
    'AI Chip': '%AI%chip%',
    'Neural': '%neural%network%'
}

keyword_results = {}
print("\nKeyword | Patents")
print("-" * 40)

for keyword, pattern in keywords.items():
    cursor.execute(f"""
    SELECT COUNT(DISTINCT cp.application_number)
    FROM uspto_patents_chinese cp
    WHERE EXISTS (
        SELECT 1 FROM temp_semiconductor_apps sa
        WHERE sa.application_number = cp.application_number
    )
    AND cp.title LIKE '{pattern}'
    """)
    count = cursor.fetchone()[0]
    keyword_results[keyword] = count
    print(f"{keyword:<20} | {count:>6,}")

# ============================================================================
# STEP 8: Save results
# ============================================================================

print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

os.makedirs(OUTPUT_DIR, exist_ok=True)

results = {
    'metadata': {
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'database': DB_PATH,
        'total_semiconductor_applications': semiconductor_apps_count,
        'chinese_semiconductor_patents': chinese_semiconductor,
        'zero_fabrication_compliant': True,
        'source': 'USPTO Patent Database'
    },
    'timeseries': timeseries_data,
    'top_assignees': assignee_data,
    'technology_breakdown': tech_data,
    'recent_trends': recent_data,
    'advanced_technology_keywords': keyword_results
}

output_file = f"{OUTPUT_DIR}/chinese_semiconductor_patents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_file}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("ANALYSIS SUMMARY")
print("="*80)

if timeseries_data:
    first_year_data = timeseries_data[0]
    last_year_data = timeseries_data[-1]
    total_patents = sum([d['patent_count'] for d in timeseries_data])

    print(f"\nChinese Semiconductor Patents {first_year_data['year']}-{last_year_data['year']}:")
    print(f"  Total patents: {total_patents:,}")
    print(f"  {first_year_data['year']}: {first_year_data['patent_count']:,} patents")
    print(f"  {last_year_data['year']}: {last_year_data['patent_count']:,} patents")

    growth = last_year_data['patent_count'] - first_year_data['patent_count']
    growth_pct = (growth / first_year_data['patent_count'] * 100) if first_year_data['patent_count'] > 0 else 0
    print(f"  Growth: {growth:+,} patents ({growth_pct:+.1f}%)")

if assignee_data:
    print(f"\nTop Assignee: {assignee_data[0]['assignee']}")
    print(f"  Patents: {assignee_data[0]['patent_count']:,}")
    print(f"  Active: {assignee_data[0]['first_year']}-{assignee_data[0]['last_year']}")

print("\nMost Active Advanced Technology Keywords:")
sorted_keywords = sorted(keyword_results.items(), key=lambda x: x[1], reverse=True)[:5]
for keyword, count in sorted_keywords:
    print(f"  {keyword}: {count:,} patents")

# Cleanup
cursor.execute("DROP TABLE IF EXISTS temp_semiconductor_apps")
conn.close()

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
