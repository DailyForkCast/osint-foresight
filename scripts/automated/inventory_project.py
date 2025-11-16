#!/usr/bin/env python3
"""
Project Inventory Script
Systematically catalog all code, data, and processes

Output: Complete inventory in JSON format
"""

import os
import json
import sqlite3
from pathlib import Path
from collections import defaultdict
from datetime import datetime

project_root = Path("C:/Projects/OSINT-Foresight")
db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

def inventory_scripts():
    """Inventory all Python scripts by category"""
    scripts_by_category = defaultdict(list)

    scripts_dir = project_root / "scripts"
    for py_file in scripts_dir.rglob("*.py"):
        # Get category from directory
        relative = py_file.relative_to(scripts_dir)
        category = str(relative.parts[0]) if len(relative.parts) > 1 else "root"

        # Get file info
        stat = py_file.stat()
        scripts_by_category[category].append({
            "name": py_file.name,
            "path": str(py_file.relative_to(project_root)),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        })

    # Sort and count
    inventory = {}
    for category in sorted(scripts_by_category.keys()):
        inventory[category] = {
            "count": len(scripts_by_category[category]),
            "total_size": sum(s["size"] for s in scripts_by_category[category]),
            "scripts": sorted(scripts_by_category[category], key=lambda x: x["name"])
        }

    return inventory

def inventory_database():
    """Inventory database tables and record counts"""
    if not db_path.exists():
        return {"error": f"Database not found: {db_path}"}

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cur.fetchall()]

    table_info = {}
    total_records = 0

    for table in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            total_records += count

            # Get column count
            cur.execute(f"PRAGMA table_info({table})")
            columns = cur.fetchall()

            table_info[table] = {
                "records": count,
                "columns": len(columns),
                "column_names": [col[1] for col in columns],
                "status": "populated" if count > 0 else "empty"
            }
        except Exception as e:
            table_info[table] = {"error": str(e)}

    conn.close()

    return {
        "total_tables": len(tables),
        "populated_tables": sum(1 for t in table_info.values() if t.get("status") == "populated"),
        "empty_tables": sum(1 for t in table_info.values() if t.get("status") == "empty"),
        "total_records": total_records,
        "tables": table_info
    }

def inventory_f_drive():
    """Inventory data sources on F: drive"""
    f_drive = Path("F:/")
    if not f_drive.exists():
        return {"error": "F: drive not accessible"}

    # Key directories to inventory
    data_dirs = [
        "OSINT_Data",
        "OSINT_WAREHOUSE",
        "OSINT_Backups",
        "TED_Data",
        "USPTO_PATENTSVIEW",
        "USPTO Data",
        "GLEIF",
        "ETO_Datasets",
        "ESTAT",
        "China_Sweeps",
        "Europe_China_Sweeps",
        "ThinkTank_Sweeps",
        "PRC_SOE_Sweeps",
        "Policy_Documents_Sweep"
    ]

    inventory = {}
    for dir_name in data_dirs:
        dir_path = f_drive / dir_name
        if dir_path.exists():
            try:
                # Count files and total size
                file_count = 0
                total_size = 0
                for item in dir_path.rglob("*"):
                    if item.is_file():
                        file_count += 1
                        total_size += item.stat().st_size

                inventory[dir_name] = {
                    "exists": True,
                    "file_count": file_count,
                    "total_size_gb": round(total_size / (1024**3), 2)
                }
            except Exception as e:
                inventory[dir_name] = {
                    "exists": True,
                    "error": str(e)
                }
        else:
            inventory[dir_name] = {"exists": False}

    return inventory

def main():
    """Run complete inventory"""
    print("="*80)
    print("PROJECT INVENTORY - Systematic Audit Phase 1")
    print("="*80 + "\n")

    print("1. Inventorying Python scripts...")
    scripts = inventory_scripts()
    print(f"   Found {sum(cat['count'] for cat in scripts.values())} scripts across {len(scripts)} categories\n")

    print("2. Inventorying database...")
    database = inventory_database()
    if "error" not in database:
        print(f"   Found {database['total_tables']} tables with {database['total_records']:,} total records\n")
    else:
        print(f"   Error: {database['error']}\n")

    print("3. Inventorying F: drive data sources...")
    f_drive = inventory_f_drive()
    print(f"   Found {sum(1 for d in f_drive.values() if d.get('exists'))} data directories\n")

    # Compile full inventory
    full_inventory = {
        "timestamp": datetime.now().isoformat(),
        "scripts": scripts,
        "database": database,
        "f_drive": f_drive
    }

    # Save to file
    output_path = project_root / "PHASE1_INVENTORY.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(full_inventory, f, indent=2)

    print(f"Complete inventory saved to: {output_path}")
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Scripts: {sum(cat['count'] for cat in scripts.values())}")
    if "error" not in database:
        print(f"Database Tables: {database['total_tables']}")
        print(f"Database Records: {database['total_records']:,}")
    print(f"Data Directories: {sum(1 for d in f_drive.values() if d.get('exists'))}")
    print("="*80)

if __name__ == "__main__":
    main()
