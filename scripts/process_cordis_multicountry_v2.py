#!/usr/bin/env python3
"""
CORDIS Multi-Country China Collaboration Analyzer V2
Properly joins project and organization data
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple

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
    'UK': 'United Kingdom', 'GB': 'United Kingdom',

    # EU Candidates & Balkans
    'AL': 'Albania', 'MK': 'North Macedonia', 'RS': 'Serbia',
    'ME': 'Montenegro', 'BA': 'Bosnia and Herzegovina', 'TR': 'Turkey',
    'UA': 'Ukraine', 'XK': 'Kosovo',

    # European Strategic
    'GE': 'Georgia', 'AM': 'Armenia', 'FO': 'Faroe Islands', 'GL': 'Greenland',

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

class CORDISMultiCountryAnalyzerV2:
    def __init__(self, base_path: str = "data/raw/source=cordis"):
        self.base_path = Path(base_path)
        self.results = defaultdict(lambda: {
            'total_projects': 0,
            'china_collaborations': 0,
            'projects_with_china': [],
            'funding_to_china_projects': 0.0,
            'ec_contribution_china_projects': 0.0,
            'technology_areas': defaultdict(int),
            'chinese_organizations': defaultdict(int),  # Count frequency
            'collaboration_years': defaultdict(int),
            'funding_schemes': defaultdict(int)
        })
        self.all_china_projects = set()

    def load_json_file(self, filepath: Path) -> List[Dict]:
        """Load and parse JSON file with error handling"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    # Handle wrapped structure
                    if len(data) == 1:
                        key = list(data.keys())[0]
                        if isinstance(data[key], list):
                            return data[key]
                    return [data]
                return []
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return []

    def process_program(self, program: str) -> Dict:
        """Process all projects and organizations from a program"""
        program_path = self.base_path / program / "projects"

        # Load projects
        project_file = program_path / "project.json"
        if not project_file.exists():
            print(f"Warning: {project_file} not found")
            return {}

        print(f"\nProcessing {program.upper()}...")
        projects = self.load_json_file(project_file)
        print(f"  Loaded {len(projects)} projects")

        # Load organizations
        org_file = program_path / "organization.json"
        organizations = self.load_json_file(org_file)
        print(f"  Loaded {len(organizations)} organization records")

        # Create project lookup
        project_dict = {p['id']: p for p in projects if isinstance(p, dict) and 'id' in p}

        # Group organizations by project
        project_orgs = defaultdict(list)
        for org in organizations:
            if isinstance(org, dict) and 'projectID' in org:
                project_orgs[org['projectID']].append(org)

        print(f"  Matched organizations to {len(project_orgs)} projects")

        # Analysis counters
        china_project_count = 0
        total_projects_analyzed = 0

        # Process each project
        for project_id, project in project_dict.items():
            orgs = project_orgs.get(project_id, [])
            if not orgs:
                continue

            total_projects_analyzed += 1

            # Get all countries in project
            countries = set()
            chinese_orgs = []

            for org in orgs:
                country = org.get('country', '').upper()
                if country:
                    countries.add(country)

                    # Track Chinese organizations
                    if country == 'CN':
                        org_name = org.get('name', 'Unknown')
                        chinese_orgs.append({
                            'name': org_name,
                            'city': org.get('city', ''),
                            'contribution': org.get('ecContribution', 0)
                        })

            # Update country statistics
            for country_code in countries:
                if country_code in COUNTRY_CODES and country_code != 'CN':
                    self.results[country_code]['total_projects'] += 1

            # Check for China collaboration
            if 'CN' in countries and len(countries) > 1:  # China plus at least one other country
                china_project_count += 1
                self.all_china_projects.add(project_id)

                # Create project info
                project_info = {
                    'id': project_id,
                    'acronym': project.get('acronym', ''),
                    'title': project.get('title', 'Unknown'),
                    'total_cost': project.get('totalCost', 0),
                    'ec_contribution': project.get('ecMaxContribution', 0),
                    'start_date': project.get('startDate', ''),
                    'end_date': project.get('endDate', ''),
                    'funding_scheme': project.get('fundingScheme', ''),
                    'topics': project.get('topics', []),
                    'chinese_orgs': chinese_orgs,
                    'partner_countries': list(countries),
                    'programme': program.upper()
                }

                # Update results for each non-China country
                for country_code in countries:
                    if country_code in COUNTRY_CODES and country_code != 'CN':
                        country_data = self.results[country_code]
                        country_data['china_collaborations'] += 1
                        country_data['projects_with_china'].append(project_info)

                        # Financial tracking
                        country_data['funding_to_china_projects'] += float(project.get('totalCost', 0))
                        country_data['ec_contribution_china_projects'] += float(project.get('ecMaxContribution', 0))

                        # Track Chinese organizations with frequency
                        for cn_org in chinese_orgs:
                            country_data['chinese_organizations'][cn_org['name']] += 1

                        # Track collaboration years
                        start_date = project.get('startDate', '')
                        if start_date and len(start_date) >= 4:
                            year = start_date[:4]
                            if year.isdigit():
                                country_data['collaboration_years'][year] += 1

                        # Track technology areas
                        topics = project.get('topics', [])
                        if isinstance(topics, list):
                            for topic in topics:
                                if isinstance(topic, str):
                                    country_data['technology_areas'][topic] += 1

                        # Track funding schemes
                        funding_scheme = project.get('fundingScheme', '')
                        if funding_scheme:
                            country_data['funding_schemes'][funding_scheme] += 1

        print(f"  Found {china_project_count} projects with China collaboration")
        print(f"  Total projects with organizations: {total_projects_analyzed}")

        return {
            'total_projects': len(projects),
            'projects_with_orgs': total_projects_analyzed,
            'china_projects': china_project_count
        }

    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        report = f"""# CORDIS Multi-Country China Collaboration Analysis
Generated: {timestamp}
Data Sources: H2020 and Horizon Europe

## Executive Summary

Total unique projects with China: {len(self.all_china_projects)}
Countries analyzed: {len(COUNTRY_CODES) - 1} (excluding China)
Countries with China collaborations: {sum(1 for c in self.results.values() if c['china_collaborations'] > 0)}

## Country Rankings by China Collaborations

| Rank | Country | China Projects | Total Projects | Collaboration Rate | EC Contribution (€M) | Avg Project Value (€M) |
|------|---------|---------------|----------------|-------------------|---------------------|----------------------|
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
                avg_value = data['funding_to_china_projects'] / data['china_collaborations'] / 1_000_000 if data['china_collaborations'] > 0 else 0

                report += f"| {rank} | {country_name} ({country_code}) | "
                report += f"{data['china_collaborations']} | "
                report += f"{data['total_projects']} | "
                report += f"{collab_rate:.2f}% | "
                report += f"{data['ec_contribution_china_projects']/1_000_000:.1f} | "
                report += f"{avg_value:.1f} |\n"
                rank += 1

        # Technology focus analysis
        report += "\n## Technology Focus Areas (Top 20)\n\n"
        all_topics = defaultdict(int)
        for data in self.results.values():
            for topic, count in data['technology_areas'].items():
                all_topics[topic] += count

        report += "| Topic | Project Count |\n|-------|-------------|\n"
        for topic, count in sorted(all_topics.items(), key=lambda x: x[1], reverse=True)[:20]:
            report += f"| {topic} | {count} |\n"

        # Top Chinese organizations
        report += "\n## Top Chinese Partner Organizations\n\n"
        all_chinese_orgs = defaultdict(int)
        for data in self.results.values():
            for org, count in data['chinese_organizations'].items():
                all_chinese_orgs[org] += count

        report += "| Organization | Collaboration Count |\n|--------------|-------------------|\n"
        for org, count in sorted(all_chinese_orgs.items(), key=lambda x: x[1], reverse=True)[:20]:
            report += f"| {org} | {count} |\n"

        # Temporal analysis
        report += "\n## Temporal Distribution\n\n"
        all_years = defaultdict(int)
        for data in self.results.values():
            for year, count in data['collaboration_years'].items():
                all_years[year] += count

        report += "| Year | Projects Started |\n|------|----------------|\n"
        for year in sorted(all_years.keys()):
            report += f"| {year} | {all_years[year]} |\n"

        # Detailed country sections for top collaborators
        report += "\n## Detailed Country Analysis (Top 15)\n\n"

        for country_code, data in sorted_countries[:15]:
            if data['china_collaborations'] > 0:
                country_name = COUNTRY_CODES.get(country_code, country_code)
                report += f"### {country_name} ({country_code})\n\n"
                report += f"**Summary Statistics:**\n"
                report += f"- Total China collaborations: {data['china_collaborations']}\n"
                report += f"- Collaboration rate: {(data['china_collaborations']/data['total_projects']*100):.2f}%\n"
                report += f"- Unique Chinese partners: {len(data['chinese_organizations'])}\n"
                report += f"- Total project value: €{data['funding_to_china_projects']:,.0f}\n"
                report += f"- EC contribution: €{data['ec_contribution_china_projects']:,.0f}\n\n"

                # Top Chinese partners for this country
                if data['chinese_organizations']:
                    report += f"**Top 5 Chinese Partners:**\n"
                    for org, count in sorted(data['chinese_organizations'].items(), key=lambda x: x[1], reverse=True)[:5]:
                        report += f"- {org}: {count} projects\n"
                    report += "\n"

                # Top technology areas for this country
                if data['technology_areas']:
                    report += f"**Top 5 Technology Areas:**\n"
                    for area, count in sorted(data['technology_areas'].items(), key=lambda x: x[1], reverse=True)[:5]:
                        report += f"- {area}: {count} projects\n"
                    report += "\n"

                report += "---\n\n"

        # Countries with no China collaboration
        no_collab = [COUNTRY_CODES[c] + f" ({c})" for c in COUNTRY_CODES
                     if c != 'CN' and (c not in self.results or self.results[c]['china_collaborations'] == 0)]
        if no_collab:
            report += f"\n## Countries with No Identified China Collaborations\n\n"
            report += ", ".join(sorted(no_collab))
            report += "\n\n*Note: This may indicate either no collaborations or incomplete data matching.*\n"

        return report

    def save_results(self):
        """Save analysis results"""
        output_dir = Path("data/processed/cordis_multicountry")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save detailed JSON results
        json_output = {
            'metadata': {
                'generated': timestamp,
                'total_china_projects': len(self.all_china_projects),
                'countries_analyzed': len(COUNTRY_CODES) - 1
            },
            'countries': {}
        }

        for country_code, data in self.results.items():
            json_output['countries'][country_code] = {
                'country_name': COUNTRY_CODES.get(country_code, country_code),
                'total_projects': data['total_projects'],
                'china_collaborations': data['china_collaborations'],
                'collaboration_rate': (data['china_collaborations'] / data['total_projects'] * 100) if data['total_projects'] > 0 else 0,
                'funding_total': data['funding_to_china_projects'],
                'ec_contribution': data['ec_contribution_china_projects'],
                'unique_chinese_orgs': len(data['chinese_organizations']),
                'chinese_organizations': dict(sorted(data['chinese_organizations'].items(), key=lambda x: x[1], reverse=True)),
                'collaboration_years': dict(data['collaboration_years']),
                'technology_areas': dict(sorted(data['technology_areas'].items(), key=lambda x: x[1], reverse=True)[:20]),
                'funding_schemes': dict(data['funding_schemes']),
                'sample_projects': data['projects_with_china'][:5]  # Save first 5 as examples
            }

        json_file = output_dir / f"cordis_china_collaborations_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=2, ensure_ascii=False)

        # Save report
        report = self.generate_report()
        report_file = output_dir / f"CORDIS_MULTICOUNTRY_ANALYSIS_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        # Save project list for verification
        project_list = []
        for data in self.results.values():
            for project in data['projects_with_china']:
                project_list.append({
                    'id': project['id'],
                    'acronym': project['acronym'],
                    'title': project['title'],
                    'chinese_orgs': [org['name'] for org in project['chinese_orgs']],
                    'countries': project['partner_countries']
                })

        # Remove duplicates
        seen = set()
        unique_projects = []
        for p in project_list:
            if p['id'] not in seen:
                seen.add(p['id'])
                unique_projects.append(p)

        project_file = output_dir / f"china_project_list_{timestamp}.json"
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(unique_projects, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to:")
        print(f"  - {json_file}")
        print(f"  - {report_file}")
        print(f"  - {project_file}")

    def run(self):
        """Run the complete analysis"""
        print("=" * 60)
        print("CORDIS Multi-Country China Collaboration Analysis V2")
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

        print(f"\nTotal unique projects with China: {len(self.all_china_projects)}")

        total_with_china = sum(1 for c in self.results.values() if c['china_collaborations'] > 0)
        print(f"Countries with China collaborations: {total_with_china}/{len(COUNTRY_CODES)-1}")

        # Top 5 collaborators
        print("\nTop 5 Countries by China Collaborations:")
        sorted_countries = sorted(
            [(code, data) for code, data in self.results.items()],
            key=lambda x: x[1]['china_collaborations'],
            reverse=True
        )

        for i, (country_code, data) in enumerate(sorted_countries[:5], 1):
            country_name = COUNTRY_CODES.get(country_code, country_code)
            rate = (data['china_collaborations']/data['total_projects']*100) if data['total_projects'] > 0 else 0
            print(f"{i}. {country_name}: {data['china_collaborations']} projects ({rate:.1f}% of {data['total_projects']} total)")

if __name__ == "__main__":
    analyzer = CORDISMultiCountryAnalyzerV2()
    analyzer.run()
