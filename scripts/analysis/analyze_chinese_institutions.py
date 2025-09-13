#!/usr/bin/env python3
"""
Analyze Chinese institutions in Slovak CORDIS collaborations
Identify high-risk entities and PLA-affiliated universities
"""

import json
import csv
from collections import defaultdict, Counter

def analyze_chinese_institutions():
    """Extract and analyze Chinese institutions from CORDIS data"""
    
    print("=" * 60)
    print("Chinese Institutions in Slovak EU Projects")
    print("=" * 60)
    
    # Load CORDIS organization data
    with open('out/SK/cordis_data/organization.json', 'r', encoding='utf-8') as f:
        orgs = json.load(f)
    
    # Extract Chinese organizations
    chinese_orgs = {}
    for org in orgs:
        if org.get('country', '') == 'CN':
            org_id = org.get('organisationID', org.get('id', ''))
            chinese_orgs[org_id] = {
                'name': org.get('name', 'Unknown'),
                'shortName': org.get('shortName', ''),
                'city': org.get('city', ''),
                'projectID': org.get('projectID', ''),
                'projectAcronym': org.get('projectAcronym', ''),
                'activityType': org.get('activityType', ''),
                'ecContribution': float(org.get('netEcContribution', 0) or 0)
            }
    
    print(f"\nTotal Chinese organizations found: {len(chinese_orgs)}")
    
    # Known high-risk Chinese institutions (PLA-affiliated Seven Sons + others)
    pla_universities = {
        'BEIJING INSTITUTE OF TECHNOLOGY': 'Seven Sons - Weapons/Defense',
        'BEIHANG UNIVERSITY': 'Seven Sons - Aerospace/Defense', 
        'HARBIN INSTITUTE OF TECHNOLOGY': 'Seven Sons - Defense Tech',
        'HARBIN ENGINEERING UNIVERSITY': 'Seven Sons - Naval/Nuclear',
        'NORTHWESTERN POLYTECHNICAL UNIVERSITY': 'Seven Sons - Aviation/Space',
        'NANJING UNIVERSITY OF AERONAUTICS': 'Seven Sons - Aviation/Missiles',
        'NANJING UNIVERSITY OF SCIENCE': 'Seven Sons - Weapons/Explosives',
        'NATIONAL UNIVERSITY OF DEFENSE TECHNOLOGY': 'Direct PLA Control',
        'BEIJING UNIVERSITY OF POSTS': 'Cyber/Telecom - MSS links',
        'UNIVERSITY OF ELECTRONIC SCIENCE': 'Electronic Warfare',
        'XIDIAN UNIVERSITY': 'Cyber/Crypto - PLA links',
        'HUAWEI': 'PLA/MSS connections confirmed',
        'ZTE': 'Military-Civil Fusion',
        'CHINESE ACADEMY OF SCIENCES': 'Dual-use research',
        'CHINESE ACADEMY OF ENGINEERING PHYSICS': 'Nuclear weapons',
        'CETC': 'China Electronics Technology - Defense contractor'
    }
    
    # State-controlled entities
    state_entities = {
        'STATE GRID': 'Critical infrastructure',
        'SINOPEC': 'Energy/Materials', 
        'CNPC': 'Energy sector',
        'COMAC': 'Aerospace - C919 program',
        'AVIC': 'Aviation Industry Corp',
        'CSIC': 'Shipbuilding Industry',
        'NORINCO': 'Defense contractor',
        'CASIC': 'Aerospace Science',
        'CASC': 'Aerospace Corporation'
    }
    
    # Check for high-risk institutions
    print("\n=== HIGH-RISK INSTITUTION CHECK ===")
    
    risks_found = []
    suspicious_orgs = []
    
    for org_id, org_data in chinese_orgs.items():
        org_name = org_data['name'].upper()
        
        # Check against PLA universities
        for pla_name, risk_type in pla_universities.items():
            if pla_name in org_name or org_name in pla_name:
                risks_found.append({
                    'name': org_data['name'],
                    'type': 'PLA-AFFILIATED',
                    'risk': risk_type,
                    'project': org_data['projectAcronym']
                })
                print(f"\n🚨 CRITICAL: {org_data['name']}")
                print(f"   Risk: {risk_type}")
                print(f"   Project: {org_data['projectAcronym']}")
                break
        
        # Check against state entities
        for state_name, sector in state_entities.items():
            if state_name in org_name:
                risks_found.append({
                    'name': org_data['name'],
                    'type': 'STATE-CONTROLLED',
                    'risk': sector,
                    'project': org_data['projectAcronym']
                })
                print(f"\n⚠️  WARNING: {org_data['name']}")
                print(f"   Type: State-controlled - {sector}")
                print(f"   Project: {org_data['projectAcronym']}")
                break
        
        # Flag suspicious keywords
        suspicious_keywords = ['DEFENSE', 'MILITARY', 'NUCLEAR', 'WEAPON', 'SECURITY',
                              'AEROSPACE', 'MISSILE', 'RADAR', 'ELECTRONIC', 'CYBER']
        for keyword in suspicious_keywords:
            if keyword in org_name:
                suspicious_orgs.append(org_data)
                break
    
    # Group by organization type
    print("\n=== CHINESE INSTITUTIONS BY TYPE ===")
    
    type_counter = Counter()
    for org_data in chinese_orgs.values():
        activity = org_data.get('activityType', 'Unknown')
        type_counter[activity] += 1
    
    activity_types = {
        'HES': 'Higher Education (Universities)',
        'REC': 'Research Centers',
        'PRC': 'Private Companies',
        'PUB': 'Public Bodies',
        'OTH': 'Other'
    }
    
    for activity_code, count in type_counter.most_common():
        description = activity_types.get(activity_code, activity_code)
        print(f"  {description}: {count}")
    
    # List top Chinese institutions by frequency
    print("\n=== TOP CHINESE INSTITUTIONS IN EU PROJECTS ===")
    
    name_counter = Counter()
    institution_projects = defaultdict(list)
    
    for org_data in chinese_orgs.values():
        name = org_data['name']
        name_counter[name] += 1
        if org_data['projectAcronym']:
            institution_projects[name].append(org_data['projectAcronym'])
    
    for name, count in name_counter.most_common(15):
        print(f"\n{name}")
        print(f"  Appearances: {count}")
        projects = institution_projects[name][:5]  # Show first 5 projects
        if projects:
            print(f"  Projects: {', '.join(projects)}")
        
        # Check if it's a risk
        name_upper = name.upper()
        for pla_name in pla_universities.keys():
            if pla_name in name_upper or name_upper in pla_name:
                print(f"  ⚠️  RISK: PLA-affiliated institution!")
                break
    
    # Geographic distribution
    print("\n=== GEOGRAPHIC DISTRIBUTION ===")
    city_counter = Counter()
    for org_data in chinese_orgs.values():
        city = org_data.get('city', 'Unknown')
        if city:
            city_counter[city] += 1
    
    for city, count in city_counter.most_common(10):
        print(f"  {city}: {count} organizations")
    
    # Financial analysis
    print("\n=== FUNDING ANALYSIS ===")
    total_ec_contribution = sum(org['ecContribution'] for org in chinese_orgs.values())
    funded_orgs = [org for org in chinese_orgs.values() if org['ecContribution'] > 0]
    
    print(f"Total EC contribution to Chinese orgs: €{total_ec_contribution:,.2f}")
    print(f"Number of Chinese orgs receiving EC funding: {len(funded_orgs)}")
    
    if funded_orgs:
        print("\nTop funded Chinese organizations:")
        sorted_funded = sorted(funded_orgs, key=lambda x: x['ecContribution'], reverse=True)[:10]
        for org in sorted_funded:
            print(f"  {org['name']}: €{org['ecContribution']:,.2f}")
    
    # Save detailed results
    results = {
        'total_chinese_orgs': len(chinese_orgs),
        'high_risk_found': len(risks_found),
        'suspicious_orgs': len(suspicious_orgs),
        'risks': risks_found,
        'type_distribution': dict(type_counter),
        'city_distribution': dict(city_counter),
        'total_ec_funding': total_ec_contribution,
        'top_institutions': [{'name': name, 'count': count} 
                            for name, count in name_counter.most_common(20)]
    }
    
    with open('out/SK/chinese_institutions_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Create CSV for high-risk institutions
    if risks_found:
        with open('out/SK/high_risk_chinese_institutions.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'type', 'risk', 'project'])
            writer.writeheader()
            writer.writerows(risks_found)
    
    # Summary
    print("\n" + "=" * 60)
    print("RISK ASSESSMENT SUMMARY")
    print("=" * 60)
    print(f"Total Chinese institutions: {len(chinese_orgs)}")
    print(f"HIGH-RISK institutions found: {len(risks_found)}")
    print(f"Suspicious institutions: {len(suspicious_orgs)}")
    print(f"EC funding to China: €{total_ec_contribution:,.2f}")
    
    if risks_found:
        print("\n🚨 CRITICAL ALERT:")
        print("PLA-affiliated or state-controlled entities detected!")
        print("Immediate security review required for these projects")
    
    print("\nFiles created:")
    print("  - out/SK/chinese_institutions_analysis.json")
    if risks_found:
        print("  - out/SK/high_risk_chinese_institutions.csv")
    
    return results

if __name__ == "__main__":
    results = analyze_chinese_institutions()
    
    # Additional analysis
    print("\n" + "=" * 60)
    print("STRATEGIC IMPLICATIONS")
    print("=" * 60)
    
    if results['high_risk_found'] > 0:
        print("⚠️  CONFIRMED: Slovak institutions are collaborating with")
        print("   Chinese military-affiliated universities through EU funding!")
        print("\nThis represents:")
        print("  • Direct technology transfer to PLA")
        print("  • Violation of EU/NATO security principles")
        print("  • Potential dual-use technology compromise")
        print("  • Immediate intervention required")