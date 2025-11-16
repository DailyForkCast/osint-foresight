#!/usr/bin/env python3
"""
OSINT Foresight Data Audit - Phase 1: Database Inventory
Complete catalog of all SQLite databases with table structures and row counts
"""

import sqlite3
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

output_dir = Path("C:/Projects/OSINT - Foresight/audit_outputs")
output_dir.mkdir(exist_ok=True)

print("="*80)
print("PHASE 1: COMPREHENSIVE DATABASE INVENTORY")
print("="*80)
print()

# Discover all .db files
print("Discovering all database files...")
print("-" * 40)

database_locations = [
    "C:/Projects/OSINT - Foresight/data",
    "F:/OSINT_WAREHOUSE",
    "F:/OSINT_Data"
]

all_databases = []

for location in database_locations:
    if os.path.exists(location):
        for root, dirs, files in os.walk(location):
            for file in files:
                if file.endswith('.db'):
                    db_path = os.path.join(root, file)
                    size_mb = round(os.path.getsize(db_path) / (1024**2), 1)
                    all_databases.append({
                        "path": db_path,
                        "name": file,
                        "size_mb": size_mb,
                        "location": root
                    })
                    print(f"  Found: {file} ({size_mb} MB)")

print(f"\nTotal databases found: {len(all_databases)}")
print()

# Process each database
print("="*80)
print("ANALYZING DATABASES")
print("="*80)
print()

database_catalog = []

for db_info in all_databases:
    db_path = db_info["path"]
    db_name = db_info["name"]

    print(f"\nDatabase: {db_name}")
    print("-" * 40)

    catalog_entry = {
        "database_name": db_name,
        "path": db_path,
        "size_mb": db_info["size_mb"],
        "tables": [],
        "total_tables": 0,
        "total_rows": 0,
        "accessible": False,
        "error": None
    }

    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        catalog_entry["total_tables"] = len(tables)
        catalog_entry["accessible"] = True

        print(f"  Tables: {len(tables)}")

        # Get row counts for each table
        for table_name in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
                row_count = cursor.fetchone()[0]

                # Get column info
                cursor.execute(f"PRAGMA table_info([{table_name}])")
                columns = cursor.fetchall()
                column_info = [{"name": col[1], "type": col[2]} for col in columns]

                table_entry = {
                    "table_name": table_name,
                    "row_count": row_count,
                    "column_count": len(column_info),
                    "columns": column_info
                }

                catalog_entry["tables"].append(table_entry)
                catalog_entry["total_rows"] += row_count

                if row_count > 0:
                    print(f"    {table_name}: {row_count:,} rows, {len(column_info)} columns")

            except Exception as e:
                print(f"    {table_name}: ERROR - {str(e)}")
                table_entry = {
                    "table_name": table_name,
                    "error": str(e)
                }
                catalog_entry["tables"].append(table_entry)

        conn.close()

        print(f"  Total rows: {catalog_entry['total_rows']:,}")

    except Exception as e:
        catalog_entry["error"] = str(e)
        print(f"  ERROR: {str(e)}")

    database_catalog.append(catalog_entry)

# Save comprehensive catalog
catalog_file = output_dir / "database_catalog_complete.json"
with open(catalog_file, "w") as f:
    json.dump(database_catalog, f, indent=2)

print(f"\n[SAVED] {catalog_file.name}")

# Create summary CSV
summary_data = []
for db in database_catalog:
    summary_data.append({
        "Database": db["database_name"],
        "Size_MB": db["size_mb"],
        "Tables": db["total_tables"],
        "Total_Rows": db["total_rows"],
        "Status": "OK" if db["accessible"] else "ERROR"
    })

summary_df = pd.DataFrame(summary_data)
summary_csv = output_dir / "database_summary.csv"
summary_df.to_csv(summary_csv, index=False)

print(f"[SAVED] {summary_csv.name}")

# Create detailed table inventory
print("\n" + "="*80)
print("CREATING DETAILED TABLE INVENTORY")
print("="*80)

all_tables = []
for db in database_catalog:
    if db["accessible"]:
        for table in db["tables"]:
            if "row_count" in table:
                all_tables.append({
                    "Database": db["database_name"],
                    "Table": table["table_name"],
                    "Rows": table["row_count"],
                    "Columns": table["column_count"],
                    "Database_Size_MB": db["size_mb"]
                })

tables_df = pd.DataFrame(all_tables)
tables_csv = output_dir / "all_tables_inventory.csv"
tables_df.to_csv(tables_csv, index=False)

print(f"[SAVED] {tables_csv.name}")

# Summary statistics
print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)
print()
print(f"Total Databases: {len(database_catalog)}")
print(f"Accessible Databases: {sum(1 for db in database_catalog if db['accessible'])}")
print(f"Total Tables: {sum(db['total_tables'] for db in database_catalog)}")
print(f"Total Rows Across All Tables: {sum(db['total_rows'] for db in database_catalog):,}")
print(f"Total Storage: {sum(db['size_mb'] for db in database_catalog):.1f} MB")
print()

# Top 10 largest tables
if len(all_tables) > 0:
    print("Top 10 Largest Tables by Row Count:")
    print("-" * 60)
    top_tables = sorted(all_tables, key=lambda x: x['Rows'], reverse=True)[:10]
    for i, table in enumerate(top_tables, 1):
        print(f"  {i}. {table['Database']}.{table['Table']}: {table['Rows']:,} rows")

print("\n" + "="*80)
print("PHASE 1 COMPLETE")
print("="*80)
print()
print(f"Output files saved to: {output_dir}")
print()
