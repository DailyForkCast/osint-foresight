#!/usr/bin/env python3
"""
Phase 1 Verification - CORRECTED
Based on initial findings, import_openalex_china_entities has data!
"""
import sqlite3
import sys
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(db_path), timeout=10)
cursor = conn.cursor()

print("="*70)
print("PHASE 1: CORRECTED VERIFICATION")
print("="*70)

# Revised list - removing import_openalex_china_entities
safe_drops = [
    'import_openalex_authors',        # 0 records
    'import_openalex_china_topics',   # 0 records, data in openalex_work_topics
    'import_openalex_funders',        # 0 records
    'import_openalex_works',          # 0 records, data in openalex_works
    'bis_entity_list'                 # 0 records, data in bis_entity_list_fixed
]

needs_investigation = [
    'import_openalex_china_entities'  # HAS 6,344 RECORDS - investigate first!
]

print("\n[VERIFICATION RESULTS]\n")

print("SAFE TO DROP (5 tables):")
for table in safe_drops:
    cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
    count = cursor.fetchone()[0]
    print(f"  [OK] {table}: {count:,} records")

print("\nNEEDS INVESTIGATION (1 table):")
for table in needs_investigation:
    cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
    count = cursor.fetchone()[0]
    print(f"  [WAIT] {table}: {count:,} records - check if migrated")

# Check the production table for comparison
cursor.execute('SELECT COUNT(*) FROM "openalex_entities"')
prod_count = cursor.fetchone()[0]
print(f"        openalex_entities (production): {prod_count:,} records")

if prod_count == 6344:
    print("        ANALYSIS: Counts match - data may be duplicated")
    print("        ACTION: Verify no unique records in staging before dropping")
else:
    print("        ANALYSIS: Counts differ - staging may have unique data")
    print("        ACTION: Must migrate before dropping")

print("\n" + "="*70)
print("REVISED PHASE 1 PLAN")
print("="*70)
print(f"\nDROP IMMEDIATELY: {len(safe_drops)} tables")
print(f"INVESTIGATE FIRST: {len(needs_investigation)} table")
print(f"\nTotal to clean: {len(safe_drops)} now, +1 after investigation")
print("="*70)

conn.close()
