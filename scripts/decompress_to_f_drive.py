#!/usr/bin/env python3
"""
DECOMPRESS ALL ARCHIVES TO F: DRIVE
Extracts 940 GB of compressed files for permanent storage and analysis
"""

import os
import json
import gzip
import zipfile
import tarfile
import shutil
from pathlib import Path
from datetime import datetime
import sys
import hashlib

class MassiveDecompressor:
    def __init__(self):
        # Target directory on F: drive
        self.target_base = Path("F:/DECOMPRESSED_DATA")
        self.target_base.mkdir(exist_ok=True)

        # Load emergency inventory to get all compressed files
        self.load_inventory()

        self.stats = {
            'started': datetime.now().isoformat(),
            'gz_files': 0,
            'gz_success': 0,
            'gz_failed': 0,
            'zip_files': 0,
            'zip_success': 0,
            'zip_failed': 0,
            'total_compressed_bytes': 0,
            'total_decompressed_bytes': 0,
            'files_created': 0,
            'errors': []
        }

    def load_inventory(self):
        """Load the emergency inventory with all compressed files"""
        inventory_path = Path("C:/Projects/OSINT - Foresight/emergency_inventory_manifest.json")

        with open(inventory_path, 'r', encoding='utf-8') as f:
            self.inventory = json.load(f)

        # Collect all compressed files
        self.compressed_files = []

        for location_name, location_data in self.inventory['datasets'].items():
            for file_info in location_data.get('files', []):
                ext = file_info.get('extension', '').lower()
                if ext in ['.gz', '.zip', '.tar', '.7z', '.bz2']:
                    file_info['location'] = location_name
                    self.compressed_files.append(file_info)

        print(f"Found {len(self.compressed_files)} compressed files to decompress")

        # Calculate total compressed size
        total_bytes = sum(f['size'] for f in self.compressed_files)
        print(f"Total compressed size: {total_bytes / 1e9:.2f} GB")

    def get_target_path(self, source_path, location):
        """Generate target path on F: drive maintaining structure"""
        source = Path(source_path)

        # Create subdirectory for each source location
        target_dir = self.target_base / location

        # Maintain directory structure
        if 'OSINT_DATA' in str(source):
            rel_path = source.relative_to(Path('F:/OSINT_DATA'))
            target_dir = target_dir / 'OSINT_DATA'
        elif 'TED_Data' in str(source):
            rel_path = source.relative_to(Path('F:/TED_Data'))
            target_dir = target_dir / 'TED_Data'
        elif 'OSINT_Backups' in str(source):
            rel_path = source.relative_to(Path('F:/OSINT_Backups'))
            target_dir = target_dir / 'OSINT_Backups'
        elif 'Horizons' in str(source):
            rel_path = source.name
            target_dir = target_dir / 'Horizons'
        else:
            rel_path = source.name

        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir / rel_path

    def decompress_gz(self, file_info):
        """Decompress a .gz file to F: drive"""
        source_path = Path(file_info['path'])

        if not source_path.exists():
            return False, "Source file not found"

        self.stats['gz_files'] += 1

        try:
            # Generate target path (remove .gz extension)
            target_path = self.get_target_path(source_path, file_info['location'])
            target_path = target_path.with_suffix('')  # Remove .gz

            print(f"  Decompressing: {source_path.name}")
            print(f"    To: {target_path}")

            # Decompress
            with gzip.open(source_path, 'rb') as gz_in:
                with open(target_path, 'wb') as f_out:
                    # Copy in chunks to handle large files
                    chunk_size = 1024 * 1024  # 1 MB chunks
                    bytes_written = 0

                    while True:
                        chunk = gz_in.read(chunk_size)
                        if not chunk:
                            break
                        f_out.write(chunk)
                        bytes_written += len(chunk)

                        # Progress indicator for large files
                        if bytes_written % (100 * 1024 * 1024) == 0:  # Every 100 MB
                            print(f"      Progress: {bytes_written / 1e9:.2f} GB")

            # Update statistics
            self.stats['gz_success'] += 1
            self.stats['total_compressed_bytes'] += file_info['size']
            self.stats['total_decompressed_bytes'] += bytes_written
            self.stats['files_created'] += 1

            print(f"    Success: {bytes_written / 1e6:.2f} MB decompressed")
            return True, target_path

        except Exception as e:
            self.stats['gz_failed'] += 1
            error_msg = f"Failed to decompress {source_path}: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"    ERROR: {str(e)}")
            return False, str(e)

    def decompress_zip(self, file_info):
        """Decompress a .zip file to F: drive"""
        source_path = Path(file_info['path'])

        if not source_path.exists():
            return False, "Source file not found"

        self.stats['zip_files'] += 1

        try:
            # Generate target directory
            target_dir = self.get_target_path(source_path, file_info['location'])
            target_dir = target_dir.with_suffix('')  # Remove .zip, create directory
            target_dir.mkdir(parents=True, exist_ok=True)

            print(f"  Extracting: {source_path.name}")
            print(f"    To: {target_dir}")

            # Extract all files
            with zipfile.ZipFile(source_path, 'r') as zip_file:
                # Get total uncompressed size
                total_size = sum(info.file_size for info in zip_file.infolist())
                print(f"    Total size: {total_size / 1e9:.2f} GB")

                # Extract all
                extracted_count = 0
                for member in zip_file.namelist():
                    zip_file.extract(member, target_dir)
                    extracted_count += 1

                    if extracted_count % 100 == 0:
                        print(f"      Extracted {extracted_count} files")

            # Update statistics
            self.stats['zip_success'] += 1
            self.stats['total_compressed_bytes'] += file_info['size']
            self.stats['total_decompressed_bytes'] += total_size
            self.stats['files_created'] += extracted_count

            print(f"    Success: {extracted_count} files extracted")
            return True, target_dir

        except Exception as e:
            self.stats['zip_failed'] += 1
            error_msg = f"Failed to extract {source_path}: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"    ERROR: {str(e)}")
            return False, str(e)

    def run(self):
        """Execute massive decompression to F: drive"""
        print("\n" + "="*70)
        print("DECOMPRESSING ALL ARCHIVES TO F: DRIVE")
        print("="*70)
        print(f"\nTarget directory: {self.target_base}")
        print(f"Files to process: {len(self.compressed_files)}")

        # Check F: drive space
        import shutil
        stat = shutil.disk_usage("F:/")
        free_gb = stat.free / 1e9
        print(f"\nF: drive free space: {free_gb:.2f} GB")

        if free_gb < 100:  # Need at least 100 GB free
            print("WARNING: Low disk space on F: drive!")
            response = input("Continue anyway? (yes/no): ")
            if response.lower() != 'yes':
                return 1

        # Process each compressed file
        for idx, file_info in enumerate(self.compressed_files, 1):
            print(f"\n[{idx}/{len(self.compressed_files)}] Processing...")

            ext = file_info.get('extension', '').lower()

            if ext == '.gz':
                success, result = self.decompress_gz(file_info)
            elif ext == '.zip':
                success, result = self.decompress_zip(file_info)
            else:
                print(f"  Skipping unsupported format: {ext}")
                continue

            # Progress report every 10 files
            if idx % 10 == 0:
                self.print_progress()

            # Check disk space periodically
            if idx % 50 == 0:
                stat = shutil.disk_usage("F:/")
                free_gb = stat.free / 1e9
                if free_gb < 10:
                    print("\n[CRITICAL] Less than 10 GB free on F: drive!")
                    print("Stopping decompression to prevent disk full.")
                    break

        # Final statistics
        self.save_results()
        self.print_final_report()

        return 0

    def print_progress(self):
        """Print progress statistics"""
        total = self.stats['gz_files'] + self.stats['zip_files']
        success = self.stats['gz_success'] + self.stats['zip_success']

        if total > 0:
            rate = success / total * 100
            print(f"\n--- Progress: {total} files, {rate:.1f}% success rate ---")
            print(f"Decompressed: {self.stats['total_decompressed_bytes'] / 1e9:.2f} GB")
            print(f"Files created: {self.stats['files_created']:,}")

    def print_final_report(self):
        """Print final decompression report"""
        print("\n" + "="*70)
        print("DECOMPRESSION COMPLETE")
        print("="*70)

        print(f"\n.gz files:")
        print(f"  Processed: {self.stats['gz_files']}")
        print(f"  Success: {self.stats['gz_success']}")
        print(f"  Failed: {self.stats['gz_failed']}")

        print(f"\n.zip files:")
        print(f"  Processed: {self.stats['zip_files']}")
        print(f"  Success: {self.stats['zip_success']}")
        print(f"  Failed: {self.stats['zip_failed']}")

        print(f"\nSpace Usage:")
        print(f"  Compressed size: {self.stats['total_compressed_bytes'] / 1e9:.2f} GB")
        print(f"  Decompressed size: {self.stats['total_decompressed_bytes'] / 1e9:.2f} GB")

        if self.stats['total_compressed_bytes'] > 0:
            ratio = self.stats['total_decompressed_bytes'] / self.stats['total_compressed_bytes']
            print(f"  Compression ratio: {ratio:.2f}x")

        print(f"\nFiles created: {self.stats['files_created']:,}")
        print(f"Target directory: {self.target_base}")

        if self.stats['errors']:
            print(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")

    def save_results(self):
        """Save decompression results"""
        self.stats['completed'] = datetime.now().isoformat()

        # Calculate duration
        start = datetime.fromisoformat(self.stats['started'])
        end = datetime.now()
        duration = (end - start).total_seconds()
        self.stats['duration_seconds'] = duration
        self.stats['duration_hours'] = duration / 3600

        # Save statistics
        stats_file = Path("C:/Projects/OSINT - Foresight/decompression_to_f_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, default=str)

        print(f"\nStatistics saved to: {stats_file}")

        # Generate detailed report
        report = "# Decompression to F: Drive Report\n\n"
        report += f"Started: {self.stats['started']}\n"
        report += f"Completed: {self.stats['completed']}\n"
        report += f"Duration: {self.stats['duration_hours']:.2f} hours\n\n"

        report += "## Results\n\n"
        report += f"- Target: {self.target_base}\n"
        report += f"- Files created: {self.stats['files_created']:,}\n"
        report += f"- Space used: {self.stats['total_decompressed_bytes'] / 1e9:.2f} GB\n\n"

        report += "## File Types\n\n"
        report += f"- .gz: {self.stats['gz_success']}/{self.stats['gz_files']} successful\n"
        report += f"- .zip: {self.stats['zip_success']}/{self.stats['zip_files']} successful\n\n"

        if self.stats['errors']:
            report += "## Errors\n\n"
            for error in self.stats['errors']:
                report += f"- {error}\n"

        report_file = Path("C:/Projects/OSINT - Foresight/decompression_to_f_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"Report saved to: {report_file}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("MASSIVE DECOMPRESSION OPERATION")
    print("="*70)
    print("\nThis will decompress ~940 GB of compressed files to F: drive")
    print("Estimated decompressed size: 2-3 TB")
    print("Estimated time: 2-4 hours")
    print("\nTarget: F:/DECOMPRESSED_DATA/")

    response = input("\nProceed with decompression? (yes/no): ")
    if response.lower() == 'yes':
        decompressor = MassiveDecompressor()
        sys.exit(decompressor.run())
    else:
        print("Decompression cancelled.")
        sys.exit(0)
