#!/usr/bin/env python3
"""
OSINT Foresight Data Audit - Phase 3: Data Quality Assessment
Automated structural profiling and deterministic quality checks
"""

import sqlite3
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

output_dir = Path("C:/Projects/OSINT - Foresight/audit_outputs")
output_dir.mkdir(exist_ok=True)

print("="*80)
print("PHASE 3: DATA QUALITY ASSESSMENT")
print("="*80)
print()

# Primary database to assess
db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

# ============================================================================
# Task 1: Structural Profiling - Top Tables
# ============================================================================

print("TASK 1: STRUCTURAL PROFILING")
print("-" * 40)

conn = sqlite3.connect(db_path, timeout=30)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

print(f"\nTotal tables: {len(tables)}")

# Profile top 20 tables by row count
table_profiles = []

for table_name in tables:
    if table_name.startswith('sqlite_'):
        continue

    try:
        # Row count
        cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
        row_count = cursor.fetchone()[0]

        if row_count == 0:
            continue  # Skip empty tables

        # Column info
        cursor.execute(f"PRAGMA table_info([{table_name}])")
        columns = cursor.fetchall()

        table_profiles.append({
            'table': table_name,
            'rows': row_count,
            'columns': len(columns),
            'column_details': [{'name': col[1], 'type': col[2], 'notnull': col[3]} for col in columns]
        })

    except Exception as e:
        print(f"  Error profiling {table_name}: {str(e)}")
        continue

# Sort by row count
table_profiles.sort(key=lambda x: x['rows'], reverse=True)

print("\nTop 20 tables by row count:")
for i, profile in enumerate(table_profiles[:20], 1):
    print(f"  {i}. {profile['table']}: {profile['rows']:,} rows, {profile['columns']} columns")

# Save profiles
with open(output_dir / "table_profiles_phase3.json", "w") as f:
    json.dump(table_profiles, f, indent=2)

print(f"\n[SAVED] table_profiles_phase3.json")

# ============================================================================
# Task 2: Duplicate Detection - Key Tables
# ============================================================================

print("\n" + "="*80)
print("TASK 2: DUPLICATE DETECTION")
print("-" * 40)

duplicate_results = {}

# Tables to check for duplicates with their primary key columns
key_tables = {
    'usaspending_china_374': ['transaction_id'],
    'ted_contracts_production': ['notice_id'],
    'openalex_works': ['work_id'],
    'uspto_patents_chinese': ['patent_number'],
    'arxiv_papers': ['arxiv_id'],
    'gleif_entities': ['lei']
}

for table, key_cols in key_tables.items():
    if table not in [p['table'] for p in table_profiles]:
        continue

    print(f"\n{table}:")

    try:
        # Check for duplicates
        key_cols_str = ', '.join(key_cols)
        cursor.execute(f"""
            SELECT {key_cols_str}, COUNT(*) as cnt
            FROM [{table}]
            GROUP BY {key_cols_str}
            HAVING cnt > 1
            LIMIT 100
        """)

        duplicates = cursor.fetchall()

        duplicate_results[table] = {
            'key_columns': key_cols,
            'duplicate_count': len(duplicates),
            'examples': [{'key': dup[0], 'count': dup[1]} for dup in duplicates[:10]]
        }

        if duplicates:
            print(f"  DUPLICATES FOUND: {len(duplicates)} duplicate keys")
            print(f"  Examples:")
            for dup in duplicates[:5]:
                print(f"    {dup[0]}: {dup[1]} occurrences")
        else:
            print(f"  OK: No duplicates found")

    except Exception as e:
        print(f"  Error: {str(e)}")
        duplicate_results[table] = {'error': str(e)}

# Save duplicate results
with open(output_dir / "duplicate_detection_results.json", "w") as f:
    json.dump(duplicate_results, f, indent=2)

print(f"\n[SAVED] duplicate_detection_results.json")

# ============================================================================
# Task 3: Missing Data Analysis
# ============================================================================

print("\n" + "="*80)
print("TASK 3: MISSING DATA ANALYSIS")
print("-" * 40)

missing_data_analysis = {}

# Sample key tables and columns
sample_tables = [
    ('usaspending_china_374', ['recipient_name', 'recipient_country', 'award_description', 'action_date']),
    ('ted_contracts_production', ['contractor_name', 'contract_value', 'publication_date']),
    ('openalex_works', ['title', 'publication_year', 'doi', 'abstract']),
    ('uspto_patents_chinese', ['patent_number', 'assignee_name', 'filing_date', 'grant_date']),
]

for table, columns in sample_tables:
    if table not in [p['table'] for p in table_profiles]:
        continue

    print(f"\n{table}:")

    try:
        cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
        total_rows = cursor.fetchone()[0]

        if total_rows == 0:
            continue

        table_analysis = {
            'total_rows': total_rows,
            'columns': {}
        }

        for col in columns:
            # Check for NULL, empty string, or common NULL representations
            cursor.execute(f"""
                SELECT COUNT(*) FROM [{table}]
                WHERE [{col}] IS NULL
                   OR [{col}] = ''
                   OR [{col}] = '\\N'
                   OR [{col}] = 'NULL'
            """)

            null_count = cursor.fetchone()[0]
            null_rate = (null_count / total_rows) * 100

            table_analysis['columns'][col] = {
                'null_count': null_count,
                'null_rate': round(null_rate, 2),
                'populated_count': total_rows - null_count
            }

            print(f"  {col}: {null_rate:.1f}% NULL ({null_count:,}/{total_rows:,})")

        missing_data_analysis[table] = table_analysis

    except Exception as e:
        print(f"  Error: {str(e)}")

# Save missing data analysis
with open(output_dir / "missing_data_analysis.json", "w") as f:
    json.dump(missing_data_analysis, f, indent=2)

print(f"\n[SAVED] missing_data_analysis.json")

# ============================================================================
# Task 4: Temporal Consistency
# ============================================================================

print("\n" + "="*80)
print("TASK 4: TEMPORAL CONSISTENCY")
print("-" * 40)

temporal_checks = {}

# Check date ranges for key tables
date_tables = [
    ('usaspending_china_374', 'action_date'),
    ('ted_contracts_production', 'publication_date'),
    ('openalex_works', 'publication_date'),
    ('uspto_patents_chinese', 'grant_date'),
    ('arxiv_papers', 'published_date')
]

for table, date_col in date_tables:
    if table not in [p['table'] for p in table_profiles]:
        continue

    print(f"\n{table}.{date_col}:")

    try:
        # Get min/max dates
        cursor.execute(f"""
            SELECT
                MIN([{date_col}]) as min_date,
                MAX([{date_col}]) as max_date,
                COUNT(DISTINCT [{date_col}]) as unique_dates,
                COUNT(*) as total_rows
            FROM [{table}]
            WHERE [{date_col}] IS NOT NULL
            AND [{date_col}] != ''
            AND [{date_col}] != '\\N'
        """)

        result = cursor.fetchone()

        if result and result[0]:
            temporal_checks[f"{table}.{date_col}"] = {
                'min_date': result[0],
                'max_date': result[1],
                'unique_dates': result[2],
                'total_rows': result[3]
            }

            print(f"  Range: {result[0]} to {result[1]}")
            print(f"  Unique dates: {result[2]:,}")
            print(f"  Total rows with dates: {result[3]:,}")

            # Check for future dates
            cursor.execute(f"""
                SELECT COUNT(*) FROM [{table}]
                WHERE [{date_col}] > date('now')
            """)
            future_count = cursor.fetchone()[0]

            if future_count > 0:
                print(f"  WARNING: {future_count} future dates found")
                temporal_checks[f"{table}.{date_col}"]['future_dates'] = future_count

    except Exception as e:
        print(f"  Error: {str(e)}")

# Save temporal checks
with open(output_dir / "temporal_consistency_results.json", "w") as f:
    json.dump(temporal_checks, f, indent=2)

print(f"\n[SAVED] temporal_consistency_results.json")

# ============================================================================
# Task 5: Geographic Consistency
# ============================================================================

print("\n" + "="*80)
print("TASK 5: GEOGRAPHIC CONSISTENCY")
print("-" * 40)

geographic_checks = {}

# Check country codes
country_tables = [
    ('usaspending_china_374', 'recipient_country'),
    ('ted_contracts_production', 'country_code'),
    ('openalex_work_authors', 'country_code'),
]

for table, country_col in country_tables:
    if table not in [p['table'] for p in table_profiles]:
        continue

    print(f"\n{table}.{country_col}:")

    try:
        # Get distinct country codes
        cursor.execute(f"""
            SELECT [{country_col}], COUNT(*) as cnt
            FROM [{table}]
            WHERE [{country_col}] IS NOT NULL
            AND [{country_col}] != ''
            GROUP BY [{country_col}]
            ORDER BY cnt DESC
            LIMIT 20
        """)

        countries = cursor.fetchall()

        # Check for invalid codes (not 2-letter)
        cursor.execute(f"""
            SELECT COUNT(*) FROM [{table}]
            WHERE [{country_col}] IS NOT NULL
            AND [{country_col}] != ''
            AND LENGTH([{country_col}]) != 2
        """)

        invalid_count = cursor.fetchone()[0]

        geographic_checks[f"{table}.{country_col}"] = {
            'unique_countries': len(countries),
            'top_10': [{'code': c[0], 'count': c[1]} for c in countries[:10]],
            'invalid_code_count': invalid_count
        }

        print(f"  Unique country codes: {len(countries)}")
        print(f"  Top 5:")
        for c in countries[:5]:
            print(f"    {c[0]}: {c[1]:,} rows")

        if invalid_count > 0:
            print(f"  WARNING: {invalid_count} invalid country codes (not 2-letter)")

    except Exception as e:
        print(f"  Error: {str(e)}")

# Save geographic checks
with open(output_dir / "geographic_consistency_results.json", "w") as f:
    json.dump(geographic_checks, f, indent=2)

print(f"\n[SAVED] geographic_consistency_results.json")

# ============================================================================
# Summary Statistics
# ============================================================================

print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

summary = {
    'audit_date': datetime.now().isoformat(),
    'database': db_path,
    'total_tables': len(table_profiles),
    'total_rows': sum(p['rows'] for p in table_profiles),
    'duplicate_issues': sum(1 for v in duplicate_results.values() if isinstance(v, dict) and v.get('duplicate_count', 0) > 0),
    'high_null_rate_columns': 0,  # >50% NULL
    'temporal_issues': sum(1 for v in temporal_checks.values() if v.get('future_dates', 0) > 0),
    'geographic_issues': sum(1 for v in geographic_checks.values() if v.get('invalid_code_count', 0) > 0)
}

# Count high NULL rate columns
for table_data in missing_data_analysis.values():
    for col_data in table_data.get('columns', {}).values():
        if col_data.get('null_rate', 0) > 50:
            summary['high_null_rate_columns'] += 1

print(f"\nTables analyzed: {summary['total_tables']}")
print(f"Total rows: {summary['total_rows']:,}")
print(f"\nQuality Issues Found:")
print(f"  Duplicate issues: {summary['duplicate_issues']}")
print(f"  High NULL rate columns (>50%): {summary['high_null_rate_columns']}")
print(f"  Temporal issues (future dates): {summary['temporal_issues']}")
print(f"  Geographic issues (invalid codes): {summary['geographic_issues']}")

# Save summary
with open(output_dir / "phase3_quality_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"\n[SAVED] phase3_quality_summary.json")

conn.close()

print("\n" + "="*80)
print("PHASE 3 TASK 1-5 COMPLETE")
print("="*80)
print(f"\nOutput files saved to: {output_dir}")
print()
