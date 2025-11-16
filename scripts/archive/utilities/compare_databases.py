#!/usr/bin/env python3
"""Compare original vs expanded Kaggle arXiv databases."""

import sqlite3

print('=' * 80)
print('KAGGLE ARXIV DATABASE COMPARISON: ORIGINAL vs EXPANDED')
print('=' * 80)

# Connect to both databases
conn_orig = sqlite3.connect('C:/Projects/OSINT - Foresight/data/kaggle_arxiv_processing_v1_original.db')
conn_new = sqlite3.connect('C:/Projects/OSINT - Foresight/data/kaggle_arxiv_processing.db')

cursor_orig = conn_orig.cursor()
cursor_new = conn_new.cursor()

# Get totals
cursor_orig.execute('SELECT COUNT(*) FROM kaggle_arxiv_papers')
orig_papers = cursor_orig.fetchone()[0]

cursor_new.execute('SELECT COUNT(*) FROM kaggle_arxiv_papers')
new_papers = cursor_new.fetchone()[0]

print(f'\nTOTAL PAPERS:')
print(f'  Original database: {orig_papers:,}')
print(f'  Expanded database: {new_papers:,}')
print(f'  Difference: {new_papers - orig_papers:+,} ({((new_papers/orig_papers - 1) * 100):+.1f}%)')

# Get technology distributions
cursor_orig.execute('''
    SELECT technology_domain, COUNT(*) as paper_count
    FROM kaggle_arxiv_technology
    GROUP BY technology_domain
    ORDER BY technology_domain
''')
orig_tech = {tech: count for tech, count in cursor_orig.fetchall()}

cursor_new.execute('''
    SELECT technology_domain, COUNT(*) as paper_count
    FROM kaggle_arxiv_technology
    GROUP BY technology_domain
    ORDER BY technology_domain
''')
new_tech = {tech: count for tech, count in cursor_new.fetchall()}

print(f'\n{"TECHNOLOGY":<20} {"ORIGINAL":>12} {"EXPANDED":>12} {"CHANGE":>12} {"% CHANGE":>10}')
print('-' * 80)

all_techs = sorted(set(list(orig_tech.keys()) + list(new_tech.keys())))
for tech in all_techs:
    orig_count = orig_tech.get(tech, 0)
    new_count = new_tech.get(tech, 0)
    diff = new_count - orig_count
    pct_change = ((new_count / orig_count - 1) * 100) if orig_count > 0 else 0
    print(f'{tech:<20} {orig_count:>12,} {new_count:>12,} {diff:>+12,} {pct_change:>+9.1f}%')

# Totals
orig_total = sum(orig_tech.values())
new_total = sum(new_tech.values())
diff_total = new_total - orig_total
pct_total = ((new_total / orig_total - 1) * 100) if orig_total > 0 else 0

print('-' * 80)
print(f'{"TOTAL":<20} {orig_total:>12,} {new_total:>12,} {diff_total:>+12,} {pct_total:>+9.1f}%')

conn_orig.close()
conn_new.close()

print('\n' + '=' * 80)
print('KEY FINDINGS:')
print('=' * 80)
print(f'[*] Biotechnology expansion: {orig_tech.get("Biotechnology", 0):,} -> {new_tech.get("Biotechnology", 0):,}')
print(f'[*] Energy expansion: {orig_tech.get("Energy", 0):,} -> {new_tech.get("Energy", 0):,}')
print(f'[*] Space expansion: {orig_tech.get("Space", 0):,} -> {new_tech.get("Space", 0):,}')
