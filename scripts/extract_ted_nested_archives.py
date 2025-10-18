#!/usr/bin/env python3
"""
Extract Double-Wrapped TED Archives
Handles the nested tar.gz structure: outer.tar.gz -> inner.tar.gz -> CSV files
"""

import os
import tarfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TEDExtractor:
    """Extract nested TED tar.gz archives to CSV files"""
    
    def __init__(self):
        self.ted_dir = Path("F:/TED_Data/monthly")
        self.output_dir = Path("F:/TED_Data/extracted_csv")
        self.temp_dir = Path("F:/TED_Data/temp_extraction")
        self.checkpoint_file = Path("C:/Projects/OSINT - Foresight/data/ted_extraction_checkpoint.json")
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
        # Load checkpoint
        self.checkpoint = self.load_checkpoint()
        
    def load_checkpoint(self):
        """Load extraction checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {
            'processed_files': [],
            'extracted_count': 0,
            'total_size_mb': 0,
            'errors': []
        }
    
    def save_checkpoint(self):
        """Save extraction checkpoint"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)
    
    def extract_nested_archive(self, archive_path: Path) -> int:
        """Extract a double-wrapped TED archive
        Returns number of CSV files extracted"""
        
        csv_count = 0
        year = archive_path.parent.name
        month = archive_path.stem.split('_')[-1]  # e.g., '2024_01' -> '01'
        
        # Create output directory for this month
        month_output = self.output_dir / year / month
        month_output.mkdir(exist_ok=True, parents=True)
        
        logging.info(f"Processing {archive_path.name}...")
        
        try:
            # Step 1: Extract outer archive to temp directory
            outer_temp = self.temp_dir / f"outer_{year}_{month}"
            outer_temp.mkdir(exist_ok=True)
            
            with tarfile.open(archive_path, 'r:gz') as outer_tar:
                logging.info(f"  Extracting outer archive...")
                outer_tar.extractall(outer_temp)
                
                # Step 2: Find and extract inner archives
                inner_archives = list(outer_temp.rglob("*.tar.gz"))
                logging.info(f"  Found {len(inner_archives)} inner archives")
                
                for inner_archive in inner_archives:
                    try:
                        with tarfile.open(inner_archive, 'r:gz') as inner_tar:
                            # Extract CSV or XML files
                            for member in inner_tar.getmembers():
                                if member.name.endswith(('.csv', '.xml', '.CSV', '.XML')):
                                    # Extract to final destination
                                    inner_tar.extract(member, month_output)
                                    csv_count += 1
                                    
                                    # Get file size
                                    extracted_file = month_output / member.name
                                    if extracted_file.exists():
                                        size_mb = extracted_file.stat().st_size / (1024 * 1024)
                                        self.checkpoint['total_size_mb'] += size_mb
                    
                    except Exception as e:
                        logging.error(f"    Error extracting inner archive {inner_archive.name}: {e}")
                        self.checkpoint['errors'].append({
                            'file': str(inner_archive),
                            'error': str(e)
                        })
            
            # Clean up temp directory
            shutil.rmtree(outer_temp, ignore_errors=True)
            
            logging.info(f"  Extracted {csv_count} CSV files to {month_output}")
            
        except Exception as e:
            logging.error(f"Error processing {archive_path.name}: {e}")
            self.checkpoint['errors'].append({
                'file': str(archive_path),
                'error': str(e)
            })
        
        return csv_count
    
    def extract_all(self, years: list = None):
        """Extract all TED archives for specified years"""
        
        if years is None:
            # Default to recent years
            years = ['2020', '2021', '2022', '2023', '2024']
        
        logging.info("="*60)
        logging.info("TED NESTED ARCHIVE EXTRACTION")
        logging.info("="*60)
        logging.info(f"Processing years: {', '.join(years)}")
        logging.info(f"Output directory: {self.output_dir}")
        
        total_archives = 0
        total_csv = 0
        
        for year in years:
            year_dir = self.ted_dir / year
            if not year_dir.exists():
                logging.warning(f"Year directory {year} not found")
                continue
            
            # Find all tar.gz files for this year
            archives = list(year_dir.glob("*.tar.gz"))
            logging.info(f"\nYear {year}: {len(archives)} archives found")
            
            for archive in archives:
                # Skip if already processed
                if str(archive) in self.checkpoint['processed_files']:
                    logging.info(f"  Skipping {archive.name} (already processed)")
                    continue
                
                # Extract this archive
                csv_count = self.extract_nested_archive(archive)
                total_csv += csv_count
                total_archives += 1
                
                # Update checkpoint
                self.checkpoint['processed_files'].append(str(archive))
                self.checkpoint['extracted_count'] += csv_count
                self.save_checkpoint()
                
                # Progress update
                logging.info(f"  Progress: {total_archives} archives, {total_csv} CSV files extracted")
        
        logging.info("\n" + "="*60)
        logging.info("EXTRACTION COMPLETE")
        logging.info("="*60)
        logging.info(f"Total archives processed: {total_archives}")
        logging.info(f"Total CSV files extracted: {self.checkpoint['extracted_count']}")
        logging.info(f"Total size: {self.checkpoint['total_size_mb']:.2f} MB")
        
        if self.checkpoint['errors']:
            logging.warning(f"Errors encountered: {len(self.checkpoint['errors'])}")
            for error in self.checkpoint['errors'][:5]:
                logging.warning(f"  - {error['file']}: {error['error']}")
        
        return self.checkpoint
    
    def verify_extraction(self):
        """Verify that extraction was successful"""
        logging.info("\nVerifying extraction...")
        
        csv_files = list(self.output_dir.rglob("*.csv"))
        logging.info(f"Total CSV files in output directory: {len(csv_files)}")
        
        # Check file sizes
        total_size = sum(f.stat().st_size for f in csv_files) / (1024**3)  # GB
        logging.info(f"Total size of extracted CSV files: {total_size:.2f} GB")
        
        # Sample some files to check structure
        if csv_files:
            import csv
            sample_file = csv_files[0]
            logging.info(f"\nSample CSV file: {sample_file.name}")
            
            try:
                with open(sample_file, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.reader(f)
                    headers = next(reader)
                    logging.info(f"Headers: {headers[:5]}...")  # Show first 5 headers
                    
                    # Count rows
                    row_count = sum(1 for _ in reader)
                    logging.info(f"Rows in sample file: {row_count:,}")
            except Exception as e:
                logging.error(f"Error reading sample CSV: {e}")


def main():
    """Main execution"""
    extractor = TEDExtractor()
    
    print("""
    ========================================
    TED NESTED ARCHIVE EXTRACTION
    ========================================
    
    This will extract double-wrapped TED archives:
    - Outer tar.gz -> Inner tar.gz -> CSV files
    - Default: Years 2020-2024
    - Output: F:/TED_Data/extracted_csv/
    
    Press Enter to start extraction...
    """)
    input()
    
    # Extract archives
    results = extractor.extract_all()
    
    # Verify extraction
    extractor.verify_extraction()
    
    print(f"\nExtraction complete! Check {extractor.output_dir} for CSV files.")
    print(f"Checkpoint saved to {extractor.checkpoint_file}")

if __name__ == "__main__":
    main()
