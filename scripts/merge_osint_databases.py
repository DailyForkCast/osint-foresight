#!/usr/bin/env python3
"""
Merge data from F:/OSINT_DATA/osint_master.db into F:/OSINT_WAREHOUSE/osint_master.db
"""

import sqlite3
import os
from datetime import datetime
import shutil

# SECURITY: Whitelist of allowed table names to prevent SQL injection
ALLOWED_TABLES = {
    'entities',
    'entity_aliases',
    'collaborations',
    'technologies',
    'publications',
    'funding',
    'procurement',
    'risk_indicators',
    'intelligence_events',
    'data_provenance',
    'cross_references',
    'china_entities',
    'patents',
    'patent_collection_stats'
}

# SECURITY: Whitelist of allowed column names for index creation
ALLOWED_COLUMNS = {
    'company_name',
    'technology_area',
    'country',
    'publication_date',
    'entity_name_english',
    'entity_type'
}

# SECURITY: Whitelist of allowed index names
ALLOWED_INDEXES = {
    'idx_patents_company',
    'idx_patents_tech',
    'idx_patents_country',
    'idx_patents_date',
    'idx_china_entities_name',
    'idx_china_entities_type'
}

def validate_table_name(table_name):
    """
    SECURITY: Validate table name against whitelist to prevent SQL injection.
    Only use table names from trusted hardcoded list.
    """
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table name: {table_name}. Not in whitelist.")
    return table_name

def validate_column_name(column_name):
    """
    SECURITY: Validate column name against whitelist to prevent SQL injection.
    """
    if column_name not in ALLOWED_COLUMNS:
        raise ValueError(f"Invalid column name: {column_name}. Not in whitelist.")
    return column_name

def validate_index_name(index_name):
    """
    SECURITY: Validate index name against whitelist to prevent SQL injection.
    """
    if index_name not in ALLOWED_INDEXES:
        raise ValueError(f"Invalid index name: {index_name}. Not in whitelist.")
    return index_name

def merge_databases():
    source_db = "F:/OSINT_DATA/osint_master.db"
    target_db = "F:/OSINT_WAREHOUSE/osint_master.db"
    backup_db = f"F:/OSINT_WAREHOUSE/osint_master_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

    print("="*70)
    print("DATABASE MERGE OPERATION")
    print("="*70)
    print(f"\nSource: {source_db}")
    print(f"Target: {target_db}")

    # First, create a backup
    print(f"\n[1] Creating backup: {backup_db}")
    shutil.copy2(target_db, backup_db)
    print("    Backup created successfully")

    # Connect to both databases
    source_conn = sqlite3.connect(source_db)
    target_conn = sqlite3.connect(target_db)

    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    # Tables to migrate from OSINT_DATA
    tables_to_migrate = list(ALLOWED_TABLES)

    print("\n[2] Migrating tables from OSINT_DATA to OSINT_WAREHOUSE:")

    total_rows_migrated = 0

    for table in tables_to_migrate:
        try:
            # SECURITY: Validate table name against whitelist
            safe_table = validate_table_name(table)

            # Check if table exists in source
            source_cursor.execute(f"SELECT COUNT(*) FROM {safe_table}")
            source_count = source_cursor.fetchone()[0]

            if source_count == 0:
                print(f"    - {safe_table}: No data to migrate")
                continue

            # Get table structure from source
            source_cursor.execute(f"PRAGMA table_info({safe_table})")
            columns_info = source_cursor.fetchall()
            column_names = [col[1] for col in columns_info]

            # Check if table exists in target
            target_cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name=?
            """, (safe_table,))

            table_exists = target_cursor.fetchone() is not None

            if not table_exists:
                # Create table in target
                source_cursor.execute(f"""
                    SELECT sql FROM sqlite_master
                    WHERE type='table' AND name=?
                """, (safe_table,))
                create_sql = source_cursor.fetchone()[0]

                target_cursor.execute(create_sql)
                print(f"    - {safe_table}: Created table")

            # Migrate data
            source_cursor.execute(f"SELECT * FROM {safe_table}")
            rows = source_cursor.fetchall()

            if safe_table == 'patents':
                # For patents, use INSERT OR IGNORE to avoid duplicates
                placeholders = ','.join(['?' for _ in column_names])
                insert_sql = f"INSERT OR IGNORE INTO {safe_table} ({','.join(column_names)}) VALUES ({placeholders})"
            else:
                # For other tables, use INSERT OR REPLACE
                placeholders = ','.join(['?' for _ in column_names])
                insert_sql = f"INSERT OR REPLACE INTO {safe_table} ({','.join(column_names)}) VALUES ({placeholders})"

            rows_before = target_cursor.execute(f"SELECT COUNT(*) FROM {safe_table}").fetchone()[0] if table_exists else 0

            for row in rows:
                try:
                    target_cursor.execute(insert_sql, row)
                except sqlite3.IntegrityError as e:
                    # Skip duplicates
                    pass

            target_conn.commit()

            rows_after = target_cursor.execute(f"SELECT COUNT(*) FROM {safe_table}").fetchone()[0]
            rows_added = rows_after - rows_before

            print(f"    - {safe_table}: Added {rows_added:,} rows (total now: {rows_after:,})")
            total_rows_migrated += rows_added

        except Exception as e:
            print(f"    - {table}: Error - {e}")

    # Also create indexes for better performance
    print("\n[3] Creating indexes for patent tables:")

    indexes = [
        ("idx_patents_company", "patents", "company_name"),
        ("idx_patents_tech", "patents", "technology_area"),
        ("idx_patents_country", "patents", "country"),
        ("idx_patents_date", "patents", "publication_date"),
        ("idx_china_entities_name", "china_entities", "entity_name_english"),
        ("idx_china_entities_type", "china_entities", "entity_type")
    ]

    for index_name, table_name, column_name in indexes:
        try:
            # SECURITY: Validate all identifiers (index, table, column) before use
            safe_index = validate_index_name(index_name)
            safe_table = validate_table_name(table_name)
            safe_column = validate_column_name(column_name)
            target_cursor.execute(f"CREATE INDEX IF NOT EXISTS {safe_index} ON {safe_table}({safe_column})")
            print(f"    Created index: {safe_index}")
        except Exception as e:
            print(f"    Index {index_name} - skipped: {e}")

    target_conn.commit()

    # Show final statistics
    print("\n[4] Final Statistics:")

    # Count total rows in target database
    target_cursor.execute("""
        SELECT name FROM sqlite_master WHERE type='table'
    """)
    tables = target_cursor.fetchall()

    total_rows = 0
    for table in tables:
        table_name = table[0]
        if table_name != 'sqlite_sequence' and table_name in ALLOWED_TABLES:
            # SECURITY: Only count tables from our whitelist
            safe_table = validate_table_name(table_name)
            count = target_cursor.execute(f"SELECT COUNT(*) FROM {safe_table}").fetchone()[0]
            if count > 0:
                total_rows += count
                if count > 100:  # Only show tables with significant data
                    print(f"    - {table_name}: {count:,} rows")

    print(f"\n    Total rows in merged database: {total_rows:,}")
    print(f"    Total new rows added: {total_rows_migrated:,}")

    # Show patent statistics
    if 'patents' in [t[0] for t in tables]:
        patent_count = target_cursor.execute("SELECT COUNT(*) FROM patents").fetchone()[0]
        print(f"\n[5] Patent Data Summary:")
        print(f"    Total patents: {patent_count:,}")

        # Patents by company
        target_cursor.execute("""
            SELECT company_name, COUNT(*) as count
            FROM patents
            WHERE company_name IS NOT NULL
            GROUP BY company_name
            ORDER BY count DESC
            LIMIT 5
        """)
        print("    Top companies:")
        for company, count in target_cursor.fetchall():
            print(f"      - {company}: {count:,}")

    # Close connections
    source_conn.close()
    target_conn.close()

    print("\n" + "="*70)
    print("MERGE COMPLETE")
    print("="*70)
    print(f"Master database: {target_db}")
    print(f"Backup saved as: {backup_db}")

if __name__ == "__main__":
    merge_databases()
