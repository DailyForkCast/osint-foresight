#!/usr/bin/env python3
"""
EPO Paginated Patent Collector - Retrieves patents beyond the 10,000 limit
Uses checkpoint files to track progress and resume collection
"""

import requests
import json
import time
from datetime import datetime
import os
import base64

class EPOPaginatedCollector:
    def __init__(self):
        self.checkpoint_dir = "F:/OSINT_DATA/epo_checkpoints"
        self.output_dir = "F:/OSINT_DATA/epo_paginated"
        self.batch_size = 100  # Patents per request
        self.max_per_session = 2000  # Limit per run to avoid timeout

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
            data={'grant_type': 'client_credentials'}
        )

        if response.status_code == 200:
            return response.json()['access_token']
        return None

    def load_checkpoint(self, query_id):
        """Load checkpoint for a specific query"""
        checkpoint_file = f"{self.checkpoint_dir}/{query_id}_checkpoint.json"

        if os.path.exists(checkpoint_file):
            with open(checkpoint_file, 'r') as f:
                return json.load(f)

        return {
            'query_id': query_id,
            'last_offset': 0,
            'total_found': None,
            'total_retrieved': 0,
            'batches_completed': [],
            'status': 'new',
            'created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }

    def save_checkpoint(self, checkpoint):
        """Save checkpoint for a query"""
        checkpoint['last_updated'] = datetime.now().isoformat()
        checkpoint_file = f"{self.checkpoint_dir}/{checkpoint['query_id']}_checkpoint.json"

        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

    def search_patents_batch(self, query, token, start_from=1, batch_size=100):
        """Search EPO for patents with pagination"""
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }

        # EPO uses 1-based indexing for ranges
        end_at = start_from + batch_size - 1
        url = f"https://ops.epo.org/3.2/rest-services/published-data/search/abstract"

        params = {
            'q': query,
            'Range': f"{start_from}-{end_at}"
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                print(f"Rate limit hit. Status: {response.status_code}")
                time.sleep(60)  # Wait a minute
                return None
            else:
                print(f"Error {response.status_code} at range {start_from}-{end_at}")
                return None

        except Exception as e:
            print(f"Request error: {e}")
            return None

    def extract_patent_data(self, response_data):
        """Extract patent information from EPO response"""
        patents = []

        try:
            if 'ops:world-patent-data' in response_data:
                search_result = response_data['ops:world-patent-data'].get('ops:biblio-search', {})

                # Get total count if available
                total_count = search_result.get('@total-result-count', 0)

                # Extract patent documents
                search_results = search_result.get('ops:search-result', {})
                if search_results:
                    # Handle both single and multiple results
                    exchange_docs = search_results.get('exchange-documents', [])
                    if not isinstance(exchange_docs, list):
                        exchange_docs = [exchange_docs]

                    for doc in exchange_docs:
                        if doc and 'exchange-document' in doc:
                            patent_info = self.parse_patent_document(doc['exchange-document'])
                            if patent_info:
                                patents.append(patent_info)

                return patents, int(total_count) if total_count else 0

        except Exception as e:
            print(f"Error extracting patent data: {e}")

        return patents, 0

    def parse_patent_document(self, doc):
        """Parse individual patent document"""
        try:
            patent = {
                'publication_number': None,
                'title': None,
                'abstract': None,
                'applicants': [],
                'inventors': [],
                'publication_date': None,
                'country': None
            }

            # Extract publication reference
            if 'bibliographic-data' in doc:
                biblio = doc['bibliographic-data']

                # Publication number
                if 'publication-reference' in biblio:
                    pub_ref = biblio['publication-reference']
                    if 'document-id' in pub_ref:
                        doc_id = pub_ref['document-id']
                        if isinstance(doc_id, list):
                            doc_id = doc_id[0]
                        patent['publication_number'] = doc_id.get('doc-number')
                        patent['country'] = doc_id.get('country')

                # Title
                if 'invention-title' in biblio:
                    title = biblio['invention-title']
                    if isinstance(title, list):
                        title = title[0]
                    patent['title'] = title if isinstance(title, str) else str(title)

            # Abstract
            if 'abstract' in doc:
                abstract = doc['abstract']
                if isinstance(abstract, dict) and 'p' in abstract:
                    patent['abstract'] = str(abstract['p'])

            return patent

        except Exception as e:
            print(f"Error parsing document: {e}")
            return None

    def collect_with_pagination(self, query, query_id, description):
        """Collect patents with pagination, saving progress"""
        print("\n" + "="*60)
        print(f"Collecting: {description}")
        print(f"Query: {query}")
        print("="*60)

        # Load checkpoint
        checkpoint = self.load_checkpoint(query_id)
        print(f"Checkpoint status: {checkpoint['status']}")
        print(f"Previously retrieved: {checkpoint['total_retrieved']}")

        # Get access token
        token = self.get_access_token()
        if not token:
            print("Failed to get access token")
            return checkpoint

        # Start from where we left off
        current_offset = checkpoint['last_offset']
        patents_collected = []
        session_count = 0

        while session_count < self.max_per_session:
            # Calculate range for this batch
            start_from = current_offset + 1

            print(f"\nBatch: Requesting patents {start_from} to {start_from + self.batch_size - 1}")

            # Make request
            response_data = self.search_patents_batch(query, token, start_from, self.batch_size)

            if not response_data:
                print("No response or rate limited. Stopping.")
                break

            # Extract patents
            batch_patents, total_count = self.extract_patent_data(response_data)

            if not batch_patents:
                print("No more patents found. Collection complete.")
                checkpoint['status'] = 'complete'
                break

            patents_collected.extend(batch_patents)
            session_count += len(batch_patents)

            # Update checkpoint
            current_offset = start_from + len(batch_patents) - 1
            checkpoint['last_offset'] = current_offset
            checkpoint['total_retrieved'] += len(batch_patents)
            checkpoint['batches_completed'].append({
                'range': f"{start_from}-{start_from + len(batch_patents) - 1}",
                'count': len(batch_patents),
                'timestamp': datetime.now().isoformat()
            })

            if checkpoint['total_found'] is None:
                checkpoint['total_found'] = total_count

            # Save checkpoint every batch
            self.save_checkpoint(checkpoint)

            print(f"  Retrieved: {len(batch_patents)} patents")
            print(f"  Total so far: {checkpoint['total_retrieved']} / {checkpoint['total_found']}")

            # Check if we've got everything
            if checkpoint['total_retrieved'] >= checkpoint['total_found']:
                checkpoint['status'] = 'complete'
                print("\nAll patents collected!")
                break

            # Rate limiting
            time.sleep(1)

        # Save collected patents
        if patents_collected:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"{self.output_dir}/{query_id}_{timestamp}.json"

            output_data = {
                'query': query,
                'description': description,
                'collection_time': datetime.now().isoformat(),
                'batch_info': {
                    'batch_start': checkpoint['last_offset'] - len(patents_collected) + 1,
                    'batch_end': checkpoint['last_offset'],
                    'patents_in_batch': len(patents_collected),
                    'total_retrieved': checkpoint['total_retrieved'],
                    'total_available': checkpoint['total_found']
                },
                'patents': patents_collected
            }

            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)

            print(f"\nBatch saved to: {output_file}")

        return checkpoint

def main():
    collector = EPOPaginatedCollector()

    # High-priority queries that hit the 10,000 limit
    queries = [
        {
            'query': 'pa=huawei',
            'id': 'huawei_patents',
            'description': 'Huawei Technologies - All Patents'
        },
        {
            'query': 'txt=semiconductor AND pa=china',
            'id': 'china_semiconductors',
            'description': 'China Semiconductor Patents'
        },
        {
            'query': 'pa=alibaba',
            'id': 'alibaba_patents',
            'description': 'Alibaba Group Patents'
        }
    ]

    print("="*60)
    print("EPO PAGINATED PATENT COLLECTION")
    print("Collecting patents beyond 10,000 limit")
    print("="*60)

    for q in queries:
        checkpoint = collector.collect_with_pagination(
            q['query'],
            q['id'],
            q['description']
        )

        print(f"\nProgress for {q['description']}:")
        print(f"  Status: {checkpoint['status']}")
        print(f"  Retrieved: {checkpoint['total_retrieved']} / {checkpoint.get('total_found', 'Unknown')}")

        if checkpoint['status'] != 'complete' and checkpoint['total_found']:
            remaining = checkpoint['total_found'] - checkpoint['total_retrieved']
            print(f"  Remaining: {remaining} patents")
            print(f"  Resume from offset: {checkpoint['last_offset']}")

if __name__ == "__main__":
    main()
