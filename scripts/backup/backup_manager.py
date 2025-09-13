#!/usr/bin/env python3
"""
OSINT Foresight Project Backup Manager
Backs up project to external drive and Google Cloud Storage
"""
import os
import shutil
import subprocess
import datetime
import json
from pathlib import Path
from typing import List, Dict
import hashlib

# Configuration
PROJECT_DIR = Path("C:/Projects/OSINT - Foresight")
EXTERNAL_BACKUP_DIR = Path("F:/OSINT_Backups/project")
ARCHIVE_DIR = Path("F:/OSINT_Backups/archives")
GCS_BUCKET = "osint-foresight-2025-backups"  # We'll create this

# Files/folders to exclude from backups
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    ".git/objects",  # Git objects (large, can be regenerated)
    ".git/lfs",      # Git LFS files
    "node_modules",
    "venv",
    "env",
    ".env",
    "*.log",
    "*.tmp",
    "~*",
    "out/SK/cordis_data",  # Large JSON files
    "data/raw/source=*",    # Raw data (can be re-pulled)
]

# Files to ALWAYS backup (even if in excluded folders)
INCLUDE_PATTERNS = [
    "*.py",
    "*.md",
    "*.yaml",
    "*.yml", 
    "*.json",
    "*.tsv",
    "*.csv",
    "Makefile",
    "requirements.txt",
    ".claude/*",
    "docs/**",
    "scripts/**",
    "src/**",
    "queries/**",
    "config/**",
]

class BackupManager:
    def __init__(self):
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_log = []
        
    def should_backup(self, file_path: Path) -> bool:
        """Determine if a file should be backed up"""
        file_str = str(file_path).replace("\\", "/")
        
        # Check excludes
        for pattern in EXCLUDE_PATTERNS:
            if pattern in file_str:
                # Check if it's explicitly included
                for include in INCLUDE_PATTERNS:
                    if include.replace("**", "") in file_str:
                        return True
                return False
        
        return True
    
    def get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file for change detection"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return ""
    
    def backup_to_external(self) -> Dict:
        """Backup project to external drive with incremental updates"""
        print(f"Backing up to external drive: {EXTERNAL_BACKUP_DIR}")
        print("-" * 60)
        
        stats = {"files_copied": 0, "files_skipped": 0, "total_size": 0}
        
        # Create manifest file for tracking
        manifest_file = EXTERNAL_BACKUP_DIR / ".backup_manifest.json"
        manifest = {}
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
        
        # Walk through project directory
        for root, dirs, files in os.walk(PROJECT_DIR):
            root_path = Path(root)
            relative_root = root_path.relative_to(PROJECT_DIR)
            
            # Filter directories
            dirs[:] = [d for d in dirs if not any(exc in d for exc in ["__pycache__", ".git", "venv", "node_modules"])]
            
            for file in files:
                source_file = root_path / file
                relative_path = relative_root / file
                
                # Check if should backup
                if not self.should_backup(source_file):
                    stats["files_skipped"] += 1
                    continue
                
                # Calculate destination
                dest_file = EXTERNAL_BACKUP_DIR / relative_path
                
                # Check if file changed
                current_hash = self.get_file_hash(source_file)
                manifest_key = str(relative_path).replace("\\", "/")
                
                if manifest.get(manifest_key) == current_hash and dest_file.exists():
                    # File unchanged, skip
                    continue
                
                # Copy file
                try:
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_file)
                    stats["files_copied"] += 1
                    stats["total_size"] += source_file.stat().st_size
                    manifest[manifest_key] = current_hash
                    print(f"  [COPY] {relative_path}")
                except Exception as e:
                    print(f"  [ERROR] {relative_path}: {e}")
        
        # Save manifest
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Create timestamped archive every week
        if datetime.datetime.now().weekday() == 0:  # Monday
            self.create_archive()
        
        print(f"\nBackup complete: {stats['files_copied']} files copied ({stats['total_size'] / 1024 / 1024:.2f} MB)")
        return stats
    
    def create_archive(self):
        """Create a timestamped archive"""
        archive_name = ARCHIVE_DIR / f"backup_{self.timestamp}.zip"
        print(f"\nCreating weekly archive: {archive_name}")
        
        # Use Python's zipfile to create archive
        import zipfile
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(EXTERNAL_BACKUP_DIR):
                for file in files:
                    if not file.startswith('.'):
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(EXTERNAL_BACKUP_DIR)
                        zipf.write(file_path, arcname)
        
        print(f"  Archive created: {archive_name.stat().st_size / 1024 / 1024:.2f} MB")
    
    def backup_to_gcs(self):
        """Backup essential project files to Google Cloud Storage"""
        print(f"\nBacking up to Google Cloud Storage")
        print("-" * 60)
        
        # First, ensure bucket exists
        gcloud_path = r"C:\Users\mrear\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud"
        gsutil_path = r"C:\Users\mrear\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gsutil"
        
        # Create bucket if not exists
        try:
            result = subprocess.run(
                f'"{gsutil_path}" ls gs://{GCS_BUCKET}',
                shell=True, capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"Creating GCS bucket: {GCS_BUCKET}")
                subprocess.run(
                    f'"{gsutil_path}" mb -p osint-foresight-2025 -l US gs://{GCS_BUCKET}',
                    shell=True
                )
        except Exception as e:
            print(f"GCS bucket check/create error: {e}")
            return
        
        # Sync essential files only (no large data)
        essential_dirs = [
            "src",
            "scripts", 
            "docs",
            "config",
            "queries",
            "reports",
            ".claude",
        ]
        
        essential_files = [
            "*.py",
            "*.md",
            "Makefile",
            "requirements.txt",
            "*.yaml",
            "*.yml",
        ]
        
        # Create a temporary staging directory
        staging_dir = Path("C:/temp/osint_backup_staging")
        staging_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy essential files to staging
        for dir_name in essential_dirs:
            source_dir = PROJECT_DIR / dir_name
            if source_dir.exists():
                dest_dir = staging_dir / dir_name
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.copytree(source_dir, dest_dir, 
                              ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        
        # Copy root level files
        for pattern in essential_files:
            for file in PROJECT_DIR.glob(pattern):
                if file.is_file():
                    shutil.copy2(file, staging_dir / file.name)
        
        # Sync to GCS
        try:
            print("Syncing to Google Cloud Storage...")
            result = subprocess.run(
                f'"{gsutil_path}" -m rsync -r -d "{staging_dir}" gs://{GCS_BUCKET}/project/',
                shell=True, capture_output=True, text=True
            )
            
            if result.returncode == 0:
                print("  [OK] Successfully synced to GCS")
                # Add timestamp file
                timestamp_file = staging_dir / "last_backup.txt"
                timestamp_file.write_text(f"Last backup: {self.timestamp}")
                subprocess.run(
                    f'"{gsutil_path}" cp "{timestamp_file}" gs://{GCS_BUCKET}/project/',
                    shell=True
                )
            else:
                print(f"  [ERROR] GCS sync failed: {result.stderr}")
        except Exception as e:
            print(f"  [ERROR] GCS sync error: {e}")
        finally:
            # Clean up staging directory
            if staging_dir.exists():
                shutil.rmtree(staging_dir)
    
    def run_full_backup(self):
        """Run complete backup to both destinations"""
        print(f"\n{'='*60}")
        print(f"OSINT Foresight Backup - {self.timestamp}")
        print(f"{'='*60}\n")
        
        # Backup to external drive
        external_stats = self.backup_to_external()
        
        # Backup to Google Cloud
        self.backup_to_gcs()
        
        print(f"\n{'='*60}")
        print("Backup Summary:")
        print(f"  External Drive: {external_stats['files_copied']} files")
        print(f"  Google Cloud: Essential files synced")
        print(f"  Timestamp: {self.timestamp}")
        print(f"{'='*60}\n")
        
        # Log backup
        log_file = PROJECT_DIR / "backup.log"
        with open(log_file, 'a') as f:
            f.write(f"{self.timestamp} - External: {external_stats['files_copied']} files, GCS: synced\n")

def main():
    """Main backup function"""
    manager = BackupManager()
    manager.run_full_backup()

if __name__ == "__main__":
    main()