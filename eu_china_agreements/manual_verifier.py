#!/usr/bin/env python3
"""
Manual URL Verification Tool
Assists with systematic manual verification of each URL
"""

import json
from pathlib import Path
from datetime import datetime
import re

class ManualVerifier:
    """Manual verification tool for URLs"""

    def __init__(self):
        """Initialize verifier"""
        self.review_dir = Path('MANUAL_REVIEW_QUEUE')
        self.verified_dir = Path('VERIFIED_CLEAN')
        self.clean_db_file = self.verified_dir / 'CLEAN_DATABASE.json'

        # European entities reference
        self.european_entities = {
            'eu_institutions': ['european commission', 'european council', 'european parliament', 'european central bank'],
            'germany': ['germany', 'german', 'deutschland', 'berlin', 'munich', 'hamburg'],
            'france': ['france', 'french', 'paris', 'lyon', 'marseille'],
            'italy': ['italy', 'italian', 'rome', 'milan', 'venice'],
            'spain': ['spain', 'spanish', 'madrid', 'barcelona'],
            'uk': ['uk', 'united kingdom', 'britain', 'british', 'london'],
            'netherlands': ['netherlands', 'dutch', 'amsterdam'],
            'poland': ['poland', 'polish', 'warsaw'],
            'belgium': ['belgium', 'belgian', 'brussels'],
            'czech': ['czech', 'czechia', 'prague'],
            'hungary': ['hungary', 'hungarian', 'budapest'],
            'sweden': ['sweden', 'swedish', 'stockholm'],
            'austria': ['austria', 'austrian', 'vienna'],
            'denmark': ['denmark', 'danish', 'copenhagen'],
            'finland': ['finland', 'finnish', 'helsinki'],
            'norway': ['norway', 'norwegian', 'oslo'],
            'switzerland': ['switzerland', 'swiss', 'zurich', 'geneva'],
            'iceland': ['iceland', 'icelandic', 'reykjavik'],
            'serbia': ['serbia', 'serbian', 'belgrade'],
            'turkey': ['turkey', 'turkish', 'ankara', 'istanbul']
        }

        # Chinese entities reference
        self.chinese_entities = [
            'china', 'chinese', 'prc', 'peoples republic',
            'beijing', 'shanghai', 'guangzhou', 'shenzhen',
            'huawei', 'alibaba', 'tencent', 'xiaomi',
            'belt and road', 'silk road', 'bri'
        ]

    def analyze_url_content(self, url):
        """Analyze URL for potential content without visiting"""
        url_lower = url.lower()

        # Quick analysis based on URL structure
        analysis = {
            'url': url,
            'domain': self.extract_domain(url),
            'contains_europe': False,
            'contains_china': False,
            'likely_agreement': False,
            'red_flags': [],
            'initial_assessment': 'unknown'
        }

        # Check for European entities
        for country, keywords in self.european_entities.items():
            if any(keyword in url_lower for keyword in keywords):
                analysis['contains_europe'] = True
                analysis['european_country'] = country
                break

        # Check for Chinese entities
        if any(entity in url_lower for entity in self.chinese_entities):
            analysis['contains_china'] = True

        # Check for agreement indicators
        agreement_indicators = ['agreement', 'mou', 'partnership', 'cooperation', 'treaty', 'deal']
        if any(indicator in url_lower for indicator in agreement_indicators):
            analysis['likely_agreement'] = True

        # Check for red flags
        red_flag_patterns = [
            'casino', 'gambling', 'poker', 'bet',
            'shop', 'store', 'buy', 'sale',
            'porn', 'sex', 'adult',
            'login', 'signin', 'password',
            'download', 'torrent'
        ]
        for pattern in red_flag_patterns:
            if pattern in url_lower:
                analysis['red_flags'].append(pattern)

        # Initial assessment
        if analysis['red_flags']:
            analysis['initial_assessment'] = 'spam/irrelevant'
        elif analysis['contains_europe'] and analysis['contains_china'] and analysis['likely_agreement']:
            analysis['initial_assessment'] = 'potential_agreement'
        elif analysis['contains_europe'] and analysis['contains_china']:
            analysis['initial_assessment'] = 'europe_china_related'
        else:
            analysis['initial_assessment'] = 'unlikely_relevant'

        return analysis

    def extract_domain(self, url):
        """Extract domain from URL"""
        try:
            if '://' in url:
                return url.split('://')[1].split('/')[0]
            return url.split('/')[0]
        except:
            return 'unknown'

    def verify_first_batch(self):
        """Manually verify the first batch as demonstration"""
        print("="*80)
        print("MANUAL VERIFICATION DEMONSTRATION")
        print("="*80)

        batch_file = self.review_dir / 'review_batch_001.json'
        with open(batch_file, 'r', encoding='utf-8') as f:
            batch_data = json.load(f)

        print(f"Batch 1: {batch_data['total_urls']} URLs to verify")
        print("\nSample verification of first 10 URLs:")

        verified_count = 0
        potential_agreements = []

        for i, item in enumerate(batch_data['urls_to_review'][:10], 1):
            url = item['url']
            analysis = self.analyze_url_content(url)

            print(f"\n{i}. URL: {url[:80]}...")
            print(f"   Domain: {analysis['domain']}")
            print(f"   Europe: {analysis['contains_europe']}")
            print(f"   China: {analysis['contains_china']}")
            print(f"   Agreement indicators: {analysis['likely_agreement']}")
            if analysis['red_flags']:
                print(f"   RED FLAGS: {', '.join(analysis['red_flags'])}")
            print(f"   Assessment: {analysis['initial_assessment']}")

            # Detailed analysis for potential agreements
            if analysis['initial_assessment'] == 'potential_agreement':
                potential_agreements.append({
                    'url': url,
                    'analysis': analysis,
                    'manual_review_needed': True
                })
                print(f"   >>> REQUIRES MANUAL REVIEW <<<")

        print(f"\n{'-'*80}")
        print(f"First 10 URLs Analysis:")
        print(f"Potential agreements requiring manual review: {len(potential_agreements)}")

        # Show potential agreements
        if potential_agreements:
            print(f"\nURLs requiring detailed manual verification:")
            for i, item in enumerate(potential_agreements, 1):
                print(f"{i}. {item['url']}")

        return potential_agreements

    def create_detailed_verification_guide(self):
        """Create guide for manual verification"""
        guide = {
            'verification_steps': [
                {
                    'step': 1,
                    'action': 'Visit the URL',
                    'check': 'Does the page load? Is it accessible?'
                },
                {
                    'step': 2,
                    'action': 'Check page title and content',
                    'check': 'Is this about an actual agreement/partnership/cooperation?'
                },
                {
                    'step': 3,
                    'action': 'Identify parties',
                    'check': 'Which European entity? Which Chinese entity?'
                },
                {
                    'step': 4,
                    'action': 'Check agreement type',
                    'check': 'MOU, Treaty, Partnership, Trade Deal, Investment?'
                },
                {
                    'step': 5,
                    'action': 'Find date and status',
                    'check': 'When signed? Still active?'
                },
                {
                    'step': 6,
                    'action': 'Verify source credibility',
                    'check': 'Official government site? News report? Think tank?'
                }
            ],
            'red_flags_to_reject': [
                'Industrial machinery advertisements',
                'Stock photos',
                'Language learning sites',
                'Dating/casino/shopping sites',
                'Login pages',
                'News ABOUT agreements (not the agreements themselves)',
                'Academic analysis (not actual agreements)',
                'URLs with geographic mismatches'
            ],
            'accept_criteria': [
                'Official government announcement of agreement',
                'Embassy/consulate announcement',
                'University partnership announcements',
                'Trade association agreements',
                'Sister city partnership documents',
                'Investment agreements',
                'Actual signed MOUs/treaties'
            ]
        }

        guide_file = self.verified_dir / 'MANUAL_VERIFICATION_GUIDE.json'
        with open(guide_file, 'w', encoding='utf-8') as f:
            json.dump(guide, f, indent=2, ensure_ascii=False)

        print(f"Manual verification guide saved: {guide_file}")
        return guide

    def create_priority_review_list(self):
        """Create list of URLs most likely to be actual agreements"""
        print("\nCreating priority review list...")

        all_potential = []

        # Analyze all batches
        for batch_file in sorted(self.review_dir.glob('review_batch_*.json')):
            with open(batch_file, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)

            for item in batch_data['urls_to_review']:
                analysis = self.analyze_url_content(item['url'])
                if analysis['initial_assessment'] == 'potential_agreement':
                    all_potential.append(analysis)

        print(f"Found {len(all_potential)} URLs with potential agreement indicators")

        # Sort by domain credibility
        government_domains = []
        university_domains = []
        organization_domains = []
        other_domains = []

        for item in all_potential:
            domain = item['domain'].lower()
            if any(ext in domain for ext in ['.gov', '.edu', '.org', 'europa.eu', 'embassy']):
                if '.gov' in domain or 'europa.eu' in domain or 'embassy' in domain:
                    government_domains.append(item)
                elif '.edu' in domain:
                    university_domains.append(item)
                elif '.org' in domain:
                    organization_domains.append(item)
            else:
                other_domains.append(item)

        priority_list = {
            'high_priority_government': government_domains,
            'medium_priority_university': university_domains,
            'medium_priority_organization': organization_domains,
            'low_priority_other': other_domains
        }

        priority_file = self.verified_dir / 'PRIORITY_REVIEW_LIST.json'
        with open(priority_file, 'w', encoding='utf-8') as f:
            json.dump(priority_list, f, indent=2, ensure_ascii=False)

        print(f"Priority breakdown:")
        print(f"  High priority (government): {len(government_domains)}")
        print(f"  Medium priority (university): {len(university_domains)}")
        print(f"  Medium priority (organization): {len(organization_domains)}")
        print(f"  Low priority (other): {len(other_domains)}")
        print(f"Priority list saved: {priority_file}")

        return priority_list

def main():
    """Run manual verification demonstration"""
    verifier = ManualVerifier()

    # Demonstrate verification process
    potential_agreements = verifier.verify_first_batch()

    # Create verification guide
    verifier.create_detailed_verification_guide()

    # Create priority review list
    priority_list = verifier.create_priority_review_list()

    print("\n" + "="*80)
    print("MANUAL VERIFICATION PROCESS READY")
    print("="*80)
    print("Next steps:")
    print("1. Review priority URLs starting with government domains")
    print("2. Visit each URL and verify actual agreement content")
    print("3. Document verified agreements in clean database")
    print("4. Reject all false positives")
    print("="*80)

if __name__ == "__main__":
    main()
