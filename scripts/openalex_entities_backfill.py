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
OpenAlex Entities Backfill - Add NULL Data Handling
Assess data quality for existing OpenAlex entities
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from core.data_quality_assessor import DataQualityAssessor

def update_schema():
    """Add data quality columns to openalex_entities table"""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

    print("="*80)
    print("OPENALEX ENTITIES SCHEMA UPDATE - NULL DATA HANDLING")
    print("="*80)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check existing columns
    cur.execute("PRAGMA table_info(openalex_entities)")
    existing_columns = {row[1] for row in cur.fetchall()}

    print(f"\nExisting table has {len(existing_columns)} columns")

    # Add new columns
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
            # SECURITY: Validate column name and type before use in SQL
            safe_col_name = validate_sql_identifier(col_name)
            safe_col_type = validate_sql_identifier(col_type)
            cur.execute(f"ALTER TABLE openalex_entities ADD COLUMN {safe_col_name} {safe_col_type}")
            added_count += 1
        else:
            print(f"  Column already exists: {col_name}")

    # Add index
    print("\nAdding index on data_quality_flag...")
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS idx_openalex_entities_quality ON openalex_entities(data_quality_flag)")
        print("  Index created successfully")
    except sqlite3.OperationalError as e:
        print(f"  Index creation error: {e}")

    conn.commit()

    # Get record count
    cur.execute("SELECT COUNT(*) FROM openalex_entities")
    total_records = cur.fetchone()[0]

    print(f"\n[OK] Schema update complete!")
    print(f"  Total records: {total_records:,}")
    print(f"  New columns added: {added_count}")

    conn.close()
    return True


def backfill_entities():
    """Backfill data quality for OpenAlex entities"""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

    print("\n" + "="*80)
    print("OPENALEX ENTITIES BACKFILL")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get total
    cur.execute("SELECT COUNT(*) FROM openalex_entities")
    total_records = cur.fetchone()[0]

    # Get unprocessed
    cur.execute("""
        SELECT COUNT(*) FROM openalex_entities
        WHERE data_quality_flag IS NULL
    """)
    remaining = cur.fetchone()[0]

    print(f"\nTotal records: {total_records:,}")
    print(f"To process: {remaining:,}\n")

    if remaining == 0:
        print("All records already processed!")
        conn.close()
        return True

    # Initialize assessor with enhanced detection
    assessor = DataQualityAssessor()

    # Get all unprocessed records
    cur.execute("""
        SELECT entity_id, country_code, city, region, name
        FROM openalex_entities
        WHERE data_quality_flag IS NULL
    """)

    records = cur.fetchall()
    start_time = datetime.now()

    print(f"Processing {len(records):,} records...")

    processed = 0
    for record in records:
        entity_id, country_code, city, region, name = record

        # Assess data quality
        # Use region as potential province indicator
        quality_record = {
            'country': country_code,
            'city': f"{city}, {region}" if city and region else (city or region or ""),
            'name': name,
            'address': None
        }

        key_fields = ['country_code', 'city', 'region', 'name']
        assessment = assessor.assess(quality_record, key_fields)

        # Update record
        cur.execute("""
            UPDATE openalex_entities
            SET data_quality_flag = ?,
                fields_with_data_count = ?,
                negative_signals = ?,
                positive_signals = ?,
                detection_rationale = ?
            WHERE entity_id = ?
        """, (
            assessment.data_quality_flag,
            assessment.fields_with_data_count,
            str(assessment.negative_signals),
            str(assessment.positive_signals),
            assessment.rationale,
            entity_id
        ))

        processed += 1

        if processed % 1000 == 0:
            conn.commit()
            print(f"  Processed {processed:,} / {len(records):,} records...")

    conn.commit()

    elapsed = (datetime.now() - start_time).total_seconds()
    rate = processed / elapsed if elapsed > 0 else 0

    print(f"\n[OK] Backfill complete!")
    print(f"  Processed: {processed:,} records in {elapsed:.1f}s ({rate:.0f} rec/sec)")

    # Show distribution
    print("\n" + "="*80)
    print("DATA QUALITY DISTRIBUTION:")
    print("="*80)

    cur.execute("""
        SELECT data_quality_flag, COUNT(*) as count
        FROM openalex_entities
        WHERE data_quality_flag IS NOT NULL
        GROUP BY data_quality_flag
        ORDER BY count DESC
    """)

    for flag, count in cur.fetchall():
        percentage = (count / total_records) * 100
        print(f"  {flag:30} {count:>6,} ({percentage:>6.2f}%)")

    # Show samples
    print("\n" + "="*80)
    print("SAMPLE RECORDS BY QUALITY FLAG:")
    print("="*80)

    for flag in ['CHINESE_CONFIRMED', 'NON_CHINESE_CONFIRMED', 'LOW_DATA', 'NO_DATA']:
        # SECURITY: Use parameterized query to prevent SQL injection
        cur.execute("""
            SELECT name, country_code, city, region
            FROM openalex_entities
            WHERE data_quality_flag = ?
            LIMIT 3
        """, (flag,))
        results = cur.fetchall()
        if results:
            print(f"\n{flag}:")
            for name, country, city, region in results:
                print(f"  - {name or 'NULL'} | {country or 'NULL'} | {city or 'NULL'} | {region or 'NULL'}")

    conn.close()

    print("\n" + "="*80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    return True


if __name__ == '__main__':
    # Update schema
    if not update_schema():
        sys.exit(1)

    # Backfill
    if not backfill_entities():
        sys.exit(1)

    print("\n" + "="*80)
    print("[SUCCESS] OpenAlex entities NULL handling complete!")
    print("="*80)
