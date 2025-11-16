#!/usr/bin/env python3
"""
Federal Register Document Importer
Imports collected Federal Register documents into osint_master.db
"""

import sqlite3
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
FEDERAL_REGISTER_DIR = Path("F:/OSINT_DATA/us_gov_tech_sweep/files")

# Technology keywords for topic mapping
TECH_KEYWORDS = [
    "advanced technology", "emerging technology", "dual-use", "AI",
    "artificial intelligence", "foundation model", "machine learning",
    "quantum", "semiconductor", "microelectronics", "chip", "space", "LEO",
    "biotechnology", "biosecurity", "advanced materials", "robotics", "autonomy",
    "cybersecurity", "HPC", "photonic", "sensing", "additive manufacturing",
    "3D printing", "navigation", "timing", "GNSS", "PNT", "critical mineral",
    "rare earth", "export control", "ECCN", "EAR", "ITAR", "supply chain",
    "standards", "6G", "Open RAN"
]

# Agency mappings
AGENCY_MAPPING = {
    'DOC/NIST': 'National Institute of Standards and Technology (NIST)',
    'DOC/BIS': 'Bureau of Industry and Security (BIS)',
    'DOC/NTIA': 'National Telecommunications and Information Administration (NTIA)',
    'FCC': 'Federal Communications Commission (FCC)',
    'FTC': 'Federal Trade Commission (FTC)',
    'DOE': 'Department of Energy (DOE)',
    'DHS': 'Department of Homeland Security (DHS)',
    'DHS/CISA': 'Cybersecurity and Infrastructure Security Agency (CISA)',
    'State': 'Department of State',
    'Treasury': 'Department of the Treasury',
    'USTR': 'Office of the U.S. Trade Representative',
    'NASA': 'National Aeronautics and Space Administration (NASA)',
    'NSF': 'National Science Foundation (NSF)',
    'DoD': 'Department of Defense (DoD)'
}


class FederalRegisterImporter:
    """Import Federal Register documents into osint_master.db"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        self.stats = {
            'total_files': 0,
            'processed': 0,
            'inserted': 0,
            'skipped_duplicates': 0,
            'errors': 0
        }

    def connect(self):
        """Connect to database"""
        logger.info(f"Connecting to database: {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def check_schema(self):
        """Check database schema"""
        logger.info("Checking database schema...")

        cursor = self.conn.cursor()

        # Check if tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name = 'thinktank_reports'
        """)

        if not cursor.fetchone():
            logger.error("thinktank_reports table not found!")
            return False

        # Get column info
        cursor.execute("PRAGMA table_info(thinktank_reports)")
        columns = [row[1] for row in cursor.fetchall()]
        logger.info(f"Found {len(columns)} columns in thinktank_reports")

        return True

    def parse_filename(self, filename: str) -> Dict:
        """Parse Federal Register filename to extract metadata"""
        # Format: YYYY_federal_register_DOC_NUMBER_title_slug.pdf
        match = re.match(r'(\d{4})_federal_register_(\d{4}-\d+)_(.+)\.pdf', filename)

        if not match:
            return None

        year = int(match.group(1))
        fr_doc_number = match.group(2)
        title_slug = match.group(3).replace('_', ' ').title()

        return {
            'year': year,
            'fr_doc_number': fr_doc_number,
            'title_slug': title_slug,
            'filename': filename
        }

    def extract_topics(self, title: str) -> List[str]:
        """Extract matching topics from title"""
        topics = []
        title_lower = title.lower()

        for keyword in TECH_KEYWORDS:
            if keyword.lower() in title_lower:
                topics.append(keyword)

        return topics

    def get_or_create_source(self, source_name: str) -> int:
        """Get or create thinktank source"""
        cursor = self.conn.cursor()

        # Check if source exists
        cursor.execute("""
            SELECT id FROM thinktank_sources
            WHERE organization_name = ?
        """, (source_name,))

        row = cursor.fetchone()
        if row:
            return row[0]

        # Create new source
        cursor.execute("""
            INSERT INTO thinktank_sources (
                organization_name,
                organization_type,
                country,
                website_url,
                focus_areas,
                is_active
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            source_name,
            'government',
            'United States',
            'https://www.federalregister.gov',
            'Technology Policy, Regulations',
            1
        ))

        self.conn.commit()
        return cursor.lastrowid

    def import_document(self, file_path: Path) -> bool:
        """Import a single Federal Register document"""

        try:
            # Parse filename
            metadata = self.parse_filename(file_path.name)
            if not metadata:
                logger.warning(f"Could not parse filename: {file_path.name}")
                return False

            # Extract basic info
            year = metadata['year']
            fr_doc_number = metadata['fr_doc_number']
            title = metadata['title_slug']

            # Compute file hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            # Check if already exists
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT report_id FROM thinktank_reports WHERE file_hash = ? OR hash_sha256 = ?
            """, (file_hash, file_hash))

            if cursor.fetchone():
                logger.debug(f"Skipping duplicate: {file_path.name}")
                self.stats['skipped_duplicates'] += 1
                return True

            # Extract topics
            topics = self.extract_topics(title)

            # Determine source (agency) from filename or default to Federal Register
            source_name = "U.S. Federal Register"
            for abbrev, full_name in AGENCY_MAPPING.items():
                if abbrev.lower().replace('/', '_') in file_path.name.lower():
                    source_name = full_name
                    break

            # Get file size
            file_size = file_path.stat().st_size

            # Build canonical URL
            canonical_url = f"https://www.federalregister.gov/documents/{year}/{fr_doc_number.split('-')[0]}/{fr_doc_number.split('-')[1]}"

            # Insert document
            cursor.execute("""
                INSERT INTO thinktank_reports (
                    title,
                    source_organization,
                    publication_date,
                    collection_date,
                    file_path,
                    file_hash,
                    file_size,
                    hash_sha256,
                    url_origin,
                    url_canonical,
                    document_type,
                    doc_type,
                    publisher_type,
                    publisher_org,
                    language,
                    processing_notes,
                    mcf_flag,
                    europe_focus_flag,
                    arctic_flag
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title,
                source_name,
                f"{year}-01-01",  # We don't have exact date from filename
                datetime.now().isoformat(),
                str(file_path),
                file_hash,
                file_size,
                file_hash,  # hash_sha256
                canonical_url,
                canonical_url,  # url_canonical
                'regulation',
                'Federal Register Document',
                'government',
                source_name,
                'en',
                json.dumps({
                    'fr_doc_number': fr_doc_number,
                    'collection': 'Federal Register',
                    'topics': topics,
                    'year': year
                }),
                0,  # Not MCF
                0,  # Not Europe-specific
                0   # Not Arctic-specific
            ))

            report_id = cursor.lastrowid

            # Insert topics (if report_topics table exists)
            if topics:
                try:
                    for topic in topics:
                        cursor.execute("""
                            INSERT OR IGNORE INTO report_topics (report_id, topic_name)
                            VALUES (?, ?)
                        """, (report_id, topic))
                except sqlite3.OperationalError:
                    # report_topics table might not exist, that's okay
                    pass

            self.conn.commit()
            self.stats['inserted'] += 1

            if self.stats['inserted'] % 100 == 0:
                logger.info(f"Imported {self.stats['inserted']} documents...")

            return True

        except Exception as e:
            logger.error(f"Error importing {file_path.name}: {e}")
            self.stats['errors'] += 1
            return False

    def import_all(self, directory: Path):
        """Import all Federal Register documents"""
        logger.info(f"Starting import from: {directory}")

        # Get all PDF files
        pdf_files = sorted(directory.glob("*.pdf"))
        self.stats['total_files'] = len(pdf_files)

        logger.info(f"Found {self.stats['total_files']} PDF files")

        for pdf_file in pdf_files:
            self.import_document(pdf_file)
            self.stats['processed'] += 1

        logger.info("Import complete!")
        self.print_stats()

    def print_stats(self):
        """Print import statistics"""
        print("\n" + "="*60)
        print("FEDERAL REGISTER IMPORT STATISTICS")
        print("="*60)
        print(f"Total files found:      {self.stats['total_files']}")
        print(f"Files processed:        {self.stats['processed']}")
        print(f"Documents inserted:     {self.stats['inserted']}")
        print(f"Duplicates skipped:     {self.stats['skipped_duplicates']}")
        print(f"Errors:                 {self.stats['errors']}")
        print("="*60)


def main():
    """Main execution"""

    # Check paths
    if not DB_PATH.exists():
        logger.error(f"Database not found: {DB_PATH}")
        return

    if not FEDERAL_REGISTER_DIR.exists():
        logger.error(f"Federal Register directory not found: {FEDERAL_REGISTER_DIR}")
        return

    # Create importer
    importer = FederalRegisterImporter(DB_PATH)

    try:
        # Connect to database
        importer.connect()

        # Check schema
        if not importer.check_schema():
            logger.error("Schema check failed")
            return

        # Import all documents
        importer.import_all(FEDERAL_REGISTER_DIR)

    finally:
        importer.close()

    logger.info("Database import complete!")


if __name__ == '__main__':
    main()
