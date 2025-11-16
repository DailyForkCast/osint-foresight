#!/usr/bin/env python3
"""
Migrate ted_contracts_production table to comprehensive schema.
Adds all missing columns required by ted_complete_production_processor.py
"""

import sqlite3
from pathlib import Path

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

print("="*80)
print("TED SCHEMA MIGRATION - Add Comprehensive Columns")
print("="*80)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get existing columns
cur.execute("PRAGMA table_info(ted_contracts_production)")
existing_columns = {row[1] for row in cur.fetchall()}
print(f"\nExisting columns: {len(existing_columns)}")

# Define all columns that should exist
required_columns = {
    # Document identification
    'document_type': 'TEXT',
    'form_type': 'TEXT',

    # Contracting authority (expanded)
    'ca_official_name': 'TEXT',
    'ca_address': 'TEXT',
    'ca_city': 'TEXT',
    'ca_postal_code': 'TEXT',
    'ca_country': 'TEXT',
    'ca_type': 'TEXT',
    'ca_main_activity': 'TEXT',

    # Contract information (expanded)
    'contract_description': 'TEXT',
    'contract_type': 'TEXT',
    'cpv_main': 'TEXT',
    'cpv_additional': 'TEXT',
    'nuts_code': 'TEXT',
    'place_of_performance': 'TEXT',

    # Contract value
    'value_estimated': 'REAL',
    'value_total': 'REAL',
    'currency': 'TEXT',

    # Award information
    'award_date': 'TEXT',
    'number_tenders_received': 'INTEGER',

    # Contractor information (expanded)
    'contractor_official_name': 'TEXT',
    'contractor_city': 'TEXT',
    'contractor_postal_code': 'TEXT',
    'contractor_sme': 'BOOLEAN',

    # Additional contractors
    'additional_contractors': 'TEXT',
    'subcontractors': 'TEXT',

    # Procedure information
    'procedure_type': 'TEXT',
    'award_criteria': 'TEXT',
    'submission_deadline': 'TEXT',
    'framework_agreement': 'BOOLEAN',
    'gpa_covered': 'BOOLEAN',

    # China detection (v3 validator)
    'chinese_entities': 'TEXT',
    'validator_version': 'TEXT DEFAULT "v3.0"',
}

# Find missing columns
missing_columns = {col: dtype for col, dtype in required_columns.items() if col not in existing_columns}

print(f"Missing columns: {len(missing_columns)}")

if not missing_columns:
    print("\n✓ Schema is already up to date!")
    conn.close()
    exit(0)

print("\nAdding missing columns:")
for col, dtype in missing_columns.items():
    try:
        cur.execute(f"ALTER TABLE ted_contracts_production ADD COLUMN {col} {dtype}")
        print(f"  ✓ Added: {col} {dtype}")
    except sqlite3.OperationalError as e:
        print(f"  ⚠ Skipped: {col} - {e}")

conn.commit()

# Verify final schema
cur.execute("PRAGMA table_info(ted_contracts_production)")
final_columns = {row[1] for row in cur.fetchall()}

print(f"\n{'='*80}")
print(f"MIGRATION COMPLETE")
print(f"{'='*80}")
print(f"Final column count: {len(final_columns)}")
print(f"Columns added: {len(missing_columns)}")

# Check record count (should be unchanged)
cur.execute("SELECT COUNT(*) FROM ted_contracts_production")
record_count = cur.fetchone()[0]
print(f"Records preserved: {record_count:,}")

conn.close()

print("\n✓ Schema migration successful!")
print("  Existing records will have NULL for new columns")
print("  New processing will populate all fields")
