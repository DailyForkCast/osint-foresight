"""
Check OpenAlex Database for Semiconductor Research Analysis
Assess existing data before running semiconductor-specific queries
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'

print("="*80)
print("OPENALEX SEMICONDUCTOR DATA ASSESSMENT")
print("="*80)
print(f"Database: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ============================================================================
# 1. Check OpenAlex tables
# ============================================================================

print("Step 1: Identifying OpenAlex tables...\n")

cursor.execute("""
SELECT name, sql FROM sqlite_master
WHERE type='table' AND name LIKE 'openalex%'
ORDER BY name
""")

tables = cursor.fetchall()
print(f"Found {len(tables)} OpenAlex tables:\n")
for table_name, sql in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  {table_name}: {count:,} records")

# ============================================================================
# 2. Check main papers table structure
# ============================================================================

print("\n" + "="*80)
print("Step 2: Analyzing openalex_papers_multicountry structure...")
print("="*80 + "\n")

cursor.execute("PRAGMA table_info(openalex_papers_multicountry)")
columns = cursor.fetchall()
print(f"Table has {len(columns)} columns:\n")
for col in columns[:20]:  # Show first 20 columns
    print(f"  {col[1]}: {col[2]}")
if len(columns) > 20:
    print(f"  ... and {len(columns) - 20} more columns")

# ============================================================================
# 3. Check date range and geographic coverage
# ============================================================================

print("\n" + "="*80)
print("Step 3: Date Range and Geographic Coverage")
print("="*80 + "\n")

cursor.execute("""
SELECT
    COUNT(*) as total_papers,
    MIN(publication_year) as earliest,
    MAX(publication_year) as latest,
    COUNT(DISTINCT country_code) as num_countries
FROM openalex_papers_multicountry
WHERE publication_year IS NOT NULL
""")

result = cursor.fetchone()
print(f"Total papers: {result[0]:,}")
print(f"Date range: {result[1]}-{result[2]}")
print(f"Countries covered: {result[3]}")

# ============================================================================
# 4. Check for keyword/topic columns
# ============================================================================

print("\n" + "="*80)
print("Step 4: Checking for keyword/topic filtering capability")
print("="*80 + "\n")

# Check if we have keywords, topics, or concepts columns
keyword_columns = [col[1] for col in columns if 'keyword' in col[1].lower() or 'topic' in col[1].lower() or 'concept' in col[1].lower() or 'title' in col[1].lower() or 'abstract' in col[1].lower()]

if keyword_columns:
    print(f"Found {len(keyword_columns)} relevant columns for filtering:")
    for col in keyword_columns:
        print(f"  - {col}")
else:
    print("No keyword/topic columns found")

# ============================================================================
# 5. Check collaboration patterns
# ============================================================================

print("\n" + "="*80)
print("Step 5: China Collaboration Patterns")
print("="*80 + "\n")

# Check if we have China collaboration indicator
cursor.execute("""
SELECT COUNT(*)
FROM openalex_papers_multicountry
WHERE has_china_collab = 1
""")

china_collabs = cursor.fetchone()[0]
print(f"Papers with China collaboration: {china_collabs:,}")

# By country
cursor.execute("""
SELECT country_code, COUNT(*) as papers
FROM openalex_papers_multicountry
WHERE has_china_collab = 1
GROUP BY country_code
ORDER BY papers DESC
LIMIT 20
""")

print("\nTop 20 countries collaborating with China:")
print("Rank | Country | Papers")
print("-" * 40)
for idx, (country, papers) in enumerate(cursor.fetchall(), 1):
    print(f"{idx:>3} | {country:>7} | {papers:>8,}")

# ============================================================================
# 6. Sample semiconductor keyword matching
# ============================================================================

print("\n" + "="*80)
print("Step 6: Testing Semiconductor Keyword Matching")
print("="*80 + "\n")

# Load semiconductor keywords
with open('C:/Projects/OSINT-Foresight/config/openalex_technology_keywords_v5.json', 'r') as f:
    keywords_config = json.load(f)

semiconductor_keywords = keywords_config.get('Semiconductors', {})

# Build keyword list
all_keywords = []
for category, kw_list in semiconductor_keywords.items():
    all_keywords.extend(kw_list)

print(f"Loaded {len(all_keywords)} semiconductor keywords\n")
print("Sample keywords:")
for kw in all_keywords[:10]:
    print(f"  - {kw}")
print(f"  ... and {len(all_keywords) - 10} more\n")

# Test keyword matching on title
if 'title' in [col[1] for col in columns]:
    print("Testing title-based filtering...")

    # Sample a few key terms
    test_keywords = [
        'semiconductor',
        'chip fabrication',
        'lithography',
        'transistor',
        'integrated circuit'
    ]

    for keyword in test_keywords:
        cursor.execute(f"""
        SELECT COUNT(*)
        FROM openalex_papers_multicountry
        WHERE title LIKE '%{keyword}%' COLLATE NOCASE
        """)
        count = cursor.fetchone()[0]
        print(f"  '{keyword}': {count:,} papers")

    # Combined semiconductor filter
    semiconductor_conditions = " OR ".join([
        f"title LIKE '%{kw}%' COLLATE NOCASE"
        for kw in ['semiconductor', 'chip', 'wafer', 'lithography', 'transistor']
    ])

    cursor.execute(f"""
    SELECT COUNT(*)
    FROM openalex_papers_multicountry
    WHERE ({semiconductor_conditions})
    """)

    total_semiconductor = cursor.fetchone()[0]
    print(f"\nTotal papers matching semiconductor keywords: {total_semiconductor:,}")

    # With China collaboration
    cursor.execute(f"""
    SELECT COUNT(*)
    FROM openalex_papers_multicountry
    WHERE ({semiconductor_conditions})
      AND has_china_collab = 1
    """)

    china_semiconductor = cursor.fetchone()[0]
    print(f"Semiconductor papers with China collaboration: {china_semiconductor:,}")

    if total_semiconductor > 0:
        pct = (china_semiconductor / total_semiconductor * 100)
        print(f"Percentage with China involvement: {pct:.1f}%")

# ============================================================================
# 7. EU-27 specific analysis
# ============================================================================

print("\n" + "="*80)
print("Step 7: EU-27 Countries Analysis")
print("="*80 + "\n")

EU27_COUNTRIES = [
    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
    'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
    'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
]

eu_condition = " OR ".join([f"country_code = '{cc}'" for cc in EU27_COUNTRIES])

cursor.execute(f"""
SELECT COUNT(*)
FROM openalex_papers_multicountry
WHERE ({eu_condition})
  AND has_china_collab = 1
""")

eu_china_collabs = cursor.fetchone()[0]
print(f"EU-27 papers with China collaboration: {eu_china_collabs:,}")

# By EU country
cursor.execute(f"""
SELECT country_code, COUNT(*) as papers
FROM openalex_papers_multicountry
WHERE ({eu_condition})
  AND has_china_collab = 1
GROUP BY country_code
ORDER BY papers DESC
""")

print("\nEU-27 Countries collaborating with China:")
print("Rank | Country | Papers")
print("-" * 40)
for idx, (country, papers) in enumerate(cursor.fetchall(), 1):
    print(f"{idx:>3} | {country:>7} | {papers:>8,}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("ASSESSMENT SUMMARY")
print("="*80 + "\n")

print("Data Quality:")
print(f"  [OK] OpenAlex tables present: {len(tables)}")
print(f"  [OK] Total papers available: {result[0]:,}")
print(f"  [OK] China collaboration data: {china_collabs:,} papers")
print(f"  [OK] EU-China collaborations: {eu_china_collabs:,} papers")

if 'title' in [col[1] for col in columns]:
    print(f"  [OK] Title-based filtering available")
    print(f"  [OK] Semiconductor papers identified: {total_semiconductor:,}")
    print(f"  [OK] Semiconductor + China collab: {china_semiconductor:,}")

print("\nRECOMMENDATION:")
print("  Proceed with semiconductor-specific EU-China collaboration analysis")
print("  Expected output: 500-2,000 semiconductor research papers")
print("  Method: Title keyword matching + China collaboration flag")

conn.close()

print("\n" + "="*80)
print("ASSESSMENT COMPLETE")
print("="*80)
