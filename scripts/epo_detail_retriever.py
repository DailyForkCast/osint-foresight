#!/usr/bin/env python3
"""
EPO Patent Detail Retriever
Retrieves full patent details from references with provenance
"""

import requests
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EPODetailRetriever:
    """Retrieve full patent details from EPO"""

    def __init__(self):
        self.start_time = datetime.now()

        # Paths
        self.config_path = Path("C:/Projects/OSINT - Foresight/config/patent_auth.json")
        self.input_dir = Path("F:/OSINT_DATA/epo_provenance_collection")
        self.output_dir = Path("F:/OSINT_DATA/epo_patent_details")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Authenticate
        self.authenticate()

    def authenticate(self):
        """Refresh and load authentication"""
        import subprocess
        subprocess.run(
            ["python", "scripts/epo_auth_from_config.py"],
            capture_output=True,
            cwd="C:/Projects/OSINT - Foresight"
        )

        with open(self.config_path, 'r') as f:
            config = json.load(f)

        self.access_token = config['epo_ops']['access_token']

        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'User-Agent': 'OSINT-Research-System/1.0'
        })

        # EPO endpoints
        self.base_url = "https://ops.epo.org/3.2/rest-services"

    def get_patent_details(self, country: str, doc_number: str, kind: str) -> Dict:
        """Retrieve full patent details from EPO"""

        # Construct URL for bibliographic data
        url = f"{self.base_url}/published-data/publication/docdb/{country}.{doc_number}.{kind}/biblio"

        try:
            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                return {
                    'status': 'success',
                    'patent_id': f"{country}{doc_number}{kind}",
                    'url': url,
                    'data': response.json(),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'patent_id': f"{country}{doc_number}{kind}",
                    'status_code': response.status_code,
                    'error': response.text[:200]
                }

        except Exception as e:
            return {
                'status': 'exception',
                'patent_id': f"{country}{doc_number}{kind}",
                'exception': str(e)
            }

    def process_collection_file(self, filepath: Path) -> Dict:
        """Process a collection file and retrieve full details"""

        print(f"\nProcessing: {filepath.name}")

        # Load collection data
        with open(filepath, 'r', encoding='utf-8') as f:
            collection_data = json.load(f)

        description = collection_data.get('description', 'Unknown')
        query = collection_data.get('query', '')

        print(f"Description: {description}")
        print(f"Query: {query}")
        print(f"Patents in collection: {len(collection_data.get('patents_collected', []))}")

        # Results container
        detailed_results = {
            'original_file': str(filepath),
            'description': description,
            'query': query,
            'processing_time': datetime.now().isoformat(),
            'patents_detailed': [],
            'statistics': {
                'total_references': 0,
                'details_retrieved': 0,
                'errors': 0
            }
        }

        # Process each patent reference
        for patent_entry in collection_data.get('patents_collected', []):
            patent_data = patent_entry.get('data', {})

            # Extract publication references
            pub_refs = patent_data.get('ops:publication-reference', [])
            if not isinstance(pub_refs, list):
                pub_refs = [pub_refs]

            for ref in pub_refs:
                if 'document-id' in ref:
                    doc_id = ref['document-id']

                    # Extract identifiers
                    country = doc_id.get('country', {}).get('$', '')
                    doc_number = doc_id.get('doc-number', {}).get('$', '')
                    kind = doc_id.get('kind', {}).get('$', '')

                    if country and doc_number:
                        detailed_results['statistics']['total_references'] += 1

                        # Retrieve full details
                        print(f"  Retrieving: {country}{doc_number}{kind}")
                        details = self.get_patent_details(country, doc_number, kind)

                        if details['status'] == 'success':
                            detailed_results['statistics']['details_retrieved'] += 1

                            # Extract key information
                            patent_info = self.extract_patent_info(details['data'])
                            patent_info['provenance'] = {
                                'source_file': str(filepath),
                                'patent_id': f"{country}{doc_number}{kind}",
                                'retrieval_time': details['timestamp'],
                                'api_url': details['url']
                            }

                            detailed_results['patents_detailed'].append(patent_info)
                        else:
                            detailed_results['statistics']['errors'] += 1

                        # Rate limiting
                        time.sleep(2)

        return detailed_results

    def extract_patent_info(self, epo_data: Dict) -> Dict:
        """Extract structured information from EPO response"""

        info = {
            'patent_number': '',
            'title': '',
            'abstract': '',
            'applicants': [],
            'inventors': [],
            'publication_date': '',
            'priority_date': '',
            'classifications': [],
            'raw_data': epo_data
        }

        try:
            if 'ops:world-patent-data' in epo_data:
                wpd = epo_data['ops:world-patent-data']

                if 'exchange-documents' in wpd:
                    ex_docs = wpd['exchange-documents']

                    if 'exchange-document' in ex_docs:
                        doc = ex_docs['exchange-document']

                        # Handle single or multiple documents
                        if isinstance(doc, list):
                            doc = doc[0]

                        # Extract bibliographic data
                        if 'bibliographic-data' in doc:
                            biblio = doc['bibliographic-data']

                            # Title
                            if 'invention-title' in biblio:
                                titles = biblio['invention-title']
                                if isinstance(titles, list):
                                    for title in titles:
                                        if title.get('@lang') == 'en':
                                            info['title'] = title.get('$', '')
                                            break
                                    if not info['title'] and titles:
                                        info['title'] = titles[0].get('$', '')
                                elif isinstance(titles, dict):
                                    info['title'] = titles.get('$', '')

                            # Abstract
                            if 'abstract' in doc:
                                abstracts = doc['abstract']
                                if isinstance(abstracts, list):
                                    for abstract in abstracts:
                                        if abstract.get('@lang') == 'en':
                                            if 'p' in abstract:
                                                info['abstract'] = abstract['p'].get('$', '')
                                                break
                                elif isinstance(abstracts, dict) and 'p' in abstracts:
                                    info['abstract'] = abstracts['p'].get('$', '')

                            # Applicants
                            if 'parties' in biblio and 'applicants' in biblio['parties']:
                                applicants = biblio['parties']['applicants']
                                if 'applicant' in applicants:
                                    app_list = applicants['applicant']
                                    if not isinstance(app_list, list):
                                        app_list = [app_list]

                                    for app in app_list:
                                        if 'applicant-name' in app and 'name' in app['applicant-name']:
                                            name = app['applicant-name']['name'].get('$', '')
                                            country = app.get('residence', {}).get('country', {}).get('$', '')
                                            info['applicants'].append({
                                                'name': name,
                                                'country': country
                                            })

                            # Inventors
                            if 'parties' in biblio and 'inventors' in biblio['parties']:
                                inventors = biblio['parties']['inventors']
                                if 'inventor' in inventors:
                                    inv_list = inventors['inventor']
                                    if not isinstance(inv_list, list):
                                        inv_list = [inv_list]

                                    for inv in inv_list:
                                        if 'inventor-name' in inv and 'name' in inv['inventor-name']:
                                            name = inv['inventor-name']['name'].get('$', '')
                                            info['inventors'].append(name)

                            # Dates
                            if 'publication-reference' in biblio:
                                pub_ref = biblio['publication-reference']
                                if 'document-id' in pub_ref:
                                    doc_ids = pub_ref['document-id']
                                    if not isinstance(doc_ids, list):
                                        doc_ids = [doc_ids]
                                    for doc_id in doc_ids:
                                        if 'date' in doc_id:
                                            info['publication_date'] = doc_id['date'].get('$', '')
                                            break

                            # Classifications
                            if 'classification-ipc' in biblio:
                                ipcs = biblio['classification-ipc']
                                if 'main-classification' in ipcs:
                                    info['classifications'].append({
                                        'type': 'IPC',
                                        'code': ipcs['main-classification'].get('$', '')
                                    })

        except Exception as e:
            logger.error(f"Error extracting patent info: {e}")

        return info

    def process_all_collections(self):
        """Process all collection files"""

        print("="*60)
        print("EPO Patent Detail Retrieval")
        print(f"Start: {self.start_time.isoformat()}")
        print("="*60)

        # Find all collection JSON files
        collection_files = list(self.input_dir.glob("*Joint_Patents*.json"))
        collection_files.extend(list(self.input_dir.glob("*Computing*.json")))
        collection_files.extend(list(self.input_dir.glob("*Infrastructure*.json")))
        collection_files.extend(list(self.input_dir.glob("*Holdings*.json")))

        # Filter out summary files
        collection_files = [f for f in collection_files if 'summary' not in f.name.lower()]

        print(f"Found {len(collection_files)} collection files to process")

        all_results = {
            'processing_session': {
                'start_time': self.start_time.isoformat(),
                'collections_processed': []
            }
        }

        for filepath in collection_files:
            results = self.process_collection_file(filepath)

            # Save individual results
            output_file = self.output_dir / f"details_{filepath.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            print(f"  Saved: {output_file.name}")
            print(f"  Details retrieved: {results['statistics']['details_retrieved']}/{results['statistics']['total_references']}")

            all_results['processing_session']['collections_processed'].append({
                'file': filepath.name,
                'description': results['description'],
                'details_retrieved': results['statistics']['details_retrieved'],
                'total_references': results['statistics']['total_references'],
                'output_file': str(output_file)
            })

        # Save session summary
        all_results['processing_session']['end_time'] = datetime.now().isoformat()
        all_results['processing_session']['total_files'] = len(collection_files)
        all_results['processing_session']['total_patents_detailed'] = sum(
            r['details_retrieved'] for r in all_results['processing_session']['collections_processed']
        )

        summary_file = self.output_dir / f"detail_retrieval_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        print("\n" + "="*60)
        print("DETAIL RETRIEVAL COMPLETE")
        print("="*60)
        print(f"Collections processed: {len(collection_files)}")
        print(f"Total patents detailed: {all_results['processing_session']['total_patents_detailed']}")
        print(f"Output directory: {self.output_dir}")
        print(f"Summary: {summary_file}")

        return all_results

def main():
    retriever = EPODetailRetriever()
    retriever.process_all_collections()

if __name__ == "__main__":
    main()
