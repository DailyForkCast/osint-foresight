#!/usr/bin/env python3
"""
Document Warehouse Integration Loader
Loads Think Tank and Europe-China documents into OSINT Master Warehouse

Supports:
- Think Tank JSON documents
- Europe-China JSON documents
- Deduplication by hash_sha256
- Proper metadata mapping
- Incremental loading (skip existing hashes)
"""

import json
import sqlite3
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import sys

# Configuration
WAREHOUSE_DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")
TEST_WAREHOUSE_DB = Path("F:/OSINT_WAREHOUSE/osint_test.db")
THINKTANK_ROOT = Path("F:/ThinkTank_Sweeps")
EUROPECHINA_ROOT = Path("F:/Europe_China_Sweeps")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('warehouse_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WarehouseIntegrator:
    """Integrates document collections into OSINT warehouse"""

    def __init__(self, warehouse_path: Path):
        self.warehouse_path = warehouse_path
        self.conn = None
        self.stats = {
            "total_processed": 0,
            "inserted": 0,
            "duplicates_skipped": 0,
            "errors": 0
        }

    def connect(self):
        """Connect to warehouse database"""
        logger.info(f"Connecting to warehouse: {self.warehouse_path}")
        self.conn = sqlite3.connect(str(self.warehouse_path))
        self.conn.row_factory = sqlite3.Row
        logger.info("Connected successfully")

    def ensure_schema(self):
        """Ensure documents table exists (SQLite compatible)"""
        logger.info("Checking/creating warehouse schema...")

        create_documents_table = """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Document Identity
            document_id TEXT,
            hash_sha256 TEXT NOT NULL UNIQUE,
            text_hash_sha256 TEXT,

            -- Document Classification
            document_type TEXT NOT NULL,

            -- Publisher Information
            publisher_org TEXT NOT NULL,
            publisher_type TEXT NOT NULL,
            publisher_country TEXT,
            publisher_domain TEXT,
            verified_publisher INTEGER DEFAULT 0,

            -- Date Information
            publication_date TEXT NOT NULL,
            publication_date_iso TEXT NOT NULL,
            date_source TEXT,
            date_confidence TEXT,
            last_modified TEXT,

            -- Content
            title TEXT NOT NULL,
            title_en TEXT,
            description TEXT,
            content_text TEXT NOT NULL,
            content_length INTEGER NOT NULL,
            language TEXT NOT NULL,

            -- File Metadata
            file_size_bytes INTEGER,
            file_format TEXT,
            canonical_url TEXT NOT NULL,
            saved_path TEXT,

            -- Provenance
            discovery_method TEXT,
            discovery_timestamp TEXT,
            fetch_url TEXT NOT NULL,
            archive_url TEXT,
            archive_timestamp TEXT,
            mirror_source_type TEXT,
            safe_access_validated INTEGER DEFAULT 1,
            blocked_domain_detected INTEGER DEFAULT 0,

            -- Extraction Metadata
            extraction_timestamp TEXT NOT NULL,
            extraction_ok INTEGER DEFAULT 0,
            qa_passed INTEGER DEFAULT 0,
            redteam_reviewed INTEGER DEFAULT 0,
            verified_safe_source INTEGER DEFAULT 0,
            reliability_weight REAL DEFAULT 0.5,
            duplicate_detected INTEGER DEFAULT 0,
            duplicate_of TEXT,

            -- Collection Metadata
            collection_run_id TEXT,
            collector_name TEXT NOT NULL,
            collector_version TEXT NOT NULL,

            -- Timestamps
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            -- Extensions (JSON)
            extensions TEXT DEFAULT '{}'
        )
        """

        self.conn.execute(create_documents_table)

        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(hash_sha256)",
            "CREATE INDEX IF NOT EXISTS idx_documents_text_hash ON documents(text_hash_sha256)",
            "CREATE INDEX IF NOT EXISTS idx_documents_pub_date ON documents(publication_date)",
            "CREATE INDEX IF NOT EXISTS idx_documents_publisher_country ON documents(publisher_country)",
            "CREATE INDEX IF NOT EXISTS idx_documents_publisher_type ON documents(publisher_type)",
            "CREATE INDEX IF NOT EXISTS idx_documents_collector ON documents(collector_name)",
            "CREATE INDEX IF NOT EXISTS idx_documents_duplicate_of ON documents(duplicate_of)",
        ]

        for index_sql in indexes:
            self.conn.execute(index_sql)

        self.conn.commit()
        logger.info("Schema ready")

    def hash_exists(self, hash_sha256: str) -> bool:
        """Check if document hash already exists"""
        cursor = self.conn.execute(
            "SELECT 1 FROM documents WHERE hash_sha256 = ? LIMIT 1",
            (hash_sha256,)
        )
        return cursor.fetchone() is not None

    def map_thinktank_document(self, doc: Dict, source_id: str) -> Dict:
        """Map Think Tank JSON to warehouse format"""
        # Extract text content (HTML snapshot or document text)
        content_text = ""
        if doc.get("document_type") == "web_snapshot":
            content_text = doc.get("html_content", "")[:10000]  # Limit for performance
        else:
            content_text = doc.get("text_content", doc.get("description", ""))

        # Determine document type
        doc_type = "web_snapshot" if doc.get("document_type") == "web_snapshot" else "report"

        # Map to warehouse format
        return {
            "document_id": doc.get("document_id"),
            "hash_sha256": doc["hash_sha256"],
            "text_hash_sha256": doc.get("text_hash_sha256", doc["hash_sha256"]),
            "document_type": doc_type,

            "publisher_org": doc.get("publisher_org", "Unknown"),
            "publisher_type": "think_tank",
            "publisher_country": self._extract_country_from_org(doc.get("publisher_org", "")),
            "publisher_domain": doc.get("source_url", "").split("/")[2] if doc.get("source_url") else "",
            "verified_publisher": 1 if doc.get("publisher_org") else 0,

            "publication_date": doc.get("publication_date_iso") or doc.get("publication_date") or datetime.utcnow().strftime("%Y-%m-%d"),
            "publication_date_iso": doc.get("publication_date_iso") or doc.get("publication_date") or datetime.utcnow().strftime("%Y-%m-%d"),
            "date_source": "metadata",
            "date_confidence": "medium",
            "last_modified": None,

            "title": doc.get("title", "Untitled"),
            "title_en": None,
            "description": doc.get("description", ""),
            "content_text": content_text,
            "content_length": len(content_text),
            "language": doc.get("language", "en"),

            "file_size_bytes": doc.get("file_size_bytes", 0),
            "file_format": doc.get("file_format", "html"),
            "canonical_url": doc.get("canonical_url") or doc.get("source_url") or doc.get("download_url") or "unknown",
            "saved_path": doc.get("saved_path", ""),

            "discovery_method": "sitemap",
            "discovery_timestamp": doc.get("discovered_timestamp", datetime.utcnow().isoformat()),
            "fetch_url": doc.get("download_url") or doc.get("canonical_url") or doc.get("source_url") or "unknown",
            "archive_url": None,
            "archive_timestamp": None,
            "mirror_source_type": "direct",
            "safe_access_validated": 1,
            "blocked_domain_detected": 0,

            "extraction_timestamp": doc.get("extraction_timestamp", datetime.utcnow().isoformat()),
            "extraction_ok": 1,
            "qa_passed": 0,  # Not yet QA'd
            "redteam_reviewed": 0,
            "verified_safe_source": 1,
            "reliability_weight": 0.7,  # Think tanks are generally reliable
            "duplicate_detected": 0,
            "duplicate_of": None,

            "collection_run_id": None,
            "collector_name": "thinktank_regional_collector",
            "collector_version": "1.0",

            "extensions": json.dumps({
                "source_id": source_id,
                "region": doc.get("region", "unknown")
            })
        }

    def map_europechina_document(self, doc: Dict, bucket: str, source_id: str) -> Dict:
        """Map Europe-China JSON to warehouse format"""
        # Extract content from provenance chain if available
        content_text = doc.get("text_preview", "")

        return {
            "document_id": None,
            "hash_sha256": doc["hash_sha256"],
            "text_hash_sha256": doc.get("text_hash_sha256", doc["hash_sha256"]),
            "document_type": "policy_document",

            "publisher_org": doc.get("source_name", "Unknown"),
            "publisher_type": bucket.lower(),
            "publisher_country": "CN",  # Europe-China sources are Chinese
            "publisher_domain": source_id,
            "verified_publisher": 1,

            "publication_date": doc.get("archive_timestamp", "")[:10] if doc.get("archive_timestamp") else datetime.utcnow().strftime("%Y-%m-%d"),
            "publication_date_iso": doc.get("archive_timestamp", "")[:10] if doc.get("archive_timestamp") else datetime.utcnow().strftime("%Y-%m-%d"),
            "date_source": "archive_timestamp",
            "date_confidence": "medium",
            "last_modified": None,

            "title": doc.get("title", "Untitled"),
            "title_en": None,
            "description": None,
            "content_text": content_text,
            "content_length": len(content_text),
            "language": doc.get("language", "zh"),

            "file_size_bytes": doc.get("file_size_bytes", 0),
            "file_format": "html",
            "canonical_url": doc.get("canonical_url", ""),
            "saved_path": doc.get("saved_path", ""),

            "discovery_method": "wayback_cdx",
            "discovery_timestamp": doc.get("extraction_timestamp", datetime.utcnow().isoformat()),
            "fetch_url": doc.get("archive_url", ""),
            "archive_url": doc.get("archive_url", ""),
            "archive_timestamp": doc.get("archive_timestamp", ""),
            "mirror_source_type": "wayback",
            "safe_access_validated": 1,
            "blocked_domain_detected": 0,

            "extraction_timestamp": doc.get("extraction_timestamp", datetime.utcnow().isoformat()),
            "extraction_ok": 1 if doc.get("extraction_ok") else 0,
            "qa_passed": 0,
            "redteam_reviewed": 0,
            "verified_safe_source": 1 if doc.get("verified_safe_source") else 0,
            "reliability_weight": 0.6,  # Archive sources slightly lower weight
            "duplicate_detected": 0,
            "duplicate_of": None,

            "collection_run_id": None,
            "collector_name": "europe_china_collector",
            "collector_version": "1.0",

            "extensions": json.dumps({
                "bucket": bucket,
                "source_id": source_id,
                "keywords_matched": doc.get("keywords_matched", []),
                "provenance_chain": doc.get("provenance_chain", [])
            })
        }

    def _extract_country_from_org(self, org_name: str) -> Optional[str]:
        """Extract country code from organization name (simple heuristic)"""
        # TODO: Improve with proper mapping
        if not org_name:
            return None

        org_lower = org_name.lower()
        country_map = {
            "brookings": "US",
            "csis": "US",
            "carnegie": "US",
            "rand": "US",
            "atlantic council": "US",
            "chatham house": "GB",
            "ciis": "CN",
            "cass": "CN",
        }

        for key, country in country_map.items():
            if key in org_lower:
                return country

        return None

    def insert_document(self, doc: Dict) -> bool:
        """Insert document into warehouse"""
        # Check for duplicate
        if self.hash_exists(doc["hash_sha256"]):
            self.stats["duplicates_skipped"] += 1
            return False

        # Build INSERT statement
        columns = list(doc.keys())
        placeholders = ["?" for _ in columns]

        sql = f"""
        INSERT INTO documents ({", ".join(columns)})
        VALUES ({", ".join(placeholders)})
        """

        try:
            self.conn.execute(sql, [doc[col] for col in columns])
            self.stats["inserted"] += 1
            return True
        except Exception as e:
            logger.error(f"Error inserting document {doc.get('hash_sha256')}: {e}")
            self.stats["errors"] += 1
            return False

    def load_thinktank_collection(self, collection_dir: Path):
        """Load Think Tank collection from items.json"""
        items_json = collection_dir / "items.json"

        if not items_json.exists():
            logger.warning(f"No items.json found in {collection_dir}")
            return

        logger.info(f"Loading Think Tank collection: {collection_dir}")

        with open(items_json, 'r', encoding='utf-8') as f:
            items = json.load(f)

        logger.info(f"Found {len(items)} items in collection")

        for item in items:
            self.stats["total_processed"] += 1

            # Map to warehouse format
            warehouse_doc = self.map_thinktank_document(item, collection_dir.name)

            # Insert
            self.insert_document(warehouse_doc)

            if self.stats["total_processed"] % 100 == 0:
                self.conn.commit()
                logger.info(f"Processed {self.stats['total_processed']} documents...")

        self.conn.commit()
        logger.info(f"Completed loading {collection_dir}")

    def load_europechina_raw(self, raw_dir: Path, bucket: str, source_id: str):
        """Load Europe-China RAW JSON files"""
        logger.info(f"Loading Europe-China RAW: {bucket}/{source_id}")

        json_files = list(raw_dir.glob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files")

        for json_file in json_files:
            self.stats["total_processed"] += 1

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    doc = json.load(f)

                # Map to warehouse format
                warehouse_doc = self.map_europechina_document(doc, bucket, source_id)

                # Insert
                self.insert_document(warehouse_doc)

                if self.stats["total_processed"] % 100 == 0:
                    self.conn.commit()
                    logger.info(f"Processed {self.stats['total_processed']} documents...")

            except Exception as e:
                logger.error(f"Error processing {json_file}: {e}")
                self.stats["errors"] += 1

        self.conn.commit()

    def run_full_integration(self):
        """Run full integration of all collections"""
        logger.info("=" * 80)
        logger.info("Starting Full Document Warehouse Integration")
        logger.info("=" * 80)

        self.connect()
        self.ensure_schema()

        # Load Think Tank collections
        logger.info("\n### THINK TANK COLLECTIONS ###")
        for collection_dir in THINKTANK_ROOT.glob("*/202*"):
            if collection_dir.is_dir():
                self.load_thinktank_collection(collection_dir)

        # Load Europe-China collections
        logger.info("\n### EUROPE-CHINA COLLECTIONS ###")
        raw_dir = EUROPECHINA_ROOT / "RAW"
        if raw_dir.exists():
            for bucket_dir in raw_dir.iterdir():
                if bucket_dir.is_dir():
                    bucket_name = bucket_dir.name
                    for source_dir in bucket_dir.iterdir():
                        if source_dir.is_dir():
                            self.load_europechina_raw(source_dir, bucket_name, source_dir.name)

        # Final stats
        self.conn.close()

        logger.info("\n" + "=" * 80)
        logger.info("Integration Complete!")
        logger.info("=" * 80)
        logger.info(f"Total Processed: {self.stats['total_processed']}")
        logger.info(f"Inserted: {self.stats['inserted']}")
        logger.info(f"Duplicates Skipped: {self.stats['duplicates_skipped']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info("=" * 80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Integrate document collections into OSINT warehouse')
    parser.add_argument('--collection', type=str, help='Specific collection directory to load')
    parser.add_argument('--type', type=str, choices=['thinktank', 'europechina'], help='Collection type')
    parser.add_argument('--full', action='store_true', help='Load all collections')
    parser.add_argument('--test', action='store_true', help='Use test database')

    args = parser.parse_args()

    db_path = TEST_WAREHOUSE_DB if args.test else WAREHOUSE_DB
    integrator = WarehouseIntegrator(db_path)

    if args.full:
        integrator.run_full_integration()
    elif args.collection and args.type:
        integrator.connect()
        integrator.ensure_schema()

        if args.type == 'thinktank':
            integrator.load_thinktank_collection(Path(args.collection))
        elif args.type == 'europechina':
            # TODO: Implement single collection loading
            pass

        integrator.conn.close()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
