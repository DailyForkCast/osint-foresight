#!/usr/bin/env python3
"""
Detailed collaboration analysis for Greece, Albania, and Kosovo
Checking for any missed China collaborations and mapping their networks
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class SpecificCountryAnalyzer:
    def __init__(self, base_path: str = "data/raw/source=cordis"):
        self.base_path = Path(base_path)
        self.target_countries = {
            'GR': 'Greece',
            'EL': 'Greece',  # Alternative code for Greece
            'AL': 'Albania',
            'XK': 'Kosovo',
            'KS': 'Kosovo'   # Alternative code for Kosovo
        }
        self.results = defaultdict(lambda: {
            'total_projects': 0,
            'projects_by_year': defaultdict(int),
            'partner_countries': defaultdict(int),
            'china_projects': [],
            'all_projects': [],
            'organizations': defaultdict(int),
            'funding_total': 0.0,
            'ec_contribution': 0.0,
            'topics': defaultdict(int),
            'coordinators': 0,
            'participants': 0
        })

    def load_json_file(self, filepath: Path) -> List[Dict]:
        """Load and parse JSON file with error handling"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return []

    def analyze_program(self, program: str):
        """Analyze collaboration patterns for target countries"""
        program_path = self.base_path / program / "projects"

        # Load projects
        project_file = program_path / "project.json"
        if not project_file.exists():
            print(f"Warning: {project_file} not found")
            return

        print(f"\nAnalyzing {program.upper()}...")
        projects = self.load_json_file(project_file)

        # Load organizations
        org_file = program_path / "organization.json"
        organizations = self.load_json_file(org_file)

        # Create project lookup
        project_dict = {p['id']: p for p in projects if isinstance(p, dict) and 'id' in p}

        # Group organizations by project
        project_orgs = defaultdict(list)
        for org in organizations:
            if isinstance(org, dict) and 'projectID' in org:
                project_orgs[org['projectID']].append(org)

        print(f"  Processing {len(project_orgs)} projects with organizations...")

        # Analyze each project
        for project_id, project in project_dict.items():
            orgs = project_orgs.get(project_id, [])
            if not orgs:
                continue

            # Get all countries and organizations in project
            countries = set()
            org_names_by_country = defaultdict(list)
            project_orgs_info = []

            for org in orgs:
                country = org.get('country', '').upper()
                if country:
                    countries.add(country)
                    org_name = org.get('name', 'Unknown')
                    org_names_by_country[country].append({
                        'name': org_name,
                        'role': org.get('role', 'participant'),
                        'contribution': org.get('ecContribution', 0)
                    })
                    project_orgs_info.append({
                        'name': org_name,
                        'country': country,
                        'city': org.get('city', ''),
                        'role': org.get('role', ''),
                        'contribution': org.get('ecContribution', 0)
                    })

            # Check if any target country is involved
            target_involved = []
            for country_code, country_name in self.target_countries.items():
                if country_code in countries:
                    target_involved.append(country_code)

            if not target_involved:
                continue

            # Project details
            project_info = {
                'id': project_id,
                'acronym': project.get('acronym', ''),
                'title': project.get('title', ''),
                'total_cost': project.get('totalCost', 0),
                'ec_contribution': project.get('ecMaxContribution', 0),
                'start_date': project.get('startDate', ''),
                'end_date': project.get('endDate', ''),
                'topics': project.get('topics', []),
                'countries': list(countries),
                'organizations': project_orgs_info,
                'programme': program.upper()
            }

            # Process for each involved target country
            for target_code in target_involved:
                # Map to standard code
                standard_code = 'GR' if target_code in ['GR', 'EL'] else target_code
                country_data = self.results[standard_code]

                country_data['total_projects'] += 1
                country_data['all_projects'].append(project_info)

                # Check coordinator
                coord_country = project.get('coordinatorCountry', '').upper()
                if coord_country == target_code:
                    country_data['coordinators'] += 1
                else:
                    country_data['participants'] += 1

                # Financial tracking
                country_data['funding_total'] += float(project.get('totalCost', 0))
                country_data['ec_contribution'] += float(project.get('ecMaxContribution', 0))

                # Year tracking
                start_date = project.get('startDate', '')
                if start_date and len(start_date) >= 4:
                    year = start_date[:4]
                    if year.isdigit():
                        country_data['projects_by_year'][year] += 1

                # Partner countries
                for partner_country in countries:
                    if partner_country not in [target_code, 'GR', 'EL', 'AL', 'XK', 'KS']:
                        country_data['partner_countries'][partner_country] += 1

                        # Special check for China
                        if partner_country == 'CN':
                            country_data['china_projects'].append(project_info)
                            print(f"    *** FOUND CHINA COLLABORATION: {standard_code} in project {project_id} ({project.get('acronym', '')})")

                # Organizations from target country
                for org_info in org_names_by_country.get(target_code, []):
                    country_data['organizations'][org_info['name']] += 1

                # Topics
                topics = project.get('topics', [])
                if isinstance(topics, list):
                    for topic in topics:
                        if isinstance(topic, str):
                            country_data['topics'][topic] += 1

    def generate_report(self) -> str:
        """Generate detailed report for target countries"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        report = f"""# Detailed Collaboration Analysis: Greece, Albania, Kosovo
Generated: {timestamp}
Data Sources: H2020 and Horizon Europe

## Executive Summary

Analyzing potential missed China collaborations and collaboration patterns.

"""

        for country_code in ['GR', 'AL', 'XK']:
            if country_code not in self.results:
                report += f"\n### {self.target_countries[country_code]} ({country_code})\n"
                report += "**NO DATA FOUND** - Country may not have participated in H2020/Horizon Europe\n\n"
                continue

            data = self.results[country_code]
            country_name = self.target_countries[country_code]

            report += f"\n## {country_name} ({country_code})\n\n"

            # China collaboration check
            if data['china_projects']:
                report += f"### *** CHINA COLLABORATIONS FOUND: {len(data['china_projects'])} ***\n\n"
                for proj in data['china_projects']:
                    report += f"- **{proj['acronym']}** ({proj['id']}): {proj['title']}\n"
                    total_cost = proj.get('total_cost', 0)
                    if isinstance(total_cost, str):
                        total_cost = float(total_cost) if total_cost.isdigit() else 0
                    report += f"  - Start: {proj['start_date']}, Total Cost: €{total_cost:,.0f}\n"
                    report += f"  - Countries: {', '.join(proj['countries'])}\n\n"
            else:
                report += "### No China Collaborations Found\n\n"

            # Overall statistics
            report += f"""### Overall Statistics
- **Total Projects**: {data['total_projects']}
- **As Coordinator**: {data['coordinators']} ({data['coordinators']/data['total_projects']*100:.1f}%)
- **As Participant**: {data['participants']} ({data['participants']/data['total_projects']*100:.1f}%)
- **Total Funding**: €{data['funding_total']:,.0f}
- **EC Contribution**: €{data['ec_contribution']:,.0f}
- **Unique Partner Countries**: {len(data['partner_countries'])}
- **Unique Organizations**: {len(data['organizations'])}

### Top 20 Partner Countries
| Country | Joint Projects |
|---------|---------------|
"""

            # Sort partner countries by collaboration count
            sorted_partners = sorted(data['partner_countries'].items(), key=lambda x: x[1], reverse=True)[:20]
            for partner_code, count in sorted_partners:
                # Check if it's China
                if partner_code == 'CN':
                    report += f"| **CHINA ({partner_code})** *** | **{count}** |\n"
                else:
                    partner_name = self.get_country_name(partner_code)
                    report += f"| {partner_name} ({partner_code}) | {count} |\n"

            # Top organizations
            report += f"\n### Top 10 {country_name} Organizations\n"
            report += "| Organization | Projects |\n|--------------|----------|\n"

            sorted_orgs = sorted(data['organizations'].items(), key=lambda x: x[1], reverse=True)[:10]
            for org_name, count in sorted_orgs:
                report += f"| {org_name} | {count} |\n"

            # Temporal distribution
            report += f"\n### Projects by Year\n"
            report += "| Year | Projects Started |\n|------|------------------|\n"

            for year in sorted(data['projects_by_year'].keys()):
                report += f"| {year} | {data['projects_by_year'][year]} |\n"

            # Top topics
            report += f"\n### Top 10 Research Topics\n"
            report += "| Topic | Projects |\n|-------|----------|\n"

            sorted_topics = sorted(data['topics'].items(), key=lambda x: x[1], reverse=True)[:10]
            for topic, count in sorted_topics:
                report += f"| {topic} | {count} |\n"

            report += "\n---\n"

        # Data quality checks
        report += "\n## Data Quality Checks\n\n"
        report += "### Country Code Verification\n"
        report += "- Checked 'GR' and 'EL' for Greece\n"
        report += "- Checked 'AL' for Albania\n"
        report += "- Checked 'XK' and 'KS' for Kosovo\n\n"

        # Search for any projects mentioning these countries in titles
        report += "### Additional Verification\n"
        report += "Searching project titles and organizations for country mentions...\n\n"

        return report

    def get_country_name(self, code: str) -> str:
        """Get country name from code"""
        country_names = {
            'DE': 'Germany', 'FR': 'France', 'IT': 'Italy', 'ES': 'Spain',
            'NL': 'Netherlands', 'BE': 'Belgium', 'UK': 'United Kingdom',
            'SE': 'Sweden', 'DK': 'Denmark', 'FI': 'Finland', 'NO': 'Norway',
            'PL': 'Poland', 'CZ': 'Czech Republic', 'AT': 'Austria',
            'PT': 'Portugal', 'IE': 'Ireland', 'CH': 'Switzerland',
            'HU': 'Hungary', 'RO': 'Romania', 'BG': 'Bulgaria',
            'SI': 'Slovenia', 'HR': 'Croatia', 'EE': 'Estonia',
            'LV': 'Latvia', 'LT': 'Lithuania', 'CY': 'Cyprus',
            'LU': 'Luxembourg', 'SK': 'Slovakia', 'MT': 'Malta',
            'TR': 'Turkey', 'RS': 'Serbia', 'UA': 'Ukraine',
            'US': 'United States', 'CA': 'Canada', 'AU': 'Australia',
            'JP': 'Japan', 'CN': 'China', 'IN': 'India', 'BR': 'Brazil',
            'IL': 'Israel', 'KR': 'South Korea', 'SG': 'Singapore',
            'ZA': 'South Africa', 'MX': 'Mexico', 'NZ': 'New Zealand',
            'CL': 'Chile', 'AR': 'Argentina', 'MY': 'Malaysia',
            'TH': 'Thailand', 'VN': 'Vietnam', 'EG': 'Egypt',
            'SA': 'Saudi Arabia', 'KE': 'Kenya', 'NG': 'Nigeria',
            'RU': 'Russia', 'BY': 'Belarus', 'KZ': 'Kazakhstan',
            'IS': 'Iceland', 'ME': 'Montenegro', 'MK': 'North Macedonia',
            'BA': 'Bosnia and Herzegovina', 'AM': 'Armenia', 'GE': 'Georgia',
            'TW': 'Taiwan', 'FO': 'Faroe Islands', 'GL': 'Greenland'
        }
        return country_names.get(code, code)

    def search_text_mentions(self, program: str):
        """Search for text mentions of countries in projects"""
        program_path = self.base_path / program / "projects"
        project_file = program_path / "project.json"

        if not project_file.exists():
            return {}

        projects = self.load_json_file(project_file)
        mentions = defaultdict(list)

        search_terms = {
            'Greece': ['Greece', 'Greek', 'Hellenic', 'Athens'],
            'Albania': ['Albania', 'Albanian', 'Tirana'],
            'Kosovo': ['Kosovo', 'Kosovar', 'Pristina', 'Prishtina']
        }

        for project in projects[:1000]:  # Sample first 1000 for speed
            if not isinstance(project, dict):
                continue

            # Check title and objective
            text_to_search = (
                project.get('title', '').lower() + ' ' +
                project.get('objective', '').lower()
            )

            for country, terms in search_terms.items():
                for term in terms:
                    if term.lower() in text_to_search:
                        mentions[country].append({
                            'id': project.get('id', ''),
                            'acronym': project.get('acronym', ''),
                            'title': project.get('title', '')
                        })
                        break

        return mentions

    def save_results(self):
        """Save analysis results"""
        output_dir = Path("data/processed/cordis_specific_countries")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save JSON results
        json_output = {
            'metadata': {
                'generated': timestamp,
                'countries_analyzed': list(self.target_countries.values())
            },
            'countries': {}
        }

        for country_code, data in self.results.items():
            json_output['countries'][country_code] = {
                'name': self.target_countries[country_code],
                'total_projects': data['total_projects'],
                'china_collaborations': len(data['china_projects']),
                'as_coordinator': data['coordinators'],
                'as_participant': data['participants'],
                'total_funding': data['funding_total'],
                'ec_contribution': data['ec_contribution'],
                'partner_countries': dict(sorted(data['partner_countries'].items(), key=lambda x: x[1], reverse=True)),
                'top_organizations': dict(sorted(data['organizations'].items(), key=lambda x: x[1], reverse=True)[:20]),
                'projects_by_year': dict(data['projects_by_year']),
                'china_projects': data['china_projects']
            }

        json_file = output_dir / f"greece_albania_kosovo_analysis_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=2, ensure_ascii=False)

        # Save report
        report = self.generate_report()
        report_file = output_dir / f"GREECE_ALBANIA_KOSOVO_ANALYSIS_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\nResults saved to:")
        print(f"  - {json_file}")
        print(f"  - {report_file}")

    def run(self):
        """Run the complete analysis"""
        print("=" * 60)
        print("Greece, Albania, Kosovo Collaboration Analysis")
        print("=" * 60)

        # Process both programs
        self.analyze_program("h2020")
        self.analyze_program("horizon")

        # Check for text mentions
        print("\nSearching for text mentions in project descriptions...")
        h2020_mentions = self.search_text_mentions("h2020")
        horizon_mentions = self.search_text_mentions("horizon")

        # Save results
        self.save_results()

        # Print summary
        print("\n" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("=" * 60)

        for country_code in ['GR', 'AL', 'XK']:
            if country_code in self.results:
                data = self.results[country_code]
                country_name = self.target_countries[country_code]
                print(f"\n{country_name} ({country_code}):")
                print(f"  Total projects: {data['total_projects']}")
                print(f"  China collaborations: {len(data['china_projects'])}")
                if data['china_projects']:
                    print(f"    *** WARNING: Found China collaborations!")
                    for proj in data['china_projects']:
                        print(f"      - {proj['acronym']} ({proj['id']})")
                print(f"  Top partners: ", end="")
                top_3 = sorted(data['partner_countries'].items(), key=lambda x: x[1], reverse=True)[:3]
                print(", ".join([f"{self.get_country_name(c[0])} ({c[1]})" for c in top_3]))
            else:
                print(f"\n{self.target_countries[country_code]} ({country_code}): NO DATA FOUND")

if __name__ == "__main__":
    analyzer = SpecificCountryAnalyzer()
    analyzer.run()
