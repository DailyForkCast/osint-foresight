#!/usr/bin/env python3
"""
Download Full OpenAlex Dataset
Downloads the complete OpenAlex data dump (~300GB compressed)
"""

import os
import requests
import json
import time
from pathlib import Path
from datetime import datetime
import hashlib
import logging
from urllib.parse import urlparse
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class OpenAlexDownloader:
    """Download full OpenAlex dataset"""
    
    def __init__(self):
        self.base_url = "https://openalex.s3.amazonaws.com/data"
        self.output_dir = Path("F:/OPENALEX_FULL")
        self.manifest_url = f"{self.base_url}/works/manifest"
        self.checkpoint_file = Path("C:/Projects/OSINT - Foresight/data/openalex_download_checkpoint.json")
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Load checkpoint
        self.checkpoint = self.load_checkpoint()
    
    def load_checkpoint(self):
        """Load download checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {
            'downloaded_files': [],
            'total_size_gb': 0,
            'last_update': None,
            'errors': []
        }
    
    def save_checkpoint(self):
        """Save download checkpoint"""
        self.checkpoint['last_update'] = datetime.now().isoformat()
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)
    
    def download_file_wget(self, url: str, output_path: Path, expected_size: int = None):
        """Download file using wget (more reliable for large files)"""
        
        # Use wget for better resume capability
        wget_cmd = [
            'wget',
            '-c',  # Continue partial downloads
            '--timeout=30',
            '--tries=5',
            '--progress=bar',
            url,
            '-O', str(output_path)
        ]
        
        try:
            logging.info(f"Downloading {output_path.name} with wget...")
            result = subprocess.run(wget_cmd, capture_output=False)
            
            if result.returncode == 0:
                actual_size = output_path.stat().st_size
                if expected_size and abs(actual_size - expected_size) > 1000:
                    logging.warning(f"Size mismatch: expected {expected_size}, got {actual_size}")
                return True
            else:
                logging.error(f"wget failed with code {result.returncode}")
                return False
                
        except FileNotFoundError:
            logging.error("wget not found. Please install wget or use WSL.")
            return False
        except Exception as e:
            logging.error(f"Download error: {e}")
            return False
    
    def download_file_python(self, url: str, output_path: Path, expected_size: int = None):
        """Download file using Python requests (fallback)"""
        
        # Check if partial file exists
        resume_pos = 0
        if output_path.exists():
            resume_pos = output_path.stat().st_size
            logging.info(f"Resuming download from {resume_pos:,} bytes")
        
        headers = {}
        if resume_pos > 0:
            headers['Range'] = f'bytes={resume_pos}-'
        
        try:
            with requests.get(url, headers=headers, stream=True, timeout=30) as r:
                r.raise_for_status()
                
                # Get total size
                total_size = int(r.headers.get('content-length', 0)) + resume_pos
                
                # Download with progress
                with open(output_path, 'ab' if resume_pos else 'wb') as f:
                    downloaded = resume_pos
                    for chunk in r.iter_content(chunk_size=8192*1024):  # 8MB chunks
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Progress update every 100MB
                            if downloaded % (100 * 1024 * 1024) == 0:
                                pct = (downloaded / total_size * 100) if total_size else 0
                                logging.info(f"  {output_path.name}: {downloaded/(1024**3):.1f}GB / {total_size/(1024**3):.1f}GB ({pct:.1f}%)")
                
                return True
                
        except Exception as e:
            logging.error(f"Download error: {e}")
            return False
    
    def get_manifest(self):
        """Get the manifest file listing all data files"""
        logging.info("Fetching OpenAlex manifest...")
        
        manifest_path = self.output_dir / "manifest.txt"
        
        try:
            response = requests.get(self.manifest_url)
            response.raise_for_status()
            
            manifest_text = response.text
            manifest_path.write_text(manifest_text)
            
            # Parse manifest
            files = []
            for line in manifest_text.strip().split('\n'):
                if line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 3:
                        files.append({
                            'path': parts[0],
                            'size': int(parts[1]),
                            'date': parts[2]
                        })
            
            logging.info(f"Found {len(files)} files in manifest")
            return files
            
        except Exception as e:
            logging.error(f"Error fetching manifest: {e}")
            return []
    
    def download_sample(self):
        """Download a small sample first to test"""
        logging.info("\n" + "="*60)
        logging.info("DOWNLOADING SAMPLE DATA")
        logging.info("="*60)
        
        # Download just a few files to test
        sample_files = [
            "works/updated_date=2024-08-27/part_000.gz",
            "works/updated_date=2024-08-27/part_001.gz",
            "institutions/updated_date=2024-08-27/part_000.gz",
            "authors/updated_date=2024-08-27/part_000.gz"
        ]
        
        for file_path in sample_files:
            url = f"{self.base_url}/{file_path}"
            output_path = self.output_dir / "data" / file_path
            output_path.parent.mkdir(exist_ok=True, parents=True)
            
            if output_path.exists():
                logging.info(f"Skipping {file_path} (already exists)")
                continue
            
            logging.info(f"Downloading {file_path}...")
            success = self.download_file_python(url, output_path)
            
            if success:
                size_mb = output_path.stat().st_size / (1024**2)
                logging.info(f"  Downloaded: {size_mb:.2f} MB")
            else:
                logging.error(f"  Failed to download {file_path}")
        
        logging.info("\nSample download complete. Check files before proceeding with full download.")
    
    def download_full_dataset(self, entity_type: str = "works", max_files: int = None):
        """Download full OpenAlex dataset for a specific entity type
        
        Entity types: works, authors, institutions, concepts, etc.
        """
        
        logging.info("\n" + "="*60)
        logging.info(f"DOWNLOADING OPENALEX {entity_type.upper()} DATA")
        logging.info("="*60)
        logging.info("WARNING: This will download ~300GB of data!")
        logging.info("Make sure you have sufficient disk space.")
        
        # Get manifest
        manifest = self.get_manifest()
        if not manifest:
            logging.error("Failed to get manifest")
            return
        
        # Filter for entity type
        entity_files = [f for f in manifest if f['path'].startswith(f"{entity_type}/")]
        logging.info(f"Found {len(entity_files)} {entity_type} files")
        
        if max_files:
            entity_files = entity_files[:max_files]
            logging.info(f"Limiting to {max_files} files")
        
        # Calculate total size
        total_size = sum(f['size'] for f in entity_files)
        logging.info(f"Total download size: {total_size / (1024**3):.2f} GB")
        
        # Download files
        for i, file_info in enumerate(entity_files, 1):
            file_path = file_info['path']
            expected_size = file_info['size']
            
            # Skip if already downloaded
            if file_path in self.checkpoint['downloaded_files']:
                logging.info(f"[{i}/{len(entity_files)}] Skipping {file_path} (already downloaded)")
                continue
            
            url = f"{self.base_url}/{file_path}"
            output_path = self.output_dir / "data" / file_path
            output_path.parent.mkdir(exist_ok=True, parents=True)
            
            logging.info(f"[{i}/{len(entity_files)}] Downloading {file_path} ({expected_size/(1024**2):.2f} MB)")
            
            # Try wget first, fallback to Python
            success = self.download_file_wget(url, output_path, expected_size)
            if not success:
                logging.info("Falling back to Python downloader...")
                success = self.download_file_python(url, output_path, expected_size)
            
            if success:
                self.checkpoint['downloaded_files'].append(file_path)
                self.checkpoint['total_size_gb'] += expected_size / (1024**3)
                self.save_checkpoint()
                logging.info(f"  Success! Total downloaded: {self.checkpoint['total_size_gb']:.2f} GB")
            else:
                self.checkpoint['errors'].append({
                    'file': file_path,
                    'timestamp': datetime.now().isoformat()
                })
                self.save_checkpoint()
                logging.error(f"  Failed to download {file_path}")
        
        logging.info("\n" + "="*60)
        logging.info("DOWNLOAD COMPLETE")
        logging.info("="*60)
        logging.info(f"Downloaded: {len(self.checkpoint['downloaded_files'])} files")
        logging.info(f"Total size: {self.checkpoint['total_size_gb']:.2f} GB")
        if self.checkpoint['errors']:
            logging.warning(f"Errors: {len(self.checkpoint['errors'])} files failed")


def main():
    """Main execution"""
    downloader = OpenAlexDownloader()
    
    print("""
    ========================================
    OPENALEX FULL DATASET DOWNLOAD
    ========================================
    
    Options:
    1. Download sample data (test ~100MB)
    2. Download full WORKS dataset (~300GB)
    3. Download INSTITUTIONS dataset (~5GB)
    4. Download AUTHORS dataset (~20GB)
    5. Exit
    
    """)
    
    choice = input("Select option (1-5): ").strip()
    
    if choice == '1':
        downloader.download_sample()
    elif choice == '2':
        confirm = input("\nThis will download ~300GB. Are you sure? (yes/no): ")
        if confirm.lower() == 'yes':
            downloader.download_full_dataset("works")
        else:
            print("Download cancelled.")
    elif choice == '3':
        downloader.download_full_dataset("institutions")
    elif choice == '4':
        downloader.download_full_dataset("authors")
    elif choice == '5':
        print("Exiting...")
    else:
        print("Invalid option")
    
    print(f"\nCheckpoint saved to {downloader.checkpoint_file}")
    print(f"Data location: {downloader.output_dir}")

if __name__ == "__main__":
    main()
