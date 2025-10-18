#!/usr/bin/env python3
"""
Deep Analysis of BRI Agreements and Failed/Cancelled Projects
Focuses on Belt and Road Initiative patterns and project failures
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

class BRIAndFailureAnalyzer:
    """Analyze BRI agreements and identify failed projects"""

    def __init__(self):
        """Initialize analyzer"""
        self.results_dir = Path('athena_results')

        # BRI-related keywords
        self.bri_keywords = [
            'belt and road', 'bri', 'belt & road', 'silk road',
            'maritime silk', 'digital silk', 'health silk',
            'infrastructure investment', 'china-europe railway',
            'port cooperation', 'industrial park', 'economic corridor'
        ]

        # Failure/cancellation indicators
        self.failure_indicators = [
            'cancelled', 'terminated', 'suspended', 'halted', 'withdrawn',
            'abandoned', 'failed', 'dispute', 'controversy', 'protest',
            'debt trap', 'renegotiat', 'review', 'reassess', 'concern',
            'opposition', 'criticism', 'problem', 'issue', 'challenge'
        ]

        # EU member states with known BRI involvement
        self.bri_eu_countries = {
            'italy': 'First G7 country to join BRI (2019)',
            'greece': 'Piraeus port investment',
            'hungary': 'Budapest-Belgrade railway',
            'poland': 'Logistics hub ambitions',
            'portugal': 'Energy and port cooperation',
            'austria': 'Railway connections',
            'czech': 'Industrial cooperation',
            'croatia': 'Peljesac bridge project'
        }

    def load_comprehensive_report(self):
        """Load the comprehensive report"""
        report_files = sorted(self.results_dir.glob('comprehensive_report_*.json'))
        if not report_files:
            return None

        latest_report = report_files[-1]
        with open(latest_report, 'r', encoding='utf-8') as f:
            return json.load(f)

    def identify_bri_agreements(self, agreements):
        """Identify BRI-related agreements with detailed classification"""
        bri_agreements = {
            'infrastructure': [],
            'ports': [],
            'railways': [],
            'energy': [],
            'digital': [],
            'financial': [],
            'other': []
        }

        for agreement in agreements:
            url = agreement.get('source_url', '').lower()
            domain = agreement.get('domain', '').lower()

            # Check for BRI keywords
            is_bri = False
            for keyword in self.bri_keywords:
                if keyword in url or keyword in domain:
                    is_bri = True
                    break

            if is_bri:
                # Classify BRI type
                if 'port' in url or 'maritime' in url:
                    bri_agreements['ports'].append(agreement)
                elif 'railway' in url or 'rail' in url or 'train' in url:
                    bri_agreements['railways'].append(agreement)
                elif 'energy' in url or 'power' in url or 'electric' in url:
                    bri_agreements['energy'].append(agreement)
                elif 'digital' in url or 'telecom' in url or '5g' in url:
                    bri_agreements['digital'].append(agreement)
                elif 'bank' in url or 'financ' in url or 'invest' in url:
                    bri_agreements['financial'].append(agreement)
                elif 'infrastructur' in url:
                    bri_agreements['infrastructure'].append(agreement)
                else:
                    bri_agreements['other'].append(agreement)

        return bri_agreements

    def identify_failed_projects(self, agreements):
        """Identify failed, cancelled, or problematic projects"""
        failed_projects = {
            'cancelled': [],
            'suspended': [],
            'controversial': [],
            'renegotiated': [],
            'under_review': []
        }

        for agreement in agreements:
            url = agreement.get('source_url', '').lower()
            domain = agreement.get('domain', '').lower()

            # Check for failure indicators
            if 'cancel' in url:
                failed_projects['cancelled'].append(agreement)
            elif 'suspend' in url or 'halt' in url:
                failed_projects['suspended'].append(agreement)
            elif 'controvers' in url or 'protest' in url or 'opposition' in url:
                failed_projects['controversial'].append(agreement)
            elif 'renegotiat' in url:
                failed_projects['renegotiated'].append(agreement)
            elif 'review' in url or 'reassess' in url:
                failed_projects['under_review'].append(agreement)

        return failed_projects

    def analyze_temporal_patterns(self, agreements):
        """Analyze temporal patterns in agreements"""
        temporal_analysis = defaultdict(lambda: {'total': 0, 'bri': 0, 'failed': 0})

        for agreement in agreements:
            crawl_date = agreement.get('crawl_date', '')
            year = crawl_date[:4] if len(crawl_date) >= 4 else 'unknown'

            if year != 'unknown':
                temporal_analysis[year]['total'] += 1

                url = agreement.get('source_url', '').lower()

                # Check if BRI-related
                for keyword in self.bri_keywords:
                    if keyword in url:
                        temporal_analysis[year]['bri'] += 1
                        break

                # Check if failed/problematic
                for indicator in self.failure_indicators:
                    if indicator in url:
                        temporal_analysis[year]['failed'] += 1
                        break

        return dict(temporal_analysis)

    def identify_sister_city_bri_overlap(self, agreements):
        """Identify sister cities that overlap with BRI projects"""
        sister_bri_overlap = []

        sister_city_keywords = ['sister', 'twin', 'friendship', 'partner city']

        for agreement in agreements:
            url = agreement.get('source_url', '').lower()

            # Check if it's both sister city AND BRI-related
            is_sister = any(keyword in url for keyword in sister_city_keywords)
            is_bri = any(keyword in url for keyword in self.bri_keywords)

            if is_sister and is_bri:
                sister_bri_overlap.append(agreement)

        return sister_bri_overlap

    def generate_detailed_report(self):
        """Generate detailed BRI and failure analysis report"""
        print("\n" + "="*80)
        print("BRI AND PROJECT FAILURE ANALYSIS")
        print("="*80)

        # Load data
        report = self.load_comprehensive_report()
        if not report:
            print("No comprehensive report found. Run generate_comprehensive_report.py first.")
            return

        agreements = report.get('all_agreements', [])
        print(f"\nAnalyzing {len(agreements)} agreements...")

        # BRI Analysis
        bri_agreements = self.identify_bri_agreements(agreements)
        total_bri = sum(len(v) for v in bri_agreements.values())

        print(f"\n1. BELT AND ROAD INITIATIVE AGREEMENTS: {total_bri}")
        print("\nBRI Agreement Types:")
        for category, items in bri_agreements.items():
            if items:
                print(f"  {category.title()}: {len(items)}")
                if len(items) > 0 and items[0]:
                    print(f"    Example: {items[0].get('domain', 'N/A')}")

        # Failed Projects Analysis
        failed_projects = self.identify_failed_projects(agreements)
        total_failed = sum(len(v) for v in failed_projects.values())

        print(f"\n2. FAILED/PROBLEMATIC PROJECTS: {total_failed}")
        print("\nProject Status Categories:")
        for status, items in failed_projects.items():
            if items:
                print(f"  {status.replace('_', ' ').title()}: {len(items)}")
                if len(items) > 0 and items[0]:
                    print(f"    Example: {items[0].get('domain', 'N/A')}")

        # EU Country BRI Involvement
        print("\n3. EU MEMBER STATE BRI INVOLVEMENT:")
        for country, description in self.bri_eu_countries.items():
            country_bri = [a for a in agreements
                          if country in a.get('source_url', '').lower() and
                          any(kw in a.get('source_url', '').lower() for kw in self.bri_keywords)]
            if country_bri:
                print(f"  {country.title()}: {len(country_bri)} agreements")
                print(f"    Context: {description}")

        # Temporal Analysis
        temporal_patterns = self.analyze_temporal_patterns(agreements)

        print("\n4. TEMPORAL PATTERNS (2023-2024):")
        for year in ['2023', '2024']:
            if year in temporal_patterns:
                data = temporal_patterns[year]
                print(f"  {year}:")
                print(f"    Total: {data['total']}")
                print(f"    BRI-related: {data['bri']}")
                print(f"    Failed/Problematic: {data['failed']}")

        # Sister City-BRI Overlap
        sister_bri = self.identify_sister_city_bri_overlap(agreements)

        print(f"\n5. SISTER CITY-BRI OVERLAP:")
        print(f"  Agreements that are both sister city AND BRI-related: {len(sister_bri)}")
        if sister_bri:
            for item in sister_bri[:3]:
                print(f"    - {item.get('domain', 'N/A')}")

        # Key Findings
        print("\n6. KEY FINDINGS:")

        # Infrastructure focus
        infra_total = len(bri_agreements['infrastructure']) + len(bri_agreements['ports']) + len(bri_agreements['railways'])
        print(f"\n  Infrastructure Focus:")
        print(f"    - {infra_total} infrastructure-related BRI agreements")
        print(f"    - Ports: {len(bri_agreements['ports'])}, Railways: {len(bri_agreements['railways'])}")

        # Digital Silk Road
        if bri_agreements['digital']:
            print(f"\n  Digital Silk Road:")
            print(f"    - {len(bri_agreements['digital'])} digital/telecom agreements identified")

        # Project challenges
        if total_failed > 0:
            print(f"\n  Project Challenges:")
            print(f"    - {total_failed} agreements show signs of problems/cancellations")
            print(f"    - {len(failed_projects.get('controversial', []))} controversial projects")
            print(f"    - {len(failed_projects.get('under_review', []))} projects under review")

        # Save detailed analysis
        analysis_report = {
            'analysis_date': datetime.now().isoformat(),
            'total_agreements_analyzed': len(agreements),
            'bri_analysis': {
                'total': total_bri,
                'by_type': {k: len(v) for k, v in bri_agreements.items()},
                'sample_agreements': {
                    k: [{'url': a.get('source_url'), 'domain': a.get('domain')}
                        for a in v[:3]]
                    for k, v in bri_agreements.items() if v
                }
            },
            'failed_projects': {
                'total': total_failed,
                'by_status': {k: len(v) for k, v in failed_projects.items()},
                'sample_projects': {
                    k: [{'url': a.get('source_url'), 'domain': a.get('domain')}
                        for a in v[:3]]
                    for k, v in failed_projects.items() if v
                }
            },
            'temporal_patterns': temporal_patterns,
            'sister_bri_overlap': len(sister_bri),
            'eu_country_involvement': {
                country: len([a for a in agreements
                            if country in a.get('source_url', '').lower() and
                            any(kw in a.get('source_url', '').lower() for kw in self.bri_keywords)])
                for country in self.bri_eu_countries.keys()
            }
        }

        output_file = self.results_dir / f'bri_failure_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_report, f, indent=2, ensure_ascii=False)

        print(f"\nDetailed analysis saved: {output_file}")

        return analysis_report

def main():
    """Run BRI and failure analysis"""
    analyzer = BRIAndFailureAnalyzer()
    analyzer.generate_detailed_report()

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
