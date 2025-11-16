#!/usr/bin/env python3
"""
Process TED Legacy Archives (2006-2022)
Uses dual-format processor to extract contractors from old XML format
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent))

from ted_eforms_enhanced_processor import TEDEFormsProcessor

print("="*80)
print("TED LEGACY ARCHIVE PROCESSING (2006-2022)")
print("="*80)

# Initialize processor
processor = TEDEFormsProcessor()

# Define year range for legacy format
START_YEAR = 2006
END_YEAR = 2022

# Track overall stats
total_stats = {
    'archives_processed': 0,
    'total_contracts': 0,
    'total_chinese': 0,
    'total_errors': 0,
    'year_breakdown': {}
}

# Process each year
for year in range(START_YEAR, END_YEAR + 1):
    print(f"\n{'='*80}")
    print(f"PROCESSING YEAR: {year}")
    print(f"{'='*80}")

    year_stats = {
        'archives': 0,
        'contracts': 0,
        'chinese': 0,
        'errors': 0
    }

    # Process each month
    for month in range(1, 13):
        archive_path = Path(f"F:/TED_Data/monthly/{year}/TED_monthly_{year}_{month:02d}.tar.gz")

        if not archive_path.exists():
            print(f"WARNING: Archive not found: {archive_path.name}")
            continue

        print(f"\n[{year}-{month:02d}] Processing {archive_path.name}...")

        try:
            stats = processor.process_monthly_archive(archive_path, year, month)

            year_stats['archives'] += 1
            year_stats['contracts'] += stats['contracts_inserted']
            year_stats['chinese'] += stats['chinese_found']
            year_stats['errors'] += stats['errors']

            print(f"  OK - Contracts: {stats['contracts_inserted']}, Chinese: {stats['chinese_found']}, Errors: {stats['errors']}")

        except Exception as e:
            print(f"  ERROR: {str(e)}")
            year_stats['errors'] += 1

    # Year summary
    print(f"\n{year} SUMMARY:")
    print(f"  Archives: {year_stats['archives']}/12")
    print(f"  Contracts: {year_stats['contracts']}")
    print(f"  Chinese: {year_stats['chinese']}")

    total_stats['archives_processed'] += year_stats['archives']
    total_stats['total_contracts'] += year_stats['contracts']
    total_stats['total_chinese'] += year_stats['chinese']
    total_stats['total_errors'] += year_stats['errors']
    total_stats['year_breakdown'][year] = year_stats

# Final summary
print(f"\n{'='*80}")
print("FINAL SUMMARY (2006-2022)")
print(f"{'='*80}")
print(f"Total archives processed: {total_stats['archives_processed']}/204")
print(f"Total contracts: {total_stats['total_contracts']:,}")
print(f"Total Chinese detected: {total_stats['total_chinese']}")
print(f"Total errors: {total_stats['total_errors']}")

# Save detailed stats
stats_file = Path("C:/Projects/OSINT - Foresight/data/ted_legacy_processing_stats.json")
with open(stats_file, 'w') as f:
    json.dump(total_stats, f, indent=2)

print(f"\nDetailed stats saved to: {stats_file}")
print("="*80)
