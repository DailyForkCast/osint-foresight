#!/usr/bin/env python3
"""
EPO China Technology Search
Working search for China-related patents in EU
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

def search_china_patents():
    """Search for China-related patents using working EPO format"""

    # Load authentication
    auth_config_path = Path("C:/Projects/OSINT - Foresight/config/patent_auth.json")
    with open(auth_config_path, 'r') as f:
        config = json.load(f)

    access_token = config['epo_ops']['access_token']

    # Setup session
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'User-Agent': 'OSINT-Research-System/1.0'
    })

    print("=" * 60)
    print("EPO China Patent Search")
    print(f"Starting analysis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    search_url = "https://ops.epo.org/3.2/rest-services/published-data/search"

    # China-related search queries that should work
    china_queries = [
        # Technology + China applicants
        'txt=5G AND pa=china',
        'txt=artificial AND pa=huawei',
        'txt=quantum AND pa=china',
        'txt=semiconductor AND pa=china',

        # China companies specifically
        'pa=huawei',
        'pa=xiaomi',
        'pa=alibaba',
        'pa=tencent',
        'pa=baidu'
    ]

    results_summary = {
        'total_patents_found': 0,
        'by_query': {},
        'sample_patents': [],
        'analysis_time': datetime.now().isoformat()
    }

    for i, query in enumerate(china_queries, 1):
        print(f"\n{i}. Searching: {query}")

        try:
            params = {
                'q': query,
                'Range': '1-10'  # Limit to 10 results per query
            }

            response = session.get(search_url, params=params, timeout=15)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                # Parse EPO response format
                total_found = 0
                patents = []

                # EPO responses can have different structures
                if 'ops:world-patent-data' in data:
                    world_data = data['ops:world-patent-data']

                    if 'ops:biblio-search' in world_data:
                        biblio_search = world_data['ops:biblio-search']

                        # Get total found
                        if '@total-result-count' in biblio_search:
                            total_found = int(biblio_search['@total-result-count'])

                        # Get patents
                        if 'ops:search-result' in biblio_search:
                            search_results = biblio_search['ops:search-result']

                            # Handle both single and multiple results
                            if isinstance(search_results, list):
                                patents = search_results
                            else:
                                patents = [search_results]

                print(f"   Found: {total_found} total patents")
                print(f"   Retrieved: {len(patents)} patent details")

                # Store results
                results_summary['by_query'][query] = {
                    'total_found': total_found,
                    'retrieved': len(patents)
                }
                results_summary['total_patents_found'] += total_found

                # Extract sample patent info
                for patent in patents[:3]:  # Just first 3 as samples
                    try:
                        # EPO patent structure
                        patent_info = extract_patent_info(patent)
                        if patent_info:
                            results_summary['sample_patents'].append(patent_info)
                            print(f"   Sample: {patent_info.get('title', 'No title')[:50]}...")
                    except Exception as e:
                        print(f"   Error extracting patent: {e}")

                # Rate limiting
                time.sleep(1)

            else:
                print(f"   Error: {response.text[:100]}")
                results_summary['by_query'][query] = {'error': response.text[:200]}

        except Exception as e:
            print(f"   Exception: {e}")
            results_summary['by_query'][query] = {'exception': str(e)}

    # Save results
    output_dir = Path("F:/OSINT_DATA/epo_china_search")
    output_dir.mkdir(parents=True, exist_ok=True)

    results_file = output_dir / f"china_patents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results_summary, f, indent=2)

    # Summary
    print("\n" + "=" * 60)
    print("CHINA PATENT SEARCH SUMMARY")
    print("=" * 60)
    print(f"Total patents found: {results_summary['total_patents_found']:,}")
    print(f"Successful queries: {len([q for q in results_summary['by_query'] if 'error' not in results_summary['by_query'][q]])}")
    print(f"Sample patents collected: {len(results_summary['sample_patents'])}")
    print(f"Results saved to: {results_file}")

    # Show top findings
    top_queries = sorted(
        [(q, data.get('total_found', 0)) for q, data in results_summary['by_query'].items() if 'total_found' in data],
        key=lambda x: x[1], reverse=True
    )

    print(f"\nTop findings:")
    for query, count in top_queries[:5]:
        print(f"  {query}: {count:,} patents")

    return results_summary

def extract_patent_info(patent_data):
    """Extract key information from EPO patent data"""
    try:
        info = {}

        # EPO structure varies, try common paths
        if 'exchange-document' in patent_data:
            doc = patent_data['exchange-document']

            # Patent number
            if 'bibliographic-data' in doc:
                biblio = doc['bibliographic-data']

                # Publication reference
                if 'publication-reference' in biblio:
                    pub_ref = biblio['publication-reference']
                    if 'document-id' in pub_ref:
                        doc_id = pub_ref['document-id']
                        if isinstance(doc_id, list):
                            doc_id = doc_id[0]

                        info['patent_number'] = doc_id.get('doc-number', {}).get('$', '')
                        info['country'] = doc_id.get('country', {}).get('$', '')
                        info['kind'] = doc_id.get('kind', {}).get('$', '')

                # Title
                if 'invention-title' in biblio:
                    title = biblio['invention-title']
                    if isinstance(title, list):
                        title = title[0]
                    info['title'] = title.get('$', '') if isinstance(title, dict) else str(title)

                # Applicants
                if 'parties' in biblio and 'applicants' in biblio['parties']:
                    applicants = biblio['parties']['applicants']
                    if 'applicant' in applicants:
                        app_list = applicants['applicant']
                        if not isinstance(app_list, list):
                            app_list = [app_list]

                        info['applicants'] = []
                        for app in app_list:
                            if 'applicant-name' in app:
                                name = app['applicant-name']
                                if 'name' in name:
                                    info['applicants'].append(name['name'].get('$', ''))

        return info
    except Exception as e:
        print(f"Error extracting patent info: {e}")
        return {}

if __name__ == "__main__":
    search_china_patents()
