#!/usr/bin/env python3
"""
Quick deployment - skip WAL checkpoint, just deploy schema
"""

import sqlite3
import sys
from pathlib import Path
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

def deploy_quick(db_path: str, schema_path: str):
    """Quick deployment without WAL operations"""

    print("=" * 70)
    print("DEPLOYING EUROPEAN INSTITUTIONS SCHEMA (QUICK MODE)")
    print("=" * 70)
    print()

    # Read schema
    print(f"Reading schema: {schema_path}")
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Connect with long timeout
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path, timeout=60.0)
    cursor = conn.cursor()

    # Execute schema - ignore "already exists" errors
    print("Executing schema statements...")

    statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
    success = 0
    exists = 0
    errors = 0

    for statement in statements:
        if statement:
            try:
                cursor.execute(statement + ';')
                success += 1
            except sqlite3.OperationalError as e:
                if 'already exists' in str(e).lower():
                    exists += 1
                else:
                    errors += 1
                    print(f"  ! Error: {e}")

    conn.commit()

    print(f"\n  -> New: {success}, Already exists: {exists}, Errors: {errors}")

    # Verify tables
    print("\nVerifying tables...")
    cursor.execute('''
        SELECT name FROM sqlite_master
        WHERE type='table' AND (name LIKE 'european_%' OR name LIKE 'institutional_%')
        ORDER BY name
    ''')

    tables = cursor.fetchall()
    print(f"  -> Found {len(tables)} institutional tables")

    for table in tables:
        # SECURITY: Validate table name before use in SQL
        safe_table = validate_sql_identifier(table[0])
        cursor.execute(f"SELECT COUNT(*) FROM {safe_table}")
        count = cursor.fetchone()[0]
        print(f"     - {table[0]}: {count} records")

    conn.close()

    print("\n" + "=" * 70)
    print("DEPLOYMENT COMPLETE")
    print("=" * 70)

    return True


if __name__ == '__main__':
    schema_path = "C:/Projects/OSINT-Foresight/schema/european_institutions_schema.sql"
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    try:
        deploy_quick(db_path, schema_path)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
