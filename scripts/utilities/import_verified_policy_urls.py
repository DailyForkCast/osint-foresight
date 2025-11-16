#!/usr/bin/env python3
"""
Import Verified Policy Document URLs

Reads the verified CSV and updates database with corrected PDF URLs.
"""

import sqlite3
import csv
import sys
from pathlib import Path
from datetime import datetime

def import_verified_urls(db_path, csv_file):
    """
    Import verified PDF URLs from CSV and update database
    """
    # Read CSV
    print("=" * 70)
    print("IMPORT VERIFIED POLICY DOCUMENT URLs")
    print("=" * 70)
    print(f"\nReading: {csv_file}")
    print()

    updates = []
    skipped = []

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            doc_id = row['document_id']
            verified_url = row['verified_pdf_url'].strip()
            notes = row['notes'].strip()

            if verified_url:
                updates.append({
                    'document_id': doc_id,
                    'url': verified_url,
                    'notes': notes,
                    'title': row['document_title'][:60]
                })
            else:
                skipped.append({
                    'document_id': doc_id,
                    'title': row['document_title'][:60],
                    'notes': notes
                })

    print(f"URLs to update: {len(updates)}")
    print(f"URLs skipped (no verified URL): {len(skipped)}")
    print()

    if not updates:
        print("No verified URLs found in CSV. Nothing to update.")
        return

    # Confirm before updating
    print("Sample of updates to be applied:")
    for i, update in enumerate(updates[:5], 1):
        print(f"\n{i}. {update['title']}")
        print(f"   New URL: {update['url'][:80]}")
        if update['notes']:
            print(f"   Notes: {update['notes']}")

    if len(updates) > 5:
        print(f"\n... and {len(updates) - 5} more")

    print()
    response = input(f"Update {len(updates)} document URLs in database? (yes/no): ")

    if response.lower() != 'yes':
        print("Update cancelled.")
        return

    # Update database
    conn = sqlite3.connect(db_path, timeout=30.0)
    cursor = conn.cursor()

    updated_count = 0
    for update in updates:
        cursor.execute('''
            UPDATE policy_documents
            SET document_url = ?
            WHERE document_id = ?
        ''', (update['url'], update['document_id']))

        updated_count += 1

    conn.commit()
    conn.close()

    print()
    print(f"[OK] Successfully updated {updated_count} document URLs")
    print()

    # Show skipped documents
    if skipped:
        print(f"Documents skipped ({len(skipped)}):")
        for skip in skipped[:10]:
            print(f"  - {skip['title']}")
            if skip['notes']:
                print(f"    Notes: {skip['notes']}")
        if len(skipped) > 10:
            print(f"  ... and {len(skipped) - 10} more")
        print()

    print("Next step: Run policy_document_processor.py to download PDFs")
    print()

if __name__ == '__main__':
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    # Find most recent verification CSV
    analysis_dir = Path("C:/Projects/OSINT-Foresight/analysis")
    csv_files = list(analysis_dir.glob("policy_urls_verification_*.csv"))

    if not csv_files:
        print("ERROR: No verification CSV file found.")
        print("Expected: analysis/policy_urls_verification_*.csv")
        print()
        print("First run: python scripts/utilities/export_policy_urls_for_verification.py")
        sys.exit(1)

    # Use most recent
    csv_file = sorted(csv_files)[-1]

    print(f"Using CSV file: {csv_file.name}")
    print()

    import_verified_urls(db_path, csv_file)
