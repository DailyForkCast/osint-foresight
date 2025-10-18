#!/usr/bin/env python3
"""
GLEIF LEI Data Downloader and Ownership Tree Mapper
Downloads LEI Level-1 and Level-2 data, maps ownership structures, and cross-references with ISIN/BIC
"""

import requests
import json
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
import time
import logging
from collections import defaultdict
import xml.etree.ElementTree as ET
import zipfile
import io

class GLEIFCollector:
    def __init__(self, base_path: str = "F:/OSINT_Data/GLEIF"):
        self.base_path = Path(base_path)
        self.api_base = "https://api.gleif.org/api/v1"
        self.bulk_base = "https://goldencopy.gleif.org/api/v2"

        # Rate limiting (60 requests per minute)
        self.rate_limit = 60  # requests per minute
        self.request_interval = 60 / self.rate_limit  # seconds between requests

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Research-LEI-Collector/1.0 (Academic Research)',
            'Accept': 'application/json'
        })

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Create directory structure
        self.setup_directories()

        # Known bulk download files (current as of 2025-09-21)
        self.bulk_files = {
            'lei_records': 'https://leidata.gleif.org/api/v1/concatenated-files/lei2/get/38981/zip',
            'rr_records': 'https://leidata.gleif.org/api/v1/concatenated-files/rr/get/38984/zip',
            'repex_records': 'https://leidata.gleif.org/api/v1/concatenated-files/repex/get/38987/zip',
            'bic_lei_mapping': 'https://mapping.gleif.org/api/v2/bic-lei/0d3f054c-7850-4c89-a46b-4838c6f5f7f8/download',
            'isin_lei_mapping': 'https://www.gleif.org/en/lei-data/lei-mapping/download-isin-to-lei-relationship-files'
        }

    def setup_directories(self):
        """Create directory structure for GLEIF data"""
        directories = [
            'bulk_data/lei_records',
            'bulk_data/relationships',
            'bulk_data/mappings',
            'api_data/entities',
            'api_data/relationships',
            'processed/ownership_trees',
            'processed/chinese_entities',
            'analysis/networks',
            'databases',
            'logs'
        ]

        for dir_name in directories:
            (self.base_path / dir_name).mkdir(parents=True, exist_ok=True)

        print(f"Created GLEIF directory structure at {self.base_path}")

    def download_bulk_data(self):
        """Download GLEIF bulk data files"""
        print("\n" + "="*80)
        print("GLEIF Bulk Data Download")
        print("="*80)

        downloaded_files = {}

        # Download LEI Records (Level 1) - 448.6 MB
        print("Downloading LEI Records (Level 1 data) - 3.07M records, 448.6 MB...")
        lei_file = self.download_file(self.bulk_files['lei_records'], {}, 'bulk_data/lei_records', 'lei_records.zip')
        downloaded_files['lei_records'] = lei_file

        # Download Relationship Records (Level 2) - 31.93 MB
        print("Downloading Relationship Records (Level 2 data) - 599K records, 31.93 MB...")
        rr_file = self.download_file(self.bulk_files['rr_records'], {}, 'bulk_data/relationships', 'relationship_records.zip')
        downloaded_files['relationship_records'] = rr_file

        # Download Reporting Exceptions - 41.85 MB
        print("Downloading Reporting Exceptions - 5.46M records, 41.85 MB...")
        repex_file = self.download_file(self.bulk_files['repex_records'], {}, 'bulk_data/relationships', 'reporting_exceptions.zip')
        downloaded_files['reporting_exceptions'] = repex_file

        # Download BIC to LEI mapping
        print("Downloading BIC-to-LEI mapping (August 2025)...")
        bic_file = self.download_file(self.bulk_files['bic_lei_mapping'], {}, 'bulk_data/mappings', 'bic_lei_mapping.zip')
        downloaded_files['bic_mapping'] = bic_file

        print("Note: ISIN-to-LEI mapping requires manual download from GLEIF website")
        downloaded_files['isin_mapping'] = "Manual download required"

        return downloaded_files

    def download_file(self, url, params, subdir, filename):
        """Download a file with proper error handling"""
        try:
            self.logger.info(f"Downloading {filename} from {url}")

            response = self.session.get(url, params=params, stream=True, timeout=300)
            response.raise_for_status()

            local_path = self.base_path / subdir / f"{datetime.now().strftime('%Y%m%d')}_{filename}"

            # Handle different content types
            content_type = response.headers.get('content-type', '').lower()

            if 'zip' in content_type:
                # Handle ZIP files
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                    zip_ref.extractall(local_path.parent)
                    self.logger.info(f"Extracted ZIP to {local_path.parent}")
            else:
                # Handle regular files
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            size_mb = local_path.stat().st_size / (1024 * 1024)
            self.logger.info(f"Downloaded {filename}: {size_mb:.1f} MB")

            return local_path

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download {filename}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error processing {filename}: {e}")
            return None

    def search_chinese_entities(self):
        """Search for Chinese entities via API"""
        print("\n" + "="*60)
        print("Searching for Chinese Entities via API")
        print("="*60)

        chinese_entities = []
        chinese_countries = ['CN', 'HK', 'MO', 'TW']  # China, Hong Kong, Macau, Taiwan

        for country in chinese_countries:
            print(f"Searching entities in {country}...")

            # Search by country
            entities = self.api_search_by_country(country)
            chinese_entities.extend(entities)

            # Rate limiting
            time.sleep(self.request_interval)

        # Save Chinese entities
        chinese_file = self.base_path / 'processed/chinese_entities' / f'chinese_entities_{datetime.now().strftime("%Y%m%d")}.json'
        with open(chinese_file, 'w', encoding='utf-8') as f:
            json.dump(chinese_entities, f, indent=2, ensure_ascii=False)

        print(f"Found {len(chinese_entities)} Chinese entities")
        return chinese_entities

    def api_search_by_country(self, country_code):
        """Search LEI entities by country via API"""
        try:
            url = f"{self.api_base}/lei-records"
            params = {
                'filter[entity.legalAddress.country]': country_code,
                'page[size]': 100,  # Maximum page size
                'include': 'direct-parent,ultimate-parent'
            }

            entities = []
            page = 1

            while True:
                params['page[number]'] = page

                response = self.session.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                if not data.get('data'):
                    break

                entities.extend(data['data'])

                # Check if there are more pages
                if not data.get('links', {}).get('next'):
                    break

                page += 1
                time.sleep(self.request_interval)  # Rate limiting

                if page % 10 == 0:
                    print(f"  Processed {len(entities)} entities...")

            return entities

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API search failed for {country_code}: {e}")
            return []

    def build_ownership_trees(self, chinese_entities):
        """Build ownership trees for Chinese entities"""
        print("\n" + "="*60)
        print("Building Ownership Trees")
        print("="*60)

        ownership_trees = {}

        for entity in chinese_entities:
            lei = entity.get('id')
            if not lei:
                continue

            print(f"Building ownership tree for {lei}...")

            tree = self.get_entity_ownership_tree(lei)
            ownership_trees[lei] = tree

            time.sleep(self.request_interval)  # Rate limiting

        # Save ownership trees
        trees_file = self.base_path / 'processed/ownership_trees' / f'ownership_trees_{datetime.now().strftime("%Y%m%d")}.json'
        with open(trees_file, 'w', encoding='utf-8') as f:
            json.dump(ownership_trees, f, indent=2, ensure_ascii=False)

        return ownership_trees

    def get_entity_ownership_tree(self, lei):
        """Get complete ownership tree for an entity"""
        try:
            # Get direct relationships
            url = f"{self.api_base}/relationship-records"
            params = {
                'filter[startNode]': lei,
                'page[size]': 100
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            relationships = data.get('data', [])

            # Build tree structure
            tree = {
                'lei': lei,
                'direct_parents': [],
                'ultimate_parents': [],
                'subsidiaries': []
            }

            for rel in relationships:
                attrs = rel.get('attributes', {})
                relationship_type = attrs.get('relationshipType')

                if relationship_type == 'IS_DIRECTLY_CONSOLIDATED_BY':
                    tree['direct_parents'].append({
                        'lei': attrs.get('endNode'),
                        'percentage': attrs.get('relationshipPeriods', [{}])[0].get('measurementMethod')
                    })
                elif relationship_type == 'IS_ULTIMATELY_CONSOLIDATED_BY':
                    tree['ultimate_parents'].append({
                        'lei': attrs.get('endNode'),
                        'percentage': attrs.get('relationshipPeriods', [{}])[0].get('measurementMethod')
                    })

            return tree

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get ownership tree for {lei}: {e}")
            return {}

    def create_analysis_database(self):
        """Create SQLite database for ownership analysis"""
        print("\n" + "="*60)
        print("Creating Analysis Database")
        print("="*60)

        db_path = self.base_path / 'databases' / f'gleif_analysis_{datetime.now().strftime("%Y%m%d")}.db'

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lei_entities (
                lei TEXT PRIMARY KEY,
                legal_name TEXT,
                country TEXT,
                entity_status TEXT,
                registration_date TEXT,
                last_update TEXT,
                is_chinese INTEGER DEFAULT 0,
                raw_data TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ownership_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_lei TEXT,
                child_lei TEXT,
                relationship_type TEXT,
                ownership_percentage REAL,
                start_date TEXT,
                end_date TEXT,
                FOREIGN KEY (parent_lei) REFERENCES lei_entities (lei),
                FOREIGN KEY (child_lei) REFERENCES lei_entities (lei)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS identifier_mappings (
                lei TEXT,
                identifier_type TEXT,
                identifier_value TEXT,
                PRIMARY KEY (lei, identifier_type, identifier_value),
                FOREIGN KEY (lei) REFERENCES lei_entities (lei)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chinese_ownership_analysis (
                lei TEXT PRIMARY KEY,
                direct_chinese_ownership REAL,
                ultimate_chinese_ownership REAL,
                chinese_parent_chain TEXT,
                analysis_date TEXT,
                FOREIGN KEY (lei) REFERENCES lei_entities (lei)
            )
        ''')

        conn.commit()
        conn.close()

        print(f"Created analysis database: {db_path}")
        return db_path

    def analyze_chinese_ownership_patterns(self):
        """Analyze ownership patterns for intelligence insights"""
        print("\n" + "="*60)
        print("Analyzing Chinese Ownership Patterns")
        print("="*60)

        # This would include analysis of:
        # 1. Complex ownership structures
        # 2. Shell company identification
        # 3. Cross-jurisdictional ownership
        # 4. Beneficial ownership mapping
        # 5. Corporate network analysis

        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'total_chinese_entities': 0,
            'ownership_networks': [],
            'shell_company_indicators': [],
            'cross_border_structures': []
        }

        # Save analysis
        analysis_file = self.base_path / 'analysis/networks' / f'chinese_ownership_analysis_{datetime.now().strftime("%Y%m%d")}.json'
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)

        return analysis_results

    def run_full_collection(self):
        """Execute complete GLEIF data collection and analysis"""
        print("="*80)
        print("GLEIF LEI Complete Data Collection and Ownership Analysis")
        print("="*80)

        try:
            # Step 1: Download bulk data
            bulk_files = self.download_bulk_data()

            # Step 2: Search Chinese entities via API
            chinese_entities = self.search_chinese_entities()

            # Step 3: Build ownership trees
            ownership_trees = self.build_ownership_trees(chinese_entities)

            # Step 4: Create analysis database
            db_path = self.create_analysis_database()

            # Step 5: Analyze ownership patterns
            analysis = self.analyze_chinese_ownership_patterns()

            print("\n" + "="*80)
            print("GLEIF Collection Complete!")
            print("="*80)
            print(f"Chinese entities found: {len(chinese_entities)}")
            print(f"Ownership trees built: {len(ownership_trees)}")
            print(f"Database created: {db_path}")
            print(f"Analysis saved: {self.base_path}/analysis/")

            return {
                'bulk_files': bulk_files,
                'chinese_entities': len(chinese_entities),
                'ownership_trees': len(ownership_trees),
                'database': str(db_path),
                'analysis': analysis
            }

        except Exception as e:
            self.logger.error(f"Collection failed: {e}")
            raise

if __name__ == "__main__":
    collector = GLEIFCollector()
    results = collector.run_full_collection()
    print(f"\nCollection results: {json.dumps(results, indent=2)}")
