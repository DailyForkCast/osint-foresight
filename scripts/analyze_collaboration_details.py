#!/usr/bin/env python3
"""
Detailed analysis of Chinese-European collaborations:
- Temporal trends by institution
- Research topics and domains
- Partner evolution over time
"""

import json
from pathlib import Path
from collections import defaultdict
import re

# Load the 68 overlapping institutions
overlap_file = Path('data/processed/phase2_20251005_093031/correlation_analysis/cordis_openaire_overlap_analysis.json')
with open(overlap_file, 'r', encoding='utf-8') as f:
    overlap_data = json.load(f)

overlap_names = {o['entity_name'].lower() for o in overlap_data['all_overlaps']}

print('='*80)
print('TEMPORAL & TOPICAL ANALYSIS OF CHINESE-EUROPEAN COLLABORATIONS')
print('='*80)
print()

# Load CORDIS projects data
projects_h2020 = Path('countries/_global/data/cordis_raw/h2020/projects/project.json')
projects_horizon = Path('countries/_global/data/cordis_raw/horizon/projects/project.json')

all_projects = []

if projects_h2020.exists():
    with open(projects_h2020, 'r', encoding='utf-8') as f:
        all_projects.extend(json.load(f))
    print(f'Loaded {len(all_projects)} H2020 projects')

if projects_horizon.exists():
    with open(projects_horizon, 'r', encoding='utf-8') as f:
        horizon_projects = json.load(f)
        all_projects.extend(horizon_projects)
    print(f'Loaded {len(horizon_projects)} Horizon projects')

print(f'Total projects loaded: {len(all_projects)}')
print()

# Load organizations
orgs_h2020 = Path('countries/_global/data/cordis_raw/h2020/projects/organization.json')
orgs_horizon = Path('countries/_global/data/cordis_raw/horizon/projects/organization.json')

all_orgs = []

if orgs_h2020.exists():
    with open(orgs_h2020, 'r', encoding='utf-8') as f:
        all_orgs.extend(json.load(f))

if orgs_horizon.exists():
    with open(orgs_horizon, 'r', encoding='utf-8') as f:
        all_orgs.extend(json.load(f))

print(f'Loaded {len(all_orgs)} organizations')
print()

# Build project -> details mapping
project_details = {}
for proj in all_projects:
    proj_id = proj.get('id')
    project_details[proj_id] = {
        'title': proj.get('title', 'Unknown'),
        'objective': proj.get('objective', ''),
        'start_date': proj.get('startDate', ''),
        'end_date': proj.get('endDate', ''),
        'funding': proj.get('totalCost', 0),
        'topics': proj.get('topics', ''),
        'frameworkProgramme': proj.get('frameworkProgramme', '')
    }

# Build project -> participants mapping
project_participants = defaultdict(list)
for org in all_orgs:
    proj_id = org.get('projectID')
    project_participants[proj_id].append({
        'name': str(org.get('name', '')),
        'country': str(org.get('country', '')).upper(),
        'role': org.get('activityType', ''),
        'funding': org.get('ecContribution', 0)
    })

# Find projects with Chinese participation
chinese_projects_detailed = []

for proj_id, participants in project_participants.items():
    # Check for Chinese participation
    chinese_orgs = []
    european_orgs = []

    eu_countries = {
        'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
        'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
        'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'GB', 'NO', 'IS', 'CH'
    }

    for p in participants:
        if p['name'].lower() in overlap_names:
            chinese_orgs.append(p)
        elif p['country'] in eu_countries:
            european_orgs.append(p)

    if chinese_orgs and proj_id in project_details:
        details = project_details[proj_id]

        # Extract year from start date (format: YYYY-MM-DD)
        year = 'Unknown'
        if details['start_date']:
            year_match = re.match(r'(\d{4})', details['start_date'])
            if year_match:
                year = year_match.group(1)

        chinese_projects_detailed.append({
            'project_id': proj_id,
            'title': details['title'],
            'year': year,
            'start_date': details['start_date'],
            'end_date': details['end_date'],
            'objective': details['objective'][:500] if details['objective'] else '',  # Truncate
            'topics': details['topics'],
            'total_funding': details['funding'],
            'chinese_participants': chinese_orgs,
            'european_participants': european_orgs,
            'total_participants': len(participants)
        })

print(f'Found {len(chinese_projects_detailed)} projects with the 68 institutions')
print()

# Temporal analysis by institution
institution_timeline = defaultdict(lambda: defaultdict(list))

for proj in chinese_projects_detailed:
    year = proj['year']
    for cn_org in proj['chinese_participants']:
        institution_timeline[cn_org['name']][year].append({
            'project_id': proj['project_id'],
            'title': proj['title'],
            'eu_partners': [p['name'] for p in proj['european_participants'][:5]]  # Top 5
        })

# Topic analysis
topic_analysis = defaultdict(lambda: {
    'projects': [],
    'institutions': set(),
    'years': set()
})

# Extract topics from project titles and objectives
def extract_research_domains(text):
    """Extract research domains from text"""
    domains = []

    keywords = {
        'AI/Machine Learning': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network'],
        'Climate/Environment': ['climate', 'environment', 'sustainability', 'carbon', 'emission', 'renewable'],
        'Health/Medicine': ['health', 'medical', 'disease', 'cancer', 'drug', 'therapy', 'clinical'],
        'Materials Science': ['material', 'nanotechnology', 'polymer', 'composite', 'graphene'],
        'Energy': ['energy', 'battery', 'solar', 'fuel cell', 'hydrogen', 'nuclear'],
        'Agriculture/Food': ['agriculture', 'food', 'crop', 'farming', 'livestock', 'nutrition'],
        'ICT/Networks': ['network', 'communication', '5g', '6g', 'internet', 'wireless', 'iot'],
        'Manufacturing': ['manufacturing', 'industry 4.0', 'automation', 'robotics', 'production'],
        'Transport': ['transport', 'mobility', 'vehicle', 'aviation', 'maritime', 'railway'],
        'Space/Aerospace': ['space', 'satellite', 'aerospace', 'navigation'],
        'Quantum': ['quantum', 'qubit'],
        'Cybersecurity': ['security', 'cyber', 'privacy', 'encryption'],
        'Water': ['water', 'ocean', 'marine', 'aquatic'],
        'Urban/Smart Cities': ['urban', 'city', 'smart cities', 'infrastructure']
    }

    text_lower = text.lower()
    for domain, keywords_list in keywords.items():
        for keyword in keywords_list:
            if keyword in text_lower:
                domains.append(domain)
                break

    return domains if domains else ['Other']

for proj in chinese_projects_detailed:
    text = f"{proj['title']} {proj['objective']}"
    domains = extract_research_domains(text)

    for domain in domains:
        topic_analysis[domain]['projects'].append(proj['project_id'])
        topic_analysis[domain]['years'].add(proj['year'])
        for cn_org in proj['chinese_participants']:
            topic_analysis[domain]['institutions'].add(cn_org['name'])

# Sort institutions by total project count
institution_totals = {
    name: sum(len(years_data) for years_data in timeline.values())
    for name, timeline in institution_timeline.items()
}

sorted_institutions = sorted(
    institution_totals.items(),
    key=lambda x: x[1],
    reverse=True
)

print('='*80)
print('TOP 20 INSTITUTIONS BY TEMPORAL ACTIVITY')
print('='*80)
print()

for inst_name, total_projects in sorted_institutions[:20]:
    timeline = institution_timeline[inst_name]
    years = sorted([y for y in timeline.keys() if y != 'Unknown'])

    print(f'{inst_name}')
    print(f'  Total projects: {total_projects}')
    if years:
        print(f'  Period: {years[0]} - {years[-1]}')
        print(f'  Yearly breakdown:')
        for year in years[-5:]:  # Last 5 years
            proj_count = len(timeline[year])
            print(f'    {year}: {proj_count} projects')
    print()

print('='*80)
print('RESEARCH DOMAINS ANALYSIS')
print('='*80)
print()

sorted_topics = sorted(
    topic_analysis.items(),
    key=lambda x: len(x[1]['projects']),
    reverse=True
)

for topic, data in sorted_topics:
    print(f'{topic}')
    print(f'  Projects: {len(data["projects"])}')
    print(f'  Chinese institutions involved: {len(data["institutions"])}')
    print(f'  Active years: {", ".join(sorted([y for y in data["years"] if y != "Unknown"]))}')
    print()

# Save detailed output
output = {
    'summary': {
        'total_projects': len(chinese_projects_detailed),
        'total_institutions': len(institution_timeline),
        'year_range': {
            'earliest': min([p['year'] for p in chinese_projects_detailed if p['year'] != 'Unknown'], default='Unknown'),
            'latest': max([p['year'] for p in chinese_projects_detailed if p['year'] != 'Unknown'], default='Unknown')
        }
    },
    'institution_timelines': {},
    'research_domains': {},
    'sample_projects': []
}

# Institution timelines
for inst_name, timeline in sorted(institution_timeline.items(), key=lambda x: institution_totals.get(x[0], 0), reverse=True)[:30]:
    output['institution_timelines'][inst_name] = {
        'total_projects': institution_totals[inst_name],
        'by_year': {year: len(projects) for year, projects in timeline.items()},
        'sample_projects': {
            year: [{'id': p['project_id'], 'title': p['title'], 'partners': p['eu_partners']}
                   for p in projects[:3]]
            for year, projects in sorted(timeline.items(), reverse=True)[:3]
        }
    }

# Research domains
for topic, data in sorted_topics:
    output['research_domains'][topic] = {
        'project_count': len(data['projects']),
        'institution_count': len(data['institutions']),
        'active_years': sorted([y for y in data['years'] if y != 'Unknown']),
        'top_institutions': sorted(list(data['institutions']))[:10]
    }

# Sample projects for each domain
for proj in chinese_projects_detailed[:50]:  # Top 50 projects
    text = f"{proj['title']} {proj['objective']}"
    domains = extract_research_domains(text)

    output['sample_projects'].append({
        'project_id': proj['project_id'],
        'title': proj['title'],
        'year': proj['year'],
        'domains': domains,
        'chinese_participants': [p['name'] for p in proj['chinese_participants']],
        'top_eu_partners': [p['name'] for p in proj['european_participants'][:5]],
        'objective_excerpt': proj['objective'][:300]
    })

output_file = Path('data/processed/phase2_20251005_093031/correlation_analysis/collaboration_details_analysis.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('='*80)
print(f'Full analysis saved to: {output_file}')
print('='*80)
