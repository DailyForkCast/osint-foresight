#!/usr/bin/env python3
"""
Comprehensive CORDIS Analysis for EU Funding Networks
Maps all EU research funding involving Italy and China connections
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class CORDISComprehensiveAnalyzer:
    """Comprehensive analysis of CORDIS EU funding data"""

    def __init__(self):
        self.output_dir = Path("data/processed/cordis_comprehensive")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.cordis_base = "https://cordis.europa.eu/api"

        # Italian institutions to track
        self.italian_institutions = [
            'leonardo', 'finmeccanica', 'fincantieri', 'eni', 'enel',
            'cnr', 'enea', 'infn', 'iit', 'asi', 'agenzia spaziale italiana',
            'politecnico di milano', 'politecnico di torino', 'universita di bologna',
            'sapienza', 'universita la sapienza', 'universita di roma',
            'universita di napoli', 'universita di firenze', 'universita di pisa',
            'bocconi', 'luiss', 'cattolica', 'tor vergata',
            'stmicroelectronics', 'prysmian', 'pirelli', 'telecom italia',
            'intesa sanpaolo', 'unicredit', 'generali',
            'stellantis', 'fiat', 'iveco', 'ferrari', 'maserati',
            'agusta', 'alenia', 'oto melara', 'selex', 'telespazio'
        ]

        # Chinese institution indicators
        self.china_indicators = [
            'china', 'chinese', 'beijing', 'shanghai', 'tsinghua', 'peking',
            'cas', 'chinese academy', 'cass', 'fudan', 'zhejiang',
            'harbin', 'xian', 'huawei', 'zte', 'alibaba', 'tencent',
            'sinopec', 'petrochina', 'state grid', 'cnooc'
        ]

        # Technology areas of interest
        self.tech_areas = [
            'artificial intelligence', 'machine learning', 'quantum',
            'cybersecurity', 'blockchain', 'semiconductor', 'microelectronics',
            '5g', '6g', 'telecommunications', 'satellite', 'space',
            'energy storage', 'battery', 'solar', 'wind', 'hydrogen',
            'biotechnology', 'nanotechnology', 'materials science',
            'robotics', 'autonomous', 'drone', 'automotive'
        ]

        self.results = {
            'projects': [],
            'italian_participation': [],
            'china_connections': [],
            'funding_analysis': {},
            'technology_mapping': {},
            'collaboration_networks': {}
        }

    def search_projects_by_country(self, country_code: str, start_year: int = 2014):
        """Search for projects by country participation"""
        logger.info(f"Searching projects for country: {country_code}")

        projects = []

        # CORDIS API endpoint for projects
        endpoint = f"{self.cordis_base}/projects"

        params = {
            'format': 'json',
            'pageSize': 1000,
            'orderBy': 'startDate',
            'page': 1
        }

        # Add country filter
        if country_code == 'IT':
            params['countryCode'] = 'IT'

        try:
            while True:
                logger.info(f"Fetching page {params['page']} for {country_code}")

                response = requests.get(endpoint, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()

                if 'projects' not in data:
                    break

                page_projects = data['projects']
                if not page_projects:
                    break

                projects.extend(page_projects)
                logger.info(f"  Found {len(page_projects)} projects on page {params['page']}")

                # Check if there are more pages
                if len(page_projects) < params['pageSize']:
                    break

                params['page'] += 1
                time.sleep(0.5)  # Rate limiting

                # Limit to reasonable number for processing
                if len(projects) >= 10000:
                    logger.info(f"Reached limit of 10,000 projects")
                    break

        except Exception as e:
            logger.error(f"Error fetching projects: {e}")

        logger.info(f"Total projects found for {country_code}: {len(projects)}")
        return projects

    def analyze_project_details(self, project):
        """Analyze detailed project information"""
        project_id = project.get('rcn') or project.get('id')

        if not project_id:
            return None

        try:
            # Get detailed project information
            detail_url = f"{self.cordis_base}/project/{project_id}"
            response = requests.get(detail_url, timeout=30)

            if response.status_code != 200:
                return None

            detail_data = response.json()

            # Extract key information
            analysis = {
                'id': project_id,
                'title': project.get('title', ''),
                'acronym': project.get('acronym', ''),
                'objective': project.get('objective', ''),
                'start_date': project.get('startDate', ''),
                'end_date': project.get('endDate', ''),
                'total_cost': project.get('totalCost', 0),
                'eu_contribution': project.get('ecMaxContribution', 0),
                'programme': project.get('frameworkProgramme', ''),
                'topic': project.get('topics', []),
                'technologies': [],
                'italian_participants': [],
                'china_connections': [],
                'coordination': project.get('coordinator', {})
            }

            # Check for Italian participation
            if 'participants' in detail_data:
                for participant in detail_data['participants']:
                    country = participant.get('country', {}).get('code', '')
                    org_name = participant.get('name', '').lower()

                    if country == 'IT':
                        analysis['italian_participants'].append({
                            'name': participant.get('name', ''),
                            'city': participant.get('city', ''),
                            'role': participant.get('role', ''),
                            'contribution': participant.get('ecContribution', 0)
                        })

                        # Check if it's a key Italian institution
                        for institution in self.italian_institutions:
                            if institution in org_name:
                                analysis['key_italian_institution'] = institution
                                break

                    # Check for Chinese connections
                    elif country == 'CN' or any(indicator in org_name for indicator in self.china_indicators):
                        analysis['china_connections'].append({
                            'name': participant.get('name', ''),
                            'country': country,
                            'city': participant.get('city', ''),
                            'role': participant.get('role', ''),
                            'contribution': participant.get('ecContribution', 0)
                        })

            # Check for technology keywords
            text_to_check = ' '.join([
                analysis['title'],
                analysis['objective'],
                str(analysis['topic'])
            ]).lower()

            for tech in self.tech_areas:
                if tech in text_to_check:
                    analysis['technologies'].append(tech)

            time.sleep(0.2)  # Rate limiting

            return analysis

        except Exception as e:
            logger.debug(f"Error analyzing project {project_id}: {e}")
            return None

    def process_italian_projects(self):
        """Process all Italian projects comprehensively"""
        logger.info("Starting comprehensive analysis of Italian EU projects...")

        # Get all Italian projects
        italian_projects = self.search_projects_by_country('IT')

        logger.info(f"Processing {len(italian_projects)} Italian projects...")

        processed_count = 0

        for i, project in enumerate(italian_projects):
            if i % 100 == 0:
                logger.info(f"Processed {i}/{len(italian_projects)} projects...")

            analysis = self.analyze_project_details(project)

            if analysis:
                self.results['projects'].append(analysis)

                # Track Italian participation
                if analysis['italian_participants']:
                    self.results['italian_participation'].append(analysis)

                # Track China connections
                if analysis['china_connections']:
                    self.results['china_connections'].append(analysis)
                    logger.info(f"China connection found: {analysis['title']}")

                processed_count += 1

                # Save intermediate results every 500 projects
                if processed_count % 500 == 0:
                    self.save_intermediate_results()

        logger.info(f"Processed {processed_count} projects successfully")

    def analyze_funding_patterns(self):
        """Analyze funding patterns and flows"""
        logger.info("Analyzing funding patterns...")

        funding_analysis = {
            'total_projects': len(self.results['projects']),
            'total_italian_participation': len(self.results['italian_participation']),
            'total_china_connections': len(self.results['china_connections']),
            'funding_by_year': defaultdict(lambda: {'count': 0, 'total': 0, 'eu_contribution': 0}),
            'funding_by_programme': defaultdict(lambda: {'count': 0, 'total': 0, 'eu_contribution': 0}),
            'italian_institutions': defaultdict(lambda: {'projects': 0, 'funding': 0}),
            'china_collaboration_funding': 0,
            'technology_funding': defaultdict(lambda: {'count': 0, 'funding': 0})
        }

        for project in self.results['projects']:
            year = project.get('start_date', '')[:4] if project.get('start_date') else 'unknown'
            programme = project.get('programme', 'unknown')
            total_cost = project.get('total_cost', 0)
            eu_contribution = project.get('eu_contribution', 0)

            # By year
            funding_analysis['funding_by_year'][year]['count'] += 1
            funding_analysis['funding_by_year'][year]['total'] += total_cost
            funding_analysis['funding_by_year'][year]['eu_contribution'] += eu_contribution

            # By programme
            funding_analysis['funding_by_programme'][programme]['count'] += 1
            funding_analysis['funding_by_programme'][programme]['total'] += total_cost
            funding_analysis['funding_by_programme'][programme]['eu_contribution'] += eu_contribution

            # Italian institutions
            for participant in project.get('italian_participants', []):
                name = participant['name']
                contribution = participant.get('contribution', 0)
                funding_analysis['italian_institutions'][name]['projects'] += 1
                funding_analysis['italian_institutions'][name]['funding'] += contribution

            # China collaboration funding
            if project.get('china_connections'):
                funding_analysis['china_collaboration_funding'] += eu_contribution

            # Technology funding
            for tech in project.get('technologies', []):
                funding_analysis['technology_funding'][tech]['count'] += 1
                funding_analysis['technology_funding'][tech]['funding'] += eu_contribution

        self.results['funding_analysis'] = funding_analysis

    def generate_collaboration_networks(self):
        """Generate collaboration network analysis"""
        logger.info("Generating collaboration networks...")

        networks = {
            'italy_china_projects': [],
            'institution_connections': defaultdict(set),
            'technology_clusters': defaultdict(set),
            'coordination_patterns': defaultdict(int)
        }

        for project in self.results['china_connections']:
            # Italy-China collaboration projects
            networks['italy_china_projects'].append({
                'project_id': project['id'],
                'title': project['title'],
                'eu_funding': project.get('eu_contribution', 0),
                'italian_orgs': [p['name'] for p in project.get('italian_participants', [])],
                'chinese_orgs': [p['name'] for p in project.get('china_connections', [])],
                'technologies': project.get('technologies', [])
            })

            # Institution connections
            italian_orgs = [p['name'] for p in project.get('italian_participants', [])]
            chinese_orgs = [p['name'] for p in project.get('china_connections', [])]

            for it_org in italian_orgs:
                for cn_org in chinese_orgs:
                    networks['institution_connections'][it_org].add(cn_org)

            # Technology clusters
            for tech in project.get('technologies', []):
                for it_org in italian_orgs:
                    networks['technology_clusters'][tech].add(it_org)
                for cn_org in chinese_orgs:
                    networks['technology_clusters'][tech].add(cn_org)

            # Coordination patterns
            coordinator = project.get('coordination', {})
            coord_country = coordinator.get('country', {}).get('code', '')
            if coord_country == 'IT' and project.get('china_connections'):
                networks['coordination_patterns']['italy_coordinated_with_china'] += 1
            elif coord_country == 'CN' and project.get('italian_participants'):
                networks['coordination_patterns']['china_coordinated_with_italy'] += 1

        # Convert sets to lists for JSON serialization
        for tech, orgs in networks['technology_clusters'].items():
            networks['technology_clusters'][tech] = list(orgs)

        for it_org, cn_orgs in networks['institution_connections'].items():
            networks['institution_connections'][it_org] = list(cn_orgs)

        self.results['collaboration_networks'] = networks

    def save_intermediate_results(self):
        """Save intermediate results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        with open(self.output_dir / f'intermediate_results_{timestamp}.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

    def save_final_results(self):
        """Save comprehensive final results"""
        logger.info("Saving final results...")

        # Save main results
        with open(self.output_dir / 'cordis_comprehensive_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        # Save specific analyses as CSVs
        if self.results['italian_participation']:
            df_italian = pd.DataFrame(self.results['italian_participation'])
            df_italian.to_csv(self.output_dir / 'italian_participation.csv', index=False)

        if self.results['china_connections']:
            df_china = pd.DataFrame(self.results['china_connections'])
            df_china.to_csv(self.output_dir / 'italy_china_collaborations.csv', index=False)

        # Generate comprehensive report
        self.generate_markdown_report()

    def generate_markdown_report(self):
        """Generate comprehensive markdown report"""
        report_path = self.output_dir / 'CORDIS_COMPREHENSIVE_ANALYSIS.md'

        with open(report_path, 'w') as f:
            f.write(f"""# CORDIS Comprehensive Analysis: Italy-China EU Funding Networks
**Generated:** {datetime.now().isoformat()}
**Source:** CORDIS EU Research Database

## Executive Summary

Comprehensive analysis of EU research funding reveals {len(self.results['china_connections'])} projects involving both Italian and Chinese institutions, with total EU funding of €{sum(p.get('eu_contribution', 0) for p in self.results['china_connections']):,.0f}.

## Key Statistics

### Overall Numbers
- Total Italian projects analyzed: {len(self.results['projects']):,}
- Projects with Italian participation: {len(self.results['italian_participation']):,}
- Italy-China collaboration projects: {len(self.results['china_connections']):,}
- Total funding to Italy-China collaborations: €{sum(p.get('eu_contribution', 0) for p in self.results['china_connections']):,.0f}

### Funding by Programme
""")

            if 'funding_analysis' in self.results:
                funding = self.results['funding_analysis']

                for programme, data in sorted(funding['funding_by_programme'].items(),
                                            key=lambda x: x[1]['eu_contribution'], reverse=True)[:10]:
                    f.write(f"- **{programme}:** €{data['eu_contribution']:,.0f} ({data['count']} projects)\n")

                f.write(f"""
### Italy-China Collaboration Projects

""")

                for project in self.results['china_connections'][:20]:
                    f.write(f"""
**{project['title']}**
- EU Funding: €{project.get('eu_contribution', 0):,.0f}
- Italian Partners: {', '.join([p['name'] for p in project.get('italian_participants', [])][:3])}
- Chinese Partners: {', '.join([p['name'] for p in project.get('china_connections', [])][:3])}
- Technologies: {', '.join(project.get('technologies', [])[:3])}
""")

                f.write(f"""
### Technology Areas

Top technology areas in Italy-China collaborations:
""")

                if 'collaboration_networks' in self.results:
                    tech_projects = defaultdict(int)
                    for project in self.results['china_connections']:
                        for tech in project.get('technologies', []):
                            tech_projects[tech] += 1

                    for tech, count in sorted(tech_projects.items(), key=lambda x: x[1], reverse=True)[:15]:
                        f.write(f"- **{tech}:** {count} projects\n")

                f.write(f"""
### Key Italian Institutions in China Collaborations
""")

                institution_projects = defaultdict(int)
                for project in self.results['china_connections']:
                    for participant in project.get('italian_participants', []):
                        institution_projects[participant['name']] += 1

                for institution, count in sorted(institution_projects.items(), key=lambda x: x[1], reverse=True)[:20]:
                    f.write(f"- **{institution}:** {count} collaborations\n")

                f.write(f"""
### Coordination Patterns
""")

                if 'collaboration_networks' in self.results:
                    coord_patterns = self.results['collaboration_networks']['coordination_patterns']
                    f.write(f"- Italy-coordinated projects with China: {coord_patterns.get('italy_coordinated_with_china', 0)}\n")
                    f.write(f"- China-coordinated projects with Italy: {coord_patterns.get('china_coordinated_with_italy', 0)}\n")

                f.write(f"""
## Risk Assessment

### Funding Exposure
- Total EU funding at risk through China collaborations: €{sum(p.get('eu_contribution', 0) for p in self.results['china_connections']):,.0f}
- Percentage of total Italian funding: {(sum(p.get('eu_contribution', 0) for p in self.results['china_connections']) / max(sum(p.get('eu_contribution', 0) for p in self.results['projects']), 1) * 100):.1f}%

### Critical Technologies
High-risk technology collaborations identified in:
""")

                critical_techs = ['artificial intelligence', 'quantum', 'cybersecurity', 'semiconductor', '5g', '6g']
                for tech in critical_techs:
                    projects_with_tech = [p for p in self.results['china_connections'] if tech in p.get('technologies', [])]
                    if projects_with_tech:
                        f.write(f"- **{tech}:** {len(projects_with_tech)} projects, €{sum(p.get('eu_contribution', 0) for p in projects_with_tech):,.0f} funding\n")

                f.write(f"""
## Implications

This CORDIS analysis reveals:

1. **Systematic China engagement** across multiple EU research programmes
2. **Significant funding flows** to joint Italy-China research projects
3. **Critical technology areas** where collaboration creates potential vulnerabilities
4. **Institutional patterns** showing which Italian organizations are most engaged

### Recommendations

1. **Enhanced due diligence** for projects involving critical technologies
2. **Technology transfer assessment** for ongoing collaborations
3. **Alternative partnership development** with allied countries
4. **Risk-based funding decisions** for future programmes

This analysis complements TED procurement and SEC filing data by revealing the research dimension of Italy-China integration.
""")

        logger.info(f"Report saved to {report_path}")

    def run_comprehensive_analysis(self):
        """Run complete CORDIS analysis"""
        logger.info("Starting comprehensive CORDIS analysis...")

        # Step 1: Process Italian projects
        self.process_italian_projects()

        # Step 2: Analyze funding patterns
        self.analyze_funding_patterns()

        # Step 3: Generate collaboration networks
        self.generate_collaboration_networks()

        # Step 4: Save results
        self.save_final_results()

        return self.results


def main():
    analyzer = CORDISComprehensiveAnalyzer()

    print("Starting comprehensive CORDIS analysis...")
    print("This will analyze EU research funding for Italy-China connections...")

    results = analyzer.run_comprehensive_analysis()

    print(f"\n=== CORDIS Analysis Complete ===")
    print(f"Total projects analyzed: {len(results['projects'])}")
    print(f"Italian participation: {len(results['italian_participation'])}")
    print(f"Italy-China collaborations: {len(results['china_connections'])}")

    if results['china_connections']:
        total_funding = sum(p.get('eu_contribution', 0) for p in results['china_connections'])
        print(f"Total EU funding to Italy-China collaborations: €{total_funding:,.0f}")


if __name__ == "__main__":
    main()
