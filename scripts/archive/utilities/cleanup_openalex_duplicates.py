#!/usr/bin/env python3
"""
Clean up duplicate records in OpenAlex database
"""

import sqlite3
from pathlib import Path

db_path = Path("F:/OSINT_Data/openalex_analytics/openalex_chinese_research.db")

if not db_path.exists():
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*80)
print("OPENALEX DATABASE CLEANUP")
print("="*80)

# Check duplicates before
cursor.execute("SELECT COUNT(*) FROM research_papers_expanded")
total_before = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT openalex_id) FROM research_papers_expanded")
unique_before = cursor.fetchone()[0]

duplicates = total_before - unique_before

print(f"\nBefore cleanup:")
print(f"  Total records: {total_before:,}")
print(f"  Unique records: {unique_before:,}")
print(f"  Duplicates: {duplicates:,}")

if duplicates > 0:
    print(f"\nRemoving {duplicates:,} duplicate records...")

    # Create temp table with deduplicated data
    cursor.execute("""
        CREATE TEMP TABLE research_papers_deduped AS
        SELECT *
        FROM research_papers_expanded
        WHERE rowid IN (
            SELECT MIN(rowid)
            FROM research_papers_expanded
            GROUP BY openalex_id
        )
    """)

    # Replace original table
    cursor.execute("DROP TABLE research_papers_expanded")
    cursor.execute("ALTER TABLE temp.research_papers_deduped RENAME TO research_papers_expanded")

    # Recreate indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_openalex_id ON research_papers_expanded(openalex_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tech_category ON research_papers_expanded(technology_category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pub_year ON research_papers_expanded(publication_year)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_collab_type ON research_papers_expanded(collaboration_type)")

    conn.commit()

    # Check after cleanup
    cursor.execute("SELECT COUNT(*) FROM research_papers_expanded")
    total_after = cursor.fetchone()[0]

    print(f"\nAfter cleanup:")
    print(f"  Total records: {total_after:,}")
    print(f"  Removed: {total_before - total_after:,} duplicates")

    # Verify by topic
    print(f"\nFinal breakdown by topic:")
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

    print(f"\n[OK] Database cleaned successfully!")
else:
    print(f"\n[OK] No duplicates found!")

conn.close()

print("\n" + "="*80)
print("CLEANUP COMPLETE")
print("="*80)
