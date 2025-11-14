#!/usr/bin/env python3
"""
Analyze overlap between multiple SQLite databases and osint_master.db
Identify redundant databases for archival/deletion
"""

import sqlite3
import os
import re
from pathlib import Path
import json
from datetime import datetime

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from dynamic SQL construction.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    # Check for valid characters only (alphanumeric + underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    # Check length (SQLite limit is 1024, we use 100 for safety)
    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    # Blacklist dangerous SQL keywords
    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier

def get_database_info(db_path):
    """Get comprehensive info about a database"""
    info = {
        'path': str(db_path),
        'size_mb': db_path.stat().st_size / (1024 * 1024) if db_path.exists() else 0,
        'tables': {},
        'total_rows': 0,
        'error': None
    }

    if not db_path.exists():
        info['error'] = 'File does not exist'
        return info

    if info['size_mb'] == 0:
        info['error'] = 'Empty file (0 bytes)'
        return info

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()

        for table_name in tables:
            table_name = table_name[0]
            # SECURITY: Validate table name before use in SQL
            safe_table = validate_sql_identifier(table_name)

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {safe_table}")
            row_count = cursor.fetchone()[0]

            # Get sample data for comparison
            cursor.execute(f"SELECT * FROM {safe_table} LIMIT 5")
            sample_rows = cursor.fetchall()

            # Get column names
            cursor.execute(f"PRAGMA table_info({safe_table})")
            columns = [col[1] for col in cursor.fetchall()]

            info['tables'][table_name] = {
                'row_count': row_count,
                'columns': columns,
                'sample_data': sample_rows
            }
            info['total_rows'] += row_count

        conn.close()
    except Exception as e:
        info['error'] = str(e)

    return info

def analyze_overlap(master_info, other_info):
    """Analyze overlap between master and another database"""
    overlap = {
        'identical_tables': [],
        'similar_tables': [],
        'unique_tables': [],
        'data_overlap_percentage': 0,
        'recommendation': ''
    }

    if other_info.get('error'):
        overlap['recommendation'] = f"DELETE - {other_info['error']}"
        return overlap

    master_tables = set(master_info['tables'].keys())
    other_tables = set(other_info['tables'].keys())

    # Check for identical tables
    for table in other_tables:
        if table in master_tables:
            # Check if structure is identical
            if master_info['tables'][table]['columns'] == other_info['tables'][table]['columns']:
                overlap['identical_tables'].append(table)
            else:
                overlap['similar_tables'].append(table)
        else:
            overlap['unique_tables'].append(table)

    # Calculate overlap percentage
    if other_tables:
        overlap_count = len(overlap['identical_tables']) + len(overlap['similar_tables'])
        overlap['data_overlap_percentage'] = (overlap_count / len(other_tables)) * 100

    # Make recommendation
    if overlap['data_overlap_percentage'] >= 80:
        overlap['recommendation'] = 'ARCHIVE - High overlap with master'
    elif overlap['data_overlap_percentage'] >= 50:
        overlap['recommendation'] = 'REVIEW - Moderate overlap, check for unique data'
    elif other_info['total_rows'] == 0:
        overlap['recommendation'] = 'DELETE - Empty database'
    elif other_info['size_mb'] < 0.1:
        overlap['recommendation'] = 'DELETE - Trivial size'
    else:
        overlap['recommendation'] = 'KEEP - Contains unique data'

    return overlap

def main():
    warehouse_dir = Path("F:/OSINT_WAREHOUSE")
    master_db = warehouse_dir / "osint_master.db"

    # Get master database info
    print("Analyzing osint_master.db...")
    master_info = get_database_info(master_db)
    print(f"Master DB: {master_info['size_mb']:.2f} MB, {len(master_info['tables'])} tables, {master_info['total_rows']:,} rows\n")

    # Analyze all other databases
    results = {}
    all_dbs = list(warehouse_dir.glob("*.db"))

    for db_path in all_dbs:
        if db_path == master_db or 'backup' in db_path.name:
            continue

        print(f"Analyzing {db_path.name}...")
        db_info = get_database_info(db_path)
        overlap = analyze_overlap(master_info, db_info)

        results[db_path.name] = {
            'size_mb': db_info['size_mb'],
            'tables': len(db_info['tables']),
            'rows': db_info['total_rows'],
            'error': db_info.get('error'),
            'overlap': overlap['data_overlap_percentage'],
            'unique_tables': overlap['unique_tables'],
            'recommendation': overlap['recommendation']
        }

    # Summary report
    print("\n" + "="*80)
    print("DATABASE CONSOLIDATION ANALYSIS REPORT")
    print("="*80)

    # Group by recommendation
    to_delete = []
    to_archive = []
    to_review = []
    to_keep = []

    for db_name, info in results.items():
        if 'DELETE' in info['recommendation']:
            to_delete.append(db_name)
        elif 'ARCHIVE' in info['recommendation']:
            to_archive.append(db_name)
        elif 'REVIEW' in info['recommendation']:
            to_review.append(db_name)
        elif 'KEEP' in info['recommendation']:
            to_keep.append(db_name)

        print(f"\n{db_name}:")
        print(f"  Size: {info['size_mb']:.2f} MB")
        print(f"  Tables: {info['tables']}")
        print(f"  Rows: {info['rows']:,}")
        if info['error']:
            print(f"  Error: {info['error']}")
        print(f"  Overlap: {info['overlap']:.1f}%")
        if info['unique_tables']:
            print(f"  Unique tables: {', '.join(info['unique_tables'][:5])}")
        print(f"  --> {info['recommendation']}")

    # Summary
    print("\n" + "="*80)
    print("RECOMMENDATIONS SUMMARY")
    print("="*80)
    print(f"\nTO DELETE ({len(to_delete)} databases):")
    for db in to_delete:
        print(f"  - {db}")

    print(f"\nTO ARCHIVE ({len(to_archive)} databases):")
    for db in to_archive:
        print(f"  - {db}")

    print(f"\nTO REVIEW ({len(to_review)} databases):")
    for db in to_review:
        print(f"  - {db}")

    print(f"\nTO KEEP ({len(to_keep)} databases):")
    for db in to_keep:
        print(f"  - {db}")

    # Save results to JSON
    results_file = Path("C:/Projects/OSINT - Foresight/data/metadata/database_consolidation_analysis.json")
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'master_db': {
                'size_mb': master_info['size_mb'],
                'tables': len(master_info['tables']),
                'rows': master_info['total_rows']
            },
            'databases': results,
            'recommendations': {
                'delete': to_delete,
                'archive': to_archive,
                'review': to_review,
                'keep': to_keep
            }
        }, f, indent=2)

    print(f"\nAnalysis saved to: {results_file}")

    return results

if __name__ == "__main__":
    results = main()