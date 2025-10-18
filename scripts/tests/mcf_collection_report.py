#!/usr/bin/env python3
"""
MCF Collection Report - Simple ASCII Version
"""

import sqlite3
from datetime import datetime
from pathlib import Path

db_path = "F:/OSINT_WAREHOUSE/osint_research.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 80)
    print("MCF COLLECTION REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Total documents
    cursor.execute("SELECT COUNT(*) FROM mcf_documents")
    total = cursor.fetchone()[0]
    print(f"TOTAL DOCUMENTS: {total}")
    print()

    # By source
    print("DOCUMENTS BY SOURCE:")
    print("-" * 50)
    cursor.execute("""
        SELECT source, COUNT(*) as count,
               AVG(relevance_score) as avg_score
        FROM mcf_documents
        GROUP BY source
        ORDER BY count DESC
    """)

    for row in cursor.fetchall():
        source, count, avg_score = row
        print(f"  {source:25} {count:4} docs | Avg: {avg_score:.3f}")

    # High relevance
    cursor.execute("SELECT COUNT(*) FROM mcf_documents WHERE relevance_score > 0.7")
    high_rel = cursor.fetchone()[0]
    print(f"\nHIGH RELEVANCE DOCS (>0.7): {high_rel}")

    # Top entities
    print("\nTOP ENTITIES FOUND:")
    print("-" * 50)
    cursor.execute("""
        SELECT entity_name, COUNT(*) as mentions
        FROM mcf_entities
        GROUP BY entity_name
        ORDER BY mentions DESC
        LIMIT 10
    """)

    for entity, mentions in cursor.fetchall():
        print(f"  {entity:30} - {mentions} mentions")

    # Recent docs
    print("\nMOST RECENT DOCUMENTS:")
    print("-" * 50)
    cursor.execute("""
        SELECT source, title, relevance_score
        FROM mcf_documents
        ORDER BY collection_timestamp DESC
        LIMIT 5
    """)

    for source, title, score in cursor.fetchall():
        title_short = title[:50] + "..." if len(title) > 50 else title
        print(f"  [{source}] {title_short} (Score: {score:.3f})")

    conn.close()
    print("\n" + "=" * 80)

except Exception as e:
    print(f"Error accessing database: {e}")

# Check output files
print("\nOUTPUT LOCATIONS:")
print("-" * 50)

locations = [
    ("Database", "F:/OSINT_WAREHOUSE/osint_research.db"),
    ("Reports", "C:/Projects/OSINT - Foresight/data/processed/mcf_enhanced/"),
    ("Logs", "F:/OSINT_WAREHOUSE/scheduled_collection.log"),
    ("Implementation Report", "C:/Projects/OSINT - Foresight/MCF_FINAL_IMPLEMENTATION_REPORT.md")
]

for name, path in locations:
    p = Path(path)
    if p.exists():
        print(f"  [OK] {name}: {path}")
    else:
        print(f"  [--] {name}: {path}")
