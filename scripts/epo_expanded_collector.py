#!/usr/bin/env python3
"""
EPO Expanded Patent Collector - Collects patents for multiple Chinese companies
Includes major tech companies and strategic technology areas
"""

import requests
import json
import time
from datetime import datetime
import os
import base64

class EPOExpandedCollector:
    def __init__(self):
        self.checkpoint_dir = "F:/OSINT_DATA/epo_checkpoints"
        self.output_dir = "F:/OSINT_DATA/epo_expanded"
        self.batch_size = 100
        self.max_per_session = 500  # Smaller batches to avoid timeouts

        os.makedirs(self.checkpoint_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def get_access_token(self):
        """Get EPO access token"""
        with open('config/epo_credentials.json', 'r') as f:
            creds = json.load(f)

        consumer_key = creds['EPO_CONSUMER_KEY']
        consumer_secret = creds['EPO_CONSUMER_SECRET']

        credentials = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()

        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(
            'https://ops.epo.org/3.2/auth/accesstoken',
            headers=headers,
            data={'grant_type': 'client_credentials'},
            timeout=10
        )

        if response.status_code == 200:
            return response.json()['access_token']
        return None

    def search_patents_count(self, query, token):
        """Get total count for a query"""
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }

        url = f"https://ops.epo.org/3.2/rest-services/published-data/search/abstract"
        params = {
            'q': query,
            'Range': '1-1'  # Just get count
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'ops:world-patent-data' in data:
                    biblio = data['ops:world-patent-data'].get('ops:biblio-search', {})
                    return int(biblio.get('@total-result-count', 0))
        except Exception as e:
            print(f"Error getting count: {e}")

        return 0

    def collect_batch(self, query, query_id, description, max_patents=500):
        """Collect a smaller batch of patents"""
        print(f"\n{'='*60}")
        print(f"Collecting: {description}")
        print(f"Query: {query}")
        print(f"Target: {max_patents} patents")
        print('='*60)

        # Get access token
        token = self.get_access_token()
        if not token:
            print("Failed to get access token")
            return None

        # First get total count
        total_count = self.search_patents_count(query, token)
        print(f"Total available: {total_count} patents")

        if total_count == 0:
            print("No patents found")
            return None

        # Collect patents
        patents = []
        collected = 0

        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }

        while collected < max_patents and collected < total_count:
            start = collected + 1
            end = min(collected + self.batch_size, max_patents, total_count)

            print(f"Fetching {start}-{end}...")

            url = f"https://ops.epo.org/3.2/rest-services/published-data/search/abstract"
            params = {
                'q': query,
                'Range': f"{start}-{end}"
            }

            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    # Parse and extract patent info (simplified)
                    if 'ops:world-patent-data' in data:
                        search_result = data['ops:world-patent-data'].get('ops:biblio-search', {})
                        results = search_result.get('ops:search-result', {})

                        if results:
                            # Extract basic info
                            doc_count = end - start + 1
                            patents.append({
                                'range': f"{start}-{end}",
                                'count': doc_count,
                                'raw_data': results
                            })
                            collected = end
                            print(f"  Retrieved: {doc_count} patents (Total: {collected}/{total_count})")
                else:
                    print(f"Error {response.status_code}")
                    break

                time.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"Request error: {e}")
                break

        # Save results
        if patents:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"{self.output_dir}/{query_id}_{timestamp}.json"

            result = {
                'query': query,
                'description': description,
                'timestamp': datetime.now().isoformat(),
                'total_available': total_count,
                'total_collected': collected,
                'patent_batches': patents
            }

            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)

            print(f"\nSaved {collected} patents to: {output_file}")
            return result

        return None

def main():
    collector = EPOExpandedCollector()

    # Expanded list of Chinese companies and technologies
    queries = [
        # Major Tech Companies
        {'query': 'pa=tencent', 'id': 'tencent', 'description': 'Tencent (WeChat, Gaming)'},
        {'query': 'pa=baidu', 'id': 'baidu', 'description': 'Baidu (Search, AI)'},
        {'query': 'pa=xiaomi', 'id': 'xiaomi', 'description': 'Xiaomi (Phones, IoT)'},
        {'query': 'pa=bytedance OR pa="byte dance"', 'id': 'bytedance', 'description': 'ByteDance (TikTok)'},
        {'query': 'pa=zte', 'id': 'zte', 'description': 'ZTE (Telecom Equipment)'},
        {'query': 'pa=lenovo', 'id': 'lenovo', 'description': 'Lenovo (Computers)'},
        {'query': 'pa=dji', 'id': 'dji', 'description': 'DJI (Drones)'},
        {'query': 'pa=oppo', 'id': 'oppo', 'description': 'OPPO (Phones)'},
        {'query': 'pa=vivo', 'id': 'vivo', 'description': 'VIVO (Phones)'},
        {'query': 'pa=byd', 'id': 'byd', 'description': 'BYD (Electric Vehicles)'},

        # Strategic Technologies
        {'query': 'txt="quantum computing" AND pa=china', 'id': 'quantum_computing', 'description': 'Quantum Computing - China'},
        {'query': 'txt="artificial intelligence" AND pa=china', 'id': 'ai_china', 'description': 'AI - China'},
        {'query': 'txt="machine learning" AND pa=china', 'id': 'ml_china', 'description': 'Machine Learning - China'},
        {'query': 'txt="5G" AND pa=china', 'id': '5g_china', 'description': '5G Technology - China'},
        {'query': 'txt="6G" AND pa=china', 'id': '6g_china', 'description': '6G Next Gen - China'},
        {'query': 'txt="blockchain" AND pa=china', 'id': 'blockchain_china', 'description': 'Blockchain - China'},
        {'query': 'txt="autonomous" AND pa=china', 'id': 'autonomous_china', 'description': 'Autonomous Systems - China'},
        {'query': 'txt="drone" AND pa=china', 'id': 'drone_china', 'description': 'Drone Technology - China'},

        # Defense & Dual-Use
        {'query': 'txt="radar" AND pa=china', 'id': 'radar_china', 'description': 'Radar Technology - China'},
        {'query': 'txt="satellite" AND pa=china', 'id': 'satellite_china', 'description': 'Satellite Tech - China'},
    ]

    print("="*60)
    print("EPO EXPANDED CHINA PATENT COLLECTION")
    print(f"Collecting {len(queries)} queries")
    print("="*60)

    results = []
    total_patents = 0

    for q in queries:
        result = collector.collect_batch(
            q['query'],
            q['id'],
            q['description'],
            max_patents=500  # Collect 500 per company/tech
        )

        if result:
            results.append(result)
            total_patents += result['total_collected']
            print(f"[SUCCESS] {q['description']}: {result['total_collected']} patents")
        else:
            print(f"[FAILED] {q['description']}: Failed")

        # Small delay between queries
        time.sleep(2)

    # Save summary
    summary_file = f"{collector.output_dir}/collection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary = {
        'collection_time': datetime.now().isoformat(),
        'queries_executed': len(queries),
        'successful_queries': len(results),
        'total_patents_collected': total_patents,
        'results': results
    }

    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "="*60)
    print("COLLECTION SUMMARY")
    print("="*60)
    print(f"Queries executed: {len(queries)}")
    print(f"Successful: {len(results)}")
    print(f"Total patents collected: {total_patents:,}")
    print(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
