#!/usr/bin/env python3
"""
Compare two OSINT databases and show their contents
"""

import sqlite3
import os
import re

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

def get_db_info(db_path):
    """Get information about a database"""
    if not os.path.exists(db_path):
        return None

    info = {
        'path': db_path,
        'size': os.path.getsize(db_path),
        'tables': {},
        'total_rows': 0
    }

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            # SECURITY: Validate table name before use in SQL
            safe_table = validate_sql_identifier(table_name)
            cursor.execute(f"SELECT COUNT(*) FROM {safe_table}")
            row_count = cursor.fetchone()[0]

            # Get column info
            cursor.execute(f"PRAGMA table_info({safe_table})")
            columns = [col[1] for col in cursor.fetchall()]

            info['tables'][table_name] = {
                'rows': row_count,
                'columns': columns
            }
            info['total_rows'] += row_count

        conn.close()

    except Exception as e:
        print(f"Error reading {db_path}: {e}")

    return info

def main():
    db1_path = "F:/OSINT_DATA/osint_master.db"
    db2_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    print("="*70)
    print("DATABASE COMPARISON")
    print("="*70)

    # Get info for both databases
    db1_info = get_db_info(db1_path)
    db2_info = get_db_info(db2_path)

    # Database 1 (OSINT_DATA)
    print(f"\n[DB1] Database 1: {db1_path}")
    if db1_info:
        print(f"   Size: {db1_info['size']:,} bytes ({db1_info['size']//1024//1024} MB)")
        print(f"   Total rows: {db1_info['total_rows']:,}")
        print(f"   Tables: {len(db1_info['tables'])}")

        print("\n   Tables in OSINT_DATA:")
        for table, info in db1_info['tables'].items():
            print(f"   - {table}: {info['rows']:,} rows")
            if info['rows'] > 0:
                print(f"     Columns: {', '.join(info['columns'][:5])}")
                if len(info['columns']) > 5:
                    print(f"              ... and {len(info['columns'])-5} more columns")
    else:
        print("   [X] Database not found")

    # Database 2 (OSINT_WAREHOUSE)
    print(f"\n[DB2] Database 2: {db2_path}")
    if db2_info:
        print(f"   Size: {db2_info['size']:,} bytes ({db2_info['size']//1024//1024} MB)")
        print(f"   Total rows: {db2_info['total_rows']:,}")
        print(f"   Tables: {len(db2_info['tables'])}")

        print("\n   Tables in OSINT_WAREHOUSE:")
        for table, info in db2_info['tables'].items():
            print(f"   - {table}: {info['rows']:,} rows")
            if info['rows'] > 0:
                print(f"     Columns: {', '.join(info['columns'][:5])}")
                if len(info['columns']) > 5:
                    print(f"              ... and {len(info['columns'])-5} more columns")
    else:
        print("   [X] Database not found")

    # Compare tables
    if db1_info and db2_info:
        print("\n" + "="*70)
        print("TABLE COMPARISON")
        print("="*70)

        db1_tables = set(db1_info['tables'].keys())
        db2_tables = set(db2_info['tables'].keys())

        only_in_db1 = db1_tables - db2_tables
        only_in_db2 = db2_tables - db1_tables
        common_tables = db1_tables & db2_tables

        if only_in_db1:
            print("\n[+] Tables only in OSINT_DATA (to be migrated):")
            for table in only_in_db1:
                print(f"   - {table} ({db1_info['tables'][table]['rows']:,} rows)")

        if only_in_db2:
            print("\n[*] Tables only in OSINT_WAREHOUSE (existing):")
            for table in only_in_db2:
                print(f"   - {table} ({db2_info['tables'][table]['rows']:,} rows)")

        if common_tables:
            print("\n[=] Tables in both databases:")
            for table in common_tables:
                db1_rows = db1_info['tables'][table]['rows']
                db2_rows = db2_info['tables'][table]['rows']
                print(f"   - {table}:")
                print(f"     OSINT_DATA: {db1_rows:,} rows")
                print(f"     OSINT_WAREHOUSE: {db2_rows:,} rows")
                if db1_rows > 0 and db2_rows == 0:
                    print(f"     -> Will migrate {db1_rows:,} rows")
                elif db1_rows > db2_rows:
                    print(f"     -> Will add {db1_rows - db2_rows:,} new rows")

if __name__ == "__main__":
    main()
