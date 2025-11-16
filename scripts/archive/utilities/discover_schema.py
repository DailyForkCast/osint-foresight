#!/usr/bin/env python3
"""
Discover actual database schema for Netherlands analysis.
"""

import sqlite3

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

def discover_schema():
    """Discover relevant table schemas."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tables we care about
    relevant_tables = [
        'cordis_projects', 'cordis_project_countries', 'cordis_china_collaborations',
        'bilateral_events', 'bilateral_academic_links',
        'academic_partnerships', 'aspi_infrastructure',
        'gleif', 'bis_entity_list',
        'semiconductor_equipment_suppliers', 'semiconductor_market_segments',
        'openaire', 'ted', 'uspto', 'epo'
    ]

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    all_tables = [t[0] for t in cursor.fetchall()]

    print("SCHEMA DISCOVERY - Netherlands Analysis")
    print("="*80)

    for table_name in all_tables:
        # Check if this table might be relevant
        if any(keyword in table_name.lower() for keyword in ['cordis', 'ted', 'patent', 'bilateral',
                                                               'gleif', 'aspi', 'academic', 'semiconductor',
                                                               'openaire', 'bis', 'country']):
            print(f"\nTable: {table_name}")

            # Get schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  Rows: {count:,}")
            except:
                count = 0
                print(f"  Rows: Error counting")

            if count > 0:
                print(f"  Columns: {', '.join([c[1] for c in columns])}")

                # Sample a row
                try:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    sample = cursor.fetchone()
                    if sample:
                        print(f"  Sample: {sample[:5]}..." if len(sample) > 5 else f"  Sample: {sample}")
                except Exception as e:
                    print(f"  Sample: Error - {e}")

    conn.close()

if __name__ == "__main__":
    discover_schema()
