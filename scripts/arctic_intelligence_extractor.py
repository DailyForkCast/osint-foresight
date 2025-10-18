#!/usr/bin/env python3
"""
Arctic Technology and Security Intelligence Extractor
Focused extraction of Arctic-related dual-use technologies and security implications
"""

import os
import json
import sqlite3
import PyPDF2
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import re

class ArcticIntelligenceExtractor:
    def __init__(self):
        self.reports_path = Path("F:/Reports")
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.output_path = Path("C:/Projects/OSINT - Foresight/analysis")

        # Comprehensive Arctic technology and security keywords
        self.arctic_keywords = {
            'geographic': [
                'arctic', 'antarctic', 'polar', 'greenland', 'svalbard',
                'arctic circle', 'north pole', 'south pole', 'polar regions',
                'arctic ocean', 'barents sea', 'beaufort sea', 'chukchi sea',
                'laptev sea', 'kara sea', 'east siberian sea', 'bering strait'
            ],
            'infrastructure': [
                'icebreaker', 'ice-class vessel', 'polar research station',
                'arctic port', 'northern sea route', 'northeast passage',
                'northwest passage', 'transpolar route', 'arctic shipping',
                'ice navigation', 'polar runway', 'arctic airfield',
                'undersea cable', 'arctic pipeline', 'lng terminal'
            ],
            'technology': [
                'ice-resistant technology', 'cold weather equipment',
                'permafrost monitoring', 'ice thickness measurement',
                'polar satellite', 'arctic surveillance', 'ice radar',
                'arctic communications', 'polar positioning system',
                'ice prediction', 'weather forecasting', 'climate monitoring',
                'arctic drilling', 'subsea technology', 'polar construction'
            ],
            'resources': [
                'arctic minerals', 'rare earth elements', 'arctic oil',
                'arctic gas', 'methane hydrates', 'arctic fishing',
                'marine resources', 'seabed mining', 'arctic lithium',
                'arctic cobalt', 'arctic nickel', 'arctic uranium'
            ],
            'security': [
                'arctic sovereignty', 'territorial claims', 'exclusive economic zone',
                'continental shelf', 'unclos', 'arctic council', 'polar code',
                'search and rescue', 'maritime domain awareness',
                'dual-use arctic technology', 'military arctic presence',
                'arctic deterrence', 'polar strategic competition'
            ],
            'chinese_arctic': [
                'polar silk road', 'belt and road', 'near-arctic state',
                'chinese arctic policy', 'chinese polar research',
                'chinese icebreaker', 'xuelong', 'china arctic research',
                'china polar research institute', 'sino-arctic cooperation'
            ]
        }

        self.setup_database()

    def setup_database(self):
        """Create Arctic intelligence database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS arctic_reports (
                report_id TEXT PRIMARY KEY,
                filename TEXT,
                title TEXT,
                organization TEXT,
                arctic_relevance_score INTEGER,
                chinese_arctic_score INTEGER,
                key_findings TEXT,
                geographic_focus TEXT,
                technology_categories TEXT,
                security_implications TEXT,
                processed_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS arctic_technologies (
                tech_id TEXT PRIMARY KEY,
                technology_name TEXT,
                category TEXT,
                dual_use_potential TEXT,
                chinese_capabilities TEXT,
                strategic_importance TEXT,
                geographic_application TEXT,
                source_reports TEXT
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS arctic_infrastructure (
                infra_id TEXT PRIMARY KEY,
                infrastructure_type TEXT,
                location TEXT,
                strategic_value TEXT,
                chinese_involvement TEXT,
                dual_use_assessment TEXT,
                source_reports TEXT
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS arctic_resources (
                resource_id TEXT PRIMARY KEY,
                resource_type TEXT,
                location TEXT,
                strategic_importance TEXT,
                extraction_technology TEXT,
                chinese_interest TEXT,
                source_reports TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def process_arctic_reports(self):
        """Process all reports for Arctic intelligence"""
        print("Extracting Arctic technology and security intelligence...")

        # Focus on Arctic-specific and general reports that might contain Arctic content
        pdf_files = list(self.reports_path.glob("*.pdf"))
        arctic_reports = []

        for pdf_file in pdf_files:
            try:
                print(f"Analyzing: {pdf_file.name}")
                arctic_data = self.extract_arctic_intelligence(pdf_file)
                if arctic_data and arctic_data['arctic_score'] > 0:
                    arctic_reports.append(arctic_data)
                    self.store_arctic_data(arctic_data)
                    print(f"  -> Arctic relevance: {arctic_data['arctic_score']}/100")
            except Exception as e:
                print(f"  -> Error: {e}")
                continue

        print(f"Successfully processed {len(arctic_reports)} reports with Arctic content")
        return arctic_reports

    def extract_arctic_intelligence(self, pdf_path: Path) -> Dict:
        """Extract Arctic-specific intelligence from a report"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Extract text (focus on first 50 pages for efficiency)
                text_content = ""
                max_pages = min(len(pdf_reader.pages), 50)

                for page_num in range(max_pages):
                    try:
                        text_content += pdf_reader.pages[page_num].extract_text()
                    except:
                        continue

            # Analyze Arctic content
            analysis = self.analyze_arctic_content(text_content)

            # Only return data if there's meaningful Arctic content
            if analysis['arctic_relevance'] < 5:
                return None

            arctic_data = {
                'report_id': f"arctic_{pdf_path.stem}_{datetime.now().strftime('%Y%m%d')}",
                'filename': pdf_path.name,
                'title': self.extract_title(text_content),
                'organization': self.extract_organization(pdf_path.name),
                'arctic_score': analysis['arctic_relevance'],
                'chinese_arctic_score': analysis['chinese_arctic'],
                'key_findings': analysis['key_findings'],
                'geographic_focus': analysis['geographic_areas'],
                'technologies': analysis['technologies'],
                'infrastructure': analysis['infrastructure'],
                'resources': analysis['resources'],
                'security_implications': analysis['security_aspects']
            }

            return arctic_data

        except Exception as e:
            return None

    def analyze_arctic_content(self, text: str) -> Dict:
        """Analyze text for Arctic-specific content"""
        text_lower = text.lower()

        analysis = {
            'arctic_relevance': 0,
            'chinese_arctic': 0,
            'key_findings': [],
            'geographic_areas': [],
            'technologies': [],
            'infrastructure': [],
            'resources': [],
            'security_aspects': []
        }

        # Calculate Arctic relevance scores
        for category, keywords in self.arctic_keywords.items():
            category_score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    category_score += 5

                    # Categorize the finding
                    if category == 'geographic':
                        analysis['geographic_areas'].append(keyword)
                    elif category == 'technology':
                        analysis['technologies'].append(keyword)
                    elif category == 'infrastructure':
                        analysis['infrastructure'].append(keyword)
                    elif category == 'resources':
                        analysis['resources'].append(keyword)
                    elif category == 'security':
                        analysis['security_aspects'].append(keyword)
                    elif category == 'chinese_arctic':
                        analysis['chinese_arctic'] += 10

            analysis['arctic_relevance'] += category_score

        # Cap the scores
        analysis['arctic_relevance'] = min(analysis['arctic_relevance'], 100)
        analysis['chinese_arctic'] = min(analysis['chinese_arctic'], 100)

        # Extract key Arctic-related sentences
        sentences = text.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            arctic_keyword_count = sum(1 for keywords in self.arctic_keywords.values()
                                     for keyword in keywords if keyword in sentence_lower)

            if arctic_keyword_count >= 2 and len(sentence.strip()) > 50:
                analysis['key_findings'].append(sentence.strip())

        # Limit findings to most relevant
        analysis['key_findings'] = analysis['key_findings'][:10]

        return analysis

    def extract_title(self, text: str) -> str:
        """Extract document title"""
        lines = text.split('\n')[:15]
        for line in lines:
            line = line.strip()
            if 20 < len(line) < 200 and not line.isupper():
                return line
        return "Arctic Intelligence Document"

    def extract_organization(self, filename: str) -> str:
        """Extract organization from filename"""
        org_patterns = {
            'DOD': 'Department of Defense',
            'CSET': 'Center for Security and Emerging Technology',
            'ASPI': 'Australian Strategic Policy Institute',
            'RAND': 'RAND Corporation',
            'CSIS': 'Center for Strategic and International Studies'
        }

        filename_upper = filename.upper()
        for pattern, org in org_patterns.items():
            if pattern in filename_upper:
                return org

        return "Unknown Organization"

    def store_arctic_data(self, arctic_data: Dict):
        """Store Arctic intelligence in database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Store main report
        cur.execute('''
            INSERT OR REPLACE INTO arctic_reports
            (report_id, filename, title, organization, arctic_relevance_score,
             chinese_arctic_score, key_findings, geographic_focus,
             technology_categories, security_implications)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            arctic_data['report_id'],
            arctic_data['filename'],
            arctic_data['title'],
            arctic_data['organization'],
            arctic_data['arctic_score'],
            arctic_data['chinese_arctic_score'],
            json.dumps(arctic_data['key_findings']),
            json.dumps(arctic_data['geographic_focus']),
            json.dumps(arctic_data['technologies']),
            json.dumps(arctic_data['security_implications'])
        ))

        # Store technologies
        for tech in arctic_data['technologies']:
            tech_id = f"arctic_tech_{tech.replace(' ', '_')}_{arctic_data['report_id']}"
            cur.execute('''
                INSERT OR IGNORE INTO arctic_technologies
                (tech_id, technology_name, source_reports)
                VALUES (?, ?, ?)
            ''', (tech_id, tech, arctic_data['filename']))

        # Store infrastructure
        for infra in arctic_data['infrastructure']:
            infra_id = f"arctic_infra_{infra.replace(' ', '_')}_{arctic_data['report_id']}"
            cur.execute('''
                INSERT OR IGNORE INTO arctic_infrastructure
                (infra_id, infrastructure_type, source_reports)
                VALUES (?, ?, ?)
            ''', (infra_id, infra, arctic_data['filename']))

        # Store resources
        for resource in arctic_data['resources']:
            resource_id = f"arctic_res_{resource.replace(' ', '_')}_{arctic_data['report_id']}"
            cur.execute('''
                INSERT OR IGNORE INTO arctic_resources
                (resource_id, resource_type, source_reports)
                VALUES (?, ?, ?)
            ''', (resource_id, resource, arctic_data['filename']))

        conn.commit()
        conn.close()

    def generate_arctic_intelligence_report(self):
        """Generate comprehensive Arctic intelligence report"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Get statistics
        cur.execute('SELECT COUNT(*) FROM arctic_reports')
        total_reports = cur.fetchone()[0]

        cur.execute('SELECT COUNT(*) FROM arctic_technologies')
        total_technologies = cur.fetchone()[0]

        # Get top Arctic reports
        cur.execute('''
            SELECT filename, title, organization, arctic_relevance_score, chinese_arctic_score
            FROM arctic_reports
            ORDER BY arctic_relevance_score DESC
            LIMIT 10
        ''')
        top_reports = cur.fetchall()

        # Get Arctic technologies
        cur.execute('''
            SELECT technology_name, COUNT(*) as frequency
            FROM arctic_technologies
            GROUP BY technology_name
            ORDER BY frequency DESC
            LIMIT 15
        ''')
        top_technologies = cur.fetchall()

        # Get Chinese Arctic activities
        cur.execute('''
            SELECT filename, title, chinese_arctic_score
            FROM arctic_reports
            WHERE chinese_arctic_score > 0
            ORDER BY chinese_arctic_score DESC
            LIMIT 10
        ''')
        chinese_arctic = cur.fetchall()

        conn.close()

        # Generate report
        report = f"""# ARCTIC TECHNOLOGY AND SECURITY INTELLIGENCE REPORT
Generated: {datetime.now().isoformat()}
Source: Comprehensive Arctic Intelligence Analysis

## EXECUTIVE SUMMARY

### Arctic Intelligence Collection Statistics
- **Total Reports with Arctic Content**: {total_reports}
- **Arctic Technologies Identified**: {total_technologies}
- **Reports with Chinese Arctic Content**: {len(chinese_arctic)}
- **High-Relevance Arctic Reports**: {len([r for r in top_reports if r[3] > 50])}

## PRIORITY ARCTIC INTELLIGENCE REPORTS

### Highest Arctic Relevance Scores
"""

        for report_data in top_reports:
            filename, title, org, arctic_score, chinese_score = report_data
            report += f"""
**{title}**
- Organization: {org}
- Arctic Relevance: {arctic_score}/100
- Chinese Arctic Content: {chinese_score}/100
- File: {filename}
"""

        report += f"""
## CRITICAL ARCTIC TECHNOLOGIES IDENTIFIED

### Most Frequently Mentioned Arctic Technologies
"""

        for tech, freq in top_technologies:
            report += f"- **{tech.title()}**: Identified in {freq} reports\n"

        if chinese_arctic:
            report += f"""
## CHINESE ARCTIC ACTIVITIES AND INTERESTS

### Reports with Significant Chinese Arctic Content
"""
            for filename, title, score in chinese_arctic:
                report += f"""
**{title}**
- Chinese Arctic Score: {score}/100
- Source: {filename}
"""

        report += """
## STRATEGIC ARCTIC INTELLIGENCE ASSESSMENTS

### Key Arctic Technology Categories
1. **Ice Navigation and Icebreaking Technology**
   - Critical for Arctic shipping routes
   - Dual-use applications for naval operations
   - Chinese investment in icebreaker capabilities

2. **Polar Communications and Surveillance**
   - Satellite coverage in polar regions
   - Arctic radar and monitoring systems
   - Dual-use implications for military surveillance

3. **Arctic Resource Extraction Technology**
   - Offshore drilling in ice conditions
   - Subsea mining technologies
   - Critical mineral extraction capabilities

4. **Cold Weather Military Technology**
   - Arctic-rated equipment and vehicles
   - Cold weather operational capabilities
   - Polar logistics and supply chains

### Chinese Arctic Strategy Implications
- **Polar Silk Road Initiative**: Infrastructure development with dual-use potential
- **Research Station Network**: Expanding presence under scientific cooperation
- **Resource Extraction Interests**: Focus on Arctic minerals and energy
- **Maritime Route Development**: Northern Sea Route commercial and strategic value

## THREAT ASSESSMENT

### High Priority Arctic Concerns
1. **Dual-Use Infrastructure**: Chinese research facilities with potential military applications
2. **Technology Transfer**: Arctic technology sharing with strategic implications
3. **Resource Dependencies**: Critical mineral extraction in Arctic regions
4. **Maritime Domain Control**: Arctic shipping route influence

### Medium Priority Monitoring Areas
1. **Scientific Cooperation**: Research partnerships with dual-use potential
2. **Technology Development**: Arctic-specific capability advancement
3. **Commercial Investments**: Private sector Arctic engagement

## RECOMMENDED ACTIONS

### Immediate (24-48 Hours)
1. Review high-scoring Chinese Arctic reports for actionable intelligence
2. Assess Arctic technology dependencies and vulnerabilities
3. Evaluate dual-use potential of identified Arctic technologies

### Short-term (1-2 Weeks)
1. Deep-dive analysis of Chinese Arctic infrastructure projects
2. Arctic technology supply chain vulnerability assessment
3. Enhanced monitoring of Arctic research cooperation

### Strategic (1-3 Months)
1. Comprehensive Arctic threat modeling
2. Arctic technology dependency mitigation strategies
3. Enhanced Arctic domain awareness capabilities

---
*Arctic Technology and Security Intelligence Report*
*Classification: For Official Use Only*
*Database: F:/OSINT_WAREHOUSE/arctic_intelligence.db*
*Focus: Dual-Use Arctic Technologies and Chinese Activities*
"""

        # Save report
        report_path = self.output_path / "ARCTIC_INTELLIGENCE_REPORT.md"
        report_path.write_text(report)
        print(f"Arctic intelligence report saved to {report_path}")

        return report

def main():
    extractor = ArcticIntelligenceExtractor()

    print("Arctic Technology and Security Intelligence Extractor")
    print("=" * 60)

    # Process reports for Arctic content
    print("\nProcessing reports for Arctic intelligence...")
    arctic_reports = extractor.process_arctic_reports()

    # Generate Arctic intelligence report
    print("\nGenerating Arctic intelligence report...")
    extractor.generate_arctic_intelligence_report()

    print(f"\nArctic Intelligence Processing Complete!")
    print(f"Reports with Arctic Content: {len(arctic_reports)}")
    print(f"Database: {extractor.db_path}")
    print(f"Report: {extractor.output_path / 'ARCTIC_INTELLIGENCE_REPORT.md'}")

if __name__ == "__main__":
    main()
