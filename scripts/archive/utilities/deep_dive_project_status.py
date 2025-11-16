#!/usr/bin/env python3
"""
Deep Dive: Complete Project Status Check
Verify actual data coverage, not assumptions
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

def deep_dive_project():
    """Comprehensive project status check"""

    print("=" * 80)
    print("DEEP DIVE: COMPLETE PROJECT STATUS")
    print("=" * 80)
    print(f"\nAnalysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB, timeout=120)
    cursor = conn.cursor()

    # ========================================================================
    # 1. ALL TABLES IN DATABASE
    # ========================================================================
    print("\n[1] ALL TABLES IN MASTER DATABASE")
    print("=" * 80)

    cursor.execute("""
        SELECT name,
               (SELECT COUNT(*) FROM sqlite_master sm WHERE sm.name = m.name AND sm.type='table') as count
        FROM sqlite_master m
        WHERE type='table'
        ORDER BY name
    """)

    all_tables = []
    for table_name, _ in cursor.fetchall():
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            all_tables.append((table_name, count))
            print(f"  {table_name:50} {count:>12,} records")
        except Exception as e:
            print(f"  {table_name:50} ERROR: {e}")

    # ========================================================================
    # 2. TED DATA - YEAR COVERAGE
    # ========================================================================
    print("\n[2] TED (EUROPEAN PROCUREMENT) - YEAR COVERAGE")
    print("=" * 80)

    # Check if ted_contracts_production exists
    ted_tables = [t for t, c in all_tables if 'ted' in t.lower()]

    if ted_tables:
        print(f"\nTED-related tables: {len(ted_tables)}")
        for table in ted_tables:
            print(f"  - {table}")

        # Get year breakdown from ted_contracts_production
        if 'ted_contracts_production' in [t for t, c in all_tables]:
            print("\n  Analyzing ted_contracts_production year coverage...")

            # Publication date analysis
            cursor.execute("""
                SELECT
                    SUBSTR(publication_date, 1, 4) as year,
                    COUNT(*) as count
                FROM ted_contracts_production
                WHERE publication_date IS NOT NULL
                GROUP BY year
                ORDER BY year
            """)

            year_data = cursor.fetchall()

            if year_data:
                print("\n  Year-by-year breakdown:")
                total = sum(c for y, c in year_data)
                for year, count in year_data:
                    pct = (count / total) * 100 if total > 0 else 0
                    print(f"    {year}: {count:>10,} records ({pct:5.1f}%)")

                print(f"\n  Total: {total:,} records")
                print(f"  Year range: {year_data[0][0]} - {year_data[-1][0]}")
                print(f"  Coverage: {len(year_data)} years")

                # Check for gaps
                years = [int(y) for y, c in year_data]
                if years:
                    min_year, max_year = min(years), max(years)
                    expected_years = set(range(min_year, max_year + 1))
                    actual_years = set(years)
                    missing_years = expected_years - actual_years

                    if missing_years:
                        print(f"\n  Missing years: {sorted(missing_years)}")
                    else:
                        print(f"\n  No gaps in coverage from {min_year} to {max_year}")

            else:
                print("\n  No publication_date data found")

            # Source archive analysis
            cursor.execute("""
                SELECT DISTINCT source_archive
                FROM ted_contracts_production
                WHERE source_archive IS NOT NULL
                ORDER BY source_archive
                LIMIT 10
            """)

            archives = cursor.fetchall()
            if archives:
                print("\n  Sample source archives (first 10):")
                for archive, in archives:
                    print(f"    {archive}")

    else:
        print("\n  No TED tables found")

    # ========================================================================
    # 3. USASPENDING DATA
    # ========================================================================
    print("\n[3] USASPENDING (US PROCUREMENT)")
    print("=" * 80)

    usaspending_tables = [t for t, c in all_tables if 'usaspending' in t.lower()]

    if usaspending_tables:
        for table in usaspending_tables:
            count = next(c for t, c in all_tables if t == table)
            print(f"  {table}: {count:,} records")

        # Check usaspending_china_305 specifically
        if 'usaspending_china_305' in usaspending_tables:
            print("\n  Detection type breakdown:")
            cursor.execute("""
                SELECT detection_types, COUNT(*) as count
                FROM usaspending_china_305
                GROUP BY detection_types
                ORDER BY count DESC
                LIMIT 5
            """)

            for detection_type, count in cursor.fetchall():
                print(f"    {count:>6,} | {detection_type}")
    else:
        print("  No USAspending tables found")

    # ========================================================================
    # 4. PATENT DATA
    # ========================================================================
    print("\n[4] PATENT DATA (USPTO)")
    print("=" * 80)

    patent_tables = [t for t, c in all_tables if 'patent' in t.lower() or 'uspto' in t.lower()]

    if patent_tables:
        for table in patent_tables:
            count = next(c for t, c in all_tables if t == table)
            print(f"  {table}: {count:,} records")
    else:
        print("  No patent tables found")

    # ========================================================================
    # 5. OPENALEX DATA
    # ========================================================================
    print("\n[5] OPENALEX (RESEARCH COLLABORATIONS)")
    print("=" * 80)

    openalex_tables = [t for t, c in all_tables if 'openalex' in t.lower()]

    if openalex_tables:
        for table in openalex_tables:
            count = next(c for t, c in all_tables if t == table)
            print(f"  {table}: {count:,} records")
    else:
        print("  No OpenAlex tables found")

    # ========================================================================
    # 6. OTHER DATA SOURCES
    # ========================================================================
    print("\n[6] OTHER DATA SOURCES")
    print("=" * 80)

    other_tables = [t for t, c in all_tables
                   if 'ted' not in t.lower()
                   and 'usaspending' not in t.lower()
                   and 'patent' not in t.lower()
                   and 'uspto' not in t.lower()
                   and 'openalex' not in t.lower()
                   and not t.startswith('sqlite_')]

    if other_tables:
        for table in other_tables:
            count = next(c for t, c in all_tables if t == table)
            print(f"  {table}: {count:,} records")
    else:
        print("  No other tables found")

    conn.close()

    # ========================================================================
    # 7. CHECK CHECKPOINT FILES
    # ========================================================================
    print("\n[7] CHECKPOINT FILES")
    print("=" * 80)

    checkpoint_files = {
        'TED Production': 'data/ted_production_checkpoint.json',
        'TED Extraction': 'data/ted_extraction_checkpoint.json',
        'TED Contractor': 'data/ted_contractor_checkpoint.json',
        'Processing Status': 'data/processing_status.json'
    }

    for name, path in checkpoint_files.items():
        p = Path(path)
        if p.exists():
            size_kb = p.stat().st_size / 1024
            print(f"\n  ✓ {name}: {path}")
            print(f"    Size: {size_kb:.1f} KB")

            # Try to read and show key info
            try:
                with open(p, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        print(f"    Keys: {', '.join(list(data.keys())[:5])}")
                        if 'last_processed_archive' in data:
                            print(f"    Last archive: {data['last_processed_archive']}")
                        if 'processed_files' in data:
                            print(f"    Processed files: {data['processed_files']}")
            except:
                pass
        else:
            print(f"\n  ✗ {name}: Not found")

    # ========================================================================
    # 8. RECENT ANALYSIS FILES
    # ========================================================================
    print("\n[8] RECENT ANALYSIS FILES (Last 10)")
    print("=" * 80)

    analysis_dir = Path("analysis")
    if analysis_dir.exists():
        recent_files = sorted(
            analysis_dir.glob("*.md"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:10]

        for file in recent_files:
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            print(f"  {mtime.strftime('%Y-%m-%d %H:%M')} | {file.name}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print(f"\n  Total tables: {len(all_tables)}")
    print(f"  TED tables: {len(ted_tables)}")
    print(f"  USAspending tables: {len(usaspending_tables)}")
    print(f"  Patent tables: {len(patent_tables)}")
    print(f"  OpenAlex tables: {len(openalex_tables)}")
    print(f"  Other tables: {len(other_tables)}")

    total_records = sum(c for t, c in all_tables if not t.startswith('sqlite_'))
    print(f"\n  Total records: {total_records:,}")

if __name__ == "__main__":
    try:
        deep_dive_project()
        print(f"\n[SUCCESS] Deep dive complete")
    except Exception as e:
        print(f"\n[ERROR] Deep dive failed: {e}")
        import traceback
        traceback.print_exc()
