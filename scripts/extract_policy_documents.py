#!/usr/bin/env python3
"""
Chinese Policy Documents - Full Text Extraction and Database Ingestion
Extracts text from 38 policy documents and ingests into OSINT database

Features:
- Multi-method PDF extraction (PyPDF2, pdfplumber, pdfminer)
- HTML content extraction with BeautifulSoup
- Quality assurance validation
- Structured data extraction
- Cross-reference preparation
"""

import os
import sys
import json
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime
import re

# PDF extraction libraries
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    print("[WARNING] PyPDF2 not available")

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    print("[WARNING] pdfplumber not available")

# HTML extraction
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("[WARNING] BeautifulSoup not available")

# Configuration
BASE_DIR = Path("F:/Policy_Documents_Sweep")
DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
OUTPUT_DIR = Path("C:/Projects/OSINT-Foresight/analysis/policy_extraction")
OUTPUT_DIR.mkdir(exist_ok=True)

# Priority levels
CRITICAL_DIRS = [
    "CRITICAL/ai_strategy",
    "CRITICAL/policy_strategy",
    "CRITICAL/talent_programs",
    "CRITICAL/national_security",
    "CRITICAL/technology_policy",
    "CRITICAL/intellectual_property"
]

HIGH_PRIORITY_DIRS = [
    "HIGH_PRIORITY"
]

MEDIUM_PRIORITY_DIRS = [
    "MEDIUM_PRIORITY"
]

class PolicyDocumentExtractor:
    """Extract text and metadata from policy documents"""

    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.extraction_stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'warnings': [],
            'errors': []
        }

    def connect_db(self):
        """Connect to OSINT database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def create_schema(self):
        """Create database tables for policy documents"""
        cursor = self.conn.cursor()

        # Main documents table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chinese_policy_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            title TEXT,
            category TEXT,
            subcategory TEXT,
            priority_level TEXT,

            -- Metadata
            issuing_agency TEXT,
            publication_date DATE,
            effective_date DATE,
            document_type TEXT,
            translation_source TEXT,
            original_language TEXT DEFAULT 'Chinese',

            -- File information
            file_path TEXT,
            file_size_bytes INTEGER,
            sha256_hash TEXT,

            -- Content
            full_text TEXT,
            full_text_length INTEGER,
            extraction_method TEXT,
            extraction_quality_score REAL,

            -- Processing metadata
            extracted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            extraction_warnings TEXT,

            -- Cross-reference flags
            mentions_soes INTEGER DEFAULT 0,
            mentions_technologies INTEGER DEFAULT 0,
            has_quantitative_targets INTEGER DEFAULT 0,
            has_timeline INTEGER DEFAULT 0
        )
        """)

        # Policy provisions table (structured extracts)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS policy_provisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            provision_type TEXT,
            section_number TEXT,
            article_number TEXT,
            provision_text TEXT,

            -- Structured data
            quantitative_value REAL,
            quantitative_unit TEXT,
            target_year INTEGER,
            technology_domain TEXT,

            FOREIGN KEY (document_id) REFERENCES chinese_policy_documents(document_id)
        )
        """)

        # Technology domains mentioned
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS policy_technology_domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            technology_domain TEXT NOT NULL,
            priority_level TEXT,
            self_sufficiency_target REAL,
            target_year INTEGER,
            context TEXT,

            FOREIGN KEY (document_id) REFERENCES chinese_policy_documents(document_id)
        )
        """)

        # Timeline and milestones
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS policy_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            milestone_date DATE,
            milestone_year INTEGER,
            milestone_description TEXT,
            milestone_type TEXT,
            quantitative_target REAL,

            FOREIGN KEY (document_id) REFERENCES chinese_policy_documents(document_id)
        )
        """)

        # Entity references (SOEs, agencies, institutions)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS policy_entity_references (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            entity_name TEXT NOT NULL,
            entity_type TEXT,
            role_description TEXT,
            is_soe INTEGER DEFAULT 0,

            FOREIGN KEY (document_id) REFERENCES chinese_policy_documents(document_id)
        )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_category ON chinese_policy_documents(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_priority ON chinese_policy_documents(priority_level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_pub_date ON chinese_policy_documents(publication_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tech_domain ON policy_technology_domains(technology_domain)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeline_year ON policy_timeline(milestone_year)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_name ON policy_entity_references(entity_name)")

        # Full text search
        cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS policy_fts USING fts5(
            document_id UNINDEXED,
            title,
            full_text,
            content=chinese_policy_documents,
            content_rowid=id
        )
        """)

        self.conn.commit()
        print("[OK] Database schema created successfully")

    def extract_pdf_pypdf2(self, pdf_path):
        """Extract text using PyPDF2"""
        if not HAS_PYPDF2:
            return None, "PyPDF2 not available"

        try:
            text_parts = []
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(reader.pages):
                    try:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                    except Exception as e:
                        print(f"[WARNING] Page {page_num} extraction failed: {e}")

            full_text = "\n\n".join(text_parts)
            return full_text, "pypdf2"
        except Exception as e:
            return None, f"PyPDF2 error: {e}"

    def extract_pdf_pdfplumber(self, pdf_path):
        """Extract text using pdfplumber (better for tables)"""
        if not HAS_PDFPLUMBER:
            return None, "pdfplumber not available"

        try:
            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)

                        # Extract tables separately
                        tables = page.extract_tables()
                        if tables:
                            for table in tables:
                                table_text = "\n".join(["\t".join(str(cell) for cell in row) for row in table if row])
                                text_parts.append(f"\n[TABLE]\n{table_text}\n[/TABLE]\n")
                    except Exception as e:
                        print(f"[WARNING] Page {page_num} extraction failed: {e}")

            full_text = "\n\n".join(text_parts)
            return full_text, "pdfplumber"
        except Exception as e:
            return None, f"pdfplumber error: {e}"

    def extract_html(self, html_path):
        """Extract text from HTML files"""
        if not HAS_BS4:
            return None, "BeautifulSoup not available"

        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            return text, "beautifulsoup"
        except Exception as e:
            return None, f"HTML extraction error: {e}"

    def validate_extraction_quality(self, pdf_path, extracted_text):
        """Validate extraction quality based on file size / text ratio"""
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

    def extract_document(self, file_path, metadata=None):
        """Extract text from a single document with multi-method fallback"""
        file_path = Path(file_path)

        print(f"\n[EXTRACTING] {file_path.name}")

        # Determine file type
        if file_path.suffix.lower() == '.pdf':
            # Try pdfplumber first (better for tables)
            text, method = self.extract_pdf_pdfplumber(file_path)

            # Fallback to PyPDF2 if pdfplumber fails
            if not text or len(text) < 100:
                print(f"[FALLBACK] Trying PyPDF2...")
                text, method = self.extract_pdf_pypdf2(file_path)

        elif file_path.suffix.lower() in ['.htm', '.html']:
            text, method = self.extract_html(file_path)

        else:
            return {
                'success': False,
                'error': f"Unsupported file type: {file_path.suffix}"
            }

        # Validate extraction
        if not text:
            return {
                'success': False,
                'error': method,
                'file_path': str(file_path)
            }

        quality_score, quality_flag = self.validate_extraction_quality(file_path, text)

        # Load metadata if available
        if not metadata:
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

        return {
            'success': True,
            'file_path': str(file_path),
            'filename': file_path.name,
            'full_text': text,
            'full_text_length': len(text),
            'extraction_method': method,
            'quality_score': quality_score,
            'quality_flag': quality_flag,
            'sha256_hash': sha256_hash,
            'file_size_bytes': os.path.getsize(file_path),
            'metadata': metadata
        }

    def insert_document(self, extraction_result):
        """Insert extracted document into database"""
        if not extraction_result['success']:
            print(f"[SKIP] {extraction_result.get('file_path', 'unknown')}: {extraction_result.get('error')}")
            self.extraction_stats['failed'] += 1
            return

        cursor = self.conn.cursor()
        metadata = extraction_result['metadata']

        # Generate document ID
        doc_id = metadata.get('document_id') or hashlib.md5(
            extraction_result['filename'].encode()
        ).hexdigest()[:16]

        # Extract category from file path
        file_path = Path(extraction_result['file_path'])
        path_parts = file_path.parts

        category = "unknown"
        subcategory = "unknown"
        priority_level = "MEDIUM"

        if "CRITICAL" in path_parts:
            priority_level = "CRITICAL"
            # Find category after CRITICAL
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

        # Insert main document
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
                extraction_result['filename'],
                metadata.get('title', extraction_result['filename']),
                category,
                subcategory,
                priority_level,
                metadata.get('issuing_agency'),
                metadata.get('publication_date'),
                metadata.get('document_type'),
                metadata.get('translation_source'),
                extraction_result['file_path'],
                extraction_result['file_size_bytes'],
                extraction_result['sha256_hash'],
                extraction_result['full_text'],
                extraction_result['full_text_length'],
                extraction_result['extraction_method'],
                extraction_result['quality_score'],
                extraction_result['quality_flag']
            ))

            # Update FTS index
            cursor.execute("""
            INSERT OR REPLACE INTO policy_fts(document_id, title, full_text)
            VALUES (?, ?, ?)
            """, (
                doc_id,
                metadata.get('title', extraction_result['filename']),
                extraction_result['full_text']
            ))

            self.conn.commit()

            print(f"[OK] Inserted: {extraction_result['filename']}")
            print(f"     Quality: {extraction_result['quality_flag']} ({extraction_result['quality_score']:.2f})")
            print(f"     Text length: {extraction_result['full_text_length']:,} chars")

            self.extraction_stats['successful'] += 1

            if extraction_result['quality_score'] < 0.8:
                self.extraction_stats['warnings'].append(
                    f"{extraction_result['filename']}: {extraction_result['quality_flag']}"
                )

        except Exception as e:
            print(f"[ERROR] Database insertion failed: {e}")
            self.extraction_stats['errors'].append(str(e))
            self.extraction_stats['failed'] += 1

    def process_directory(self, directory):
        """Process all documents in a directory"""
        directory = Path(directory)

        if not directory.exists():
            print(f"[ERROR] Directory not found: {directory}")
            return

        # Find all PDF and HTML files
        pdf_files = list(directory.rglob("*.pdf"))
        html_files = list(directory.rglob("*.htm")) + list(directory.rglob("*.html"))

        all_files = pdf_files + html_files

        print(f"\n[INFO] Found {len(all_files)} files in {directory}")
        print(f"       PDFs: {len(pdf_files)}, HTML: {len(html_files)}")

        for file_path in all_files:
            self.extraction_stats['total_files'] += 1
            result = self.extract_document(file_path)
            self.insert_document(result)

    def print_summary(self):
        """Print extraction summary"""
        print("\n" + "="*70)
        print("EXTRACTION SUMMARY")
        print("="*70)
        print(f"Total files processed: {self.extraction_stats['total_files']}")
        print(f"Successful: {self.extraction_stats['successful']}")
        print(f"Failed: {self.extraction_stats['failed']}")

        if self.extraction_stats['warnings']:
            print(f"\nWarnings ({len(self.extraction_stats['warnings'])}):")
            for warning in self.extraction_stats['warnings'][:10]:
                print(f"  - {warning}")
            if len(self.extraction_stats['warnings']) > 10:
                print(f"  ... and {len(self.extraction_stats['warnings']) - 10} more")

        if self.extraction_stats['errors']:
            print(f"\nErrors ({len(self.extraction_stats['errors'])}):")
            for error in self.extraction_stats['errors'][:5]:
                print(f"  - {error}")

        print("="*70)

        # Save detailed log
        log_path = OUTPUT_DIR / f"extraction_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.extraction_stats, f, indent=2, ensure_ascii=False)
        print(f"\nDetailed log saved to: {log_path}")


def main():
    """Main execution"""
    print("="*70)
    print("CHINESE POLICY DOCUMENTS - FULL TEXT EXTRACTION")
    print("="*70)

    # Check for required libraries
    missing_libs = []
    if not HAS_PYPDF2:
        missing_libs.append("PyPDF2")
    if not HAS_PDFPLUMBER:
        missing_libs.append("pdfplumber")
    if not HAS_BS4:
        missing_libs.append("beautifulsoup4")

    if missing_libs:
        print(f"\n[WARNING] Missing libraries: {', '.join(missing_libs)}")
        print("Install with: pip install PyPDF2 pdfplumber beautifulsoup4 lxml")

        if not HAS_PYPDF2 and not HAS_PDFPLUMBER:
            print("\n[ERROR] At least one PDF extraction library required!")
            return 1

    # Initialize extractor
    extractor = PolicyDocumentExtractor(DB_PATH)
    extractor.connect_db()

    # Create schema
    print("\n[STEP 1] Creating database schema...")
    extractor.create_schema()

    # Process CRITICAL documents first
    print("\n[STEP 2] Processing CRITICAL priority documents...")
    for subdir in CRITICAL_DIRS:
        full_path = BASE_DIR / subdir
        if full_path.exists():
            print(f"\n--- Processing: {subdir} ---")
            extractor.process_directory(full_path)

    # Process HIGH priority documents
    print("\n[STEP 3] Processing HIGH priority documents...")
    for subdir in HIGH_PRIORITY_DIRS:
        full_path = BASE_DIR / subdir
        if full_path.exists():
            print(f"\n--- Processing: {subdir} ---")
            extractor.process_directory(full_path)

    # Process MEDIUM priority documents
    print("\n[STEP 4] Processing MEDIUM priority documents...")
    for subdir in MEDIUM_PRIORITY_DIRS:
        full_path = BASE_DIR / subdir
        if full_path.exists():
            print(f"\n--- Processing: {subdir} ---")
            extractor.process_directory(full_path)

    # Print summary
    extractor.print_summary()

    # Close connection
    extractor.conn.close()

    print("\n[COMPLETE] Full text extraction finished")
    return 0


if __name__ == "__main__":
    sys.exit(main())
