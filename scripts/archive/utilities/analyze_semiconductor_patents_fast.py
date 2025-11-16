"""
USPTO Semiconductor Patent Analysis - FAST VERSION
Analyzes Chinese patents with semiconductor keywords (no CPC join required)
Zero Fabrication Protocol: All data from USPTO database
"""

import sqlite3
import json
from datetime import datetime
import os

DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'
OUTPUT_DIR = 'C:/Projects/OSINT-Foresight/analysis/patents'

print("="*80)
print("USPTO SEMICONDUCTOR PATENT ANALYSIS - FAST VERSION")
print("="*80)
print(f"Database: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ============================================================================
# Semiconductor keyword patterns (broad coverage)
# ============================================================================

SEMICONDUCTOR_KEYWORDS = [
    '%semiconductor%',
    '%chip%',
    '%integrated circuit%',
    '% IC %',
    '%CMOS%',
    '%FinFET%',
    '%transistor%',
    '%wafer%',
    '%fab%',
    '%lithography%',
    '%DRAM%',
    '%NAND%',
    '%flash memory%',
    '%SRAM%',
    '%memory%device%',
    '%gate%oxide%',
    '%silicon%dioxide%',
    '%dielectric%',
    '%etching%',
    '%deposition%',
    '%photoresist%',
    '%EUV%',
    '%nanometer%',
    '% nm %',
    '%package%substrate%',
    '%die%bonding%',
    '%TSV%',  # Through-Silicon Via
    '%3D%packag%',
    '%chiplet%',
    '%SoC%',  # System on Chip
    '%ASIC%',
    '%FPGA%'
]

# Build WHERE clause
where_conditions = ' OR '.join([f"title LIKE '{kw}'" for kw in SEMICONDUCTOR_KEYWORDS])

# ============================================================================
# STEP 1: Count semiconductor patents
# ============================================================================

print("Step 1: Identifying semiconductor patents by title keywords...\n")

query = f"""
SELECT COUNT(DISTINCT application_number)
FROM uspto_patents_chinese
WHERE {where_conditions}
"""

cursor.execute(query)
total_semiconductor = cursor.fetchone()[0]
print(f"  Total Chinese semiconductor patents (by keywords): {total_semiconductor:,}\n")

# ============================================================================
# STEP 2: Time-series analysis
# ============================================================================

print("="*80)
print("TIME-SERIES ANALYSIS (2000-2025)")
print("="*80)

query = f"""
SELECT
    year,
    COUNT(DISTINCT application_number) as patent_count
FROM uspto_patents_chinese
WHERE ({where_conditions})
  AND year IS NOT NULL
  AND year BETWEEN 2000 AND 2025
GROUP BY year
ORDER BY year
"""

cursor.execute(query)

timeseries_data = []
print("\nYear | Patents | YoY Change")
print("-" * 60)

prev_count = None
for row in cursor.fetchall():
    year = row[0]
    count = row[1]

    if prev_count:
        yoy_change = count - prev_count
        yoy_pct = (yoy_change / prev_count * 100) if prev_count > 0 else 0
        change_str = f"{yoy_change:+6,} ({yoy_pct:+6.1f}%)"
    else:
        change_str = "baseline"

    print(f"{year} | {count:>7,} | {change_str}")

    timeseries_data.append({
        'year': year,
        'patent_count': count,
        'yoy_change': (count - prev_count) if prev_count else 0,
        'yoy_pct': ((count - prev_count) / prev_count * 100) if prev_count else 0
    })

    prev_count = count

# ============================================================================
# STEP 3: Top assignees
# ============================================================================

print("\n" + "="*80)
print("TOP ASSIGNEES IN SEMICONDUCTOR")
print("="*80)

query = f"""
SELECT
    assignee_name,
    COUNT(DISTINCT application_number) as patent_count,
    MIN(year) as first_year,
    MAX(year) as last_year
FROM uspto_patents_chinese
WHERE ({where_conditions})
  AND assignee_name IS NOT NULL
  AND assignee_name != ''
GROUP BY assignee_name
HAVING patent_count >= 20
ORDER BY patent_count DESC
LIMIT 50
"""

cursor.execute(query)

assignee_data = []
print("\nRank | Assignee | Patents | Years")
print("-" * 90)

for idx, row in enumerate(cursor.fetchall(), 1):
    assignee = row[0][:55]
    count = row[1]
    first_year = row[2]
    last_year = row[3]

    print(f"{idx:>3} | {assignee:<55} | {count:>6,} | {first_year}-{last_year}")

    assignee_data.append({
        'rank': idx,
        'assignee': row[0],
        'patent_count': count,
        'first_year': first_year,
        'last_year': last_year
    })

# ============================================================================
# STEP 4: Technology keywords breakdown
# ============================================================================

print("\n" + "="*80)
print("TECHNOLOGY KEYWORD BREAKDOWN")
print("="*80)

tech_keywords = {
    'Memory (DRAM/NAND/Flash)': "title LIKE '%DRAM%' OR title LIKE '%NAND%' OR title LIKE '%flash memory%' OR title LIKE '%SRAM%'",
    'Manufacturing Process': "title LIKE '%lithography%' OR title LIKE '%etching%' OR title LIKE '%deposition%' OR title LIKE '%photoresist%'",
    'Advanced Transistors': "title LIKE '%FinFET%' OR title LIKE '%gate%around%' OR title LIKE '%transistor%'",
    'Packaging': "title LIKE '%package%' OR title LIKE '%TSV%' OR title LIKE '%3D%packag%' OR title LIKE '%chiplet%'",
    'Logic/Design': "title LIKE '%ASIC%' OR title LIKE '%FPGA%' OR title LIKE '%SoC%' OR title LIKE '%logic%circuit%'",
    'Advanced Nodes': "title LIKE '%nanometer%' OR title LIKE '% nm %' OR title LIKE '%EUV%'",
    'AI/ML Chips': "title LIKE '%neural%' OR title LIKE '%AI%chip%' OR title LIKE '%machine learning%'",
    'Materials': "title LIKE '%silicon%dioxide%' OR title LIKE '%dielectric%' OR title LIKE '%gate%oxide%'"
}

tech_breakdown = {}
print("\nTechnology Area | Patents")
print("-" * 60)

for tech_name, condition in tech_keywords.items():
    query = f"""
    SELECT COUNT(DISTINCT application_number)
    FROM uspto_patents_chinese
    WHERE {condition}
    AND ({where_conditions})
    """

    cursor.execute(query)
    count = cursor.fetchone()[0]
    tech_breakdown[tech_name] = count
    print(f"{tech_name:<35} | {count:>8,}")

# ============================================================================
# STEP 5: Recent trends (2020-2025) - Major Chinese companies
# ============================================================================

print("\n" + "="*80)
print("RECENT TRENDS (2020-2025) - Major Chinese Semiconductor Companies")
print("="*80)

companies = {
    'SMIC': "assignee_name LIKE '%SMIC%' OR assignee_name LIKE '%Semiconductor Manufacturing International%'",
    'Huawei/HiSilicon': "assignee_name LIKE '%Huawei%' OR assignee_name LIKE '%HiSilicon%'",
    'YMTC': "assignee_name LIKE '%YMTC%' OR assignee_name LIKE '%Yangtze%Memory%'",
    'BOE': "assignee_name LIKE '%BOE%'",
    'CXMT': "assignee_name LIKE '%ChangXin%' OR assignee_name LIKE '%CXMT%'",
    'Alibaba': "assignee_name LIKE '%Alibaba%' OR assignee_name LIKE '%T-Head%'",
    'Tencent': "assignee_name LIKE '%Tencent%'",
    'Baidu': "assignee_name LIKE '%Baidu%'"
}

recent_company_data = {}

for company_name, condition in companies.items():
    query = f"""
    SELECT year, COUNT(DISTINCT application_number) as count
    FROM uspto_patents_chinese
    WHERE ({condition})
      AND ({where_conditions})
      AND year >= 2020
    GROUP BY year
    ORDER BY year
    """

    cursor.execute(query)
    company_data = {row[0]: row[1] for row in cursor.fetchall()}
    recent_company_data[company_name] = company_data

print("\n     | " + " | ".join([f"{name:>8}" for name in companies.keys()]))
print("-" * 110)

for year in range(2020, 2026):
    row_data = [f"{year}"]
    for company_name in companies.keys():
        count = recent_company_data[company_name].get(year, 0)
        row_data.append(f"{count:>8,}")
    print(" | ".join(row_data))

# ============================================================================
# STEP 6: Advanced technology detection
# ============================================================================

print("\n" + "="*80)
print("ADVANCED TECHNOLOGY INDICATORS")
print("="*80)

advanced_tech = {
    'EUV Lithography': '%EUV%',
    'Extreme Ultraviolet': '%extreme%ultraviolet%',
    'FinFET': '%FinFET%',
    'Gate-All-Around (GAA)': '%gate%around%',
    '3nm or smaller': '%3nm%',
    '5nm process': '%5nm%',
    '7nm process': '%7nm%',
    '3D NAND': '%3D%NAND%',
    'MRAM': '%MRAM%',
    'ReRAM': '%ReRAM%',
    'Chiplet': '%chiplet%',
    'AI Accelerator': '%AI%accelerat%',
    'Neural Processing': '%neural%process%',
    'Quantum': '%quantum%'
}

advanced_results = {}
print("\nAdvanced Technology | Patents")
print("-" * 60)

for tech_name, pattern in advanced_tech.items():
    query = f"""
    SELECT COUNT(DISTINCT application_number)
    FROM uspto_patents_chinese
    WHERE title LIKE '{pattern}'
    """

    cursor.execute(query)
    count = cursor.fetchone()[0]
    advanced_results[tech_name] = count
    print(f"{tech_name:<30} | {count:>8,}")

# ============================================================================
# STEP 7: Export control era comparison (pre/post 2022)
# ============================================================================

print("\n" + "="*80)
print("EXPORT CONTROL ERA COMPARISON")
print("="*80)

query = f"""
SELECT
    CASE
        WHEN year < 2019 THEN 'Pre-Trade War (2000-2018)'
        WHEN year BETWEEN 2019 AND 2021 THEN 'Trade War Era (2019-2021)'
        WHEN year >= 2022 THEN 'CHIPS Act Era (2022+)'
    END as era,
    COUNT(DISTINCT application_number) as patents
FROM uspto_patents_chinese
WHERE ({where_conditions})
  AND year IS NOT NULL
  AND year BETWEEN 2000 AND 2025
GROUP BY era
ORDER BY MIN(year)
"""

cursor.execute(query)

print("\nEra | Patents | Avg/Year")
print("-" * 60)

for row in cursor.fetchall():
    era = row[0]
    patents = row[1]

    if 'Pre-Trade' in era:
        years = 19  # 2000-2018
    elif 'Trade War' in era:
        years = 3   # 2019-2021
    else:  # CHIPS Act
        years = 4   # 2022-2025

    avg_per_year = patents / years

    print(f"{era:<30} | {patents:>7,} | {avg_per_year:>8,.0f}")

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
        'method': 'Title keyword matching (H01L, G11C, H03K equivalents)',
        'total_semiconductor_patents': total_semiconductor,
        'zero_fabrication_compliant': True,
        'source': 'USPTO Patent Database',
        'note': 'Fast analysis using title keywords. CPC validation available separately.'
    },
    'timeseries_2000_2025': timeseries_data,
    'top_50_assignees': assignee_data,
    'technology_breakdown': tech_breakdown,
    'recent_company_trends_2020_2025': recent_company_data,
    'advanced_technology_indicators': advanced_results
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
    first_year = timeseries_data[0]
    last_year = timeseries_data[-1]
    total_patents = sum([d['patent_count'] for d in timeseries_data])

    print(f"\nChinese Semiconductor Patents ({first_year['year']}-{last_year['year']}):")
    print(f"  Total: {total_patents:,}")
    print(f"  {first_year['year']}: {first_year['patent_count']:,}")
    print(f"  {last_year['year']}: {last_year['patent_count']:,}")

    growth = last_year['patent_count'] - first_year['patent_count']
    growth_pct = (growth / first_year['patent_count'] * 100) if first_year['patent_count'] > 0 else 0
    print(f"  Growth: {growth:+,} ({growth_pct:+.0f}%)")

    # Find peak year
    peak_year = max(timeseries_data, key=lambda x: x['patent_count'])
    print(f"  Peak year: {peak_year['year']} with {peak_year['patent_count']:,} patents")

if assignee_data:
    print(f"\nTop 5 Assignees:")
    for i in range(min(5, len(assignee_data))):
        assignee = assignee_data[i]
        print(f"  {i+1}. {assignee['assignee']}: {assignee['patent_count']:,} patents")

print(f"\nMost Common Technology: {max(tech_breakdown, key=tech_breakdown.get)}")
print(f"  Patents: {tech_breakdown[max(tech_breakdown, key=tech_breakdown.get)]:,}")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)

conn.close()
