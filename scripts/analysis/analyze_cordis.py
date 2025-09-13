#!/usr/bin/env python3
"""
CORDIS Data Analysis for Slovakia Research Security
Analyzes EU-funded projects for Slovak-China collaborations
"""

import json
import csv
from collections import defaultdict, Counter
from datetime import datetime

def load_json_file(filepath):
    """Load JSON file with proper encoding"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []

def analyze_slovak_organizations():
    """Find and analyze Slovak organizations"""
    print("\n=== ANALYZING SLOVAK ORGANIZATIONS ===")
    
    orgs = load_json_file('out/SK/cordis_data/organization.json')
    projects = load_json_file('out/SK/cordis_data/project.json')
    
    # Find Slovak organizations
    slovak_orgs = {}
    chinese_orgs = {}
    
    for org in orgs:
        country_code = org.get('country', '')
        org_id = org.get('organisationID', org.get('id', ''))
        
        if country_code == 'SK':
            slovak_orgs[org_id] = {
                'id': org_id,
                'name': org.get('name', 'Unknown'),
                'shortName': org.get('shortName', ''),
                'projects': [],
                'projectID': org.get('projectID', ''),
                'ecContribution': float(org.get('netEcContribution', 0) or 0)
            }
        elif country_code == 'CN':
            chinese_orgs[org_id] = {
                'id': org_id,
                'name': org.get('name', 'Unknown'),
                'projects': [],
                'projectID': org.get('projectID', '')
            }
    
    print(f"Found {len(slovak_orgs)} Slovak organizations")
    print(f"Found {len(chinese_orgs)} Chinese organizations")
    
    # Build project-org mapping from organization data
    project_org_map = defaultdict(list)
    for org_id, org_data in slovak_orgs.items():
        if org_data['projectID']:
            project_org_map[org_data['projectID']].append(org_id)
    
    for org_id, org_data in chinese_orgs.items():
        if org_data['projectID']:
            project_org_map[org_data['projectID']].append(org_id)
    
    # Analyze projects
    slovak_projects = []
    joint_projects = []
    
    for project in projects:
        project_id = project.get('id', '')
        
        # Check if this project has Slovak or Chinese participants
        participant_org_ids = project_org_map.get(project_id, [])
        
        has_slovak = any(org_id in slovak_orgs for org_id in participant_org_ids)
        has_chinese = any(org_id in chinese_orgs for org_id in participant_org_ids)
        
        if has_slovak or project_id in project_org_map:
            project_data = {
                'id': project.get('id'),
                'acronym': project.get('acronym', ''),
                'title': project.get('title', ''),
                'startDate': project.get('startDate', ''),
                'endDate': project.get('endDate', ''),
                'totalCost': project.get('totalCost', 0),
                'participants': participant_org_ids,
                'has_chinese': has_chinese
            }
            
            slovak_projects.append(project_data)
            
            if has_chinese:
                joint_projects.append(project_data)
                
            # Track projects for each org
            for org_id in participant_org_ids:
                if org_id in slovak_orgs:
                    slovak_orgs[org_id]['projects'].append(project_id)
                if org_id in chinese_orgs:
                    chinese_orgs[org_id]['projects'].append(project_id)
    
    print(f"\nFound {len(slovak_projects)} projects with Slovak participation")
    print(f"Found {len(joint_projects)} Slovak-Chinese joint projects")
    
    # Top Slovak institutions by project count
    print("\n=== TOP SLOVAK INSTITUTIONS BY PROJECT COUNT ===")
    sorted_orgs = sorted(slovak_orgs.values(), key=lambda x: len(x['projects']), reverse=True)[:15]
    
    results = []
    for org in sorted_orgs:
        result = {
            'name': org['name'],
            'shortName': org['shortName'],
            'project_count': len(org['projects'])
        }
        results.append(result)
        print(f"{org['name']}: {len(org['projects'])} projects")
    
    # Save results
    with open('out/SK/cordis_slovak_institutions.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'shortName', 'project_count'])
        writer.writeheader()
        writer.writerows(results)
    
    return slovak_projects, joint_projects, slovak_orgs

def analyze_technology_domains(projects):
    """Analyze technology domains and topics"""
    print("\n=== TECHNOLOGY DOMAIN ANALYSIS ===")
    
    topics = load_json_file('out/SK/cordis_data/topics.json')
    euroscivoc = load_json_file('out/SK/cordis_data/euroSciVoc.json')
    
    # Create topic lookup (handle different structures)
    topic_lookup = {}
    for t in topics:
        if isinstance(t, dict):
            code = t.get('code', t.get('id', ''))
            if code:
                topic_lookup[code] = t.get('title', t.get('name', ''))
    
    # Count domains
    domain_counter = Counter()
    critical_tech_projects = []
    
    critical_keywords = [
        'quantum', 'artificial intelligence', 'AI', 'machine learning',
        'biotechnology', 'semiconductor', 'nanotechnology', '5G', '6G',
        'cyber', 'security', 'defense', 'space', 'satellite'
    ]
    
    for project in projects:
        title = project.get('title', '').lower()
        
        # Check for critical technologies
        is_critical = any(kw in title for kw in critical_keywords)
        if is_critical:
            critical_tech_projects.append(project)
    
    print(f"Found {len(critical_tech_projects)} projects in critical technology areas")
    
    # Save critical projects
    with open('out/SK/cordis_critical_tech.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'acronym', 'title', 'startDate', 'totalCost', 'has_chinese'])
        writer.writeheader()
        for p in critical_tech_projects:
            writer.writerow({
                'id': p['id'],
                'acronym': p['acronym'],
                'title': p['title'],
                'startDate': p['startDate'],
                'totalCost': p['totalCost'],
                'has_chinese': p.get('has_chinese', False)
            })
    
    return critical_tech_projects

def analyze_joint_projects(joint_projects, slovak_orgs):
    """Detailed analysis of Slovak-Chinese joint projects"""
    print("\n=== SLOVAK-CHINESE JOINT PROJECTS ANALYSIS ===")
    
    if not joint_projects:
        print("No direct Slovak-Chinese joint projects found")
        return
    
    print(f"\nFound {len(joint_projects)} joint projects:")
    
    results = []
    for project in joint_projects:
        print(f"\nProject: {project['acronym']} - {project['title']}")
        print(f"  Period: {project['startDate']} to {project['endDate']}")
        total_cost = project.get('totalCost', 0)
        if isinstance(total_cost, str):
            total_cost = float(total_cost) if total_cost else 0
        print(f"  Total Cost: €{total_cost:,.2f}")
        
        # Find Slovak participants
        slovak_participants = []
        for pid in project['participants']:
            if pid in slovak_orgs:
                slovak_participants.append(slovak_orgs[pid]['name'])
        
        print(f"  Slovak participants: {', '.join(slovak_participants)}")
        
        results.append({
            'project_id': project['id'],
            'acronym': project['acronym'],
            'title': project['title'],
            'startDate': project['startDate'],
            'endDate': project['endDate'],
            'totalCost': project['totalCost'],
            'slovak_participants': '; '.join(slovak_participants)
        })
    
    # Save joint projects
    with open('out/SK/cordis_slovak_chinese_joint.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['project_id', 'acronym', 'title', 'startDate', 'endDate', 'totalCost', 'slovak_participants'])
        writer.writeheader()
        writer.writerows(results)

def analyze_funding_flows(slovak_projects):
    """Analyze funding patterns and concentrations"""
    print("\n=== FUNDING ANALYSIS ===")
    
    total_funding = sum(p.get('totalCost', 0) for p in slovak_projects)
    projects_with_dates = [p for p in slovak_projects if p.get('startDate')]
    
    # Group by year
    yearly_funding = defaultdict(lambda: {'count': 0, 'total': 0})
    for project in projects_with_dates:
        try:
            year = project['startDate'][:4]
            yearly_funding[year]['count'] += 1
            yearly_funding[year]['total'] += project.get('totalCost', 0)
        except:
            continue
    
    print(f"Total EU funding to Slovak projects: €{total_funding:,.2f}")
    print("\nFunding by year:")
    for year in sorted(yearly_funding.keys()):
        data = yearly_funding[year]
        print(f"  {year}: {data['count']} projects, €{data['total']:,.2f}")
    
    # Calculate concentration
    large_projects = [p for p in slovak_projects if p.get('totalCost', 0) > 1000000]
    print(f"\nProjects > €1M: {len(large_projects)} ({len(large_projects)/len(slovak_projects)*100:.1f}%)")

def main():
    """Main analysis function"""
    print("CORDIS Data Analysis for Slovakia")
    print("=" * 50)
    
    # Analyze organizations and projects
    slovak_projects, joint_projects, slovak_orgs = analyze_slovak_organizations()
    
    # Analyze technology domains
    critical_projects = analyze_technology_domains(slovak_projects)
    
    # Analyze joint projects
    analyze_joint_projects(joint_projects, slovak_orgs)
    
    # Analyze funding
    analyze_funding_flows(slovak_projects)
    
    # Generate summary report
    print("\n" + "=" * 50)
    print("SUMMARY REPORT")
    print("=" * 50)
    print(f"Slovak organizations in HORIZON: {len(slovak_orgs)}")
    print(f"Projects with Slovak participation: {len(slovak_projects)}")
    print(f"Slovak-Chinese joint projects: {len(joint_projects)}")
    print(f"Critical technology projects: {len(critical_projects)}")
    
    # Risk assessment
    risk_score = 0
    if len(joint_projects) > 0:
        risk_score += 30
    if len(critical_projects) > 10:
        risk_score += 20
    if any(p.get('has_chinese') for p in critical_projects):
        risk_score += 50
    
    print(f"\nRISK ASSESSMENT: {risk_score}/100")
    if risk_score >= 50:
        print("WARNING: High risk of technology transfer detected")
    elif risk_score >= 30:
        print("CAUTION: Medium risk - monitoring required")
    else:
        print("Low risk profile in HORIZON program")
    
    print("\nOutput files created:")
    print("  - out/SK/cordis_slovak_institutions.csv")
    print("  - out/SK/cordis_critical_tech.csv")
    print("  - out/SK/cordis_slovak_chinese_joint.csv")

if __name__ == "__main__":
    main()