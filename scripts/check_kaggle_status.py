#!/usr/bin/env python3
"""Quick check of Kaggle arXiv processing status"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

db_path = "C:/Projects/OSINT - Foresight/data/kaggle_arxiv_processing.db"

if not Path(db_path).exists():
    print("[ERROR] Database not found - processing may not have started")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get counts
    papers = cursor.execute("SELECT COUNT(*) FROM kaggle_arxiv_papers").fetchone()[0]
    authors = cursor.execute("SELECT COUNT(*) FROM kaggle_arxiv_authors").fetchone()[0]
    tech_classifications = cursor.execute("SELECT COUNT(*) FROM kaggle_arxiv_technology").fetchone()[0]

    # Get technology breakdown
    tech_counts = cursor.execute("""
        SELECT technology_domain, COUNT(DISTINCT arxiv_id) as count
        FROM kaggle_arxiv_technology
        GROUP BY technology_domain
        ORDER BY count DESC
    """).fetchall()

    # Get latest submission date
    latest = cursor.execute("""
        SELECT MAX(submission_year), MAX(submission_month)
        FROM kaggle_arxiv_papers
    """).fetchone()

    conn.close()

    # Print status
    print(f"\n{'='*60}")
    print("KAGGLE ARXIV PROCESSING STATUS")
    print(f"{'='*60}")
    print(f"Total papers processed: {papers:,}")
    print(f"Total author records: {authors:,}")
    print(f"Technology classifications: {tech_classifications:,}")
    print(f"Progress: {(papers/2300000)*100:.1f}% (target: 2.3M papers)")
    print(f"Latest paper: {latest[0]}-{latest[1]:02d}")

    print(f"\n[Technology Distribution]")
    print(f"{'-'*60}")
    for tech, count in tech_counts[:10]:
        pct = (count / papers) * 100 if papers > 0 else 0
        print(f"  {tech:20s}: {count:8,} papers ({pct:5.1f}%)")

    # Calculate if still processing
    if papers < 2300000:
        remaining = 2300000 - papers
        print(f"\n[Still processing...]")
        print(f"   Remaining: {remaining:,} papers ({(remaining/2300000)*100:.1f}%)")
    else:
        print(f"\n[Processing complete!]")

    print(f"{'='*60}\n")

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
