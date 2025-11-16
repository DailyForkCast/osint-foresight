#!/usr/bin/env python3
"""
Production runner for 101-column USAspending files.

Processes both 101-column files (26.7 GB total):
- 5847.dat.gz (14.5 GB)
- 5836.dat.gz (12.2 GB)

Output: F:/OSINT_WAREHOUSE/osint_master.db (table: usaspending_china_101)
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from process_usaspending_101_column import USAspending101Processor

def main():
    """Run production processing on both 101-column files."""

    print("="*80)
    print("USAspending 101-Column PRODUCTION RUN")
    print("="*80)
    print("\nTarget files:")
    print("  1. 5847.dat.gz (14.5 GB)")
    print("  2. 5836.dat.gz (12.2 GB)")
    print("\nTotal: 26.7 GB")
    print("="*80)

    # Initialize processor
    processor = USAspending101Processor()

    # Define files to process
    data_dir = Path("F:/OSINT_DATA/USAspending/extracted_data")
    files = [
        data_dir / "5847.dat.gz",  # 14.5 GB
        data_dir / "5836.dat.gz",  # 12.2 GB
    ]

    # Process each file
    for file_path in files:
        if not file_path.exists():
            print(f"\nERROR: File not found: {file_path}")
            continue

        print(f"\n{'='*80}")
        print(f"Starting: {file_path.name}")
        print(f"{'='*80}")

        try:
            # Process full file (no max_records limit)
            total_detections = processor.process_file(file_path)
            processor.stats['files_processed'] += 1

            print(f"\n✓ Completed: {file_path.name}")
            print(f"  Detections: {total_detections:,}")

        except Exception as e:
            print(f"\n✗ ERROR processing {file_path.name}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Print final summary
    print(f"\n{'='*80}")
    print("PRODUCTION RUN COMPLETE")
    print(f"{'='*80}")
    processor.print_summary()

    # Save checkpoint
    import json
    from datetime import datetime

    checkpoint = {
        'completion_date': datetime.now().isoformat(),
        'files_processed': processor.stats['files_processed'],
        'total_records': processor.stats['total_records'],
        'total_detections': processor.stats['china_detected'],
        'total_value': processor.stats['total_value'],
        'detection_rate': processor.stats['china_detected'] / max(processor.stats['total_records'], 1),
        'format': '101-column',
        'note': 'Taiwan (ROC) excluded from China (PRC) detection. Award amounts from field 29.',
    }

    checkpoint_path = processor.output_dir / "checkpoint.json"
    with open(checkpoint_path, 'w') as f:
        json.dump(checkpoint, f, indent=2)

    print(f"\nCheckpoint saved: {checkpoint_path}")
    print(f"Database table: usaspending_china_101")
    print(f"Location: F:/OSINT_WAREHOUSE/osint_master.db")


if __name__ == '__main__':
    main()
