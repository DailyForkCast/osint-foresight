#!/usr/bin/env python3
"""Investigate original database for duplicates or data quality issues."""

import sqlite3

conn = sqlite3.connect('C:/Projects/OSINT - Foresight/data/kaggle_arxiv_processing_v1_original.db')
cursor = conn.cursor()

print('=' * 80)
print('INVESTIGATING ORIGINAL DATABASE')
print('=' * 80)

# Check for duplicate technology classifications
cursor.execute('''
    SELECT arxiv_id, technology_domain, COUNT(*) as dup_count
    FROM kaggle_arxiv_technology
    GROUP BY arxiv_id, technology_domain
    HAVING COUNT(*) > 1
    LIMIT 10
''')
duplicates = cursor.fetchall()

if duplicates:
    print('\n[CRITICAL] DUPLICATE TECHNOLOGY CLASSIFICATIONS FOUND:')
    print(f'Sample duplicates (showing first 10):')
    for arxiv_id, tech, count in duplicates:
        print(f'  Paper {arxiv_id} has {count} duplicate {tech} classifications')

    # Get total duplicate count
    cursor.execute('''
        SELECT COUNT(*)
        FROM (
            SELECT arxiv_id, technology_domain
            FROM kaggle_arxiv_technology
            GROUP BY arxiv_id, technology_domain
            HAVING COUNT(*) > 1
        )
    ''')
    total_dups = cursor.fetchone()[0]
    print(f'\nTotal papers with duplicate classifications: {total_dups:,}')
else:
    print('\n[OK] No duplicate technology classifications found')

# Check average classifications per paper
cursor.execute('SELECT COUNT(*) FROM kaggle_arxiv_papers')
total_papers = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM kaggle_arxiv_technology')
total_classifications = cursor.fetchone()[0]

print(f'\n{"-" * 80}')
print(f'Total papers: {total_papers:,}')
print(f'Total technology classifications: {total_classifications:,}')
print(f'Average classifications per paper: {total_classifications / total_papers:.2f}')

# Sample a paper to see its classifications
cursor.execute('''
    SELECT arxiv_id, COUNT(*) as tech_count
    FROM kaggle_arxiv_technology
    GROUP BY arxiv_id
    ORDER BY tech_count DESC
    LIMIT 1
''')
max_paper = cursor.fetchone()
print(f'\n{"-" * 80}')
print(f'Paper with most classifications: {max_paper[0]} ({max_paper[1]} technologies)')

cursor.execute('''
    SELECT technology_domain, match_score
    FROM kaggle_arxiv_technology
    WHERE arxiv_id = ?
''', (max_paper[0],))
classifications = cursor.fetchall()
print(f'Classifications for {max_paper[0]}:')
for tech, score in classifications:
    print(f'  - {tech}: {score:.2f}')

conn.close()
