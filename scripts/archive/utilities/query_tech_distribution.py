#!/usr/bin/env python3
"""Query Kaggle arXiv technology distribution from database."""

import sqlite3

# Connect to database
conn = sqlite3.connect('C:/Projects/OSINT - Foresight/data/kaggle_arxiv_processing.db')
cursor = conn.cursor()

# Get technology distribution
cursor.execute('''
    SELECT technology_domain, COUNT(*) as paper_count
    FROM kaggle_arxiv_technology
    GROUP BY technology_domain
    ORDER BY paper_count DESC
''')
results = cursor.fetchall()

print('=' * 60)
print('KAGGLE ARXIV TECHNOLOGY DISTRIBUTION')
print('=' * 60)
total = sum([count for _, count in results])
print(f'Total technology classifications: {total:,}\n')

for tech, count in results:
    pct = (count / total) * 100
    print(f'{tech:20s}: {count:7,} papers ({pct:5.1f}%)')

# Get total unique papers
cursor.execute('SELECT COUNT(*) FROM kaggle_arxiv_papers')
total_papers = cursor.fetchone()[0]
print(f'\n{"-" * 60}')
print(f'Total unique papers: {total_papers:,}')
print(f'Average technologies per paper: {total / total_papers:.2f}')

conn.close()
