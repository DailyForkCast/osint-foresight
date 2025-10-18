#!/usr/bin/env python3
"""
Check MCF Collection Statistics
Shows what has been collected so far
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

def check_mcf_collection():
    """Display MCF collection statistics"""

    db_path = "F:/OSINT_WAREHOUSE/osint_research.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("=" * 80)
        print("MCF COLLECTION STATISTICS")
        print("=" * 80)
        print(f"Database: {db_path}")
        print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 1. Total documents collected
        cursor.execute("SELECT COUNT(*) FROM mcf_documents")
        total_docs = cursor.fetchone()[0]
        print(f"📊 TOTAL DOCUMENTS COLLECTED: {total_docs}")
        print()

        # 2. Documents by source
        print("📁 DOCUMENTS BY SOURCE:")
        print("-" * 50)
        cursor.execute("""
            SELECT source, COUNT(*) as count,
                   AVG(relevance_score) as avg_score,
                   MAX(relevance_score) as max_score
            FROM mcf_documents
            GROUP BY source
            ORDER BY count DESC
        """)

        for row in cursor.fetchall():
            source, count, avg_score, max_score = row
            print(f"  {source:20} {count:4} docs | Avg Score: {avg_score:.3f} | Max: {max_score:.3f}")

        # 3. High relevance documents
        print()
        print("🎯 HIGH RELEVANCE DOCUMENTS (Score > 0.7):")
        print("-" * 50)
        cursor.execute("""
            SELECT COUNT(*) FROM mcf_documents
            WHERE relevance_score > 0.7
        """)
        high_relevance = cursor.fetchone()[0]
        print(f"  {high_relevance} documents with high MCF relevance")

        # 4. Top entities found
        print()
        print("🏢 TOP CHINESE ENTITIES DETECTED:")
        print("-" * 50)
        cursor.execute("""
            SELECT entity_name, entity_type, COUNT(*) as mentions
            FROM mcf_entities
            GROUP BY entity_name
            ORDER BY mentions DESC
            LIMIT 10
        """)

        for row in cursor.fetchall():
            entity, entity_type, mentions = row
            print(f"  {entity:30} ({entity_type:15}) - {mentions} mentions")

        # 5. Recent collections
        print()
        print("📅 RECENT COLLECTIONS (Last 5):")
        print("-" * 50)
        cursor.execute("""
            SELECT source, title, relevance_score, collection_timestamp
            FROM mcf_documents
            ORDER BY collection_timestamp DESC
            LIMIT 5
        """)

        for row in cursor.fetchall():
            source, title, score, timestamp = row
            title_short = title[:60] + "..." if len(title) > 60 else title
            print(f"  [{source}] {title_short}")
            print(f"    Score: {score:.3f} | Collected: {timestamp}")

        # 6. Scheduled collection stats
        print()
        print("⏰ SCHEDULED COLLECTION RUNS:")
        print("-" * 50)
        cursor.execute("""
            SELECT run_number, timestamp, total_docs
            FROM scheduled_collection_log
            ORDER BY run_number DESC
            LIMIT 5
        """)

        scheduled_runs = cursor.fetchall()
        if scheduled_runs:
            for run_num, timestamp, docs in scheduled_runs:
                print(f"  Run #{run_num}: {docs} docs | {timestamp}")
        else:
            print("  No scheduled runs completed yet")

        # 7. Collection by date
        print()
        print("📈 COLLECTION TREND (By Date):")
        print("-" * 50)
        cursor.execute("""
            SELECT DATE(collection_timestamp) as date, COUNT(*) as daily_count
            FROM mcf_documents
            GROUP BY DATE(collection_timestamp)
            ORDER BY date DESC
            LIMIT 7
        """)

        for row in cursor.fetchall():
            date, count = row
            print(f"  {date}: {count} documents")

        conn.close()

        print()
        print("=" * 80)
        print("✅ Collection system is operational")
        print()

        # Check for output files
        output_dirs = [
            "C:/Projects/OSINT - Foresight/data/processed/mcf_orchestrated",
            "C:/Projects/OSINT - Foresight/data/processed/mcf_enhanced",
            "C:/Projects/OSINT - Foresight/MCF_FINAL_IMPLEMENTATION_REPORT.md",
            "C:/Projects/OSINT - Foresight/MCF_SCHEDULED_COLLECTION_UPDATE.md"
        ]

        print("📂 OUTPUT FILES & REPORTS:")
        print("-" * 50)
        for path_str in output_dirs:
            path = Path(path_str)
            if path.exists():
                if path.is_file():
                    print(f"  ✓ {path.name}")
                else:
                    json_files = list(path.glob("*.json"))
                    if json_files:
                        print(f"  ✓ {path.name}/: {len(json_files)} JSON reports")

        print()
        print("💡 To view specific documents, reports are saved in:")
        print("   - F:/OSINT_WAREHOUSE/ (logs and daily reports)")
        print("   - C:/Projects/OSINT - Foresight/data/processed/mcf_enhanced/")

    except sqlite3.OperationalError as e:
        print(f"❌ Database error: {e}")
        print("   Database may not exist yet or no data collected")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    check_mcf_collection()
