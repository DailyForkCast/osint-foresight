#!/usr/bin/env python3
"""
Enhanced Overnight Decompression with Progress Tracking
Processes 64 GB of compressed USASpending data
"""

import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import time
import json

class OvernightDecompressor:
    def __init__(self):
        self.large_files = [
            "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5801.dat.gz",
            "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5836.dat.gz",
            "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5847.dat.gz",
            "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5848.dat.gz",
            "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5862.dat.gz"
        ]

        self.status = {
            'start_time': None,
            'end_time': None,
            'files_processed': [],
            'total_compressed_size': 0,
            'total_decompressed_size': 0,
            'errors': [],
            'china_patterns_found': 0
        }

        self.china_keywords = ['china', 'chinese', 'beijing', 'shanghai', 'huawei', 'zte']

    def calculate_total_size(self):
        """Calculate total size of files to process"""
        total = 0
        for file_path in self.large_files:
            gz_file = Path(file_path)
            if gz_file.exists():
                size_gb = gz_file.stat().st_size / 1e9
                total += size_gb
                print(f"  {gz_file.name}: {size_gb:.2f} GB")
        self.status['total_compressed_size'] = total
        return total

    def scan_for_china_patterns(self, file_path, sample_lines=1000):
        """Quick scan for China patterns in first N lines"""
        china_count = 0
        try:
            with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f):
                    if i >= sample_lines:
                        break

                    line_lower = line.lower()
                    for keyword in self.china_keywords:
                        if keyword in line_lower:
                            china_count += 1
                            break
        except Exception as e:
            print(f"    Warning: Could not scan for patterns: {str(e)[:50]}")

        return china_count

    def decompress_file(self, file_path):
        """Decompress a single file with progress tracking"""
        gz_file = Path(file_path)

        if not gz_file.exists():
            print(f"  File not found: {gz_file.name}")
            self.status['errors'].append(f"Not found: {gz_file.name}")
            return False

        output = gz_file.with_suffix('')
        compressed_size = gz_file.stat().st_size

        print(f"\nProcessing: {gz_file.name}")
        print(f"  Compressed size: {compressed_size / 1e9:.2f} GB")

        # Quick China pattern scan
        print("  Scanning for China patterns...")
        patterns = self.scan_for_china_patterns(gz_file)
        if patterns > 0:
            print(f"  [ALERT] Found {patterns} China patterns in sample!")
            self.status['china_patterns_found'] += patterns

        # Decompress
        start = time.time()
        print(f"  Decompressing to {output.name}...")

        try:
            bytes_processed = 0
            chunk_size = 10 * 1024 * 1024  # 10MB chunks

            with gzip.open(gz_file, 'rb') as f_in:
                with open(output, 'wb') as f_out:
                    while True:
                        chunk = f_in.read(chunk_size)
                        if not chunk:
                            break
                        f_out.write(chunk)
                        bytes_processed += len(chunk)

                        # Progress indicator every 500MB
                        if bytes_processed % (500 * 1024 * 1024) == 0:
                            progress_gb = bytes_processed / 1e9
                            elapsed = time.time() - start
                            rate = progress_gb / elapsed if elapsed > 0 else 0
                            print(f"    Progress: {progress_gb:.1f} GB @ {rate:.1f} GB/s")

            # Get final size
            decompressed_size = output.stat().st_size
            elapsed = time.time() - start

            print(f"  Decompressed size: {decompressed_size / 1e9:.2f} GB")
            print(f"  Compression ratio: {decompressed_size / compressed_size:.1f}x")
            print(f"  Time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
            print(f"  Rate: {compressed_size / elapsed / 1e6:.1f} MB/s")

            # Update status
            self.status['files_processed'].append({
                'file': gz_file.name,
                'compressed_gb': compressed_size / 1e9,
                'decompressed_gb': decompressed_size / 1e9,
                'time_seconds': elapsed,
                'china_patterns': patterns
            })
            self.status['total_decompressed_size'] += decompressed_size / 1e9

            # Remove original to save space
            print(f"  Removing original compressed file...")
            gz_file.unlink()

            return True

        except Exception as e:
            print(f"  ERROR: {str(e)}")
            self.status['errors'].append(f"Failed {gz_file.name}: {str(e)[:100]}")
            return False

    def run(self):
        """Execute the overnight decompression"""
        print("="*70)
        print("OVERNIGHT DECOMPRESSION - USASpending Large Files")
        print("="*70)

        self.status['start_time'] = datetime.now().isoformat()
        print(f"\nStart time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Calculate total size
        print(f"\nFiles to process:")
        total_gb = self.calculate_total_size()
        print(f"\nTotal compressed size: {total_gb:.2f} GB")
        print(f"Estimated decompressed size: ~{total_gb * 3:.0f} GB")
        print(f"Estimated time: 8-12 hours")

        print("\n" + "-"*70)

        # Process each file
        for i, file_path in enumerate(self.large_files, 1):
            print(f"\n[File {i}/{len(self.large_files)}]")
            self.decompress_file(file_path)

            # Estimate remaining time
            if self.status['files_processed']:
                avg_time = sum(f['time_seconds'] for f in self.status['files_processed']) / len(self.status['files_processed'])
                remaining = len(self.large_files) - i
                est_remaining = avg_time * remaining / 60
                print(f"\nEstimated time remaining: {est_remaining:.0f} minutes")

        # Final summary
        self.status['end_time'] = datetime.now().isoformat()

        print("\n" + "="*70)
        print("DECOMPRESSION COMPLETE")
        print("="*70)

        print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if self.status['start_time']:
            start = datetime.fromisoformat(self.status['start_time'])
            elapsed = datetime.now() - start
            print(f"Total time: {elapsed}")

        print(f"\nSummary:")
        print(f"  Files processed: {len(self.status['files_processed'])}/{len(self.large_files)}")
        print(f"  Total decompressed: {self.status['total_decompressed_size']:.2f} GB")
        print(f"  China patterns found: {self.status['china_patterns_found']}")

        if self.status['errors']:
            print(f"\nErrors encountered:")
            for error in self.status['errors']:
                print(f"  - {error}")

        # Save status
        status_file = Path("C:/Projects/OSINT - Foresight/overnight_status.json")
        with open(status_file, 'w') as f:
            json.dump(self.status, f, indent=2)
        print(f"\nStatus saved to: {status_file}")

        # China alert
        if self.status['china_patterns_found'] > 0:
            print("\n" + "!"*70)
            print(f"ALERT: {self.status['china_patterns_found']} China patterns detected!")
            print("Run china_pattern_dashboard.py for detailed analysis")
            print("!"*70)


if __name__ == "__main__":
    decompressor = OvernightDecompressor()
    decompressor.run()
