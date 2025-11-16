#!/usr/bin/env python3
"""
Production runner for 374-column USAspending files.

Processes files 5877.dat.gz and 5878.dat.gz (100GB total, 46% of dataset).

Features:
- Checkpoint/resume capability
- Progress tracking
- Error handling
- Database integration
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))
from process_usaspending_374_column import USAspending374Processor

def load_checkpoint(checkpoint_file):
    """Load checkpoint if exists."""
    if checkpoint_file.exists():
        with open(checkpoint_file, 'r') as f:
            return json.load(f)
    return None

def save_checkpoint(checkpoint_file, overall_stats):
    """Save checkpoint after each file."""
    checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
    with open(checkpoint_file, 'w') as f:
        json.dump(overall_stats, f, indent=2)

def main():
    """Run production processing for 374-column files."""

    print("="*80)
    print("TERMINAL C - 374-COLUMN PRODUCTION RUN")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Setup
    data_dir = Path("F:/OSINT_DATA/USAspending/extracted_data")
    checkpoint_file = Path("data/processed/usaspending_374_production/checkpoint.json")

    # Target files (374-column format)
    target_files = [
        "5877.dat.gz",  # ~50GB
        "5878.dat.gz",  # ~50GB
    ]

    # Load checkpoint
    checkpoint = load_checkpoint(checkpoint_file)
    if checkpoint:
        print(f"RESUMING from checkpoint")
        print(f"  Previously processed: {len(checkpoint['files'])} files")
        print(f"  Total detections so far: {checkpoint.get('total_detections', 0):,}")
        print()
        overall_stats = checkpoint
    else:
        print(f"STARTING fresh run")
        print()
        overall_stats = {
            'run_started': datetime.now().isoformat(),
            'files': [],
            'total_records': 0,
            'total_detections': 0,
            'total_value': 0.0,
            'format': '374-column',
        }

    # Get list of completed files
    completed_files = set(f['filename'] for f in overall_stats['files'] if f.get('status') == 'success')

    # Process each file
    processor = USAspending374Processor()

    for file_idx, filename in enumerate(target_files, 1):
        # Skip if already processed
        if filename in completed_files:
            print(f"\n[{file_idx}/{len(target_files)}] [SKIP] {filename} (already processed)")
            continue

        file_path = data_dir / filename

        if not file_path.exists():
            print(f"\n[{file_idx}/{len(target_files)}] [ERROR] {filename} not found")
            overall_stats['files'].append({
                'filename': filename,
                'status': 'file_not_found',
                'timestamp': datetime.now().isoformat(),
            })
            save_checkpoint(checkpoint_file, overall_stats)
            continue

        print(f"\n[{file_idx}/{len(target_files)}] Processing {filename}")
        print(f"Size: {file_path.stat().st_size / (1024**3):.1f} GB")

        try:
            start_time = time.time()

            # Process file (no max_records limit - process everything)
            # Note: New streaming version saves to database automatically
            total_detections = processor.process_file(file_path)

            elapsed = time.time() - start_time

            # Update overall stats
            file_stats = {
                'filename': filename,
                'records': processor.stats['total_records'],
                'detections': total_detections,
                'value': processor.stats['total_value'],
                'processing_time_seconds': elapsed,
                'detection_rate': total_detections / max(processor.stats['total_records'], 1) * 100,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
            }

            overall_stats['files'].append(file_stats)
            overall_stats['total_records'] += processor.stats['total_records']
            overall_stats['total_detections'] += total_detections
            overall_stats['total_value'] += file_stats['value']

            # Save checkpoint
            save_checkpoint(checkpoint_file, overall_stats)

            print(f"\n  File completed:")
            print(f"    Records: {processor.stats['total_records']:,}")
            print(f"    Detections: {total_detections:,} ({file_stats['detection_rate']:.3f}%)")
            print(f"    Value: ${file_stats['value']:,.2f}")
            print(f"    Time: {elapsed/60:.1f} minutes")
            print(f"    Rate: {processor.stats['total_records']/elapsed:,.0f} records/second")

        except Exception as e:
            print(f"\n  ERROR processing {filename}: {e}")
            overall_stats['files'].append({
                'filename': filename,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
            })
            save_checkpoint(checkpoint_file, overall_stats)
            continue

    # Final summary
    print("\n" + "="*80)
    print("TERMINAL C - 374-COLUMN PRODUCTION RUN COMPLETE")
    print("="*80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nFiles processed: {len([f for f in overall_stats['files'] if f['status'] == 'success'])}/{len(target_files)}")
    print(f"Total records: {overall_stats['total_records']:,}")
    print(f"Total detections: {overall_stats['total_detections']:,}")
    print(f"Overall detection rate: {overall_stats['total_detections']/max(overall_stats['total_records'], 1)*100:.3f}%")
    print(f"Total value: ${overall_stats['total_value']:,.2f}")

    if overall_stats.get('run_started'):
        run_duration = (datetime.now() - datetime.fromisoformat(overall_stats['run_started'])).total_seconds()
        print(f"Total runtime: {run_duration/3600:.1f} hours")

    print("\nFile breakdown:")
    for f in overall_stats['files']:
        if f['status'] == 'success':
            print(f"  {f['filename']}: {f['records']:,} records, {f['detections']:,} detections ({f['detection_rate']:.3f}%)")

    print("\nCheckpoint saved to:", checkpoint_file)
    print("Results saved to: F:/OSINT_WAREHOUSE/osint_master.db (table: usaspending_china_374)")
    print("="*80)


if __name__ == '__main__':
    main()
