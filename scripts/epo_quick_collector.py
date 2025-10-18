#!/usr/bin/env python3
"""
EPO Quick Patent Collector
Focused collection of critical patent data
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

def collect_critical_patents():
    """Collect critical patents with proper segmentation"""

    # Refresh token first
    import subprocess
    subprocess.run(["python", "scripts/epo_auth_from_config.py"], cwd="C:/Projects/OSINT - Foresight")

    # Load authentication
    with open("C:/Projects/OSINT - Foresight/config/patent_auth.json", 'r') as f:
        config = json.load(f)

    access_token = config['epo_ops']['access_token']

    # Setup session
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'User-Agent': 'OSINT-Research-System/1.0'
    })

    search_url = "https://ops.epo.org/3.2/rest-services/published-data/search"

    # Output directory
    output_dir = Path("F:/OSINT_DATA/epo_critical_patents")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*60)
    print("EPO Critical Patent Collection")
    print("="*60)

    # Priority queries - small enough to complete quickly
    priority_queries = [
        # Joint patents (small datasets)
        ("pa=china AND pa=germany", "China-Germany Joint", 275),
        ("pa=china AND pa=france", "China-France Joint", 276),
        ("pa=china AND pa=italy", "China-Italy Joint", 126),
        ("pa=huawei AND pa=siemens", "Huawei-Siemens Joint", 18),
        ("pa=huawei AND pa=nokia", "Huawei-Nokia Joint", 34),

        # Critical tech (limited scope)
        ("txt=\"5G infrastructure\"", "5G Infrastructure", 26),
        ("txt=\"quantum computing\" AND pa=china", "Quantum Computing China", 182),
        ("txt=\"brain computer interface\"", "Brain-Computer Interface", 2369),
        ("pa=\"hong kong\" AND pa=\"holdings\"", "Hong Kong Holdings", 162),
    ]

    all_results = {
        'collection_time': datetime.now().isoformat(),
        'queries': {}
    }

    for query, description, expected_count in priority_queries:
        print(f"\n{description}")
        print(f"Query: {query}")
        print(f"Expected: {expected_count:,} patents")

        try:
            # Get total count
            params = {'q': query, 'Range': '1-1'}
            response = session.get(search_url, params=params, timeout=15)

            if response.status_code != 200:
                print(f"  Error: Status {response.status_code}")
                continue

            data = response.json()
            total_count = 0

            if 'ops:world-patent-data' in data:
                world_data = data['ops:world-patent-data']
                if 'ops:biblio-search' in world_data:
                    biblio_search = world_data['ops:biblio-search']
                    if '@total-result-count' in biblio_search:
                        total_count = int(biblio_search['@total-result-count'])

            print(f"  Actual: {total_count:,} patents")

            # Collect patents if reasonable count
            patents_collected = []

            if total_count > 0 and total_count <= 2000:
                # Collect in batches of 100
                for start in range(1, min(total_count + 1, 2000), 100):
                    end = min(start + 99, total_count, 2000)
                    range_str = f"{start}-{end}"

                    params = {'q': query, 'Range': range_str}
                    response = session.get(search_url, params=params, timeout=15)

                    if response.status_code == 200:
                        batch_data = response.json()

                        if 'ops:world-patent-data' in batch_data:
                            world_data = batch_data['ops:world-patent-data']
                            if 'ops:biblio-search' in world_data:
                                biblio_search = world_data['ops:biblio-search']
                                if 'ops:search-result' in biblio_search:
                                    search_results = biblio_search['ops:search-result']

                                    # Extract patent details
                                    if isinstance(search_results, list):
                                        for result in search_results:
                                            patents_collected.append(extract_patent_info(result))
                                    elif search_results:
                                        patents_collected.append(extract_patent_info(search_results))

                    print(f"  Collected {start}-{end}")
                    time.sleep(1)  # Rate limiting

                print(f"  ✓ Total collected: {len(patents_collected)}")

                # Save individual query results
                query_file = output_dir / f"{description.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(query_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'description': description,
                        'query': query,
                        'total_count': total_count,
                        'patents_collected': len(patents_collected),
                        'patents': patents_collected
                    }, f, indent=2, ensure_ascii=False)

                all_results['queries'][description] = {
                    'query': query,
                    'total_count': total_count,
                    'collected': len(patents_collected),
                    'file': str(query_file)
                }

            elif total_count > 2000:
                print(f"  ⚠ Too large for quick collection (needs segmentation)")
                all_results['queries'][description] = {
                    'query': query,
                    'total_count': total_count,
                    'collected': 0,
                    'note': 'Requires date segmentation'
                }

        except Exception as e:
            print(f"  Error: {e}")
            continue

    # Save summary
    summary_file = output_dir / f"collection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print("\n" + "="*60)
    print("COLLECTION COMPLETE")
    print("="*60)
    print(f"Results saved to: {output_dir}")
    print(f"Summary: {summary_file}")

    # Print summary stats
    total_collected = sum(q.get('collected', 0) for q in all_results['queries'].values())
    print(f"Total patents collected: {total_collected:,}")

    return all_results

def extract_patent_info(patent_data):
    """Extract key patent information"""
    info = {}

    try:
        if 'exchange-document' in patent_data:
            doc = patent_data['exchange-document']

            # Get basic info
            if '@country' in doc:
                info['country'] = doc['@country']
            if '@doc-number' in doc:
                info['doc_number'] = doc['@doc-number']
            if '@kind' in doc:
                info['kind'] = doc['@kind']

            if 'bibliographic-data' in doc:
                biblio = doc['bibliographic-data']

                # Title
                if 'invention-title' in biblio:
                    title = biblio['invention-title']
                    if isinstance(title, list):
                        title = title[0]
                    if isinstance(title, dict) and '$' in title:
                        info['title'] = title['$']

                # Applicants
                if 'parties' in biblio and 'applicants' in biblio['parties']:
                    applicants = biblio['parties']['applicants']
                    if 'applicant' in applicants:
                        app_list = applicants['applicant']
                        if not isinstance(app_list, list):
                            app_list = [app_list]

                        info['applicants'] = []
                        for app in app_list:
                            if 'applicant-name' in app and 'name' in app['applicant-name']:
                                name = app['applicant-name']['name']
                                if '$' in name:
                                    info['applicants'].append(name['$'])

                # Publication date
                if 'publication-reference' in biblio:
                    pub_ref = biblio['publication-reference']
                    if 'document-id' in pub_ref:
                        doc_id = pub_ref['document-id']
                        if isinstance(doc_id, list):
                            doc_id = doc_id[0]
                        if 'date' in doc_id and '$' in doc_id['date']:
                            info['publication_date'] = doc_id['date']['$']

    except Exception as e:
        info['extraction_error'] = str(e)

    return info

if __name__ == "__main__":
    collect_critical_patents()
