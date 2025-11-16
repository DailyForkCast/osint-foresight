#!/usr/bin/env python3
"""
Policy Document Processor
Downloads, extracts text, and processes policy documents

ZERO FABRICATION PROTOCOL:
- Only extract text that actually exists in documents
- Mark fields as NULL if extraction fails
- Document extraction quality and issues
- No inference or guessing
"""

import sqlite3
import requests
import hashlib
import os
from pathlib import Path
from datetime import datetime
import json
import time

# PDF processing libraries
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("WARNING: PyPDF2 not available - PDF text extraction limited")

def download_document(url, save_path, timeout=30):
    """
    Download document from URL

    Returns: (success, file_path, error_message)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()

        # Save file
        with open(save_path, 'wb') as f:
            f.write(response.content)

        return True, save_path, None

    except requests.exceptions.Timeout:
        return False, None, f"Timeout after {timeout}s"
    except requests.exceptions.RequestException as e:
        return False, None, f"Download error: {str(e)}"
    except Exception as e:
        return False, None, f"Unexpected error: {str(e)}"

def extract_pdf_text(pdf_path):
    """
    Extract text from PDF

    Returns: (success, text, metadata, error_message)
    """
    if not PDF_AVAILABLE:
        return False, None, None, "PyPDF2 not installed"

    try:
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)

            # Extract metadata
            metadata = {
                'pages': len(pdf_reader.pages),
                'encrypted': pdf_reader.is_encrypted
            }

            # Try to get PDF info
            if pdf_reader.metadata:
                metadata['title'] = pdf_reader.metadata.get('/Title', None)
                metadata['author'] = pdf_reader.metadata.get('/Author', None)
                metadata['creation_date'] = pdf_reader.metadata.get('/CreationDate', None)

            # Extract text from all pages
            text_parts = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    print(f"  Warning: Could not extract text from page {page_num+1}: {e}")

            full_text = '\n\n'.join(text_parts)

            # Check if we got meaningful text
            if len(full_text.strip()) < 100:
                return False, None, metadata, "Insufficient text extracted (likely scanned PDF - needs OCR)"

            return True, full_text, metadata, None

    except Exception as e:
        return False, None, None, f"PDF extraction error: {str(e)}"

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def extract_first_page_summary(text, max_chars=2000):
    """
    Extract first page or first N characters as summary
    NOT an analytical summary - just the document's own text
    """
    if not text:
        return None

    # Take first max_chars characters
    summary = text[:max_chars].strip()

    if len(text) > max_chars:
        # Try to break at sentence
        last_period = summary.rfind('.')
        if last_period > max_chars * 0.7:  # If we found a period in last 30%
            summary = summary[:last_period + 1]

    return summary

def process_policy_document(document_id, db_path, download_dir):
    """
    Process a single policy document:
    1. Download from URL
    2. Extract text
    3. Update database with extracted content

    Returns: (success, message)
    """
    conn = sqlite3.connect(db_path, timeout=30.0)
    cursor = conn.cursor()

    # Get document info
    cursor.execute('''
        SELECT document_title, document_url, country_code
        FROM policy_documents
        WHERE document_id = ?
    ''', (document_id,))

    result = cursor.fetchone()
    if not result:
        conn.close()
        return False, f"Document {document_id} not found in database"

    title, url, country_code = result

    print(f"\nProcessing: {title}")
    print(f"  URL: {url}")

    # Create download directory if needed
    country_dir = Path(download_dir) / country_code
    country_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename from document_id
    filename = f"{document_id}.pdf"
    save_path = country_dir / filename

    # Download document
    print(f"  Downloading...")
    success, file_path, error = download_document(url, save_path)

    if not success:
        print(f"  [FAIL] Download failed: {error}")

        # Update database with failure info
        cursor.execute('''
            UPDATE policy_documents
            SET document_text = NULL,
                summary = NULL
            WHERE document_id = ?
        ''', (document_id,))
        conn.commit()
        conn.close()

        return False, f"Download failed: {error}"

    print(f"  [OK] Downloaded to {save_path}")

    # Calculate file hash
    file_hash = calculate_file_hash(save_path)
    file_size = os.path.getsize(save_path)

    # Extract text from PDF
    print(f"  Extracting text...")
    success, text, metadata, error = extract_pdf_text(save_path)

    extraction_status = {}

    if not success:
        print(f"  [FAIL] Text extraction failed: {error}")
        extraction_status = {
            'extraction_ok': False,
            'extraction_error': error,
            'needs_ocr': 'scanned PDF' in str(error).lower()
        }

        # Update database with metadata only
        cursor.execute('''
            UPDATE policy_documents
            SET document_text = NULL,
                summary = NULL
            WHERE document_id = ?
        ''', (document_id,))

    else:
        print(f"  [OK] Extracted {len(text)} characters")
        print(f"  [OK] Document has {metadata.get('pages', 'unknown')} pages")

        # Generate summary (first page text)
        summary = extract_first_page_summary(text, max_chars=2000)

        extraction_status = {
            'extraction_ok': True,
            'text_length': len(text),
            'pages': metadata.get('pages'),
            'pdf_metadata': metadata
        }

        # Update database with extracted text
        cursor.execute('''
            UPDATE policy_documents
            SET document_text = ?,
                summary = ?
            WHERE document_id = ?
        ''', (text, summary, document_id))

        print(f"  [OK] Updated database with extracted text")

    conn.commit()
    conn.close()

    if success:
        return True, f"Successfully processed {title}"
    else:
        return False, f"Downloaded but text extraction failed: {error}"

def process_all_documents(db_path, download_dir, limit=None, skip_existing=True):
    """
    Process all policy documents in database

    Args:
        db_path: Path to database
        download_dir: Directory to save downloaded files
        limit: Maximum number of documents to process (None = all)
        skip_existing: Skip documents that already have text extracted
    """
    conn = sqlite3.connect(db_path, timeout=30.0)
    cursor = conn.cursor()

    # Get documents to process
    if skip_existing:
        query = '''
            SELECT document_id, document_title
            FROM policy_documents
            WHERE document_text IS NULL
            ORDER BY country_code, publication_date DESC
        '''
    else:
        query = '''
            SELECT document_id, document_title
            FROM policy_documents
            ORDER BY country_code, publication_date DESC
        '''

    if limit:
        query += f' LIMIT {limit}'

    cursor.execute(query)
    documents = cursor.fetchall()
    conn.close()

    print("=" * 70)
    print("POLICY DOCUMENT PROCESSING")
    print("=" * 70)
    print(f"\nDocuments to process: {len(documents)}")
    print(f"Download directory: {download_dir}")
    print()

    successful = 0
    failed = 0

    for i, (doc_id, title) in enumerate(documents, 1):
        print(f"\n[{i}/{len(documents)}] Processing document...")

        success, message = process_policy_document(doc_id, db_path, download_dir)

        if success:
            successful += 1
        else:
            failed += 1

        # Rate limiting - be respectful to government servers
        if i < len(documents):
            print(f"\n  Waiting 2 seconds before next download...")
            time.sleep(2)

    print("\n" + "=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)
    print(f"\nSuccessful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(documents)}")
    print()

if __name__ == '__main__':
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    download_dir = "F:/OSINT_DATA/policy_documents"

    # Start with first 5 documents as a test
    print("Starting with first 5 documents as test run...")
    print()

    process_all_documents(
        db_path=db_path,
        download_dir=download_dir,
        limit=5,
        skip_existing=True
    )
