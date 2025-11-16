#!/usr/bin/env python3
"""
Update TED Database Schema - Add NULL Data Handling Columns
Adds data quality tracking fields to existing ted_contracts_production table
"""

import sqlite3
import sys
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from core.data_quality_assessor import DataQualityAssessor

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
    """Add new columns to ted_contracts_production table"""

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
        WHERE type='table' AND name='ted_contracts_production'
    """)

    if not cur.fetchone():
        print("WARNING: ted_contracts_production table does not exist yet")
        print("It will be created when the processor runs")
        conn.close()
        return True

    # Check existing columns
    cur.execute("PRAGMA table_info(ted_contracts_production)")
    existing_columns = {row[1] for row in cur.fetchall()}

    print(f"\nExisting table has {len(existing_columns)} columns")

    # Add new columns if they don't exist
    new_columns = [
        ('data_quality_flag', 'TEXT'),
        ('fields_with_data_count', 'INTEGER'),
        ('negative_signals', 'TEXT'),
        ('positive_signals', 'TEXT'),
        ('detection_rationale', 'TEXT')
    ]

    added_count = 0
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            print(f"  Adding column: {col_name} {col_type}")
            try:
                # SECURITY: Validate column name and type before use in SQL
                safe_col_name = validate_sql_identifier(col_name)
                safe_col_type = validate_sql_identifier(col_type)
                cur.execute(f"ALTER TABLE ted_contracts_production ADD COLUMN {safe_col_name} {safe_col_type}")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"    Error adding {col_name}: {e}")
        else:
            print(f"  Column already exists: {col_name}")

    # Add index for data_quality_flag
    print("\nAdding index on data_quality_flag...")
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ted_prod_data_quality ON ted_contracts_production(data_quality_flag)")
        print("  Index created successfully")
    except sqlite3.OperationalError as e:
        print(f"  Index creation error (may already exist): {e}")

    conn.commit()

    # Get record count
    cur.execute("SELECT COUNT(*) FROM ted_contracts_production")
    total_records = cur.fetchone()[0]

    print(f"\n[OK] Schema update complete!")
    print(f"  Total records in table: {total_records:,}")
    print(f"  New columns added: {added_count}")

    conn.close()
    return True


def backfill_data_quality():
    """Backfill data quality flags for existing records"""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return False

    print(f"\n{'='*80}")
    print("BACKFILLING DATA QUALITY FLAGS")
    print('='*80)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check if table exists
    cur.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='ted_contracts_production'
    """)

    if not cur.fetchone():
        print("No existing data to backfill")
        conn.close()
        return True

    # Initialize assessor
    assessor = DataQualityAssessor()

    # Get records without data quality flags
    cur.execute("""
        SELECT id, contractor_country, contractor_name, contractor_address
        FROM ted_contracts_production
        WHERE data_quality_flag IS NULL
        LIMIT 10000
    """)

    records = cur.fetchall()
    total_to_process = len(records)

    if total_to_process == 0:
        print("No records need backfilling")
        conn.close()
        return True

    print(f"Processing {total_to_process:,} records...")

    processed = 0
    for record in records:
        record_id, country, name, address = record

        # Assess data quality (using only available fields)
        quality_record = {
            'country': country,
            'city': None,  # Not available in this table version
            'name': name,
            'address': address
        }

        key_fields = ['contractor_country', 'contractor_name', 'contractor_address']

        assessment = assessor.assess(quality_record, key_fields)

        # Update record
        cur.execute("""
            UPDATE ted_contracts_production
            SET data_quality_flag = ?,
                fields_with_data_count = ?,
                negative_signals = ?,
                positive_signals = ?,
                detection_rationale = ?
            WHERE id = ?
        """, (
            assessment.data_quality_flag,
            assessment.fields_with_data_count,
            str(assessment.negative_signals),
            str(assessment.positive_signals),
            assessment.rationale,
            record_id
        ))

        processed += 1
        if processed % 1000 == 0:
            conn.commit()
            print(f"  Processed {processed:,} / {total_to_process:,} records...")

    conn.commit()

    print(f"\n[OK] Backfill complete! Processed {processed:,} records")

    # Show distribution
    print("\nData Quality Distribution:")
    cur.execute("""
        SELECT data_quality_flag, COUNT(*) as count
        FROM ted_contracts_production
        WHERE data_quality_flag IS NOT NULL
        GROUP BY data_quality_flag
        ORDER BY count DESC
    """)

    for flag, count in cur.fetchall():
        percentage = (count / total_to_process) * 100
        print(f"  {flag}: {count:,} ({percentage:.1f}%)")

    conn.close()
    return True


if __name__ == '__main__':
    print("="*80)
    print("TED DATABASE SCHEMA UPDATE - NULL DATA HANDLING")
    print("="*80)

    # Step 1: Update schema
    if not update_schema():
        sys.exit(1)

    # Step 2: Check if auto-backfill is requested
    auto_backfill = '--auto' in sys.argv or '--backfill' in sys.argv

    if auto_backfill:
        print("\n" + "="*80)
        print("Auto-backfill mode enabled")
        if not backfill_data_quality():
            sys.exit(1)
    else:
        # Interactive mode
        print("\n" + "="*80)
        response = input("Do you want to backfill existing records? (y/n): ").strip().lower()

        if response == 'y':
            if not backfill_data_quality():
                sys.exit(1)
        else:
            print("Skipping backfill. Run this script again to backfill later.")

    print("\n" + "="*80)
    print("[SUCCESS] ALL DONE!")
    print("="*80)
