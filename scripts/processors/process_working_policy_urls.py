#!/usr/bin/env python3
"""
Process Policy Documents with Working URLs

Only processes documents where URL check returned 200 OK
Uses the results from check_policy_urls_batch.py
"""

import sqlite3
import json
import sys
from pathlib import Path
from policy_document_processor import process_policy_document

def load_url_check_results():
    """
    Load most recent URL check results
    """
    analysis_dir = Path("C:/Projects/OSINT-Foresight/analysis")
    check_files = list(analysis_dir.glob("policy_url_check_*.json"))

    if not check_files:
        print("ERROR: No URL check results found")
        print("First run: python scripts/utilities/check_policy_urls_batch.py")
        sys.exit(1)

    # Use most recent
    check_file = sorted(check_files)[-1]

    print(f"Loading URL check results from: {check_file.name}")

    with open(check_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data

def process_working_urls(db_path, download_dir, limit=None):
    """
    Process only documents with working URLs (200 OK)
    """
    # Load URL check results
    check_data = load_url_check_results()

    # Get document IDs with successful URLs
    working_doc_ids = [
        result['doc_id']
        for result in check_data['results']
        if result['success']
    ]

    print()
    print("=" * 70)
    print("PROCESSING POLICY DOCUMENTS (WORKING URLs ONLY)")
    print("=" * 70)
    print(f"\nTotal working URLs: {len(working_doc_ids)}")
    print(f"Total broken URLs: {check_data['failed']} (will skip)")
    print(f"Download directory: {download_dir}")

    if limit:
        print(f"Limit: {limit} documents")
        working_doc_ids = working_doc_ids[:limit]

    print()

    # Get document details from database
    conn = sqlite3.connect(db_path, timeout=30.0)
    cursor = conn.cursor()

    placeholders = ','.join('?' * len(working_doc_ids))
    cursor.execute(f'''
        SELECT document_id, document_title, country_code
        FROM policy_documents
        WHERE document_id IN ({placeholders})
        ORDER BY country_code, publication_date DESC
    ''', working_doc_ids)

    documents = cursor.fetchall()
    conn.close()

    print(f"Processing {len(documents)} documents...")
    print()

    successful = 0
    failed = 0

    for i, (doc_id, title, country) in enumerate(documents, 1):
        print(f"[{i}/{len(documents)}] [{country}] Processing...")
        print(f"  Title: {title}")

        success, message = process_policy_document(doc_id, db_path, download_dir)

        if success:
            successful += 1
        else:
            failed += 1

        # Rate limiting - be respectful to government servers
        if i < len(documents):
            import time
            time.sleep(2)

    print()
    print("=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)
    print(f"\nSuccessful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total processed: {len(documents)}")
    print()

    # Show what was skipped
    print(f"Skipped {check_data['failed']} documents with broken URLs")
    print("To fix broken URLs, run manual verification:")
    print("  1. Update CSV: analysis/policy_urls_verification_*.csv")
    print("  2. Import: python scripts/utilities/import_verified_policy_urls.py")
    print("  3. Rerun: python scripts/processors/policy_document_processor.py")
    print()

if __name__ == '__main__':
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    download_dir = "F:/OSINT_DATA/policy_documents"

    # Process all working URLs (no limit)
    process_working_urls(
        db_path=db_path,
        download_dir=download_dir,
        limit=None  # Process all working URLs
    )
