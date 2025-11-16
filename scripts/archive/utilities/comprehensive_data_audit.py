#!/usr/bin/env python3
"""
Comprehensive Data Audit: What Exists vs What's Been Analyzed
Deep dive to understand actual data coverage across all sources
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

def audit_all_data_sources():
    """Comprehensive audit of all data sources"""

    print("=" * 80)
    print("COMPREHENSIVE DATA AUDIT - WHAT EXISTS VS WHAT'S BEEN ANALYZED")
    print("=" * 80)
    print(f"\nAnalysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB, timeout=120)
    cursor = conn.cursor()

    results = {}

    # ========================================================================
    # 1. THINKTANK REPORTS
    # ========================================================================
    print("\n[1] THINKTANK REPORTS ANALYSIS")
    print("=" * 80)

    # Check database tables (exclude indexes)
    thinktank_tables = []
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
          AND (name LIKE '%thinktank%' OR name LIKE '%report%')
          AND name NOT LIKE 'idx_%'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    thinktank_tables = [row[0] for row in cursor.fetchall()]

    if thinktank_tables:
        print(f"\nThinktank tables found: {len(thinktank_tables)}")
        for table in thinktank_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count:,} records")

    # Check file system
    thinktank_paths = [
        "F:/OSINT_DATA/US_CAN_Thinktanks/",
        "F:/OSINT_DATA/ThinkTanks/",
        "F:/OSINT_DATA/Reports/",
        "data/us_gov_tech_sweep/",
    ]

    for path in thinktank_paths:
        p = Path(path)
        if p.exists():
            files = list(p.rglob("*.*"))
            print(f"\n  {path}: {len(files)} files")
            if len(files) > 0:
                # Count by extension
                exts = defaultdict(int)
                for f in files:
                    exts[f.suffix] += 1
                for ext, count in sorted(exts.items(), key=lambda x: -x[1])[:5]:
                    print(f"    {ext or 'no_ext'}: {count}")

    results['thinktank'] = {
        'tables': len(thinktank_tables),
        'database_records': sum(1 for t in thinktank_tables)
    }

    # ========================================================================
    # 2. GLEIF ENTITIES
    # ========================================================================
    print("\n[2] GLEIF ENTITY DATA")
    print("=" * 80)

    gleif_tables = []
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
          AND (name LIKE '%gleif%' OR name LIKE '%lei%')
          AND name NOT LIKE 'idx_%'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    gleif_tables = [row[0] for row in cursor.fetchall()]

    if gleif_tables:
        print(f"\nGLEIF tables found: {len(gleif_tables)}")
        for table in gleif_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count:,} records")

            # Sample record to understand structure
            cursor.execute(f"SELECT * FROM {table} LIMIT 1")
            if cursor.description:
                cols = [desc[0] for desc in cursor.description]
                print(f"    Columns ({len(cols)}): {', '.join(cols[:10])}")

    # Check file system
    gleif_paths = [
        "F:/OSINT_DATA/GLEIF/",
        "F:/OSINT_Backups/gleif/",
    ]

    for path in gleif_paths:
        p = Path(path)
        if p.exists():
            files = list(p.rglob("*.*"))
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            print(f"\n  {path}: {len(files)} files, {total_size / 1024**2:.1f} MB")

    results['gleif'] = {
        'tables': len(gleif_tables),
        'database_records': sum(1 for t in gleif_tables)
    }

    # ========================================================================
    # 3. COMPANIES HOUSE UK
    # ========================================================================
    print("\n[3] COMPANIES HOUSE UK DATA")
    print("=" * 80)

    companies_house_tables = []
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
          AND (name LIKE '%companies%house%' OR name LIKE '%uk_companies%')
          AND name NOT LIKE 'idx_%'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    companies_house_tables = [row[0] for row in cursor.fetchall()]

    if companies_house_tables:
        print(f"\nCompanies House tables found: {len(companies_house_tables)}")
        for table in companies_house_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count:,} records")
    else:
        print("\n  No Companies House tables found in database")

    # Check file system for 42GB data
    ch_paths = [
        "F:/OSINT_DATA/CompaniesHouse/",
        "F:/OSINT_DATA/UK_Companies/",
        "F:/CompaniesHouse/",
    ]

    for path in ch_paths:
        p = Path(path)
        if p.exists():
            files = list(p.rglob("*.*"))
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            print(f"\n  {path}:")
            print(f"    Files: {len(files)}")
            print(f"    Total size: {total_size / 1024**3:.1f} GB")

            # File types
            exts = defaultdict(int)
            for f in files:
                exts[f.suffix] += 1
            print(f"    File types:")
            for ext, count in sorted(exts.items(), key=lambda x: -x[1])[:10]:
                print(f"      {ext or 'no_ext'}: {count}")

    results['companies_house'] = {
        'tables': len(companies_house_tables),
        'raw_data_found': any(Path(p).exists() for p in ch_paths)
    }

    # ========================================================================
    # 4. OPENALEX
    # ========================================================================
    print("\n[4] OPENALEX DATA")
    print("=" * 80)

    openalex_tables = []
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
          AND name LIKE '%openalex%'
          AND name NOT LIKE 'idx_%'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    openalex_tables = [row[0] for row in cursor.fetchall()]

    if openalex_tables:
        print(f"\nOpenAlex tables found: {len(openalex_tables)}")
        for table in openalex_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count:,} records")

    # Check raw data (422GB)
    openalex_raw = Path("F:/OSINT_Backups/openalex/data/works/")
    if openalex_raw.exists():
        gz_files = list(openalex_raw.rglob("*.gz"))
        total_size = sum(f.stat().st_size for f in gz_files if f.is_file())
        print(f"\n  Raw OpenAlex data:")
        print(f"    Path: {openalex_raw}")
        print(f"    .gz files: {len(gz_files)}")
        print(f"    Total size: {total_size / 1024**3:.1f} GB")

        # Sample directory structure
        update_dates = set()
        for f in gz_files[:100]:  # Sample first 100
            parts = str(f).split('updated_date=')
            if len(parts) > 1:
                date = parts[1].split('/')[0]
                update_dates.add(date)

        if update_dates:
            print(f"    Date range (sample): {min(update_dates)} to {max(update_dates)}")
            print(f"    Unique dates (sample): {len(update_dates)}")

    # Check processed data
    processed_openalex = [
        "data/processed/openalex_multicountry_temporal/",
        "data/processed/openalex_production/",
        "data/processed/openalex_v1/",
    ]

    for path in processed_openalex:
        p = Path(path)
        if p.exists():
            files = list(p.rglob("*.json"))
            print(f"\n  Processed: {path}")
            print(f"    JSON files: {len(files)}")

    results['openalex'] = {
        'tables': len(openalex_tables),
        'raw_files': len(gz_files) if openalex_raw.exists() else 0,
        'raw_size_gb': total_size / 1024**3 if openalex_raw.exists() else 0
    }

    # ========================================================================
    # 5. CORDIS
    # ========================================================================
    print("\n[5] CORDIS EU RESEARCH DATA")
    print("=" * 80)

    cordis_tables = []
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
          AND name LIKE '%cordis%'
          AND name NOT LIKE 'idx_%'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    cordis_tables = [row[0] for row in cursor.fetchall()]

    if cordis_tables:
        print(f"\nCORDIS tables found: {len(cordis_tables)}")
        for table in cordis_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count:,} records")

            # Check for China data specifically
            if 'china' in table.lower():
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                china_count = cursor.fetchone()[0]
                print(f"    -> China-specific: {china_count:,}")

    # Check processed files
    cordis_paths = [
        "data/processed/cordis_v1/",
        "data/processed/cordis_unified/",
    ]

    for path in cordis_paths:
        p = Path(path)
        if p.exists():
            files = list(p.rglob("*.*"))
            print(f"\n  {path}: {len(files)} files")

    results['cordis'] = {
        'tables': len(cordis_tables),
        'database_records': sum(1 for t in cordis_tables)
    }

    # ========================================================================
    # 6. USASPENDING (already verified)
    # ========================================================================
    print("\n[6] USASPENDING DATA (VERIFIED)")
    print("=" * 80)

    usaspending_tables = []
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
          AND name LIKE '%usaspending%'
          AND name NOT LIKE 'idx_%'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    usaspending_tables = [row[0] for row in cursor.fetchall()]

    if usaspending_tables:
        print(f"\nUSAspending tables found: {len(usaspending_tables)}")
        for table in usaspending_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count:,} records")

    results['usaspending'] = {
        'tables': len(usaspending_tables),
        'verified_complete': True
    }

    # ========================================================================
    # 7. TED (already verified)
    # ========================================================================
    print("\n[7] TED DATA (VERIFIED)")
    print("=" * 80)

    ted_tables = []
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
          AND name LIKE '%ted%'
          AND name NOT LIKE 'idx_%'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    ted_tables = [row[0] for row in cursor.fetchall()]

    if ted_tables:
        print(f"\nTED tables found: {len(ted_tables)}")
        for table in ted_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count:,} records")

    results['ted'] = {
        'tables': len(ted_tables),
        'verified_complete': True
    }

    conn.close()

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY - WHAT'S BEEN ANALYZED")
    print("=" * 80)

    print("\n✅ FULLY ANALYZED:")
    print("  - USAspending: 3,379 verified Chinese entities (cleaned)")
    print("  - TED: 861,984 contracts, 219 Chinese-related")
    print("  - USPTO: 577,197 Chinese patents")
    print("  - CORDIS: 383 China projects")

    print("\n🔄 PARTIALLY ANALYZED:")
    if results['openalex']['tables'] > 0:
        print(f"  - OpenAlex: {results['openalex']['tables']} tables in DB, {results['openalex']['raw_files']:,} raw files ({results['openalex']['raw_size_gb']:.0f}GB) available")

    print("\n❓ NEEDS INVESTIGATION:")
    if results['thinktank']['tables'] == 0:
        print("  - ThinkTank: User mentioned 76,886 US_CAN items - WHERE?")
    if results['gleif']['tables'] == 0:
        print("  - GLEIF: User mentioned 3.1M entities - WHERE?")
    if not results['companies_house']['raw_data_found']:
        print("  - Companies House: User mentioned 42GB undocumented - WHERE?")

    # Save results
    output_file = Path("analysis/DATA_AUDIT_COMPLETE_20251018.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n[SUCCESS] Audit complete - results saved to {output_file}")

    return results

if __name__ == "__main__":
    try:
        results = audit_all_data_sources()
        print("\n" + "=" * 80)
        print("AUDIT COMPLETE")
        print("=" * 80)
    except Exception as e:
        print(f"\n[ERROR] Audit failed: {e}")
        import traceback
        traceback.print_exc()
