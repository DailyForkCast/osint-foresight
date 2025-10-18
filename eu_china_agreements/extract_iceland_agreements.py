#!/usr/bin/env python3
"""
Extract and analyze all Iceland-China agreements from verified data
"""

import json
from pathlib import Path
from collections import Counter
from datetime import datetime

def extract_iceland_agreements():
    """Extract all Iceland agreements from strict verification results"""

    # Load the strict verification results
    verification_file = Path('athena_results/STRICT_VERIFICATION_20250928_163222.json')

    with open(verification_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Filter for Iceland agreements
    iceland_agreements = []
    for agreement in data['verified_list']:
        if agreement['european_entity'] == 'iceland':
            iceland_agreements.append(agreement)

    print("="*80)
    print(f"ICELAND-CHINA AGREEMENTS ANALYSIS")
    print(f"Total found: {len(iceland_agreements)}")
    print("="*80)

    # Analyze agreement types
    type_counts = Counter(a['agreement_type'] for a in iceland_agreements)
    print("\nBy Agreement Type:")
    for agreement_type, count in type_counts.most_common():
        print(f"  {agreement_type:20} {count:3} agreements")

    # Print all URLs
    print("\n" + "-"*80)
    print("COMPLETE LIST OF ICELAND-CHINA AGREEMENT URLs:")
    print("-"*80)

    for i, agreement in enumerate(iceland_agreements, 1):
        print(f"\n{i}. Type: {agreement['agreement_type'].upper()}")
        print(f"   URL: {agreement['url']}")

    # Analyze URL patterns
    print("\n" + "-"*80)
    print("DOMAIN ANALYSIS:")
    print("-"*80)

    domains = Counter()
    for agreement in iceland_agreements:
        url = agreement['url']
        # Extract domain
        if '://' in url:
            domain = url.split('://')[1].split('/')[0]
            domains[domain] += 1

    print("\nTop domains hosting Iceland-China content:")
    for domain, count in domains.most_common(10):
        print(f"  {domain:40} {count:3} URLs")

    # Look for specific keywords in URLs
    print("\n" + "-"*80)
    print("KEYWORD ANALYSIS:")
    print("-"*80)

    keywords_to_check = [
        'arctic', 'polar', 'trade', 'investment', 'university',
        'embassy', 'minister', 'president', 'xi', 'reykjavik',
        'geothermal', 'energy', 'tourism', 'fisheries', 'aluminum'
    ]

    keyword_counts = Counter()
    keyword_examples = {}

    for agreement in iceland_agreements:
        url_lower = agreement['url'].lower()
        for keyword in keywords_to_check:
            if keyword in url_lower:
                keyword_counts[keyword] += 1
                if keyword not in keyword_examples:
                    keyword_examples[keyword] = agreement['url']

    print("\nKeywords found in Iceland-China URLs:")
    for keyword, count in keyword_counts.most_common():
        print(f"  {keyword:15} {count:3} occurrences")
        print(f"    Example: {keyword_examples[keyword][:100]}")

    # Save Iceland-specific report
    iceland_report = {
        'extraction_date': datetime.now().isoformat(),
        'total_iceland_agreements': len(iceland_agreements),
        'agreement_types': dict(type_counts),
        'top_domains': dict(domains.most_common(20)),
        'keyword_analysis': dict(keyword_counts),
        'all_agreements': iceland_agreements
    }

    output_file = Path('athena_results/iceland_china_agreements.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(iceland_report, f, indent=2, ensure_ascii=False)

    print(f"\n" + "="*80)
    print(f"Iceland-China agreements report saved to: {output_file}")
    print(f"Total verified Iceland-China agreements: {len(iceland_agreements)}")
    print("="*80)

    return iceland_agreements

if __name__ == "__main__":
    extract_iceland_agreements()
