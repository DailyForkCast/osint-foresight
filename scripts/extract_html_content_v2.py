#!/usr/bin/env python3
"""
HTML Content Extraction Pipeline v2
Two-phase approach: Extract to JSON, then batch update database
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
EXTRACTION_OUTPUT = 'analysis/html_extractions.jsonl'
LOG_FILE = 'analysis/html_extraction_log_v2.json'

# HTML cleaning configuration
REMOVE_TAGS = ['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']
MIN_CONTENT_LENGTH = 100

def extract_text_from_html(html_path):
    """Extract clean text from HTML file"""
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()

        # Check if PDF
        if html_content.strip().startswith('%PDF'):
            return None, False, "File is PDF, not HTML"

        if len(html_content.strip()) < 100:
            return None, False, "HTML file too short"

        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove unwanted elements
        for tag in REMOVE_TAGS:
            for element in soup.find_all(tag):
                element.decompose()

        # Try to find main content
        main_content = None
        for selector in ['article', 'main', '[role="main"]', '.content', '.main-content']:
            main_content = soup.select_one(selector)
            if main_content:
                break

        if not main_content:
            main_content = soup.find('body') or soup

        # Extract text
        text = main_content.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        if len(text) < MIN_CONTENT_LENGTH:
            return None, False, f"Content too short: {len(text)} chars"

        return text, True, None

    except Exception as e:
        return None, False, str(e)

def phase1_extract_to_json(limit=None):
    """Phase 1: Extract all HTML to JSON file"""
    print("="*80)
    print("PHASE 1: EXTRACT HTML TO JSON")
    print("="*80)

    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    cursor = conn.cursor()

    query = '''
        SELECT id, saved_path, document_type, publisher_org, title
        FROM documents
        WHERE content_text = ''
          AND saved_path IS NOT NULL
    '''
    if limit:
        query += f' LIMIT {limit}'

    cursor.execute(query)
    documents = cursor.fetchall()
    conn.close()

    total = len(documents)
    print(f"Found {total:,} documents to process\n")

    stats = {
        'total': total,
        'successful': 0,
        'failed': 0,
        'pdf_files': 0,
        'file_not_found': 0,
        'content_too_short': 0
    }

    # Extract and save to JSONL
    os.makedirs(os.path.dirname(EXTRACTION_OUTPUT), exist_ok=True)

    with open(EXTRACTION_OUTPUT, 'w', encoding='utf-8') as out_file:
        for doc_id, saved_path, doc_type, publisher, title in tqdm(documents, desc="Extracting HTML"):
            if not os.path.exists(saved_path):
                stats['file_not_found'] += 1
                continue

            text, success, error = extract_text_from_html(saved_path)

            if success:
                stats['successful'] += 1
                result = {
                    'id': doc_id,
                    'content_text': text,
                    'content_length': len(text)
                }
                out_file.write(json.dumps(result, ensure_ascii=False) + '\n')
            else:
                stats['failed'] += 1
                if 'pdf' in error.lower():
                    stats['pdf_files'] += 1
                elif 'not found' in error.lower():
                    stats['file_not_found'] += 1
                elif 'too short' in error.lower():
                    stats['content_too_short'] += 1

    print(f"\n{'='*80}")
    print("PHASE 1 COMPLETE")
    print(f"{'='*80}")
    print(f"Successful: {stats['successful']:,}")
    print(f"Failed: {stats['failed']:,}")
    print(f"  - PDFs: {stats['pdf_files']:,}")
    print(f"  - File not found: {stats['file_not_found']:,}")
    print(f"  - Too short: {stats['content_too_short']:,}")
    print(f"\nExtractions saved to: {EXTRACTION_OUTPUT}")

    with open(LOG_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

    return stats

def phase2_update_database():
    """Phase 2: Batch update database from JSON"""
    print(f"\n{'='*80}")
    print("PHASE 2: UPDATE DATABASE")
    print(f"{'='*80}")

    if not os.path.exists(EXTRACTION_OUTPUT):
        print(f"ERROR: {EXTRACTION_OUTPUT} not found. Run phase 1 first.")
        return

    # Read extractions
    extractions = []
    with open(EXTRACTION_OUTPUT, 'r', encoding='utf-8') as f:
        for line in f:
            extractions.append(json.loads(line))

    print(f"Loaded {len(extractions):,} extractions")

    # Update database
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    cursor = conn.cursor()

    print("Updating database (this may take a few minutes)...")

    for i, extraction in enumerate(tqdm(extractions, desc="Updating DB"), 1):
        cursor.execute('''
            UPDATE documents
            SET content_text = ?,
                content_length = ?,
                updated_at = ?
            WHERE id = ?
        ''', (
            extraction['content_text'],
            extraction['content_length'],
            datetime.now().isoformat(),
            extraction['id']
        ))

        # Commit every 100 rows
        if i % 100 == 0:
            conn.commit()

    conn.commit()
    conn.close()

    print(f"\n{'='*80}")
    print("PHASE 2 COMPLETE")
    print(f"{'='*80}")
    print(f"Updated {len(extractions):,} documents in database")

if __name__ == "__main__":
    import sys

    limit = None
    for arg in sys.argv:
        if arg.startswith('--limit='):
            limit = int(arg.split('=')[1])

    if '--help' in sys.argv:
        print("""
HTML Content Extraction Pipeline v2 (Two-Phase)

Usage:
  python extract_html_content_v2.py [--limit=N]

This runs both phases:
  Phase 1: Extract HTML to JSON file
  Phase 2: Batch update database

Or run phases separately:
  python -c "from extract_html_content_v2 import phase1_extract_to_json; phase1_extract_to_json()"
  python -c "from extract_html_content_v2 import phase2_update_database; phase2_update_database()"
""")
        sys.exit(0)

    # Run both phases
    stats = phase1_extract_to_json(limit=limit)
    if stats['successful'] > 0:
        phase2_update_database()
    else:
        print("\nNo successful extractions, skipping database update")
