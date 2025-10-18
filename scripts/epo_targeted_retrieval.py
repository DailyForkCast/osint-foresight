#!/usr/bin/env python3
"""
EPO Targeted Patent Retrieval
Retrieve full details for high-value EU-China collaboration patents
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EPOTargetedRetrieval:
    """Retrieve specific high-value patents"""

    def __init__(self):
        self.start_time = datetime.now()

        # Setup paths
        self.config_path = Path("C:/Projects/OSINT - Foresight/config/patent_auth.json")
        self.input_dir = Path("F:/OSINT_DATA/epo_provenance_collection")
        self.output_dir = Path("F:/OSINT_DATA/epo_targeted_patents")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Authenticate
        self.authenticate()

    def authenticate(self):
        """Authenticate with EPO"""
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

        self.base_url = "https://ops.epo.org/3.2/rest-services"

    def get_full_document(self, country: str, doc_number: str, kind: str) -> Dict:
        """Get full patent document including abstract and claims"""

        patent_id = f"{country}{doc_number}{kind}"
        results = {
            'patent_id': patent_id,
            'retrieval_time': datetime.now().isoformat(),
            'sections': {}
        }

        # Endpoints to try
        endpoints = [
            ('biblio', f"{self.base_url}/published-data/publication/docdb/{country}.{doc_number}.{kind}/biblio"),
            ('abstract', f"{self.base_url}/published-data/publication/docdb/{country}.{doc_number}.{kind}/abstract"),
            ('description', f"{self.base_url}/published-data/publication/docdb/{country}.{doc_number}.{kind}/description"),
            ('claims', f"{self.base_url}/published-data/publication/docdb/{country}.{doc_number}.{kind}/claims")
        ]

        for section_name, url in endpoints:
            try:
                response = self.session.get(url, timeout=15)

                if response.status_code == 200:
                    results['sections'][section_name] = {
                        'status': 'success',
                        'data': response.json()
                    }
                else:
                    results['sections'][section_name] = {
                        'status': 'error',
                        'status_code': response.status_code
                    }

                time.sleep(1)  # Rate limiting

            except Exception as e:
                results['sections'][section_name] = {
                    'status': 'exception',
                    'error': str(e)
                }

        return results

    def extract_key_info(self, full_document: Dict) -> Dict:
        """Extract key information from full document"""

        info = {
            'patent_id': full_document['patent_id'],
            'title': '',
            'abstract': '',
            'applicants': [],
            'inventors': [],
            'classifications': [],
            'claims_count': 0,
            'priority_date': '',
            'publication_date': ''
        }

        # Extract from biblio section
        if 'biblio' in full_document['sections'] and full_document['sections']['biblio']['status'] == 'success':
            biblio_data = full_document['sections']['biblio']['data']

            # Parse bibliographic data
            if 'ops:world-patent-data' in biblio_data:
                wpd = biblio_data['ops:world-patent-data']

                if 'exchange-documents' in wpd:
                    ex_docs = wpd['exchange-documents']

                    if 'exchange-document' in ex_docs:
                        doc = ex_docs['exchange-document']
                        if isinstance(doc, list):
                            doc = doc[0]

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

                            # Classifications
                            if 'classifications-ipcr' in biblio:
                                ipcr = biblio['classifications-ipcr']
                                if 'classification-ipcr' in ipcr:
                                    class_list = ipcr['classification-ipcr']
                                    if not isinstance(class_list, list):
                                        class_list = [class_list]

                                    for cls in class_list[:5]:  # Top 5 classifications
                                        text = cls.get('text', {}).get('$', '')
                                        if text:
                                            info['classifications'].append(text)

        # Extract abstract
        if 'abstract' in full_document['sections'] and full_document['sections']['abstract']['status'] == 'success':
            abstract_data = full_document['sections']['abstract']['data']

            if 'ops:world-patent-data' in abstract_data:
                wpd = abstract_data['ops:world-patent-data']

                if 'exchange-documents' in wpd:
                    ex_docs = wpd['exchange-documents']

                    if 'exchange-document' in ex_docs:
                        doc = ex_docs['exchange-document']
                        if isinstance(doc, list):
                            doc = doc[0]

                        if 'abstract' in doc:
                            abstracts = doc['abstract']
                            if isinstance(abstracts, list):
                                for abstract in abstracts:
                                    if abstract.get('@lang') == 'en' and 'p' in abstract:
                                        info['abstract'] = abstract['p'].get('$', '')
                                        break
                            elif isinstance(abstracts, dict) and 'p' in abstracts:
                                info['abstract'] = abstracts['p'].get('$', '')

        # Count claims
        if 'claims' in full_document['sections'] and full_document['sections']['claims']['status'] == 'success':
            claims_data = full_document['sections']['claims']['data']

            # Count claim elements
            claims_str = json.dumps(claims_data)
            info['claims_count'] = claims_str.count('claim-text')

        return info

    def retrieve_priority_patents(self):
        """Retrieve full details for priority patents"""

        print("="*60)
        print("EPO Targeted Patent Retrieval")
        print(f"Start: {self.start_time.isoformat()}")
        print("="*60)

        # Priority targets - most valuable patents
        priority_targets = [
            # Huawei-Siemens collaborations
            ("US", "2024217973", "A1", "Huawei-Siemens Joint"),
            ("CN", "119943666", "A", "Huawei-Siemens Joint"),

            # China-Germany high-tech
            ("CN", "222866222", "U", "China-Germany Joint"),
            ("CN", "119781723", "A", "China-Germany Joint"),

            # Quantum computing
            ("CN", "119863925", "A", "Quantum Computing China"),
            ("WO", "2024193329", "A1", "Quantum Computing China"),

            # 5G Infrastructure
            ("CN", "119865988", "A", "5G Infrastructure"),
            ("US", "2024323765", "A1", "5G Infrastructure"),

            # China-France collaboration
            ("CN", "119859901", "A", "China-France Joint"),
            ("WO", "2024187844", "A1", "China-France Joint")
        ]

        all_results = {
            'retrieval_session': {
                'start_time': self.start_time.isoformat(),
                'patents_retrieved': []
            }
        }

        for country, doc_number, kind, category in priority_targets:
            patent_id = f"{country}{doc_number}{kind}"
            print(f"\nRetrieving: {patent_id} ({category})")

            # Get full document
            full_doc = self.get_full_document(country, doc_number, kind)

            # Extract key information
            key_info = self.extract_key_info(full_doc)
            key_info['category'] = category

            # Print summary
            print(f"  Title: {key_info['title'][:60]}..." if key_info['title'] else "  Title: Not available")
            print(f"  Applicants: {len(key_info['applicants'])}")
            if key_info['applicants']:
                for app in key_info['applicants'][:3]:  # First 3 applicants
                    # Handle unicode characters in names
                    name = app['name'].encode('ascii', 'ignore').decode('ascii')
                    print(f"    - {name} ({app['country']})")
            print(f"  Abstract: {'Available' if key_info['abstract'] else 'Not available'}")
            print(f"  Claims: {key_info['claims_count']}")
            print(f"  Classifications: {len(key_info['classifications'])}")

            # Save individual patent
            patent_file = self.output_dir / f"{patent_id.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            full_doc['extracted_info'] = key_info

            with open(patent_file, 'w', encoding='utf-8') as f:
                json.dump(full_doc, f, indent=2, ensure_ascii=False)

            all_results['retrieval_session']['patents_retrieved'].append({
                'patent_id': patent_id,
                'category': category,
                'title': key_info['title'][:100] if key_info['title'] else '',
                'applicants_count': len(key_info['applicants']),
                'has_abstract': bool(key_info['abstract']),
                'claims_count': key_info['claims_count'],
                'file': str(patent_file)
            })

            time.sleep(2)  # Rate limiting

        # Save session summary
        all_results['retrieval_session']['end_time'] = datetime.now().isoformat()
        all_results['retrieval_session']['total_patents'] = len(all_results['retrieval_session']['patents_retrieved'])

        summary_file = self.output_dir / f"targeted_retrieval_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        print("\n" + "="*60)
        print("TARGETED RETRIEVAL COMPLETE")
        print("="*60)
        print(f"Patents retrieved: {all_results['retrieval_session']['total_patents']}")
        print(f"Output directory: {self.output_dir}")
        print(f"Summary: {summary_file}")

        # Intelligence summary
        print("\n" + "="*60)
        print("INTELLIGENCE SUMMARY")
        print("="*60)

        for patent in all_results['retrieval_session']['patents_retrieved']:
            if patent['has_abstract'] or patent['claims_count'] > 0:
                print(f"\n{patent['category']} - {patent['patent_id']}")
                print(f"  Title: {patent['title']}")
                print(f"  Applicants: {patent['applicants_count']}")
                print(f"  Claims: {patent['claims_count']}")

        return all_results

def main():
    retriever = EPOTargetedRetrieval()
    retriever.retrieve_priority_patents()

if __name__ == "__main__":
    main()
