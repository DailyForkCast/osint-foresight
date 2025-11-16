#!/usr/bin/env python3
"""
Update USPTO Database Schema - Add NULL Data Handling Columns
Adds data quality tracking fields to existing uspto_patents_chinese table
"""

import sqlite3
import sys
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

def update_schema():
    """Add new columns to uspto_patents_chinese table"""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return False

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check if table exists
    cur.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='uspto_patents_chinese'
    """)

    if not cur.fetchone():
        print("WARNING: uspto_patents_chinese table does not exist yet")
        print("It will be created when the processor runs")
        conn.close()
        return True

    # Check existing columns
    cur.execute("PRAGMA table_info(uspto_patents_chinese)")
    existing_columns = {row[1] for row in cur.fetchall()}

    print(f"\nExisting table has {len(existing_columns)} columns")

    # Add new columns if they don't exist
    new_columns = [
        ('data_quality_flag', 'TEXT'),
        ('fields_with_data_count', 'INTEGER')
    ]

    added_count = 0
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            print(f"  Adding column: {col_name} {col_type}")
            try:
                # SECURITY: Validate column name and type before use in SQL
                safe_col_name = validate_sql_identifier(col_name)
                safe_col_type = validate_sql_identifier(col_type)
                cur.execute(f"ALTER TABLE uspto_patents_chinese ADD COLUMN {safe_col_name} {safe_col_type}")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"    Error adding {col_name}: {e}")
        else:
            print(f"  Column already exists: {col_name}")

    # Add index for data_quality_flag
    print("\nAdding index on data_quality_flag...")
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS idx_uspto_data_quality ON uspto_patents_chinese(data_quality_flag)")
        print("  Index created successfully")
    except sqlite3.OperationalError as e:
        print(f"  Index creation error (may already exist): {e}")

    conn.commit()

    # Get record count
    cur.execute("SELECT COUNT(*) FROM uspto_patents_chinese")
    total_records = cur.fetchone()[0]

    print(f"\n[OK] Schema update complete!")
    print(f"  Total records in table: {total_records:,}")
    print(f"  New columns added: {added_count}")

    # Show note about reprocessing
    print("\n" + "="*80)
    print("NOTE: Existing records need to be REPROCESSED to populate quality flags.")
    print("")
    print("The USPTO processor has been updated to assess data quality, but existing")
    print("records were created before this feature. To populate data_quality_flag")
    print("and fields_with_data_count for existing records, you have two options:")
    print("")
    print("Option 1: Reprocess USPTO patent files with updated processor")
    print("  python scripts/process_uspto_patents_chinese_streaming.py")
    print("")
    print("Option 2: Create a backfill script (similar to TED backfill)")
    print("  This would assess existing records and update quality flags")
    print("="*80)

    conn.close()
    return True


if __name__ == '__main__':
    print("="*80)
    print("USPTO DATABASE SCHEMA UPDATE - NULL DATA HANDLING")
    print("="*80)

    if not update_schema():
        sys.exit(1)

    print("\n" + "="*80)
    print("[SUCCESS] Schema update complete!")
    print("")
    print("Next steps:")
    print("1. Reprocess USPTO data OR create backfill script")
    print("2. Run validation: python scripts/validate_data_quality.py")
    print("="*80)
