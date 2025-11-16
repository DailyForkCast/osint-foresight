#!/usr/bin/env python3
"""
Create Performance Indexes for GLEIF Tables

Purpose: Dramatically speed up Chinese→European relationship queries
Expected Improvement: 30-60 minutes → 30-60 seconds (100X faster!)

Indexes to create:
  1. gleif_entities.legal_address_country - For parent/child country filtering
  2. gleif_entities.hq_address_country - For HQ-based country filtering
  3. gleif_relationships.relationship_status - For ACTIVE relationship filtering
  4. gleif_relationships.parent_lei - For join performance
  5. gleif_relationships.child_lei - For join performance

Last Updated: 2025-11-04
Author: OSINT Foresight Project
"""

import sqlite3
import time
from datetime import datetime

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

def create_indexes():
    """Create indexes on GLEIF tables"""
    print("="*80)
    print("GLEIF INDEX CREATION")
    print("="*80)
    print(f"Started: {datetime.now()}")
    print(f"Database: {DB_PATH}")
    print()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Define indexes to create
    indexes = [
        {
            "name": "idx_gleif_entities_legal_country",
            "table": "gleif_entities",
            "column": "legal_address_country",
            "description": "Filter entities by legal address country (e.g., CN, DE, GB)"
        },
        {
            "name": "idx_gleif_entities_hq_country",
            "table": "gleif_entities",
            "column": "hq_address_country",
            "description": "Filter entities by HQ country (backup for legal address)"
        },
        {
            "name": "idx_gleif_relationships_status",
            "table": "gleif_relationships",
            "column": "relationship_status",
            "description": "Filter for ACTIVE relationships"
        },
        {
            "name": "idx_gleif_relationships_parent_lei",
            "table": "gleif_relationships",
            "column": "parent_lei",
            "description": "JOIN performance (parent entity lookup)"
        },
        {
            "name": "idx_gleif_relationships_child_lei",
            "table": "gleif_relationships",
            "column": "child_lei",
            "description": "JOIN performance (child entity lookup)"
        }
    ]

    # Check what already exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index' AND name LIKE 'idx_gleif%'
        ORDER BY name
    """)
    existing_indexes = set(row[0] for row in cursor.fetchall())

    print("Existing GLEIF indexes:")
    if existing_indexes:
        for idx in sorted(existing_indexes):
            print(f"  - {idx}")
    else:
        print("  (None)")
    print()

    # Create each index
    created = 0
    skipped = 0
    errors = []

    for idx in indexes:
        index_name = idx['name']

        if index_name in existing_indexes:
            print(f"[SKIP] {index_name}")
            print(f"       Already exists")
            skipped += 1
            continue

        print(f"[CREATE] {index_name}")
        print(f"         Table: {idx['table']}")
        print(f"         Column: {idx['column']}")
        print(f"         Purpose: {idx['description']}")

        sql = f"CREATE INDEX {index_name} ON {idx['table']}({idx['column']})"

        try:
            start_time = time.time()
            cursor.execute(sql)
            conn.commit()
            elapsed = time.time() - start_time

            print(f"         Status: SUCCESS (took {elapsed:.1f}s)")
            created += 1

        except sqlite3.OperationalError as e:
            print(f"         Status: ERROR - {e}")
            errors.append(f"{index_name}: {e}")

        print()

    # Summary
    print("="*80)
    print("INDEX CREATION SUMMARY")
    print("="*80)
    print(f"Total indexes planned: {len(indexes)}")
    print(f"Created: {created}")
    print(f"Skipped (already exist): {skipped}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(f"  - {error}")

    # Verify indexes were created
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index' AND name LIKE 'idx_gleif%'
        ORDER BY name
    """)
    final_indexes = [row[0] for row in cursor.fetchall()]

    print(f"\nFinal GLEIF indexes ({len(final_indexes)} total):")
    for idx in final_indexes:
        print(f"  - {idx}")

    # Estimate index sizes
    print("\n" + "="*80)
    print("INDEX SIZE ESTIMATES")
    print("="*80)

    for idx in indexes:
        if idx['name'] in final_indexes:
            # Get approximate row count
            cursor.execute(f"SELECT COUNT(*) FROM {idx['table']}")
            row_count = cursor.fetchone()[0]

            # Rough estimate: 20-50 bytes per index entry
            estimated_mb = (row_count * 35) / (1024 * 1024)

            print(f"{idx['name']:45} ~{estimated_mb:,.1f} MB ({row_count:,} rows)")

    print("\n" + "="*80)
    print("PERFORMANCE IMPACT")
    print("="*80)
    print("Expected query performance improvement:")
    print("  BEFORE indexes: 30-60 minutes (full table scans)")
    print("  AFTER indexes:  30-60 seconds (indexed lookups)")
    print("  Improvement:    100X faster!")
    print()
    print("Queries that will benefit:")
    print("  - Chinese->European relationship extraction")
    print("  - Any country-based entity filtering")
    print("  - JOIN operations on parent_lei/child_lei")
    print()

    conn.close()

    print("="*80)
    print(f"COMPLETE: {datetime.now()}")
    print("="*80)

if __name__ == "__main__":
    create_indexes()
