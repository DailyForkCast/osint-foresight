#!/usr/bin/env python3
"""
CORDIS Data Processing Pipeline
Extracts, validates, and analyzes CORDIS Horizon Europe data
"""

import json
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CORDISProcessor:
    """Process CORDIS Horizon Europe data."""

    def __init__(self, base_path: str = "C:/Projects/OSINT - Foresight/data/raw/source=cordis/horizon"):
        """Initialize with base data path."""
        self.base_path = Path(base_path)
        self.data = {
            'projects': {},
            'deliverables': {},
            'publications': {},
            'reports': {}
        }
        self.metadata = {
            'processing_date': datetime.now().strftime('%Y-%m-%d'),
            'accessed_date': '2025-09-14'
        }

    def extract_all(self) -> Dict[str, bool]:
        """Extract all CORDIS ZIP files."""
        extraction_status = {}

        datasets = {
            'projects': 'projects/cordis-HORIZONprojects-json.zip',
            'deliverables': 'deliverables/cordis-HORIZONdeliverables-json.zip',
            'publications': 'publications/cordis-HORIZONpublications-json.zip',
            'reports': 'report_summaries/cordis-HORIZONreports-json.zip'
        }

        for name, zip_path in datasets.items():
            full_path = self.base_path / zip_path
            extraction_status[name] = self.extract_dataset(full_path)

        return extraction_status

    def extract_dataset(self, zip_path: Path) -> bool:
        """Extract a single CORDIS dataset."""
        if not zip_path.exists():
            logger.warning(f"ZIP file not found: {zip_path}")
            return False

        try:
            extract_to = zip_path.parent
            logger.info(f"Extracting {zip_path.name} to {extract_to}")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)

            logger.info(f"Successfully extracted {zip_path.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to extract {zip_path}: {e}")
            return False

    def load_projects(self) -> Dict[str, Any]:
        """Load and structure project data."""
        projects_path = self.base_path / 'projects'

        # Core project data
        project_file = projects_path / 'project.json'
        if project_file.exists():
            with open(project_file, 'r', encoding='utf-8') as f:
                self.data['projects']['core'] = json.load(f)
                logger.info(f"Loaded {len(self.data['projects']['core'])} projects")

        # Organizations
        org_file = projects_path / 'organization.json'
        if org_file.exists():
            with open(org_file, 'r', encoding='utf-8') as f:
                self.data['projects']['organizations'] = json.load(f)
                logger.info(f"Loaded {len(self.data['projects']['organizations'])} organizations")

        # Additional files
        additional_files = [
            'euroSciVoc.json',
            'topics.json',
            'webLink.json',
            'legalBasis.json',
            'policyPriorities.json'
        ]

        for filename in additional_files:
            file_path = projects_path / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    key = filename.replace('.json', '')
                    self.data['projects'][key] = json.load(f)
                    logger.info(f"Loaded {filename}")

        return self.data['projects']

    def filter_slovakia(self) -> Dict[str, List[Any]]:
        """Filter all data for Slovak participation."""
        slovakia_data = {
            'projects': [],
            'organizations': [],
            'deliverables': [],
            'publications': [],
            'reports': []
        }

        # Filter projects with Slovak participation
        if 'core' in self.data['projects']:
            for project in self.data['projects']['core']:
                # Check if Slovakia in project countries
                if 'SK' in project.get('countries', []):
                    slovakia_data['projects'].append(project)

        logger.info(f"Found {len(slovakia_data['projects'])} projects with Slovak participation")

        # Get Slovak organizations
        if 'organizations' in self.data['projects']:
            for org in self.data['projects']['organizations']:
                if org.get('country') == 'SK':
                    slovakia_data['organizations'].append(org)

        logger.info(f"Found {len(slovakia_data['organizations'])} Slovak organizations")

        # Filter deliverables, publications, reports by Slovak projects
        slovak_project_ids = {p.get('id') for p in slovakia_data['projects']}

        # Add related deliverables
        if self.data.get('deliverables'):
            for deliverable in self.data['deliverables'].get('core', []):
                if deliverable.get('projectId') in slovak_project_ids:
                    slovakia_data['deliverables'].append(deliverable)

        # Add related publications
        if self.data.get('publications'):
            for publication in self.data['publications'].get('core', []):
                if publication.get('projectId') in slovak_project_ids:
                    slovakia_data['publications'].append(publication)

        return slovakia_data

    def analyze_slovakia(self, slovakia_data: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Analyze Slovak participation in Horizon Europe."""
        analysis = {
            'summary': {
                'total_projects': len(slovakia_data['projects']),
                'total_organizations': len(slovakia_data['organizations']),
                'total_deliverables': len(slovakia_data['deliverables']),
                'total_publications': len(slovakia_data['publications'])
            },
            'financial': {
                'total_eu_contribution': 0,
                'total_project_cost': 0,
                'average_contribution': 0
            },
            'temporal': {
                'projects_by_year': {},
                'active_projects': 0,
                'completed_projects': 0
            },
            'thematic': {
                'top_topics': {},
                'euroscivoc_categories': {}
            },
            'collaboration': {
                'top_partner_countries': {},
                'consortium_sizes': []
            },
            'organizations': {
                'top_participants': {},
                'coordinator_count': 0
            }
        }

        # Financial analysis
        for project in slovakia_data['projects']:
            ec_contribution = project.get('ecMaxContribution', 0)
            total_cost = project.get('totalCost', 0)

            analysis['financial']['total_eu_contribution'] += ec_contribution
            analysis['financial']['total_project_cost'] += total_cost

        if slovakia_data['projects']:
            analysis['financial']['average_contribution'] = (
                analysis['financial']['total_eu_contribution'] / len(slovakia_data['projects'])
            )

        # Temporal analysis
        current_date = datetime.strptime('2025-09-14', '%Y-%m-%d')

        for project in slovakia_data['projects']:
            # Extract start year
            start_date = project.get('startDate')
            if start_date:
                year = start_date[:4]
                analysis['temporal']['projects_by_year'][year] = (
                    analysis['temporal']['projects_by_year'].get(year, 0) + 1
                )

            # Check if active
            end_date = project.get('endDate')
            if end_date:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                if end_datetime > current_date:
                    analysis['temporal']['active_projects'] += 1
                else:
                    analysis['temporal']['completed_projects'] += 1

        # Partner country analysis
        for project in slovakia_data['projects']:
            countries = project.get('countries', [])
            analysis['collaboration']['consortium_sizes'].append(len(countries))

            for country in countries:
                if country != 'SK':
                    analysis['collaboration']['top_partner_countries'][country] = (
                        analysis['collaboration']['top_partner_countries'].get(country, 0) + 1
                    )

        # Sort top partner countries
        analysis['collaboration']['top_partner_countries'] = dict(
            sorted(
                analysis['collaboration']['top_partner_countries'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        )

        # Organization analysis
        for org in slovakia_data['organizations']:
            org_name = org.get('name', 'Unknown')
            analysis['organizations']['top_participants'][org_name] = (
                analysis['organizations']['top_participants'].get(org_name, 0) + 1
            )

            if org.get('role') == 'coordinator':
                analysis['organizations']['coordinator_count'] += 1

        return analysis

    def generate_report(self, slovakia_data: Dict, analysis: Dict) -> str:
        """Generate Slovakia CORDIS analysis report."""
        report = []
        report.append("# Slovakia Horizon Europe Participation Analysis")
        report.append(f"\n*Analysis Date: {self.metadata['processing_date']}*")
        report.append(f"*Data Accessed: {self.metadata['accessed_date']}*")
        report.append("\n## Executive Summary\n")

        # Summary statistics
        report.append(f"- **Total Projects with Slovak Participation**: {analysis['summary']['total_projects']}")
        report.append(f"- **Slovak Organizations Involved**: {analysis['summary']['total_organizations']}")
        report.append(f"- **Project Deliverables**: {analysis['summary']['total_deliverables']}")
        report.append(f"- **Scientific Publications**: {analysis['summary']['total_publications']}")

        # Financial overview
        report.append("\n## Financial Overview\n")
        report.append(f"- **Total EU Contribution**: €{analysis['financial']['total_eu_contribution']:,.2f}")
        report.append(f"- **Total Project Costs**: €{analysis['financial']['total_project_cost']:,.2f}")
        report.append(f"- **Average EU Contribution per Project**: €{analysis['financial']['average_contribution']:,.2f}")

        # Temporal distribution
        report.append("\n## Temporal Distribution\n")
        report.append(f"- **Active Projects**: {analysis['temporal']['active_projects']}")
        report.append(f"- **Completed Projects**: {analysis['temporal']['completed_projects']}")

        if analysis['temporal']['projects_by_year']:
            report.append("\n### Projects by Start Year:")
            for year, count in sorted(analysis['temporal']['projects_by_year'].items()):
                report.append(f"- {year}: {count} projects")

        # Collaboration patterns
        report.append("\n## International Collaboration\n")
        report.append("\n### Top Partner Countries:")
        for country, count in list(analysis['collaboration']['top_partner_countries'].items())[:10]:
            report.append(f"- {country}: {count} joint projects")

        if analysis['collaboration']['consortium_sizes']:
            avg_size = sum(analysis['collaboration']['consortium_sizes']) / len(analysis['collaboration']['consortium_sizes'])
            report.append(f"\n**Average Consortium Size**: {avg_size:.1f} countries")

        # Top organizations
        report.append("\n## Top Slovak Organizations\n")
        top_orgs = sorted(
            analysis['organizations']['top_participants'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        for org, count in top_orgs:
            report.append(f"- {org}: {count} projects")

        report.append(f"\n**Organizations as Coordinators**: {analysis['organizations']['coordinator_count']}")

        # Key projects (examples)
        report.append("\n## Example Projects\n")
        for project in slovakia_data['projects'][:5]:
            report.append(f"\n### {project.get('acronym', 'N/A')}")
            report.append(f"- **Title**: {project.get('title', 'N/A')}")
            report.append(f"- **Grant Agreement**: {project.get('id', 'N/A')}")
            report.append(f"- **EU Contribution**: €{project.get('ecMaxContribution', 0):,.2f}")
            report.append(f"- **Duration**: {project.get('startDate', 'N/A')} to {project.get('endDate', 'N/A')}")

        # Data citation
        report.append("\n## Citation\n")
        report.append("```")
        report.append("European Commission. (2025). CORDIS - EU research projects under Horizon Europe (2021-2027).")
        report.append("Retrieved 2025-09-14, from https://cordis.europa.eu/data/")
        report.append("```")

        return "\n".join(report)

    def save_slovakia_data(self, slovakia_data: Dict, analysis: Dict):
        """Save Slovak-specific data and analysis."""
        output_path = Path("C:/Projects/OSINT - Foresight/data/processed/slovakia_cordis")
        output_path.mkdir(parents=True, exist_ok=True)

        # Save filtered data
        with open(output_path / 'slovakia_projects.json', 'w', encoding='utf-8') as f:
            json.dump(slovakia_data['projects'], f, indent=2, ensure_ascii=False)

        with open(output_path / 'slovakia_organizations.json', 'w', encoding='utf-8') as f:
            json.dump(slovakia_data['organizations'], f, indent=2, ensure_ascii=False)

        # Save analysis
        with open(output_path / 'slovakia_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        # Save report
        report = self.generate_report(slovakia_data, analysis)
        with open(output_path / 'SLOVAKIA_CORDIS_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"Saved Slovakia CORDIS data to {output_path}")


def main():
    """Main processing function."""
    processor = CORDISProcessor()

    print("\n[1] Extracting CORDIS datasets...")
    extraction_status = processor.extract_all()
    print(f"    Extraction status: {extraction_status}")

    print("\n[2] Loading project data...")
    processor.load_projects()

    print("\n[3] Filtering for Slovakia...")
    slovakia_data = processor.filter_slovakia()

    print("\n[4] Analyzing Slovak participation...")
    analysis = processor.analyze_slovakia(slovakia_data)

    print("\n[5] Generating report...")
    report = processor.generate_report(slovakia_data, analysis)

    print("\n[6] Saving results...")
    processor.save_slovakia_data(slovakia_data, analysis)

    print("\n[COMPLETE] Slovakia CORDIS analysis complete!")
    print(f"  - Projects: {len(slovakia_data['projects'])}")
    print(f"  - Organizations: {len(slovakia_data['organizations'])}")
    print(f"  - Total EU funding: €{analysis['financial']['total_eu_contribution']:,.2f}")


if __name__ == "__main__":
    main()
