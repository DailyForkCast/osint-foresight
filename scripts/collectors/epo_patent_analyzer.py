#!/usr/bin/env python3
"""
EPO Patent Analyzer for Italy
Analyzes European Patent Office data for Italian innovation patterns and China collaborations
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EPOPatentAnalyzer:
    """Analyze EPO patent data for Italy"""

    def __init__(self, data_path: str = "F:/OSINT_Data/EPO_PATENTS"):
        self.data_path = Path(data_path)
        self.output_dir = Path("artifacts/ITA/patent_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Technology classification (IPC codes)
        self.tech_classifications = {
            'semiconductors': ['H01L', 'H03K', 'H03L'],
            'ai_computing': ['G06N', 'G06F', 'G06K'],
            'telecommunications': ['H04B', 'H04L', 'H04W'],
            'aerospace': ['B64C', 'B64D', 'B64G'],
            'biotechnology': ['C12N', 'C12P', 'C12Q'],
            'nanotechnology': ['B82Y'],
            'quantum': ['G06N10', 'H04L9'],
            'robotics': ['B25J', 'B62D57'],
            'energy': ['H01M', 'H02J', 'H02S']
        }

        self.results = {
            'summary': {},
            'by_year': defaultdict(lambda: defaultdict(int)),
            'by_technology': defaultdict(lambda: defaultdict(int)),
            'italian_patents': [],
            'china_collaborations': [],
            'key_inventors': defaultdict(int),
            'key_assignees': defaultdict(int),
            'technology_trends': {}
        }

    def analyze_patent_file(self, filepath: Path) -> Dict:
        """Analyze a single patent file"""

        try:
            # Parse patent data (XML or JSON depending on format)
            if filepath.suffix == '.xml':
                tree = ET.parse(filepath)
                root = tree.getroot()
                patent = self._parse_xml_patent(root)
            elif filepath.suffix == '.json':
                with open(filepath, 'r', encoding='utf-8') as f:
                    patent = json.load(f)
            else:
                return None

            # Check for Italian involvement
            has_italian = False
            has_chinese = False

            # Analyze inventors
            for inventor in patent.get('inventors', []):
                country = inventor.get('country', '')
                if country == 'IT':
                    has_italian = True
                    self.results['key_inventors'][inventor.get('name', 'Unknown')] += 1
                elif country == 'CN':
                    has_chinese = True

            # Analyze assignees/applicants
            for assignee in patent.get('assignees', []):
                country = assignee.get('country', '')
                if country == 'IT':
                    has_italian = True
                    self.results['key_assignees'][assignee.get('name', 'Unknown')] += 1
                elif country == 'CN':
                    has_chinese = True

            if has_italian:
                # Extract patent details
                patent_data = {
                    'publication_number': patent.get('publication_number'),
                    'title': patent.get('title'),
                    'abstract': patent.get('abstract'),
                    'filing_date': patent.get('filing_date'),
                    'publication_date': patent.get('publication_date'),
                    'ipc_codes': patent.get('ipc_codes', []),
                    'inventors': patent.get('inventors', []),
                    'assignees': patent.get('assignees', []),
                    'technology_fields': self._classify_technology(patent.get('ipc_codes', [])),
                    'has_chinese_collaboration': has_chinese,
                    'citations_count': len(patent.get('citations', [])),
                    'cited_by_count': patent.get('cited_by_count', 0)
                }

                self.results['italian_patents'].append(patent_data)

                # Track China collaborations
                if has_chinese:
                    self.results['china_collaborations'].append(patent_data)

                # Update statistics
                year = patent_data['publication_date'][:4] if patent_data['publication_date'] else 'unknown'
                self.results['by_year'][year]['total'] += 1
                if has_chinese:
                    self.results['by_year'][year]['china_collab'] += 1

                # Track by technology
                for tech in patent_data['technology_fields']:
                    self.results['by_technology'][tech]['total'] += 1
                    if has_chinese:
                        self.results['by_technology'][tech]['china_collab'] += 1

                return patent_data

        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")
            return None

    def _parse_xml_patent(self, root) -> Dict:
        """Parse XML patent data"""

        patent = {
            'publication_number': root.findtext('.//publication-reference/document-id/doc-number', ''),
            'title': root.findtext('.//invention-title', ''),
            'abstract': root.findtext('.//abstract', ''),
            'filing_date': root.findtext('.//application-reference/document-id/date', ''),
            'publication_date': root.findtext('.//publication-reference/document-id/date', ''),
            'ipc_codes': [],
            'inventors': [],
            'assignees': []
        }

        # Extract IPC codes
        for ipc in root.findall('.//classification-ipc'):
            code = ipc.findtext('.//section', '') + ipc.findtext('.//class', '') + ipc.findtext('.//subclass', '')
            if code:
                patent['ipc_codes'].append(code)

        # Extract inventors
        for inventor in root.findall('.//inventor'):
            patent['inventors'].append({
                'name': inventor.findtext('.//name', ''),
                'country': inventor.findtext('.//country', '')
            })

        # Extract assignees
        for assignee in root.findall('.//assignee'):
            patent['assignees'].append({
                'name': assignee.findtext('.//orgname', ''),
                'country': assignee.findtext('.//country', '')
            })

        return patent

    def _classify_technology(self, ipc_codes: List[str]) -> List[str]:
        """Classify patent into technology categories based on IPC codes"""

        technologies = []
        for code in ipc_codes:
            for tech_name, tech_codes in self.tech_classifications.items():
                if any(code.startswith(tc) for tc in tech_codes):
                    technologies.append(tech_name)

        return list(set(technologies))  # Remove duplicates

    def analyze_all_patents(self):
        """Analyze all patent files in the data directory"""

        logger.info(f"Analyzing patents in {self.data_path}")

        # Find all patent files
        patent_files = list(self.data_path.glob("**/*.xml")) + list(self.data_path.glob("**/*.json"))

        logger.info(f"Found {len(patent_files)} patent files")

        for i, filepath in enumerate(patent_files):
            if i % 1000 == 0:
                logger.info(f"Processing patent {i}/{len(patent_files)}")

            self.analyze_patent_file(filepath)

    def analyze_trends(self):
        """Analyze patent trends over time"""

        # Calculate collaboration rates by year
        for year in self.results['by_year']:
            total = self.results['by_year'][year]['total']
            china_collab = self.results['by_year'][year]['china_collab']
            if total > 0:
                self.results['by_year'][year]['china_rate'] = (china_collab / total) * 100

        # Calculate collaboration rates by technology
        for tech in self.results['by_technology']:
            total = self.results['by_technology'][tech]['total']
            china_collab = self.results['by_technology'][tech]['china_collab']
            if total > 0:
                self.results['by_technology'][tech]['china_rate'] = (china_collab / total) * 100

        # Identify top inventors and assignees
        self.results['top_inventors'] = sorted(
            self.results['key_inventors'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]

        self.results['top_assignees'] = sorted(
            self.results['key_assignees'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]

    def generate_summary(self):
        """Generate summary statistics"""

        total_patents = len(self.results['italian_patents'])
        china_collabs = len(self.results['china_collaborations'])

        self.results['summary'] = {
            'total_italian_patents': total_patents,
            'china_collaborations': china_collabs,
            'collaboration_rate': (china_collabs / total_patents * 100) if total_patents > 0 else 0,
            'years_analyzed': list(self.results['by_year'].keys()),
            'top_technology_fields': sorted(
                [(tech, data['total']) for tech, data in self.results['by_technology'].items()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'top_inventors_count': len(self.results['key_inventors']),
            'top_assignees_count': len(self.results['key_assignees'])
        }

    def save_results(self):
        """Save analysis results"""

        # Save full results
        output_file = self.output_dir / "epo_italy_patents.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            # Convert defaultdicts to regular dicts for JSON serialization
            results_to_save = {
                'summary': self.results['summary'],
                'by_year': dict(self.results['by_year']),
                'by_technology': dict(self.results['by_technology']),
                'top_inventors': self.results.get('top_inventors', []),
                'top_assignees': self.results.get('top_assignees', []),
                'china_collaboration_count': len(self.results['china_collaborations'])
            }
            json.dump(results_to_save, f, indent=2)

        logger.info(f"Results saved to {output_file}")

        # Generate report
        self.generate_markdown_report()

    def generate_markdown_report(self):
        """Generate markdown report"""

        report = f"""# Italy EPO Patent Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d')}
**Data Source:** European Patent Office
**Focus:** Italian patents and China collaborations

## Executive Summary

- **Total Italian Patents:** {self.results['summary'].get('total_italian_patents', 0):,}
- **China Collaborations:** {self.results['summary'].get('china_collaborations', 0):,}
- **Collaboration Rate:** {self.results['summary'].get('collaboration_rate', 0):.1f}%
- **Unique Inventors:** {self.results['summary'].get('top_inventors_count', 0):,}
- **Unique Assignees:** {self.results['summary'].get('top_assignees_count', 0):,}

## Technology Fields

"""

        # Add technology field analysis
        for tech, count in self.results['summary'].get('top_technology_fields', []):
            tech_data = self.results['by_technology'].get(tech, {})
            china_rate = tech_data.get('china_rate', 0)
            report += f"- **{tech.upper()}**: {count} patents ({china_rate:.1f}% with China)\n"

        # Add yearly trends
        report += "\n## Patent Trends by Year\n\n"

        for year in sorted(self.results['by_year'].keys())[-5:]:  # Last 5 years
            data = self.results['by_year'][year]
            report += f"- **{year}**: {data['total']} patents, {data.get('china_collab', 0)} with China ({data.get('china_rate', 0):.1f}%)\n"

        # Add top assignees
        report += "\n## Top Italian Patent Assignees\n\n"

        for assignee, count in self.results.get('top_assignees', [])[:10]:
            report += f"- {assignee}: {count} patents\n"

        # Add top inventors
        report += "\n## Top Italian Inventors\n\n"

        for inventor, count in self.results.get('top_inventors', [])[:10]:
            report += f"- {inventor}: {count} patents\n"

        # Save report
        report_file = self.output_dir / "epo_italy_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"Report saved to {report_file}")

def main():
    """Run EPO patent analysis for Italy"""

    analyzer = EPOPatentAnalyzer()

    print("\n" + "="*60)
    print("EPO PATENT ANALYSIS - ITALY")
    print("="*60 + "\n")

    # Analyze patents
    analyzer.analyze_all_patents()
    analyzer.analyze_trends()
    analyzer.generate_summary()
    analyzer.save_results()

    # Print summary
    print("\nSummary:")
    for key, value in analyzer.results['summary'].items():
        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], tuple):
            print(f"  {key}:")
            for item in value[:5]:
                print(f"    - {item[0]}: {item[1]}")
        else:
            print(f"  {key}: {value}")

    print(f"\nResults saved to: artifacts/ITA/patent_analysis/")

if __name__ == "__main__":
    main()
