#!/usr/bin/env python3
"""
OSINT Foresight Data Audit - Phase 0 & Phase 1
Based on audit prompt v2.0
"""

import sqlite3
import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
import pandas as pd

# Output directory
output_dir = Path("C:/Projects/OSINT - Foresight/audit_outputs")
output_dir.mkdir(exist_ok=True)

print("="*80)
print("PHASE 0: PRE-FLIGHT CHECKS & ENVIRONMENT VERIFICATION")
print("="*80)
print()

# 1. Environment Check
print("1. ENVIRONMENT CHECK")
print("-" * 40)

env_report = {
    "audit_date": datetime.now().isoformat(),
    "python_version": sys.version,
    "platform": sys.platform,
}

print(f"Python: {sys.version.split()[0]}")
print(f"Platform: {sys.platform}")

# Check key libraries
libs_available = {}
for lib in ['pandas', 'sqlite3', 'json', 'csv', 'gzip', 'numpy', 'matplotlib']:
    try:
        __import__(lib)
        libs_available[lib] = True
        print(f"  [OK] {lib}")
    except ImportError:
        libs_available[lib] = False
        print(f"  [MISS] {lib}")

env_report["libraries"] = libs_available

# Disk space
import shutil
c_stats = shutil.disk_usage("C:/")
f_stats = shutil.disk_usage("F:/")

print(f"\nDisk Space:")
print(f"  C: {c_stats.free / (1024**3):.1f} GB free of {c_stats.total / (1024**3):.1f} GB")
print(f"  F: {f_stats.free / (1024**3):.1f} GB free of {f_stats.total / (1024**3):.1f} GB")

env_report["disk_space"] = {
    "C_free_gb": round(c_stats.free / (1024**3), 1),
    "C_total_gb": round(c_stats.total / (1024**3), 1),
    "F_free_gb": round(f_stats.free / (1024**3), 1),
    "F_total_gb": round(f_stats.total / (1024**3), 1)
}

# Save environment report
with open(output_dir / "environment_report.json", "w") as f:
    json.dump(env_report, f, indent=2)

print(f"\n[SAVED] environment_report.json")

# 2. Database Access Test
print("\n2. DATABASE ACCESS TEST")
print("-" * 40)

databases = [
    "C:/Projects/OSINT - Foresight/data/kaggle_arxiv_processing.db",
    "C:/Projects/OSINT - Foresight/data/osint_warehouse.db",
    "C:/Projects/OSINT - Foresight/data/github_activity.db"
]

db_test_results = []

for db_path in databases:
    result = {
        "path": db_path,
        "exists": os.path.exists(db_path),
        "readable": False,
        "table_count": 0,
        "size_mb": 0
    }

    if os.path.exists(db_path):
        result["size_mb"] = round(os.path.getsize(db_path) / (1024**2), 1)

        try:
            conn = sqlite3.connect(db_path, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            result["table_count"] = cursor.fetchone()[0]
            result["readable"] = True
            conn.close()
            print(f"  [OK] {Path(db_path).name} - {result['table_count']} tables, {result['size_mb']} MB")
        except Exception as e:
            result["error"] = str(e)
            print(f"  [FAIL] {Path(db_path).name} - {str(e)}")
    else:
        print(f"  [MISS] {Path(db_path).name} - File not found")

    db_test_results.append(result)

# Save database test results
with open(output_dir / "database_access_test.json", "w") as f:
    json.dump(db_test_results, f, indent=2)

print(f"\n[SAVED] database_access_test.json")

# 3. Sample File Accessibility Test
print("\n3. SAMPLE FILE ACCESSIBILITY TEST")
print("-" * 40)

# Test a few key files
test_files = [
    "F:/Kaggle_arXiv.zip",
    "F:/usaspending-db_20250906.zip",
    "F:/GLEIF/bulk_data",  # directory
    "F:/TED_Data/monthly",  # directory
]

file_test_results = []

for file_path in test_files:
    result = {
        "path": file_path,
        "exists": os.path.exists(file_path),
        "is_dir": os.path.isdir(file_path) if os.path.exists(file_path) else False,
        "readable": False,
        "size_mb": 0
    }

    if os.path.exists(file_path):
        try:
            if os.path.isdir(file_path):
                # Count files in directory
                files = list(Path(file_path).iterdir())
                result["file_count"] = len(files)
                result["readable"] = True
                print(f"  [OK] {Path(file_path).name}/ - Directory with {len(files)} items")
            else:
                result["size_mb"] = round(os.path.getsize(file_path) / (1024**2), 1)
                # Try to read first few bytes
                with open(file_path, 'rb') as f:
                    f.read(1024)
                result["readable"] = True
                print(f"  [OK] {Path(file_path).name} - {result['size_mb']} MB")
        except Exception as e:
            result["error"] = str(e)
            print(f"  [FAIL] {Path(file_path).name} - {str(e)}")
    else:
        print(f"  [MISS] {Path(file_path).name} - Not found")

    file_test_results.append(result)

with open(output_dir / "file_accessibility_test.json", "w") as f:
    json.dump(file_test_results, f, indent=2)

print(f"\n[SAVED] file_accessibility_test.json")

print("\n" + "="*80)
print("PHASE 0 COMPLETE")
print("="*80)
print()
print("NEXT STEP: Phase 1 (Comprehensive Inventory)")
print("This will scan all databases and catalog their contents.")
print()
