#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create GLEIF ETL 100-Record Manual Validation Worksheet
Purpose: Generate Excel file for manual precision validation per ETL framework
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

print("="*80)
print("GLEIF ETL VALIDATION WORKSHEET GENERATOR")
print("="*80)
print(f"Started: {datetime.now()}")
print()

# Connect to database
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get 100 most recent GLEIF corporate links
print("Extracting 100-record sample from bilateral_corporate_links...")
cursor.execute("""
    SELECT
        link_id,
        country_code,
        chinese_entity,
        foreign_entity,
        relationship_type,
        gleif_lei,
        created_at
    FROM bilateral_corporate_links
    WHERE created_at >= datetime('now', '-2 hours')
      AND gleif_lei IS NOT NULL
    ORDER BY created_at DESC
    LIMIT 100
""")

records = []
for row in cursor.fetchall():
    records.append({
        'Record_ID': len(records) + 1,
        'Link_ID': row['link_id'],
        'Country': row['country_code'],
        'Chinese_Entity': row['chinese_entity'] or '',
        'Foreign_Entity': row['foreign_entity'] or '',
        'Relationship_Type': row['relationship_type'],
        'GLEIF_LEI': row['gleif_lei'],
        'GLEIF_Verification_URL': f"https://search.gleif.org/#/record/{row['gleif_lei']}",
        'Valid': '',  # For manual review
        'Notes': '',  # For manual notes
        'Created_At': row['created_at']
    })

print(f"[OK] Extracted {len(records)} records")

# Create DataFrame
df = pd.DataFrame(records)

# Create Excel file with multiple sheets
filename = f"analysis/etl_validation/GLEIF_100_Record_Validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

print(f"\nCreating Excel validation worksheet: {filename}")

with pd.ExcelWriter(filename, engine='openpyxl') as writer:
    # Sheet 1: Validation Records
    df.to_excel(writer, sheet_name='Validation_Sample', index=False)

    # Sheet 2: Instructions
    instructions = pd.DataFrame({
        'Step': [
            1,
            2,
            3,
            4,
            5,
            6,
            7
        ],
        'Instruction': [
            'OBJECTIVE: Verify that 90%+ of records are TRUE POSITIVES (valid Chinese->European relationships)',
            'For each record, click the GLEIF_Verification_URL to verify the relationship in the official GLEIF registry',
            'Check: Is the Chinese_Entity truly a Chinese company? (Look for CN country code in GLEIF)',
            'Check: Is the Foreign_Entity truly in the specified European country?',
            'Check: Does the relationship type (subsidiary/branch) match GLEIF data?',
            'Mark "Valid" column: Y = True Positive, N = False Positive, ? = Uncertain',
            'Add notes in "Notes" column for any issues or interesting findings'
        ]
    })
    instructions.to_excel(writer, sheet_name='Instructions', index=False)

    # Sheet 3: Summary Statistics
    summary = pd.DataFrame({
        'Metric': [
            'Total Records',
            'Created Date',
            'ETL Script',
            'Data Source',
            'Validation Status',
            'Country Count',
            'Countries',
            '',
            'PRECISION REQUIREMENT',
            'Minimum Valid Records',
            'Maximum Invalid Records'
        ],
        'Value': [
            len(records),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'etl_corporate_links_from_gleif_v6_comprehensive.py',
            'GLEIF (Global Legal Entity Identifier Foundation)',
            'PENDING MANUAL REVIEW',
            df['Country'].nunique(),
            ', '.join(sorted(df['Country'].unique())),
            '',
            '≥90% precision to PASS',
            '≥90 valid records',
            '≤10 invalid records'
        ]
    })
    summary.to_excel(writer, sheet_name='Summary', index=False)

    # Sheet 4: Country Distribution
    country_dist = df.groupby('Country').size().reset_index(name='Count')
    country_dist = country_dist.sort_values('Count', ascending=False)
    country_dist.to_excel(writer, sheet_name='Country_Distribution', index=False)

    # Sheet 5: Relationship Type Distribution
    rel_dist = df.groupby('Relationship_Type').size().reset_index(name='Count')
    rel_dist = rel_dist.sort_values('Count', ascending=False)
    rel_dist.to_excel(writer, sheet_name='Relationship_Types', index=False)

print(f"[OK] Excel file created successfully")
print()

# Print summary
print("="*80)
print("VALIDATION WORKSHEET SUMMARY")
print("="*80)
print(f"Total records: {len(records)}")
print(f"Countries covered: {df['Country'].nunique()}")
print(f"Relationship types: {df['Relationship_Type'].nunique()}")
print()

print("Country distribution:")
for country, count in country_dist.values:
    print(f"  {country}: {count}")
print()

print("Relationship type distribution:")
for rel_type, count in rel_dist.values:
    print(f"  {rel_type}: {count}")
print()

print("="*80)
print("NEXT STEPS")
print("="*80)
print(f"1. Open Excel file: {filename}")
print("2. Review each record using GLEIF_Verification_URL")
print("3. Mark 'Valid' column: Y/N/?")
print("4. Calculate precision: (Y records / 100) * 100%")
print("5. PASS = ≥90%, FAIL = <90%")
print()
print("[OK] Validation worksheet ready for manual review")
print("="*80)

conn.close()
