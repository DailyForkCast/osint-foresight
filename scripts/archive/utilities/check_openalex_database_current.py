#!/usr/bin/env python3
"""
Check current status of OpenAlex database
"""

import sqlite3
from pathlib import Path
import pandas as pd

db_path = Path("F:/OSINT_Data/openalex_analytics/openalex_chinese_research.db")

if not db_path.exists():
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)

print("="*80)
print("OPENALEX DATABASE CURRENT STATUS")
print("="*80)

# Get all tables
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print(f"\nTables in database: {', '.join(tables)}")

# Check each table
for table in tables:
    print(f"\n[{table.upper()}]")

    # Get count
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  Total records: {count:,}")

    # If it's a research papers table, get breakdown by topic
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]

    if 'technology_category' in columns:
        print(f"\n  Breakdown by technology:")
        cursor.execute(f"""
            SELECT technology_category, COUNT(*) as count
            FROM {table}
            GROUP BY technology_category
            ORDER BY count DESC
        """)

        for row in cursor.fetchall():
            topic = row[0]
            topic_count = row[1]
            print(f"    {topic}: {topic_count:,}")

        # Get year range
        if 'publication_year' in columns:
            cursor.execute(f"""
                SELECT MIN(publication_year), MAX(publication_year)
                FROM {table}
            """)
            min_year, max_year = cursor.fetchone()
            print(f"\n  Year range: {min_year}-{max_year}")

        # Check for duplicates
        if 'openalex_id' in columns:
            cursor.execute(f"""
                SELECT COUNT(*) - COUNT(DISTINCT openalex_id) as duplicates
                FROM {table}
            """)
            duplicates = cursor.fetchone()[0]
            print(f"  Duplicate records: {duplicates:,}")

# Overall summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

# Get total unique papers across all tables
if 'research_papers_expanded' in tables:
    cursor.execute("SELECT COUNT(DISTINCT openalex_id) FROM research_papers_expanded")
    unique_expanded = cursor.fetchone()[0]
    print(f"\nUnique papers in expanded table: {unique_expanded:,}")

if 'research_papers' in tables:
    cursor.execute("SELECT COUNT(DISTINCT openalex_id) FROM research_papers")
    unique_initial = cursor.fetchone()[0]
    print(f"Unique papers in initial table: {unique_initial:,}")

conn.close()

# Check CSV files too
csv_dir = Path("data/openalex_chinese_research")
if csv_dir.exists():
    print("\n" + "="*80)
    print("CSV FILES STATUS")
    print("="*80)

    csv_files = list(csv_dir.glob("*_expanded.csv"))
    print(f"\nFound {len(csv_files)} expanded CSV files:")

    total_csv_records = 0
    for csv_file in sorted(csv_files):
        df = pd.read_csv(csv_file)
        total_csv_records += len(df)
        topic = csv_file.stem.replace('_expanded', '')
        print(f"  {topic}: {len(df):,} records")

    print(f"\nTotal records in CSV files: {total_csv_records:,}")

print("\n" + "="*80)
print("COMPARISON TO TARGET")
print("="*80)

targets = {
    'semiconductors': 30026,
    'artificial_intelligence': 8929,
    'quantum_computing': 10635,
    'advanced_materials': 24339,
    '5g_wireless': 3160,
    'robotics': 48771,
    'biotechnology': 5198,
    'aerospace': 10425,
    'new_energy': 10870,
    'advanced_manufacturing': 27838
}

total_target = sum(targets.values())
print(f"\nTotal target across all topics: {total_target:,}")
print(f"\nWe need to extract: {total_target - unique_expanded:,} more papers")
print(f"Current coverage: {unique_expanded/total_target*100:.1f}%")
