#!/usr/bin/env python3
"""
Update Harvester with Discovered Paths
Consolidate findings from CEIAS, IFRI, and Arctic Institute investigations
"""

import json
import os
from typing import Dict, List

def load_investigation_results():
    """Load all investigation results"""
    results = {}

    # Load CEIAS results (from successful test)
    ceias_data = {
        'base_url': 'https://ceias.eu',
        'working_paths': [
            '/en/publications',  # Score: 45 (15 pubs * 3)
            '/sk/publications',  # Slovak publications
            '/en/asia',          # Asia content section
            '/sk/asia'           # Slovak Asia section
        ],
        'china_content_found': True,
        'extraction_method': 'custom_ceias_extraction'
    }
    results['ceias'] = ceias_data

    # Load IFRI results
    ifri_file = 'data/test_harvest/ifri_investigation_results.json'
    if os.path.exists(ifri_file):
        with open(ifri_file, 'r', encoding='utf-8') as f:
            ifri_data = json.load(f)

        # Extract recommended paths from IFRI
        ifri_paths = [
            '/fr/regions/asie-et-indo-pacifique',    # Score: 163
            '/fr/publications',                       # Score: 141
            '/fr/actualites',                        # Score: 141
            '/fr/centre-russieeurasie',              # Score: 139
            '/en/regions/asia-and-indo-pacific'      # Score: 88
        ]
        results['ifri'] = {
            'base_url': 'https://www.ifri.org',
            'working_paths': ifri_paths,
            'china_content_found': True,
            'language_notes': 'Primarily French content'
        }

    # Load Arctic Institute results
    arctic_file = 'data/test_harvest/arctic_investigation_results.json'
    if os.path.exists(arctic_file):
        with open(arctic_file, 'r', encoding='utf-8') as f:
            arctic_data = json.load(f)

        # Extract recommended paths from Arctic Institute
        arctic_paths = [
            '/china',                                # Direct China page
            '/chinese',                              # Chinese content page
            '/tags/china',                           # China tagged content
            '/tags/chinese',                         # Chinese tagged content
            '/?s=china',                             # China search results
            '/publications',                         # Publications with China content
            '/geopolitics',                          # Geopolitics section
            '/tag/defense-and-security/'             # Security content
        ]
        results['arctic'] = {
            'base_url': 'https://www.thearcticinstitute.org',
            'working_paths': arctic_paths,
            'china_content_found': True,
            'specialization': 'Arctic geopolitics and China Arctic engagement'
        }

    return results

def generate_updated_source_config():
    """Generate updated source configuration for harvester"""
    results = load_investigation_results()

    updated_sources = {
        'CEIAS': {
            'base_url': 'https://ceias.eu',
            'paths': results['ceias']['working_paths'],
            'extraction_method': 'custom_ceias',
            'language': 'en_sk',
            'notes': 'Requires custom extraction method for article content'
        },

        'IFRI': {
            'base_url': 'https://www.ifri.org',
            'paths': results['ifri']['working_paths'] if 'ifri' in results else [],
            'extraction_method': 'standard_with_french',
            'language': 'fr_en',
            'notes': 'Primarily French language, strong Asia-Pacific research'
        },

        'Arctic Institute': {
            'base_url': 'https://www.thearcticinstitute.org',
            'paths': results['arctic']['working_paths'] if 'arctic' in results else [],
            'extraction_method': 'standard',
            'language': 'en',
            'notes': 'Specialized in Arctic geopolitics, excellent China Arctic content'
        },

        'Jamestown Foundation': {
            'base_url': 'https://jamestown.org',
            'paths': [
                '/programs/china-brief',
                '/programs/eurasia-daily-monitor',
                '/brief',
                '/china',
                '/publications'
            ],
            'extraction_method': 'standard',
            'language': 'en',
            'notes': 'Already working well from previous tests'
        }
    }

    return updated_sources

def print_summary():
    """Print summary of discoveries and updates"""
    results = load_investigation_results()

    print("=" * 80)
    print("HARVESTER UPDATE SUMMARY")
    print("=" * 80)

    print("DISCOVERED WORKING PATHS:")
    print()

    for source, data in results.items():
        print(f"{source.upper()}:")
        print(f"  Base URL: {data['base_url']}")
        print(f"  China content found: {data['china_content_found']}")
        print(f"  Working paths:")
        for path in data['working_paths']:
            print(f"    - {path}")
        if 'language_notes' in data:
            print(f"  Notes: {data['language_notes']}")
        if 'specialization' in data:
            print(f"  Specialization: {data['specialization']}")
        print()

    print("KEY FINDINGS:")
    print("  - CEIAS: Extensive China content, requires custom extraction")
    print("  - IFRI: Strong Asia-Pacific research, primarily French language")
    print("  - Arctic Institute: Excellent Arctic-China geopolitics content")
    print("  - All sources have working paths with confirmed China content")
    print()

    print("NEXT STEPS:")
    print("  1. Update quick_thinktank_test.py with new paths")
    print("  2. Add custom extraction method for CEIAS")
    print("  3. Add French language support for IFRI")
    print("  4. Test all sources together with new configuration")

def update_test_script():
    """Update the test script with discovered paths"""

    # Read current test script
    test_script_path = 'scripts/quick_thinktank_test.py'
    with open(test_script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Updated source configuration
    new_sources = '''        # Updated with investigation findings
        sources = {
            'Jamestown Foundation': {
                'base_url': 'https://jamestown.org',
                'paths': ['/programs/china-brief', '/programs/eurasia-daily-monitor', '/brief', '/china', '/publications']
            },
            'CEIAS': {
                'base_url': 'https://ceias.eu',
                'paths': ['/en/publications', '/sk/publications', '/en/asia', '/sk/asia']
            },
            'IFRI': {
                'base_url': 'https://www.ifri.org',
                'paths': ['/fr/regions/asie-et-indo-pacifique', '/fr/publications', '/fr/actualites', '/en/regions/asia-and-indo-pacific']
            },
            'Arctic Institute': {
                'base_url': 'https://www.thearcticinstitute.org',
                'paths': ['/china', '/chinese', '/tags/china', '/publications', '/geopolitics', '/?s=china']
            }
        }'''

    # Find and replace the sources section
    import re
    pattern = r'(\s+)(sources = \{.*?\})'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        indent = match.group(1)
        updated_content = content.replace(match.group(0), indent + new_sources)

        # Write updated content
        with open(test_script_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        print(f"Updated {test_script_path} with discovered paths")
    else:
        print(f"Could not find sources section in {test_script_path}")

if __name__ == '__main__':
    print_summary()

    # Save updated configuration
    updated_config = generate_updated_source_config()
    output_file = 'data/test_harvest/updated_source_config.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(updated_config, f, indent=2, ensure_ascii=False)

    print(f"Saved updated configuration to: {output_file}")

    # Update test script
    update_test_script()
