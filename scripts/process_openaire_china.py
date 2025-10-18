"""
OpenAIRE China Project Processor
Extracts EU-China research collaborations from OpenAIRE data
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List

class OpenAIREChinaProcessor:
    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.raw_paths = [
            "F:/OSINT_Data/openaire_comprehensive_20250921",
            "F:/OSINT_Data/openaire_multicountry_20250921"
        ]
        self.output_path = "data/processed/openaire_china_deep"

        # Enhanced China detection
        self.china_entities = {
            'institutions': [
                'tsinghua', 'peking', 'fudan', 'zhejiang', 'shanghai jiao tong',
                'ustc', 'nanjing', 'wuhan', 'xi\'an jiaotong', 'harbin institute',
                'chinese academy of sciences', 'cas ', 'beijing institute'
            ],
            'companies': [
                'huawei', 'zte', 'alibaba', 'tencent', 'baidu', 'bytedance',
                'xiaomi', 'dji', 'sensetime', 'megvii', 'iflytek', 'hikvision'
            ],
            'locations': [
                'beijing', 'shanghai', 'shenzhen', 'guangzhou', 'hangzhou',
                'chengdu', 'wuhan', 'xi\'an', 'nanjing', 'tianjin'
            ]
        }

        os.makedirs(self.output_path, exist_ok=True)

    def process(self):
        print(f"[{datetime.now()}] Starting OpenAIRE China processing...")

        all_projects = []
        funding_analysis = {}
        technology_mapping = {}

        for path in self.raw_paths:
            if os.path.exists(path):
                print(f"Processing {path}...")
                projects = self.process_directory(path)
                all_projects.extend(projects)

        # Analyze projects
        for project in all_projects:
            # Track funding
            if 'funding' in project:
                funding = project['funding'].get('amount', 0)
                funder = project['funding'].get('funder', 'Unknown')
                funding_analysis[funder] = funding_analysis.get(funder, 0) + funding

            # Track technology areas
            for keyword in project.get('keywords', []):
                technology_mapping[keyword] = technology_mapping.get(keyword, 0) + 1

        # Save results
        self.save_results(all_projects, funding_analysis, technology_mapping)
        return len(all_projects)

    def process_directory(self, directory):
        china_projects = []

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.json', '.jsonl')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            if file.endswith('.jsonl'):
                                for line in f:
                                    data = json.loads(line)
                                    if self.has_china_involvement(data):
                                        project = self.extract_project_info(data)
                                        china_projects.append(project)
                            else:
                                data = json.load(f)
                                if isinstance(data, list):
                                    for item in data:
                                        if self.has_china_involvement(item):
                                            project = self.extract_project_info(item)
                                            china_projects.append(project)
                                elif self.has_china_involvement(data):
                                    project = self.extract_project_info(data)
                                    china_projects.append(project)
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

        return china_projects

    def has_china_involvement(self, data):
        text = json.dumps(data).lower()

        # Check for Chinese institutions
        for inst in self.china_entities['institutions']:
            if inst in text:
                return True

        # Check for Chinese companies
        for company in self.china_entities['companies']:
            if company in text:
                return True

        # Check for Chinese locations
        for location in self.china_entities['locations']:
            if location in text:
                return True

        # Check country codes
        if '"cn"' in text or '"chn"' in text or 'china' in text:
            return True

        return False

    def extract_project_info(self, data):
        return {
            'id': data.get('id', data.get('projectId', '')),
            'title': data.get('title', data.get('projectTitle', '')),
            'acronym': data.get('acronym', ''),
            'start_date': data.get('startDate', ''),
            'end_date': data.get('endDate', ''),
            'funding': self.extract_funding(data),
            'participants': self.extract_participants(data),
            'keywords': data.get('keywords', data.get('subjects', [])),
            'china_entities': self.identify_china_entities(data),
            'risk_level': self.assess_risk_level(data)
        }

    def extract_funding(self, data):
        funding = {
            'amount': 0,
            'currency': 'EUR',
            'funder': ''
        }

        if 'funding' in data:
            funding['amount'] = data['funding'].get('amount', 0)
            funding['funder'] = data['funding'].get('funder', '')
        elif 'totalCost' in data:
            funding['amount'] = data.get('totalCost', 0)
            funding['funder'] = data.get('fundingScheme', '')

        return funding

    def extract_participants(self, data):
        participants = []

        if 'participants' in data:
            for p in data['participants']:
                participants.append({
                    'name': p.get('name', ''),
                    'country': p.get('country', ''),
                    'role': p.get('role', 'participant')
                })
        elif 'organizations' in data:
            for org in data['organizations']:
                participants.append({
                    'name': org.get('name', ''),
                    'country': org.get('country', ''),
                    'role': org.get('role', 'participant')
                })

        return participants

    def identify_china_entities(self, data):
        found = []
        text = json.dumps(data).lower()

        for category, entities in self.china_entities.items():
            for entity in entities:
                if entity in text:
                    found.append({
                        'type': category,
                        'entity': entity
                    })

        return found

    def assess_risk_level(self, data):
        risk_score = 0

        # Check for dual-use keywords
        dual_use_keywords = [
            'quantum', 'ai', 'artificial intelligence', 'semiconductor',
            'aerospace', 'nuclear', 'missile', 'cryptography', 'cyber',
            'defense', 'military', '5g', '6g', 'biotechnology'
        ]

        text = json.dumps(data).lower()
        for keyword in dual_use_keywords:
            if keyword in text:
                risk_score += 10

        # Check for Chinese military universities
        military_unis = ['nudt', 'national defense', 'pla ']
        for uni in military_unis:
            if uni in text:
                risk_score += 50

        if risk_score >= 50:
            return 'HIGH'
        elif risk_score >= 20:
            return 'MEDIUM'
        else:
            return 'LOW'

    def save_results(self, projects, funding, technologies):
        # Save to JSON
        output_file = os.path.join(self.output_path, f'openaire_china_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'extraction_date': datetime.now().isoformat(),
                'total_projects': len(projects),
                'high_risk_projects': len([p for p in projects if p['risk_level'] == 'HIGH']),
                'total_funding': sum(funding.values()),
                'top_funders': sorted(funding.items(), key=lambda x: x[1], reverse=True)[:10],
                'top_technologies': sorted(technologies.items(), key=lambda x: x[1], reverse=True)[:20],
                'projects': projects[:500]  # First 500 projects
            }, f, indent=2)

        print(f"Saved {len(projects)} OpenAIRE projects to {output_file}")

        # Save to database
        self.save_to_database(projects)

    def save_to_database(self, projects):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS openaire_china_deep
                       (id TEXT PRIMARY KEY, title TEXT, acronym TEXT,
                        start_date TEXT, end_date TEXT, funding_amount REAL,
                        participants TEXT, china_entities TEXT, risk_level TEXT,
                        processed_date TEXT)''')

        for project in projects:
            cur.execute('''INSERT OR REPLACE INTO openaire_china_deep VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (project['id'], project['title'], project['acronym'],
                        project['start_date'], project['end_date'],
                        project['funding']['amount'],
                        json.dumps(project['participants']),
                        json.dumps(project['china_entities']),
                        project['risk_level'],
                        datetime.now().isoformat()))

        conn.commit()
        conn.close()

if __name__ == "__main__":
    processor = OpenAIREChinaProcessor()
    count = processor.process()
    print(f"Completed OpenAIRE processing: {count} EU-China projects found")