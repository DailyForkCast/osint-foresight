#!/usr/bin/env python3
"""
Complete Data Audit - Verify Everything
Go through all harvested data and verify what we actually have
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
import re
from datetime import datetime

class CompleteDataAuditor:
    """Audit all data with zero assumptions"""

    def __init__(self):
        """Initialize auditor"""
        self.results_dir = Path('athena_results')
        self.all_urls = []
        self.verified_data = {
            'total_files': 0,
            'total_raw_results': 0,
            'unique_urls': 0,
            'duplicate_urls': 0,
            'verification_results': {},
            'actual_categories': defaultdict(list),
            'misclassified': []
        }

        # Strict category definitions
        self.strict_categories = {
            'sister_city': {
                'required': ['sister', 'twin', 'jumelage', 'städtepartner', 'gemellaggio'],
                'exclude': ['sister company', 'sister organization']
            },
            'university': {
                'required': ['university', 'universität', 'université', 'università', 'college', 'academic'],
                'exclude': ['university hospital', 'university press']
            },
            'government': {
                'required': ['government', 'ministry', 'embassy', 'consulate', 'parliament', 'council'],
                'exclude': []
            },
            'trade': {
                'required': ['trade', 'export', 'import', 'commerce', 'fta', 'free trade'],
                'exclude': ['trademark', 'trade union']
            },
            'bri': {
                'required': ['belt and road', 'belt & road', 'bri', 'silk road', 'belt-and-road'],
                'exclude': []
            },
            'infrastructure': {
                'required': ['port', 'railway', 'highway', 'bridge', 'airport', 'infrastructure'],
                'exclude': ['port of entry', 'support']
            },
            'energy': {
                'required': ['energy', 'power plant', 'renewable', 'nuclear', 'solar', 'wind power'],
                'exclude': ['energy drink']
            },
            'technology': {
                'required': ['5g', 'huawei', 'technology transfer', 'tech cooperation', 'digital'],
                'exclude': []
            },
            'investment': {
                'required': ['investment', 'investor', 'fdi', 'capital', 'funding'],
                'exclude': ['investment advice']
            },
            'climate': {
                'required': ['climate', 'carbon', 'green', 'environment', 'sustainable'],
                'exclude': ['business climate', 'political climate']
            }
        }

    def load_all_harvest_files(self):
        """Load ALL harvest files and extract URLs"""
        print("Loading all harvest files...")

        # Find all JSON files in results directory
        json_files = list(self.results_dir.glob('*.json'))
        print(f"Found {len(json_files)} JSON files")

        for json_file in json_files:
            print(f"\nProcessing: {json_file.name}")
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.verified_data['total_files'] += 1

                    # Extract URLs from different possible structures
                    urls_found = self.extract_urls_from_data(data, json_file.name)
                    print(f"  Extracted {urls_found} URLs from {json_file.name}")

            except Exception as e:
                print(f"  ERROR loading {json_file.name}: {e}")

        # Remove duplicates and count
        unique_urls = list(set(self.all_urls))
        self.verified_data['total_raw_results'] = len(self.all_urls)
        self.verified_data['unique_urls'] = len(unique_urls)
        self.verified_data['duplicate_urls'] = len(self.all_urls) - len(unique_urls)

        return unique_urls

    def extract_urls_from_data(self, data, filename):
        """Recursively extract all URLs from any data structure"""
        urls_found = 0

        def extract_recursive(obj, path=""):
            nonlocal urls_found

            if isinstance(obj, dict):
                for key, value in obj.items():
                    # Look for URL-like keys
                    if any(url_key in key.lower() for url_key in ['url', 'source_url', 'link']):
                        if isinstance(value, str) and value.startswith('http'):
                            self.all_urls.append(value)
                            urls_found += 1
                    # Recurse
                    extract_recursive(value, f"{path}.{key}")

            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item, f"{path}[]")

            elif isinstance(obj, str):
                # Check if it's a URL
                if obj.startswith('http'):
                    # Only count if in a results context
                    if 'result' in path.lower():
                        self.all_urls.append(obj)
                        urls_found += 1

        extract_recursive(data)
        return urls_found

    def verify_url_content(self, url):
        """Verify what a URL actually contains based on strict criteria"""
        url_lower = url.lower()

        # Check for China/Chinese keywords first
        china_keywords = ['china', 'chinese', 'beijing', 'shanghai', 'sino-', 'prc', 'zhongguo']
        has_china = any(keyword in url_lower for keyword in china_keywords)

        # Check for Europe keywords
        europe_keywords = [
            # EU countries
            'austria', 'belgium', 'bulgaria', 'croatia', 'cyprus', 'czech', 'denmark',
            'estonia', 'finland', 'france', 'germany', 'greece', 'hungary', 'ireland',
            'italy', 'latvia', 'lithuania', 'luxembourg', 'malta', 'netherlands',
            'poland', 'portugal', 'romania', 'slovakia', 'slovenia', 'spain', 'sweden',
            # Non-EU
            'uk', 'united kingdom', 'britain', 'switzerland', 'norway', 'iceland',
            'serbia', 'albania', 'macedonia', 'montenegro', 'bosnia', 'kosovo',
            'turkey', 'georgia', 'armenia', 'azerbaijan',
            # General
            'europe', 'eu', 'european'
        ]
        has_europe = any(keyword in url_lower for keyword in europe_keywords)

        # Check for cooperation/agreement keywords
        agreement_keywords = [
            'agreement', 'cooperation', 'partnership', 'mou', 'memorandum',
            'treaty', 'deal', 'contract', 'accord', 'pact', 'joint'
        ]
        has_agreement = any(keyword in url_lower for keyword in agreement_keywords)

        # Determine categories
        categories = []
        for category, rules in self.strict_categories.items():
            # Check required keywords
            has_required = any(req in url_lower for req in rules['required'])
            # Check exclusions
            has_excluded = any(excl in url_lower for excl in rules['exclude'])

            if has_required and not has_excluded:
                categories.append(category)

        return {
            'url': url,
            'has_china': has_china,
            'has_europe': has_europe,
            'has_agreement': has_agreement,
            'is_relevant': has_china and has_europe,
            'categories': categories
        }

    def audit_all_data(self):
        """Perform complete audit of all data"""
        print("\n" + "="*80)
        print("COMPLETE DATA AUDIT - ZERO TRUST VERIFICATION")
        print("="*80)

        # Load all URLs
        unique_urls = self.load_all_harvest_files()

        print(f"\n--- RAW DATA STATISTICS ---")
        print(f"Total files processed: {self.verified_data['total_files']}")
        print(f"Total raw results: {self.verified_data['total_raw_results']}")
        print(f"Unique URLs: {self.verified_data['unique_urls']}")
        print(f"Duplicates removed: {self.verified_data['duplicate_urls']}")

        # Verify each URL
        print(f"\n--- VERIFYING {len(unique_urls)} UNIQUE URLs ---")

        relevant_agreements = []
        irrelevant_urls = []

        for url in unique_urls:
            verification = self.verify_url_content(url)

            if verification['is_relevant']:
                relevant_agreements.append(verification)
                # Add to categories
                for category in verification['categories']:
                    self.verified_data['actual_categories'][category].append(url)
            else:
                irrelevant_urls.append(verification)

        # Statistics
        print(f"\n--- VERIFICATION RESULTS ---")
        print(f"URLs with China keyword: {sum(1 for v in relevant_agreements + irrelevant_urls if v['has_china'])}")
        print(f"URLs with Europe keyword: {sum(1 for v in relevant_agreements + irrelevant_urls if v['has_europe'])}")
        print(f"URLs with Agreement keyword: {sum(1 for v in relevant_agreements + irrelevant_urls if v['has_agreement'])}")
        print(f"\nRELEVANT (China + Europe): {len(relevant_agreements)}")
        print(f"IRRELEVANT: {len(irrelevant_urls)}")

        # Category breakdown
        print(f"\n--- VERIFIED CATEGORIES ---")
        for category, urls in sorted(self.verified_data['actual_categories'].items(),
                                    key=lambda x: len(x[1]), reverse=True):
            print(f"{category:20} {len(urls):5} agreements")

        # Sample relevant agreements
        print(f"\n--- SAMPLE RELEVANT AGREEMENTS ---")
        for agreement in relevant_agreements[:10]:
            print(f"URL: {agreement['url'][:100]}")
            print(f"  Categories: {', '.join(agreement['categories']) if agreement['categories'] else 'uncategorized'}")

        # Sample irrelevant URLs
        print(f"\n--- SAMPLE IRRELEVANT URLS ---")
        china_only = [u for u in irrelevant_urls if u['has_china'] and not u['has_europe']]
        europe_only = [u for u in irrelevant_urls if u['has_europe'] and not u['has_china']]
        neither = [u for u in irrelevant_urls if not u['has_china'] and not u['has_europe']]

        print(f"China-only (no Europe): {len(china_only)}")
        if china_only:
            print(f"  Example: {china_only[0]['url'][:100]}")

        print(f"Europe-only (no China): {len(europe_only)}")
        if europe_only:
            print(f"  Example: {europe_only[0]['url'][:100]}")

        print(f"Neither China nor Europe: {len(neither)}")
        if neither:
            print(f"  Example: {neither[0]['url'][:100]}")

        # Save audit results
        audit_report = {
            'audit_timestamp': datetime.now().isoformat(),
            'files_processed': self.verified_data['total_files'],
            'total_raw_results': self.verified_data['total_raw_results'],
            'unique_urls': self.verified_data['unique_urls'],
            'duplicates': self.verified_data['duplicate_urls'],
            'relevant_agreements': len(relevant_agreements),
            'irrelevant_urls': len(irrelevant_urls),
            'category_counts': {cat: len(urls) for cat, urls in self.verified_data['actual_categories'].items()},
            'sample_relevant': [
                {
                    'url': a['url'],
                    'categories': a['categories']
                }
                for a in relevant_agreements[:50]
            ],
            'breakdown': {
                'china_only': len(china_only),
                'europe_only': len(europe_only),
                'neither': len(neither)
            }
        }

        output_file = self.results_dir / f'COMPLETE_AUDIT_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(audit_report, f, indent=2, ensure_ascii=False)

        print(f"\n--- AUDIT REPORT SAVED ---")
        print(f"Location: {output_file}")

        # Final summary
        print(f"\n" + "="*80)
        print(f"FINAL VERIFIED COUNT")
        print(f"="*80)
        print(f"ACTUAL Europe-China Agreements: {len(relevant_agreements)}")
        print(f"(Not 4,579 as previously reported)")
        print(f"\nThis is the VERIFIED count based on URLs that:")
        print(f"1. Contain China/Chinese keywords")
        print(f"2. Contain European country/entity keywords")
        print(f"3. Are unique (duplicates removed)")

        return audit_report

def main():
    """Run complete audit"""
    auditor = CompleteDataAuditor()
    auditor.audit_all_data()

if __name__ == "__main__":
    main()
