#!/usr/bin/env python3
"""
Update Database Schema - Add Importance Tier Fields

Adds three new fields to all USAspending tables:
- importance_tier (TEXT): TIER_1, TIER_2, TIER_3
- importance_score (REAL): 1.0, 0.5, 0.1
- commodity_type (TEXT): office_supplies, hardware, etc.
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

# Tables to update
TABLES = [
    'usaspending_china_305',
    'usaspending_china_101',
    'usaspending_china_comprehensive'
]

def check_schema(cursor, table_name):
    """Check current schema of a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return {col[1]: col[2] for col in columns}  # {name: type}

def add_importance_fields(cursor, table_name):
    """Add importance tier fields to a table."""

    print(f"\n--- Updating {table_name} ---")

    # Check current schema
    schema = check_schema(cursor, table_name)
    print(f"Current columns: {len(schema)}")

    # Check if fields already exist
    if 'importance_tier' in schema:
        print("  importance_tier already exists")
    else:
        print("  Adding importance_tier (TEXT DEFAULT 'TIER_2')...")
        cursor.execute(f"""
            ALTER TABLE {table_name}
            ADD COLUMN importance_tier TEXT DEFAULT 'TIER_2'
        """)
        print("  [OK] importance_tier added")

    if 'importance_score' in schema:
        print("  importance_score already exists")
    else:
        print("  Adding importance_score (REAL DEFAULT 0.5)...")
        cursor.execute(f"""
            ALTER TABLE {table_name}
            ADD COLUMN importance_score REAL DEFAULT 0.5
        """)
        print("  [OK] importance_score added")

    if 'commodity_type' in schema:
        print("  commodity_type already exists")
    else:
        print("  Adding commodity_type (TEXT)...")
        cursor.execute(f"""
            ALTER TABLE {table_name}
            ADD COLUMN commodity_type TEXT
        """)
        print("  [OK] commodity_type added")

    # Verify new schema
    schema_new = check_schema(cursor, table_name)
    print(f"Updated columns: {len(schema_new)}")

    return schema_new

def main():
    """Update all tables with importance tier fields."""

    print("="*80)
    print("UPDATING DATABASE SCHEMA - IMPORTANCE TIER FIELDS")
    print("="*80)
    print(f"\nDatabase: {DB_PATH}")
    print(f"Tables: {', '.join(TABLES)}")

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check that tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}

    for table in TABLES:
        if table not in existing_tables:
            print(f"\n[WARNING] Table {table} does not exist, skipping...")
            continue

        # Get record count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        record_count = cursor.fetchone()[0]
        print(f"\n{table}: {record_count:,} records")

        # Add fields
        schema_new = add_importance_fields(cursor, table)

        # Commit changes
        conn.commit()
        print(f"  [OK] Changes committed")

    # Close connection
    conn.close()

    print("\n" + "="*80)
    print("SCHEMA UPDATE COMPLETE")
    print("="*80)

    # Summary
    print("\nNext Steps:")
    print("1. Implement categorization logic in processors")
    print("2. Re-process all records to populate importance tier fields")
    print("3. Validate categorization accuracy on sample")

    print("\nNew Fields Added:")
    print("  - importance_tier: TIER_1 (strategic) | TIER_2 (tech) | TIER_3 (commodity)")
    print("  - importance_score: 1.0 (high) | 0.5 (medium) | 0.1 (very low)")
    print("  - commodity_type: office_supplies, hardware, etc.")

    print("\nExample Query (Strategic entities only):")
    print("  SELECT * FROM usaspending_china_305")
    print("  WHERE importance_tier = 'TIER_1'")
    print("  ORDER BY award_amount DESC;")

    print("\nExample Query (Exclude commodities):")
    print("  SELECT * FROM usaspending_china_305")
    print("  WHERE importance_tier IN ('TIER_1', 'TIER_2')")
    print("  ORDER BY importance_score DESC, award_amount DESC;")

if __name__ == '__main__':
    main()
