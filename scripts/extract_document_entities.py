#!/usr/bin/env python3
"""
Document Entity Extraction Pipeline
Extracts named entities from warehouse documents using spaCy NER

Features:
- Multi-language support (English, Chinese)
- Entity normalization for matching
- Incremental processing (skip already processed docs)
- Batch processing for performance
- Custom technology domain detection
- Fuzzy matching preparation
"""

import json
import sqlite3
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
import sys

# NLP libraries
import spacy
from spacy.tokens import Doc
from rapidfuzz import fuzz

# Configuration
WAREHOUSE_DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")
TEST_WAREHOUSE_DB = Path("F:/OSINT_WAREHOUSE/osint_test.db")

# Technology domains for custom detection
TECH_DOMAINS = {
    "semiconductors": [
        "semiconductor", "chip", "wafer", "lithography", "tsmc", "asml",
        "euv", "photoresist", "mosfet", "transistor", "fab", "foundry",
        "silicon", "gallium nitride", "gan", "sic", "cmos"
    ],
    "quantum": [
        "quantum", "qubit", "quantum computing", "quantum communication",
        "quantum cryptography", "superconducting", "topological", "ion trap",
        "quantum supremacy", "quantum entanglement"
    ],
    "ai": [
        "artificial intelligence", "machine learning", "deep learning", "neural network",
        "transformer", "llm", "large language model", "computer vision",
        "natural language processing", "nlp", "reinforcement learning"
    ],
    "space": [
        "satellite", "launch vehicle", "rocket", "space station", "orbit",
        "spacecraft", "space exploration", "mars", "moon", "aerospace",
        "beidou", "gps", "navigation", "remote sensing"
    ],
    "energy": [
        "solar", "wind", "nuclear", "fusion", "battery", "energy storage",
        "grid", "renewable", "lithium", "hydrogen", "fuel cell",
        "photovoltaic", "turbine"
    ],
    "advanced_materials": [
        "graphene", "carbon nanotube", "metamaterial", "superconductor",
        "alloy", "composite", "rare earth", "ceramic", "polymer"
    ],
    "neuroscience": [
        "brain", "neural", "neuron", "cognitive", "brain-computer interface",
        "bci", "neurotechnology", "neuromorphic"
    ],
    "smart_city": [
        "smart city", "iot", "internet of things", "5g", "6g",
        "surveillance", "facial recognition", "traffic management"
    ],
    "biotechnology": [
        "crispr", "gene editing", "synthetic biology", "biotech",
        "genetic engineering", "dna", "rna", "mrna", "vaccine"
    ]
}

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('entity_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EntityExtractor:
    """Extracts and normalizes named entities from documents"""

    def __init__(self, warehouse_path: Path, batch_size: int = 100):
        self.warehouse_path = warehouse_path
        self.batch_size = batch_size
        self.conn = None

        # Load spaCy models
        logger.info("Loading spaCy models...")
        self.nlp_en = spacy.load("en_core_web_sm")
        self.nlp_zh = spacy.load("zh_core_web_sm")
        logger.info("Models loaded successfully")

        # Statistics
        self.stats = {
            "documents_processed": 0,
            "entities_extracted": 0,
            "orgs_extracted": 0,
            "persons_extracted": 0,
            "gpes_extracted": 0,
            "errors": 0
        }

    def connect(self):
        """Connect to warehouse database"""
        logger.info(f"Connecting to warehouse: {self.warehouse_path}")
        self.conn = sqlite3.connect(str(self.warehouse_path))
        self.conn.row_factory = sqlite3.Row
        logger.info("Connected successfully")

    def ensure_entity_schema(self):
        """Create document_entities table if not exists"""
        logger.info("Ensuring entity schema exists...")

        # Create document_entities table directly
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS document_entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            document_hash TEXT NOT NULL,
            entity_text TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_canonical TEXT NOT NULL,
            confidence REAL DEFAULT 1.0,
            position_start INTEGER,
            position_end INTEGER,
            sentence_context TEXT,
            matched_uspto_entities TEXT,
            matched_openalex_authors TEXT,
            matched_ted_contractors TEXT,
            matched_usaspending_recipients TEXT,
            match_confidence REAL DEFAULT 0.0,
            match_method TEXT,
            verified_match INTEGER DEFAULT 0,
            tech_domains TEXT,
            extracted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            matched_at TEXT,
            verified_at TEXT,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
        """

        self.conn.execute(create_table_sql)

        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_entities_document_id ON document_entities(document_id)",
            "CREATE INDEX IF NOT EXISTS idx_entities_document_hash ON document_entities(document_hash)",
            "CREATE INDEX IF NOT EXISTS idx_entities_text ON document_entities(entity_text)",
            "CREATE INDEX IF NOT EXISTS idx_entities_canonical ON document_entities(entity_canonical)",
            "CREATE INDEX IF NOT EXISTS idx_entities_type ON document_entities(entity_type)",
            "CREATE INDEX IF NOT EXISTS idx_entities_confidence ON document_entities(confidence)",
            "CREATE INDEX IF NOT EXISTS idx_entities_doc_type ON document_entities(document_id, entity_type)",
            "CREATE INDEX IF NOT EXISTS idx_entities_type_canonical ON document_entities(entity_type, entity_canonical)",
        ]

        for index_sql in indexes:
            self.conn.execute(index_sql)

        self.conn.commit()
        logger.info("Entity schema ready")

    def normalize_entity(self, text: str) -> str:
        """Normalize entity text for matching"""
        # Convert to lowercase
        canonical = text.lower()

        # Remove extra whitespace
        canonical = re.sub(r'\s+', ' ', canonical).strip()

        # Remove common punctuation
        canonical = re.sub(r'[,\.;:\'"!?()]', '', canonical)

        # Remove "the", "inc", "ltd", "co", etc.
        canonical = re.sub(r'\b(the|inc|ltd|llc|co|corp|corporation|company)\b', '', canonical)
        canonical = re.sub(r'\s+', ' ', canonical).strip()

        return canonical

    def detect_tech_domains(self, text: str) -> List[str]:
        """Detect technology domains mentioned in text"""
        text_lower = text.lower()
        detected_domains = []

        for domain, keywords in TECH_DOMAINS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_domains.append(domain)
                    break  # Found at least one keyword, move to next domain

        return detected_domains

    def extract_entities_from_text(
        self,
        text: str,
        language: str,
        doc_id: int,
        doc_hash: str,
        max_length: int = 100000
    ) -> List[Dict]:
        """Extract entities from text using spaCy"""

        # Truncate very long texts for performance
        if len(text) > max_length:
            text = text[:max_length]

        # Select appropriate model
        nlp = self.nlp_en if language == 'en' else self.nlp_zh

        # Process text
        try:
            doc = nlp(text)
        except Exception as e:
            logger.error(f"Error processing document {doc_id}: {e}")
            return []

        # Extract entities
        entities = []
        for ent in doc.ents:
            # Filter entity types we care about
            if ent.label_ in ['ORG', 'PERSON', 'GPE', 'PRODUCT', 'DATE', 'MONEY', 'LOC']:

                entity_text = ent.text.strip()
                if not entity_text or len(entity_text) < 2:
                    continue

                # Get sentence context
                sent_start = max(0, ent.start - 5)
                sent_end = min(len(doc), ent.end + 5)
                context = doc[sent_start:sent_end].text

                # Normalize entity
                canonical = self.normalize_entity(entity_text)

                # Detect technology domains in context
                tech_domains = self.detect_tech_domains(context)

                entity_dict = {
                    "document_id": doc_id,
                    "document_hash": doc_hash,
                    "entity_text": entity_text,
                    "entity_type": ent.label_,
                    "entity_canonical": canonical,
                    "confidence": 1.0,  # spaCy entities are high confidence
                    "position_start": ent.start_char,
                    "position_end": ent.end_char,
                    "sentence_context": context[:500],  # Limit context length
                    "tech_domains": json.dumps(tech_domains) if tech_domains else None,
                    "matched_uspto_entities": None,
                    "matched_openalex_authors": None,
                    "matched_ted_contractors": None,
                    "matched_usaspending_recipients": None,
                    "match_confidence": 0.0,
                    "match_method": None,
                    "verified_match": 0
                }

                entities.append(entity_dict)

        return entities

    def insert_entities(self, entities: List[Dict]) -> int:
        """Insert entities into database"""
        if not entities:
            return 0

        inserted = 0

        for entity in entities:
            try:
                # Check if this exact entity already exists
                cursor = self.conn.execute("""
                    SELECT 1 FROM document_entities
                    WHERE document_id = ?
                      AND entity_canonical = ?
                      AND entity_type = ?
                    LIMIT 1
                """, (
                    entity["document_id"],
                    entity["entity_canonical"],
                    entity["entity_type"]
                ))

                if cursor.fetchone():
                    continue  # Skip duplicate

                # Insert entity
                self.conn.execute("""
                    INSERT INTO document_entities (
                        document_id, document_hash, entity_text, entity_type,
                        entity_canonical, confidence, position_start, position_end,
                        sentence_context, tech_domains, matched_uspto_entities,
                        matched_openalex_authors, matched_ted_contractors,
                        matched_usaspending_recipients, match_confidence,
                        match_method, verified_match
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entity["document_id"],
                    entity["document_hash"],
                    entity["entity_text"],
                    entity["entity_type"],
                    entity["entity_canonical"],
                    entity["confidence"],
                    entity["position_start"],
                    entity["position_end"],
                    entity["sentence_context"],
                    entity["tech_domains"],
                    entity["matched_uspto_entities"],
                    entity["matched_openalex_authors"],
                    entity["matched_ted_contractors"],
                    entity["matched_usaspending_recipients"],
                    entity["match_confidence"],
                    entity["match_method"],
                    entity["verified_match"]
                ))

                inserted += 1

            except Exception as e:
                logger.error(f"Error inserting entity '{entity.get('entity_text')}': {e}")
                self.stats["errors"] += 1

        return inserted

    def get_unprocessed_documents(self, limit: Optional[int] = None) -> List[Dict]:
        """Get documents that haven't been processed for entity extraction yet"""

        query = """
        SELECT
            d.id,
            d.hash_sha256,
            d.title,
            d.content_text,
            d.language,
            d.publisher_org,
            d.publisher_country
        FROM documents d
        WHERE d.duplicate_detected = 0
          AND d.content_length > 100
          AND d.id NOT IN (
              SELECT DISTINCT document_id
              FROM document_entities
          )
        ORDER BY d.id ASC
        """

        if limit:
            query += f" LIMIT {limit}"

        cursor = self.conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def process_document(self, doc: Dict) -> int:
        """Process a single document and extract entities"""

        # Extract entities
        entities = self.extract_entities_from_text(
            text=doc['content_text'],
            language=doc['language'],
            doc_id=doc['id'],
            doc_hash=doc['hash_sha256']
        )

        # Insert entities
        inserted = self.insert_entities(entities)

        # Update statistics
        self.stats["documents_processed"] += 1
        self.stats["entities_extracted"] += inserted

        for entity in entities:
            if entity["entity_type"] == "ORG":
                self.stats["orgs_extracted"] += 1
            elif entity["entity_type"] == "PERSON":
                self.stats["persons_extracted"] += 1
            elif entity["entity_type"] == "GPE":
                self.stats["gpes_extracted"] += 1

        return inserted

    def process_batch(self, documents: List[Dict]):
        """Process a batch of documents"""

        for doc in documents:
            try:
                entities_count = self.process_document(doc)

                if self.stats["documents_processed"] % 10 == 0:
                    logger.info(
                        f"Processed {self.stats['documents_processed']} documents, "
                        f"extracted {self.stats['entities_extracted']} entities"
                    )

            except Exception as e:
                logger.error(f"Error processing document {doc['id']}: {e}")
                self.stats["errors"] += 1

        # Commit batch
        self.conn.commit()

    def run_extraction(self, limit: Optional[int] = None):
        """Run entity extraction on all unprocessed documents"""
        logger.info("=" * 80)
        logger.info("Starting Entity Extraction")
        logger.info("=" * 80)

        self.connect()
        self.ensure_entity_schema()

        # Get unprocessed documents
        logger.info("Fetching unprocessed documents...")
        documents = self.get_unprocessed_documents(limit=limit)
        total_docs = len(documents)

        if total_docs == 0:
            logger.info("No unprocessed documents found. All documents already processed!")
            return

        logger.info(f"Found {total_docs} unprocessed documents")

        # Process in batches
        for i in range(0, total_docs, self.batch_size):
            batch = documents[i:i + self.batch_size]
            logger.info(f"\nProcessing batch {i // self.batch_size + 1} ({len(batch)} documents)...")
            self.process_batch(batch)

        # Final statistics
        self.conn.close()

        logger.info("\n" + "=" * 80)
        logger.info("Entity Extraction Complete!")
        logger.info("=" * 80)
        logger.info(f"Documents Processed: {self.stats['documents_processed']}")
        logger.info(f"Total Entities Extracted: {self.stats['entities_extracted']}")
        logger.info(f"  - Organizations: {self.stats['orgs_extracted']}")
        logger.info(f"  - Persons: {self.stats['persons_extracted']}")
        logger.info(f"  - Locations (GPE): {self.stats['gpes_extracted']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info("=" * 80)

    def get_entity_statistics(self):
        """Get statistics about extracted entities"""
        self.connect()

        stats = {}

        # Total entities
        cursor = self.conn.execute("SELECT COUNT(*) FROM document_entities")
        stats['total_entities'] = cursor.fetchone()[0]

        # By type
        cursor = self.conn.execute("""
            SELECT entity_type, COUNT(*) as count
            FROM document_entities
            GROUP BY entity_type
            ORDER BY count DESC
        """)
        stats['by_type'] = dict(cursor.fetchall())

        # Top organizations
        cursor = self.conn.execute("""
            SELECT entity_canonical, COUNT(DISTINCT document_id) as doc_count
            FROM document_entities
            WHERE entity_type = 'ORG'
            GROUP BY entity_canonical
            ORDER BY doc_count DESC
            LIMIT 20
        """)
        stats['top_orgs'] = dict(cursor.fetchall())

        # Documents with entities
        cursor = self.conn.execute("""
            SELECT COUNT(DISTINCT document_id)
            FROM document_entities
        """)
        stats['documents_with_entities'] = cursor.fetchone()[0]

        self.conn.close()

        return stats


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Extract named entities from warehouse documents')
    parser.add_argument('--limit', type=int, help='Limit number of documents to process')
    parser.add_argument('--test', action='store_true', help='Use test database')
    parser.add_argument('--stats', action='store_true', help='Show entity statistics')

    args = parser.parse_args()

    db_path = TEST_WAREHOUSE_DB if args.test else WAREHOUSE_DB
    extractor = EntityExtractor(db_path)

    if args.stats:
        # Show statistics
        stats = extractor.get_entity_statistics()
        print("\n" + "=" * 80)
        print("Entity Extraction Statistics")
        print("=" * 80)
        print(f"Total Entities: {stats['total_entities']}")
        print(f"Documents with Entities: {stats['documents_with_entities']}")
        print("\nBy Entity Type:")
        for entity_type, count in stats['by_type'].items():
            print(f"  {entity_type}: {count}")
        print("\nTop 20 Organizations:")
        for org, count in list(stats['top_orgs'].items())[:20]:
            print(f"  {org}: {count} documents")
        print("=" * 80)
    else:
        # Run extraction
        extractor.run_extraction(limit=args.limit)


if __name__ == '__main__':
    main()
