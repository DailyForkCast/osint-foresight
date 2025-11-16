#!/usr/bin/env python3
"""
Safe deployment of European Institutions Schema
Handles WAL files and database locks properly
"""

import sqlite3
import sys
import time
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

def deploy_schema_safe(db_path: str, schema_path: str):
    """Deploy schema with proper WAL handling"""

    print("=" * 70)
    print("DEPLOYING EUROPEAN INSTITUTIONS SCHEMA (SAFE MODE)")
    print("=" * 70)
    print()

    # Check files exist
    if not Path(schema_path).exists():
        print(f"X Schema file not found: {schema_path}")
        return False

    if not Path(db_path).parent.exists():
        print(f"X Database directory not found: {Path(db_path).parent}")
        return False

    try:
        # Read schema
        print(f"Reading schema: {schema_path}")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Connect to database with timeout
        print(f"Connecting to database: {db_path}")
        print("(Setting timeout to 30 seconds...)")

        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()

        # Checkpoint WAL first
        print("Checkpointing WAL files...")
        try:
            cursor.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            conn.commit()
            print("  -> WAL checkpoint complete")
        except Exception as e:
            print(f"  -> WAL checkpoint warning: {e}")

        # Execute schema in smaller chunks
        print("\nExecuting schema statements...")

        # Split schema into individual statements
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]

        success_count = 0
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    cursor.execute(statement + ';')
                    success_count += 1
                    if i % 10 == 0:
                        print(f"  -> Executed {i}/{len(statements)} statements...")
                except sqlite3.OperationalError as e:
                    if 'already exists' in str(e).lower():
                        # Table/view/index already exists - that's OK
                        success_count += 1
                    else:
                        print(f"  -> Error on statement {i}: {e}")

        conn.commit()
        print(f"  -> Successfully executed {success_count}/{len(statements)} statements")

        # Verify tables created
        print("\nVerifying tables created...")
        cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type='table' AND (name LIKE 'european_%' OR name LIKE 'institutional_%')
            ORDER BY name
        ''')

        tables = cursor.fetchall()
        if tables:
            print(f"\n+ Successfully created/verified {len(tables)} tables:")
            for table in tables:
                # Count records
                # SECURITY: Validate table name before use in SQL
                safe_table = validate_sql_identifier(table[0])
                cursor.execute(f"SELECT COUNT(*) FROM {safe_table}")
                count = cursor.fetchone()[0]
                print(f"  - {table[0]} ({count} records)")
        else:
            print("X No tables created - check schema file")
            conn.close()
            return False

        # Verify views
        cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type='view' AND name LIKE 'v_%'
            ORDER BY name
        ''')
        views = cursor.fetchall()
        if views:
            print(f"\n+ Successfully created/verified {len(views)} views:")
            for view in views:
                print(f"  - {view[0]}")

        # Verify indexes
        cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type='index' AND name LIKE 'idx_%'
        ''')
        indexes = cursor.fetchall()
        if indexes:
            print(f"\n+ Successfully created/verified {len(indexes)} indexes")
            print(f"  (Performance optimization enabled)")

        conn.close()

        print("\n" + "=" * 70)
        print("+ SCHEMA DEPLOYMENT COMPLETE")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Run proof-of-concept collector:")
        print("     python scripts/collectors/institutional_collector_germany_poc.py")
        print()

        return True

    except sqlite3.Error as e:
        print(f"\nX Database error: {e}")
        return False
    except Exception as e:
        print(f"\nX Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main deployment function"""

    # Paths
    schema_path = "C:/Projects/OSINT-Foresight/schema/european_institutions_schema.sql"
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    # Deploy
    success = deploy_schema_safe(db_path, schema_path)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
