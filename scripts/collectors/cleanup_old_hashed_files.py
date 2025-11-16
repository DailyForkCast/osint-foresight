#!/usr/bin/env python3
"""
Cleanup Old Hash-Based Files

After renaming operation, remove the old hash-based files if the new renamed files exist.
This handles the case where shutil.move() created copies instead of moving files.

Usage:
    python cleanup_old_hashed_files.py --collection-dir "F:/ThinkTank_Sweeps/US_CAN/20251013"
    python cleanup_old_hashed_files.py --collection-dir "F:/ThinkTank_Sweeps/US_CAN/20251013" --dry-run
"""

import argparse
import json
import re
import logging
from pathlib import Path
from typing import Set

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HashFileCleanup:
    """Remove old hash-based files after successful rename to human-readable names."""

    def __init__(self, collection_dir: str, dry_run: bool = False):
        self.collection_dir = Path(collection_dir)
        self.dry_run = dry_run
        self.items_json_path = self.collection_dir / "items.json"

        self.deleted_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.total_freed_bytes = 0

    def is_hash_filename(self, filename: str) -> bool:
        """Check if filename is a hash-based filename (64 hex chars)."""
        name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
        # Check if it's exactly 64 hexadecimal characters (SHA256 hash)
        return bool(re.match(r'^[0-9a-f]{64}$', name_without_ext))

    def is_renamed_filename(self, filename: str) -> bool:
        """Check if filename is in the new date-based format."""
        # Check if filename starts with YYYY-MM-DD pattern
        if len(filename) < 10:
            return False
        try:
            if filename[4] == '-' and filename[7] == '-':
                int(filename[:4])  # Year
                int(filename[5:7])  # Month
                int(filename[8:10])  # Day
                return True
        except ValueError:
            pass
        return False

    def get_old_hash_filenames(self, items: list) -> Set[str]:
        """
        Extract old hash-based filenames that should be deleted.

        Logic:
        - If an item's current saved_path uses the new naming format,
          we can derive what the old hash-based filename was from hash_sha256
        """
        old_hash_files = set()

        for item in items:
            saved_path = item.get('saved_path', '')
            hash_sha256 = item.get('hash_sha256', '')

            if not saved_path or not hash_sha256:
                continue

            # Get current filename
            current_filename = Path(saved_path).name

            # If current filename is in new format, the old one would be hash-based
            if self.is_renamed_filename(current_filename):
                # Get file extension from current file
                ext = Path(current_filename).suffix
                # Old filename would be: {hash}{ext}
                old_filename = f"{hash_sha256}{ext}"
                old_hash_files.add(old_filename)

        return old_hash_files

    def cleanup_directory(self, directory: Path, old_hash_files: Set[str]):
        """Clean up hash-based files in a directory."""
        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return

        logger.info(f"Cleaning up directory: {directory}")

        # Scan all files in directory
        for file_path in directory.rglob('*'):
            if not file_path.is_file():
                continue

            filename = file_path.name

            # Check if this is a hash-based file that should be deleted
            if filename in old_hash_files:
                file_size = file_path.stat().st_size

                if self.dry_run:
                    logger.info(f"  [DRY RUN] Would delete: {filename} ({file_size:,} bytes)")
                    self.deleted_count += 1
                    self.total_freed_bytes += file_size
                else:
                    try:
                        file_path.unlink()
                        logger.debug(f"  Deleted: {filename} ({file_size:,} bytes)")
                        self.deleted_count += 1
                        self.total_freed_bytes += file_size
                    except Exception as e:
                        logger.error(f"  Error deleting {filename}: {e}")
                        self.error_count += 1

    def run(self):
        """Main execution flow."""
        logger.info(f"\n{'='*60}")
        logger.info(f"Hash File Cleanup")
        logger.info(f"Collection: {self.collection_dir}")
        logger.info(f"Dry Run: {self.dry_run}")
        logger.info(f"{'='*60}\n")

        # Load items.json
        logger.info("Loading items.json...")
        with open(self.items_json_path, 'r', encoding='utf-8') as f:
            items = json.load(f)

        logger.info(f"Found {len(items)} items")

        # Get set of old hash filenames to delete
        logger.info("Identifying old hash-based files...")
        old_hash_files = self.get_old_hash_filenames(items)
        logger.info(f"Found {len(old_hash_files)} old hash-based files to remove")

        # Clean up files directory
        files_dir = self.collection_dir / "files"
        if files_dir.exists():
            self.cleanup_directory(files_dir, old_hash_files)

        # Clean up snapshots directory (recursively)
        snapshots_dir = self.collection_dir / "snapshots"
        if snapshots_dir.exists():
            self.cleanup_directory(snapshots_dir, old_hash_files)

        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"Cleanup Complete")
        logger.info(f"{'='*60}")
        logger.info(f"Files deleted: {self.deleted_count}")
        logger.info(f"Errors: {self.error_count}")
        logger.info(f"Space freed: {self.total_freed_bytes:,} bytes ({self.total_freed_bytes/1024/1024:.1f} MB)")
        logger.info(f"{'='*60}\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Clean up old hash-based files after rename")
    parser.add_argument("--collection-dir", required=True,
                        help="Path to collection directory")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be deleted without actually deleting")

    args = parser.parse_args()

    cleanup = HashFileCleanup(args.collection_dir, dry_run=args.dry_run)
    cleanup.run()


if __name__ == "__main__":
    main()
