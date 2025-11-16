#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extract Enhanced Chinese Entity Lists for Patent Detection
Extracts: SOEs, Universities, Government Entities from ASPI datasets
"""

import json
import csv
import sys

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def extract_aspi_universities():
    """Extract universities from ASPI MISP dataset"""
    universities = set()
    military_institutions = set()
    seven_sons_explicit = {
        'BEIHANG UNIVERSITY',
        'BEIJING INSTITUTE OF TECHNOLOGY',
        'HARBIN INSTITUTE OF TECHNOLOGY',
        'HARBIN ENGINEERING UNIVERSITY',
        'NORTHWESTERN POLYTECHNICAL UNIVERSITY',
        'NANJING UNIVERSITY OF AERONAUTICS AND ASTRONAUTICS',
        'NANJING UNIVERSITY OF SCIENCE AND TECHNOLOGY'
    }
    seven_sons = set()
    defense_conglomerates = set()
    defense_research_institutes = set()

    with open('C:/Projects/OSINT - Foresight/data/external/aspi/MISP_china_defence_universities.json',
              'r', encoding='utf-8') as f:
        aspi_data = json.load(f)

    for item in aspi_data.get('values', []):
        name = item.get('value', '')
        if name:
            name_upper = name.upper()
            universities.add(name_upper)

            # Add synonyms/aliases
            if 'meta' in item and 'aliases' in item['meta']:
                for alias in item['meta']['aliases']:
                    universities.add(alias.upper())

            # Categorize by type
            if 'meta' in item:
                categories = item['meta'].get('categories', [])
                if isinstance(categories, str):
                    categories = [categories]

                for cat in categories:
                    cat_lower = cat.lower()
                    if 'military' in cat_lower:
                        military_institutions.add(name_upper)
                    elif 'defense industry' in cat_lower or 'conglomerate' in cat_lower:
                        defense_conglomerates.add(name_upper)

                # Check if it's in Seven Sons
                # Extract just the English name (before Chinese characters)
                english_name = name.split('(')[0].strip().upper()
                if english_name in seven_sons_explicit or any(seven in english_name for seven in seven_sons_explicit):
                    seven_sons.add(name_upper)

                # Check for research institutes
                if 'RESEARCH' in name_upper or 'INSTITUTE' in name_upper or 'ACADEMY' in name_upper:
                    if any(word in name_upper for word in ['CHINA', 'CHINESE', 'NATIONAL', 'PLA', '人民解放军']):
                        defense_research_institutes.add(name_upper)

    return {
        'all_universities': universities,
        'military_institutions': military_institutions,
        'seven_sons': seven_sons,
        'defense_conglomerates': defense_conglomerates,
        'defense_research_institutes': defense_research_institutes
    }

def extract_aspi_companies():
    """Extract companies from ASPI China Tech Map dataset"""
    companies = set()
    soe_companies = set()
    private_companies = set()

    with open('C:/Users/mrear/Downloads/data.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            company_str = row.get('Company', '')
            if company_str:
                # Extract company name (format is 'ID | Company Name')
                parts = company_str.split('|')
                if len(parts) == 2:
                    company = parts[1].strip().upper()
                    companies.add(company)

                    # Categorize by ownership
                    ownership = row.get('ownership_structure_id_ref', '')
                    if 'State-owned' in ownership:
                        soe_companies.add(company)
                    elif 'Private' in ownership:
                        private_companies.add(company)

    return {
        'all_companies': companies,
        'soe_companies': soe_companies,
        'private_companies': private_companies
    }

def add_known_soes():
    """Add known major Chinese SOEs not in ASPI data"""
    major_soes = {
        # Defense Industry
        'CHINA AEROSPACE SCIENCE AND TECHNOLOGY CORPORATION', 'CASC',
        'CHINA AEROSPACE SCIENCE AND INDUSTRY CORPORATION', 'CASIC',
        'AVIATION INDUSTRY CORPORATION OF CHINA', 'AVIC',
        'CHINA STATE SHIPBUILDING CORPORATION', 'CSSC',
        'CHINA NORTH INDUSTRIES GROUP CORPORATION', 'NORINCO',
        'CHINA SOUTH INDUSTRIES GROUP CORPORATION',
        'CHINA ELECTRONICS TECHNOLOGY GROUP CORPORATION', 'CETC',
        'CHINA NATIONAL NUCLEAR CORPORATION', 'CNNC',

        # Telecommunications
        'CHINA MOBILE',
        'CHINA TELECOM',
        'CHINA UNICOM',

        # Energy
        'STATE GRID CORPORATION OF CHINA',
        'CHINA NATIONAL PETROLEUM CORPORATION', 'CNPC',
        'SINOPEC',
        'CHINA NATIONAL OFFSHORE OIL CORPORATION', 'CNOOC',

        # Manufacturing
        'CHINA RAILWAY GROUP',
        'CHINA RAILWAY CONSTRUCTION CORPORATION',
        'CHINA COMMUNICATIONS CONSTRUCTION COMPANY',
        'CHINA METALLURGICAL GROUP CORPORATION',

        # Technology
        'CHINA ELECTRONICS CORPORATION', 'CEC',
        'CHINA SOFTWARE CORPORATION',

        # Finance
        'BANK OF CHINA',
        'INDUSTRIAL AND COMMERCIAL BANK OF CHINA', 'ICBC',
        'CHINA CONSTRUCTION BANK',
        'AGRICULTURAL BANK OF CHINA',
    }
    return major_soes

def add_government_entities():
    """Add Chinese government entity patterns"""
    government_entities = {
        # National Level
        'CHINESE ACADEMY OF SCIENCES', 'CAS',
        'CHINESE ACADEMY OF ENGINEERING',
        'CHINESE ACADEMY OF SOCIAL SCIENCES',
        'STATE COUNCIL',
        'MINISTRY OF SCIENCE AND TECHNOLOGY',
        'MINISTRY OF INDUSTRY AND INFORMATION TECHNOLOGY', 'MIIT',
        'MINISTRY OF NATIONAL DEFENSE',
        'PEOPLE\'S LIBERATION ARMY', 'PLA',

        # Research Institutes
        'CHINA ACADEMY OF ENGINEERING PHYSICS', 'CAEP',
        'CHINA ELECTRONICS TECHNOLOGY GROUP',

        # Provincial patterns (will be matched with province names)
        'PROVINCIAL GOVERNMENT',
        'PROVINCIAL ACADEMY',
        'PROVINCIAL INSTITUTE',

        # Municipal patterns (will be matched with city names)
        'MUNICIPAL GOVERNMENT',
        'MUNICIPAL BUREAU',
        'MUNICIPAL INSTITUTE',
    }
    return government_entities

def main():
    print("="*80)
    print("EXTRACTING ENHANCED CHINESE ENTITY LISTS")
    print("="*80)

    # Extract from ASPI datasets
    print("\n1. Extracting universities from ASPI MISP dataset...")
    univ_data = extract_aspi_universities()
    print(f"   Total universities/institutions: {len(univ_data['all_universities'])}")
    print(f"   Military institutions: {len(univ_data['military_institutions'])}")
    print(f"   Seven Sons of Defense: {len(univ_data['seven_sons'])}")
    print(f"   Defense conglomerates: {len(univ_data['defense_conglomerates'])}")
    print(f"   Defense research institutes: {len(univ_data['defense_research_institutes'])}")

    print("\n2. Extracting companies from ASPI China Tech Map...")
    company_data = extract_aspi_companies()
    print(f"   Total companies: {len(company_data['all_companies'])}")
    print(f"   SOE companies: {len(company_data['soe_companies'])}")
    print(f"   Private companies: {len(company_data['private_companies'])}")

    print("\n3. Adding known major SOEs...")
    major_soes = add_known_soes()
    print(f"   Additional SOEs: {len(major_soes)}")

    print("\n4. Adding government entities...")
    gov_entities = add_government_entities()
    print(f"   Government entities: {len(gov_entities)}")

    # Combine all
    all_soes = company_data['soe_companies'].union(major_soes)
    all_companies = company_data['all_companies'].union(major_soes)

    # Also include defense conglomerates in SOEs
    all_soes = all_soes.union(univ_data['defense_conglomerates'])

    # Create comprehensive entity dictionary
    entity_dict = {
        'universities': {
            'all': sorted(list(univ_data['all_universities'])),
            'military': sorted(list(univ_data['military_institutions'])),
            'seven_sons': sorted(list(univ_data['seven_sons'])),
            'defense_research_institutes': sorted(list(univ_data['defense_research_institutes']))
        },
        'companies': {
            'all': sorted(list(all_companies)),
            'soe': sorted(list(all_soes)),
            'private': sorted(list(company_data['private_companies'])),
            'defense_conglomerates': sorted(list(univ_data['defense_conglomerates']))
        },
        'government': {
            'entities': sorted(list(gov_entities))
        },
        'statistics': {
            'total_universities': len(univ_data['all_universities']),
            'total_military_institutions': len(univ_data['military_institutions']),
            'total_seven_sons': len(univ_data['seven_sons']),
            'total_defense_research_institutes': len(univ_data['defense_research_institutes']),
            'total_companies': len(all_companies),
            'total_soes': len(all_soes),
            'total_defense_conglomerates': len(univ_data['defense_conglomerates']),
            'total_government_entities': len(gov_entities)
        }
    }

    # Save to JSON
    output_file = 'C:/Projects/OSINT - Foresight/data/chinese_entities_enhanced.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(entity_dict, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print("EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"\nSaved to: {output_file}")
    print(f"\nTotal entities extracted:")
    print(f"  Universities: {entity_dict['statistics']['total_universities']}")
    print(f"  Military Institutions: {entity_dict['statistics']['total_military_institutions']}")
    print(f"  Seven Sons: {entity_dict['statistics']['total_seven_sons']}")
    print(f"  Defense Research Institutes: {entity_dict['statistics']['total_defense_research_institutes']}")
    print(f"  Companies: {entity_dict['statistics']['total_companies']}")
    print(f"  SOEs: {entity_dict['statistics']['total_soes']}")
    print(f"  Defense Conglomerates: {entity_dict['statistics']['total_defense_conglomerates']}")
    print(f"  Government: {entity_dict['statistics']['total_government_entities']}")

    # Print sample of each category
    print(f"\n{'='*80}")
    print("SAMPLE ENTITIES")
    print(f"{'='*80}")

    print("\nSeven Sons of Defense (ALL):")
    for univ in entity_dict['universities']['seven_sons']:
        print(f"  - {univ}")

    print("\nDefense Conglomerates (sample - first 10):")
    for company in entity_dict['companies']['defense_conglomerates'][:10]:
        print(f"  - {company}")

    print("\nSOE Companies (sample - first 10):")
    for company in entity_dict['companies']['soe'][:10]:
        print(f"  - {company}")

    print("\nGovernment Entities (sample - first 10):")
    for entity in entity_dict['government']['entities'][:10]:
        print(f"  - {entity}")

    print("\nMilitary Institutions (sample - first 10):")
    for inst in sorted(list(entity_dict['universities']['military']))[:10]:
        print(f"  - {inst}")

if __name__ == '__main__':
    main()
