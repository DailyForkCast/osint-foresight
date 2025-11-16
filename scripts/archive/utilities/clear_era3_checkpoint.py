#!/usr/bin/env python3
"""
Clear Era 3 archives from checkpoint to enable reprocessing with UBL parser

This script removes Era 3 archives (Feb 2024 - Aug 2025) from the checkpoint
so they can be reprocessed with the UBL-integrated processor.
"""
import json
from pathlib import Path
from datetime import datetime

def clear_era3_checkpoint():
    """Remove Era 3 archives from checkpoint"""

    checkpoint_path = Path("C:/Projects/OSINT - Foresight/data/ted_production_checkpoint.json")

    # Load checkpoint
    with open(checkpoint_path) as f:
        checkpoint = json.load(f)

    # Identify Era 3 archives (2024-02 onwards)
    era3_patterns = [
        '2024_02', '2024_03', '2024_04', '2024_05', '2024_06', '2024_07',
        '2024_08', '2024_09', '2024_10', '2024_11', '2024_12',
        '2025_01', '2025_02', '2025_03', '2025_04', '2025_05',
        '2025_06', '2025_07', '2025_08', '2025_09', '2025_10',
        '2025_11', '2025_12'
    ]

    original_count = len(checkpoint['processed_archives'])

    # Also add late 2023 to catch missing data
    era3_patterns.extend(['2023_12'])

    # Filter out Era 3 archives
    era3_removed = []
    new_processed = []

    for archive in checkpoint['processed_archives']:
        if any(pattern in archive for pattern in era3_patterns):
            era3_removed.append(archive)
        else:
            new_processed.append(archive)

    # Update checkpoint
    checkpoint['processed_archives'] = new_processed
    checkpoint['last_update'] = datetime.now().isoformat()

    # Backup original
    backup_path = checkpoint_path.with_suffix('.json.backup_before_era3_clear')
    with open(backup_path, 'w') as f:
        json.dump(checkpoint, f, indent=2)
    print(f"Backup saved: {backup_path}")

    # Save updated checkpoint
    with open(checkpoint_path, 'w') as f:
        json.dump(checkpoint, f, indent=2)

    # Report
    print("\n" + "="*80)
    print("ERA 3 CHECKPOINT CLEARED")
    print("="*80)
    print(f"Original archives: {original_count}")
    print(f"Remaining archives: {len(new_processed)}")
    print(f"Removed archives: {len(era3_removed)}")
    print()
    print("Removed archives (ready for reprocessing):")
    for arch in sorted(era3_removed):
        print(f"  - {Path(arch).name}")
    print()
    print("These archives will now be reprocessed with UBL parser integration.")
    print("="*80)

if __name__ == '__main__':
    clear_era3_checkpoint()
