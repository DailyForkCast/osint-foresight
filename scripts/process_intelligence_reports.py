#!/usr/bin/env python3
"""
Intelligence Report Processing Pipeline
Extracts entities, risk indicators, and technologies from PDF reports
"""

import sqlite3
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import json

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("WARNING: PyMuPDF not installed. Install with: pip install PyMuPDF")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IntelligenceReportProcessor:
    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.reports_dir = Path("F:/Reports")

        # Entity patterns (companies, institutions, universities)
        self.entity_patterns = {
            'company': [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Technologies|Technology|Corporation|Corp|Company|Co|Ltd|Limited|Inc|Industries|Systems|Group)\.?)\b',
                r'\b(Huawei|ZTE|SMIC|Hikvision|Dahua|iFlytek|SenseTime|Megvii|DJI|BGI|Tencent|Alibaba|Baidu|ByteDance)\b',
            ],
            'university': [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:University|Institute|Academy|College)(?:\s+of\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)?)\b',
                r'\b(Tsinghua|Peking|Harbin|Beijing\s+Institute|Northwestern\s+Polytechnical)\b',
            ],
            'institution': [
                r'\b(Chinese\s+Academy\s+of\s+Sciences|CAS|Ministry\s+of\s+\w+|People\'s\s+Liberation\s+Army|PLA)\b',
            ]
        }

        # Risk indicator keywords
        self.risk_indicators = {
            'military_civil_fusion': [
                'military-civil fusion', 'MCF', 'civil-military integration',
                'dual-use', 'PLA', 'People\'s Liberation Army', 'defense industry'
            ],
            'technology_transfer': [
                'technology transfer', 'IP theft', 'intellectual property',
                'espionage', 'cyber espionage', 'industrial espionage',
                'forced technology transfer', 'joint ventures'
            ],
            'surveillance': [
                'surveillance', 'facial recognition', 'mass surveillance',
                'social credit', 'Uyghur', 'Xinjiang', 'human rights violations',
                'surveillance state'
            ],
            'supply_chain': [
                'supply chain', 'critical infrastructure', 'dependency',
                'single point of failure', 'strategic vulnerability',
                'rare earth', 'chokepoint'
            ],
            'strategic_competition': [
                'Made in China 2025', 'Belt and Road', 'BRI',
                'strategic competition', 'great power competition',
                'technological supremacy', 'military modernization'
            ]
        }

        # Technology categories
        self.technology_keywords = {
            'AI': ['artificial intelligence', 'AI', 'machine learning', 'deep learning',
                   'neural network', 'computer vision', 'natural language processing'],
            'Quantum': ['quantum computing', 'quantum communication', 'quantum sensing',
                       'quantum cryptography', 'quantum supremacy'],
            'Semiconductor': ['semiconductor', 'chip', 'microchip', 'fabrication',
                            'lithography', 'EUV', 'foundry', 'wafer'],
            'Aerospace': ['aerospace', 'hypersonic', 'missile', 'satellite',
                         'space', 'launch vehicle', 'rocket'],
            'Biotechnology': ['biotechnology', 'biotech', 'genomics', 'gene editing',
                            'CRISPR', 'synthetic biology', 'bioinformatics'],
            'Telecommunications': ['5G', '6G', 'telecommunications', 'network',
                                  'base station', 'spectrum'],
            'Autonomous': ['autonomous', 'UAV', 'drone', 'unmanned', 'robotics',
                          'autonomous vehicle'],
            'Cybersecurity': ['cybersecurity', 'cyber attack', 'hacking', 'malware',
                            'encryption', 'zero-day'],
            'Advanced_Materials': ['advanced materials', 'nanomaterials', 'composites',
                                  'metamaterials', 'graphene'],
            'Energy': ['nuclear', 'fusion', 'battery', 'solar', 'renewable energy',
                      'energy storage']
        }

    def extract_text_from_pdf(self, pdf_path: Path) -> Tuple[str, int]:
        """Extract text from PDF using PyMuPDF"""
        if not HAS_PYMUPDF:
            logger.error("PyMuPDF not installed")
            return "", 0

        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            page_count = len(doc)
            doc.close()
            return text, page_count
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path.name}: {e}")
            return "", 0

    def _map_entity_type(self, extracted_type: str) -> str:
        """Map extracted entity type to database schema-compliant type"""
        type_mapping = {
            'company': 'company',
            'university': 'organization',
            'institution': 'organization'
        }
        return type_mapping.get(extracted_type, 'organization')

    def extract_entities(self, text: str, report_id: int) -> List[Dict]:
        """Extract entities using regex patterns (OPTIMIZED for large texts)"""
        # OPTIMIZATION: Limit text processing to first 100K chars for speed
        text_sample = text[:100000] if len(text) > 100000 else text

        entities = []
        seen = set()  # Avoid duplicates

        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_sample, re.IGNORECASE)
                for match in matches:
                    entity_name = match.group(0).strip()

                    # Normalize
                    entity_name_normalized = ' '.join(entity_name.split())

                    # Skip if already seen or too short
                    if entity_name_normalized in seen or len(entity_name_normalized) < 5:
                        continue

                    seen.add(entity_name_normalized)

                    # OPTIMIZATION: Approximate mention count (don't scan entire text)
                    # Just count in sample and extrapolate if needed
                    mentions_in_sample = text_sample.lower().count(entity_name_normalized.lower())
                    if len(text) > 100000:
                        mention_count = int(mentions_in_sample * (len(text) / 100000))
                    else:
                        mention_count = mentions_in_sample

                    # Extract context (50 chars before/after first mention)
                    context_match = re.search(rf'.{{0,50}}{re.escape(entity_name_normalized)}.{{0,50}}', text_sample, re.IGNORECASE)
                    context = context_match.group(0) if context_match else ""

                    # Assess risk level (use sample text only)
                    risk_level = self._assess_entity_risk(entity_name_normalized, text_sample)

                    # Map entity type to database-compliant value
                    db_entity_type = self._map_entity_type(entity_type)

                    entities.append({
                        'report_id': report_id,
                        'entity_type': db_entity_type,
                        'entity_name': entity_name_normalized,
                        'mention_count': mention_count,
                        'context_snippets': context[:200],  # First 200 chars
                        'risk_level': risk_level,
                        'confidence': 0.7 if mention_count >= 3 else 0.5
                    })

        # Sort by mention count
        entities.sort(key=lambda x: x['mention_count'], reverse=True)

        return entities[:100]  # Top 100 entities per report

    def _assess_entity_risk(self, entity_name: str, text: str) -> str:
        """Assess risk level based on context around entity mentions"""
        # Find sentences containing the entity
        sentences = re.findall(rf'[^.!?]*{re.escape(entity_name)}[^.!?]*[.!?]', text, re.IGNORECASE)

        risk_keywords = {
            'CRITICAL': ['sanctions', 'banned', 'prohibited', 'entity list', 'military', 'espionage', 'threat'],
            'HIGH': ['concern', 'surveillance', 'dual-use', 'strategic', 'risk'],
            'MEDIUM': ['cooperation', 'partnership', 'collaboration', 'research'],
        }

        for risk_level, keywords in risk_keywords.items():
            for sentence in sentences:
                if any(kw in sentence.lower() for kw in keywords):
                    return risk_level

        return 'LOW'

    def _map_risk_category(self, extracted_category: str) -> str:
        """Map extracted risk category to database schema-compliant category"""
        category_mapping = {
            'military_civil_fusion': 'military',
            'technology_transfer': 'technology_transfer',
            'surveillance': 'influence',
            'supply_chain': 'supply_chain',
            'strategic_competition': 'influence'
        }
        return category_mapping.get(extracted_category, 'influence')

    def extract_risk_indicators(self, text: str, report_id: int) -> List[Dict]:
        """Extract risk indicators from text (OPTIMIZED)"""
        # OPTIMIZATION: Use first 100K chars for sampling
        text_sample = text[:100000] if len(text) > 100000 else text

        risks = []

        for risk_category, keywords in self.risk_indicators.items():
            matches = []
            for keyword in keywords:
                # Simple count-based approach instead of regex matching
                if keyword.lower() in text_sample.lower():
                    # Find one example sentence
                    idx = text_sample.lower().find(keyword.lower())
                    if idx != -1:
                        # Extract sentence around keyword
                        start = max(0, idx - 100)
                        end = min(len(text_sample), idx + 100)
                        snippet = text_sample[start:end]
                        matches.append(snippet)

            if matches:
                # Combine all matches for this category
                risk_description = ' ... '.join(matches[:3])[:500]  # First 3 sentences, max 500 chars

                # Assess severity based on frequency and keywords
                severity = self._assess_severity(matches, risk_category)

                # Map risk category to database-compliant value
                db_risk_category = self._map_risk_category(risk_category)

                # Map to database-compliant likelihood values
                if len(matches) > 10:
                    likelihood = 'LIKELY'
                elif len(matches) > 5:
                    likelihood = 'POSSIBLE'
                else:
                    likelihood = 'UNLIKELY'

                # Map to database-compliant evidence_quality values
                if len(matches) >= 5:
                    evidence_quality = 'STRONG'
                elif len(matches) >= 3:
                    evidence_quality = 'MODERATE'
                else:
                    evidence_quality = 'WEAK'

                risks.append({
                    'report_id': report_id,
                    'risk_category': db_risk_category,
                    'risk_description': risk_description,
                    'severity': severity,
                    'likelihood': likelihood,
                    'evidence_quality': evidence_quality
                })

        return risks

    def _assess_severity(self, matches: List[str], category: str) -> str:
        """Assess severity based on match count and category"""
        count = len(matches)

        critical_categories = ['military_civil_fusion', 'technology_transfer', 'surveillance']

        if category in critical_categories:
            if count >= 10:
                return 'CRITICAL'
            elif count >= 5:
                return 'HIGH'
            else:
                return 'MEDIUM'
        else:
            if count >= 15:
                return 'HIGH'
            elif count >= 8:
                return 'MEDIUM'
            else:
                return 'LOW'

    def extract_technologies(self, text: str, report_id: int) -> List[Dict]:
        """Extract technology mentions from text (OPTIMIZED)"""
        # OPTIMIZATION: Use first 100K chars for sampling
        text_sample = text[:100000] if len(text) > 100000 else text

        technologies = []

        for tech_category, keywords in self.technology_keywords.items():
            matches = []
            for keyword in keywords:
                # Simple substring search instead of regex
                if keyword.lower() in text_sample.lower():
                    matches.append(keyword)

            if matches:
                # Simplified context extraction
                context = self._extract_tech_context(text_sample, tech_category, keywords)

                # Assess dual-use nature
                dual_use = self._is_dual_use(tech_category, text_sample)

                technologies.append({
                    'report_id': report_id,
                    'technology_category': tech_category,
                    'specific_technology': ', '.join(matches[:5]),
                    'dual_use_flag': dual_use,
                    'military_application': context.get('military', ''),
                    'civilian_application': context.get('civilian', ''),
                    'china_capability_assessment': self._assess_china_capability(text_sample, tech_category)
                })

        return technologies

    def _extract_tech_context(self, text: str, tech_category: str, keywords: List[str]) -> Dict:
        """Extract military and civilian application context"""
        context = {'military': '', 'civilian': ''}

        for keyword in keywords:
            # Find sentences with military keywords
            mil_pattern = rf'[^.!?]*{re.escape(keyword)}[^.!?]*(?:military|defense|weapon|warfare|PLA)[^.!?]*[.!?]'
            mil_matches = re.findall(mil_pattern, text, re.IGNORECASE)
            if mil_matches:
                context['military'] = mil_matches[0][:200]

            # Find sentences with civilian keywords
            civ_pattern = rf'[^.!?]*{re.escape(keyword)}[^.!?]*(?:civilian|commercial|consumer|market)[^.!?]*[.!?]'
            civ_matches = re.findall(civ_pattern, text, re.IGNORECASE)
            if civ_matches:
                context['civilian'] = civ_matches[0][:200]

        return context

    def _is_dual_use(self, tech_category: str, text: str) -> bool:
        """Determine if technology is dual-use"""
        dual_use_categories = ['AI', 'Quantum', 'Aerospace', 'Biotechnology',
                               'Autonomous', 'Cybersecurity', 'Advanced_Materials']

        if tech_category in dual_use_categories:
            return True

        # Check for explicit dual-use mentions
        dual_use_keywords = ['dual-use', 'dual use', 'military-civil', 'civil-military']
        return any(kw in text.lower() for kw in dual_use_keywords)

    def _assess_china_capability(self, text: str, tech_category: str) -> str:
        """Assess China's capability in this technology area"""
        # Look for assessment keywords
        leader_keywords = ['leader', 'leading', 'dominance', 'dominant', 'ahead', 'superior']
        competitive_keywords = ['competitive', 'parity', 'catching up', 'advancing']
        lagging_keywords = ['lag', 'behind', 'dependent', 'reliant', 'weakness']

        tech_text = re.findall(rf'[^.!?]*(?:China|Chinese|PRC)[^.!?]*{tech_category}[^.!?]*[.!?]', text, re.IGNORECASE)
        tech_context = ' '.join(tech_text).lower()

        if any(kw in tech_context for kw in leader_keywords):
            return 'LEADING'
        elif any(kw in tech_context for kw in competitive_keywords):
            return 'COMPETITIVE'
        elif any(kw in tech_context for kw in lagging_keywords):
            return 'LAGGING'
        else:
            return 'UNKNOWN'

    def create_report_record(self, pdf_path: Path, page_count: int) -> int:
        """Create report record in database and return report_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create reports table if doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                title TEXT,
                source TEXT,
                publication_date TEXT,
                page_count INTEGER,
                processed_date DATETIME,
                file_path TEXT
            )
        """)

        # Infer metadata from filename
        filename = pdf_path.name
        source = 'UNKNOWN'
        if 'CSET' in filename or 'MILITARY-AND-SECURITY' in filename:
            source = 'CSET'
        elif 'ASPI' in filename:
            source = 'ASPI'
        elif 'DOD' in filename or 'MILITARY' in filename:
            source = 'DOD'
        elif any(x in filename for x in ['Allen', 'Swope', 'Shivakumar', 'Hader']):
            source = 'CSIS'

        # Extract year from filename if possible
        year_match = re.search(r'(20\d{2})', filename)
        pub_date = year_match.group(1) if year_match else None

        cursor.execute("""
            INSERT INTO reports (filename, title, source, publication_date, page_count, processed_date, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (filename, filename.replace('.pdf', '').replace('_', ' '), source, pub_date,
              page_count, datetime.now().isoformat(), str(pdf_path)))

        report_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return report_id

    def populate_database(self, report_id: int, entities: List[Dict], risks: List[Dict], technologies: List[Dict]):
        """Populate report analysis tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Insert entities
        for entity in entities:
            cursor.execute("""
                INSERT INTO report_entities (
                    report_id, entity_type, entity_name, mention_count,
                    context_snippets, risk_level, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (entity['report_id'], entity['entity_type'], entity['entity_name'],
                  entity['mention_count'], entity['context_snippets'],
                  entity['risk_level'], entity['confidence']))

        # Insert risk indicators
        for risk in risks:
            cursor.execute("""
                INSERT INTO report_risk_indicators (
                    report_id, risk_category, risk_description, severity,
                    likelihood, evidence_quality
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (risk['report_id'], risk['risk_category'], risk['risk_description'],
                  risk['severity'], risk['likelihood'], risk['evidence_quality']))

        # Insert technologies
        for tech in technologies:
            cursor.execute("""
                INSERT INTO report_technologies (
                    report_id, technology_category, specific_technology,
                    dual_use_flag, military_application, civilian_application,
                    china_capability_assessment
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tech['report_id'], tech['technology_category'], tech['specific_technology'],
                  tech['dual_use_flag'], tech['military_application'],
                  tech['civilian_application'], tech['china_capability_assessment']))

        conn.commit()
        conn.close()

    def process_all_reports(self):
        """Process all PDF reports in F:/Reports"""
        logger.info("Starting intelligence report processing...")

        if not HAS_PYMUPDF:
            logger.error("Cannot proceed without PyMuPDF. Install with: pip install PyMuPDF")
            return

        pdf_files = list(self.reports_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF reports")

        processed = 0
        failed = 0

        for pdf_path in pdf_files:
            try:
                logger.info(f"Processing: {pdf_path.name}")

                # Extract text
                text, page_count = self.extract_text_from_pdf(pdf_path)
                if not text:
                    logger.warning(f"No text extracted from {pdf_path.name}")
                    failed += 1
                    continue

                logger.info(f"  Extracted {len(text):,} characters from {page_count} pages")

                # Create report record
                report_id = self.create_report_record(pdf_path, page_count)

                # Extract entities
                entities = self.extract_entities(text, report_id)
                logger.info(f"  Found {len(entities)} entities")

                # Extract risk indicators
                risks = self.extract_risk_indicators(text, report_id)
                logger.info(f"  Found {len(risks)} risk indicators")

                # Extract technologies
                technologies = self.extract_technologies(text, report_id)
                logger.info(f"  Found {len(technologies)} technologies")

                # Populate database
                self.populate_database(report_id, entities, risks, technologies)

                processed += 1
                logger.info(f"  ✓ Successfully processed {pdf_path.name}")

            except Exception as e:
                logger.error(f"  ✗ Failed to process {pdf_path.name}: {e}")
                failed += 1

        logger.info(f"\n{'='*80}")
        logger.info(f"Processing complete!")
        logger.info(f"  Processed: {processed}/{len(pdf_files)}")
        logger.info(f"  Failed: {failed}/{len(pdf_files)}")
        logger.info(f"{'='*80}")

        return processed, failed

    def generate_summary_report(self):
        """Generate summary of processed reports"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        # Get statistics
        report_count = conn.execute('SELECT COUNT(*) FROM reports').fetchone()[0]
        entity_count = conn.execute('SELECT COUNT(*) FROM report_entities').fetchone()[0]
        risk_count = conn.execute('SELECT COUNT(*) FROM report_risk_indicators').fetchone()[0]
        tech_count = conn.execute('SELECT COUNT(*) FROM report_technologies').fetchone()[0]

        # Top entities
        top_entities = conn.execute('''
            SELECT entity_name, SUM(mention_count) as total_mentions, COUNT(*) as report_count
            FROM report_entities
            GROUP BY entity_name
            ORDER BY total_mentions DESC
            LIMIT 20
        ''').fetchall()

        # Risk categories
        risk_categories = conn.execute('''
            SELECT risk_category, COUNT(*) as count,
                   SUM(CASE WHEN severity='CRITICAL' THEN 1 ELSE 0 END) as critical_count
            FROM report_risk_indicators
            GROUP BY risk_category
            ORDER BY count DESC
        ''').fetchall()

        # Technology categories
        tech_categories = conn.execute('''
            SELECT technology_category, COUNT(*) as count,
                   SUM(CASE WHEN dual_use_flag=1 THEN 1 ELSE 0 END) as dual_use_count,
                   china_capability_assessment
            FROM report_technologies
            GROUP BY technology_category, china_capability_assessment
            ORDER BY count DESC
        ''').fetchall()

        conn.close()

        # Generate markdown report
        report = f"""# Intelligence Report Processing Summary
**Generated:** {datetime.now().isoformat()}

## Overview

- **Reports Processed:** {report_count}
- **Entities Extracted:** {entity_count:,}
- **Risk Indicators Identified:** {risk_count:,}
- **Technologies Catalogued:** {tech_count:,}

## Top 20 Entities by Mentions

| Entity | Total Mentions | Reports |
|--------|----------------|---------|
"""
        for entity in top_entities:
            report += f"| {entity['entity_name']} | {entity['total_mentions']} | {entity['report_count']} |\n"

        report += f"""
## Risk Indicators by Category

| Category | Total | Critical |
|----------|-------|----------|
"""
        for risk in risk_categories:
            report += f"| {risk['risk_category']} | {risk['count']} | {risk['critical_count']} |\n"

        report += f"""
## Technology Categories

| Technology | Mentions | Dual-Use | China Capability |
|------------|----------|----------|------------------|
"""
        for tech in tech_categories:
            report += f"| {tech['technology_category']} | {tech['count']} | {tech['dual_use_count']} | {tech['china_capability_assessment']} |\n"

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/INTELLIGENCE_REPORTS_SUMMARY.md")
        report_path.write_text(report, encoding='utf-8')

        logger.info(f"\nSummary report saved to: {report_path}")

        return report


if __name__ == "__main__":
    processor = IntelligenceReportProcessor()

    # Process all reports
    processed, failed = processor.process_all_reports()

    # Generate summary
    if processed > 0:
        processor.generate_summary_report()
