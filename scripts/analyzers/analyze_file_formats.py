#!/usr/bin/env python3
"""Quick analysis of USAspending file formats."""

import gzip
from pathlib import Path
from collections import defaultdict

data_dir = Path("F:/OSINT_DATA/USAspending/extracted_data")

format_counts = defaultdict(list)

print("Analyzing files...")
for i, filepath in enumerate(sorted(data_dir.glob("*.dat.gz")), 1):
    try:
        with gzip.open(filepath, 'rt', encoding='utf-8', errors='replace') as f:
            first_line = f.readline()
            col_count = len(first_line.split('\t'))
            size_gb = filepath.stat().st_size / (1024**3)
            format_counts[col_count].append((filepath.name, size_gb))
            if i % 10 == 0:
                print(f"  Processed {i} files...")
    except Exception as e:
        print(f"  Error on {filepath.name}: {e}")

print("\n" + "="*80)
print("FILE FORMAT ANALYSIS")
print("="*80)

for col_count in sorted(format_counts.keys()):
    files = format_counts[col_count]
    total_size = sum(size for _, size in files)
    print(f"\n{col_count} columns: {len(files)} files, {total_size:.1f} GB total")
    print(f"  Files: {', '.join(name for name, _ in files[:10])}")
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more")

print("\n" + "="*80)
