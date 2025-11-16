#!/usr/bin/env python3
"""
Retroactive File Renamer for Think Tank Collections

Renames hash-based filenames to human-readable format:
- From: 7b7ec92b1e7fb67537d6be0cad3bc834ea31ca27bf9eec495af1b849aaa15cd3.pdf
- To: 2016-06-15_brookings_our-history.pdf

Usage:
    python rename_thinktank_files.py --collection-dir "F:/ThinkTank_Sweeps/US_CAN/20251013"
    python rename_thinktank_files.py --collection-dir "F:/ThinkTank_Sweeps/US_CAN/20251013" --dry-run
"""

import argparse
import json
import csv
import re
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class ThinkTankFileRenamer:
    """Rename hash-based filenames to human-readable format."""

    def __init__(self, collection_dir: str, dry_run: bool = False):
        """
        Initialize renamer.

        Args:
            collection_dir: Path to collection directory (e.g., F:/ThinkTank_Sweeps/US_CAN/20251013)
            dry_run: If True, show what would be renamed without actually renaming
        """
        self.collection_dir = Path(collection_dir)
        self.dry_run = dry_run

        # Subdirectories
        self.files_dir = self.collection_dir / "files"
        self.snapshots_dir = self.collection_dir / "snapshots"

        # Output files
        self.items_json_path = self.collection_dir / "items.json"
        self.items_csv_path = self.collection_dir / "items.csv"
        self.file_manifest_path = self.collection_dir / "file_manifest.csv"

        # Tracking
        self.renamed_count = 0
        self.skipped_count = 0
        self.collision_count = 0
        self.error_count = 0

    def slugify(self, text: str, max_length: int = 80) -> str:
        """Convert text to URL-friendly slug."""
        if not text:
            return "untitled"

        # Remove organization suffix (e.g., "| Brookings")
        text = re.sub(r'\s*[|\-–]\s*\w+\s*$', '', text)

        # Convert to lowercase
        text = text.lower()

        # Replace non-alphanumeric with hyphens
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)

        # Trim hyphens from ends
        text = text.strip('-')

        # Truncate to max length
        if len(text) > max_length:
            text = text[:max_length].rsplit('-', 1)[0]

        return text or "untitled"

    def get_think_tank_slug(self, domain: str) -> str:
        """Get short slug for think tank organization."""
        # Remove www., .org, .edu, .com, etc.
        slug = domain.replace('www.', '')
        slug = re.sub(r'\.(org|edu|com|net|gov|int|mil)$', '', slug)

        # Take first part if multiple dots remain
        if '.' in slug:
            slug = slug.split('.')[0]

        return slug

    def generate_filename(self, item: Dict[str, Any], ext: str) -> str:
        """
        Generate human-readable filename.

        Format: YYYY-MM-DD_think-tank-slug_title-slug.ext
        """
        # Extract date
        date_str = "0000-00-00"
        if item.get("publication_date_iso"):
            try:
                pub_date = datetime.fromisoformat(item["publication_date_iso"].replace('Z', '+00:00'))
                date_str = pub_date.strftime("%Y-%m-%d")
            except:
                # Use today as fallback
                date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        else:
            # Use today
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Get think tank slug
        think_tank_slug = self.get_think_tank_slug(item.get("publisher_org", "unknown"))

        # Get title slug
        title_slug = self.slugify(item.get("title", "untitled"))

        # Combine
        filename = f"{date_str}_{think_tank_slug}_{title_slug}{ext}"

        return filename

    def rename_item_file(self, item: Dict[str, Any]) -> bool:
        """
        Rename a single item's file.

        Args:
            item: Item dictionary from items.json

        Returns:
            True if renamed successfully, False otherwise
        """
        old_path_str = item.get("saved_path")
        if not old_path_str:
            logging.warning(f"Item has no saved_path: {item.get('canonical_url')}")
            self.skipped_count += 1
            return False

        old_path = Path(old_path_str)

        # Check if file exists
        if not old_path.exists():
            logging.warning(f"File not found: {old_path}")
            self.skipped_count += 1
            return False

        # Get file extension
        ext = old_path.suffix

        # Generate new filename
        new_filename = self.generate_filename(item, ext)

        # Determine new path
        if item.get("document_type") == "web_snapshot":
            # Snapshots go in snapshots/{domain}/ subdirectory
            domain = item.get("publisher_org", "unknown")
            new_path = self.snapshots_dir / domain / new_filename
        else:
            # Files go in files/ directory
            new_path = self.files_dir / new_filename

        # Handle filename collisions
        if new_path.exists() and new_path != old_path:
            # Append hash suffix
            sha256 = item.get("hash_sha256", "")[:8]
            filename_base = new_filename.rsplit('.', 1)[0]
            new_filename = f"{filename_base}_{sha256}{ext}"
            if item.get("document_type") == "web_snapshot":
                domain = item.get("publisher_org", "unknown")
                new_path = self.snapshots_dir / domain / new_filename
            else:
                new_path = self.files_dir / new_filename
            self.collision_count += 1
            logging.debug(f"Collision resolved: {new_filename}")

        # Rename file
        if old_path == new_path:
            logging.debug(f"Already renamed: {new_path.name}")
            self.skipped_count += 1
            return False

        if self.dry_run:
            logging.info(f"[DRY RUN] Would rename:")
            logging.info(f"  From: {old_path.name}")
            logging.info(f"  To:   {new_path.name}")
            self.renamed_count += 1
        else:
            try:
                # Ensure parent directory exists
                new_path.parent.mkdir(parents=True, exist_ok=True)
                # Rename
                shutil.move(str(old_path), str(new_path))
                logging.info(f"Renamed: {old_path.name} → {new_path.name}")
                # Update item with new path
                item["saved_path"] = str(new_path)
                self.renamed_count += 1
            except Exception as e:
                logging.error(f"Error renaming {old_path.name}: {e}")
                self.error_count += 1
                return False

        return True

    def run(self):
        """Main execution flow."""
        logging.info(f"\n{'='*60}")
        logging.info(f"Think Tank File Renamer")
        logging.info(f"Collection: {self.collection_dir}")
        logging.info(f"Dry Run: {self.dry_run}")
        logging.info(f"{'='*60}\n")

        # Load items.json
        logging.info("Loading items.json...")
        with open(self.items_json_path, 'r', encoding='utf-8') as f:
            items = json.load(f)

        logging.info(f"Found {len(items)} items to process")

        # Rename each item's file
        for idx, item in enumerate(items, 1):
            if idx % 100 == 0:
                logging.info(f"Progress: {idx}/{len(items)} items processed")
            self.rename_item_file(item)

        # Save updated items.json
        if not self.dry_run and self.renamed_count > 0:
            logging.info("\nSaving updated items.json...")
            with open(self.items_json_path, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)

            # Regenerate items.csv
            logging.info("Regenerating items.csv...")
            if items:
                with open(self.items_csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=items[0].keys())
                    writer.writeheader()
                    writer.writerows(items)

            # Regenerate file_manifest.csv
            logging.info("Regenerating file_manifest.csv...")
            with open(self.file_manifest_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["hash_sha256", "saved_path", "bytes", "source_url", "canonical_url", "publisher_org", "title"])
                for item in items:
                    if item.get("hash_sha256"):
                        writer.writerow([
                            item.get("hash_sha256", ""),
                            item.get("saved_path", ""),
                            item.get("file_size_bytes", 0),
                            item.get("download_url", ""),
                            item.get("canonical_url", ""),
                            item.get("publisher_org", ""),
                            item.get("title", "")
                        ])

        # Summary
        logging.info(f"\n{'='*60}")
        logging.info(f"Renaming Complete")
        logging.info(f"{'='*60}")
        logging.info(f"Total items: {len(items)}")
        logging.info(f"Renamed: {self.renamed_count}")
        logging.info(f"Skipped: {self.skipped_count}")
        logging.info(f"Collisions resolved: {self.collision_count}")
        logging.info(f"Errors: {self.error_count}")
        logging.info(f"{'='*60}\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Think Tank File Renamer")
    parser.add_argument("--collection-dir", required=True,
                        help="Path to collection directory (e.g., F:/ThinkTank_Sweeps/US_CAN/20251013)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be renamed without actually renaming")

    args = parser.parse_args()

    renamer = ThinkTankFileRenamer(args.collection_dir, dry_run=args.dry_run)
    renamer.run()


if __name__ == "__main__":
    main()
