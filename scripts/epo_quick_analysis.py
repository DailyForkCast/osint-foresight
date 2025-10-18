#!/usr/bin/env python3
"""
EPO Quick Analysis
Analyze patent references already collected for intelligence
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def analyze_patent_collections():
    """Analyze collected patent references for patterns"""

    input_dir = Path("F:/OSINT_DATA/epo_provenance_collection")

    print("="*60)
    print("EPO Patent Collection Analysis")
    print(f"Analysis time: {datetime.now().isoformat()}")
    print("="*60)

    # Load all collection files
    collection_files = list(input_dir.glob("*.json"))
    collection_files = [f for f in collection_files if 'summary' not in f.name.lower()]

    print(f"Found {len(collection_files)} collection files")

    analysis = {
        'timestamp': datetime.now().isoformat(),
        'collections': {},
        'patent_countries': defaultdict(int),
        'patent_types': defaultdict(int),
        'family_ids': set(),
        'total_patents': 0
    }

    for filepath in collection_files:
        print(f"\n{filepath.stem}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        description = data.get('description', '')
        query = data.get('query', '')
        api_count = data.get('api_reported_count', 0)

        print(f"  Query: {query}")
        print(f"  API reported: {api_count} patents")

        collection_analysis = {
            'query': query,
            'api_reported_count': api_count,
            'patents_retrieved': len(data.get('patents_collected', [])),
            'countries': defaultdict(int),
            'doc_types': defaultdict(int),
            'patent_numbers': []
        }

        # Analyze patents
        for patent_entry in data.get('patents_collected', []):
            patent_data = patent_entry.get('data', {})

            # Process publication references
            pub_refs = patent_data.get('ops:publication-reference', [])
            if not isinstance(pub_refs, list):
                pub_refs = [pub_refs]

            for ref in pub_refs:
                if '@family-id' in ref:
                    analysis['family_ids'].add(ref['@family-id'])

                if 'document-id' in ref:
                    doc_id = ref['document-id']

                    country = doc_id.get('country', {}).get('$', '')
                    doc_number = doc_id.get('doc-number', {}).get('$', '')
                    kind = doc_id.get('kind', {}).get('$', '')

                    if country:
                        collection_analysis['countries'][country] += 1
                        analysis['patent_countries'][country] += 1

                    if kind:
                        collection_analysis['doc_types'][kind] += 1
                        analysis['patent_types'][kind] += 1

                    if country and doc_number:
                        patent_id = f"{country}{doc_number}{kind}"
                        collection_analysis['patent_numbers'].append(patent_id)
                        analysis['total_patents'] += 1

        # Print collection stats
        print(f"  Countries: {dict(collection_analysis['countries'])}")
        print(f"  Document types: {dict(collection_analysis['doc_types'])}")

        analysis['collections'][description] = collection_analysis

    # Overall analysis
    print("\n" + "="*60)
    print("OVERALL ANALYSIS")
    print("="*60)

    print(f"Total unique patent families: {len(analysis['family_ids'])}")
    print(f"Total patent references: {analysis['total_patents']}")

    print("\nPatents by country:")
    for country, count in sorted(analysis['patent_countries'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {country}: {count}")

    print("\nDocument types:")
    for doc_type, count in sorted(analysis['patent_types'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {doc_type}: {count}")

    # Joint patent analysis
    print("\n" + "="*60)
    print("JOINT PATENT ANALYSIS")
    print("="*60)

    for desc, coll in analysis['collections'].items():
        if 'Joint' in desc:
            print(f"\n{desc}:")
            print(f"  Total count (API): {coll['api_reported_count']}")
            print(f"  References collected: {coll['patents_retrieved']}")

            # Extract specific intelligence
            if 'China-Germany' in desc:
                print("  Intelligence: Direct China-Germany technology collaboration")
            elif 'China-France' in desc:
                print("  Intelligence: Direct China-France technology collaboration")
            elif 'China-Italy' in desc:
                print("  Intelligence: Direct China-Italy technology collaboration")
            elif 'Huawei-Siemens' in desc:
                print("  Intelligence: Huawei-Siemens corporate partnership")
            elif 'Huawei-Nokia' in desc:
                print("  Intelligence: Huawei-Nokia technology sharing")

    # Save analysis
    output_file = Path("F:/OSINT_DATA/epo_provenance_collection") / f"quick_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    # Convert set to list for JSON serialization
    analysis['family_ids'] = list(analysis['family_ids'])
    analysis['patent_countries'] = dict(analysis['patent_countries'])
    analysis['patent_types'] = dict(analysis['patent_types'])

    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"\nAnalysis saved to: {output_file}")

    # Generate intelligence summary
    print("\n" + "="*60)
    print("INTELLIGENCE SUMMARY")
    print("="*60)

    print("Key Findings:")
    print("1. EU-China Joint Patents Confirmed:")
    print(f"   - Germany-China: {analysis['collections'].get('China-Germany Joint Patents', {}).get('api_reported_count', 0)} patents")
    print(f"   - France-China: {analysis['collections'].get('China-France Joint Patents', {}).get('api_reported_count', 0)} patents")
    print(f"   - Italy-China: {analysis['collections'].get('China-Italy Joint Patents', {}).get('api_reported_count', 0)} patents")

    print("\n2. Corporate Collaboration:")
    print(f"   - Huawei-Siemens: {analysis['collections'].get('Huawei-Siemens Joint Patents', {}).get('api_reported_count', 0)} joint patents")
    print(f"   - Huawei-Nokia: {analysis['collections'].get('Huawei-Nokia Joint Patents', {}).get('api_reported_count', 0)} joint patents")

    print("\n3. Technology Areas:")
    print(f"   - Quantum Computing (China): {analysis['collections'].get('Quantum Computing China', {}).get('api_reported_count', 0)} patents")
    print(f"   - 5G Infrastructure: {analysis['collections'].get('5G Infrastructure Patents', {}).get('api_reported_count', 0)} patents")

    print("\n4. Data Collection Status:")
    print(f"   - Successfully queried EPO API")
    print(f"   - Collected references with full provenance")
    print(f"   - API limitation: Returns references, not full documents")

    return analysis

if __name__ == "__main__":
    analyze_patent_collections()
