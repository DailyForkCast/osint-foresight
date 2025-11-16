#!/usr/bin/env python3
"""
Phase 1 Verification - Confirm tables are safe to DROP
"""
import sqlite3
from pathlib import Path

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(db_path), timeout=10)
cursor = conn.cursor()

print("="*70)
print("PHASE 1: VERIFYING SAFE-TO-DROP TABLES")
print("="*70)

# Tables we plan to drop
drop_candidates = [
    'import_openalex_authors',
    'import_openalex_china_entities',
    'import_openalex_china_topics',
    'import_openalex_funders',
    'import_openalex_works',
    'bis_entity_list'  # Only if bis_entity_list_fixed has data
]

# Production tables that should have the imported data
production_checks = {
    'import_openalex_authors': 'openalex_authors_full',
    'import_openalex_china_entities': 'openalex_entities',
    'import_openalex_china_topics': 'openalex_work_topics',
    'import_openalex_funders': 'openalex_funders_full',
    'import_openalex_works': 'openalex_works',
    'bis_entity_list': 'bis_entity_list_fixed'
}

safe_to_drop = []
needs_investigation = []

print("\n[VERIFICATION CHECKS]\n")

for drop_table in drop_candidates:
    print(f"Checking: {drop_table}")

    # Check if table is empty
    try:
        cursor.execute(f'SELECT COUNT(*) FROM "{drop_table}"')
        drop_count = cursor.fetchone()[0]
        print(f"  Records in {drop_table}: {drop_count:,}")
    except Exception as e:
        print(f"  ERROR reading {drop_table}: {e}")
        needs_investigation.append(drop_table)
        continue

    # Check if production table exists and has data
    prod_table = production_checks.get(drop_table)
    if prod_table:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{prod_table}"')
            prod_count = cursor.fetchone()[0]
            print(f"  Records in {prod_table}: {prod_count:,}")

            if drop_count == 0 and prod_count > 0:
                print(f"  ✓ SAFE TO DROP - data migrated to production")
                safe_to_drop.append(drop_table)
            elif drop_count == 0 and prod_count == 0:
                print(f"  ⚠ WARNING - both tables empty, but safe to drop staging")
                safe_to_drop.append(drop_table)
            else:
                print(f"  ✗ NOT SAFE - staging table has data!")
                needs_investigation.append(drop_table)
        except Exception as e:
            print(f"  ERROR reading {prod_table}: {e}")
            needs_investigation.append(drop_table)
    else:
        if drop_count == 0:
            print(f"  ✓ Empty - safe to drop")
            safe_to_drop.append(drop_table)

    print()

# Check for foreign key dependencies
print("\n[FOREIGN KEY CHECK]")
for table in drop_candidates:
    cursor.execute(f'PRAGMA foreign_key_list("{table}")')
    fkeys = cursor.fetchall()
    if fkeys:
        print(f"⚠ {table} has foreign keys: {fkeys}")
        if table in safe_to_drop:
            safe_to_drop.remove(table)
            needs_investigation.append(table)
    else:
        print(f"✓ {table} has no foreign key dependencies")

print("\n" + "="*70)
print("VERIFICATION SUMMARY")
print("="*70)
print(f"\nSafe to DROP ({len(safe_to_drop)} tables):")
for table in safe_to_drop:
    print(f"  ✓ {table}")

if needs_investigation:
    print(f"\nNeeds Investigation ({len(needs_investigation)} tables):")
    for table in needs_investigation:
        print(f"  ⚠ {table}")

print("\n" + "="*70)

conn.close()

# Return exit code
import sys
sys.exit(0 if len(needs_investigation) == 0 else 1)
