#!/usr/bin/env python3
"""
OSINT Foresight Data Audit - Phase 2: Processing History & Documentation
Identifies code, transformations, and processing assumptions
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
import pandas as pd

output_dir = Path("C:/Projects/OSINT - Foresight/audit_outputs")
output_dir.mkdir(exist_ok=True)

print("="*80)
print("PHASE 2: PROCESSING HISTORY & DOCUMENTATION")
print("="*80)
print()

# ============================================================================
# Task 1: Identify Raw vs. Processed Data
# ============================================================================

print("TASK 1: IDENTIFYING RAW VS. PROCESSED DATA")
print("-" * 40)

raw_processed_mapping = []

# Known raw data locations
raw_data_indicators = {
    "F:/usaspending-db_20250906.zip": {
        "type": "raw",
        "format": "zip",
        "size_gb": 41.5,
        "processed_location": "osint_master.db: usaspending_* tables",
        "record_estimate": "3M+ contracts"
    },
    "F:/Kaggle_arXiv.zip": {
        "type": "raw",
        "format": "zip",
        "size_gb": 1.5,
        "processed_location": "kaggle_arxiv_processing.db",
        "record_estimate": "1.4M papers"
    },
    "F:/TED_Data/": {
        "type": "raw",
        "format": "CSV/XML/UBL",
        "size_gb": 28,
        "processed_location": "osint_master.db: ted_contracts_production",
        "record_estimate": "1.1M contracts"
    },
    "F:/USPTO_PATENTSVIEW/": {
        "type": "raw",
        "format": "TSV",
        "size_gb": 8.1,
        "processed_location": "osint_master.db: uspto_* tables",
        "record_estimate": "65M+ classifications"
    },
    "F:/OSINT_Backups/openalex/": {
        "type": "raw",
        "format": "JSONL (compressed)",
        "size_gb": 422,
        "processed_location": "osint_master.db: openalex_* tables",
        "record_estimate": "17K works"
    },
    "F:/GLEIF/": {
        "type": "raw",
        "format": "XML/JSON",
        "size_gb": 9.4,
        "processed_location": "osint_master.db: gleif_entities",
        "record_estimate": "3.1M entities"
    }
}

print("Known Raw → Processed Mappings:")
for raw_path, details in raw_data_indicators.items():
    print(f"\n  {raw_path}")
    print(f"    → {details['processed_location']}")
    print(f"    Format: {details['format']}, Size: {details['size_gb']} GB")
    print(f"    Records: {details['record_estimate']}")

# Save mapping
with open(output_dir / "raw_vs_processed_mapping.json", "w") as f:
    json.dump(raw_data_indicators, f, indent=2)

print(f"\n[SAVED] raw_vs_processed_mapping.json")

# ============================================================================
# Task 2: Code Discovery
# ============================================================================

print("\n" + "="*80)
print("TASK 2: CODE DISCOVERY")
print("-" * 40)

code_extensions = ['.py', '.sql', '.ipynb', '.sh', '.bat', '.R']
project_root = Path("C:/Projects/OSINT - Foresight")

code_inventory = []
code_by_type = {}

print("Scanning for code files...")

for root, dirs, files in os.walk(project_root):
    # Skip certain directories
    if any(skip in root for skip in ['.git', '__pycache__', 'node_modules', 'venv', '.venv']):
        continue

    for file in files:
        ext = Path(file).suffix.lower()
        if ext in code_extensions:
            file_path = os.path.join(root, file)

            try:
                size_kb = round(os.path.getsize(file_path) / 1024, 1)

                # Count lines of code
                if ext in ['.py', '.sql', '.sh', '.bat', '.R']:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())
                    except:
                        lines = 0
                else:
                    lines = 0

                # Try to extract purpose from filename/comments
                purpose = Path(file).stem.replace('_', ' ').title()

                code_entry = {
                    "filename": file,
                    "path": file_path,
                    "language": ext[1:].upper(),
                    "size_kb": size_kb,
                    "lines": lines,
                    "purpose": purpose
                }

                code_inventory.append(code_entry)

                if ext not in code_by_type:
                    code_by_type[ext] = []
                code_by_type[ext].append(file)

            except Exception as e:
                continue

print(f"\nCode files found: {len(code_inventory)}")
print("\nBy language:")
for ext, files in sorted(code_by_type.items()):
    print(f"  {ext}: {len(files)} files")

# Save code inventory
code_df = pd.DataFrame(code_inventory)
if len(code_df) > 0:
    code_df = code_df.sort_values('lines', ascending=False)
    code_df.to_csv(output_dir / "code_inventory.csv", index=False)
    print(f"\n[SAVED] code_inventory.csv ({len(code_df)} files)")

# ============================================================================
# Task 3: Identify Key Processing Scripts
# ============================================================================

print("\n" + "="*80)
print("TASK 3: KEY PROCESSING SCRIPTS")
print("-" * 40)

# Look for scripts with specific patterns
processing_patterns = {
    "import": r"import_.*\.py",
    "process": r"process_.*\.py",
    "collect": r"collect.*\.py",
    "integrate": r"integrate.*\.py",
    "extract": r"extract.*\.py",
    "analyze": r"analyze.*\.py"
}

key_scripts = {}

for pattern_name, pattern in processing_patterns.items():
    matching_scripts = []
    for entry in code_inventory:
        if re.match(pattern, entry['filename'], re.IGNORECASE):
            matching_scripts.append({
                "filename": entry['filename'],
                "path": entry['path'],
                "lines": entry['lines'],
                "size_kb": entry['size_kb']
            })

    if matching_scripts:
        key_scripts[pattern_name] = matching_scripts
        print(f"\n{pattern_name.upper()} scripts ({len(matching_scripts)}):")
        for script in sorted(matching_scripts, key=lambda x: x['lines'], reverse=True)[:5]:
            print(f"  - {script['filename']} ({script['lines']} lines)")

# Save key scripts
with open(output_dir / "key_processing_scripts.json", "w") as f:
    json.dump(key_scripts, f, indent=2)

print(f"\n[SAVED] key_processing_scripts.json")

# ============================================================================
# Task 4: Database Schema Analysis
# ============================================================================

print("\n" + "="*80)
print("TASK 4: DATABASE SCHEMA PATTERNS")
print("-" * 40)

# Analyze table naming patterns from Phase 1
import sqlite3

db_path = "C:/Projects/OSINT - Foresight/data/osint_warehouse.db"

try:
    # Read the database catalog from Phase 1
    with open(output_dir / "database_catalog_complete.json", "r") as f:
        catalog = json.load(f)

    # Find osint_master.db
    osint_master = None
    for db in catalog:
        if db['database_name'] == 'osint_master.db' and db['size_mb'] > 20000:
            osint_master = db
            break

    if osint_master:
        print(f"\nAnalyzing osint_master.db ({osint_master['total_tables']} tables)")

        # Group tables by prefix
        table_groups = {}
        for table in osint_master['tables']:
            if 'table_name' not in table:
                continue

            table_name = table['table_name']

            # Extract prefix (first part before underscore)
            parts = table_name.split('_')
            if len(parts) > 1:
                prefix = parts[0]
            else:
                prefix = 'other'

            if prefix not in table_groups:
                table_groups[prefix] = []

            table_groups[prefix].append({
                'name': table_name,
                'rows': table.get('row_count', 0)
            })

        print("\nTable groups by prefix:")
        for prefix in sorted(table_groups.keys(), key=lambda x: len(table_groups[x]), reverse=True)[:15]:
            tables = table_groups[prefix]
            total_rows = sum(t['rows'] for t in tables)
            print(f"  {prefix}_* : {len(tables)} tables, {total_rows:,} rows")

        # Save table groups
        with open(output_dir / "table_groups_by_prefix.json", "w") as f:
            json.dump(table_groups, f, indent=2)

        print(f"\n[SAVED] table_groups_by_prefix.json")

except Exception as e:
    print(f"Could not analyze database schema: {str(e)}")

# ============================================================================
# Task 5: Documentation Discovery
# ============================================================================

print("\n" + "="*80)
print("TASK 5: DOCUMENTATION DISCOVERY")
print("-" * 40)

doc_patterns = ['README', '.md', 'GUIDE', 'DOCUMENTATION', 'SCHEMA']
docs_found = []

for root, dirs, files in os.walk(project_root):
    if any(skip in root for skip in ['.git', '__pycache__', 'node_modules']):
        continue

    for file in files:
        if any(pattern.lower() in file.lower() for pattern in doc_patterns):
            file_path = os.path.join(root, file)
            try:
                size_kb = round(os.path.getsize(file_path) / 1024, 1)
                docs_found.append({
                    "filename": file,
                    "path": file_path,
                    "size_kb": size_kb
                })
            except:
                continue

print(f"\nDocumentation files found: {len(docs_found)}")

# Group by directory
doc_by_dir = {}
for doc in docs_found:
    dir_name = Path(doc['path']).parent.name
    if dir_name not in doc_by_dir:
        doc_by_dir[dir_name] = []
    doc_by_dir[dir_name].append(doc['filename'])

print("\nBy directory:")
for dir_name, files in sorted(doc_by_dir.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
    print(f"  {dir_name}/: {len(files)} docs")

# Save documentation inventory
docs_df = pd.DataFrame(docs_found)
if len(docs_df) > 0:
    docs_df.to_csv(output_dir / "documentation_inventory.csv", index=False)
    print(f"\n[SAVED] documentation_inventory.csv")

# ============================================================================
# Summary
# ============================================================================

print("\n" + "="*80)
print("PHASE 2 SUMMARY")
print("="*80)
print(f"\nRaw data sources mapped: {len(raw_data_indicators)}")
print(f"Code files cataloged: {len(code_inventory)}")
print(f"Documentation files found: {len(docs_found)}")
print(f"\nProcessing script categories:")
for pattern_name, scripts in key_scripts.items():
    print(f"  {pattern_name}: {len(scripts)} scripts")

print("\n" + "="*80)
print("PHASE 2 COMPLETE")
print("="*80)
print(f"\nOutput files saved to: {output_dir}")
print("\nNext: Manual review of key scripts to document transformations")
print()
