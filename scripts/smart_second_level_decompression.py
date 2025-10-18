#!/usr/bin/env python3
"""
Smart Second-Level Decompression with progress tracking
Handles large .gz files efficiently
"""

import gzip
import json
import shutil
import os
from pathlib import Path
from datetime import datetime
import sys

class SmartDecompressor:
    def __init__(self):
        self.source_root = Path("F:/DECOMPRESSED_DATA")
        self.stats = {
            'started': datetime.now().isoformat(),
            'gz_files_found': 0,
            'successfully_decompressed': 0,
            'failed': 0,
            'skipped_large': 0,
            'total_bytes_decompressed': 0,
            'large_files': []
        }

    def find_and_categorize_gz_files(self):
        """Find and categorize .gz files by size"""
        print("\nScanning for .gz files...")

        small_files = []  # < 100MB
        medium_files = []  # 100MB - 1GB
        large_files = []   # > 1GB

        for gz_file in self.source_root.rglob('*.gz'):
            size = gz_file.stat().st_size

            if size < 100 * 1024 * 1024:  # < 100MB
                small_files.append((gz_file, size))
            elif size < 1024 * 1024 * 1024:  # < 1GB
                medium_files.append((gz_file, size))
            else:  # >= 1GB
                large_files.append((gz_file, size))

        self.stats['gz_files_found'] = len(small_files) + len(medium_files) + len(large_files)

        print(f"\nFound {self.stats['gz_files_found']} .gz files:")
        print(f"  Small (<100MB): {len(small_files)}")
        print(f"  Medium (100MB-1GB): {len(medium_files)}")
        print(f"  Large (>1GB): {len(large_files)}")

        if large_files:
            print("\nLarge files detected:")
            for f, size in large_files[:5]:
                print(f"  {f.name}: {size/1e9:.2f} GB")
                self.stats['large_files'].append({
                    'name': f.name,
                    'path': str(f),
                    'size_gb': round(size/1e9, 2)
                })

        return small_files, medium_files, large_files

    def decompress_file_with_progress(self, gz_path, size):
        """Decompress with progress indication"""
        try:
            output_path = gz_path.with_suffix('')

            # Handle existing files
            if output_path.exists():
                base = output_path.stem
                suffix = output_path.suffix if output_path.suffix else '.dat'
                output_path = output_path.parent / f"{base}_decompressed{suffix}"

            print(f"  Decompressing {gz_path.name} ({size/1e6:.1f} MB)...", end='')

            # Decompress
            with gzip.open(gz_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out, length=1024*1024)  # 1MB chunks

            output_size = output_path.stat().st_size
            self.stats['total_bytes_decompressed'] += output_size
            self.stats['successfully_decompressed'] += 1

            # Remove original to save space
            gz_path.unlink()

            print(f" Done! ({output_size/1e6:.1f} MB)")
            return True

        except Exception as e:
            print(f" Failed: {str(e)[:50]}")
            self.stats['failed'] += 1
            return False

    def run(self):
        """Execute smart decompression"""
        print("\n" + "="*70)
        print("SMART SECOND-LEVEL DECOMPRESSION")
        print("="*70)

        # Categorize files
        small, medium, large = self.find_and_categorize_gz_files()

        if not (small or medium or large):
            print("No .gz files found")
            return 0

        # Process small files first (quick wins)
        if small:
            print(f"\n[Phase 1/3] Processing {len(small)} small files...")
            for gz_file, size in small:
                self.decompress_file_with_progress(gz_file, size)

        # Process medium files
        if medium:
            print(f"\n[Phase 2/3] Processing {len(medium)} medium files...")
            for gz_file, size in medium:
                self.decompress_file_with_progress(gz_file, size)

        # Handle large files
        if large:
            print(f"\n[Phase 3/3] Large files (>1GB):")
            print("WARNING: Large files will take significant time to decompress")

            for gz_file, size in large:
                print(f"\nFile: {gz_file.name} ({size/1e9:.2f} GB)")
                response = input("Decompress this file? (y/n/skip all): ").lower()

                if response == 'skip all':
                    self.stats['skipped_large'] = len(large)
                    print(f"Skipping all {len(large)} large files")
                    break
                elif response == 'y':
                    print("Decompressing large file (this may take several minutes)...")
                    self.decompress_file_with_progress(gz_file, size)
                else:
                    self.stats['skipped_large'] += 1
                    print("Skipped")

        # Save statistics
        self.save_results()

        # Print summary
        print("\n" + "="*70)
        print("DECOMPRESSION COMPLETE")
        print("="*70)
        print(f"\nResults:")
        print(f"  Total files found: {self.stats['gz_files_found']}")
        print(f"  Successfully decompressed: {self.stats['successfully_decompressed']}")
        print(f"  Failed: {self.stats['failed']}")
        print(f"  Skipped (large): {self.stats['skipped_large']}")
        print(f"  Total decompressed: {self.stats['total_bytes_decompressed']/1e9:.2f} GB")

        return 0

    def save_results(self):
        """Save decompression results"""
        self.stats['completed'] = datetime.now().isoformat()

        with open("C:/Projects/OSINT - Foresight/smart_decompression_stats.json", 'w') as f:
            json.dump(self.stats, f, indent=2)

        print("\nStats saved to smart_decompression_stats.json")


if __name__ == "__main__":
    decompressor = SmartDecompressor()
    sys.exit(decompressor.run())
