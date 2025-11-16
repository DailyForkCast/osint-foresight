#!/usr/bin/env python3
"""
Retry failed PDF extractions using PyMuPDF (fitz)
PyMuPDF is often better at extracting text from complex PDFs
"""

import os
import sys
import json
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("[ERROR] PyMuPDF not available. Install with: pip install pymupdf")
    sys.exit(1)

# Configuration
BASE_DIR = Path("F:/Policy_Documents_Sweep")
DB_PATH = Path("C:/Projects/OSINT-Foresight/database/osint_master.db")

# Failed documents to retry
FAILED_DOCS = [
    "CRITICAL/talent_programs/CSET_Key Economic and Technical Foreign Experts Plan/CSET_Key Economic and Technical Foreign Experts Plan.pdf",
    "CRITICAL/talent_programs/CSET_Funding Program for Overseas Students in S&T Activities/CSET_Funding Program for Overseas Students in S&T Activities.pdf",
    "CRITICAL/talent_programs/International Training Program for Artificial Intelligence Talents in Chinese Universities - Expert Forum/International Training Program for Artificial Intelligence Talents in Chinese Universities - Expert Forum.pdf",
    "CRITICAL/intellectual_property/Lexology_Regulations_of_the_State_Council_on_Handling_Foreign-Related_Intellectual_Property_Disputes/Lexology_Regulations_of_the_State_Council_on_Handling_Foreign-Related_Intellectual_Property_Disputes.pdf",
    "HIGH_PRIORITY/think_tank_analysis/Brookings_Unleashing_NQPF_Chinas_strategy_for_technology_led_growth/Brookings_Unleashing_NQPF_Chinas_strategy_for_technology_led_growth.pdf"
]

def extract_pdf_pymupdf(pdf_path):
    """Extract text using PyMuPDF (fitz)"""
    try:
        doc = fitz.open(pdf_path)
        text_parts = []

        for page_num, page in enumerate(doc):
            try:
                text = page.get_text()
                if text:
                    text_parts.append(text)

                # Also try extracting blocks with better formatting
                blocks = page.get_text("blocks")
                if blocks and len(blocks) > 0:
                    print(f"  Page {page_num + 1}: {len(blocks)} text blocks")

            except Exception as e:
                print(f"[WARNING] Page {page_num + 1} extraction failed: {e}")

        doc.close()
        full_text = "\n\n".join(text_parts)
        return full_text, "pymupdf"

    except Exception as e:
        return None, f"PyMuPDF error: {e}"

def validate_extraction_quality(pdf_path, extracted_text):
    """Validate extraction quality"""
    if not extracted_text:
        return 0.0, "FAILED_NO_TEXT"

    file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    text_length_kb = len(extracted_text) / 1024

    if file_size_mb == 0:
        return 0.5, "UNKNOWN_SMALL_FILE"

    ratio = text_length_kb / file_size_mb

    # Quality scoring
    if ratio < 3:
        return 0.3, "WARNING_LOW_EXTRACTION"
    elif ratio > 50:
        return 0.6, "WARNING_POSSIBLE_DUPLICATION"
    elif 5 <= ratio <= 30:
        return 1.0, "EXCELLENT"
    elif 3 <= ratio < 5 or 30 < ratio <= 50:
        return 0.8, "GOOD"
    else:
        return 0.5, "UNCERTAIN"

def insert_document(conn, file_path, extracted_text, extraction_method, quality_score, quality_flag):
    """Insert extracted document into database"""
    cursor = conn.cursor()

    file_path = Path(file_path)

    # Load metadata if available
    metadata_path = file_path.parent / "metadata.json"
    if metadata_path.exists():
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except Exception as e:
            print(f"[WARNING] Metadata load failed: {e}")
            metadata = {}
    else:
        metadata = {}

    # Calculate hash
    with open(file_path, 'rb') as f:
        sha256_hash = hashlib.sha256(f.read()).hexdigest()

    # Generate document ID
    doc_id = metadata.get('document_id') or hashlib.md5(
        file_path.name.encode()
    ).hexdigest()[:16]

    # Extract category from path
    path_parts = file_path.parts
    category = "unknown"
    subcategory = "unknown"
    priority_level = "MEDIUM"

    if "CRITICAL" in path_parts:
        priority_level = "CRITICAL"
        for i, part in enumerate(path_parts):
            if part == "CRITICAL" and i + 1 < len(path_parts):
                category = path_parts[i + 1]
                if i + 2 < len(path_parts):
                    subcategory = path_parts[i + 2]
                break
    elif "HIGH_PRIORITY" in path_parts:
        priority_level = "HIGH"
        for i, part in enumerate(path_parts):
            if part == "HIGH_PRIORITY" and i + 1 < len(path_parts):
                category = path_parts[i + 1]
                if i + 2 < len(path_parts):
                    subcategory = path_parts[i + 2]
                break

    # Insert or update
    try:
        cursor.execute("""
        INSERT OR REPLACE INTO chinese_policy_documents (
            document_id, filename, title, category, subcategory, priority_level,
            issuing_agency, publication_date, document_type, translation_source,
            file_path, file_size_bytes, sha256_hash,
            full_text, full_text_length, extraction_method, extraction_quality_score,
            extraction_warnings
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            file_path.name,
            metadata.get('title', file_path.name),
            category,
            subcategory,
            priority_level,
            metadata.get('issuing_agency'),
            metadata.get('publication_date'),
            metadata.get('document_type'),
            metadata.get('translation_source'),
            str(file_path),
            os.path.getsize(file_path),
            sha256_hash,
            extracted_text,
            len(extracted_text),
            extraction_method,
            quality_score,
            quality_flag
        ))

        # Update FTS index
        cursor.execute("""
        INSERT OR REPLACE INTO policy_fts(document_id, title, full_text)
        VALUES (?, ?, ?)
        """, (
            doc_id,
            metadata.get('title', file_path.name),
            extracted_text
        ))

        conn.commit()
        return True

    except Exception as e:
        print(f"[ERROR] Database insertion failed: {e}")
        return False

def main():
    """Retry failed extractions"""
    print("="*80)
    print("RETRY FAILED EXTRACTIONS USING PYMUPDF")
    print("="*80)
    print()

    if not HAS_PYMUPDF:
        print("[ERROR] PyMuPDF not available")
        return 1

    # Connect to database
    conn = sqlite3.connect(DB_PATH)

    results = {
        'total': len(FAILED_DOCS),
        'successful': 0,
        'failed': 0,
        'details': []
    }

    for doc_path in FAILED_DOCS:
        full_path = BASE_DIR / doc_path

        if not full_path.exists():
            print(f"[SKIP] File not found: {full_path.name}")
            results['failed'] += 1
            results['details'].append({
                'file': str(full_path.name),
                'status': 'not_found'
            })
            continue

        print(f"\n[EXTRACTING] {full_path.name}")
        print(f"  Size: {os.path.getsize(full_path) / (1024*1024):.2f} MB")

        # Extract using PyMuPDF
        text, method = extract_pdf_pymupdf(full_path)

        if not text or len(text) < 100:
            print(f"[FAILED] Extraction yielded no text or too little text")
            print(f"  Method: {method}")
            print(f"  Text length: {len(text) if text else 0}")
            results['failed'] += 1
            results['details'].append({
                'file': str(full_path.name),
                'status': 'failed',
                'error': method
            })
            continue

        # Validate quality
        quality_score, quality_flag = validate_extraction_quality(full_path, text)

        print(f"[SUCCESS] Extracted {len(text):,} characters")
        print(f"  Method: {method}")
        print(f"  Quality: {quality_flag} ({quality_score:.2f})")

        # Insert into database
        if insert_document(conn, full_path, text, method, quality_score, quality_flag):
            print(f"[OK] Inserted into database")
            results['successful'] += 1
            results['details'].append({
                'file': str(full_path.name),
                'status': 'success',
                'chars': len(text),
                'quality': quality_flag
            })
        else:
            print(f"[ERROR] Database insertion failed")
            results['failed'] += 1
            results['details'].append({
                'file': str(full_path.name),
                'status': 'db_error'
            })

    conn.close()

    # Print summary
    print("\n" + "="*80)
    print("RETRY SUMMARY")
    print("="*80)
    print(f"Total attempted: {results['total']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print()

    if results['successful'] > 0:
        print("Successfully extracted:")
        for detail in results['details']:
            if detail['status'] == 'success':
                print(f"  ✓ {detail['file'][:60]} - {detail['chars']:,} chars ({detail['quality']})")

    if results['failed'] > 0:
        print("\nStill failed:")
        for detail in results['details']:
            if detail['status'] != 'success':
                print(f"  ✗ {detail['file'][:60]}")

    print("="*80)

    # Save detailed results
    output_file = Path("C:/Projects/OSINT-Foresight/analysis/policy_extraction") / f"retry_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nDetailed results saved to: {output_file}")

    return 0 if results['successful'] == results['total'] else 1

if __name__ == "__main__":
    sys.exit(main())
