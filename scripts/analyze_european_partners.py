#!/usr/bin/env python3
"""
Analyze European partners of the 68 overlapping Chinese institutions
"""

import json
from pathlib import Path
from collections import defaultdict

# Load the 68 overlapping institutions
overlap_file = Path('data/processed/phase2_20251005_093031/correlation_analysis/cordis_openaire_overlap_analysis.json')
with open(overlap_file, 'r', encoding='utf-8') as f:
    overlap_data = json.load(f)

# Get list of the 68 institution names
overlap_names = {o['entity_name'].lower() for o in overlap_data['all_overlaps']}

print(f'Analyzing European partners for {len(overlap_names)} Chinese institutions...')
print()

# Load CORDIS detections to get project IDs
cordis_det = Path('data/processed/cordis_v1/detections.ndjson')

# Collect all project IDs from Chinese institutions
chinese_projects = set()
with open(cordis_det, 'r', encoding='utf-8') as f:
    for line in f:
        det = json.loads(line)
        entity_name = det.get('entity_name', '').lower()
        if entity_name in overlap_names:
            chinese_projects.add(det.get('project_id'))

print(f'Found {len(chinese_projects)} unique EU projects involving the 68 institutions')
print()
print('Loading full CORDIS organization data to find European partners...')

# Load organizations to map project participants
# CORDIS has organization.json in projects directory
orgs_h2020 = Path('countries/_global/data/cordis_raw/h2020/projects/organization.json')
orgs_horizon = Path('countries/_global/data/cordis_raw/horizon/projects/organization.json')

all_orgs = []

if orgs_h2020.exists():
    with open(orgs_h2020, 'r', encoding='utf-8') as f:
        all_orgs.extend(json.load(f))
    print(f'Loaded {len(all_orgs)} H2020 organizations')

if orgs_horizon.exists():
    with open(orgs_horizon, 'r', encoding='utf-8') as f:
        horizon_orgs = json.load(f)
        all_orgs.extend(horizon_orgs)
    print(f'Loaded {len(horizon_orgs)} Horizon organizations')

if all_orgs:

    print(f'Loaded {len(all_orgs)} total organizations')

    # Build project -> participants mapping
    project_orgs = defaultdict(list)
    for org in all_orgs:
        proj_id = org.get('projectID')
        if proj_id in chinese_projects:
            project_orgs[proj_id].append(org)

    # Analyze European partners
    eu_partners = defaultdict(lambda: {
        'projects': set(),
        'chinese_collaborators': set(),
        'country': None
    })

    # EU country codes
    eu_countries = {
        'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
        'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
        'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'GB', 'NO', 'IS', 'CH'
    }

    for proj_id, orgs in project_orgs.items():
        # Separate Chinese and European orgs
        chinese_in_project = []
        european_in_project = []

        for org in orgs:
            org_name = str(org.get('name', '')).lower()
            org_country = str(org.get('country', '')).upper()

            if org_name in overlap_names:
                chinese_in_project.append(org_name)
            elif org_country in eu_countries:
                european_in_project.append((org.get('name'), org_country))

        # Record partnerships
        for eu_org_name, eu_country in european_in_project:
            for cn_org in chinese_in_project:
                eu_partners[eu_org_name]['projects'].add(proj_id)
                eu_partners[eu_org_name]['chinese_collaborators'].add(cn_org)
                eu_partners[eu_org_name]['country'] = eu_country

    # Sort by number of collaborations
    sorted_partners = sorted(
        eu_partners.items(),
        key=lambda x: (len(x[1]['projects']), len(x[1]['chinese_collaborators'])),
        reverse=True
    )

    print('='*80)
    print('TOP 50 EUROPEAN PARTNERS OF THE 68 CHINESE INSTITUTIONS')
    print('='*80)
    print()

    for i, (org_name, data) in enumerate(sorted_partners[:50], 1):
        print(f'{i:2d}. {org_name} ({data["country"]})')
        print(f'    {len(data["projects"])} projects | {len(data["chinese_collaborators"])} Chinese institutions')
        print()

    # Country analysis
    country_stats = defaultdict(lambda: {'orgs': set(), 'projects': set(), 'chinese_partners': set()})

    for org_name, data in eu_partners.items():
        country = data['country']
        country_stats[country]['orgs'].add(org_name)
        country_stats[country]['projects'].update(data['projects'])
        country_stats[country]['chinese_partners'].update(data['chinese_collaborators'])

    print('='*80)
    print('EUROPEAN COUNTRIES BY COLLABORATION INTENSITY')
    print('='*80)
    print()

    sorted_countries = sorted(
        country_stats.items(),
        key=lambda x: len(x[1]['projects']),
        reverse=True
    )

    for country, stats in sorted_countries[:20]:
        print(f'{country}: {len(stats["projects"])} projects | {len(stats["orgs"])} institutions | {len(stats["chinese_partners"])} Chinese partners')

    # Save detailed results
    output = {
        'summary': {
            'total_eu_partners': len(eu_partners),
            'total_projects': len(chinese_projects),
            'total_chinese_institutions': len(overlap_names)
        },
        'top_50_partners': [],
        'country_breakdown': []
    }

    for org_name, data in sorted_partners[:50]:
        output['top_50_partners'].append({
            'organization': org_name,
            'country': data['country'],
            'projects': len(data['projects']),
            'chinese_collaborators': len(data['chinese_collaborators']),
            'sample_chinese_partners': sorted(list(data['chinese_collaborators']))[:5]
        })

    for country, stats in sorted_countries:
        output['country_breakdown'].append({
            'country': country,
            'projects': len(stats['projects']),
            'institutions': len(stats['orgs']),
            'chinese_partners': len(stats['chinese_partners'])
        })

    output_file = Path('data/processed/phase2_20251005_093031/correlation_analysis/european_partners_analysis.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print()
    print('='*80)
    print(f'Full analysis saved to: {output_file}')
    print('='*80)

else:
    print('No organizations data found')
