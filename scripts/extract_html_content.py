#!/usr/bin/env python3
"""
HTML Content Extraction Pipeline
Extracts clean text from HTML files and updates database
"""

import sqlite3
import os
from bs4 import BeautifulSoup
from datetime import datetime
import json
from tqdm import tqdm
import re

# Configuration
DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'
LOG_FILE = 'analysis/html_extraction_log.json'
BATCH_SIZE = 100  # Commit every 100 documents

# HTML cleaning configuration
REMOVE_TAGS = ['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']
MIN_CONTENT_LENGTH = 100  # Minimum characters to consider valid content

def extract_text_from_html(html_path):
    """
    Extract clean text from HTML file

    Args:
        html_path: Path to HTML file

    Returns:
        tuple: (extracted_text, extraction_success, error_message)
    """
    try:
        # Read HTML file
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()

        # Check if this is actually a PDF file (not HTML)
        if html_content.strip().startswith('%PDF'):
            return None, False, "File is PDF, not HTML (skipping)"

        # Check if content is too short before parsing
        if len(html_content.strip()) < 100:
            return None, False, "HTML file too short"

        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove unwanted elements
        for tag in REMOVE_TAGS:
            for element in soup.find_all(tag):
                element.decompose()

        # Try to find main content area first
        main_content = None

        # Common main content selectors
        content_selectors = [
            'article',
            'main',
            '[role="main"]',
            '.content',
            '.main-content',
            '#content',
            '#main-content',
            '.article-content',
            '.post-content',
        ]

        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        # If no main content found, use body
        if not main_content:
            main_content = soup.find('body')

        # If still nothing, use entire soup
        if not main_content:
            main_content = soup

        # Extract text
        text = main_content.get_text(separator=' ', strip=True)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double newline
        text = text.strip()

        # Validate content length
        if len(text) < MIN_CONTENT_LENGTH:
            return None, False, f"Content too short: {len(text)} chars"

        return text, True, None

    except Exception as e:
        return None, False, str(e)

def process_documents(dry_run=False, limit=None):
    """
    Process documents without content

    Args:
        dry_run: If True, don't update database (just test)
        limit: Maximum number of documents to process (None = all)
    """
    print("="*80)
    print("HTML CONTENT EXTRACTION PIPELINE")
    print("="*80)
    print(f"Database: {DB_PATH}")
    print(f"Mode: {'DRY RUN (no database updates)' if dry_run else 'PRODUCTION'}")
    print(f"Limit: {limit if limit else 'All documents'}")
    print(f"Batch size: {BATCH_SIZE}")
    print("="*80)

    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")  # Allow concurrent reads
    cursor = conn.cursor()

    # Get documents to process
    query = '''
        SELECT id, saved_path, document_type, publisher_org, title
        FROM documents
        WHERE content_text = ''
          AND saved_path IS NOT NULL
          AND saved_path != ''
    '''

    if limit:
        query += f' LIMIT {limit}'

    cursor.execute(query)
    documents = cursor.fetchall()

    total_docs = len(documents)
    print(f"\nFound {total_docs:,} documents to process\n")

    if total_docs == 0:
        print("No documents to process!")
        conn.close()
        return

    # Statistics
    stats = {
        'start_time': datetime.now().isoformat(),
        'total_documents': total_docs,
        'successful': 0,
        'failed': 0,
        'file_not_found': 0,
        'content_too_short': 0,
        'pdf_files': 0,
        'errors': [],
        'samples': []
    }

    # Process documents
    processed = 0

    for doc_id, saved_path, doc_type, publisher, title in tqdm(documents, desc="Processing HTML"):
        processed += 1

        # Check if file exists
        if not os.path.exists(saved_path):
            stats['file_not_found'] += 1
            stats['errors'].append({
                'doc_id': doc_id,
                'error': 'File not found',
                'path': saved_path
            })
            continue

        # Extract text
        extracted_text, success, error_msg = extract_text_from_html(saved_path)

        if success:
            stats['successful'] += 1

            # Save first 5 samples for validation
            if len(stats['samples']) < 5:
                stats['samples'].append({
                    'doc_id': doc_id,
                    'title': title[:100],
                    'publisher': publisher,
                    'content_length': len(extracted_text),
                    'content_preview': extracted_text[:500]
                })

            # Update database (if not dry run)
            if not dry_run:
                cursor.execute('''
                    UPDATE documents
                    SET content_text = ?,
                        content_length = ?,
                        updated_at = ?
                    WHERE id = ?
                ''', (extracted_text, len(extracted_text), datetime.now().isoformat(), doc_id))

                # Commit in batches
                if processed % BATCH_SIZE == 0:
                    conn.commit()
                    tqdm.write(f"  Committed batch at {processed}/{total_docs}")
        else:
            stats['failed'] += 1

            if 'too short' in error_msg.lower():
                stats['content_too_short'] += 1
            elif 'pdf' in error_msg.lower():
                stats['pdf_files'] += 1

            # Only log first 50 errors
            if len(stats['errors']) < 50:
                stats['errors'].append({
                    'doc_id': doc_id,
                    'title': title[:100] if title else 'N/A',
                    'error': error_msg,
                    'path': saved_path[:100]
                })

    # Final commit
    if not dry_run:
        conn.commit()
        print("\n\nFinal commit completed")

    conn.close()

    # Update statistics
    stats['end_time'] = datetime.now().isoformat()
    stats['dry_run'] = dry_run

    # Print summary
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"Total documents: {total_docs:,}")
    print(f"Successful: {stats['successful']:,} ({100*stats['successful']/total_docs:.1f}%)")
    print(f"Failed: {stats['failed']:,} ({100*stats['failed']/total_docs:.1f}%)")
    print(f"  - PDF files (skipped): {stats['pdf_files']:,}")
    print(f"  - File not found: {stats['file_not_found']:,}")
    print(f"  - Content too short: {stats['content_too_short']:,}")
    print(f"  - Other errors: {stats['failed'] - stats['file_not_found'] - stats['content_too_short'] - stats['pdf_files']:,}")

    if stats['successful'] > 0:
        avg_length = sum(s['content_length'] for s in stats['samples']) / len(stats['samples'])
        print(f"\nAverage content length (sample): {avg_length:,.0f} characters")

    # Save log
    os.makedirs(os.path.dirname(LOG_FILE) if os.path.dirname(LOG_FILE) else '.', exist_ok=True)
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"\nDetailed log saved to: {LOG_FILE}")

    # Show sample extractions
    if stats['samples']:
        print("\n" + "="*80)
        print("SAMPLE EXTRACTIONS (first 3)")
        print("="*80)
        for i, sample in enumerate(stats['samples'][:3], 1):
            print(f"\n--- Sample {i} ---")
            # Handle Unicode in output
            try:
                print(f"Title: {sample['title']}")
                print(f"Publisher: {sample['publisher']}")
                print(f"Length: {sample['content_length']:,} characters")
                preview = sample['content_preview'][:300].encode('ascii', errors='replace').decode('ascii')
                print(f"Preview:\n{preview}...")
            except Exception as e:
                print(f"Error displaying sample: {e}")

    # Show errors if any
    if stats['errors']:
        print("\n" + "="*80)
        print(f"ERRORS (showing first 10 of {len(stats['errors'])})")
        print("="*80)
        for i, error in enumerate(stats['errors'][:10], 1):
            print(f"\n{i}. {error.get('title', 'N/A')[:60]}")
            print(f"   Error: {error['error']}")

    return stats

if __name__ == "__main__":
    import sys

    # Parse arguments
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv

    # Check for limit
    limit = None
    for arg in sys.argv:
        if arg.startswith('--limit='):
            limit = int(arg.split('=')[1])
        elif arg.startswith('-l'):
            try:
                limit = int(sys.argv[sys.argv.index(arg) + 1])
            except:
                pass

    # Show help
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
HTML Content Extraction Pipeline

Usage:
  python extract_html_content.py [options]

Options:
  --dry-run, -n          Test mode, don't update database
  --limit=N, -l N        Process only first N documents
  --help, -h             Show this help

Examples:
  # Test on 10 documents
  python extract_html_content.py --dry-run --limit=10

  # Process first 100 documents
  python extract_html_content.py --limit=100

  # Process all documents
  python extract_html_content.py
""")
        sys.exit(0)

    # Run extraction
    process_documents(dry_run=dry_run, limit=limit)
