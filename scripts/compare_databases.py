#!/usr/bin/env python3
"""
Compare contents of two SQL databases
"""

import sqlite3
from pathlib import Path

def analyze_database(db_path: str):
    """Analyze a database and return statistics"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    stats = {
        "path": db_path,
        "size_mb": Path(db_path).stat().st_size / (1024 * 1024),
        "tables": {},
        "mcf_data": {},
        "cordis_data": {},
        "sec_data": {}
    }

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    for table_name in tables:
        table = table_name[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        stats["tables"][table] = count

        # MCF specific tables
        if 'mcf' in table.lower():
            stats["mcf_data"][table] = count

        # CORDIS specific tables
        elif 'cordis' in table.lower():
            stats["cordis_data"][table] = count

        # SEC specific tables
        elif 'sec' in table.lower():
            stats["sec_data"][table] = count

    conn.close()
    return stats

def compare_databases():
    """Compare the two databases"""

    # Database paths
    db1_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    db2_path = "F:/OSINT_WAREHOUSE/osint_research.db"

    print("=" * 80)
    print("SQL DATABASE COMPARISON")
    print("=" * 80)

    # Analyze both databases
    db1_stats = analyze_database(db1_path)
    db2_stats = analyze_database(db2_path)

    # Database 1 Info
    print(f"\n[DATABASE 1]: {db1_path}")
    print(f"   Size: {db1_stats['size_mb']:.2f} MB")
    print(f"   Total Tables: {len(db1_stats['tables'])}")

    if db1_stats['tables']:
        print("\n   Tables and Record Counts:")
        for table, count in sorted(db1_stats['tables'].items()):
            print(f"      - {table}: {count:,} records")

    # Database 2 Info
    print(f"\n[DATABASE 2]: {db2_path}")
    print(f"   Size: {db2_stats['size_mb']:.2f} MB")
    print(f"   Total Tables: {len(db2_stats['tables'])}")

    if db2_stats['tables']:
        print("\n   Tables and Record Counts:")
        for table, count in sorted(db2_stats['tables'].items()):
            print(f"      - {table}: {count:,} records")

    # Comparison Summary
    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)

    # Find common and unique tables
    tables1 = set(db1_stats['tables'].keys())
    tables2 = set(db2_stats['tables'].keys())

    common_tables = tables1.intersection(tables2)
    unique_to_db1 = tables1 - tables2
    unique_to_db2 = tables2 - tables1

    print(f"\n[Common Tables]: {len(common_tables)}")
    if common_tables:
        for table in sorted(common_tables):
            count1 = db1_stats['tables'][table]
            count2 = db2_stats['tables'][table]
            diff = count2 - count1
            print(f"   - {table}: DB1={count1:,} | DB2={count2:,} | Diff={diff:+,}")

    print(f"\n[Unique to DATABASE 1]: {len(unique_to_db1)}")
    if unique_to_db1:
        for table in sorted(unique_to_db1):
            print(f"   - {table}: {db1_stats['tables'][table]:,} records")

    print(f"\n[Unique to DATABASE 2]: {len(unique_to_db2)}")
    if unique_to_db2:
        for table in sorted(unique_to_db2):
            print(f"   - {table}: {db2_stats['tables'][table]:,} records")

    # Content Analysis
    print("\n" + "=" * 80)
    print("CONTENT ANALYSIS")
    print("=" * 80)

    # MCF Data
    print("\n[MCF (Military-Civil Fusion) Data]:")
    mcf1_total = sum(db1_stats['mcf_data'].values())
    mcf2_total = sum(db2_stats['mcf_data'].values())
    print(f"   DATABASE 1: {mcf1_total:,} total MCF records")
    print(f"   DATABASE 2: {mcf2_total:,} total MCF records")

    # CORDIS Data
    print("\n[CORDIS (EU Research) Data]:")
    cordis1_total = sum(db1_stats['cordis_data'].values())
    cordis2_total = sum(db2_stats['cordis_data'].values())
    print(f"   DATABASE 1: {cordis1_total:,} total CORDIS records")
    print(f"   DATABASE 2: {cordis2_total:,} total CORDIS records")

    # SEC Data
    print("\n[SEC EDGAR Data]:")
    sec1_total = sum(db1_stats['sec_data'].values())
    sec2_total = sum(db2_stats['sec_data'].values())
    print(f"   DATABASE 1: {sec1_total:,} total SEC records")
    print(f"   DATABASE 2: {sec2_total:,} total SEC records")

    # Sample MCF documents from Database 2
    print("\n" + "=" * 80)
    print("SAMPLE MCF DOCUMENTS FROM DATABASE 2 (F: drive)")
    print("=" * 80)

    try:
        conn2 = sqlite3.connect(db2_path)
        cursor2 = conn2.cursor()

        # Check if mcf_documents table exists
        cursor2.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mcf_documents'")
        if cursor2.fetchone():
            cursor2.execute("""
                SELECT title, relevance_score, collector
                FROM mcf_documents
                ORDER BY relevance_score DESC
                LIMIT 5
            """)
            docs = cursor2.fetchall()

            if docs:
                print("\nTop 5 MCF Documents by Relevance:")
                for i, (title, score, collector) in enumerate(docs, 1):
                    print(f"{i}. [{score:.2f}] {title[:60]}... (Source: {collector})")

        conn2.close()
    except Exception as e:
        print(f"Could not read MCF documents: {e}")

    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    if mcf2_total > mcf1_total:
        print("\n-> DATABASE 2 (F: drive) has more MCF data that should be imported")

    if unique_to_db2:
        print(f"-> DATABASE 2 has {len(unique_to_db2)} unique tables to consider importing")

    if unique_to_db1:
        print(f"-> DATABASE 1 (local) has {len(unique_to_db1)} tables not in DATABASE 2")

    print("\n[MERGE STRATEGY]:")
    print("   1. Import missing MCF documents from DATABASE 2 to DATABASE 1")
    print("   2. Preserve CORDIS and SEC data in DATABASE 1")
    print("   3. Consider merging unique tables from DATABASE 2")
    print("   4. Use DATABASE 1 as the master going forward")

if __name__ == "__main__":
    compare_databases()
