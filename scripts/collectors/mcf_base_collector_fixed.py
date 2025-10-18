#!/usr/bin/env python3
"""
Fixed MCF Base Collector with extract_main_content method
"""

import requests
import sqlite3
import json
import re
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCFBaseCollector:
    """Base class for MCF collectors with all required methods"""

    def __init__(self, warehouse_path: str = "F:/OSINT_WAREHOUSE/osint_research.db"):
        self.warehouse_path = warehouse_path
        self.setup_database()

        # MCF keyword categories and weights
        self.mcf_keywords = {
            'direct_mcf': {
                'weight': 5,
                'keywords': ['military civil fusion', 'MCF', '军民融合', 'civil military integration',
                             'military-civil fusion', 'civil-military integration']
            },
            'pla_industry': {
                'weight': 4,
                'keywords': ['PLA', "People's Liberation Army", 'Chinese military', 'defense industrial base',
                             'defense innovation', 'military modernization', 'A2/AD', 'anti-access']
            },
            'technology_transfer': {
                'weight': 4,
                'keywords': ['technology transfer', 'talent program', 'thousand talents', 'Made in China 2025',
                             'dual-use', 'dual use', 'technology diversion', 'illicit transfer']
            },
            'dual_use': {
                'weight': 3,
                'keywords': ['dual-use technology', 'dual use technology', 'civil technology',
                             'commercial off-the-shelf', 'COTS', 'spin-on', 'spin-off']
            },
            'chinese_companies': {
                'weight': 3,
                'keywords': ['AVIC', 'NORINCO', 'CETC', 'CASIC', 'CASC', 'SASTIND', 'AECC',
                             'Huawei', 'ZTE', 'DJI', 'Hikvision', 'SenseTime', 'Megvii']
            }
        }

    def setup_database(self):
        """Initialize database tables for MCF documents"""
        try:
            conn = sqlite3.connect(self.warehouse_path)
            cursor = conn.cursor()

            # MCF documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mcf_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    title TEXT,
                    content TEXT,
                    relevance_score REAL,
                    collector TEXT,
                    collection_timestamp TEXT,
                    metadata TEXT
                )
            ''')

            # MCF entities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mcf_entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    entity_name TEXT,
                    entity_type TEXT,
                    context TEXT,
                    FOREIGN KEY(document_id) REFERENCES mcf_documents(id)
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("MCF database schema initialized successfully")
        except Exception as e:
            logger.error(f"Database setup error: {e}")

    def extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML page"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()

        # Try to find main content area
        content_selectors = [
            'main',
            'article',
            '.content',
            '.main-content',
            '#content',
            '.post-content',
            '.entry-content',
            'div[role="main"]'
        ]

        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        # If no main content area found, use body
        if not main_content:
            main_content = soup.find('body')

        if main_content:
            # Get text and clean it up
            text = main_content.get_text(separator=' ', strip=True)
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            return text

        return ""

    def fetch_url_with_retry(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Fetch URL with exponential backoff retry"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                wait_time = 2 ** (attempt + 2)  # 4, 8, 16 seconds
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch {url} after {max_retries} attempts")
        return None

    def calculate_mcf_relevance(self, text: str) -> float:
        """Calculate MCF relevance score for text"""
        if not text:
            return 0.0

        text_lower = text.lower()
        total_score = 0
        max_possible_score = 0

        for category, config in self.mcf_keywords.items():
            weight = config['weight']
            keywords = config['keywords']
            max_possible_score += weight

            for keyword in keywords:
                if keyword.lower() in text_lower:
                    total_score += weight
                    break  # Only count each category once

        # Normalize to 0-1 range
        if max_possible_score > 0:
            return total_score / max_possible_score
        return 0.0

    def extract_chinese_entities(self, text: str) -> List[Dict]:
        """Extract Chinese defense entities from text"""
        entities = []

        # Chinese defense companies and organizations
        entity_patterns = {
            'AVIC': 'defense_company',
            'NORINCO': 'defense_company',
            'CETC': 'defense_company',
            'CASIC': 'defense_company',
            'CASC': 'defense_company',
            'AECC': 'defense_company',
            'SASTIND': 'government_agency',
            'Huawei': 'technology_company',
            'ZTE': 'technology_company',
            'DJI': 'technology_company',
            'Hikvision': 'technology_company',
            "People's Liberation Army": 'military',
            'PLA': 'military',
            'Central Military Commission': 'military',
            'Beijing Institute of Technology': 'university',
            'Harbin Engineering University': 'university',
            'NUDT': 'university',
            'National University of Defense Technology': 'university'
        }

        for entity_name, entity_type in entity_patterns.items():
            if entity_name in text:
                # Extract context around entity mention
                pattern = re.compile(r'.{0,100}' + re.escape(entity_name) + r'.{0,100}')
                matches = pattern.findall(text)

                for match in matches[:3]:  # Limit to 3 mentions per entity
                    entities.append({
                        'entity_name': entity_name,
                        'entity_type': entity_type,
                        'context': match.strip()
                    })

        return entities

    def save_to_database(self, document: Dict) -> bool:
        """Save document and entities to database"""
        try:
            conn = sqlite3.connect(self.warehouse_path)
            cursor = conn.cursor()

            # Insert document
            cursor.execute('''
                INSERT OR REPLACE INTO mcf_documents
                (url, title, content, relevance_score, collector, collection_timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                document.get('url', ''),
                document.get('title', ''),
                document.get('content', ''),
                document.get('relevance_score', 0.0),
                document.get('collector', 'unknown'),
                document.get('collection_timestamp', datetime.now().isoformat()),
                json.dumps(document.get('metadata', {}))
            ))

            doc_id = cursor.lastrowid

            # Insert entities
            entities = document.get('entities', [])
            for entity in entities:
                cursor.execute('''
                    INSERT INTO mcf_entities (document_id, entity_name, entity_type, context)
                    VALUES (?, ?, ?, ?)
                ''', (doc_id, entity['entity_name'], entity['entity_type'], entity.get('context', '')))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            return False

    def extract_document_metadata(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract metadata from webpage"""
        metadata = {
            'title': 'Unknown',
            'publication_date': None,
            'authors': [],
            'tags': []
        }

        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)

        # Meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '')

        # Publication date
        date_selectors = ['time', '.date', '.published', 'meta[property="article:published_time"]']
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get('content') or date_elem.get_text()
                if date_text:
                    metadata['publication_date'] = date_text
                    break

        return metadata
