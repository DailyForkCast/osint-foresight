#!/usr/bin/env python3
"""
Simple backup script for OSINT Foresight Project
Backs up to external drive F: with smart incremental updates
"""
import os
import shutil
import datetime
from pathlib import Path
import json

# Configuration
PROJECT_DIR = Path("C:/Projects/OSINT - Foresight")
BACKUP_DIR = Path("F:/OSINT_Backups/project")
ARCHIVE_DIR = Path("F:/OSINT_Backups/archives")

# What to exclude (large/regeneratable files)
EXCLUDE = [
    "__pycache__", ".pyc", ".git/objects", ".git/lfs",
    "node_modules", "venv", "env", ".env",
    "out/SK/cordis_data",  # Large JSON files
    "data/raw",  # Raw data can be re-downloaded
]

def should_backup(file_path: str) -> bool:
    """Check if file should be backed up"""
    for pattern in EXCLUDE:
        if pattern in file_path:
            return False
    return True

def backup_project():
    """Backup project with incremental updates"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"OSINT Foresight Backup - {timestamp}")
    print("=" * 60)
    print(f"Source: {PROJECT_DIR}")
    print(f"Destination: {BACKUP_DIR}")
    print("-" * 60)
    
    # Track what we copy
    copied_files = 0
    skipped_files = 0
    total_size = 0
    
    # Create backup directory if needed
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Walk through project
    for root, dirs, files in os.walk(PROJECT_DIR):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not any(exc in d for exc in EXCLUDE)]
        
        for file in files:
            source_file = Path(root) / file
            relative_path = source_file.relative_to(PROJECT_DIR)
            dest_file = BACKUP_DIR / relative_path
            
            # Check if should backup
            if not should_backup(str(source_file)):
                skipped_files += 1
                continue
            
            # Check if file needs updating
            needs_copy = False
            if not dest_file.exists():
                needs_copy = True
            else:
                # Compare modification times
                source_mtime = source_file.stat().st_mtime
                dest_mtime = dest_file.stat().st_mtime
                if source_mtime > dest_mtime:
                    needs_copy = True
            
            if needs_copy:
                try:
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_file)
                    copied_files += 1
                    total_size += source_file.stat().st_size
                    print(f"  [COPY] {relative_path}")
                except Exception as e:
                    print(f"  [ERROR] {relative_path}: {e}")
    
    # Summary
    print("-" * 60)
    print(f"Backup Complete!")
    print(f"  Files copied: {copied_files}")
    print(f"  Files skipped: {skipped_files}")
    print(f"  Total size: {total_size / 1024 / 1024:.2f} MB")
    
    # Save backup info
    info_file = BACKUP_DIR / "backup_info.json"
    info = {
        "last_backup": timestamp,
        "files_copied": copied_files,
        "files_skipped": skipped_files,
        "total_size_mb": round(total_size / 1024 / 1024, 2)
    }
    
    with open(info_file, 'w') as f:
        json.dump(info, f, indent=2)
    
    # Create weekly archive (on Mondays)
    if datetime.datetime.now().weekday() == 0:
        create_archive(timestamp)
    
    return copied_files

def create_archive(timestamp):
    """Create a zip archive of the backup"""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archive_name = ARCHIVE_DIR / f"backup_{timestamp}.zip"
    
    print(f"\nCreating weekly archive...")
    
    import zipfile
    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(BACKUP_DIR):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(BACKUP_DIR)
                zipf.write(file_path, arcname)
    
    size_mb = archive_name.stat().st_size / 1024 / 1024
    print(f"  Archive created: {archive_name.name} ({size_mb:.2f} MB)")

def restore_project(source_backup=None):
    """Restore project from backup"""
    if source_backup is None:
        source_backup = BACKUP_DIR
    
    print(f"Restoring from: {source_backup}")
    print("WARNING: This will overwrite existing files!")
    response = input("Continue? (y/n): ")
    
    if response.lower() != 'y':
        print("Restore cancelled")
        return
    
    # Copy back
    for root, dirs, files in os.walk(source_backup):
        for file in files:
            if file == "backup_info.json":
                continue
            
            source_file = Path(root) / file
            relative_path = source_file.relative_to(source_backup)
            dest_file = PROJECT_DIR / relative_path
            
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, dest_file)
            print(f"  [RESTORE] {relative_path}")
    
    print("Restore complete!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_project()
    else:
        backup_project()