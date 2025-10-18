#!/usr/bin/env python3
"""
EPO Strategic Patent Analysis
Data-driven analysis of technology patterns - no assumptions or interpretations
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def analyze_strategic_patents():
    """Analyze strategic patent patterns with zero assumptions"""

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
    print("EPO Strategic Patent Analysis")
    print("Data collection only - no interpretations")
    print("=" * 60)

    search_url = "https://ops.epo.org/3.2/rest-services/published-data/search"

    # Strategic priorities - data collection only
    analysis_categories = {

        "Chinese_Companies_EU_Patents": {
            "description": "Patents filed by Chinese entities in EU",
            "queries": [
                ('pa=huawei', 'Huawei patents'),
                ('pa=xiaomi', 'Xiaomi patents'),
                ('pa=alibaba', 'Alibaba patents'),
                ('pa=tencent', 'Tencent patents'),
                ('pa=baidu', 'Baidu patents'),
                ('pa=zte', 'ZTE patents'),
                ('pa=lenovo', 'Lenovo patents'),
                ('pa=byd', 'BYD patents'),
                ('pa=dji', 'DJI patents'),
                ('pa=bytedance', 'ByteDance patents'),
                ('pa="china mobile"', 'China Mobile patents'),
                ('pa="china telecom"', 'China Telecom patents'),
            ]
        },

        "Technology_Specific": {
            "description": "Critical technology areas",
            "queries": [
                # 5G/6G
                ('txt=5G AND pa=china', '5G with China applicants'),
                ('txt=6G AND pa=china', '6G with China applicants'),
                ('txt="5G infrastructure"', '5G infrastructure'),

                # Quantum
                ('txt="quantum computing" AND pa=china', 'Quantum computing China'),
                ('txt="quantum communication"', 'Quantum communication'),
                ('txt="quantum encryption"', 'Quantum encryption'),

                # Semiconductors
                ('txt=semiconductor AND pa=china', 'Semiconductor China'),
                ('txt="chip design"', 'Chip design'),
                ('txt="integrated circuit"', 'Integrated circuits'),

                # AI/ML
                ('txt="artificial intelligence" AND pa=china', 'AI China'),
                ('txt="machine learning" AND pa=china', 'ML China'),
                ('txt="neural network"', 'Neural networks'),

                # Space Technology
                ('txt=satellite AND pa=china', 'Satellite China'),
                ('txt="low earth orbit"', 'Low earth orbit'),
                ('txt="space technology"', 'Space technology'),

                # Neurocognitive
                ('txt="brain computer interface"', 'Brain-computer interface'),
                ('txt="neurotechnology"', 'Neurotechnology'),
                ('txt="cognitive computing"', 'Cognitive computing'),

                # Biotechnology
                ('txt=biotechnology AND pa=china', 'Biotechnology China'),
                ('txt="gene editing"', 'Gene editing'),
                ('txt=CRISPR', 'CRISPR technology'),

                # Advanced Materials
                ('txt="graphene" AND pa=china', 'Graphene China'),
                ('txt="metamaterial"', 'Metamaterials'),
                ('txt="nanomaterial"', 'Nanomaterials'),
            ]
        },

        "Joint_Applications": {
            "description": "Patents with multiple country applicants",
            "queries": [
                ('pa=china AND pa=germany', 'China-Germany joint'),
                ('pa=china AND pa=france', 'China-France joint'),
                ('pa=china AND pa=italy', 'China-Italy joint'),
                ('pa=china AND pa=netherlands', 'China-Netherlands joint'),
                ('pa=huawei AND pa=siemens', 'Huawei-Siemens'),
                ('pa=huawei AND pa=nokia', 'Huawei-Nokia'),
                ('pa=china AND pa=university', 'China-University joint'),
            ]
        },

        "Corporate_Structures": {
            "description": "Corporate entity patterns",
            "queries": [
                ('pa="beijing" AND pa="limited"', 'Beijing limited companies'),
                ('pa="shanghai" AND pa="technology"', 'Shanghai tech companies'),
                ('pa="shenzhen" AND pa="innovation"', 'Shenzhen innovation companies'),
                ('pa="hong kong" AND pa="holdings"', 'Hong Kong holdings'),
                ('pa="luxembourg" AND pa=china', 'Luxembourg-China connection'),
                ('pa="ireland" AND pa=china', 'Ireland-China connection'),
                ('pa="cayman" AND pa=technology', 'Cayman tech entities'),
            ]
        }
    }

    results = {
        'analysis_time': datetime.now().isoformat(),
        'categories': {},
        'raw_data': [],
        'statistics': {
            'total_queries': 0,
            'successful_queries': 0,
            'total_patents_found': 0
        }
    }

    # Process each category
    for category_name, category_data in analysis_categories.items():
        print(f"\n{category_name}: {category_data['description']}")
        print("-" * 40)

        category_results = {
            'description': category_data['description'],
            'queries': {}
        }

        for query, description in category_data['queries']:
            results['statistics']['total_queries'] += 1
            print(f"\n  {description}")
            print(f"  Query: {query}")

            try:
                params = {
                    'q': query,
                    'Range': '1-10'  # Get first 10 for detail
                }

                response = session.get(search_url, params=params, timeout=15)

                if response.status_code == 200:
                    data = response.json()

                    # Extract count only - no interpretation
                    total_found = 0
                    patent_samples = []

                    if 'ops:world-patent-data' in data:
                        world_data = data['ops:world-patent-data']
                        if 'ops:biblio-search' in world_data:
                            biblio_search = world_data['ops:biblio-search']
                            if '@total-result-count' in biblio_search:
                                total_found = int(biblio_search['@total-result-count'])

                            # Extract patent details if available
                            if 'ops:search-result' in biblio_search:
                                search_results = biblio_search['ops:search-result']
                                if isinstance(search_results, list):
                                    for result in search_results[:3]:
                                        patent_samples.append(extract_patent_facts(result))
                                elif search_results:
                                    patent_samples.append(extract_patent_facts(search_results))

                    print(f"  Found: {total_found:,} patents")

                    category_results['queries'][description] = {
                        'query': query,
                        'count': total_found,
                        'samples': patent_samples
                    }

                    results['statistics']['successful_queries'] += 1
                    results['statistics']['total_patents_found'] += total_found

                    # Store raw data
                    results['raw_data'].append({
                        'category': category_name,
                        'description': description,
                        'query': query,
                        'count': total_found,
                        'timestamp': datetime.now().isoformat()
                    })

                else:
                    print(f"  Status: {response.status_code}")
                    category_results['queries'][description] = {
                        'query': query,
                        'error': response.status_code
                    }

                time.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"  Error: {str(e)[:100]}")
                category_results['queries'][description] = {
                    'query': query,
                    'exception': str(e)[:200]
                }

        results['categories'][category_name] = category_results

    # Save results - just data, no interpretation
    output_dir = Path("F:/OSINT_DATA/epo_strategic_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save raw JSON
    json_file = output_dir / f"strategic_patent_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Create factual report
    report_file = output_dir / f"strategic_patent_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# EPO Strategic Patent Data Collection\n")
        f.write(f"**Analysis Date:** {results['analysis_time']}\n")
        f.write(f"**Queries Executed:** {results['statistics']['total_queries']}\n")
        f.write(f"**Successful Queries:** {results['statistics']['successful_queries']}\n")
        f.write(f"**Total Patents Found:** {results['statistics']['total_patents_found']:,}\n\n")

        # Report findings by category - facts only
        for category_name, category_data in results['categories'].items():
            f.write(f"\n## {category_name}\n")
            f.write(f"**Description:** {category_data['description']}\n\n")

            # Sort by count
            sorted_queries = sorted(
                [(desc, data) for desc, data in category_data['queries'].items() if 'count' in data],
                key=lambda x: x[1]['count'],
                reverse=True
            )

            for desc, data in sorted_queries:
                f.write(f"- **{desc}**: {data['count']:,} patents\n")
                f.write(f"  - Query: `{data['query']}`\n")

        # Top findings - just numbers
        f.write("\n## Highest Patent Counts\n")
        all_findings = []
        for category_name, category_data in results['categories'].items():
            for desc, data in category_data['queries'].items():
                if 'count' in data:
                    all_findings.append((desc, data['count'], data['query']))

        all_findings.sort(key=lambda x: x[1], reverse=True)

        for desc, count, query in all_findings[:20]:
            f.write(f"1. {desc}: **{count:,}** patents\n")

    print("\n" + "=" * 60)
    print("DATA COLLECTION COMPLETE")
    print("=" * 60)
    print(f"Total queries: {results['statistics']['total_queries']}")
    print(f"Successful: {results['statistics']['successful_queries']}")
    print(f"Total patents found: {results['statistics']['total_patents_found']:,}")
    print(f"\nData saved to: {json_file}")
    print(f"Report saved to: {report_file}")

    return results

def extract_patent_facts(patent_data):
    """Extract only factual information from patent data"""
    facts = {}

    try:
        if 'exchange-document' in patent_data:
            doc = patent_data['exchange-document']

            if 'bibliographic-data' in doc:
                biblio = doc['bibliographic-data']

                # Patent number
                if 'publication-reference' in biblio:
                    pub_ref = biblio['publication-reference']
                    if 'document-id' in pub_ref:
                        doc_id = pub_ref['document-id']
                        if isinstance(doc_id, list):
                            doc_id = doc_id[0]
                        facts['patent_number'] = doc_id.get('doc-number', {}).get('$', '')
                        facts['country'] = doc_id.get('country', {}).get('$', '')

                # Title
                if 'invention-title' in biblio:
                    title = biblio['invention-title']
                    if isinstance(title, list):
                        title = title[0]
                    facts['title'] = title.get('$', '') if isinstance(title, dict) else str(title)

                # Applicants
                if 'parties' in biblio and 'applicants' in biblio['parties']:
                    applicants = biblio['parties']['applicants']
                    if 'applicant' in applicants:
                        app_list = applicants['applicant']
                        if not isinstance(app_list, list):
                            app_list = [app_list]
                        facts['applicants'] = []
                        for app in app_list:
                            if 'applicant-name' in app:
                                name = app['applicant-name']
                                if 'name' in name:
                                    facts['applicants'].append(name['name'].get('$', ''))
    except:
        pass  # If extraction fails, return what we have

    return facts

if __name__ == "__main__":
    # Update todo list
    analyze_strategic_patents()
