#!/usr/bin/env python3
"""Scanner for files 5801, 5836, 5847, 5862"""
from full_file_china_scanner import scan_entire_file
from pathlib import Path
import json
import sys

if len(sys.argv) > 1:
    file_name = sys.argv[1]
else:
    print("Usage: python scan_other_files.py <filename>")
    sys.exit(1)

base = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/")
file_path = base / file_name

if file_path.exists():
    results = scan_entire_file(file_path, file_name)
    output_name = f'complete_{file_name.replace(".dat", "")}_china.json'
    with open(output_name, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"DONE: {file_name} - Found {results['china_references']:,} China references")
else:
    print(f"ERROR: {file_name} not found")
