#!/usr/bin/env python3
"""
Regenerate CSV files from items.json
Use this after rename operation if CSV regeneration failed due to file lock
"""

import json
import csv
from pathlib import Path
import sys

def regenerate_csv_files(collection_dir: str):
    """Regenerate items.csv and file_manifest.csv from items.json"""
    collection_path = Path(collection_dir)
    items_json_path = collection_path / "items.json"
    items_csv_path = collection_path / "items.csv"
    file_manifest_path = collection_path / "file_manifest.csv"

    print(f"Loading items.json from: {items_json_path}")
    with open(items_json_path, 'r', encoding='utf-8') as f:
        items = json.load(f)

    print(f"Found {len(items)} items")

    # Regenerate items.csv
    print(f"Regenerating items.csv...")
    if items:
        with open(items_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=items[0].keys())
            writer.writeheader()
            writer.writerows(items)
        print(f"Created: {items_csv_path}")

    # Regenerate file_manifest.csv
    print(f"Regenerating file_manifest.csv...")
    with open(file_manifest_path, 'w', newline='', encoding='utf-8') as f:
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
        print(f"Created: {file_manifest_path}")

    print(f"\nCSV regeneration complete!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python regenerate_csv_files.py <collection_dir>")
        print("Example: python regenerate_csv_files.py F:/ThinkTank_Sweeps/US_CAN/20251013")
        sys.exit(1)

    collection_dir = sys.argv[1]
    regenerate_csv_files(collection_dir)
