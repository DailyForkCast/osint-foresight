#!/usr/bin/env python3
"""
Quick TED Analysis - Process single month for immediate insights
"""

import json
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuickTEDAnalyzer:
    def __init__(self):
        self.ted_path = Path("F:/TED_Data/monthly")
        self.output_path = Path("reports/country=IT/ted_quick_analysis.json")

        # Focus on key technologies
        self.tech_keywords = {
            'ai_ml': ['artificial intelligence', 'machine learning', 'AI'],
            'quantum': ['quantum'],
            'semiconductors': ['semiconductor', 'microchip', 'chip'],
            'aerospace': ['aerospace', 'satellite', 'drone'],
            'cybersecurity': ['cybersecurity', 'cyber security'],
            'defense': ['defense', 'defence', 'military']
        }

        self.results = {
            'month_analyzed': '',
            'total_procurements': 0,
            'italian_procurements': 0,
            'tech_procurements': 0,
            'sample_findings': []
        }

    def is_italian_procurement(self, root):
        """Check if procurement is from Italian authority"""

        # Look for Italian country codes
        for country in root.findall('.//COUNTRY'):
            if country.get('VALUE') == 'IT':
                return True

        # Look for Italian city/organization names
        text_content = ET.tostring(root, encoding='unicode', method='text').lower()
        italian_indicators = [
            'italia', 'italy', 'roma', 'milano', 'torino',
            'ministero', 'agenzia', 'comune', 'regione'
        ]

        return any(indicator in text_content for indicator in italian_indicators)

    def identify_technologies(self, text_content):
        """Identify technology categories in procurement"""
        found_techs = []
        text_lower = text_content.lower()

        for tech_cat, keywords in self.tech_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_techs.append(tech_cat)

        return found_techs

    def analyze_single_file(self, file_obj):
        """Analyze single XML procurement file"""
        try:
            content = file_obj.read()
            root = ET.fromstring(content)

            self.results['total_procurements'] += 1

            if self.is_italian_procurement(root):
                self.results['italian_procurements'] += 1

                # Extract text content
                text_content = ET.tostring(root, encoding='unicode', method='text')
                technologies = self.identify_technologies(text_content)

                if technologies:
                    self.results['tech_procurements'] += 1

                    # Extract basic info for sample
                    title = root.findtext('.//TITLE_TEXT', 'No title')
                    contracting_body = root.findtext('.//OFFICIALNAME', 'Unknown authority')

                    sample = {
                        'title': title[:100] + '...' if len(title) > 100 else title,
                        'authority': contracting_body,
                        'technologies': technologies
                    }

                    if len(self.results['sample_findings']) < 10:
                        self.results['sample_findings'].append(sample)

                    logger.info(f"Found tech procurement: {technologies} - {title[:50]}...")

        except Exception as e:
            logger.warning(f"Error processing file: {e}")

    def process_recent_month(self):
        """Process the most recent available month"""

        # Find most recent month with data
        recent_months = []
        for year_dir in sorted(self.ted_path.iterdir(), reverse=True):
            if year_dir.is_dir() and year_dir.name.isdigit():
                month_files = list(year_dir.glob("TED_monthly_*.tar.gz"))
                if month_files:
                    recent_months.extend([(year_dir.name, f) for f in sorted(month_files)])

        if not recent_months:
            logger.error("No TED data found")
            return

        # Process most recent month
        year, tar_file = recent_months[0]
        self.results['month_analyzed'] = f"{year}/{tar_file.name}"

        logger.info(f"Processing {tar_file}")

        try:
            with tarfile.open(tar_file, 'r:gz') as outer_tar:
                # TED files contain nested archives
                for member in outer_tar.getmembers():
                    if member.name.endswith('.tar.gz'):
                        inner_tar_file = outer_tar.extractfile(member)
                        if inner_tar_file:
                            try:
                                with tarfile.open(fileobj=inner_tar_file, mode='r:gz') as inner_tar:
                                    for inner_member in inner_tar.getmembers():
                                        if inner_member.name.endswith('.xml'):
                                            xml_file = inner_tar.extractfile(inner_member)
                                            if xml_file:
                                                self.analyze_single_file(xml_file)

                                                # Limit processing for quick analysis
                                                if self.results['total_procurements'] > 1000:
                                                    logger.info("Processed 1000 files for quick analysis")
                                                    return
                            except Exception as e:
                                logger.warning(f"Error with inner archive: {e}")

        except Exception as e:
            logger.error(f"Error processing {tar_file}: {e}")

    def generate_report(self):
        """Generate quick analysis report"""

        # Calculate percentages
        if self.results['total_procurements'] > 0:
            italian_pct = (self.results['italian_procurements'] / self.results['total_procurements']) * 100
            tech_pct = (self.results['tech_procurements'] / self.results['total_procurements']) * 100
        else:
            italian_pct = tech_pct = 0

        report = {
            'analysis_date': datetime.now().isoformat(),
            'data_source': self.results['month_analyzed'],
            'summary': {
                'total_procurements_sampled': self.results['total_procurements'],
                'italian_procurements': self.results['italian_procurements'],
                'italian_percentage': round(italian_pct, 2),
                'technology_procurements': self.results['tech_procurements'],
                'tech_percentage': round(tech_pct, 2)
            },
            'sample_tech_procurements': self.results['sample_findings'],
            'next_steps': [
                'Run full multi-year analysis with complete TED dataset',
                'Identify Chinese suppliers in Italian technology procurements',
                'Map procurement patterns by technology category',
                'Analyze value trends over time'
            ]
        }

        # Save report
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Quick analysis report saved to {self.output_path}")
        return report

def main():
    analyzer = QuickTEDAnalyzer()
    analyzer.process_recent_month()
    report = analyzer.generate_report()

    print(f"\n=== TED Quick Analysis Results ===")
    print(f"Data source: {report['data_source']}")
    print(f"Total procurements sampled: {report['summary']['total_procurements_sampled']}")
    print(f"Italian procurements: {report['summary']['italian_procurements']} ({report['summary']['italian_percentage']}%)")
    print(f"Technology procurements: {report['summary']['technology_procurements']} ({report['summary']['tech_percentage']}%)")
    print(f"\nSample findings: {len(report['sample_tech_procurements'])} technology procurements identified")

if __name__ == "__main__":
    main()
