#!/usr/bin/env python3
"""
Create Prioritized URL Verification CSV

Combines URL check results and processing results to create an enhanced CSV
with priority markers and status indicators for efficient manual verification.
"""

import sqlite3
import csv
import json
from pathlib import Path
from datetime import datetime

def load_url_check_results():
    """Load most recent URL check results"""
    analysis_dir = Path("C:/Projects/OSINT-Foresight/analysis")
    check_files = list(analysis_dir.glob("policy_url_check_*.json"))

    if not check_files:
        return None

    check_file = sorted(check_files)[-1]
    print(f"Loading URL check results: {check_file.name}")

    with open(check_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Create lookup dict by doc_id
    results = {}
    for result in data['results']:
        results[result['doc_id']] = result

    return results

def get_extracted_documents(db_path):
    """Get list of documents that already have text extracted"""
    conn = sqlite3.connect(db_path, timeout=30.0)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT document_id, LENGTH(document_text) as text_length
        FROM policy_documents
        WHERE document_text IS NOT NULL
    ''')

    extracted = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()

    return extracted

def create_prioritized_csv(db_path, output_file):
    """
    Create enhanced CSV with priority and status markers
    """
    print("=" * 70)
    print("CREATING PRIORITIZED URL VERIFICATION CSV")
    print("=" * 70)
    print()

    # Load URL check results
    url_check = load_url_check_results()

    # Get documents with extracted text
    extracted_docs = get_extracted_documents(db_path)
    print(f"Documents with text extracted: {len(extracted_docs)}")
    print()

    # Get all documents from database
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
            document_url
        FROM policy_documents
        ORDER BY country_code, publication_date DESC
    ''')

    documents = cursor.fetchall()
    conn.close()

    # Process and categorize documents
    done = []
    priority_broken = []
    need_pdf_link = []

    for doc in documents:
        doc_id, country, doc_type, title, issuing_body, pub_date, url = doc

        # Get URL check status
        url_status = url_check.get(doc_id) if url_check else None

        # Determine category and priority
        if doc_id in extracted_docs:
            # Already extracted - DONE
            category = "DONE"
            priority = "0_SKIP"
            status_detail = f"Text extracted ({extracted_docs[doc_id]:,} chars)"
            done.append((doc_id, category, priority, status_detail))
        elif url_status and not url_status['success']:
            # URL definitely broken - PRIORITY
            category = "BROKEN_URL"
            priority = "1_PRIORITY"
            error = url_status.get('error')
            if error:
                status_detail = f"URL broken: {error[:100]}"
            else:
                status_code = url_status.get('status_code', 'Unknown')
                status_detail = f"URL broken: HTTP {status_code}"
            priority_broken.append((doc_id, category, priority, status_detail))
        elif url_status and url_status['success']:
            # URL works but returned HTML - NEED PDF LINK
            category = "HTML_PAGE"
            priority = "2_NEED_PDF"
            status_detail = "Landing page - find PDF download link"
            need_pdf_link.append((doc_id, category, priority, status_detail))
        else:
            # Unknown status
            category = "UNKNOWN"
            priority = "3_CHECK"
            status_detail = "No check data - verify manually"
            need_pdf_link.append((doc_id, category, priority, status_detail))

    # Write enhanced CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Enhanced header
        writer.writerow([
            'priority',
            'status',
            'document_id',
            'country_code',
            'document_type',
            'document_title',
            'issuing_body',
            'publication_date',
            'current_url',
            'verified_pdf_url',
            'notes',
            'status_detail'
        ])

        # Write documents in priority order
        for doc in documents:
            doc_id, country, doc_type, title, issuing_body, pub_date, url = doc

            # Find category info
            category = "UNKNOWN"
            priority = "3_CHECK"
            status_detail = ""

            for cat_docs in [done, priority_broken, need_pdf_link]:
                for item in cat_docs:
                    if item[0] == doc_id:
                        category = item[1]
                        priority = item[2]
                        status_detail = item[3]
                        break

            writer.writerow([
                priority,
                category,
                doc_id,
                country,
                doc_type,
                title,
                issuing_body,
                pub_date,
                url,
                '',  # verified_pdf_url - to be filled
                '',  # notes - to be filled
                status_detail
            ])

    print(f"[OK] Created prioritized CSV: {output_file}")
    print()
    print("SUMMARY BY PRIORITY:")
    print(f"  0_SKIP (Already done):      {len(done)}")
    print(f"  1_PRIORITY (Broken URLs):   {len(priority_broken)}")
    print(f"  2_NEED_PDF (HTML pages):    {len(need_pdf_link)}")
    print(f"  Total documents:            {len(documents)}")
    print()
    print("WORKFLOW RECOMMENDATIONS:")
    print()
    print("Phase 1 - Skip (2 documents):")
    print("  These already have text extracted. No action needed.")
    print()
    print("Phase 2 - Fix Broken URLs (45 documents):")
    print("  These URLs definitely don't work. Priority search required.")
    print("  - Use WebSearch to find correct URLs")
    print("  - Check official government archives")
    print("  - Some may no longer be available online")
    print()
    print("Phase 3 - Find PDF Links (51 documents):")
    print("  These are HTML landing pages. Visit and find PDF download.")
    print("  - EUR-Lex: Look for 'Download PDF' button")
    print("  - Government sites: Look for PDF icon or download link")
    print("  - Right-click PDF link -> Copy link address")
    print()
    print("TIP: Sort CSV by 'priority' column in Excel for efficient workflow")
    print()

if __name__ == '__main__':
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"C:/Projects/OSINT-Foresight/analysis/policy_urls_PRIORITIZED_{timestamp}.csv"

    create_prioritized_csv(db_path, output_file)

    print(f"Next step: Open {output_file} in Excel")
    print("Sort by 'priority' column and start with 1_PRIORITY items")
    print()
