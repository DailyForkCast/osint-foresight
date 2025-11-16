#!/usr/bin/env python3
"""
Recreate OpenAlex database from CSV files
"""

import sqlite3
from pathlib import Path
import pandas as pd

db_path = Path("F:/OSINT_Data/openalex_analytics/openalex_chinese_research.db")
csv_dir = Path("data/openalex_chinese_research")

print("="*80)
print("RECREATING OPENALEX DATABASE FROM CSV FILES")
print("="*80)

# Load all CSV files
csv_files = list(csv_dir.glob("*_expanded.csv"))

print(f"\nFound {len(csv_files)} CSV files:")
for csv_file in sorted(csv_files):
    print(f"  - {csv_file.name}")

print(f"\nLoading CSV files...")

all_dfs = []
total_records = 0

for csv_file in sorted(csv_files):
    df = pd.read_csv(csv_file)
    all_dfs.append(df)
    total_records += len(df)
    topic = csv_file.stem.replace('_expanded', '')
    print(f"  {topic}: {len(df):,} records")

# Combine all dataframes
print(f"\nCombining all data...")
combined_df = pd.concat(all_dfs, ignore_index=True)

print(f"  Total records: {len(combined_df):,}")

# Remove duplicates
print(f"\nRemoving duplicates...")
before_dedup = len(combined_df)
combined_df = combined_df.drop_duplicates(subset=['openalex_id'], keep='first')
after_dedup = len(combined_df)

print(f"  Before: {before_dedup:,}")
print(f"  After: {after_dedup:,}")
print(f"  Removed: {before_dedup - after_dedup:,} duplicates")

# Create database
print(f"\nCreating database table...")

conn = sqlite3.connect(db_path)

# Drop if exists and recreate
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS research_papers_expanded")

# Write to database
combined_df.to_sql('research_papers_expanded', conn, if_exists='replace', index=False)

# Create indices
print(f"\nCreating indices...")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_openalex_id ON research_papers_expanded(openalex_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_tech_category ON research_papers_expanded(technology_category)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_pub_year ON research_papers_expanded(publication_year)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_collab_type ON research_papers_expanded(collaboration_type)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_doi ON research_papers_expanded(doi)")

conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM research_papers_expanded")
final_count = cursor.fetchone()[0]

print(f"\n[OK] Database created successfully!")
print(f"  Table: research_papers_expanded")
print(f"  Records: {final_count:,}")

# Breakdown by topic
print(f"\nBreakdown by topic:")
cursor.execute("""
    SELECT technology_category, COUNT(*) as count
    FROM research_papers_expanded
    GROUP BY technology_category
    ORDER BY count DESC
""")

for row in cursor.fetchall():
    topic = row[0]
    count = row[1]
    print(f"  {topic}: {count:,}")

conn.close()

print("\n" + "="*80)
print("DATABASE RECREATION COMPLETE")
print("="*80)
print(f"\nDatabase: {db_path}")
print(f"Unique records: {final_count:,}")
