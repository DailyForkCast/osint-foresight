#!/usr/bin/env python3
"""
Comprehensive validation of OpenAIRE, OpenAlex, and ArXiv datasets

Checks for:
1. Data completeness (empty fields, missing country data)
2. Coverage statistics (Netherlands and other EU countries)
3. Chinese collaboration detection
4. Temporal coverage
5. Schema validation
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

def log(msg):
    """Log with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

def validate_openaire(conn):
    """Validate OpenAIRE dataset."""
    cursor = conn.cursor()

    log("\n" + "="*80)
    log("OPENAIRE VALIDATION")
    log("="*80)

    # Get table schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%openaire%'")
    tables = [row[0] for row in cursor.fetchall()]
    log(f"\nOpenAIRE tables: {tables}")

    results = {}

    for table in tables:
        log(f"\n[{table}]")

        # Row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        log(f"  Total rows: {count:,}")

        # Get column names
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]

        # Check for empty/null key fields
        if 'primary_country' in columns:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE primary_country IS NULL OR primary_country = ''")
            empty_country = cursor.fetchone()[0]
            log(f"  Empty primary_country: {empty_country:,} ({empty_country/count*100 if count > 0 else 0:.1f}%)")

        # Look for any partner country column (multiple naming conventions)
        partner_cols = [c for c in columns if 'partner' in c.lower() and 'country' in c.lower()]
        if partner_cols:
            col = partner_cols[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL OR {col} = ''")
            empty_partner = cursor.fetchone()[0]
            log(f"  Empty {col}: {empty_partner:,} ({empty_partner/count*100 if count > 0 else 0:.1f}%)")

        if 'is_china_collaboration' in columns:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE is_china_collaboration = 1")
            china_count = cursor.fetchone()[0]
            log(f"  China collaborations: {china_count:,} ({china_count/count*100 if count > 0 else 0:.1f}%)")

        # Netherlands specific
        if 'primary_country' in columns:
            # Build NL query dynamically based on available columns
            partner_cols = [c for c in columns if 'partner' in c.lower() and 'country' in c.lower()]
            if partner_cols:
                partner_col = partner_cols[0]
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table}
                    WHERE primary_country = 'NL' OR {partner_col} = 'NL'
                """)
                nl_count = cursor.fetchone()[0]
                log(f"  Netherlands involvement: {nl_count:,}")

                if 'is_china_collaboration' in columns:
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM {table}
                        WHERE (primary_country = 'NL' OR {partner_col} = 'NL')
                        AND is_china_collaboration = 1
                    """)
                    nl_china = cursor.fetchone()[0]
                    log(f"  NL-China collaborations: {nl_china:,}")
            else:
                # Just check primary_country
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE primary_country = 'NL'")
                nl_count = cursor.fetchone()[0]
                if nl_count > 0:
                    log(f"  Netherlands (primary only): {nl_count:,}")

        results[table] = {
            'total_rows': count,
            'columns': columns
        }

    return results

def validate_openalex(conn):
    """Validate OpenAlex dataset."""
    cursor = conn.cursor()

    log("\n" + "="*80)
    log("OPENALEX VALIDATION")
    log("="*80)

    # Get table schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%openalex%'")
    tables = [row[0] for row in cursor.fetchall()]
    log(f"\nOpenAlex tables: {tables}")

    results = {}

    for table in tables:
        log(f"\n[{table}]")

        # Row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        log(f"  Total rows: {count:,}")

        if count == 0:
            log(f"  WARNING: Table {table} is EMPTY")
            continue

        # Get column names
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        log(f"  Columns: {', '.join(columns[:10])}{'...' if len(columns) > 10 else ''}")

        # Check for country fields
        country_cols = [c for c in columns if 'country' in c.lower()]
        if country_cols:
            log(f"  Country columns found: {country_cols}")

            for col in country_cols:
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL OR {col} = ''")
                empty = cursor.fetchone()[0]
                log(f"    Empty {col}: {empty:,} ({empty/count*100:.1f}%)")

        # Check for Chinese involvement
        chinese_cols = [c for c in columns if 'china' in c.lower() or 'chinese' in c.lower()]
        if chinese_cols:
            log(f"  Chinese columns found: {chinese_cols}")
            for col in chinese_cols:
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} = 1 OR {col} = 'true'")
                china_count = cursor.fetchone()[0]
                log(f"    {col} = TRUE: {china_count:,} ({china_count/count*100:.1f}%)")

        # Netherlands check
        for col in country_cols:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} = 'NL' OR {col} LIKE '%Netherlands%'")
            nl_count = cursor.fetchone()[0]
            if nl_count > 0:
                log(f"  Netherlands in {col}: {nl_count:,}")

        # Sample a few records
        cursor.execute(f"SELECT * FROM {table} LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            log(f"  Sample record structure: {len(columns)} fields")

        results[table] = {
            'total_rows': count,
            'columns': columns,
            'country_columns': country_cols,
            'chinese_columns': chinese_cols
        }

    return results

def validate_arxiv(conn):
    """Validate ArXiv dataset."""
    cursor = conn.cursor()

    log("\n" + "="*80)
    log("ARXIV VALIDATION")
    log("="*80)

    # Get table schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%arxiv%'")
    tables = [row[0] for row in cursor.fetchall()]
    log(f"\nArXiv tables: {tables}")

    if not tables:
        log("  WARNING: No ArXiv tables found!")
        return {}

    results = {}

    for table in tables:
        log(f"\n[{table}]")

        # Row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        log(f"  Total rows: {count:,}")

        if count == 0:
            log(f"  WARNING: Table {table} is EMPTY")
            continue

        # Get column names
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        log(f"  Columns: {', '.join(columns[:10])}{'...' if len(columns) > 10 else ''}")

        # Check for author/affiliation fields
        author_cols = [c for c in columns if 'author' in c.lower() or 'affiliation' in c.lower()]
        if author_cols:
            log(f"  Author/affiliation columns: {author_cols}")

            for col in author_cols[:3]:  # Check first 3
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL OR {col} = ''")
                empty = cursor.fetchone()[0]
                log(f"    Empty {col}: {empty:,} ({empty/count*100:.1f}%)")

        # Check for Chinese involvement
        chinese_cols = [c for c in columns if 'china' in c.lower() or 'chinese' in c.lower()]
        if chinese_cols:
            log(f"  Chinese columns found: {chinese_cols}")
            for col in chinese_cols:
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} = 1")
                china_count = cursor.fetchone()[0]
                log(f"    {col} = 1: {china_count:,} ({china_count/count*100:.1f}%)")

        # Temporal coverage
        date_cols = [c for c in columns if 'date' in c.lower() or 'year' in c.lower()]
        if date_cols:
            date_col = date_cols[0]
            cursor.execute(f"SELECT MIN({date_col}), MAX({date_col}) FROM {table} WHERE {date_col} IS NOT NULL")
            min_date, max_date = cursor.fetchone()
            log(f"  Temporal range ({date_col}): {min_date} to {max_date}")

        results[table] = {
            'total_rows': count,
            'columns': columns,
            'author_columns': author_cols,
            'chinese_columns': chinese_cols
        }

    return results

def generate_summary(openaire_results, openalex_results, arxiv_results):
    """Generate summary report."""
    log("\n" + "="*80)
    log("VALIDATION SUMMARY")
    log("="*80)

    log("\n[DATA AVAILABILITY]")
    log(f"  OpenAIRE tables: {len(openaire_results)}")
    log(f"  OpenAlex tables: {len(openalex_results)}")
    log(f"  ArXiv tables: {len(arxiv_results)}")

    # Calculate total records
    total_openaire = sum(r.get('total_rows', 0) for r in openaire_results.values())
    total_openalex = sum(r.get('total_rows', 0) for r in openalex_results.values())
    total_arxiv = sum(r.get('total_rows', 0) for r in arxiv_results.values())

    log(f"\n[TOTAL RECORDS]")
    log(f"  OpenAIRE: {total_openaire:,}")
    log(f"  OpenAlex: {total_openalex:,}")
    log(f"  ArXiv: {total_arxiv:,}")

    log("\n[ISSUES FOUND]")
    issues = []

    # Check for empty tables
    for name, results in [('OpenAIRE', openaire_results), ('OpenAlex', openalex_results), ('ArXiv', arxiv_results)]:
        empty_tables = [t for t, r in results.items() if r.get('total_rows', 0) == 0]
        if empty_tables:
            issues.append(f"{name}: {len(empty_tables)} empty tables - {empty_tables}")

    if issues:
        for issue in issues:
            log(f"  - {issue}")
    else:
        log("  No critical issues found")

    log("\n[RECOMMENDATIONS]")

    if total_openalex == 0:
        log("  ⚠ OpenAlex: No data found - may need reprocessing similar to CORDIS")
    else:
        log("  ✓ OpenAlex: Data present, appears functional")

    if total_openaire == 0:
        log("  ⚠ OpenAIRE: No data found - check data ingestion")
    else:
        log("  ✓ OpenAIRE: Data present, appears functional")

    if total_arxiv == 0:
        log("  ⚠ ArXiv: Not integrated - may want to add")
    else:
        log("  ✓ ArXiv: Data present, appears functional")

def main():
    """Main validation function."""
    start_time = datetime.now()

    log("="*80)
    log("RESEARCH DATASETS VALIDATION - START")
    log("="*80)

    # Connect to database
    conn = sqlite3.connect(DB_PATH)

    # Validate each dataset
    openaire_results = validate_openaire(conn)
    openalex_results = validate_openalex(conn)
    arxiv_results = validate_arxiv(conn)

    # Generate summary
    generate_summary(openaire_results, openalex_results, arxiv_results)

    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'openaire': openaire_results,
        'openalex': openalex_results,
        'arxiv': arxiv_results
    }

    output_file = "analysis/research_datasets_validation.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    log(f"\nResults saved to: {output_file}")

    # Cleanup
    conn.close()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    log("\n" + "="*80)
    log("RESEARCH DATASETS VALIDATION - COMPLETE")
    log(f"Duration: {duration:.1f} seconds")
    log("="*80)

if __name__ == "__main__":
    main()
