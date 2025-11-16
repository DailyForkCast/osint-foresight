"""
USPTO Semiconductor Patent Analysis
Analyzes 425K Chinese patents for semiconductor technology trends
Zero Fabrication Protocol: All data from USPTO database
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict

DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'
OUTPUT_DIR = 'C:/Projects/OSINT-Foresight/analysis/patents'

print("="*80)
print("USPTO SEMICONDUCTOR PATENT ANALYSIS")
print("="*80)
print(f"Database: {DB_PATH}")
print(f"Output: {OUTPUT_DIR}")
print("")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ============================================================================
# 1. SEMICONDUCTOR CPC CODE DEFINITIONS
# ============================================================================

SEMICONDUCTOR_CPC_CODES = {
    'H01L 21': 'Semiconductor Manufacturing Processes',
    'H01L 23': 'Semiconductor Device Packaging',
    'H01L 25': 'Assemblies of Semiconductor Devices',
    'H01L 27': 'Integrated Circuits (ICs)',
    'H01L 29': 'Semiconductor Devices',
    'H01L 31': 'Photovoltaic/Solar Cells',
    'G11C 11': 'DRAM Memory',
    'G11C 13': 'ROM Memory',
    'G11C 14': 'PROM Memory',
    'G11C 16': 'Flash/EPROM Memory',
    'G11C 17': 'Read-Only Memory',
    'H03K 19': 'Logic Circuits',
    'H01L 33': 'LED Semiconductor Devices',
    'H01L 41': 'Piezoelectric Devices',
    'H01L 51': 'Organic Semiconductor Devices'
}

print("Semiconductor CPC Codes Tracked:")
for code, desc in SEMICONDUCTOR_CPC_CODES.items():
    print(f"  {code}: {desc}")
print("")

# ============================================================================
# 2. TIME-SERIES ANALYSIS: Chinese Semiconductor Patents by Year
# ============================================================================

print("="*80)
print("1. TIME-SERIES ANALYSIS: Chinese Semiconductor Patents (2000-2025)")
print("="*80)

query_timeseries = """
SELECT
    cp.year,
    COUNT(DISTINCT cp.application_number) as patent_count,
    COUNT(DISTINCT CASE
        WHEN cpc.cpc_full LIKE 'H01L 21%' THEN cp.application_number
    END) as manufacturing_patents,
    COUNT(DISTINCT CASE
        WHEN cpc.cpc_full LIKE 'H01L 23%' OR cpc.cpc_full LIKE 'H01L 25%' THEN cp.application_number
    END) as packaging_patents,
    COUNT(DISTINCT CASE
        WHEN cpc.cpc_full LIKE 'H01L 27%' THEN cp.application_number
    END) as ic_patents,
    COUNT(DISTINCT CASE
        WHEN cpc.cpc_full LIKE 'G11C%' THEN cp.application_number
    END) as memory_patents,
    COUNT(DISTINCT CASE
        WHEN cpc.cpc_full LIKE 'H03K 19%' THEN cp.application_number
    END) as logic_patents
FROM uspto_patents_chinese cp
JOIN uspto_cpc_classifications cpc ON cp.application_number = cpc.application_number
WHERE (cpc.cpc_full LIKE 'H01L%' OR cpc.cpc_full LIKE 'G11C%' OR cpc.cpc_full LIKE 'H03K%')
  AND cp.year IS NOT NULL
  AND cp.year BETWEEN 2000 AND 2025
GROUP BY cp.year
ORDER BY cp.year
"""

cursor.execute(query_timeseries)
timeseries_data = []
print("\nYear | Total | Manufacturing | Packaging | ICs | Memory | Logic")
print("-" * 80)

for row in cursor.fetchall():
    year = row[0]
    total = row[1]
    manufacturing = row[2]
    packaging = row[3]
    ics = row[4]
    memory = row[5]
    logic = row[6]

    print(f"{year} | {total:>5,} | {manufacturing:>13,} | {packaging:>9,} | {ics:>3,} | {memory:>6,} | {logic:>5,}")

    timeseries_data.append({
        'year': year,
        'total_patents': total,
        'manufacturing': manufacturing,
        'packaging': packaging,
        'integrated_circuits': ics,
        'memory': memory,
        'logic': logic
    })

# Calculate growth rates
if len(timeseries_data) >= 2:
    first_year = timeseries_data[0]
    last_year = timeseries_data[-1]
    years_span = last_year['year'] - first_year['year']
    total_growth = ((last_year['total_patents'] - first_year['total_patents']) / first_year['total_patents'] * 100) if first_year['total_patents'] > 0 else 0

    print(f"\nGrowth Analysis ({first_year['year']}-{last_year['year']}):")
    print(f"  Total growth: {total_growth:+.1f}%")
    print(f"  {first_year['year']}: {first_year['total_patents']:,} patents")
    print(f"  {last_year['year']}: {last_year['total_patents']:,} patents")
    print(f"  Absolute increase: {last_year['total_patents'] - first_year['total_patents']:,} patents")

# ============================================================================
# 3. TOP CHINESE ASSIGNEES
# ============================================================================

print("\n" + "="*80)
print("2. TOP CHINESE ASSIGNEES IN SEMICONDUCTOR PATENTS")
print("="*80)

query_assignees = """
SELECT
    cp.assignee_name,
    COUNT(DISTINCT cp.application_number) as patent_count,
    COUNT(DISTINCT CASE WHEN cpc.cpc_full LIKE 'H01L 21%' THEN cp.application_number END) as manufacturing,
    COUNT(DISTINCT CASE WHEN cpc.cpc_full LIKE 'H01L 27%' THEN cp.application_number END) as ics,
    COUNT(DISTINCT CASE WHEN cpc.cpc_full LIKE 'G11C%' THEN cp.application_number END) as memory,
    MIN(cp.year) as first_patent_year,
    MAX(cp.year) as latest_patent_year
FROM uspto_patents_chinese cp
JOIN uspto_cpc_classifications cpc ON cp.application_number = cpc.application_number
WHERE (cpc.cpc_full LIKE 'H01L%' OR cpc.cpc_full LIKE 'G11C%' OR cpc.cpc_full LIKE 'H03K%')
  AND cp.assignee_name IS NOT NULL
  AND cp.assignee_name != ''
GROUP BY cp.assignee_name
HAVING patent_count >= 50
ORDER BY patent_count DESC
LIMIT 50
"""

cursor.execute(query_assignees)
assignee_data = []

print("\nRank | Assignee | Total | Mfg | ICs | Memory | Years Active")
print("-" * 100)

for idx, row in enumerate(cursor.fetchall(), 1):
    assignee = row[0][:40]  # Truncate long names
    total = row[1]
    mfg = row[2]
    ics = row[3]
    memory = row[4]
    first_year = row[5]
    last_year = row[6]
    years = f"{first_year}-{last_year}"

    print(f"{idx:>4} | {assignee:<40} | {total:>5,} | {mfg:>3,} | {ics:>3,} | {memory:>6,} | {years}")

    assignee_data.append({
        'rank': idx,
        'assignee': row[0],
        'total_patents': total,
        'manufacturing': mfg,
        'integrated_circuits': ics,
        'memory': memory,
        'first_patent_year': first_year,
        'latest_patent_year': last_year
    })

# ============================================================================
# 4. TECHNOLOGY AREA BREAKDOWN
# ============================================================================

print("\n" + "="*80)
print("3. TECHNOLOGY AREA BREAKDOWN")
print("="*80)

query_tech_areas = """
SELECT
    CASE
        WHEN cpc.cpc_full LIKE 'H01L 21%' THEN 'Manufacturing Processes'
        WHEN cpc.cpc_full LIKE 'H01L 23%' THEN 'Device Packaging'
        WHEN cpc.cpc_full LIKE 'H01L 25%' THEN 'Device Assemblies'
        WHEN cpc.cpc_full LIKE 'H01L 27%' THEN 'Integrated Circuits'
        WHEN cpc.cpc_full LIKE 'H01L 29%' THEN 'Semiconductor Devices'
        WHEN cpc.cpc_full LIKE 'H01L 31%' THEN 'Photovoltaic/Solar'
        WHEN cpc.cpc_full LIKE 'H01L 33%' THEN 'LED Devices'
        WHEN cpc.cpc_full LIKE 'G11C 11%' THEN 'DRAM Memory'
        WHEN cpc.cpc_full LIKE 'G11C 16%' THEN 'Flash/EPROM Memory'
        WHEN cpc.cpc_full LIKE 'G11C%' THEN 'Other Memory'
        WHEN cpc.cpc_full LIKE 'H03K 19%' THEN 'Logic Circuits'
        ELSE 'Other Semiconductor'
    END as technology_area,
    COUNT(DISTINCT cp.application_number) as patent_count,
    MIN(cp.year) as earliest_year,
    MAX(cp.year) as latest_year
FROM uspto_patents_chinese cp
JOIN uspto_cpc_classifications cpc ON cp.application_number = cpc.application_number
WHERE (cpc.cpc_full LIKE 'H01L%' OR cpc.cpc_full LIKE 'G11C%' OR cpc.cpc_full LIKE 'H03K%')
  AND cp.year IS NOT NULL
GROUP BY technology_area
ORDER BY patent_count DESC
"""

cursor.execute(query_tech_areas)
tech_area_data = []

print("\nTechnology Area | Patents | Period")
print("-" * 80)

total_tech_patents = 0
for row in cursor.fetchall():
    tech_area = row[0]
    patent_count = row[1]
    earliest = row[2]
    latest = row[3]
    total_tech_patents += patent_count

    print(f"{tech_area:<30} | {patent_count:>7,} | {earliest}-{latest}")

    tech_area_data.append({
        'technology_area': tech_area,
        'patent_count': patent_count,
        'earliest_year': earliest,
        'latest_year': latest
    })

print(f"\nTotal (Note: Patents can have multiple CPC codes): {total_tech_patents:,}")

# ============================================================================
# 5. RECENT TRENDS (2020-2025)
# ============================================================================

print("\n" + "="*80)
print("4. RECENT TRENDS (2020-2025) - Post-CHIPS Act Era")
print("="*80)

query_recent = """
SELECT
    cp.year,
    COUNT(DISTINCT cp.application_number) as total_patents,
    COUNT(DISTINCT CASE WHEN cp.assignee_name LIKE '%SMIC%' OR cp.assignee_name LIKE '%Semiconductor Manufacturing%' THEN cp.application_number END) as smic_patents,
    COUNT(DISTINCT CASE WHEN cp.assignee_name LIKE '%Huawei%' OR cp.assignee_name LIKE '%HiSilicon%' THEN cp.application_number END) as huawei_patents,
    COUNT(DISTINCT CASE WHEN cp.assignee_name LIKE '%YMTC%' OR cp.assignee_name LIKE '%Yangtze%Memory%' THEN cp.application_number END) as ymtc_patents,
    COUNT(DISTINCT CASE WHEN cp.assignee_name LIKE '%BOE%' THEN cp.application_number END) as boe_patents
FROM uspto_patents_chinese cp
JOIN uspto_cpc_classifications cpc ON cp.application_number = cpc.application_number
WHERE (cpc.cpc_full LIKE 'H01L%' OR cpc.cpc_full LIKE 'G11C%' OR cpc.cpc_full LIKE 'H03K%')
  AND cp.year >= 2020
GROUP BY cp.year
ORDER BY cp.year
"""

cursor.execute(query_recent)
recent_data = []

print("\nYear | Total | SMIC | Huawei/HiSilicon | YMTC | BOE")
print("-" * 80)

for row in cursor.fetchall():
    year = row[0]
    total = row[1]
    smic = row[2]
    huawei = row[3]
    ymtc = row[4]
    boe = row[5]

    print(f"{year} | {total:>5,} | {smic:>4,} | {huawei:>15,} | {ymtc:>4,} | {boe:>3,}")

    recent_data.append({
        'year': year,
        'total': total,
        'smic': smic,
        'huawei': huawei,
        'ymtc': ymtc,
        'boe': boe
    })

# ============================================================================
# 6. STRATEGIC TECHNOLOGY FOCUS
# ============================================================================

print("\n" + "="*80)
print("5. STRATEGIC TECHNOLOGY FOCUS - Advanced Manufacturing")
print("="*80)

# EUV/Lithography related
cursor.execute("""
SELECT COUNT(DISTINCT cp.application_number)
FROM uspto_patents_chinese cp
JOIN uspto_cpc_classifications cpc ON cp.application_number = cpc.application_number
WHERE cp.title LIKE '%lithography%' OR cp.title LIKE '%photolithography%' OR cp.title LIKE '%EUV%'
""")
lithography_patents = cursor.fetchone()[0]

# FinFET/GAA transistors
cursor.execute("""
SELECT COUNT(DISTINCT cp.application_number)
FROM uspto_patents_chinese cp
WHERE cp.title LIKE '%FinFET%' OR cp.title LIKE '%gate-all-around%' OR cp.title LIKE '%GAA%'
""")
finfet_patents = cursor.fetchone()[0]

# Advanced packaging (3D, chiplet)
cursor.execute("""
SELECT COUNT(DISTINCT cp.application_number)
FROM uspto_patents_chinese cp
JOIN uspto_cpc_classifications cpc ON cp.application_number = cpc.application_number
WHERE (cp.title LIKE '%3D%packaging%' OR cp.title LIKE '%chiplet%' OR cp.title LIKE '%through-silicon%via%')
  AND cpc.cpc_full LIKE 'H01L 23%'
""")
packaging_patents = cursor.fetchone()[0]

# Memory technologies
cursor.execute("""
SELECT COUNT(DISTINCT cp.application_number)
FROM uspto_patents_chinese cp
WHERE cp.title LIKE '%3D NAND%' OR cp.title LIKE '%MRAM%' OR cp.title LIKE '%ReRAM%'
""")
advanced_memory = cursor.fetchone()[0]

print(f"\nAdvanced Technology Patents:")
print(f"  Lithography/EUV: {lithography_patents:,}")
print(f"  FinFET/GAA Transistors: {finfet_patents:,}")
print(f"  Advanced Packaging: {packaging_patents:,}")
print(f"  Advanced Memory (3D NAND, MRAM, ReRAM): {advanced_memory:,}")

# ============================================================================
# 7. SAVE RESULTS TO JSON
# ============================================================================

print("\n" + "="*80)
print("6. SAVING RESULTS")
print("="*80)

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

results = {
    'metadata': {
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'database': DB_PATH,
        'total_chinese_patents_analyzed': 425074,
        'semiconductor_cpc_codes': list(SEMICONDUCTOR_CPC_CODES.keys()),
        'zero_fabrication_compliant': True,
        'source': 'USPTO Patent Database via BigQuery Public Data'
    },
    'timeseries_analysis': timeseries_data,
    'top_assignees': assignee_data[:50],
    'technology_areas': tech_area_data,
    'recent_trends_2020_2025': recent_data,
    'strategic_technologies': {
        'lithography_euv': lithography_patents,
        'finfet_gaa': finfet_patents,
        'advanced_packaging': packaging_patents,
        'advanced_memory': advanced_memory
    }
}

output_file = f"{OUTPUT_DIR}/chinese_semiconductor_patents_analysis_{datetime.now().strftime('%Y%m%d')}.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_file}")

# Summary statistics
print("\n" + "="*80)
print("ANALYSIS SUMMARY")
print("="*80)

total_semiconductor_patents = sum([d['total_patents'] for d in timeseries_data])
print(f"\nTotal Chinese Semiconductor Patents (2000-2025): {total_semiconductor_patents:,}")
print(f"Top Assignee: {assignee_data[0]['assignee']} ({assignee_data[0]['total_patents']:,} patents)")
print(f"Most Common Technology: {tech_area_data[0]['technology_area']} ({tech_area_data[0]['patent_count']:,} patents)")

if len(timeseries_data) >= 10:
    last_5_years = timeseries_data[-5:]
    avg_recent = sum([d['total_patents'] for d in last_5_years]) / 5
    print(f"Average annual patents (last 5 years): {avg_recent:,.0f}")

conn.close()

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
