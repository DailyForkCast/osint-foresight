#!/usr/bin/env python3
"""
Second-Level Decompression: Extract nested .gz files within decompressed archives
Handles the 74 .gz files found in F:/DECOMPRESSED_DATA/
"""

import gzip
import json
import shutil
from pathlib import Path
from datetime import datetime
import sys

class SecondLevelDecompressor:
    def __init__(self):
        self.source_root = Path("F:/DECOMPRESSED_DATA")
        self.stats = {
            'started': datetime.now().isoformat(),
            'gz_files_found': 0,
            'successfully_decompressed': 0,
            'failed': 0,
            'total_bytes_decompressed': 0,
            'files_by_location': {}
        }

    def find_gz_files(self):
        """Find all .gz files in decompressed directory"""
        print("\nSearching for nested .gz files...")

        gz_files = []
        for gz_file in self.source_root.rglob('*.gz'):
            gz_files.append(gz_file)

            # Track by location
            location = gz_file.parent.name
            if location not in self.stats['files_by_location']:
                self.stats['files_by_location'][location] = {
                    'count': 0,
                    'decompressed': 0,
                    'failed': 0
                }
            self.stats['files_by_location'][location]['count'] += 1

        self.stats['gz_files_found'] = len(gz_files)
        print(f"Found {len(gz_files)} .gz files to decompress")

        return gz_files

    def decompress_file(self, gz_path):
        """Decompress a single .gz file"""
        try:
            # Determine output path (remove .gz extension)
            output_path = gz_path.with_suffix('')

            # If output already exists, add a suffix
            if output_path.exists():
                base = output_path.stem
                suffix = output_path.suffix if output_path.suffix else '.dat'
                output_path = output_path.parent / f"{base}_decompressed{suffix}"

            # Decompress
            with gzip.open(gz_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Get sizes
            input_size = gz_path.stat().st_size
            output_size = output_path.stat().st_size

            # Update stats
            location = gz_path.parent.name
            self.stats['files_by_location'][location]['decompressed'] += 1
            self.stats['total_bytes_decompressed'] += output_size

            # Remove original .gz file to save space
            gz_path.unlink()

            return True, output_size, str(output_path)

        except Exception as e:
            print(f"  Error decompressing {gz_path.name}: {str(e)[:100]}")
            location = gz_path.parent.name
            self.stats['files_by_location'][location]['failed'] += 1
            return False, 0, None

    def run(self):
        """Execute second-level decompression"""
        print("\n" + "="*70)
        print("SECOND-LEVEL DECOMPRESSION")
        print("="*70)
        print(f"\nSource: {self.source_root}")

        # Find all .gz files
        gz_files = self.find_gz_files()

        if not gz_files:
            print("No .gz files found for second-level decompression")
            return 0

        print(f"\nDecompressing {len(gz_files)} files...")

        # Process each file
        for i, gz_file in enumerate(gz_files, 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(gz_files)} files...")

            success, size, output_path = self.decompress_file(gz_file)

            if success:
                self.stats['successfully_decompressed'] += 1
                print(f"  [{i}/{len(gz_files)}] Decompressed: {gz_file.name} -> {size/1e6:.1f} MB")
            else:
                self.stats['failed'] += 1

        # Calculate final stats
        self.stats['completed'] = datetime.now().isoformat()

        # Save stats
        self.save_stats()

        # Print summary
        print("\n" + "="*70)
        print("DECOMPRESSION COMPLETE")
        print("="*70)
        print(f"\nResults:")
        print(f"  Files found: {self.stats['gz_files_found']}")
        print(f"  Successfully decompressed: {self.stats['successfully_decompressed']}")
        print(f"  Failed: {self.stats['failed']}")
        print(f"  Total decompressed: {self.stats['total_bytes_decompressed']/1e9:.2f} GB")

        print("\nBy location:")
        for location, counts in self.stats['files_by_location'].items():
            print(f"  {location}: {counts['decompressed']}/{counts['count']} decompressed")

        return 0

    def save_stats(self):
        """Save decompression statistics"""
        stats_file = Path("C:/Projects/OSINT - Foresight/second_level_decompression_stats.json")

        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

        print(f"\nStats saved to: {stats_file}")


if __name__ == "__main__":
    decompressor = SecondLevelDecompressor()
    sys.exit(decompressor.run())
