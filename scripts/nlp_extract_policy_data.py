#!/usr/bin/env python3
"""
NLP Extraction for Chinese Policy Documents
Extracts:
- Quantitative data (percentages, dollar amounts, years, targets)
- Named entities (SOEs, agencies, institutions, people)
- Timeline and milestones
- Technology domains
"""

import os
import sys
import re
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

# Technology domain keywords (based on Made in China 2025 + common tech areas)
TECHNOLOGY_DOMAINS = {
    'semiconductors': [
        'semiconductor', 'chip', 'integrated circuit', 'microchip', 'wafer',
        'ASML', 'lithography', 'EUV', 'fabrication', 'foundry', 'TSMC',
        'silicon', 'CMOS', 'transistor', 'photolithography'
    ],
    'artificial_intelligence': [
        'artificial intelligence', 'AI', 'machine learning', 'deep learning',
        'neural network', 'computer vision', 'natural language processing',
        'NLP', 'speech recognition', 'facial recognition', 'algorithm'
    ],
    'quantum_computing': [
        'quantum', 'qubit', 'quantum computing', 'quantum communication',
        'quantum cryptography', 'quantum supremacy', 'superposition', 'entanglement'
    ],
    'robotics': [
        'robot', 'robotics', 'automation', 'autonomous', 'industrial robot',
        'collaborative robot', 'cobot', 'unmanned'
    ],
    'aerospace': [
        'aerospace', 'aircraft', 'aviation', 'satellite', 'space', 'rocket',
        'UAV', 'drone', 'C919', 'COMAC'
    ],
    'biotechnology': [
        'biotech', 'biotechnology', 'pharmaceutical', 'genomics', 'gene editing',
        'CRISPR', 'biopharmaceutical', 'vaccine', 'antibody', 'clinical trial'
    ],
    'new_energy_vehicles': [
        'electric vehicle', 'EV', 'battery', 'lithium', 'BYD', 'NIO',
        'autonomous driving', 'self-driving', 'CATL', 'new energy vehicle'
    ],
    'telecommunications': [
        '5G', '6G', 'telecommunications', 'Huawei', 'ZTE', 'base station',
        'network equipment', 'telecom', 'wireless'
    ],
    'advanced_materials': [
        'advanced material', 'nanomaterial', 'composite', 'rare earth',
        'graphene', 'superconductor', 'metamaterial'
    ],
    'big_data': [
        'big data', 'data analytics', 'cloud computing', 'data center',
        'data processing', 'data mining'
    ]
}

# Chinese entities to watch for (SOEs, agencies)
CHINESE_ENTITIES = [
    # State Councils and Ministries
    'State Council', 'NDRC', 'MIIT', 'Ministry of Industry and Information Technology',
    'Ministry of Science and Technology', 'MOST', 'Ministry of Education',
    'Ministry of Commerce', 'MOFCOM', 'Ministry of Finance', 'MOF',
    'National Development and Reform Commission',

    # Major SOEs
    'SMIC', 'Semiconductor Manufacturing International Corporation',
    'Huawei', 'ZTE', 'China Telecom', 'China Mobile', 'China Unicom',
    'COMAC', 'Commercial Aircraft Corporation of China',
    'AVIC', 'Aviation Industry Corporation of China',
    'CSSC', 'China State Shipbuilding Corporation',
    'CRRC', 'China Railway Rolling Stock Corporation',
    'State Grid', 'China National Nuclear Corporation',

    # Research Institutions
    'Chinese Academy of Sciences', 'CAS',
    'Chinese Academy of Engineering', 'CAE',
    'Tsinghua University', 'Peking University', 'Fudan University',

    # Talent Programs
    'Thousand Talents', 'Youth Thousand Talents',
    'Changjiang Scholars', 'National Special Support Program',

    # Other Key Terms
    'National Intelligence Law', 'Military-Civil Fusion',
    'National Integrated Circuit', 'Big Fund'
]

class PolicyNLPExtractor:
    """Extract structured data from policy documents using NLP"""

    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.stats = {
            'documents_processed': 0,
            'provisions_extracted': 0,
            'entities_extracted': 0,
            'timelines_extracted': 0,
            'tech_domains_extracted': 0
        }

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def extract_quantitative_data(self, text, document_id):
        """Extract percentages, dollar amounts, years, and quantitative targets"""
        provisions = []

        # Pattern 1: Percentage targets (e.g., "40%", "70%", "self-sufficiency rate of 40%")
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*(?:%|percent)\s*(?:by\s*)?(\d{4})?'
        for match in re.finditer(percentage_pattern, text, re.IGNORECASE):
            value = float(match.group(1))
            year = int(match.group(2)) if match.group(2) else None

            # Get context (50 chars before and after)
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end].replace('\n', ' ').strip()

            provisions.append({
                'document_id': document_id,
                'provision_type': 'percentage_target',
                'quantitative_value': value,
                'quantitative_unit': 'percent',
                'target_year': year,
                'context': context
            })

        # Pattern 2: Dollar amounts (e.g., "$100 billion", "100 billion yuan", "RMB 1 trillion")
        money_pattern = r'(?:USD|RMB|\$|¥)\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(billion|million|trillion)?'
        for match in re.finditer(money_pattern, text, re.IGNORECASE):
            value_str = match.group(1).replace(',', '')
            value = float(value_str)
            multiplier = match.group(2).lower() if match.group(2) else None

            if multiplier == 'billion':
                value *= 1e9
            elif multiplier == 'million':
                value *= 1e6
            elif multiplier == 'trillion':
                value *= 1e12

            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end].replace('\n', ' ').strip()

            provisions.append({
                'document_id': document_id,
                'provision_type': 'financial_target',
                'quantitative_value': value,
                'quantitative_unit': 'USD' if '$' in match.group(0) or 'USD' in match.group(0) else 'CNY',
                'context': context
            })

        # Pattern 3: Years as targets (e.g., "by 2025", "by 2030", "2020 target")
        year_target_pattern = r'(?:by|in|year|target)\s*(\d{4})'
        for match in re.finditer(year_target_pattern, text, re.IGNORECASE):
            year = int(match.group(1))

            # Only include realistic future years (2015-2050)
            if 2015 <= year <= 2050:
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end].replace('\n', ' ').strip()

                provisions.append({
                    'document_id': document_id,
                    'provision_type': 'year_target',
                    'target_year': year,
                    'context': context
                })

        return provisions

    def extract_entities(self, text, document_id):
        """Extract mentions of Chinese entities (SOEs, agencies, institutions)"""
        entities = []

        # Simple pattern matching for known entities
        for entity in CHINESE_ENTITIES:
            # Case-insensitive search
            pattern = re.compile(r'\b' + re.escape(entity) + r'\b', re.IGNORECASE)

            for match in pattern.finditer(text):
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end].replace('\n', ' ').strip()

                # Determine entity type
                entity_type = 'unknown'
                if any(keyword in entity.lower() for keyword in ['ministry', 'commission', 'council', 'administration']):
                    entity_type = 'government_agency'
                elif any(keyword in entity.lower() for keyword in ['corporation', 'company', 'group', 'smic', 'huawei', 'zte']):
                    entity_type = 'state_owned_enterprise'
                elif any(keyword in entity.lower() for keyword in ['university', 'academy', 'institute']):
                    entity_type = 'research_institution'
                elif 'talent' in entity.lower() or 'scholar' in entity.lower():
                    entity_type = 'talent_program'

                entities.append({
                    'document_id': document_id,
                    'entity_name': entity,
                    'entity_type': entity_type,
                    'role_description': context
                })

        # Deduplicate entities (keep first occurrence)
        seen = set()
        unique_entities = []
        for entity in entities:
            key = (entity['entity_name'].lower(), entity['document_id'])
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)

        return unique_entities

    def extract_timeline(self, text, document_id):
        """Extract timeline milestones (specific dates and goals)"""
        milestones = []

        # Pattern: "by 2025", "by 2030", with associated goals
        milestone_pattern = r'(?:by|in|year)\s*(\d{4})[,:\s]+([^.!?]{10,200})'

        for match in re.finditer(milestone_pattern, text, re.IGNORECASE):
            year = int(match.group(1))
            description = match.group(2).strip()

            if 2015 <= year <= 2050 and len(description) > 10:
                # Determine milestone type
                milestone_type = 'general'
                if any(keyword in description.lower() for keyword in ['self-sufficiency', 'domestic', 'indigenous']):
                    milestone_type = 'self_sufficiency_target'
                elif any(keyword in description.lower() for keyword in ['world leader', 'global leader', 'dominance']):
                    milestone_type = 'global_leadership_goal'
                elif any(keyword in description.lower() for keyword in ['r&d', 'research', 'innovation']):
                    milestone_type = 'rd_investment_target'

                milestones.append({
                    'document_id': document_id,
                    'milestone_year': year,
                    'milestone_description': description[:500],  # Truncate long descriptions
                    'milestone_type': milestone_type
                })

        return milestones

    def extract_technology_domains(self, text, document_id):
        """Extract mentions of technology domains and priority areas"""
        tech_mentions = []

        for domain, keywords in TECHNOLOGY_DOMAINS.items():
            for keyword in keywords:
                pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)

                matches = list(pattern.finditer(text))
                if matches:
                    # Get context for first mention
                    first_match = matches[0]
                    start = max(0, first_match.start() - 150)
                    end = min(len(text), first_match.end() + 150)
                    context = text[start:end].replace('\n', ' ').strip()

                    # Determine priority level from context
                    priority_level = 'mentioned'
                    if any(word in context.lower() for word in ['priority', 'key', 'critical', 'strategic', 'core']):
                        priority_level = 'high_priority'
                    elif any(word in context.lower() for word in ['important', 'significant', 'major']):
                        priority_level = 'medium_priority'

                    tech_mentions.append({
                        'document_id': document_id,
                        'technology_domain': domain,
                        'priority_level': priority_level,
                        'context': context,
                        'mention_count': len(matches)
                    })
                    break  # Only record once per domain per document

        return tech_mentions

    def insert_provisions(self, provisions):
        """Insert provisions into database"""
        cursor = self.conn.cursor()

        for prov in provisions:
            try:
                cursor.execute("""
                INSERT INTO policy_provisions (
                    document_id, provision_type, provision_text,
                    quantitative_value, quantitative_unit, target_year,
                    technology_domain
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    prov['document_id'],
                    prov['provision_type'],
                    prov.get('context', ''),
                    prov.get('quantitative_value'),
                    prov.get('quantitative_unit'),
                    prov.get('target_year'),
                    prov.get('technology_domain')
                ))
                self.stats['provisions_extracted'] += 1
            except Exception as e:
                print(f"[WARNING] Failed to insert provision: {e}")

        self.conn.commit()

    def insert_entities(self, entities):
        """Insert entity references into database"""
        cursor = self.conn.cursor()

        for entity in entities:
            try:
                cursor.execute("""
                INSERT INTO policy_entity_references (
                    document_id, entity_name, entity_type, role_description
                ) VALUES (?, ?, ?, ?)
                """, (
                    entity['document_id'],
                    entity['entity_name'],
                    entity['entity_type'],
                    entity['role_description']
                ))
                self.stats['entities_extracted'] += 1
            except Exception as e:
                print(f"[WARNING] Failed to insert entity: {e}")

        self.conn.commit()

    def insert_timeline(self, milestones):
        """Insert timeline milestones into database"""
        cursor = self.conn.cursor()

        for milestone in milestones:
            try:
                cursor.execute("""
                INSERT INTO policy_timeline (
                    document_id, milestone_year, milestone_description, milestone_type
                ) VALUES (?, ?, ?, ?)
                """, (
                    milestone['document_id'],
                    milestone['milestone_year'],
                    milestone['milestone_description'],
                    milestone['milestone_type']
                ))
                self.stats['timelines_extracted'] += 1
            except Exception as e:
                print(f"[WARNING] Failed to insert timeline: {e}")

        self.conn.commit()

    def insert_tech_domains(self, tech_mentions):
        """Insert technology domain mentions into database"""
        cursor = self.conn.cursor()

        for tech in tech_mentions:
            try:
                cursor.execute("""
                INSERT INTO policy_technology_domains (
                    document_id, technology_domain, priority_level, context
                ) VALUES (?, ?, ?, ?)
                """, (
                    tech['document_id'],
                    tech['technology_domain'],
                    tech['priority_level'],
                    tech['context']
                ))
                self.stats['tech_domains_extracted'] += 1
            except Exception as e:
                print(f"[WARNING] Failed to insert tech domain: {e}")

        self.conn.commit()

    def process_all_documents(self):
        """Process all documents in database"""
        cursor = self.conn.cursor()

        # Get all documents
        docs = cursor.execute("""
        SELECT document_id, title, full_text, priority_level
        FROM chinese_policy_documents
        ORDER BY priority_level, title
        """).fetchall()

        print(f"\nProcessing {len(docs)} documents...")
        print("="*80)

        for doc in docs:
            doc_id = doc['document_id']
            title = doc['title']
            text = doc['full_text']
            priority = doc['priority_level']

            if not text:
                print(f"\n[SKIP] {title} - No text available")
                continue

            print(f"\n[PROCESSING] {title[:60]}")
            print(f"  Priority: {priority}")
            print(f"  Text length: {len(text):,} chars")

            # Extract all components
            provisions = self.extract_quantitative_data(text, doc_id)
            entities = self.extract_entities(text, doc_id)
            timeline = self.extract_timeline(text, doc_id)
            tech_domains = self.extract_technology_domains(text, doc_id)

            print(f"  Extracted: {len(provisions)} provisions, {len(entities)} entities, " +
                  f"{len(timeline)} milestones, {len(tech_domains)} tech domains")

            # Insert into database
            if provisions:
                self.insert_provisions(provisions)
            if entities:
                self.insert_entities(entities)
            if timeline:
                self.insert_timeline(timeline)
            if tech_domains:
                self.insert_tech_domains(tech_domains)

            self.stats['documents_processed'] += 1

        print("\n" + "="*80)
        print("EXTRACTION COMPLETE")
        print("="*80)
        print(f"Documents processed: {self.stats['documents_processed']}")
        print(f"Provisions extracted: {self.stats['provisions_extracted']}")
        print(f"Entities extracted: {self.stats['entities_extracted']}")
        print(f"Timeline milestones: {self.stats['timelines_extracted']}")
        print(f"Tech domains mapped: {self.stats['tech_domains_extracted']}")
        print("="*80)


def main():
    """Main execution"""
    print("="*80)
    print("POLICY DOCUMENTS - NLP EXTRACTION")
    print("="*80)

    extractor = PolicyNLPExtractor(DB_PATH)
    extractor.connect()

    # Process all documents
    extractor.process_all_documents()

    extractor.conn.close()

    # Save statistics
    stats_file = Path("C:/Projects/OSINT-Foresight/analysis/policy_extraction") / f"nlp_extraction_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(extractor.stats, f, indent=2)

    print(f"\nStatistics saved to: {stats_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
