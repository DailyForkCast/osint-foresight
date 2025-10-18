#!/usr/bin/env python3
"""
CORDIS Multi-Country China Collaboration Analyzer
Processes H2020 and Horizon Europe data to identify China collaborations
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import re

# Country codes mapping
COUNTRY_CODES = {
    # EU Core & Associated
    'DE': 'Germany', 'FR': 'France', 'IT': 'Italy', 'ES': 'Spain',
    'NL': 'Netherlands', 'BE': 'Belgium', 'LU': 'Luxembourg',
    'SE': 'Sweden', 'DK': 'Denmark', 'FI': 'Finland', 'NO': 'Norway',
    'IS': 'Iceland', 'PL': 'Poland', 'CZ': 'Czech Republic',
    'SK': 'Slovakia', 'HU': 'Hungary', 'RO': 'Romania', 'BG': 'Bulgaria',
    'HR': 'Croatia', 'SI': 'Slovenia', 'EE': 'Estonia', 'LV': 'Latvia',
    'LT': 'Lithuania', 'GR': 'Greece', 'CY': 'Cyprus', 'MT': 'Malta',
    'PT': 'Portugal', 'AT': 'Austria', 'IE': 'Ireland', 'CH': 'Switzerland',
    'UK': 'United Kingdom', 'GB': 'United Kingdom',  # Both UK and GB codes

    # EU Candidates & Balkans
    'AL': 'Albania', 'MK': 'North Macedonia', 'RS': 'Serbia',
    'ME': 'Montenegro', 'BA': 'Bosnia and Herzegovina', 'TR': 'Turkey',
    'UA': 'Ukraine', 'XK': 'Kosovo',

    # Global Partners
    'US': 'United States', 'CA': 'Canada', 'AU': 'Australia',
    'NZ': 'New Zealand', 'JP': 'Japan', 'KR': 'South Korea',
    'SG': 'Singapore', 'TW': 'Taiwan', 'IN': 'India', 'TH': 'Thailand',
    'MY': 'Malaysia', 'VN': 'Vietnam', 'IL': 'Israel', 'AE': 'United Arab Emirates',
    'SA': 'Saudi Arabia', 'BR': 'Brazil', 'MX': 'Mexico', 'AR': 'Argentina',
    'CL': 'Chile', 'ZA': 'South Africa', 'EG': 'Egypt', 'KE': 'Kenya',
    'NG': 'Nigeria', 'RU': 'Russia', 'BY': 'Belarus', 'KZ': 'Kazakhstan',

    # Target country
    'CN': 'China'
}

class CORDISMultiCountryAnalyzer:
    def __init__(self, base_path: str = "data/raw/source=cordis"):
        self.base_path = Path(base_path)
        self.results = defaultdict(lambda: {
            'total_projects': 0,
            'china_collaborations': 0,
            'projects_with_china': [],
            'funding_to_china_projects': 0.0,
            'technology_areas': defaultdict(int),
            'chinese_organizations': set(),
            'collaboration_years': defaultdict(int)
        })

    def load_json_file(self, filepath: Path) -> List[Dict]:
        """Load and parse JSON file with error handling"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    # Handle wrapped JSON structure
                    if 'project' in data:
                        return data['project']
                    return [data]
                return data if isinstance(data, list) else [data]
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return []

    def extract_countries_from_project(self, project: Dict) -> Set[str]:
        """Extract all country codes from a project"""
        countries = set()

        # Check organizations
        if 'organizations' in project:
            orgs = project['organizations']
            if isinstance(orgs, dict):
                orgs = [orgs]
            for org in orgs:
                if isinstance(org, dict):
                    # Check country field
                    if 'country' in org:
                        country = org['country']
                        if isinstance(country, str):
                            countries.add(country.upper())
                    # Check address
                    if 'address' in org and isinstance(org['address'], dict):
                        if 'country' in org['address']:
                            countries.add(org['address']['country'].upper())

        # Check coordinator country
        if 'coordinatorCountry' in project:
            countries.add(project['coordinatorCountry'].upper())

        return countries

    def identify_chinese_organizations(self, project: Dict) -> List[str]:
        """Identify Chinese organizations in a project"""
        chinese_orgs = []

        if 'organizations' in project:
            orgs = project['organizations']
            if isinstance(orgs, dict):
                orgs = [orgs]

            for org in orgs:
                if isinstance(org, dict):
                    is_chinese = False

                    # Check if organization is from China
                    if 'country' in org and org['country'].upper() == 'CN':
                        is_chinese = True
                    elif 'address' in org and isinstance(org['address'], dict):
                        if 'country' in org['address'] and org['address']['country'].upper() == 'CN':
                            is_chinese = True

                    if is_chinese:
                        org_name = org.get('name', 'Unknown')
                        chinese_orgs.append(org_name)

        return chinese_orgs

    def process_program(self, program: str) -> Dict:
        """Process all projects from a program (h2020 or horizon)"""
        program_path = self.base_path / program / "projects"
        project_file = program_path / "project.json"

        if not project_file.exists():
            print(f"Warning: {project_file} not found")
            return {}

        print(f"\nProcessing {program.upper()} projects...")
        projects = self.load_json_file(project_file)

        program_stats = {
            'total_projects': len(projects),
            'countries_with_china': defaultdict(int),
            'china_only_projects': 0
        }

        for project in projects:
            if not isinstance(project, dict):
                continue

            countries = self.extract_countries_from_project(project)

            # Track all country participation
            for country_code in countries:
                if country_code in COUNTRY_CODES and country_code != 'CN':
                    self.results[country_code]['total_projects'] += 1

            # Check for China collaboration
            if 'CN' in countries:
                chinese_orgs = self.identify_chinese_organizations(project)

                # Extract project details
                project_info = {
                    'id': project.get('id', 'Unknown'),
                    'title': project.get('title', 'Unknown'),
                    'acronym': project.get('acronym', ''),
                    'funding': project.get('totalCost', 0),
                    'start_date': project.get('startDate', ''),
                    'chinese_orgs': chinese_orgs,
                    'topics': project.get('topics', []),
                    'programme': program.upper()
                }

                # Update results for each country collaborating with China
                for country_code in countries:
                    if country_code in COUNTRY_CODES and country_code != 'CN':
                        country_data = self.results[country_code]
                        country_data['china_collaborations'] += 1
                        country_data['projects_with_china'].append(project_info)
                        country_data['funding_to_china_projects'] += float(project.get('totalCost', 0))

                        # Track Chinese organizations
                        for org in chinese_orgs:
                            country_data['chinese_organizations'].add(org)

                        # Track collaboration years
                        start_date = project.get('startDate', '')
                        if start_date:
                            year = start_date[:4]
                            if year.isdigit():
                                country_data['collaboration_years'][year] += 1

                        # Track technology areas
                        if 'topics' in project:
                            topics = project['topics']
                            if isinstance(topics, list):
                                for topic in topics:
                                    if isinstance(topic, str):
                                        country_data['technology_areas'][topic] += 1

                        program_stats['countries_with_china'][country_code] += 1

                # Check if only China (no EU partners)
                if countries == {'CN'}:
                    program_stats['china_only_projects'] += 1

        return program_stats

    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        report = f"""# CORDIS Multi-Country China Collaboration Analysis
Generated: {timestamp}
Data Sources: H2020 and Horizon Europe

## Executive Summary

Total countries analyzed: {len(COUNTRY_CODES) - 1} (excluding China)
Countries with China collaborations: {sum(1 for c in self.results.values() if c['china_collaborations'] > 0)}

## Country Rankings by China Collaborations

| Rank | Country | China Projects | Total Projects | Collaboration Rate | Total Funding (€) |
|------|---------|---------------|----------------|-------------------|------------------|
"""

        # Sort countries by number of China collaborations
        sorted_countries = sorted(
            [(code, data) for code, data in self.results.items()],
            key=lambda x: x[1]['china_collaborations'],
            reverse=True
        )

        rank = 1
        for country_code, data in sorted_countries:
            if data['china_collaborations'] > 0:
                country_name = COUNTRY_CODES.get(country_code, country_code)
                collab_rate = (data['china_collaborations'] / data['total_projects'] * 100) if data['total_projects'] > 0 else 0

                report += f"| {rank} | {country_name} ({country_code}) | "
                report += f"{data['china_collaborations']} | "
                report += f"{data['total_projects']} | "
                report += f"{collab_rate:.2f}% | "
                report += f"€{data['funding_to_china_projects']:,.0f} |\n"
                rank += 1

        # Add detailed country sections for top collaborators
        report += "\n## Detailed Country Analysis\n\n"

        for country_code, data in sorted_countries[:10]:  # Top 10 countries
            if data['china_collaborations'] > 0:
                country_name = COUNTRY_CODES.get(country_code, country_code)
                report += f"### {country_name} ({country_code})\n\n"
                report += f"- **Total China collaborations**: {data['china_collaborations']}\n"
                report += f"- **Unique Chinese organizations**: {len(data['chinese_organizations'])}\n"
                report += f"- **Total funding to China projects**: €{data['funding_to_china_projects']:,.0f}\n"

                # Year distribution
                report += f"\n**Collaboration Timeline**:\n"
                for year in sorted(data['collaboration_years'].keys()):
                    report += f"- {year}: {data['collaboration_years'][year]} projects\n"

                # Top technology areas
                report += f"\n**Top Technology Areas**:\n"
                top_areas = sorted(data['technology_areas'].items(), key=lambda x: x[1], reverse=True)[:5]
                for area, count in top_areas:
                    report += f"- {area}: {count} projects\n"

                # Top Chinese partners
                report += f"\n**Top Chinese Partners**:\n"
                for org in list(data['chinese_organizations'])[:5]:
                    report += f"- {org}\n"

                report += "\n---\n\n"

        # Countries with no China collaboration
        no_collab = [COUNTRY_CODES[c] for c in COUNTRY_CODES if c != 'CN' and c not in self.results or self.results[c]['china_collaborations'] == 0]
        if no_collab:
            report += f"\n## Countries with No China Collaborations\n\n"
            report += ", ".join(sorted(no_collab))
            report += "\n"

        return report

    def save_results(self):
        """Save analysis results"""
        output_dir = Path("data/processed/cordis_multicountry")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save detailed JSON results
        json_output = {}
        for country_code, data in self.results.items():
            json_output[country_code] = {
                'country_name': COUNTRY_CODES.get(country_code, country_code),
                'total_projects': data['total_projects'],
                'china_collaborations': data['china_collaborations'],
                'collaboration_rate': (data['china_collaborations'] / data['total_projects'] * 100) if data['total_projects'] > 0 else 0,
                'funding_to_china_projects': data['funding_to_china_projects'],
                'unique_chinese_orgs': len(data['chinese_organizations']),
                'chinese_organizations': list(data['chinese_organizations']),
                'collaboration_years': dict(data['collaboration_years']),
                'technology_areas': dict(data['technology_areas']),
                'project_count': len(data['projects_with_china'])
            }

        with open(output_dir / f"cordis_china_collaborations_{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
            json.dump(json_output, f, indent=2)

        # Save report
        report = self.generate_report()
        with open(output_dir / f"CORDIS_MULTICOUNTRY_ANALYSIS_{datetime.now().strftime('%Y%m%d')}.md", 'w') as f:
            f.write(report)

        print(f"\nResults saved to {output_dir}")

    def run(self):
        """Run the complete analysis"""
        print("=" * 60)
        print("CORDIS Multi-Country China Collaboration Analysis")
        print("=" * 60)

        # Process H2020
        h2020_stats = self.process_program("h2020")

        # Process Horizon Europe
        horizon_stats = self.process_program("horizon")

        # Generate and save results
        self.save_results()

        # Print summary
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)

        total_with_china = sum(1 for c in self.results.values() if c['china_collaborations'] > 0)
        print(f"\nCountries with China collaborations: {total_with_china}/{len(COUNTRY_CODES)-1}")

        # Top 5 collaborators
        print("\nTop 5 Countries by China Collaborations:")
        sorted_countries = sorted(
            [(code, data) for code, data in self.results.items()],
            key=lambda x: x[1]['china_collaborations'],
            reverse=True
        )

        for i, (country_code, data) in enumerate(sorted_countries[:5], 1):
            country_name = COUNTRY_CODES.get(country_code, country_code)
            print(f"{i}. {country_name}: {data['china_collaborations']} projects")

if __name__ == "__main__":
    analyzer = CORDISMultiCountryAnalyzer()
    analyzer.run()
