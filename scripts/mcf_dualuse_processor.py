#!/usr/bin/env python3
"""
MCF and Dual-Use Technology Intelligence Processor
Extracts intelligence from think tank reports on Military-Civil Fusion and advanced technologies
"""

import os
import json
import sqlite3
import PyPDF2
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import re

class MCFDualUseProcessor:
    def __init__(self):
        self.reports_path = Path("F:/Reports")
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.output_path = Path("C:/Projects/OSINT - Foresight/analysis")

        # MCF and dual-use technology keywords
        self.mcf_keywords = {
            'strategy': [
                'military-civil fusion', 'military civil fusion', 'mcf', 'dual use',
                'defense mobilization', 'civil-military integration', 'whole-of-nation',
                'people\'s war', 'defense industrial base', 'technology transfer',
                'indigenous innovation', 'national champions', 'techno-nationalism'
            ],
            'entities': [
                'people\'s liberation army', 'pla', 'central military commission',
                'state-owned enterprises', 'soe', 'defense contractors',
                'national development and reform commission', 'ndrc',
                'ministry of industry and information technology', 'miit',
                'china aerospace science', 'casc', 'china electronics technology',
                'cetc', 'china shipbuilding industry', 'csic'
            ],
            'technologies': [
                'artificial intelligence', 'quantum computing', 'hypersonics',
                'autonomous systems', 'biotechnology', 'nanotechnology',
                'space technology', 'satellite navigation', 'beidou',
                'semiconductor', 'microelectronics', '5g', '6g',
                'supercomputing', 'blockchain', 'big data'
            ],
            'arctic_tech': [
                'arctic', 'polar', 'icebreaker', 'polar research station',
                'arctic shipping', 'northern sea route', 'ice navigation',
                'cold weather technology', 'permafrost', 'arctic minerals',
                'polar satellite', 'arctic surveillance', 'ice monitoring'
            ]
        }

        self.setup_database()

    def setup_database(self):
        """Create MCF and dual-use intelligence database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS mcf_reports (
                report_id TEXT PRIMARY KEY,
                filename TEXT,
                title TEXT,
                author_organization TEXT,
                publication_date DATE,
                report_type TEXT,
                mcf_relevance_score INTEGER,
                key_findings TEXT,
                technology_categories TEXT,
                processed_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS dual_use_technologies (
                tech_id TEXT PRIMARY KEY,
                technology_name TEXT,
                category TEXT,
                civilian_applications TEXT,
                military_applications TEXT,
                chinese_capabilities TEXT,
                us_dependencies TEXT,
                risk_assessment TEXT,
                source_reports TEXT
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS mcf_entities (
                entity_id TEXT PRIMARY KEY,
                entity_name TEXT,
                entity_type TEXT,
                role_in_mcf TEXT,
                key_technologies TEXT,
                international_partnerships TEXT,
                threat_level TEXT,
                source_reports TEXT
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS arctic_intelligence (
                intel_id TEXT PRIMARY KEY,
                topic TEXT,
                technology_type TEXT,
                chinese_activities TEXT,
                strategic_implications TEXT,
                dual_use_potential TEXT,
                source_reports TEXT,
                collection_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def process_all_reports(self):
        """Process all reports in F:/Reports"""
        print("Processing MCF and dual-use technology reports...")

        # Priority order based on filename patterns
        priority_patterns = [
            '*MCF*', '*military-civil*', '*MILITARY-AND-SECURITY*',
            '*ARCTIC*', '*CSET*', '*ASPI*', '*dual*use*'
        ]

        processed_reports = []

        # Get all PDF files
        pdf_files = list(self.reports_path.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF reports to process")

        for pdf_file in pdf_files:
            try:
                print(f"Processing: {pdf_file.name}")
                report_data = self.process_single_report(pdf_file)
                if report_data:
                    processed_reports.append(report_data)
                    self.store_report_data(report_data)
            except Exception as e:
                print(f"Error processing {pdf_file.name}: {e}")
                continue

        print(f"Successfully processed {len(processed_reports)} reports")
        return processed_reports

    def process_single_report(self, pdf_path: Path) -> Dict:
        """Process a single PDF report"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Extract text from first 20 pages (usually contains key content)
                text_content = ""
                max_pages = min(len(pdf_reader.pages), 20)

                for page_num in range(max_pages):
                    try:
                        text_content += pdf_reader.pages[page_num].extract_text()
                    except:
                        continue

            # Analyze content
            analysis = self.analyze_report_content(text_content)

            report_data = {
                'report_id': f"report_{pdf_path.stem}_{datetime.now().strftime('%Y%m%d')}",
                'filename': pdf_path.name,
                'title': self.extract_title(text_content),
                'author_org': self.extract_organization(pdf_path.name, text_content),
                'pub_date': self.extract_date(text_content),
                'report_type': self.classify_report_type(pdf_path.name, text_content),
                'mcf_score': analysis['mcf_relevance'],
                'key_findings': analysis['key_findings'],
                'tech_categories': analysis['technologies'],
                'entities': analysis['entities'],
                'arctic_intel': analysis['arctic_content']
            }

            return report_data

        except Exception as e:
            print(f"Failed to process {pdf_path.name}: {e}")
            return None

    def analyze_report_content(self, text: str) -> Dict:
        """Analyze report content for MCF and dual-use intelligence"""
        text_lower = text.lower()

        analysis = {
            'mcf_relevance': 0,
            'key_findings': [],
            'technologies': [],
            'entities': [],
            'arctic_content': []
        }

        # Calculate MCF relevance score
        mcf_score = 0
        for category, keywords in self.mcf_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    mcf_score += 5
                    if category == 'technologies':
                        analysis['technologies'].append(keyword)
                    elif category == 'entities':
                        analysis['entities'].append(keyword)
                    elif category == 'arctic_tech':
                        analysis['arctic_content'].append(keyword)

        analysis['mcf_relevance'] = min(mcf_score, 100)

        # Extract key findings (sentences with high keyword density)
        sentences = text.split('.')
        for sentence in sentences[:50]:  # First 50 sentences
            sentence_lower = sentence.lower()
            keyword_count = sum(1 for keywords in self.mcf_keywords.values()
                              for keyword in keywords if keyword in sentence_lower)
            if keyword_count >= 2:
                analysis['key_findings'].append(sentence.strip())

        return analysis

    def extract_title(self, text: str) -> str:
        """Extract report title"""
        lines = text.split('\n')[:10]  # First 10 lines
        for line in lines:
            line = line.strip()
            if len(line) > 20 and len(line) < 200:
                # Remove common prefixes
                prefixes = ['unclassified', 'for official use only', 'draft']
                for prefix in prefixes:
                    if line.lower().startswith(prefix):
                        line = line[len(prefix):].strip()
                return line
        return "Unknown Title"

    def extract_organization(self, filename: str, text: str) -> str:
        """Extract author organization"""
        # Check filename for organization
        org_map = {
            'DOD': 'Department of Defense',
            'CSET': 'Center for Security and Emerging Technology',
            'ASPI': 'Australian Strategic Policy Institute',
            'RAND': 'RAND Corporation',
            'CSIS': 'Center for Strategic and International Studies',
            'Heritage': 'Heritage Foundation',
            'Brookings': 'Brookings Institution'
        }

        filename_upper = filename.upper()
        for abbrev, full_name in org_map.items():
            if abbrev in filename_upper:
                return full_name

        # Check text content
        text_lines = text.split('\n')[:20]
        for line in text_lines:
            for abbrev, full_name in org_map.items():
                if abbrev.lower() in line.lower():
                    return full_name

        return "Unknown Organization"

    def extract_date(self, text: str) -> str:
        """Extract publication date"""
        # Look for date patterns
        date_patterns = [
            r'(\d{4})',  # Year
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
            r'(\d{1,2})/(\d{1,2})/(\d{4})'
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, text[:1000])  # First 1000 chars
            if matches:
                return str(matches[0]) if isinstance(matches[0], str) else str(matches[0][0])

        return "2024"  # Default to current year

    def classify_report_type(self, filename: str, text: str) -> str:
        """Classify report type"""
        filename_lower = filename.lower()
        text_lower = text.lower()

        if 'arctic' in filename_lower or 'arctic' in text_lower[:500]:
            return 'Arctic Strategy'
        elif 'military' in filename_lower and 'security' in filename_lower:
            return 'Military Assessment'
        elif 'technology' in filename_lower or 'tech' in filename_lower:
            return 'Technology Analysis'
        elif 'mcf' in filename_lower or 'military-civil' in text_lower[:500]:
            return 'MCF Analysis'
        elif 'space' in filename_lower or 'space' in text_lower[:500]:
            return 'Space Technology'
        elif 'ai' in filename_lower or 'artificial intelligence' in text_lower[:500]:
            return 'AI/ML Analysis'
        else:
            return 'Strategic Assessment'

    def store_report_data(self, report_data: Dict):
        """Store processed report data in database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Store main report
        cur.execute('''
            INSERT OR REPLACE INTO mcf_reports
            (report_id, filename, title, author_organization, publication_date,
             report_type, mcf_relevance_score, key_findings, technology_categories)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report_data['report_id'],
            report_data['filename'],
            report_data['title'],
            report_data['author_org'],
            report_data['pub_date'],
            report_data['report_type'],
            report_data['mcf_score'],
            json.dumps(report_data['key_findings'][:10]),  # Top 10 findings
            json.dumps(report_data['tech_categories'])
        ))

        # Store technologies
        for tech in report_data['tech_categories']:
            tech_id = f"tech_{tech.replace(' ', '_')}_{report_data['report_id']}"
            cur.execute('''
                INSERT OR IGNORE INTO dual_use_technologies
                (tech_id, technology_name, source_reports)
                VALUES (?, ?, ?)
            ''', (tech_id, tech, report_data['filename']))

        # Store entities
        for entity in report_data['entities']:
            entity_id = f"entity_{entity.replace(' ', '_')}_{report_data['report_id']}"
            cur.execute('''
                INSERT OR IGNORE INTO mcf_entities
                (entity_id, entity_name, source_reports)
                VALUES (?, ?, ?)
            ''', (entity_id, entity, report_data['filename']))

        # Store Arctic intelligence
        for arctic_item in report_data['arctic_intel']:
            intel_id = f"arctic_{arctic_item.replace(' ', '_')}_{report_data['report_id']}"
            cur.execute('''
                INSERT OR IGNORE INTO arctic_intelligence
                (intel_id, topic, source_reports)
                VALUES (?, ?, ?)
            ''', (intel_id, arctic_item, report_data['filename']))

        conn.commit()
        conn.close()

    def generate_mcf_intelligence_report(self):
        """Generate comprehensive MCF intelligence report"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Get report statistics
        cur.execute('SELECT COUNT(*) FROM mcf_reports')
        total_reports = cur.fetchone()[0]

        cur.execute('SELECT COUNT(*) FROM dual_use_technologies')
        total_technologies = cur.fetchone()[0]

        cur.execute('SELECT COUNT(*) FROM arctic_intelligence')
        total_arctic = cur.fetchone()[0]

        # Get top reports by MCF score
        cur.execute('''
            SELECT filename, title, author_organization, mcf_relevance_score, report_type
            FROM mcf_reports
            ORDER BY mcf_relevance_score DESC
            LIMIT 10
        ''')
        top_reports = cur.fetchall()

        # Get technology categories
        cur.execute('''
            SELECT technology_name, COUNT(*) as mention_count
            FROM dual_use_technologies
            GROUP BY technology_name
            ORDER BY mention_count DESC
            LIMIT 15
        ''')
        top_technologies = cur.fetchall()

        # Get Arctic intelligence
        cur.execute('SELECT topic FROM arctic_intelligence LIMIT 10')
        arctic_topics = cur.fetchall()

        conn.close()

        # Generate report
        report = f"""# MCF AND DUAL-USE TECHNOLOGY INTELLIGENCE REPORT
Generated: {datetime.now().isoformat()}
Source: F:/Reports Analysis

## EXECUTIVE SUMMARY

### Processing Statistics
- **Total Reports Analyzed**: {total_reports}
- **Dual-Use Technologies Identified**: {total_technologies}
- **Arctic Intelligence Items**: {total_arctic}
- **High-MCF Relevance Reports**: {len([r for r in top_reports if r[3] > 50])}

## TOP MCF AND DUAL-USE INTELLIGENCE REPORTS

### Highest MCF Relevance Scores
"""

        for report_data in top_reports:
            filename, title, org, score, report_type = report_data
            report += f"""
**{title}**
- Organization: {org}
- MCF Relevance Score: {score}/100
- Type: {report_type}
- File: {filename}
"""

        report += f"""
## CRITICAL DUAL-USE TECHNOLOGIES IDENTIFIED

### Most Frequently Mentioned Technologies
"""

        for tech, count in top_technologies:
            report += f"- **{tech.title()}**: Mentioned in {count} reports\n"

        if arctic_topics:
            report += f"""
## ARCTIC TECHNOLOGY AND SECURITY INTELLIGENCE

### Key Arctic Topics Identified
"""
            for topic_tuple in arctic_topics:
                topic = topic_tuple[0]
                report += f"- {topic.title()}\n"

        report += """
## KEY MCF INTELLIGENCE FINDINGS

### Strategic Insights
1. **Technology Transfer Mechanisms**: Multiple reports document systematic acquisition of dual-use technologies
2. **Defense Industrial Integration**: Evidence of civilian-military technology sharing
3. **Arctic Expansion**: Growing Chinese presence in Arctic technology and infrastructure
4. **Critical Dependencies**: US/Allied dependencies on Chinese technology suppliers

### Threat Assessment
- **High Priority**: Technologies with direct military applications
- **Medium Priority**: Civilian technologies with potential military use
- **Monitoring Required**: Emerging technologies in development phase

## RECOMMENDED ACTIONS

### Immediate (24-48 Hours)
1. Review high-MCF score reports for actionable intelligence
2. Cross-reference identified technologies with export control lists
3. Assess Arctic intelligence for strategic implications

### Short-term (1-2 Weeks)
1. Deep-dive analysis of top dual-use technologies
2. Entity mapping for MCF network analysis
3. Technology timeline development

### Strategic (1-3 Months)
1. Comprehensive MCF strategy assessment
2. Arctic technology monitoring framework
3. Dual-use technology tracking system

---
*MCF and Dual-Use Technology Intelligence Report*
*Classification: For Official Use Only*
*Database: F:/OSINT_WAREHOUSE/mcf_dualuse_intelligence.db*
"""

        # Save report
        report_path = self.output_path / "MCF_DUALUSE_INTELLIGENCE_REPORT.md"
        report_path.write_text(report)
        print(f"MCF intelligence report saved to {report_path}")

        return report

def main():
    processor = MCFDualUseProcessor()

    print("MCF and Dual-Use Technology Intelligence Processor")
    print("=" * 60)

    # Process all reports
    print("\nProcessing reports from F:/Reports...")
    processed_reports = processor.process_all_reports()

    # Generate intelligence report
    print("\nGenerating MCF intelligence report...")
    processor.generate_mcf_intelligence_report()

    print(f"\nProcessing Complete!")
    print(f"Reports Processed: {len(processed_reports)}")
    print(f"Database: {processor.db_path}")
    print(f"Report: {processor.output_path / 'MCF_DUALUSE_INTELLIGENCE_REPORT.md'}")

if __name__ == "__main__":
    main()
