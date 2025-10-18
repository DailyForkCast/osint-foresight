"""
OpenAlex China Collaboration Processor
Processes bulk OpenAlex data for China research collaborations
"""

import os
import json
import sqlite3
import gzip
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class OpenAlexChinaProcessor:
    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.raw_path = "F:/OSINT_Backups/openalex"
        self.output_path = "data/processed/openalex_china_deep"
        self.china_keywords = [
            'china', 'chinese', 'beijing', 'shanghai', 'shenzhen', 'guangzhou',
            'tsinghua', 'peking university', 'fudan', 'zhejiang', 'cas',
            'chinese academy of sciences', 'huawei', 'alibaba', 'tencent'
        ]

        os.makedirs(self.output_path, exist_ok=True)

    def process(self):
        print(f"[{datetime.now()}] Starting OpenAlex China processing...")

        # Find all OpenAlex files
        files = self.find_openalex_files()
        print(f"Found {len(files)} OpenAlex files to process")

        china_collaborations = []
        technology_areas = {}
        institution_network = {}

        for i, file_path in enumerate(files[:100], 1):  # Process first 100 for now
            if i % 10 == 0:
                print(f"Processing file {i}/{min(100, len(files))}: {file_path}")

            try:
                data = self.read_file(file_path)

                # Check for China involvement
                if self.has_china_connection(data):
                    collaboration = self.extract_collaboration(data)
                    china_collaborations.append(collaboration)

                    # Track technology areas
                    if 'concepts' in data:
                        for concept in data.get('concepts', []):
                            tech = concept.get('display_name', 'Unknown')
                            technology_areas[tech] = technology_areas.get(tech, 0) + 1

                    # Build institution network
                    if 'authorships' in data:
                        institutions = [a.get('institutions', []) for a in data['authorships']]
                        self.update_network(institution_network, institutions)

            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue

        # Save results
        self.save_results(china_collaborations, technology_areas, institution_network)
        return len(china_collaborations)

    def find_openalex_files(self):
        files = []
        for root, dirs, filenames in os.walk(self.raw_path):
            for filename in filenames:
                if filename.endswith(('.json', '.jsonl', '.gz')):
                    files.append(os.path.join(root, filename))
        return files

    def read_file(self, file_path):
        if file_path.endswith('.gz'):
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                return json.loads(f.read())
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

    def has_china_connection(self, data):
        text_to_check = json.dumps(data).lower()
        return any(keyword in text_to_check for keyword in self.china_keywords)

    def extract_collaboration(self, data):
        return {
            'id': data.get('id', ''),
            'title': data.get('title', ''),
            'publication_date': data.get('publication_date', ''),
            'cited_by_count': data.get('cited_by_count', 0),
            'concepts': [c.get('display_name') for c in data.get('concepts', [])][:5],
            'institutions': self.extract_institutions(data),
            'china_involvement': self.classify_china_involvement(data)
        }

    def extract_institutions(self, data):
        institutions = set()
        for authorship in data.get('authorships', []):
            for inst in authorship.get('institutions', []):
                name = inst.get('display_name', '')
                country = inst.get('country_code', '')
                if name:
                    institutions.add(f"{name} ({country})")
        return list(institutions)

    def classify_china_involvement(self, data):
        # Classify the type of China involvement
        china_institutions = 0
        total_institutions = 0

        for authorship in data.get('authorships', []):
            for inst in authorship.get('institutions', []):
                total_institutions += 1
                if inst.get('country_code') == 'CN':
                    china_institutions += 1

        if china_institutions == 0:
            return 'indirect'
        elif china_institutions == total_institutions:
            return 'china_only'
        else:
            return 'collaboration'

    def update_network(self, network, institutions):
        # Build co-occurrence network
        for inst_list in institutions:
            for inst1 in inst_list:
                name1 = inst1.get('display_name', '')
                if name1 not in network:
                    network[name1] = {}
                for inst2 in inst_list:
                    if inst1 != inst2:
                        name2 = inst2.get('display_name', '')
                        network[name1][name2] = network[name1].get(name2, 0) + 1

    def save_results(self, collaborations, technologies, network):
        # Save collaboration data
        output_file = os.path.join(self.output_path, f'china_collaborations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'extraction_date': datetime.now().isoformat(),
                'total_collaborations': len(collaborations),
                'collaborations': collaborations[:1000],  # First 1000
                'top_technologies': sorted(technologies.items(), key=lambda x: x[1], reverse=True)[:50],
                'network_size': len(network)
            }, f, indent=2)

        print(f"Saved {len(collaborations)} collaborations to {output_file}")

        # Also save to database
        self.save_to_database(collaborations)

    def save_to_database(self, collaborations):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS openalex_china_deep
                       (id TEXT PRIMARY KEY, title TEXT, publication_date TEXT,
                        cited_by_count INTEGER, concepts TEXT, institutions TEXT,
                        china_involvement TEXT, processed_date TEXT)''')

        for collab in collaborations:
            cur.execute('''INSERT OR REPLACE INTO openalex_china_deep VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (collab['id'], collab['title'], collab['publication_date'],
                        collab['cited_by_count'], json.dumps(collab['concepts']),
                        json.dumps(collab['institutions']), collab['china_involvement'],
                        datetime.now().isoformat()))

        conn.commit()
        conn.close()

if __name__ == "__main__":
    processor = OpenAlexChinaProcessor()
    count = processor.process()
    print(f"Completed OpenAlex processing: {count} China collaborations found")