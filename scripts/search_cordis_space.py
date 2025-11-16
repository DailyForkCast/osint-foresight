"""
Search CORDIS for space technology projects
NO FABRICATION - Only report actual project data
"""

import json
from pathlib import Path
from collections import defaultdict

def search_space_projects():
    h2020_path = Path("C:/Projects/OSINT - Foresight/countries/_global/data/cordis_raw/h2020/projects/project.json")
    horizon_path = Path("C:/Projects/OSINT - Foresight/countries/_global/data/cordis_raw/horizon/projects/project.json")

    # Comprehensive space keywords covering all 15 subfields
    space_keywords = [
        # General
        'space', 'satellite', 'orbital', 'launch', 'rocket',
        # Subfield 1: Reusable Launch
        'reusable launch', 'reusable rocket', 'launch vehicle',
        # Subfield 2: Satellite Constellations
        'constellation', 'smallsat', 'cubesat', 'nanosatellite',
        # Subfield 3: In-Orbit Servicing
        'in-orbit servicing', 'on-orbit', 'satellite servicing', 'refueling',
        # Subfield 4: Lunar
        'lunar', 'moon', 'cislunar', 'ISRU',
        # Subfield 5: Debris Removal
        'debris', 'debris removal', 'ADR', 'active debris',
        # Subfield 6: Propulsion
        'propulsion', 'electric propulsion', 'ion drive', 'nuclear propulsion',
        # Subfield 7: Communications
        'space communication', 'satellite communication', 'deep space',
        # Subfield 8: ISR/Remote Sensing
        'remote sensing', 'earth observation', 'ISR', 'reconnaissance',
        # Subfield 9: Human Spaceflight
        'human spaceflight', 'manned mission', 'astronaut', 'life support',
        # Subfield 10: In-Space Manufacturing
        'in-space manufacturing', 'additive manufacturing', '3D printing',
        # Subfield 11: Cryogenic
        'cryogenic', 'cryogen', 'liquid hydrogen', 'liquid oxygen',
        # Subfield 12: SSA
        'space situational awareness', 'SSA', 'space surveillance', 'tracking',
        # Subfield 13: Robotic Exploration
        'robotic', 'rover', 'lander', 'planetary',
        # Subfield 14: Small Satellites
        'small satellite', 'microsatellite',
        # Subfield 15: Ground Infrastructure
        'spaceport', 'ground station', 'tracking station', 'launch site'
    ]

    results = {
        'h2020_projects': [],
        'horizon_projects': [],
        'total_funding': 0,
        'countries': defaultdict(int),
        'coordinators': defaultdict(int),
        'topics': defaultdict(int)
    }

    # Search H2020
    print("Searching H2020 projects...")
    if h2020_path.exists():
        with open(h2020_path, 'r', encoding='utf-8') as f:
            try:
                projects = json.load(f)
                for project in projects:
                    title = project.get('title', '').lower()
                    objective = project.get('objective', '').lower()
                    keywords = project.get('keywords', '').lower()

                    combined = f"{title} {objective} {keywords}"

                    if any(kw in combined for kw in space_keywords):
                        project_info = {
                            'id': project.get('id'),
                            'title': project.get('title'),
                            'acronym': project.get('acronym'),
                            'objective': project.get('objective', '')[:500],
                            'totalCost': project.get('totalCost'),
                            'ecMaxContribution': project.get('ecMaxContribution'),
                            'startDate': project.get('startDate'),
                            'endDate': project.get('endDate'),
                            'status': project.get('status'),
                            'coordinator': project.get('coordinator'),
                            'coordinatorCountry': project.get('coordinatorCountry'),
                            'keywords': project.get('keywords'),
                            'source': 'H2020'
                        }
                        results['h2020_projects'].append(project_info)

                        if project.get('ecMaxContribution'):
                            results['total_funding'] += float(project.get('ecMaxContribution', 0))
                        if project.get('coordinatorCountry'):
                            results['countries'][project.get('coordinatorCountry')] += 1
                        if project.get('coordinator'):
                            results['coordinators'][project.get('coordinator')] += 1

                print(f"Found {len(results['h2020_projects'])} H2020 space projects")
            except Exception as e:
                print(f"Error: {e}")

    # Search Horizon Europe
    print("Searching Horizon Europe projects...")
    if horizon_path.exists():
        with open(horizon_path, 'r', encoding='utf-8') as f:
            try:
                projects = json.load(f)
                for project in projects:
                    title = project.get('title', '').lower()
                    objective = project.get('objective', '').lower()
                    keywords = project.get('keywords', '').lower()

                    combined = f"{title} {objective} {keywords}"

                    if any(kw in combined for kw in space_keywords):
                        project_info = {
                            'id': project.get('id'),
                            'title': project.get('title'),
                            'acronym': project.get('acronym'),
                            'objective': project.get('objective', '')[:500],
                            'totalCost': project.get('totalCost'),
                            'ecMaxContribution': project.get('ecMaxContribution'),
                            'startDate': project.get('startDate'),
                            'endDate': project.get('endDate'),
                            'status': project.get('status'),
                            'coordinator': project.get('coordinator'),
                            'coordinatorCountry': project.get('coordinatorCountry'),
                            'keywords': project.get('keywords'),
                            'source': 'Horizon Europe'
                        }
                        results['horizon_projects'].append(project_info)

                        if project.get('ecMaxContribution'):
                            results['total_funding'] += float(project.get('ecMaxContribution', 0))
                        if project.get('coordinatorCountry'):
                            results['countries'][project.get('coordinatorCountry')] += 1
                        if project.get('coordinator'):
                            results['coordinators'][project.get('coordinator')] += 1

                print(f"Found {len(results['horizon_projects'])} Horizon Europe space projects")
            except Exception as e:
                print(f"Error: {e}")

    # Compile report
    all_projects = results['h2020_projects'] + results['horizon_projects']

    report = {
        'source': 'CORDIS - H2020 and Horizon Europe',
        'query_date': '2025-10-06',
        'search_keywords': space_keywords,
        'total_space_projects': len(all_projects),
        'breakdown': {
            'h2020': len(results['h2020_projects']),
            'horizon_europe': len(results['horizon_projects'])
        },
        'total_eu_funding': results['total_funding'],
        'top_countries': sorted(results['countries'].items(),
                               key=lambda x: x[1], reverse=True)[:30],
        'top_coordinators': sorted(results['coordinators'].items(),
                                  key=lambda x: x[1], reverse=True)[:50],
        'all_projects': all_projects
    }

    # Save
    output_path = "C:/Projects/OSINT - Foresight/analysis/space_tech/cordis_space_projects.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n=== CORDIS SPACE ANALYSIS ===")
    print(f"Total space projects: {report['total_space_projects']}")
    print(f"Total EU funding: €{report['total_eu_funding']:,.0f}")
    print(f"\nTop 10 Countries:")
    for country, count in report['top_countries'][:10]:
        print(f"  {country}: {count} projects")
    print(f"\nReport saved to: {output_path}")

    return report

if __name__ == '__main__':
    search_space_projects()
