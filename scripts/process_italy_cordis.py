#!/usr/bin/env python3
"""
Italy CORDIS Data Analysis
Processes H2020 and Horizon Europe data to identify Italy-relevant projects
Focus on defense, technology sovereignty, and critical technologies
"""

import json
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set
import logging
from collections import defaultdict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ItalyCORDISAnalyzer:
    """Analyze CORDIS data for Italy-relevant projects."""

    def __init__(self):
        """Initialize analyzer with Italy focus areas."""
        self.base_path = Path("C:/Projects/OSINT - Foresight/data/raw/source=cordis")
        self.external_path = Path("F:/2025-09-14 Horizons")

        # Italy strategic focus areas from Executive Brief
        self.focus_areas = {
            'defense': [
                'defense', 'defence', 'military', 'security', 'nato',
                'dual-use', 'dual use', 'missile', 'radar', 'surveillance'
            ],
            'naval': [
                'naval', 'maritime', 'ship', 'submarine', 'frigate',
                'vessel', 'marine', 'underwater', 'sonar', 'torpedo'
            ],
            'space': [
                'space', 'satellite', 'galileo', 'copernicus', 'cosmo-skymed',
                'earth observation', 'launch', 'orbit', 'gnss', 'esa'
            ],
            'aerospace': [
                'aerospace', 'aircraft', 'helicopter', 'aviation', 'drone',
                'uav', 'unmanned', 'flight', 'avionics', 'tempest', 'gcap'
            ],
            'cyber': [
                'cyber', 'cybersecurity', 'information security', 'network security',
                'critical infrastructure', 'encryption', 'quantum communication'
            ],
            'semiconductors': [
                'semiconductor', 'chip', 'microelectronic', 'photonic', 'quantum',
                'processor', 'integrated circuit', 'fab', 'foundry', 'euv'
            ],
            'ai_emerging': [
                'artificial intelligence', 'machine learning', 'deep learning',
                'quantum computing', 'quantum technology', 'robotics', 'autonomous'
            ],
            'critical_materials': [
                'rare earth', 'critical material', 'strategic material',
                'battery', 'lithium', 'cobalt', 'supply chain resilience'
            ],
            'energy': [
                'renewable energy', 'nuclear', 'fusion', 'hydrogen',
                'energy storage', 'grid', 'clean energy', 'sustainability'
            ]
        }

        # Key Italian organizations to track
        self.italian_orgs = {
            'leonardo', 'finmeccanica', 'fincantieri', 'thales alenia',
            'telespazio', 'iveco', 'oto melara', 'mbda italia',
            'elettronica', 'vitrociset', 'avio', 'piaggio aerospace',
            'cnr', 'enea', 'infn', 'asi', 'ingv', 'iit',
            'politecnico di milano', 'politecnico di torino',
            'università di roma', 'sapienza', 'università di bologna',
            'università di pisa', 'università di padova'
        }

        # NATO and EU strategic programs
        self.strategic_programs = {
            'edidp', 'edf', 'pesco', 'permanent structured cooperation',
            'diana', 'nato innovation', 'tempest', 'gcap', 'fcas',
            'eurodrone', 'male rpas', 'ipcei', 'digital europe',
            'horizon europe', 'defence fund', 'resceu', 'eu4health'
        }

        self.results = {
            'h2020': defaultdict(list),
            'horizon': defaultdict(list),
            'combined': defaultdict(list)
        }

    def extract_data(self, programme: str) -> Dict[str, Any]:
        """Extract CORDIS data for a specific programme."""
        logger.info(f"Extracting {programme} data...")

        if programme == 'h2020':
            files = {
                'projects': self.external_path / 'cordis-h2020projects-json.zip',
                'deliverables': self.external_path / 'cordis-h2020projectDeliverables-json.zip',
                'publications': self.external_path / 'cordis-h2020projectPublications-json (1).zip',
                'reports': self.external_path / 'cordis-h2020reports-json.zip'
            }
        else:  # horizon
            files = {
                'projects': self.external_path / 'cordis-HORIZONprojects-json (1).zip',
                'deliverables': self.external_path / 'cordis-HORIZONprojectDeliverables-json.zip',
                'publications': self.external_path / 'cordis-HORIZONprojectPublications-json.zip',
                'reports': self.external_path / 'cordis-HORIZONreports-json.zip'
            }

        # Create extraction directory
        extract_path = self.base_path / programme
        extract_path.mkdir(parents=True, exist_ok=True)

        data = {}

        for data_type, zip_path in files.items():
            if zip_path.exists():
                logger.info(f"  Extracting {data_type} from {zip_path.name}")

                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        # Extract to programme folder
                        extract_to = extract_path / data_type
                        extract_to.mkdir(exist_ok=True)
                        zip_ref.extractall(extract_to)

                        # Load main JSON files
                        json_files = list(extract_to.glob("*.json"))
                        for json_file in json_files:
                            if 'project.json' in json_file.name or 'projects.json' in json_file.name:
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    data['projects'] = json.load(f)
                                    logger.info(f"    Loaded {len(data.get('projects', []))} projects")
                            elif 'organization' in json_file.name:
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    data['organizations'] = json.load(f)
                                    logger.info(f"    Loaded {len(data.get('organizations', []))} organizations")
                            elif 'deliverable' in json_file.name and 'project' not in json_file.name:
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    data['deliverables'] = json.load(f)
                            elif 'publication' in json_file.name and 'project' not in json_file.name:
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    data['publications'] = json.load(f)
                            elif 'topics' in json_file.name:
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    data['topics'] = json.load(f)
                            elif 'euroSciVoc' in json_file.name:
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    data['euroSciVoc'] = json.load(f)

                except Exception as e:
                    logger.error(f"  Error extracting {data_type}: {e}")
            else:
                logger.warning(f"  File not found: {zip_path}")

        return data

    def analyze_italy_projects(self, data: Dict[str, Any], programme: str) -> Dict[str, List]:
        """Analyze projects for Italy relevance."""
        italy_projects = defaultdict(list)

        if 'projects' not in data:
            logger.warning(f"No projects data found for {programme}")
            return italy_projects

        projects = data.get('projects', [])
        organizations = data.get('organizations', [])

        # Create org lookup
        org_lookup = {org.get('id'): org for org in organizations} if organizations else {}

        logger.info(f"Analyzing {len(projects)} {programme} projects for Italy relevance...")

        for project in projects:
            italy_involvement = False
            italy_coordinator = False
            strategic_relevance = []

            # Check if Italy is involved
            countries = project.get('countries', [])
            if 'IT' in countries:
                italy_involvement = True

            # Check coordinator
            coordinator_id = project.get('coordinator')
            if coordinator_id and coordinator_id in org_lookup:
                coord_org = org_lookup[coordinator_id]
                if coord_org.get('country') == 'IT':
                    italy_coordinator = True

            # Check for Italian organizations
            italian_partners = []
            participant_ids = project.get('participants', [])
            for part_id in participant_ids:
                if part_id in org_lookup:
                    org = org_lookup[part_id]
                    if org.get('country') == 'IT':
                        org_name = org.get('name', '').lower()
                        italian_partners.append(org.get('name'))

                        # Check if it's a key Italian org
                        for key_org in self.italian_orgs:
                            if key_org in org_name:
                                strategic_relevance.append(f"Key org: {org.get('name')}")
                                break

            # Check strategic relevance
            if italy_involvement or italian_partners:
                # Check title and objective for focus areas
                title = project.get('title', '').lower()
                objective = project.get('objective', '').lower()
                acronym = project.get('acronym', '')

                for area, keywords in self.focus_areas.items():
                    for keyword in keywords:
                        if keyword in title or keyword in objective:
                            strategic_relevance.append(area)
                            break

                # Check for strategic programs
                for program in self.strategic_programs:
                    if program in title or program in objective:
                        strategic_relevance.append(f"Strategic: {program.upper()}")

                # Categorize project
                if strategic_relevance:
                    project_info = {
                        'id': project.get('id'),
                        'acronym': acronym,
                        'title': project.get('title'),
                        'start_date': project.get('startDate'),
                        'end_date': project.get('endDate'),
                        'total_cost': project.get('totalCost', 0),
                        'eu_contribution': project.get('ecMaxContribution', 0),
                        'italy_coordinator': italy_coordinator,
                        'italian_partners': italian_partners,
                        'strategic_areas': list(set(strategic_relevance)),
                        'countries': countries,
                        'status': project.get('status'),
                        'topics': project.get('topics', []),
                        'programme': programme.upper()
                    }

                    # Categorize by relevance
                    if italy_coordinator and any('defense' in s or 'naval' in s or 'space' in s
                                                 for s in strategic_relevance):
                        italy_projects['critical_strategic'].append(project_info)
                    elif italy_coordinator:
                        italy_projects['italy_led'].append(project_info)
                    elif len([s for s in strategic_relevance if 'Key org' in s]) > 0:
                        italy_projects['key_organization'].append(project_info)
                    elif strategic_relevance:
                        italy_projects['strategic_participant'].append(project_info)
                    else:
                        italy_projects['other_participant'].append(project_info)

        # Log summary
        for category, projects in italy_projects.items():
            logger.info(f"  {category}: {len(projects)} projects")

        return italy_projects

    def identify_critical_projects(self, italy_projects: Dict) -> Dict[str, List]:
        """Identify most critical projects for Italy's strategic interests."""
        critical = {
            'defense_dual_use': [],
            'technology_sovereignty': [],
            'china_risk_mitigation': [],
            'nato_alignment': [],
            'innovation_ecosystem': []
        }

        for category, projects in italy_projects.items():
            for project in projects:
                areas = project.get('strategic_areas', [])
                title_lower = project.get('title', '').lower()

                # Defense and dual-use
                if any(area in ['defense', 'naval', 'aerospace', 'cyber'] for area in areas):
                    critical['defense_dual_use'].append(project)

                # Technology sovereignty
                if any(area in ['semiconductors', 'ai_emerging', 'quantum'] for area in areas):
                    critical['technology_sovereignty'].append(project)

                # Supply chain resilience (China risk)
                if any(area in ['critical_materials', 'semiconductors'] for area in areas):
                    critical['china_risk_mitigation'].append(project)

                # NATO alignment
                if any(keyword in title_lower for keyword in
                       ['nato', 'stanag', 'defence', 'military', 'interoperability']):
                    critical['nato_alignment'].append(project)

                # Innovation ecosystem
                if project.get('italy_coordinator') and project.get('eu_contribution', 0) > 1000000:
                    critical['innovation_ecosystem'].append(project)

        return critical

    def generate_report(self, all_results: Dict) -> str:
        """Generate comprehensive Italy CORDIS analysis report."""
        report = []
        report.append("# Italy CORDIS Analysis Report")
        report.append("## EU Research Projects Strategic Assessment")
        report.append(f"\n*Analysis Date: {datetime.now().strftime('%Y-%m-%d')}*")
        report.append("*Focus: Defense, Technology Sovereignty, and Critical Technologies*")

        # Executive Summary
        report.append("\n## Executive Summary\n")

        total_projects = 0
        total_funding = 0
        italy_led = 0

        for programme in ['h2020', 'horizon']:
            for category, projects in all_results[programme].items():
                total_projects += len(projects)
                for project in projects:
                    if project.get('italy_coordinator'):
                        italy_led += 1
                        total_funding += project.get('eu_contribution', 0)

        report.append(f"- **Total Italy-Relevant Projects**: {total_projects}")
        report.append(f"- **Italy-Led Projects**: {italy_led}")
        report.append(f"- **Total EU Funding to Italy-Led Projects**: €{total_funding:,.2f}")

        # Strategic Categories
        report.append("\n## Strategic Project Categories\n")

        # Critical Strategic Projects
        critical_strategic = []
        for programme in ['h2020', 'horizon']:
            critical_strategic.extend(all_results[programme].get('critical_strategic', []))

        if critical_strategic:
            report.append("\n### 🔴 Critical Strategic Projects (Defense/Space/Naval)")
            report.append(f"**Count**: {len(critical_strategic)} projects\n")

            # Sort by EU contribution
            critical_strategic.sort(key=lambda x: x.get('eu_contribution', 0), reverse=True)

            for project in critical_strategic[:10]:  # Top 10
                report.append(f"\n#### {project['acronym']} - {project['title']}")
                report.append(f"- **Programme**: {project['programme']}")
                report.append(f"- **EU Funding**: €{project.get('eu_contribution', 0):,.2f}")
                report.append(f"- **Period**: {project.get('start_date', 'N/A')} to {project.get('end_date', 'N/A')}")
                report.append(f"- **Strategic Areas**: {', '.join(project.get('strategic_areas', []))}")
                report.append(f"- **Italian Partners**: {', '.join(project.get('italian_partners', [])[:3])}")

        # Technology Sovereignty Projects
        report.append("\n### 🟡 Technology Sovereignty Projects")

        tech_sovereignty = []
        for programme in ['h2020', 'horizon']:
            for project in all_results[programme].get('critical_strategic', []) + \
                         all_results[programme].get('italy_led', []) + \
                         all_results[programme].get('key_organization', []):
                areas = project.get('strategic_areas', [])
                if any(area in ['semiconductors', 'ai_emerging', 'quantum', 'cyber'] for area in areas):
                    tech_sovereignty.append(project)

        # Remove duplicates
        seen = set()
        unique_tech = []
        for project in tech_sovereignty:
            if project['id'] not in seen:
                seen.add(project['id'])
                unique_tech.append(project)

        report.append(f"**Count**: {len(unique_tech)} projects\n")

        for project in unique_tech[:5]:  # Top 5
            report.append(f"- **{project['acronym']}**: {project['title'][:80]}...")
            report.append(f"  - Areas: {', '.join(project.get('strategic_areas', []))}")
            report.append(f"  - Funding: €{project.get('eu_contribution', 0):,.2f}")

        # Key Italian Organizations
        report.append("\n## Key Italian Organizations Performance\n")

        org_participation = defaultdict(int)
        org_funding = defaultdict(float)
        org_leadership = defaultdict(int)

        for programme in ['h2020', 'horizon']:
            for category, projects in all_results[programme].items():
                for project in projects:
                    for partner in project.get('italian_partners', []):
                        org_participation[partner] += 1
                        if project.get('italy_coordinator'):
                            org_leadership[partner] += 1
                            org_funding[partner] += project.get('eu_contribution', 0)

        # Top organizations by participation
        top_orgs = sorted(org_participation.items(), key=lambda x: x[1], reverse=True)[:10]

        report.append("### Top Organizations by Participation")
        for org, count in top_orgs:
            leadership = org_leadership.get(org, 0)
            funding = org_funding.get(org, 0)
            report.append(f"- **{org}**: {count} projects ({leadership} as coordinator, €{funding:,.2f} funding)")

        # NATO and Defense Alignment
        report.append("\n## NATO and Defense Alignment\n")

        nato_projects = []
        for programme in ['h2020', 'horizon']:
            for category, projects in all_results[programme].items():
                for project in projects:
                    title_lower = project.get('title', '').lower()
                    if any(keyword in title_lower for keyword in ['nato', 'defence', 'military', 'stanag']):
                        nato_projects.append(project)

        report.append(f"**NATO-Relevant Projects**: {len(nato_projects)}\n")

        for project in nato_projects[:5]:
            report.append(f"- **{project['acronym']}**: {project['title'][:100]}...")

        # China Risk Mitigation
        report.append("\n## Supply Chain and China Risk Mitigation\n")

        supply_chain_projects = []
        for programme in ['h2020', 'horizon']:
            for category, projects in all_results[programme].items():
                for project in projects:
                    areas = project.get('strategic_areas', [])
                    if 'critical_materials' in areas or 'supply chain' in project.get('title', '').lower():
                        supply_chain_projects.append(project)

        report.append(f"**Supply Chain Resilience Projects**: {len(supply_chain_projects)}\n")

        # Recommendations
        report.append("\n## Strategic Recommendations\n")

        report.append("### 1. Leverage Existing EU Projects")
        report.append("- Maximize participation in identified strategic projects")
        report.append("- Strengthen coordination between Italian partners")
        report.append("- Ensure technology transfer to national capabilities")

        report.append("\n### 2. Focus Areas for Future Calls")
        report.append("- **Priority 1**: Defense technologies and dual-use applications")
        report.append("- **Priority 2**: Semiconductor and quantum technologies")
        report.append("- **Priority 3**: Space and satellite systems")
        report.append("- **Priority 4**: Cybersecurity and critical infrastructure")

        report.append("\n### 3. Strengthen Key Organizations")
        report.append("- Support Leonardo, Fincantieri, and other prime contractors")
        report.append("- Enhance university-industry collaboration")
        report.append("- Build consortiums for major EU calls")

        # Data Sources
        report.append("\n## Data Sources\n")
        report.append("- H2020 Projects Database (2014-2020)")
        report.append("- Horizon Europe Projects Database (2021-2027)")
        report.append("- Analysis Date: " + datetime.now().strftime('%Y-%m-%d'))
        report.append("- Focus: Italy participation with strategic technology emphasis")

        return "\n".join(report)

    def run_analysis(self):
        """Run complete Italy CORDIS analysis."""
        logger.info("Starting Italy CORDIS Analysis...")

        # Process H2020
        logger.info("\n=== Processing H2020 Data ===")
        h2020_data = self.extract_data('h2020')
        h2020_italy = self.analyze_italy_projects(h2020_data, 'h2020')
        self.results['h2020'] = h2020_italy

        # Process Horizon Europe
        logger.info("\n=== Processing Horizon Europe Data ===")
        horizon_data = self.extract_data('horizon')
        horizon_italy = self.analyze_italy_projects(horizon_data, 'horizon')
        self.results['horizon'] = horizon_italy

        # Identify critical projects
        logger.info("\n=== Identifying Critical Projects ===")
        h2020_critical = self.identify_critical_projects(h2020_italy)
        horizon_critical = self.identify_critical_projects(horizon_italy)

        self.results['h2020_critical'] = h2020_critical
        self.results['horizon_critical'] = horizon_critical

        # Generate report
        logger.info("\n=== Generating Report ===")
        report = self.generate_report(self.results)

        # Save results
        output_path = Path("C:/Projects/OSINT - Foresight/data/processed/italy_cordis")
        output_path.mkdir(parents=True, exist_ok=True)

        # Save report
        with open(output_path / "ITALY_CORDIS_ANALYSIS.md", 'w', encoding='utf-8') as f:
            f.write(report)

        # Save detailed results
        with open(output_path / "italy_cordis_results.json", 'w', encoding='utf-8') as f:
            # Convert to serializable format
            serializable_results = {}
            for key, value in self.results.items():
                if isinstance(value, defaultdict):
                    serializable_results[key] = dict(value)
                else:
                    serializable_results[key] = value
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)

        logger.info(f"\nAnalysis complete! Results saved to {output_path}")

        return report


def main():
    """Main function."""
    analyzer = ItalyCORDISAnalyzer()
    report = analyzer.run_analysis()

    # Print summary
    print("\n" + "="*60)
    print("ITALY CORDIS ANALYSIS COMPLETE")
    print("="*60)

    # Quick stats
    total_projects = 0
    for programme in ['h2020', 'horizon']:
        for category, projects in analyzer.results[programme].items():
            total_projects += len(projects)

    print(f"Total Italy-relevant projects analyzed: {total_projects}")
    print(f"Output saved to: data/processed/italy_cordis/")
    print("\nKey files created:")
    print("  - ITALY_CORDIS_ANALYSIS.md (main report)")
    print("  - italy_cordis_results.json (detailed data)")


if __name__ == "__main__":
    main()
