#!/usr/bin/env python3
"""
Export Policy Document URLs for Manual Verification

Exports all policy document URLs to CSV for manual verification and updating.
"""

import sqlite3
import csv
from pathlib import Path
from datetime import datetime

def export_urls_for_verification(db_path, output_file):
    """
    Export all policy document URLs to CSV for manual verification
    """
    conn = sqlite3.connect(db_path, timeout=30.0)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            document_id,
            country_code,
            document_type,
            document_title,
            issuing_body,
            publication_date,
            document_url,
            document_text IS NOT NULL as text_extracted
        FROM policy_documents
        ORDER BY country_code, publication_date DESC
    ''')

    documents = cursor.fetchall()
    conn.close()

    print("=" * 70)
    print("POLICY DOCUMENT URL EXPORT")
    print("=" * 70)
    print(f"\nTotal documents: {len(documents)}")
    print(f"Output file: {output_file}")
    print()

    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'document_id',
            'country_code',
            'document_type',
            'document_title',
            'issuing_body',
            'publication_date',
            'current_url',
            'verified_pdf_url',  # Empty column to fill in
            'notes',              # Empty column for notes
            'text_extracted'
        ])

        # Data rows
        for doc in documents:
            doc_id, country, doc_type, title, issuing_body, pub_date, url, text_extracted = doc

            writer.writerow([
                doc_id,
                country,
                doc_type,
                title,
                issuing_body,
                pub_date,
                url,
                '',  # verified_pdf_url - to be filled manually
                '',  # notes - for any observations
                'YES' if text_extracted else 'NO'
            ])

    print(f"[OK] Exported {len(documents)} documents to {output_file}")
    print()
    print("INSTRUCTIONS:")
    print("1. Open the CSV file in Excel or text editor")
    print("2. For each document, visit the 'current_url'")
    print("3. Find the actual PDF download link")
    print("4. Paste the direct PDF URL in 'verified_pdf_url' column")
    print("5. Add any notes (e.g., 'PDF not available', 'requires login', etc.)")
    print("6. Save the file")
    print("7. Run import_verified_policy_urls.py to update database")
    print()
    print("TIP: Focus on EUR-Lex URLs first - they have 'Download PDF' buttons")
    print("TIP: For HTML-only pages, note that in 'notes' column")
    print()

if __name__ == '__main__':
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    # Create export with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"C:/Projects/OSINT-Foresight/analysis/policy_urls_verification_{timestamp}.csv"

    export_urls_for_verification(db_path, output_file)

    print(f"Next step: Verify URLs and then run:")
    print(f"  python scripts/utilities/import_verified_policy_urls.py")
    print()
