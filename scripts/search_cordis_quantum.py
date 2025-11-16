"""
Search CORDIS JSON files for quantum technology projects
NO FABRICATION - Only report actual project data from CORDIS files
"""

import json
from pathlib import Path
from collections import defaultdict

def search_quantum_projects():
    # Path to CORDIS data
    h2020_path = Path("C:/Projects/OSINT - Foresight/countries/_global/data/cordis_raw/h2020/projects/project.json")
    horizon_path = Path("C:/Projects/OSINT - Foresight/countries/_global/data/cordis_raw/horizon/projects/project.json")

    quantum_keywords = [
        'quantum', 'qubit', 'entanglement', 'superposition',
        'quantum computing', 'quantum sensor', 'quantum communication'
    ]

    results = {
        'h2020_projects': [],
        'horizon_projects': [],
        'total_funding': 0,
        'countries': defaultdict(int),
        'coordinators': defaultdict(int),
        'topics': defaultdict(int)
    }

    # Search H2020 projects
    print("Searching H2020 projects...")
    if h2020_path.exists():
        with open(h2020_path, 'r', encoding='utf-8') as f:
            try:
                projects = json.load(f)  # Data is directly an array

                for project in projects:
                    title = project.get('title', '').lower()
                    objective = project.get('objective', '').lower()

                    if any(kw in title or kw in objective for kw in quantum_keywords):
                        project_info = {
                            'id': project.get('id'),
                            'title': project.get('title'),
                            'acronym': project.get('acronym'),
                            'objective': project.get('objective', '')[:500],  # First 500 chars
                            'totalCost': project.get('totalCost'),
                            'ecMaxContribution': project.get('ecMaxContribution'),
                            'startDate': project.get('startDate'),
                            'endDate': project.get('endDate'),
                            'status': project.get('status'),
                            'programme': project.get('programme'),
                            'coordinator': project.get('coordinator'),
                            'coordinatorCountry': project.get('coordinatorCountry'),
                            'source': 'H2020'
                        }
                        results['h2020_projects'].append(project_info)

                        # Aggregate stats
                        if project.get('ecMaxContribution'):
                            results['total_funding'] += float(project.get('ecMaxContribution', 0))
                        if project.get('coordinatorCountry'):
                            results['countries'][project.get('coordinatorCountry')] += 1
                        if project.get('coordinator'):
                            results['coordinators'][project.get('coordinator')] += 1

                print(f"Found {len(results['h2020_projects'])} H2020 quantum projects")

            except Exception as e:
                print(f"Error reading H2020 data: {e}")

    # Search Horizon Europe projects
    print("Searching Horizon Europe projects...")
    if horizon_path.exists():
        with open(horizon_path, 'r', encoding='utf-8') as f:
            try:
                projects = json.load(f)  # Data is directly an array

                for project in projects:
                    title = project.get('title', '').lower()
                    objective = project.get('objective', '').lower()

                    if any(kw in title or kw in objective for kw in quantum_keywords):
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
                            'programme': project.get('programme'),
                            'coordinator': project.get('coordinator'),
                            'coordinatorCountry': project.get('coordinatorCountry'),
                            'source': 'Horizon Europe'
                        }
                        results['horizon_projects'].append(project_info)

                        # Aggregate stats
                        if project.get('ecMaxContribution'):
                            results['total_funding'] += float(project.get('ecMaxContribution', 0))
                        if project.get('coordinatorCountry'):
                            results['countries'][project.get('coordinatorCountry')] += 1
                        if project.get('coordinator'):
                            results['coordinators'][project.get('coordinator')] += 1

                print(f"Found {len(results['horizon_projects'])} Horizon Europe quantum projects")

            except Exception as e:
                print(f"Error reading Horizon data: {e}")

    # Compile final report
    all_projects = results['h2020_projects'] + results['horizon_projects']

    report = {
        'source': 'CORDIS - H2020 and Horizon Europe',
        'query_date': '2025-10-06',
        'search_keywords': quantum_keywords,
        'files_searched': [str(h2020_path), str(horizon_path)],
        'total_quantum_projects': len(all_projects),
        'breakdown': {
            'h2020': len(results['h2020_projects']),
            'horizon_europe': len(results['horizon_projects'])
        },
        'total_eu_funding': results['total_funding'],
        'top_countries': sorted(results['countries'].items(),
                               key=lambda x: x[1], reverse=True)[:20],
        'top_coordinators': sorted(results['coordinators'].items(),
                                  key=lambda x: x[1], reverse=True)[:30],
        'all_projects': all_projects
    }

    # Save report
    output_path = "C:/Projects/OSINT - Foresight/analysis/quantum_tech/cordis_quantum_projects.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n=== CORDIS QUANTUM ANALYSIS ===")
    print(f"Total quantum projects: {report['total_quantum_projects']}")
    print(f"Total EU funding: €{report['total_eu_funding']:,.0f}")
    print(f"\nTop 10 Countries:")
    for country, count in report['top_countries'][:10]:
        print(f"  {country}: {count} projects")
    print(f"\nTop 10 Coordinators:")
    for org, count in report['top_coordinators'][:10]:
        print(f"  {org}: {count} projects")

    print(f"\nReport saved to: {output_path}")

    return report

if __name__ == '__main__':
    search_quantum_projects()
