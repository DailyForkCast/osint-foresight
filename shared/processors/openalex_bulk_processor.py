#!/usr/bin/env python3
"""
OpenAlex Bulk Data Processor for Italy
Processes OpenAlex data for Italian institutions and China collaborations
"""

import json
import requests
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import gzip
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAlexBulkProcessor:
    def __init__(self):
        self.output_path = Path("data/processed/openalex_italy")
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Use the existing OpenAlex backup data
        self.backup_path = Path("F:/OSINT_Backups/openalex/data")

        # Italian institutions to focus on
        self.italian_keywords = [
            'sapienza', 'bologna', 'milan', 'padua', 'naples', 'turin',
            'politecnico', 'florence', 'pisa', 'rome', 'venice', 'genoa',
            'cnr', 'infn', 'enea', 'iit', 'leonardo', 'italian', 'italy'
        ]

        # Chinese institutions
        self.chinese_keywords = [
            'chinese academy', 'tsinghua', 'peking', 'beijing', 'shanghai',
            'zhejiang', 'fudan', 'nanjing', 'wuhan', 'harbin', 'china'
        ]

        self.results = {
            'italian_institutions': [],
            'china_collaborations': [],
            'dual_use_research': [],
            'statistics': defaultdict(int)
        }

    def process_institutions_file(self, file_path: Path) -> list:
        """Process an institutions data file"""
        italian_institutions = []

        try:
            # Handle both .gz and regular JSON files
            if file_path.suffix == '.gz':
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    for line in f:
                        try:
                            inst = json.loads(line)
                            if self.is_italian_institution(inst):
                                italian_institutions.append(self.extract_institution_info(inst))
                        except json.JSONDecodeError:
                            continue
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f) if file_path.suffix == '.json' else []
                    if isinstance(data, list):
                        for inst in data:
                            if self.is_italian_institution(inst):
                                italian_institutions.append(self.extract_institution_info(inst))

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

        return italian_institutions

    def is_italian_institution(self, inst: dict) -> bool:
        """Check if institution is Italian"""
        # Check country
        if inst.get('country_code') == 'IT':
            return True

        # Check name and aliases
        name = (inst.get('display_name', '') + ' ' +
                ' '.join(inst.get('display_name_alternatives', []))).lower()

        return any(keyword in name for keyword in self.italian_keywords)

    def extract_institution_info(self, inst: dict) -> dict:
        """Extract relevant institution information"""
        return {
            'id': inst.get('id'),
            'name': inst.get('display_name'),
            'ror': inst.get('ror'),
            'type': inst.get('type'),
            'works_count': inst.get('works_count', 0),
            'cited_by_count': inst.get('cited_by_count', 0),
            'homepage': inst.get('homepage_url'),
            'concepts': self.extract_top_concepts(inst)
        }

    def extract_top_concepts(self, inst: dict) -> list:
        """Extract top research concepts"""
        concepts = inst.get('x_concepts', [])
        return [{'name': c.get('display_name'), 'score': c.get('score')}
                for c in concepts[:10]]

    def analyze_collaborations(self, works_data: list) -> dict:
        """Analyze works for China collaborations"""
        collaborations = {
            'total_works': len(works_data),
            'china_collaborations': [],
            'collaboration_rate': 0.0,
            'top_chinese_partners': defaultdict(int),
            'research_areas': defaultdict(int)
        }

        for work in works_data:
            # Check for China collaboration
            has_china = False
            institutions = work.get('institutions', [])

            italian_count = sum(1 for i in institutions if i.get('country_code') == 'IT')
            chinese_count = sum(1 for i in institutions if i.get('country_code') == 'CN')

            if italian_count > 0 and chinese_count > 0:
                has_china = True
                collaborations['china_collaborations'].append({
                    'title': work.get('title'),
                    'year': work.get('publication_year'),
                    'doi': work.get('doi'),
                    'chinese_institutions': [i.get('display_name') for i in institutions
                                            if i.get('country_code') == 'CN']
                })

                # Track Chinese partners
                for inst in institutions:
                    if inst.get('country_code') == 'CN':
                        collaborations['top_chinese_partners'][inst.get('display_name', 'Unknown')] += 1

            # Track research areas
            for concept in work.get('concepts', []):
                collaborations['research_areas'][concept.get('display_name', 'Unknown')] += 1

        if collaborations['total_works'] > 0:
            collaborations['collaboration_rate'] = (
                len(collaborations['china_collaborations']) / collaborations['total_works'] * 100
            )

        return collaborations

    def check_dual_use_research(self, work: dict) -> list:
        """Check for dual-use research indicators"""
        dual_use_keywords = [
            'quantum', 'cryptography', 'encryption', 'satellite', 'radar',
            'artificial intelligence', 'machine learning', 'deep learning',
            'semiconductor', 'microchip', 'nanotechnology', 'graphene',
            'biotechnology', 'synthetic biology', 'genome', 'pathogen',
            'nuclear', 'fusion', 'laser', 'hypersonic', 'missile',
            'drone', 'autonomous', 'robotics', 'surveillance'
        ]

        found_keywords = []

        # Check title and abstract
        text = (work.get('title', '') + ' ' +
                ' '.join([c.get('display_name', '') for c in work.get('concepts', [])])).lower()

        for keyword in dual_use_keywords:
            if keyword in text:
                found_keywords.append(keyword)

        return found_keywords

    def process_backup_data(self):
        """Process OpenAlex backup data if available"""
        if not self.backup_path.exists():
            logger.warning(f"Backup path not found: {self.backup_path}")
            return None

        logger.info(f"Processing OpenAlex backup data from {self.backup_path}")

        # Look for institutions data
        inst_files = list(self.backup_path.glob("institutions*.json*"))
        inst_files.extend(list(self.backup_path.glob("*.gz")))

        all_italian_institutions = []

        for file_path in inst_files:
            logger.info(f"Processing {file_path.name}...")
            institutions = self.process_institutions_file(file_path)
            all_italian_institutions.extend(institutions)
            logger.info(f"  Found {len(institutions)} Italian institutions")

        # Sort by works count
        all_italian_institutions.sort(key=lambda x: x.get('works_count', 0), reverse=True)

        self.results['italian_institutions'] = all_italian_institutions
        self.results['statistics']['total_institutions'] = len(all_italian_institutions)
        self.results['statistics']['total_works'] = sum(i.get('works_count', 0)
                                                       for i in all_italian_institutions)

        return all_italian_institutions

    def fetch_recent_collaborations(self, limit: int = 10):
        """Try to fetch recent collaboration data via API"""
        logger.info("Attempting to fetch recent collaboration data...")

        base_url = "https://api.openalex.org/works"

        # Query for Italy-China collaborations
        params = {
            'filter': 'institutions.country_code:IT,institutions.country_code:CN,from_publication_date:2023-01-01',
            'per_page': 100,
            'mailto': 'research@example.com'
        }

        try:
            response = requests.get(base_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                works = data.get('results', [])

                logger.info(f"Found {len(works)} recent Italy-China collaborations")

                for work in works:
                    dual_use = self.check_dual_use_research(work)
                    if dual_use:
                        self.results['dual_use_research'].append({
                            'title': work.get('title'),
                            'year': work.get('publication_year'),
                            'keywords': dual_use,
                            'doi': work.get('doi')
                        })

                self.results['statistics']['recent_collaborations'] = len(works)
                self.results['statistics']['dual_use_papers'] = len(self.results['dual_use_research'])

                return works

        except Exception as e:
            logger.warning(f"API fetch failed: {e}")

        return []

    def generate_report(self) -> dict:
        """Generate analysis report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': dict(self.results['statistics']),
            'top_institutions': self.results['italian_institutions'][:20],
            'dual_use_research_count': len(self.results['dual_use_research']),
            'risk_assessment': self.assess_risk(),
            'recommendations': self.generate_recommendations()
        }

        return report

    def assess_risk(self) -> dict:
        """Assess overall risk level"""
        dual_use_count = len(self.results['dual_use_research'])

        risk_level = 'LOW'
        if dual_use_count > 10:
            risk_level = 'MEDIUM'
        if dual_use_count > 50:
            risk_level = 'HIGH'

        return {
            'level': risk_level,
            'dual_use_papers': dual_use_count,
            'confidence': 0.7
        }

    def generate_recommendations(self) -> list:
        """Generate recommendations"""
        recs = []

        if len(self.results['dual_use_research']) > 20:
            recs.append("PRIORITY: Review dual-use research collaborations for export control")

        if self.results['statistics']['total_institutions'] > 50:
            recs.append("EXPAND: Deep dive into top 10 institutions with highest China collaboration")

        recs.extend([
            "MONITOR: Track new publications monthly",
            "VALIDATE: Cross-reference with patent and funding data",
            "INVESTIGATE: Author-level mobility patterns"
        ])

        return recs

def main():
    processor = OpenAlexBulkProcessor()

    logger.info("="*60)
    logger.info("OPENALEX BULK DATA PROCESSING - ITALY")
    logger.info("="*60)

    # Process backup data
    institutions = processor.process_backup_data()

    if institutions:
        logger.info(f"\nProcessed {len(institutions)} Italian institutions")
        logger.info(f"Top 5 by publication count:")
        for i, inst in enumerate(institutions[:5], 1):
            logger.info(f"  {i}. {inst['name']}: {inst.get('works_count', 0):,} works")

    # Try to fetch recent data
    recent_works = processor.fetch_recent_collaborations()

    # Generate report
    report = processor.generate_report()

    # Save results
    output_file = processor.output_path / f"openalex_italy_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    logger.info(f"\nResults saved to: {output_file}")

    # Display summary
    logger.info("\n" + "="*60)
    logger.info("ANALYSIS SUMMARY")
    logger.info("="*60)
    logger.info(f"Total Italian Institutions: {report['statistics']['total_institutions']}")
    logger.info(f"Total Works: {report['statistics'].get('total_works', 0):,}")
    logger.info(f"Dual-Use Research Papers: {report['dual_use_research_count']}")
    logger.info(f"Risk Level: {report['risk_assessment']['level']}")

    return report

if __name__ == "__main__":
    main()
