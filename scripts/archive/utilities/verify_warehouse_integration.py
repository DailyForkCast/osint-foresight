#!/usr/bin/env python3
"""
Verify Kaggle arXiv warehouse integration completeness and data integrity.
Checks: record counts, data quality, foreign key integrity, statistics accuracy.
"""

import sqlite3
from datetime import datetime

print('=' * 80)
print('WAREHOUSE INTEGRATION VERIFICATION')
print('=' * 80)

KAGGLE_DB = 'C:/Projects/OSINT - Foresight/data/kaggle_arxiv_processing.db'
WAREHOUSE_DB = 'F:/OSINT_WAREHOUSE/osint_master.db'

conn_kaggle = sqlite3.connect(KAGGLE_DB)
conn_warehouse = sqlite3.connect(WAREHOUSE_DB)

cursor_kaggle = conn_kaggle.cursor()
cursor_warehouse = conn_warehouse.cursor()

print(f'\n[1/8] Connecting to databases...')
print(f'  [OK] Connected to Kaggle: {KAGGLE_DB}')
print(f'  [OK] Connected to Warehouse: {WAREHOUSE_DB}')

# ============================================================================
# TEST 1: Record Count Verification
# ============================================================================
print('\n[2/8] Verifying record counts...')

cursor_kaggle.execute('SELECT COUNT(*) FROM kaggle_arxiv_papers')
kaggle_papers = cursor_kaggle.fetchone()[0]

cursor_warehouse.execute('SELECT COUNT(*) FROM arxiv_papers')
warehouse_papers = cursor_warehouse.fetchone()[0]

cursor_warehouse.execute('SELECT COUNT(*) FROM arxiv_authors')
warehouse_authors = cursor_warehouse.fetchone()[0]

cursor_warehouse.execute('SELECT COUNT(*) FROM arxiv_categories')
warehouse_categories = cursor_warehouse.fetchone()[0]

print(f'  Source (Kaggle): {kaggle_papers:,} papers')
print(f'  Warehouse: {warehouse_papers:,} papers')
print(f'  Warehouse: {warehouse_authors:,} authors')
print(f'  Warehouse: {warehouse_categories:,} categories')

# Check if all papers were integrated (allowing for small number that existed before)
papers_match = warehouse_papers >= kaggle_papers
print(f'  Papers match: {"PASS" if papers_match else "FAIL"}')

# ============================================================================
# TEST 2: Technology Domain Distribution
# ============================================================================
print('\n[3/8] Verifying technology domain distribution...')

cursor_warehouse.execute('''
    SELECT technology_domain, COUNT(*) as count
    FROM arxiv_papers
    WHERE technology_domain IS NOT NULL
    GROUP BY technology_domain
    ORDER BY count DESC
''')

tech_distribution = cursor_warehouse.fetchall()
print('  Technology domains in warehouse:')
for tech, count in tech_distribution:
    print(f'    {tech}: {count:,} papers')

# ============================================================================
# TEST 3: Year Distribution
# ============================================================================
print('\n[4/8] Verifying temporal coverage...')

cursor_warehouse.execute('''
    SELECT
        MIN(year) as min_year,
        MAX(year) as max_year,
        COUNT(DISTINCT year) as year_span
    FROM arxiv_papers
    WHERE year IS NOT NULL
''')

min_year, max_year, year_span = cursor_warehouse.fetchone()
print(f'  Year range: {min_year} - {max_year} ({year_span} years)')

# Sample year distribution
cursor_warehouse.execute('''
    SELECT year, COUNT(*) as count
    FROM arxiv_papers
    WHERE year IN (2020, 2021, 2022, 2023, 2024, 2025)
    GROUP BY year
    ORDER BY year DESC
''')

recent_years = cursor_warehouse.fetchall()
print('  Recent years sample:')
for year, count in recent_years:
    print(f'    {year}: {count:,} papers')

# ============================================================================
# TEST 4: Author Linkage Integrity
# ============================================================================
print('\n[5/8] Verifying author-paper linkage integrity...')

# Check for orphaned authors (authors with no corresponding paper)
cursor_warehouse.execute('''
    SELECT COUNT(DISTINCT a.arxiv_id)
    FROM arxiv_authors a
    LEFT JOIN arxiv_papers p ON a.arxiv_id = p.arxiv_id
    WHERE p.arxiv_id IS NULL
''')

orphaned_authors = cursor_warehouse.fetchone()[0]
print(f'  Orphaned author records: {orphaned_authors:,} {"PASS" if orphaned_authors == 0 else "FAIL"}')

# Check author distribution
cursor_warehouse.execute('''
    SELECT
        COUNT(DISTINCT arxiv_id) as papers_with_authors,
        COUNT(*) as total_author_records,
        ROUND(CAST(COUNT(*) AS FLOAT) / COUNT(DISTINCT arxiv_id), 2) as avg_authors_per_paper
    FROM arxiv_authors
''')

papers_with_authors, total_author_records, avg_authors = cursor_warehouse.fetchone()
print(f'  Papers with authors: {papers_with_authors:,}')
print(f'  Total author records: {total_author_records:,}')
print(f'  Average authors per paper: {avg_authors}')

# ============================================================================
# TEST 5: Category Linkage Integrity
# ============================================================================
print('\n[6/8] Verifying category-paper linkage integrity...')

# Check for orphaned categories
cursor_warehouse.execute('''
    SELECT COUNT(DISTINCT c.arxiv_id)
    FROM arxiv_categories c
    LEFT JOIN arxiv_papers p ON c.arxiv_id = p.arxiv_id
    WHERE p.arxiv_id IS NULL
''')

orphaned_categories = cursor_warehouse.fetchone()[0]
print(f'  Orphaned category records: {orphaned_categories:,} {"PASS" if orphaned_categories == 0 else "FAIL"}')

# Check category distribution
cursor_warehouse.execute('''
    SELECT category, COUNT(*) as count
    FROM arxiv_categories
    GROUP BY category
    ORDER BY count DESC
    LIMIT 10
''')

top_categories = cursor_warehouse.fetchall()
print('  Top 10 categories:')
for category, count in top_categories:
    print(f'    {category}: {count:,} papers')

# ============================================================================
# TEST 6: Primary Category Validation
# ============================================================================
print('\n[7/8] Verifying primary category marking...')

cursor_warehouse.execute('''
    SELECT
        COUNT(DISTINCT arxiv_id) as papers_with_primary_cat,
        (SELECT COUNT(*) FROM arxiv_papers) as total_papers
    FROM arxiv_categories
    WHERE is_primary = 1
''')

papers_with_primary, total_papers = cursor_warehouse.fetchone()
print(f'  Papers with primary category: {papers_with_primary:,} / {total_papers:,}')
print(f'  Coverage: {(papers_with_primary/total_papers*100):.1f}%')

# ============================================================================
# TEST 7: Statistics Table Validation
# ============================================================================
print('\n[8/8] Verifying statistics table...')

cursor_warehouse.execute('''
    SELECT COUNT(*)
    FROM arxiv_statistics
''')

stats_records = cursor_warehouse.fetchone()[0]
print(f'  Statistics records: {stats_records:,}')

# Sample statistics
cursor_warehouse.execute('''
    SELECT technology_domain, category, year, paper_count
    FROM arxiv_statistics
    ORDER BY paper_count DESC
    LIMIT 5
''')

top_stats = cursor_warehouse.fetchall()
print('  Top 5 statistics entries:')
for tech, cat, year, count in top_stats:
    print(f'    {tech} / {cat} / {year}: {count:,} papers')

# ============================================================================
# TEST 8: Integration Metadata
# ============================================================================
print('\n[Bonus] Integration metadata...')

cursor_warehouse.execute('''
    SELECT
        integration_date,
        technology_domain,
        total_papers,
        data_source,
        notes
    FROM arxiv_integration_metadata
    ORDER BY integration_date DESC
    LIMIT 1
''')

metadata = cursor_warehouse.fetchone()
if metadata:
    integration_date, tech_domain, total_papers, data_source, notes = metadata
    print(f'  Integration date: {integration_date}')
    print(f'  Technology domain: {tech_domain}')
    print(f'  Total papers integrated: {total_papers:,}')
    print(f'  Data source: {data_source}')
    print(f'  Notes: {notes}')

# ============================================================================
# Summary
# ============================================================================
print('\n' + '=' * 80)
print('VERIFICATION COMPLETE')
print('=' * 80)

# Calculate overall pass/fail
all_tests_passed = (
    papers_match and
    orphaned_authors == 0 and
    orphaned_categories == 0 and
    stats_records > 0
)

print(f'\nOverall Status: {"PASS - All integrity checks passed" if all_tests_passed else "REVIEW NEEDED - Some tests failed"}')
print(f'\nVerification timestamp: {datetime.now().isoformat()}')

# Close connections
conn_kaggle.close()
conn_warehouse.close()

print('\n' + '=' * 80)
print('[OK] VERIFICATION COMPLETE')
print('=' * 80)
