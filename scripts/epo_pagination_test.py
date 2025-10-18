#!/usr/bin/env python3
"""
EPO Pagination Test
Test pagination through large result sets beyond 10,000 limit
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

def test_epo_pagination():
    """Test EPO pagination to access results beyond 10,000"""

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
    print("EPO Pagination Test")
    print("Testing access to results beyond 10,000")
    print("=" * 60)

    search_url = "https://ops.epo.org/3.2/rest-services/published-data/search"

    # Test with a query that has 10,000+ results
    test_query = "pa=huawei"  # We know this has 10,000+ patents

    print(f"\nTest Query: {test_query}")
    print("Testing different range strategies:\n")

    # Strategy 1: Try different range formats
    range_tests = [
        ("1-100", "First 100"),
        ("101-200", "Second 100"),
        ("1001-1100", "Around 1000"),
        ("5001-5100", "Around 5000"),
        ("9901-10000", "Last 100 of first 10k"),
        ("10001-10100", "First 100 beyond 10k"),
        ("10001-10010", "Small range beyond 10k"),
        ("20001-20010", "Far beyond 10k"),
    ]

    results = {
        'query': test_query,
        'pagination_tests': {},
        'total_accessible': 0,
        'max_accessible_index': 0
    }

    for range_param, description in range_tests:
        print(f"Testing Range {range_param}: {description}")

        try:
            params = {
                'q': test_query,
                'Range': range_param
            }

            response = session.get(search_url, params=params, timeout=15)
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                # Check if we got results
                actual_results = 0
                if 'ops:world-patent-data' in data:
                    world_data = data['ops:world-patent-data']
                    if 'ops:biblio-search' in world_data:
                        biblio_search = world_data['ops:biblio-search']

                        # Get total count
                        total_count = 0
                        if '@total-result-count' in biblio_search:
                            total_count = int(biblio_search['@total-result-count'])

                        # Check actual results returned
                        if 'ops:search-result' in biblio_search:
                            search_results = biblio_search['ops:search-result']
                            if isinstance(search_results, list):
                                actual_results = len(search_results)
                            elif search_results:
                                actual_results = 1

                        print(f"  Total in database: {total_count:,}")
                        print(f"  Results returned: {actual_results}")

                        # Track maximum accessible
                        range_end = int(range_param.split('-')[1])
                        if actual_results > 0 and range_end > results['max_accessible_index']:
                            results['max_accessible_index'] = range_end

                results['pagination_tests'][range_param] = {
                    'description': description,
                    'status': response.status_code,
                    'results_returned': actual_results,
                    'total_count': total_count
                }

            elif response.status_code == 404:
                print(f"  Range not found (beyond accessible limit)")
                results['pagination_tests'][range_param] = {
                    'description': description,
                    'status': 404,
                    'error': 'Range beyond limit'
                }

            elif response.status_code == 400:
                print(f"  Bad request (invalid range)")
                error_msg = response.text[:100]
                print(f"  Error: {error_msg}")
                results['pagination_tests'][range_param] = {
                    'description': description,
                    'status': 400,
                    'error': error_msg
                }

            else:
                print(f"  Other error: {response.status_code}")
                results['pagination_tests'][range_param] = {
                    'description': description,
                    'status': response.status_code,
                    'error': response.text[:100]
                }

            time.sleep(1)  # Rate limiting

        except Exception as e:
            print(f"  Exception: {e}")
            results['pagination_tests'][range_param] = {
                'description': description,
                'exception': str(e)
            }

    # Strategy 2: Test date-based pagination
    print("\n" + "=" * 60)
    print("Testing Date-Based Pagination Strategy")
    print("=" * 60)

    date_ranges = [
        ("pd=2023", "Year 2023"),
        ("pd=2022", "Year 2022"),
        ("pd>=20230101 AND pd<=20230331", "Q1 2023"),
        ("pd>=20230401 AND pd<=20230630", "Q2 2023"),
    ]

    for date_filter, description in date_ranges:
        full_query = f"{test_query} AND {date_filter}"
        print(f"\n{description}: {full_query}")

        try:
            params = {
                'q': full_query,
                'Range': '1-100'
            }

            response = session.get(search_url, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()

                total_count = 0
                if 'ops:world-patent-data' in data:
                    world_data = data['ops:world-patent-data']
                    if 'ops:biblio-search' in world_data:
                        biblio_search = world_data['ops:biblio-search']
                        if '@total-result-count' in biblio_search:
                            total_count = int(biblio_search['@total-result-count'])

                print(f"  Total results: {total_count:,}")

                if total_count < 10000:
                    print(f"  ✓ Can retrieve all {total_count} results")
                else:
                    print(f"  ⚠ Still exceeds 10,000 limit")

        except Exception as e:
            print(f"  Error: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("PAGINATION ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Maximum accessible index: {results['max_accessible_index']}")

    # Save results
    output_dir = Path("F:/OSINT_DATA/epo_pagination_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    results_file = output_dir / f"pagination_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {results_file}")

    # Provide strategy recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDED PAGINATION STRATEGIES")
    print("=" * 60)
    print("1. Date-based filtering: Break large queries by year/quarter/month")
    print("2. Technology filtering: Add specific technology terms to narrow results")
    print("3. Country filtering: Add country codes to segment results")
    print("4. IPC classification: Use patent classification codes")
    print("5. Incremental ranges: Process in chunks up to the accessible limit")

    return results

if __name__ == "__main__":
    test_epo_pagination()
