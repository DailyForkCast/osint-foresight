"""
OpenAlex JSONL China Processor
Handles newline-delimited JSON format from OpenAlex bulk data
"""

import os
import json
import gzip
import sqlite3
from datetime import datetime
from typing import Dict, List, Generator

class OpenAlexJSONLProcessor:
    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.raw_path = "F:/OSINT_Backups/openalex"
        self.output_path = "data/processed/openalex_china_jsonl"

        # Comprehensive China detection
        self.china_patterns = {
            'institutions': [
                'tsinghua', 'peking', 'fudan', 'zhejiang', 'shanghai jiao',
                'chinese academy', 'cas ', 'beijing', 'wuhan university',
                'nanjing', 'harbin', 'ustc', 'sun yat-sen', 'xiamen'
            ],
            'countries': ['CN', 'CHN', 'China', 'china'],
            'keywords': [
                'china', 'chinese', 'beijing', 'shanghai', 'guangzhou',
                'shenzhen', 'hong kong', 'macau', 'taiwan'
            ]
        }

        os.makedirs(self.output_path, exist_ok=True)
        self.stats = {
            'files_processed': 0,
            'records_scanned': 0,
            'china_found': 0,
            'errors': 0
        }

    def read_jsonl_gz(self, file_path: str) -> Generator:
        """Read gzipped JSONL file line by line"""
        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            self.stats['errors'] += 1

    def process(self):
        print(f"[{datetime.now()}] Starting OpenAlex JSONL processing...")

        # Find all .gz files
        gz_files = []
        for root, dirs, files in os.walk(self.raw_path):
            for file in files:
                if file.endswith('.gz'):
                    gz_files.append(os.path.join(root, file))

        print(f"Found {len(gz_files)} .gz files to process")

        china_collaborations = []
        technology_map = {}
        institution_network = {}

        # Process files
        for i, file_path in enumerate(gz_files[:500], 1):  # Process first 500 files
            if i % 50 == 0:
                print(f"Processing file {i}/{min(500, len(gz_files))}: {os.path.basename(file_path)}")
                print(f"  Stats: {self.stats['china_found']} China items found from {self.stats['records_scanned']} records")

            self.stats['files_processed'] += 1

            # Process each line in the JSONL file
            for record in self.read_jsonl_gz(file_path):
                self.stats['records_scanned'] += 1

                if self.has_china_connection(record):
                    self.stats['china_found'] += 1

                    # Extract collaboration info
                    collab = self.extract_collaboration(record)
                    china_collaborations.append(collab)

                    # Track technology areas
                    for concept in record.get('concepts', []):
                        tech = concept.get('display_name', '')
                        if tech:
                            technology_map[tech] = technology_map.get(tech, 0) + 1

                    # Track institutions
                    self.update_institution_network(record, institution_network)

                    # Save periodically
                    if len(china_collaborations) >= 1000:
                        self.save_batch(china_collaborations, technology_map)
                        china_collaborations = []

        # Save final batch
        if china_collaborations:
            self.save_batch(china_collaborations, technology_map)

        # Print final stats
        print(f"\n=== OpenAlex Processing Complete ===")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Records scanned: {self.stats['records_scanned']:,}")
        print(f"China connections found: {self.stats['china_found']:,}")
        print(f"Error count: {self.stats['errors']}")
        print(f"Top technologies: {list(sorted(technology_map.items(), key=lambda x: x[1], reverse=True)[:10])}")

        return self.stats['china_found']

    def has_china_connection(self, record: Dict) -> bool:
        """Check if record has China connection"""
        # Check authorships for Chinese institutions
        for authorship in record.get('authorships', []):
            for inst in authorship.get('institutions', []):
                # Check country
                if inst.get('country_code') in self.china_patterns['countries']:
                    return True
                # Check institution name
                inst_name = inst.get('display_name', '').lower()
                for pattern in self.china_patterns['institutions']:
                    if pattern in inst_name:
                        return True

        # Check title/abstract for China keywords
        text = (record.get('title', '') + ' ' +
                record.get('abstract', '')).lower()
        for keyword in self.china_patterns['keywords']:
            if keyword in text:
                return True

        return False

    def extract_collaboration(self, record: Dict) -> Dict:
        """Extract collaboration details"""
        china_institutions = []
        other_institutions = []

        for authorship in record.get('authorships', []):
            for inst in authorship.get('institutions', []):
                inst_info = {
                    'name': inst.get('display_name', ''),
                    'country': inst.get('country_code', ''),
                    'type': inst.get('type', '')
                }

                if inst.get('country_code') in self.china_patterns['countries']:
                    china_institutions.append(inst_info)
                else:
                    other_institutions.append(inst_info)

        return {
            'id': record.get('id', ''),
            'doi': record.get('doi', ''),
            'title': record.get('title', ''),
            'publication_date': record.get('publication_date', ''),
            'type': record.get('type', ''),
            'cited_by_count': record.get('cited_by_count', 0),
            'china_institutions': china_institutions,
            'collaborating_institutions': other_institutions,
            'concepts': [c.get('display_name') for c in record.get('concepts', [])][:5],
            'is_international': len(other_institutions) > 0
        }

    def update_institution_network(self, record: Dict, network: Dict):
        """Update institution collaboration network"""
        institutions = []
        for authorship in record.get('authorships', []):
            for inst in authorship.get('institutions', []):
                name = inst.get('display_name', '')
                if name:
                    institutions.append(name)

        # Create co-occurrence pairs
        for i, inst1 in enumerate(institutions):
            if inst1 not in network:
                network[inst1] = {}
            for inst2 in institutions[i+1:]:
                network[inst1][inst2] = network[inst1].get(inst2, 0) + 1

    def save_batch(self, collaborations: List, technology_map: Dict):
        """Save a batch of collaborations"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save to JSON
        output_file = os.path.join(self.output_path, f'batch_{timestamp}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'extraction_date': datetime.now().isoformat(),
                'batch_size': len(collaborations),
                'collaborations': collaborations,
                'top_technologies': sorted(technology_map.items(),
                                          key=lambda x: x[1], reverse=True)[:20]
            }, f, indent=2)

        print(f"  Saved batch of {len(collaborations)} to {output_file}")

        # Save to database
        self.save_to_database(collaborations)

    def save_to_database(self, collaborations: List):
        """Save to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS openalex_china_jsonl
                       (id TEXT PRIMARY KEY, doi TEXT, title TEXT,
                        publication_date TEXT, type TEXT, cited_by_count INTEGER,
                        china_institutions TEXT, collaborating_institutions TEXT,
                        concepts TEXT, is_international INTEGER,
                        processed_date TEXT)''')

        for collab in collaborations:
            cur.execute('''INSERT OR REPLACE INTO openalex_china_jsonl
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (collab['id'], collab['doi'], collab['title'],
                        collab['publication_date'], collab['type'],
                        collab['cited_by_count'],
                        json.dumps(collab['china_institutions']),
                        json.dumps(collab['collaborating_institutions']),
                        json.dumps(collab['concepts']),
                        1 if collab['is_international'] else 0,
                        datetime.now().isoformat()))

        conn.commit()
        conn.close()

if __name__ == "__main__":
    processor = OpenAlexJSONLProcessor()
    count = processor.process()
    print(f"\nTotal China collaborations found: {count}")