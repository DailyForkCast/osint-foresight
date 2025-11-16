#!/usr/bin/env python3
"""
Production runner for 305-column USAspending file.

Processes 5848.dat.gz (15.4 GB) with Taiwan exclusion.
Output: F:/OSINT_WAREHOUSE/osint_master.db (table: usaspending_china_305)
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from process_usaspending_305_column import USAspending305Processor


def main():
    """Run production processing on 305-column file."""

    print("="*80)
    print("USAspending 305-Column PRODUCTION RUN")
    print("="*80)
    print("\nTarget file:")
    print("  - 5848.dat.gz (15.4 GB)")
    print("\nDatabase: F:/OSINT_WAREHOUSE/osint_master.db")
    print("Table: usaspending_china_305")
    print("="*80)

    # Initialize processor
    processor = USAspending305Processor()

    # Define file to process
    data_file = Path("F:/OSINT_DATA/USAspending/extracted_data/5848.dat.gz")

    if not data_file.exists():
        print(f"\nERROR: File not found: {data_file}")
        return

    # Process full file (no max_records limit)
    try:
        total_detections = processor.process_file(data_file)
        processor.stats['files_processed'] += 1

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
            'format': '305-column',
            'note': 'Taiwan (ROC) excluded from China (PRC) detection. Includes Hong Kong detections.',
        }

        checkpoint_path = processor.output_dir / "checkpoint.json"
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        print(f"\nCheckpoint saved: {checkpoint_path}")
        print(f"Database: F:/OSINT_WAREHOUSE/osint_master.db")
        print(f"Table: usaspending_china_305")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
