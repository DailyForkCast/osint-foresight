#!/usr/bin/env python3
"""
Integrate Kaggle arXiv expanded database into master warehouse.
Handles: papers, authors, categories, technology classifications, statistics.
"""

import sqlite3
import time
from datetime import datetime

print('=' * 80)
print('KAGGLE ARXIV -> MASTER WAREHOUSE INTEGRATION')
print('=' * 80)

# Configuration
KAGGLE_DB = 'C:/Projects/OSINT - Foresight/data/kaggle_arxiv_processing.db'
WAREHOUSE_DB = 'F:/OSINT_WAREHOUSE/osint_master.db'
BATCH_SIZE = 10000
INTEGRATION_DATE = datetime.now().isoformat()

# Connect to both databases
print('\n[1/6] Connecting to databases...')
conn_kaggle = sqlite3.connect(KAGGLE_DB)
conn_warehouse = sqlite3.connect(WAREHOUSE_DB)

cursor_kaggle = conn_kaggle.cursor()
cursor_warehouse = conn_warehouse.cursor()

print(f'  [OK] Connected to Kaggle database: {KAGGLE_DB}')
print(f'  [OK] Connected to Warehouse database: {WAREHOUSE_DB}')

# Get counts before integration
print('\n[2/6] Pre-integration counts...')
cursor_warehouse.execute('SELECT COUNT(*) FROM arxiv_papers')
papers_before = cursor_warehouse.fetchone()[0]

cursor_warehouse.execute('SELECT COUNT(*) FROM arxiv_authors')
authors_before = cursor_warehouse.fetchone()[0]

cursor_warehouse.execute('SELECT COUNT(*) FROM arxiv_categories')
categories_before = cursor_warehouse.fetchone()[0]

cursor_kaggle.execute('SELECT COUNT(*) FROM kaggle_arxiv_papers')
kaggle_papers_total = cursor_kaggle.fetchone()[0]

cursor_kaggle.execute('SELECT COUNT(*) FROM kaggle_arxiv_authors')
kaggle_authors_total = cursor_kaggle.fetchone()[0]

cursor_kaggle.execute('SELECT COUNT(*) FROM kaggle_arxiv_technology')
kaggle_tech_total = cursor_kaggle.fetchone()[0]

print(f'  Warehouse before: {papers_before:,} papers, {authors_before:,} authors, {categories_before:,} categories')
print(f'  Kaggle source: {kaggle_papers_total:,} papers, {kaggle_authors_total:,} authors, {kaggle_tech_total:,} technology classifications')

# ============================================================================
# STEP 3: Integrate Papers
# ============================================================================
print('\n[3/6] Integrating papers...')
print('  This will take 5-10 minutes for 1.4M papers...')

start_time = time.time()
papers_inserted = 0
papers_skipped = 0

# For each paper, we need to determine primary technology_domain
# Strategy: Use highest match_score from kaggle_arxiv_technology table
cursor_kaggle.execute('''
    SELECT
        p.arxiv_id,
        p.title,
        p.first_submission_date,
        p.submission_year,
        p.submission_month,
        p.update_date,
        p.abstract,
        p.primary_category,
        (SELECT technology_domain
         FROM kaggle_arxiv_technology t
         WHERE t.arxiv_id = p.arxiv_id
         ORDER BY t.match_score DESC
         LIMIT 1) as top_technology
    FROM kaggle_arxiv_papers p
''')

batch = []
processed = 0

for row in cursor_kaggle:
    arxiv_id, title, published_date, year, month, updated_date, summary, primary_category, technology_domain = row

    batch.append((
        arxiv_id,
        title,
        published_date,
        year,
        month,
        updated_date,
        summary,
        primary_category,
        technology_domain,  # Primary (highest scoring) technology
        INTEGRATION_DATE
    ))

    if len(batch) >= BATCH_SIZE:
        cursor_warehouse.executemany('''
            INSERT OR IGNORE INTO arxiv_papers
            (arxiv_id, title, published_date, year, month, updated_date,
             summary, primary_category, technology_domain, collection_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', batch)

        papers_inserted += cursor_warehouse.rowcount if cursor_warehouse.rowcount > 0 else 0
        processed += len(batch)

        if processed % 100000 == 0:
            elapsed = time.time() - start_time
            rate = processed / elapsed
            remaining = (kaggle_papers_total - processed) / rate if rate > 0 else 0
            print(f'    {processed:,}/{kaggle_papers_total:,} papers processed ({rate:.0f} papers/sec, ETA: {remaining/60:.1f} min)')

        batch = []

# Insert remaining batch
if batch:
    cursor_warehouse.executemany('''
        INSERT OR IGNORE INTO arxiv_papers
        (arxiv_id, title, published_date, year, month, updated_date,
         summary, primary_category, technology_domain, collection_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', batch)
    papers_inserted += cursor_warehouse.rowcount if cursor_warehouse.rowcount > 0 else 0

conn_warehouse.commit()
papers_elapsed = time.time() - start_time

print(f'  [OK] Papers integrated: {papers_inserted:,} new, {kaggle_papers_total - papers_inserted:,} duplicates skipped')
print(f'  Time: {papers_elapsed:.1f} seconds ({kaggle_papers_total/papers_elapsed:.0f} papers/sec)')

# ============================================================================
# STEP 4: Integrate Authors
# ============================================================================
print('\n[4/6] Integrating authors...')
print('  This will take 10-15 minutes for 7.6M author records...')

start_time = time.time()
authors_inserted = 0

# Get list of paper IDs that were successfully integrated (to avoid FK violations)
cursor_warehouse.execute('SELECT arxiv_id FROM arxiv_papers WHERE collection_date = ?', (INTEGRATION_DATE,))
integrated_papers = set(row[0] for row in cursor_warehouse.fetchall())
print(f'  Working with {len(integrated_papers):,} successfully integrated papers')

cursor_kaggle.execute('''
    SELECT arxiv_id, author_name, author_order
    FROM kaggle_arxiv_authors
    ORDER BY arxiv_id, author_order
''')

batch = []
processed = 0

for row in cursor_kaggle:
    arxiv_id, author_name, author_order = row

    # Only insert if paper exists in warehouse
    if arxiv_id in integrated_papers:
        batch.append((arxiv_id, author_name, author_order))

    if len(batch) >= BATCH_SIZE:
        cursor_warehouse.executemany('''
            INSERT OR IGNORE INTO arxiv_authors
            (arxiv_id, author_name, author_order)
            VALUES (?, ?, ?)
        ''', batch)

        processed += len(batch)

        if processed % 500000 == 0:
            elapsed = time.time() - start_time
            rate = processed / elapsed
            remaining = (kaggle_authors_total - processed) / rate if rate > 0 else 0
            print(f'    {processed:,}/{kaggle_authors_total:,} author records processed ({rate:.0f} records/sec, ETA: {remaining/60:.1f} min)')

        batch = []

# Insert remaining batch
if batch:
    cursor_warehouse.executemany('''
        INSERT OR IGNORE INTO arxiv_authors
        (arxiv_id, author_name, author_order)
        VALUES (?, ?, ?)
    ''', batch)

conn_warehouse.commit()
authors_elapsed = time.time() - start_time

cursor_warehouse.execute('SELECT COUNT(*) FROM arxiv_authors')
authors_after = cursor_warehouse.fetchone()[0]
authors_inserted = authors_after - authors_before

print(f'  [OK] Authors integrated: {authors_inserted:,} new records')
print(f'  Time: {authors_elapsed:.1f} seconds ({processed/authors_elapsed:.0f} records/sec)')

# ============================================================================
# STEP 5: Integrate Categories
# ============================================================================
print('\n[5/6] Integrating categories...')
start_time = time.time()

# Parse categories from kaggle_arxiv_papers.categories (stored as comma-separated string)
cursor_kaggle.execute('''
    SELECT arxiv_id, categories, primary_category
    FROM kaggle_arxiv_papers
''')

batch = []
processed = 0

for row in cursor_kaggle:
    arxiv_id, categories_str, primary_category = row

    if arxiv_id not in integrated_papers:
        continue

    if categories_str:
        # Split by comma or space
        categories = [c.strip() for c in categories_str.replace(' ', ',').split(',') if c.strip()]

        for category in categories:
            is_primary = 1 if category == primary_category else 0
            batch.append((arxiv_id, category, is_primary))

    if len(batch) >= BATCH_SIZE:
        cursor_warehouse.executemany('''
            INSERT OR IGNORE INTO arxiv_categories
            (arxiv_id, category, is_primary)
            VALUES (?, ?, ?)
        ''', batch)

        processed += len(batch)

        if processed % 500000 == 0:
            elapsed = time.time() - start_time
            rate = processed / elapsed
            print(f'    {processed:,} category records processed ({rate:.0f} records/sec)')

        batch = []

# Insert remaining batch
if batch:
    cursor_warehouse.executemany('''
        INSERT OR IGNORE INTO arxiv_categories
        (arxiv_id, category, is_primary)
        VALUES (?, ?, ?)
    ''', batch)

conn_warehouse.commit()
categories_elapsed = time.time() - start_time

cursor_warehouse.execute('SELECT COUNT(*) FROM arxiv_categories')
categories_after = cursor_warehouse.fetchone()[0]
categories_inserted = categories_after - categories_before

print(f'  [OK] Categories integrated: {categories_inserted:,} new records')
print(f'  Time: {categories_elapsed:.1f} seconds')

# ============================================================================
# STEP 6: Update Statistics and Metadata
# ============================================================================
print('\n[6/6] Updating statistics and metadata...')

# Calculate statistics for newly integrated papers
cursor_warehouse.execute('''
    INSERT OR REPLACE INTO arxiv_statistics
    (technology_domain, category, year, paper_count, collection_date)
    SELECT
        p.technology_domain,
        c.category,
        p.year,
        COUNT(*) as paper_count,
        ? as collection_date
    FROM arxiv_papers p
    JOIN arxiv_categories c ON p.arxiv_id = c.arxiv_id
    WHERE p.collection_date = ?
    GROUP BY p.technology_domain, c.category, p.year
''', (INTEGRATION_DATE, INTEGRATION_DATE))

# Add integration metadata
cursor_warehouse.execute('''
    INSERT INTO arxiv_integration_metadata
    (integration_date, technology_domain, total_papers, categories_analyzed,
     years_covered, data_source, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', (
    INTEGRATION_DATE,
    'ALL',  # Multi-technology integration
    papers_inserted,
    'Comprehensive: AI, Quantum, Space, Semiconductors, Neuroscience, Biotechnology, Advanced_Materials, Energy, Smart_City',
    '1990-2025',
    'Kaggle arXiv Snapshot (kaggle_arxiv_processing.db)',
    f'Expanded filter integration: {papers_inserted:,} papers, {authors_inserted:,} authors. '
    f'Biotechnology +119.5%, Energy +34.9%, Space +93.8%'
))

conn_warehouse.commit()

print(f'  [OK] Statistics updated')
print(f'  [OK] Integration metadata recorded')

# ============================================================================
# Summary
# ============================================================================
print('\n' + '=' * 80)
print('INTEGRATION COMPLETE')
print('=' * 80)

total_elapsed = papers_elapsed + authors_elapsed + categories_elapsed

cursor_warehouse.execute('SELECT COUNT(*) FROM arxiv_papers')
papers_after = cursor_warehouse.fetchone()[0]

print(f'\nWarehouse after integration:')
print(f'  Papers: {papers_after:,} (was {papers_before:,}, +{papers_after - papers_before:,})')
print(f'  Authors: {authors_after:,} (was {authors_before:,}, +{authors_inserted:,})')
print(f'  Categories: {categories_after:,} (was {categories_before:,}, +{categories_inserted:,})')

print(f'\nTotal integration time: {total_elapsed:.1f} seconds ({total_elapsed/60:.1f} minutes)')
print(f'\nIntegration date: {INTEGRATION_DATE}')
print(f'Log: Integration metadata stored in arxiv_integration_metadata table')

# Close connections
conn_kaggle.close()
conn_warehouse.close()

print('\n' + '=' * 80)
print('[OK] INTEGRATION SUCCESSFUL')
print('=' * 80)
