#!/usr/bin/env python3
"""Scanner for file 5848.dat - 222 GB"""
from full_file_china_scanner import scan_entire_file
from pathlib import Path
import json

file_path = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5848.dat")
if file_path.exists():
    results = scan_entire_file(file_path, "5848.dat")
    with open('complete_5848_china.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"DONE: 5848.dat - Found {results['china_references']:,} China references")
