#!/usr/bin/env python3
"""
Get list of currently flagged TED entities for user review
"""

import sqlite3
import json
from pathlib import Path

db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

print("Connecting to database...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get list of all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%ted%'")
tables = cursor.fetchall()
print(f"\nTED-related tables found: {len(tables)}")
for table in tables:
    print(f"  - {table[0]}")

# Look for the legacy/flagged contractors
table_candidates = [
    'ted_chinese_contractors_legacy',
    'ted_chinese_contractors',
    'ted_chinese_entities',
    'ted_contractors'
]

flagged_entities = []

for table_name in table_candidates:
    try:
        # Check if table exists and has data
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"\n{'='*80}")
            print(f"Table: {table_name} - {count:,} records")
            print(f"{'='*80}")

            # Get schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            schema = cursor.fetchall()
            columns = [col[1] for col in schema]
            print(f"Columns: {', '.join(columns)}")

            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()

            if rows:
                print("\nSample records:")
                for i, row in enumerate(rows, 1):
                    print(f"\n  Record {i}:")
                    for col, val in zip(columns, row):
                        if val is not None and str(val).strip():
                            print(f"    {col}: {val}")

            # If this looks like contractor/entity table, get full list
            if any(col in columns for col in ['contractor_name', 'name', 'entity_name']):
                name_col = next((col for col in ['contractor_name', 'name', 'entity_name'] if col in columns), columns[0])

                # Get all unique entities with counts
                query = f"""
                    SELECT {name_col}, COUNT(*) as contract_count
                    FROM {table_name}
                    GROUP BY {name_col}
                    ORDER BY contract_count DESC
                """
                cursor.execute(query)
                entities = cursor.fetchall()

                print(f"\n\nTotal unique entities: {len(entities)}")
                print(f"\nTop 20 by contract count:")
                for i, (name, count) in enumerate(entities[:20], 1):
                    print(f"  {i:2}. {name} ({count} contracts)")

                # Save full list
                flagged_entities.append({
                    'table': table_name,
                    'count': len(entities),
                    'entities': [{'name': name, 'contract_count': count} for name, count in entities]
                })

    except sqlite3.OperationalError as e:
        # Table doesn't exist or error accessing it
        continue

# Save flagged entities to file for review
if flagged_entities:
    output_file = "analysis/ted_flagged_entities_for_review.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(flagged_entities, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"Full entity list saved to: {output_file}")
    print(f"{'='*80}")

    # Also create a CSV for easier review
    csv_file = "analysis/ted_flagged_entities_for_review.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write("table,entity_name,contract_count,decision,notes\n")
        for table_data in flagged_entities:
            for entity in table_data['entities']:
                # Escape commas in entity names
                name = entity['name'].replace('"', '""')
                f.write(f'"{table_data["table"]}","{name}",{entity["contract_count"]},,\n')

    print(f"CSV for review saved to: {csv_file}")
    print(f"\nYou can open the CSV to mark your decisions:")
    print(f"  - Decision column: KEEP, REMOVE, VERIFY, UNCERTAIN")
    print(f"  - Notes column: Add any notes about the entity")
else:
    print("\nNo flagged entities found in database.")
    print("Checking for the original 295 contracts mentioned in reports...")

    # Check ted_contracts table for any flagged contracts
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name = 'ted_contracts'
    """)
    if cursor.fetchone():
        cursor.execute("SELECT COUNT(*) FROM ted_contracts")
        total = cursor.fetchone()[0]
        print(f"\nted_contracts table has {total:,} total contracts")
        print("The original 295 flagged contracts may need to be re-identified.")

conn.close()
print("\nDone!")
