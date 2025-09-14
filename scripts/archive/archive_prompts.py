#!/usr/bin/env python3
"""
Prompt Archive Manager
Automatically archives prompt files older than 72 hours (configurable)
Respects exclusion list in .prompt-archive-config
"""

import os
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('prompt_archive.log'),
        logging.StreamHandler()
    ]
)

class PromptArchiver:
    def __init__(self, prompts_dir='.', config_file='.prompt-archive-config'):
        self.prompts_dir = Path(prompts_dir)
        self.config_file = self.prompts_dir / config_file
        self.archive_dir = None
        self.exclusions = set()
        self.archive_hours = 72
        self.load_config()

    def load_config(self):
        """Load configuration from .prompt-archive-config file"""
        if not self.config_file.exists():
            logging.warning(f"Config file {self.config_file} not found. Using defaults.")
            self.archive_dir = self.prompts_dir / 'archive'
            return

        with open(self.config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse settings
                if line.startswith('ARCHIVE_AFTER_HOURS='):
                    try:
                        self.archive_hours = int(line.split('=')[1])
                    except ValueError:
                        logging.error(f"Invalid ARCHIVE_AFTER_HOURS value: {line}")
                elif line.startswith('ARCHIVE_FOLDER='):
                    folder_name = line.split('=')[1]
                    self.archive_dir = self.prompts_dir / folder_name
                elif line.startswith('CHECK_FREQUENCY='):
                    pass  # For future use with scheduling
                elif '=' not in line:
                    # It's a file to exclude
                    self.exclusions.add(line)

        # Default archive directory if not set
        if self.archive_dir is None:
            self.archive_dir = self.prompts_dir / 'archive'

        logging.info(f"Loaded config: Archive after {self.archive_hours} hours")
        logging.info(f"Exclusions: {len(self.exclusions)} files")

    def should_archive(self, file_path):
        """Check if a file should be archived based on age and exclusions"""
        file_path = Path(file_path)

        # Check if file is in exclusion list
        if file_path.name in self.exclusions:
            logging.debug(f"Skipping {file_path.name} - in exclusion list")
            return False

        # Skip directories
        if file_path.is_dir():
            return False

        # Skip files already in archive
        if 'archive' in file_path.parts:
            return False

        # Skip non-prompt files (keep only .md, .txt, .docx)
        valid_extensions = {'.md', '.txt', '.docx'}
        if file_path.suffix.lower() not in valid_extensions:
            return False

        # Check file age
        file_age_seconds = time.time() - file_path.stat().st_mtime
        file_age_hours = file_age_seconds / 3600

        if file_age_hours > self.archive_hours:
            logging.info(f"File {file_path.name} is {file_age_hours:.1f} hours old - will archive")
            return True

        logging.debug(f"File {file_path.name} is {file_age_hours:.1f} hours old - keeping")
        return False

    def archive_file(self, file_path):
        """Move a file to the archive directory"""
        file_path = Path(file_path)

        # Create archive directory if it doesn't exist
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Generate archive path with timestamp
        timestamp = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y%m%d')
        archive_name = f"{timestamp}_{file_path.name}"
        archive_path = self.archive_dir / archive_name

        # Handle duplicates
        counter = 1
        while archive_path.exists():
            archive_name = f"{timestamp}_{counter}_{file_path.name}"
            archive_path = self.archive_dir / archive_name
            counter += 1

        # Move the file
        try:
            shutil.move(str(file_path), str(archive_path))
            logging.info(f"Archived: {file_path.name} -> {archive_path.name}")
            return True
        except Exception as e:
            logging.error(f"Failed to archive {file_path.name}: {e}")
            return False

    def run(self, dry_run=False):
        """Run the archiver on all files in the prompts directory"""
        logging.info(f"Starting archive run (dry_run={dry_run})")

        archived_count = 0
        skipped_count = 0

        # Get all files in prompts directory (not recursive into archive)
        for file_path in self.prompts_dir.iterdir():
            if file_path.is_file() and self.should_archive(file_path):
                if dry_run:
                    logging.info(f"[DRY RUN] Would archive: {file_path.name}")
                else:
                    if self.archive_file(file_path):
                        archived_count += 1
            else:
                skipped_count += 1

        logging.info(f"Archive run complete: {archived_count} files archived, {skipped_count} skipped")
        return archived_count, skipped_count

def main():
    """Main entry point for script"""
    import argparse

    parser = argparse.ArgumentParser(description='Archive old prompt files')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be archived without actually moving files')
    parser.add_argument('--dir', default='.',
                        help='Directory containing prompts (default: current directory)')
    parser.add_argument('--force', action='store_true',
                        help='Archive all eligible files regardless of age')

    args = parser.parse_args()

    archiver = PromptArchiver(prompts_dir=args.dir)

    if args.force:
        archiver.archive_hours = 0  # Archive everything not excluded
        logging.warning("FORCE MODE: Archiving all eligible files regardless of age")

    archived, skipped = archiver.run(dry_run=args.dry_run)

    if args.dry_run:
        print(f"\n[DRY RUN] Would archive {archived} files, skip {skipped} files")
    else:
        print(f"\nArchived {archived} files, skipped {skipped} files")

if __name__ == '__main__':
    main()
