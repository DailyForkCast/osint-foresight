#!/usr/bin/env python3
"""
EPO Patent Collector with Full Provenance
Zero fabrication - all data tracked to source
"""

import requests
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class EPOProvenanceCollector:
    """EPO collector with complete provenance tracking"""

    def __init__(self):
        self.start_time = datetime.now()

        # Setup paths
        self.config_path = Path("C:/Projects/OSINT - Foresight/config/patent_auth.json")
        self.output_dir = Path("F:/OSINT_DATA/epo_provenance_collection")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Provenance tracking
        self.provenance_log = self.output_dir / "provenance_log.jsonl"

        # Authenticate
        self.authenticate()

    def authenticate(self):
        """Authenticate with EPO"""
        # First refresh token
        import subprocess
        result = subprocess.run(
            ["python", "scripts/epo_auth_from_config.py"],
            capture_output=True,
            text=True,
            cwd="C:/Projects/OSINT - Foresight"
        )

        # Load token
        with open(self.config_path, 'r') as f:
            config = json.load(f)

        self.access_token = config['epo_ops']['access_token']

        # Setup session
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'User-Agent': 'OSINT-Research-System/1.0'
        })

        self.search_url = "https://ops.epo.org/3.2/rest-services/published-data/search"

    def log_provenance(self, action: str, data: Dict):
        """Log provenance for every action"""
        provenance_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'data': data
        }

        with open(self.provenance_log, 'a') as f:
            f.write(json.dumps(provenance_entry) + '\n')

    def execute_query(self, query: str, range_str: str) -> Dict:
        """Execute EPO query with full tracking"""

        query_start = datetime.now()

        # Build request
        params = {
            'q': query,
            'Range': range_str
        }

        # Log query attempt
        self.log_provenance('query_attempt', {
            'query': query,
            'range': range_str,
            'url': self.search_url,
            'timestamp': query_start.isoformat()
        })

        try:
            # Execute request
            response = self.session.get(
                self.search_url,
                params=params,
                timeout=15
            )

            query_end = datetime.now()
            duration_ms = (query_end - query_start).total_seconds() * 1000

            # Log response
            self.log_provenance('query_response', {
                'query': query,
                'range': range_str,
                'status_code': response.status_code,
                'duration_ms': duration_ms,
                'response_size_bytes': len(response.content),
                'headers': dict(response.headers)
            })

            if response.status_code == 200:
                data = response.json()

                # Extract results with provenance
                result = {
                    'query': query,
                    'range': range_str,
                    'status': 'success',
                    'timestamp': query_start.isoformat(),
                    'duration_ms': duration_ms,
                    'raw_response': data,
                    'provenance': {
                        'source': 'EPO OPS API v3.2',
                        'url': self.search_url,
                        'access_token_used': self.access_token[:8] + '...',
                        'response_headers': dict(response.headers)
                    }
                }

                # Parse count and patents
                total_count = 0
                patents = []

                if 'ops:world-patent-data' in data:
                    world_data = data['ops:world-patent-data']
                    if 'ops:biblio-search' in world_data:
                        biblio_search = world_data['ops:biblio-search']
                        if '@total-result-count' in biblio_search:
                            total_count = int(biblio_search['@total-result-count'])

                        if 'ops:search-result' in biblio_search:
                            search_results = biblio_search['ops:search-result']
                            if isinstance(search_results, list):
                                patents = search_results
                            elif search_results:
                                patents = [search_results]

                result['total_count'] = total_count
                result['patents_in_response'] = len(patents)
                result['patents'] = patents

                return result

            else:
                # Handle error
                return {
                    'query': query,
                    'range': range_str,
                    'status': 'error',
                    'status_code': response.status_code,
                    'error_text': response.text[:500],
                    'timestamp': query_start.isoformat()
                }

        except Exception as e:
            # Log exception
            self.log_provenance('query_exception', {
                'query': query,
                'range': range_str,
                'exception': str(e),
                'timestamp': datetime.now().isoformat()
            })

            return {
                'query': query,
                'range': range_str,
                'status': 'exception',
                'exception': str(e),
                'timestamp': query_start.isoformat()
            }

    def collect_with_provenance(self, query: str, description: str, expected_count: Optional[int] = None):
        """Collect patents with complete provenance tracking"""

        print(f"\n{'='*60}")
        print(f"Collecting: {description}")
        print(f"Query: {query}")
        if expected_count:
            print(f"Expected count (from previous analysis): {expected_count}")
        print(f"{'='*60}")

        collection_start = datetime.now()

        # First get total count
        count_result = self.execute_query(query, "1-1")

        if count_result['status'] != 'success':
            print(f"Error getting count: {count_result.get('status_code', count_result.get('exception'))}")
            return None

        total_count = count_result['total_count']
        print(f"Actual count from API: {total_count}")

        # Collection metadata
        collection_data = {
            'description': description,
            'query': query,
            'expected_count': expected_count,
            'api_reported_count': total_count,
            'collection_start': collection_start.isoformat(),
            'api_queries': [],
            'patents_collected': [],
            'provenance': {
                'collector': 'EPOProvenanceCollector',
                'source': 'EPO OPS API v3.2',
                'authentication': 'Bearer token',
                'rate_limit': '30 requests/minute'
            }
        }

        # Collect patents (max 2000 accessible)
        max_accessible = min(total_count, 2000)

        if total_count > 0 and total_count <= 2000:
            print(f"Collecting {total_count} patents...")

            # Collect in batches of 100
            for start in range(1, max_accessible + 1, 100):
                end = min(start + 99, max_accessible)
                range_str = f"{start}-{end}"

                print(f"  Fetching range {range_str}...")

                result = self.execute_query(query, range_str)

                # Store query metadata
                collection_data['api_queries'].append({
                    'range': range_str,
                    'status': result['status'],
                    'timestamp': result['timestamp'],
                    'patents_returned': result.get('patents_in_response', 0)
                })

                if result['status'] == 'success':
                    # Extract patents with provenance
                    for patent in result.get('patents', []):
                        patent_with_provenance = {
                            'data': patent,
                            'provenance': {
                                'query': query,
                                'range': range_str,
                                'api_response_time': result['timestamp'],
                                'position_in_response': len(collection_data['patents_collected'])
                            }
                        }
                        collection_data['patents_collected'].append(patent_with_provenance)

                    print(f"    Retrieved {result.get('patents_in_response', 0)} patents")
                else:
                    print(f"    Error: {result.get('status_code', result.get('exception'))}")

                # Rate limiting
                time.sleep(2)

        elif total_count > 2000:
            print(f"Dataset exceeds 2000 limit - needs segmentation")
            print(f"Only first 2000 accessible via API")
            collection_data['note'] = 'Dataset truncated at API limit of 2000'

        # Calculate collection statistics
        collection_end = datetime.now()
        collection_data['collection_end'] = collection_end.isoformat()
        collection_data['collection_duration_seconds'] = (collection_end - collection_start).total_seconds()
        collection_data['total_patents_collected'] = len(collection_data['patents_collected'])
        collection_data['collection_complete'] = collection_data['total_patents_collected'] == min(total_count, 2000)

        # Save collection
        if collection_data['patents_collected']:
            # Generate unique filename with hash for verification
            data_hash = hashlib.sha256(
                json.dumps(collection_data['patents_collected'], sort_keys=True).encode()
            ).hexdigest()[:8]

            filename = f"{description.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{data_hash}.json"
            filepath = self.output_dir / filename

            collection_data['file_hash'] = data_hash
            collection_data['file_path'] = str(filepath)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(collection_data, f, indent=2, ensure_ascii=False)

            print(f"\nCollection saved:")
            print(f"  File: {filepath}")
            print(f"  Patents collected: {collection_data['total_patents_collected']}")
            print(f"  Hash: {data_hash}")

            # Log collection completion
            self.log_provenance('collection_complete', {
                'description': description,
                'query': query,
                'patents_collected': collection_data['total_patents_collected'],
                'file_path': str(filepath),
                'file_hash': data_hash
            })

        return collection_data

    def run_priority_collections(self):
        """Run high-priority collections with provenance"""

        print("="*60)
        print("EPO Patent Collection with Full Provenance")
        print(f"Start time: {self.start_time.isoformat()}")
        print("="*60)

        # Priority collections - joint patents and small datasets
        priority_queries = [
            ("pa=china AND pa=germany", "China-Germany Joint Patents", 275),
            ("pa=china AND pa=france", "China-France Joint Patents", 276),
            ("pa=china AND pa=italy", "China-Italy Joint Patents", 126),
            ("pa=huawei AND pa=siemens", "Huawei-Siemens Joint Patents", 18),
            ("pa=huawei AND pa=nokia", "Huawei-Nokia Joint Patents", 34),
            ("txt=\"quantum computing\" AND pa=china", "Quantum Computing China", 182),
            ("txt=\"5G infrastructure\"", "5G Infrastructure Patents", 26),
            ("pa=\"hong kong\" AND pa=\"holdings\"", "Hong Kong Holdings Patents", 162),
        ]

        summary = {
            'collection_session': {
                'start_time': self.start_time.isoformat(),
                'collector': 'EPOProvenanceCollector',
                'collections': []
            }
        }

        for query, description, expected in priority_queries:
            result = self.collect_with_provenance(query, description, expected)

            if result:
                summary['collection_session']['collections'].append({
                    'description': description,
                    'query': query,
                    'expected_count': expected,
                    'api_count': result['api_reported_count'],
                    'collected': result['total_patents_collected'],
                    'complete': result['collection_complete'],
                    'file_hash': result.get('file_hash'),
                    'file_path': result.get('file_path')
                })

        # Save session summary
        summary['collection_session']['end_time'] = datetime.now().isoformat()
        summary['collection_session']['total_collections'] = len(summary['collection_session']['collections'])
        summary['collection_session']['total_patents'] = sum(
            c['collected'] for c in summary['collection_session']['collections']
        )

        summary_file = self.output_dir / f"session_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print("\n" + "="*60)
        print("COLLECTION SESSION COMPLETE")
        print("="*60)
        print(f"Collections completed: {summary['collection_session']['total_collections']}")
        print(f"Total patents collected: {summary['collection_session']['total_patents']}")
        print(f"Session summary: {summary_file}")
        print(f"Provenance log: {self.provenance_log}")

        return summary

def main():
    collector = EPOProvenanceCollector()
    collector.run_priority_collections()

if __name__ == "__main__":
    main()
