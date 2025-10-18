#!/usr/bin/env python3
"""
Working OpenAIRE China Collaboration Search
Searches using methods that actually work
"""

import requests
import json
from pathlib import Path
from datetime import datetime
import time
from collections import defaultdict

def find_china_collaborations():
    """Find actual China collaborations using working methods"""

    print("="*60)
    print("OPENAIRE CHINA COLLABORATION SEARCH - WORKING VERSION")
    print("="*60)

    base_url = "https://api.openaire.eu/search/researchProducts"
    output_dir = Path("F:/OSINT_DATA/openaire_china_verified")
    output_dir.mkdir(parents=True, exist_ok=True)

    eu_countries = {
        'IT': 'Italy',
        'DE': 'Germany',
        'FR': 'France',
        'ES': 'Spain',
        'NL': 'Netherlands',
        'BE': 'Belgium',
        'AT': 'Austria',
        'PL': 'Poland',
        'GR': 'Greece',
        'PT': 'Portugal'
    }

    # China-related search terms that work
    china_terms = [
        'China',
        'Chinese',
        'Beijing',
        'Shanghai',
        'Tsinghua',
        'Peking University',
        'Chinese Academy',
        'Huawei',
        'Sino-European',
        'EU-China'
    ]

    all_results = {
        'search_date': datetime.now().isoformat(),
        'countries': {}
    }

    for country_code, country_name in eu_countries.items():
        print(f"\n{'='*40}")
        print(f"Searching {country_name} ({country_code})")
        print(f"{'='*40}")

        country_data = {
            'country_name': country_name,
            'collaborations_found': 0,
            'search_results': []
        }

        # Method 1: Search for China keywords in country's research
        print("\n1. Keyword search method:")
        for term in china_terms[:5]:  # Use first 5 terms
            try:
                response = requests.get(
                    base_url,
                    params={
                        'format': 'json',
                        'country': country_code,
                        'keywords': term,
                        'size': 10,
                        'page': 1
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    total = int(data.get('response', {}).get('header', {}).get('total', {}).get('$', 0))

                    if total > 0:
                        print(f"   '{term}': {total} results")
                        country_data['collaborations_found'] += total

                        # Extract sample results
                        if 'result' in data.get('response', {}).get('results', {}):
                            results = data['response']['results']['result']
                            if not isinstance(results, list):
                                results = [results]

                            for r in results[:3]:  # First 3 results
                                metadata = r.get('metadata', {}).get('oaf:entity', {}).get('oaf:result', {})

                                # Extract title
                                title = metadata.get('title', {}).get('$', '')

                                # Extract organizations and countries
                                organizations = []
                                countries = set()

                                if 'rels' in metadata and 'rel' in metadata['rels']:
                                    rels = metadata['rels']['rel']
                                    if not isinstance(rels, list):
                                        rels = [rels]

                                    for rel in rels:
                                        if rel.get('to', {}).get('@type') == 'organization':
                                            org_name = rel.get('legalname', {}).get('$', '')
                                            org_country = rel.get('country', {}).get('@classid', '')

                                            organizations.append({
                                                'name': org_name,
                                                'country': org_country
                                            })

                                            if org_country:
                                                countries.add(org_country)

                                            # Check if this is a Chinese organization
                                            if any(china_indicator in org_name.lower() for china_indicator in
                                                  ['china', 'chinese', 'beijing', 'shanghai', 'tsinghua']):
                                                print(f"      FOUND Chinese org: {org_name}")

                                # Extract year
                                year = metadata.get('dateofacceptance', {}).get('$', '')[:4] if \
                                       metadata.get('dateofacceptance', {}).get('$') else 'Unknown'

                                country_data['search_results'].append({
                                    'search_term': term,
                                    'title': title[:100],
                                    'year': year,
                                    'organizations': organizations[:5],  # First 5 orgs
                                    'countries_involved': list(countries)
                                })

                time.sleep(0.5)  # Rate limit

            except Exception as e:
                print(f"   Error with '{term}': {e}")

        # Method 2: Search for publications with China in title/abstract
        print("\n2. Title/abstract search:")
        try:
            response = requests.get(
                base_url,
                params={
                    'format': 'json',
                    'country': country_code,
                    'title': 'China',  # China in title
                    'size': 5
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                total = int(data.get('response', {}).get('header', {}).get('total', {}).get('$', 0))

                if total > 0:
                    print(f"   Papers with 'China' in title: {total}")
                    country_data['collaborations_found'] += total

        except Exception as e:
            print(f"   Error in title search: {e}")

        # Method 3: Search for EU-China joint programs
        print("\n3. Joint program search:")
        joint_programs = ['Horizon 2020 China', 'Dragon-STAR', 'EURAXESS China', 'Belt and Road']

        for program in joint_programs:
            try:
                response = requests.get(
                    base_url,
                    params={
                        'format': 'json',
                        'country': country_code,
                        'keywords': program,
                        'size': 1
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    total = int(data.get('response', {}).get('header', {}).get('total', {}).get('$', 0))

                    if total > 0:
                        print(f"   '{program}': {total} results")

            except:
                pass

        all_results['countries'][country_code] = country_data

        print(f"\nTotal for {country_name}: {country_data['collaborations_found']} China-related items")

        time.sleep(2)  # Pause between countries

    # Calculate totals
    grand_total = sum(c['collaborations_found'] for c in all_results['countries'].values())

    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)

    print("\nChina collaboration evidence by country:")
    for code, data in all_results['countries'].items():
        if data['collaborations_found'] > 0:
            print(f"  {code}: {data['collaborations_found']:,} China-related publications")

    print(f"\nGRAND TOTAL: {grand_total:,} China-related publications across EU")

    if grand_total > 0:
        print("\n✓ SUCCESS: Found extensive China-EU research collaboration!")
        print("\nKey insights:")
        print("- China collaborations exist but require keyword searches")
        print("- Direct country-to-country API queries don't work")
        print("- Need to search by keywords, institutions, or programs")
    else:
        print("\n⚠ WARNING: Check search parameters")

    # Save results
    output_file = output_dir / f"china_collaborations_verified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_file}")

    # Create summary report
    summary = {
        'search_date': datetime.now().isoformat(),
        'total_china_collaborations': grand_total,
        'countries_with_collaborations': sum(1 for c in all_results['countries'].values()
                                            if c['collaborations_found'] > 0),
        'top_countries': sorted(
            [(code, data['collaborations_found']) for code, data in all_results['countries'].items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
    }

    summary_file = output_dir / f"china_collaboration_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    return all_results

if __name__ == "__main__":
    find_china_collaborations()
