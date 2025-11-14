#!/usr/bin/env python3
import sqlite3
import re
from pathlib import Path

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

def check_cordis_schema():
    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
    if not db_path.exists():
        print("Database not found")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check what CORDIS tables exist
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%cordis%'")
    cordis_tables = cur.fetchall()

    print("CORDIS Tables found:")
    for table in cordis_tables:
        print(f"- {table[0]}")

    # Check schema for each table
    for table in cordis_tables:
        table_name = table[0]
        # SECURITY: Validate table name before use in SQL
        safe_table = validate_sql_identifier(table_name)
        print(f"\nSchema for {table_name}:")
        cur.execute(f"PRAGMA table_info({safe_table})")
        columns = cur.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

        # Show sample data
        cur.execute(f"SELECT * FROM {safe_table} LIMIT 3")
        samples = cur.fetchall()
        print(f"\nSample data from {table_name}:")
        for row in samples:
            print(f"  {row}")

    conn.close()

if __name__ == "__main__":
    check_cordis_schema()
