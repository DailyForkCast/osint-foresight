#!/usr/bin/env python3
"""
USAspending Production Full Run - All 74 Files

Process all 215 GB of USAspending data using validated detection logic.
Expected: 8-10 hours, 5k-10k detections, $100B-200B value.
"""

import gzip
import json
import time
from pathlib import Path
from datetime import datetime
from process_usaspending_comprehensive import USAspendingComprehensiveProcessor

def load_checkpoint(checkpoint_file):
    """Load checkpoint if exists."""
    if checkpoint_file.exists():
        with open(checkpoint_file, 'r') as f:
            return json.load(f)
    return None

def save_checkpoint(checkpoint_file, data):
    """Save checkpoint."""
    with open(checkpoint_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  [Checkpoint saved: {datetime.now().strftime('%H:%M:%S')}]")

def process_all_files():
    """Process all USAspending files with checkpoint support."""

    data_dir = Path("F:/OSINT_DATA/USAspending/extracted_data")
    output_dir = Path("data/processed/usaspending_production_full")
    output_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_file = output_dir / "checkpoint.json"

    # Get all files
    files = sorted(data_dir.glob("*.dat.gz"))

    print("="*80)
    print("USASPENDING PRODUCTION FULL RUN - TERMINAL C")
    print("="*80)
    print(f"Files to process: {len(files)}")
    print(f"Total size: {sum(f.stat().st_size for f in files) / (1024**3):.1f} GB")
    print(f"Output directory: {output_dir}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load checkpoint if exists
    checkpoint = load_checkpoint(checkpoint_file)
    if checkpoint:
        print(f"[CHECKPOINT] Resuming from checkpoint")
        print(f"  Files completed: {checkpoint['files_processed']}")
        print(f"  Detections so far: {checkpoint['total_detections']:,}")
        overall_stats = checkpoint
        completed_files = set(f['filename'] for f in checkpoint['files'] if f.get('status') == 'success')
        print(f"  Skipping {len(completed_files)} already-processed files")
    else:
        print("[NEW RUN] Starting fresh")
        completed_files = set()
        overall_stats = {
            'start_time': datetime.now().isoformat(),
            'files_processed': 0,
            'files_failed': 0,
            'total_records': 0,
            'total_detections': 0,
            'total_value': 0.0,
            'processing_times': [],
            'files': []
        }

    print("="*80)
    print()

    start_time = time.time()

    for file_idx, file_path in enumerate(files, 1):
        # Skip if already processed (checkpoint resume)
        if file_path.name in completed_files:
            print(f"\n[{file_idx}/{len(files)}] [SKIP] {file_path.name} (already processed)")
            continue

        file_start = time.time()

        print(f"\n[{file_idx}/{len(files)}] Processing: {file_path.name}")
        print(f"  Size: {file_path.stat().st_size / (1024**3):.2f} GB")

        try:
            # Create processor for this file
            processor = USAspendingComprehensiveProcessor()

            # Process file (no max_records limit for production)
            detections = processor.process_file(file_path)

            # Save results
            processor.save_results(detections, file_path.stem)

            # Update overall stats
            file_time = time.time() - file_start
            overall_stats['files_processed'] += 1
            overall_stats['total_records'] += processor.stats['total_records']
            overall_stats['total_detections'] += processor.stats['china_detected']
            overall_stats['total_value'] += processor.stats['total_value']
            overall_stats['processing_times'].append(file_time)

            overall_stats['files'].append({
                'filename': file_path.name,
                'records': processor.stats['total_records'],
                'detections': processor.stats['china_detected'],
                'value': processor.stats['total_value'],
                'processing_time_seconds': file_time,
                'status': 'success'
            })

            print(f"  [OK] Complete: {processor.stats['total_records']:,} records, "
                  f"{processor.stats['china_detected']} detections, "
                  f"${processor.stats['total_value']:,.0f}")
            print(f"  Time: {file_time/60:.1f} minutes")

            # Progress summary
            elapsed = time.time() - start_time
            avg_time = sum(overall_stats['processing_times']) / len(overall_stats['processing_times'])
            remaining_files = len(files) - file_idx
            estimated_remaining = avg_time * remaining_files

            print(f"\n  Progress: {file_idx}/{len(files)} files ({file_idx/len(files)*100:.1f}%)")
            print(f"  Elapsed: {elapsed/3600:.1f} hours")
            print(f"  Estimated remaining: {estimated_remaining/3600:.1f} hours")
            print(f"  Total so far: {overall_stats['total_detections']:,} detections, "
                  f"${overall_stats['total_value']:,.0f}")

            # Save checkpoint after each successful file
            save_checkpoint(checkpoint_file, overall_stats)

        except Exception as e:
            print(f"  [ERROR]: {str(e)}")
            overall_stats['files_failed'] += 1
            overall_stats['files'].append({
                'filename': file_path.name,
                'status': 'failed',
                'error': str(e)
            })
            continue

    # Final summary
    total_time = time.time() - start_time
    overall_stats['end_time'] = datetime.now().isoformat()
    overall_stats['total_processing_time_hours'] = total_time / 3600

    print("\n" + "="*80)
    print("PRODUCTION RUN COMPLETE")
    print("="*80)
    print(f"Files processed: {overall_stats['files_processed']}/{len(files)}")
    print(f"Files failed: {overall_stats['files_failed']}")
    print(f"Total records: {overall_stats['total_records']:,}")
    print(f"Total detections: {overall_stats['total_detections']:,} "
          f"({overall_stats['total_detections']/overall_stats['total_records']*100:.4f}%)")
    print(f"Total value: ${overall_stats['total_value']:,.2f}")
    print(f"Processing time: {total_time/3600:.2f} hours")
    print("="*80)

    # Save overall summary
    summary_file = output_dir / "PRODUCTION_RUN_SUMMARY.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(overall_stats, f, indent=2)

    print(f"\nSaved summary: {summary_file}")

    # Create human-readable report
    report_file = output_dir / "PRODUCTION_RUN_REPORT.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("USASPENDING PRODUCTION RUN - FINAL REPORT\n")
        f.write("="*80 + "\n\n")

        f.write(f"Start Time: {overall_stats['start_time']}\n")
        f.write(f"End Time: {overall_stats['end_time']}\n")
        f.write(f"Total Processing Time: {total_time/3600:.2f} hours\n\n")

        f.write(f"Files Processed: {overall_stats['files_processed']}/{len(files)}\n")
        f.write(f"Files Failed: {overall_stats['files_failed']}\n\n")

        f.write(f"Total Records Processed: {overall_stats['total_records']:,}\n")
        f.write(f"China-Related Detections: {overall_stats['total_detections']:,}\n")
        f.write(f"Detection Rate: {overall_stats['total_detections']/overall_stats['total_records']*100:.4f}%\n")
        f.write(f"Total Value: ${overall_stats['total_value']:,.2f}\n\n")

        f.write("="*80 + "\n")
        f.write("FILE-BY-FILE SUMMARY\n")
        f.write("="*80 + "\n\n")

        for file_info in overall_stats['files']:
            if file_info['status'] == 'success':
                f.write(f"{file_info['filename']}\n")
                f.write(f"  Records: {file_info['records']:,}\n")
                f.write(f"  Detections: {file_info['detections']:,}\n")
                f.write(f"  Value: ${file_info['value']:,.2f}\n")
                f.write(f"  Time: {file_info['processing_time_seconds']/60:.1f} min\n\n")
            else:
                f.write(f"{file_info['filename']}\n")
                f.write(f"  Status: FAILED\n")
                f.write(f"  Error: {file_info.get('error', 'Unknown')}\n\n")

    print(f"Saved report: {report_file}")
    print("\n[COMPLETE] PRODUCTION RUN COMPLETE")

if __name__ == '__main__':
    process_all_files()
