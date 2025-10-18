#!/usr/bin/env python3
"""
MCF Base Collector Framework
Implements core Military-Civil Fusion intelligence collection capabilities
Based on MCF_HARVESTING_STRATEGY.md analysis
"""

import requests
import json
import re
import hashlib
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import urljoin, urlparse
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCFBaseCollector:
    """Base class for Military-Civil Fusion intelligence collection"""

    def __init__(self, warehouse_path: str = "F:/OSINT_WAREHOUSE/osint_research.db"):
        self.warehouse_path = warehouse_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # MCF keyword scoring system
        self.mcf_keywords = {
            'direct_mcf': {
                'weight': 5,
                'keywords': [
                    'military civil fusion', 'military-civil fusion', 'MCF',
                    '军民融合', 'dual use', 'dual-use', 'civil-military integration'
                ]
            },
            'pla_industry': {
                'weight': 4,
                'keywords': [
                    'PLA', 'AVIC', 'AECC', 'NORINCO', 'CETC', 'CASIC', 'CSSC', 'CSIC',
                    'defense industry', 'defense industrial base', 'military industrial complex'
                ]
            },
            'technology_transfer': {
                'weight': 4,
                'keywords': [
                    'technology transfer', 'talent program', 'thousand talents',
                    'joint laboratory', 'joint lab', 'joint research', 'tech transfer'
                ]
            },
            'policy_instruments': {
                'weight': 3,
                'keywords': [
                    'MIIT', 'SASAC', 'guidance funds', 'subsidies', 'industrial policy',
                    'Made in China 2025', 'state support', 'SOE', 'state-owned enterprise'
                ]
            },
            'export_controls': {
                'weight': 3,
                'keywords': [
                    'export control', 'BIS', 'entity list', 'sanctions', 'end use', 'end user',
                    'shell company', 'front company', 'circumvention'
                ]
            },
            'standards': {
                'weight': 3,
                'keywords': [
                    '3GPP', 'standards', 'standardization', 'technical standards',
                    'ISO', 'ITU', 'procurement', 'specifications'
                ]
            }
        }

        # Chinese entity patterns
        self.entity_patterns = {
            'companies': [
                'AVIC', 'AECC', 'NORINCO', 'CETC', 'CASIC', 'CSSC', 'CSIC',
                'CASC', 'CNNC', 'CNOOC', 'CNPC', 'Sinopec', 'State Grid',
                'China Mobile', 'China Telecom', 'China Unicom', 'Huawei', 'ZTE',
                'CRRC', 'COMAC', 'Baidu', 'Alibaba', 'Tencent'
            ],
            'institutes': [
                'Chinese Academy of Sciences', 'CAS', 'Tsinghua University',
                'Peking University', 'Beijing University of Technology',
                'National University of Defense Technology', 'NUDT'
            ],
            'programs': [
                'Thousand Talents', 'Made in China 2025', 'Belt and Road',
                'BRI', 'National Intelligence Law', 'Cybersecurity Law',
                'Data Security Law', 'Foreign Investment Law'
            ],
            'government_bodies': [
                'MIIT', 'SASAC', 'MOST', 'CMC', 'State Council', 'NDRC',
                'Ministry of Commerce', 'MOFCOM', 'CAC', 'MSS'
            ]
        }

        # Initialize database schema
        self._init_mcf_database()

    def _init_mcf_database(self):
        """Initialize MCF-specific database tables"""
        try:
            conn = sqlite3.connect(self.warehouse_path)
            cursor = conn.cursor()

            # MCF documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mcf_documents (
                    id INTEGER PRIMARY KEY,
                    source_id VARCHAR(50),
                    document_type VARCHAR(50),
                    title TEXT,
                    url TEXT UNIQUE,
                    publication_date DATE,
                    authors_json TEXT,
                    mcf_relevance_score FLOAT,
                    entities_json TEXT,
                    provenance_json TEXT,
                    content_text TEXT,
                    pdf_hash VARCHAR(64),
                    html_hash VARCHAR(64),
                    collected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    classification VARCHAR(50),
                    language VARCHAR(10),
                    version VARCHAR(20)
                )
            """)

            # MCF entities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mcf_entities (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(200) UNIQUE,
                    type VARCHAR(50),
                    chinese_name VARCHAR(200),
                    aliases TEXT,
                    description TEXT,
                    first_seen DATE,
                    last_updated DATE DEFAULT CURRENT_DATE,
                    verification_status VARCHAR(20) DEFAULT 'unverified',
                    confidence_score FLOAT DEFAULT 0.0
                )
            """)

            # MCF relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mcf_relationships (
                    id INTEGER PRIMARY KEY,
                    entity1_id INTEGER,
                    entity2_id INTEGER,
                    relationship_type VARCHAR(50),
                    confidence_score FLOAT,
                    source_document_id INTEGER,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (entity1_id) REFERENCES mcf_entities(id),
                    FOREIGN KEY (entity2_id) REFERENCES mcf_entities(id),
                    FOREIGN KEY (source_document_id) REFERENCES mcf_documents(id)
                )
            """)

            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mcf_docs_source ON mcf_documents(source_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mcf_docs_relevance ON mcf_documents(mcf_relevance_score)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mcf_entities_type ON mcf_entities(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mcf_entities_name ON mcf_entities(name)")

            conn.commit()
            conn.close()
            logger.info("MCF database schema initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize MCF database: {e}")
            raise

    def calculate_mcf_relevance(self, content: str) -> float:
        """Calculate MCF relevance score for content"""
        if not content:
            return 0.0

        score = 0.0
        content_lower = content.lower()

        for category, config in self.mcf_keywords.items():
            category_score = 0
            for keyword in config['keywords']:
                # Count occurrences of each keyword
                occurrences = content_lower.count(keyword.lower())
                if occurrences > 0:
                    # Diminishing returns for multiple occurrences
                    keyword_score = min(occurrences * 0.1, 0.3)
                    category_score += keyword_score

            # Apply category weight
            score += category_score * (config['weight'] / 5.0)

        # Normalize to 0-1 range
        return min(score, 1.0)

    def extract_mcf_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract MCF-relevant entities from content"""
        entities = {
            'companies': [],
            'institutes': [],
            'programs': [],
            'government_bodies': [],
            'technologies': []
        }

        content_upper = content.upper()

        # Extract entities by category
        for category, entity_list in self.entity_patterns.items():
            for entity in entity_list:
                if entity.upper() in content_upper:
                    if entity not in entities[category]:
                        entities[category].append(entity)

        # Extract technology keywords
        tech_keywords = [
            'hypersonic', 'quantum', 'artificial intelligence', 'AI', 'machine learning',
            'semiconductor', '5G', '6G', 'facial recognition', 'surveillance',
            'biotechnology', 'genetic engineering', 'nanotechnology', 'robotics'
        ]

        for tech in tech_keywords:
            if tech.lower() in content.lower():
                if tech not in entities['technologies']:
                    entities['technologies'].append(tech)

        return entities

    def generate_content_hashes(self, content: str, url: str) -> Tuple[str, str]:
        """Generate SHA256 hashes for content tracking"""
        html_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # For PDF hash, use URL as proxy (would need actual PDF content)
        pdf_hash = hashlib.sha256(url.encode('utf-8')).hexdigest() if url.endswith('.pdf') else None

        return html_hash, pdf_hash

    def store_mcf_document(self, document_data: Dict) -> Optional[int]:
        """Store MCF document in database"""
        try:
            conn = sqlite3.connect(self.warehouse_path)
            cursor = conn.cursor()

            # Check if document already exists
            cursor.execute("SELECT id FROM mcf_documents WHERE url = ?", (document_data['url'],))
            existing = cursor.fetchone()

            if existing:
                logger.info(f"Document already exists: {document_data['url']}")
                conn.close()
                return existing[0]

            # Insert new document
            cursor.execute("""
                INSERT INTO mcf_documents (
                    source_id, document_type, title, url, publication_date,
                    authors_json, mcf_relevance_score, entities_json, provenance_json,
                    content_text, pdf_hash, html_hash, classification, language, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document_data.get('source_id'),
                document_data.get('document_type'),
                document_data.get('title'),
                document_data.get('url'),
                document_data.get('publication_date'),
                json.dumps(document_data.get('authors', [])),
                document_data.get('mcf_relevance_score', 0.0),
                json.dumps(document_data.get('entities', {})),
                json.dumps(document_data.get('provenance', {})),
                document_data.get('content_text'),
                document_data.get('pdf_hash'),
                document_data.get('html_hash'),
                document_data.get('classification', 'unclassified'),
                document_data.get('language', 'en'),
                document_data.get('version', '1.0')
            ))

            doc_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"Stored MCF document: {document_data['title'][:50]}... (ID: {doc_id})")
            return doc_id

        except Exception as e:
            logger.error(f"Failed to store MCF document: {e}")
            return None

    def store_mcf_entity(self, entity_data: Dict) -> Optional[int]:
        """Store or update MCF entity in database"""
        try:
            conn = sqlite3.connect(self.warehouse_path)
            cursor = conn.cursor()

            # Check if entity already exists
            cursor.execute("SELECT id FROM mcf_entities WHERE name = ?", (entity_data['name'],))
            existing = cursor.fetchone()

            if existing:
                # Update existing entity
                cursor.execute("""
                    UPDATE mcf_entities SET
                        type = ?, chinese_name = ?, aliases = ?, description = ?,
                        last_updated = CURRENT_DATE, verification_status = ?, confidence_score = ?
                    WHERE id = ?
                """, (
                    entity_data.get('type'),
                    entity_data.get('chinese_name'),
                    entity_data.get('aliases'),
                    entity_data.get('description'),
                    entity_data.get('verification_status', 'unverified'),
                    entity_data.get('confidence_score', 0.0),
                    existing[0]
                ))
                entity_id = existing[0]
            else:
                # Insert new entity
                cursor.execute("""
                    INSERT INTO mcf_entities (
                        name, type, chinese_name, aliases, description,
                        first_seen, verification_status, confidence_score
                    ) VALUES (?, ?, ?, ?, ?, CURRENT_DATE, ?, ?)
                """, (
                    entity_data['name'],
                    entity_data.get('type'),
                    entity_data.get('chinese_name'),
                    entity_data.get('aliases'),
                    entity_data.get('description'),
                    entity_data.get('verification_status', 'unverified'),
                    entity_data.get('confidence_score', 0.0)
                ))
                entity_id = cursor.lastrowid

            conn.commit()
            conn.close()
            return entity_id

        except Exception as e:
            logger.error(f"Failed to store MCF entity: {e}")
            return None

    def fetch_url_with_retry(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Fetch URL with retry logic and rate limiting"""
        for attempt in range(max_retries):
            try:
                time.sleep(2)  # Rate limiting
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                    return None
                time.sleep(5 * (attempt + 1))  # Exponential backoff

        return None

    def process_document(self, url: str, source_id: str, **metadata) -> Optional[Dict]:
        """Process a single document for MCF intelligence"""
        logger.info(f"Processing document: {url}")

        # Fetch document
        response = self.fetch_url_with_retry(url)
        if not response:
            return None

        content = response.text
        html_hash, pdf_hash = self.generate_content_hashes(content, url)

        # Calculate MCF relevance
        mcf_score = self.calculate_mcf_relevance(content)

        # Skip documents with very low MCF relevance
        if mcf_score < 0.1:
            logger.info(f"Skipping document with low MCF relevance ({mcf_score:.2f}): {url}")
            return None

        # Extract entities
        entities = self.extract_mcf_entities(content)

        # Build document data
        document_data = {
            'source_id': source_id,
            'url': url,
            'mcf_relevance_score': mcf_score,
            'entities': entities,
            'content_text': content[:50000],  # Limit content size
            'html_hash': html_hash,
            'pdf_hash': pdf_hash,
            'provenance': {
                'collected_date': datetime.now().isoformat(),
                'collector': self.__class__.__name__,
                'url': url,
                'response_status': response.status_code,
                'content_type': response.headers.get('content-type', 'unknown')
            },
            **metadata
        }

        # Store document
        doc_id = self.store_mcf_document(document_data)

        if doc_id:
            # Store extracted entities
            for entity_type, entity_list in entities.items():
                for entity_name in entity_list:
                    entity_data = {
                        'name': entity_name,
                        'type': entity_type,
                        'confidence_score': 0.7,  # Default confidence
                        'verification_status': 'detected'
                    }
                    self.store_mcf_entity(entity_data)

        return document_data

    def get_mcf_statistics(self) -> Dict:
        """Get MCF collection statistics"""
        try:
            conn = sqlite3.connect(self.warehouse_path)
            cursor = conn.cursor()

            stats = {}

            # Document statistics
            cursor.execute("SELECT COUNT(*) FROM mcf_documents")
            stats['total_documents'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM mcf_documents WHERE mcf_relevance_score >= 0.7")
            stats['high_relevance_documents'] = cursor.fetchone()[0]

            cursor.execute("SELECT source_id, COUNT(*) FROM mcf_documents GROUP BY source_id")
            stats['documents_by_source'] = dict(cursor.fetchall())

            # Entity statistics
            cursor.execute("SELECT COUNT(*) FROM mcf_entities")
            stats['total_entities'] = cursor.fetchone()[0]

            cursor.execute("SELECT type, COUNT(*) FROM mcf_entities GROUP BY type")
            stats['entities_by_type'] = dict(cursor.fetchall())

            # Average MCF relevance
            cursor.execute("SELECT AVG(mcf_relevance_score) FROM mcf_documents")
            avg_relevance = cursor.fetchone()[0]
            stats['average_mcf_relevance'] = round(avg_relevance, 3) if avg_relevance else 0.0

            conn.close()
            return stats

        except Exception as e:
            logger.error(f"Failed to get MCF statistics: {e}")
            return {}

# Example usage and testing
if __name__ == "__main__":
    # Initialize MCF collector
    mcf_collector = MCFBaseCollector()

    # Test MCF relevance calculation
    test_content = """
    The military-civil fusion strategy aims to integrate civilian and military
    capabilities in China. AVIC and other defense companies are key players in
    dual-use technology development. The PLA benefits from technology transfer
    through Thousand Talents programs.
    """

    mcf_score = mcf_collector.calculate_mcf_relevance(test_content)
    entities = mcf_collector.extract_mcf_entities(test_content)

    print(f"MCF Relevance Score: {mcf_score:.3f}")
    print(f"Extracted Entities: {entities}")

    # Get current statistics
    stats = mcf_collector.get_mcf_statistics()
    print(f"\nMCF Database Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
