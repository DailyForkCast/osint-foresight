#!/usr/bin/env python3
"""
EPO Batch Patent Collector - Optimized for China patents
Collects patents in smaller batches to avoid timeouts
"""

import requests
import json
import time
from datetime import datetime
import os
import base64

def get_access_token():
    """Get EPO access token"""
    # Read credentials from config
    with open('config/epo_credentials.json', 'r') as f:
        creds = json.load(f)

    consumer_key = creds['EPO_CONSUMER_KEY']
    consumer_secret = creds['EPO_CONSUMER_SECRET']

    # Encode credentials
    credentials = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()

    # Get token
    headers = {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(
        'https://ops.epo.org/3.2/auth/accesstoken',
        headers=headers,
        data={'grant_type': 'client_credentials'}
    )

    if response.status_code == 200:
        return response.json()['access_token']
    return None

def search_patents(query, token, start=0, limit=10):
    """Search EPO for patents"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    url = f"https://ops.epo.org/3.2/rest-services/published-data/search/abstract?q={query}&Range={start}-{start+limit-1}"

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"Search error: {e}")

    return None

def collect_china_patents():
    """Main collection function"""
    print("=" * 60)
    print("EPO China Patent Batch Collection")
    print(f"Started: {datetime.now()}")
    print("=" * 60)

    # Get access token
    token = get_access_token()
    if not token:
        print("Failed to get access token")
        return

    print("[SUCCESS] Authenticated with EPO")

    # Key China technology queries
    queries = [
        ('5G AND pa=china', '5G Technology'),
        ('artificial intelligence AND pa=china', 'AI'),
        ('quantum AND pa=china', 'Quantum Computing'),
        ('semiconductor AND pa=china', 'Semiconductors'),
        ('battery AND pa=china', 'Battery Technology'),
        ('solar AND pa=china', 'Solar Energy'),
        ('pa=huawei', 'Huawei'),
        ('pa=xiaomi', 'Xiaomi'),
        ('pa=alibaba', 'Alibaba'),
        ('pa=tencent', 'Tencent'),
        ('pa=baidu', 'Baidu'),
        ('pa=bytedance', 'ByteDance'),
        ('pa=zte', 'ZTE'),
        ('pa=lenovo', 'Lenovo'),
        ('pa=dji', 'DJI Drones')
    ]

    results = {}
    total_patents = 0

    for query, label in queries:
        print(f"\nSearching: {label}")
        print(f"Query: {query}")

        # Search first batch
        data = search_patents(query, token, 0, 25)

        if data:
            try:
                # Extract total count
                if 'ops:world-patent-data' in data:
                    biblio = data['ops:world-patent-data'].get('ops:biblio-search', {})
                    total = biblio.get('@total-result-count', 0)

                    results[label] = {
                        'query': query,
                        'total': int(total) if total else 0,
                        'timestamp': datetime.now().isoformat()
                    }

                    print(f"  Found: {total} patents")
                    total_patents += int(total) if total else 0
            except Exception as e:
                print(f"  Error parsing results: {e}")

        # Small delay to avoid rate limiting
        time.sleep(1)

    # Save results
    output_dir = "F:/OSINT_DATA/epo_china_batch"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"{output_dir}/china_patents_batch_{timestamp}.json"

    summary = {
        'collection_time': datetime.now().isoformat(),
        'total_patents_found': total_patents,
        'queries_executed': len(queries),
        'results': results
    }

    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print("COLLECTION SUMMARY")
    print("=" * 60)
    print(f"Total patents found: {total_patents:,}")
    print(f"Queries executed: {len(queries)}")
    print(f"Results saved to: {output_file}")

    # Print top results
    print("\nTop findings:")
    sorted_results = sorted(results.items(), key=lambda x: x[1]['total'], reverse=True)
    for label, data in sorted_results[:5]:
        print(f"  {label}: {data['total']:,} patents")

    return summary

if __name__ == "__main__":
    collect_china_patents()
