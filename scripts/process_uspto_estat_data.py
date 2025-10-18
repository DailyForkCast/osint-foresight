#!/usr/bin/env python3
"""
USPTO and ESTAT Data Processing Pipeline
Handles decompression, processing, and preparation for SQL import
"""

import os
import json
import gzip
import zipfile
import tarfile
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import hashlib
import shutil
import concurrent.futures
from typing import Dict, List, Tuple, Optional

class DataProcessor:
    def __init__(self):
        self.base_dir = Path("C:/Projects/OSINT - Foresight")
        self.uspto_dir = Path("F:/USPTO Data")
        self.estat_dir = Path("F:/ESTAT")
        self.output_dir = Path("F:/DECOMPRESSED_DATA")
        self.processed_dir = Path("F:/PROCESSED_DATA")

        # Create output directories
        self.uspto_output = self.output_dir / "uspto_data"
        self.estat_output = self.output_dir / "estat_data"
        self.uspto_output.mkdir(parents=True, exist_ok=True)
        self.estat_output.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.setup_logging()

        # Track progress
        self.progress_file = self.base_dir / "data" / "processing_progress.json"
        self.load_progress()

    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = self.base_dir / "logs"
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"data_processing_{datetime.now():%Y%m%d_%H%M%S}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_progress(self):
        """Load previous processing progress"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                'uspto': {'processed': [], 'failed': [], 'stats': {}},
                'estat': {'processed': [], 'failed': [], 'stats': {}},
                'last_update': None
            }

    def save_progress(self):
        """Save processing progress"""
        self.progress['last_update'] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def get_file_hash(self, filepath: Path) -> str:
        """Calculate file hash for deduplication"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def decompress_file(self, filepath: Path, output_dir: Path) -> Tuple[bool, str, List[Path]]:
        """Decompress a single file and return extracted files"""
        extracted_files = []

        try:
            if filepath.suffix.lower() == '.zip':
                return self.decompress_zip(filepath, output_dir)
            elif filepath.suffix.lower() == '.gz':
                return self.decompress_gz(filepath, output_dir)
            elif filepath.suffix.lower() in ['.tar', '.tgz']:
                return self.decompress_tar(filepath, output_dir)
            else:
                return False, f"Unsupported format: {filepath.suffix}", []

        except Exception as e:
            self.logger.error(f"Failed to decompress {filepath}: {e}")
            return False, str(e), []

    def decompress_zip(self, filepath: Path, output_dir: Path) -> Tuple[bool, str, List[Path]]:
        """Decompress ZIP file"""
        extracted_files = []

        try:
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                # Create subdirectory for this archive
                archive_dir = output_dir / filepath.stem
                archive_dir.mkdir(parents=True, exist_ok=True)

                # Extract all files
                for member in zip_ref.namelist():
                    zip_ref.extract(member, archive_dir)
                    extracted_files.append(archive_dir / member)

            self.logger.info(f"Extracted {len(extracted_files)} files from {filepath.name}")
            return True, f"Extracted {len(extracted_files)} files", extracted_files

        except Exception as e:
            return False, str(e), []

    def decompress_gz(self, filepath: Path, output_dir: Path) -> Tuple[bool, str, List[Path]]:
        """Decompress GZ file"""
        try:
            output_file = output_dir / filepath.stem

            with gzip.open(filepath, 'rb') as gz_file:
                with open(output_file, 'wb') as out_file:
                    shutil.copyfileobj(gz_file, out_file)

            self.logger.info(f"Decompressed {filepath.name} to {output_file.name}")
            return True, "Successfully decompressed", [output_file]

        except Exception as e:
            return False, str(e), []

    def decompress_tar(self, filepath: Path, output_dir: Path) -> Tuple[bool, str, List[Path]]:
        """Decompress TAR file"""
        extracted_files = []

        try:
            archive_dir = output_dir / filepath.stem
            archive_dir.mkdir(parents=True, exist_ok=True)

            with tarfile.open(filepath, 'r:*') as tar:
                tar.extractall(archive_dir)
                for member in tar.getmembers():
                    if member.isfile():
                        extracted_files.append(archive_dir / member.name)

            self.logger.info(f"Extracted {len(extracted_files)} files from {filepath.name}")
            return True, f"Extracted {len(extracted_files)} files", extracted_files

        except Exception as e:
            return False, str(e), []

    def process_uspto_data(self):
        """Process all USPTO data files"""
        self.logger.info("Starting USPTO data processing")

        uspto_files = list(self.uspto_dir.glob("*.zip")) + list(self.uspto_dir.glob("*.ZIP"))
        self.logger.info(f"Found {len(uspto_files)} USPTO files to process")

        for file in uspto_files:
            if file.name in self.progress['uspto']['processed']:
                self.logger.info(f"Skipping already processed: {file.name}")
                continue

            self.logger.info(f"Processing {file.name} ({file.stat().st_size / 1e9:.2f} GB)")

            success, msg, extracted = self.decompress_file(file, self.uspto_output)

            if success:
                self.progress['uspto']['processed'].append(file.name)
                self.progress['uspto']['stats'][file.name] = {
                    'size': file.stat().st_size,
                    'extracted_files': len(extracted),
                    'message': msg,
                    'timestamp': datetime.now().isoformat()
                }

                # Process extracted files if they're CSV or TSV
                for extracted_file in extracted:
                    if extracted_file.suffix.lower() in ['.csv', '.tsv', '.txt']:
                        self.prepare_for_sql(extracted_file, 'uspto')
            else:
                self.progress['uspto']['failed'].append({
                    'file': file.name,
                    'error': msg,
                    'timestamp': datetime.now().isoformat()
                })

            self.save_progress()

    def process_estat_data(self):
        """Process all ESTAT data files"""
        self.logger.info("Starting ESTAT data processing")

        estat_files = list(self.estat_dir.glob("*.gz")) + list(self.estat_dir.glob("*.xml"))
        self.logger.info(f"Found {len(estat_files)} ESTAT files to process")

        for file in estat_files:
            if file.name in self.progress['estat']['processed']:
                self.logger.info(f"Skipping already processed: {file.name}")
                continue

            self.logger.info(f"Processing {file.name}")

            if file.suffix.lower() == '.gz':
                success, msg, extracted = self.decompress_file(file, self.estat_output)

                if success:
                    self.progress['estat']['processed'].append(file.name)
                    self.progress['estat']['stats'][file.name] = {
                        'size': file.stat().st_size,
                        'extracted_files': len(extracted),
                        'message': msg,
                        'timestamp': datetime.now().isoformat()
                    }

                    # Process TSV files
                    for extracted_file in extracted:
                        if extracted_file.suffix.lower() == '.tsv':
                            self.prepare_for_sql(extracted_file, 'estat')
                else:
                    self.progress['estat']['failed'].append({
                        'file': file.name,
                        'error': msg,
                        'timestamp': datetime.now().isoformat()
                    })

            elif file.suffix.lower() == '.xml':
                # Copy XML files for later processing
                shutil.copy2(file, self.estat_output)
                self.progress['estat']['processed'].append(file.name)

            self.save_progress()

    def prepare_for_sql(self, filepath: Path, source: str):
        """Prepare data file for SQL import"""
        try:
            # Create SQL-ready directory
            sql_ready_dir = self.processed_dir / f"{source}_sql_ready"
            sql_ready_dir.mkdir(exist_ok=True)

            # Get file info
            file_info = {
                'original_file': filepath.name,
                'source': source,
                'size': filepath.stat().st_size,
                'rows': 0,
                'columns': [],
                'sample_data': []
            }

            # Read first few lines to understand structure
            if filepath.suffix.lower() in ['.csv', '.tsv', '.txt']:
                delimiter = '\t' if filepath.suffix.lower() == '.tsv' else ','

                try:
                    # Read header and sample
                    df_sample = pd.read_csv(filepath, delimiter=delimiter, nrows=5, on_bad_lines='skip')

                    file_info['columns'] = list(df_sample.columns)
                    file_info['sample_data'] = df_sample.to_dict('records')

                    # Count total rows (memory-efficient)
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        file_info['rows'] = sum(1 for line in f) - 1  # Subtract header

                    # Create metadata file
                    metadata_file = sql_ready_dir / f"{filepath.stem}_metadata.json"
                    with open(metadata_file, 'w') as f:
                        json.dump(file_info, f, indent=2)

                    self.logger.info(f"Prepared {filepath.name} for SQL import: {file_info['rows']} rows, {len(file_info['columns'])} columns")

                except Exception as e:
                    self.logger.error(f"Error reading {filepath}: {e}")

        except Exception as e:
            self.logger.error(f"Error preparing {filepath} for SQL: {e}")

    def generate_summary(self):
        """Generate processing summary"""
        summary = {
            'processing_time': datetime.now().isoformat(),
            'uspto': {
                'total_files': len(list(self.uspto_dir.glob("*.zip")) + list(self.uspto_dir.glob("*.ZIP"))),
                'processed': len(self.progress['uspto']['processed']),
                'failed': len(self.progress['uspto']['failed']),
                'total_size_gb': sum(s['size'] for s in self.progress['uspto']['stats'].values()) / 1e9
            },
            'estat': {
                'total_files': len(list(self.estat_dir.glob("*.gz")) + list(self.estat_dir.glob("*.xml"))),
                'processed': len(self.progress['estat']['processed']),
                'failed': len(self.progress['estat']['failed']),
                'total_size_mb': sum(s.get('size', 0) for s in self.progress['estat']['stats'].values()) / 1e6
            }
        }

        # Save summary
        summary_file = self.base_dir / "data" / "processing_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        # Print summary
        print("\n" + "="*60)
        print("DATA PROCESSING SUMMARY")
        print("="*60)
        print(f"\nUSPTO Data:")
        print(f"  Total files: {summary['uspto']['total_files']}")
        print(f"  Processed: {summary['uspto']['processed']}")
        print(f"  Failed: {summary['uspto']['failed']}")
        print(f"  Total size: {summary['uspto']['total_size_gb']:.2f} GB")

        print(f"\nESTAT Data:")
        print(f"  Total files: {summary['estat']['total_files']}")
        print(f"  Processed: {summary['estat']['processed']}")
        print(f"  Failed: {summary['estat']['failed']}")
        print(f"  Total size: {summary['estat']['total_size_mb']:.2f} MB")

        return summary

    def run(self):
        """Run the complete processing pipeline"""
        self.logger.info("Starting data processing pipeline")

        # Process USPTO data
        self.process_uspto_data()

        # Process ESTAT data
        self.process_estat_data()

        # Generate summary
        summary = self.generate_summary()

        self.logger.info("Data processing complete")
        return summary


if __name__ == "__main__":
    processor = DataProcessor()
    processor.run()
