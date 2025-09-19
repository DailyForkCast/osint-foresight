#!/usr/bin/env python3
"""
TED (Tenders Electronic Daily) Italy Procurement Analyzer
Analyzes Italian public procurement data for technology and defense patterns
"""

import json
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TEDItalyAnalyzer:
    """Analyze Italian procurement data from TED archives"""

    def __init__(self, ted_data_path: str = "F:/TED_Data"):
        self.ted_path = Path(ted_data_path)
        self.output_dir = Path("artifacts/ITA/ted_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Critical technology keywords for procurement analysis
        self.tech_keywords = {
            'ai_ml': ['artificial intelligence', 'machine learning', 'neural network', 'deep learning'],
            'quantum': ['quantum', 'qubit', 'quantum computing', 'quantum communication'],
            'semiconductors': ['semiconductor', 'microchip', 'integrated circuit', 'processor'],
            'aerospace': ['aerospace', 'satellite', 'spacecraft', 'launch vehicle', 'drone', 'UAV'],
            'cybersecurity': ['cybersecurity', 'encryption', 'firewall', 'intrusion detection'],
            'defense': ['defense', 'military', 'weapon', 'missile', 'radar', 'sonar'],
            'telecommunications': ['5G', '6G', 'telecommunications', 'network infrastructure'],
            'energy': ['renewable energy', 'battery', 'solar', 'wind power', 'energy storage']
        }

        # Italian contracting authorities of interest
        self.key_authorities = [
            'Leonardo', 'Fincantieri', 'ASI', 'CNR', 'ENEA', 'IIT',
            'Ministero della Difesa', 'Ministry of Defence',
            'Agenzia Spaziale Italiana', 'Italian Space Agency'
        ]

        self.results = {
            'summary': {},
            'by_year': {},
            'by_technology': {},
            'by_authority': {},
            'china_linked': [],
            'high_value_contracts': [],
            'technology_trends': {}
        }

    def analyze_procurement_file(self, filepath: Path) -> Dict:
        """Analyze a single TED XML file for Italian procurements"""

        try:
            tree = ET.parse(filepath)
            root = tree.getroot()

            # Check if it's an Italian procurement
            country = root.findtext('.//ISO_COUNTRY', default='')
            if country != 'IT':
                return None

            procurement = {
                'file': filepath.name,
                'country': country,
                'date': root.findtext('.//DATE_PUB', default=''),
                'authority': root.findtext('.//OFFICIALNAME', default=''),
                'title': root.findtext('.//TITLE', default=''),
                'description': root.findtext('.//SHORT_DESCR', default=''),
                'value': self._extract_value(root),
                'cpv_codes': self._extract_cpv_codes(root),
                'technologies': [],
                'china_risk': False
            }

            # Analyze for technology categories
            text_to_analyze = f"{procurement['title']} {procurement['description']}".lower()
            for tech_cat, keywords in self.tech_keywords.items():
                if any(keyword in text_to_analyze for keyword in keywords):
                    procurement['technologies'].append(tech_cat)

            # Check for China-related suppliers or mentions
            if any(term in text_to_analyze for term in ['china', 'chinese', 'huawei', 'zte', 'hikvision']):
                procurement['china_risk'] = True

            return procurement

        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")
            return None

    def _extract_value(self, root) -> float:
        """Extract contract value from XML"""
        try:
            value_text = root.findtext('.//VALUE', default='0')
            # Remove currency symbols and convert
            value_clean = ''.join(c for c in value_text if c.isdigit() or c == '.')
            return float(value_clean) if value_clean else 0
        except:
            return 0

    def _extract_cpv_codes(self, root) -> List[str]:
        """Extract CPV (Common Procurement Vocabulary) codes"""
        cpv_codes = []
        for cpv in root.findall('.//CPV_CODE'):
            code = cpv.get('CODE', '')
            if code:
                cpv_codes.append(code)
        return cpv_codes

    def process_monthly_archive(self, tar_path: Path) -> Dict:
        """Process a monthly TED archive file"""

        logger.info(f"Processing {tar_path.name}")
        monthly_results = {
            'total_italian': 0,
            'tech_procurements': 0,
            'china_linked': 0,
            'total_value': 0,
            'by_technology': {},
            'procurements': []
        }

        try:
            with tarfile.open(tar_path, 'r:gz') as tar:
                for member in tar.getmembers():
                    if member.name.endswith('.xml'):
                        f = tar.extractfile(member)
                        if f:
                            result = self.analyze_procurement_file(f)
                            if result:
                                monthly_results['total_italian'] += 1
                                monthly_results['total_value'] += result['value']

                                if result['technologies']:
                                    monthly_results['tech_procurements'] += 1
                                    for tech in result['technologies']:
                                        monthly_results['by_technology'][tech] = \
                                            monthly_results['by_technology'].get(tech, 0) + 1

                                if result['china_risk']:
                                    monthly_results['china_linked'] += 1
                                    self.results['china_linked'].append(result)

                                if result['value'] > 10000000:  # High value > €10M
                                    self.results['high_value_contracts'].append(result)

                                monthly_results['procurements'].append(result)

        except Exception as e:
            logger.error(f"Error processing archive {tar_path}: {e}")

        return monthly_results

    def analyze_all_ted_data(self, start_year: int = 2020, end_year: int = 2025):
        """Analyze all TED data for specified years"""

        logger.info(f"Analyzing TED data from {start_year} to {end_year}")

        for year in range(start_year, end_year + 1):
            year_dir = self.ted_path / "monthly" / str(year)
            if not year_dir.exists():
                logger.warning(f"Year directory {year_dir} not found")
                continue

            year_results = {
                'total_procurements': 0,
                'tech_procurements': 0,
                'china_linked': 0,
                'total_value': 0,
                'by_month': {},
                'by_technology': {}
            }

            # Process each monthly archive
            for tar_file in sorted(year_dir.glob("*.tar.gz")):
                month_results = self.process_monthly_archive(tar_file)

                # Aggregate results
                month_key = tar_file.stem.split('_')[-1]  # Extract month
                year_results['by_month'][month_key] = month_results
                year_results['total_procurements'] += month_results['total_italian']
                year_results['tech_procurements'] += month_results['tech_procurements']
                year_results['china_linked'] += month_results['china_linked']
                year_results['total_value'] += month_results['total_value']

                # Aggregate technology categories
                for tech, count in month_results['by_technology'].items():
                    year_results['by_technology'][tech] = \
                        year_results['by_technology'].get(tech, 0) + count

            self.results['by_year'][year] = year_results
            logger.info(f"Year {year}: {year_results['total_procurements']} Italian procurements")

    def analyze_technology_trends(self):
        """Analyze technology procurement trends over time"""

        trends = {}
        for year, year_data in self.results['by_year'].items():
            for tech, count in year_data['by_technology'].items():
                if tech not in trends:
                    trends[tech] = {}
                trends[tech][year] = count

        self.results['technology_trends'] = trends

    def generate_summary(self):
        """Generate summary statistics"""

        total_procurements = sum(
            year_data['total_procurements']
            for year_data in self.results['by_year'].values()
        )

        total_tech = sum(
            year_data['tech_procurements']
            for year_data in self.results['by_year'].values()
        )

        total_china = sum(
            year_data['china_linked']
            for year_data in self.results['by_year'].values()
        )

        total_value = sum(
            year_data['total_value']
            for year_data in self.results['by_year'].values()
        )

        self.results['summary'] = {
            'total_italian_procurements': total_procurements,
            'technology_procurements': total_tech,
            'china_linked_procurements': total_china,
            'total_value_eur': total_value,
            'tech_procurement_rate': (total_tech / total_procurements * 100) if total_procurements > 0 else 0,
            'china_risk_rate': (total_china / total_procurements * 100) if total_procurements > 0 else 0,
            'high_value_contracts': len(self.results['high_value_contracts']),
            'analysis_period': f"{min(self.results['by_year'].keys())}-{max(self.results['by_year'].keys())}"
        }

    def save_results(self):
        """Save analysis results"""

        # Save full results
        output_file = self.output_dir / "ted_italy_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"Results saved to {output_file}")

        # Save summary report
        self.generate_markdown_report()

    def generate_markdown_report(self):
        """Generate markdown report of findings"""

        report = f"""# Italy TED Procurement Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d')}
**Data Source:** TED (Tenders Electronic Daily)
**Analysis Period:** {self.results['summary'].get('analysis_period', 'N/A')}

## Executive Summary

- **Total Italian Procurements:** {self.results['summary'].get('total_italian_procurements', 0):,}
- **Technology-Related:** {self.results['summary'].get('technology_procurements', 0):,} ({self.results['summary'].get('tech_procurement_rate', 0):.1f}%)
- **China-Linked:** {self.results['summary'].get('china_linked_procurements', 0):,} ({self.results['summary'].get('china_risk_rate', 0):.1f}%)
- **Total Value:** €{self.results['summary'].get('total_value_eur', 0):,.0f}
- **High-Value Contracts (>€10M):** {self.results['summary'].get('high_value_contracts', 0)}

## Technology Procurement Trends

"""

        # Add technology trends
        for tech in self.results['technology_trends']:
            report += f"\n### {tech.upper()}\n"
            for year in sorted(self.results['technology_trends'][tech].keys()):
                count = self.results['technology_trends'][tech][year]
                report += f"- {year}: {count} procurements\n"

        # Add China-linked procurements
        if self.results['china_linked']:
            report += "\n## China-Linked Procurements (Sample)\n\n"
            for proc in self.results['china_linked'][:10]:  # First 10
                report += f"- **{proc['authority']}**: {proc['title'][:100]}... (€{proc['value']:,.0f})\n"

        # Save report
        report_file = self.output_dir / "ted_italy_report.md"
        with open(report_file, 'w') as f:
            f.write(report)

        logger.info(f"Report saved to {report_file}")

def main():
    """Run TED Italy analysis"""

    analyzer = TEDItalyAnalyzer()

    print("\n" + "="*60)
    print("TED ITALY PROCUREMENT ANALYSIS")
    print("="*60 + "\n")

    # Analyze data
    analyzer.analyze_all_ted_data(start_year=2020, end_year=2025)
    analyzer.analyze_technology_trends()
    analyzer.generate_summary()
    analyzer.save_results()

    # Print summary
    print("\nSummary:")
    for key, value in analyzer.results['summary'].items():
        print(f"  {key}: {value}")

    print(f"\nResults saved to: artifacts/ITA/ted_analysis/")

if __name__ == "__main__":
    main()
