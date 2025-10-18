#!/usr/bin/env python3
"""
OpenAIRE Deep China Collaboration Search
Enhanced search with multiple China identifiers and search strategies
"""

import requests
import json
from pathlib import Path
from datetime import datetime
import time
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChinaCollaborationDeepSearch:
    """Enhanced search for China collaborations using multiple strategies"""

    def __init__(self):
        self.base_url = "https://api.openaire.eu/search"
        self.session = requests.Session()
        self.output_dir = Path("F:/OSINT_DATA/openaire_china_deep")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Multiple China identifiers
        self.china_identifiers = [
            'CN',           # ISO code
            'CHN',          # Alternative code
            'China',        # Full name
            'Chinese',      # Adjective
            'PRC',          # People's Republic of China
            'Beijing',      # Capital
            'Shanghai',     # Major city
            'Shenzhen',     # Tech hub
            'Tsinghua',     # Top university
            'Peking',       # Peking University
            'CAS',          # Chinese Academy of Sciences
            'Huawei',       # Major company
            'Alibaba',      # Major company
            'Baidu',        # Major company
            'ZTE',          # Major company
            'Xiaomi',       # Major company
            'Hong Kong',    # SAR
            'HK',           # Hong Kong code
            'Macau',        # SAR
            'Academia Sinica'  # Taiwan institution (for completeness)
        ]

        # Keywords that suggest China collaboration
        self.china_keywords = [
            'Sino-European',
            'EU-China',
            'China-EU',
            'Belt and Road',
            'BRI',
            'Silk Road',
            'Made in China 2025',
            'China 2025',
            'Dragon-STAR',
            'SENET',
            'EURAXESS China'
        ]

        # Chinese institution patterns
        self.chinese_institutions = [
            'Chinese Academy',
            'China University',
            'University of China',
            'Institute of China',
            'National Laboratory',
            'State Key Laboratory',
            'Beijing Institute',
            'Shanghai Institute',
            'Wuhan Institute',
            'Guangzhou',
            'Nanjing',
            'Harbin',
            'Dalian',
            'Fudan',
            'Zhejiang',
            'USTC',
            'SJTU'
        ]

    def search_direct_collaborations(self, eu_country: str) -> Dict:
        """Search for direct EU-China collaborations"""

        results = {
            'country': eu_country,
            'timestamp': datetime.now().isoformat(),
            'collaborations': [],
            'search_strategies': []
        }

        print(f"\n{'='*60}")
        print(f"DEEP SEARCH: {eu_country}-China Collaborations")
        print(f"{'='*60}")

        # Strategy 1: Direct country-to-country search
        print("\n1. Direct country search...")
        for china_id in ['CN', 'China', 'CHN']:
            try:
                url = f"{self.base_url}/researchProducts"
                params = {
                    'format': 'json',
                    'country': f'{eu_country},{china_id}',
                    'size': 50
                }

                response = self.session.get(url, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    total = data.get('response', {}).get('header', {}).get('total', {}).get('$', 0)

                    if int(total) > 0:
                        print(f"   FOUND: {total} collaborations with {china_id}")
                        results['search_strategies'].append({
                            'strategy': 'direct_country',
                            'query': f'{eu_country},{china_id}',
                            'count': int(total)
                        })

                        # Get sample results
                        if 'result' in data.get('response', {}).get('results', {}):
                            sample = data['response']['results']['result']
                            if not isinstance(sample, list):
                                sample = [sample]
                            results['collaborations'].extend(sample[:10])

                time.sleep(1)

            except Exception as e:
                logger.error(f"Error in direct search: {e}")

        # Strategy 2: Keyword-based search
        print("\n2. Keyword-based search...")
        for keyword in self.china_keywords[:5]:  # Test with first 5 keywords
            try:
                url = f"{self.base_url}/researchProducts"
                params = {
                    'format': 'json',
                    'country': eu_country,
                    'keywords': keyword,
                    'size': 10
                }

                response = self.session.get(url, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    total = data.get('response', {}).get('header', {}).get('total', {}).get('$', 0)

                    if int(total) > 0:
                        print(f"   FOUND: {total} results for '{keyword}'")
                        results['search_strategies'].append({
                            'strategy': 'keyword',
                            'query': keyword,
                            'count': int(total)
                        })

                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error in keyword search: {e}")

        # Strategy 3: Organization search
        print("\n3. Chinese organization search...")
        for org in self.chinese_institutions[:5]:  # Test with first 5 institutions
            try:
                url = f"{self.base_url}/researchProducts"
                params = {
                    'format': 'json',
                    'country': eu_country,
                    'organizationName': org,
                    'size': 10
                }

                response = self.session.get(url, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    total = data.get('response', {}).get('header', {}).get('total', {}).get('$', 0)

                    if int(total) > 0:
                        print(f"   FOUND: {total} results for '{org}'")
                        results['search_strategies'].append({
                            'strategy': 'organization',
                            'query': org,
                            'count': int(total)
                        })

                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error in organization search: {e}")

        # Strategy 4: Project search with China terms
        print("\n4. Project title search...")
        china_project_terms = ['China', 'Chinese', 'Sino', 'Beijing', 'Shanghai']

        for term in china_project_terms:
            try:
                url = f"{self.base_url}/projects"
                params = {
                    'format': 'json',
                    'participantCountries': eu_country,
                    'keywords': term,
                    'size': 10
                }

                response = self.session.get(url, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    total = data.get('response', {}).get('header', {}).get('total', {}).get('$', 0)

                    if int(total) > 0:
                        print(f"   FOUND: {total} projects with '{term}'")
                        results['search_strategies'].append({
                            'strategy': 'project',
                            'query': term,
                            'count': int(total)
                        })

                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error in project search: {e}")

        # Strategy 5: Author affiliation search
        print("\n5. Author affiliation search...")
        try:
            # Search for publications with authors from both countries
            url = f"{self.base_url}/researchProducts"
            params = {
                'format': 'json',
                'country': eu_country,
                'size': 100  # Get larger sample
            }

            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if 'result' in data.get('response', {}).get('results', {}):
                    results_list = data['response']['results']['result']
                    if not isinstance(results_list, list):
                        results_list = [results_list]

                    china_affiliated = 0
                    for item in results_list:
                        # Check for China in any field
                        item_str = str(item).lower()
                        for china_term in ['china', 'chinese', 'beijing', 'shanghai', 'hong kong']:
                            if china_term in item_str:
                                china_affiliated += 1
                                break

                    if china_affiliated > 0:
                        print(f"   FOUND: {china_affiliated} items with China affiliations in sample of {len(results_list)}")
                        results['search_strategies'].append({
                            'strategy': 'affiliation_scan',
                            'query': 'content_analysis',
                            'count': china_affiliated,
                            'sample_size': len(results_list)
                        })

        except Exception as e:
            logger.error(f"Error in affiliation search: {e}")

        # Calculate totals
        total_found = sum(s['count'] for s in results['search_strategies'])

        print(f"\n{'='*60}")
        print(f"SUMMARY for {eu_country}")
        print(f"{'='*60}")
        print(f"Total potential collaborations found: {total_found}")
        print(f"Search strategies used: {len(results['search_strategies'])}")

        if results['search_strategies']:
            print("\nTop findings:")
            sorted_strategies = sorted(results['search_strategies'],
                                     key=lambda x: x['count'],
                                     reverse=True)[:5]
            for s in sorted_strategies:
                print(f"  - {s['strategy']}: {s['query']} ({s['count']} results)")

        # Save results
        output_file = self.output_dir / f"{eu_country}_china_deep_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: {output_file}")

        return results

    def run_comprehensive_search(self):
        """Run deep search for priority EU countries"""

        priority_countries = [
            'IT',  # Italy
            'DE',  # Germany
            'FR',  # France
            'NL',  # Netherlands
            'ES',  # Spain
            'BE',  # Belgium
            'AT',  # Austria
            'PL',  # Poland
            'GR',  # Greece
            'PT'   # Portugal
        ]

        all_results = {
            'search_date': datetime.now().isoformat(),
            'countries_analyzed': {},
            'total_collaborations_found': 0,
            'search_methods': list(set(self.china_identifiers + self.china_keywords))
        }

        for country in priority_countries:
            country_results = self.search_direct_collaborations(country)
            all_results['countries_analyzed'][country] = country_results

            country_total = sum(s['count'] for s in country_results['search_strategies'])
            all_results['total_collaborations_found'] += country_total

            time.sleep(3)  # Pause between countries

        # Save comprehensive results
        final_output = self.output_dir / f"comprehensive_china_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(final_output, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        print("\n" + "="*60)
        print("COMPREHENSIVE SEARCH COMPLETE")
        print("="*60)
        print(f"Total potential China collaborations: {all_results['total_collaborations_found']}")
        print(f"Countries analyzed: {len(priority_countries)}")
        print(f"Results saved to: {final_output}")

        return all_results

def main():
    searcher = ChinaCollaborationDeepSearch()
    searcher.run_comprehensive_search()

if __name__ == "__main__":
    main()
