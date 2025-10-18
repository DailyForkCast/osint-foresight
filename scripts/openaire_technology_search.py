#!/usr/bin/env python3
"""
OpenAIRE Technology-Specific Search

Searches for specific technology areas where China collaborations
are more likely to be detected.
"""

import os
import sys
import json
import time
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add the collectors directory to Python path
sys.path.append(str(Path(__file__).parent / "collectors"))
from openaire_client import OpenAIREClient

# Priority countries (smaller set for faster testing)
TEST_COUNTRIES = {
    'IT': 'Italy',
    'DE': 'Germany',
    'HU': 'Hungary',
    'GR': 'Greece'
}

# Technology keywords that are likely to show collaborations
TECHNOLOGY_KEYWORDS = [
    'artificial intelligence',
    'quantum computing',
    'biotechnology',
    'nanotechnology',
    '5G',
    'semiconductor',
    'battery technology',
    'solar energy',
    'machine learning'
]

def search_technology_collaborations(client, country_code, keyword, max_results=100):
    """Search for specific technology collaborations"""

    print(f"  Searching {country_code} for '{keyword}'...")

    try:
        # Search with keyword filter
        data = client.search_research_products(
            country=country_code,
            keywords=keyword,
            from_date='2020-01-01',  # Recent research
            size=50,
            page=1
        )

        # Get total count
        total = 0
        if data.get('response', {}).get('header', {}).get('total'):
            total = int(data['response']['header']['total']['$'])

        # Extract results if any
        results = []
        if data.get('response', {}).get('results', {}).get('result'):
            results = data['response']['results']['result']
            if not isinstance(results, list):
                results = [results]

        # Look for China collaborations in the results
        china_collabs = []
        for result in results:
            try:
                # Extract organization relationships
                metadata = result['metadata']['oaf:entity']['oaf:result']

                if 'rels' in metadata and 'rel' in metadata['rels']:
                    rels = metadata['rels']['rel']
                    if not isinstance(rels, list):
                        rels = [rels]

                    countries = set()
                    organizations = []

                    for rel in rels:
                        if rel.get('to', {}).get('@type') == 'organization':
                            country = rel.get('country', {}).get('@classid', '')
                            org_name = rel.get('legalname', {}).get('$', '')

                            if country:
                                countries.add(country)
                                organizations.append({
                                    'country': country,
                                    'organization': org_name
                                })

                    # Check if China is involved
                    if 'CN' in countries:
                        title = metadata.get('title', {}).get('$', '')
                        date = metadata.get('dateofacceptance', {}).get('$', '')

                        china_collabs.append({
                            'title': title,
                            'date': date,
                            'keyword': keyword,
                            'countries': list(countries),
                            'organizations': organizations
                        })

            except Exception as e:
                continue

        return {
            'keyword': keyword,
            'country': country_code,
            'total_results': total,
            'china_collaborations': len(china_collabs),
            'collaboration_details': china_collabs[:5]  # First 5 for details
        }

    except Exception as e:
        return {
            'keyword': keyword,
            'country': country_code,
            'error': str(e)
        }

def main():
    """Execute technology-specific search"""

    print("="*60)
    print("OpenAIRE Technology-Specific Search")
    print("="*60)
    print(f"Countries: {len(TEST_COUNTRIES)}")
    print(f"Keywords: {len(TECHNOLOGY_KEYWORDS)}")
    print()

    # Initialize client
    output_dir = "C:/Projects/OSINT - Foresight/data/processed/openaire_technology"
    client = OpenAIREClient(output_dir=output_dir)

    all_results = []

    for country_code, country_name in TEST_COUNTRIES.items():
        print(f"Analyzing {country_name} ({country_code}):")

        country_results = []

        for keyword in TECHNOLOGY_KEYWORDS:
            result = search_technology_collaborations(
                client, country_code, keyword, max_results=100
            )
            country_results.append(result)
            all_results.append(result)

            # Show immediate results
            if 'china_collaborations' in result:
                collabs = result['china_collaborations']
                total = result['total_results']
                print(f"    {keyword}: {collabs} China collabs / {total} total")
            else:
                print(f"    {keyword}: ERROR - {result.get('error', 'Unknown')}")

            time.sleep(0.5)  # Rate limiting

        print()

    # Analyze results
    print("SUMMARY:")
    print("-" * 40)

    total_collaborations = 0
    keywords_with_collabs = 0
    countries_with_collabs = 0

    # Country summary
    country_totals = {}
    for country_code in TEST_COUNTRIES:
        country_collabs = sum(r.get('china_collaborations', 0)
                            for r in all_results
                            if r.get('country') == country_code)
        country_totals[country_code] = country_collabs
        total_collaborations += country_collabs
        if country_collabs > 0:
            countries_with_collabs += 1

    # Keyword summary
    keyword_totals = {}
    for keyword in TECHNOLOGY_KEYWORDS:
        keyword_collabs = sum(r.get('china_collaborations', 0)
                            for r in all_results
                            if r.get('keyword') == keyword)
        keyword_totals[keyword] = keyword_collabs
        if keyword_collabs > 0:
            keywords_with_collabs += 1

    print(f"Total China collaborations found: {total_collaborations}")
    print(f"Countries with collaborations: {countries_with_collabs}/{len(TEST_COUNTRIES)}")
    print(f"Keywords with collaborations: {keywords_with_collabs}/{len(TECHNOLOGY_KEYWORDS)}")
    print()

    # Top results
    print("Top Countries:")
    for country, count in sorted(country_totals.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {country}: {count} collaborations")

    print("\nTop Keywords:")
    for keyword, count in sorted(keyword_totals.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {keyword}: {count} collaborations")

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = Path(output_dir) / f"technology_search_results_{timestamp}.json"

    final_results = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'countries': TEST_COUNTRIES,
            'keywords': TECHNOLOGY_KEYWORDS,
            'method': 'Technology-specific keyword search'
        },
        'summary': {
            'total_collaborations': total_collaborations,
            'countries_with_collaborations': countries_with_collabs,
            'keywords_with_collaborations': keywords_with_collabs
        },
        'country_totals': country_totals,
        'keyword_totals': keyword_totals,
        'detailed_results': all_results
    }

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nResults saved to: {results_file}")
    print("="*60)

if __name__ == "__main__":
    main()
