#!/usr/bin/env python3
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


"""
Deploy European Institutions Schema to Database
Purpose: Load institutional intelligence tables into osint_master.db
"""

import sqlite3
import sys
from pathlib import Path

def deploy_schema(db_path: str, schema_path: str):
    """Deploy schema SQL file to database"""

    print("=" * 70)
    print("DEPLOYING EUROPEAN INSTITUTIONS SCHEMA")
    print("=" * 70)
    print()

    # Check files exist
    if not Path(schema_path).exists():
        print(f"✗ Schema file not found: {schema_path}")
        return False

    if not Path(db_path).parent.exists():
        print(f"✗ Database directory not found: {Path(db_path).parent}")
        return False

    try:
        # Read schema
        print(f"Reading schema: {schema_path}")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Connect to database
        print(f"Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute schema
        print("Executing schema statements...")
        cursor.executescript(schema_sql)
        conn.commit()

        # Verify tables created
        print("\nVerifying tables created...")
        cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type='table' AND name LIKE 'european_%' OR name LIKE 'institutional_%'
            ORDER BY name
        ''')

        tables = cursor.fetchall()
        if tables:
            print(f"\n✓ Successfully created {len(tables)} tables:")
            for table in tables:
                # Count records
                # SECURITY: Validate table name before use in SQL
                safe_table = validate_sql_identifier(table[0])
                cursor.execute(f"SELECT COUNT(*) FROM {safe_table}")
                count = cursor.fetchone()[0]
                print(f"  • {table[0]} ({count} records)")
        else:
            print("✗ No tables created - check schema file")
            return False

        # Verify views
        cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type='view' AND name LIKE 'v_%'
            ORDER BY name
        ''')
        views = cursor.fetchall()
        if views:
            print(f"\n✓ Successfully created {len(views)} views:")
            for view in views:
                print(f"  • {view[0]}")

        # Verify indexes
        cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type='index' AND name LIKE 'idx_%'
        ''')
        indexes = cursor.fetchall()
        if indexes:
            print(f"\n✓ Successfully created {len(indexes)} indexes:")
            print(f"  (Performance optimization enabled)")

        conn.close()

        print("\n" + "=" * 70)
        print("✓ SCHEMA DEPLOYMENT COMPLETE")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Run proof-of-concept collector:")
        print("     python scripts/collectors/institutional_collector_germany_poc.py")
        print()
        print("  2. Query the data:")
        print("     sqlite3 F:/OSINT_WAREHOUSE/osint_master.db")
        print("     SELECT * FROM v_china_focused_institutions;")
        print()

        return True

    except sqlite3.Error as e:
        print(f"\n✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main deployment function"""

    # Paths
    schema_path = "C:/Projects/OSINT-Foresight/schema/european_institutions_schema.sql"
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    # Deploy
    success = deploy_schema(db_path, schema_path)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
