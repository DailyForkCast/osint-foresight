#!/usr/bin/env python3
"""
Complete Error Analysis - Identify What Went Wrong
Systematic review of all quarantined data to understand errors
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
import re
from urllib.parse import urlparse

class ErrorAnalyzer:
    """Analyze all errors in the quarantined data"""

    def __init__(self):
        """Initialize error analyzer"""
        self.quarantine_dir = Path('QUARANTINE_DATA')
        self.all_urls = []
        self.error_categories = defaultdict(list)
        self.analysis_results = {
            'obviously_wrong': [],
            'uncertain': [],
            'likely_valid': [],
            'error_patterns': {},
            'root_causes': []
        }

    def load_all_quarantined_data(self):
        """Load all URLs from quarantined files"""
        print("Loading all quarantined data...")

        for json_file in self.quarantine_dir.glob('**/*.json'):
            if 'LOG' not in json_file.name:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self._extract_urls_with_source(data, json_file.name)
                except Exception as e:
                    print(f"Error loading {json_file}: {e}")

        print(f"Loaded {len(self.all_urls)} URLs from quarantined data")
        return len(self.all_urls)

    def _extract_urls_with_source(self, obj, source_file, path=""):
        """Recursively extract URLs with source tracking"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ['url', 'source_url'] and isinstance(value, str) and value.startswith('http'):
                    self.all_urls.append({
                        'url': value,
                        'source_file': source_file,
                        'found_in': path + '.' + key
                    })
                else:
                    self._extract_urls_with_source(value, source_file, path + '.' + key)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._extract_urls_with_source(item, source_file, path + f'[{i}]')

    def analyze_error_patterns(self):
        """Identify patterns in errors"""
        print("\nAnalyzing error patterns...")

        error_patterns = {
            'domain_prefix_errors': [],
            'keyword_matching_errors': [],
            'geographic_mismatches': [],
            'spam_and_irrelevant': [],
            'language_sites': [],
            'industrial_machinery': [],
            'stock_photos': [],
            'casino_gambling': [],
            'login_pages': [],
            'news_vs_agreements': [],
            'think_tank_analysis': []
        }

        for url_data in self.all_urls:
            url = url_data['url'].lower()
            domain = self._extract_domain(url)

            # Domain prefix errors (the "is" problem)
            if any(prefix in domain for prefix in ['isbm', 'istudy', 'isdp', 'istock', 'isin']):
                error_patterns['domain_prefix_errors'].append({
                    'url': url_data['url'],
                    'domain': domain,
                    'issue': 'Domain prefix "is" incorrectly matched Iceland'
                })

            # Keyword matching errors
            if 'moulding' in url and 'mou' not in url.replace('moulding', ''):
                error_patterns['keyword_matching_errors'].append({
                    'url': url_data['url'],
                    'issue': '"moulding" incorrectly matched "MOU"'
                })

            # Geographic mismatches
            non_europe_indicators = ['gov.za', 'gov.gy', 'gov.au', '.cn', '.jp', '.kr', '.in']
            if any(indicator in domain for indicator in non_europe_indicators):
                error_patterns['geographic_mismatches'].append({
                    'url': url_data['url'],
                    'domain': domain,
                    'issue': 'Non-European domain incorrectly flagged as European'
                })

            # Spam categories
            if any(spam in url for spam in ['casino', 'gambling', 'poker', 'bet']):
                error_patterns['casino_gambling'].append({
                    'url': url_data['url'],
                    'issue': 'Gambling/casino site'
                })

            if 'istudy-china.com' in domain:
                error_patterns['language_sites'].append({
                    'url': url_data['url'],
                    'issue': 'Chinese language learning site'
                })

            if 'isbmmachines.com' in domain:
                error_patterns['industrial_machinery'].append({
                    'url': url_data['url'],
                    'issue': 'Industrial machinery advertisement'
                })

            if 'istockphoto.com' in domain:
                error_patterns['stock_photos'].append({
                    'url': url_data['url'],
                    'issue': 'Stock photography site'
                })

            if any(login in url for login in ['login', 'signin', 'password']):
                error_patterns['login_pages'].append({
                    'url': url_data['url'],
                    'issue': 'Login/authentication page'
                })

        self.analysis_results['error_patterns'] = error_patterns
        return error_patterns

    def categorize_urls(self):
        """Categorize each URL as obviously wrong, uncertain, or likely valid"""
        print("\nCategorizing URLs...")

        for url_data in self.all_urls:
            url = url_data['url']
            url_lower = url.lower()
            domain = self._extract_domain(url_lower)

            category = self._analyze_url_validity(url, url_lower, domain)

            self.analysis_results[category].append({
                'url': url,
                'domain': domain,
                'source_file': url_data['source_file'],
                'reasoning': self._get_categorization_reasoning(url, url_lower, domain)
            })

    def _analyze_url_validity(self, url, url_lower, domain):
        """Analyze if URL is obviously wrong, uncertain, or likely valid"""

        # Obviously wrong patterns
        obvious_wrong = [
            'casino', 'gambling', 'poker', 'bet', 'slot',
            'isbmmachines.com', 'istudy-china.com', 'istockphoto.com',
            'login', 'signin', 'password', 'robots.txt',
            'shop', 'store', 'buy', 'sale', 'discount',
            'porn', 'sex', 'adult', 'escort',
            'download', 'torrent', 'crack'
        ]

        if any(pattern in url_lower for pattern in obvious_wrong):
            return 'obviously_wrong'

        # Geographic mismatches (non-European domains)
        non_europe_domains = ['.za', '.au', '.nz', '.in', '.jp', '.kr', '.sg', '.my']
        if any(domain.endswith(ne) for ne in non_europe_domains):
            return 'obviously_wrong'

        # Likely valid patterns
        valid_indicators = [
            # Government domains
            '.gov.', 'europa.eu', 'embassy', 'consulate',
            # Official agreements
            'agreement', 'treaty', 'mou', 'memorandum',
            # Specific cooperation
            'cooperation', 'partnership', 'bilateral'
        ]

        # European domains
        eu_domains = [
            '.uk', '.de', '.fr', '.it', '.es', '.nl', '.be', '.at',
            '.ch', '.se', '.dk', '.no', '.fi', '.pl', '.cz', '.hu',
            '.gr', '.pt', '.ie', '.lu', '.si', '.sk', '.hr', '.bg',
            '.ro', '.lt', '.lv', '.ee', '.cy', '.mt', '.rs', '.al',
            '.mk', '.me', '.ba', '.tr', '.ge', '.am', '.az', '.is'
        ]

        has_europe = any(domain.endswith(eu) for eu in eu_domains)
        has_china = any(china in url_lower for china in ['china', 'chinese', 'beijing', 'shanghai'])
        has_agreement = any(indicator in url_lower for indicator in valid_indicators)

        if has_europe and has_china and has_agreement:
            return 'likely_valid'
        elif has_europe and has_china:
            return 'uncertain'
        else:
            return 'obviously_wrong'

    def _get_categorization_reasoning(self, url, url_lower, domain):
        """Get reasoning for categorization"""
        reasons = []

        # Check for obvious problems
        if any(spam in url_lower for spam in ['casino', 'gambling', 'bet']):
            reasons.append("Contains gambling/casino keywords")

        if 'isbmmachines.com' in domain:
            reasons.append("Industrial machinery advertisement site")

        if 'istudy-china.com' in domain:
            reasons.append("Chinese language learning site")

        if 'istockphoto.com' in domain:
            reasons.append("Stock photography site")

        # Check for valid indicators
        if '.gov' in domain:
            reasons.append("Government domain")

        if 'europa.eu' in domain:
            reasons.append("EU institution domain")

        if any(word in url_lower for word in ['agreement', 'treaty', 'mou']):
            reasons.append("Contains agreement keywords")

        # Geographic analysis
        if any(domain.endswith(ext) for ext in ['.uk', '.de', '.fr', '.it']):
            reasons.append("European country domain")

        if any(china in url_lower for china in ['china', 'chinese', 'beijing']):
            reasons.append("Contains China references")

        return "; ".join(reasons) if reasons else "No specific indicators found"

    def _extract_domain(self, url):
        """Extract domain from URL"""
        try:
            if '://' in url:
                return url.split('://')[1].split('/')[0]
            return url.split('/')[0]
        except:
            return 'unknown'

    def identify_root_causes(self):
        """Identify root causes of errors"""
        root_causes = [
            {
                'cause': 'Overly Broad Pattern Matching',
                'description': 'Used ".is" to match Iceland but caught "isbm", "istudy", "istock"',
                'impact': 'Massive false positives',
                'example': 'isbmmachines.com flagged as Iceland'
            },
            {
                'cause': 'Substring Matching Without Context',
                'description': 'Matched "mou" in "moulding" as Memorandum of Understanding',
                'impact': 'Industrial machinery ads flagged as MOUs',
                'example': 'blow-moulding-machine URLs flagged as agreements'
            },
            {
                'cause': 'No Content Verification',
                'description': 'Only checked URL patterns, never visited actual pages',
                'impact': 'Cannot distinguish agreements from ads/news/analysis',
                'example': 'Casino sites flagged as cooperation agreements'
            },
            {
                'cause': 'Geographic Pattern Overmatching',
                'description': 'Any URL containing European keywords flagged as European',
                'impact': 'Non-European sites incorrectly included',
                'example': 'South African .gov.za sites flagged as European'
            },
            {
                'cause': 'No Source Credibility Assessment',
                'description': 'All domains treated equally regardless of credibility',
                'impact': 'Spam sites weighted same as government sites',
                'example': 'Stock photo sites counted as official sources'
            },
            {
                'cause': 'Automatic Categorization Without Validation',
                'description': 'Query names used as categories without verification',
                'impact': 'Sister cities query returned general cooperation results',
                'example': '1,289 results labeled "sister cities" but only 15 actually contained "sister"'
            },
            {
                'cause': 'No Duplicate Detection',
                'description': 'Same URLs counted multiple times across different queries',
                'impact': 'Inflated total counts',
                'example': 'URLs appearing in multiple harvest files'
            },
            {
                'cause': 'Common Crawl Noise Not Filtered',
                'description': 'Treated Common Crawl as curated database instead of raw web crawl',
                'impact': 'Massive amounts of irrelevant content included',
                'example': 'SEO spam, broken links, random commercial content'
            }
        ]

        self.analysis_results['root_causes'] = root_causes
        return root_causes

    def generate_comprehensive_report(self):
        """Generate comprehensive error analysis report"""
        print("\nGenerating comprehensive error analysis...")

        # Count categories
        obviously_wrong_count = len(self.analysis_results['obviously_wrong'])
        uncertain_count = len(self.analysis_results['uncertain'])
        likely_valid_count = len(self.analysis_results['likely_valid'])
        total_count = len(self.all_urls)

        # Calculate error rates
        error_rate = (obviously_wrong_count / total_count) * 100 if total_count > 0 else 0

        report = {
            'analysis_timestamp': '2025-09-28T17:00:00',
            'total_urls_analyzed': total_count,
            'categorization': {
                'obviously_wrong': {
                    'count': obviously_wrong_count,
                    'percentage': f"{error_rate:.1f}%",
                    'examples': self.analysis_results['obviously_wrong'][:10]
                },
                'uncertain': {
                    'count': uncertain_count,
                    'percentage': f"{(uncertain_count/total_count)*100:.1f}%" if total_count > 0 else "0%",
                    'examples': self.analysis_results['uncertain'][:10]
                },
                'likely_valid': {
                    'count': likely_valid_count,
                    'percentage': f"{(likely_valid_count/total_count)*100:.1f}%" if total_count > 0 else "0%",
                    'examples': self.analysis_results['likely_valid'][:10]
                }
            },
            'error_patterns': self.analysis_results['error_patterns'],
            'root_causes': self.analysis_results['root_causes'],
            'lessons_learned': [
                'Pattern matching on URLs alone is insufficient',
                'Content verification is mandatory',
                'Source credibility must be assessed',
                'Geographic indicators need strict validation',
                'Duplicate detection is essential',
                'Common Crawl requires heavy filtering'
            ]
        }

        # Save report
        report_file = Path('ERROR_ANALYSIS_COMPLETE.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Print summary
        print("\n" + "="*80)
        print("COMPLETE ERROR ANALYSIS RESULTS")
        print("="*80)
        print(f"Total URLs analyzed: {total_count}")
        print(f"Obviously wrong: {obviously_wrong_count} ({error_rate:.1f}%)")
        print(f"Uncertain: {uncertain_count} ({(uncertain_count/total_count)*100:.1f}%)")
        print(f"Likely valid: {likely_valid_count} ({(likely_valid_count/total_count)*100:.1f}%)")

        print(f"\nTop error patterns:")
        for pattern_name, urls in self.analysis_results['error_patterns'].items():
            if urls:
                print(f"  {pattern_name}: {len(urls)} URLs")

        print(f"\nReport saved: {report_file}")
        return report

def main():
    """Run complete error analysis"""
    analyzer = ErrorAnalyzer()

    # Load all data
    analyzer.load_all_quarantined_data()

    # Analyze error patterns
    analyzer.analyze_error_patterns()

    # Categorize URLs
    analyzer.categorize_urls()

    # Identify root causes
    analyzer.identify_root_causes()

    # Generate report
    analyzer.generate_comprehensive_report()

if __name__ == "__main__":
    main()
