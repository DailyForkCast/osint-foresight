"""
Check OpenAlex Actual Database Structure
Identify correct tables and schema for semiconductor analysis
"""

import sqlite3
import json

DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'

print("="*80)
print("OPENALEX ACTUAL STRUCTURE ASSESSMENT")
print("="*80)
print(f"Database: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ============================================================================
# 1. Check openalex_works structure (496K records)
# ============================================================================

print("="*80)
print("1. openalex_works Table Structure")
print("="*80 + "\n")

cursor.execute("PRAGMA table_info(openalex_works)")
columns = cursor.fetchall()
print(f"Columns in openalex_works ({len(columns)} total):\n")
for col in columns:
    print(f"  {col[1]}: {col[2]}")

# ============================================================================
# 2. Sample data from openalex_works
# ============================================================================

print("\n" + "="*80)
print("2. Sample Records from openalex_works")
print("="*80 + "\n")

cursor.execute("SELECT * FROM openalex_works LIMIT 1")
sample = cursor.fetchone()

if sample:
    print("Sample record:")
    for idx, col in enumerate(columns):
        col_name = col[1]
        value = sample[idx]
        if value and len(str(value)) > 100:
            value = str(value)[:100] + "..."
        print(f"  {col_name}: {value}")

# ============================================================================
# 3. Check date range
# ============================================================================

print("\n" + "="*80)
print("3. Date Range Analysis")
print("="*80 + "\n")

date_cols = [col[1] for col in columns if 'date' in col[1].lower() or 'year' in col[1].lower()]
print(f"Found {len(date_cols)} date-related columns: {', '.join(date_cols)}\n")

if 'publication_year' in [col[1] for col in columns]:
    cursor.execute("""
    SELECT
        COUNT(*) as total,
        MIN(publication_year) as earliest,
        MAX(publication_year) as latest
    FROM openalex_works
    WHERE publication_year IS NOT NULL
    """)
    result = cursor.fetchone()
    print(f"Total works: {result[0]:,}")
    print(f"Date range: {result[1]}-{result[2]}")

# ============================================================================
# 4. Check for China/collaboration indicators
# ============================================================================

print("\n" + "="*80)
print("4. China Collaboration Indicators")
print("="*80 + "\n")

# Check columns
china_cols = [col[1] for col in columns if 'china' in col[1].lower() or 'country' in col[1].lower() or 'collab' in col[1].lower()]
if china_cols:
    print(f"Found {len(china_cols)} China-related columns:")
    for col in china_cols:
        print(f"  - {col}")
else:
    print("No direct China columns found in openalex_works")

# ============================================================================
# 5. Check openalex_work_authors for country info
# ============================================================================

print("\n" + "="*80)
print("5. openalex_work_authors Table (7.9M records)")
print("="*80 + "\n")

cursor.execute("PRAGMA table_info(openalex_work_authors)")
author_cols = cursor.fetchall()
print(f"Columns in openalex_work_authors ({len(author_cols)} total):\n")
for col in author_cols:
    print(f"  {col[1]}: {col[2]}")

# Sample data
cursor.execute("SELECT * FROM openalex_work_authors LIMIT 1")
author_sample = cursor.fetchone()
if author_sample:
    print("\nSample record:")
    for idx, col in enumerate(author_cols):
        print(f"  {col[1]}: {author_sample[idx]}")

# ============================================================================
# 6. Check openalex_work_topics for keywords
# ============================================================================

print("\n" + "="*80)
print("6. openalex_work_topics Table (736K records)")
print("="*80 + "\n")

cursor.execute("PRAGMA table_info(openalex_work_topics)")
topic_cols = cursor.fetchall()
print(f"Columns in openalex_work_topics ({len(topic_cols)} total):\n")
for col in topic_cols:
    print(f"  {col[1]}: {col[2]}")

# Sample data
cursor.execute("SELECT * FROM openalex_work_topics LIMIT 5")
topic_samples = cursor.fetchall()
if topic_samples:
    print("\nSample records:")
    for sample in topic_samples:
        print(f"  {sample}")

# ============================================================================
# 7. Test semiconductor keyword matching
# ============================================================================

print("\n" + "="*80)
print("7. Testing Semiconductor Keyword Matching on openalex_works")
print("="*80 + "\n")

# Check if we have title column
if 'title' in [col[1] for col in columns]:
    test_keywords = ['semiconductor', 'chip', 'transistor', 'lithography', 'wafer']

    for keyword in test_keywords:
        cursor.execute(f"""
        SELECT COUNT(*)
        FROM openalex_works
        WHERE title LIKE '%{keyword}%' COLLATE NOCASE
        """)
        count = cursor.fetchone()[0]
        print(f"  '{keyword}': {count:,} works")

    # Combined count
    semiconductor_conditions = " OR ".join([
        f"title LIKE '%{kw}%' COLLATE NOCASE"
        for kw in test_keywords
    ])

    cursor.execute(f"""
    SELECT COUNT(*)
    FROM openalex_works
    WHERE ({semiconductor_conditions})
    """)

    total = cursor.fetchone()[0]
    print(f"\nTotal semiconductor-related works: {total:,}")

# ============================================================================
# 8. Check openalex_entities for institutions
# ============================================================================

print("\n" + "="*80)
print("8. openalex_entities Table (6,344 records)")
print("="*80 + "\n")

cursor.execute("PRAGMA table_info(openalex_entities)")
entity_cols = cursor.fetchall()
print(f"Columns in openalex_entities ({len(entity_cols)} total):\n")
for col in entity_cols:
    print(f"  {col[1]}: {col[2]}")

# Check for country field
if 'country_code' in [col[1] for col in entity_cols]:
    cursor.execute("""
    SELECT country_code, COUNT(*) as count
    FROM openalex_entities
    WHERE country_code IS NOT NULL
    GROUP BY country_code
    ORDER BY count DESC
    LIMIT 20
    """)

    print("\nTop 20 countries in openalex_entities:")
    for country, count in cursor.fetchall():
        print(f"  {country}: {count:,}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("ASSESSMENT SUMMARY")
print("="*80 + "\n")

print("OpenAlex Schema:")
print("  - openalex_works: 496,392 records (main papers)")
print("  - openalex_work_authors: 7,936,171 records (author affiliations)")
print("  - openalex_work_topics: 736,042 records (topic classifications)")
print("  - openalex_entities: 6,344 records (institutions)")
print("\nNext Step:")
print("  Need to JOIN openalex_works with openalex_work_authors to get country collaborations")
print("  Filter by title keywords for semiconductor research")
print("  Identify EU-China co-authorship patterns")

conn.close()

print("\n" + "="*80)
print("ASSESSMENT COMPLETE")
print("="*80)
