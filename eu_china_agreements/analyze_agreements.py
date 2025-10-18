#!/usr/bin/env python3
"""
Comprehensive Analysis of EU-China Agreements from Common Crawl
Processes 1,934 discovered agreements with geographic and thematic categorization
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import re
from urllib.parse import urlparse

class AgreementAnalyzer:
    """Analyzes discovered EU-China agreements"""

    def __init__(self, harvest_file):
        """Load harvest results"""
        self.harvest_file = Path(harvest_file)
        with open(self.harvest_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        # EU countries for filtering
        self.eu_countries = {
            'austria', 'belgium', 'bulgaria', 'croatia', 'cyprus', 'czech',
            'denmark', 'estonia', 'finland', 'france', 'germany', 'greece',
            'hungary', 'ireland', 'italy', 'latvia', 'lithuania', 'luxembourg',
            'malta', 'netherlands', 'poland', 'portugal', 'romania', 'slovakia',
            'slovenia', 'spain', 'sweden'
        }

        # Chinese cities for identification
        self.chinese_cities = {
            'beijing', 'shanghai', 'guangzhou', 'shenzhen', 'tianjin', 'wuhan',
            'chengdu', 'chongqing', 'hangzhou', 'nanjing', 'xian', 'suzhou',
            'qingdao', 'dalian', 'ningbo', 'xiamen', 'foshan', 'dongguan'
        }

        # Agreement type keywords
        self.agreement_types = {
            'sister_city': ['sister', 'twin', 'jumelage', 'städtepartner', 'gemellaggio'],
            'trade': ['trade', 'commerce', 'export', 'import', 'fta', 'economic'],
            'investment': ['investment', 'investor', 'capital', 'funding'],
            'technology': ['technology', 'tech', 'innovation', 'research', 'science'],
            'education': ['university', 'academic', 'education', 'student', 'exchange'],
            'climate': ['climate', 'environment', 'green', 'carbon', 'renewable'],
            'infrastructure': ['belt', 'road', 'bri', 'infrastructure', 'port', 'railway'],
            'health': ['health', 'medical', 'pandemic', 'covid', 'pharmaceutical']
        }

    def extract_all_agreements(self):
        """Extract and combine all agreement types"""
        all_agreements = []

        # Extract sister cities
        sister_cities = self.data['detailed_results']['sister_cities'].get('results', [])
        for item in sister_cities:
            if isinstance(item, dict) and item.get('source_url', '').startswith('http'):
                item['category'] = 'sister_city'
                all_agreements.append(item)

        # Extract university partnerships
        universities = self.data['detailed_results']['university_partnerships'].get('results', [])
        for item in universities:
            if isinstance(item, dict) and item.get('source_url', '').startswith('http'):
                item['category'] = 'university'
                all_agreements.append(item)

        # Extract government agreements
        government = self.data['detailed_results']['government_agreements'].get('results', [])
        for item in government:
            if isinstance(item, dict) and item.get('source_url', '').startswith('http'):
                item['category'] = 'government'
                all_agreements.append(item)

        return all_agreements

    def identify_eu_agreements(self, agreements):
        """Filter for EU-related agreements"""
        eu_agreements = []

        for agreement in agreements:
            url = agreement.get('source_url', '').lower()
            domain = agreement.get('domain', '').lower()

            # Check for EU domains
            is_eu = False

            # Direct EU domains
            if '.eu' in domain or 'europa.eu' in domain or 'eureporter' in domain:
                is_eu = True

            # Check for EU country domains
            for country in self.eu_countries:
                if country in domain or f'.{country[:2]}' in domain:
                    is_eu = True
                    agreement['eu_country'] = country
                    break

            # Check URL content for EU references
            if not is_eu:
                for country in self.eu_countries:
                    if country in url:
                        is_eu = True
                        agreement['eu_country'] = country
                        break

            if is_eu:
                eu_agreements.append(agreement)

        return eu_agreements

    def categorize_by_type(self, agreements):
        """Categorize agreements by type"""
        categorized = defaultdict(list)

        for agreement in agreements:
            url = agreement.get('source_url', '').lower()

            # Identify agreement type
            for type_name, keywords in self.agreement_types.items():
                for keyword in keywords:
                    if keyword in url:
                        categorized[type_name].append(agreement)
                        agreement['agreement_type'] = type_name
                        break

        return dict(categorized)

    def extract_geographic_patterns(self, agreements):
        """Extract geographic distribution"""
        geographic = {
            'by_country': defaultdict(list),
            'by_city': defaultdict(list),
            'china_cities': defaultdict(list)
        }

        for agreement in agreements:
            # Extract EU country
            if 'eu_country' in agreement:
                geographic['by_country'][agreement['eu_country']].append(agreement)

            # Extract cities from URL
            url = agreement.get('source_url', '').lower()
            for city in self.chinese_cities:
                if city in url:
                    geographic['china_cities'][city].append(agreement)
                    agreement['china_city'] = city

        return geographic

    def identify_key_partnerships(self, agreements):
        """Identify high-value strategic partnerships"""
        key_partnerships = []

        strategic_keywords = [
            'strategic', 'comprehensive', 'framework', 'bilateral',
            'memorandum', 'mou', 'cooperation agreement', 'joint declaration'
        ]

        for agreement in agreements:
            url = agreement.get('source_url', '').lower()
            is_strategic = False

            for keyword in strategic_keywords:
                if keyword in url:
                    is_strategic = True
                    agreement['strategic_level'] = 'high'
                    break

            if is_strategic or agreement.get('category') == 'government':
                key_partnerships.append(agreement)

        return key_partnerships

    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("=" * 80)
        print("EU-CHINA AGREEMENTS ANALYSIS REPORT")
        print("=" * 80)

        # Extract all agreements
        all_agreements = self.extract_all_agreements()
        print(f"\nTotal agreements discovered: {len(all_agreements)}")

        # Filter for EU agreements
        eu_agreements = self.identify_eu_agreements(all_agreements)
        print(f"EU-related agreements: {len(eu_agreements)}")

        # Categorize by type
        categorized = self.categorize_by_type(eu_agreements)
        print("\nAgreements by Type:")
        for type_name, items in categorized.items():
            print(f"  {type_name}: {len(items)}")

        # Geographic distribution
        geographic = self.extract_geographic_patterns(eu_agreements)
        print("\nGeographic Distribution:")
        print("  EU Countries involved:")
        for country, items in sorted(geographic['by_country'].items(),
                                    key=lambda x: len(x[1]), reverse=True)[:10]:
            print(f"    {country.capitalize()}: {len(items)} agreements")

        print("\n  Chinese cities mentioned:")
        for city, items in sorted(geographic['china_cities'].items(),
                                 key=lambda x: len(x[1]), reverse=True)[:10]:
            print(f"    {city.capitalize()}: {len(items)} agreements")

        # Key partnerships
        key_partnerships = self.identify_key_partnerships(eu_agreements)
        print(f"\nStrategic partnerships identified: {len(key_partnerships)}")

        # Sample key partnerships
        print("\nSample Strategic Partnerships:")
        for partnership in key_partnerships[:10]:
            url = partnership.get('source_url', '')
            domain = partnership.get('domain', '')
            print(f"  - {domain}")
            print(f"    URL: {url[:100]}...")

        # Save detailed report
        report = {
            'analysis_date': datetime.now().isoformat(),
            'total_agreements': len(all_agreements),
            'eu_agreements': len(eu_agreements),
            'categorized': {k: len(v) for k, v in categorized.items()},
            'geographic': {
                'countries': {k: len(v) for k, v in geographic['by_country'].items()},
                'china_cities': {k: len(v) for k, v in geographic['china_cities'].items()}
            },
            'strategic_partnerships': len(key_partnerships),
            'sample_strategic': [
                {
                    'url': p.get('source_url'),
                    'domain': p.get('domain'),
                    'date': p.get('crawl_date'),
                    'type': p.get('agreement_type')
                }
                for p in key_partnerships[:20]
            ],
            'eu_agreements_detailed': eu_agreements
        }

        # Save report
        output_file = Path('athena_results') / f'analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nDetailed report saved: {output_file}")

        return report

    def create_verification_priority_list(self, eu_agreements):
        """Create prioritized list for manual verification"""
        # Prioritize by strategic importance
        priority_agreements = []

        for agreement in eu_agreements:
            score = 0

            # Government agreements get highest priority
            if agreement.get('category') == 'government':
                score += 10

            # Strategic keywords boost priority
            url = agreement.get('source_url', '').lower()
            if 'strategic' in url or 'framework' in url or 'bilateral' in url:
                score += 5

            # Recent agreements are higher priority
            if '2024' in agreement.get('crawl_date', ''):
                score += 3
            elif '2023' in agreement.get('crawl_date', ''):
                score += 2

            # Major cities/countries boost priority
            if agreement.get('china_city') in ['beijing', 'shanghai', 'guangzhou']:
                score += 2

            agreement['priority_score'] = score
            priority_agreements.append(agreement)

        # Sort by priority
        priority_agreements.sort(key=lambda x: x['priority_score'], reverse=True)

        # Save priority list
        priority_file = Path('athena_results') / 'verification_priority.json'
        with open(priority_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_for_verification': len(priority_agreements),
                'high_priority': priority_agreements[:50],
                'verification_instructions': [
                    "1. Visit each URL to verify agreement exists",
                    "2. Confirm parties (EU entity + Chinese entity)",
                    "3. Note agreement date and current status",
                    "4. Extract key terms and commitments",
                    "5. Check for related documents or updates"
                ]
            }, f, indent=2, ensure_ascii=False)

        print(f"\nVerification priority list saved: {priority_file}")
        print(f"High priority items for verification: {len(priority_agreements[:50])}")

        return priority_agreements[:50]

def main():
    """Main execution"""
    harvest_file = Path('athena_results') / 'athena_harvest_20250928_130607.json'

    if not harvest_file.exists():
        print(f"Harvest file not found: {harvest_file}")
        return

    analyzer = AgreementAnalyzer(harvest_file)
    report = analyzer.generate_report()

    # Extract EU agreements for priority verification
    all_agreements = analyzer.extract_all_agreements()
    eu_agreements = analyzer.identify_eu_agreements(all_agreements)
    priority_list = analyzer.create_verification_priority_list(eu_agreements)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print(f"EU-China agreements requiring verification: {len(eu_agreements)}")
    print(f"High priority items: {len(priority_list)}")
    print("=" * 80)

if __name__ == "__main__":
    main()
