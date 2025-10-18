#!/usr/bin/env python3
"""
Strategic Analysis of Non-EU Europe-China Agreements
Deep dive into patterns, BRI involvement, and geopolitical implications
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import re

class NonEUStrategicAnalyzer:
    """Analyze strategic patterns in non-EU Europe-China agreements"""

    def __init__(self):
        """Initialize analyzer"""
        self.results_dir = Path('athena_results')

        # Strategic corridors and initiatives
        self.strategic_patterns = {
            'middle_corridor': {
                'keywords': ['middle corridor', 'trans-caspian', 'titr', 'traceca'],
                'countries': ['turkey', 'georgia', 'azerbaijan', 'armenia'],
                'significance': 'Alternative to Russian route for China-Europe trade'
            },
            '17_plus_1': {
                'keywords': ['17+1', '16+1', 'ceec', 'china-cee'],
                'countries': ['serbia', 'albania', 'north macedonia', 'montenegro', 'bosnia'],
                'significance': 'China engagement mechanism with Central/Eastern Europe'
            },
            'polar_silk_road': {
                'keywords': ['arctic', 'polar silk road', 'ice silk road', 'northern sea route'],
                'countries': ['norway', 'iceland'],
                'significance': 'Arctic shipping routes and resource extraction'
            },
            'financial_hubs': {
                'keywords': ['rmb', 'yuan', 'clearing', 'fintech', 'stock exchange'],
                'countries': ['uk', 'switzerland'],
                'significance': 'RMB internationalization and financial connectivity'
            },
            'digital_silk_road': {
                'keywords': ['5g', 'huawei', 'zte', 'digital', 'smart city', 'surveillance'],
                'countries': ['serbia', 'turkey'],
                'significance': 'Technology transfer and digital infrastructure'
            }
        }

        # Critical infrastructure types
        self.infrastructure_types = {
            'ports': ['port', 'maritime', 'harbor', 'terminal'],
            'railways': ['railway', 'rail', 'train', 'locomotive'],
            'energy': ['power plant', 'energy', 'nuclear', 'renewable', 'hydropower'],
            'highways': ['highway', 'motorway', 'road', 'bridge'],
            'telecom': ['5g', 'fiber', 'cable', 'telecom', 'network']
        }

        # Chinese state-owned enterprises
        self.chinese_soes = [
            'cosco', 'china railway', 'sinopec', 'cnpc', 'state grid',
            'china construction', 'china communications', 'sinohydro',
            'huawei', 'zte', 'china telecom', 'china mobile'
        ]

    def load_harvest_data(self):
        """Load the non-EU harvest results"""
        harvest_files = sorted(self.results_dir.glob('non_eu_harvest_*.json'))
        if not harvest_files:
            return None

        latest_file = harvest_files[-1]
        print(f"Loading {latest_file}")

        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def analyze_strategic_corridors(self, data):
        """Analyze involvement in strategic corridors"""
        corridor_analysis = {}

        all_results = []
        for region, queries in data['results_by_region'].items():
            for query_name, results in queries.items():
                all_results.extend(results)

        for corridor_name, corridor_info in self.strategic_patterns.items():
            matching_agreements = []

            for result in all_results:
                url = result.get('url', '').lower()
                domain = result.get('domain', '').lower()

                # Check for corridor keywords
                for keyword in corridor_info['keywords']:
                    if keyword in url or keyword in domain:
                        matching_agreements.append(result)
                        break

            corridor_analysis[corridor_name] = {
                'total_agreements': len(matching_agreements),
                'significance': corridor_info['significance'],
                'key_countries': corridor_info['countries'],
                'sample_agreements': matching_agreements[:5]
            }

        return corridor_analysis

    def analyze_infrastructure_projects(self, data):
        """Identify critical infrastructure projects"""
        infrastructure_projects = defaultdict(list)

        all_results = []
        for region, queries in data['results_by_region'].items():
            for query_name, results in queries.items():
                all_results.extend(results)

        for result in all_results:
            url = result.get('url', '').lower()

            for infra_type, keywords in self.infrastructure_types.items():
                for keyword in keywords:
                    if keyword in url:
                        infrastructure_projects[infra_type].append({
                            'url': result['url'],
                            'domain': result['domain'],
                            'region': self._identify_region(url)
                        })
                        break

        return dict(infrastructure_projects)

    def analyze_soe_involvement(self, data):
        """Identify Chinese SOE involvement"""
        soe_involvement = defaultdict(list)

        all_results = []
        for region, queries in data['results_by_region'].items():
            for query_name, results in queries.items():
                all_results.extend(results)

        for result in all_results:
            url = result.get('url', '').lower()

            for soe in self.chinese_soes:
                if soe in url:
                    soe_involvement[soe].append({
                        'url': result['url'],
                        'domain': result['domain']
                    })

        return dict(soe_involvement)

    def analyze_country_profiles(self, data):
        """Create strategic profiles for each country"""
        country_profiles = {}

        # Key countries of interest
        key_countries = {
            'serbia': {'region': 'balkans', 'eu_candidate': True, 'bri_member': True},
            'turkey': {'region': 'turkey', 'eu_candidate': True, 'nato_member': True},
            'uk': {'region': 'western', 'g7_member': True, 'five_eyes': True},
            'switzerland': {'region': 'western', 'neutral': True, 'financial_center': True},
            'norway': {'region': 'nordic', 'nato_member': True, 'arctic_council': True},
            'georgia': {'region': 'caucasus', 'eu_aspirant': True, 'strategic_location': True}
        }

        for country, info in key_countries.items():
            country_agreements = []
            region_data = data['results_by_region'].get(info['region'], {})

            for query_name, results in region_data.items():
                if country in query_name:
                    country_agreements.extend(results)

            # Analyze agreement types
            agreement_types = Counter()
            for agreement in country_agreements:
                url = agreement.get('url', '').lower()
                if 'trade' in url:
                    agreement_types['trade'] += 1
                if 'investment' in url:
                    agreement_types['investment'] += 1
                if 'infrastructure' in url:
                    agreement_types['infrastructure'] += 1
                if 'technology' in url or '5g' in url:
                    agreement_types['technology'] += 1
                if 'university' in url or 'education' in url:
                    agreement_types['education'] += 1

            country_profiles[country] = {
                'total_agreements': len(country_agreements),
                'characteristics': info,
                'agreement_types': dict(agreement_types),
                'sample_agreements': country_agreements[:3]
            }

        return country_profiles

    def _identify_region(self, url):
        """Helper to identify region from URL"""
        regions = {
            'balkans': ['serbia', 'albania', 'macedonia', 'montenegro', 'bosnia', 'kosovo'],
            'nordic': ['norway', 'iceland', 'nordic', 'scandinav'],
            'western': ['uk', 'britain', 'london', 'switzerland', 'swiss'],
            'caucasus': ['armenia', 'azerbaijan', 'georgia', 'tbilisi', 'baku', 'yerevan'],
            'turkey': ['turkey', 'turkish', 'ankara', 'istanbul']
        }

        for region, keywords in regions.items():
            for keyword in keywords:
                if keyword in url:
                    return region
        return 'unknown'

    def generate_strategic_report(self):
        """Generate comprehensive strategic analysis report"""
        print("\n" + "="*80)
        print("NON-EU EUROPE-CHINA STRATEGIC ANALYSIS")
        print("="*80)

        # Load data
        data = self.load_harvest_data()
        if not data:
            print("No harvest data found")
            return

        # Analyze strategic corridors
        corridors = self.analyze_strategic_corridors(data)
        print("\n1. STRATEGIC CORRIDORS AND INITIATIVES:")
        for corridor, info in corridors.items():
            if info['total_agreements'] > 0:
                print(f"\n{corridor.upper().replace('_', ' ')}:")
                print(f"  Agreements found: {info['total_agreements']}")
                print(f"  Significance: {info['significance']}")
                print(f"  Key countries: {', '.join(info['key_countries'])}")
                if info['sample_agreements']:
                    print(f"  Example: {info['sample_agreements'][0]['domain']}")

        # Analyze infrastructure
        infrastructure = self.analyze_infrastructure_projects(data)
        print("\n2. CRITICAL INFRASTRUCTURE PROJECTS:")
        total_infra = sum(len(v) for v in infrastructure.values())
        print(f"Total infrastructure agreements: {total_infra}")
        for infra_type, projects in sorted(infrastructure.items(),
                                          key=lambda x: len(x[1]), reverse=True):
            if projects:
                print(f"  {infra_type.title()}: {len(projects)} projects")
                regions = Counter(p['region'] for p in projects)
                top_region = regions.most_common(1)[0] if regions else ('unknown', 0)
                print(f"    Primary region: {top_region[0]} ({top_region[1]} projects)")

        # Analyze SOE involvement
        soe_involvement = self.analyze_soe_involvement(data)
        if soe_involvement:
            print("\n3. CHINESE STATE-OWNED ENTERPRISE INVOLVEMENT:")
            print(f"Total SOEs identified: {len(soe_involvement)}")
            for soe, agreements in sorted(soe_involvement.items(),
                                         key=lambda x: len(x[1]), reverse=True)[:5]:
                print(f"  {soe.upper()}: {len(agreements)} agreements")

        # Country profiles
        profiles = self.analyze_country_profiles(data)
        print("\n4. KEY COUNTRY PROFILES:")
        for country, profile in sorted(profiles.items(),
                                      key=lambda x: x[1]['total_agreements'], reverse=True):
            if profile['total_agreements'] > 0:
                print(f"\n{country.upper()}:")
                print(f"  Total agreements: {profile['total_agreements']}")
                chars = profile['characteristics']
                status = []
                if chars.get('eu_candidate'):
                    status.append('EU candidate')
                if chars.get('nato_member'):
                    status.append('NATO member')
                if chars.get('bri_member'):
                    status.append('BRI member')
                if chars.get('financial_center'):
                    status.append('Financial center')
                if status:
                    print(f"  Status: {', '.join(status)}")
                if profile['agreement_types']:
                    print(f"  Focus areas: {', '.join(profile['agreement_types'].keys())}")

        # Key findings
        print("\n5. KEY STRATEGIC FINDINGS:")

        # 17+1 mechanism
        ceec_total = corridors.get('17_plus_1', {}).get('total_agreements', 0)
        if ceec_total > 0:
            print(f"\n17+1 Cooperation Mechanism:")
            print(f"  - {ceec_total} agreements found")
            print(f"  - Key for China's Central/Eastern Europe strategy")

        # Middle Corridor
        middle_corridor = corridors.get('middle_corridor', {}).get('total_agreements', 0)
        if middle_corridor > 0:
            print(f"\nMiddle Corridor (Trans-Caspian):")
            print(f"  - {middle_corridor} agreements found")
            print(f"  - Alternative to Russia route gaining importance")

        # Arctic engagement
        arctic = corridors.get('polar_silk_road', {}).get('total_agreements', 0)
        if arctic > 0:
            print(f"\nPolar Silk Road:")
            print(f"  - {arctic} Arctic-related agreements")
            print(f"  - Norway and Iceland key partners")

        # Financial connectivity
        financial = corridors.get('financial_hubs', {}).get('total_agreements', 0)
        if financial > 0:
            print(f"\nFinancial Connectivity:")
            print(f"  - {financial} financial agreements")
            print(f"  - London and Zurich as RMB hubs")

        # Save comprehensive report
        report = {
            'analysis_date': datetime.now().isoformat(),
            'total_agreements': data['analysis']['summary']['total'],
            'strategic_corridors': {
                name: {
                    'total': info['total_agreements'],
                    'significance': info['significance']
                }
                for name, info in corridors.items()
            },
            'infrastructure_projects': {
                infra_type: len(projects)
                for infra_type, projects in infrastructure.items()
            },
            'soe_involvement': {
                soe: len(agreements)
                for soe, agreements in soe_involvement.items()
            },
            'country_profiles': {
                country: {
                    'total': profile['total_agreements'],
                    'characteristics': profile['characteristics'],
                    'focus_areas': profile['agreement_types']
                }
                for country, profile in profiles.items()
            }
        }

        output_file = self.results_dir / f'non_eu_strategic_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nStrategic analysis saved: {output_file}")

        return report

def main():
    """Run strategic analysis"""
    analyzer = NonEUStrategicAnalyzer()
    analyzer.generate_strategic_report()

    print("\n" + "="*80)
    print("STRATEGIC ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
